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
const OUTPUT_PREFIX: usize = 1;

#[link(name = "ta-lib", kind = "static")]
extern "C" {
    fn TA_Initialize() -> c_int;
    fn TA_Shutdown() -> c_int;
    fn TA_GetVersionString() -> *const c_char;
    fn TA_HMA(
        start: c_int,
        end: c_int,
        price: *const f64,
        period: c_int,
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

#[derive(Clone, Copy, Debug)]
enum Pattern {
    Finite,
    Zero,
    NegativeZero,
    Constant,
    Ramp,
    Reverse,
    Alternating,
    HeadNan,
    InteriorNan,
    HeadInf,
    InteriorNegativeInf,
}
impl Pattern {
    fn name(self) -> &'static str {
        match self {
            Self::Finite => "finite",
            Self::Zero => "zero",
            Self::NegativeZero => "negative_zero",
            Self::Constant => "constant",
            Self::Ramp => "ramp",
            Self::Reverse => "reverse",
            Self::Alternating => "alternating",
            Self::HeadNan => "head_nan",
            Self::InteriorNan => "interior_nan",
            Self::HeadInf => "head_inf",
            Self::InteriorNegativeInf => "interior_negative_inf",
        }
    }
    fn input(self, close: &[f64]) -> Vec<f64> {
        let mut data = close.to_vec();
        for (i, v) in data.iter_mut().enumerate() {
            match self {
                Self::Zero => *v = 0.,
                Self::NegativeZero => *v = -0.,
                Self::Constant => *v = 100.,
                Self::Ramp => *v = i as f64,
                Self::Reverse => *v = (close.len() - i) as f64,
                Self::Alternating => *v = if i % 2 == 0 { 1e100 } else { -1e100 },
                _ => (),
            }
        }
        match self {
            Self::HeadNan => data[0] = f64::from_bits(0x7ff8_0000_0000_1234),
            Self::InteriorNan => data[500] = f64::from_bits(0x7ff8_0000_0000_4321),
            Self::HeadInf => data[0] = f64::INFINITY,
            Self::InteriorNegativeInf => data[500] = f64::NEG_INFINITY,
            _ => (),
        }
        data
    }
}
#[derive(Debug)]
struct Case {
    name: String,
    n: usize,
    period: i32,
    start: usize,
    sma_control: bool,
    pattern: Pattern,
    timed: bool,
}
impl Case {
    fn iterations(&self) -> usize {
        (100_000 / self.n).max(1)
    }
    fn range(&self) -> (usize, usize) {
        let p = self.period as usize;
        let lookback = if self.sma_control {
            p - 1
        } else {
            p - 1 + (p as f64).sqrt() as usize - 1
        };
        let beg = self.start.max(lookback);
        if beg >= self.n {
            (0, 0)
        } else {
            (beg, self.n - beg)
        }
    }
}
fn cases() -> Vec<Case> {
    let mut result = Vec::new();
    for n in [20, 100, 512, 1000, 10_000, 1_000_000] {
        for sma_control in [false, true] {
            result.push(Case {
                name: format!(
                    "{}/p20/{n}",
                    if sma_control { "sma_control" } else { "hma" }
                ),
                n,
                period: 20,
                start: 0,
                sma_control,
                pattern: Pattern::Finite,
                timed: true,
            });
        }
    }
    for (period, n) in [(2703, 10_000), (2704, 10_000), (100_000, 1_000_000)] {
        result.push(Case {
            name: format!("hma/p{period}/{n}"),
            n,
            period,
            start: 0,
            sma_control: false,
            pattern: Pattern::Finite,
            timed: true,
        });
    }
    for n in [1, 2, 3, 5, 10, 20, 21, 100, 1000, 10_000, 1_000_000] {
        for p in [
            1, 2, 3, 4, 9, 10, 15, 16, 17, 20, 25, 26, 81, 82, 100, 101, 2703, 2704, 99_999,
            100_000,
        ] {
            result.push(validation_case(n, p, 0, Pattern::Finite));
        }
    }
    for pattern in [
        Pattern::Zero,
        Pattern::NegativeZero,
        Pattern::Constant,
        Pattern::Ramp,
        Pattern::Reverse,
        Pattern::Alternating,
        Pattern::HeadNan,
        Pattern::InteriorNan,
        Pattern::HeadInf,
        Pattern::InteriorNegativeInf,
    ] {
        for period in [1, 2, 3, 4, 20, 100] {
            for start in [0, 25, 500] {
                result.push(validation_case(1000, period, start, pattern));
            }
        }
    }
    for start in [1, 19, 20, 25, 99, 100, 500] {
        result.push(validation_case(1000, 20, start, Pattern::Finite));
    }
    for n in [22, 23, 53, 54, 55, 98, 99, 178, 179, 180] {
        result.push(validation_case(n, 20, 0, Pattern::Finite));
    }
    assert_eq!(result.iter().filter(|c| c.timed).count(), 15);
    assert_eq!(result.iter().filter(|c| !c.timed).count(), 417);
    result
}
fn validation_case(n: usize, period: i32, start: usize, pattern: Pattern) -> Case {
    Case {
        name: format!(
            "validation/hma/{}/p{period}/n{n}/start{start}",
            pattern.name()
        ),
        n,
        period,
        start,
        sma_control: false,
        pattern,
        timed: false,
    }
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
    assert_eq!(out.len(), case.n + 8);
    let end = case.n - 1;
    match backend {
        0 => {
            let r = if case.sma_control {
                current.sma(
                    case.start,
                    end,
                    price,
                    case.period,
                    &mut out[OUTPUT_PREFIX..],
                )
            } else {
                current.hma(
                    case.start,
                    end,
                    price,
                    case.period,
                    &mut out[OUTPUT_PREFIX..],
                )
            }
            .unwrap();
            (r.beg_idx, r.count)
        }
        1 => {
            let r = if case.sma_control {
                registry.sma(
                    case.start,
                    end,
                    price,
                    case.period,
                    &mut out[OUTPUT_PREFIX..],
                )
            } else {
                registry.hma(
                    case.start,
                    end,
                    price,
                    case.period,
                    &mut out[OUTPUT_PREFIX..],
                )
            }
            .unwrap();
            (r.beg_idx, r.count)
        }
        2 => {
            let (mut beg, mut count) = (-1, -1);
            // n<=1M, start<n, all buffers remain live/disjoint, output covers the full range.
            let rc = unsafe {
                if case.sma_control {
                    TA_SMA(
                        case.start as c_int,
                        end as c_int,
                        price.as_ptr(),
                        case.period,
                        &mut beg,
                        &mut count,
                        out[OUTPUT_PREFIX..].as_mut_ptr(),
                    )
                } else {
                    TA_HMA(
                        case.start as c_int,
                        end as c_int,
                        price.as_ptr(),
                        case.period,
                        &mut beg,
                        &mut count,
                        out[OUTPUT_PREFIX..].as_mut_ptr(),
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
        out[..OUTPUT_PREFIX]
            .iter()
            .chain(&out[OUTPUT_PREFIX + range.1..])
            .all(|v| v.to_bits() == CANARY),
        "{} guard overwritten",
        case.name
    );
    if case.timed {
        assert!(out[OUTPUT_PREFIX..OUTPUT_PREFIX + range.1]
            .iter()
            .all(|v| v.is_finite()));
    }
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
    assert_eq!(
        signed_zero, 0,
        "{} {backend}: signed zero differs",
        case.name
    );
    let kind = if case.timed { "parity" } else { "validation" };
    println!("{{\"kind\":{kind:?},\"case\":{:?},\"backend\":{backend:?},\"count\":{},\"exact\":{exact},\"within_tolerance\":{within_tolerance},\"signed_zero\":{signed_zero},\"nonfinite_same\":{nonfinite_same},\"max_abs\":{max_abs},\"max_scaled\":{max_scaled}}}",case.name,case.range().1);
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
    let capture_only = options.capture_only;
    let capture_written = options.capture.is_some();
    assert_eq!(env!("HMA_CURRENT_VERSION"), "0.8.4");
    assert_eq!(env!("HMA_REGISTRY_VERSION"), "0.8.3");
    let reference = CReference::new();
    let version = reference.version();
    assert!(
        version.starts_with("0.8.1 "),
        "wrong C reference: {version}"
    );
    let bytes = fs::read(env::var("HMA_CLOSE_BIN").expect("HMA_CLOSE_BIN")).unwrap();
    assert_eq!(bytes.len(), 8_000_000);
    let close: Vec<f64> = bytes
        .chunks_exact(8)
        .map(|v| f64::from_le_bytes(v.try_into().unwrap()))
        .collect();
    assert!(close.iter().all(|v| v.is_finite()));
    let current = ta_lib::Core::new();
    let registry = ta_lib_registry::Core::new();
    let cases = cases();
    println!("{{\"kind\":\"metadata\",\"format\":1,\"cases\":15,\"validation_cases\":417,\"backends\":[\"current\",\"registry083\",\"originalc081\"],\"canary_bits\":\"7ff80000000055aa\",\"output_prefix\":{OUTPUT_PREFIX},\"warmups\":{WARMUPS},\"repeats\":{REPEATS},\"capture_only\":{capture_only},\"capture_written\":{capture_written},\"arch\":{:?},\"os\":{:?},\"registry_version\":\"0.8.3\",\"current_version\":\"0.8.4\",\"c_version\":{version:?},\"capture_records\":1296,\"tolerance_relative\":4e-15,\"tolerance_floor\":\"max_abs_finite_input\"}}",env::consts::ARCH,env::consts::OS);
    let mut file = options
        .capture
        .as_ref()
        .map(|p| BufWriter::new(File::create(p).unwrap()));
    if let Some(file) = &mut file {
        file.write_all(b"HMAWGT01").unwrap();
    }
    for case in &cases {
        let price = case.pattern.input(&close[..case.n]);
        let scale = price
            .iter()
            .filter(|v| v.is_finite())
            .fold(0.0_f64, |s, v| s.max(v.abs()));
        let mut outputs: [Vec<f64>; 3] =
            std::array::from_fn(|_| vec![f64::from_bits(CANARY); case.n + 8]);
        for (backend, out) in outputs.iter_mut().enumerate() {
            let range = call(&current, &registry, case, backend, &price, out);
            check_tail(case, out, range);
            if let Some(file) = &mut file {
                capture(file, case, BACKENDS[backend], out);
            }
        }
        let end = OUTPUT_PREFIX + case.range().1;
        for backend in 0..3 {
            parity(
                case,
                BACKENDS[backend],
                &outputs[backend][OUTPUT_PREFIX..end],
                &outputs[0][OUTPUT_PREFIX..end],
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
    for case in cases.iter().filter(|c| c.timed) {
        let price = &close[..case.n];
        for (backend, label) in BACKENDS.iter().enumerate() {
            let mut out = vec![f64::from_bits(CANARY); case.n + 8];
            for _ in 0..WARMUPS {
                black_box(call(&current, &registry, case, backend, price, &mut out));
            }
            let iterations = case.iterations();
            let mut samples = Vec::with_capacity(REPEATS);
            for _ in 0..REPEATS {
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
            println!("{{\"kind\":\"case\",\"case\":{:?},\"backend\":{label:?},\"n\":{},\"beg\":{},\"count\":{},\"period\":{},\"start\":{},\"iterations\":{iterations},\"warmups\":{WARMUPS},\"empty_range_control\":{},\"samples_ns\":{samples:?}}}",case.name,case.n,case.range().0,case.range().1,case.period,case.start,case.range().1==0);
        }
    }
}
#[cfg(test)]
mod tests {
    use super::{cases, parse_options, Options};
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
    #[test]
    fn fixed_inventory_has_valid_unique_ranges_and_empty_control() {
        let cases = cases();
        let names: std::collections::BTreeSet<_> = cases.iter().map(|c| &c.name).collect();
        assert_eq!(names.len(), cases.len());
        for c in &cases {
            assert!(c.start < c.n);
            let (beg, count) = c.range();
            assert!(beg + count <= c.n);
            assert_eq!(
                count == 0,
                beg == 0
                    && c.period > 1
                    && c.n <= ((c.period - 1) as usize + (c.period as f64).sqrt() as usize - 1)
            );
        }
        assert_eq!(
            cases.iter().filter(|c| c.timed && c.range().1 == 0).count(),
            1
        );
    }
}
