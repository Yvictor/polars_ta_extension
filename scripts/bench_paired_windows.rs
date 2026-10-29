#![cfg_attr(paired_alloc_probe, allow(dead_code))]

#[cfg(not(paired_alloc_probe))]
use std::time::Instant;
use std::{env, fs, hint::black_box, io::Write};
use ta_lib::{Core, FuncUnstId, OutRange, RetCode};

const MAGIC: &[u8; 8] = b"PAIRWIN1";
const REAL_CANARY: u64 = 0x7ff8_0000_0000_55aa;
const INT_CANARY: i32 = 0x55aa_33cc;
const WARMUPS: usize = 5;
const REPEATS: usize = 31;
const TIMED_CASES: usize = 28;
const VALIDATION_CASES: usize = 494;

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
enum Function {
    Supertrend,
    Accbands,
    Kvo,
    Wavetrend,
    Macd,
    Macdfix,
    Ema,
    Sma,
}
const FUNCTIONS: [Function; 8] = [
    Function::Supertrend,
    Function::Accbands,
    Function::Kvo,
    Function::Wavetrend,
    Function::Macd,
    Function::Macdfix,
    Function::Ema,
    Function::Sma,
];
impl Function {
    fn name(self) -> &'static str {
        match self {
            Self::Supertrend => "supertrend",
            Self::Accbands => "accbands",
            Self::Kvo => "kvo",
            Self::Wavetrend => "wavetrend",
            Self::Macd => "macd_control",
            Self::Macdfix => "macdfix_control",
            Self::Ema => "ema_control",
            Self::Sma => "sma_control",
        }
    }
    fn parse(s: &str) -> Self {
        FUNCTIONS
            .into_iter()
            .find(|f| f.name() == s)
            .expect("unknown function")
    }
    fn affected(self) -> bool {
        matches!(
            self,
            Self::Supertrend | Self::Accbands | Self::Kvo | Self::Wavetrend
        )
    }
    fn outputs(self) -> (usize, usize) {
        match self {
            Self::Supertrend => (1, 1),
            Self::Accbands | Self::Macd | Self::Macdfix => (3, 0),
            Self::Kvo | Self::Wavetrend => (2, 0),
            Self::Ema | Self::Sma => (1, 0),
        }
    }
    fn needs_price(self) -> bool {
        self.affected()
    }
    fn defaults(self) -> [i32; 3] {
        match self {
            Self::Supertrend => [10, 0, 0],
            Self::Accbands => [20, 0, 0],
            Self::Kvo => [34, 55, 13],
            Self::Wavetrend => [10, 21, 4],
            Self::Macd => [12, 26, 9],
            Self::Macdfix => [9, 0, 0],
            Self::Ema | Self::Sma => [30, 0, 0],
        }
    }
}
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
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
const PATTERNS: [Pattern; 10] = [
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
];
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
}
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
enum ParamVariant {
    Default,
    Minimum,
    Sentinels,
    MaxFirst,
    Invalid,
}
impl ParamVariant {
    fn name(self) -> &'static str {
        match self {
            Self::Default => "default",
            Self::Minimum => "minimum",
            Self::Sentinels => "sentinels",
            Self::MaxFirst => "maxfirst",
            Self::Invalid => "invalid",
        }
    }
}
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
enum Capacity {
    Default,
    Minimal,
    Short,
    Empty,
}
#[derive(Clone, Debug)]
struct Case {
    name: String,
    function: Function,
    n: usize,
    start: usize,
    end: usize,
    pattern: Pattern,
    params: ParamVariant,
    unstable: u32,
    capacity: Capacity,
    short_input: bool,
    error: Option<RetCode>,
    timed: bool,
}
impl Case {
    fn basic(function: Function, n: usize) -> Self {
        Self {
            name: String::new(),
            function,
            n,
            start: 0,
            end: n - 1,
            pattern: Pattern::Finite,
            params: ParamVariant::Default,
            unstable: 0,
            capacity: Capacity::Default,
            short_input: false,
            error: None,
            timed: false,
        }
    }
    fn iterations(&self) -> usize {
        (100_000 / self.n).max(1)
    }
    fn parameters(&self) -> ([i32; 3], f64) {
        let mut p = self.function.defaults();
        let mut multiplier = 3.;
        match self.params {
            ParamVariant::Default => (),
            ParamVariant::Invalid => p[0] = 0,
            ParamVariant::MaxFirst => p[0] = 100_000,
            ParamVariant::Sentinels => {
                p = [i32::MIN; 3];
                multiplier = Core::REAL_DEFAULT;
            }
            ParamVariant::Minimum => {
                p = match self.function {
                    Function::Supertrend | Function::Accbands => [2, 0, 0],
                    Function::Ema | Function::Sma => [1, 0, 0],
                    Function::Kvo => [2, 2, 2],
                    Function::Wavetrend => [2, 1, 1],
                    Function::Macd => [2, 2, 1],
                    Function::Macdfix => [1, 0, 0],
                };
                multiplier = 0.;
            }
        }
        (p, multiplier)
    }
    fn core(&self) -> Core {
        if self.unstable == 0 {
            Core::new()
        } else {
            Core::builder()
                .unstable_period(
                    if self.function == Function::Supertrend {
                        FuncUnstId::ATR
                    } else {
                        FuncUnstId::EMA
                    },
                    self.unstable,
                )
                .build()
                .unwrap()
        }
    }
    fn lookback(&self, core: &Core) -> Result<usize, RetCode> {
        let (p, m) = self.parameters();
        match self.function {
            Function::Supertrend => core.supertrend_lookback(p[0], m),
            Function::Accbands => core.accbands_lookback(p[0]),
            Function::Kvo => core.kvo_lookback(p[0], p[1], p[2]),
            Function::Wavetrend => core.wavetrend_lookback(p[0], p[1], p[2]),
            Function::Macd => core.macd_lookback(p[0], p[1], p[2]),
            Function::Macdfix => core.macdfix_lookback(p[0]),
            Function::Ema => core.ema_lookback(p[0]),
            Function::Sma => core.sma_lookback(p[0]),
        }
    }
    fn expected_range(&self, core: &Core) -> (usize, usize) {
        let beg = self.start.max(self.lookback(core).unwrap());
        if beg > self.end {
            (0, 0)
        } else {
            (beg, self.end - beg + 1)
        }
    }
    fn output_capacity(&self, core: &Core) -> usize {
        match self.capacity {
            Capacity::Default => self.n + 7,
            Capacity::Minimal => self.expected_range(core).1,
            Capacity::Short => 1,
            Capacity::Empty => 0,
        }
    }
}
fn timed_case(name: &str) -> Case {
    let parts: Vec<_> = name.split('/').collect();
    assert_eq!(parts.len(), 3);
    assert_eq!(parts[1], "default");
    let function = Function::parse(parts[0]);
    let n = parts[2].parse::<usize>().unwrap();
    assert!(
        if function.affected() {
            [100, 1000, 10_000, 1_000_000].contains(&n)
        } else {
            [512, 10_000, 1_000_000].contains(&n)
        },
        "unknown timed length"
    );
    let mut c = Case::basic(function, n);
    c.name = name.to_owned();
    c.timed = true;
    c
}
fn all_cases() -> Vec<Case> {
    let mut result = Vec::new();
    for function in FUNCTIONS {
        for &n in if function.affected() {
            &[100, 1000, 10_000, 1_000_000][..]
        } else {
            &[512, 10_000, 1_000_000][..]
        } {
            result.push(timed_case(&format!("{}/default/{n}", function.name())));
        }
    }
    for function in FUNCTIONS {
        for n in [1, 2, 3, 10, 29, 30, 31, 64, 100, 1000] {
            let mut c = Case::basic(function, n);
            c.name = format!("validation/{}/finite/n{n}/start0", function.name());
            result.push(c);
        }
        for start in [1, 19, 20, 25, 99, 100, 500, 999] {
            let mut c = Case::basic(function, 1000);
            c.start = start;
            c.name = format!("validation/{}/partial/n1000/start{start}", function.name());
            result.push(c);
        }
        for pattern in PATTERNS {
            for start in [0, 25, 500] {
                let mut c = Case::basic(function, 1000);
                c.start = start;
                c.pattern = pattern;
                c.name = format!(
                    "validation/{}/{}/n1000/start{start}",
                    function.name(),
                    pattern.name()
                );
                result.push(c);
            }
        }
        for kind in [
            "invalid_param",
            "short_input",
            "empty_output",
            "short_output",
            "invalid_range",
            "start_overflow",
            "end_overflow",
        ] {
            let mut c = Case::basic(function, 1000);
            c.name = format!("validation/{}/error/{kind}", function.name());
            c.error = Some(match kind {
                "invalid_range" | "end_overflow" => RetCode::OutOfRangeEndIndex,
                "start_overflow" => RetCode::OutOfRangeStartIndex,
                _ => RetCode::BadParam,
            });
            match kind {
                "invalid_param" => c.params = ParamVariant::Invalid,
                "short_input" => c.short_input = true,
                "empty_output" => c.capacity = Capacity::Empty,
                "short_output" => c.capacity = Capacity::Short,
                "invalid_range" => {
                    c.start = 10;
                    c.end = 9;
                }
                "start_overflow" => {
                    c.start = Core::INDEX_MAX + 1;
                    c.end = c.start;
                }
                "end_overflow" => c.end = Core::INDEX_MAX + 1,
                _ => unreachable!(),
            }
            result.push(c);
        }
        let mut c = Case::basic(function, 1000);
        c.name = format!("validation/{}/minimal_output", function.name());
        c.capacity = Capacity::Minimal;
        result.push(c);
        let mut c = Case::basic(function, 1);
        c.name = format!(
            "validation/{}/error/empty_output_before_warmup",
            function.name()
        );
        c.capacity = Capacity::Empty;
        c.error = Some(RetCode::BadParam);
        result.push(c);
        for params in [
            ParamVariant::Minimum,
            ParamVariant::Sentinels,
            ParamVariant::MaxFirst,
        ] {
            let mut c = Case::basic(
                function,
                if params == ParamVariant::MaxFirst {
                    250_000
                } else {
                    1000
                },
            );
            c.params = params;
            c.name = format!("validation/{}/params/{}", function.name(), params.name());
            result.push(c);
        }
    }
    for function in [
        Function::Supertrend,
        Function::Kvo,
        Function::Wavetrend,
        Function::Macd,
        Function::Macdfix,
        Function::Ema,
    ] {
        for &unstable in if function == Function::Supertrend {
            &[1, 2, 10, 50][..]
        } else {
            &[1, 3][..]
        } {
            let mut c = Case::basic(function, 1000);
            c.unstable = unstable;
            c.name = format!("validation/{}/unstable/{unstable}", function.name());
            result.push(c);
        }
    }
    assert_eq!(result.iter().filter(|c| c.timed).count(), TIMED_CASES);
    assert_eq!(result.iter().filter(|c| !c.timed).count(), VALIDATION_CASES);
    result
}
struct InputSource {
    bytes: Vec<u8>,
    fnv: u64,
}
impl InputSource {
    fn read() -> Self {
        let bytes = fs::read(env::var("PAIRED_CLOSE_BIN").expect("PAIRED_CLOSE_BIN")).unwrap();
        assert_eq!(bytes.len(), 8_000_000);
        let fnv = bytes.iter().fold(0xcbf2_9ce4_8422_2325_u64, |h, b| {
            (h ^ u64::from(*b)).wrapping_mul(0x0000_0100_0000_01b3)
        });
        Self { bytes, fnv }
    }
}
struct Data {
    close: Vec<f64>,
    high: Vec<f64>,
    low: Vec<f64>,
    volume: Vec<f64>,
}
impl Data {
    fn new(source: &InputSource, case: &Case) -> Self {
        let mut close: Vec<f64> = source.bytes[..case.n * 8]
            .chunks_exact(8)
            .map(|v| f64::from_le_bytes(v.try_into().unwrap()))
            .collect();
        assert!(close.iter().all(|v| v.is_finite()));
        for (i, v) in close.iter_mut().enumerate() {
            match case.pattern {
                Pattern::Zero => *v = 0.,
                Pattern::NegativeZero => *v = -0.,
                Pattern::Constant => *v = 100.,
                Pattern::Ramp => *v = i as f64,
                Pattern::Reverse => *v = (case.n - i) as f64,
                Pattern::Alternating => *v = if i % 2 == 0 { 1e100 } else { -1e100 },
                _ => (),
            }
        }
        match case.pattern {
            Pattern::HeadNan => close[0] = f64::from_bits(0x7ff8_0000_0000_1234),
            Pattern::InteriorNan => close[500] = f64::from_bits(0x7ff8_0000_0000_4321),
            Pattern::HeadInf => close[0] = f64::INFINITY,
            Pattern::InteriorNegativeInf => close[500] = f64::NEG_INFINITY,
            _ => (),
        }
        let (high, low) = if case.function.needs_price() {
            (
                close.iter().map(|v| v + 1.).collect(),
                close.iter().map(|v| v - 1.).collect(),
            )
        } else {
            (Vec::new(), Vec::new())
        };
        let volume = if case.function == Function::Kvo {
            (0..case.n)
                .map(|i| 100. + ((i * 37) % 901) as f64)
                .collect()
        } else {
            Vec::new()
        };
        if case.short_input {
            close.truncate(case.n - 1);
        }
        Self {
            close,
            high,
            low,
            volume,
        }
    }
}
struct Output {
    real: [Vec<f64>; 3],
    integer: Vec<i32>,
}
impl Output {
    fn new(case: &Case) -> Self {
        let (r, i) = case.function.outputs();
        Self {
            real: std::array::from_fn(|j| {
                if j < r {
                    vec![f64::from_bits(REAL_CANARY); case.n + 8]
                } else {
                    Vec::new()
                }
            }),
            integer: if i > 0 {
                vec![INT_CANARY; case.n + 8]
            } else {
                Vec::new()
            },
        }
    }
    fn guards(&self, case: &Case, count: usize) {
        for real in self.real.iter().take(case.function.outputs().0) {
            assert!(
                real[..1]
                    .iter()
                    .chain(&real[1 + count..])
                    .all(|v| v.to_bits() == REAL_CANARY),
                "{} float guard",
                case.name
            );
        }
        if !self.integer.is_empty() {
            assert!(
                self.integer[..1]
                    .iter()
                    .chain(&self.integer[1 + count..])
                    .all(|v| *v == INT_CANARY),
                "{} integer guard",
                case.name
            );
        }
    }
}
fn call(
    core: &Core,
    case: &Case,
    data: &Data,
    out: &mut Output,
    capacity: usize,
) -> Result<OutRange, RetCode> {
    let [p0, p1, p2] = case.parameters().0;
    let m = case.parameters().1;
    let [a, b, c] = &mut out.real;
    match case.function {
        Function::Supertrend => core.supertrend(
            case.start,
            case.end,
            &data.high,
            &data.low,
            &data.close,
            p0,
            m,
            &mut a[1..1 + capacity],
            &mut out.integer[1..1 + capacity],
        ),
        Function::Accbands => core.accbands(
            case.start,
            case.end,
            &data.high,
            &data.low,
            &data.close,
            p0,
            &mut a[1..1 + capacity],
            &mut b[1..1 + capacity],
            &mut c[1..1 + capacity],
        ),
        Function::Kvo => core.kvo(
            case.start,
            case.end,
            &data.high,
            &data.low,
            &data.close,
            &data.volume,
            p0,
            p1,
            p2,
            &mut a[1..1 + capacity],
            &mut b[1..1 + capacity],
        ),
        Function::Wavetrend => core.wavetrend(
            case.start,
            case.end,
            &data.high,
            &data.low,
            &data.close,
            p0,
            p1,
            p2,
            &mut a[1..1 + capacity],
            &mut b[1..1 + capacity],
        ),
        Function::Macd => core.macd(
            case.start,
            case.end,
            &data.close,
            p0,
            p1,
            p2,
            &mut a[1..1 + capacity],
            &mut b[1..1 + capacity],
            &mut c[1..1 + capacity],
        ),
        Function::Macdfix => core.macdfix(
            case.start,
            case.end,
            &data.close,
            p0,
            &mut a[1..1 + capacity],
            &mut b[1..1 + capacity],
            &mut c[1..1 + capacity],
        ),
        Function::Ema => core.ema(
            case.start,
            case.end,
            &data.close,
            p0,
            &mut a[1..1 + capacity],
        ),
        Function::Sma => core.sma(
            case.start,
            case.end,
            &data.close,
            p0,
            &mut a[1..1 + capacity],
        ),
    }
}
struct Checked {
    status: String,
    beg: usize,
    count: usize,
    capacity: usize,
    record: Vec<u8>,
}
fn append_string(bytes: &mut Vec<u8>, value: &str) {
    bytes.extend_from_slice(&(value.len() as u32).to_le_bytes());
    bytes.extend_from_slice(value.as_bytes());
}
fn record(case: &Case, status: &str, beg: usize, count: usize, out: &Output) -> Vec<u8> {
    let mut payload = Vec::new();
    append_string(&mut payload, &case.name);
    append_string(&mut payload, status);
    let (r, i) = case.function.outputs();
    for value in [case.n, case.start, case.end, beg, count, r, i] {
        payload.extend_from_slice(&(value as u64).to_le_bytes());
    }
    for values in out.real.iter().take(r) {
        payload.extend_from_slice(&(values.len() as u64).to_le_bytes());
        for v in values {
            payload.extend_from_slice(&v.to_bits().to_le_bytes());
        }
    }
    if i > 0 {
        payload.extend_from_slice(&(out.integer.len() as u64).to_le_bytes());
        for v in &out.integer {
            payload.extend_from_slice(&v.to_le_bytes());
        }
    }
    let mut bytes = Vec::with_capacity(8 + payload.len());
    bytes.extend_from_slice(&(payload.len() as u64).to_le_bytes());
    bytes.extend_from_slice(&payload);
    bytes
}
fn checked(core: &Core, case: &Case, data: &Data, out: &mut Output) -> Checked {
    let capacity = case.output_capacity(core);
    let result = call(core, case, data, out, capacity);
    let (status, beg, count) = match result {
        Ok(range) => {
            assert!(case.error.is_none(), "{} expected rejection", case.name);
            assert_eq!(
                (range.beg_idx, range.count),
                case.expected_range(core),
                "{} range",
                case.name
            );
            ("Success".to_owned(), range.beg_idx, range.count)
        }
        Err(code) => {
            assert_eq!(Some(code), case.error, "{} unexpected error", case.name);
            (format!("{code:?}"), 0, 0)
        }
    };
    out.guards(case, count);
    if case.timed {
        for r in out.real.iter().take(case.function.outputs().0) {
            assert!(
                r[1..1 + count].iter().all(|v| v.is_finite()),
                "{} finite timed output",
                case.name
            );
        }
    }
    let record = record(case, &status, beg, count, out);
    Checked {
        status,
        beg,
        count,
        capacity,
        record,
    }
}
fn capture_file(record: &[u8]) -> Vec<u8> {
    let mut bytes = Vec::with_capacity(8 + record.len());
    bytes.extend_from_slice(MAGIC);
    bytes.extend_from_slice(record);
    bytes
}
fn write_capture(path: &str, bytes: &[u8]) {
    fs::write(path, bytes).unwrap();
}
fn write_new_capture(path: &str, bytes: &[u8]) {
    let mut file = fs::OpenOptions::new()
        .write(true)
        .create_new(true)
        .open(path)
        .unwrap();
    file.write_all(bytes).unwrap();
}
#[derive(Debug, PartialEq, Eq)]
enum Options {
    CaptureFull {
        output: String,
    },
    CaptureCase {
        case: String,
        output: String,
    },
    Bench {
        case: String,
        golden: String,
        actual: String,
    },
}
fn parse_options(args: &[String]) -> Options {
    let valid_path = |v: &str| assert!(!v.is_empty() && !v.starts_with("--"), "path required");
    match args.get(1).map(String::as_str) {
        Some("--capture-full") => {
            assert_eq!(args.len(), 3);
            valid_path(&args[2]);
            Options::CaptureFull {
                output: args[2].clone(),
            }
        }
        Some("--capture-case") => {
            assert_eq!(args.len(), 4);
            timed_case(&args[2]);
            valid_path(&args[3]);
            Options::CaptureCase {
                case: args[2].clone(),
                output: args[3].clone(),
            }
        }
        Some("--bench") => {
            assert_eq!(args.len(), 5);
            timed_case(&args[2]);
            valid_path(&args[3]);
            valid_path(&args[4]);
            assert_ne!(args[3], args[4], "golden must remain read-only");
            Options::Bench {
                case: args[2].clone(),
                golden: args[3].clone(),
                actual: args[4].clone(),
            }
        }
        _ => panic!(
            "--capture-full OUT | --capture-case CASE OUT | --bench CASE GOLDEN ACTUAL_CAPTURE"
        ),
    }
}
fn metadata(
    mode: &str,
    selected: Option<&str>,
    source: &InputSource,
    validated: bool,
    selected_bytes: usize,
) {
    let selected = selected.map_or_else(|| "null".to_owned(), |s| format!("{s:?}"));
    let records = if mode == "capture-full" {
        TIMED_CASES + VALIDATION_CASES
    } else {
        1
    };
    println!("{{\"kind\":\"metadata\",\"format\":1,\"mode\":{mode:?},\"selected_case\":{selected},\"cases\":{TIMED_CASES},\"validation_cases\":{VALIDATION_CASES},\"capture_records\":{records},\"warmups\":{WARMUPS},\"repeats\":{REPEATS},\"arch\":{:?},\"os\":{:?},\"version\":\"0.8.4\",\"input_bytes\":{},\"close_fnv1a64\":\"{:016x}\",\"selected_validated\":{validated},\"actual_capture_written\":true,\"selected_record_bytes\":{selected_bytes}}}",env::consts::ARCH,env::consts::OS,source.bytes.len(),source.fnv);
}
fn common_json(case: &Case, c: &Checked) -> String {
    let (r, i) = case.function.outputs();
    format!("\"case\":{:?},\"n\":{},\"start\":{},\"end\":{},\"status\":{:?},\"beg\":{},\"count\":{},\"real_outputs\":{r},\"integer_outputs\":{i},\"output_capacity\":{},\"pattern\":{:?},\"param_variant\":{:?},\"unstable\":{},\"short_input\":{},\"record_bytes\":{}",case.name,case.n,case.start,case.end,c.status,c.beg,c.count,c.capacity,case.pattern.name(),case.params.name(),case.unstable,case.short_input,c.record.len())
}
fn exact_golden(actual: &[u8], expected: &[u8]) {
    assert_eq!(
        actual.len(),
        expected.len(),
        "selected golden length differs"
    );
    assert!(
        actual == expected,
        "selected record differs from globally prevalidated golden"
    );
}
#[cfg(not(paired_alloc_probe))]
fn main() {
    let options = parse_options(&env::args().collect::<Vec<_>>());
    assert_eq!(env!("PAIRED_VERSION"), "0.8.4");
    let source = InputSource::read();
    match options {
        Options::CaptureFull { output } => {
            metadata("capture-full", None, &source, false, 0);
            let mut bytes = MAGIC.to_vec();
            for case in all_cases() {
                let core = case.core();
                let data = Data::new(&source, &case);
                let mut out = Output::new(&case);
                let c = checked(&core, &case, &data, &mut out);
                println!("{{\"kind\":\"capture\",{}}}", common_json(&case, &c));
                bytes.extend_from_slice(&c.record);
            }
            write_capture(&output, &bytes);
        }
        Options::CaptureCase { case, output } => {
            let case = timed_case(&case);
            let core = case.core();
            let data = Data::new(&source, &case);
            let mut out = Output::new(&case);
            let c = checked(&core, &case, &data, &mut out);
            let bytes = capture_file(&c.record);
            write_capture(&output, &bytes);
            metadata(
                "capture-case",
                Some(&case.name),
                &source,
                false,
                bytes.len(),
            );
            println!("{{\"kind\":\"capture\",{}}}", common_json(&case, &c));
        }
        Options::Bench {
            case,
            golden,
            actual,
        } => {
            // A timed child constructs and calls this selected fixture only.
            let case = timed_case(&case);
            let core = case.core();
            let data = Data::new(&source, &case);
            let mut out = Output::new(&case);
            let c = checked(&core, &case, &data, &mut out);
            let bytes = capture_file(&c.record);
            let expected = fs::read(&golden).unwrap();
            write_new_capture(&actual, &bytes);
            exact_golden(&bytes, &expected);
            metadata("bench", Some(&case.name), &source, true, bytes.len());
            drop(bytes);
            drop(expected);
            for _ in 0..WARMUPS {
                black_box(call(&core, &case, &data, &mut out, c.capacity)).unwrap();
            }
            let iterations = case.iterations();
            let mut samples = Vec::with_capacity(REPEATS);
            for _ in 0..REPEATS {
                let start = Instant::now();
                for _ in 0..iterations {
                    black_box(call(
                        black_box(&core),
                        black_box(&case),
                        black_box(&data),
                        black_box(&mut out),
                        black_box(c.capacity),
                    ))
                    .unwrap();
                }
                samples.push(start.elapsed().as_nanos() as f64 / iterations as f64);
            }
            out.guards(&case, c.count);
            println!("{{\"kind\":\"case\",{},\"iterations\":{iterations},\"warmups\":{WARMUPS},\"samples_ns\":{samples:?}}}",common_json(&case,&c));
        }
    }
}
#[cfg(all(test, not(paired_alloc_probe)))]
mod tests {
    use super::*;
    fn args(tail: &[&str]) -> Vec<String> {
        std::iter::once("benchmark")
            .chain(tail.iter().copied())
            .map(str::to_owned)
            .collect()
    }
    #[test]
    fn timed_command_requires_selected_case_and_distinct_golden_actual_paths() {
        assert_eq!(
            parse_options(&args(&[
                "--bench",
                "supertrend/default/100",
                "golden.bin",
                "actual.bin"
            ])),
            Options::Bench {
                case: "supertrend/default/100".to_owned(),
                golden: "golden.bin".to_owned(),
                actual: "actual.bin".to_owned()
            }
        );
        assert!(std::panic::catch_unwind(|| parse_options(&args(&[
            "--bench",
            "supertrend/default/100",
            "same",
            "same"
        ])))
        .is_err());
    }
    #[test]
    fn capture_commands_are_separate_from_timer() {
        assert_eq!(
            parse_options(&args(&["--capture-full", "full.bin"])),
            Options::CaptureFull {
                output: "full.bin".to_owned()
            }
        );
        assert_eq!(
            parse_options(&args(&[
                "--capture-case",
                "ema_control/default/512",
                "one.bin"
            ])),
            Options::CaptureCase {
                case: "ema_control/default/512".to_owned(),
                output: "one.bin".to_owned()
            }
        );
    }
    #[test]
    fn malformed_or_unknown_cases_fail_before_input_or_any_timer() {
        for tail in [
            vec![],
            vec!["31"],
            vec!["--allocation-case", "supertrend/default/100"],
            vec!["--bench", "supertrend/default/100", "only-golden"],
            vec!["--bench", "supertrend/default/99", "g", "a"],
            vec!["--capture-case", "unknown/default/100", "a"],
            vec!["--capture-full", "--capture-only"],
            vec!["--capture-full", "a", "extra"],
        ] {
            assert!(
                std::panic::catch_unwind(|| parse_options(&args(&tail))).is_err(),
                "{tail:?}"
            );
        }
    }
    #[test]
    fn selected_golden_mismatch_is_rejected_before_timing() {
        exact_golden(b"same", b"same");
        assert!(std::panic::catch_unwind(|| exact_golden(b"bad", b"old")).is_err());
        assert!(std::panic::catch_unwind(|| exact_golden(b"bad", b"longer")).is_err());
    }
    #[test]
    fn fixed_full_inventory_is_unique_and_valid() {
        let cases = all_cases();
        let names: std::collections::BTreeSet<_> = cases.iter().map(|c| &c.name).collect();
        assert_eq!(names.len(), TIMED_CASES + VALIDATION_CASES);
        for c in &cases {
            assert!(c.n > 0 && c.n <= 1_000_000);
            if c.timed {
                assert!(c.error.is_none());
                assert_eq!(c.start, 0);
                assert_eq!(c.end, c.n - 1);
                assert_eq!(timed_case(&c.name).function, c.function);
            }
        }
    }
}

