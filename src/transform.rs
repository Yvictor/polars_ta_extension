use crate::missing::{Masked, NoParams};
use crate::utils::{cast_series_to_f64, get_series_f64_ptr, ta_code2err};
use polars::prelude::*;
use pyo3_polars::derive::polars_expr;
use talib::transform::ta_avgprice;
use talib::transform::ta_medprice;
use talib::transform::ta_typprice;
use talib::transform::ta_wclprice;

#[polars_expr(output_type=Float64)]
fn avgprice(inputs: &[Series], kwargs: Masked<NoParams>) -> PolarsResult<Series> {
    kwargs.apply(inputs, |_| avgprice_unmasked(inputs))
}

fn avgprice_unmasked(inputs: &[Series]) -> PolarsResult<Series> {
    let inputs = &crate::utils::broadcast_inputs(inputs)?;
    let open = &mut cast_series_to_f64(&inputs[0])?;
    let high = &mut cast_series_to_f64(&inputs[1])?;
    let low = &mut cast_series_to_f64(&inputs[2])?;
    let close = &mut cast_series_to_f64(&inputs[3])?;
    let (open_ptr, _open) = get_series_f64_ptr(open)?;
    let (high_ptr, _high) = get_series_f64_ptr(high)?;
    let (low_ptr, _low) = get_series_f64_ptr(low)?;
    let (close_ptr, _close) = get_series_f64_ptr(close)?;
    let len = open.len();
    let res = ta_avgprice(open_ptr, high_ptr, low_ptr, close_ptr, len);
    match res {
        Ok(out) => Ok(Float64Chunked::from_vec("", out).into_series()),
        Err(ret_code) => ta_code2err(ret_code),
    }
}

#[polars_expr(output_type=Float64)]
fn medprice(inputs: &[Series], kwargs: Masked<NoParams>) -> PolarsResult<Series> {
    kwargs.apply(inputs, |_| medprice_unmasked(inputs))
}

fn medprice_unmasked(inputs: &[Series]) -> PolarsResult<Series> {
    let inputs = &crate::utils::broadcast_inputs(inputs)?;
    let high = &mut cast_series_to_f64(&inputs[0])?;
    let low = &mut cast_series_to_f64(&inputs[1])?;
    let (high_ptr, _high) = get_series_f64_ptr(high)?;
    let (low_ptr, _low) = get_series_f64_ptr(low)?;
    let len = high.len();
    let res = ta_medprice(high_ptr, low_ptr, len);
    match res {
        Ok(out) => Ok(Float64Chunked::from_vec("", out).into_series()),
        Err(ret_code) => ta_code2err(ret_code),
    }
}

#[polars_expr(output_type=Float64)]
fn typprice(inputs: &[Series], kwargs: Masked<NoParams>) -> PolarsResult<Series> {
    kwargs.apply(inputs, |_| typprice_unmasked(inputs))
}

fn typprice_unmasked(inputs: &[Series]) -> PolarsResult<Series> {
    let inputs = &crate::utils::broadcast_inputs(inputs)?;
    let high = &mut cast_series_to_f64(&inputs[1])?;
    let low = &mut cast_series_to_f64(&inputs[2])?;
    let close = &mut cast_series_to_f64(&inputs[0])?;
    let (high_ptr, _high) = get_series_f64_ptr(high)?;
    let (low_ptr, _low) = get_series_f64_ptr(low)?;
    let (close_ptr, _close) = get_series_f64_ptr(close)?;
    let len = high.len();
    let res = ta_typprice(high_ptr, low_ptr, close_ptr, len);
    match res {
        Ok(out) => Ok(Float64Chunked::from_vec("", out).into_series()),
        Err(ret_code) => ta_code2err(ret_code),
    }
}

#[polars_expr(output_type=Float64)]
fn wclprice(inputs: &[Series], kwargs: Masked<NoParams>) -> PolarsResult<Series> {
    kwargs.apply(inputs, |_| wclprice_unmasked(inputs))
}

fn wclprice_unmasked(inputs: &[Series]) -> PolarsResult<Series> {
    let inputs = &crate::utils::broadcast_inputs(inputs)?;
    let high = &mut cast_series_to_f64(&inputs[1])?;
    let low = &mut cast_series_to_f64(&inputs[2])?;
    let close = &mut cast_series_to_f64(&inputs[0])?;
    let (high_ptr, _high) = get_series_f64_ptr(high)?;
    let (low_ptr, _low) = get_series_f64_ptr(low)?;
    let (close_ptr, _close) = get_series_f64_ptr(close)?;
    let len = high.len();
    let res = ta_wclprice(high_ptr, low_ptr, close_ptr, len);
    match res {
        Ok(out) => Ok(Float64Chunked::from_vec("", out).into_series()),
        Err(ret_code) => ta_code2err(ret_code),
    }
}
