// Bindings for the explicitly preserved legacy EMA family.
use super::*;
pub fn guarded_call(
    id: FuncId,
    input: &[&[f64]],
    p: &Params,
    outputs: &mut [Output],
    offset: usize,
) -> Option<Result<OutRange, RetCode>> {
    if !supports(id) {
        return None;
    }
    // Conservative routing preserves original arithmetic for large offsets,
    // long smoothing periods and nonfinite/overflow inputs.
    let long_period = p
        .iter()
        .any(|(key, value)| key.contains("period") && matches!(value,Param::Int(v) if *v>128));
    if id != FuncId::ADOSC && !long_period && !input.iter().any(|s| has_trigger(s)) {
        return None;
    }
    let end = input[0].len() - 1;
    Some(match (id, outputs) {
        (FuncId::EMA, [Output::Real(out0)]) => LEGACY.ema(
            0,
            end,
            input[0],
            int(p, "timeperiod", 30),
            &mut out0[offset..],
        ),
        (FuncId::APO, [Output::Real(out0)]) => LEGACY.apo(
            0,
            end,
            input[0],
            int(p, "fastperiod", 12),
            int(p, "slowperiod", 26),
            match MAType::try_from(int(p, "matype", 1)) {
                Ok(v) => v,
                Err(e) => return Some(Err(e)),
            },
            &mut out0[offset..],
        ),
        (FuncId::MACD, [Output::Real(out0), Output::Real(out1), Output::Real(out2)]) => LEGACY
            .macd(
                0,
                end,
                input[0],
                int(p, "fastperiod", 12),
                int(p, "slowperiod", 26),
                int(p, "signalperiod", 9),
                &mut out0[offset..],
                &mut out1[offset..],
                &mut out2[offset..],
            ),
        (FuncId::MACDFIX, [Output::Real(out0), Output::Real(out1), Output::Real(out2)]) => LEGACY
            .macdfix(
                0,
                end,
                input[0],
                int(p, "signalperiod", 9),
                &mut out0[offset..],
                &mut out1[offset..],
                &mut out2[offset..],
            ),
        (FuncId::MACDEXT, [Output::Real(out0), Output::Real(out1), Output::Real(out2)]) => LEGACY
            .macdext(
                0,
                end,
                input[0],
                int(p, "fastperiod", 12),
                match MAType::try_from(int(p, "fastmatype", 0)) {
                    Ok(v) => v,
                    Err(e) => return Some(Err(e)),
                },
                int(p, "slowperiod", 26),
                match MAType::try_from(int(p, "slowmatype", 0)) {
                    Ok(v) => v,
                    Err(e) => return Some(Err(e)),
                },
                int(p, "signalperiod", 9),
                match MAType::try_from(int(p, "signalmatype", 0)) {
                    Ok(v) => v,
                    Err(e) => return Some(Err(e)),
                },
                &mut out0[offset..],
                &mut out1[offset..],
                &mut out2[offset..],
            ),
        (FuncId::ERI, [Output::Real(out0), Output::Real(out1)]) => LEGACY.eri(
            0,
            end,
            input[0],
            input[1],
            input[2],
            int(p, "timeperiod", 13),
            &mut out0[offset..],
            &mut out1[offset..],
        ),
        (FuncId::EFI, [Output::Real(out0)]) => LEGACY.efi(
            0,
            end,
            input[0],
            input[1],
            int(p, "timeperiod", 13),
            &mut out0[offset..],
        ),
        (FuncId::KC, [Output::Real(out0), Output::Real(out1), Output::Real(out2)]) => LEGACY.kc(
            0,
            end,
            input[0],
            input[1],
            input[2],
            int(p, "timeperiod", 20),
            int(p, "atrperiod", 10),
            real(p, "nbdev", 2.0),
            &mut out0[offset..],
            &mut out1[offset..],
            &mut out2[offset..],
        ),
        (FuncId::ZLEMA, [Output::Real(out0)]) => LEGACY.zlema(
            0,
            end,
            input[0],
            int(p, "timeperiod", 30),
            &mut out0[offset..],
        ),
        (FuncId::SMI, [Output::Real(out0), Output::Real(out1)]) => LEGACY.smi(
            0,
            end,
            input[0],
            input[1],
            input[2],
            int(p, "timeperiod", 13),
            int(p, "fastperiod", 2),
            int(p, "slowperiod", 25),
            int(p, "signalperiod", 9),
            &mut out0[offset..],
            &mut out1[offset..],
        ),
        (FuncId::TSI, [Output::Real(out0)]) => LEGACY.tsi(
            0,
            end,
            input[0],
            int(p, "firstperiod", 25),
            int(p, "secondperiod", 13),
            &mut out0[offset..],
        ),
        (FuncId::MA, [Output::Real(out0)]) => LEGACY.ma(
            0,
            end,
            input[0],
            int(p, "timeperiod", 30),
            match MAType::try_from(int(p, "matype", 0)) {
                Ok(v) => v,
                Err(e) => return Some(Err(e)),
            },
            &mut out0[offset..],
        ),
        (FuncId::DEMA, [Output::Real(out0)]) => LEGACY.dema(
            0,
            end,
            input[0],
            int(p, "timeperiod", 30),
            &mut out0[offset..],
        ),
        (FuncId::TEMA, [Output::Real(out0)]) => LEGACY.tema(
            0,
            end,
            input[0],
            int(p, "timeperiod", 30),
            &mut out0[offset..],
        ),
        (FuncId::T3, [Output::Real(out0)]) => LEGACY.t3(
            0,
            end,
            input[0],
            int(p, "timeperiod", 5),
            real(p, "vfactor", 0.7),
            &mut out0[offset..],
        ),
        (FuncId::ADOSC, [Output::Real(out0)]) => LEGACY.adosc(
            0,
            end,
            input[0],
            input[1],
            input[2],
            input[3],
            int(p, "fastperiod", 3),
            int(p, "slowperiod", 10),
            &mut out0[offset..],
        ),
        (FuncId::CMO, [Output::Real(out0)]) => LEGACY.cmo(
            0,
            end,
            input[0],
            int(p, "timeperiod", 14),
            &mut out0[offset..],
        ),
        (FuncId::TRIX, [Output::Real(out0)]) => LEGACY.trix(
            0,
            end,
            input[0],
            int(p, "timeperiod", 30),
            &mut out0[offset..],
        ),
        (FuncId::PPO, [Output::Real(out0)]) => LEGACY.ppo(
            0,
            end,
            input[0],
            int(p, "fastperiod", 12),
            int(p, "slowperiod", 26),
            match MAType::try_from(int(p, "matype", 1)) {
                Ok(v) => v,
                Err(e) => return Some(Err(e)),
            },
            &mut out0[offset..],
        ),
        (FuncId::PVO, [Output::Real(out0)]) => LEGACY.pvo(
            0,
            end,
            input[0],
            int(p, "fastperiod", 12),
            int(p, "slowperiod", 26),
            match MAType::try_from(int(p, "matype", 1)) {
                Ok(v) => v,
                Err(e) => return Some(Err(e)),
            },
            &mut out0[offset..],
        ),
        (FuncId::BBANDS, [Output::Real(out0), Output::Real(out1), Output::Real(out2)]) => LEGACY
            .bbands(
                0,
                end,
                input[0],
                int(p, "timeperiod", 20),
                real(p, "nbdevup", 2.0),
                real(p, "nbdevdn", 2.0),
                match MAType::try_from(int(p, "matype", 0)) {
                    Ok(v) => v,
                    Err(e) => return Some(Err(e)),
                },
                &mut out0[offset..],
                &mut out1[offset..],
                &mut out2[offset..],
            ),
        (FuncId::STDDEV, [Output::Real(out0)]) => LEGACY.stddev(
            0,
            end,
            input[0],
            int(p, "timeperiod", 5),
            real(p, "nbdev", 1.0),
            &mut out0[offset..],
        ),
        (FuncId::MAVP, [Output::Real(out0)]) => LEGACY.mavp(
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
            &mut out0[offset..],
        ),
        (FuncId::VAR, [Output::Real(out0)]) => LEGACY.var(
            0,
            end,
            input[0],
            int(p, "timeperiod", 5),
            real(p, "nbdev", 1.0),
            &mut out0[offset..],
        ),
        (FuncId::CORREL, [Output::Real(out0)]) => LEGACY.correl(
            0,
            end,
            input[0],
            input[1],
            int(p, "timeperiod", 30),
            &mut out0[offset..],
        ),
        _ => return None,
    })
}

