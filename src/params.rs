//! Numeric plugin options, decoded without trial-deserialization errors.
use serde::{de, Deserialize, Deserializer};

#[derive(Debug)]
pub enum Param {
    Int(i32),
    Real(f64),
}
// Keep empty and single-option calls small. A second distinct key promotes
// into the original uncapped tree; no fixed-capacity array crosses callbacks.
// Pickle's dictionary, memo and key-string allocations remain unchanged.
#[derive(Debug)]
pub enum Params {
    Empty,
    One(String, Param),
    Tree(std::collections::BTreeMap<String, Param>),
}

impl Default for Params {
    fn default() -> Self {
        Self::Empty
    }
}

impl Params {
    pub fn new() -> Self {
        Self::Empty
    }

    pub fn get(&self, key: &str) -> Option<&Param> {
        match self {
            Self::Empty => None,
            Self::One(k, value) => (k == key).then_some(value),
            Self::Tree(tree) => tree.get(key),
        }
    }

    pub fn iter(&self) -> impl Iterator<Item = (&String, &Param)> {
        let (one, tree) = match self {
            Self::Empty => (None, None),
            Self::One(key, value) => (Some((key, value)), None),
            Self::Tree(tree) => (None, Some(tree.iter())),
        };
        one.into_iter().chain(tree.into_iter().flatten())
    }

    pub fn insert(&mut self, key: String, value: Param) -> Option<Param> {
        match self {
            Self::Empty => {
                *self = Self::One(key, value);
                None
            }
            Self::One(k, current) if *k == key => Some(std::mem::replace(current, value)),
            Self::One(..) => {
                let Self::One(previous_key, previous_value) = std::mem::replace(self, Self::Empty)
                else {
                    unreachable!()
                };
                let mut tree = std::collections::BTreeMap::new();
                tree.insert(previous_key, previous_value);
                let replaced = tree.insert(key, value);
                *self = Self::Tree(tree);
                replaced
            }
            Self::Tree(tree) => tree.insert(key, value),
        }
    }

    #[cfg(test)]
    fn len(&self) -> usize {
        match self {
            Self::Empty => 0,
            Self::One(..) => 1,
            Self::Tree(tree) => tree.len(),
        }
    }
}

impl<const N: usize> From<[(String, Param); N]> for Params {
    fn from(values: [(String, Param); N]) -> Self {
        let mut params = Self::new();
        for (key, value) in values {
            params.insert(key, value);
        }
        params
    }
}