#[cfg(paired_alloc_probe)]
mod allocation_probe {
    use std::alloc::{GlobalAlloc, Layout, System};
    use std::sync::atomic::{AtomicBool, AtomicU64, Ordering};

    struct CounterAllocator;
    #[global_allocator]
    static ALLOCATOR: CounterAllocator = CounterAllocator;
    static ENABLED: AtomicBool = AtomicBool::new(false);
    static ALLOC_REQUESTS: AtomicU64 = AtomicU64::new(0);
    static ALLOC_BYTES: AtomicU64 = AtomicU64::new(0);
    static REALLOC_REQUESTS: AtomicU64 = AtomicU64::new(0);
    static REALLOC_BYTES: AtomicU64 = AtomicU64::new(0);
    static DEALLOC_REQUESTS: AtomicU64 = AtomicU64::new(0);
    static DEALLOC_BYTES: AtomicU64 = AtomicU64::new(0);

    // Each request is forwarded unchanged to System. Realloc bytes are its new
    // requested size; its implicit old-block release is not a dealloc request.
    unsafe impl GlobalAlloc for CounterAllocator {
        unsafe fn alloc(&self, layout: Layout) -> *mut u8 {
            if ENABLED.load(Ordering::Relaxed) {
                ALLOC_REQUESTS.fetch_add(1, Ordering::Relaxed);
                ALLOC_BYTES.fetch_add(layout.size() as u64, Ordering::Relaxed);
            }
            unsafe { System.alloc(layout) }
        }
        unsafe fn alloc_zeroed(&self, layout: Layout) -> *mut u8 {
            if ENABLED.load(Ordering::Relaxed) {
                ALLOC_REQUESTS.fetch_add(1, Ordering::Relaxed);
                ALLOC_BYTES.fetch_add(layout.size() as u64, Ordering::Relaxed);
            }
            unsafe { System.alloc_zeroed(layout) }
        }
        unsafe fn realloc(&self, ptr: *mut u8, layout: Layout, new_size: usize) -> *mut u8 {
            if ENABLED.load(Ordering::Relaxed) {
                REALLOC_REQUESTS.fetch_add(1, Ordering::Relaxed);
                REALLOC_BYTES.fetch_add(new_size as u64, Ordering::Relaxed);
            }
            unsafe { System.realloc(ptr, layout, new_size) }
        }
        unsafe fn dealloc(&self, ptr: *mut u8, layout: Layout) {
            if ENABLED.load(Ordering::Relaxed) {
                DEALLOC_REQUESTS.fetch_add(1, Ordering::Relaxed);
                DEALLOC_BYTES.fetch_add(layout.size() as u64, Ordering::Relaxed);
            }
            unsafe { System.dealloc(ptr, layout) }
        }
    }
    #[derive(Debug, PartialEq, Eq)]
    pub(super) struct Snapshot {
        pub alloc_requests: u64,
        pub alloc_requested_bytes: u64,
        pub realloc_requests: u64,
        pub realloc_requested_bytes: u64,
        pub dealloc_requests: u64,
        pub dealloc_requested_bytes: u64,
    }
    pub(super) fn begin() {
        assert!(!ENABLED.load(Ordering::SeqCst));
        for counter in [
            &ALLOC_REQUESTS,
            &ALLOC_BYTES,
            &REALLOC_REQUESTS,
            &REALLOC_BYTES,
            &DEALLOC_REQUESTS,
            &DEALLOC_BYTES,
        ] {
            counter.store(0, Ordering::SeqCst);
        }
        ENABLED.store(true, Ordering::SeqCst);
    }
    pub(super) fn end() -> Snapshot {
        ENABLED.store(false, Ordering::SeqCst);
        Snapshot {
            alloc_requests: ALLOC_REQUESTS.load(Ordering::SeqCst),
            alloc_requested_bytes: ALLOC_BYTES.load(Ordering::SeqCst),
            realloc_requests: REALLOC_REQUESTS.load(Ordering::SeqCst),
            realloc_requested_bytes: REALLOC_BYTES.load(Ordering::SeqCst),
            dealloc_requests: DEALLOC_REQUESTS.load(Ordering::SeqCst),
            dealloc_requested_bytes: DEALLOC_BYTES.load(Ordering::SeqCst),
        }
    }
}

