//! Diagnostic only: preallocated kernel vs complete adapter, not additive stages.
use crate::native::{bind_params, compute, core, Param, Params};
use polars::prelude::*;
use std::{hint::black_box, time::Instant};
use ta_lib::abstract_api::FuncId;

#[test]
#[ignore = "release-only diagnostic; raw distributions are archived by CI"]
fn adapter_cost_probe() {
    println!(
        "COST_PROBE metadata_functions={}",
        ta_lib::abstract_api::FUNCS.len()
    );
    println!(
        "COST_PROBE metadata_names={:?}",
        ta_lib::abstract_api::FUNCS
            .iter()
            .map(|f| f.name)
            .collect::<Vec<_>>()
    );
    for n in [100usize, 10_000, 1_000_000] {
        let x = (0..n)
            .map(|i| 100. + (i as f64 * 0.1).sin())
            .collect::<Vec<_>>();
        let high = x.iter().map(|v| v + 1.).collect::<Vec<_>>();
        let low = x.iter().map(|v| v - 1.).collect::<Vec<_>>();
        let series = [
            Series::from_vec("close", x.clone()),
            Series::from_vec("high", high.clone()),
            Series::from_vec("low", low.clone()),
        ];
        for (id, period) in [(FuncId::EMA, 30), (FuncId::ATR, 14)] {
            let params = Params::from([("timeperiod".to_owned(), Param::Int(period))]);
            let mut output = vec![f64::NAN; n];
            let order: &[usize] = if id == FuncId::EMA { &[0] } else { &[1, 2, 0] };
            let inputs = if id == FuncId::EMA {
                &series[..1]
            } else {
                &series[..]
            };
            let iterations = if n == 100 {
                2000
            } else if n == 10_000 {
                50
            } else {
                3
            };
            for mode in ["setup_lookback", "preallocated_kernel", "complete_adapter"] {
                let iterations = if mode == "setup_lookback" {
                    10_000
                } else {
                    iterations
                };
                let mut samples = Vec::new();
                for _ in 0..9 {
                    let start = Instant::now();
                    for _ in 0..iterations {
                        match mode {
                            "setup_lookback" => {
                                let mut call = black_box(id).new_call(core());
                                bind_params(&mut call, black_box(&params)).unwrap();
                                black_box(call.lookback().unwrap());
                            }
                            "preallocated_kernel" => {
                                let range = if id == FuncId::EMA {
                                    core().ema(
                                        0,
                                        n - 1,
                                        black_box(&x),
                                        period,
                                        black_box(&mut output),
                                    )
                                } else {
                                    core().atr(
                                        0,
                                        n - 1,
                                        black_box(&high),
                                        black_box(&low),
                                        black_box(&x),
                                        period,
                                        black_box(&mut output),
                                    )
                                }
                                .unwrap();
                                black_box(range);
                            }
                            _ => {
                                black_box(
                                    compute(
                                        black_box(id),
                                        black_box(inputs),
                                        black_box(&params),
                                        order,
                                        &[],
                                    )
                                    .unwrap(),
                                );
                            }
                        }
                    }
                    samples.push(start.elapsed().as_nanos() as f64 / iterations as f64);
                }
                println!(
                    "COST_PROBE {:?}/{}/{mode} iterations={iterations} ns_per_call={samples:?}",
                    id, n
                );
            }
            // Validate the direct kernel's compact output against adapter alignment.
            let got = compute(id, inputs, &params, order, &[]).unwrap();
            let begin = if id == FuncId::EMA {
                core().ema(0, n - 1, &x, period, &mut output)
            } else {
                core().atr(0, n - 1, &high, &low, &x, period, &mut output)
            }
            .unwrap();
            assert_eq!(
                &got.f64().unwrap().cont_slice().unwrap()
                    [begin.beg_idx..begin.beg_idx + begin.count],
                &output[..begin.count]
            );
        }
    }
}
