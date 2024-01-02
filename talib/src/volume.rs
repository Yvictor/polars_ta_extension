use crate::utils::make_vec;
// use serde::Deserialize;
use talib_sys::{TA_OBV_Lookback, TA_OBV};
use talib_sys::{TA_Integer, TA_RetCode};

pub fn ta_obv(
    real_ptr: *const f64,
    volume_ptr: *const f64,
    len: usize,
) -> Result<Vec<f64>, TA_RetCode> {
    let mut out_begin: TA_Integer = 0;
    let mut out_size: TA_Integer = 0;
    let lookback = unsafe { TA_OBV_Lookback() };
    let (mut out, ptr) = make_vec(len, lookback);
    let ret_code = unsafe {
        TA_OBV(
            0,
            len as i32 - 1,
            real_ptr,
            volume_ptr,
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