use crate::utils::make_vec;
use serde::Deserialize;
use talib_sys::{
    TA_BETA_Lookback, TA_CORREL_Lookback, TA_Integer, TA_LINEARREG_ANGLE_Lookback,
    TA_LINEARREG_INTERCEPT_Lookback, TA_LINEARREG_Lookback, TA_LINEARREG_SLOPE_Lookback,
    TA_RetCode, TA_STDDEV_Lookback, TA_TSF_Lookback, TA_VAR_Lookback, TA_BETA, TA_CORREL,
    TA_LINEARREG, TA_LINEARREG_ANGLE, TA_LINEARREG_INTERCEPT, TA_LINEARREG_SLOPE, TA_STDDEV,
    TA_TSF, TA_VAR,
};

#[derive(Deserialize)]
pub struct BetaKwargs {
    timeperiod: i32,
}

pub fn ta_beta(
    real0_ptr: *const f64,
    real1_ptr: *const f64,
    len: usize,
    kwargs: &BetaKwargs,
) -> Result<Vec<f64>, TA_RetCode> {
    let mut out_begin: TA_Integer = 0;
    let mut out_size: TA_Integer = 0;
    let lookback = unsafe { TA_BETA_Lookback(kwargs.timeperiod) };
    let (mut out, ptr) = make_vec(len, lookback);
    let ret_code = unsafe {
        TA_BETA(
            0,
            len as i32 - 1,
            real0_ptr,
            real1_ptr,
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
pub struct CorrelKwargs {
    timeperiod: i32,
}

pub fn ta_correl(
    real0_ptr: *const f64,
    real1_ptr: *const f64,
    len: usize,
    kwargs: &CorrelKwargs,
) -> Result<Vec<f64>, TA_RetCode> {
    let mut out_begin: TA_Integer = 0;
    let mut out_size: TA_Integer = 0;
    let lookback = unsafe { TA_CORREL_Lookback(kwargs.timeperiod) };
    let (mut out, ptr) = make_vec(len, lookback);
    let ret_code = unsafe {
        TA_CORREL(
            0,
            len as i32 - 1,
            real0_ptr,
            real1_ptr,
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
pub struct LinearRegKwargs {
    timeperiod: i32,
}

pub fn ta_linearreg(
    real_ptr: *const f64,
    len: usize,
    kwargs: &LinearRegKwargs,
) -> Result<Vec<f64>, TA_RetCode> {
    let mut out_begin: TA_Integer = 0;
    let mut out_size: TA_Integer = 0;
    let lookback = unsafe { TA_LINEARREG_Lookback(kwargs.timeperiod) };
    let (mut out, ptr) = make_vec(len, lookback);
    let ret_code = unsafe {
        TA_LINEARREG(
            0,
            len as i32 - 1,
            real_ptr,
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
pub struct LinearRegAngleKwargs {
    timeperiod: i32,
}

pub fn ta_linearreg_angle(
    real_ptr: *const f64,
    len: usize,
    kwargs: &LinearRegAngleKwargs,
) -> Result<Vec<f64>, TA_RetCode> {
    let mut out_begin: TA_Integer = 0;
    let mut out_size: TA_Integer = 0;
    let lookback =
        unsafe { TA_LINEARREG_ANGLE_Lookback(kwargs.timeperiod) };
    let (mut out, ptr) = make_vec(len, lookback);
    let ret_code = unsafe {
        TA_LINEARREG_ANGLE(
            0,
            len as i32 - 1,
            real_ptr,
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
pub struct LinearRegInterceptKwargs {
    timeperiod: i32,
}

pub fn ta_linearreg_intercept(
    real_ptr: *const f64,
    len: usize,
    kwargs: &LinearRegInterceptKwargs,
) -> Result<Vec<f64>, TA_RetCode> {
    let mut out_begin: TA_Integer = 0;
    let mut out_size: TA_Integer = 0;
    let lookback =
        unsafe { TA_LINEARREG_INTERCEPT_Lookback(kwargs.timeperiod) };
    let (mut out, ptr) = make_vec(len, lookback);
    let ret_code = unsafe {
        TA_LINEARREG_INTERCEPT(
            0,
            len as i32 - 1,
            real_ptr,
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
pub struct LinearRegSlopeKwargs {
    timeperiod: i32,
}

pub fn ta_linearreg_slope(
    real_ptr: *const f64,
    len: usize,
    kwargs: &LinearRegSlopeKwargs,
) -> Result<Vec<f64>, TA_RetCode> {
    let mut out_begin: TA_Integer = 0;
    let mut out_size: TA_Integer = 0;
    let lookback =
        unsafe { TA_LINEARREG_SLOPE_Lookback(kwargs.timeperiod) };
    let (mut out, ptr) = make_vec(len, lookback);
    let ret_code = unsafe {
        TA_LINEARREG_SLOPE(
            0,
            len as i32 - 1,
            real_ptr,
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
pub struct StdDevKwargs {
    timeperiod: i32,
    nbdev: f64,
}

pub fn ta_stddev(
    real_ptr: *const f64,
    len: usize,
    kwargs: &StdDevKwargs,
) -> Result<Vec<f64>, TA_RetCode> {
    let mut out_begin: TA_Integer = 0;
    let mut out_size: TA_Integer = 0;

    let lookback = unsafe { TA_STDDEV_Lookback(kwargs.timeperiod, kwargs.nbdev) };
    let (mut out, ptr) = make_vec(len, lookback);
    let ret_code = unsafe {
        TA_STDDEV(
            0,
            len as i32 - 1,
            real_ptr,
            kwargs.timeperiod,
            kwargs.nbdev,
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
                out = vec![0.0; len];
            }
            Ok(out)
        }
        _ => Err(ret_code),
    }
}

#[derive(Deserialize)]
pub struct TsfKwargs {
    timeperiod: i32,
}

pub fn ta_tsf(
    real_ptr: *const f64,
    len: usize,
    kwargs: &TsfKwargs,
) -> Result<Vec<f64>, TA_RetCode> {
    let mut out_begin: TA_Integer = 0;
    let mut out_size: TA_Integer = 0;

    let lookback = unsafe { TA_TSF_Lookback(kwargs.timeperiod) };
    let (mut out, ptr) = make_vec(len, lookback);
    let ret_code = unsafe {
        TA_TSF(
            0,
            len as i32 - 1,
            real_ptr,
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
                out = vec![0.0; len];
            }
            Ok(out)
        }
        _ => Err(ret_code),
    }
}

#[derive(Deserialize)]
pub struct VarKwargs {
    timeperiod: i32,
    nbdev: f64,
}

pub fn ta_var(
    real_ptr: *const f64,
    len: usize,
    kwargs: &VarKwargs,
) -> Result<Vec<f64>, TA_RetCode> {
    let mut out_begin: TA_Integer = 0;
    let mut out_size: TA_Integer = 0;

    let lookback = unsafe { TA_VAR_Lookback(kwargs.timeperiod, kwargs.nbdev) };
    let (mut out, ptr) = make_vec(len, lookback);
    let ret_code = unsafe {
        TA_VAR(
            0,
            len as i32 - 1,
            real_ptr,
            kwargs.timeperiod,
            kwargs.nbdev,
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
                out = vec![0.0; len];
            }
            Ok(out)
        }
        _ => Err(ret_code),
    }
}