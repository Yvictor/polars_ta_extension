use crate::utils::make_vec;
use serde::Deserialize;
use talib_sys::{
    TA_BBANDS_Lookback, TA_EMA_Lookback, TA_Integer, TA_MAType, TA_RetCode, TA_BBANDS, TA_EMA,
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
    let lookback = unsafe {
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
            len as i32 - 1,
            real_ptr,
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
    let out_size = (out_begin + out_size) as usize;
    match ret_code {
        TA_RetCode::TA_SUCCESS => {
            if out_size != 0 {
                unsafe {
                    outrealupperband.set_len(out_size);
                    outrealmiddleband.set_len(out_size);
                    outreallowerband.set_len(out_size);
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

#[derive(Deserialize)]
pub struct EMAKwargs {
    timeperiod: i32,
}

pub fn ta_ema(
    real_ptr: *const f64,
    len: usize,
    kwargs: &EMAKwargs,
) -> Result<Vec<f64>, TA_RetCode> {
    let mut out_begin: TA_Integer = 0;
    let mut out_size: TA_Integer = 0;
    let lookback = unsafe { TA_EMA_Lookback(kwargs.timeperiod) };
    let (mut out, ptr) = make_vec(len, lookback);
    let ret_code = unsafe {
        TA_EMA(
            0,
            len as i32 - 1,
            real_ptr,
            kwargs.timeperiod,
            &mut out_begin,
            &mut out_size,
            ptr,
        )
    };
    match ret_code {
        TA_RetCode::TA_SUCCESS => {
            let out_size = (out_begin + out_size) as usize;
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
