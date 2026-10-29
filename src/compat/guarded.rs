// Bindings for the explicitly preserved legacy EMA family.
use super::*;
// A classification is valid only for the same function and immutable slice.
// Construction stays private so unrelated callers cannot bypass the guard.
#[derive(Clone, Copy)]
pub(crate) struct FirstInputClass<'a> {
    id: FuncId,
    input: &'a [f64],
    trigger: bool,
}
impl FirstInputClass<'_> {
    fn for_input(self, id: FuncId, input: &[f64]) -> Option<bool> {
        (self.id == id && std::ptr::eq(self.input, input)).then_some(self.trigger)
    }
}

pub(crate) fn initialized_first<'a>(
    id: FuncId,
    input: &'a [f64],
    p: &Params,
    begin: usize,
    offset: usize,
) -> Option<(Vec<f64>, FirstInputClass<'a>)> {
    if offset >= input.len()
        || !matches!(id, FuncId::VAR | FuncId::STDDEV | FuncId::CORREL | FuncId::BBANDS | FuncId::MACD)
        || p.iter().any(|(key, value)| {
            key.contains("period") && matches!(value, Param::Int(v) if *v > 128)
        })
    {
        return None;
    }
    let first = input.get(begin..)?;
    if first.first().is_some_and(|v| !v.is_finite() || v.abs() > 1024.) {
        return None;
    }
    let mut output = Vec::with_capacity(input.len());
    output.resize(begin, f64::NAN);
    output.extend(first.iter().map(|_| f64::NAN));
    let trigger = has_trigger(first);
    Some((output, FirstInputClass { id, input: first, trigger }))
}

