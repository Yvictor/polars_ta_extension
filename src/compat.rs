//! Legacy semantics absent from ta-lib 0.8.3. All code uses checked slices.
//! Batch-only kernels cite pinned upstream sources and retain their BSD notices.
//! Normal inputs use 0.8.3 except explicit compatibility and backported SMA/HMA routes.
#![allow(non_snake_case)]
use ta_lib::{Core, MAType, OutRange, RetCode};
mod cmou;
mod correl;
mod hma;
mod mavp;
mod mavp_sma;
mod maxindex;
mod minindex;
mod minmaxindex;
mod percentile;
mod percentrank;
mod rsi;
mod stochrsi;
mod var;

mod adosc;
mod apo;
mod bbands;
mod cmo;
mod dema;
mod efi;
mod ema;
mod eri;
mod kc;
mod ma;
mod macd;
mod macdext;
mod macdfix;
mod ppo;
mod pvo;
mod smi;
mod stddev;
mod t3;
mod tema;
mod trix;
mod tsi;
mod zlema;
pub struct CompatCore;
impl std::ops::Deref for CompatCore {
    type Target = Core;
    fn deref(&self) -> &Core {
        crate::native::core()
    }
}
impl CompatCore {
    const REAL_DEFAULT: f64 = Core::REAL_DEFAULT;
    const REAL_MIN: f64 = Core::REAL_MIN;
    const REAL_MAX: f64 = Core::REAL_MAX;
}
pub static LEGACY: CompatCore = CompatCore;
use crate::native::{Output, Param, Params};
mod guarded;
use ta_lib::abstract_api::FuncId;
fn int(p: &Params, key: &str, default: i32) -> i32 {
    match p.get(key) {
        Some(Param::Int(v)) if *v != i32::MIN => *v,
        _ => default,
    }
}
fn real(p: &Params, key: &str, default: f64) -> f64 {
    match p.get(key) {
        Some(Param::Real(v)) if *v != Core::REAL_DEFAULT => *v,
        Some(Param::Int(v)) => f64::from(*v),
        _ => default,
    }
}

pub fn lookback(id: FuncId, p: &Params) -> Option<Result<usize, RetCode>> {
    Some(match id {
        FuncId::PERCENTILE => {
            LEGACY.percentile_lookback(int(p, "timeperiod", 30), real(p, "percentile", 50.))
        }
        FuncId::PERCENTRANK => LEGACY.percentrank_lookback(int(p, "timeperiod", 100)),
        FuncId::MAVP => LEGACY.mavp_lookback(
            int(p, "minperiod", 2),
            int(p, "maxperiod", 30),
            match MAType::try_from(int(p, "matype", 0)) {
                Ok(v) => v,
                Err(e) => return Some(Err(e)),
            },
        ),
        _ => return None,
    })
}

pub struct CompatCall {
    pub result: Result<OutRange, RetCode>,
    pub restore_native_prefix: bool,
}

