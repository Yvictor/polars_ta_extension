//! Selected upstream kernel; C mode labels both call the direct public C API.
use std::{env, fs, hint::black_box, io::Write, time::Instant};
#[cfg(not(c_reference))]
use ta_lib::{
    abstract_api::{FuncId, InputType, OutputType},
    Core, RetCode,
};
const CANARY: i32 = 0x5a5a5a5a;
const EDGES: [(usize, usize); 9] = [
    (0, 0),
    (0, 1),
    (0, 2),
    (1, 5),
    (2, 5),
    (3, 10),
    (17, 63),
    (42, 48),
    (63, 63),
];
#[cfg(c_reference)]
extern "C" {
    fn TA_Initialize() -> i32;
    fn TA_GetVersionString() -> *const std::os::raw::c_char;
    fn TA_CDLENGULFING(
        s: i32,
        e: i32,
        o: *const f64,
        h: *const f64,
        l: *const f64,
        c: *const f64,
        b: *mut i32,
        n: *mut i32,
        out: *mut i32,
    ) -> i32;
    fn TA_CDLDOJI(
        s: i32,
        e: i32,
        o: *const f64,
        h: *const f64,
        l: *const f64,
        c: *const f64,
        b: *mut i32,
        n: *mut i32,
        out: *mut i32,
    ) -> i32;
}
#[derive(Debug)]
struct Opt {
    indicator: String,
    fixture: String,
    mode: String,
    n: usize,
    iters: usize,
    input: String,
    capture: String,
    golden: Option<String>,
}
fn options(a: &[String]) -> Opt {
    assert!(
        a.len() == 9 || a.len() == 10,
        "indicator fixture mode n iterations input capture --capture-only | --golden PATH"
    );
    assert!(["engulf", "doji"].contains(&a[1].as_str()));
    assert!(["white", "alternating", "equality_ieee"].contains(&a[2].as_str()));
    assert!(["typed", "abstract"].contains(&a[3].as_str()));
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
        mode: a[3].clone(),
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
    assert_eq!(&d[..8], b"ENGDATA1");
    let n = u64::from_le_bytes(d[8..16].try_into().unwrap()) as usize;
    let z = u64::from_le_bytes(d[16..24].try_into().unwrap()) as usize;
    assert_eq!(n, o.n);
    assert_eq!(z, o.fixture.len());
    assert_eq!(&d[24..24 + z], o.fixture.as_bytes());
    let d = &d[24 + z..];
    assert_eq!(d.len(), 4 * n * 8);
    let v: [Vec<f64>; 4] = std::array::from_fn(|i| {
        d[i * n * 8..(i + 1) * n * 8]
            .chunks_exact(8)
            .map(|x| f64::from_le_bytes(x.try_into().unwrap()))
            .collect()
    });
    assert!(v.iter().all(|x| x[..2].iter().all(|x| x.is_finite())));
    v
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
            assert!(v.starts_with("0.8.1 "));
            Self {}
        }
        #[cfg(not(c_reference))]
        {
            Self { core: Core::new() }
        }
    }
    fn lb(indicator: &str) -> usize {
        if indicator == "engulf" {
            2
        } else {
            10
        }
    }
    fn metadata(&self, o: &Opt) {
        #[cfg(not(c_reference))]
        {
            let id = if o.indicator == "engulf" {
                FuncId::CDLENGULFING
            } else {
                FuncId::CDLDOJI
            };
            let f = id.info();
            assert_eq!(f.inputs.len(), 1);
            assert!(matches!(f.inputs[0].kind, InputType::Price));
            assert_eq!(f.inputs[0].flags.0, 15);
            assert_eq!(f.outputs.len(), 1);
            assert!(matches!(f.outputs[0].kind, OutputType::Integer));
            let lookback = if o.mode == "typed" {
                if o.indicator == "engulf" {
                    self.core.cdlengulfing_lookback()
                } else {
                    self.core.cdldoji_lookback()
                }
            } else {
                id.new_call(&self.core).lookback()
            };
            assert_eq!(lookback.unwrap(), Self::lb(&o.indicator));
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
        out: &mut [i32],
    ) -> Result<(usize, usize), i32> {
        #[cfg(c_reference)]
        {
            // Only fixed, disjoint, sufficiently sized buffers reach the C pointers.
            assert!(v.iter().all(|x| x.len() == v[0].len()));
            assert!(out.len() >= v[0].len());
            let mut b = -777;
            let mut n = -888;
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
            let rc = unsafe {
                if o.indicator == "engulf" {
                    TA_CDLENGULFING(
                        s,
                        e,
                        v[0].as_ptr(),
                        v[1].as_ptr(),
                        v[2].as_ptr(),
                        v[3].as_ptr(),
                        &mut b,
                        &mut n,
                        out.as_mut_ptr(),
                    )
                } else {
                    TA_CDLDOJI(
                        s,
                        e,
                        v[0].as_ptr(),
                        v[1].as_ptr(),
                        v[2].as_ptr(),
                        v[3].as_ptr(),
                        &mut b,
                        &mut n,
                        out.as_mut_ptr(),
                    )
                }
            };
            if rc != 0 {
                assert_eq!((b, n), (-777, -888));
                Err(rc)
            } else {
                assert!(b >= 0 && n >= 0);
                Ok((b as usize, n as usize))
            }
        }
        #[cfg(not(c_reference))]
        {
            let id = if o.indicator == "engulf" {
                FuncId::CDLENGULFING
            } else {
                FuncId::CDLDOJI
            };
            let r = if o.mode == "typed" {
                if o.indicator == "engulf" {
                    self.core.cdlengulfing(s, e, v[0], v[1], v[2], v[3], out)
                } else {
                    self.core.cdldoji(s, e, v[0], v[1], v[2], v[3], out)
                }
            } else {
                let mut h = id.new_call(&self.core);
                h.set_price_input(
                    0,
                    Some(v[0]),
                    Some(v[1]),
                    Some(v[2]),
                    Some(v[3]),
                    None,
                    None,
                )
                .unwrap();
                h.set_int_output(0, out).unwrap();
                h.call(s, e)
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
fn record(n: usize, (b, c): (usize, usize), out: &[i32]) -> Vec<u8> {
    assert!(b + c <= n);
    assert!(out[c..].iter().all(|&x| x == CANARY));
    let mut d = Vec::with_capacity(4 * n + 64);
    d.extend_from_slice(b"ENGOUT01");
    for x in [n, b, c] {
        d.extend_from_slice(&(x as u64).to_le_bytes());
    }
    for _ in 0..b {
        d.extend_from_slice(&0i32.to_le_bytes());
    }
    for x in &out[..c] {
        assert!([-100, -80, 0, 80, 100].contains(x));
        d.extend_from_slice(&x.to_le_bytes());
    }
    for _ in b + c..n + 8 {
        d.extend_from_slice(&CANARY.to_le_bytes());
    }
    assert_eq!(d.len(), 4 * n + 64);
    d
}
fn edges(en: &Engine, o: &Opt, values: &[Vec<f64>; 4]) -> Vec<u8> {
    let v = std::array::from_fn(|i| &values[i][..64]);
    let mut d = Vec::new();
    for (s, e) in EDGES {
        let mut out = vec![CANARY; 72];
        let r = en.run(o, v, s, e, &mut out).unwrap();
        assert_eq!(r, expected(o, s, e));
        d.extend(record(64, r, &out));
    }
    for (s, e, code) in [(10, 9, 13), (usize::MAX, 63, 12), (0, usize::MAX, 13)] {
        let mut out = vec![CANARY; 72];
        assert_eq!(en.run(o, v, s, e, &mut out), Err(code));
        assert!(out.iter().all(|&x| x == CANARY));
    }
    #[cfg(not(c_reference))]
    {
        for slot in 0..4 {
            let mut short = v;
            short[slot] = &v[slot][..63];
            let mut out = vec![CANARY; 72];
            assert_eq!(
                en.run(o, short, 0, 63, &mut out),
                Err(RetCode::BadParam as i32)
            );
            assert!(out.iter().all(|&x| x == CANARY));
        }
        let mut out = vec![CANARY; 72];
        assert_eq!(
            en.run(o, v, 0, 63, &mut out[..1]),
            Err(RetCode::BadParam as i32)
        );
        assert!(out.iter().all(|&x| x == CANARY));
    }
    d
}
fn write_capture(path: &str, data: &[u8]) {
    let mut file = fs::OpenOptions::new()
        .write(true)
        .create_new(true)
        .open(path)
        .unwrap();
    file.write_all(data).unwrap();
}
fn main() {
    let o = options(&env::args().collect::<Vec<_>>());
    let en = Engine::new();
    en.metadata(&o);
    let values = load(&o);
    let v = std::array::from_fn(|i| values[i].as_slice());
    let mut out = vec![CANARY; o.n + 8];
    let r = en.run(&o, v, 0, o.n - 1, &mut out).unwrap();
    assert_eq!(r, expected(&o, 0, o.n - 1));
    let selected = record(o.n, r, &out);
    if o.golden.is_none() {
        let mut d = edges(&en, &o, &values);
        d.extend(&selected);
        write_capture(&o.capture, &d);
        println!("{{\"kind\":\"capture\",\"indicator\":{:?},\"fixture\":{:?},\"mode\":{:?},\"n\":{},\"edge_records\":9,\"range_errors\":3,\"short_checks\":{},\"timed\":false}}",o.indicator,o.fixture,o.mode,o.n,if cfg!(c_reference){0}else{5});
        return;
    }
    write_capture(&o.capture, &selected);
    assert_eq!(selected, fs::read(o.golden.as_ref().unwrap()).unwrap());
    drop(selected);
    println!("{{\"kind\":\"validation\",\"indicator\":{:?},\"fixture\":{:?},\"mode\":{:?},\"n\":{},\"beg\":{},\"count\":{},\"golden_verified\":true}}",o.indicator,o.fixture,o.mode,o.n,r.0,r.1);
    for _ in 0..5 {
        black_box(en.run(&o, v, 0, o.n - 1, &mut out).unwrap());
    }
    let mut samples = Vec::with_capacity(31);
    for _ in 0..31 {
        let t = Instant::now();
        for _ in 0..o.iters {
            let got = en
                .run(black_box(&o), black_box(v), 0, o.n - 1, black_box(&mut out))
                .unwrap();
            assert_eq!(got, r);
            black_box(&out[..got.1]);
        }
        samples.push(t.elapsed().as_nanos() as f64 / o.iters as f64);
    }
    let last = en.run(&o, v, 0, o.n - 1, &mut out).unwrap();
    assert_eq!(
        record(o.n, last, &out),
        fs::read(o.golden.as_ref().unwrap()).unwrap()
    );
    println!("{{\"kind\":\"case\",\"indicator\":{:?},\"fixture\":{:?},\"mode\":{:?},\"n\":{},\"iterations\":{},\"warmups\":5,\"samples_ns\":{:?}}}",o.indicator,o.fixture,o.mode,o.n,o.iters,samples);
}
#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn selected_cli() {
        let a = |v: &[&str]| v.iter().map(|x| x.to_string()).collect::<Vec<_>>();
        assert!(options(&a(&[
            "p",
            "engulf",
            "white",
            "typed",
            "100",
            "1000",
            "i",
            "o",
            "--capture-only"
        ]))
        .golden
        .is_none());
        for v in [
            vec![
                "p", "engulf", "white", "typed", "100", "1000", "i", "o", "--golden", "o",
            ],
            vec![
                "p",
                "doji",
                "white",
                "all",
                "100",
                "1000",
                "i",
                "o",
                "--capture-only",
            ],
            vec![
                "p",
                "doji",
                "white",
                "typed",
                "101",
                "1000",
                "i",
                "o",
                "--capture-only",
            ],
        ] {
            assert!(std::panic::catch_unwind(|| options(&a(&v))).is_err());
        }
    }
    #[test]
    fn full_tail() {
        let mut v = vec![CANARY; 108];
        v[..98].fill(0);
        assert_eq!(record(100, (2, 98), &v).len(), 464);
        v[107] = 0;
        assert!(std::panic::catch_unwind(|| record(100, (2, 98), &v)).is_err());
    }
}
