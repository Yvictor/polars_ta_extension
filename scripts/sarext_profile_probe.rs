//! Selected SAREXT stage diagnostic, not product throughput or additive costs.
use polars::prelude::*;
use std::{
    alloc::{GlobalAlloc, Layout},
    hint::black_box,
    sync::atomic::{AtomicBool, AtomicUsize, Ordering},
    time::Instant,
};
use ta_lib::{
    abstract_api::{FuncId, InputType, OutputType},
    Core, OutRange,
};
static INNER: jemallocator::Jemalloc = jemallocator::Jemalloc;
struct Count;
static ENABLED: AtomicBool = AtomicBool::new(false);
static COUNTS: [AtomicUsize; 4] = [
    AtomicUsize::new(0),
    AtomicUsize::new(0),
    AtomicUsize::new(0),
    AtomicUsize::new(0),
];
#[cfg(sarext_counter)]
unsafe impl GlobalAlloc for Count {
    unsafe fn alloc(&self, l: Layout) -> *mut u8 {
        if ENABLED.load(Ordering::Relaxed) {
            COUNTS[0].fetch_add(1, Ordering::Relaxed);
            COUNTS[1].fetch_add(l.size(), Ordering::Relaxed);
        }
        INNER.alloc(l)
    }
    unsafe fn alloc_zeroed(&self, l: Layout) -> *mut u8 {
        if ENABLED.load(Ordering::Relaxed) {
            COUNTS[0].fetch_add(1, Ordering::Relaxed);
            COUNTS[1].fetch_add(l.size(), Ordering::Relaxed);
            COUNTS[2].fetch_add(1, Ordering::Relaxed);
        }
        INNER.alloc_zeroed(l)
    }
    unsafe fn realloc(&self, p: *mut u8, l: Layout, n: usize) -> *mut u8 {
        if ENABLED.load(Ordering::Relaxed) {
            COUNTS[0].fetch_add(1, Ordering::Relaxed);
            COUNTS[1].fetch_add(n, Ordering::Relaxed);
            COUNTS[3].fetch_add(1, Ordering::Relaxed);
        }
        INNER.realloc(p, l, n)
    }
    unsafe fn dealloc(&self, p: *mut u8, l: Layout) {
        INNER.dealloc(p, l)
    }
}
#[cfg(sarext_counter)]
#[global_allocator]
static ALLOC: Count = Count;
#[cfg(not(sarext_counter))]
#[global_allocator]
static ALLOC: jemallocator::Jemalloc = jemallocator::Jemalloc;
extern "C" {
    fn TA_Initialize() -> i32;
    fn TA_GetVersionString() -> *const std::os::raw::c_char;
    fn TA_SAREXT_Lookback(a: f64, b: f64, c: f64, d: f64, e: f64, f: f64, g: f64, h: f64) -> i32;
    fn TA_SAREXT(
        s: i32,
        e: i32,
        high: *const f64,
        low: *const f64,
        a: f64,
        b: f64,
        c: f64,
        d: f64,
        f: f64,
        g: f64,
        h: f64,
        i: f64,
        beg: *mut i32,
        count: *mut i32,
        out: *mut f64,
    ) -> i32;
}
const CANARY: u64 = 0x7ff80000000055aa;
const KEYS: [&str; 8] = [
    "startvalue",
    "offsetonreverse",
    "accelerationinitlong",
    "accelerationlong",
    "accelerationmaxlong",
    "accelerationinitshort",
    "accelerationshort",
    "accelerationmaxshort",
];
const KERNEL: [&str; 4] = ["c081", "rust_typed", "rust_generic", "native_full"];
#[derive(Debug)]
struct Cli {
    fixture: String,
    n: usize,
    mode: String,
    input: String,
    pickle: String,
    capture: String,
    action: String,
    golden: Option<String>,
}
fn options(a: &[String]) -> Cli {
    assert!(
        a.len() == 8 || a.len() == 9,
        "fixture n mode input pickle capture --capture-only|--counter GOLDEN|--golden GOLDEN"
    );
    let n = a[2].parse().unwrap();
    let f = a[1].as_str();
    let m = a[3].as_str();
    let valid = if KERNEL.contains(&m) {
        ["default", "reversal"].contains(&f) && [100, 1000, 10000, 1000000].contains(&n)
    } else if ["decode_old", "decode_current"].contains(&m) {
        ["default", "reversal", "add"].contains(&f) && n == 0
    } else if ["setup_c", "setup_current"].contains(&m) {
        ["default", "reversal"].contains(&f) && n == 0
    } else {
        ["init_nan", "init_prefix"].contains(&m)
            && f == "init"
            && [100, 1000, 10000, 1000000].contains(&n)
    };
    assert!(valid, "fixed selected inventory only");
    let action = a[7].clone();
    let golden = if action == "--capture-only" {
        assert_eq!(a.len(), 8);
        None
    } else {
        assert!(["--golden", "--counter"].contains(&action.as_str()));
        assert_eq!(a.len(), 9);
        Some(a[8].clone())
    };
    assert!(
        !(cfg!(sarext_counter) && action == "--golden"),
        "counter binary cannot time"
    );
    assert!(
        !(!cfg!(sarext_counter) && action == "--counter"),
        "primary binary has no counter wrapper"
    );
    Cli {
        fixture: a[1].clone(),
        n,
        mode: a[3].clone(),
        input: a[4].clone(),
        pickle: a[5].clone(),
        capture: a[6].clone(),
        action,
        golden,
    }
}
fn iterations(c: &Cli) -> usize {
    if c.n == 0 {
        10000
    } else {
        match c.n {
            100 => 1000,
            1000 => 100,
            10000 => 10,
            1000000 => 1,
            _ => unreachable!(),
        }
    }
}
fn params(p: [f64; 8]) -> native::Params {
    KEYS.into_iter()
        .zip(p)
        .map(|(k, v)| (k.into(), native::Param::Real(v)))
        .collect()
}
fn old_words(x: &old_envelope::Masked<talib_original::overlap::SarExtKwargs>) -> Vec<u64> {
    let p = &x.params;
    let mut v = [
        p.startvalue,
        p.offsetonreverse,
        p.accelerationinitlong,
        p.accelerationlong,
        p.accelerationmaxlong,
        p.accelerationinitshort,
        p.accelerationshort,
        p.accelerationmaxshort,
    ]
    .map(f64::to_bits)
    .to_vec();
    v.extend([x.lookback as u64, x.recursive as u64]);
    v
}
fn new_words(x: &new_envelope::Masked<native::Params>) -> Vec<u64> {
    let mut v = KEYS
        .iter()
        .map(|k| match x.params.get(*k).unwrap() {
            native::Param::Real(v) => v.to_bits(),
            native::Param::Int(v) => (*v as f64).to_bits(),
        })
        .collect::<Vec<_>>();
    assert_eq!(x.params.len(), 8);
    v.extend([x.lookback as u64, x.recursive as u64]);
    v
}
fn read_input(c: &Cli) -> ([f64; 8], Vec<f64>, Vec<f64>) {
    let b = std::fs::read(&c.input).unwrap();
    assert_eq!(&b[..8], b"SARINPUT");
    let n = u64::from_le_bytes(b[8..16].try_into().unwrap()) as usize;
    assert_eq!(n, c.n);
    assert_eq!(b.len(), 80 + n * 16);
    let p =
        std::array::from_fn(|i| f64::from_le_bytes(b[16 + i * 8..24 + i * 8].try_into().unwrap()));
    let load = |start| {
        b[start..start + n * 8]
            .chunks_exact(8)
            .map(|x| f64::from_le_bytes(x.try_into().unwrap()))
            .collect()
    };
    {
        let h: Vec<f64> = load(80);
        let l: Vec<f64> = load(80 + n * 8);
        if n > 0 {
            assert!(h[..2].iter().chain(&l[..2]).all(|x| x.is_finite()));
        }
        (p, h, l)
    }
}
fn c_lb(p: &[f64; 8]) -> i32 {
    unsafe { TA_SAREXT_Lookback(p[0], p[1], p[2], p[3], p[4], p[5], p[6], p[7]) }
}
fn c_raw(
    h: &[f64],
    l: &[f64],
    p: &[f64; 8],
    s: usize,
    e: usize,
    out: &mut [f64],
) -> (i32, usize, usize) {
    assert!(s <= i32::MAX as usize && e <= i32::MAX as usize);
    let (mut b, mut n) = (0, 0);
    let ret = unsafe {
        TA_SAREXT(
            s as i32,
            e as i32,
            h.as_ptr(),
            l.as_ptr(),
            p[0],
            p[1],
            p[2],
            p[3],
            p[4],
            p[5],
            p[6],
            p[7],
            &mut b,
            &mut n,
            out.as_mut_ptr(),
        )
    };
    assert!(b >= 0 && n >= 0);
    (ret, b as usize, n as usize)
}
fn c_call(
    h: &[f64],
    l: &[f64],
    p: &[f64; 8],
    s: usize,
    e: usize,
    out: &mut [f64],
) -> Result<OutRange, i32> {
    let (code, beg_idx, count) = c_raw(h, l, p, s, e, out);
    if code == 0 {
        Ok(OutRange { beg_idx, count })
    } else {
        Err(code)
    }
}

