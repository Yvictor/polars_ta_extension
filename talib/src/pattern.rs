use crate::utils::make_vec;
use serde::Deserialize;
use talib_sys::{TA_CDLABANDONEDBABY_Lookback, TA_CDLABANDONEDBABY};
use talib_sys::{TA_Integer, TA_RetCode};

#[derive(Deserialize)]
pub struct CDLABANDONEDBABYKwargs {
    penetration: f64,
}

pub fn ta_cdlabandonedbaby(
    open_ptr: *const f64,
    high_ptr: *const f64,
    low_ptr: *const f64,
    close_ptr: *const f64,
    len: usize,
    kwargs: &CDLABANDONEDBABYKwargs,
) -> Result<Vec<i32>, TA_RetCode> {
    let mut out_begin: TA_Integer = 0;
    let mut out_size: TA_Integer = 0;
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
    let out_size = (out_begin + out_size) as usize;
    match ret_code {
        TA_RetCode::TA_SUCCESS => {
            if out_size != 0 {
                unsafe {
                    out.set_len(out_size);
                }
            } else {
                unsafe {
                    out.set_len(len);
                }
            }
            Ok(out)
        }
        _ => Err(ret_code),
    }
}
