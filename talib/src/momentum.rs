use crate::utils::{check_begin_idx1, check_begin_idx2, check_begin_idx3, check_begin_idx4};
use crate::{common::TimePeriodKwargs, utils::make_vec};
use derive_builder::Builder;
use serde::Deserialize;
use talib_sys::{TA_ADXR_Lookback, TA_ADXR};
use talib_sys::{TA_ADX_Lookback, TA_ADX};
use talib_sys::{TA_APO_Lookback, TA_APO};
use talib_sys::{TA_AROONOSC_Lookback, TA_AROONOSC};
use talib_sys::{TA_AROON_Lookback, TA_AROON};
use talib_sys::{TA_BOP_Lookback, TA_BOP};
use talib_sys::{TA_CCI_Lookback, TA_CCI};
use talib_sys::{TA_CMO_Lookback, TA_CMO};
use talib_sys::{TA_DX_Lookback, TA_DX};
use talib_sys::{TA_Integer, TA_MAType, TA_RetCode};
use talib_sys::{TA_MACDEXT_Lookback, TA_MACDEXT};
use talib_sys::{TA_MACDFIX_Lookback, TA_MACDFIX};
use talib_sys::{TA_MACD_Lookback, TA_MACD};
use talib_sys::{TA_MFI_Lookback, TA_MFI};
use talib_sys::{TA_MINUS_DI_Lookback, TA_MINUS_DI};
use talib_sys::{TA_MINUS_DM_Lookback, TA_MINUS_DM};
use talib_sys::{TA_MOM_Lookback, TA_MOM};
use talib_sys::{TA_PLUS_DI_Lookback, TA_PLUS_DI};
use talib_sys::{TA_PLUS_DM_Lookback, TA_PLUS_DM};
use talib_sys::{TA_PPO_Lookback, TA_PPO};
use talib_sys::{TA_ROCP_Lookback, TA_ROCP};
use talib_sys::{TA_ROCR100_Lookback, TA_ROCR100};
use talib_sys::{TA_ROCR_Lookback, TA_ROCR};
use talib_sys::{TA_ROC_Lookback, TA_ROC};
use talib_sys::{TA_RSI_Lookback, TA_RSI};
use talib_sys::{TA_STOCHF_Lookback, TA_STOCHF};
use talib_sys::{TA_STOCHRSI_Lookback, TA_STOCHRSI};
use talib_sys::{TA_STOCH_Lookback, TA_STOCH};
use talib_sys::{TA_TRIX_Lookback, TA_TRIX};
use talib_sys::{TA_ULTOSC_Lookback, TA_ULTOSC};
use talib_sys::{TA_WILLR_Lookback, TA_WILLR};

