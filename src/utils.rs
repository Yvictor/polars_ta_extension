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

/// A plugin must validate lengths before handing raw buffers to C.
pub fn validate_input_lengths(inputs: &[Series]) -> PolarsResult<()> {
    if let Some(first) = inputs.first() {
        if inputs.iter().any(|s| s.len() != first.len()) {
            return Err(PolarsError::ShapeMismatch(
                "TA-Lib inputs must have equal lengths".into(),
            ));
        }
    }
    Ok(())
}
