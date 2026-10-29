use polars::datatypes::DataType;
use polars::prelude::{PolarsError, PolarsResult, Series};
use std::borrow::Cow;

pub fn cast_series_to_f64(series: &Series) -> PolarsResult<Series> {
    Ok(match series.dtype() {
        DataType::Float64 => Ok(series.clone()),
        _ => series.cast(&DataType::Float64),
    }?
    .rechunk())
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
