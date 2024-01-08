use crate::utils::{check_begin_idx4, make_vec};
use serde::Deserialize;
use talib_sys::{TA_CDL2CROWS_Lookback, TA_CDL2CROWS};
use talib_sys::{TA_CDL3BLACKCROWS_Lookback, TA_CDL3BLACKCROWS};
use talib_sys::{TA_CDL3INSIDE_Lookback, TA_CDL3INSIDE};
use talib_sys::{TA_CDL3LINESTRIKE_Lookback, TA_CDL3LINESTRIKE};
use talib_sys::{TA_CDL3OUTSIDE_Lookback, TA_CDL3OUTSIDE};
use talib_sys::{TA_CDL3STARSINSOUTH_Lookback, TA_CDL3STARSINSOUTH};
use talib_sys::{TA_CDL3WHITESOLDIERS_Lookback, TA_CDL3WHITESOLDIERS};
use talib_sys::{TA_CDLABANDONEDBABY_Lookback, TA_CDLABANDONEDBABY};
use talib_sys::{TA_CDLADVANCEBLOCK_Lookback, TA_CDLADVANCEBLOCK};
use talib_sys::{TA_CDLBELTHOLD_Lookback, TA_CDLBELTHOLD};
use talib_sys::{TA_CDLBREAKAWAY_Lookback, TA_CDLBREAKAWAY};
use talib_sys::{TA_CDLCLOSINGMARUBOZU_Lookback, TA_CDLCLOSINGMARUBOZU};
use talib_sys::{TA_CDLCONCEALBABYSWALL_Lookback, TA_CDLCONCEALBABYSWALL};
use talib_sys::{TA_CDLCOUNTERATTACK_Lookback, TA_CDLCOUNTERATTACK};
use talib_sys::{TA_CDLDARKCLOUDCOVER_Lookback, TA_CDLDARKCLOUDCOVER};
use talib_sys::{TA_CDLDOJISTAR_Lookback, TA_CDLDOJISTAR};
use talib_sys::{TA_CDLDOJI_Lookback, TA_CDLDOJI};
use talib_sys::{TA_CDLDRAGONFLYDOJI_Lookback, TA_CDLDRAGONFLYDOJI};
use talib_sys::{TA_CDLENGULFING_Lookback, TA_CDLENGULFING};
use talib_sys::{TA_CDLEVENINGDOJISTAR_Lookback, TA_CDLEVENINGDOJISTAR};
use talib_sys::{TA_CDLEVENINGSTAR_Lookback, TA_CDLEVENINGSTAR};
use talib_sys::{TA_CDLGAPSIDESIDEWHITE_Lookback, TA_CDLGAPSIDESIDEWHITE};
use talib_sys::{TA_CDLGRAVESTONEDOJI_Lookback, TA_CDLGRAVESTONEDOJI};
use talib_sys::{TA_CDLHAMMER_Lookback, TA_CDLHAMMER};
use talib_sys::{TA_CDLHANGINGMAN_Lookback, TA_CDLHANGINGMAN};
use talib_sys::{TA_CDLHARAMICROSS_Lookback, TA_CDLHARAMICROSS};
use talib_sys::{TA_CDLHARAMI_Lookback, TA_CDLHARAMI};
use talib_sys::{TA_CDLHIGHWAVE_Lookback, TA_CDLHIGHWAVE};
use talib_sys::{TA_CDLHIKKAKEMOD_Lookback, TA_CDLHIKKAKEMOD};
use talib_sys::{TA_CDLHIKKAKE_Lookback, TA_CDLHIKKAKE};
use talib_sys::{TA_CDLHOMINGPIGEON_Lookback, TA_CDLHOMINGPIGEON};
use talib_sys::{TA_CDLIDENTICAL3CROWS_Lookback, TA_CDLIDENTICAL3CROWS};
use talib_sys::{TA_CDLINNECK_Lookback, TA_CDLINNECK};
use talib_sys::{TA_CDLINVERTEDHAMMER_Lookback, TA_CDLINVERTEDHAMMER};
use talib_sys::{TA_CDLKICKINGBYLENGTH_Lookback, TA_CDLKICKINGBYLENGTH};
use talib_sys::{TA_CDLKICKING_Lookback, TA_CDLKICKING};
use talib_sys::{TA_CDLLADDERBOTTOM_Lookback, TA_CDLLADDERBOTTOM};
use talib_sys::{TA_CDLLONGLEGGEDDOJI_Lookback, TA_CDLLONGLEGGEDDOJI};
use talib_sys::{TA_CDLLONGLINE_Lookback, TA_CDLLONGLINE};
use talib_sys::{TA_CDLMARUBOZU_Lookback, TA_CDLMARUBOZU};
use talib_sys::{TA_CDLMATCHINGLOW_Lookback, TA_CDLMATCHINGLOW};
use talib_sys::{TA_CDLMATHOLD_Lookback, TA_CDLMATHOLD};
use talib_sys::{TA_CDLMORNINGDOJISTAR_Lookback, TA_CDLMORNINGDOJISTAR};
use talib_sys::{TA_CDLMORNINGSTAR_Lookback, TA_CDLMORNINGSTAR};
use talib_sys::{TA_CDLONNECK_Lookback, TA_CDLONNECK};
use talib_sys::{TA_CDLPIERCING_Lookback, TA_CDLPIERCING};
use talib_sys::{TA_CDLRICKSHAWMAN_Lookback, TA_CDLRICKSHAWMAN};
use talib_sys::{TA_CDLRISEFALL3METHODS_Lookback, TA_CDLRISEFALL3METHODS};
use talib_sys::{TA_CDLSEPARATINGLINES_Lookback, TA_CDLSEPARATINGLINES};
use talib_sys::{TA_CDLSHOOTINGSTAR_Lookback, TA_CDLSHOOTINGSTAR};
use talib_sys::{TA_CDLSHORTLINE_Lookback, TA_CDLSHORTLINE};
use talib_sys::{TA_CDLSPINNINGTOP_Lookback, TA_CDLSPINNINGTOP};
use talib_sys::{TA_CDLSTALLEDPATTERN_Lookback, TA_CDLSTALLEDPATTERN};
use talib_sys::{TA_CDLSTICKSANDWICH_Lookback, TA_CDLSTICKSANDWICH};
use talib_sys::{TA_CDLTAKURI_Lookback, TA_CDLTAKURI};
use talib_sys::{TA_CDLTASUKIGAP_Lookback, TA_CDLTASUKIGAP};
use talib_sys::{TA_CDLTHRUSTING_Lookback, TA_CDLTHRUSTING};
use talib_sys::{TA_CDLTRISTAR_Lookback, TA_CDLTRISTAR};
use talib_sys::{TA_CDLUNIQUE3RIVER_Lookback, TA_CDLUNIQUE3RIVER};
use talib_sys::{TA_CDLUPSIDEGAP2CROWS_Lookback, TA_CDLUPSIDEGAP2CROWS};
use talib_sys::{TA_CDLXSIDEGAP3METHODS_Lookback, TA_CDLXSIDEGAP3METHODS};
use talib_sys::{TA_Integer, TA_RetCode};

#[derive(Deserialize)]
pub struct CDLKwargs {
    penetration: f64,
}

