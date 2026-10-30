//! SAREXT's fixed option layout and supported typed Core call.
#![forbid(unsafe_code)]
use crate::{native, params::Param};
use polars::prelude::*;
use serde::{de, Deserialize, Deserializer};
use ta_lib::{abstract_api::FuncId, Core, OutRange, RetCode};

#[derive(Debug, Clone, Copy)]
pub(crate) struct SarExtParams {
    pub(crate) startvalue: f64,
    pub(crate) offsetonreverse: f64,
    pub(crate) accelerationinitlong: f64,
    pub(crate) accelerationlong: f64,
    pub(crate) accelerationmaxlong: f64,
    pub(crate) accelerationinitshort: f64,
    pub(crate) accelerationshort: f64,
    pub(crate) accelerationmaxshort: f64,
}
impl Default for SarExtParams {
    fn default() -> Self {
        Self {
            startvalue: 0.,
            offsetonreverse: 0.,
            accelerationinitlong: 0.02,
            accelerationlong: 0.02,
            accelerationmaxlong: 0.2,
            accelerationinitshort: 0.02,
            accelerationshort: 0.02,
            accelerationmaxshort: 0.2,
        }
    }
}
impl<'de> Deserialize<'de> for SarExtParams {
    fn deserialize<D: Deserializer<'de>>(deserializer: D) -> Result<Self, D::Error> {
        struct Options;
        impl<'de> de::Visitor<'de> for Options {
            type Value = SarExtParams;
            fn expecting(&self, formatter: &mut std::fmt::Formatter) -> std::fmt::Result {
                formatter.write_str("a map")
            }
            fn visit_map<M: de::MapAccess<'de>>(self, mut map: M) -> Result<Self::Value, M::Error> {
                let mut options = SarExtParams::default();
                // Decode unknown values too: the existing map rejects nonnumeric
                // values even when binding would ignore their key. Repeated keys
                // retain the map's last-value-wins behavior after each value is read.
                while let Some((key, value)) = map.next_entry::<String, Param>()? {
                    let value = match value {
                        Param::Int(v) => f64::from(v),
                        Param::Real(v) => v,
                    };
                    match key.as_str() {
                        "startvalue" => options.startvalue = value,
                        "offsetonreverse" => options.offsetonreverse = value,
                        "accelerationinitlong" => options.accelerationinitlong = value,
                        "accelerationlong" => options.accelerationlong = value,
                        "accelerationmaxlong" => options.accelerationmaxlong = value,
                        "accelerationinitshort" => options.accelerationinitshort = value,
                        "accelerationshort" => options.accelerationshort = value,
                        "accelerationmaxshort" => options.accelerationmaxshort = value,
                        _ => {}
                    }
                }
                Ok(options)
            }
        }
        deserializer.deserialize_map(Options)
    }
}
impl SarExtParams {
    fn lookback(&self, core: &Core) -> Result<usize, RetCode> {
        core.sarext_lookback(
            self.startvalue,
            self.offsetonreverse,
            self.accelerationinitlong,
            self.accelerationlong,
            self.accelerationmaxlong,
            self.accelerationinitshort,
            self.accelerationshort,
            self.accelerationmaxshort,
        )
    }
    fn call(
        &self,
        core: &Core,
        high: &[f64],
        low: &[f64],
        output: &mut [f64],
    ) -> Result<OutRange, RetCode> {
        crate::sarext_legacy::call(
            core,
            0,
            high.len() - 1,
            high,
            low,
            self.startvalue,
            self.offsetonreverse,
            self.accelerationinitlong,
            self.accelerationlong,
            self.accelerationmaxlong,
            self.accelerationinitshort,
            self.accelerationshort,
            self.accelerationmaxshort,
            output,
        )
    }
}

