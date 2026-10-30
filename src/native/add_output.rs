//! Construct ADD values once through safe Vec initialization.
#![forbid(unsafe_code)]

/// The adapter has already validated metadata, parameters and aligned inputs.
/// Decline unexpected lengths or an invalid prefix before allocating anything.
pub(super) fn try_build(left: &[f64], right: &[f64], begin: usize) -> Option<Vec<f64>> {
    if left.len() != right.len() {
        return None;
    }
    let left_values = left.get(begin..)?;
    let right_values = right.get(begin..)?;
    let mut output = Vec::with_capacity(left.len());
    output.resize(begin, f64::NAN);
    output.extend(left_values.iter().zip(right_values).map(|(&a, &b)| a + b));
    Some(output)
}

#[cfg(test)]
mod tests {
    use super::*;
    use ta_lib::{
        abstract_api::{FuncId, InputType, OutputType},
        Core,
    };

    #[test]
    fn pinned_add_metadata_is_two_reals_one_real_and_zero_lookback() {
        let info = FuncId::ADD.info();
        assert_eq!(info.inputs.len(), 2);
        assert!(info
            .inputs
            .iter()
            .all(|x| matches!(x.kind, InputType::Real)));
        assert!(info.opt_inputs.is_empty());
        assert_eq!(info.outputs.len(), 1);
        assert!(matches!(info.outputs[0].kind, OutputType::Real));
        assert_eq!(Core::new().add_lookback(), Ok(0));
    }

    #[test]
    fn all_ieee_pairs_and_prefixes_match_pinned_core_including_signed_zero() {
        let values = [
            f64::NEG_INFINITY,
            -f64::MAX,
            -2.,
            -1.,
            -0.,
            0.,
            f64::from_bits(1),
            1.,
            2.,
            f64::MAX,
            f64::INFINITY,
            f64::from_bits(0x7ff8_0000_0000_0042),
            f64::from_bits(0xfff0_0000_0000_0001),
        ];
        let core = Core::new();
        for a in values {
            for b in values {
                let left = [f64::NAN, a, a, a, a, a, a, a, a];
                let right = [f64::NAN, b, b, b, b, b, b, b, b];
                for begin in [0, 1, 3, left.len()] {
                    let got = try_build(&left, &right, begin).unwrap();
                    let mut expected = vec![f64::NAN; left.len()];
                    if begin < left.len() {
                        let range = core
                            .add(
                                0,
                                left.len() - begin - 1,
                                &left[begin..],
                                &right[begin..],
                                &mut expected[begin..],
                            )
                            .unwrap();
                        assert_eq!(range.beg_idx, 0);
                        assert_eq!(range.count, left.len() - begin);
                    }
                    for (actual, want) in got.iter().zip(&expected) {
                        if want.is_nan() {
                            assert!(actual.is_nan());
                        } else {
                            assert_eq!(actual.to_bits(), want.to_bits());
                        }
                    }
                    assert_eq!(got.len(), left.len());
                }
            }
        }
    }

    #[test]
    fn empty_all_prefix_and_invalid_shapes_preserve_contract() {
        assert!(try_build(&[], &[], 0).unwrap().is_empty());
        assert!(try_build(&[], &[], 1).is_none());
        assert!(try_build(&[1.], &[], 0).is_none());
        assert!(try_build(&[1.], &[2.], 2).is_none());
        let all_prefix = try_build(&[1.; 33], &[2.; 33], 33).unwrap();
        assert_eq!(all_prefix.len(), 33);
        assert!(all_prefix.iter().all(|x| x.to_bits() == f64::NAN.to_bits()));
    }

    #[test]
    fn adapter_keeps_metadata_errors_before_add_construction() {
        use crate::native::{compute, Params};
        use polars::prelude::*;
        let inputs = [
            Series::new("left", &[1., 2.]),
            Series::new("right", &[3., 4.]),
        ];
        assert!(compute::<2, 1>(FuncId::ADD, &inputs[..1], &Params::new(), &[0, 1], &[]).is_err());
        assert!(compute::<2, 1>(FuncId::ADD, &inputs, &Params::new(), &[0], &[]).is_err());
        let mismatched = [inputs[0].clone(), Series::new("right", &[1., 2., 3.])];
        assert!(compute::<2, 1>(FuncId::ADD, &mismatched, &Params::new(), &[0, 1], &[]).is_err());
        let result =
            compute::<2, 1>(FuncId::ADD, &inputs, &Params::new(), &[0, 1], &["sum"]).unwrap();
        assert_eq!(result.name(), "sum");
        assert_eq!(result.f64().unwrap().cont_slice().unwrap(), &[4., 6.]);
    }
}
