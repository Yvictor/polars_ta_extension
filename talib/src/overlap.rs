use crate::common::TimePeriodKwargs;
use crate::utils::{check_begin_idx1, check_begin_idx2, make_vec};
use derive_builder::Builder;
use serde::Deserialize;
use talib_sys::{
    TA_BBANDS_Lookback, TA_DEMA_Lookback, TA_EMA_Lookback, TA_HT_TRENDLINE_Lookback, TA_Integer,
    TA_KAMA_Lookback, TA_MAMA_Lookback, TA_MAType, TA_MAVP_Lookback, TA_MA_Lookback,
    TA_MIDPOINT_Lookback, TA_MIDPRICE_Lookback, TA_RetCode, TA_SAREXT_Lookback, TA_SAR_Lookback,
    TA_SMA_Lookback, TA_T3_Lookback, TA_TEMA_Lookback, TA_TRIMA_Lookback, TA_WMA_Lookback,
    TA_BBANDS, TA_DEMA, TA_EMA, TA_HT_TRENDLINE, TA_KAMA, TA_MA, TA_MAMA, TA_MAVP, TA_MIDPOINT,
    TA_MIDPRICE, TA_SAR, TA_SAREXT, TA_SMA, TA_T3, TA_TEMA, TA_TRIMA, TA_WMA,
};
use crate::utils::cannot_produce_output;
use crate::utils::make_default_vec;
use crate::utils::check_begin_idx3;
use talib_sys::{TA_ACCBANDS_Lookback, TA_ACCBANDS};
use talib_sys::{TA_DONCHIAN_Lookback, TA_DONCHIAN};
use talib_sys::{TA_HMA_Lookback, TA_HMA};
use talib_sys::{TA_KC_Lookback, TA_KC};
use talib_sys::{TA_RMA_Lookback, TA_RMA};
use talib_sys::{TA_SUPERTREND_Lookback, TA_SUPERTREND};
use talib_sys::{TA_VWMA_Lookback, TA_VWMA};
use talib_sys::{TA_ZLEMA_Lookback, TA_ZLEMA};

#[derive(Builder, Deserialize)]
pub struct BBANDSKwargs {
    #[builder(default = "5")]
    pub timeperiod: i32,
    #[builder(default = "2.0")]
    pub nbdevup: f64,
    #[builder(default = "2.0")]
    pub nbdevdn: f64,
    pub matype: TA_MAType,
}

pub fn ta_bbands(
    real_ptr: *const f64,
    len: usize,
    kwargs: &BBANDSKwargs,
) -> Result<(Vec<f64>, Vec<f64>, Vec<f64>), TA_RetCode> {
    let mut out_begin: TA_Integer = 0;
    let mut out_size: TA_Integer = 0;
    let begin_idx = check_begin_idx1(len, real_ptr) as i32;
    let end_idx = len as i32 - begin_idx - 1;
    let lookback = begin_idx
        + unsafe {
            TA_BBANDS_Lookback(
                kwargs.timeperiod,
                kwargs.nbdevup,
                kwargs.nbdevdn,
                kwargs.matype,
            )
        };
    let (mut outrealupperband, u_ptr) = make_vec(len, lookback);
    let (mut outrealmiddleband, m_ptr) = make_vec(len, lookback);
    let (mut outreallowerband, l_ptr) = make_vec(len, lookback);
    let ret_code = unsafe {
        TA_BBANDS(
            0,
            end_idx,
            real_ptr.offset(begin_idx as isize),
            kwargs.timeperiod,
            kwargs.nbdevup,
            kwargs.nbdevdn,
            kwargs.matype,
            &mut out_begin,
            &mut out_size,
            u_ptr,
            m_ptr,
            l_ptr,
        )
    };
    let out_size_begin = (begin_idx + out_begin + out_size) as usize;
    match ret_code {
        TA_RetCode::TA_SUCCESS => {
            if out_size != 0 {
                unsafe {
                    outrealupperband.set_len(out_size_begin);
                    outrealmiddleband.set_len(out_size_begin);
                    outreallowerband.set_len(out_size_begin);
                }
            } else {
                unsafe {
                    outrealupperband.set_len(len);
                    outrealmiddleband.set_len(len);
                    outreallowerband.set_len(len);
                }
            }
            Ok((outrealupperband, outrealmiddleband, outreallowerband))
        }
        _ => Err(ret_code),
    }
}

