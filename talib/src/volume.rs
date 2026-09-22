use crate::utils::{make_vec, check_begin_idx4, check_begin_idx2};
use serde::Deserialize;
use talib_sys::{TA_ADOSC_Lookback, TA_AD_Lookback, TA_OBV_Lookback, TA_AD, TA_ADOSC, TA_OBV};
use talib_sys::{TA_Integer, TA_RetCode};
use derive_builder::Builder;
use crate::utils::cannot_produce_output;
use crate::utils::make_default_vec;
use crate::utils::check_begin_idx1;
use crate::utils::check_begin_idx3;
use talib_sys::TA_MAType;
use crate::common::TimePeriodKwargs;
use talib_sys::{TA_CMF_Lookback, TA_CMF};
use talib_sys::{TA_EFI_Lookback, TA_EFI};
use talib_sys::{TA_MARKETFI_Lookback, TA_MARKETFI};
use talib_sys::{TA_NVI_Lookback, TA_NVI};
use talib_sys::{TA_PVI_Lookback, TA_PVI};
use talib_sys::{TA_PVO_Lookback, TA_PVO};
use talib_sys::{TA_PVT_Lookback, TA_PVT};
use talib_sys::{TA_RVOL_Lookback, TA_RVOL};
use talib_sys::{TA_VWAP_Lookback, TA_VWAP};