pub fn guarded_call(
    id: FuncId,
    input: &[&[f64]],
    p: &Params,
    outputs: &mut [Output],
    offset: usize,
    first_class: Option<FirstInputClass<'_>>,
) -> Option<Result<OutRange, RetCode>> {
    if !supports(id) {
        return None;
    }
    // Conservative routing preserves original arithmetic for large offsets,
    // long smoothing periods and nonfinite/overflow inputs.
    let long_period = p
        .iter()
        .any(|(key, value)| key.contains("period") && matches!(value,Param::Int(v) if *v>128));
    if id != FuncId::ADOSC
        && !long_period
        && !input.iter().enumerate().any(|(index, values)| {
            if index == 0 {
                first_class
                    .and_then(|proof| proof.for_input(id, values))
                    .unwrap_or_else(|| has_trigger(values))
            } else {
                has_trigger(values)
            }
        })
    {
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
        .fold(false, |bad, v| bad | !(v.abs() <= 1024.))
}

#[cfg(test)]
mod scan_tests {
    use super::has_trigger;
    #[test]
    fn fused_initialization_preserves_bits_and_shifted_predicate() {
        use super::*;
        let mut state = 0x291026_u64;
        for len in [1usize, 2, 7, 31, 100, 1000] {
            for begin in [0, len / 2, len - 1] {
                for _ in 0..128 {
                    let mut input = vec![100.; len];
                    input[..begin].fill(f64::NAN);
                    for value in input.iter_mut().skip(begin + 1) {
                        state = state.wrapping_mul(6364136223846793005).wrapping_add(1);
                        *value = f64::from_bits(state);
                    }
                    for id in [FuncId::VAR, FuncId::STDDEV, FuncId::CORREL, FuncId::BBANDS, FuncId::MACD] {
                        let (out, class) = initialized_first(id, &input, &Params::new(), begin, begin).unwrap();
                        assert_eq!(out.len(), len);
                        assert_eq!(out.capacity(), len);
                        assert!(out.iter().all(|v| v.to_bits() == f64::NAN.to_bits()));
                        assert_eq!(class.for_input(id, &input[begin..]), Some(has_trigger(&input[begin..])));
                    }
                }
            }
        }
    }

    #[test]
    fn fused_token_includes_function_pointer_and_slice_length() {
        use super::*;
        let values = [1., 2., 3., f64::NAN];
        let (_, class) = initialized_first(FuncId::VAR, &values[..3], &Params::new(), 0, 0).unwrap();
        assert_eq!(class.for_input(FuncId::VAR, &values[..3]), Some(false));
        assert_eq!(class.for_input(FuncId::STDDEV, &values[..3]), None);
        assert_eq!(class.for_input(FuncId::VAR, &values[..4]), None);
        assert_eq!(class.for_input(FuncId::VAR, &values[1..]), None);
        let distinct = [1., 2., 3.];
        assert_eq!(class.for_input(FuncId::VAR, &distinct), None);
    }

    #[test]
    fn fusion_skips_forced_unsupported_first_trigger_and_no_call() {
        use super::*;
        let values = [1., 2., 3.];
        for id in [FuncId::EMA, FuncId::ADOSC, FuncId::SMA, FuncId::SAREXT] {
            assert!(initialized_first(id, &values, &Params::new(), 0, 0).is_none());
        }
        assert!(initialized_first(FuncId::VAR, &values, &Params::new(), usize::MAX, values.len()).is_none());
        assert!(initialized_first(FuncId::VAR, &values, &Params::new(), usize::MAX, 0).is_none());
        assert!(initialized_first(FuncId::VAR, &[], &Params::new(), usize::MAX, 0).is_none());
        for trigger in [f64::NAN, f64::INFINITY, f64::NEG_INFINITY, 1025., -1025.] {
            assert!(initialized_first(FuncId::VAR, &[trigger, 1.], &Params::new(), 0, 0).is_none());
        }
        for period in [i32::MIN, 0, 30, 128, 129, 10000] {
            let params = [("timeperiod".to_owned(), Param::Int(period))].into_iter().collect();
            assert_eq!(initialized_first(FuncId::VAR, &values, &params, 0, 0).is_none(), period > 128);
        }
        let params = [("unrelated".to_owned(), Param::Int(10000))].into_iter().collect();
        assert!(initialized_first(FuncId::VAR, &values, &params, 0, 0).is_some());
    }

    #[test]
    fn classification_cannot_hide_second_input_trigger_or_change_guard_result() {
        use super::*;
        let a = vec![1.; 256];
        let mut b = vec![2.; 256];
        b[200] = 2048.;
        for id in [FuncId::VAR, FuncId::STDDEV, FuncId::CORREL, FuncId::BBANDS, FuncId::MACD] {
            let params = Params::new();
            let offset = id.new_call(crate::native::core()).lookback().unwrap();
            let (_, class) = initialized_first(id, &a, &params, 0, offset).unwrap();
            let input_values = [a.as_slice(), b.as_slice()];
            let inputs = &input_values[..if id == FuncId::CORREL { 2 } else { 1 }];
            let mut old: Vec<Output> = id.info().outputs.iter().map(|_| Output::Real(vec![f64::NAN; 256])).collect();
            let mut new: Vec<Output> = id.info().outputs.iter().map(|_| Output::Real(vec![f64::NAN; 256])).collect();
            let expected = guarded_call(id, inputs, &params, &mut old, offset, None);
            let actual = guarded_call(id, inputs, &params, &mut new, offset, Some(class));
            assert_eq!(expected, actual);
            assert_eq!(expected.is_some(), id == FuncId::CORREL);
            if let Some(result) = expected {
                assert!(result.is_ok(), "the legacy branch must actually write valid outputs");
            }
            for (old, new) in old.iter().zip(&new) {
                if let (Output::Real(old), Output::Real(new)) = (old, new) {
                    assert!(old.iter().zip(new).all(|(a, b)| a.to_bits() == b.to_bits()));
                }
            }
        }
    }

    #[test]
    fn unordered_bound_matches_ieee_routing_predicate() {
        let mut state = 0x9137_a822_45cf_672du64;
        for _ in 0..100_000 {
            state = state.wrapping_mul(6364136223846793005).wrapping_add(1);
            let value = f64::from_bits(state);
            assert_eq!(
                !(value.abs() <= 1024.),
                !value.is_finite() || value.abs() > 1024.
            );
        }
        for bits in [
            0,
            1,
            0x8000_0000_0000_0000,
            0x7ff0_0000_0000_0000,
            0xfff0_0000_0000_0000,
            0x7ff0_0000_0000_0001,
            0x7ff8_0000_0000_0001,
            1024f64.to_bits() - 1,
            1024f64.to_bits(),
            1024f64.to_bits() + 1,
        ] {
            let value = f64::from_bits(bits);
            assert_eq!(
                !(value.abs() <= 1024.),
                !value.is_finite() || value.abs() > 1024.
            );
            assert_eq!(
                has_trigger(&[0., value]),
                !value.is_finite() || value.abs() > 1024.
            );
        }
    }

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
