use crate::utils::{get_series_f64_ptr, ta_code2err};
use polars::prelude::*;
use pyo3_polars::derive::polars_expr;
use talib::volume::ta_obv;

#[polars_expr(output_type=Float64)]
fn obv(inputs: &[Series]) -> PolarsResult<Series> {
    let close = &mut inputs[0].to_float()?.rechunk();
    let volume = &mut inputs[1].to_float()?.rechunk();
    let (close_ptr, _close) = get_series_f64_ptr(close)?;
    let (volume_ptr, _volume) = get_series_f64_ptr(volume)?;
    let len = close.len();
    let res = ta_obv(close_ptr, volume_ptr, len);
    match res {
        Ok(out) => Ok(Float64Chunked::from_vec("", out).into_series()),
        Err(ret_code) => ta_code2err(ret_code),
    }
}
