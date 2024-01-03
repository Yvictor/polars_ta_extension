use crate::utils::make_vec;
use serde::Deserialize;
use talib_sys::{TA_ADOSC_Lookback, TA_AD_Lookback, TA_OBV_Lookback, TA_AD, TA_ADOSC, TA_OBV};
use talib_sys::{TA_Integer, TA_RetCode};

pub fn ta_ad(
    high_ptr: *const f64,
    low_ptr: *const f64,
    close_ptr: *const f64,
    volume_ptr: *const f64,
    len: usize,
) -> Result<Vec<f64>, TA_RetCode> {
    let mut out_begin: TA_Integer = 0;
    let mut out_size: TA_Integer = 0;
    let lookback = unsafe { TA_AD_Lookback() };
    let (mut out, ptr) = make_vec(len, lookback);
    let ret_code = unsafe {
        TA_AD(
            0,
            len as i32 - 1,
            high_ptr,
            low_ptr,
            close_ptr,
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

#[derive(Deserialize)]
pub struct ADOSCKwargs {
    fastperiod: i32,
    slowperiod: i32,
}

pub fn ta_adosc(
    high_ptr: *const f64,
    low_ptr: *const f64,
    close_ptr: *const f64,
    volume_ptr: *const f64,
    len: usize,
    kwargs: &ADOSCKwargs,
) -> Result<Vec<f64>, TA_RetCode> {
    let mut out_begin: TA_Integer = 0;
    let mut out_size: TA_Integer = 0;
    let lookback = unsafe { TA_ADOSC_Lookback(kwargs.fastperiod, kwargs.slowperiod) };
    let (mut out, ptr) = make_vec(len, lookback);
    let ret_code = unsafe {
        TA_ADOSC(
            0,
            len as i32 - 1,
            high_ptr,
            low_ptr,
            close_ptr,
            volume_ptr,
            kwargs.fastperiod,
            kwargs.slowperiod,
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
