use crate::utils::{check_begin_idx2, check_begin_idx1};
use crate::{common::TimePeriodKwargs, utils::make_vec};

use talib_sys::{TA_ACOS_Lookback, TA_ACOS};
use talib_sys::{TA_ADD_Lookback, TA_Integer, TA_RetCode, TA_ADD};
use talib_sys::{TA_ASIN_Lookback, TA_ASIN};
use talib_sys::{TA_ATAN_Lookback, TA_ATAN};
use talib_sys::{TA_CEIL_Lookback, TA_CEIL};
use talib_sys::{TA_COSH_Lookback, TA_COSH};
use talib_sys::{TA_COS_Lookback, TA_COS};
use talib_sys::{TA_DIV_Lookback, TA_DIV};
use talib_sys::{TA_EXP_Lookback, TA_EXP};
use talib_sys::{TA_FLOOR_Lookback, TA_FLOOR};
use talib_sys::{TA_LN_Lookback, TA_LN};
use talib_sys::{TA_LOG10_Lookback, TA_LOG10};
use talib_sys::{TA_MAXINDEX_Lookback, TA_MAXINDEX};
use talib_sys::{TA_MAX_Lookback, TA_MAX};
use talib_sys::{TA_MININDEX_Lookback, TA_MININDEX};
use talib_sys::{TA_MINMAXINDEX_Lookback, TA_MINMAXINDEX};
use talib_sys::{TA_MINMAX_Lookback, TA_MINMAX};
use talib_sys::{TA_MIN_Lookback, TA_MIN};
use talib_sys::{TA_MULT_Lookback, TA_MULT};
use talib_sys::{TA_SINH_Lookback, TA_SINH};
use talib_sys::{TA_SIN_Lookback, TA_SIN};
use talib_sys::{TA_SQRT_Lookback, TA_SQRT};
use talib_sys::{TA_SUB_Lookback, TA_SUB};
use talib_sys::{TA_SUM_Lookback, TA_SUM};
use talib_sys::{TA_TANH_Lookback, TA_TANH};
use talib_sys::{TA_TAN_Lookback, TA_TAN};