pub(crate) fn compute(inputs: &[Series], params: &SarExtParams) -> PolarsResult<Series> {
    let prepared = native::prepare_inputs::<2, 1>(FuncId::SAREXT, inputs, &[0, 1])?;
    let slices = native::prepared_slices(&prepared)?;
    let len = native::checked_input_len(&slices)?;
    // Parameter validation stays after preparation and before begin/output work,
    // including on empty and warm-up-only inputs. Use the official defaults,
    // range guards and REAL_DEFAULT semantics through the public typed API.
    let lookback = params.lookback(native::core()).map_err(native::error)?;
    let begin = native::first_usable(&slices, len);
    let offset = begin.saturating_add(lookback).min(len);
    let mut output = vec![f64::NAN; len];
    let mut written = 0;
    if offset < len {
        let range = params
            .call(
                native::core(),
                &slices[0][begin..],
                &slices[1][begin..],
                &mut output[offset..],
            )
            .map_err(native::error)?;
        polars_ensure!(range.beg_idx == lookback && range.count <= len-offset,
            ComputeError: "unexpected TA-Lib output range");
        written = range.count;
    }
    Ok(native::output_series(
        native::Output::Real(output),
        "",
        offset,
        written,
    ))
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::{
        missing::Masked,
        native::{Param, Params},
    };
    use ta_lib::abstract_api::{InputType, OptInputType, OutputType};

    const KEYS: [&str; 8] = [
        "startvalue",
        "offsetonreverse",
        "accelerationinitlong",
        "accelerationlong",
        "accelerationmaxlong",
        "accelerationinitshort",
        "accelerationshort",
        "accelerationmaxshort",
    ];
    fn values(p: &SarExtParams) -> [f64; 8] {
        [
            p.startvalue,
            p.offsetonreverse,
            p.accelerationinitlong,
            p.accelerationlong,
            p.accelerationmaxlong,
            p.accelerationinitshort,
            p.accelerationshort,
            p.accelerationmaxshort,
        ]
    }
    fn from_map(p: &Params) -> SarExtParams {
        let mut v = values(&SarExtParams::default());
        for (i, k) in KEYS.iter().enumerate() {
            if let Some(x) = p.get(*k) {
                v[i] = match x {
                    Param::Int(n) => f64::from(*n),
                    Param::Real(x) => *x,
                };
            }
        }
        SarExtParams {
            startvalue: v[0],
            offsetonreverse: v[1],
            accelerationinitlong: v[2],
            accelerationlong: v[3],
            accelerationmaxlong: v[4],
            accelerationinitshort: v[5],
            accelerationshort: v[6],
            accelerationmaxshort: v[7],
        }
    }
    fn to_map(p: &SarExtParams) -> Params {
        KEYS.into_iter()
            .zip(values(p))
            .map(|(k, v)| (k.into(), Param::Real(v)))
            .collect()
    }
    fn compare_series(actual: Series, expected: Series) {
        assert_eq!(actual.dtype(), expected.dtype());
        assert_eq!(actual.name(), expected.name());
        assert_eq!(actual.len(), expected.len());
        assert_eq!(actual.null_count(), expected.null_count());
        for (a, b) in actual
            .f64()
            .unwrap()
            .into_iter()
            .zip(expected.f64().unwrap())
        {
            match (a, b) {
                (Some(a), Some(b)) if a.is_nan() || b.is_nan() => assert!(a.is_nan() && b.is_nan()),
                (Some(a), Some(b)) if b.to_bits() == (-0.0f64).to_bits() && a.to_bits() == 0 => {
                    // Intentional C0.8.1 short-store compatibility; strict C
                    // reference tests below distinguish legitimate long -0.
                }
                (Some(a), Some(b)) => assert_eq!(a.to_bits(), b.to_bits()),
                (a, b) => assert_eq!(a, b),
            }
        }
    }

    #[test]
    fn exact_metadata_and_defaults_match_pinned_core_not_builder_defaults() {
        let info = FuncId::SAREXT.info();
        assert_eq!(info.inputs.len(), 1);
        assert!(matches!(info.inputs[0].kind, InputType::Price));
        assert_eq!(info.inputs[0].flags.0, 6);
        assert_eq!(info.outputs.len(), 1);
        assert!(matches!(info.outputs[0].kind, OutputType::Real));
        assert_eq!(info.opt_inputs.len(), 8);
        let defaults = values(&SarExtParams::default());
        assert_eq!(defaults, [0., 0., 0.02, 0.02, 0.2, 0.02, 0.02, 0.2]);
        for ((opt, key), value) in info.opt_inputs.iter().zip(KEYS).zip(defaults) {
            assert_eq!(crate::generated::option_key(opt.param_name), key);
            let OptInputType::RealRange { default, .. } = opt.kind else {
                panic!("real option")
            };
            assert_eq!(default.to_bits(), value.to_bits());
        }
        assert_eq!(SarExtParams::default().lookback(native::core()), Ok(1));
    }

    #[test]
    fn pickle_numeric_key_duplicate_unknown_and_error_contracts_match_map() {
        let mut tested = 0;
        for line in include_str!("../tests/data/sarext-params-pickle.hex")
            .lines()
            .filter(|x| !x.starts_with('#'))
        {
            let (label, hex) = line.split_once('\t').unwrap();
            let bytes = (0..hex.len())
                .step_by(2)
                .map(|i| u8::from_str_radix(&hex[i..i + 2], 16).unwrap())
                .collect::<Vec<_>>();
            let got = serde_pickle::from_slice::<SarExtParams>(&bytes, Default::default());
            let want = serde_pickle::from_slice::<Params>(&bytes, Default::default());
            match (got, want) {
                (Ok(a), Ok(b)) => {
                    assert_eq!(
                        values(&a).map(f64::to_bits),
                        values(&from_map(&b)).map(f64::to_bits),
                        "{label}"
                    );
                    let mut holder = FuncId::SAREXT.new_call(native::core());
                    native::bind_params(&mut holder, &b).unwrap();
                    assert_eq!(a.lookback(native::core()), holder.lookback(), "{label}");
                }
                (Err(a), Err(b)) => assert_eq!(a.to_string(), b.to_string(), "{label}"),
                (a, b) => panic!("{label}: {a:?} vs {b:?}"),
            }
            tested += 1;
        }
        assert_eq!(tested, 765);
    }

    #[test]
    fn actual_masked_envelope_matches_all_eight_map_fields() {
        let bytes = include_bytes!("../tests/data/kwargs-sarext-protocol5.pkl");
        let actual: Masked<SarExtParams> =
            serde_pickle::from_slice(bytes, Default::default()).unwrap();
        let expected: Masked<Params> = serde_pickle::from_slice(bytes, Default::default()).unwrap();
        assert_eq!(
            (actual.lookback, actual.recursive),
            (expected.lookback, expected.recursive)
        );
        assert_eq!(
            values(&actual.params).map(f64::to_bits),
            values(&from_map(&expected.params)).map(f64::to_bits)
        );
    }

    #[test]
    fn typed_execution_matches_core_except_declared_legacy_short_zero_boundary() {
        for len in [0, 1, 2, 3, 33, 1000] {
            let high: Vec<Option<f64>> = (0..len)
                .map(|i| match i % 19 {
                    0 => None,
                    1 => Some(f64::NAN),
                    2 => Some(f64::INFINITY),
                    3 => Some(f64::NEG_INFINITY),
                    4 => Some(-0.),
                    _ => Some(20. + (i % 13) as f64),
                })
                .collect();
            let low: Vec<Option<f64>> = (0..len)
                .map(|i| match i % 23 {
                    0 => Some(f64::NAN),
                    1 => None,
                    2 => Some(-0.),
                    3 => Some(0.),
                    _ => Some(10. + (i % 11) as f64),
                })
                .collect();
            let inputs = [Series::new("high", high), Series::new("low", low)];
            for v in [
                0.,
                -0.,
                0.1,
                -0.1,
                1.,
                -1.,
                Core::REAL_DEFAULT,
                Core::REAL_MIN,
                Core::REAL_MAX,
                f64::NAN,
                f64::INFINITY,
                f64::NEG_INFINITY,
            ] {
                for key in KEYS {
                    let map = Params::from([(key.into(), Param::Real(v))]);
                    let typed = from_map(&map);
                    let a = compute(&inputs, &typed);
                    let b = native::compute::<2, 1>(FuncId::SAREXT, &inputs, &map, &[0, 1], &[]);
                    match (a, b) {
                        (Ok(a), Ok(b)) => compare_series(a, b),
                        (Err(a), Err(b)) => assert_eq!(a.to_string(), b.to_string()),
                        (a, b) => panic!("len{len}/{key}/{v:?}: {a:?} vs {b:?}"),
                    }
                }
            }
        }
    }

    #[test]
    fn preparation_and_parameter_error_order_matches_generic_on_invalid_inputs() {
        let invalid = SarExtParams {
            startvalue: f64::NAN,
            ..Default::default()
        };
        let good = [
            Series::new("high", &[2., 3., 4.]),
            Series::new("low", &[1., 2., 3.]),
        ];
        let variants = [
            vec![],
            vec![good[0].clone()],
            vec![good[0].clone(), Series::new("low", &[1., 2.])],
            vec![Series::new("high", &["x", "y", "z"]), good[1].clone()],
            good.to_vec(),
        ];
        for p in [SarExtParams::default(), invalid] {
            for inputs in &variants {
                let a = compute(inputs, &p);
                let b = native::compute::<2, 1>(FuncId::SAREXT, inputs, &to_map(&p), &[0, 1], &[]);
                match (a, b) {
                    (Ok(a), Ok(b)) => compare_series(a, b),
                    (Err(a), Err(b)) => assert_eq!(a.to_string(), b.to_string()),
                    (a, b) => panic!("{a:?} vs {b:?}"),
                }
            }
        }
    }
    #[test]
    fn subtraction_and_negation_only_differ_at_positive_zero_for_non_nan_values() {
        let mut state = 0x8016_5d32_814e_774bu64;
        let fixed = [
            0u64,
            1,
            0x8000_0000_0000_0000,
            0x8000_0000_0000_0001,
            f64::INFINITY.to_bits(),
            f64::NEG_INFINITY.to_bits(),
            f64::MAX.to_bits(),
            (-f64::MAX).to_bits(),
            0x7ff8_0000_0000_0042,
            0xfff0_0000_0000_0001,
        ];
        for i in 0..65546 {
            state = state
                .wrapping_mul(6364136223846793005)
                .wrapping_add(1442695040888963407);
            let bits = if i < fixed.len() { fixed[i] } else { state };
            let value = f64::from_bits(bits);
            let old = 0.0 - value;
            let new = -value;
            if value.is_nan() {
                assert!(old.is_nan() && new.is_nan());
            } else if bits == 0 {
                assert_eq!(old.to_bits(), 0);
                assert_eq!(new.to_bits(), (-0.0f64).to_bits());
            } else {
                assert_eq!(old.to_bits(), new.to_bits());
            }
        }
    }

    #[test]
    fn legacy_short_zero_and_legitimate_long_negative_zero_are_distinct() {
        let p = SarExtParams {
            startvalue: -2.,
            accelerationinitshort: 0.5,
            accelerationshort: 0.,
            accelerationmaxshort: 0.5,
            ..Default::default()
        };
        let high = [-1., -1., -1., -1.];
        let low = [-2., -2., -2., -2.];
        let mut old = [123.; 8];
        let mut new = old;
        let range = p.call(native::core(), &high, &low, &mut old[2..6]).unwrap();
        let core_range = native::core()
            .sarext(
                0,
                3,
                &high,
                &low,
                p.startvalue,
                p.offsetonreverse,
                p.accelerationinitlong,
                p.accelerationlong,
                p.accelerationmaxlong,
                p.accelerationinitshort,
                p.accelerationshort,
                p.accelerationmaxshort,
                &mut new[2..6],
            )
            .unwrap();
        assert_eq!(range, core_range);
        assert_eq!(range.count, 3);
        assert_eq!(old[3].to_bits(), 0);
        assert_eq!(new[3].to_bits(), (-0.0f64).to_bits());
        assert_eq!(&old[..2], &[123.; 2]);
        assert_eq!(&old[5..], &[123.; 3]);
        let high = [2., 3., 4.];
        let low = [-0., 1., 2.];
        let mut output = [123.; 5];
        let range = SarExtParams::default()
            .call(native::core(), &high, &low, &mut output[1..4])
            .unwrap();
        assert_eq!(range.count, 2);
        assert_eq!(output[1].to_bits(), (-0.0f64).to_bits());
        assert_eq!(output[0], 123.);
        assert_eq!(&output[3..], &[123.; 2]);
    }
}
