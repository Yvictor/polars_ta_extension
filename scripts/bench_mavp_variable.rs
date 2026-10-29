use std::{
    env,
    ffi::{c_char, c_int, CStr},
    fs::{self, File},
    hint::black_box,
    io::{BufWriter, Read, Write},
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
    fn TA_MA(
        start: c_int,
        end: c_int,
        price: *const f64,
        period: c_int,
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
    fn version() -> String {
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
    Mama,
}
impl Kind {
    fn code(self) -> i32 {
        match self {
            Self::Sma => 0,
            Self::Ema => 1,
            Self::Wma => 2,
            Self::Mama => ta_lib::MAType::MAMA as i32,
        }
    }
}
struct Case {
    name: String,
    n: usize,
    min: i32,
    kind: Kind,
    sma_control: bool,
    mama_control: bool,
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
        let beg = if self.mama_control {
            32
        } else if self.sma_control {
            13
        } else {
            29
        };
        (beg, self.n - beg)
    }
}
fn case_spec(name: &str) -> (usize, &str, Kind, bool) {
    let parts: Vec<_> = name.split('/').collect();
    let (pattern, kind, n, control) = match parts.as_slice() {
        ["mavp", pattern, "SMA", n]
            if ["one", "four", "few", "many", "blocked", "clamped"].contains(pattern) =>
        {
            (*pattern, Kind::Sma, *n, false)
        }
        ["mavp", "four", "EMA", n] => ("four", Kind::Ema, *n, false),
        ["mavp", "four", "WMA", n] => ("four", Kind::Wma, *n, false),
        ["sma_control", "SMA", n] => ("four", Kind::Sma, *n, true),
        ["ma_control", "MAMA", n] if ["100", "1000000"].contains(n) => {
            ("mama", Kind::Mama, *n, false)
        }
        _ => panic!("unknown case: {name}"),
    };
    let n_text = n;
    let n = n.parse::<usize>().unwrap();
    assert_eq!(n.to_string(), n_text, "noncanonical case size");
    assert!([100, 1000, 10_000, 1_000_000].contains(&n), "unknown size");
    (n, pattern, kind, control)
}
fn make_case(name: &str) -> Case {
    let (n, pattern, kind, sma_control) = case_spec(name);
    let mama_control = matches!(kind, Kind::Mama);
    let periods = (0..if mama_control { 0 } else { n })
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
    Case {
        name: name.to_owned(),
        n,
        min: if pattern == "clamped" { 1 } else { 2 },
        kind,
        sma_control,
        mama_control,
        periods,
    }
}
fn cases() -> Vec<Case> {
    let mut result = Vec::new();
    for n in [100, 1000, 10_000, 1_000_000] {
        for pattern in ["one", "four", "few", "many", "blocked", "clamped"] {
            result.push(make_case(&format!("mavp/{pattern}/SMA/{n}")));
        }
        result.push(make_case(&format!("sma_control/SMA/{n}")));
        result.push(make_case(&format!("mavp/four/EMA/{n}")));
        result.push(make_case(&format!("mavp/four/WMA/{n}")));
    }
    for n in [100, 1_000_000] {
        result.push(make_case(&format!("ma_control/MAMA/{n}")));
    }
    assert_eq!(result.len(), 38);
    result
}
struct Engines {
    current: Option<ta_lib::Core>,
    registry: Option<ta_lib_registry::Core>,
    _reference: Option<CReference>,
}
impl Engines {
    fn new(backend: Option<usize>) -> Self {
        Self {
            current: (backend.is_none() || backend == Some(0)).then(ta_lib::Core::new),
            registry: (backend.is_none() || backend == Some(1)).then(ta_lib_registry::Core::new),
            _reference: (backend.is_none() || backend == Some(2)).then(CReference::new),
        }
    }
}
fn call(
    engines: &Engines,
    case: &Case,
    backend: usize,
    price: &[f64],
    out: &mut [f64],
) -> (usize, usize) {
    assert_eq!(price.len(), case.n);
    assert_eq!(
        case.periods.len(),
        if case.mama_control { 0 } else { case.n }
    );
    assert_eq!(out.len(), case.n + 8);
    match backend {
        0 => {
            let current = engines.current.as_ref().unwrap();
            let r = if case.mama_control {
                current.ma(0, case.n - 1, price, 20, ta_lib::MAType::MAMA, out)
            } else if case.sma_control {
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
            let registry = engines.registry.as_ref().unwrap();
            let r = if case.mama_control {
                registry.ma(0, case.n - 1, price, 20, ta_lib_registry::MAType::MAMA, out)
            } else if case.sma_control {
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
                if case.mama_control {
                    TA_MA(
                        0,
                        (case.n - 1) as c_int,
                        price.as_ptr(),
                        20,
                        case.kind.code(),
                        &mut beg,
                        &mut count,
                        out.as_mut_ptr(),
                    )
                } else if case.sma_control {
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
    if case.mama_control {
        return (1, None, None, 0, 0);
    }
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
    capture: String,
    capture_only: bool,
    case: Option<String>,
    backend: Option<usize>,
    golden: Option<String>,
}
fn parse_options(args: &[String]) -> Options {
    assert!(
        args.len() >= 3,
        "31 CAPTURE_PATH [--case CASE --backend BACKEND --golden PATH] [--capture-only]"
    );
    assert_eq!(args[1].parse::<usize>().unwrap(), REPEATS);
    assert!(
        !args[2].is_empty() && !args[2].starts_with("--"),
        "capture path required"
    );
    let (mut capture_only, mut case, mut backend, mut golden) = (false, None, None, None);
    let mut i = 3;
    while i < args.len() {
        match args[i].as_str() {
            "--capture-only" => {
                assert!(!capture_only, "duplicate flag");
                capture_only = true;
                i += 1;
            }
            "--case" => {
                assert!(case.is_none(), "duplicate case");
                let value = args.get(i + 1).expect("case value");
                case_spec(value);
                case = Some(value.clone());
                i += 2;
            }
            "--backend" => {
                assert!(backend.is_none(), "duplicate backend");
                let value = args.get(i + 1).expect("backend value");
                backend = Some(
                    BACKENDS
                        .iter()
                        .position(|v| v == value)
                        .expect("unknown backend"),
                );
                i += 2;
            }
            "--golden" => {
                assert!(golden.is_none(), "duplicate golden");
                let value = args.get(i + 1).expect("golden value");
                assert!(!value.is_empty() && !value.starts_with("--"));
                golden = Some(value.clone());
                i += 2;
            }
            _ => panic!("unknown argument: {}", args[i]),
        }
    }
    assert_eq!(
        case.is_some(),
        backend.is_some(),
        "case and backend must be selected together"
    );
    if case.is_some() {
        assert!(golden.is_some(), "selected children require golden");
        assert_ne!(
            golden.as_deref(),
            Some(args[2].as_str()),
            "capture must not overwrite golden"
        );
    } else {
        assert!(capture_only, "global timing is forbidden");
        assert!(golden.is_none(), "golden requires selectors");
    }
    Options {
        capture: args[2].clone(),
        capture_only,
        case,
        backend,
        golden,
    }
}
fn metadata(options: &Options) {
    let isolated = options.case.is_some();
    let (scope, count, records) = if isolated {
        ("isolated", 1, 1)
    } else {
        ("full", 38, 114)
    };
    let backends = options.backend.map_or_else(
        || "[\"current\",\"registry083\",\"originalc081\"]".to_owned(),
        |b| format!("[{:?}]", BACKENDS[b]),
    );
    let selected = options.case.as_ref().map_or_else(String::new, |case| {
        format!(
            ",\"selected_case\":{case:?},\"selected_backend\":{:?}",
            BACKENDS[options.backend.unwrap()]
        )
    });
    let version = CReference::version();
    assert!(version.starts_with("0.8.1 "));
    println!("{{\"kind\":\"metadata\",\"format\":2,\"scope\":{scope:?},\"cases\":{count},\"backends\":{backends},\"canary_bits\":\"7ff80000000055aa\",\"warmups\":{WARMUPS},\"repeats\":{REPEATS},\"capture_only\":{},\"capture_written\":true,\"arch\":{:?},\"os\":{:?},\"registry_version\":\"0.8.3\",\"current_version\":\"0.8.4\",\"c_version\":{version:?},\"capture_records\":{records},\"tolerance_relative\":4e-15,\"tolerance_floor\":\"max_abs_input\"{selected}}}", options.capture_only, env::consts::ARCH, env::consts::OS);
}
fn price_prefix(n: usize) -> Vec<f64> {
    let mut file = File::open(env::var("MAVP_CLOSE_BIN").expect("MAVP_CLOSE_BIN")).unwrap();
    assert_eq!(file.metadata().unwrap().len(), 8_000_000);
    let mut bytes = vec![0; n * 8];
    file.read_exact(&mut bytes).unwrap();
    let price: Vec<_> = bytes
        .chunks_exact(8)
        .map(|v| f64::from_le_bytes(v.try_into().unwrap()))
        .collect();
    assert!(price.iter().all(|v| v.is_finite()));
    price
}
fn full_capture(options: &Options) {
    let engines = Engines::new(None);
    let price = price_prefix(1_000_000);
    let mut file = BufWriter::new(File::create(&options.capture).unwrap());
    file.write_all(b"MAVPVC01").unwrap();
    for case in cases() {
        let price = &price[..case.n];
        let scale = price.iter().fold(0.0_f64, |a, v| a.max(v.abs()));
        let mut outputs: [Vec<f64>; 3] =
            std::array::from_fn(|_| vec![f64::from_bits(CANARY); case.n + 8]);
        for (backend, out) in outputs.iter_mut().enumerate() {
            let range = call(&engines, &case, backend, price, out);
            check_tail(&case, out, range);
            capture(&mut file, &case, BACKENDS[backend], out);
        }
        for backend in 0..3 {
            parity(
                &case,
                BACKENDS[backend],
                &outputs[backend][..case.range().1],
                &outputs[0][..case.range().1],
                scale,
            );
        }
    }
    file.flush().unwrap();
}
fn isolated(options: &Options) {
    let case = make_case(options.case.as_ref().unwrap());
    let backend = options.backend.unwrap();
    let label = BACKENDS[backend];
    let engines = Engines::new(Some(backend));
    let price = price_prefix(case.n);
    let mut out = vec![f64::from_bits(CANARY); case.n + 8];
    let range = call(&engines, &case, backend, &price, &mut out);
    check_tail(&case, &out, range);
    {
        let mut file = BufWriter::new(File::create(&options.capture).unwrap());
        file.write_all(b"MAVPVC01").unwrap();
        capture(&mut file, &case, label, &out);
        file.flush().unwrap();
    }
    // This process has called only the selected kernel. The global parent gate
    // supplied this golden; compare full values/ranges/tails before any timer.
    let golden_bytes = {
        let actual = fs::read(&options.capture).unwrap();
        let golden = fs::read(options.golden.as_ref().unwrap()).unwrap();
        assert!(
            actual == golden,
            "selected capture differs from prevalidated golden"
        );
        golden.len()
    };
    println!("{{\"kind\":\"validation\",\"case\":{:?},\"backend\":{label:?},\"n\":{},\"beg\":{},\"count\":{},\"written_finite\":{},\"tail_canary\":{},\"golden_verified\":true,\"golden_bytes\":{golden_bytes}}}", case.name, case.n, range.0, range.1, range.1, out.len() - range.1);
    if options.capture_only {
        return;
    }
    let (distinct, dense, selected, temp_bytes, index_bytes) = work_counts(&case);
    for _ in 0..WARMUPS {
        black_box(call(&engines, &case, backend, &price, &mut out));
    }
    let iterations = case.iterations();
    let mut samples = Vec::with_capacity(REPEATS);
    for _ in 0..REPEATS {
        let start = Instant::now();
        for _ in 0..iterations {
            black_box(call(
                black_box(&engines),
                black_box(&case),
                black_box(backend),
                black_box(&price),
                black_box(&mut out),
            ));
        }
        samples.push(start.elapsed().as_nanos() as f64 / iterations as f64);
    }
    check_tail(&case, &out, case.range());
    println!("{{\"kind\":\"case\",\"case\":{:?},\"backend\":{label:?},\"n\":{},\"beg\":{},\"count\":{},\"iterations\":{iterations},\"warmups\":{WARMUPS},\"samples_ns\":{samples:?},\"distinct_periods\":{distinct},\"main433_dense_divides\":{},\"selected_divides\":{},\"main433_temp_bytes\":{temp_bytes},\"main433_sorted_index_bytes\":{index_bytes}}}", case.name, case.n, range.0, range.1, optional(dense), optional(selected));
}
fn verify_mama_metadata() {
    macro_rules! verify {
        ($library:ident) => {{
            use $library::abstract_api::{FuncId, OptInputType};
            let input = FuncId::MA
                .info()
                .opt_inputs
                .iter()
                .find(|v| v.param_name == "optInMAType")
                .unwrap();
            let OptInputType::IntegerList { values, .. } = input.kind else {
                panic!("MA type metadata");
            };
            let code = values.iter().find(|(_, name)| *name == "MAMA").unwrap().0;
            assert_eq!(code, i64::from(ta_lib::MAType::MAMA as i32));
            assert_eq!($library::MAType::MAMA as i32, 7);
        }};
    }
    verify!(ta_lib);
    verify!(ta_lib_registry);
}
fn main() {
    let options = parse_options(&env::args().collect::<Vec<_>>());
    assert_eq!(env!("MAVP_CURRENT_VERSION"), "0.8.4");
    assert_eq!(env!("MAVP_REGISTRY_VERSION"), "0.8.3");
    if options
        .case
        .as_deref()
        .is_none_or(|name| name.starts_with("ma_control/"))
    {
        verify_mama_metadata();
    }
    metadata(&options);
    if options.case.is_some() {
        isolated(&options);
    } else {
        full_capture(&options);
    }
}
#[cfg(test)]
mod tests {
    use super::*;
    fn args(tail: &[&str]) -> Vec<String> {
        std::iter::once("benchmark")
            .chain(tail.iter().copied())
            .map(str::to_owned)
            .collect()
    }
    #[test]
    fn mama_controls_are_metadata_verified_direct_ma_without_period_tape() {
        verify_mama_metadata();
        for n in [100, 1_000_000] {
            let case = make_case(&format!("ma_control/MAMA/{n}"));
            assert!(case.mama_control && !case.sma_control && case.periods.is_empty());
            assert_eq!(case.kind.code(), 7);
            assert_eq!(case.range(), (32, n - 32));
            assert_eq!(work_counts(&case), (1, None, None, 0, 0));
        }
        for name in [
            "ma_control/MAMA/1000",
            "ma_control/MAMA/10000",
            "mavp/four/MAMA/100",
            "ma_control/MAMA/0100",
        ] {
            assert!(std::panic::catch_unwind(|| case_spec(name)).is_err());
        }
    }
    #[test]
    fn full_capture_remains_global_and_untimed() {
        let options = parse_options(&args(&["31", "capture.bin", "--capture-only"]));
        assert!(options.capture_only && options.case.is_none() && options.backend.is_none());
    }
    #[test]
    fn selected_commands_require_both_selectors_and_golden() {
        for mode in [false, true] {
            let mut values = vec![
                "31",
                "capture.bin",
                "--case",
                "mavp/four/SMA/100",
                "--backend",
                "current",
                "--golden",
                "golden.bin",
            ];
            if mode {
                values.push("--capture-only");
            }
            let options = parse_options(&args(&values));
            assert_eq!(options.capture_only, mode);
            assert_eq!(options.backend, Some(0));
            assert_eq!(options.case.as_deref(), Some("mavp/four/SMA/100"));
        }
    }
    #[test]
    fn malformed_or_stale_timed_commands_fail_before_any_input_or_timer() {
        for values in [
            vec![],
            vec!["31"],
            vec!["31", "capture.bin"],
            vec!["5", "capture.bin", "--capture-only"],
            vec![
                "31",
                "capture.bin",
                "--case",
                "mavp/four/SMA/100",
                "--capture-only",
            ],
            vec![
                "31",
                "capture.bin",
                "--backend",
                "current",
                "--capture-only",
            ],
            vec![
                "31",
                "capture.bin",
                "--case",
                "mavp/four/SMA/100",
                "--backend",
                "current",
            ],
            vec![
                "31",
                "capture.bin",
                "--case",
                "mavp/four/SMA/1",
                "--backend",
                "current",
                "--golden",
                "g",
            ],
            vec![
                "31",
                "capture.bin",
                "--case",
                "mavp/four/SMA/100",
                "--backend",
                "unknown",
                "--golden",
                "g",
            ],
            vec!["31", "capture.bin", "--golden", "g", "--capture-only"],
            vec!["31", "capture.bin", "--capture-only", "--capture-only"],
        ] {
            assert!(
                std::panic::catch_unwind(|| parse_options(&args(&values))).is_err(),
                "{values:?}"
            );
        }
    }
    #[test]
    fn chosen_engines_have_no_sibling_backend() {
        for backend in 0..3 {
            let engines = Engines::new(Some(backend));
            assert_eq!(engines.current.is_some(), backend == 0);
            assert_eq!(engines.registry.is_some(), backend == 1);
            assert_eq!(engines._reference.is_some(), backend == 2);
        }
    }
    #[test]
    fn selected_case_inventory_is_identical() {
        let all = cases();
        assert_eq!(all.len(), 38);
        for case in all {
            let selected = make_case(&case.name);
            assert_eq!(selected.n, case.n);
            assert_eq!(selected.range(), case.range());
            assert!(selected
                .periods
                .iter()
                .zip(case.periods)
                .all(|(a, b)| a.to_bits() == b.to_bits()));
        }
    }
}