pub fn ta_ad(
    high_ptr: *const f64,
    low_ptr: *const f64,
    close_ptr: *const f64,
    volume_ptr: *const f64,
    len: usize,
) -> Result<Vec<f64>, TA_RetCode> {
    let mut out_begin: TA_Integer = 0;
    let mut out_size: TA_Integer = 0;
    let begin_idx = check_begin_idx4(len, high_ptr, low_ptr, close_ptr, volume_ptr) as i32;
    let end_idx = len as i32 - begin_idx - 1;
    let lookback = begin_idx + unsafe { TA_AD_Lookback() };
    let (mut out, ptr) = make_vec(len, lookback);
    let ret_code = unsafe {
        TA_AD(
            0,
            end_idx,
            high_ptr.offset(begin_idx as isize),
            low_ptr.offset(begin_idx as isize),
            close_ptr.offset(begin_idx as isize),
            volume_ptr.offset(begin_idx as isize),
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
pub struct ADOSCKwargs {
    #[builder(default = "3")]
    pub fastperiod: i32,
    #[builder(default = "10")]
    pub slowperiod: i32,
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
    let begin_idx = check_begin_idx4(len, high_ptr, low_ptr, close_ptr, volume_ptr) as i32;
    let end_idx = len as i32 - begin_idx - 1;
    let lookback = begin_idx + unsafe { TA_ADOSC_Lookback(kwargs.fastperiod, kwargs.slowperiod) };
    let (mut out, ptr) = make_vec(len, lookback);
    let ret_code = unsafe {
        TA_ADOSC(
            0,
            end_idx,
            high_ptr.offset(begin_idx as isize),
            low_ptr.offset(begin_idx as isize),
            close_ptr.offset(begin_idx as isize),
            volume_ptr.offset(begin_idx as isize),
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

pub fn ta_obv(
    real_ptr: *const f64,
    volume_ptr: *const f64,
    len: usize,
) -> Result<Vec<f64>, TA_RetCode> {
    let mut out_begin: TA_Integer = 0;
    let mut out_size: TA_Integer = 0;
    let begin_idx = check_begin_idx2(len, real_ptr, volume_ptr) as i32;
    let end_idx = len as i32 - begin_idx - 1;
    let lookback = begin_idx + unsafe { TA_OBV_Lookback() };
    let (mut out, ptr) = make_vec(len, lookback);
    let ret_code = unsafe {
        TA_OBV(
            0,
            end_idx,
            real_ptr.offset(begin_idx as isize),
            volume_ptr.offset(begin_idx as isize),
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

pub fn ta_cmf(
    high_ptr: *const f64,
    low_ptr: *const f64,
    close_ptr: *const f64,
    volume_ptr: *const f64,
    len: usize,
    kwargs: &TimePeriodKwargs,
) -> Result<Vec<f64>, TA_RetCode> {
    let mut out_begin: TA_Integer = 0;
    let mut out_size: TA_Integer = 0;
    let begin_idx = check_begin_idx4(len, high_ptr, low_ptr, close_ptr, volume_ptr) as i32;
    let end_idx = len as i32 - begin_idx - 1;
    let lookback = begin_idx + unsafe { TA_CMF_Lookback(kwargs.timeperiod) };
    if lookback < 0 {
        return Err(TA_RetCode::TA_BAD_PARAM);
    }
    if cannot_produce_output(len, lookback) {
        return Ok(make_default_vec(len));
    }
    let (mut out, ptr) = make_vec(len, lookback);
    let ret_code = unsafe {
        TA_CMF(
            0,
            end_idx,
            high_ptr.offset(begin_idx as isize),
            low_ptr.offset(begin_idx as isize),
            close_ptr.offset(begin_idx as isize),
            volume_ptr.offset(begin_idx as isize),
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

pub fn ta_efi(
    close_ptr: *const f64,
    volume_ptr: *const f64,
    len: usize,
    kwargs: &TimePeriodKwargs,
) -> Result<Vec<f64>, TA_RetCode> {
    let mut out_begin: TA_Integer = 0;
    let mut out_size: TA_Integer = 0;
    let begin_idx = check_begin_idx2(len, close_ptr, volume_ptr) as i32;
    let end_idx = len as i32 - begin_idx - 1;
    let lookback = begin_idx + unsafe { TA_EFI_Lookback(kwargs.timeperiod) };
    if lookback < 0 {
        return Err(TA_RetCode::TA_BAD_PARAM);
    }
    if cannot_produce_output(len, lookback) {
        return Ok(make_default_vec(len));
    }
    let (mut out, ptr) = make_vec(len, lookback);
    let ret_code = unsafe {
        TA_EFI(
            0,
            end_idx,
            close_ptr.offset(begin_idx as isize),
            volume_ptr.offset(begin_idx as isize),
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

pub fn ta_marketfi(
    high_ptr: *const f64,
    low_ptr: *const f64,
    volume_ptr: *const f64,
    len: usize,
) -> Result<Vec<f64>, TA_RetCode> {
    let mut out_begin: TA_Integer = 0;
    let mut out_size: TA_Integer = 0;
    let begin_idx = check_begin_idx3(len, high_ptr, low_ptr, volume_ptr) as i32;
    let end_idx = len as i32 - begin_idx - 1;
    let lookback = begin_idx + unsafe { TA_MARKETFI_Lookback() };
    if lookback < 0 {
        return Err(TA_RetCode::TA_BAD_PARAM);
    }
    if cannot_produce_output(len, lookback) {
        return Ok(make_default_vec(len));
    }
    let (mut out, ptr) = make_vec(len, lookback);
    let ret_code = unsafe {
        TA_MARKETFI(
            0,
            end_idx,
            high_ptr.offset(begin_idx as isize),
            low_ptr.offset(begin_idx as isize),
            volume_ptr.offset(begin_idx as isize),
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

pub fn ta_nvi(
    close_ptr: *const f64,
    volume_ptr: *const f64,
    len: usize,
) -> Result<Vec<f64>, TA_RetCode> {
    let mut out_begin: TA_Integer = 0;
    let mut out_size: TA_Integer = 0;
    let begin_idx = check_begin_idx2(len, close_ptr, volume_ptr) as i32;
    let end_idx = len as i32 - begin_idx - 1;
    let lookback = begin_idx + unsafe { TA_NVI_Lookback() };
    if lookback < 0 {
        return Err(TA_RetCode::TA_BAD_PARAM);
    }
    if cannot_produce_output(len, lookback) {
        return Ok(make_default_vec(len));
    }
    let (mut out, ptr) = make_vec(len, lookback);
    let ret_code = unsafe {
        TA_NVI(
            0,
            end_idx,
            close_ptr.offset(begin_idx as isize),
            volume_ptr.offset(begin_idx as isize),
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

pub fn ta_pvi(
    close_ptr: *const f64,
    volume_ptr: *const f64,
    len: usize,
) -> Result<Vec<f64>, TA_RetCode> {
    let mut out_begin: TA_Integer = 0;
    let mut out_size: TA_Integer = 0;
    let begin_idx = check_begin_idx2(len, close_ptr, volume_ptr) as i32;
    let end_idx = len as i32 - begin_idx - 1;
    let lookback = begin_idx + unsafe { TA_PVI_Lookback() };
    if lookback < 0 {
        return Err(TA_RetCode::TA_BAD_PARAM);
    }
    if cannot_produce_output(len, lookback) {
        return Ok(make_default_vec(len));
    }
    let (mut out, ptr) = make_vec(len, lookback);
    let ret_code = unsafe {
        TA_PVI(
            0,
            end_idx,
            close_ptr.offset(begin_idx as isize),
            volume_ptr.offset(begin_idx as isize),
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
pub struct PvoKwargs {
    #[builder(default = "12")]
    pub fastperiod: i32,
    #[builder(default = "26")]
    pub slowperiod: i32,
    pub matype: TA_MAType,
}

pub fn ta_pvo(
    volume_ptr: *const f64,
    len: usize,
    kwargs: &PvoKwargs,
) -> Result<Vec<f64>, TA_RetCode> {
    let mut out_begin: TA_Integer = 0;
    let mut out_size: TA_Integer = 0;
    let begin_idx = check_begin_idx1(len, volume_ptr) as i32;
    let end_idx = len as i32 - begin_idx - 1;
    let lookback = begin_idx + unsafe { TA_PVO_Lookback(kwargs.fastperiod, kwargs.slowperiod, kwargs.matype) };
    if lookback < 0 {
        return Err(TA_RetCode::TA_BAD_PARAM);
    }
    if cannot_produce_output(len, lookback) {
        return Ok(make_default_vec(len));
    }
    let (mut out, ptr) = make_vec(len, lookback);
    let ret_code = unsafe {
        TA_PVO(
            0,
            end_idx,
            volume_ptr.offset(begin_idx as isize),
            kwargs.fastperiod,
            kwargs.slowperiod,
            kwargs.matype,
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

pub fn ta_pvt(
    close_ptr: *const f64,
    volume_ptr: *const f64,
    len: usize,
) -> Result<Vec<f64>, TA_RetCode> {
    let mut out_begin: TA_Integer = 0;
    let mut out_size: TA_Integer = 0;
    let begin_idx = check_begin_idx2(len, close_ptr, volume_ptr) as i32;
    let end_idx = len as i32 - begin_idx - 1;
    let lookback = begin_idx + unsafe { TA_PVT_Lookback() };
    if lookback < 0 {
        return Err(TA_RetCode::TA_BAD_PARAM);
    }
    if cannot_produce_output(len, lookback) {
        return Ok(make_default_vec(len));
    }
    let (mut out, ptr) = make_vec(len, lookback);
    let ret_code = unsafe {
        TA_PVT(
            0,
            end_idx,
            close_ptr.offset(begin_idx as isize),
            volume_ptr.offset(begin_idx as isize),
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

pub fn ta_rvol(
    volume_ptr: *const f64,
    len: usize,
    kwargs: &TimePeriodKwargs,
) -> Result<Vec<f64>, TA_RetCode> {
    let mut out_begin: TA_Integer = 0;
    let mut out_size: TA_Integer = 0;
    let begin_idx = check_begin_idx1(len, volume_ptr) as i32;
    let end_idx = len as i32 - begin_idx - 1;
    let lookback = begin_idx + unsafe { TA_RVOL_Lookback(kwargs.timeperiod) };
    if lookback < 0 {
        return Err(TA_RetCode::TA_BAD_PARAM);
    }
    if cannot_produce_output(len, lookback) {
        return Ok(make_default_vec(len));
    }
    let (mut out, ptr) = make_vec(len, lookback);
    let ret_code = unsafe {
        TA_RVOL(
            0,
            end_idx,
            volume_ptr.offset(begin_idx as isize),
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

pub fn ta_vwap(
    high_ptr: *const f64,
    low_ptr: *const f64,
    close_ptr: *const f64,
    volume_ptr: *const f64,
    len: usize,
) -> Result<Vec<f64>, TA_RetCode> {
    let mut out_begin: TA_Integer = 0;
    let mut out_size: TA_Integer = 0;
    let begin_idx = check_begin_idx4(len, high_ptr, low_ptr, close_ptr, volume_ptr) as i32;
    let end_idx = len as i32 - begin_idx - 1;
    let lookback = begin_idx + unsafe { TA_VWAP_Lookback() };
    if lookback < 0 {
        return Err(TA_RetCode::TA_BAD_PARAM);
    }
    if cannot_produce_output(len, lookback) {
        return Ok(make_default_vec(len));
    }
    let (mut out, ptr) = make_vec(len, lookback);
    let ret_code = unsafe {
        TA_VWAP(
            0,
            end_idx,
            high_ptr.offset(begin_idx as isize),
            low_ptr.offset(begin_idx as isize),
            close_ptr.offset(begin_idx as isize),
            volume_ptr.offset(begin_idx as isize),
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