fn typed(
    h: &[f64],
    l: &[f64],
    p: &[f64; 8],
    s: usize,
    e: usize,
    out: &mut [f64],
) -> Result<OutRange, ta_lib::RetCode> {
    native::core().sarext(
        s, e, h, l, p[0], p[1], p[2], p[3], p[4], p[5], p[6], p[7], out,
    )
}
enum State {
    Decode(Vec<u8>),
    Setup([f64; 8], Option<native::Params>),
    Kernel {
        p: [f64; 8],
        h: Vec<f64>,
        l: Vec<f64>,
        out: Vec<f64>,
        map: Option<native::Params>,
    },
    Full {
        inputs: [Series; 2],
        map: native::Params,
    },
    Init,
}
fn state(c: &Cli) -> State {
    if c.mode.starts_with("decode_") {
        return State::Decode(std::fs::read(&c.pickle).unwrap());
    }
    if c.mode.starts_with("init_") {
        return State::Init;
    }
    let (p, h, l) = read_input(c);
    if c.mode.starts_with("setup_") {
        return State::Setup(p, (c.mode == "setup_current").then(|| params(p)));
    }
    if c.mode == "native_full" {
        State::Full {
            inputs: [Series::from_vec("high", h), Series::from_vec("low", l)],
            map: params(p),
        }
    } else {
        State::Kernel {
            p,
            h,
            l,
            out: vec![f64::from_bits(CANARY); c.n + 8],
            map: (c.mode == "rust_generic").then(|| params(p)),
        }
    }
}
fn run(s: &mut State, c: &Cli) -> Option<Series> {
    match s {
        State::Decode(b) => {
            if c.fixture == "add" {
                if c.mode == "decode_old" {
                    black_box(
                        serde_pickle::from_slice::<old_envelope::Masked<old_envelope::NoParams>>(
                            black_box(b),
                            Default::default(),
                        )
                        .unwrap(),
                    );
                } else {
                    black_box(
                        serde_pickle::from_slice::<new_envelope::Masked<native::Params>>(
                            black_box(b),
                            Default::default(),
                        )
                        .unwrap(),
                    );
                }
            } else if c.mode == "decode_old" {
                black_box(
                    serde_pickle::from_slice::<
                        old_envelope::Masked<talib_original::overlap::SarExtKwargs>,
                    >(black_box(b), Default::default())
                    .unwrap(),
                );
            } else {
                black_box(
                    serde_pickle::from_slice::<new_envelope::Masked<native::Params>>(
                        black_box(b),
                        Default::default(),
                    )
                    .unwrap(),
                );
            }
            None
        }
        State::Setup(p, map) => {
            let lb = if c.mode == "setup_c" {
                c_lb(black_box(p)) as usize
            } else {
                let mut call = black_box(FuncId::SAREXT).new_call(native::core());
                native::bind_params(&mut call, black_box(map.as_ref().unwrap())).unwrap();
                call.lookback().unwrap()
            };
            assert_eq!(black_box(lb), 1);
            None
        }
        State::Kernel { p, h, l, out, map } => {
            let r = match c.mode.as_str() {
                "c081" => c_call(
                    black_box(h),
                    black_box(l),
                    black_box(p),
                    0,
                    c.n - 1,
                    black_box(out),
                )
                .unwrap(),
                "rust_typed" => typed(
                    black_box(h),
                    black_box(l),
                    black_box(p),
                    0,
                    c.n - 1,
                    black_box(out),
                )
                .unwrap(),
                "rust_generic" => {
                    let mut call = black_box(FuncId::SAREXT).new_call(native::core());
                    native::bind_params(&mut call, black_box(map.as_ref().unwrap())).unwrap();
                    call.set_price_input(
                        0,
                        None,
                        Some(black_box(h)),
                        Some(black_box(l)),
                        None,
                        None,
                        None,
                    )
                    .unwrap();
                    call.set_output(0, black_box(out)).unwrap();
                    call.call(0, c.n - 1).unwrap()
                }
                _ => unreachable!(),
            };
            assert_eq!((r.beg_idx, r.count), (1, c.n - 1));
            black_box(out);
            None
        }
        State::Full { inputs, map } => {
            let r = native::compute::<2, 1>(
                FuncId::SAREXT,
                black_box(inputs),
                black_box(map),
                &[0, 1],
                &[],
            )
            .unwrap();
            assert_eq!(r.len(), c.n);
            assert_eq!(r.null_count(), 0);
            Some(r)
        }
        State::Init => {
            let v = if c.mode == "init_nan" {
                vec![f64::NAN; black_box(c.n)]
            } else {
                let mut v = Vec::with_capacity(black_box(c.n));
                v.push(f64::NAN);
                v
            };
            black_box(v.as_slice());
            black_box(v);
            None
        }
    }
}
fn capture(s: &State, last: Option<&Series>, c: &Cli) -> Vec<u8> {
    let words = match s {
        State::Decode(b) => {
            if c.fixture == "add" {
                if c.mode == "decode_old" {
                    let v: old_envelope::Masked<old_envelope::NoParams> =
                        serde_pickle::from_slice(b, Default::default()).unwrap();
                    vec![v.lookback as u64, v.recursive as u64]
                } else {
                    let v: new_envelope::Masked<native::Params> =
                        serde_pickle::from_slice(b, Default::default()).unwrap();
                    assert!(v.params.is_empty());
                    vec![v.lookback as u64, v.recursive as u64]
                }
            } else if c.mode == "decode_old" {
                old_words(&serde_pickle::from_slice(b, Default::default()).unwrap())
            } else {
                new_words(&serde_pickle::from_slice(b, Default::default()).unwrap())
            }
        }
        State::Setup(p, map) => vec![if c.mode == "setup_c" {
            c_lb(p) as u64
        } else {
            let mut call = FuncId::SAREXT.new_call(native::core());
            native::bind_params(&mut call, map.as_ref().unwrap()).unwrap();
            call.lookback().unwrap() as u64
        }],
        State::Kernel { out, .. } => {
            assert!(out[c.n - 1..].iter().all(|v| v.to_bits() == CANARY));
            let mut v = vec![1, c.n as u64 - 1, f64::NAN.to_bits()];
            v.extend(out[..c.n - 1].iter().map(|x| x.to_bits()));
            v.extend([CANARY; 8]);
            v
        }
        State::Full { .. } => {
            let out = last.unwrap();
            let mut v = vec![1, c.n as u64 - 1];
            v.extend(
                out.f64()
                    .unwrap()
                    .cont_slice()
                    .unwrap()
                    .iter()
                    .map(|x| x.to_bits()),
            );
            v.extend([CANARY; 8]);
            v
        }
        State::Init => {
            let v = if c.mode == "init_nan" {
                vec![f64::NAN; c.n]
            } else {
                let mut v = Vec::with_capacity(c.n);
                v.push(f64::NAN);
                v
            };
            assert!(v.iter().all(|v| v.is_nan()));
            vec![v.len() as u64, v.capacity() as u64, v[0].to_bits()]
        }
    };
    let mut b = b"SARDIAG1".to_vec();
    b.extend_from_slice(&(words.len() as u64).to_le_bytes());
    for w in words {
        b.extend_from_slice(&w.to_le_bytes())
    }
    b
}
fn metadata() {
    let f = FuncId::SAREXT.info();
    assert_eq!(f.inputs.len(), 1);
    assert!(matches!(f.inputs[0].kind, InputType::Price));
    assert_eq!(f.inputs[0].flags.0, 6);
    assert_eq!(f.opt_inputs.len(), 8);
    assert_eq!(f.outputs.len(), 1);
    assert!(matches!(f.outputs[0].kind, OutputType::Real));
}
fn main() {
    if std::env::args().nth(1).as_deref() == Some("--ieee-contracts") {
        assert_eq!(std::env::args().count(), 2);
        assert_eq!(unsafe { TA_Initialize() }, 0);
        let v = unsafe { std::ffi::CStr::from_ptr(TA_GetVersionString()) }
            .to_str()
            .unwrap();
        assert!(v.starts_with("0.8.1 "));
        println!("C_VERSION {v}");
        ieee_contracts();
        return;
    }
    #[cfg(sarext_probe_contracts)]
    {
        contracts();
        return;
    }
    let c = options(&std::env::args().collect::<Vec<_>>());
    metadata();
    assert_eq!(unsafe { TA_Initialize() }, 0);
    let v = unsafe { std::ffi::CStr::from_ptr(TA_GetVersionString()) }
        .to_str()
        .unwrap();
    assert!(v.starts_with("0.8.1 "));
    println!("C_VERSION {v}");
    let mut s = state(&c);
    let last = run(&mut s, &c);
    let b = capture(&s, last.as_ref(), &c);
    drop(last);
    if let Some(g) = &c.golden {
        assert_eq!(
            std::fs::read(g).unwrap(),
            b,
            "selected golden before any warmup/timer"
        )
    }
    std::fs::write(&c.capture, &b).unwrap();
    drop(b);
    println!(
        "VALIDATE fixture={} mode={} n={} golden_verified={} physical_tail={}",
        c.fixture,
        c.mode,
        c.n,
        c.golden.is_some(),
        KERNEL.contains(&c.mode.as_str()) && c.mode != "native_full"
    );
    if c.action == "--capture-only" {
        return;
    }
    for _ in 0..5 {
        drop(black_box(run(&mut s, &c)))
    }
    #[cfg(sarext_counter)]
    {
        assert_eq!(c.action, "--counter");
        for v in &COUNTS {
            v.store(0, Ordering::Relaxed)
        }
        ENABLED.store(true, Ordering::Relaxed);
        drop(black_box(run(&mut s, &c)));
        ENABLED.store(false, Ordering::Relaxed);
        let counts = COUNTS.each_ref().map(|v| v.load(Ordering::Relaxed));
        println!("COUNTER counts={counts:?}");
        return;
    }
    #[cfg(not(sarext_counter))]
    {
        let iters = iterations(&c);
        let mut ns = Vec::with_capacity(31);
        for _ in 0..31 {
            let start = Instant::now();
            for _ in 0..iters {
                drop(black_box(run(&mut s, &c)))
            }
            ns.push(start.elapsed().as_nanos() as f64 / iters as f64)
        }
        let last = run(&mut s, &c);
        assert_eq!(
            std::fs::read(c.golden.as_ref().unwrap()).unwrap(),
            capture(&s, last.as_ref(), &c)
        );
        println!("PROBE iters={iters} warmups=5 samples={ns:?}");
    }
}
#[cfg(sarext_probe_contracts)]
fn contracts() {
    for mode in KERNEL {
        let a = ["p", "default", "100", mode, "i", "p", "o", "--capture-only"].map(String::from);
        assert!(options(&a).golden.is_none());
    }
    for (f, n, m) in [
        ("default", "0", "decode_old"),
        ("add", "0", "decode_current"),
        ("default", "0", "setup_current"),
        ("init", "1000", "init_prefix"),
    ] {
        let a = ["p", f, n, m, "i", "p", "o", "--counter", "g"].map(String::from);
        if cfg!(sarext_counter) {
            assert_eq!(options(&a).golden.as_deref(), Some("g"));
        } else {
            assert!(std::panic::catch_unwind(|| options(&a)).is_err());
        }
    }
    for (f, n, m) in [
        ("other", "100", "c081"),
        ("add", "100", "decode_old"),
        ("default", "100", "setup_c"),
        ("default", "1", "rust_typed"),
        ("default", "0", "init_prefix"),
    ] {
        let a = ["p", f, n, m, "i", "p", "o", "--capture-only"].map(String::from);
        assert!(std::panic::catch_unwind(|| options(&a)).is_err())
    }
    metadata();
    assert_eq!(
        compare_written(
            &[1., f64::NAN],
            &[1., f64::from_bits(0xfff8000000001234)],
            0,
            0,
            0,
            1
        ),
        1
    );
    assert_eq!(compare_written(&[], &[], 0, 0, 0, 0), 0);
    for (x, y) in [
        (1., f64::from_bits(1f64.to_bits() + 1)),
        (0., -0.),
        (f64::INFINITY, f64::NEG_INFINITY),
        (f64::INFINITY, 1.),
        (f64::NAN, 1.),
        (1., f64::NAN),
        (f64::NAN, f64::INFINITY),
    ] {
        assert!(std::panic::catch_unwind(|| compare_written(&[x], &[y], 0, 0, 0, 1)).is_err());
    }
    assert!(std::panic::catch_unwind(|| compare_written(
        &[f64::NAN, 1.],
        &[1., f64::NAN],
        0,
        0,
        0,
        1
    ))
    .is_err());
    assert!(std::panic::catch_unwind(|| compare_written(&[1.], &[], 0, 0, 0, 1)).is_err());
    for which in 0..2 {
        let mut a = [1., f64::from_bits(CANARY)];
        let mut b = a;
        if which == 0 {
            a[1] = f64::NAN
        } else {
            b[1] = f64::NAN
        }
        assert!(std::panic::catch_unwind(|| check_tails(&a, &b, 1)).is_err());
    }
    assert!(std::panic::catch_unwind(|| same_range(
        &OutRange {
            beg_idx: 1,
            count: 1
        },
        &OutRange {
            beg_idx: 2,
            count: 1
        }
    ))
    .is_err());
    assert!(std::panic::catch_unwind(|| same_range(
        &OutRange {
            beg_idx: 1,
            count: 1
        },
        &OutRange {
            beg_idx: 1,
            count: 2
        }
    ))
    .is_err());
    let timed = [
        "p",
        "default",
        "100",
        "rust_typed",
        "i",
        "p",
        "o",
        "--golden",
        "g",
    ]
    .map(String::from);
    if cfg!(sarext_counter) {
        assert!(std::panic::catch_unwind(|| options(&timed)).is_err())
    } else {
        assert_eq!(options(&timed).golden.as_deref(), Some("g"));
    }
    println!("SAREXT_CLI_CONTRACTS PASS");
}

