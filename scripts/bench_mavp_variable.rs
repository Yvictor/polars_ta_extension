use std::{
    env,
    ffi::{c_char, c_int, CStr},
    fs::{self, File},
    hint::black_box,
    io::{BufWriter, Write},
    time::Instant,
};

const CANARY: u64 = 0x7ff8_0000_0000_55aa;
const WARMUPS: usize = 5;
const REPEATS: usize = 31;
const BACKENDS: [&str; 3] = ["current", "registry083", "originalc081"];

#[link(name = "ta-lib", kind = "static")]
extern "C" {
    fn TA_Initialize() -> c_int;
    fn TA_Shutdown() -> c_int;
    fn TA_GetVersionString() -> *const c_char;
    fn TA_MAVP(
        start: c_int,
        end: c_int,
        price: *const f64,
        periods: *const f64,
        min: c_int,
        max: c_int,
        kind: c_int,
        beg: *mut c_int,
        count: *mut c_int,
        out: *mut f64,
    ) -> c_int;
    fn TA_SMA(
        start: c_int,
        end: c_int,
        price: *const f64,
        period: c_int,
        beg: *mut c_int,
        count: *mut c_int,
        out: *mut f64,
    ) -> c_int;
}

struct CReference;
impl CReference {
    fn new() -> Self {
        // This reference is initialized once and outlives every synchronous call.
        assert_eq!(unsafe { TA_Initialize() }, 0);
        Self
    }
    fn version(&self) -> String {
        // The official API returns a process-lifetime NUL-terminated string.
        unsafe { CStr::from_ptr(TA_GetVersionString()) }
            .to_str()
            .unwrap()
            .to_owned()
    }
}
impl Drop for CReference {
    fn drop(&mut self) {
        assert_eq!(unsafe { TA_Shutdown() }, 0);
    }
}

