use crate::utils::{check_begin_idx2, check_begin_idx3, check_begin_idx4, make_vec};
use talib_sys::{TA_AVGPRICE_Lookback, TA_Integer, TA_RetCode, TA_AVGPRICE};
use talib_sys::{TA_MEDPRICE_Lookback, TA_MEDPRICE};
use talib_sys::{TA_TYPPRICE_Lookback, TA_TYPPRICE};
use talib_sys::{TA_WCLPRICE_Lookback, TA_WCLPRICE};
use crate::utils::cannot_produce_output;
use crate::utils::make_default_vec;
use crate::utils::check_begin_idx1;
use crate::common::TimePeriodKwargs;
use talib_sys::{TA_AVGDEV_Lookback, TA_AVGDEV};
use talib_sys::{TA_HA_Lookback, TA_HA};

pub fn ta_avgprice(
    open_ptr: *const f64,
    high_ptr: *const f64,
    low_ptr: *const f64,
    close_ptr: *const f64,
    len: usize,
) -> Result<Vec<f64>, TA_RetCode> {
    let mut out_begin: TA_Integer = 0;
    let mut out_size: TA_Integer = 0;
    let begin_idx = check_begin_idx4(len, open_ptr, high_ptr, low_ptr, close_ptr) as i32;
    let end_idx = len as i32 - begin_idx - 1;
    let lookback = begin_idx + unsafe { TA_AVGPRICE_Lookback() };
    let (mut out, ptr) = make_vec(len, lookback);
    let ret_code = unsafe {
        TA_AVGPRICE(
            0,
            end_idx,
            open_ptr.offset(begin_idx as isize),
            high_ptr.offset(begin_idx as isize),
            low_ptr.offset(begin_idx as isize),
            close_ptr.offset(begin_idx as isize),
            &mut out_begin,
            &mut out_size,
            ptr,
        )
    };
    let out_size_begin = (begin_idx + out_begin + out_size) as usize;
    match ret_code {
        TA_RetCode::TA_SUCCESS => {
            if out_size != 0 {
                unsafe {
                    out.set_len(out_size_begin);
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
    let begin_idx = check_begin_idx2(len, high_ptr, low_ptr) as i32;
    let end_idx = len as i32 - begin_idx - 1;
    let lookback = begin_idx + unsafe { TA_MEDPRICE_Lookback() };
    let (mut out, ptr) = make_vec(len, lookback);
    let ret_code = unsafe {
        TA_MEDPRICE(
            0,
            end_idx,
            high_ptr.offset(begin_idx as isize),
            low_ptr.offset(begin_idx as isize),
            &mut out_begin,
            &mut out_size,
            ptr,
        )
    };
    let out_size_begin = (begin_idx + out_begin + out_size) as usize;
    match ret_code {
        TA_RetCode::TA_SUCCESS => {
            if out_size != 0 {
                unsafe {
                    out.set_len(out_size_begin);
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
    let begin_idx = check_begin_idx3(len, high_ptr, low_ptr, close_ptr) as i32;
    let end_idx = len as i32 - begin_idx - 1;
    let lookback = begin_idx + unsafe { TA_TYPPRICE_Lookback() };
    let (mut out, ptr) = make_vec(len, lookback);
    let ret_code = unsafe {
        TA_TYPPRICE(
            0,
            end_idx,
            high_ptr.offset(begin_idx as isize),
            low_ptr.offset(begin_idx as isize),
            close_ptr.offset(begin_idx as isize),
            &mut out_begin,
            &mut out_size,
            ptr,
        )
    };
    let out_size_begin = (begin_idx + out_begin + out_size) as usize;
    match ret_code {
        TA_RetCode::TA_SUCCESS => {
            if out_size != 0 {
                unsafe {
                    out.set_len(out_size_begin);
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
    let begin_idx = check_begin_idx3(len, high_ptr, low_ptr, close_ptr) as i32;
    let end_idx = len as i32 - begin_idx - 1;
    let lookback = begin_idx + unsafe { TA_WCLPRICE_Lookback() };
    let (mut out, ptr) = make_vec(len, lookback);
    let ret_code = unsafe {
        TA_WCLPRICE(
            0,
            end_idx,
            high_ptr.offset(begin_idx as isize),
            low_ptr.offset(begin_idx as isize),
            close_ptr.offset(begin_idx as isize),
            &mut out_begin,
            &mut out_size,
            ptr,
        )
    };
    let out_size_begin = (begin_idx + out_begin + out_size) as usize;
    match ret_code {
        TA_RetCode::TA_SUCCESS => {
            if out_size != 0 {
                unsafe {
                    out.set_len(out_size_begin);
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

pub fn ta_avgdev(
    real_ptr: *const f64,
    len: usize,
    kwargs: &TimePeriodKwargs,
) -> Result<Vec<f64>, TA_RetCode> {
    let mut out_begin: TA_Integer = 0;
    let mut out_size: TA_Integer = 0;
    let begin_idx = check_begin_idx1(len, real_ptr) as i32;
    let end_idx = len as i32 - begin_idx - 1;
    let lookback = begin_idx + unsafe { TA_AVGDEV_Lookback(kwargs.timeperiod) };
    if lookback < 0 {
        return Err(TA_RetCode::TA_BAD_PARAM);
    }
    if cannot_produce_output(len, lookback) {
        return Ok(make_default_vec(len));
    }
    let (mut out, ptr) = make_vec(len, lookback);
    let ret_code = unsafe {
        TA_AVGDEV(
            0,
            end_idx,
            real_ptr.offset(begin_idx as isize),
            kwargs.timeperiod,
            &mut out_begin,
            &mut out_size,
            ptr,
        )
    };
    let out_size_begin = (begin_idx + out_begin + out_size) as usize;
    match ret_code {
        TA_RetCode::TA_SUCCESS => {
            if out_size != 0 {
                unsafe {
                    out.set_len(out_size_begin);
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

pub fn ta_ha(
    open_ptr: *const f64,
    high_ptr: *const f64,
    low_ptr: *const f64,
    close_ptr: *const f64,
    len: usize,
) -> Result<(Vec<f64>, Vec<f64>, Vec<f64>, Vec<f64>), TA_RetCode> {
    let mut out_begin: TA_Integer = 0;
    let mut out_size: TA_Integer = 0;
    let begin_idx = check_begin_idx4(len, open_ptr, high_ptr, low_ptr, close_ptr) as i32;
    let end_idx = len as i32 - begin_idx - 1;
    let lookback = begin_idx + unsafe { TA_HA_Lookback() };
    if lookback < 0 {
        return Err(TA_RetCode::TA_BAD_PARAM);
    }
    if cannot_produce_output(len, lookback) {
        return Ok((make_default_vec(len), make_default_vec(len), make_default_vec(len), make_default_vec(len)));
    }
    let (mut outhaopen, outhaopen_ptr) = make_vec(len, lookback);
    let (mut outhahigh, outhahigh_ptr) = make_vec(len, lookback);
    let (mut outhalow, outhalow_ptr) = make_vec(len, lookback);
    let (mut outhaclose, outhaclose_ptr) = make_vec(len, lookback);
    let ret_code = unsafe {
        TA_HA(
            0,
            end_idx,
            open_ptr.offset(begin_idx as isize),
            high_ptr.offset(begin_idx as isize),
            low_ptr.offset(begin_idx as isize),
            close_ptr.offset(begin_idx as isize),
            &mut out_begin,
            &mut out_size,
            outhaopen_ptr,
            outhahigh_ptr,
            outhalow_ptr,
            outhaclose_ptr,
        )
    };
    let out_size_begin = (begin_idx + out_begin + out_size) as usize;
    match ret_code {
        TA_RetCode::TA_SUCCESS => {
            if out_size != 0 {
                unsafe {
                    outhaopen.set_len(out_size_begin);
                    outhahigh.set_len(out_size_begin);
                    outhalow.set_len(out_size_begin);
                    outhaclose.set_len(out_size_begin);
                }
            } else {
                unsafe {
                    outhaopen.set_len(len);
                    outhahigh.set_len(len);
                    outhalow.set_len(len);
                    outhaclose.set_len(len);
                }
            }
            Ok((outhaopen, outhahigh, outhalow, outhaclose))
        }
        _ => Err(ret_code),
    }
}