fn ieee_contracts() {
    metadata();
    let mut comparisons = 0;
    let mut nan_differences = 0;
    let mut full_checks = 0;
    let mut errors = 0;
    for p in [
        [0., 0., 0.02, 0.02, 0.2, 0.02, 0.02, 0.2],
        [-101., 0.05, 0.03, 0.04, 0.3, 0.025, 0.035, 0.25],
    ] {
        for shape in 0..10 {
            let mut h = (0..64)
                .map(|i| 100. + ((i % 8) as f64 - 4.) * 10. + 1.)
                .collect::<Vec<_>>();
            let mut l = h.iter().map(|v| v - 2.).collect::<Vec<_>>();
            let x = match shape {
                0 => None,
                1 => Some(f64::NAN),
                2 => Some(f64::INFINITY),
                3 => Some(f64::NEG_INFINITY),
                4 => Some(0.),
                5 => Some(-0.),
                6 => Some(f64::MAX),
                7 => Some(-f64::MAX),
                8 => Some(f64::from_bits(0x7ff8000000001234)),
                _ => Some(f64::MIN_POSITIVE),
            };
            if let Some(x) = x {
                h[9] = x;
                l[13] = x;
            }
            for (s, e) in [(0, 63), (1, 63), (7, 31), (0, 0), (0, 1)] {
                let mut a = vec![f64::from_bits(CANARY); 72];
                let mut b = a.clone();
                let ar = c_call(&h, &l, &p, s, e, &mut a).unwrap();
                let br = typed(&h, &l, &p, s, e, &mut b).unwrap();
                same_range(&ar, &br);
                let nan_count =
                    compare_written(&a[..ar.count], &b[..br.count], p[0].to_bits(), shape, s, e);
                nan_differences += nan_count;
                check_tails(&a, &b, ar.count);
                println!("IEEE_ROW pstart={:016x} shape={shape} start={s} end={e} beg={} count={} nan_bit_differences={nan_count}",p[0].to_bits(),ar.beg_idx,ar.count);
                comparisons += 1;
                if s == 0 && e == 63 {
                    let inputs = [
                        Series::from_vec("h", h.clone()),
                        Series::from_vec("l", l.clone()),
                    ];
                    let full =
                        native::compute::<2, 1>(FuncId::SAREXT, &inputs, &params(p), &[0, 1], &[])
                            .unwrap();
                    let f = full.f64().unwrap().cont_slice().unwrap();
                    assert_eq!(f.len(), 64);
                    assert_eq!(f[0].to_bits(), f64::NAN.to_bits());
                    assert_eq!(
                        f[1..].iter().map(|v| v.to_bits()).collect::<Vec<_>>(),
                        b[..63].iter().map(|v| v.to_bits()).collect::<Vec<_>>()
                    );
                    full_checks += 1;
                }
            }
        }
        for i in 0..8 {
            for value in [f64::NAN, f64::INFINITY, f64::NEG_INFINITY] {
                let mut bad = p;
                bad[i] = value;
                let mut out = vec![f64::from_bits(CANARY); 72];
                assert!(matches!(
                    typed(&[101.; 64], &[99.; 64], &bad, 0, 63, &mut out),
                    Err(ta_lib::RetCode::BadParam)
                ));
                assert!(out.iter().all(|v| v.to_bits() == CANARY));
                let mut c_out = vec![f64::from_bits(CANARY); 72];
                let (code, beg, count) = c_raw(&[101.; 64], &[99.; 64], &bad, 0, 63, &mut c_out);
                if code == 0 {
                    assert_eq!((beg, count), (1, 63));
                } else {
                    assert_eq!((beg, count), (0, 0));
                }
                assert!(c_out[count..].iter().all(|v| v.to_bits() == CANARY));
                let bits = c_out.iter().map(|v| v.to_bits()).collect::<Vec<_>>();
                println!("OPTION_C_RESULT pstart={:016x} option={i} value_bits={:016x} code={code} beg={beg} count={count} core=BadParam raw_bits={bits:?}",p[0].to_bits(),value.to_bits());
                errors += 1;
            }
        }
        for i in 1..8 {
            let mut bad = p;
            bad[i] = -1.;
            let mut a = vec![f64::from_bits(CANARY); 72];
            let mut b = a.clone();
            assert!(c_call(&[101.; 64], &[99.; 64], &bad, 0, 63, &mut a).is_err());
            assert!(typed(&[101.; 64], &[99.; 64], &bad, 0, 63, &mut b).is_err());
            assert!(a.iter().chain(&b).all(|v| v.to_bits() == CANARY));
            errors += 1;
        }
        for n in [0, 1, 62] {
            let mut out = vec![f64::from_bits(CANARY); n];
            assert!(typed(&[101.; 64], &[99.; 64], &p, 0, 63, &mut out).is_err());
            assert!(out.iter().all(|v| v.to_bits() == CANARY));
            errors += 1;
        }
    }
    assert_eq!((comparisons, full_checks, errors), (100, 20, 68));
    println!("IEEE_CONTRACTS comparisons={comparisons} full={full_checks} invalid_no_writes={errors} nan_bit_differences={nan_differences} policy=nan_positions_other_bits_exact nonfinite_options_observed=48");
}

