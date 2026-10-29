#![allow(dead_code, unused_imports)]
// Linked to the wheel dependencies and production Linux Jemalloc.
use polars::prelude::*;
use std::{
    alloc::{GlobalAlloc, Layout, System},
    hint::black_box,
    sync::atomic::{AtomicBool, AtomicUsize, Ordering},
    time::Instant,
};
use ta_lib::{abstract_api::FuncId, OutRange};
static INNER: jemallocator::Jemalloc = jemallocator::Jemalloc;
struct Count;
static ENABLED: AtomicBool = AtomicBool::new(false);
static ALLOCS: AtomicUsize = AtomicUsize::new(0);
static BYTES: AtomicUsize = AtomicUsize::new(0);
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
    fn TA_MINMAXINDEX(
        s: i32,
        e: i32,
        x: *const f64,
        p: i32,
        b: *mut i32,
        n: *mut i32,
        lo: *mut i32,
        hi: *mut i32,
    ) -> i32;
}
extern "C" {
    fn TA_GetVersionString() -> *const std::os::raw::c_char;
}
fn main() {
    let version = unsafe { std::ffi::CStr::from_ptr(TA_GetVersionString()) }
        .to_str()
        .unwrap();
    assert!(version.starts_with("0.8.1"), "wrong C baseline: {version}");
    println!("C_VERSION {version}");
    let args = std::env::args().collect::<Vec<_>>();
    let name = &args[1];
    let mode = &args[2];
    let n: usize = args[3].parse().unwrap();
    let iters: usize = args[4].parse().unwrap();
    let bytes = std::fs::read(&args[5]).unwrap();
    let x = bytes
        .chunks_exact(8)
        .take(n)
        .map(|b| f64::from_le_bytes(b.try_into().unwrap()))
        .collect::<Vec<_>>();
    let o = x.iter().map(|v| v - 0.1).collect::<Vec<_>>();
    let h = x.iter().map(|v| v + 1.0).collect::<Vec<_>>();
    let l = x.iter().map(|v| v - 1.0).collect::<Vec<_>>();
    assert_eq!(x.len(), n);
    let id = if name == "doji" {
        FuncId::CDLDOJI
    } else {
        FuncId::MINMAXINDEX
    };
    let p = if name == "doji" {
        native::Params::new()
    } else {
        native::Params::from([("timeperiod".into(), native::Param::Int(30))])
    };
    let inputs = if name == "doji" {
        vec![
            Series::from_vec("open", o.clone()),
            Series::from_vec("high", h.clone()),
            Series::from_vec("low", l.clone()),
            Series::from_vec("close", x.clone()),
        ]
    } else {
        vec![Series::from_vec("close", x.clone())]
    };
    let mut a = vec![0i32; n];
    let mut b = a.clone();
    unsafe { assert_eq!(TA_Initialize(), 0) };
    let direct = |a: &mut [i32], b: &mut [i32], kind: &str| -> OutRange {
        if kind == "ffi" {
            let (mut beg, mut count) = (0, 0);
            let code = unsafe {
                if name == "doji" {
                    TA_CDLDOJI(
                        0,
                        n as i32 - 1,
                        o.as_ptr(),
                        h.as_ptr(),
                        l.as_ptr(),
                        x.as_ptr(),
                        &mut beg,
                        &mut count,
                        a.as_mut_ptr(),
                    )
                } else {
                    TA_MINMAXINDEX(
                        0,
                        n as i32 - 1,
                        x.as_ptr(),
                        30,
                        &mut beg,
                        &mut count,
                        a.as_mut_ptr(),
                        b.as_mut_ptr(),
                    )
                }
            };
            assert_eq!(code, 0);
            OutRange {
                beg_idx: beg as usize,
                count: count as usize,
            }
        } else if name == "doji" {
            native::core().cdldoji(0, n - 1, &o, &h, &l, &x, a).unwrap()
        } else if kind == "modern" {
            native::core().minmaxindex(0, n - 1, &x, 30, a, b).unwrap()
        } else {
            compat::LEGACY.minmaxindex(0, n - 1, &x, 30, a, b).unwrap()
        }
    };
    let full = || -> Series {
        if name == "doji" {
            native::compute::<4, 1>(id, &inputs, &p, &[0, 1, 2, 3], &[]).unwrap()
        } else {
            native::compute::<1, 2>(id, &inputs, &p, &[0], &["minidx", "maxidx"]).unwrap()
        }
    };
    let materialize = || -> Series {
        if name == "doji" {
            Series::from_vec("", vec![0i32; n])
        } else {
            let fields = [
                Series::from_vec("minidx", vec![0i32; n]),
                Series::from_vec("maxidx", vec![0i32; n]),
            ];
            StructChunked::new("", &fields).unwrap().into_series()
        }
    };
    if mode == "validate" {
        let r = direct(&mut a, &mut b, "kernel");
        let mut ca = vec![0; n];
        let mut cb = vec![0; n];
        let cr = direct(&mut ca, &mut cb, "ffi");
        assert_eq!((r.beg_idx, r.count), (cr.beg_idx, cr.count));
        assert_eq!(&a[..r.count], &ca[..r.count]);
        if name != "doji" {
            assert_eq!(&b[..r.count], &cb[..r.count]);
        }
        if name == "mmi" {
            let mut ma = vec![0; n];
            let mut mb = vec![0; n];
            let mr = direct(&mut ma, &mut mb, "modern");
            assert_eq!((mr.beg_idx, mr.count), (cr.beg_idx, cr.count));
            assert_eq!(&ma[..mr.count], &ca[..cr.count]);
            assert_eq!(&mb[..mr.count], &cb[..cr.count]);
        }
        let got = full();
        let fields = if name == "doji" {
            vec![got]
        } else {
            got.struct_().unwrap().fields().to_vec()
        };
        for (i, s) in fields.iter().enumerate() {
            let v = s.i32().unwrap();
            let v = v.cont_slice().unwrap();
            assert!(v[..r.beg_idx].iter().all(|v| *v == 0));
            assert_eq!(
                &v[r.beg_idx..r.beg_idx + r.count],
                if i == 0 { &a[..r.count] } else { &b[..r.count] }
            );
        }
        println!("VALIDATE {name} n={n} direct_C_and_adapter_exact=true range={r:?}");
        return;
    }
    let mut run = || match mode.as_str() {
        "newcall" => {
            black_box(black_box(id).new_call(black_box(native::core())));
        }
        "setup" => {
            let mut holder = black_box(id).new_call(native::core());
            native::bind_params(&mut holder, &p).unwrap();
            black_box(holder.lookback().unwrap());
        }
        "abstract" => {
            let mut holder = black_box(id).new_call(native::core());
            native::bind_params(&mut holder, &p).unwrap();
            if name == "doji" {
                holder
                    .set_price_input(0, Some(&o), Some(&h), Some(&l), Some(&x), None, None)
                    .unwrap();
            } else {
                holder.set_input(0, &x).unwrap();
            }
            holder.set_int_output(0, &mut a).unwrap();
            if name != "doji" {
                holder.set_int_output(1, &mut b).unwrap();
            }
            black_box(holder.call(0, n - 1).unwrap());
        }
        "full" => drop(black_box(full())),
        "init_zero_int" => drop(black_box(vec![0i32; black_box(n)])),
        "init_nan_real" => drop(black_box(vec![f64::NAN; black_box(n)])),
        "materialize" => drop(black_box(materialize())),
        kind => {
            black_box(direct(black_box(&mut a), black_box(&mut b), kind));
        }
    };
    for _ in 0..3 {
        run();
    }
    ALLOCS.store(0, Ordering::Relaxed);
    BYTES.store(0, Ordering::Relaxed);
    ENABLED.store(true, Ordering::Relaxed);
    run();
    ENABLED.store(false, Ordering::Relaxed);
    let ac = ALLOCS.load(Ordering::Relaxed);
    let ab = BYTES.load(Ordering::Relaxed);
    let mut samples = Vec::new();
    for _ in 0..7 {
        let start = Instant::now();
        for _ in 0..iters {
            run();
        }
        samples.push(start.elapsed().as_nanos() as f64 / iters as f64);
    }
    println!(
        "PROBE {name}/{mode}/{n} allocations={ac} bytes={ab} holder_bytes={} ns={samples:?}",
        std::mem::size_of::<ta_lib::abstract_api::ParamHolder>()
    );
}
