//! Legacy semantics absent from ta-lib 0.8.3. All code uses checked slices.
//! Batch-only kernels adapted from the official v0.8.1 tag; BSD notice in each file.
//! Normal inputs use the 0.8.3 crate except RSI/STOCHRSI and index tie handling.
#![allow(non_snake_case)]
use ta_lib::{Core, MAType, OutRange, RetCode};
mod cmou;
mod correl;
mod mavp;
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

/// Returns None when the released crate can preserve this call's semantics.
pub fn call(
    id: FuncId,
    input: &[&[f64]],
    p: &Params,
    outputs: &mut [Output],
    offset: usize,
) -> Option<Result<OutRange, RetCode>> {
    use FuncId::*;
    if let Some(result) = guarded::guarded_call(id, input, p, outputs, offset) {
        return Some(result);
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
    let needs_nonfinite = matches!(id, CMOU | PERCENTILE | VAR | STDDEV | CORREL);
    let nonfinite = needs_nonfinite && input.iter().any(|s| s.iter().any(|v| !v.is_finite()));
    Some(match (id, outputs) {
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
                Err(e) => return Some(Err(e)),
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
        (VAR, [Output::Real(out)]) if nonfinite => LEGACY.var(
            0,
            end,
            input[0],
            period,
            real(p, "nbdev", 1.),
            &mut out[offset..],
        ),
        (STDDEV, [Output::Real(out)]) if nonfinite => LEGACY
            .var(0, end, input[0], period, 1., &mut out[offset..])
            .map(|range| {
                let scale = real(p, "nbdev", 1.);
                for v in &mut out[offset..offset + range.count] {
                    *v = v.sqrt() * scale;
                }
                range
            }),
        (CORREL, [Output::Real(out)]) if nonfinite => {
            LEGACY.correl(0, end, input[0], input[1], period, &mut out[offset..])
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
                    Err(e) => return Some(Err(e)),
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