/// Returns None when the released crate can preserve this call's semantics.
pub fn call(
    id: FuncId,
    input: &[&[f64]],
    p: &Params,
    outputs: &mut [Output],
    offset: usize,
) -> Option<CompatCall> {
    use FuncId::*;
    if let Some(result) = guarded::guarded_call(id, input, p, outputs, offset) {
        return Some(CompatCall {
            result,
            restore_native_prefix: true,
        });
    }
    if let (HMA, [Output::Real(out)]) = (id, &mut *outputs) {
        return Some(CompatCall {
            result: LEGACY.hma_weights(
                0,
                input[0].len() - 1,
                input[0],
                int(p, "timeperiod", 20),
                &mut out[offset..],
            ),
            restore_native_prefix: false,
        });
    }
    if id == MAVP {
        let min = int(p, "minperiod", 2);
        let max = int(p, "maxperiod", 30);
        if min == max && (1..=10000).contains(&min) {
            if let [Output::Real(out)] = outputs {
                // Upstream fixed-bound shortcut (7f395b820): after the guard,
                // normalized periods cannot affect this ordinary MA call.
                let result = MAType::try_from(int(p, "matype", 0)).and_then(|ma| {
                    crate::native::core().ma(
                        0,
                        input[0].len() - 1,
                        input[0],
                        min,
                        ma,
                        &mut out[offset..],
                    )
                });
                return Some(CompatCall {
                    result,
                    restore_native_prefix: false,
                });
            }
        }
    }
    if id == MAVP
        && int(p, "matype", 0) == 0
        && (1..=10000).contains(&int(p, "minperiod", 2))
        && (1..=10000).contains(&int(p, "maxperiod", 30))
    {
        if let [Output::Real(out)] = outputs {
            // The existing guard has proved this input needs no legacy prefix.
            return Some(CompatCall {
                result: mavp_sma::call(
                    input[0],
                    input[1],
                    int(p, "minperiod", 2),
                    int(p, "maxperiod", 30),
                    &mut out[offset..],
                ),
                restore_native_prefix: false,
            });
        }
    }
    let end = input[0].len() - 1;
    let period = int(
        p,
        "timeperiod",
        if matches!(id, RSI | CMOU | STOCHRSI) {
            14
        } else if matches!(id, VAR | STDDEV) {
            5
        } else {
            30
        },
    );
    // Guarded dispatch above already handles every nonfinite VAR/STDDEV/
    // CORREL call with the generated output arity. CMOU always uses the legacy
    // path below. Only PERCENTILE needs another nonfinite classification.
    let nonfinite = id == PERCENTILE && input.iter().any(|s| s.iter().any(|v| !v.is_finite()));
    let result = match (id, outputs) {
        (RSI, [Output::Real(out)]) => LEGACY.rsi(0, end, input[0], period, &mut out[offset..]),
        (STOCHRSI, [Output::Real(k), Output::Real(d)]) => LEGACY.stochrsi(
            0,
            end,
            input[0],
            period,
            int(p, "fastk_period", 5),
            int(p, "fastd_period", 3),
            match MAType::try_from(int(p, "fastd_matype", 0)) {
                Ok(v) => v,
                Err(e) => {
                    return Some(CompatCall {
                        result: Err(e),
                        restore_native_prefix: true,
                    })
                }
            },
            &mut k[offset..],
            &mut d[offset..],
        ),
        (MAXINDEX, [Output::Integer(out)]) => {
            LEGACY.maxindex(0, end, input[0], period, &mut out[offset..])
        }
        (MININDEX, [Output::Integer(out)]) => {
            LEGACY.minindex(0, end, input[0], period, &mut out[offset..])
        }
        (MINMAXINDEX, [Output::Integer(min), Output::Integer(max)]) => LEGACY.minmaxindex(
            0,
            end,
            input[0],
            period,
            &mut min[offset..],
            &mut max[offset..],
        ),
        (CMOU, [Output::Real(out)]) => LEGACY.cmou(0, end, input[0], period, &mut out[offset..]),
        (PERCENTILE, [Output::Real(out)]) if nonfinite || period > 10000 => LEGACY.percentile(
            0,
            end,
            input[0],
            period,
            real(p, "percentile", 50.),
            &mut out[offset..],
        ),
        (PERCENTRANK, [Output::Real(out)]) if period > 10000 => {
            LEGACY.percentrank(0, end, input[0], period, &mut out[offset..])
        }
        (MAVP, [Output::Real(out)])
            if int(p, "maxperiod", 30) > 10000 || int(p, "minperiod", 2) > 10000 =>
        {
            LEGACY.mavp(
                0,
                end,
                input[0],
                input[1],
                int(p, "minperiod", 2),
                int(p, "maxperiod", 30),
                match MAType::try_from(int(p, "matype", 0)) {
                    Ok(v) => v,
                    Err(e) => {
                        return Some(CompatCall {
                            result: Err(e),
                            restore_native_prefix: true,
                        })
                    }
                },
                &mut out[offset..],
            )
        }
        (PPO | PVO, [Output::Real(out)]) if matches!(int(p, "matype", 1), 0 | 2 | 5 | 9) => {
            match MAType::try_from(int(p, "matype", 1)) {
                Ok(ma) => percent_osc(
                    input[0],
                    int(p, "fastperiod", 12),
                    int(p, "slowperiod", 26),
                    ma,
                    &mut out[offset..],
                ),
                Err(e) => Err(e),
            }
        }
        _ => return None,
    };
    Some(CompatCall {
        result,
        restore_native_prefix: true,
    })
}

