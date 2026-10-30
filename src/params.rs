//! Numeric plugin options, decoded without trial-deserialization errors.
use serde::{de, Deserialize, Deserializer};

#[derive(Debug)]
pub enum Param {
    Int(i32),
    Real(f64),
}
// The prior untagged derive tried i32 before f64, allocating a Serde error for
// every real parameter. Pickle already reports the numeric kind; preserve that
// distinction directly, including the old fallback of large integers to Real.
impl<'de> Deserialize<'de> for Param {
    fn deserialize<D: Deserializer<'de>>(deserializer: D) -> Result<Self, D::Error> {
        struct Numeric;
        impl<'de> de::Visitor<'de> for Numeric {
            type Value = Param;
            fn expecting(&self, formatter: &mut std::fmt::Formatter) -> std::fmt::Result {
                formatter.write_str("an integer or real parameter")
            }
            fn visit_i64<E: de::Error>(self, value: i64) -> Result<Param, E> {
                Ok(match i32::try_from(value) {
                    Ok(value) => Param::Int(value),
                    Err(_) => Param::Real(value as f64),
                })
            }
            fn visit_u64<E: de::Error>(self, value: u64) -> Result<Param, E> {
                Ok(match i32::try_from(value) {
                    Ok(value) => Param::Int(value),
                    Err(_) => Param::Real(value as f64),
                })
            }
            fn visit_f64<E: de::Error>(self, value: f64) -> Result<Param, E> {
                Ok(Param::Real(value))
            }
            fn visit_bool<E: de::Error>(self, _: bool) -> Result<Param, E> {
                Err(non_numeric())
            }
            fn visit_char<E: de::Error>(self, _: char) -> Result<Param, E> {
                Err(non_numeric())
            }
            fn visit_str<E: de::Error>(self, _: &str) -> Result<Param, E> {
                Err(non_numeric())
            }
            fn visit_bytes<E: de::Error>(self, _: &[u8]) -> Result<Param, E> {
                Err(non_numeric())
            }
            fn visit_unit<E: de::Error>(self) -> Result<Param, E> {
                Err(non_numeric())
            }
            fn visit_none<E: de::Error>(self) -> Result<Param, E> {
                Err(non_numeric())
            }
            fn visit_some<D: Deserializer<'de>>(self, value: D) -> Result<Param, D::Error> {
                de::IgnoredAny::deserialize(value)?;
                Err(non_numeric())
            }
            fn visit_seq<A: de::SeqAccess<'de>>(self, mut values: A) -> Result<Param, A::Error> {
                // The old derive decoded nested content before rejecting it.
                // Drain it so malformed nested values retain their exact error.
                while values.next_element::<de::IgnoredAny>()?.is_some() {}
                Err(non_numeric())
            }
            fn visit_map<A: de::MapAccess<'de>>(self, mut values: A) -> Result<Param, A::Error> {
                while values
                    .next_entry::<de::IgnoredAny, de::IgnoredAny>()?
                    .is_some()
                {}
                Err(non_numeric())
            }
        }
        fn non_numeric<E: de::Error>() -> E {
            E::custom("data did not match any variant of untagged enum Param")
        }
        deserializer.deserialize_any(Numeric)
    }
}

#[cfg(test)]
pub(crate) mod legacy {
    // Keep the old type name as well as its derive so failure messages match.
    #[derive(Debug, serde::Deserialize)]
    #[serde(untagged)]
    pub(crate) enum Param {
        Int(i32),
        Real(f64),
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::missing::Masked;
    use std::collections::BTreeMap;

    #[test]
    fn numeric_pickle_kinds_and_errors_match_untagged_decoder() {
        // Real Python pickle bytes, protocols 0..=5: i32/i64 boundaries, default
        // sentinels, huge integers, signed zero, nonfinite and nonnumeric values.
        for line in include_str!("../tests/data/param-values-pickle.hex")
            .lines()
            .filter(|s| !s.starts_with('#'))
        {
            let (label, hex) = line.split_once('\t').unwrap();
            let bytes = (0..hex.len())
                .step_by(2)
                .map(|i| u8::from_str_radix(&hex[i..i + 2], 16).unwrap())
                .collect::<Vec<_>>();
            let actual = serde_pickle::from_slice::<Param>(&bytes, Default::default());
            let expected = serde_pickle::from_slice::<legacy::Param>(&bytes, Default::default());
            match (actual, expected) {
                (Ok(Param::Int(a)), Ok(legacy::Param::Int(b))) => assert_eq!(a, b, "{label}"),
                (Ok(Param::Real(a)), Ok(legacy::Param::Real(b))) => {
                    assert_eq!(a.to_bits(), b.to_bits(), "{label}")
                }
                (Err(a), Err(b)) => assert_eq!(a.to_string(), b.to_string(), "{label}"),
                (actual, expected) => panic!("{label}: {actual:?} vs {expected:?}"),
            }
        }
    }

    #[test]
    fn actual_plugin_envelopes_preserve_all_fields() {
        for bytes in [
            &include_bytes!("../tests/data/kwargs-add-protocol5.pkl")[..],
            &include_bytes!("../tests/data/kwargs-ema-protocol5.pkl")[..],
            &include_bytes!("../tests/data/kwargs-atr-protocol5.pkl")[..],
            &include_bytes!("../tests/data/kwargs-macd-protocol5.pkl")[..],
            &include_bytes!("../tests/data/kwargs-bbands-protocol5.pkl")[..],
            &include_bytes!("../tests/data/kwargs-macdext-protocol5.pkl")[..],
            &include_bytes!("../tests/data/kwargs-sarext-protocol5.pkl")[..],
        ] {
            let actual: Masked<BTreeMap<String, Param>> =
                serde_pickle::from_slice(bytes, Default::default()).unwrap();
            let expected: Masked<BTreeMap<String, legacy::Param>> =
                serde_pickle::from_slice(bytes, Default::default()).unwrap();
            assert_eq!(
                (actual.lookback, actual.recursive),
                (expected.lookback, expected.recursive)
            );
            assert_eq!(actual.params.len(), expected.params.len());
            for ((ak, a), (bk, b)) in actual.params.iter().zip(&expected.params) {
                assert_eq!(ak, bk);
                match (a, b) {
                    (Param::Int(a), legacy::Param::Int(b)) => assert_eq!(a, b),
                    (Param::Real(a), legacy::Param::Real(b)) => {
                        assert_eq!(a.to_bits(), b.to_bits())
                    }
                    _ => panic!("numeric kind changed for {ak}"),
                }
            }
        }
    }
}
