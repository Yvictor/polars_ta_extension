#![forbid(unsafe_code)]
use std::io::{BufWriter, Write};
use std::path::Path;
use ta_lib::{Core, OutRange, RetCode};
const POISON: u64 = 0x7ff8_0000_0000_55aa;
fn prices(n: usize, shape: usize) -> Vec<f64> {
    (0..n).map(|i| {
        let wave = 64.0 + ((i % 37) as i32 - 18) as f64 * 0.125;
        match shape {
            0 => wave,
            1 => if i == n / 3 { 1e9 } else { wave },
            2 => if (i / 41) % 2 == 0 { 3.3 } else { wave },
            3 => 1e12 + ((i % 37) as i32 - 18) as f64 * 0.125,
            4 => 42.0,
            5 => 0.0,
            6 => -0.0,
            7 => if i % 3 == 0 { -0.0 } else { 0.0 },
            8 => f64::from_bits((i % 7 + 1) as u64),
            9 => if i == n / 3 { f64::from_bits(0x7ff8_0000_0000_1234) } else { wave },
            10 => if i == n / 3 { f64::INFINITY } else { wave },
            11 => if i == n / 3 { f64::NEG_INFINITY } else { wave },
            12 => if i % 2 == 0 { 1e200 } else { -1e200 },
            _ => unreachable!(),
        }
    }).collect()
}
#[derive(Clone, Copy)]
struct Case { n: usize, shape: usize, period: i32, start: usize, end: usize, cap: usize, dev: f64 }
fn call(core: &Core, c: Case, function: usize, api: usize, input: &[f64], out: &mut [f64]) -> Result<OutRange, RetCode> {
    if api == 0 {
        if function == 0 { core.var(c.start, c.end, input, c.period, c.dev, out) }
        else { core.stddev(c.start, c.end, input, c.period, c.dev, out) }
    } else {
        let mut holder = ta_lib::abstract_api::get_func_handle(if function == 0 { "VAR" } else { "STDDEV" }).unwrap().new_call(core);
        holder.set_input(0, input)?;
        holder.set_opt_input(0, c.period)?;
        holder.set_opt_input(1, c.dev)?;
        holder.set_output(0, out)?;
        holder.call(c.start, c.end)
    }
}
fn main() {
    let dest = std::env::args().nth(1).expect("capture directory");
    let dest = Path::new(&dest); std::fs::create_dir_all(dest).unwrap();
    let mut meta = BufWriter::new(std::fs::File::create(dest.join("index.tsv")).unwrap());
    let mut words = BufWriter::new(std::fs::File::create(dest.join("outputs.bin")).unwrap());
    let core = Core::new(); let mut cases = Vec::new();
    for n in [0usize, 1, 2, 3, 5, 14, 15, 30, 31, 64, 257, 1025] {
        for shape in 0..13 {
            for period in [0i32, 1, 2, 3, 5, 14, 30, 128, Core::INTEGER_DEFAULT] {
                let effective = if period == Core::INTEGER_DEFAULT { 5 } else { period.max(1) as usize };
                for (start, end) in [(0, n.saturating_sub(1)), (n / 2, n.saturating_sub(1)), (n, n.saturating_sub(1))] {
                    let begin = start.max(effective - 1); let count = if begin <= end { end - begin + 1 } else { 0 };
                    let mut caps = vec![0, count.saturating_sub(1), count + 7]; caps.sort_unstable(); caps.dedup();
                    for cap in caps { cases.push(Case { n, shape, period, start, end, cap, dev: 1.0 }); }
                }
            }
        }
    }
    for period in [2i32, 3, 5, 14, 30, 128] {
        for n in [32 * period as usize - 1, 32 * period as usize, 32 * period as usize + 1] {
            for shape in [0usize, 1, 2, 3, 7, 9, 10, 11] {
                for start in [0, period as usize, n / 3] {
                    cases.push(Case { n, shape, period, start, end: n - 1, cap: n - start.max(period as usize - 1) + 7, dev: 1.0 });
                }
            }
        }
    }
    for period in [1i32, 2, 14, Core::INTEGER_DEFAULT, -1, 100001] {
        for shape in [0usize, 5, 6, 7, 9, 10, 11] {
            for dev in [0.0, -0.0, -1.0, 2.5, Core::REAL_DEFAULT, f64::NAN, f64::INFINITY, 4e37] {
                cases.push(Case { n: 64, shape, period, start: 3, end: 63, cap: 71, dev });
            }
        }
    }
    for period in [20000i32, 100000] {
        for shape in [0usize, 1, 3, 7] {
            for start in [0, period as usize, period as usize + 1] {
                cases.push(Case { n: period as usize + 3, shape, period, start, end: period as usize + 2, cap: 12, dev: 1.0 });
            }
        }
    }
    for (start, end) in [(Core::INDEX_MAX + 1, Core::INDEX_MAX + 1), (0, Core::INDEX_MAX + 1), (8, 7)] {
        cases.push(Case { n: 32, shape: 0, period: 14, start, end, cap: 8, dev: 1.0 });
    }
    let mut id = 0; let mut offset = 0;
    for c in cases {
        let input = prices(c.n, c.shape);
        for function in 0..2 { for api in 0..2 {
            let mut output = vec![f64::from_bits(POISON); c.cap];
            let result = call(&core, c, function, api, &input, &mut output);
            let (code, beg, count) = match result { Ok(range) => (0, range.beg_idx, range.count), Err(code) => (code.as_c_int(), 0, 0) };
            writeln!(meta, "{id}\t{}\t{}\t{}\t{}\t{}\t{}\t{function}\t{api}\t{:016x}\t{code}\t{beg}\t{count}\t{offset}", c.n, c.shape, c.period, c.start, c.end, c.cap, c.dev.to_bits()).unwrap();
            for value in output { words.write_all(&value.to_bits().to_le_bytes()).unwrap(); }
            offset += c.cap; id += 1;
        }}
    }
    meta.flush().unwrap(); words.flush().unwrap();
    println!("public VAR/STDDEV captures: {id} calls/{offset} words; typed+abstract, no timings");
}
