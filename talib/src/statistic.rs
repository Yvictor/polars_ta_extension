use crate::utils::{make_vec, check_begin_idx2, check_begin_idx1};
use serde::Deserialize;
use talib_sys::{
    TA_BETA_Lookback, TA_CORREL_Lookback, TA_Integer, TA_LINEARREG_ANGLE_Lookback,
    TA_LINEARREG_INTERCEPT_Lookback, TA_LINEARREG_Lookback, TA_LINEARREG_SLOPE_Lookback,
    TA_RetCode, TA_STDDEV_Lookback, TA_TSF_Lookback, TA_VAR_Lookback, TA_BETA, TA_CORREL,
    TA_LINEARREG, TA_LINEARREG_ANGLE, TA_LINEARREG_INTERCEPT, TA_LINEARREG_SLOPE, TA_STDDEV,
    TA_TSF, TA_VAR,
};
use derive_builder::Builder;
use crate::utils::cannot_produce_output;
use crate::utils::make_default_vec;
use crate::common::TimePeriodKwargs;
use talib_sys::{TA_PERCENTILE_Lookback, TA_PERCENTILE};
use talib_sys::{TA_PERCENTRANK_Lookback, TA_PERCENTRANK};

#[derive(Builder, Deserialize)]
pub struct BetaKwargs {
    #[builder(default = "5")]
    pub timeperiod: i32,
}

