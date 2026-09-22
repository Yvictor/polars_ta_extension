use polars::datatypes::DataType;
use polars::prelude::{ChunkFillNullValue, IntoSeries, PolarsError, PolarsResult, Series};
use talib_sys::TA_RetCode;

pub fn cast_series_to_f64(series: &Series) -> PolarsResult<Series> {
    Ok(match series.dtype() {
        DataType::Float64 => Ok(series.clone()),
        _ => series.cast(&DataType::Float64),
    }?
    .rechunk())
}

/// Borrow contiguous, non-null values: C never mutates its inputs.
/// The optional owner keeps a null-to-NaN conversion alive for the FFI call.
pub fn get_series_f64_ptr(series: &mut Series) -> PolarsResult<(*const f64, Option<Series>)> {
    if series.null_count() != 0 {
        let owner = series.f64()?.fill_null_with_values(f64::NAN)?.into_series();
        let ptr = owner.f64()?.cont_slice()?.as_ptr();
        Ok((ptr, Some(owner)))
    } else {
        Ok((series.f64()?.cont_slice()?.as_ptr(), None))
    }
}

pub fn ta_code2err(ret_code: TA_RetCode) -> PolarsResult<Series> {
    Err(PolarsError::ComputeError(
        format!("Could not compute indicator, err: {:?}", ret_code).into(),
    ))
}

/// Align plugin inputs before handing raw buffers to C: length-1 inputs
/// (Polars literals) broadcast to the common length, anything else must match.
pub fn broadcast_inputs(inputs: &[Series]) -> PolarsResult<Vec<Series>> {
    // A scalar also broadcasts to zero rows. Taking max(0, 1) would reject
    // a valid filtered-to-empty column paired with a literal.
    let len = inputs
        .iter()
        .map(|s| s.len())
        .find(|&len| len != 1)
        .unwrap_or(1);
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
        .collect()
}
