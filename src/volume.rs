use crate::utils::{cast_series_to_f64, get_series_f64_ptr, ta_code2err};
use polars::prelude::*;
use pyo3_polars::derive::polars_expr;
use talib::volume::{ta_ad, ta_adosc, ta_obv, ADOSCKwargs};
use talib::volume::{ta_cmf};
use talib::common::TimePeriodKwargs;
use talib::volume::{ta_efi};
use talib::volume::{ta_marketfi};
use talib::volume::{ta_nvi};
use talib::volume::{ta_pvi};
use talib::volume::{ta_pvo, PvoKwargs};
use talib::volume::{ta_pvt};
use talib::volume::{ta_rvol};
use talib::volume::{ta_vwap};

#[polars_expr(output_type=Float64)]
fn obv(inputs: &[Series]) -> PolarsResult<Series> {
    let close = &mut cast_series_to_f64(&inputs[0])?;
    let volume = &mut cast_series_to_f64(&inputs[1])?;
    let (close_ptr, _close) = get_series_f64_ptr(close)?;
    let (volume_ptr, _volume) = get_series_f64_ptr(volume)?;
    let len = close.len();
    let res = ta_obv(close_ptr, volume_ptr, len);
    match res {
        Ok(out) => Ok(Float64Chunked::from_vec("", out).into_series()),
        Err(ret_code) => ta_code2err(ret_code),
    }
}

#[polars_expr(output_type=Float64)]
fn ad(inputs: &[Series]) -> PolarsResult<Series> {
    let high = &mut cast_series_to_f64(&inputs[1])?;
    let low = &mut cast_series_to_f64(&inputs[2])?;
    let close = &mut cast_series_to_f64(&inputs[0])?;
    let volume = &mut cast_series_to_f64(&inputs[3])?;
    let (high_ptr, _high) = get_series_f64_ptr(high)?;
    let (low_ptr, _low) = get_series_f64_ptr(low)?;
    let (close_ptr, _close) = get_series_f64_ptr(close)?;
    let (volume_ptr, _volume) = get_series_f64_ptr(volume)?;
    let len = high.len();
    let res = ta_ad(high_ptr, low_ptr, close_ptr, volume_ptr, len);
    match res {
        Ok(out) => Ok(Float64Chunked::from_vec("", out).into_series()),
        Err(ret_code) => ta_code2err(ret_code),
    }
}

#[polars_expr(output_type=Float64)]
fn adosc(inputs: &[Series], kwargs: ADOSCKwargs) -> PolarsResult<Series> {
    let close = &mut cast_series_to_f64(&inputs[0])?;
    let high = &mut cast_series_to_f64(&inputs[1])?;
    let low = &mut cast_series_to_f64(&inputs[2])?;
    let volume = &mut cast_series_to_f64(&inputs[3])?;
    let (high_ptr, _high) = get_series_f64_ptr(high)?;
    let (low_ptr, _low) = get_series_f64_ptr(low)?;
    let (close_ptr, _close) = get_series_f64_ptr(close)?;
    let (volume_ptr, _volume) = get_series_f64_ptr(volume)?;
    let len = high.len();
    let res = ta_adosc(high_ptr, low_ptr, close_ptr, volume_ptr, len, &kwargs);
    match res {
        Ok(out) => Ok(Float64Chunked::from_vec("", out).into_series()),
        Err(ret_code) => ta_code2err(ret_code),
    }
}

#[polars_expr(output_type=Float64)]
fn cmf(inputs: &[Series], kwargs: TimePeriodKwargs) -> PolarsResult<Series> {
    let close = &mut cast_series_to_f64(&inputs[0])?;
    let high = &mut cast_series_to_f64(&inputs[1])?;
    let low = &mut cast_series_to_f64(&inputs[2])?;
    let volume = &mut cast_series_to_f64(&inputs[3])?;
    let (close_ptr, _close) = get_series_f64_ptr(close)?;
    let (high_ptr, _high) = get_series_f64_ptr(high)?;
    let (low_ptr, _low) = get_series_f64_ptr(low)?;
    let (volume_ptr, _volume) = get_series_f64_ptr(volume)?;
    let len = close.len();
    let res = ta_cmf(high_ptr, low_ptr, close_ptr, volume_ptr, len, &kwargs);
    match res {
        Ok(out) => Ok(Float64Chunked::from_vec("", out).into_series()),
        Err(ret_code) => ta_code2err(ret_code),
    }
}

#[polars_expr(output_type=Float64)]
fn efi(inputs: &[Series], kwargs: TimePeriodKwargs) -> PolarsResult<Series> {
    let close = &mut cast_series_to_f64(&inputs[0])?;
    let volume = &mut cast_series_to_f64(&inputs[1])?;
    let (close_ptr, _close) = get_series_f64_ptr(close)?;
    let (volume_ptr, _volume) = get_series_f64_ptr(volume)?;
    let len = close.len();
    let res = ta_efi(close_ptr, volume_ptr, len, &kwargs);
    match res {
        Ok(out) => Ok(Float64Chunked::from_vec("", out).into_series()),
        Err(ret_code) => ta_code2err(ret_code),
    }
}

