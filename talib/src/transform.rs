use crate::utils::make_vec;
use talib_sys::{TA_AVGPRICE_Lookback, TA_Integer, TA_RetCode, TA_AVGPRICE};
use talib_sys::{TA_MEDPRICE_Lookback, TA_MEDPRICE};
use talib_sys::{TA_TYPPRICE_Lookback, TA_TYPPRICE};
use talib_sys::{TA_WCLPRICE_Lookback, TA_WCLPRICE};

pub fn ta_avgprice(
    open_ptr: *const f64,
    high_ptr: *const f64,
    low_ptr: *const f64,
    close_ptr: *const f64,
    len: usize,
) -> Result<Vec<f64>, TA_RetCode> {
    let mut out_begin: TA_Integer = 0;
    let mut out_size: TA_Integer = 0;
    let lookback = unsafe { TA_AVGPRICE_Lookback() };
    let (mut out, ptr) = make_vec(len, lookback);
    let ret_code = unsafe {
        TA_AVGPRICE(
            0,
            len as i32 - 1,
            open_ptr,
            high_ptr,
            low_ptr,
            close_ptr,
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

pub fn ta_medprice(
    high_ptr: *const f64,
    low_ptr: *const f64,
    len: usize,
) -> Result<Vec<f64>, TA_RetCode> {
    let mut out_begin: TA_Integer = 0;
    let mut out_size: TA_Integer = 0;
    let lookback = unsafe { TA_MEDPRICE_Lookback() };
    let (mut out, ptr) = make_vec(len, lookback);
    let ret_code = unsafe {
        TA_MEDPRICE(
            0,
            len as i32 - 1,
            high_ptr,
            low_ptr,
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

pub fn ta_typprice(
    high_ptr: *const f64,
    low_ptr: *const f64,
    close_ptr: *const f64,
    len: usize,
) -> Result<Vec<f64>, TA_RetCode> {
    let mut out_begin: TA_Integer = 0;
    let mut out_size: TA_Integer = 0;
    let lookback = unsafe { TA_TYPPRICE_Lookback() };
    let (mut out, ptr) = make_vec(len, lookback);
    let ret_code = unsafe {
        TA_TYPPRICE(
            0,
            len as i32 - 1,
            high_ptr,
            low_ptr,
            close_ptr,
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

pub fn ta_wclprice(
    high_ptr: *const f64,
    low_ptr: *const f64,
    close_ptr: *const f64,
    len: usize,
) -> Result<Vec<f64>, TA_RetCode> {
    let mut out_begin: TA_Integer = 0;
    let mut out_size: TA_Integer = 0;
    let lookback = unsafe { TA_WCLPRICE_Lookback() };
    let (mut out, ptr) = make_vec(len, lookback);
    let ret_code = unsafe {
        TA_WCLPRICE(
            0,
            len as i32 - 1,
            high_ptr,
            low_ptr,
            close_ptr,
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