use crate::utils::{get_series_f64_ptr, ta_code2err};
use polars::prelude::*;
use pyo3_polars::derive::polars_expr;
use talib::pattern::{ta_cdlabandonedbaby, CDLABANDONEDBABYKwargs};

#[polars_expr(output_type=Int32)]
fn cdlabandonedbaby(inputs: &[Series], kwargs: CDLABANDONEDBABYKwargs) -> PolarsResult<Series> {
    let open = &mut inputs[0].to_float()?.rechunk();
    let high = &mut inputs[1].to_float()?.rechunk();
    let low = &mut inputs[2].to_float()?.rechunk();
    let close = &mut inputs[3].to_float()?.rechunk();
    let (open_ptr, _open) = get_series_f64_ptr(open)?;
    let (high_ptr, _high) = get_series_f64_ptr(high)?;
    let (low_ptr, _low) = get_series_f64_ptr(low)?;
    let (close_ptr, _close) = get_series_f64_ptr(close)?;
    let len = close.len();

    let res = ta_cdlabandonedbaby(open_ptr, high_ptr, low_ptr, close_ptr, len, &kwargs);
    match res {
        Ok(out) => Ok(Int32Chunked::from_vec("", out).into_series()),
        Err(ret_code) => ta_code2err(ret_code),
    }
}