pub fn ta_adx(
    high_ptr: *const f64,
    low_ptr: *const f64,
    close_ptr: *const f64,
    len: usize,
    kwargs: &TimePeriodKwargs,
) -> Result<Vec<f64>, TA_RetCode> {
    let mut out_begin: TA_Integer = 0;
    let mut out_size: TA_Integer = 0;
    let begin_idx = check_begin_idx3(len, high_ptr, low_ptr, close_ptr) as i32;
    let end_idx = len as i32 - begin_idx - 1;
    let lookback = begin_idx + unsafe { TA_ADX_Lookback(kwargs.timeperiod) };
    let (mut out, ptr) = make_vec(len, lookback);
    let ret_code = unsafe {
        TA_ADX(
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

pub fn ta_adxr(
    high_ptr: *const f64,
    low_ptr: *const f64,
    close_ptr: *const f64,
    len: usize,
    kwargs: &TimePeriodKwargs,
) -> Result<Vec<f64>, TA_RetCode> {
    let mut out_begin: TA_Integer = 0;
    let mut out_size: TA_Integer = 0;
    let begin_idx = check_begin_idx3(len, high_ptr, low_ptr, close_ptr) as i32;
    let end_idx = len as i32 - begin_idx - 1;
    let lookback = begin_idx + unsafe { TA_ADXR_Lookback(kwargs.timeperiod) };
    let (mut out, ptr) = make_vec(len, lookback);
    let ret_code = unsafe {
        TA_ADXR(
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

#[derive(Builder, Deserialize)]
pub struct ApoKwargs {
    #[builder(default = "12")]
    pub fastperiod: i32,
    #[builder(default = "26")]
    pub slowperiod: i32,
    pub matype: TA_MAType,
}

pub fn ta_apo(
    input_ptr: *const f64,
    len: usize,
    kwargs: &ApoKwargs,
) -> Result<Vec<f64>, TA_RetCode> {
    let mut out_begin: TA_Integer = 0;
    let mut out_size: TA_Integer = 0;
    let begin_idx = check_begin_idx1(len, input_ptr) as i32;
    let end_idx = len as i32 - begin_idx - 1;
    let lookback =
        begin_idx + unsafe { TA_APO_Lookback(kwargs.fastperiod, kwargs.slowperiod, kwargs.matype) };
    let (mut out, ptr) = make_vec(len, lookback);
    let ret_code = unsafe {
        TA_APO(
            0,
            end_idx,
            input_ptr.offset(begin_idx as isize),
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

pub fn ta_aroon(
    high_ptr: *const f64,
    low_ptr: *const f64,
    len: usize,
    kwargs: &TimePeriodKwargs,
) -> Result<(Vec<f64>, Vec<f64>), TA_RetCode> {
    let mut out_begin: TA_Integer = 0;
    let mut out_size: TA_Integer = 0;
    let begin_idx = check_begin_idx2(len, high_ptr, low_ptr) as i32;
    let end_idx = len as i32 - begin_idx - 1;
    let lookback = begin_idx + unsafe { TA_AROON_Lookback(kwargs.timeperiod) };
    let (mut outaroondown, ptr1) = make_vec(len, lookback);
    let (mut outaroonup, ptr2) = make_vec(len, lookback);
    let ret_code = unsafe {
        TA_AROON(
            0,
            end_idx,
            high_ptr.offset(begin_idx as isize),
            low_ptr.offset(begin_idx as isize),
            kwargs.timeperiod,
            &mut out_begin,
            &mut out_size,
            ptr1,
            ptr2,
        )
    };
    let out_size_begin = (begin_idx + out_begin + out_size) as usize;
    match ret_code {
        TA_RetCode::TA_SUCCESS => {
            if out_size != 0 {
                unsafe {
                    outaroondown.set_len(out_size_begin);
                    outaroonup.set_len(out_size_begin);
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

pub fn ta_aroonosc(
    high_ptr: *const f64,
    low_ptr: *const f64,
    len: usize,
    kwargs: &TimePeriodKwargs,
) -> Result<Vec<f64>, TA_RetCode> {
    let mut out_begin: TA_Integer = 0;
    let mut out_size: TA_Integer = 0;
    let begin_idx = check_begin_idx2(len, high_ptr, low_ptr) as i32;
    let end_idx = len as i32 - begin_idx - 1;
    let lookback = begin_idx + unsafe { TA_AROONOSC_Lookback(kwargs.timeperiod) };
    let (mut out, ptr) = make_vec(len, lookback);
    let ret_code = unsafe {
        TA_AROONOSC(
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

pub fn ta_bop(
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
    let lookback = begin_idx + unsafe { TA_BOP_Lookback() };
    let (mut out, ptr) = make_vec(len, lookback);
    let ret_code = unsafe {
        TA_BOP(
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
            unsafe {
                out.set_len(out_size_begin);
            }
            Ok(out)
        }
        _ => Err(ret_code),
    }
}

pub fn ta_cci(
    high_ptr: *const f64,
    low_ptr: *const f64,
    close_ptr: *const f64,
    len: usize,
    kwargs: &TimePeriodKwargs,
) -> Result<Vec<f64>, TA_RetCode> {
    let mut out_begin: TA_Integer = 0;
    let mut out_size: TA_Integer = 0;
    let begin_idx = check_begin_idx3(len, high_ptr, low_ptr, close_ptr) as i32;
    let end_idx = len as i32 - begin_idx - 1;
    let lookback = begin_idx + unsafe { TA_CCI_Lookback(kwargs.timeperiod) };
    let (mut out, ptr) = make_vec(len, lookback);
    let ret_code = unsafe {
        TA_CCI(
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

pub fn ta_cmo(
    input_ptr: *const f64,
    len: usize,
    kwargs: &TimePeriodKwargs,
) -> Result<Vec<f64>, TA_RetCode> {
    let mut out_begin: TA_Integer = 0;
    let mut out_size: TA_Integer = 0;
    let begin_idx = check_begin_idx1(len, input_ptr) as i32;
    let end_idx = len as i32 - begin_idx - 1;
    let lookback = begin_idx + unsafe { TA_CMO_Lookback(kwargs.timeperiod) };
    let (mut out, ptr) = make_vec(len, lookback);
    let ret_code = unsafe {
        TA_CMO(
            0,
            end_idx,
            input_ptr.offset(begin_idx as isize),
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

pub fn ta_dx(
    high_ptr: *const f64,
    low_ptr: *const f64,
    close_ptr: *const f64,
    len: usize,
    kwargs: &TimePeriodKwargs,
) -> Result<Vec<f64>, TA_RetCode> {
    let mut out_begin: TA_Integer = 0;
    let mut out_size: TA_Integer = 0;
    let begin_idx = check_begin_idx3(len, high_ptr, low_ptr, close_ptr) as i32;
    let end_idx = len as i32 - begin_idx - 1;
    let lookback = begin_idx + unsafe { TA_DX_Lookback(kwargs.timeperiod) };
    let (mut outdx, ptr) = make_vec(len, lookback);
    let ret_code = unsafe {
        TA_DX(
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
                    outdx.set_len(out_size_begin);
                }
            } else {
                unsafe {
                    outdx.set_len(len);
                }
            }
            Ok(outdx)
        }
        _ => Err(ret_code),
    }
}

#[derive(Builder, Deserialize)]
pub struct MacdKwargs {
    #[builder(default = "12")]
    pub fastperiod: i32,
    #[builder(default = "26")]
    pub slowperiod: i32,
    #[builder(default = "9")]
    pub signalperiod: i32,
}

pub fn ta_macd(
    input_ptr: *const f64,
    len: usize,
    kwargs: &MacdKwargs,
) -> Result<(Vec<f64>, Vec<f64>, Vec<f64>), TA_RetCode> {
    let mut out_begin: TA_Integer = 0;
    let mut out_size: TA_Integer = 0;
    let begin_idx = check_begin_idx1(len, input_ptr) as i32;
    let end_idx = len as i32 - begin_idx - 1;
    let lookback = begin_idx
        + unsafe { TA_MACD_Lookback(kwargs.fastperiod, kwargs.slowperiod, kwargs.signalperiod) };
    let (mut outmacd, ptr1) = make_vec(len, lookback);
    let (mut outmacdsignal, ptr2) = make_vec(len, lookback);
    let (mut outmacdhist, ptr3) = make_vec(len, lookback);
    let ret_code = unsafe {
        TA_MACD(
            0,
            end_idx,
            input_ptr.offset(begin_idx as isize),
            kwargs.fastperiod,
            kwargs.slowperiod,
            kwargs.signalperiod,
            &mut out_begin,
            &mut out_size,
            ptr1,
            ptr2,
            ptr3,
        )
    };
    let out_size_begin = (begin_idx + out_begin + out_size) as usize;

    match ret_code {
        TA_RetCode::TA_SUCCESS => {
            unsafe {
                outmacd.set_len(out_size_begin);
                outmacdsignal.set_len(out_size_begin);
                outmacdhist.set_len(out_size_begin);
            }
            Ok((outmacd, outmacdsignal, outmacdhist))
        }
        _ => Err(ret_code),
    }
}

#[derive(Builder, Deserialize)]
pub struct MacdExtKwargs {
    #[builder(default = "12")]
    pub fastperiod: i32,
    #[builder(default = "1")]
    pub fastmatype: TA_MAType,
    #[builder(default = "26")]
    pub slowperiod: i32,
    pub slowmatype: TA_MAType,
    #[builder(default = "9")]
    pub signalperiod: i32,
    pub signalmatype: TA_MAType,
}

pub fn ta_macdext(
    input_ptr: *const f64,
    len: usize,
    kwargs: &MacdExtKwargs,
) -> Result<(Vec<f64>, Vec<f64>, Vec<f64>), TA_RetCode> {
    let mut out_begin: TA_Integer = 0;
    let mut out_size: TA_Integer = 0;
    let begin_idx = check_begin_idx1(len, input_ptr) as i32;
    let end_idx = len as i32 - begin_idx - 1;
    let lookback = begin_idx
        + unsafe {
            TA_MACDEXT_Lookback(
                kwargs.fastperiod,
                kwargs.fastmatype,
                kwargs.slowperiod,
                kwargs.slowmatype,
                kwargs.signalperiod,
                kwargs.signalmatype,
            )
        };
    let (mut outmacd, ptr1) = make_vec(len, lookback);
    let (mut outmacdsignal, ptr2) = make_vec(len, lookback);
    let (mut outmacdhist, ptr3) = make_vec(len, lookback);
    let ret_code = unsafe {
        TA_MACDEXT(
            0,
            end_idx,
            input_ptr.offset(begin_idx as isize),
            kwargs.fastperiod,
            kwargs.fastmatype,
            kwargs.slowperiod,
            kwargs.slowmatype,
            kwargs.signalperiod,
            kwargs.signalmatype,
            &mut out_begin,
            &mut out_size,
            ptr1,
            ptr2,
            ptr3,
        )
    };
    let out_size_begin = (begin_idx + out_begin + out_size) as usize;

    match ret_code {
        TA_RetCode::TA_SUCCESS => {
            unsafe {
                outmacd.set_len(out_size_begin);
                outmacdsignal.set_len(out_size_begin);
                outmacdhist.set_len(out_size_begin);
            }
            Ok((outmacd, outmacdsignal, outmacdhist))
        }
        _ => Err(ret_code),
    }
}

#[derive(Builder, Deserialize)]
pub struct MacdFixKwargs {
    #[builder(default = "9")]
    pub signalperiod: i32,
}

pub fn ta_macdfix(
    input_ptr: *const f64,
    len: usize,
    kwargs: &MacdFixKwargs,
) -> Result<(Vec<f64>, Vec<f64>, Vec<f64>), TA_RetCode> {
    let mut out_begin: TA_Integer = 0;
    let mut out_size: TA_Integer = 0;
    let begin_idx = check_begin_idx1(len, input_ptr) as i32;
    let end_idx = len as i32 - begin_idx - 1;
    let lookback = begin_idx + unsafe { TA_MACDFIX_Lookback(kwargs.signalperiod) };
    let (mut outmacd, ptr1) = make_vec(len, lookback);
    let (mut outmacdsignal, ptr2) = make_vec(len, lookback);
    let (mut outmacdhist, ptr3) = make_vec(len, lookback);
    let ret_code = unsafe {
        TA_MACDFIX(
            0,
            end_idx,
            input_ptr.offset(begin_idx as isize),
            kwargs.signalperiod,
            &mut out_begin,
            &mut out_size,
            ptr1,
            ptr2,
            ptr3,
        )
    };
    let out_size_begin = (begin_idx + out_begin + out_size) as usize;

    match ret_code {
        TA_RetCode::TA_SUCCESS => {
            unsafe {
                outmacd.set_len(out_size_begin);
                outmacdsignal.set_len(out_size_begin);
                outmacdhist.set_len(out_size_begin);
            }
            Ok((outmacd, outmacdsignal, outmacdhist))
        }
        _ => Err(ret_code),
    }
}

pub fn ta_mfi(
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
    let lookback = begin_idx + unsafe { TA_MFI_Lookback(kwargs.timeperiod) };
    let (mut out, ptr) = make_vec(len, lookback);
    let ret_code = unsafe {
        TA_MFI(
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

pub fn ta_minus_di(
    high_ptr: *const f64,
    low_ptr: *const f64,
    close_ptr: *const f64,
    len: usize,
    kwargs: &TimePeriodKwargs,
) -> Result<Vec<f64>, TA_RetCode> {
    let mut out_begin: TA_Integer = 0;
    let mut out_size: TA_Integer = 0;
    let begin_idx = check_begin_idx3(len, high_ptr, low_ptr, close_ptr) as i32;
    let end_idx = len as i32 - begin_idx - 1;
    let lookback = begin_idx + unsafe { TA_MINUS_DI_Lookback(kwargs.timeperiod) };
    let (mut out, ptr) = make_vec(len, lookback);
    let ret_code = unsafe {
        TA_MINUS_DI(
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
                unsafe { out.set_len(out_size_begin) }
            } else {
                unsafe { out.set_len(len) }
            }
            Ok(out)
        }
        _ => Err(ret_code),
    }
}

pub fn ta_minus_dm(
    high_ptr: *const f64,
    low_ptr: *const f64,
    len: usize,
    kwargs: &TimePeriodKwargs,
) -> Result<Vec<f64>, TA_RetCode> {
    let mut out_begin: TA_Integer = 0;
    let mut out_size = 0;
    let begin_idx = check_begin_idx2(len, high_ptr, low_ptr) as i32;
    let end_idx = len as i32 - begin_idx - 1;
    let lookback = begin_idx + unsafe { TA_MINUS_DM_Lookback(kwargs.timeperiod) };
    let (mut out, ptr) = make_vec(len, lookback);
    let ret_code = unsafe {
        TA_MINUS_DM(
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
                unsafe { out.set_len(out_size_begin) }
            } else {
                unsafe { out.set_len(len) }
            }
            Ok(out)
        }
        _ => Err(ret_code),
    }
}

pub fn ta_mom(
    input_ptr: *const f64,
    len: usize,
    kwargs: &TimePeriodKwargs,
) -> Result<Vec<f64>, TA_RetCode> {
    let mut out_begin = 0;
    let mut out_size = 0;
    let begin_idx = check_begin_idx1(len, input_ptr) as i32;
    let end_idx = len as i32 - begin_idx - 1;
    let lookback = begin_idx + unsafe { TA_MOM_Lookback(kwargs.timeperiod) };
    let (mut out, ptr) = make_vec(len, lookback);
    let ret_code = unsafe {
        TA_MOM(
            0,
            end_idx,
            input_ptr.offset(begin_idx as isize),
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
                unsafe { out.set_len(out_size_begin) }
            } else {
                unsafe { out.set_len(len) }
            }
            Ok(out)
        }
        _ => Err(ret_code),
    }
}

pub fn ta_plus_di(
    high_ptr: *const f64,
    low_ptr: *const f64,
    close_ptr: *const f64,
    len: usize,
    kwargs: &TimePeriodKwargs,
) -> Result<Vec<f64>, TA_RetCode> {
    let mut out_begin = 0;
    let mut out_size = 0;
    let begin_idx = check_begin_idx3(len, high_ptr, low_ptr, close_ptr) as i32;
    let end_idx = len as i32 - begin_idx - 1;
    let lookback = begin_idx + unsafe { TA_PLUS_DI_Lookback(kwargs.timeperiod) };
    let (mut out, ptr) = make_vec(len, lookback);
    let ret_code = unsafe {
        TA_PLUS_DI(
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
                unsafe { out.set_len(out_size_begin) }
            } else {
                unsafe { out.set_len(len) }
            }
            Ok(out)
        }
        _ => Err(ret_code),
    }
}

pub fn ta_plus_dm(
    high_ptr: *const f64,
    low_ptr: *const f64,
    len: usize,
    kwargs: &TimePeriodKwargs,
) -> Result<Vec<f64>, TA_RetCode> {
    let mut out_begin = 0;
    let mut out_size = 0;
    let begin_idx = check_begin_idx2(len, high_ptr, low_ptr) as i32;
    let end_idx = len as i32 - begin_idx - 1;
    let lookback = begin_idx + unsafe { TA_PLUS_DM_Lookback(kwargs.timeperiod) };
    let (mut out, ptr) = make_vec(len, lookback);
    let ret_code = unsafe {
        TA_PLUS_DM(
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
                unsafe { out.set_len(out_size_begin) }
            } else {
                unsafe { out.set_len(len) }
            }
            Ok(out)
        }
        _ => Err(ret_code),
    }
}

#[derive(Builder, Deserialize)]
pub struct PpoKwargs {
    #[builder(default = "12")]
    pub fastperiod: i32,
    #[builder(default = "26")]
    pub slowperiod: i32,
    pub matype: TA_MAType,
}

pub fn ta_ppo(
    input_ptr: *const f64,
    len: usize,
    kwargs: &PpoKwargs,
) -> Result<Vec<f64>, TA_RetCode> {
    let mut out_begin = 0;
    let mut out_size = 0;
    let begin_idx = check_begin_idx1(len, input_ptr) as i32;
    let end_idx = len as i32 - begin_idx - 1;
    let lookback =
        begin_idx + unsafe { TA_PPO_Lookback(kwargs.fastperiod, kwargs.slowperiod, kwargs.matype) };
    let (mut out, ptr) = make_vec(len, lookback);
    let ret_code = unsafe {
        TA_PPO(
            0,
            end_idx,
            input_ptr.offset(begin_idx as isize),
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
                unsafe { out.set_len(out_size_begin) }
            } else {
                unsafe { out.set_len(len) }
            }
            Ok(out)
        }
        _ => Err(ret_code),
    }
}

pub fn ta_roc(
    input_ptr: *const f64,
    len: usize,
    kwargs: &TimePeriodKwargs,
) -> Result<Vec<f64>, TA_RetCode> {
    let mut out_begin = 0;
    let mut out_size = 0;
    let begin_idx = check_begin_idx1(len, input_ptr) as i32;
    let end_idx = len as i32 - begin_idx - 1;
    let lookback = begin_idx + unsafe { TA_ROC_Lookback(kwargs.timeperiod) };
    let (mut out, ptr) = make_vec(len, lookback);
    let ret_code = unsafe {
        TA_ROC(
            0,
            end_idx,
            input_ptr.offset(begin_idx as isize),
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
                unsafe { out.set_len(out_size_begin) }
            } else {
                unsafe { out.set_len(len) }
            }
            Ok(out)
        }
        _ => Err(ret_code),
    }
}

pub fn ta_rocp(
    input_ptr: *const f64,
    len: usize,
    kwargs: &TimePeriodKwargs,
) -> Result<Vec<f64>, TA_RetCode> {
    let mut out_begin = 0;
    let mut out_size = 0;
    let begin_idx = check_begin_idx1(len, input_ptr) as i32;
    let end_idx = len as i32 - begin_idx - 1;
    let lookback = begin_idx + unsafe { TA_ROCP_Lookback(kwargs.timeperiod) };
    let (mut out, ptr) = make_vec(len, lookback);
    let ret_code = unsafe {
        TA_ROCP(
            0,
            end_idx,
            input_ptr.offset(begin_idx as isize),
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
                unsafe { out.set_len(out_size_begin) }
            } else {
                unsafe { out.set_len(len) }
            }
            Ok(out)
        }
        _ => Err(ret_code),
    }
}

pub fn ta_rocr(
    input_ptr: *const f64,
    len: usize,
    kwargs: &TimePeriodKwargs,
) -> Result<Vec<f64>, TA_RetCode> {
    let mut out_begin = 0;
    let mut out_size = 0;
    let begin_idx = check_begin_idx1(len, input_ptr) as i32;
    let end_idx = len as i32 - begin_idx - 1;
    let lookback = begin_idx + unsafe { TA_ROCR_Lookback(kwargs.timeperiod) };
    let (mut out, ptr) = make_vec(len, lookback);
    let ret_code = unsafe {
        TA_ROCR(
            0,
            end_idx,
            input_ptr.offset(begin_idx as isize),
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
                unsafe { out.set_len(out_size_begin) }
            } else {
                unsafe { out.set_len(len) }
            }
            Ok(out)
        }
        _ => Err(ret_code),
    }
}

pub fn ta_rocr100(
    input_ptr: *const f64,
    len: usize,
    kwargs: &TimePeriodKwargs,
) -> Result<Vec<f64>, TA_RetCode> {
    let mut out_begin = 0;
    let mut out_size = 0;
    let begin_idx = check_begin_idx1(len, input_ptr) as i32;
    let end_idx = len as i32 - begin_idx - 1;
    let lookback = begin_idx + unsafe { TA_ROCR100_Lookback(kwargs.timeperiod) };
    let (mut out, ptr) = make_vec(len, lookback);
    let ret_code = unsafe {
        TA_ROCR100(
            0,
            end_idx,
            input_ptr.offset(begin_idx as isize),
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
                unsafe { out.set_len(out_size_begin) }
            } else {
                unsafe { out.set_len(len) }
            }
            Ok(out)
        }
        _ => Err(ret_code),
    }
}

pub fn ta_rsi(
    input_ptr: *const f64,
    len: usize,
    kwargs: &TimePeriodKwargs,
) -> Result<Vec<f64>, TA_RetCode> {
    let mut out_begin = 0;
    let mut out_size = 0;
    let begin_idx = check_begin_idx1(len, input_ptr) as i32;
    let end_idx = len as i32 - begin_idx - 1;
    let lookback = begin_idx + unsafe { TA_RSI_Lookback(kwargs.timeperiod) };
    let (mut out, ptr) = make_vec(len, lookback);
    let ret_code = unsafe {
        TA_RSI(
            0,
            end_idx,
            input_ptr.offset(begin_idx as isize),
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
                unsafe { out.set_len(out_size_begin) }
            } else {
                unsafe { out.set_len(len) }
            }
            Ok(out)
        }
        _ => Err(ret_code),
    }
}

#[derive(Builder, Deserialize)]
pub struct StochKwargs {
    #[builder(default = "12")]
    pub fastk_period: i32,
    #[builder(default = "3")]
    pub slowk_period: i32,
    pub slowk_matype: TA_MAType,
    #[builder(default = "3")]
    pub slowd_period: i32,
    pub slowd_matype: TA_MAType,
}

pub fn ta_stoch(
    high_ptr: *const f64,
    low_ptr: *const f64,
    close_ptr: *const f64,
    len: usize,
    kwargs: &StochKwargs,
) -> Result<(Vec<f64>, Vec<f64>), TA_RetCode> {
    let mut out_begin = 0;
    let mut out_size = 0;
    let begin_idx = check_begin_idx3(len, high_ptr, low_ptr, close_ptr) as i32;
    let end_idx = len as i32 - begin_idx - 1;
    let lookback = begin_idx
        + unsafe {
            TA_STOCH_Lookback(
                kwargs.fastk_period,
                kwargs.slowk_period,
                kwargs.slowk_matype,
                kwargs.slowd_period,
                kwargs.slowd_matype,
            )
        };
    let (mut outslowk, ptr1) = make_vec(len, lookback);
    let (mut outslowd, ptr2) = make_vec(len, lookback);
    let ret_code = unsafe {
        TA_STOCH(
            0,
            end_idx,
            high_ptr.offset(begin_idx as isize),
            low_ptr.offset(begin_idx as isize),
            close_ptr.offset(begin_idx as isize),
            kwargs.fastk_period,
            kwargs.slowk_period,
            kwargs.slowk_matype,
            kwargs.slowd_period,
            kwargs.slowd_matype,
            &mut out_begin,
            &mut out_size,
            ptr1,
            ptr2,
        )
    };
    let out_size_begin = (begin_idx + out_begin + out_size) as usize;

    match ret_code {
        TA_RetCode::TA_SUCCESS => {
            if out_size != 0 {
                unsafe {
                    outslowk.set_len(out_size_begin);
                    outslowd.set_len(out_size_begin);
                }
            } else {
                unsafe {
                    outslowk.set_len(len);
                    outslowd.set_len(len);
                }
            }
            Ok((outslowk, outslowd))
        }
        _ => Err(ret_code),
    }
}

#[derive(Builder, Deserialize)]
pub struct StochfKwargs {
    #[builder(default = "12")]
    pub fastk_period: i32,
    #[builder(default = "3")]
    pub fastd_period: i32,
    pub fastd_matype: TA_MAType,
}

pub fn ta_stochf(
    high_ptr: *const f64,
    low_ptr: *const f64,
    close_ptr: *const f64,
    len: usize,
    kwargs: &StochfKwargs,
) -> Result<(Vec<f64>, Vec<f64>), TA_RetCode> {
    let mut out_begin = 0;
    let mut out_size = 0;
    let begin_idx = check_begin_idx3(len, high_ptr, low_ptr, close_ptr) as i32;
    let end_idx = len as i32 - begin_idx - 1;
    let lookback = begin_idx
        + unsafe {
            TA_STOCHF_Lookback(
                kwargs.fastk_period,
                kwargs.fastd_period,
                kwargs.fastd_matype,
            )
        };
    let (mut outfastk, ptr1) = make_vec(len, lookback);
    let (mut outfastd, ptr2) = make_vec(len, lookback);
    let ret_code = unsafe {
        TA_STOCHF(
            0,
            end_idx,
            high_ptr.offset(begin_idx as isize),
            low_ptr.offset(begin_idx as isize),
            close_ptr.offset(begin_idx as isize),
            kwargs.fastk_period,
            kwargs.fastd_period,
            kwargs.fastd_matype,
            &mut out_begin,
            &mut out_size,
            ptr1,
            ptr2,
        )
    };
    let out_size_begin = (begin_idx + out_begin + out_size) as usize;

    match ret_code {
        TA_RetCode::TA_SUCCESS => {
            if out_size != 0 {
                unsafe {
                    outfastk.set_len(out_size_begin);
                    outfastd.set_len(out_size_begin);
                }
            } else {
                unsafe {
                    outfastk.set_len(len);
                    outfastd.set_len(len);
                }
            }
            Ok((outfastk, outfastd))
        }
        _ => Err(ret_code),
    }
}

#[derive(Builder, Deserialize)]
pub struct StochRsiKwargs {
    #[builder(default = "14")]
    pub timeperiod: i32,
    #[builder(default = "9")]
    pub fastk_period: i32,
    #[builder(default = "3")]
    pub fastd_period: i32,
    pub fastd_matype: TA_MAType,
}

pub fn ta_stochrsi(
    input_ptr: *const f64,
    len: usize,
    kwargs: &StochRsiKwargs,
) -> Result<(Vec<f64>, Vec<f64>), TA_RetCode> {
    let mut out_begin = 0;
    let mut out_size = 0;
    let begin_idx = check_begin_idx1(len, input_ptr) as i32;
    let end_idx = len as i32 - begin_idx - 1;
    let lookback = begin_idx
        + unsafe {
            TA_STOCHRSI_Lookback(
                kwargs.timeperiod,
                kwargs.fastk_period,
                kwargs.fastd_period,
                kwargs.fastd_matype,
            )
        };
    let (mut outfastk, ptr1) = make_vec(len, lookback);
    let (mut outfastd, ptr2) = make_vec(len, lookback);
    let ret_code = unsafe {
        TA_STOCHRSI(
            0,
            end_idx,
            input_ptr.offset(begin_idx as isize),
            kwargs.timeperiod,
            kwargs.fastk_period,
            kwargs.fastd_period,
            kwargs.fastd_matype,
            &mut out_begin,
            &mut out_size,
            ptr1,
            ptr2,
        )
    };
    let out_size_begin = (begin_idx + out_begin + out_size) as usize;

    match ret_code {
        TA_RetCode::TA_SUCCESS => {
            if out_size != 0 {
                unsafe {
                    outfastk.set_len(out_size_begin);
                    outfastd.set_len(out_size_begin);
                }
            } else {
                unsafe {
                    outfastk.set_len(len);
                    outfastd.set_len(len);
                }
            }
            Ok((outfastk, outfastd))
        }
        _ => Err(ret_code),
    }
}

pub fn ta_trix(
    input_ptr: *const f64,
    len: usize,
    kwargs: &TimePeriodKwargs,
) -> Result<Vec<f64>, TA_RetCode> {
    let mut out_begin = 0;
    let mut out_size = 0;
    let begin_idx = check_begin_idx1(len, input_ptr) as i32;
    let end_idx = len as i32 - begin_idx - 1;
    let lookback = begin_idx + unsafe { TA_TRIX_Lookback(kwargs.timeperiod) };
    let (mut out, ptr) = make_vec(len, lookback);
    let ret_code = unsafe {
        TA_TRIX(
            0,
            end_idx,
            input_ptr.offset(begin_idx as isize),
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
                unsafe { out.set_len(out_size_begin) }
            } else {
                unsafe { out.set_len(len) }
            }
            Ok(out)
        }
        _ => Err(ret_code),
    }
}

#[derive(Builder, Deserialize)]
pub struct UltOscKwargs {
    #[builder(default = "7")]
    pub timeperiod1: i32,
    #[builder(default = "14")]
    pub timeperiod2: i32,
    #[builder(default = "28")]
    pub timeperiod3: i32,
}

pub fn ta_ultosc(
    high_ptr: *const f64,
    low_ptr: *const f64,
    close_ptr: *const f64,
    len: usize,
    kwargs: &UltOscKwargs,
) -> Result<Vec<f64>, TA_RetCode> {
    let mut out_begin = 0;
    let mut out_size = 0;
    let begin_idx = check_begin_idx3(len, high_ptr, low_ptr, close_ptr) as i32;
    let end_idx = len as i32 - begin_idx - 1;
    let lookback = begin_idx
        + unsafe { TA_ULTOSC_Lookback(kwargs.timeperiod1, kwargs.timeperiod2, kwargs.timeperiod3) };
    let (mut out, ptr) = make_vec(len, lookback);
    let ret_code = unsafe {
        TA_ULTOSC(
            0,
            end_idx,
            high_ptr.offset(begin_idx as isize),
            low_ptr.offset(begin_idx as isize),
            close_ptr.offset(begin_idx as isize),
            kwargs.timeperiod1,
            kwargs.timeperiod2,
            kwargs.timeperiod3,
            &mut out_begin,
            &mut out_size,
            ptr,
        )
    };
    let out_size_begin = (begin_idx + out_begin + out_size) as usize;

    match ret_code {
        TA_RetCode::TA_SUCCESS => {
            if out_size != 0 {
                unsafe { out.set_len(out_size_begin) }
            } else {
                unsafe { out.set_len(len) }
            }
            Ok(out)
        }
        _ => Err(ret_code),
    }
}

pub fn ta_willr(
    high_ptr: *const f64,
    low_ptr: *const f64,
    close_ptr: *const f64,
    len: usize,
    kwargs: &TimePeriodKwargs,
) -> Result<Vec<f64>, TA_RetCode> {
    let mut out_begin = 0;
    let mut out_size = 0;
    let begin_idx = check_begin_idx3(len, high_ptr, low_ptr, close_ptr) as i32;
    let end_idx = len as i32 - begin_idx - 1;
    let lookback = begin_idx + unsafe { TA_WILLR_Lookback(kwargs.timeperiod) };
    let (mut out, ptr) = make_vec(len, lookback);
    let ret_code = unsafe {
        TA_WILLR(
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
                unsafe { out.set_len(out_size_begin) }
            } else {
                unsafe { out.set_len(len) }
            }
            Ok(out)
        }
        _ => Err(ret_code),
    }
}
