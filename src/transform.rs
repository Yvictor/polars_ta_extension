use crate::utils::{cast_series_to_f64, get_series_f64_ptr, ta_code2err};
use polars::prelude::*;
use pyo3_polars::derive::polars_expr;
use talib::transform::ta_avgprice;
use talib::transform::ta_medprice;
use talib::transform::ta_typprice;
use talib::transform::ta_wclprice;
use talib::transform::{ta_avgdev};
use talib::common::TimePeriodKwargs;
use talib::transform::{ta_ha};

#[polars_expr(output_type=Float64)]
fn avgprice(inputs: &[Series]) -> PolarsResult<Series> {
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
fn medprice(inputs: &[Series]) -> PolarsResult<Series> {
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
fn typprice(inputs: &[Series]) -> PolarsResult<Series> {
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
fn wclprice(inputs: &[Series]) -> PolarsResult<Series> {
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

#[polars_expr(output_type=Float64)]
fn avgdev(inputs: &[Series], kwargs: TimePeriodKwargs) -> PolarsResult<Series> {
    let real = &mut cast_series_to_f64(&inputs[0])?;
    let (real_ptr, _real) = get_series_f64_ptr(real)?;
    let len = real.len();
    let res = ta_avgdev(real_ptr, len, &kwargs);
    match res {
        Ok(out) => Ok(Float64Chunked::from_vec("", out).into_series()),
        Err(ret_code) => ta_code2err(ret_code),
    }
}

pub fn ha_output(_: &[Field]) -> PolarsResult<Field> {
    let haopen = Field::new("haopen", DataType::Float64);
    let hahigh = Field::new("hahigh", DataType::Float64);
    let halow = Field::new("halow", DataType::Float64);
    let haclose = Field::new("haclose", DataType::Float64);
    let v: Vec<Field> = vec![haopen, hahigh, halow, haclose];
    Ok(Field::new("", DataType::Struct(v)))
}

#[polars_expr(output_type_func=ha_output)]
fn ha(inputs: &[Series]) -> PolarsResult<Series> {
    let open = &mut cast_series_to_f64(&inputs[0])?;
    let high = &mut cast_series_to_f64(&inputs[1])?;
    let low = &mut cast_series_to_f64(&inputs[2])?;
    let close = &mut cast_series_to_f64(&inputs[3])?;
    let (open_ptr, _open) = get_series_f64_ptr(open)?;
    let (high_ptr, _high) = get_series_f64_ptr(high)?;
    let (low_ptr, _low) = get_series_f64_ptr(low)?;
    let (close_ptr, _close) = get_series_f64_ptr(close)?;
    let len = open.len();
    let res = ta_ha(open_ptr, high_ptr, low_ptr, close_ptr, len);
    match res {
        Ok((outhaopen, outhahigh, outhalow, outhaclose)) => {
            let haopen = Series::from_vec("haopen", outhaopen);
            let hahigh = Series::from_vec("hahigh", outhahigh);
            let halow = Series::from_vec("halow", outhalow);
            let haclose = Series::from_vec("haclose", outhaclose);
            let out = StructChunked::new("", &[haopen, hahigh, halow, haclose])?;
            Ok(out.into_series())
        }
        Err(ret_code) => ta_code2err(ret_code),
    }
}
