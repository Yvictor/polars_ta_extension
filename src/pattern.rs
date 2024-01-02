use crate::utils::{get_series_f64_ptr, make_vec};
use polars::prelude::*;
use pyo3_polars::derive::polars_expr;
use serde::Deserialize;
use talib_sys::{TA_CDLABANDONEDBABY_Lookback, TA_CDLABANDONEDBABY};
use talib_sys::{TA_Integer, TA_RetCode};

#[derive(Deserialize)]
pub struct CDLABANDONEDBABYKwargs {
    penetration: f64,
}


#[polars_expr(output_type=Int32)]
fn cdlabandonedbaby(inputs: &[Series], kwargs: CDLABANDONEDBABYKwargs) -> PolarsResult<Series> {
    let open = &mut inputs[0].to_float()?.rechunk();
    let high = &mut inputs[1].to_float()?.rechunk();
    let low = &mut inputs[2].to_float()?.rechunk();
    let close = &mut inputs[3].to_float()?.rechunk();
    let mut out_begin: TA_Integer = 0;
    let mut out_size: TA_Integer = 0;
    let len = close.len();
    let (open_ptr, _open) = get_series_f64_ptr(open)?;
    let (high_ptr, _high) = get_series_f64_ptr(high)?;
    let (low_ptr, _low) = get_series_f64_ptr(low)?;
    let (close_ptr, _close) = get_series_f64_ptr(close)?;

    let lookback = unsafe { TA_CDLABANDONEDBABY_Lookback(kwargs.penetration) };
    let (mut out, ptr) = make_vec(len, lookback);
    let ret_code = unsafe {
        TA_CDLABANDONEDBABY(
            0,
            len as i32 - 1,
            open_ptr,
            high_ptr,
            low_ptr,
            close_ptr,
            kwargs.penetration,
            &mut out_begin,
            &mut out_size,
            ptr,
        )
    };
    
    match ret_code {
        TA_RetCode::TA_SUCCESS => {
            let out_size = (out_begin + out_size) as usize;
            if out_size != 0 {
                unsafe {
                    out.set_len(out_size);
                }
            } else {
                unsafe {
                    out.set_len(len);
                }
            }
            let out_ser = Int32Chunked::from_vec("", out);
            Ok(out_ser.into_series())
        }
        _ => Err(PolarsError::ComputeError(
            format!("Could not compute indicator, err: {:?}", ret_code).into(),
        )),
    }
}
