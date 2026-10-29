#![allow(dead_code, unused_imports)]
// Linked to the wheel dependencies and production Linux Jemalloc.
use polars::prelude::*;
use std::{
    alloc::{GlobalAlloc, Layout, System},
    hint::black_box,
    sync::atomic::{AtomicBool, AtomicUsize, Ordering},
    time::Instant,
};
use ta_lib::{
    abstract_api::{FuncId, InputType, OutputType},
    OutRange,
};
static INNER: jemallocator::Jemalloc = jemallocator::Jemalloc;
struct Count;
static ENABLED: AtomicBool = AtomicBool::new(false);
static ALLOCS: AtomicUsize = AtomicUsize::new(0);
static BYTES: AtomicUsize = AtomicUsize::new(0);
static ZEROED: AtomicUsize = AtomicUsize::new(0);
static REALLOCATED: AtomicUsize = AtomicUsize::new(0);
unsafe impl GlobalAlloc for Count {
    unsafe fn alloc(&self, l: Layout) -> *mut u8 {
        if ENABLED.load(Ordering::Relaxed) {
            ALLOCS.fetch_add(1, Ordering::Relaxed);
            BYTES.fetch_add(l.size(), Ordering::Relaxed);
        }
        INNER.alloc(l)
    }
    unsafe fn alloc_zeroed(&self, l: Layout) -> *mut u8 {
        if ENABLED.load(Ordering::Relaxed) {
            ZEROED.fetch_add(1, Ordering::Relaxed);
            ALLOCS.fetch_add(1, Ordering::Relaxed);
            BYTES.fetch_add(l.size(), Ordering::Relaxed);
        }
        INNER.alloc_zeroed(l)
    }
    unsafe fn dealloc(&self, p: *mut u8, l: Layout) {
        INNER.dealloc(p, l)
    }
    unsafe fn realloc(&self, p: *mut u8, l: Layout, n: usize) -> *mut u8 {
        if ENABLED.load(Ordering::Relaxed) {
            REALLOCATED.fetch_add(1, Ordering::Relaxed);
            ALLOCS.fetch_add(1, Ordering::Relaxed);
            BYTES.fetch_add(n, Ordering::Relaxed);
        }
        INNER.realloc(p, l, n)
    }
}
#[global_allocator]
static ALLOC: Count = Count;
extern "C" {
    fn TA_Initialize() -> i32;
    fn TA_CDLENGULFING_Lookback() -> i32;
    fn TA_GetVersionString() -> *const std::os::raw::c_char;
    fn TA_CDLENGULFING(
        s: i32,
        e: i32,
        o: *const f64,
        h: *const f64,
        l: *const f64,
        c: *const f64,
        beg: *mut i32,
        count: *mut i32,
        out: *mut i32,
    ) -> i32;
}
const CANARY: i32 = 0x5a5a5a5a;
const MODES: [&str; 4] = ["c081", "rust_typed", "rust_generic", "native_full"];
struct Cli {
    fixture: String,
    mode: String,
    n: usize,
    iters: usize,
    input: String,
    capture: String,
    golden: Option<String>,
}
fn options(args: &[String]) -> Cli {
    assert!(
        args.len() == 8 || args.len() == 9,
        "fixture mode n iters input capture --capture-only | --golden FILE"
    );
    let fixture = args[1].clone();
    let mode = args[2].clone();
    assert!(["white", "alternating", "equality_ieee"].contains(&fixture.as_str()));
    assert!(MODES.contains(&mode.as_str()));
    let n = args[3].parse::<usize>().unwrap();
    let iters = args[4].parse::<usize>().unwrap();
    assert_eq!(
        iters,
        match n {
            100 => 1000,
            10000 => 10,
            1000000 => 1,
            _ => panic!("fixed lengths only"),
        }
    );
    let golden = if args.len() == 8 {
        assert_eq!(args[7], "--capture-only");
        None
    } else {
        assert_eq!(args[7], "--golden");
        Some(args[8].clone())
    };
    Cli {
        fixture,
        mode,
        n,
        iters,
        input: args[5].clone(),
        capture: args[6].clone(),
        golden,
    }
}
fn load(cli: &Cli) -> [Vec<f64>; 4] {
    let bytes = std::fs::read(&cli.input).unwrap();
    assert_eq!(&bytes[..8], b"ENGDATA1");
    let n = u64::from_le_bytes(bytes[8..16].try_into().unwrap()) as usize;
    let name_len = u64::from_le_bytes(bytes[16..24].try_into().unwrap()) as usize;
    assert_eq!(n, cli.n);
    assert_eq!(&bytes[24..24 + name_len], cli.fixture.as_bytes());
    let body = &bytes[24 + name_len..];
    assert_eq!(body.len(), 4 * n * 8);
    let values: [Vec<f64>; 4] = std::array::from_fn(|i| {
        body[i * n * 8..(i + 1) * n * 8]
            .chunks_exact(8)
            .map(|x| f64::from_le_bytes(x.try_into().unwrap()))
            .collect()
    });
    assert!(
        values.iter().all(|v| v[..2].iter().all(|x| x.is_finite())),
        "common finite initial prefix required"
    );
    values
}
fn metadata() {
    let info = FuncId::CDLENGULFING.info();
    assert_eq!(info.inputs.len(), 1);
    assert!(matches!(info.inputs[0].kind, InputType::Price));
    assert_eq!(info.inputs[0].flags.0, 15);
    assert_eq!(info.outputs.len(), 1);
    assert!(matches!(info.outputs[0].kind, OutputType::Integer));
}
enum State {
    Preallocated {
        values: [Vec<f64>; 4],
        out: Vec<i32>,
    },
    Full {
        inputs: [Series; 4],
        params: native::Params,
    },
}
fn state(cli: &Cli) -> State {
    let values = load(cli);
    if cli.mode == "native_full" {
        let [o, h, l, c] = values;
        State::Full {
            inputs: [
                Series::from_vec("open", o),
                Series::from_vec("high", h),
                Series::from_vec("low", l),
                Series::from_vec("close", c),
            ],
            params: native::Params::new(),
        }
    } else {
        State::Preallocated {
            values,
            out: vec![CANARY; cli.n + 8],
        }
    }
}
fn run(state: &mut State, cli: &Cli) -> Option<Series> {
    match state {
        State::Full { inputs, params } => {
            let result =
                native::compute::<4, 1>(FuncId::CDLENGULFING, inputs, params, &[0, 1, 2, 3], &[])
                    .unwrap();
            assert_eq!(result.len(), cli.n);
            assert_eq!(result.null_count(), 0);
            Some(result)
        }
        State::Preallocated { values, out } => {
            let [o, h, l, c] = values;
            let range = match cli.mode.as_str() {
                "c081" => {
                    let mut beg = 0i32;
                    let mut count = 0i32;
                    let code = unsafe {
                        TA_CDLENGULFING(
                            0,
                            (cli.n - 1) as i32,
                            o.as_ptr(),
                            h.as_ptr(),
                            l.as_ptr(),
                            c.as_ptr(),
                            &mut beg,
                            &mut count,
                            out.as_mut_ptr(),
                        )
                    };
                    assert_eq!(code, 0);
                    assert!(beg >= 0 && count >= 0);
                    OutRange {
                        beg_idx: beg as usize,
                        count: count as usize,
                    }
                }
                "rust_typed" => native::core()
                    .cdlengulfing(0, cli.n - 1, o, h, l, c, out)
                    .unwrap(),
                "rust_generic" => {
                    let mut holder = FuncId::CDLENGULFING.new_call(native::core());
                    holder
                        .set_price_input(0, Some(o), Some(h), Some(l), Some(c), None, None)
                        .unwrap();
                    holder.set_int_output(0, out).unwrap();
                    holder.call(0, cli.n - 1).unwrap()
                }
                _ => unreachable!(),
            };
            assert_eq!((range.beg_idx, range.count), (2, cli.n - 2));
            black_box(&out[..cli.n - 2]);
            None
        }
    }
}
fn captured(state: &State, result: Option<&Series>, n: usize) -> (Vec<u8>, [usize; 5]) {
    let mut aligned = Vec::with_capacity(n + 8);
    if let Some(result) = result {
        let values = result.i32().unwrap();
        let slice = values.cont_slice().unwrap();
        assert_eq!(&slice[..2], &[0, 0]);
        aligned.extend_from_slice(slice);
    } else if let State::Preallocated { out, .. } = state {
        assert!(
            out[n - 2..].iter().all(|v| *v == CANARY),
            "output tail changed"
        );
        aligned.extend_from_slice(&[0, 0]);
        aligned.extend_from_slice(&out[..n - 2]);
    } else {
        unreachable!()
    }
    let mut hits = [0usize; 5];
    for value in &aligned[2..] {
        hits[match *value {
            -100 => 0,
            -80 => 1,
            0 => 2,
            80 => 3,
            100 => 4,
            _ => panic!("invalid candle value"),
        }] += 1;
    }
    aligned.extend_from_slice(&[CANARY; 8]);
    let mut bytes = Vec::with_capacity(4 * n + 64);
    bytes.extend_from_slice(b"ENGOUT01");
    for value in [n, 2, n - 2] {
        bytes.extend_from_slice(&(value as u64).to_le_bytes());
    }
    for value in aligned {
        bytes.extend_from_slice(&value.to_le_bytes());
    }
    assert_eq!(bytes.len(), 4 * n + 64);
    (bytes, hits)
}
#[cfg(not(engulf_probe_contracts))]
fn main() {
    let cli = options(&std::env::args().collect::<Vec<_>>());
    metadata();
    let version = unsafe { std::ffi::CStr::from_ptr(TA_GetVersionString()) }
        .to_str()
        .unwrap();
    assert!(version.starts_with("0.8.1 "));
    println!("C_VERSION {version}");
    if cli.mode == "c081" {
        assert_eq!(unsafe { TA_Initialize() }, 0);
        assert_eq!(unsafe { TA_CDLENGULFING_Lookback() }, 2);
    } else {
        assert_eq!(
            FuncId::CDLENGULFING
                .new_call(native::core())
                .lookback()
                .unwrap(),
            2
        );
    }
    let mut state = state(&cli);
    let first = run(&mut state, &cli);
    let (bytes, hits) = captured(&state, first.as_ref(), cli.n);
    drop(first);
    assert_eq!(hits.iter().sum::<usize>(), cli.n - 2);
    if cli.fixture == "white" {
        assert_eq!(hits, [0, 0, cli.n - 2, 0, 0]);
    }
    if cli.fixture == "alternating" {
        assert!(hits[0] > 0 && hits[4] > 0);
    }
    if cli.fixture == "equality_ieee" {
        assert!(hits.iter().all(|n| *n > 0));
    }
    std::fs::write(&cli.capture, &bytes).unwrap();
    if let Some(path) = &cli.golden {
        assert_eq!(
            std::fs::read(path).unwrap(),
            bytes,
            "full exact golden mismatch"
        );
    }
    println!("VALIDATE fixture={} mode={} n={} beg=2 count={} record_tail=8 physical_tail_checked={} hits={hits:?} exact_golden={}",cli.fixture,cli.mode,cli.n,cli.n-2,cli.mode!="native_full",cli.golden.is_some());
    drop(bytes);
    if cli.golden.is_none() {
        return;
    }
    for _ in 0..5 {
        drop(black_box(run(black_box(&mut state), &cli)));
    }
    ALLOCS.store(0, Ordering::Relaxed);
    BYTES.store(0, Ordering::Relaxed);
    ZEROED.store(0, Ordering::Relaxed);
    REALLOCATED.store(0, Ordering::Relaxed);
    ENABLED.store(true, Ordering::Relaxed);
    drop(black_box(run(black_box(&mut state), &cli)));
    ENABLED.store(false, Ordering::Relaxed);
    let counts = [
        ALLOCS.load(Ordering::Relaxed),
        BYTES.load(Ordering::Relaxed),
        ZEROED.load(Ordering::Relaxed),
        REALLOCATED.load(Ordering::Relaxed),
    ];
    let mut samples = Vec::with_capacity(31);
    for _ in 0..31 {
        let start = Instant::now();
        for _ in 0..cli.iters {
            drop(black_box(run(black_box(&mut state), &cli)));
        }
        samples.push(start.elapsed().as_nanos() as f64 / cli.iters as f64);
    }
    let last = run(&mut state, &cli);
    let (last_bytes, last_hits) = captured(&state, last.as_ref(), cli.n);
    assert_eq!(last_hits, hits);
    assert_eq!(
        std::fs::read(cli.golden.as_ref().unwrap()).unwrap(),
        last_bytes,
        "post-timing full exact golden mismatch"
    );
    println!(
        "PROBE fixture={} mode={} n={} iters={} warmups=5 counts={counts:?} ns={samples:?}",
        cli.fixture, cli.mode, cli.n, cli.iters
    );
}
#[cfg(engulf_probe_contracts)]
mod tests {
    use super::*;
    pub fn run() {
        exact_mode_and_capture_selectors();
        bad_modes_sizes_and_partial_selectors_fail();
        actual_ohlc_metadata_is_four_prices_one_integer();
    }
    fn args(extra: &[&str]) -> Vec<String> {
        extra.iter().map(|v| v.to_string()).collect()
    }
    fn exact_mode_and_capture_selectors() {
        let cli = options(&args(&[
            "probe",
            "white",
            "rust_generic",
            "100",
            "1000",
            "input",
            "capture",
            "--capture-only",
        ]));
        assert!(cli.golden.is_none());
        let cli = options(&args(&[
            "probe",
            "equality_ieee",
            "native_full",
            "10000",
            "10",
            "input",
            "capture",
            "--golden",
            "golden",
        ]));
        assert_eq!(cli.golden.as_deref(), Some("golden"));
    }
    fn bad_modes_sizes_and_partial_selectors_fail() {
        for values in [
            vec![
                "p",
                "white",
                "bad",
                "100",
                "1000",
                "i",
                "o",
                "--capture-only",
            ],
            vec![
                "p",
                "white",
                "c081",
                "101",
                "1000",
                "i",
                "o",
                "--capture-only",
            ],
            vec!["p", "white", "c081", "100", "1", "i", "o", "--capture-only"],
            vec!["p", "white", "c081", "100", "1000", "i", "o", "--golden"],
        ] {
            assert!(std::panic::catch_unwind(|| options(&args(&values))).is_err());
        }
    }
    fn actual_ohlc_metadata_is_four_prices_one_integer() {
        metadata();
    }
}
#[cfg(engulf_probe_contracts)]
mod input_contract_tests {
    use super::*;
    pub fn run() {
        a_nonfinite_initial_price_is_rejected_instead_of_moving_the_adapter_start();
    }
    fn a_nonfinite_initial_price_is_rejected_instead_of_moving_the_adapter_start() {
        let path = std::env::temp_dir().join(format!("engulf-prefix-{}.bin", std::process::id()));
        let cli = Cli {
            fixture: "white".into(),
            mode: "c081".into(),
            n: 100,
            iters: 1000,
            input: path.to_str().unwrap().into(),
            capture: "unused".into(),
            golden: None,
        };
        for bad_column in 0..4 {
            let mut bytes = b"ENGDATA1".to_vec();
            bytes.extend_from_slice(&100u64.to_le_bytes());
            bytes.extend_from_slice(&5u64.to_le_bytes());
            bytes.extend_from_slice(b"white");
            for column in 0..4 {
                for row in 0..100 {
                    let value = if column == bad_column && row == 0 {
                        f64::NAN
                    } else {
                        100.
                    };
                    bytes.extend_from_slice(&value.to_le_bytes());
                }
            }
            std::fs::write(&path, &bytes).unwrap();
            assert!(std::panic::catch_unwind(|| load(&cli)).is_err());
        }
        std::fs::remove_file(path).unwrap();
    }
}

#[cfg(engulf_probe_contracts)]
fn main() {
    tests::run();
    input_contract_tests::run();
    println!("PASS4 probe-only contract checks; native crate tests run separately");
}