pub fn ta_beta(
    real0_ptr: *const f64,
    real1_ptr: *const f64,
    len: usize,
    kwargs: &BetaKwargs,
) -> Result<Vec<f64>, TA_RetCode> {
    let mut out_begin: TA_Integer = 0;
    let mut out_size: TA_Integer = 0;
    let begin_idx = check_begin_idx2(len, real0_ptr, real1_ptr) as i32;
    let end_idx = len as i32 - begin_idx - 1;
    let lookback = begin_idx + unsafe { TA_BETA_Lookback(kwargs.timeperiod) };
    let (mut out, ptr) = make_vec(len, lookback);
    let ret_code = unsafe {
        TA_BETA(
            0,
            end_idx,
            real0_ptr.offset(begin_idx as isize),
            real1_ptr.offset(begin_idx as isize),
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
pub struct CorrelKwargs {
    #[builder(default = "30")]
    pub timeperiod: i32,
}

pub fn ta_correl(
    real0_ptr: *const f64,
    real1_ptr: *const f64,
    len: usize,
    kwargs: &CorrelKwargs,
) -> Result<Vec<f64>, TA_RetCode> {
    let mut out_begin: TA_Integer = 0;
    let mut out_size: TA_Integer = 0;
    let begin_idx = check_begin_idx2(len, real0_ptr, real1_ptr) as i32;
    let end_idx = len as i32 - begin_idx - 1;
    let lookback = begin_idx + unsafe { TA_CORREL_Lookback(kwargs.timeperiod) };
    let (mut out, ptr) = make_vec(len, lookback);
    let ret_code = unsafe {
        TA_CORREL(
            0,
            end_idx,
            real0_ptr.offset(begin_idx as isize),
            real1_ptr.offset(begin_idx as isize),
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
pub struct LinearRegKwargs {
    #[builder(default = "14")]
    pub timeperiod: i32,
}

pub fn ta_linearreg(
    real_ptr: *const f64,
    len: usize,
    kwargs: &LinearRegKwargs,
) -> Result<Vec<f64>, TA_RetCode> {
    let mut out_begin: TA_Integer = 0;
    let mut out_size: TA_Integer = 0;
    let begin_idx = check_begin_idx1(len, real_ptr) as i32;
    let end_idx = len as i32 - begin_idx - 1;
    let lookback = begin_idx + unsafe { TA_LINEARREG_Lookback(kwargs.timeperiod) };
    let (mut out, ptr) = make_vec(len, lookback);
    let ret_code = unsafe {
        TA_LINEARREG(
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
pub struct LinearRegAngleKwargs {
    #[builder(default = "14")]
    pub timeperiod: i32,
}

pub fn ta_linearreg_angle(
    real_ptr: *const f64,
    len: usize,
    kwargs: &LinearRegAngleKwargs,
) -> Result<Vec<f64>, TA_RetCode> {
    let mut out_begin: TA_Integer = 0;
    let mut out_size: TA_Integer = 0;
    let begin_idx = check_begin_idx1(len, real_ptr) as i32;
    let end_idx = len as i32 - begin_idx - 1;
    let lookback = begin_idx + unsafe{ TA_LINEARREG_ANGLE_Lookback(kwargs.timeperiod) };
    let (mut out, ptr) = make_vec(len, lookback);
    let ret_code = unsafe {
        TA_LINEARREG_ANGLE(
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
pub struct LinearRegInterceptKwargs {
    #[builder(default = "14")]
    pub timeperiod: i32,
}

pub fn ta_linearreg_intercept(
    real_ptr: *const f64,
    len: usize,
    kwargs: &LinearRegInterceptKwargs,
) -> Result<Vec<f64>, TA_RetCode> {
    let mut out_begin: TA_Integer = 0;
    let mut out_size: TA_Integer = 0;
    let begin_idx = check_begin_idx1(len, real_ptr) as i32;
    let end_idx = len as i32 - begin_idx - 1;
    let lookback = begin_idx + unsafe{ TA_LINEARREG_INTERCEPT_Lookback(kwargs.timeperiod) };
    let (mut out, ptr) = make_vec(len, lookback);
    let ret_code = unsafe {
        TA_LINEARREG_INTERCEPT(
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
pub struct LinearRegSlopeKwargs {
    #[builder(default = "14")]
    pub timeperiod: i32,
}

pub fn ta_linearreg_slope(
    real_ptr: *const f64,
    len: usize,
    kwargs: &LinearRegSlopeKwargs,
) -> Result<Vec<f64>, TA_RetCode> {
    let mut out_begin: TA_Integer = 0;
    let mut out_size: TA_Integer = 0;
    let begin_idx = check_begin_idx1(len, real_ptr) as i32;
    let end_idx = len as i32 - begin_idx - 1;
    let lookback = begin_idx + unsafe { TA_LINEARREG_SLOPE_Lookback(kwargs.timeperiod) };
    let (mut out, ptr) = make_vec(len, lookback);
    let ret_code = unsafe {
        TA_LINEARREG_SLOPE(
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
pub struct StdDevKwargs {
    #[builder(default = "5")]
    pub timeperiod: i32,
    #[builder(default = "1.0")]
    pub nbdev: f64,
}

pub fn ta_stddev(
    real_ptr: *const f64,
    len: usize,
    kwargs: &StdDevKwargs,
) -> Result<Vec<f64>, TA_RetCode> {
    let mut out_begin: TA_Integer = 0;
    let mut out_size: TA_Integer = 0;
    let begin_idx = check_begin_idx1(len, real_ptr) as i32;
    let end_idx = len as i32 - begin_idx - 1;
    let lookback = begin_idx + unsafe { TA_STDDEV_Lookback(kwargs.timeperiod, kwargs.nbdev) };
    let (mut out, ptr) = make_vec(len, lookback);
    let ret_code = unsafe {
        TA_STDDEV(
            0,
            end_idx,
            real_ptr.offset(begin_idx as isize),
            kwargs.timeperiod,
            kwargs.nbdev,
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
                out = vec![0.0; len];
            }
            Ok(out)
        }
        _ => Err(ret_code),
    }
}

#[derive(Builder, Deserialize)]
pub struct TsfKwargs {
    #[builder(default = "14")]
    pub timeperiod: i32,
}

pub fn ta_tsf(
    real_ptr: *const f64,
    len: usize,
    kwargs: &TsfKwargs,
) -> Result<Vec<f64>, TA_RetCode> {
    let mut out_begin: TA_Integer = 0;
    let mut out_size: TA_Integer = 0;
    let begin_idx = check_begin_idx1(len, real_ptr) as i32;
    let end_idx = len as i32 - begin_idx - 1;
    let lookback = begin_idx + unsafe { TA_TSF_Lookback(kwargs.timeperiod) };
    let (mut out, ptr) = make_vec(len, lookback);
    let ret_code = unsafe {
        TA_TSF(
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
                out = vec![0.0; len];
            }
            Ok(out)
        }
        _ => Err(ret_code),
    }
}

#[derive(Builder, Deserialize)]
pub struct VarKwargs {
    #[builder(default = "5")]
    pub timeperiod: i32,
    #[builder(default = "1.0")]
    pub nbdev: f64,
}

pub fn ta_var(
    real_ptr: *const f64,
    len: usize,
    kwargs: &VarKwargs,
) -> Result<Vec<f64>, TA_RetCode> {
    let mut out_begin: TA_Integer = 0;
    let mut out_size: TA_Integer = 0;
    let begin_idx = check_begin_idx1(len, real_ptr) as i32;
    let end_idx = len as i32 - begin_idx - 1;
    let lookback = begin_idx + unsafe { TA_VAR_Lookback(kwargs.timeperiod, kwargs.nbdev) };
    let (mut out, ptr) = make_vec(len, lookback);
    let ret_code = unsafe {
        TA_VAR(
            0,
            end_idx,
            real_ptr.offset(begin_idx as isize),
            kwargs.timeperiod,
            kwargs.nbdev,
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
                out = vec![0.0; len];
            }
            Ok(out)
        }
        _ => Err(ret_code),
    }
}

#[derive(Builder, Deserialize)]
pub struct PercentileKwargs {
    #[builder(default = "30")]
    pub timeperiod: i32,
    #[builder(default = "50.0")]
    pub percentile: f64,
}

pub fn ta_percentile(
    real_ptr: *const f64,
    len: usize,
    kwargs: &PercentileKwargs,
) -> Result<Vec<f64>, TA_RetCode> {
    let mut out_begin: TA_Integer = 0;
    let mut out_size: TA_Integer = 0;
    let begin_idx = check_begin_idx1(len, real_ptr) as i32;
    let end_idx = len as i32 - begin_idx - 1;
    let lookback = begin_idx + unsafe { TA_PERCENTILE_Lookback(kwargs.timeperiod, kwargs.percentile) };
    if lookback < 0 {
        return Err(TA_RetCode::TA_BAD_PARAM);
    }
    if cannot_produce_output(len, lookback) {
        return Ok(make_default_vec(len));
    }
    let (mut out, ptr) = make_vec(len, lookback);
    let ret_code = unsafe {
        TA_PERCENTILE(
            0,
            end_idx,
            real_ptr.offset(begin_idx as isize),
            kwargs.timeperiod,
            kwargs.percentile,
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

pub fn ta_percentrank(
    real_ptr: *const f64,
    len: usize,
    kwargs: &TimePeriodKwargs,
) -> Result<Vec<f64>, TA_RetCode> {
    let mut out_begin: TA_Integer = 0;
    let mut out_size: TA_Integer = 0;
    let begin_idx = check_begin_idx1(len, real_ptr) as i32;
    let end_idx = len as i32 - begin_idx - 1;
    let lookback = begin_idx + unsafe { TA_PERCENTRANK_Lookback(kwargs.timeperiod) };
    if lookback < 0 {
        return Err(TA_RetCode::TA_BAD_PARAM);
    }
    if cannot_produce_output(len, lookback) {
        return Ok(make_default_vec(len));
    }
    let (mut out, ptr) = make_vec(len, lookback);
    let ret_code = unsafe {
        TA_PERCENTRANK(
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
