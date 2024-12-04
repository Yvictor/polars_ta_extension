use crate::utils::{cast_series_to_f64, get_series_f64_ptr, ta_code2err};
use polars::prelude::*;
use talib::volatility::{ta_atr, ta_natr, ta_trange, ATRKwargs, NATRKwargs};

// #[polars_expr(output_type=Float64)]
pub fn atr(inputs: &[Series], kwargs: ATRKwargs) -> PolarsResult<Series> {
    let close = &mut cast_series_to_f64(&inputs[0])?;
    let high = &mut cast_series_to_f64(&inputs[1])?;
    let low = &mut cast_series_to_f64(&inputs[2])?;
    let (high_ptr, _high) = get_series_f64_ptr(high)?;
    let (low_ptr, _low) = get_series_f64_ptr(low)?;
    let (close_ptr, _close) = get_series_f64_ptr(close)?;
    let len = close.len();
    let res = ta_atr(high_ptr, low_ptr, close_ptr, len, &kwargs);
    match res {
        Ok(out) => Ok(Float64Chunked::from_vec("".into(), out).into_series()),
        Err(ret_code) => ta_code2err(ret_code),
    }
}

// #[polars_expr(output_type=Float64)]
pub fn trange(inputs: &[Series]) -> PolarsResult<Series> {
    let close = &mut cast_series_to_f64(&inputs[0])?;
    let high = &mut cast_series_to_f64(&inputs[1])?;
    let low = &mut cast_series_to_f64(&inputs[2])?;
    let (high_ptr, _high) = get_series_f64_ptr(high)?;
    let (low_ptr, _low) = get_series_f64_ptr(low)?;
    let (close_ptr, _close) = get_series_f64_ptr(close)?;
    let len = close.len();
    let res = ta_trange(high_ptr, low_ptr, close_ptr, len);
    match res {
        Ok(out) => Ok(Float64Chunked::from_vec("".into(), out).into_series()),
        Err(ret_code) => ta_code2err(ret_code),
    }
}

// #[polars_expr(output_type=Float64)]
pub fn natr(inputs: &[Series], kwargs: NATRKwargs) -> PolarsResult<Series> {
    let close = &mut cast_series_to_f64(&inputs[0])?;
    let high = &mut cast_series_to_f64(&inputs[1])?;
    let low = &mut cast_series_to_f64(&inputs[2])?;
    let (high_ptr, _high) = get_series_f64_ptr(high)?;
    let (low_ptr, _low) = get_series_f64_ptr(low)?;
    let (close_ptr, _close) = get_series_f64_ptr(close)?;
    let len = close.len();

    let res = ta_natr(high_ptr, low_ptr, close_ptr, len, &kwargs);

    match res {
        Ok(out) => {
            let out_ser = Float64Chunked::from_vec("".into(), out);
            Ok(out_ser.into_series())
        }
        Err(ret_code) => ta_code2err(ret_code),
    }
}
