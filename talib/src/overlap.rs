use crate::common::TimePeriodKwargs;
use crate::utils::{check_begin_idx1, check_begin_idx2, make_vec};
use serde::Deserialize;
use talib_sys::{
    TA_BBANDS_Lookback, TA_DEMA_Lookback, TA_EMA_Lookback, TA_HT_TRENDLINE_Lookback, TA_Integer,
    TA_KAMA_Lookback, TA_MAMA_Lookback, TA_MAType, TA_MAVP_Lookback, TA_MA_Lookback,
    TA_MIDPOINT_Lookback, TA_MIDPRICE_Lookback, TA_RetCode, TA_SAREXT_Lookback, TA_SAR_Lookback,
    TA_SMA_Lookback, TA_T3_Lookback, TA_TEMA_Lookback, TA_TRIMA_Lookback, TA_WMA_Lookback,
    TA_BBANDS, TA_DEMA, TA_EMA, TA_HT_TRENDLINE, TA_KAMA, TA_MA, TA_MAMA, TA_MAVP, TA_MIDPOINT,
    TA_MIDPRICE, TA_SAR, TA_SAREXT, TA_SMA, TA_T3, TA_TEMA, TA_TRIMA, TA_WMA,
};

#[derive(Deserialize)]
pub struct BBANDSKwargs {
    timeperiod: i32,
    nbdevup: f64,
    nbdevdn: f64,
    matype: TA_MAType,
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

#[derive(Deserialize)]
pub struct MaKwargs {
    timeperiod: i32,
    matype: TA_MAType,
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

#[derive(Deserialize)]
pub struct MamaKwargs {
    fastlimit: f64,
    slowlimit: f64,
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

#[derive(Deserialize)]
pub struct MavpKwargs {
    minperiod: i32,
    maxperiod: i32,
    matype: TA_MAType,
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

#[derive(Deserialize)]
pub struct SarKwargs {
    acceleration: f64,
    maximum: f64,
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

#[derive(Deserialize)]
pub struct SarExtKwargs {
    startvalue: f64,
    offsetonreverse: f64,
    accelerationinitlong: f64,
    accelerationlong: f64,
    accelerationmaxlong: f64,
    accelerationinitshort: f64,
    accelerationshort: f64,
    accelerationmaxshort: f64,
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

#[derive(Deserialize)]
pub struct T3Kwargs {
    timeperiod: i32,
    vfactor: f64,
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
