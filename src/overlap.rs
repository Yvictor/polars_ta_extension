use polars::prelude::*;
use pyo3_polars::derive::polars_expr;
use serde::Deserialize;
// use std::fmt::Write;
use talib_sys::{TA_BBANDS_Lookback, TA_BBANDS, TA_EMA_Lookback, TA_EMA, TA_Integer, TA_MAType, TA_Real, TA_RetCode};

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
    let input = &mut inputs[0].to_float()?.rechunk();
    let mut out_begin: TA_Integer = 0;
    let mut out_size: TA_Integer = 0;
    let mut outrealupperband: Vec<TA_Real> = Vec::with_capacity(input.len());
    let mut outrealmiddleband: Vec<TA_Real> = Vec::with_capacity(input.len());
    let mut outreallowerband: Vec<TA_Real> = Vec::with_capacity(input.len());
    let input_ptr: *const f64 = if input.has_validity() {
        let input: Vec<f64> = input
            .f64()?
            .into_iter()
            .map(|x| x.unwrap_or(std::f64::NAN))
            .collect();
        input.as_ptr()
    } else {
        input.as_single_ptr()? as *const f64
    };
    let lookback = unsafe {
        TA_BBANDS_Lookback(
            kwargs.timeperiod,
            kwargs.nbdevup,
            kwargs.nbdevdn,
            kwargs.matype,
        ) as usize
    };
    for _ in 0..lookback {
        outrealupperband.push(std::f64::NAN);
        outrealmiddleband.push(std::f64::NAN);
        outreallowerband.push(std::f64::NAN);
    }
    let ret_code = unsafe {
        TA_BBANDS(
            0,
            input.len() as i32 - 1,
            input_ptr,
            kwargs.timeperiod,
            kwargs.nbdevup,
            kwargs.nbdevdn,
            kwargs.matype,
            &mut out_begin,
            &mut out_size,
            outrealupperband[lookback..].as_mut_ptr(),
            outrealmiddleband[lookback..].as_mut_ptr(),
            outreallowerband[lookback..].as_mut_ptr(),
        )
    };
    match ret_code {
        TA_RetCode::TA_SUCCESS => {
            unsafe {
                outrealupperband.set_len((out_begin + out_size) as usize);
                outrealmiddleband.set_len((out_begin + out_size) as usize);
                outreallowerband.set_len((out_begin + out_size) as usize);
            }
            // let out_ser = Float64Chunked::from_vec("", outreallowerband);
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
    let input = &mut inputs[0].to_float()?;//.rechunk();
    let mut out_begin: TA_Integer = 0;
    let mut out_size: TA_Integer = 0;
    let mut out: Vec<TA_Real> = Vec::with_capacity(input.len());
    let input_vec: Vec<f64>;
    println!("has_validity: {}", input.has_validity());
    println!("len: {}", input.len());
    println!("null_count: {}", input.null_count());
    let input_ptr: *const f64 = if input.has_validity() {
        input_vec = input
            .f64()?
            .into_iter()
            .map(|x| x.unwrap_or(std::f64::NAN))
            .collect();

        input_vec.as_ptr()
    } else {
        // input_vec = vec![];
        input.as_single_ptr()? as *const f64
    };
    // let ca = input.f64()?;
    // let r: Float64Chunked = ca.apply_generic(|x| {
    //     print!("{},", x.unwrap_or(std::f64::NAN));
    //     x
    // });
    // // input_ca.apply_generic(|x| {
    // //     if let Some(x) = x {
    // //         None
    // //     } else {
    // //         None
    // //     }
    // // });
    let lookback = unsafe { TA_EMA_Lookback(kwargs.timeperiod) as usize };
    for _ in 0..lookback {
        out.push(std::f64::NAN);
    }
    // println!("vec: [");
    // for i in input_vec {
    //     print!("{}, ", i)
    // }
    // println!("]");
    let ret_code = unsafe {
        TA_EMA(
            0,
            input.len() as i32 - 1,
            input_ptr,
            kwargs.timeperiod,
            &mut out_begin,
            &mut out_size,
            out[lookback..].as_mut_ptr(),
        )
    };
    match ret_code {
        TA_RetCode::TA_SUCCESS => {
            unsafe {
                out.set_len((out_begin + out_size) as usize);
            }
            let out_ser = Float64Chunked::from_vec("", out);
            Ok(out_ser.into_series())
        }
        _ => Err(PolarsError::ComputeError(
            format!("Could not compute indicator, err: {:?}", ret_code).into(),
        )),
    }
}