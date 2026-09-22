use crate::utils::{check_begin_idx3, make_vec};
use serde::Deserialize;
use talib_sys::{
    TA_ATR_Lookback, TA_Integer, TA_NATR_Lookback, TA_RetCode, TA_TRANGE_Lookback, TA_ATR, TA_NATR,
    TA_TRANGE,
};
use derive_builder::Builder;
use crate::utils::cannot_produce_output;
use crate::utils::make_default_vec;
use crate::utils::check_begin_idx1;
use crate::utils::check_begin_idx2;
use crate::common::TimePeriodKwargs;
use talib_sys::{TA_ADR_Lookback, TA_ADR};
use talib_sys::{TA_CVI_Lookback, TA_CVI};
use talib_sys::{TA_MASSI_Lookback, TA_MASSI};
use talib_sys::{TA_RVI_Lookback, TA_RVI};

#[derive(Builder, Deserialize)]
pub struct ATRKwargs {
    #[builder(default = "14")]
    pub timeperiod: i32,
}

pub fn ta_atr(
    high_ptr: *const f64,
    low_ptr: *const f64,
    close_ptr: *const f64,
    len: usize,
    kwargs: &ATRKwargs,
) -> Result<Vec<f64>, TA_RetCode> {
    let mut out_begin: TA_Integer = 0;
    let mut out_size: TA_Integer = 0;
    let begin_idx = check_begin_idx3(len, high_ptr, low_ptr, close_ptr) as i32;
    let end_idx = len as i32 - begin_idx - 1;
    let lookback = begin_idx + unsafe { TA_ATR_Lookback(kwargs.timeperiod) };
    let (mut out, ptr) = make_vec(len, lookback);
    let ret_code = unsafe {
        TA_ATR(
            0,
            end_idx,
            high_ptr.offset(begin_idx as isize),
            low_ptr.offset(begin_idx as isize),
            close_ptr.offset(begin_idx as isize),
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

pub fn ta_trange(
    high_ptr: *const f64,
    low_ptr: *const f64,
    close_ptr: *const f64,
    len: usize,
) -> Result<Vec<f64>, TA_RetCode> {
    let mut out_begin: TA_Integer = 0;
    let mut out_size: TA_Integer = 0;
    let begin_idx = check_begin_idx3(len, high_ptr, low_ptr, close_ptr) as i32;
    let end_idx = len as i32 - begin_idx - 1;
    let lookback = begin_idx + unsafe { TA_TRANGE_Lookback() };
    let (mut out, ptr) = make_vec(len, lookback);
    let ret_code = unsafe {
        TA_TRANGE(
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

#[derive(Builder, Deserialize)]
pub struct NATRKwargs {
    #[builder(default = "14")]
    pub timeperiod: i32,
}

pub fn ta_natr(
    high_ptr: *const f64,
    low_ptr: *const f64,
    close_ptr: *const f64,
    len: usize,
    kwargs: &NATRKwargs,
) -> Result<Vec<f64>, TA_RetCode> {
    let mut out_begin: TA_Integer = 0;
    let mut out_size: TA_Integer = 0;
    let begin_idx = check_begin_idx3(len, high_ptr, low_ptr, close_ptr) as i32;
    let end_idx = len as i32 - begin_idx - 1;
    let lookback = begin_idx + unsafe { TA_NATR_Lookback(kwargs.timeperiod) };
    let (mut out, ptr) = make_vec(len, lookback);
    let ret_code = unsafe {
        TA_NATR(
            0,
            end_idx,
            high_ptr.offset(begin_idx as isize),
            low_ptr.offset(begin_idx as isize),
            close_ptr.offset(begin_idx as isize),
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

pub fn ta_adr(
    high_ptr: *const f64,
    low_ptr: *const f64,
    len: usize,
    kwargs: &TimePeriodKwargs,
) -> Result<Vec<f64>, TA_RetCode> {
    let mut out_begin: TA_Integer = 0;
    let mut out_size: TA_Integer = 0;
    let begin_idx = check_begin_idx2(len, high_ptr, low_ptr) as i32;
    let end_idx = len as i32 - begin_idx - 1;
    let lookback = begin_idx + unsafe { TA_ADR_Lookback(kwargs.timeperiod) };
    if lookback < 0 {
        return Err(TA_RetCode::TA_BAD_PARAM);
    }
    if cannot_produce_output(len, lookback) {
        return Ok(make_default_vec(len));
    }
    let (mut out, ptr) = make_vec(len, lookback);
    let ret_code = unsafe {
        TA_ADR(
            0,
            end_idx,
            high_ptr.offset(begin_idx as isize),
            low_ptr.offset(begin_idx as isize),
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

#[derive(Builder, Deserialize)]
pub struct CviKwargs {
    #[builder(default = "10")]
    pub timeperiod: i32,
    #[builder(default = "10")]
    pub rocperiod: i32,
}

pub fn ta_cvi(
    high_ptr: *const f64,
    low_ptr: *const f64,
    len: usize,
    kwargs: &CviKwargs,
) -> Result<Vec<f64>, TA_RetCode> {
    let mut out_begin: TA_Integer = 0;
    let mut out_size: TA_Integer = 0;
    let begin_idx = check_begin_idx2(len, high_ptr, low_ptr) as i32;
    let end_idx = len as i32 - begin_idx - 1;
    let lookback = begin_idx + unsafe { TA_CVI_Lookback(kwargs.timeperiod, kwargs.rocperiod) };
    if lookback < 0 {
        return Err(TA_RetCode::TA_BAD_PARAM);
    }
    if cannot_produce_output(len, lookback) {
        return Ok(make_default_vec(len));
    }
    let (mut out, ptr) = make_vec(len, lookback);
    let ret_code = unsafe {
        TA_CVI(
            0,
            end_idx,
            high_ptr.offset(begin_idx as isize),
            low_ptr.offset(begin_idx as isize),
            kwargs.timeperiod,
            kwargs.rocperiod,
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

#[derive(Builder, Deserialize)]
pub struct MassiKwargs {
    #[builder(default = "9")]
    pub fastperiod: i32,
    #[builder(default = "25")]
    pub slowperiod: i32,
}

pub fn ta_massi(
    high_ptr: *const f64,
    low_ptr: *const f64,
    len: usize,
    kwargs: &MassiKwargs,
) -> Result<Vec<f64>, TA_RetCode> {
    let mut out_begin: TA_Integer = 0;
    let mut out_size: TA_Integer = 0;
    let begin_idx = check_begin_idx2(len, high_ptr, low_ptr) as i32;
    let end_idx = len as i32 - begin_idx - 1;
    let lookback = begin_idx + unsafe { TA_MASSI_Lookback(kwargs.fastperiod, kwargs.slowperiod) };
    if lookback < 0 {
        return Err(TA_RetCode::TA_BAD_PARAM);
    }
    if cannot_produce_output(len, lookback) {
        return Ok(make_default_vec(len));
    }
    let (mut out, ptr) = make_vec(len, lookback);
    let ret_code = unsafe {
        TA_MASSI(
            0,
            end_idx,
            high_ptr.offset(begin_idx as isize),
            low_ptr.offset(begin_idx as isize),
            kwargs.fastperiod,
            kwargs.slowperiod,
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

#[derive(Builder, Deserialize)]
pub struct RviKwargs {
    #[builder(default = "14")]
    pub timeperiod: i32,
    #[builder(default = "10")]
    pub stddevperiod: i32,
}

pub fn ta_rvi(
    real_ptr: *const f64,
    len: usize,
    kwargs: &RviKwargs,
) -> Result<Vec<f64>, TA_RetCode> {
    let mut out_begin: TA_Integer = 0;
    let mut out_size: TA_Integer = 0;
    let begin_idx = check_begin_idx1(len, real_ptr) as i32;
    let end_idx = len as i32 - begin_idx - 1;
    let lookback = begin_idx + unsafe { TA_RVI_Lookback(kwargs.timeperiod, kwargs.stddevperiod) };
    if lookback < 0 {
        return Err(TA_RetCode::TA_BAD_PARAM);
    }
    if cannot_produce_output(len, lookback) {
        return Ok(make_default_vec(len));
    }
    let (mut out, ptr) = make_vec(len, lookback);
    let ret_code = unsafe {
        TA_RVI(
            0,
            end_idx,
            real_ptr.offset(begin_idx as isize),
            kwargs.timeperiod,
            kwargs.stddevperiod,
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