pub fn ta_add(
    real0_ptr: *const f64,
    real1_ptr: *const f64,
    len: usize,
) -> Result<Vec<f64>, TA_RetCode> {
    let mut out_begin: TA_Integer = 0;
    let mut out_size: TA_Integer = 0;
    let begin_idx = check_begin_idx2(len, real0_ptr, real1_ptr) as i32;
    let end_idx = len as i32 - begin_idx - 1;
    let lookback = begin_idx + unsafe { TA_ADD_Lookback() };
    let (mut out, ptr) = make_vec(len, lookback);
    let ret_code = unsafe {
        TA_ADD(
            0,
            end_idx,
            real0_ptr.offset(begin_idx as isize),
            real1_ptr.offset(begin_idx as isize),
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

pub fn ta_div(
    real0_ptr: *const f64,
    real1_ptr: *const f64,
    len: usize,
) -> Result<Vec<f64>, TA_RetCode> {
    let mut out_begin: TA_Integer = 0;
    let mut out_size: TA_Integer = 0;
    let begin_idx = check_begin_idx2(len, real0_ptr, real1_ptr) as i32;
    let end_idx = len as i32 - begin_idx - 1;
    let lookback = begin_idx + unsafe { TA_DIV_Lookback() };
    let (mut out, ptr) = make_vec(len, lookback);
    let ret_code = unsafe {
        TA_DIV(
            0,
            end_idx,
            real0_ptr.offset(begin_idx as isize),
            real1_ptr.offset(begin_idx as isize),
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

pub fn ta_max(
    real_ptr: *const f64,
    len: usize,
    kwargs: &TimePeriodKwargs,
) -> Result<Vec<f64>, TA_RetCode> {
    let mut out_begin: TA_Integer = 0;
    let mut out_size: TA_Integer = 0;
    let begin_idx = check_begin_idx1(len, real_ptr) as i32;
    let end_idx = len as i32 - begin_idx - 1;
    let lookback = begin_idx + unsafe { TA_MAX_Lookback(kwargs.timeperiod) };
    let (mut out, ptr) = make_vec(len, lookback);
    let ret_code = unsafe {
        TA_MAX(
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

pub fn ta_maxindex(
    real_ptr: *const f64,
    len: usize,
    kwargs: &TimePeriodKwargs,
) -> Result<Vec<i32>, TA_RetCode> {
    let mut out_begin: TA_Integer = 0;
    let mut out_size: TA_Integer = 0;
    let begin_idx = check_begin_idx1(len, real_ptr) as i32;
    let end_idx = len as i32 - begin_idx - 1;
    let lookback = begin_idx + unsafe { TA_MAXINDEX_Lookback(kwargs.timeperiod) };
    let (mut out, ptr) = make_vec(len, lookback);
    let ret_code = unsafe {
        TA_MAXINDEX(
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

pub fn ta_min(
    real_ptr: *const f64,
    len: usize,
    kwargs: &TimePeriodKwargs,
) -> Result<Vec<f64>, TA_RetCode> {
    let mut out_begin: TA_Integer = 0;
    let mut out_size: TA_Integer = 0;
    let begin_idx = check_begin_idx1(len, real_ptr) as i32;
    let end_idx = len as i32 - begin_idx - 1;
    let lookback = begin_idx + unsafe { TA_MIN_Lookback(kwargs.timeperiod) };
    let (mut out, ptr) = make_vec(len, lookback);
    let ret_code = unsafe {
        TA_MIN(
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

pub fn ta_minindex(
    real_ptr: *const f64,
    len: usize,
    kwargs: &TimePeriodKwargs,
) -> Result<Vec<i32>, TA_RetCode> {
    let mut out_begin: TA_Integer = 0;
    let mut out_size: TA_Integer = 0;
    let begin_idx = check_begin_idx1(len, real_ptr) as i32;
    let end_idx = len as i32 - begin_idx - 1;
    let lookback = begin_idx + unsafe { TA_MININDEX_Lookback(kwargs.timeperiod) };
    let (mut out, ptr) = make_vec(len, lookback);
    let ret_code = unsafe {
        TA_MININDEX(
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

pub fn ta_minmax(
    real_ptr: *const f64,
    len: usize,
    kwargs: &TimePeriodKwargs,
) -> Result<(Vec<f64>, Vec<f64>), TA_RetCode> {
    let mut out_begin: TA_Integer = 0;
    let mut out_size: TA_Integer = 0;
    let begin_idx = check_begin_idx1(len, real_ptr) as i32;
    let end_idx = len as i32 - begin_idx - 1;
    let lookback = begin_idx + unsafe { TA_MINMAX_Lookback(kwargs.timeperiod) };
    let (mut out_min, ptr_min) = make_vec(len, lookback);
    let (mut out_max, ptr_max) = make_vec(len, lookback);
    let ret_code = unsafe {
        TA_MINMAX(
            0,
            end_idx,
            real_ptr.offset(begin_idx as isize),
            kwargs.timeperiod,
            &mut out_begin,
            &mut out_size,
            ptr_min,
            ptr_max,
        )
    };
    let out_size_begin = (begin_idx + out_begin + out_size) as usize;
    match ret_code {
        TA_RetCode::TA_SUCCESS => {
            if out_size != 0 {
                unsafe {
                    out_min.set_len(out_size_begin);
                }
                unsafe {
                    out_max.set_len(out_size_begin);
                }
            } else {
                unsafe {
                    out_min.set_len(len);
                }
                unsafe {
                    out_max.set_len(len);
                }
            }
            Ok((out_min, out_max))
        }
        _ => Err(ret_code),
    }
}

pub fn ta_minmaxindex(
    real_ptr: *const f64,
    len: usize,
    kwargs: &TimePeriodKwargs,
) -> Result<(Vec<i32>, Vec<i32>), TA_RetCode> {
    let mut out_begin: TA_Integer = 0;
    let mut out_size: TA_Integer = 0;
    let begin_idx = check_begin_idx1(len, real_ptr) as i32;
    let end_idx = len as i32 - begin_idx - 1;
    let lookback = begin_idx + unsafe { TA_MINMAXINDEX_Lookback(kwargs.timeperiod) };
    let (mut out_min, ptr_min) = make_vec(len, lookback);
    let (mut out_max, ptr_max) = make_vec(len, lookback);
    let ret_code = unsafe {
        TA_MINMAXINDEX(
            0,
            end_idx,
            real_ptr.offset(begin_idx as isize),
            kwargs.timeperiod,
            &mut out_begin,
            &mut out_size,
            ptr_min,
            ptr_max,
        )
    };
    let out_size_begin = (begin_idx + out_begin + out_size) as usize;
    match ret_code {
        TA_RetCode::TA_SUCCESS => {
            if out_size != 0 {
                unsafe {
                    out_min.set_len(out_size_begin);
                }
                unsafe {
                    out_max.set_len(out_size_begin);
                }
            } else {
                unsafe {
                    out_min.set_len(len);
                }
                unsafe {
                    out_max.set_len(len);
                }
            }
            Ok((out_min, out_max))
        }
        _ => Err(ret_code),
    }
}

pub fn ta_mult(
    real0_ptr: *const f64,
    real1_ptr: *const f64,
    len: usize,
) -> Result<Vec<f64>, TA_RetCode> {
    let mut out_begin: TA_Integer = 0;
    let mut out_size: TA_Integer = 0;
    let begin_idx = check_begin_idx2(len, real0_ptr, real1_ptr) as i32;
    let end_idx = len as i32 - begin_idx - 1;
    let lookback = begin_idx + unsafe { TA_MULT_Lookback() };
    let (mut out, ptr) = make_vec(len, lookback);
    let ret_code = unsafe {
        TA_MULT(
            0,
            end_idx,
            real0_ptr.offset(begin_idx as isize),
            real1_ptr.offset(begin_idx as isize),
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

pub fn ta_sub(
    real0_ptr: *const f64,
    real1_ptr: *const f64,
    len: usize,
) -> Result<Vec<f64>, TA_RetCode> {
    let mut out_begin: TA_Integer = 0;
    let mut out_size: TA_Integer = 0;
    let begin_idx = check_begin_idx2(len, real0_ptr, real1_ptr) as i32;
    let end_idx = len as i32 - begin_idx - 1;
    let lookback = begin_idx + unsafe { TA_SUB_Lookback() };
    let (mut out, ptr) = make_vec(len, lookback);
    let ret_code = unsafe {
        TA_SUB(
            0,
            end_idx,
            real0_ptr.offset(begin_idx as isize),
            real1_ptr.offset(begin_idx as isize),
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

pub fn ta_sum(
    real_ptr: *const f64,
    len: usize,
    kwargs: &TimePeriodKwargs,
) -> Result<Vec<f64>, TA_RetCode> {
    let mut out_begin: TA_Integer = 0;
    let mut out_size: TA_Integer = 0;
    let begin_idx = check_begin_idx1(len, real_ptr) as i32;
    let end_idx = len as i32 - begin_idx - 1;
    let lookback = begin_idx + unsafe { TA_SUM_Lookback(kwargs.timeperiod) };
    let (mut out, ptr) = make_vec(len, lookback);
    let ret_code = unsafe {
        TA_SUM(
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

pub fn ta_acos(real_ptr: *const f64, len: usize) -> Result<Vec<f64>, TA_RetCode> {
    let mut out_begin: TA_Integer = 0;
    let mut out_size: TA_Integer = 0;
    let begin_idx = check_begin_idx1(len, real_ptr) as i32;
    let end_idx = len as i32 - begin_idx - 1;
    let lookback = begin_idx + unsafe { TA_ACOS_Lookback() };
    let (mut out, ptr) = make_vec(len, lookback);
    let ret_code = unsafe {
        TA_ACOS(
            0,
            end_idx,
            real_ptr.offset(begin_idx as isize),
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

pub fn ta_asin(real_ptr: *const f64, len: usize) -> Result<Vec<f64>, TA_RetCode> {
    let mut out_begin: TA_Integer = 0;
    let mut out_size: TA_Integer = 0;
    let begin_idx = check_begin_idx1(len, real_ptr) as i32;
    let end_idx = len as i32 - begin_idx - 1;
    let lookback = begin_idx + unsafe { TA_ASIN_Lookback() };
    let (mut out, ptr) = make_vec(len, lookback);
    let ret_code = unsafe {
        TA_ASIN(
            0,
            end_idx,
            real_ptr.offset(begin_idx as isize),
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

pub fn ta_atan(real_ptr: *const f64, len: usize) -> Result<Vec<f64>, TA_RetCode> {
    let begin_idx = check_begin_idx1(len, real_ptr) as i32;
    let end_idx = len as i32 - begin_idx - 1;
    let lookback = begin_idx + unsafe { TA_ATAN_Lookback() };
    let (mut out, ptr) = make_vec(len, lookback);
    let mut out_begin: TA_Integer = 0;
    let mut out_size: TA_Integer = 0;
    let ret_code = unsafe {
        TA_ATAN(
            0,
            end_idx,
            real_ptr.offset(begin_idx as isize),
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

pub fn ta_ceil(real_ptr: *const f64, len: usize) -> Result<Vec<f64>, TA_RetCode> {
    let begin_idx = check_begin_idx1(len, real_ptr) as i32;
    let end_idx = len as i32 - begin_idx - 1;
    let lookback = begin_idx + unsafe { TA_CEIL_Lookback() };
    let (mut out, ptr) = make_vec(len, lookback);
    let mut out_begin: TA_Integer = 0;
    let mut out_size: TA_Integer = 0;
    let ret_code = unsafe {
        TA_CEIL(
            0,
            end_idx,
            real_ptr.offset(begin_idx as isize),
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

pub fn ta_cos(real_ptr: *const f64, len: usize) -> Result<Vec<f64>, TA_RetCode> {
    let begin_idx = check_begin_idx1(len, real_ptr) as i32;
    let end_idx = len as i32 - begin_idx - 1;
    let lookback = begin_idx + unsafe { TA_COS_Lookback() };
    let (mut out, ptr) = make_vec(len, lookback);
    let mut out_begin: TA_Integer = 0;
    let mut out_size: TA_Integer = 0;
    let ret_code = unsafe {
        TA_COS(
            0,
            end_idx,
            real_ptr.offset(begin_idx as isize),
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

pub fn ta_cosh(real_ptr: *const f64, len: usize) -> Result<Vec<f64>, TA_RetCode> {
    let begin_idx = check_begin_idx1(len, real_ptr) as i32;
    let end_idx = len as i32 - begin_idx - 1;
    let lookback = begin_idx + unsafe { TA_COSH_Lookback() };
    let (mut out, ptr) = make_vec(len, lookback);
    let mut out_begin: TA_Integer = 0;
    let mut out_size: TA_Integer = 0;
    let ret_code = unsafe {
        TA_COSH(
            0,
            end_idx,
            real_ptr.offset(begin_idx as isize),
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

pub fn ta_exp(real_ptr: *const f64, len: usize) -> Result<Vec<f64>, TA_RetCode> {
    let begin_idx = check_begin_idx1(len, real_ptr) as i32;
    let end_idx = len as i32 - begin_idx - 1;
    let lookback = begin_idx + unsafe { TA_EXP_Lookback() };
    let (mut out, ptr) = make_vec(len, lookback);
    let mut out_begin: TA_Integer = 0;
    let mut out_size: TA_Integer = 0;

    let ret_code = unsafe {
        TA_EXP(
            0,
            end_idx,
            real_ptr.offset(begin_idx as isize),
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

pub fn ta_floor(real_ptr: *const f64, len: usize) -> Result<Vec<f64>, TA_RetCode> {
    let begin_idx = check_begin_idx1(len, real_ptr) as i32;
    let end_idx = len as i32 - begin_idx - 1;
    let lookback = begin_idx + unsafe { TA_FLOOR_Lookback() };
    let (mut out, ptr) = make_vec(len, lookback);
    let mut out_begin: TA_Integer = 0;
    let mut out_size: TA_Integer = 0;

    let ret_code = unsafe {
        TA_FLOOR(
            0,
            end_idx,
            real_ptr.offset(begin_idx as isize),
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

pub fn ta_ln(real_ptr: *const f64, len: usize) -> Result<Vec<f64>, TA_RetCode> {
    let begin_idx = check_begin_idx1(len, real_ptr) as i32;
    let end_idx = len as i32 - begin_idx - 1;
    let lookback = begin_idx + unsafe { TA_LN_Lookback() };
    let (mut out, ptr) = make_vec(len, lookback);
    let mut out_begin: TA_Integer = 0;
    let mut out_size: TA_Integer = 0;

    let ret_code = unsafe {
        TA_LN(
            0,
            end_idx,
            real_ptr.offset(begin_idx as isize),
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

pub fn ta_log10(real_ptr: *const f64, len: usize) -> Result<Vec<f64>, TA_RetCode> {
    let begin_idx = check_begin_idx1(len, real_ptr) as i32;
    let end_idx = len as i32 - begin_idx - 1;
    let lookback = begin_idx + unsafe { TA_LOG10_Lookback() };
    let (mut out, ptr) = make_vec(len, lookback);
    let mut out_begin: TA_Integer = 0;
    let mut out_size: TA_Integer = 0;

    let ret_code = unsafe {
        TA_LOG10(
            0,
            end_idx,
            real_ptr.offset(begin_idx as isize),
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

pub fn ta_sin(real_ptr: *const f64, len: usize) -> Result<Vec<f64>, TA_RetCode> {
    let begin_idx = check_begin_idx1(len, real_ptr) as i32;
    let end_idx = len as i32 - begin_idx - 1;
    let lookback = begin_idx + unsafe { TA_SIN_Lookback() };
    let (mut out, ptr) = make_vec(len, lookback);
    let mut out_begin: TA_Integer = 0;
    let mut out_size: TA_Integer = 0;

    let ret_code = unsafe {
        TA_SIN(
            0,
            end_idx,
            real_ptr.offset(begin_idx as isize),
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

pub fn ta_sinh(real_ptr: *const f64, len: usize) -> Result<Vec<f64>, TA_RetCode> {
    let begin_idx = check_begin_idx1(len, real_ptr) as i32;
    let end_idx = len as i32 - begin_idx - 1;
    let lookback = begin_idx + unsafe { TA_SINH_Lookback() };
    let (mut out, ptr) = make_vec(len, lookback);
    let mut out_begin: TA_Integer = 0;
    let mut out_size: TA_Integer = 0;

    let ret_code = unsafe {
        TA_SINH(
            0,
            end_idx,
            real_ptr.offset(begin_idx as isize),
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

pub fn ta_sqrt(real_ptr: *const f64, len: usize) -> Result<Vec<f64>, TA_RetCode> {
    let begin_idx = check_begin_idx1(len, real_ptr) as i32;
    let end_idx = len as i32 - begin_idx - 1;
    let lookback = begin_idx + unsafe { TA_SQRT_Lookback() };
    let (mut out, ptr) = make_vec(len, lookback);
    let mut out_begin: TA_Integer = 0;
    let mut out_size: TA_Integer = 0;

    let ret_code = unsafe {
        TA_SQRT(
            0,
            end_idx,
            real_ptr.offset(begin_idx as isize),
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

pub fn ta_tan(real_ptr: *const f64, len: usize) -> Result<Vec<f64>, TA_RetCode> {
    let begin_idx = check_begin_idx1(len, real_ptr) as i32;
    let end_idx = len as i32 - begin_idx - 1;
    let lookback = begin_idx + unsafe { TA_TAN_Lookback() };
    let (mut out, ptr) = make_vec(len, lookback);
    let mut out_begin: TA_Integer = 0;
    let mut out_size: TA_Integer = 0;

    let ret_code = unsafe {
        TA_TAN(
            0,
            end_idx,
            real_ptr.offset(begin_idx as isize),
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

pub fn ta_tanh(real_ptr: *const f64, len: usize) -> Result<Vec<f64>, TA_RetCode> {
    let begin_idx = check_begin_idx1(len, real_ptr) as i32;
    let end_idx = len as i32 - begin_idx - 1;
    let lookback = begin_idx + unsafe { TA_TANH_Lookback() };
    let (mut out, ptr) = make_vec(len, lookback);
    let mut out_begin: TA_Integer = 0;
    let mut out_size: TA_Integer = 0;

    let ret_code = unsafe {
        TA_TANH(
            0,
            end_idx,
            real_ptr.offset(begin_idx as isize),
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