#[derive(Clone, Copy)]
enum Kind {
    Sma,
    Ema,
    Wma,
}
impl Kind {
    fn name(self) -> &'static str {
        match self {
            Self::Sma => "SMA",
            Self::Ema => "EMA",
            Self::Wma => "WMA",
        }
    }
    fn code(self) -> i32 {
        match self {
            Self::Sma => 0,
            Self::Ema => 1,
            Self::Wma => 2,
        }
    }
}
struct Case {
    name: String,
    n: usize,
    min: i32,
    kind: Kind,
    sma_control: bool,
    periods: Vec<f64>,
}
impl Case {
    fn iterations(&self) -> usize {
        match self.n {
            100 => 1000,
            1000 => 100,
            10_000 => 10,
            1_000_000 => 1,
            _ => unreachable!(),
        }
    }
    fn range(&self) -> (usize, usize) {
        let beg = if self.sma_control { 13 } else { 29 };
        (beg, self.n - beg)
    }
}
fn cases() -> Vec<Case> {
    let mut cases = Vec::new();
    for n in [100, 1000, 10_000, 1_000_000] {
        for pattern in ["one", "four", "few", "many", "blocked", "clamped"] {
            let periods = (0..n)
                .map(|i| match pattern {
                    "one" => 14.,
                    "four" => [3., 5., 9., 14.][i % 4],
                    "few" => [3., 14.][i % 2],
                    "many" => (2 + i % 29) as f64,
                    "blocked" => [3., 5., 9., 14.][(i * 4 / n).min(3)],
                    "clamped" => [f64::NAN, f64::NEG_INFINITY, 1., 3.75, 9., f64::INFINITY][i % 6],
                    _ => unreachable!(),
                })
                .collect();
            cases.push(Case {
                name: format!("mavp/{pattern}/SMA/{n}"),
                n,
                min: if pattern == "clamped" { 1 } else { 2 },
                kind: Kind::Sma,
                sma_control: false,
                periods,
            });
        }
        for (kind, sma_control) in [(Kind::Sma, true), (Kind::Ema, false), (Kind::Wma, false)] {
            cases.push(Case {
                name: if sma_control {
                    format!("sma_control/SMA/{n}")
                } else {
                    format!("mavp/four/{}/{n}", kind.name())
                },
                n,
                min: 2,
                kind,
                sma_control,
                periods: (0..n).map(|i| [3., 5., 9., 14.][i % 4]).collect(),
            });
        }
    }
    assert_eq!(cases.len(), 36);
    cases
}
fn call(
    current: &ta_lib::Core,
    registry: &ta_lib_registry::Core,
    case: &Case,
    backend: usize,
    price: &[f64],
    out: &mut [f64],
) -> (usize, usize) {
    assert_eq!(price.len(), case.n);
    assert_eq!(case.periods.len(), case.n);
    assert_eq!(out.len(), case.n + 8);
    match backend {
        0 => {
            let r = if case.sma_control {
                current.sma(0, case.n - 1, price, 14, out)
            } else {
                current.mavp(
                    0,
                    case.n - 1,
                    price,
                    &case.periods,
                    case.min,
                    30,
                    ta_lib::MAType::try_from(case.kind.code()).unwrap(),
                    out,
                )
            }
            .unwrap();
            (r.beg_idx, r.count)
        }
        1 => {
            let r = if case.sma_control {
                registry.sma(0, case.n - 1, price, 14, out)
            } else {
                registry.mavp(
                    0,
                    case.n - 1,
                    price,
                    &case.periods,
                    case.min,
                    30,
                    ta_lib_registry::MAType::try_from(case.kind.code()).unwrap(),
                    out,
                )
            }
            .unwrap();
            (r.beg_idx, r.count)
        }
        2 => {
            let mut beg = -1;
            let mut count = -1;
            // All inputs cover 0..n, output capacity exceeds n, and arrays stay
            // alive and disjoint throughout this synchronous official C call.
            let rc = unsafe {
                if case.sma_control {
                    TA_SMA(
                        0,
                        (case.n - 1) as c_int,
                        price.as_ptr(),
                        14,
                        &mut beg,
                        &mut count,
                        out.as_mut_ptr(),
                    )
                } else {
                    TA_MAVP(
                        0,
                        (case.n - 1) as c_int,
                        price.as_ptr(),
                        case.periods.as_ptr(),
                        case.min,
                        30,
                        case.kind.code(),
                        &mut beg,
                        &mut count,
                        out.as_mut_ptr(),
                    )
                }
            };
            assert_eq!(rc, 0, "C call {}", case.name);
            (
                usize::try_from(beg).unwrap(),
                usize::try_from(count).unwrap(),
            )
        }
        _ => unreachable!(),
    }
}
fn check_tail(case: &Case, out: &[f64], range: (usize, usize)) {
    assert_eq!(range, case.range(), "{} range", case.name);
    assert!(
        out[..range.1].iter().all(|v| v.is_finite()),
        "{} nonfinite output for finite input",
        case.name
    );
    assert!(
        out[range.1..].iter().all(|v| v.to_bits() == CANARY),
        "{} tail overwritten",
        case.name
    );
}
fn capture(file: &mut BufWriter<File>, case: &Case, backend: &str, out: &[f64]) {
    let name = format!("{backend}/{}", case.name);
    file.write_all(&(name.len() as u32).to_le_bytes()).unwrap();
    file.write_all(name.as_bytes()).unwrap();
    let (beg, count) = case.range();
    for value in [case.n, beg, count, out.len()] {
        file.write_all(&(value as u64).to_le_bytes()).unwrap();
    }
    for value in out {
        file.write_all(&value.to_bits().to_le_bytes()).unwrap();
    }
}
fn parity(case: &Case, backend: &str, actual: &[f64], expected: &[f64], input_scale: f64) {
    let (mut exact, mut within_tolerance, mut signed_zero, mut nonfinite_same) =
        (0usize, 0usize, 0usize, 0usize);
    let (mut max_abs, mut max_scaled) = (0.0_f64, 0.0_f64);
    for (i, (&a, &b)) in actual.iter().zip(expected).enumerate() {
        if a.to_bits() == b.to_bits() {
            exact += 1;
        } else if a == 0. && b == 0. {
            signed_zero += 1;
        } else if a.is_nan() && b.is_nan() {
            nonfinite_same += 1;
        } else {
            assert!(
                a.is_finite() && b.is_finite(),
                "{} {backend} nonfinite row{i}: {a} != {b}",
                case.name
            );
            let delta = (a - b).abs();
            let scale = input_scale.max(b.abs());
            max_abs = max_abs.max(delta);
            max_scaled = max_scaled.max(delta / scale);
            assert!(
                delta <= 4e-15 * scale,
                "{} {backend} row{i}: {a} != {b}",
                case.name
            );
            within_tolerance += 1;
        }
    }
    assert_eq!(
        exact + within_tolerance + signed_zero + nonfinite_same,
        case.range().1
    );
    assert_eq!(signed_zero, 0);
    assert_eq!(nonfinite_same, 0);
    println!("{{\"kind\":\"parity\",\"case\":{:?},\"backend\":{backend:?},\"count\":{},\"exact\":{exact},\"within_tolerance\":{within_tolerance},\"signed_zero\":{signed_zero},\"nonfinite_same\":{nonfinite_same},\"max_abs\":{max_abs},\"max_scaled\":{max_scaled}}}", case.name, case.range().1);
}
fn work_counts(case: &Case) -> (usize, Option<usize>, Option<usize>, usize, usize) {
    let (_, count) = case.range();
    if case.sma_control {
        return (1, Some(count), Some(count), 0, 0);
    }
    let mut last = [None; 31];
    let mut selected = 0;
    for (i, &value) in case.periods[29..].iter().enumerate() {
        let p = if value.is_nan() || value < f64::from(case.min) {
            case.min as usize
        } else if value > 30. {
            30
        } else {
            value as usize
        };
        last[p] = Some(i);
        selected += usize::from(p > 1);
    }
    let distinct = last.iter().flatten().count();
    let dense = last
        .iter()
        .enumerate()
        .filter_map(|(p, last)| if p > 1 { last.map(|i| i + 1) } else { None })
        .sum();
    let divides = matches!(case.kind, Kind::Sma);
    (
        distinct,
        divides.then_some(dense),
        divides.then_some(selected),
        if distinct > 1 { count * 8 } else { 0 },
        if distinct > 1 { count * 4 } else { 0 },
    )
}
fn optional(value: Option<usize>) -> String {
    value.map_or_else(|| "null".to_owned(), |v| v.to_string())
}
#[derive(Debug, PartialEq, Eq)]
struct Options {
    capture: Option<String>,
    capture_only: bool,
}
fn parse_options(args: &[String]) -> Options {
    assert!(
        (2..=4).contains(&args.len()),
        "REPEATS [CAPTURE_PATH [--capture-only]]"
    );
    assert_eq!(args[1].parse::<usize>().unwrap(), REPEATS);
    let capture = args.get(2).cloned();
    if let Some(path) = &capture {
        assert!(
            !path.is_empty() && !path.starts_with("--"),
            "capture path required before flag"
        );
    }
    let capture_only = args.len() == 4;
    if capture_only {
        assert_eq!(args[3], "--capture-only");
    }
    Options {
        capture,
        capture_only,
    }
}
fn main() {
    let options = parse_options(&env::args().collect::<Vec<_>>());
    let repeats = REPEATS;
    let capture_only = options.capture_only;
    let capture_written = options.capture.is_some();
    assert_eq!(env!("MAVP_CURRENT_VERSION"), "0.8.4");
    assert_eq!(env!("MAVP_REGISTRY_VERSION"), "0.8.3");
    let reference = CReference::new();
    let version = reference.version();
    assert!(
        version.starts_with("0.8.1 "),
        "wrong C reference: {version}"
    );
    let bytes = fs::read(env::var("MAVP_CLOSE_BIN").expect("MAVP_CLOSE_BIN")).unwrap();
    assert_eq!(bytes.len(), 8_000_000);
    let price: Vec<f64> = bytes
        .chunks_exact(8)
        .map(|v| f64::from_le_bytes(v.try_into().unwrap()))
        .collect();
    assert!(price.iter().all(|v| v.is_finite()));
    let current = ta_lib::Core::new();
    let registry = ta_lib_registry::Core::new();
    let cases = cases();
    println!("{{\"kind\":\"metadata\",\"format\":1,\"cases\":36,\"backends\":[\"current\",\"registry083\",\"originalc081\"],\"canary_bits\":\"7ff80000000055aa\",\"warmups\":{WARMUPS},\"repeats\":{repeats},\"capture_only\":{capture_only},\"capture_written\":{capture_written},\"arch\":{:?},\"os\":{:?},\"registry_version\":\"0.8.3\",\"current_version\":\"0.8.4\",\"c_version\":{version:?},\"capture_records\":108,\"tolerance_relative\":4e-15,\"tolerance_floor\":\"max_abs_input\"}}", env::consts::ARCH, env::consts::OS);
    let mut file = options
        .capture
        .as_ref()
        .map(|path| BufWriter::new(File::create(path).unwrap()));
    if let Some(file) = &mut file {
        file.write_all(b"MAVPVC01").unwrap();
    }
    for case in &cases {
        let price = &price[..case.n];
        let scale = price.iter().fold(0.0_f64, |scale, v| scale.max(v.abs()));
        let mut outputs: [Vec<f64>; 3] =
            std::array::from_fn(|_| vec![f64::from_bits(CANARY); case.n + 8]);
        for (backend, out) in outputs.iter_mut().enumerate() {
            let range = call(&current, &registry, case, backend, price, out);
            check_tail(case, out, range);
            if let Some(file) = &mut file {
                capture(file, case, BACKENDS[backend], out);
            }
        }
        for backend in 0..3 {
            parity(
                case,
                BACKENDS[backend],
                &outputs[backend][..case.range().1],
                &outputs[0][..case.range().1],
                scale,
            );
        }
    }
    if let Some(file) = &mut file {
        file.flush().unwrap();
    }
    drop(file);
    if capture_only {
        return;
    }
    for case in &cases {
        let price = &price[..case.n];
        let (distinct, dense, selected, temp_bytes, index_bytes) = work_counts(case);
        for (backend, label) in BACKENDS.iter().enumerate() {
            let mut out = vec![f64::from_bits(CANARY); case.n + 8];
            for _ in 0..WARMUPS {
                black_box(call(&current, &registry, case, backend, price, &mut out));
            }
            let iterations = case.iterations();
            let mut samples = Vec::with_capacity(repeats);
            for _ in 0..repeats {
                let start = Instant::now();
                for _ in 0..iterations {
                    black_box(call(
                        black_box(&current),
                        black_box(&registry),
                        black_box(case),
                        black_box(backend),
                        black_box(price),
                        black_box(&mut out),
                    ));
                }
                samples.push(start.elapsed().as_nanos() as f64 / iterations as f64);
            }
            check_tail(case, &out, case.range());
            println!("{{\"kind\":\"case\",\"case\":{:?},\"backend\":{label:?},\"n\":{},\"beg\":{},\"count\":{},\"iterations\":{iterations},\"warmups\":{WARMUPS},\"samples_ns\":{samples:?},\"distinct_periods\":{distinct},\"main433_dense_divides\":{},\"selected_divides\":{},\"main433_temp_bytes\":{temp_bytes},\"main433_sorted_index_bytes\":{index_bytes}}}", case.name, case.n, case.range().0, case.range().1, optional(dense), optional(selected));
        }
    }
}