impl<'de> Deserialize<'de> for Params {
    fn deserialize<D: Deserializer<'de>>(deserializer: D) -> Result<Self, D::Error> {
        struct Map;
        impl<'de> de::Visitor<'de> for Map {
            type Value = Params;
            fn expecting(&self, f: &mut std::fmt::Formatter) -> std::fmt::Result {
                f.write_str("a map")
            }
            fn visit_map<A: de::MapAccess<'de>>(self, mut values: A) -> Result<Params, A::Error> {
                let mut params = Params::new();
                // Decode every key/value in wire order before replacing a prior
                // key, preserving errors even for overwritten/unknown values.
                while let Some((key, value)) = values.next_entry::<String, Param>()? {
                    params.insert(key, value);
                }
                Ok(params)
            }
        }
        deserializer.deserialize_map(Map)
    }
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
    fn singleton_promotes_only_on_a_distinct_key() {
        let mut values = Params::new();
        assert!(matches!(values, Params::Empty));
        assert!(values.insert("z".to_owned(), Param::Int(7)).is_none());
        assert!(matches!(values, Params::One(..)));
        assert!(matches!(
            values.insert("z".to_owned(), Param::Real(-0.0)),
            Some(Param::Int(7))
        ));
        assert!(matches!(values, Params::One(..)));
        assert!(values.insert("a".to_owned(), Param::Int(2)).is_none());
        assert!(matches!(values, Params::Tree(_)));
        assert!(
            matches!(values.get("z"), Some(Param::Real(value)) if value.to_bits() == (-0.0_f64).to_bits())
        );
        assert_eq!(
            values
                .iter()
                .map(|(key, _)| key.as_str())
                .collect::<Vec<_>>(),
            ["a", "z"]
        );
    }

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
            let actual: Masked<Params> =
                serde_pickle::from_slice(bytes, Default::default()).unwrap();
            let expected: Masked<BTreeMap<String, Param>> =
                serde_pickle::from_slice(bytes, Default::default()).unwrap();
            assert_eq!(
                (actual.lookback, actual.recursive),
                (expected.lookback, expected.recursive)
            );
            assert_eq!(actual.params.len(), expected.params.len());
            for (ak, b) in &expected.params {
                let a = actual.params.get(ak).unwrap();
                match (a, b) {
                    (Param::Int(a), Param::Int(b)) => assert_eq!(a, b),
                    (Param::Real(a), Param::Real(b)) => {
                        assert_eq!(a.to_bits(), b.to_bits())
                    }
                    _ => panic!("numeric kind changed for {ak}"),
                }
            }
        }
    }

    #[test]
    fn map_container_preserves_tree_values_and_wire_order_errors() {
        for line in include_str!("../tests/data/param-maps-pickle.hex")
            .lines()
            .filter(|line| !line.starts_with('#'))
        {
            let (label, hex) = line.split_once('\t').unwrap();
            let bytes: Vec<_> = (0..hex.len())
                .step_by(2)
                .map(|i| u8::from_str_radix(&hex[i..i + 2], 16).unwrap())
                .collect();
            let actual = serde_pickle::from_slice::<Params>(&bytes, Default::default());
            let expected =
                serde_pickle::from_slice::<BTreeMap<String, Param>>(&bytes, Default::default());
            match (actual, expected) {
                (Ok(actual), Ok(expected)) => {
                    assert_eq!(actual.len(), expected.len(), "{label}");
                    for (key, expected) in expected {
                        match (actual.get(&key), expected) {
                            (Some(Param::Int(a)), Param::Int(b)) => {
                                assert_eq!(*a, b, "{label}/{key}")
                            }
                            (Some(Param::Real(a)), Param::Real(b)) => {
                                assert_eq!(a.to_bits(), b.to_bits(), "{label}/{key}")
                            }
                            value => panic!("{label}/{key}: {value:?}"),
                        }
                    }
                }
                (Err(a), Err(b)) => assert_eq!(a.to_string(), b.to_string(), "{label}"),
                result => panic!("{label}: {result:?}"),
            }
        }
    }

    #[test]
    fn parameter_map_keeps_large_maps_duplicates_and_full_metadata_lookback() {
        let mut values = Params::new();
        for i in 0..64 {
            assert!(values.insert(format!("key{i}"), Param::Int(i)).is_none());
        }
        for i in [0, 7, 8, 63] {
            assert!(
                matches!(values.insert(format!("key{i}"), Param::Real(-0.0)), Some(Param::Int(v)) if v == i)
            );
            assert!(
                matches!(values.get(&format!("key{i}")), Some(Param::Real(v)) if v.to_bits() == (-0.0_f64).to_bits())
            );
        }
        assert_eq!(values.len(), 64);
        let id = ta_lib::abstract_api::FuncId::KSTEXT;
        assert_eq!(id.info().opt_inputs.len(), 11);
        let mut values = Params::new();
        for option in id.info().opt_inputs {
            use ta_lib::abstract_api::OptInputType;
            let value = match option.kind {
                OptInputType::IntegerRange { default, .. } => Param::Int(default),
                OptInputType::IntegerList { default, .. } => {
                    Param::Int(default.try_into().unwrap())
                }
                OptInputType::RealRange { default, .. }
                | OptInputType::RealList { default, .. } => Param::Real(default),
            };
            values.insert(
                crate::generated::option_key(option.param_name).into_owned(),
                value,
            );
        }
        let mut call = id.new_call(crate::native::core());
        crate::native::bind_params(&mut call, &values).unwrap();
        assert_eq!(
            call.lookback(),
            id.new_call(crate::native::core()).lookback()
        );
    }

    #[test]
    fn parameter_map_preserves_plugin_envelope_errors_and_unknown_fields() {
        for line in include_str!("../tests/data/param-map-envelopes-pickle.hex")
            .lines()
            .filter(|line| !line.starts_with('#'))
        {
            let (label, hex) = line.split_once('\t').unwrap();
            let bytes: Vec<_> = (0..hex.len())
                .step_by(2)
                .map(|i| u8::from_str_radix(&hex[i..i + 2], 16).unwrap())
                .collect();
            let actual = serde_pickle::from_slice::<Masked<Params>>(&bytes, Default::default());
            let expected = serde_pickle::from_slice::<Masked<BTreeMap<String, Param>>>(
                &bytes,
                Default::default(),
            );
            match (actual, expected) {
                (Ok(actual), Ok(expected)) => {
                    assert_eq!(
                        (actual.lookback, actual.recursive),
                        (expected.lookback, expected.recursive),
                        "{label}"
                    );
                    assert_eq!(actual.params.len(), expected.params.len(), "{label}");
                    for (key, expected) in expected.params {
                        match (actual.params.get(&key), expected) {
                            (Some(Param::Int(a)), Param::Int(b)) => {
                                assert_eq!(*a, b, "{label}/{key}")
                            }
                            (Some(Param::Real(a)), Param::Real(b)) => {
                                assert_eq!(a.to_bits(), b.to_bits(), "{label}/{key}")
                            }
                            value => panic!("{label}/{key}: {value:?}"),
                        }
                    }
                }
                (Err(a), Err(b)) => assert_eq!(a.to_string(), b.to_string(), "{label}"),
                result => panic!(
                    "container/envelope outcome differs: {label}, ok states {:?}",
                    (result.0.is_ok(), result.1.is_ok())
                ),
            }
        }
    }
}
