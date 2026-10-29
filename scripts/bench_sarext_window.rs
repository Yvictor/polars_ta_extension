//! Fixed selected public kernel. Unsafe is confined to valid-buffer C FFI.
use std::{env, fs, hint::black_box, io::Write, time::Instant};
#[cfg(not(c_reference))]
use ta_lib::{
    abstract_api::{FuncId, InputType, OutputType},
    Core, RetCode,
};
const CANARY: u64 = 0x7ff8_0000_0000_55aa;
const EDGES: [(usize, usize); 10] = [
    (0, 0),
    (0, 1),
    (0, 2),
    (1, 5),
    (2, 5),
    (3, 10),
    (17, 63),
    (42, 48),
    (63, 63),
    (0, 63),
];
const IEEE_SHAPES: usize = 17;
#[cfg(c_reference)]
extern "C" {
    fn TA_Initialize() -> i32;
    fn TA_GetVersionString() -> *const std::os::raw::c_char;
    fn TA_SAR(
        s: i32,
        e: i32,
        h: *const f64,
        l: *const f64,
        a: f64,
        m: f64,
        b: *mut i32,
        n: *mut i32,
        out: *mut f64,
    ) -> i32;
    fn TA_SAREXT(
        s: i32,
        e: i32,
        h: *const f64,
        l: *const f64,
        p0: f64,
        p1: f64,
        p2: f64,
        p3: f64,
        p4: f64,
        p5: f64,
        p6: f64,
        p7: f64,
        b: *mut i32,
        n: *mut i32,
        out: *mut f64,
    ) -> i32;
    fn TA_ADD(
        s: i32,
        e: i32,
        a: *const f64,
        b: *const f64,
        beg: *mut i32,
        n: *mut i32,
        out: *mut f64,
    ) -> i32;
}
#[derive(Clone, Debug)]
struct Opt {
    indicator: String,
    fixture: String,
    n: usize,
    iters: usize,
    input: String,
    capture: String,
    golden: Option<String>,
}
impl Opt {
    fn params(&self) -> [f64; 8] {
        if self.fixture == "reversal" {
            [-101., 0.05, 0.03, 0.04, 0.3, 0.025, 0.035, 0.25]
        } else {
            [0., 0., 0.02, 0.02, 0.2, 0.02, 0.02, 0.2]
        }
    }
}
fn options(a: &[String]) -> Opt {
    assert!(
        a.len() == 9 || a.len() == 10,
        "indicator fixture typed n iterations input capture --capture-only | --golden PATH"
    );
    assert!(["sar", "sarext", "add"].contains(&a[1].as_str()));
    assert!(["default", "reversal"].contains(&a[2].as_str()));
    assert!(a[1] != "add" || a[2] == "default");
    assert_eq!(a[3], "typed");
    let n = a[4].parse().unwrap();
    let iters = a[5].parse().unwrap();
    assert_eq!(
        iters,
        match n {
            100 => 1000,
            10000 => 10,
            1000000 => 1,
            _ => panic!("fixed sizes"),
        }
    );
    let golden = if a.len() == 9 {
        assert_eq!(a[8], "--capture-only");
        None
    } else {
        assert_eq!(a[8], "--golden");
        Some(a[9].clone())
    };
    assert_ne!(golden.as_deref(), Some(a[7].as_str()));
    Opt {
        indicator: a[1].clone(),
        fixture: a[2].clone(),
        n,
        iters,
        input: a[6].clone(),
        capture: a[7].clone(),
        golden,
    }
}
fn load(o: &Opt) -> [Vec<f64>; 4] {
    let d = fs::read(&o.input).unwrap();
    assert!(d.len() >= 24);
    assert_eq!(&d[..8], b"SARDATA1");
    let n = u64::from_le_bytes(d[8..16].try_into().unwrap()) as usize;
    let z = u64::from_le_bytes(d[16..24].try_into().unwrap()) as usize;
    assert_eq!(n, o.n);
    assert_eq!(z, o.fixture.len());
    assert_eq!(&d[24..24 + z], o.fixture.as_bytes());
    let d = &d[24 + z..];
    assert_eq!(d.len(), 4 * n * 8);
    let values = std::array::from_fn(|i| {
        d[i * n * 8..(i + 1) * n * 8]
            .chunks_exact(8)
            .map(|x| f64::from_le_bytes(x.try_into().unwrap()))
            .collect::<Vec<_>>()
    });
    assert!(values.iter().all(|v| v.iter().all(|x| x.is_finite())));
    values
}
fn hardware_fma() -> bool {
    #[cfg(target_arch = "x86_64")]
    {
        std::arch::is_x86_feature_detected!("fma")
    }
    #[cfg(not(target_arch = "x86_64"))]
    {
        false
    }
}
struct Engine {
    #[cfg(not(c_reference))]
    core: Core,
}
impl Engine {
    fn new() -> Self {
        #[cfg(c_reference)]
        {
            assert_eq!(unsafe { TA_Initialize() }, 0);
            let v = unsafe { std::ffi::CStr::from_ptr(TA_GetVersionString()) }
                .to_str()
                .unwrap();
            assert!(v.starts_with("0.8.3 "));
            Self {}
        }
        #[cfg(not(c_reference))]
        {
            Self { core: Core::new() }
        }
    }
    fn lb(ind: &str) -> usize {
        if ind == "add" {
            0
        } else {
            1
        }
    }
    fn metadata(&self, o: &Opt) {
        #[cfg(not(c_reference))]
        {
            let id = match o.indicator.as_str() {
                "sar" => FuncId::SAR,
                "sarext" => FuncId::SAREXT,
                _ => FuncId::ADD,
            };
            let info = id.info();
            assert_eq!(info.outputs.len(), 1);
            assert!(matches!(info.outputs[0].kind, OutputType::Real));
            if o.indicator == "add" {
                assert_eq!(info.inputs.len(), 2);
                assert!(info
                    .inputs
                    .iter()
                    .all(|i| matches!(i.kind, InputType::Real)));
            } else {
                assert_eq!(info.inputs.len(), 1);
                assert!(matches!(info.inputs[0].kind, InputType::Price));
                assert_eq!(info.inputs[0].flags.0, 6);
            }
            let p = o.params();
            let lb = match o.indicator.as_str() {
                "sar" => self.core.sar_lookback(p[3], p[4]),
                "sarext" => self
                    .core
                    .sarext_lookback(p[0], p[1], p[2], p[3], p[4], p[5], p[6], p[7]),
                _ => self.core.add_lookback(),
            };
            assert_eq!(lb.unwrap(), Self::lb(&o.indicator));
        }
        #[cfg(c_reference)]
        {
            let _ = o;
        }
    }
    fn run(
        &self,
        o: &Opt,
        v: [&[f64]; 4],
        s: usize,
        e: usize,
        p: [f64; 8],
        out: &mut [f64],
    ) -> Result<(usize, usize), i32> {
        #[cfg(c_reference)]
        {
            // C has no length contract. Reject only in the driver, never call it
            // with short inputs/output; index-error probes use allocated64 bars.
            assert!(v.iter().all(|x| x.len() == v[0].len()));
            assert!(out.len() >= v[0].len());
            assert!(e == usize::MAX || e < v[0].len());
            let (mut b, mut n) = (0, 0);
            let s = if s == usize::MAX {
                -1
            } else {
                i32::try_from(s).unwrap()
            };
            let e = if e == usize::MAX {
                -1
            } else {
                i32::try_from(e).unwrap()
            };
            let code = unsafe {
                match o.indicator.as_str() {
                    "sar" => TA_SAR(
                        s,
                        e,
                        v[1].as_ptr(),
                        v[2].as_ptr(),
                        p[3],
                        p[4],
                        &mut b,
                        &mut n,
                        out.as_mut_ptr(),
                    ),
                    "sarext" => TA_SAREXT(
                        s,
                        e,
                        v[1].as_ptr(),
                        v[2].as_ptr(),
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
                    ),
                    _ => TA_ADD(
                        s,
                        e,
                        v[0].as_ptr(),
                        v[3].as_ptr(),
                        &mut b,
                        &mut n,
                        out.as_mut_ptr(),
                    ),
                }
            };
            if code != 0 {
                assert_eq!((b, n), (0, 0));
                Err(code)
            } else {
                assert!(b >= 0 && n >= 0);
                Ok((b as usize, n as usize))
            }
        }
        #[cfg(not(c_reference))]
        {
            let r = match o.indicator.as_str() {
                "sar" => self.core.sar(s, e, v[1], v[2], p[3], p[4], out),
                "sarext" => self.core.sarext(
                    s, e, v[1], v[2], p[0], p[1], p[2], p[3], p[4], p[5], p[6], p[7], out,
                ),
                _ => self.core.add(s, e, v[0], v[3], out),
            };
            r.map(|x| (x.beg_idx, x.count)).map_err(|x| x as i32)
        }
    }
}
fn expected(o: &Opt, s: usize, e: usize) -> (usize, usize) {
    let b = s.max(Engine::lb(&o.indicator));
    if b > e {
        (0, 0)
    } else {
        (b, e - b + 1)
    }
}
fn poison(n: usize) -> Vec<f64> {
    vec![f64::from_bits(CANARY); n]
}
fn record(n: usize, (b, c): (usize, usize), out: &[f64]) -> Vec<u8> {
    assert_eq!(out.len(), n + 8);
    assert!(b + c <= n);
    assert!(out[c..].iter().all(|x| x.to_bits() == CANARY));
    let mut d = Vec::with_capacity(8 * n + 96);
    d.extend_from_slice(b"SAROUT01");
    for x in [n, b, c] {
        d.extend_from_slice(&(x as u64).to_le_bytes());
    }
    for x in out {
        d.extend_from_slice(&x.to_bits().to_le_bytes());
    }
    assert_eq!(d.len(), 8 * n + 96);
    d
}
fn ieee(shape: usize) -> [Vec<f64>; 4] {
    let mut v: [Vec<f64>; 4] = std::array::from_fn(|i| {
        (0..64)
            .map(|j| 100. + (j % 7) as f64 + (i as f64 - 1.) * 0.1)
            .collect()
    });
    for j in 0..64 {
        v[1][j] = v[3][j] + 1.;
        v[2][j] = v[3][j] - 1.;
    }
    match shape {
        0 => {}
        1 => {
            for x in &mut v {
                x.fill(100.);
            }
        }
        2 => {
            for x in &mut v {
                x.fill(0.);
            }
        }
        3 => {
            for x in &mut v {
                x.fill(-0.);
            }
        }
        4 => {
            for x in &mut v {
                for (j, z) in x.iter_mut().enumerate() {
                    *z = if j % 2 == 0 { -0. } else { 0. };
                }
            }
        }
        5..=8 => {
            v[1][[0, 1, 17, 63][shape - 5]] = f64::from_bits(0x7ff8_0000_0000_0123);
        }
        9..=12 => {
            v[2][[0, 1, 17, 63][shape - 9]] = f64::from_bits(0xfff8_0000_0000_0456);
        }
        13 => {
            v[1][17] = f64::INFINITY;
            v[2][31] = f64::NEG_INFINITY;
        }
        14 => {
            for j in 0..64 {
                v[1][j] = if j % 2 == 0 {
                    f64::INFINITY
                } else {
                    f64::NEG_INFINITY
                };
                v[2][j] = -v[1][j];
            }
        }
        15 => {
            for j in 0..64 {
                v[1][j] = 1e308;
                v[2][j] = -1e308;
                v[0][j] = 1e308;
                v[3][j] = 1e308;
            }
        }
        16 => {
            // Published zero-sign boundary: API accepts inverted high/low.
            let low = [
                101., 100., 101., 96., 105., 95., 108., 91., 100., 99., 103., 98., 103., 94., 107.,
                93., 102., 97., 102., 97., 105., 96., 105., 92., 101., 99., 104., 95., 104., 95.,
                107., 94., 99., 98., 103., 97., 106., 93., 106., 93.,
            ];
            v[1].fill(0.);
            for j in 0..64 {
                v[2][j] = low[j % low.len()];
            }
        }
        _ => panic!("fixed IEEE shapes"),
    }
    v
}
fn capture_edges(en: &Engine, o: &Opt, values: &[Vec<f64>; 4]) -> (Vec<u8>, usize, usize) {
    let mut d = Vec::new();
    let p = o.params();
    // Fixture prefix first, then all17 IEEE patterns; every ten-range record
    // retains the physical unwritten tail, including zero-count calls.
    for pattern in 0..=IEEE_SHAPES {
        let owned;
        if pattern == 0 {
            owned = std::array::from_fn(|i| values[i][..64].to_vec());
        } else {
            owned = ieee(pattern - 1);
        }
        let v = std::array::from_fn(|i| owned[i].as_slice());
        for (s, e) in EDGES {
            let mut out = poison(72);
            let got = en.run(o, v, s, e, p, &mut out).unwrap();
            assert_eq!(got, expected(o, s, e));
            d.extend(record(64, got, &out));
        }
    }
    let v = std::array::from_fn(|i| &values[i][..64]);
    for (s, e, code) in [(10, 9, 13), (usize::MAX, 63, 12), (0, usize::MAX, 13)] {
        let mut out = poison(72);
        assert_eq!(en.run(o, v, s, e, p, &mut out), Err(code));
        assert!(out.iter().all(|x| x.to_bits() == CANARY));
    }
    let positions: &[usize] = match o.indicator.as_str() {
        "sar" => &[3, 4],
        "sarext" => &[0, 1, 2, 3, 4, 5, 6, 7],
        _ => &[],
    };
    let mut errors = 0;
    for &i in positions {
        for invalid in [f64::NAN, f64::INFINITY, f64::NEG_INFINITY] {
            let mut q = p;
            q[i] = invalid;
            let mut out = poison(72);
            assert_eq!(en.run(o, v, 0, 63, q, &mut out), Err(2));
            assert!(out.iter().all(|x| x.to_bits() == CANARY));
            errors += 1;
        }
    }
    #[cfg(not(c_reference))]
    {
        let consumed: &[usize] = if o.indicator == "add" {
            &[0, 3]
        } else {
            &[1, 2]
        };
        for &i in consumed {
            let mut short = v;
            short[i] = &v[i][..63];
            let mut out = poison(72);
            assert_eq!(
                en.run(o, short, 0, 63, p, &mut out),
                Err(RetCode::BadParam as i32)
            );
            assert!(out.iter().all(|x| x.to_bits() == CANARY));
        }
        let mut out = poison(72);
        assert_eq!(
            en.run(o, v, 0, 63, p, &mut out[..1]),
            Err(RetCode::BadParam as i32)
        );
        assert!(out.iter().all(|x| x.to_bits() == CANARY));
    }
    (d, errors, if cfg!(c_reference) { 0 } else { 3 })
}
fn write_capture(path: &str, data: &[u8]) {
    let mut f = fs::OpenOptions::new()
        .write(true)
        .create_new(true)
        .open(path)
        .unwrap();
    f.write_all(data).unwrap();
}
fn main() {
    let o = options(&env::args().collect::<Vec<_>>());
    let en = Engine::new();
    en.metadata(&o);
    let values = load(&o);
    let v = std::array::from_fn(|i| values[i].as_slice());
    let p = o.params();
    let mut out = poison(o.n + 8);
    let got = en.run(&o, v, 0, o.n - 1, p, &mut out).unwrap();
    assert_eq!(got, expected(&o, 0, o.n - 1));
    let selected = record(o.n, got, &out);
    if o.golden.is_none() {
        let (mut d, param_errors, short_checks) = capture_edges(&en, &o, &values);
        d.extend(selected);
        write_capture(&o.capture, &d);
        println!("{{\"kind\":\"capture\",\"indicator\":{:?},\"fixture\":{:?},\"mode\":\"typed\",\"n\":{},\"edge_records\":180,\"range_errors\":3,\"parameter_errors\":{},\"short_checks\":{},\"hardware_fma\":{},\"timed\":false}}",o.indicator,o.fixture,o.n,param_errors,short_checks,hardware_fma());
        return;
    }
    write_capture(&o.capture, &selected);
    assert_eq!(selected, fs::read(o.golden.as_ref().unwrap()).unwrap());
    drop(selected);
    println!("{{\"kind\":\"validation\",\"indicator\":{:?},\"fixture\":{:?},\"mode\":\"typed\",\"n\":{},\"beg\":{},\"count\":{},\"golden_verified\":true,\"hardware_fma\":{}}}",o.indicator,o.fixture,o.n,got.0,got.1,hardware_fma());
    for _ in 0..5 {
        black_box(en.run(&o, v, 0, o.n - 1, p, &mut out).unwrap());
    }
    let mut samples = Vec::with_capacity(31);
    for _ in 0..31 {
        let t = Instant::now();
        for _ in 0..o.iters {
            let r = en
                .run(
                    black_box(&o),
                    black_box(v),
                    0,
                    o.n - 1,
                    black_box(p),
                    black_box(&mut out),
                )
                .unwrap();
            assert_eq!(r, got);
            black_box(&out[..r.1]);
        }
        samples.push(t.elapsed().as_nanos() as f64 / o.iters as f64);
    }
    let last = en.run(&o, v, 0, o.n - 1, p, &mut out).unwrap();
    assert_eq!(
        record(o.n, last, &out),
        fs::read(o.golden.as_ref().unwrap()).unwrap()
    );
    println!("{{\"kind\":\"case\",\"indicator\":{:?},\"fixture\":{:?},\"mode\":\"typed\",\"n\":{},\"iterations\":{},\"warmups\":5,\"samples_ns\":{:?}}}",o.indicator,o.fixture,o.n,o.iters,samples);
}
#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn cli_selected_only() {
        let a = |v: &[&str]| v.iter().map(|x| x.to_string()).collect::<Vec<_>>();
        assert!(options(&a(&[
            "p",
            "sar",
            "default",
            "typed",
            "100",
            "1000",
            "input",
            "out",
            "--capture-only"
        ]))
        .golden
        .is_none());
        for v in [
            vec![
                "p",
                "sar",
                "default",
                "abstract",
                "100",
                "1000",
                "input",
                "out",
                "--capture-only",
            ],
            vec![
                "p",
                "add",
                "reversal",
                "typed",
                "100",
                "1000",
                "input",
                "out",
                "--capture-only",
            ],
            vec![
                "p",
                "sar",
                "default",
                "typed",
                "101",
                "1000",
                "input",
                "out",
                "--capture-only",
            ],
            vec![
                "p", "sar", "default", "typed", "100", "1000", "input", "out", "--golden", "out",
            ],
        ] {
            assert!(std::panic::catch_unwind(|| options(&a(&v))).is_err());
        }
    }
    #[test]
    fn tail_nan_payload_not_relaxed() {
        let mut out = poison(108);
        out[..99].fill(0.);
        assert_eq!(record(100, (1, 99), &out).len(), 896);
        out[107] = f64::NAN;
        assert!(std::panic::catch_unwind(|| record(100, (1, 99), &out)).is_err());
    }
    #[test]
    fn all_ieee_shapes_are_distinct() {
        let arrays: Vec<_> = (0..IEEE_SHAPES)
            .map(|s| {
                ieee(s)
                    .iter()
                    .flat_map(|v| v.iter().map(|x| x.to_bits()))
                    .collect::<Vec<_>>()
            })
            .collect();
        for (i, a) in arrays.iter().enumerate() {
            assert!(arrays[..i].iter().all(|b| a != b));
        }
    }
}
