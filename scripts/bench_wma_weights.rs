//! Native public calls only; unsafe is confined to validated C FFI buffers/handles.
use std::{env, fs, hint::black_box, io::Write, path::Path, time::Instant};
#[cfg(not(c_reference))]
use ta_lib::{Core, MAType, MavpStream, WmaStream};
const POISON: u64 = 0x7ff8_0000_0000_55aa;
#[cfg(c_reference)]
mod c_api {
    use std::ffi::{c_char, c_void};
    extern "C" {
        pub fn TA_Initialize() -> i32;
        pub fn TA_GetVersionString() -> *const c_char;
        pub fn TA_WMA(
            s: i32,
            e: i32,
            x: *const f64,
            p: i32,
            b: *mut i32,
            n: *mut i32,
            o: *mut f64,
        ) -> i32;
        pub fn TA_MA(
            s: i32,
            e: i32,
            x: *const f64,
            p: i32,
            t: i32,
            b: *mut i32,
            n: *mut i32,
            o: *mut f64,
        ) -> i32;
        pub fn TA_MAVP(
            s: i32,
            e: i32,
            x: *const f64,
            p: *const f64,
            min: i32,
            max: i32,
            t: i32,
            b: *mut i32,
            n: *mut i32,
            o: *mut f64,
        ) -> i32;
        pub fn TA_EMA(
            s: i32,
            e: i32,
            x: *const f64,
            p: i32,
            b: *mut i32,
            n: *mut i32,
            o: *mut f64,
        ) -> i32;
        pub fn TA_ADD(
            s: i32,
            e: i32,
            x: *const f64,
            y: *const f64,
            b: *mut i32,
            n: *mut i32,
            o: *mut f64,
        ) -> i32;
        pub fn TA_WMA_Open(s: *mut *mut c_void, x: *const f64, n: i32, p: i32, o: *mut f64) -> i32;
        pub fn TA_WMA_Update(s: *mut c_void, x: f64, o: *mut f64) -> i32;
        pub fn TA_WMA_Peek(s: *const c_void, x: f64, o: *mut f64) -> i32;
        pub fn TA_WMA_Value(s: *const c_void, o: *mut f64) -> i32;
        pub fn TA_WMA_OutRange(s: *const c_void, b: *mut i32, n: *mut i32) -> i32;
        pub fn TA_WMA_Clone(s: *const c_void, d: *mut *mut c_void) -> i32;
        pub fn TA_WMA_Close(s: *mut c_void) -> i32;
        pub fn TA_MAVP_Open(
            s: *mut *mut c_void,
            x: *const f64,
            p: *const f64,
            n: i32,
            min: i32,
            max: i32,
            t: i32,
            o: *mut f64,
        ) -> i32;
        pub fn TA_MAVP_Update(s: *mut c_void, x: f64, p: f64, o: *mut f64) -> i32;
        pub fn TA_MAVP_Peek(s: *const c_void, x: f64, p: f64, o: *mut f64) -> i32;
        pub fn TA_MAVP_Value(s: *const c_void, o: *mut f64) -> i32;
        pub fn TA_MAVP_OutRange(s: *const c_void, b: *mut i32, n: *mut i32) -> i32;
        pub fn TA_MAVP_Clone(s: *const c_void, d: *mut *mut c_void) -> i32;
        pub fn TA_MAVP_Close(s: *mut c_void) -> i32;
    }
}
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
struct Case {
    kind: &'static str,
    p: i32,
    n: usize,
}
const CASES: [Case; 15] = [
    Case {
        kind: "wma",
        p: 2,
        n: 1000000,
    },
    Case {
        kind: "wma",
        p: 3,
        n: 1000000,
    },
    Case {
        kind: "wma",
        p: 14,
        n: 1000000,
    },
    Case {
        kind: "wma",
        p: 30,
        n: 1000000,
    },
    Case {
        kind: "wma",
        p: 200,
        n: 1000000,
    },
    Case {
        kind: "wma",
        p: 1000,
        n: 1000000,
    },
    Case {
        kind: "wma",
        p: 14,
        n: 100,
    },
    Case {
        kind: "wma",
        p: 14,
        n: 10000,
    },
    Case {
        kind: "mavp",
        p: 30,
        n: 100,
    },
    Case {
        kind: "mavp",
        p: 30,
        n: 10000,
    },
    Case {
        kind: "mavp",
        p: 30,
        n: 1000000,
    },
    Case {
        kind: "stream",
        p: 14,
        n: 10000,
    },
    Case {
        kind: "bank",
        p: 30,
        n: 10000,
    },
    Case {
        kind: "ema",
        p: 14,
        n: 1000000,
    },
    Case {
        kind: "add",
        p: 0,
        n: 1000000,
    },
];
impl Case {
    fn name(self) -> String {
        format!("{}_{}_{}", self.kind, self.p, self.n)
    }
    fn iters(self) -> usize {
        match self.n {
            100 => 1000,
            10000 => 10,
            1000000 => 1,
            _ => panic!("fixedsize"),
        }
    }
    fn range(self) -> (usize, usize) {
        let b = match self.kind {
            "add" => 0,
            _ => (self.p - 1) as usize,
        };
        (b, self.n - b)
    }
    fn history(self) -> usize {
        self.p as usize
    }
}
fn selected(name: &str) -> Case {
    let cases: Vec<_> = CASES.into_iter().filter(|c| c.name() == name).collect();
    assert_eq!(cases.len(), 1, "unknowncase");
    cases[0]
}
fn equivalent(a: f64, b: f64) -> bool {
    a.to_bits() == b.to_bits() || (a.is_nan() && b.is_nan())
}
#[cfg(not(c_reference))]
struct Engine(Core);
#[cfg(c_reference)]
struct Engine;
impl Engine {
    fn new() -> Self {
        #[cfg(c_reference)]
        {
            assert_eq!(unsafe { c_api::TA_Initialize() }, 0);
            Self
        }
        #[cfg(not(c_reference))]
        {
            Self(Core::new())
        }
    }
    fn batch(
        &self,
        kind: &str,
        s: usize,
        e: usize,
        x: &[f64],
        periods: &[f64],
        second: &[f64],
        p: i32,
        o: &mut [f64],
    ) -> (i32, usize, usize) {
        assert!(s <= e && e < x.len() && e < periods.len() && e < second.len());
        assert!(e <= 1000000);
        let lb = match kind {
            "mavp" => 29,
            "add" => 0,
            _ => (p - 1) as usize,
        };
        let beg = s.max(lb);
        let count = if beg > e { 0 } else { e - beg + 1 };
        assert!(o.len() >= count + 8);
        #[cfg(c_reference)]
        {
            let mut b = -321;
            let mut n = -654;
            // All arrays cover e, output holds the complete requested prefix plus canaries.
            let code = unsafe {
                match kind {
                    "wma" => c_api::TA_WMA(
                        s as i32,
                        e as i32,
                        x.as_ptr(),
                        p,
                        &mut b,
                        &mut n,
                        o.as_mut_ptr(),
                    ),
                    "ma" => c_api::TA_MA(
                        s as i32,
                        e as i32,
                        x.as_ptr(),
                        p,
                        2,
                        &mut b,
                        &mut n,
                        o.as_mut_ptr(),
                    ),
                    "mavp" => c_api::TA_MAVP(
                        s as i32,
                        e as i32,
                        x.as_ptr(),
                        periods.as_ptr(),
                        2,
                        30,
                        2,
                        &mut b,
                        &mut n,
                        o.as_mut_ptr(),
                    ),
                    "ema" => c_api::TA_EMA(
                        s as i32,
                        e as i32,
                        x.as_ptr(),
                        p,
                        &mut b,
                        &mut n,
                        o.as_mut_ptr(),
                    ),
                    "add" => c_api::TA_ADD(
                        s as i32,
                        e as i32,
                        x.as_ptr(),
                        second.as_ptr(),
                        &mut b,
                        &mut n,
                        o.as_mut_ptr(),
                    ),
                    _ => panic!("kind"),
                }
            };
            if code == 0 {
                assert!(b >= 0 && n >= 0);
                (0, b as usize, n as usize)
            } else {
                (code, 0, 0)
            }
        }
        #[cfg(not(c_reference))]
        {
            let r = match kind {
                "wma" => self.0.wma(s, e, x, p, o),
                "ma" => self.0.ma(s, e, x, p, MAType::WMA, o),
                "mavp" => self.0.mavp(s, e, x, periods, 2, 30, MAType::WMA, o),
                "ema" => self.0.ema(s, e, x, p, o),
                "add" => self.0.add(s, e, x, second, o),
                _ => panic!("kind"),
            };
            match r {
                Ok(r) => (0, r.beg_idx, r.count),
                Err(e) => (e.as_c_int(), 0, 0),
            }
        }
    }
    fn open(&self, bank: bool, x: &[f64], periods: &[f64], p: i32) -> (Stream, f64) {
        assert!(!x.is_empty() && x.len() == periods.len() && x.len() <= 1000000);
        #[cfg(c_reference)]
        {
            let mut ptr = std::ptr::null_mut();
            let mut value = f64::from_bits(POISON);
            let code = unsafe {
                if bank {
                    c_api::TA_MAVP_Open(
                        &mut ptr,
                        x.as_ptr(),
                        periods.as_ptr(),
                        x.len() as i32,
                        2,
                        30,
                        2,
                        &mut value,
                    )
                } else {
                    c_api::TA_WMA_Open(&mut ptr, x.as_ptr(), x.len() as i32, p, &mut value)
                }
            };
            assert_eq!(code, 0);
            assert!(!ptr.is_null());
            (Stream { ptr, bank }, value)
        }
        #[cfg(not(c_reference))]
        {
            if bank {
                let (s, v) = self.0.mavp_open(x, periods, 2, 30, MAType::WMA).unwrap();
                (Stream::Bank(s), v)
            } else {
                let (s, v) = self.0.wma_open(x, p).unwrap();
                (Stream::Wma(s), v)
            }
        }
    }
}
#[cfg(not(c_reference))]
#[derive(Clone)]
enum Stream {
    Wma(WmaStream),
    Bank(MavpStream),
}
#[cfg(c_reference)]
struct Stream {
    ptr: *mut std::ffi::c_void,
    bank: bool,
}
#[cfg(c_reference)]
impl Clone for Stream {
    fn clone(&self) -> Self {
        let mut ptr = std::ptr::null_mut();
        let code = unsafe {
            if self.bank {
                c_api::TA_MAVP_Clone(self.ptr, &mut ptr)
            } else {
                c_api::TA_WMA_Clone(self.ptr, &mut ptr)
            }
        };
        assert_eq!(code, 0);
        assert!(!ptr.is_null());
        Self {
            ptr,
            bank: self.bank,
        }
    }
}
#[cfg(c_reference)]
impl Drop for Stream {
    fn drop(&mut self) {
        let code = unsafe {
            if self.bank {
                c_api::TA_MAVP_Close(self.ptr)
            } else {
                c_api::TA_WMA_Close(self.ptr)
            }
        };
        assert_eq!(code, 0);
    }
}
impl Stream {
    fn range(&self) -> (usize, usize) {
        #[cfg(c_reference)]
        {
            let mut b = -1;
            let mut n = -1;
            let code = unsafe {
                if self.bank {
                    c_api::TA_MAVP_OutRange(self.ptr, &mut b, &mut n)
                } else {
                    c_api::TA_WMA_OutRange(self.ptr, &mut b, &mut n)
                }
            };
            assert_eq!(code, 0);
            assert!(b >= 0 && n >= 0);
            (b as usize, n as usize)
        }
        #[cfg(not(c_reference))]
        {
            let r = match self {
                Self::Wma(s) => s.out_range(),
                Self::Bank(s) => s.out_range(),
            };
            (r.beg_idx, r.count)
        }
    }
    fn value(&self) -> f64 {
        #[cfg(c_reference)]
        {
            let mut v = f64::from_bits(POISON);
            let code = unsafe {
                if self.bank {
                    c_api::TA_MAVP_Value(self.ptr, &mut v)
                } else {
                    c_api::TA_WMA_Value(self.ptr, &mut v)
                }
            };
            assert_eq!(code, 0);
            v
        }
        #[cfg(not(c_reference))]
        {
            match self {
                Self::Wma(s) => s.value(),
                Self::Bank(s) => s.value(),
            }
        }
    }
    fn eval(&mut self, x: f64, p: f64, peek: bool) -> (i32, f64) {
        #[cfg(c_reference)]
        {
            let mut v = f64::from_bits(POISON);
            let code = unsafe {
                match (self.bank, peek) {
                    (true, true) => c_api::TA_MAVP_Peek(self.ptr, x, p, &mut v),
                    (true, false) => c_api::TA_MAVP_Update(self.ptr, x, p, &mut v),
                    (false, true) => c_api::TA_WMA_Peek(self.ptr, x, &mut v),
                    (false, false) => c_api::TA_WMA_Update(self.ptr, x, &mut v),
                }
            };
            if code != 0 {
                assert_eq!(v.to_bits(), POISON);
            }
            (code, v)
        }
        #[cfg(not(c_reference))]
        {
            let r = match (self, peek) {
                (Self::Wma(s), true) => s.peek(x),
                (Self::Wma(s), false) => s.update(x),
                (Self::Bank(s), true) => s.peek(x, p),
                (Self::Bank(s), false) => s.update(x, p),
            };
            match r {
                Ok(v) => (0, v),
                Err(e) => (e.as_c_int(), f64::from_bits(POISON)),
            }
        }
    }
}
fn words(path: &Path) -> Vec<f64> {
    let d = fs::read(path).unwrap();
    assert_eq!(d.len() % 8, 0);
    d.chunks_exact(8)
        .map(|x| f64::from_bits(u64::from_le_bytes(x.try_into().unwrap())))
        .collect()
}
fn contract(input: &Path, out: &Path) {
    fs::create_dir_all(out).unwrap();
    let engine = Engine::new();
    let mut index = fs::File::create(out.join("index.tsv")).unwrap();
    for line in fs::read_to_string(input.join("index.tsv")).unwrap().lines() {
        let f: Vec<_> = line.split('\t').collect();
        assert_eq!(f.len(), 9);
        let id = f[0];
        assert!(id.bytes().all(|x| x.is_ascii_alphanumeric()));
        let mode = f[1];
        let x = words(&input.join(f[2]));
        let periods = words(&input.join(f[3]));
        let num = |i: usize| f[i].parse::<usize>().unwrap();
        let s = num(4);
        let e = num(5);
        let p = f[6].parse().unwrap();
        let cap = num(7);
        let history = num(8);
        let mut values = vec![f64::from_bits(POISON); cap];
        let mut events = String::new();
        let (code, beg, count) = if mode == "stream" || mode == "bank" {
            let (mut stream, last) =
                engine.open(mode == "bank", &x[..history], &periods[..history], p);
            values.clear();
            values.push(last);
            let (b, n) = stream.range();
            events += &format!("open\t0\t0\t{b}\t{n}\n");
            for i in history..x.len() {
                let before = stream.range();
                let value = stream.value().to_bits();
                let (pc, pv) = stream.eval(x[i], periods[i], true);
                assert_eq!(stream.range(), before);
                assert_eq!(stream.value().to_bits(), value);
                let mut fork = stream.clone();
                let (fc, fv) = fork.eval(x[i], periods[i], false);
                let (uc, uv) = stream.eval(x[i], periods[i], false);
                assert_eq!(fc, uc);
                assert!(equivalent(fv, uv));
                if uc != 0 {
                    assert_eq!(stream.range(), before);
                    assert_eq!(stream.value().to_bits(), value);
                }
                values.extend([pv, uv, stream.value()]);
                let (b, n) = stream.range();
                events += &format!("step\t{pc}\t{uc}\t{b}\t{n}\n");
            }
            let (b, n) = stream.range();
            (0, b, n)
        } else {
            engine.batch(mode, s, e, &x, &periods, &x, p, &mut values)
        };
        if mode != "stream" && mode != "bank" {
            assert!(values[count..].iter().all(|v| v.to_bits() == POISON));
        }
        let bytes: Vec<_> = values
            .iter()
            .flat_map(|x| x.to_bits().to_le_bytes())
            .collect();
        fs::write(out.join(format!("{id}.bin")), bytes).unwrap();
        fs::write(out.join(format!("{id}.events")), events).unwrap();
        writeln!(index, "{id}\t{code}\t{beg}\t{count}\t{}", values.len()).unwrap();
    }
}
struct Data {
    x: Vec<f64>,
    periods: Vec<f64>,
    second: Vec<f64>,
}
fn load(path: &str, n: usize) -> Data {
    let d = fs::read(path).unwrap();
    assert_eq!(d.len(), 16 + 24 * n);
    assert_eq!(&d[..8], b"WMAFIX01");
    assert_eq!(u64::from_le_bytes(d[8..16].try_into().unwrap()) as usize, n);
    let mut v = d[16..]
        .chunks_exact(8)
        .map(|x| f64::from_bits(u64::from_le_bytes(x.try_into().unwrap())));
    let x = v.by_ref().take(n).collect();
    let periods = v.by_ref().take(n).collect();
    let second = v.collect();
    Data { x, periods, second }
}
fn capture(c: Case, range: (usize, usize), out: &[f64]) -> Vec<u8> {
    assert_eq!(range, c.range());
    assert_eq!(out.len(), c.n + 8);
    assert!(out[range.1..].iter().all(|x| x.to_bits() == POISON));
    let mut b = Vec::new();
    b.extend(b"WMAOUT01");
    for x in [c.n, range.0, range.1] {
        b.extend((x as u64).to_le_bytes());
    }
    for x in out {
        b.extend(x.to_bits().to_le_bytes());
    }
    b
}
fn sample(
    engine: &Engine,
    c: Case,
    data: &Data,
    out: &mut [f64],
    seed: &Option<(Stream, f64)>,
    iters: usize,
) -> (u128, (usize, usize)) {
    // Clone/open allocations and drops are outside the interval for every real public implementation.
    let mut streams: Vec<_> = seed
        .as_ref()
        .map(|(s, _)| (0..iters).map(|_| s.clone()).collect())
        .unwrap_or_default();
    out.fill(f64::from_bits(POISON));
    let mut range = (0, 0);
    let start = Instant::now();
    if let Some((_, last)) = seed {
        for stream in &mut streams {
            out[0] = *last;
            for i in c.history()..c.n {
                let (code, value) =
                    stream.eval(black_box(data.x[i]), black_box(data.periods[i]), false);
                assert_eq!(code, 0);
                out[i - c.history() + 1] = value;
            }
        }
    } else {
        for _ in 0..iters {
            let (code, b, n) = engine.batch(
                c.kind,
                0,
                c.n - 1,
                black_box(&data.x),
                black_box(&data.periods),
                black_box(&data.second),
                black_box(c.p),
                black_box(out),
            );
            assert_eq!(code, 0);
            range = (b, n);
        }
    }
    let elapsed = start.elapsed().as_nanos();
    if let Some(stream) = streams.last() {
        range = stream.range();
    }
    black_box(&*out);
    drop(streams);
    (elapsed, range)
}
fn benchmark(args: &[String]) {
    assert!(
        args.len() == 6 || args.len() == 7,
        "CASE INPUT CAPTURE --capture-only | --golden PATH"
    );
    let c = selected(&args[1]);
    let data = load(&args[2], c.n);
    assert!(data
        .x
        .iter()
        .chain(&data.periods)
        .chain(&data.second)
        .all(|x| x.is_finite()));
    let output = &args[3];
    let golden = if args.len() == 6 {
        assert_eq!(args[4], "--capture-only");
        assert_eq!(args[5], "typed");
        None
    } else {
        assert_eq!(args[4], "--golden");
        assert_eq!(args[6], "typed");
        assert_ne!(args[3], args[5]);
        Some(fs::read(&args[5]).unwrap())
    };
    let engine = Engine::new();
    let seed = if c.kind == "stream" || c.kind == "bank" {
        Some(engine.open(
            c.kind == "bank",
            &data.x[..c.history()],
            &data.periods[..c.history()],
            c.p,
        ))
    } else {
        None
    };
    let mut out = vec![f64::from_bits(POISON); c.n + 8];
    let (_, range) = sample(&engine, c, &data, &mut out, &seed, 1);
    let initial = capture(c, range, &out);
    fs::write(output, &initial).unwrap();
    let Some(golden) = golden else {
        return;
    };
    assert_eq!(golden, initial, "preflight values differ");
    for _ in 0..5 {
        let (_, r) = sample(&engine, c, &data, &mut out, &seed, c.iters());
        assert_eq!(capture(c, r, &out), golden, "warmup values differ");
    }
    let mut samples = Vec::new();
    for _ in 0..31 {
        let (ns, r) = sample(&engine, c, &data, &mut out, &seed, c.iters());
        assert!(ns > 0);
        assert_eq!(capture(c, r, &out), golden, "timed values differ");
        samples.push(ns as f64 / c.iters() as f64 / 1e6);
    }
    fs::write(output, capture(c, c.range(), &out)).unwrap();
    println!("{{\"case\":\"{}\",\"n\":{},\"iterations\":{},\"repeats\":31,\"warmups\":5,\"checked_values\":{},\"samples_ms\":{:?}}}",c.name(),c.n,c.iters(),c.range().1,samples);
}
fn main() {
    let a: Vec<_> = env::args().collect();
    if a.get(1).map(String::as_str) == Some("--contract") {
        assert_eq!(a.len(), 4);
        contract(Path::new(&a[2]), Path::new(&a[3]));
    } else if a.get(1).map(String::as_str) == Some("--describe") {
        #[cfg(c_reference)]
        {
            let _ = Engine::new();
            let s = unsafe { std::ffi::CStr::from_ptr(c_api::TA_GetVersionString()) }
                .to_str()
                .unwrap();
            println!("{{\"c_reference\":true,\"version\":\"{s}\"}}");
        }
        #[cfg(not(c_reference))]
        {
            println!("{{\"c_reference\":false,\"version\":\"native\"}}");
        }
    } else {
        benchmark(&a);
    }
}
#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn fixed_inventory_is_unique() {
        let mut names: Vec<_> = CASES.into_iter().map(Case::name).collect();
        names.sort();
        names.dedup();
        assert_eq!(names.len(), 15);
        assert_eq!(
            CASES
                .iter()
                .filter(|c| c.kind == "stream" || c.kind == "bank")
                .count(),
            2
        );
    }
    #[test]
    fn unknown_case_rejected() {
        assert!(std::panic::catch_unwind(|| selected("wma_15_100")).is_err());
    }
    #[test]
    fn range_and_iterations_are_fixed() {
        assert_eq!(selected("wma_14_100").range(), (13, 87));
        assert_eq!(selected("mavp_30_100").range(), (29, 71));
        assert_eq!(selected("bank_30_10000").iters(), 10);
    }
}
