use crate::utils::{get_series_f64_ptr, ta_code2err};
use polars::prelude::*;
use pyo3_polars::derive::polars_expr;

use talib::overlap::{ta_bbands, ta_ema, BBANDSKwargs, EMAKwargs};

pub fn bbands_output(_: &[Field]) -> PolarsResult<Field> {
    let u = Field::new("upperband", DataType::Float64);
    let m = Field::new("middleband", DataType::Float64);
    let l = Field::new("lowerband", DataType::Float64);
    let v: Vec<Field> = vec![u, m, l];
    Ok(Field::new("", DataType::Struct(v)))
}

#[polars_expr(output_type_func=bbands_output)]
fn bbands(inputs: &[Series], kwargs: BBANDSKwargs) -> PolarsResult<Series> {
    let input = &mut inputs[0].to_float()?.rechunk();
    let (input_ptr, _input) = get_series_f64_ptr(input)?;
    let len = input.len();
    let res = ta_bbands(input_ptr, len, &kwargs);
    match res {
        Ok((outrealupperband, outrealmiddleband, outreallowerband)) => {
            let u = Series::from_vec("upperband", outrealupperband);
            let m = Series::from_vec("middleband", outrealmiddleband);
            let l = Series::from_vec("lowerband", outreallowerband);
            let out = StructChunked::new("", &[u, m, l])?;
            Ok(out.into_series())
        }
        Err(ret_code) => ta_code2err(ret_code),
    }
}

#[polars_expr(output_type=Float64)]
fn ema(inputs: &[Series], kwargs: EMAKwargs) -> PolarsResult<Series> {
    let input = &mut inputs[0].to_float()?.rechunk();
    let (input_ptr, _input) = get_series_f64_ptr(input)?;
    let len = input.len();
    // println!("has_validity: {}", input.has_validity());
    // println!("len: {}", input.len());
    // println!("null_count: {}", input.null_count());
    let res = ta_ema(input_ptr, len, &kwargs);
    match res {
        Ok(out) => Ok(Float64Chunked::from_vec("", out).into_series()),
        Err(ret_code) => ta_code2err(ret_code),
    }
}