pub fn supports(id: FuncId) -> bool {
    matches!(
        id,
        FuncId::EMA
            | FuncId::APO
            | FuncId::MACD
            | FuncId::MACDFIX
            | FuncId::MACDEXT
            | FuncId::ERI
            | FuncId::EFI
            | FuncId::KC
            | FuncId::ZLEMA
            | FuncId::SMI
            | FuncId::TSI
            | FuncId::MA
            | FuncId::DEMA
            | FuncId::TEMA
            | FuncId::T3
            | FuncId::ADOSC
            | FuncId::CMO
            | FuncId::TRIX
            | FuncId::PPO
            | FuncId::PVO
            | FuncId::BBANDS
            | FuncId::STDDEV
            | FuncId::MAVP
            | FuncId::VAR
            | FuncId::CORREL
    )
}

// A boolean reduction lets LLVM vectorize the normal all-finite scan while
// preserving the exact routing predicate. Large values at row zero stay cheap.
fn has_trigger(values: &[f64]) -> bool {
    if values
        .first()
        .is_some_and(|v| !v.is_finite() || v.abs() > 1024.)
    {
        return true;
    }
    values
        .iter()
        .fold(false, |bad, v| bad | !v.is_finite() | (v.abs() > 1024.))
}

#[cfg(test)]
mod scan_tests {
    use super::has_trigger;
    #[test]
    fn vectorizable_scan_matches_original_predicate() {
        let mut state = 19u64;
        let mut values = vec![100.; 1024];
        for len in [0, 1, 7, 8, 31, 128, 1024] {
            assert_eq!(
                has_trigger(&values[..len]),
                values[..len]
                    .iter()
                    .any(|v| !v.is_finite() || v.abs() > 1024.)
            );
            for position in 0..len {
                for value in [
                    f64::NAN,
                    f64::INFINITY,
                    f64::NEG_INFINITY,
                    1024.,
                    1024.00001,
                    -1025.,
                    0.,
                ] {
                    values[position] = value;
                    assert_eq!(
                        has_trigger(&values[..len]),
                        values[..len]
                            .iter()
                            .any(|v| !v.is_finite() || v.abs() > 1024.)
                    );
                }
                state = state.wrapping_mul(6364136223846793005).wrapping_add(1);
                values[position] = f64::from_bits(state);
                assert_eq!(
                    has_trigger(&values[..len]),
                    values[..len]
                        .iter()
                        .any(|v| !v.is_finite() || v.abs() > 1024.)
                );
                values[position] = 100.;
            }
        }
    }
}
