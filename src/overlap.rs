use crate::utils::{get_series_f64_ptr, make_vec};
use polars::prelude::*;
use pyo3_polars::derive::polars_expr;
use serde::Deserialize;
use talib_sys::{
    TA_BBANDS_Lookback, TA_EMA_Lookback, TA_Integer, TA_MAType, TA_RetCode, TA_BBANDS,
    TA_EMA,
};

#[derive(Deserialize)]
pub struct BBANDSKwargs {
    timeperiod: i32,
    nbdevup: f64,
    nbdevdn: f64,
    matype: TA_MAType,
}

pub fn bbands_output(_: &[Field]) -> PolarsResult<Field> {
    let u = Field::new("upperband", DataType::Float64);
    let m = Field::new("middleband", DataType::Float64);
    let l = Field::new("lowerband", DataType::Float64);
    let v: Vec<Field> = vec![u, m, l];
    Ok(Field::new("", DataType::Struct(v)))
}

#[polars_expr(output_type_func=bbands_output)]
fn bbands(inputs: &[Series], kwargs: BBANDSKwargs) -> PolarsResult<Series> {
    let mut out_begin: TA_Integer = 0;
    let mut out_size: TA_Integer = 0;
    let input = &mut inputs[0].to_float()?.rechunk();
    let (input_ptr, _input) = get_series_f64_ptr(input)?;
    let len = input.len();
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
            input_ptr,
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
    match ret_code {
        TA_RetCode::TA_SUCCESS => {
            let out_size = (out_begin + out_size) as usize;
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
            let u = Series::from_vec("upperband", outrealupperband);
            let m = Series::from_vec("middleband", outrealmiddleband);
            let l = Series::from_vec("lowerband", outreallowerband);
            let out = StructChunked::new("", &[u, m, l])?;
            Ok(out.into_series())
        }
        _ => Err(PolarsError::ComputeError(
            format!("Could not compute indicator, err: {:?}", ret_code).into(),
        )),
    }
}

#[derive(Deserialize)]
pub struct EMAKwargs {
    timeperiod: i32,
}

#[polars_expr(output_type=Float64)]
fn ema(inputs: &[Series], kwargs: EMAKwargs) -> PolarsResult<Series> {
    let mut out_begin: TA_Integer = 0;
    let mut out_size: TA_Integer = 0;
    // println!("has_validity: {}", input.has_validity());
    // println!("len: {}", input.len());
    // println!("null_count: {}", input.null_count());
    let input = &mut inputs[0].to_float()?.rechunk();
    let (input_ptr, _input) = get_series_f64_ptr(input)?;
    let len = input.len();
    let lookback = unsafe { TA_EMA_Lookback(kwargs.timeperiod) };
    let (mut out, ptr) = make_vec(len , lookback);
    let ret_code = unsafe {
        TA_EMA(
            0,
            len as i32 - 1,
            input_ptr,
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
            let out_ser = Float64Chunked::from_vec("", out);
            Ok(out_ser.into_series())
        }
        _ => Err(PolarsError::ComputeError(
            format!("Could not compute indicator, err: {:?}", ret_code).into(),
        )),
    }
}
