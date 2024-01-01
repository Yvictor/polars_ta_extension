use polars::prelude::*;
use pyo3_polars::derive::polars_expr;
use serde::Deserialize;
// use std::fmt::Write;
use talib_sys::{TA_NATR_Lookback, TA_NATR, TA_Integer, TA_Real, TA_RetCode};


#[derive(Deserialize)]
pub struct EMAKwargs {
    timeperiod: i32,
}

fn get_series_f64_ptr(series: &mut Series) -> PolarsResult<*const f64> {
    if series.has_validity() {
        let series: Vec<f64> = series
            .f64()?
            .into_iter()
            .map(|x| x.unwrap_or(std::f64::NAN))
            .collect();
        Ok(series.as_ptr())
    } else {
        Ok(series.as_single_ptr()? as *const f64)
    }
}

#[polars_expr(output_type=Float64)]
fn natr(inputs: &[Series], kwargs: EMAKwargs) -> PolarsResult<Series> {
    let close = &mut inputs[0].to_float()?.rechunk();
    let high = &mut inputs[1].to_float()?.rechunk();
    let low = &mut inputs[2].to_float()?.rechunk();
    let mut out_begin: TA_Integer = 0;
    let mut out_size: TA_Integer = 0;
    let len = close.len();
    let mut out: Vec<TA_Real> = Vec::with_capacity(len);
    let high_ptr = get_series_f64_ptr(high)?;
    let low_ptr = get_series_f64_ptr(low)?;
    let close_ptr = get_series_f64_ptr(close)?;

    let lookback = unsafe { TA_NATR_Lookback(kwargs.timeperiod) as usize };
    for _ in 0..lookback {
        out.push(std::f64::NAN);
    }
    let ret_code = unsafe {
        TA_NATR(
            0,
            len as i32 - 1,
            high_ptr,
            low_ptr,
            close_ptr,
            kwargs.timeperiod,
            &mut out_begin,
            &mut out_size,
            out[lookback..].as_mut_ptr(),
        )
    };
    match ret_code {
        TA_RetCode::TA_SUCCESS => {
            unsafe {
                out.set_len((out_begin + out_size) as usize);
            }
            let out_ser = Float64Chunked::from_vec("", out);
            Ok(out_ser.into_series())
        }
        _ => Err(PolarsError::ComputeError(
            format!("Could not compute indicator, err: {:?}", ret_code).into(),
        )),
    }
}