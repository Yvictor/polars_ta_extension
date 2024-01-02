use crate::utils::{get_series_f64_ptr, ta_code2err};
use polars::prelude::*;
use pyo3_polars::derive::polars_expr;
use talib::momentum::{ta_adx, ADXKwargs, ta_aroon, ArronKwargs};


#[polars_expr(output_type=Float64)]
fn adx(inputs: &[Series], kwargs: ADXKwargs) -> PolarsResult<Series> {
    let high = &mut inputs[1].to_float()?.rechunk();
    let low = &mut inputs[2].to_float()?.rechunk();
    let close = &mut inputs[0].to_float()?.rechunk();
    let (high_ptr, _high) = get_series_f64_ptr(high)?;
    let (low_ptr, _low) = get_series_f64_ptr(low)?;
    let (close_ptr, _close) = get_series_f64_ptr(close)?;
    let len = close.len();
    let res = ta_adx(high_ptr, low_ptr, close_ptr, len, &kwargs);
    match res {
        Ok(out) => Ok(Float64Chunked::from_vec("", out).into_series()),
        Err(ret_code) => ta_code2err(ret_code),
    }
}

pub fn arron_output(_: &[Field]) -> PolarsResult<Field> {
    let d = Field::new("aroondown", DataType::Float64);
    let u = Field::new("aroonup", DataType::Float64);
    let v: Vec<Field> = vec![d, u];
    Ok(Field::new("", DataType::Struct(v)))
}

#[polars_expr(output_type_func=arron_output)]
fn aroon(inputs: &[Series], kwargs: ArronKwargs) -> PolarsResult<Series> {
    let high = &mut inputs[0].to_float()?.rechunk();
    let low = &mut inputs[1].to_float()?.rechunk();    
    let (high_ptr, _high) = get_series_f64_ptr(high)?;
    let (low_ptr, _low) = get_series_f64_ptr(low)?;
    let len = high.len();
    let res = ta_aroon(high_ptr, low_ptr, len, &kwargs);
    match res {
        Ok((outaroondown, outaroonup)) => {
            let d = Series::from_vec("aroondown", outaroondown);
            let u = Series::from_vec("aroonup", outaroonup);
            let out = StructChunked::new("", &[d, u])?;
            Ok(out.into_series())
        }
        Err(ret_code) => ta_code2err(ret_code),
    }
}