pub fn ta_dema(
    real_ptr: *const f64,
    len: usize,
    kwargs: &TimePeriodKwargs,
) -> Result<Vec<f64>, TA_RetCode> {
    let mut out_begin: TA_Integer = 0;
    let mut out_size: TA_Integer = 0;
    let begin_idx = check_begin_idx1(len, real_ptr) as i32;
    let end_idx = len as i32 - begin_idx - 1;
    let lookback = begin_idx + unsafe { TA_DEMA_Lookback(kwargs.timeperiod) };
    let (mut out, ptr) = make_vec(len, lookback);
    let ret_code = unsafe {
        TA_DEMA(
            0,
            end_idx,
            real_ptr.offset(begin_idx as isize),
            kwargs.timeperiod,
            &mut out_begin,
            &mut out_size,
            ptr,
        )
    };
    match ret_code {
        TA_RetCode::TA_SUCCESS => {
            let out_size_begin = (begin_idx + out_begin + out_size) as usize;
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

pub fn ta_ema(
    real_ptr: *const f64,
    len: usize,
    kwargs: &TimePeriodKwargs,
) -> Result<Vec<f64>, TA_RetCode> {
    let mut out_begin: TA_Integer = 0;
    let mut out_size: TA_Integer = 0;
    let begin_idx = check_begin_idx1(len, real_ptr) as i32;
    let end_idx = len as i32 - begin_idx - 1;
    let lookback = begin_idx + unsafe { TA_EMA_Lookback(kwargs.timeperiod) };
    let (mut out, ptr) = make_vec(len, lookback);
    let ret_code = unsafe {
        TA_EMA(
            0,
            end_idx,
            real_ptr.offset(begin_idx as isize),
            kwargs.timeperiod,
            &mut out_begin,
            &mut out_size,
            ptr,
        )
    };
    match ret_code {
        TA_RetCode::TA_SUCCESS => {
            let out_size_begin = (begin_idx + out_begin + out_size) as usize;
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

pub fn ta_ht_trendline(real_ptr: *const f64, len: usize) -> Result<Vec<f64>, TA_RetCode> {
    let mut out_begin: TA_Integer = 0;
    let mut out_size: TA_Integer = 0;
    let begin_idx = check_begin_idx1(len, real_ptr) as i32;
    let end_idx = len as i32 - begin_idx - 1;
    let lookback = begin_idx + unsafe { TA_HT_TRENDLINE_Lookback() };
    let (mut out, ptr) = make_vec(len, lookback);
    let ret_code = unsafe {
        TA_HT_TRENDLINE(
            0,
            end_idx,
            real_ptr.offset(begin_idx as isize),
            &mut out_begin,
            &mut out_size,
            ptr,
        )
    };
    match ret_code {
        TA_RetCode::TA_SUCCESS => {
            let out_size_begin = (begin_idx + out_begin + out_size) as usize;
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

pub fn ta_kama(
    real_ptr: *const f64,
    len: usize,
    kwargs: &TimePeriodKwargs,
) -> Result<Vec<f64>, TA_RetCode> {
    let mut out_begin: TA_Integer = 0;
    let mut out_size: TA_Integer = 0;
    let begin_idx = check_begin_idx1(len, real_ptr) as i32;
    let end_idx = len as i32 - begin_idx - 1;
    let lookback = begin_idx + unsafe { TA_KAMA_Lookback(kwargs.timeperiod) };
    let (mut out, ptr) = make_vec(len, lookback);
    let ret_code = unsafe {
        TA_KAMA(
            0,
            end_idx,
            real_ptr.offset(begin_idx as isize),
            kwargs.timeperiod,
            &mut out_begin,
            &mut out_size,
            ptr,
        )
    };
    match ret_code {
        TA_RetCode::TA_SUCCESS => {
            let out_size_begin = (begin_idx + out_begin + out_size) as usize;
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
pub struct MaKwargs {
    #[builder(default = "30")]
    pub timeperiod: i32,
    pub matype: TA_MAType,
}

pub fn ta_ma(real_ptr: *const f64, len: usize, kwargs: &MaKwargs) -> Result<Vec<f64>, TA_RetCode> {
    let mut out_begin: TA_Integer = 0;
    let mut out_size: TA_Integer = 0;
    let begin_idx = check_begin_idx1(len, real_ptr) as i32;
    let end_idx = len as i32 - begin_idx - 1;
    let lookback = begin_idx + unsafe { TA_MA_Lookback(kwargs.timeperiod, kwargs.matype) };
    let (mut out, ptr) = make_vec(len, lookback);
    let ret_code = unsafe {
        TA_MA(
            0,
            end_idx,
            real_ptr.offset(begin_idx as isize),
            kwargs.timeperiod,
            kwargs.matype,
            &mut out_begin,
            &mut out_size,
            ptr,
        )
    };
    match ret_code {
        TA_RetCode::TA_SUCCESS => {
            let out_size_begin = (begin_idx + out_begin + out_size) as usize;
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
pub struct MamaKwargs {
    #[builder(default = "0.5")]
    pub fastlimit: f64,
    #[builder(default = "0.05")]
    pub slowlimit: f64,
}

pub fn ta_mama(
    real_ptr: *const f64,
    len: usize,
    kwargs: &MamaKwargs,
) -> Result<(Vec<f64>, Vec<f64>), TA_RetCode> {
    // output: mama, fama
    let mut out_begin: TA_Integer = 0;
    let mut out_size: TA_Integer = 0;
    let begin_idx = check_begin_idx1(len, real_ptr) as i32;
    let end_idx = len as i32 - begin_idx - 1;
    let lookback = begin_idx + unsafe { TA_MAMA_Lookback(kwargs.fastlimit, kwargs.slowlimit) };
    let (mut outreal, r_ptr) = make_vec(len, lookback);
    let (mut outimag, i_ptr) = make_vec(len, lookback);
    let ret_code = unsafe {
        TA_MAMA(
            0,
            end_idx,
            real_ptr.offset(begin_idx as isize),
            kwargs.fastlimit,
            kwargs.slowlimit,
            &mut out_begin,
            &mut out_size,
            r_ptr,
            i_ptr,
        )
    };
    let out_size_begin = (begin_idx + out_begin + out_size) as usize;
    match ret_code {
        TA_RetCode::TA_SUCCESS => {
            if out_size != 0 {
                unsafe {
                    outreal.set_len(out_size_begin);
                    outimag.set_len(out_size_begin);
                }
            } else {
                unsafe {
                    outreal.set_len(len);
                    outimag.set_len(len);
                }
            }
            Ok((outreal, outimag))
        }
        _ => Err(ret_code),
    }
}

#[derive(Builder, Deserialize)]
pub struct MavpKwargs {
    #[builder(default = "3")]
    pub minperiod: i32,
    #[builder(default = "30")]
    pub maxperiod: i32,
    pub matype: TA_MAType,
}

pub fn ta_mavp(
    real_ptr: *const f64,
    periods_ptr: *const f64,
    len: usize,
    kwargs: &MavpKwargs,
) -> Result<Vec<f64>, TA_RetCode> {
    let mut out_begin: TA_Integer = 0;
    let mut out_size: TA_Integer = 0;
    let begin_idx = check_begin_idx2(len, real_ptr, periods_ptr) as i32;
    let end_idx = len as i32 - begin_idx - 1;
    let lookback =
        begin_idx + unsafe { TA_MAVP_Lookback(kwargs.minperiod, kwargs.maxperiod, kwargs.matype) };
    let (mut out, ptr) = make_vec(len, lookback);
    let ret_code = unsafe {
        TA_MAVP(
            0,
            end_idx,
            real_ptr.offset(begin_idx as isize),
            periods_ptr.offset(begin_idx as isize),
            kwargs.minperiod,
            kwargs.maxperiod,
            kwargs.matype,
            &mut out_begin,
            &mut out_size,
            ptr,
        )
    };
    match ret_code {
        TA_RetCode::TA_SUCCESS => {
            let out_size_begin = (begin_idx + out_begin + out_size) as usize;
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

pub fn ta_midpoint(
    real_ptr: *const f64,
    len: usize,
    kwargs: &TimePeriodKwargs,
) -> Result<Vec<f64>, TA_RetCode> {
    let mut out_begin: TA_Integer = 0;
    let mut out_size: TA_Integer = 0;
    let begin_idx = check_begin_idx1(len, real_ptr) as i32;
    let end_idx = len as i32 - begin_idx - 1;
    let lookback = begin_idx + unsafe { TA_MIDPOINT_Lookback(kwargs.timeperiod) };
    let (mut out, ptr) = make_vec(len, lookback);
    let ret_code = unsafe {
        TA_MIDPOINT(
            0,
            end_idx,
            real_ptr.offset(begin_idx as isize),
            kwargs.timeperiod,
            &mut out_begin,
            &mut out_size,
            ptr,
        )
    };
    match ret_code {
        TA_RetCode::TA_SUCCESS => {
            let out_size_begin = (begin_idx + out_begin + out_size) as usize;
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

pub fn ta_midprice(
    high_ptr: *const f64,
    low_ptr: *const f64,
    len: usize,
    kwargs: &TimePeriodKwargs,
) -> Result<Vec<f64>, TA_RetCode> {
    let mut out_begin: TA_Integer = 0;
    let mut out_size: TA_Integer = 0;
    let begin_idx = check_begin_idx2(len, high_ptr, low_ptr) as i32;
    let end_idx = len as i32 - begin_idx - 1;
    let lookback = begin_idx + unsafe { TA_MIDPRICE_Lookback(kwargs.timeperiod) };
    let (mut out, ptr) = make_vec(len, lookback);
    let ret_code = unsafe {
        TA_MIDPRICE(
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
pub struct SarKwargs {
    #[builder(default = "0.02")]
    pub acceleration: f64,
    #[builder(default = "0.2")]
    pub maximum: f64,
}

pub fn ta_sar(
    high_ptr: *const f64,
    low_ptr: *const f64,
    len: usize,
    kwargs: &SarKwargs,
) -> Result<Vec<f64>, TA_RetCode> {
    // output: real
    let mut out_begin: TA_Integer = 0;
    let mut out_size: TA_Integer = 0;
    let begin_idx = check_begin_idx2(len, high_ptr, low_ptr) as i32;
    let end_idx = len as i32 - begin_idx - 1;
    let lookback = begin_idx + unsafe { TA_SAR_Lookback(kwargs.acceleration, kwargs.maximum) };
    let (mut out, ptr) = make_vec(len, lookback);
    let ret_code = unsafe {
        TA_SAR(
            0,
            end_idx,
            high_ptr.offset(begin_idx as isize),
            low_ptr.offset(begin_idx as isize),
            kwargs.acceleration,
            kwargs.maximum,
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
pub struct SarExtKwargs {
    #[builder(default = "0.02")]
    pub startvalue: f64,
    #[builder(default = "0.02")]
    pub offsetonreverse: f64,
    #[builder(default = "0.02")]
    pub accelerationinitlong: f64,
    #[builder(default = "0.02")]
    pub accelerationlong: f64,
    #[builder(default = "0.02")]
    pub accelerationmaxlong: f64,
    #[builder(default = "0.02")]
    pub accelerationinitshort: f64,
    #[builder(default = "0.02")]
    pub accelerationshort: f64,
    #[builder(default = "0.02")]
    pub accelerationmaxshort: f64,
}

pub fn ta_sarext(
    high_ptr: *const f64,
    low_ptr: *const f64,
    len: usize,
    kwargs: &SarExtKwargs,
) -> Result<Vec<f64>, TA_RetCode> {
    // output: real
    let mut out_begin: TA_Integer = 0;
    let mut out_size: TA_Integer = 0;
    let begin_idx = check_begin_idx2(len, high_ptr, low_ptr) as i32;
    let end_idx = len as i32 - begin_idx - 1;
    let lookback = begin_idx
        + unsafe {
            TA_SAREXT_Lookback(
                kwargs.startvalue,
                kwargs.offsetonreverse,
                kwargs.accelerationinitlong,
                kwargs.accelerationlong,
                kwargs.accelerationmaxlong,
                kwargs.accelerationinitshort,
                kwargs.accelerationshort,
                kwargs.accelerationmaxshort,
            )
        };
    let (mut out, ptr) = make_vec(len, lookback);
    let ret_code = unsafe {
        TA_SAREXT(
            0,
            end_idx,
            high_ptr.offset(begin_idx as isize),
            low_ptr.offset(begin_idx as isize),
            kwargs.startvalue,
            kwargs.offsetonreverse,
            kwargs.accelerationinitlong,
            kwargs.accelerationlong,
            kwargs.accelerationmaxlong,
            kwargs.accelerationinitshort,
            kwargs.accelerationshort,
            kwargs.accelerationmaxshort,
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

pub fn ta_sma(
    real_ptr: *const f64,
    len: usize,
    kwargs: &TimePeriodKwargs,
) -> Result<Vec<f64>, TA_RetCode> {
    // output: real
    let mut out_begin: TA_Integer = 0;
    let mut out_size: TA_Integer = 0;
    let begin_idx = check_begin_idx1(len, real_ptr) as i32;
    let end_idx = len as i32 - begin_idx - 1;
    let lookback = begin_idx + unsafe { TA_SMA_Lookback(kwargs.timeperiod) };
    let (mut out, ptr) = make_vec(len, lookback);
    let ret_code = unsafe {
        TA_SMA(
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

#[derive(Builder, Deserialize)]
pub struct T3Kwargs {
    #[builder(default = "30")]
    pub timeperiod: i32,
    #[builder(default = "0.7")]
    pub vfactor: f64,
}

pub fn ta_t3(real_ptr: *const f64, len: usize, kwargs: &T3Kwargs) -> Result<Vec<f64>, TA_RetCode> {
    // output: real
    let mut out_begin: TA_Integer = 0;
    let mut out_size: TA_Integer = 0;
    let begin_idx = check_begin_idx1(len, real_ptr) as i32;
    let end_idx = len as i32 - 1 - begin_idx;
    let lookback = begin_idx + unsafe { TA_T3_Lookback(kwargs.timeperiod, kwargs.vfactor) };
    let (mut out, ptr) = make_vec(len, lookback);
    let ret_code = unsafe {
        TA_T3(
            0,
            end_idx,
            real_ptr.offset(begin_idx as isize),
            kwargs.timeperiod,
            kwargs.vfactor,
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
                    out.set_len(len as usize);
                }
            }
            Ok(out)
        }
        _ => Err(ret_code),
    }
}

pub fn ta_tema(
    real_ptr: *const f64,
    len: usize,
    kwargs: &TimePeriodKwargs,
) -> Result<Vec<f64>, TA_RetCode> {
    // output: real
    let mut out_begin: TA_Integer = 0;
    let mut out_size: TA_Integer = 0;
    let begin_idx = check_begin_idx1(len, real_ptr) as i32;
    let end_idx = len as i32 - 1 - begin_idx;
    let lookback = begin_idx + unsafe { TA_TEMA_Lookback(kwargs.timeperiod) };
    let (mut out, ptr) = make_vec(len, lookback);
    let ret_code = unsafe {
        TA_TEMA(
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
                unsafe { out.set_len(out_size_begin) }
            } else {
                unsafe { out.set_len(len) }
            }
            Ok(out)
        }
        _ => Err(ret_code),
    }
}

pub fn ta_trima(
    real_ptr: *const f64,
    len: usize,
    kwargs: &TimePeriodKwargs,
) -> Result<Vec<f64>, TA_RetCode> {
    // output: real
    let mut out_begin: TA_Integer = 0;
    let mut out_size: TA_Integer = 0;
    let begin_idx = check_begin_idx1(len, real_ptr) as i32;
    let end_idx = len as i32 - 1 - begin_idx;
    let lookback = begin_idx + unsafe { TA_TRIMA_Lookback(kwargs.timeperiod) };
    let (mut out, ptr) = make_vec(len, lookback);
    let ret_code = unsafe {
        TA_TRIMA(
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
                unsafe { out.set_len(out_size_begin) }
            } else {
                unsafe { out.set_len(len) }
            }
            Ok(out)
        }
        _ => Err(ret_code),
    }
}

pub fn ta_wma(
    real_ptr: *const f64,
    len: usize,
    kwargs: &TimePeriodKwargs,
) -> Result<Vec<f64>, TA_RetCode> {
    // output: real
    let mut out_begin: TA_Integer = 0;
    let mut out_size: TA_Integer = 0;
    let begin_idx = check_begin_idx1(len, real_ptr) as i32;
    let end_idx = len as i32 - 1 - begin_idx;
    let lookback = begin_idx + unsafe { TA_WMA_Lookback(kwargs.timeperiod) };
    let (mut out, ptr) = make_vec(len, lookback);
    let ret_code = unsafe {
        TA_WMA(
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
                unsafe { out.set_len(out_size_begin) }
            } else {
                unsafe { out.set_len(len) }
            }
            Ok(out)
        }
        _ => Err(ret_code),
    }
}

pub fn ta_accbands(
    high_ptr: *const f64,
    low_ptr: *const f64,
    close_ptr: *const f64,
    len: usize,
    kwargs: &TimePeriodKwargs,
) -> Result<(Vec<f64>, Vec<f64>, Vec<f64>), TA_RetCode> {
    let mut out_begin: TA_Integer = 0;
    let mut out_size: TA_Integer = 0;
    let begin_idx = check_begin_idx3(len, high_ptr, low_ptr, close_ptr) as i32;
    let end_idx = len as i32 - begin_idx - 1;
    let lookback = begin_idx + unsafe { TA_ACCBANDS_Lookback(kwargs.timeperiod) };
    if lookback < 0 {
        return Err(TA_RetCode::TA_BAD_PARAM);
    }
    if cannot_produce_output(len, lookback) {
        return Ok((make_default_vec(len), make_default_vec(len), make_default_vec(len)));
    }
    let (mut outupperband, outupperband_ptr) = make_vec(len, lookback);
    let (mut outmiddleband, outmiddleband_ptr) = make_vec(len, lookback);
    let (mut outlowerband, outlowerband_ptr) = make_vec(len, lookback);
    let ret_code = unsafe {
        TA_ACCBANDS(
            0,
            end_idx,
            high_ptr.offset(begin_idx as isize),
            low_ptr.offset(begin_idx as isize),
            close_ptr.offset(begin_idx as isize),
            kwargs.timeperiod,
            &mut out_begin,
            &mut out_size,
            outupperband_ptr,
            outmiddleband_ptr,
            outlowerband_ptr,
        )
    };
    let out_size_begin = (begin_idx + out_begin + out_size) as usize;
    match ret_code {
        TA_RetCode::TA_SUCCESS => {
            if out_size != 0 {
                unsafe {
                    outupperband.set_len(out_size_begin);
                    outmiddleband.set_len(out_size_begin);
                    outlowerband.set_len(out_size_begin);
                }
            } else {
                unsafe {
                    outupperband.set_len(len);
                    outmiddleband.set_len(len);
                    outlowerband.set_len(len);
                }
            }
            Ok((outupperband, outmiddleband, outlowerband))
        }
        _ => Err(ret_code),
    }
}

pub fn ta_donchian(
    high_ptr: *const f64,
    low_ptr: *const f64,
    len: usize,
    kwargs: &TimePeriodKwargs,
) -> Result<(Vec<f64>, Vec<f64>, Vec<f64>), TA_RetCode> {
    let mut out_begin: TA_Integer = 0;
    let mut out_size: TA_Integer = 0;
    let begin_idx = check_begin_idx2(len, high_ptr, low_ptr) as i32;
    let end_idx = len as i32 - begin_idx - 1;
    let lookback = begin_idx + unsafe { TA_DONCHIAN_Lookback(kwargs.timeperiod) };
    if lookback < 0 {
        return Err(TA_RetCode::TA_BAD_PARAM);
    }
    if cannot_produce_output(len, lookback) {
        return Ok((make_default_vec(len), make_default_vec(len), make_default_vec(len)));
    }
    let (mut outupperband, outupperband_ptr) = make_vec(len, lookback);
    let (mut outmiddleband, outmiddleband_ptr) = make_vec(len, lookback);
    let (mut outlowerband, outlowerband_ptr) = make_vec(len, lookback);
    let ret_code = unsafe {
        TA_DONCHIAN(
            0,
            end_idx,
            high_ptr.offset(begin_idx as isize),
            low_ptr.offset(begin_idx as isize),
            kwargs.timeperiod,
            &mut out_begin,
            &mut out_size,
            outupperband_ptr,
            outmiddleband_ptr,
            outlowerband_ptr,
        )
    };
    let out_size_begin = (begin_idx + out_begin + out_size) as usize;
    match ret_code {
        TA_RetCode::TA_SUCCESS => {
            if out_size != 0 {
                unsafe {
                    outupperband.set_len(out_size_begin);
                    outmiddleband.set_len(out_size_begin);
                    outlowerband.set_len(out_size_begin);
                }
            } else {
                unsafe {
                    outupperband.set_len(len);
                    outmiddleband.set_len(len);
                    outlowerband.set_len(len);
                }
            }
            Ok((outupperband, outmiddleband, outlowerband))
        }
        _ => Err(ret_code),
    }
}

pub fn ta_hma(
    real_ptr: *const f64,
    len: usize,
    kwargs: &TimePeriodKwargs,
) -> Result<Vec<f64>, TA_RetCode> {
    let mut out_begin: TA_Integer = 0;
    let mut out_size: TA_Integer = 0;
    let begin_idx = check_begin_idx1(len, real_ptr) as i32;
    let end_idx = len as i32 - begin_idx - 1;
    let lookback = begin_idx + unsafe { TA_HMA_Lookback(kwargs.timeperiod) };
    if lookback < 0 {
        return Err(TA_RetCode::TA_BAD_PARAM);
    }
    if cannot_produce_output(len, lookback) {
        return Ok(make_default_vec(len));
    }
    let (mut out, ptr) = make_vec(len, lookback);
    let ret_code = unsafe {
        TA_HMA(
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

#[derive(Builder, Deserialize)]
pub struct KcKwargs {
    #[builder(default = "20")]
    pub timeperiod: i32,
    #[builder(default = "10")]
    pub atrperiod: i32,
    #[builder(default = "2.0")]
    pub nbdev: f64,
}

pub fn ta_kc(
    high_ptr: *const f64,
    low_ptr: *const f64,
    close_ptr: *const f64,
    len: usize,
    kwargs: &KcKwargs,
) -> Result<(Vec<f64>, Vec<f64>, Vec<f64>), TA_RetCode> {
    let mut out_begin: TA_Integer = 0;
    let mut out_size: TA_Integer = 0;
    let begin_idx = check_begin_idx3(len, high_ptr, low_ptr, close_ptr) as i32;
    let end_idx = len as i32 - begin_idx - 1;
    let lookback = begin_idx + unsafe { TA_KC_Lookback(kwargs.timeperiod, kwargs.atrperiod, kwargs.nbdev) };
    if lookback < 0 {
        return Err(TA_RetCode::TA_BAD_PARAM);
    }
    if cannot_produce_output(len, lookback) {
        return Ok((make_default_vec(len), make_default_vec(len), make_default_vec(len)));
    }
    let (mut outupperband, outupperband_ptr) = make_vec(len, lookback);
    let (mut outmiddleband, outmiddleband_ptr) = make_vec(len, lookback);
    let (mut outlowerband, outlowerband_ptr) = make_vec(len, lookback);
    let ret_code = unsafe {
        TA_KC(
            0,
            end_idx,
            high_ptr.offset(begin_idx as isize),
            low_ptr.offset(begin_idx as isize),
            close_ptr.offset(begin_idx as isize),
            kwargs.timeperiod,
            kwargs.atrperiod,
            kwargs.nbdev,
            &mut out_begin,
            &mut out_size,
            outupperband_ptr,
            outmiddleband_ptr,
            outlowerband_ptr,
        )
    };
    let out_size_begin = (begin_idx + out_begin + out_size) as usize;
    match ret_code {
        TA_RetCode::TA_SUCCESS => {
            if out_size != 0 {
                unsafe {
                    outupperband.set_len(out_size_begin);
                    outmiddleband.set_len(out_size_begin);
                    outlowerband.set_len(out_size_begin);
                }
            } else {
                unsafe {
                    outupperband.set_len(len);
                    outmiddleband.set_len(len);
                    outlowerband.set_len(len);
                }
            }
            Ok((outupperband, outmiddleband, outlowerband))
        }
        _ => Err(ret_code),
    }
}

pub fn ta_rma(
    real_ptr: *const f64,
    len: usize,
    kwargs: &TimePeriodKwargs,
) -> Result<Vec<f64>, TA_RetCode> {
    let mut out_begin: TA_Integer = 0;
    let mut out_size: TA_Integer = 0;
    let begin_idx = check_begin_idx1(len, real_ptr) as i32;
    let end_idx = len as i32 - begin_idx - 1;
    let lookback = begin_idx + unsafe { TA_RMA_Lookback(kwargs.timeperiod) };
    if lookback < 0 {
        return Err(TA_RetCode::TA_BAD_PARAM);
    }
    if cannot_produce_output(len, lookback) {
        return Ok(make_default_vec(len));
    }
    let (mut out, ptr) = make_vec(len, lookback);
    let ret_code = unsafe {
        TA_RMA(
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

#[derive(Builder, Deserialize)]
pub struct SupertrendKwargs {
    #[builder(default = "10")]
    pub timeperiod: i32,
    #[builder(default = "3.0")]
    pub multiplier: f64,
}

pub fn ta_supertrend(
    high_ptr: *const f64,
    low_ptr: *const f64,
    close_ptr: *const f64,
    len: usize,
    kwargs: &SupertrendKwargs,
) -> Result<(Vec<f64>, Vec<i32>), TA_RetCode> {
    let mut out_begin: TA_Integer = 0;
    let mut out_size: TA_Integer = 0;
    let begin_idx = check_begin_idx3(len, high_ptr, low_ptr, close_ptr) as i32;
    let end_idx = len as i32 - begin_idx - 1;
    let lookback = begin_idx + unsafe { TA_SUPERTREND_Lookback(kwargs.timeperiod, kwargs.multiplier) };
    if lookback < 0 {
        return Err(TA_RetCode::TA_BAD_PARAM);
    }
    if cannot_produce_output(len, lookback) {
        return Ok((make_default_vec(len), make_default_vec(len)));
    }
    let (mut outsupertrend, outsupertrend_ptr) = make_vec(len, lookback);
    let (mut outtrend, outtrend_ptr) = make_vec(len, lookback);
    let ret_code = unsafe {
        TA_SUPERTREND(
            0,
            end_idx,
            high_ptr.offset(begin_idx as isize),
            low_ptr.offset(begin_idx as isize),
            close_ptr.offset(begin_idx as isize),
            kwargs.timeperiod,
            kwargs.multiplier,
            &mut out_begin,
            &mut out_size,
            outsupertrend_ptr,
            outtrend_ptr,
        )
    };
    let out_size_begin = (begin_idx + out_begin + out_size) as usize;
    match ret_code {
        TA_RetCode::TA_SUCCESS => {
            if out_size != 0 {
                unsafe {
                    outsupertrend.set_len(out_size_begin);
                    outtrend.set_len(out_size_begin);
                }
            } else {
                unsafe {
                    outsupertrend.set_len(len);
                    outtrend.set_len(len);
                }
            }
            Ok((outsupertrend, outtrend))
        }
        _ => Err(ret_code),
    }
}

pub fn ta_vwma(
    real_ptr: *const f64,
    volume_ptr: *const f64,
    len: usize,
    kwargs: &TimePeriodKwargs,
) -> Result<Vec<f64>, TA_RetCode> {
    let mut out_begin: TA_Integer = 0;
    let mut out_size: TA_Integer = 0;
    let begin_idx = check_begin_idx2(len, real_ptr, volume_ptr) as i32;
    let end_idx = len as i32 - begin_idx - 1;
    let lookback = begin_idx + unsafe { TA_VWMA_Lookback(kwargs.timeperiod) };
    if lookback < 0 {
        return Err(TA_RetCode::TA_BAD_PARAM);
    }
    if cannot_produce_output(len, lookback) {
        return Ok(make_default_vec(len));
    }
    let (mut out, ptr) = make_vec(len, lookback);
    let ret_code = unsafe {
        TA_VWMA(
            0,
            end_idx,
            real_ptr.offset(begin_idx as isize),
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

pub fn ta_zlema(
    real_ptr: *const f64,
    len: usize,
    kwargs: &TimePeriodKwargs,
) -> Result<Vec<f64>, TA_RetCode> {
    let mut out_begin: TA_Integer = 0;
    let mut out_size: TA_Integer = 0;
    let begin_idx = check_begin_idx1(len, real_ptr) as i32;
    let end_idx = len as i32 - begin_idx - 1;
    let lookback = begin_idx + unsafe { TA_ZLEMA_Lookback(kwargs.timeperiod) };
    if lookback < 0 {
        return Err(TA_RetCode::TA_BAD_PARAM);
    }
    if cannot_produce_output(len, lookback) {
        return Ok(make_default_vec(len));
    }
    let (mut out, ptr) = make_vec(len, lookback);
    let ret_code = unsafe {
        TA_ZLEMA(
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
