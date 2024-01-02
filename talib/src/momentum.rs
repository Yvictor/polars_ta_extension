use crate::utils::make_vec;
use serde::Deserialize;
use talib_sys::{TA_ADX_Lookback, TA_Integer, TA_RetCode, TA_ADX};
use talib_sys::{TA_AROON_Lookback, TA_AROON};

#[derive(Deserialize)]
pub struct ADXKwargs {
    timeperiod: i32,
}

pub fn ta_adx(high_ptr: *const f64, low_ptr: *const f64, close_ptr: *const f64, len: usize, kwargs: &ADXKwargs) -> Result<Vec<f64>, TA_RetCode> {
    let mut out_begin: TA_Integer = 0;
    let mut out_size: TA_Integer = 0;
    let lookback = unsafe { TA_ADX_Lookback(kwargs.timeperiod) };
    let (mut out, ptr) = make_vec(len, lookback);
    let ret_code = unsafe {
        TA_ADX(
            0,
            len as i32 - 1,
            high_ptr,
            low_ptr,
            close_ptr,
            kwargs.timeperiod,
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


#[derive(Deserialize)]
pub struct ArronKwargs {
    timeperiod: i32,
}

pub fn ta_aroon(high_ptr: *const f64, low_ptr: *const f64, len: usize, kwargs: &ArronKwargs) -> Result<(Vec<f64>, Vec<f64>), TA_RetCode> {
    let mut out_begin: TA_Integer = 0;
    let mut out_size: TA_Integer = 0;
    let lookback = unsafe { TA_AROON_Lookback(kwargs.timeperiod) };
    let (mut outaroondown, ptr1) = make_vec(len, lookback);
    let (mut outaroonup, ptr2) = make_vec(len, lookback);
    let ret_code = unsafe {
        TA_AROON(
            0,
            len as i32 - 1,
            high_ptr,
            low_ptr,
            kwargs.timeperiod,
            &mut out_begin,
            &mut out_size,
            ptr1,
            ptr2,
        )
    };
    let out_size = (out_begin + out_size) as usize;
    match ret_code {
        TA_RetCode::TA_SUCCESS => {
            if out_size != 0 {
                unsafe {
                    outaroondown.set_len(out_size);
                    outaroonup.set_len(out_size);
                }
            } else {
                unsafe {
                    outaroondown.set_len(len);
                    outaroonup.set_len(len);
                }
            }
            Ok((outaroondown, outaroonup))
        }
        _ => Err(ret_code),
    }
}