#[cfg(paired_alloc_probe)]
fn parse_allocation_options(args: &[String]) -> String {
    assert_eq!(args.len(), 3, "--allocation-case CASE");
    assert_eq!(
        args[1], "--allocation-case",
        "diagnostic binary has no timing modes"
    );
    timed_case(&args[2]);
    args[2].clone()
}

#[cfg(paired_alloc_probe)]
fn main() {
    let name = parse_allocation_options(&env::args().collect::<Vec<_>>());
    assert_eq!(env!("PAIRED_VERSION"), "0.8.4");
    let source = InputSource::read();
    let case = timed_case(&name);
    let core = case.core();
    let data = Data::new(&source, &case);
    let mut output = Output::new(&case);
    let capacity = case.output_capacity(&core);
    // Observable counters may change optimizer allocation elision. Equal request
    // counts support, but do not prove, the uninstrumented primary footprint.
    allocation_probe::begin();
    let result = black_box(call(
        black_box(&core),
        black_box(&case),
        black_box(&data),
        black_box(&mut output),
        black_box(capacity),
    ));
    let counts = allocation_probe::end();
    let (status, beg, count) = match result {
        Ok(range) => {
            assert_eq!((range.beg_idx, range.count), case.expected_range(&core));
            ("Success".to_owned(), range.beg_idx, range.count)
        }
        Err(code) => (format!("{code:?}"), 0, 0),
    };
    output.guards(&case, count);
    println!("{{\"kind\":\"allocation\",\"format\":1,\"case\":{:?},\"n\":{},\"start\":{},\"end\":{},\"status\":{status:?},\"beg\":{beg},\"count\":{count},\"version\":\"0.8.4\",\"arch\":{:?},\"os\":{:?},\"input_bytes\":{},\"close_fnv1a64\":\"{:016x}\",\"alloc_requests\":{},\"alloc_requested_bytes\":{},\"realloc_requests\":{},\"realloc_requested_bytes\":{},\"dealloc_requests\":{},\"dealloc_requested_bytes\":{}}}",
        case.name, case.n, case.start, case.end, env::consts::ARCH, env::consts::OS,
        source.bytes.len(), source.fnv, counts.alloc_requests, counts.alloc_requested_bytes,
        counts.realloc_requests, counts.realloc_requested_bytes, counts.dealloc_requests,
        counts.dealloc_requested_bytes);
}