// Migration policy: NaN positions match; every non-NaN bit (including zero/Inf sign) matches.
// This helper is ONLY for successfully written cross-language prefixes, never tails/full Rust.
fn compare_written(a: &[f64], b: &[f64], pstart: u64, shape: usize, s: usize, e: usize) -> usize {
    assert_eq!(a.len(), b.len());
    let mut differences = 0;
    for (i, (x, y)) in a.iter().zip(b).enumerate() {
        if x.to_bits() == y.to_bits() {
            continue;
        }
        assert!(x.is_nan()&&y.is_nan(),"non-NaN IEEE difference pstart={pstart:016x} shape={shape} start={s} end={e} index={i} c={:016x} rust={:016x}",x.to_bits(),y.to_bits());
        println!("IEEE_NAN_DIFF pstart={pstart:016x} shape={shape} start={s} end={e} index={i} c_bits={:016x} rust_bits={:016x}",x.to_bits(),y.to_bits());
        differences += 1;
    }
    differences
}

fn same_range(a: &OutRange, b: &OutRange) {
    assert_eq!((a.beg_idx, a.count), (b.beg_idx, b.count));
}
fn check_tails(a: &[f64], b: &[f64], count: usize) {
    assert_eq!(a.len(), b.len());
    assert!(a[count..].iter().all(|v| v.to_bits() == CANARY));
    assert!(b[count..].iter().all(|v| v.to_bits() == CANARY));
    if count == 0 {
        assert_eq!(
            a.iter().map(|v| v.to_bits()).collect::<Vec<_>>(),
            b.iter().map(|v| v.to_bits()).collect::<Vec<_>>()
        );
    }
}