#[polars_expr(output_type=Float64)]
fn marketfi(inputs: &[Series]) -> PolarsResult<Series> {
    let high = &mut cast_series_to_f64(&inputs[0])?;
    let low = &mut cast_series_to_f64(&inputs[1])?;
    let volume = &mut cast_series_to_f64(&inputs[2])?;
    let (high_ptr, _high) = get_series_f64_ptr(high)?;
    let (low_ptr, _low) = get_series_f64_ptr(low)?;
    let (volume_ptr, _volume) = get_series_f64_ptr(volume)?;
    let len = high.len();
    let res = ta_marketfi(high_ptr, low_ptr, volume_ptr, len);
    match res {
        Ok(out) => Ok(Float64Chunked::from_vec("", out).into_series()),
        Err(ret_code) => ta_code2err(ret_code),
    }
}

#[polars_expr(output_type=Float64)]
fn nvi(inputs: &[Series]) -> PolarsResult<Series> {
    let close = &mut cast_series_to_f64(&inputs[0])?;
    let volume = &mut cast_series_to_f64(&inputs[1])?;
    let (close_ptr, _close) = get_series_f64_ptr(close)?;
    let (volume_ptr, _volume) = get_series_f64_ptr(volume)?;
    let len = close.len();
    let res = ta_nvi(close_ptr, volume_ptr, len);
    match res {
        Ok(out) => Ok(Float64Chunked::from_vec("", out).into_series()),
        Err(ret_code) => ta_code2err(ret_code),
    }
}

#[polars_expr(output_type=Float64)]
fn pvi(inputs: &[Series]) -> PolarsResult<Series> {
    let close = &mut cast_series_to_f64(&inputs[0])?;
    let volume = &mut cast_series_to_f64(&inputs[1])?;
    let (close_ptr, _close) = get_series_f64_ptr(close)?;
    let (volume_ptr, _volume) = get_series_f64_ptr(volume)?;
    let len = close.len();
    let res = ta_pvi(close_ptr, volume_ptr, len);
    match res {
        Ok(out) => Ok(Float64Chunked::from_vec("", out).into_series()),
        Err(ret_code) => ta_code2err(ret_code),
    }
}

#[polars_expr(output_type=Float64)]
fn pvo(inputs: &[Series], kwargs: PvoKwargs) -> PolarsResult<Series> {
    let volume = &mut cast_series_to_f64(&inputs[0])?;
    let (volume_ptr, _volume) = get_series_f64_ptr(volume)?;
    let len = volume.len();
    let res = ta_pvo(volume_ptr, len, &kwargs);
    match res {
        Ok(out) => Ok(Float64Chunked::from_vec("", out).into_series()),
        Err(ret_code) => ta_code2err(ret_code),
    }
}

#[polars_expr(output_type=Float64)]
fn pvt(inputs: &[Series]) -> PolarsResult<Series> {
    let close = &mut cast_series_to_f64(&inputs[0])?;
    let volume = &mut cast_series_to_f64(&inputs[1])?;
    let (close_ptr, _close) = get_series_f64_ptr(close)?;
    let (volume_ptr, _volume) = get_series_f64_ptr(volume)?;
    let len = close.len();
    let res = ta_pvt(close_ptr, volume_ptr, len);
    match res {
        Ok(out) => Ok(Float64Chunked::from_vec("", out).into_series()),
        Err(ret_code) => ta_code2err(ret_code),
    }
}

#[polars_expr(output_type=Float64)]
fn rvol(inputs: &[Series], kwargs: TimePeriodKwargs) -> PolarsResult<Series> {
    let volume = &mut cast_series_to_f64(&inputs[0])?;
    let (volume_ptr, _volume) = get_series_f64_ptr(volume)?;
    let len = volume.len();
    let res = ta_rvol(volume_ptr, len, &kwargs);
    match res {
        Ok(out) => Ok(Float64Chunked::from_vec("", out).into_series()),
        Err(ret_code) => ta_code2err(ret_code),
    }
}

#[polars_expr(output_type=Float64)]
fn vwap(inputs: &[Series]) -> PolarsResult<Series> {
    let close = &mut cast_series_to_f64(&inputs[0])?;
    let high = &mut cast_series_to_f64(&inputs[1])?;
    let low = &mut cast_series_to_f64(&inputs[2])?;
    let volume = &mut cast_series_to_f64(&inputs[3])?;
    let (close_ptr, _close) = get_series_f64_ptr(close)?;
    let (high_ptr, _high) = get_series_f64_ptr(high)?;
    let (low_ptr, _low) = get_series_f64_ptr(low)?;
    let (volume_ptr, _volume) = get_series_f64_ptr(volume)?;
    let len = close.len();
    let res = ta_vwap(high_ptr, low_ptr, close_ptr, volume_ptr, len);
    match res {
        Ok(out) => Ok(Float64Chunked::from_vec("", out).into_series()),
        Err(ret_code) => ta_code2err(ret_code),
    }
}
