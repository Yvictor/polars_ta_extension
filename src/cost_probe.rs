//! Diagnostic only: preallocated kernel vs complete adapter, not additive stages.
use crate::native::{bind_params, compute, core, Param, Params};
use polars::prelude::*;
use std::{hint::black_box, time::Instant};
use ta_lib::abstract_api::FuncId;

#[test]
#[ignore = "release-only diagnostic; raw distributions are archived by CI"]
fn adapter_cost_probe() {
    kwargs_cost_probe();
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
            for mode in [
                "setup_lookback",
                "abstract_kernel",
                "preallocated_kernel",
                "complete_adapter",
            ] {
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
                            "abstract_kernel" => {
                                let mut call = black_box(id).new_call(core());
                                bind_params(&mut call, black_box(&params)).unwrap();
                                if id == FuncId::EMA {
                                    call.set_input(0, black_box(&x)).unwrap();
                                } else {
                                    call.set_price_input(
                                        0,
                                        None,
                                        Some(black_box(&high)),
                                        Some(black_box(&low)),
                                        Some(black_box(&x)),
                                        None,
                                        None,
                                    )
                                    .unwrap();
                                }
                                call.set_output(0, black_box(&mut output)).unwrap();
                                black_box(call.call(0, n - 1).unwrap());
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
                                let _ = black_box(
                                    compute_probe(
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
            let got = compute_probe(id, inputs, &params, order, &[]).unwrap();
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

fn compute_probe(
    id: FuncId,
    inputs: &[Series],
    params: &Params,
    order: &[usize],
    names: &[&str],
) -> PolarsResult<Series> {
    if id == FuncId::EMA {
        compute::<1, 1>(id, inputs, params, order, names)
    } else {
        compute::<3, 1>(id, inputs, params, order, names)
    }
}

// The derive macro decodes this envelope once per plugin callback, before
// compute. Keep this stage separate from numerical/adapter timings above.
fn kwargs_cost_probe() {
    use crate::{missing::Masked, params::legacy};
    use serde::Deserialize;
    use std::collections::BTreeMap;
    fn samples<T: for<'de> Deserialize<'de>>(bytes: &[u8]) -> Vec<f64> {
        let decode =
            || serde_pickle::from_slice::<Masked<T>>(black_box(bytes), Default::default()).unwrap();
        for _ in 0..256 {
            black_box(decode());
        }
        (0..9)
            .map(|_| {
                let start = Instant::now();
                for _ in 0..10_000 {
                    black_box(decode());
                }
                start.elapsed().as_nanos() as f64 / 10_000.
            })
            .collect()
    }
    for (name, bytes) in [
        (
            "ADD",
            &include_bytes!("../tests/data/kwargs-add-protocol5.pkl")[..],
        ),
        (
            "EMA",
            &include_bytes!("../tests/data/kwargs-ema-protocol5.pkl")[..],
        ),
        (
            "ATR",
            &include_bytes!("../tests/data/kwargs-atr-protocol5.pkl")[..],
        ),
        (
            "MACD",
            &include_bytes!("../tests/data/kwargs-macd-protocol5.pkl")[..],
        ),
        (
            "BBANDS",
            &include_bytes!("../tests/data/kwargs-bbands-protocol5.pkl")[..],
        ),
        (
            "MACDEXT",
            &include_bytes!("../tests/data/kwargs-macdext-protocol5.pkl")[..],
        ),
        (
            "SAREXT",
            &include_bytes!("../tests/data/kwargs-sarext-protocol5.pkl")[..],
        ),
    ] {
        let old = samples::<BTreeMap<String, legacy::Param>>(bytes);
        let current = samples::<Params>(bytes);
        println!("COST_PROBE {name}/kwargs_pickle_old iterations=10000 ns_per_call={old:?}");
        println!(
            "COST_PROBE {name}/kwargs_pickle_current iterations=10000 ns_per_call={current:?}"
        );
    }
}