pub fn ta_cdl2crows(
    open_ptr: *const f64,
    high_ptr: *const f64,
    low_ptr: *const f64,
    close_ptr: *const f64,
    len: usize,
) -> Result<Vec<i32>, TA_RetCode> {
    let mut out_begin: TA_Integer = 0;
    let mut out_size: TA_Integer = 0;
    let begin_idx = check_begin_idx4(len, open_ptr, high_ptr, low_ptr, close_ptr) as i32;
    let end_idx = len as i32 - begin_idx - 1;
    let lookback = begin_idx + unsafe { TA_CDL2CROWS_Lookback() };
    let (mut out, ptr) = make_vec(len, lookback);
    let ret_code = unsafe {
        TA_CDL2CROWS(
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

pub fn ta_cdl3blackcrows(
    open_ptr: *const f64,
    high_ptr: *const f64,
    low_ptr: *const f64,
    close_ptr: *const f64,
    len: usize,
) -> Result<Vec<i32>, TA_RetCode> {
    let mut out_begin: TA_Integer = 0;
    let mut out_size: TA_Integer = 0;
    let begin_idx = check_begin_idx4(len, open_ptr, high_ptr, low_ptr, close_ptr) as i32;
    let end_idx = len as i32 - begin_idx - 1;
    let lookback = begin_idx + unsafe { TA_CDL3BLACKCROWS_Lookback() };
    let (mut out, ptr) = make_vec(len, lookback);
    let ret_code = unsafe {
        TA_CDL3BLACKCROWS(
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

pub fn ta_cdl3inside(
    open_ptr: *const f64,
    high_ptr: *const f64,
    low_ptr: *const f64,
    close_ptr: *const f64,
    len: usize,
) -> Result<Vec<i32>, TA_RetCode> {
    let mut out_begin: TA_Integer = 0;
    let mut out_size: TA_Integer = 0;
    let begin_idx = check_begin_idx4(len, open_ptr, high_ptr, low_ptr, close_ptr) as i32;
    let end_idx = len as i32 - begin_idx - 1;
    let lookback = begin_idx + unsafe { TA_CDL3INSIDE_Lookback() };
    let (mut out, ptr) = make_vec(len, lookback);
    let ret_code = unsafe {
        TA_CDL3INSIDE(
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

pub fn ta_cdl3linestrike(
    open_ptr: *const f64,
    high_ptr: *const f64,
    low_ptr: *const f64,
    close_ptr: *const f64,
    len: usize,
) -> Result<Vec<i32>, TA_RetCode> {
    let mut out_begin: TA_Integer = 0;
    let mut out_size: TA_Integer = 0;
    let begin_idx = check_begin_idx4(len, open_ptr, high_ptr, low_ptr, close_ptr) as i32;
    let end_idx = len as i32 - begin_idx - 1;
    let lookback = begin_idx + unsafe { TA_CDL3LINESTRIKE_Lookback() };
    let (mut out, ptr) = make_vec(len, lookback);
    let ret_code = unsafe {
        TA_CDL3LINESTRIKE(
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

pub fn ta_cdl3outside(
    open_ptr: *const f64,
    high_ptr: *const f64,
    low_ptr: *const f64,
    close_ptr: *const f64,
    len: usize,
) -> Result<Vec<i32>, TA_RetCode> {
    let mut out_begin: TA_Integer = 0;
    let mut out_size: TA_Integer = 0;
    let begin_idx = check_begin_idx4(len, open_ptr, high_ptr, low_ptr, close_ptr) as i32;
    let end_idx = len as i32 - begin_idx - 1;
    let lookback = begin_idx + unsafe { TA_CDL3OUTSIDE_Lookback() };
    let (mut out, ptr) = make_vec(len, lookback);
    let ret_code = unsafe {
        TA_CDL3OUTSIDE(
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

pub fn ta_cdl3starsinsouth(
    open_ptr: *const f64,
    high_ptr: *const f64,
    low_ptr: *const f64,
    close_ptr: *const f64,
    len: usize,
) -> Result<Vec<i32>, TA_RetCode> {
    let mut out_begin: TA_Integer = 0;
    let mut out_size: TA_Integer = 0;
    let begin_idx = check_begin_idx4(len, open_ptr, high_ptr, low_ptr, close_ptr) as i32;
    let end_idx = len as i32 - begin_idx - 1;
    let lookback = begin_idx + unsafe { TA_CDL3STARSINSOUTH_Lookback() };
    let (mut out, ptr) = make_vec(len, lookback);
    let ret_code = unsafe {
        TA_CDL3STARSINSOUTH(
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

pub fn ta_cdl3whitesoldiers(
    open_ptr: *const f64,
    high_ptr: *const f64,
    low_ptr: *const f64,
    close_ptr: *const f64,
    len: usize,
) -> Result<Vec<i32>, TA_RetCode> {
    let mut out_begin: TA_Integer = 0;
    let mut out_size: TA_Integer = 0;
    let begin_idx = check_begin_idx4(len, open_ptr, high_ptr, low_ptr, close_ptr) as i32;
    let end_idx = len as i32 - begin_idx - 1;
    let lookback = begin_idx + unsafe { TA_CDL3WHITESOLDIERS_Lookback() };
    let (mut out, ptr) = make_vec(len, lookback);
    let ret_code = unsafe {
        TA_CDL3WHITESOLDIERS(
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

pub fn ta_cdlabandonedbaby(
    open_ptr: *const f64,
    high_ptr: *const f64,
    low_ptr: *const f64,
    close_ptr: *const f64,
    len: usize,
    kwargs: &CDLKwargs,
) -> Result<Vec<i32>, TA_RetCode> {
    let mut out_begin: TA_Integer = 0;
    let mut out_size: TA_Integer = 0;
    let begin_idx = check_begin_idx4(len, open_ptr, high_ptr, low_ptr, close_ptr) as i32;
    let end_idx = len as i32 - begin_idx - 1;
    let lookback = begin_idx + unsafe { TA_CDLABANDONEDBABY_Lookback(kwargs.penetration) };
    let (mut out, ptr) = make_vec(len, lookback);
    let ret_code = unsafe {
        TA_CDLABANDONEDBABY(
            0,
            end_idx,
            open_ptr.offset(begin_idx as isize),
            high_ptr.offset(begin_idx as isize),
            low_ptr.offset(begin_idx as isize),
            close_ptr.offset(begin_idx as isize),
            kwargs.penetration,
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

pub fn ta_cdladvanceblock(
    open_ptr: *const f64,
    high_ptr: *const f64,
    low_ptr: *const f64,
    close_ptr: *const f64,

    len: usize,
) -> Result<Vec<i32>, TA_RetCode> {
    let mut out_begin: TA_Integer = 0;
    let mut out_size: TA_Integer = 0;

    let begin_idx = check_begin_idx4(len, open_ptr, high_ptr, low_ptr, close_ptr) as i32;
    let end_idx = len as i32 - begin_idx - 1;
    let lookback = begin_idx + unsafe { TA_CDLADVANCEBLOCK_Lookback() };

    let (mut out, ptr) = make_vec(len, lookback);

    let ret_code = unsafe {
        TA_CDLADVANCEBLOCK(
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

pub fn ta_cdlbelthold(
    open_ptr: *const f64,
    high_ptr: *const f64,
    low_ptr: *const f64,
    close_ptr: *const f64,
    len: usize,
) -> Result<Vec<i32>, TA_RetCode> {
    let mut out_begin: TA_Integer = 0;
    let mut out_size: TA_Integer = 0;

    let begin_idx = check_begin_idx4(len, open_ptr, high_ptr, low_ptr, close_ptr) as i32;
    let end_idx = len as i32 - begin_idx - 1;
    let lookback = begin_idx + unsafe { TA_CDLBELTHOLD_Lookback() };
    let (mut out, ptr) = make_vec(len, lookback);

    let ret_code = unsafe {
        TA_CDLBELTHOLD(
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

pub fn ta_cdlbreakaway(
    open_ptr: *const f64,
    high_ptr: *const f64,
    low_ptr: *const f64,
    close_ptr: *const f64,

    len: usize,
) -> Result<Vec<i32>, TA_RetCode> {
    let mut out_begin: TA_Integer = 0;
    let mut out_size: TA_Integer = 0;

    let begin_idx = check_begin_idx4(len, open_ptr, high_ptr, low_ptr, close_ptr) as i32;
    let end_idx = len as i32 - begin_idx - 1;
    let lookback = begin_idx + unsafe { TA_CDLBREAKAWAY_Lookback() };

    let (mut out, ptr) = make_vec(len, lookback);

    let ret_code = unsafe {
        TA_CDLBREAKAWAY(
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

pub fn ta_cdlclosingmarubozu(
    open_ptr: *const f64,
    high_ptr: *const f64,
    low_ptr: *const f64,
    close_ptr: *const f64,
    len: usize,
) -> Result<Vec<i32>, TA_RetCode> {
    let mut out_begin: TA_Integer = 0;
    let mut out_size: TA_Integer = 0;

    let begin_idx = check_begin_idx4(len, open_ptr, high_ptr, low_ptr, close_ptr) as i32;
    let end_idx = len as i32 - begin_idx - 1;
    let lookback = begin_idx + unsafe { TA_CDLCLOSINGMARUBOZU_Lookback() };

    let (mut out, ptr) = make_vec(len, lookback);

    let ret_code = unsafe {
        TA_CDLCLOSINGMARUBOZU(
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

pub fn ta_cdlconcealbabyswall(
    open_ptr: *const f64,
    high_ptr: *const f64,
    low_ptr: *const f64,
    close_ptr: *const f64,

    len: usize,
) -> Result<Vec<i32>, TA_RetCode> {
    let mut out_begin: TA_Integer = 0;

    let mut out_size: TA_Integer = 0;

    let begin_idx = check_begin_idx4(len, open_ptr, high_ptr, low_ptr, close_ptr) as i32;
    let end_idx = len as i32 - begin_idx - 1;
    let lookback = begin_idx + unsafe { TA_CDLCONCEALBABYSWALL_Lookback() };

    let (mut out, ptr) = make_vec(len, lookback);

    let ret_code = unsafe {
        TA_CDLCONCEALBABYSWALL(
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
                unsafe { out.set_len(out_size_begin) };
            } else {
                unsafe { out.set_len(len) };
            }

            Ok(out)
        }
        _ => Err(ret_code),
    }
}

pub fn ta_cdlcounterattack(
    open_ptr: *const f64,
    high_ptr: *const f64,
    low_ptr: *const f64,
    close_ptr: *const f64,

    len: usize,
) -> Result<Vec<i32>, TA_RetCode> {
    let mut out_begin: TA_Integer = 0;

    let mut out_size: TA_Integer = 0;

    let begin_idx = check_begin_idx4(len, open_ptr, high_ptr, low_ptr, close_ptr) as i32;
    let end_idx = len as i32 - begin_idx - 1;
    let lookback = begin_idx + unsafe { TA_CDLCOUNTERATTACK_Lookback() };

    let (mut out, ptr) = make_vec(len, lookback);

    let ret_code = unsafe {
        TA_CDLCOUNTERATTACK(
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
                unsafe { out.set_len(out_size_begin) };
            } else {
                unsafe { out.set_len(len) };
            }

            Ok(out)
        }
        _ => Err(ret_code),
    }
}

pub fn ta_cdldarkcloudcover(
    open_ptr: *const f64,
    high_ptr: *const f64,
    low_ptr: *const f64,
    close_ptr: *const f64,
    len: usize,
    kwargs: &CDLKwargs,
) -> Result<Vec<i32>, TA_RetCode> {
    let mut out_begin: TA_Integer = 0;

    let mut out_size: TA_Integer = 0;

    let begin_idx = check_begin_idx4(len, open_ptr, high_ptr, low_ptr, close_ptr) as i32;
    let end_idx = len as i32 - begin_idx - 1;
    let lookback = begin_idx + unsafe { TA_CDLDARKCLOUDCOVER_Lookback(kwargs.penetration) };

    let (mut out, ptr) = make_vec(len, lookback);

    let ret_code = unsafe {
        TA_CDLDARKCLOUDCOVER(
            0,
            end_idx,
            open_ptr.offset(begin_idx as isize),
            high_ptr.offset(begin_idx as isize),
            low_ptr.offset(begin_idx as isize),
            close_ptr.offset(begin_idx as isize),
            kwargs.penetration,
            &mut out_begin,
            &mut out_size,
            ptr,
        )
    };

    let out_size_begin = (begin_idx + out_begin + out_size) as usize;

    // println!("out_size: {}", out_size);

    match ret_code {
        TA_RetCode::TA_SUCCESS => {
            if out_size != 0 {
                unsafe { out.set_len(out_size_begin) };
            } else {
                unsafe { out.set_len(len) };
            }

            Ok(out)
        }
        _ => Err(ret_code),
    }
}

pub fn ta_cdldojistar(
    open_ptr: *const f64,
    high_ptr: *const f64,
    low_ptr: *const f64,
    close_ptr: *const f64,

    len: usize,
) -> Result<Vec<i32>, TA_RetCode> {
    let mut out_begin: TA_Integer = 0;

    let mut out_size: TA_Integer = 0;

    let begin_idx = check_begin_idx4(len, open_ptr, high_ptr, low_ptr, close_ptr) as i32;
    let end_idx = len as i32 - begin_idx - 1;
    let lookback = begin_idx + unsafe { TA_CDLDOJISTAR_Lookback() };

    let (mut out, ptr) = make_vec(len, lookback);

    let ret_code = unsafe {
        TA_CDLDOJISTAR(
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

    // println!("out_begin: {}", out_begin);
    // println!("out_size: {}", out_size);

    let out_size_begin = (begin_idx + out_begin + out_size) as usize;

    // println!("out_size: {}", out_size);

    match ret_code {
        TA_RetCode::TA_SUCCESS => {
            if out_size != 0 {
                unsafe { out.set_len(out_size_begin) };
            } else {
                unsafe { out.set_len(len) };
            }

            Ok(out)
        }
        _ => Err(ret_code),
    }
}

pub fn ta_cdldoji(
    open_ptr: *const f64,
    high_ptr: *const f64,
    low_ptr: *const f64,
    close_ptr: *const f64,
    len: usize,
) -> Result<Vec<i32>, TA_RetCode> {
    let mut out_begin: TA_Integer = 0;

    let mut out_size: TA_Integer = 0;

    let begin_idx = check_begin_idx4(len, open_ptr, high_ptr, low_ptr, close_ptr) as i32;
    let end_idx = len as i32 - begin_idx - 1;
    let lookback = begin_idx + unsafe { TA_CDLDOJI_Lookback() };

    let (mut out, ptr) = make_vec(len, lookback);

    let ret_code = unsafe {
        TA_CDLDOJI(
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

pub fn ta_cdldragonflydoji(
    open_ptr: *const f64,
    high_ptr: *const f64,
    low_ptr: *const f64,
    close_ptr: *const f64,

    len: usize,
) -> Result<Vec<i32>, TA_RetCode> {
    let mut out_begin: TA_Integer = 0;

    let mut out_size: TA_Integer = 0;

    let begin_idx = check_begin_idx4(len, open_ptr, high_ptr, low_ptr, close_ptr) as i32;
    let end_idx = len as i32 - begin_idx - 1;
    let lookback = begin_idx + unsafe { TA_CDLDRAGONFLYDOJI_Lookback() };

    let (mut out, ptr) = make_vec(len, lookback);

    let ret_code = unsafe {
        TA_CDLDRAGONFLYDOJI(
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

pub fn ta_cdlengulfing(
    open_ptr: *const f64,
    high_ptr: *const f64,
    low_ptr: *const f64,
    close_ptr: *const f64,

    len: usize,
) -> Result<Vec<i32>, TA_RetCode> {
    let mut out_begin: TA_Integer = 0;

    let mut out_size: TA_Integer = 0;

    let begin_idx = check_begin_idx4(len, open_ptr, high_ptr, low_ptr, close_ptr) as i32;
    let end_idx = len as i32 - begin_idx - 1;
    let lookback = begin_idx + unsafe { TA_CDLENGULFING_Lookback() };

    let (mut out, ptr) = make_vec(len, lookback);

    let ret_code = unsafe {
        TA_CDLENGULFING(
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

pub fn ta_cdleveningdojistar(
    open_ptr: *const f64,
    high_ptr: *const f64,
    low_ptr: *const f64,
    close_ptr: *const f64,
    len: usize,
    kwargs: &CDLKwargs,
) -> Result<Vec<i32>, TA_RetCode> {
    let mut out_begin: TA_Integer = 0;

    let mut out_size: TA_Integer = 0;

    let begin_idx = check_begin_idx4(len, open_ptr, high_ptr, low_ptr, close_ptr) as i32;
    let end_idx = len as i32 - begin_idx - 1;
    let lookback = begin_idx + unsafe { TA_CDLEVENINGDOJISTAR_Lookback(kwargs.penetration) };

    let (mut out, ptr) = make_vec(len, lookback);

    let ret_code = unsafe {
        TA_CDLEVENINGDOJISTAR(
            0,
            end_idx,
            open_ptr.offset(begin_idx as isize),
            high_ptr.offset(begin_idx as isize),
            low_ptr.offset(begin_idx as isize),
            close_ptr.offset(begin_idx as isize),
            kwargs.penetration,
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

pub fn ta_cdleveningstar(
    open_ptr: *const f64,
    high_ptr: *const f64,
    low_ptr: *const f64,
    close_ptr: *const f64,
    len: usize,
    kwargs: &CDLKwargs,
) -> Result<Vec<i32>, TA_RetCode> {
    let mut out_begin: TA_Integer = 0;

    let mut out_size: TA_Integer = 0;

    let begin_idx = check_begin_idx4(len, open_ptr, high_ptr, low_ptr, close_ptr) as i32;
    let end_idx = len as i32 - begin_idx - 1;
    let lookback = begin_idx + unsafe { TA_CDLEVENINGSTAR_Lookback(kwargs.penetration) };

    let (mut out, ptr) = make_vec(len, lookback);

    let ret_code = unsafe {
        TA_CDLEVENINGSTAR(
            0,
            end_idx,
            open_ptr.offset(begin_idx as isize),
            high_ptr.offset(begin_idx as isize),
            low_ptr.offset(begin_idx as isize),
            close_ptr.offset(begin_idx as isize),
            kwargs.penetration,
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

pub fn ta_cdlgapsidesidewhite(
    open_ptr: *const f64,
    high_ptr: *const f64,
    low_ptr: *const f64,
    close_ptr: *const f64,
    len: usize,
) -> Result<Vec<i32>, TA_RetCode> {
    let mut out_begin: TA_Integer = 0;
    let mut out_size: TA_Integer = 0;
    let begin_idx = check_begin_idx4(len, open_ptr, high_ptr, low_ptr, close_ptr) as i32;
    let end_idx = len as i32 - begin_idx - 1;
    let lookback = begin_idx + unsafe { TA_CDLGAPSIDESIDEWHITE_Lookback() };
    let (mut out, ptr) = make_vec(len, lookback);
    let ret_code = unsafe {
        TA_CDLGAPSIDESIDEWHITE(
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
    // println!("out_size: {}", out_size);
    match ret_code {
        TA_RetCode::TA_SUCCESS => {
            if out_size != 0 {
                unsafe {
                    out.set_len(out_size_begin);
                    // println!("out.len(): {}", out.len());
                }
            } else {
                unsafe {
                    out.set_len(len);
                    // println!("out.len(): {}", out.len());
                }
            }
            Ok(out)
        }
        _ => Err(ret_code),
    }
}

pub fn ta_cdlgravestonedoji(
    open_ptr: *const f64,
    high_ptr: *const f64,
    low_ptr: *const f64,
    close_ptr: *const f64,

    len: usize,
) -> Result<Vec<i32>, TA_RetCode> {
    let mut out_begin: TA_Integer = 0;

    let mut out_size: TA_Integer = 0;

    let begin_idx = check_begin_idx4(len, open_ptr, high_ptr, low_ptr, close_ptr) as i32;
    let end_idx = len as i32 - begin_idx - 1;
    let lookback = begin_idx + unsafe { TA_CDLGRAVESTONEDOJI_Lookback() };

    let (mut out, ptr) = make_vec(len, lookback);

    let ret_code = unsafe {
        TA_CDLGRAVESTONEDOJI(
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
                unsafe { out.set_len(out_size_begin) };
            } else {
                unsafe { out.set_len(len) };
            }

            Ok(out)
        }
        _ => Err(ret_code),
    }
}

pub fn ta_cdlhammer(
    open_ptr: *const f64,
    high_ptr: *const f64,
    low_ptr: *const f64,
    close_ptr: *const f64,

    len: usize,
) -> Result<Vec<i32>, TA_RetCode> {
    let mut out_begin: TA_Integer = 0;

    let mut out_size: TA_Integer = 0;

    let begin_idx = check_begin_idx4(len, open_ptr, high_ptr, low_ptr, close_ptr) as i32;
    let end_idx = len as i32 - begin_idx - 1;
    let lookback = begin_idx + unsafe { TA_CDLHAMMER_Lookback() };

    let (mut out, ptr) = make_vec(len, lookback);

    let ret_code = unsafe {
        TA_CDLHAMMER(
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
                unsafe { out.set_len(out_size_begin) };
            } else {
                unsafe { out.set_len(len) };
            }

            Ok(out)
        }
        _ => Err(ret_code),
    }
}

pub fn ta_cdlhangingman(
    open_ptr: *const f64,
    high_ptr: *const f64,
    low_ptr: *const f64,
    close_ptr: *const f64,
    len: usize,
) -> Result<Vec<i32>, TA_RetCode> {
    let mut out_begin: TA_Integer = 0;

    let mut out_size: TA_Integer = 0;

    let begin_idx = check_begin_idx4(len, open_ptr, high_ptr, low_ptr, close_ptr) as i32;
    let end_idx = len as i32 - begin_idx - 1;
    let lookback = begin_idx + unsafe { TA_CDLHANGINGMAN_Lookback() };

    let (mut out, ptr) = make_vec(len, lookback);

    let ret_code = unsafe {
        TA_CDLHANGINGMAN(
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
                unsafe { out.set_len(out_size_begin) };
            } else {
                unsafe { out.set_len(len) };
            }

            Ok(out)
        }
        _ => Err(ret_code),
    }
}

pub fn ta_cdlharamicross(
    open_ptr: *const f64,
    high_ptr: *const f64,
    low_ptr: *const f64,
    close_ptr: *const f64,
    len: usize,
) -> Result<Vec<i32>, TA_RetCode> {
    let mut out_begin: TA_Integer = 0;
    let mut out_size: TA_Integer = 0;

    let begin_idx = check_begin_idx4(len, open_ptr, high_ptr, low_ptr, close_ptr) as i32;
    let end_idx = len as i32 - begin_idx - 1;
    let lookback = begin_idx + unsafe { TA_CDLHARAMICROSS_Lookback() };
    let (mut out, ptr) = make_vec(len, lookback);
    let ret_code = unsafe {
        TA_CDLHARAMICROSS(
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
                unsafe { out.set_len(out_size_begin) };
            } else {
                unsafe { out.set_len(len) };
            }

            Ok(out)
        }
        _ => Err(ret_code),
    }
}

pub fn ta_cdlharami(
    open_ptr: *const f64,
    high_ptr: *const f64,
    low_ptr: *const f64,
    close_ptr: *const f64,
    len: usize,
) -> Result<Vec<i32>, TA_RetCode> {
    let mut out_begin: TA_Integer = 0;

    let mut out_size: TA_Integer = 0;

    let begin_idx = check_begin_idx4(len, open_ptr, high_ptr, low_ptr, close_ptr) as i32;
    let end_idx = len as i32 - begin_idx - 1;
    let lookback = begin_idx + unsafe { TA_CDLHARAMI_Lookback() };

    let (mut out, ptr) = make_vec(len, lookback);

    let ret_code = unsafe {
        TA_CDLHARAMI(
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
                unsafe { out.set_len(out_size_begin) };
            } else {
                unsafe { out.set_len(len) };
            }

            Ok(out)
        }
        _ => Err(ret_code),
    }
}

pub fn ta_cdlhighwave(
    open_ptr: *const f64,
    high_ptr: *const f64,
    low_ptr: *const f64,
    close_ptr: *const f64,

    len: usize,
) -> Result<Vec<i32>, TA_RetCode> {
    // println!("len: {}", len);

    let mut out_begin: TA_Integer = 0;

    let mut out_size: TA_Integer = 0;

    let begin_idx = check_begin_idx4(len, open_ptr, high_ptr, low_ptr, close_ptr) as i32;
    let end_idx = len as i32 - begin_idx - 1;
    let lookback = begin_idx + unsafe { TA_CDLHIGHWAVE_Lookback() };
    let (mut out, ptr) = make_vec(len, lookback);
    let ret_code = unsafe {
        TA_CDLHIGHWAVE(
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
                    // println!("out.len(): {}", out.len());
                }
            } else {
                unsafe {
                    out.set_len(len);
                    // println!("out.len(): {}", out.len());
                }
            }
            Ok(out)
        }
        _ => Err(ret_code),
    }
}

pub fn ta_cdlhikkakemod(
    open_ptr: *const f64,
    high_ptr: *const f64,
    low_ptr: *const f64,
    close_ptr: *const f64,
    len: usize,
) -> Result<Vec<i32>, TA_RetCode> {
    let mut out_begin: TA_Integer = 0;

    let mut out_size: TA_Integer = 0;

    let begin_idx = check_begin_idx4(len, open_ptr, high_ptr, low_ptr, close_ptr) as i32;
    let end_idx = len as i32 - begin_idx - 1;
    let lookback = begin_idx + unsafe { TA_CDLHIKKAKEMOD_Lookback() };

    let (mut out, ptr) = make_vec(len, lookback);

    let ret_code = unsafe {
        TA_CDLHIKKAKEMOD(
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

    // println!("out_begin: {}", out_begin);
    // println!("out_size: {}", out_size);

    let out_size_begin = (begin_idx + out_begin + out_size) as usize;

    // println!("out_size: {}", out_size);

    match ret_code {
        TA_RetCode::TA_SUCCESS => {
            if out_size != 0 {
                unsafe { out.set_len(out_size_begin) };
            } else {
                unsafe { out.set_len(len) };
            }

            Ok(out)
        }
        _ => Err(ret_code),
    }
}

pub fn ta_cdlhikkake(
    open_ptr: *const f64,
    high_ptr: *const f64,
    low_ptr: *const f64,
    close_ptr: *const f64,

    len: usize,
) -> Result<Vec<i32>, TA_RetCode> {
    // println!("len: {}", len);

    let mut out_begin: TA_Integer = 0;

    let mut out_size: TA_Integer = 0;

    let begin_idx = check_begin_idx4(len, open_ptr, high_ptr, low_ptr, close_ptr) as i32;
    let end_idx = len as i32 - begin_idx - 1;
    let lookback = begin_idx + unsafe { TA_CDLHIKKAKE_Lookback() };

    // println!("lookback: {}", lookback);

    let (mut out, ptr) = make_vec(len, lookback);

    // println!("out.len(): {}", out.len());

    let ret_code = unsafe {
        TA_CDLHIKKAKE(
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

    // println!("out_begin: {}", out_begin);
    // println!("out_size: {}", out_size);

    let out_size_begin = (begin_idx + out_begin + out_size) as usize;

    // println!("out_size: {}", out_size);

    match ret_code {
        TA_RetCode::TA_SUCCESS => {
            if out_size != 0 {
                unsafe { out.set_len(out_size_begin) };
            } else {
                unsafe { out.set_len(len) };
            }
            // println!("out.len(): {}", out.len());

            Ok(out)
        }
        _ => Err(ret_code),
    }
}

pub fn ta_cdlhomingpigeon(
    open_ptr: *const f64,
    high_ptr: *const f64,
    low_ptr: *const f64,
    close_ptr: *const f64,

    len: usize,
) -> Result<Vec<i32>, TA_RetCode> {
    // println!("len: {}", len);

    let mut out_begin: TA_Integer = 0;

    let mut out_size: TA_Integer = 0;

    let begin_idx = check_begin_idx4(len, open_ptr, high_ptr, low_ptr, close_ptr) as i32;
    let end_idx = len as i32 - begin_idx - 1;
    let lookback = begin_idx + unsafe { TA_CDLHOMINGPIGEON_Lookback() };

    // println!("lookback: {}", lookback);

    let (mut out, ptr) = make_vec(len, lookback);

    // println!("out.len(): {}", out.len());

    let ret_code = unsafe {
        TA_CDLHOMINGPIGEON(
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

    // println!("out_begin: {}", out_begin);
    // println!("out_size: {}", out_size);

    let out_size_begin = (begin_idx + out_begin + out_size) as usize;

    // println!("out_size: {}", out_size);

    match ret_code {
        TA_RetCode::TA_SUCCESS => {
            if out_size != 0 {
                unsafe { out.set_len(out_size_begin) };
            } else {
                unsafe { out.set_len(len) };
            }
            // println!("out.len(): {}", out.len());

            Ok(out)
        }
        _ => Err(ret_code),
    }
}

pub fn ta_cdlidentical3crows(
    open_ptr: *const f64,
    high_ptr: *const f64,
    low_ptr: *const f64,
    close_ptr: *const f64,
    len: usize,
) -> Result<Vec<i32>, TA_RetCode> {
    // println!("len: {}", len);

    let mut out_begin: TA_Integer = 0;

    let mut out_size: TA_Integer = 0;

    let begin_idx = check_begin_idx4(len, open_ptr, high_ptr, low_ptr, close_ptr) as i32;
    let end_idx = len as i32 - begin_idx - 1;
    let lookback = begin_idx + unsafe { TA_CDLIDENTICAL3CROWS_Lookback() };

    let (mut out, ptr) = make_vec(len, lookback);

    let ret_code = unsafe {
        TA_CDLIDENTICAL3CROWS(
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
                unsafe { out.set_len(out_size_begin) };
            } else {
                unsafe { out.set_len(len) };
            }
            // println!("out.len(): {}", out.len());

            Ok(out)
        }
        _ => Err(ret_code),
    }
}

pub fn ta_cdlinneck(
    open_ptr: *const f64,
    high_ptr: *const f64,
    low_ptr: *const f64,
    close_ptr: *const f64,

    len: usize,
) -> Result<Vec<i32>, TA_RetCode> {
    // println!("len: {}", len);

    let mut out_begin: TA_Integer = 0;

    let mut out_size: TA_Integer = 0;

    let begin_idx = check_begin_idx4(len, open_ptr, high_ptr, low_ptr, close_ptr) as i32;
    let end_idx = len as i32 - begin_idx - 1;
    let lookback = begin_idx + unsafe { TA_CDLINNECK_Lookback() };

    let (mut out, ptr) = make_vec(len, lookback);

    let ret_code = unsafe {
        TA_CDLINNECK(
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
                unsafe { out.set_len(out_size_begin) };
            } else {
                unsafe { out.set_len(len) };
            }
            // println!("out.len(): {}", out.len());

            Ok(out)
        }
        _ => Err(ret_code),
    }
}

pub fn ta_cdlinvertedhammer(
    open_ptr: *const f64,
    high_ptr: *const f64,
    low_ptr: *const f64,
    close_ptr: *const f64,

    len: usize,
) -> Result<Vec<i32>, TA_RetCode> {
    // println!("len: {}", len);

    let mut out_begin: TA_Integer = 0;

    let mut out_size: TA_Integer = 0;

    let begin_idx = check_begin_idx4(len, open_ptr, high_ptr, low_ptr, close_ptr) as i32;
    let end_idx = len as i32 - begin_idx - 1;
    let lookback = begin_idx + unsafe { TA_CDLINVERTEDHAMMER_Lookback() };

    let (mut out, ptr) = make_vec(len, lookback);

    let ret_code = unsafe {
        TA_CDLINVERTEDHAMMER(
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
                unsafe { out.set_len(out_size_begin) };
            } else {
                unsafe { out.set_len(len) };
            }
            // println!("out.len(): {}", out.len());

            Ok(out)
        }
        _ => Err(ret_code),
    }
}

pub fn ta_cdlkickingbylength(
    open_ptr: *const f64,
    high_ptr: *const f64,
    low_ptr: *const f64,
    close_ptr: *const f64,

    len: usize,
) -> Result<Vec<i32>, TA_RetCode> {
    // println!("len: {}", len);

    let mut out_begin: TA_Integer = 0;

    let mut out_size: TA_Integer = 0;

    let begin_idx = check_begin_idx4(len, open_ptr, high_ptr, low_ptr, close_ptr) as i32;
    let end_idx = len as i32 - begin_idx - 1;
    let lookback = begin_idx + unsafe { TA_CDLKICKINGBYLENGTH_Lookback() };

    let (mut out, ptr) = make_vec(len, lookback);

    let ret_code = unsafe {
        TA_CDLKICKINGBYLENGTH(
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
                unsafe { out.set_len(out_size_begin) };
            } else {
                unsafe { out.set_len(len) };
            }
            // println!("out.len(): {}", out.len());

            Ok(out)
        }
        _ => Err(ret_code),
    }
}

pub fn ta_cdlkicking(
    open_ptr: *const f64,
    high_ptr: *const f64,
    low_ptr: *const f64,
    close_ptr: *const f64,

    len: usize,
) -> Result<Vec<i32>, TA_RetCode> {
    // println!("len: {}", len);

    let mut out_begin: TA_Integer = 0;

    let mut out_size: TA_Integer = 0;

    let begin_idx = check_begin_idx4(len, open_ptr, high_ptr, low_ptr, close_ptr) as i32;
    let end_idx = len as i32 - begin_idx - 1;
    let lookback = begin_idx + unsafe { TA_CDLKICKING_Lookback() };

    let (mut out, ptr) = make_vec(len, lookback);

    let ret_code = unsafe {
        TA_CDLKICKING(
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
            // println!("out_begin: {}", out_begin);
            // println!("out_size: {}", out_size);

            if out_size != 0 {
                unsafe { out.set_len(out_size_begin) };
            } else {
                unsafe { out.set_len(len) };
            }
            // println!("out.len(): {}", out.len());

            Ok(out)
        }
        _ => Err(ret_code),
    }
}

pub fn ta_cdlladderbottom(
    open_ptr: *const f64,
    high_ptr: *const f64,
    low_ptr: *const f64,
    close_ptr: *const f64,

    len: usize,
) -> Result<Vec<i32>, TA_RetCode> {
    // println!("len: {}", len);

    let mut out_begin: TA_Integer = 0;

    let mut out_size: TA_Integer = 0;

    let begin_idx = check_begin_idx4(len, open_ptr, high_ptr, low_ptr, close_ptr) as i32;
    let end_idx = len as i32 - begin_idx - 1;
    let lookback = begin_idx + unsafe { TA_CDLLADDERBOTTOM_Lookback() };

    let (mut out, ptr) = make_vec(len, lookback);

    let ret_code = unsafe {
        TA_CDLLADDERBOTTOM(
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
    // println!("out_begin: {}", out_begin);
    // println!("out_size: {}", out_size);

    match ret_code {
        TA_RetCode::TA_SUCCESS => {
            // println!("out_begin: {}", out_begin);
            // println!("out_size: {}", out_size);

            if out_size != 0 {
                unsafe { out.set_len(out_size_begin) };
            } else {
                unsafe { out.set_len(len) };
            }
            // println!("out.len(): {}", out.len());

            Ok(out)
        }
        _ => Err(ret_code),
    }
}

pub fn ta_cdllongleggeddoji(
    open_ptr: *const f64,
    high_ptr: *const f64,
    low_ptr: *const f64,
    close_ptr: *const f64,
    len: usize,
) -> Result<Vec<i32>, TA_RetCode> {
    let mut out_begin: TA_Integer = 0;

    let mut out_size: TA_Integer = 0;

    let begin_idx = check_begin_idx4(len, open_ptr, high_ptr, low_ptr, close_ptr) as i32;
    let end_idx = len as i32 - begin_idx - 1;
    let lookback = begin_idx + unsafe { TA_CDLLONGLEGGEDDOJI_Lookback() };

    let (mut out, ptr) = make_vec(len, lookback);

    let ret_code = unsafe {
        TA_CDLLONGLEGGEDDOJI(
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
                unsafe { out.set_len(out_size_begin) };
            } else {
                unsafe { out.set_len(len) };
            }

            Ok(out)
        }
        _ => Err(ret_code),
    }
}

pub fn ta_cdllongline(
    open_ptr: *const f64,
    high_ptr: *const f64,
    low_ptr: *const f64,
    close_ptr: *const f64,

    len: usize,
) -> Result<Vec<i32>, TA_RetCode> {
    let mut out_begin: TA_Integer = 0;

    let mut out_size: TA_Integer = 0;

    let begin_idx = check_begin_idx4(len, open_ptr, high_ptr, low_ptr, close_ptr) as i32;
    let end_idx = len as i32 - begin_idx - 1;
    let lookback = begin_idx + unsafe { TA_CDLLONGLINE_Lookback() };

    let (mut out, ptr) = make_vec(len, lookback);

    let ret_code = unsafe {
        TA_CDLLONGLINE(
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

    // println!("out_begin: {}", out_begin);
    // println!("out_size: {}", out_size);

    match ret_code {
        TA_RetCode::TA_SUCCESS => {
            if out_size != 0 {
                unsafe { out.set_len(out_size_begin) };
            } else {
                unsafe { out.set_len(len) };
            }

            Ok(out)
        }
        _ => Err(ret_code),
    }
}

pub fn ta_cdlmarubozu(
    open_ptr: *const f64,
    high_ptr: *const f64,
    low_ptr: *const f64,
    close_ptr: *const f64,
    len: usize,
) -> Result<Vec<i32>, TA_RetCode> {
    let mut out_begin: TA_Integer = 0;
    let mut out_size: TA_Integer = 0;
    let begin_idx = check_begin_idx4(len, open_ptr, high_ptr, low_ptr, close_ptr) as i32;
    let end_idx = len as i32 - begin_idx - 1;
    let lookback = begin_idx + unsafe { TA_CDLMARUBOZU_Lookback() };
    let (mut out, ptr) = make_vec(len, lookback);
    let ret_code = unsafe {
        TA_CDLMARUBOZU(
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
                unsafe { out.set_len(out_size_begin) };
            } else {
                unsafe { out.set_len(len) };
            }
            Ok(out)
        }
        _ => Err(ret_code),
    }
}

pub fn ta_cdlmatchinglow(
    open_ptr: *const f64,
    high_ptr: *const f64,
    low_ptr: *const f64,
    close_ptr: *const f64,
    len: usize,
) -> Result<Vec<i32>, TA_RetCode> {
    let mut out_begin: TA_Integer = 0;
    let mut out_size: TA_Integer = 0;
    let begin_idx = check_begin_idx4(len, open_ptr, high_ptr, low_ptr, close_ptr) as i32;
    let end_idx = len as i32 - begin_idx - 1;
    let lookback = begin_idx + unsafe { TA_CDLMATCHINGLOW_Lookback() };
    let (mut out, ptr) = make_vec(len, lookback);
    let ret_code = unsafe {
        TA_CDLMATCHINGLOW(
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
                unsafe { out.set_len(out_size_begin) }
            } else {
                unsafe { out.set_len(len) }
            }
            Ok(out)
        }
        _ => Err(ret_code),
    }
}

pub fn ta_cdlmathold(
    open_ptr: *const f64,
    high_ptr: *const f64,
    low_ptr: *const f64,
    close_ptr: *const f64,
    len: usize,
    kwargs: &CDLKwargs,
) -> Result<Vec<i32>, TA_RetCode> {
    let mut out_begin: TA_Integer = 0;
    let mut out_size: TA_Integer = 0;
    let begin_idx = check_begin_idx4(len, open_ptr, high_ptr, low_ptr, close_ptr) as i32;
    let end_idx = len as i32 - begin_idx - 1;
    let lookback = begin_idx + unsafe { TA_CDLMATHOLD_Lookback(kwargs.penetration) };
    let (mut out, ptr) = make_vec(len, lookback);
    let ret_code = unsafe {
        TA_CDLMATHOLD(
            0,
            end_idx,
            open_ptr.offset(begin_idx as isize),
            high_ptr.offset(begin_idx as isize),
            low_ptr.offset(begin_idx as isize),
            close_ptr.offset(begin_idx as isize),
            kwargs.penetration,
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

pub fn ta_cdlmorningdojistar(
    open_ptr: *const f64,
    high_ptr: *const f64,
    low_ptr: *const f64,
    close_ptr: *const f64,
    len: usize,
    kwargs: &CDLKwargs,
) -> Result<Vec<i32>, TA_RetCode> {
    let mut out_begin: TA_Integer = 0;
    let mut out_size: TA_Integer = 0;
    let begin_idx = check_begin_idx4(len, open_ptr, high_ptr, low_ptr, close_ptr) as i32;
    let end_idx = len as i32 - begin_idx - 1;
    let lookback = begin_idx + unsafe { TA_CDLMORNINGDOJISTAR_Lookback(kwargs.penetration) };
    let (mut out, ptr) = make_vec(len, lookback);
    let ret_code = unsafe {
        TA_CDLMORNINGDOJISTAR(
            0,
            end_idx,
            open_ptr.offset(begin_idx as isize),
            high_ptr.offset(begin_idx as isize),
            low_ptr.offset(begin_idx as isize),
            close_ptr.offset(begin_idx as isize),
            kwargs.penetration,
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

pub fn ta_cdlmorningstar(
    open_ptr: *const f64,
    high_ptr: *const f64,
    low_ptr: *const f64,
    close_ptr: *const f64,
    len: usize,
    kwargs: &CDLKwargs,
) -> Result<Vec<i32>, TA_RetCode> {
    let mut out_begin: TA_Integer = 0;
    let mut out_size: TA_Integer = 0;
    let begin_idx = check_begin_idx4(len, open_ptr, high_ptr, low_ptr, close_ptr) as i32;
    let end_idx = len as i32 - begin_idx - 1;
    let lookback = begin_idx + unsafe { TA_CDLMORNINGSTAR_Lookback(kwargs.penetration) };
    let (mut out, ptr) = make_vec(len, lookback);

    let ret_code = unsafe {
        TA_CDLMORNINGSTAR(
            0,
            end_idx,
            open_ptr.offset(begin_idx as isize),
            high_ptr.offset(begin_idx as isize),
            low_ptr.offset(begin_idx as isize),
            close_ptr.offset(begin_idx as isize),
            kwargs.penetration,
            &mut out_begin,
            &mut out_size,
            ptr,
        )
    };
    let out_size_begin = (begin_idx + out_begin + out_size) as usize;
    match ret_code {
        TA_RetCode::TA_SUCCESS => {
            if out_size != 0 {
                unsafe { out.set_len(out_size_begin) };
            } else {
                unsafe { out.set_len(len) };
            }
            Ok(out)
        }
        _ => Err(ret_code),
    }
}

pub fn ta_cdlonneck(
    open_ptr: *const f64,
    high_ptr: *const f64,
    low_ptr: *const f64,
    close_ptr: *const f64,
    len: usize,
) -> Result<Vec<i32>, TA_RetCode> {
    let mut out_begin: TA_Integer = 0;
    let mut out_size: TA_Integer = 0;

    let begin_idx = check_begin_idx4(len, open_ptr, high_ptr, low_ptr, close_ptr) as i32;
    let end_idx = len as i32 - begin_idx - 1;
    let lookback = begin_idx + unsafe { TA_CDLONNECK_Lookback() };
    let (mut out, ptr) = make_vec(len, lookback);

    let ret_code = unsafe {
        TA_CDLONNECK(
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
                unsafe { out.set_len(out_size_begin) }
            } else {
                unsafe { out.set_len(len) }
            }
            Ok(out)
        }
        _ => Err(ret_code),
    }
}

pub fn ta_cdlpiercing(
    open_ptr: *const f64,
    high_ptr: *const f64,
    low_ptr: *const f64,
    close_ptr: *const f64,
    len: usize,
) -> Result<Vec<i32>, TA_RetCode> {
    let mut out_begin: TA_Integer = 0;
    let mut out_size: TA_Integer = 0;

    let begin_idx = check_begin_idx4(len, open_ptr, high_ptr, low_ptr, close_ptr) as i32;
    let end_idx = len as i32 - begin_idx - 1;
    let lookback = begin_idx + unsafe { TA_CDLPIERCING_Lookback() };
    let (mut out, ptr) = make_vec(len, lookback);

    let ret_code = unsafe {
        TA_CDLPIERCING(
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
                unsafe { out.set_len(out_size_begin) };
            } else {
                unsafe { out.set_len(len) };
            }

            Ok(out)
        }
        _ => Err(ret_code),
    }
}

pub fn ta_cdlrickshawman(
    open_ptr: *const f64,
    high_ptr: *const f64,
    low_ptr: *const f64,
    close_ptr: *const f64,
    len: usize,
) -> Result<Vec<i32>, TA_RetCode> {
    let mut out_begin: TA_Integer = 0;
    let mut out_size: TA_Integer = 0;

    let begin_idx = check_begin_idx4(len, open_ptr, high_ptr, low_ptr, close_ptr) as i32;
    let end_idx = len as i32 - begin_idx - 1;
    let lookback = begin_idx + unsafe { TA_CDLRICKSHAWMAN_Lookback() };
    let (mut out, ptr) = make_vec(len, lookback);
    let ret_code = unsafe {
        TA_CDLRICKSHAWMAN(
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
                unsafe { out.set_len(out_size_begin) };
            } else {
                unsafe { out.set_len(len) };
            }
            Ok(out)
        }
        _ => Err(ret_code),
    }
}

pub fn ta_cdlrisefall3methods(
    open_ptr: *const f64,
    high_ptr: *const f64,
    low_ptr: *const f64,
    close_ptr: *const f64,
    len: usize,
) -> Result<Vec<i32>, TA_RetCode> {
    let mut out_begin: TA_Integer = 0;

    let mut out_size: TA_Integer = 0;

    let begin_idx = check_begin_idx4(len, open_ptr, high_ptr, low_ptr, close_ptr) as i32;
    let end_idx = len as i32 - 1 - begin_idx;

    let lookback = begin_idx + unsafe { TA_CDLRISEFALL3METHODS_Lookback() };

    let (mut out, ptr) = make_vec(len, lookback);

    let ret_code = unsafe {
        TA_CDLRISEFALL3METHODS(
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
                unsafe { out.set_len(out_size_begin) };
            } else {
                unsafe { out.set_len(len) };
            }

            Ok(out)
        }
        _ => Err(ret_code),
    }
}

pub fn ta_cdlseparatinglines(
    open_ptr: *const f64,
    high_ptr: *const f64,
    low_ptr: *const f64,
    close_ptr: *const f64,

    len: usize,
) -> Result<Vec<i32>, TA_RetCode> {
    let mut out_begin: TA_Integer = 0;

    let mut out_size: TA_Integer = 0;

    let begin_idx = check_begin_idx4(len, open_ptr, high_ptr, low_ptr, close_ptr) as i32;
    let end_idx = len as i32 - begin_idx - 1;
    let lookback = begin_idx + unsafe { TA_CDLSEPARATINGLINES_Lookback() };

    let (mut out, ptr) = make_vec(len, lookback);

    let ret_code = unsafe {
        TA_CDLSEPARATINGLINES(
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

    // println!("out_begin: {}", out_begin);
    // println!("out_size: {}", out_size);

    let out_size_begin = (begin_idx + out_begin + out_size) as usize;

    // println!("out_size: {}", out_size);

    match ret_code {
        TA_RetCode::TA_SUCCESS => {
            // println!("out_size: {}", out_size);

            if out_size != 0 {
                unsafe { out.set_len(out_size_begin) };
            } else {
                unsafe { out.set_len(len) };
                // println!("out.len(): {}", out.len());
            }

            Ok(out)
        }
        _ => Err(ret_code),
    }
}

pub fn ta_cdlshootingstar(
    open_ptr: *const f64,
    high_ptr: *const f64,
    low_ptr: *const f64,
    close_ptr: *const f64,

    len: usize,
) -> Result<Vec<i32>, TA_RetCode> {
    let mut out_begin: TA_Integer = 0;

    let mut out_size: TA_Integer = 0;

    let begin_idx = check_begin_idx4(len, open_ptr, high_ptr, low_ptr, close_ptr) as i32;
    let end_idx = len as i32 - begin_idx - 1;
    let lookback = begin_idx + unsafe { TA_CDLSHOOTINGSTAR_Lookback() };

    let (mut out, ptr) = make_vec(len, lookback);

    let ret_code = unsafe {
        TA_CDLSHOOTINGSTAR(
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

    // println!("out_begin: {}", out_begin);
    // println!("out_size: {}", out_size);

    let out_size_begin = (begin_idx + out_begin + out_size) as usize;

    // println!("out_size: {}", out_size);

    match ret_code {
        TA_RetCode::TA_SUCCESS => {
            // println!("out_size: {}", out_size);

            if out_size != 0 {
                unsafe { out.set_len(out_size_begin) };
            } else {
                unsafe { out.set_len(len) };
                // println!("out.len(): {}", out.len());
            }

            Ok(out)
        }
        _ => Err(ret_code),
    }
}

pub fn ta_cdlshortline(
    open_ptr: *const f64,
    high_ptr: *const f64,
    low_ptr: *const f64,
    close_ptr: *const f64,

    len: usize,
) -> Result<Vec<i32>, TA_RetCode> {
    let mut out_begin: TA_Integer = 0;
    let mut out_size: TA_Integer = 0;
    let begin_idx = check_begin_idx4(len, open_ptr, high_ptr, low_ptr, close_ptr) as i32;
    let end_idx = len as i32 - begin_idx - 1;
    let lookback = begin_idx + unsafe { TA_CDLSHORTLINE_Lookback() };
    let (mut out, ptr) = make_vec(len, lookback);
    let ret_code = unsafe {
        TA_CDLSHORTLINE(
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
                unsafe { out.set_len(out_size_begin) };
            } else {
                unsafe { out.set_len(len) };
                // println!("out.len(): {}", out.len());
            }

            Ok(out)
        }
        _ => Err(ret_code),
    }
}

pub fn ta_cdlspinningtop(
    open_ptr: *const f64,
    high_ptr: *const f64,
    low_ptr: *const f64,
    close_ptr: *const f64,

    len: usize,
) -> Result<Vec<i32>, TA_RetCode> {
    let mut out_begin: TA_Integer = 0;
    let mut out_size: TA_Integer = 0;
    let begin_idx = check_begin_idx4(len, open_ptr, high_ptr, low_ptr, close_ptr) as i32;
    let end_idx = len as i32 - begin_idx - 1;
    let lookback = begin_idx + unsafe { TA_CDLSPINNINGTOP_Lookback() };
    let (mut out, ptr) = make_vec(len, lookback);
    let ret_code = unsafe {
        TA_CDLSPINNINGTOP(
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
                unsafe { out.set_len(out_size_begin) };
            } else {
                unsafe { out.set_len(len) };
                // println!("out.len(): {}", out.len());
            }

            Ok(out)
        }
        _ => Err(ret_code),
    }
}

pub fn ta_cdlstalledpattern(
    open_ptr: *const f64,
    high_ptr: *const f64,
    low_ptr: *const f64,
    close_ptr: *const f64,

    len: usize,
) -> Result<Vec<i32>, TA_RetCode> {
    let mut out_begin: TA_Integer = 0;
    let mut out_size: TA_Integer = 0;
    let begin_idx = check_begin_idx4(len, open_ptr, high_ptr, low_ptr, close_ptr) as i32;
    let end_idx = len as i32 - begin_idx - 1;
    let lookback = begin_idx + unsafe { TA_CDLSTALLEDPATTERN_Lookback() };
    let (mut out, ptr) = make_vec(len, lookback);
    let ret_code = unsafe {
        TA_CDLSTALLEDPATTERN(
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
                unsafe { out.set_len(out_size_begin) };
            } else {
                unsafe { out.set_len(len) };
                // println!("out.len(): {}", out.len());
            }

            Ok(out)
        }
        _ => Err(ret_code),
    }
}

pub fn ta_cdlsticksandwich(
    open_ptr: *const f64,
    high_ptr: *const f64,
    low_ptr: *const f64,
    close_ptr: *const f64,

    len: usize,
) -> Result<Vec<i32>, TA_RetCode> {
    let mut out_begin: TA_Integer = 0;
    let mut out_size: TA_Integer = 0;
    let begin_idx = check_begin_idx4(len, open_ptr, high_ptr, low_ptr, close_ptr) as i32;
    let end_idx = len as i32 - begin_idx - 1;
    let lookback = begin_idx + unsafe { TA_CDLSTICKSANDWICH_Lookback() };
    let (mut out, ptr) = make_vec(len, lookback);
    let ret_code = unsafe {
        TA_CDLSTICKSANDWICH(
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
                unsafe { out.set_len(out_size_begin) };
            } else {
                unsafe { out.set_len(len) };
                // println!("out.len(): {}", out.len());
            }

            Ok(out)
        }
        _ => Err(ret_code),
    }
}

pub fn ta_cdltakuri(
    open_ptr: *const f64,
    high_ptr: *const f64,
    low_ptr: *const f64,
    close_ptr: *const f64,

    len: usize,
) -> Result<Vec<i32>, TA_RetCode> {
    let mut out_begin: TA_Integer = 0;
    let mut out_size: TA_Integer = 0;
    let begin_idx = check_begin_idx4(len, open_ptr, high_ptr, low_ptr, close_ptr) as i32;
    let end_idx = len as i32 - begin_idx - 1;
    let lookback = begin_idx + unsafe { TA_CDLTAKURI_Lookback() };
    let (mut out, ptr) = make_vec(len, lookback);
    let ret_code = unsafe {
        TA_CDLTAKURI(
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
    // println!("out_begin: {}", out_begin);
    // println!("out_size: {}", out_size);

    match ret_code {
        TA_RetCode::TA_SUCCESS => {
            // println!("out_size: {}", out_size);

            if out_size != 0 {
                unsafe { out.set_len(out_size_begin) };
            } else {
                unsafe { out.set_len(len) };
                // println!("out.len(): {}", out.len());
            }

            Ok(out)
        }
        _ => Err(ret_code),
    }
}

pub fn ta_cdltasukigap(
    open_ptr: *const f64,
    high_ptr: *const f64,
    low_ptr: *const f64,
    close_ptr: *const f64,

    len: usize,
) -> Result<Vec<i32>, TA_RetCode> {
    let mut out_begin: TA_Integer = 0;
    let mut out_size: TA_Integer = 0;
    let begin_idx = check_begin_idx4(len, open_ptr, high_ptr, low_ptr, close_ptr) as i32;
    let end_idx = len as i32 - begin_idx - 1;
    let lookback = begin_idx + unsafe { TA_CDLTASUKIGAP_Lookback() };
    let (mut out, ptr) = make_vec(len, lookback);
    let ret_code = unsafe {
        TA_CDLTASUKIGAP(
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

    // println!("out_begin: {}", out_begin);
    // println!("out_size: {}", out_size);

    match ret_code {
        TA_RetCode::TA_SUCCESS => {
            // println!("out_size: {}", out_size);

            if out_size != 0 {
                unsafe { out.set_len(out_size_begin) };
            } else {
                unsafe { out.set_len(len) };

                // println!("out.len(): {}", out.len());
            }

            Ok(out)
        }
        _ => Err(ret_code),
    }
}

pub fn ta_cdlthrusting(
    open_ptr: *const f64,
    high_ptr: *const f64,
    low_ptr: *const f64,
    close_ptr: *const f64,
    len: usize,
) -> Result<Vec<i32>, TA_RetCode> {
    let mut out_begin: TA_Integer = 0;
    let mut out_size: TA_Integer = 0;
    let begin_idx = check_begin_idx4(len, open_ptr, high_ptr, low_ptr, close_ptr) as i32;
    let end_idx = len as i32 - begin_idx - 1;
    let lookback = begin_idx + unsafe { TA_CDLTHRUSTING_Lookback() };
    let (mut out, ptr) = make_vec(len, lookback);
    let ret_code = unsafe {
        TA_CDLTHRUSTING(
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

    // println!("out_begin: {}", out_begin);
    // println!("out_size: {}", out_size);

    match ret_code {
        TA_RetCode::TA_SUCCESS => {
            // println!("out_size: {}", out_size);

            if out_size != 0 {
                unsafe { out.set_len(out_size_begin) };
            } else {
                unsafe { out.set_len(len) };

                // println!("out.len(): {}", out.len());
            }

            Ok(out)
        }
        _ => Err(ret_code),
    }
}

pub fn ta_cdltristar(
    open_ptr: *const f64,
    high_ptr: *const f64,
    low_ptr: *const f64,
    close_ptr: *const f64,
    len: usize,
) -> Result<Vec<i32>, TA_RetCode> {
    let mut out_begin: TA_Integer = 0;
    let mut out_size: TA_Integer = 0;
    let begin_idx = check_begin_idx4(len, open_ptr, high_ptr, low_ptr, close_ptr) as i32;
    let end_idx = len as i32 - begin_idx - 1;
    let lookback = begin_idx + unsafe { TA_CDLTRISTAR_Lookback() };
    let (mut out, ptr) = make_vec(len, lookback);
    let ret_code = unsafe {
        TA_CDLTRISTAR(
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

    // println!("out_begin: {}", out_begin);
    // println!("out_size: {}", out_size);

    match ret_code {
        TA_RetCode::TA_SUCCESS => {
            // println!("out_size: {}", out_size);

            if out_size != 0 {
                unsafe { out.set_len(out_size_begin) };
            } else {
                unsafe { out.set_len(len) };

                // println!("out.len(): {}", out.len());
            }

            Ok(out)
        }
        _ => Err(ret_code),
    }
}

pub fn ta_cdlunique3river(
    open_ptr: *const f64,
    high_ptr: *const f64,
    low_ptr: *const f64,
    close_ptr: *const f64,
    len: usize,
) -> Result<Vec<i32>, TA_RetCode> {
    let mut out_begin: TA_Integer = 0;
    let mut out_size: TA_Integer = 0;
    let begin_idx = check_begin_idx4(len, open_ptr, high_ptr, low_ptr, close_ptr) as i32;
    let end_idx = len as i32 - begin_idx - 1;
    let lookback = begin_idx + unsafe { TA_CDLUNIQUE3RIVER_Lookback() };
    let (mut out, ptr) = make_vec(len, lookback);
    let ret_code = unsafe {
        TA_CDLUNIQUE3RIVER(
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
                unsafe { out.set_len(out_size_begin) };
            } else {
                unsafe { out.set_len(len) };
            }

            Ok(out)
        }
        _ => Err(ret_code),
    }
}

pub fn ta_cdlupsidegap2crows(
    open_ptr: *const f64,
    high_ptr: *const f64,
    low_ptr: *const f64,
    close_ptr: *const f64,

    len: usize,
) -> Result<Vec<i32>, TA_RetCode> {
    let mut out_begin: TA_Integer = 0;
    let mut out_size: TA_Integer = 0;
    let begin_idx = check_begin_idx4(len, open_ptr, high_ptr, low_ptr, close_ptr) as i32;
    let end_idx = len as i32 - begin_idx - 1;
    let lookback = begin_idx + unsafe { TA_CDLUPSIDEGAP2CROWS_Lookback() };
    let (mut out, ptr) = make_vec(len, lookback);
    let ret_code = unsafe {
        TA_CDLUPSIDEGAP2CROWS(
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
                unsafe { out.set_len(out_size_begin) };
            } else {
                unsafe { out.set_len(len) };
            }

            Ok(out)
        }
        _ => Err(ret_code),
    }
}

pub fn ta_cdlxsidegap3methods(
    open_ptr: *const f64,
    high_ptr: *const f64,
    low_ptr: *const f64,
    close_ptr: *const f64,

    len: usize,
) -> Result<Vec<i32>, TA_RetCode> {
    let mut out_begin: TA_Integer = 0;
    let mut out_size: TA_Integer = 0;
    let begin_idx = check_begin_idx4(len, open_ptr, high_ptr, low_ptr, close_ptr) as i32;
    let end_idx = len as i32 - begin_idx - 1;
    let lookback = begin_idx + unsafe { TA_CDLXSIDEGAP3METHODS_Lookback() };
    let (mut out, ptr) = make_vec(len, lookback);
    let ret_code = unsafe {
        TA_CDLXSIDEGAP3METHODS(
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
                unsafe { out.set_len(out_size_begin) };
            } else {
                unsafe { out.set_len(len) };
            }

            Ok(out)
        }
        _ => Err(ret_code),
    }
}