#[cfg(test)]
mod tests {
    use super::{parse_options, Options};
    fn args(tail: &[&str]) -> Vec<String> {
        std::iter::once("benchmark")
            .chain(tail.iter().copied())
            .map(str::to_owned)
            .collect()
    }
    #[test]
    fn timed_controller_command_requires_no_capture() {
        assert_eq!(
            parse_options(&args(&["31"])),
            Options {
                capture: None,
                capture_only: false
            }
        );
    }
    #[test]
    fn timed_capture_is_optional() {
        assert_eq!(
            parse_options(&args(&["31", "capture.bin"])),
            Options {
                capture: Some("capture.bin".to_owned()),
                capture_only: false
            }
        );
    }
    #[test]
    fn capture_only_command_requires_a_path() {
        assert_eq!(
            parse_options(&args(&["31", "capture.bin", "--capture-only"])),
            Options {
                capture: Some("capture.bin".to_owned()),
                capture_only: true
            }
        );
        assert!(
            std::panic::catch_unwind(|| parse_options(&args(&["31", "--capture-only"]))).is_err()
        );
    }
    #[test]
    fn malformed_commands_are_rejected_before_any_input_or_timer() {
        for tail in [
            vec![],
            vec!["5"],
            vec!["bad"],
            vec!["31", ""],
            vec!["31", "capture.bin", "--unknown"],
            vec!["31", "capture.bin", "--capture-only", "extra"],
        ] {
            assert!(
                std::panic::catch_unwind(|| parse_options(&args(&tail))).is_err(),
                "{tail:?}"
            );
        }
    }
}