#[cfg(all(test, paired_alloc_probe))]
mod allocation_tests {
    use super::*;
    fn args(tail: &[&str]) -> Vec<String> {
        std::iter::once("diagnostic")
            .chain(tail.iter().copied())
            .map(str::to_owned)
            .collect()
    }
    #[test]
    fn diagnostic_accepts_only_one_allocation_case() {
        assert_eq!(
            parse_allocation_options(&args(&["--allocation-case", "supertrend/default/100"])),
            "supertrend/default/100"
        );
    }
    #[test]
    fn diagnostic_rejects_all_primary_modes_and_unknown_cases() {
        for tail in [
            vec![],
            vec!["--capture-full", "full.bin"],
            vec!["--capture-case", "supertrend/default/100", "out.bin"],
            vec![
                "--bench",
                "supertrend/default/100",
                "golden.bin",
                "actual.bin",
            ],
            vec!["--allocation-case", "supertrend/default/99"],
            vec!["--allocation-case", "supertrend/default/100", "extra"],
        ] {
            assert!(std::panic::catch_unwind(|| parse_allocation_options(&args(&tail))).is_err());
        }
    }
    #[test]
    fn counters_distinguish_requests_sizes_and_stop_before_cleanup() {
        use std::alloc::{alloc, alloc_zeroed, dealloc, handle_alloc_error, realloc, Layout};
        let old = Layout::from_size_align(32, 8).unwrap();
        let new = Layout::from_size_align(64, 8).unwrap();
        let zeroed = Layout::from_size_align(24, 8).unwrap();
        allocation_probe::begin();
        // These layout/pointer pairs follow the std::alloc contract, and black_box
        // retains their observable use while the diagnostic counts the requests.
        let p = unsafe { alloc(old) };
        if p.is_null() {
            handle_alloc_error(old)
        }
        let p = unsafe { realloc(black_box(p), old, 64) };
        if p.is_null() {
            handle_alloc_error(new)
        }
        let z = unsafe { alloc_zeroed(zeroed) };
        if z.is_null() {
            handle_alloc_error(zeroed)
        }
        unsafe { dealloc(black_box(p), new) };
        let counts = allocation_probe::end();
        unsafe { dealloc(black_box(z), zeroed) };
        assert_eq!(
            counts,
            allocation_probe::Snapshot {
                alloc_requests: 2,
                alloc_requested_bytes: 56,
                realloc_requests: 1,
                realloc_requested_bytes: 64,
                dealloc_requests: 1,
                dealloc_requested_bytes: 64
            }
        );
    }
}