// Preserve the pre-0.8.3 combine rule on windowed MAs, including residue after
// a fractional series becomes zero. The MA kernels themselves remain upstream.
fn percent_osc(
    input: &[f64],
    fast: i32,
    slow: i32,
    ma: MAType,
    out: &mut [f64],
) -> Result<OutRange, RetCode> {
    let (fast, slow) = (fast.min(slow), fast.max(slow));
    let mut fast_values = vec![0.; input.len()];
    let fr = crate::native::core().ma(0, input.len() - 1, input, fast, ma, &mut fast_values)?;
    let sr = crate::native::core().ma(0, input.len() - 1, input, slow, ma, out)?;
    let offset = fr.count - sr.count;
    for i in 0..sr.count {
        let v = out[i];
        out[i] = if v > -1e-14 && v < 1e-14 {
            0.
        } else {
            (fast_values[i + offset] - v) / v * 100.
        };
    }
    Ok(sr)
}

/// Prefix that would have taken the normal native route on a finite input.
pub fn native_prefix(id: FuncId, input: &[&[f64]], p: &Params) -> Option<usize> {
    use FuncId::*;
    if matches!(
        id,
        RSI | STOCHRSI | MAXINDEX | MININDEX | MINMAXINDEX | ADOSC | CMOU
    ) {
        return None;
    }
    if matches!(id, PPO | PVO) && matches!(int(p, "matype", 1), 0 | 2 | 5 | 9) {
        return None;
    }
    let guarded = guarded::supports(id);
    if guarded
        && p.iter()
            .any(|(key, value)| key.contains("period") && matches!(value,Param::Int(v) if *v>128))
    {
        return None;
    }
    if matches!(id, PERCENTILE | PERCENTRANK) && int(p, "timeperiod", 30) > 10000 {
        return None;
    }
    // Choose the first causal trigger, including a later finite large value.
    // Removing/replacing a future observation cannot change prior rounding.
    (0..input[0].len()).find(|&row| {
        input
            .iter()
            .any(|s| !s[row].is_finite() || (guarded && s[row].abs() > 1024.))
    })
}

#[cfg(test)]
mod fixed_mavp_tests {
    use super::*;
    #[test]
    fn ordinary_fixed_mavp_is_exact_for_every_public_ma_and_retains_tails() {
        for mode in 0..=13 {
            for (minimum, maximum, period) in [
                (2, 2, 2),
                (i32::MIN, 2, 2),
                (30, i32::MIN, 30),
                (14, 14, 14),
                (128, 128, 128),
            ] {
                let price: Vec<_> = (0..2048).map(|i| 100. + (i % 19) as f64 / 100.).collect();
                let periods: Vec<_> = (0..2048)
                    .map(|i| [-100., -0., 3.75, 1024.][i % 4])
                    .collect();
                let mut params = Params::new();
                params.insert("minperiod".into(), Param::Int(minimum));
                params.insert("maxperiod".into(), Param::Int(maximum));
                params.insert("matype".into(), Param::Int(mode));
                let mut expected = vec![f64::NAN; 2048];
                let range = crate::native::core()
                    .mavp(
                        0,
                        2047,
                        &price,
                        &periods,
                        minimum,
                        maximum,
                        MAType::try_from(mode).unwrap(),
                        &mut expected,
                    )
                    .unwrap();
                let mut output = [Output::Real(vec![f64::NAN; 2048])];
                let call = super::call(
                    FuncId::MAVP,
                    &[&price, &periods],
                    &params,
                    &mut output,
                    range.beg_idx,
                )
                .unwrap();
                assert!(!call.restore_native_prefix);
                let actual = call.result.unwrap();
                assert_eq!((actual.beg_idx, actual.count), (range.beg_idx, range.count));
                let Output::Real(values) = &output[0] else {
                    unreachable!()
                };
                assert!(values[..range.beg_idx].iter().all(|x| x.is_nan()));
                for (a, b) in values[range.beg_idx..range.beg_idx + range.count]
                    .iter()
                    .zip(&expected[..range.count])
                {
                    assert!(
                        a.to_bits() == b.to_bits() || (a.is_nan() && b.is_nan()),
                        "mode{mode}/p{period}"
                    );
                }
                assert!(values[range.beg_idx + range.count..]
                    .iter()
                    .all(|x| x.is_nan()));
            }
        }
    }
}
