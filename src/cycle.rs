use crate::utils::{get_series_f64_ptr, ta_code2err};
use polars::prelude::*;
use pyo3_polars::derive::polars_expr;
use talib::cycle::ta_ht_dcperiod;

#[polars_expr(output_type=Float64)]
fn ht_dcperiod(inputs: &[Series]) -> PolarsResult<Series> {
    let mut real = inputs[0].to_float()?.rechunk();
    let (real_ptr, _real) = get_series_f64_ptr(&mut real)?;
    let res = ta_ht_dcperiod(real_ptr, real.len());
    match res {
        Ok(out) => Ok(Float64Chunked::from_vec("", out).into_series()),
        Err(ret_code) => ta_code2err(ret_code),
    }
}
