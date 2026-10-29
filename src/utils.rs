use polars::datatypes::DataType;
use polars::prelude::{PolarsError, PolarsResult, Series};
use std::borrow::Cow;

pub fn cast_series_to_f64(series: &Series) -> PolarsResult<Series> {
    let values = match series.dtype() {
        DataType::Float64 => Ok(series.clone()),
        _ => series.cast(&DataType::Float64),
    }?;
    Ok(if values.n_chunks() == 1 {
        values
    } else {
        values.rechunk()
    })
}

/// Align plugin inputs before handing borrowed buffers to TA-Lib: length-1 inputs
/// (Polars literals) broadcast to the common length, anything else must match.
pub fn broadcast_inputs(inputs: &[Series]) -> PolarsResult<Cow<'_, [Series]>> {
    // A scalar also broadcasts to zero rows. Taking max(0, 1) would reject
    // a valid filtered-to-empty column paired with a literal.
    let len = inputs
        .iter()
        .map(|s| s.len())
        .find(|&len| len != 1)
        .unwrap_or(1);
    if inputs.iter().all(|s| s.len() == len) {
        return Ok(Cow::Borrowed(inputs));
    }
    inputs
        .iter()
        .map(|s| {
            if s.len() == len {
                Ok(s.clone())
            } else if s.len() == 1 {
                Ok(s.new_from_index(0, len))
            } else {
                Err(PolarsError::ShapeMismatch(
                    "indicator input lengths differ".into(),
                ))
            }
        })
        .collect::<PolarsResult<Vec<_>>>()
        .map(Cow::Owned)
}

#[cfg(test)]
mod tests {
    use super::*;
    use polars::prelude::NamedFrom;

    #[test]
    fn sliced_float_validity_and_ieee_values_are_preserved() {
        let source = Series::new(
            "values",
            &[
                Some(1.),
                None,
                Some(-0.),
                Some(f64::INFINITY),
                Some(f64::NAN),
                Some(8.),
            ],
        );
        let source = source.slice(1, 4);
        let result = cast_series_to_f64(&source).unwrap();
        let values = result.f64().unwrap();
        assert_eq!(result.len(), 4);
        assert_eq!(result.null_count(), 1);
        assert_eq!(values.get(0), None);
        assert_eq!(values.get(1).unwrap().to_bits(), (-0.0f64).to_bits());
        assert_eq!(values.get(2), Some(f64::INFINITY));
        assert!(values.get(3).unwrap().is_nan());
    }

    #[test]
    fn sliced_integer_chunks_produce_the_required_contiguous_float_buffer() {
        let mut source = Series::new("values", &[10i64, -2, 7]);
        source.append(&Series::new("values", &[0i64, 99])).unwrap();
        let result = cast_series_to_f64(&source.slice(1, 3)).unwrap();
        assert_eq!(result.f64().unwrap().cont_slice().unwrap(), &[-2., 7., 0.]);
    }
}
