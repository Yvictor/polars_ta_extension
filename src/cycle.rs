use crate::utils::get_series_f64_ptr;
use polars::prelude::*;
use pyo3_polars::derive::polars_expr;
use talib_sys::{TA_HT_DCPERIOD_Lookback, TA_Integer, TA_Real, TA_RetCode, TA_HT_DCPERIOD};

#[polars_expr(output_type=Float64)]
fn ht_dcperiod(inputs: &[Series]) -> PolarsResult<Series> {
    let real = &mut inputs[0].to_float()?.rechunk();
    let mut out_begin: TA_Integer = 0;
    let mut out_size: TA_Integer = 0;
    let len = real.len();
    let mut out: Vec<TA_Real> = Vec::with_capacity(len);
    let (real_ptr, _real) = get_series_f64_ptr(real)?;

    let lookback = unsafe { TA_HT_DCPERIOD_Lookback() as usize };
    for _ in 0..lookback {
        out.push(std::f64::NAN);
    }
    let ret_code = unsafe {
        TA_HT_DCPERIOD(
            0,
            len as i32 - 1,
            real_ptr,
            &mut out_begin,
            &mut out_size,
            out[lookback..].as_mut_ptr(),
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
            let out_ser = Float64Chunked::from_vec("", out);
            Ok(out_ser.into_series())
        }
        _ => Err(PolarsError::ComputeError(
            format!("Could not compute indicator, err: {:?}", ret_code).into(),
        )),
    }
}
