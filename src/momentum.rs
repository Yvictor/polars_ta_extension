use crate::utils::{cast_series_to_f64, get_series_f64_ptr, ta_code2err};
use polars::prelude::*;
use pyo3_polars::derive::polars_expr;
use talib::common::TimePeriodKwargs;
use talib::momentum::{
    ta_adx, ta_adxr, ta_apo, ta_aroon, ta_aroonosc, ta_bop, ta_cci, ta_cmo, ta_dx, ta_macd,
    ta_macdext, ta_macdfix, ta_mfi, ta_minus_di, ta_minus_dm, ta_mom, ta_plus_di, ta_plus_dm,
    ta_ppo, ta_roc, ta_rocp, ta_rocr, ta_rocr100, ta_rsi, ta_stoch, ta_stochf, ta_stochrsi,
    ta_trix, ta_ultosc, ta_willr,
};
use talib::momentum::{
    ApoKwargs, MacdExtKwargs, MacdFixKwargs, MacdKwargs, PpoKwargs, StochKwargs, StochRsiKwargs,
    StochfKwargs, UltOscKwargs,
};
use talib::momentum::{ta_ac, AcKwargs};
use talib::momentum::{ta_ao, AoKwargs};
use talib::momentum::{ta_cmou};
use talib::momentum::{ta_coppock, CoppockKwargs};
use talib::momentum::{ta_dpo};
use talib::momentum::{ta_er};
use talib::momentum::{ta_eri};
use talib::momentum::{ta_fosc};
use talib::momentum::{ta_fractal, FractalKwargs};
use talib::momentum::{ta_imi};
use talib::momentum::{ta_kdj, KdjKwargs};
use talib::momentum::{ta_qstick};
use talib::momentum::{ta_smi, SmiKwargs};
use talib::momentum::{ta_tsi, TsiKwargs};
use talib::momentum::{ta_vhf};
use talib::momentum::{ta_vortex};
use talib::momentum::{ta_wad};

#[polars_expr(output_type=Float64)]
fn adx(inputs: &[Series], kwargs: TimePeriodKwargs) -> PolarsResult<Series> {
    let high = &mut cast_series_to_f64(&inputs[1])?;
    let low = &mut cast_series_to_f64(&inputs[2])?;
    let close = &mut cast_series_to_f64(&inputs[0])?;
    let (high_ptr, _high) = get_series_f64_ptr(high)?;
    let (low_ptr, _low) = get_series_f64_ptr(low)?;
    let (close_ptr, _close) = get_series_f64_ptr(close)?;
    let len = close.len();
    let res = ta_adx(high_ptr, low_ptr, close_ptr, len, &kwargs);
    match res {
        Ok(out) => Ok(Float64Chunked::from_vec("", out).into_series()),
        Err(ret_code) => ta_code2err(ret_code),
    }
}

#[polars_expr(output_type=Float64)]
fn adxr(inputs: &[Series], kwargs: TimePeriodKwargs) -> PolarsResult<Series> {
    let high = &mut cast_series_to_f64(&inputs[1])?;
    let low = &mut cast_series_to_f64(&inputs[2])?;
    let close = &mut cast_series_to_f64(&inputs[0])?;
    let (high_ptr, _high) = get_series_f64_ptr(high)?;
    let (low_ptr, _low) = get_series_f64_ptr(low)?;
    let (close_ptr, _close) = get_series_f64_ptr(close)?;
    let len = close.len();
    let res = ta_adxr(high_ptr, low_ptr, close_ptr, len, &kwargs);
    match res {
        Ok(out) => Ok(Float64Chunked::from_vec("", out).into_series()),
        Err(ret_code) => ta_code2err(ret_code),
    }
}

#[polars_expr(output_type=Float64)]
fn apo(inputs: &[Series], kwargs: ApoKwargs) -> PolarsResult<Series> {
    let input = &mut cast_series_to_f64(&inputs[0])?;
    let (input_ptr, _input) = get_series_f64_ptr(input)?;
    let len = input.len();
    let res = ta_apo(input_ptr, len, &kwargs);
    match res {
        Ok(out) => Ok(Float64Chunked::from_vec("", out).into_series()),
        Err(ret_code) => ta_code2err(ret_code),
    }
}

pub fn arron_output(_: &[Field]) -> PolarsResult<Field> {
    let d = Field::new("aroondown", DataType::Float64);
    let u = Field::new("aroonup", DataType::Float64);
    let v: Vec<Field> = vec![d, u];
    Ok(Field::new("", DataType::Struct(v)))
}

#[polars_expr(output_type_func=arron_output)]
fn aroon(inputs: &[Series], kwargs: TimePeriodKwargs) -> PolarsResult<Series> {
    let high = &mut cast_series_to_f64(&inputs[0])?;
    let low = &mut cast_series_to_f64(&inputs[1])?;
    let (high_ptr, _high) = get_series_f64_ptr(high)?;
    let (low_ptr, _low) = get_series_f64_ptr(low)?;
    let len = high.len();
    let res = ta_aroon(high_ptr, low_ptr, len, &kwargs);
    match res {
        Ok((outaroondown, outaroonup)) => {
            let d = Series::from_vec("aroondown", outaroondown);
            let u = Series::from_vec("aroonup", outaroonup);
            let out = StructChunked::new("", &[d, u])?;
            Ok(out.into_series())
        }
        Err(ret_code) => ta_code2err(ret_code),
    }
}

#[polars_expr(output_type=Float64)]
fn aroonosc(inputs: &[Series], kwargs: TimePeriodKwargs) -> PolarsResult<Series> {
    let high = &mut cast_series_to_f64(&inputs[0])?;
    let low = &mut cast_series_to_f64(&inputs[1])?;
    let (high_ptr, _high) = get_series_f64_ptr(high)?;
    let (low_ptr, _low) = get_series_f64_ptr(low)?;
    let len = high.len();
    let res = ta_aroonosc(high_ptr, low_ptr, len, &kwargs);
    match res {
        Ok(out) => Ok(Float64Chunked::from_vec("", out).into_series()),
        Err(ret_code) => ta_code2err(ret_code),
    }
}

#[polars_expr(output_type=Float64)]
fn bop(inputs: &[Series]) -> PolarsResult<Series> {
    let open = &mut cast_series_to_f64(&inputs[0])?;
    let high = &mut cast_series_to_f64(&inputs[1])?;
    let low = &mut cast_series_to_f64(&inputs[2])?;
    let close = &mut cast_series_to_f64(&inputs[3])?;
    let (open_ptr, _open) = get_series_f64_ptr(open)?;
    let (high_ptr, _high) = get_series_f64_ptr(high)?;
    let (low_ptr, _low) = get_series_f64_ptr(low)?;
    let (close_ptr, _close) = get_series_f64_ptr(close)?;
    let len = close.len();
    let res = ta_bop(open_ptr, high_ptr, low_ptr, close_ptr, len);
    match res {
        Ok(out) => Ok(Float64Chunked::from_vec("", out).into_series()),
        Err(ret_code) => ta_code2err(ret_code),
    }
}

#[polars_expr(output_type=Float64)]
fn cci(inputs: &[Series], kwargs: TimePeriodKwargs) -> PolarsResult<Series> {
    let high = &mut cast_series_to_f64(&inputs[1])?;
    let low = &mut cast_series_to_f64(&inputs[2])?;
    let close = &mut cast_series_to_f64(&inputs[0])?;
    let (high_ptr, _high) = get_series_f64_ptr(high)?;
    let (low_ptr, _low) = get_series_f64_ptr(low)?;
    let (close_ptr, _close) = get_series_f64_ptr(close)?;
    let len = close.len();
    let res = ta_cci(high_ptr, low_ptr, close_ptr, len, &kwargs);
    match res {
        Ok(out) => Ok(Float64Chunked::from_vec("", out).into_series()),
        Err(ret_code) => ta_code2err(ret_code),
    }
}

#[polars_expr(output_type=Float64)]
fn cmo(inputs: &[Series], kwargs: TimePeriodKwargs) -> PolarsResult<Series> {
    let input = &mut cast_series_to_f64(&inputs[0])?;
    let (input_ptr, _input) = get_series_f64_ptr(input)?;
    let len = input.len();
    let res = ta_cmo(input_ptr, len, &kwargs);
    match res {
        Ok(out) => Ok(Float64Chunked::from_vec("", out).into_series()),
        Err(ret_code) => ta_code2err(ret_code),
    }
}

#[polars_expr(output_type=Float64)]
fn dx(inputs: &[Series], kwargs: TimePeriodKwargs) -> PolarsResult<Series> {
    let high = &mut cast_series_to_f64(&inputs[1])?;
    let low = &mut cast_series_to_f64(&inputs[2])?;
    let close = &mut cast_series_to_f64(&inputs[0])?;
    let (high_ptr, _high) = get_series_f64_ptr(high)?;
    let (low_ptr, _low) = get_series_f64_ptr(low)?;
    let (close_ptr, _close) = get_series_f64_ptr(close)?;
    let len = close.len();
    let res = ta_dx(high_ptr, low_ptr, close_ptr, len, &kwargs);
    match res {
        Ok(out) => Ok(Float64Chunked::from_vec("", out).into_series()),
        Err(ret_code) => ta_code2err(ret_code),
    }
}

pub fn macd_output(_: &[Field]) -> PolarsResult<Field> {
    let macd = Field::new("macd", DataType::Float64);
    let macdsignal = Field::new("macdsignal", DataType::Float64);
    let macdhist = Field::new("macdhist", DataType::Float64);
    let v: Vec<Field> = vec![macd, macdsignal, macdhist];
    Ok(Field::new("", DataType::Struct(v)))
}

#[polars_expr(output_type_func=macd_output)]
fn macd(inputs: &[Series], kwargs: MacdKwargs) -> PolarsResult<Series> {
    let input = &mut cast_series_to_f64(&inputs[0])?;
    let (input_ptr, _input) = get_series_f64_ptr(input)?;
    let len = input.len();
    let res = ta_macd(input_ptr, len, &kwargs);
    match res {
        Ok((outmacd, outmacdsignal, outmacdhist)) => {
            let macd = Series::from_vec("macd", outmacd);
            let macdsignal = Series::from_vec("macdsignal", outmacdsignal);
            let macdhist = Series::from_vec("macdhist", outmacdhist);
            let out = StructChunked::new("", &[macd, macdsignal, macdhist])?;
            Ok(out.into_series())
        }
        Err(ret_code) => ta_code2err(ret_code),
    }
}

#[polars_expr(output_type_func=macd_output)]
fn macdext(inputs: &[Series], kwargs: MacdExtKwargs) -> PolarsResult<Series> {
    let input = &mut cast_series_to_f64(&inputs[0])?;
    let (input_ptr, _input) = get_series_f64_ptr(input)?;
    let len = input.len();
    let res = ta_macdext(input_ptr, len, &kwargs);
    match res {
        Ok((outmacd, outmacdsignal, outmacdhist)) => {
            let macd = Series::from_vec("macd", outmacd);
            let macdsignal = Series::from_vec("macdsignal", outmacdsignal);
            let macdhist = Series::from_vec("macdhist", outmacdhist);
            let out = StructChunked::new("", &[macd, macdsignal, macdhist])?;
            Ok(out.into_series())
        }
        Err(ret_code) => ta_code2err(ret_code),
    }
}

#[polars_expr(output_type_func=macd_output)]
fn macdfix(inputs: &[Series], kwargs: MacdFixKwargs) -> PolarsResult<Series> {
    let input = &mut cast_series_to_f64(&inputs[0])?;
    let (input_ptr, _input) = get_series_f64_ptr(input)?;
    let len = input.len();
    let res = ta_macdfix(input_ptr, len, &kwargs);
    match res {
        Ok((outmacd, outmacdsignal, outmacdhist)) => {
            let macd = Series::from_vec("macd", outmacd);
            let macdsignal = Series::from_vec("macdsignal", outmacdsignal);
            let macdhist = Series::from_vec("macdhist", outmacdhist);
            let out = StructChunked::new("", &[macd, macdsignal, macdhist])?;
            Ok(out.into_series())
        }
        Err(ret_code) => ta_code2err(ret_code),
    }
}

#[polars_expr(output_type=Float64)]
fn mfi(inputs: &[Series], kwargs: TimePeriodKwargs) -> PolarsResult<Series> {
    let high = &mut cast_series_to_f64(&inputs[1])?;
    let low = &mut cast_series_to_f64(&inputs[2])?;
    let close = &mut cast_series_to_f64(&inputs[0])?;
    let volume = &mut cast_series_to_f64(&inputs[3])?;
    let (high_ptr, _high) = get_series_f64_ptr(high)?;
    let (low_ptr, _low) = get_series_f64_ptr(low)?;
    let (close_ptr, _close) = get_series_f64_ptr(close)?;
    let (volume_ptr, _volume) = get_series_f64_ptr(volume)?;
    let len = close.len();
    let res = ta_mfi(high_ptr, low_ptr, close_ptr, volume_ptr, len, &kwargs);
    match res {
        Ok(out) => Ok(Float64Chunked::from_vec("", out).into_series()),
        Err(ret_code) => ta_code2err(ret_code),
    }
}

#[polars_expr(output_type=Float64)]
fn minus_di(inputs: &[Series], kwargs: TimePeriodKwargs) -> PolarsResult<Series> {
    let high = &mut cast_series_to_f64(&inputs[1])?;
    let low = &mut cast_series_to_f64(&inputs[2])?;
    let close = &mut cast_series_to_f64(&inputs[0])?;
    let (high_ptr, _high) = get_series_f64_ptr(high)?;
    let (low_ptr, _low) = get_series_f64_ptr(low)?;
    let (close_ptr, _close) = get_series_f64_ptr(close)?;
    let len = close.len();
    let res = ta_minus_di(high_ptr, low_ptr, close_ptr, len, &kwargs);
    match res {
        Ok(out) => Ok(Float64Chunked::from_vec("", out).into_series()),
        Err(ret_code) => ta_code2err(ret_code),
    }
}

#[polars_expr(output_type=Float64)]
fn minus_dm(inputs: &[Series], kwargs: TimePeriodKwargs) -> PolarsResult<Series> {
    let high = &mut cast_series_to_f64(&inputs[0])?;
    let low = &mut cast_series_to_f64(&inputs[1])?;
    let (high_ptr, _high) = get_series_f64_ptr(high)?;
    let (low_ptr, _low) = get_series_f64_ptr(low)?;
    let len = high.len();
    let res = ta_minus_dm(high_ptr, low_ptr, len, &kwargs);
    match res {
        Ok(out) => Ok(Float64Chunked::from_vec("", out).into_series()),
        Err(ret_code) => ta_code2err(ret_code),
    }
}

#[polars_expr(output_type=Float64)]
fn mom(inputs: &[Series], kwargs: TimePeriodKwargs) -> PolarsResult<Series> {
    let input = &mut cast_series_to_f64(&inputs[0])?;
    let (input_ptr, _input) = get_series_f64_ptr(input)?;
    let len = input.len();
    let res = ta_mom(input_ptr, len, &kwargs);
    match res {
        Ok(out) => Ok(Float64Chunked::from_vec("", out).into_series()),
        Err(ret_code) => ta_code2err(ret_code),
    }
}

#[polars_expr(output_type=Float64)]
fn plus_di(inputs: &[Series], kwargs: TimePeriodKwargs) -> PolarsResult<Series> {
    let high = &mut cast_series_to_f64(&inputs[1])?;
    let low = &mut cast_series_to_f64(&inputs[2])?;
    let close = &mut cast_series_to_f64(&inputs[0])?;
    let (high_ptr, _high) = get_series_f64_ptr(high)?;
    let (low_ptr, _low) = get_series_f64_ptr(low)?;
    let (close_ptr, _close) = get_series_f64_ptr(close)?;
    let len = close.len();
    let res = ta_plus_di(high_ptr, low_ptr, close_ptr, len, &kwargs);
    match res {
        Ok(out) => Ok(Float64Chunked::from_vec("", out).into_series()),
        Err(ret_code) => ta_code2err(ret_code),
    }
}

#[polars_expr(output_type=Float64)]
fn plus_dm(inputs: &[Series], kwargs: TimePeriodKwargs) -> PolarsResult<Series> {
    let high = &mut cast_series_to_f64(&inputs[0])?;
    let low = &mut cast_series_to_f64(&inputs[1])?;
    let (high_ptr, _high) = get_series_f64_ptr(high)?;
    let (low_ptr, _low) = get_series_f64_ptr(low)?;
    let len = high.len();
    let res = ta_plus_dm(high_ptr, low_ptr, len, &kwargs);
    match res {
        Ok(out) => Ok(Float64Chunked::from_vec("", out).into_series()),
        Err(ret_code) => ta_code2err(ret_code),
    }
}

#[polars_expr(output_type=Float64)]
fn ppo(inputs: &[Series], kwargs: PpoKwargs) -> PolarsResult<Series> {
    let input = &mut cast_series_to_f64(&inputs[0])?;
    let (input_ptr, _input) = get_series_f64_ptr(input)?;
    let len = input.len();
    let res = ta_ppo(input_ptr, len, &kwargs);
    match res {
        Ok(out) => Ok(Float64Chunked::from_vec("", out).into_series()),
        Err(ret_code) => ta_code2err(ret_code),
    }
}

#[polars_expr(output_type=Float64)]
fn roc(inputs: &[Series], kwargs: TimePeriodKwargs) -> PolarsResult<Series> {
    let input = &mut cast_series_to_f64(&inputs[0])?;
    let (input_ptr, _input) = get_series_f64_ptr(input)?;
    let len = input.len();
    let res = ta_roc(input_ptr, len, &kwargs);
    match res {
        Ok(out) => Ok(Float64Chunked::from_vec("", out).into_series()),
        Err(ret_code) => ta_code2err(ret_code),
    }
}

#[polars_expr(output_type=Float64)]
fn rocp(inputs: &[Series], kwargs: TimePeriodKwargs) -> PolarsResult<Series> {
    let input = &mut cast_series_to_f64(&inputs[0])?;
    let (input_ptr, _input) = get_series_f64_ptr(input)?;
    let len = input.len();
    let res = ta_rocp(input_ptr, len, &kwargs);
    match res {
        Ok(out) => Ok(Float64Chunked::from_vec("", out).into_series()),
        Err(ret_code) => ta_code2err(ret_code),
    }
}

#[polars_expr(output_type=Float64)]
fn rocr(inputs: &[Series], kwargs: TimePeriodKwargs) -> PolarsResult<Series> {
    let input = &mut cast_series_to_f64(&inputs[0])?;
    let (input_ptr, _input) = get_series_f64_ptr(input)?;
    let len = input.len();
    let res = ta_rocr(input_ptr, len, &kwargs);
    match res {
        Ok(out) => Ok(Float64Chunked::from_vec("", out).into_series()),
        Err(ret_code) => ta_code2err(ret_code),
    }
}

#[polars_expr(output_type=Float64)]
fn rocr100(inputs: &[Series], kwargs: TimePeriodKwargs) -> PolarsResult<Series> {
    let input = &mut cast_series_to_f64(&inputs[0])?;
    let (input_ptr, _input) = get_series_f64_ptr(input)?;
    let len = input.len();
    let res = ta_rocr100(input_ptr, len, &kwargs);
    match res {
        Ok(out) => Ok(Float64Chunked::from_vec("", out).into_series()),
        Err(ret_code) => ta_code2err(ret_code),
    }
}

#[polars_expr(output_type=Float64)]
fn rsi(inputs: &[Series], kwargs: TimePeriodKwargs) -> PolarsResult<Series> {
    let input = &mut cast_series_to_f64(&inputs[0])?;
    let (input_ptr, _input) = get_series_f64_ptr(input)?;
    let len = input.len();
    let res = ta_rsi(input_ptr, len, &kwargs);
    match res {
        Ok(out) => Ok(Float64Chunked::from_vec("", out).into_series()),
        Err(ret_code) => ta_code2err(ret_code),
    }
}

pub fn stoch_output(_: &[Field]) -> PolarsResult<Field> {
    let slowk = Field::new("slowk", DataType::Float64);
    let slowd = Field::new("slowd", DataType::Float64);
    let v: Vec<Field> = vec![slowk, slowd];
    Ok(Field::new("", DataType::Struct(v)))
}

#[polars_expr(output_type_func=stoch_output)]
fn stoch(inputs: &[Series], kwargs: StochKwargs) -> PolarsResult<Series> {
    let high = &mut cast_series_to_f64(&inputs[1])?;
    let low = &mut cast_series_to_f64(&inputs[2])?;
    let close = &mut cast_series_to_f64(&inputs[0])?;
    let (high_ptr, _high) = get_series_f64_ptr(high)?;
    let (low_ptr, _low) = get_series_f64_ptr(low)?;
    let (close_ptr, _close) = get_series_f64_ptr(close)?;
    let len = close.len();
    let res = ta_stoch(high_ptr, low_ptr, close_ptr, len, &kwargs);
    match res {
        Ok((outslowk, outslowd)) => {
            let slowk = Series::from_vec("slowk", outslowk);
            let slowd = Series::from_vec("slowd", outslowd);
            let out = StructChunked::new("", &[slowk, slowd])?;
            Ok(out.into_series())
        }
        Err(ret_code) => ta_code2err(ret_code),
    }
}

pub fn stochf_output(_: &[Field]) -> PolarsResult<Field> {
    let fastk = Field::new("fastk", DataType::Float64);
    let fastd = Field::new("fastd", DataType::Float64);
    let v: Vec<Field> = vec![fastk, fastd];
    Ok(Field::new("", DataType::Struct(v)))
}

#[polars_expr(output_type_func=stochf_output)]
fn stochf(inputs: &[Series], kwargs: StochfKwargs) -> PolarsResult<Series> {
    let high = &mut cast_series_to_f64(&inputs[1])?;
    let low = &mut cast_series_to_f64(&inputs[2])?;
    let close = &mut cast_series_to_f64(&inputs[0])?;
    let (high_ptr, _high) = get_series_f64_ptr(high)?;
    let (low_ptr, _low) = get_series_f64_ptr(low)?;
    let (close_ptr, _close) = get_series_f64_ptr(close)?;
    let len = close.len();
    let res = ta_stochf(high_ptr, low_ptr, close_ptr, len, &kwargs);
    match res {
        Ok((outfastk, outfastd)) => {
            let fastk = Series::from_vec("fastk", outfastk);
            let fastd = Series::from_vec("fastd", outfastd);
            let out = StructChunked::new("", &[fastk, fastd])?;
            Ok(out.into_series())
        }
        Err(ret_code) => ta_code2err(ret_code),
    }
}

#[polars_expr(output_type_func=stochf_output)]
fn stochrsi(inputs: &[Series], kwargs: StochRsiKwargs) -> PolarsResult<Series> {
    let input = &mut cast_series_to_f64(&inputs[0])?;
    let (input_ptr, _input) = get_series_f64_ptr(input)?;
    let len = input.len();
    let res = ta_stochrsi(input_ptr, len, &kwargs);
    match res {
        Ok((outfastk, outfastd)) => {
            let fastk = Series::from_vec("fastk", outfastk);
            let fastd = Series::from_vec("fastd", outfastd);
            let out = StructChunked::new("", &[fastk, fastd])?;
            Ok(out.into_series())
        }
        Err(ret_code) => ta_code2err(ret_code),
    }
}

#[polars_expr(output_type=Float64)]
fn trix(inputs: &[Series], kwargs: TimePeriodKwargs) -> PolarsResult<Series> {
    let input = &mut cast_series_to_f64(&inputs[0])?;
    let (input_ptr, _input) = get_series_f64_ptr(input)?;
    let len = input.len();
    let res = ta_trix(input_ptr, len, &kwargs);
    match res {
        Ok(out) => Ok(Float64Chunked::from_vec("", out).into_series()),
        Err(ret_code) => {
            println!("{:?}", ret_code);
            ta_code2err(ret_code)
        }
    }
}

#[polars_expr(output_type=Float64)]
fn ultosc(inputs: &[Series], kwargs: UltOscKwargs) -> PolarsResult<Series> {
    let high = &mut cast_series_to_f64(&inputs[1])?;
    let low = &mut cast_series_to_f64(&inputs[2])?;
    let close = &mut cast_series_to_f64(&inputs[0])?;
    let (high_ptr, _high) = get_series_f64_ptr(high)?;
    let (low_ptr, _low) = get_series_f64_ptr(low)?;
    let (close_ptr, _close) = get_series_f64_ptr(close)?;
    let len = close.len();
    let res = ta_ultosc(high_ptr, low_ptr, close_ptr, len, &kwargs);
    match res {
        Ok(out) => Ok(Float64Chunked::from_vec("", out).into_series()),
        Err(ret_code) => {
            println!("{:?}", ret_code);
            ta_code2err(ret_code)
        }
    }
}

#[polars_expr(output_type=Float64)]
fn willr(inputs: &[Series], kwargs: TimePeriodKwargs) -> PolarsResult<Series> {
    let high = &mut cast_series_to_f64(&inputs[1])?;
    let low = &mut cast_series_to_f64(&inputs[2])?;
    let close = &mut cast_series_to_f64(&inputs[0])?;
    let (high_ptr, _high) = get_series_f64_ptr(high)?;
    let (low_ptr, _low) = get_series_f64_ptr(low)?;
    let (close_ptr, _close) = get_series_f64_ptr(close)?;
    let len = close.len();
    let res = ta_willr(high_ptr, low_ptr, close_ptr, len, &kwargs);
    match res {
        Ok(out) => Ok(Float64Chunked::from_vec("", out).into_series()),
        Err(ret_code) => {
            println!("{:?}", ret_code);
            ta_code2err(ret_code)
        }
    }
}

#[polars_expr(output_type=Float64)]
fn ac(inputs: &[Series], kwargs: AcKwargs) -> PolarsResult<Series> {
    let high = &mut cast_series_to_f64(&inputs[0])?;
    let low = &mut cast_series_to_f64(&inputs[1])?;
    let (high_ptr, _high) = get_series_f64_ptr(high)?;
    let (low_ptr, _low) = get_series_f64_ptr(low)?;
    let len = high.len();
    let res = ta_ac(high_ptr, low_ptr, len, &kwargs);
    match res {
        Ok(out) => Ok(Float64Chunked::from_vec("", out).into_series()),
        Err(ret_code) => ta_code2err(ret_code),
    }
}

#[polars_expr(output_type=Float64)]
fn ao(inputs: &[Series], kwargs: AoKwargs) -> PolarsResult<Series> {
    let high = &mut cast_series_to_f64(&inputs[0])?;
    let low = &mut cast_series_to_f64(&inputs[1])?;
    let (high_ptr, _high) = get_series_f64_ptr(high)?;
    let (low_ptr, _low) = get_series_f64_ptr(low)?;
    let len = high.len();
    let res = ta_ao(high_ptr, low_ptr, len, &kwargs);
    match res {
        Ok(out) => Ok(Float64Chunked::from_vec("", out).into_series()),
        Err(ret_code) => ta_code2err(ret_code),
    }
}

#[polars_expr(output_type=Float64)]
fn cmou(inputs: &[Series], kwargs: TimePeriodKwargs) -> PolarsResult<Series> {
    let real = &mut cast_series_to_f64(&inputs[0])?;
    let (real_ptr, _real) = get_series_f64_ptr(real)?;
    let len = real.len();
    let res = ta_cmou(real_ptr, len, &kwargs);
    match res {
        Ok(out) => Ok(Float64Chunked::from_vec("", out).into_series()),
        Err(ret_code) => ta_code2err(ret_code),
    }
}

#[polars_expr(output_type=Float64)]
fn coppock(inputs: &[Series], kwargs: CoppockKwargs) -> PolarsResult<Series> {
    let real = &mut cast_series_to_f64(&inputs[0])?;
    let (real_ptr, _real) = get_series_f64_ptr(real)?;
    let len = real.len();
    let res = ta_coppock(real_ptr, len, &kwargs);
    match res {
        Ok(out) => Ok(Float64Chunked::from_vec("", out).into_series()),
        Err(ret_code) => ta_code2err(ret_code),
    }
}

#[polars_expr(output_type=Float64)]
fn dpo(inputs: &[Series], kwargs: TimePeriodKwargs) -> PolarsResult<Series> {
    let real = &mut cast_series_to_f64(&inputs[0])?;
    let (real_ptr, _real) = get_series_f64_ptr(real)?;
    let len = real.len();
    let res = ta_dpo(real_ptr, len, &kwargs);
    match res {
        Ok(out) => Ok(Float64Chunked::from_vec("", out).into_series()),
        Err(ret_code) => ta_code2err(ret_code),
    }
}

#[polars_expr(output_type=Float64)]
fn er(inputs: &[Series], kwargs: TimePeriodKwargs) -> PolarsResult<Series> {
    let real = &mut cast_series_to_f64(&inputs[0])?;
    let (real_ptr, _real) = get_series_f64_ptr(real)?;
    let len = real.len();
    let res = ta_er(real_ptr, len, &kwargs);
    match res {
        Ok(out) => Ok(Float64Chunked::from_vec("", out).into_series()),
        Err(ret_code) => ta_code2err(ret_code),
    }
}

pub fn eri_output(_: &[Field]) -> PolarsResult<Field> {
    let bullpower = Field::new("bullpower", DataType::Float64);
    let bearpower = Field::new("bearpower", DataType::Float64);
    let v: Vec<Field> = vec![bullpower, bearpower];
    Ok(Field::new("", DataType::Struct(v)))
}

#[polars_expr(output_type_func=eri_output)]
fn eri(inputs: &[Series], kwargs: TimePeriodKwargs) -> PolarsResult<Series> {
    let close = &mut cast_series_to_f64(&inputs[0])?;
    let high = &mut cast_series_to_f64(&inputs[1])?;
    let low = &mut cast_series_to_f64(&inputs[2])?;
    let (close_ptr, _close) = get_series_f64_ptr(close)?;
    let (high_ptr, _high) = get_series_f64_ptr(high)?;
    let (low_ptr, _low) = get_series_f64_ptr(low)?;
    let len = close.len();
    let res = ta_eri(high_ptr, low_ptr, close_ptr, len, &kwargs);
    match res {
        Ok((outbullpower, outbearpower)) => {
            let bullpower = Series::from_vec("bullpower", outbullpower);
            let bearpower = Series::from_vec("bearpower", outbearpower);
            let out = StructChunked::new("", &[bullpower, bearpower])?;
            Ok(out.into_series())
        }
        Err(ret_code) => ta_code2err(ret_code),
    }
}

#[polars_expr(output_type=Float64)]
fn fosc(inputs: &[Series], kwargs: TimePeriodKwargs) -> PolarsResult<Series> {
    let real = &mut cast_series_to_f64(&inputs[0])?;
    let (real_ptr, _real) = get_series_f64_ptr(real)?;
    let len = real.len();
    let res = ta_fosc(real_ptr, len, &kwargs);
    match res {
        Ok(out) => Ok(Float64Chunked::from_vec("", out).into_series()),
        Err(ret_code) => ta_code2err(ret_code),
    }
}

pub fn fractal_output(_: &[Field]) -> PolarsResult<Field> {
    let swinghigh = Field::new("swinghigh", DataType::Int32);
    let swinglow = Field::new("swinglow", DataType::Int32);
    let v: Vec<Field> = vec![swinghigh, swinglow];
    Ok(Field::new("", DataType::Struct(v)))
}

#[polars_expr(output_type_func=fractal_output)]
fn fractal(inputs: &[Series], kwargs: FractalKwargs) -> PolarsResult<Series> {
    let high = &mut cast_series_to_f64(&inputs[0])?;
    let low = &mut cast_series_to_f64(&inputs[1])?;
    let (high_ptr, _high) = get_series_f64_ptr(high)?;
    let (low_ptr, _low) = get_series_f64_ptr(low)?;
    let len = high.len();
    let res = ta_fractal(high_ptr, low_ptr, len, &kwargs);
    match res {
        Ok((outswinghigh, outswinglow)) => {
            let swinghigh = Series::from_vec("swinghigh", outswinghigh);
            let swinglow = Series::from_vec("swinglow", outswinglow);
            let out = StructChunked::new("", &[swinghigh, swinglow])?;
            Ok(out.into_series())
        }
        Err(ret_code) => ta_code2err(ret_code),
    }
}

#[polars_expr(output_type=Float64)]
fn imi(inputs: &[Series], kwargs: TimePeriodKwargs) -> PolarsResult<Series> {
    let open = &mut cast_series_to_f64(&inputs[0])?;
    let close = &mut cast_series_to_f64(&inputs[1])?;
    let (open_ptr, _open) = get_series_f64_ptr(open)?;
    let (close_ptr, _close) = get_series_f64_ptr(close)?;
    let len = open.len();
    let res = ta_imi(open_ptr, close_ptr, len, &kwargs);
    match res {
        Ok(out) => Ok(Float64Chunked::from_vec("", out).into_series()),
        Err(ret_code) => ta_code2err(ret_code),
    }
}

pub fn kdj_output(_: &[Field]) -> PolarsResult<Field> {
    let k = Field::new("k", DataType::Float64);
    let d = Field::new("d", DataType::Float64);
    let j = Field::new("j", DataType::Float64);
    let v: Vec<Field> = vec![k, d, j];
    Ok(Field::new("", DataType::Struct(v)))
}

#[polars_expr(output_type_func=kdj_output)]
fn kdj(inputs: &[Series], kwargs: KdjKwargs) -> PolarsResult<Series> {
    let close = &mut cast_series_to_f64(&inputs[0])?;
    let high = &mut cast_series_to_f64(&inputs[1])?;
    let low = &mut cast_series_to_f64(&inputs[2])?;
    let (close_ptr, _close) = get_series_f64_ptr(close)?;
    let (high_ptr, _high) = get_series_f64_ptr(high)?;
    let (low_ptr, _low) = get_series_f64_ptr(low)?;
    let len = close.len();
    let res = ta_kdj(high_ptr, low_ptr, close_ptr, len, &kwargs);
    match res {
        Ok((outk, outd, outj)) => {
            let k = Series::from_vec("k", outk);
            let d = Series::from_vec("d", outd);
            let j = Series::from_vec("j", outj);
            let out = StructChunked::new("", &[k, d, j])?;
            Ok(out.into_series())
        }
        Err(ret_code) => ta_code2err(ret_code),
    }
}

#[polars_expr(output_type=Float64)]
fn qstick(inputs: &[Series], kwargs: TimePeriodKwargs) -> PolarsResult<Series> {
    let open = &mut cast_series_to_f64(&inputs[0])?;
    let close = &mut cast_series_to_f64(&inputs[1])?;
    let (open_ptr, _open) = get_series_f64_ptr(open)?;
    let (close_ptr, _close) = get_series_f64_ptr(close)?;
    let len = open.len();
    let res = ta_qstick(open_ptr, close_ptr, len, &kwargs);
    match res {
        Ok(out) => Ok(Float64Chunked::from_vec("", out).into_series()),
        Err(ret_code) => ta_code2err(ret_code),
    }
}

pub fn smi_output(_: &[Field]) -> PolarsResult<Field> {
    let smi = Field::new("smi", DataType::Float64);
    let smisignal = Field::new("smisignal", DataType::Float64);
    let v: Vec<Field> = vec![smi, smisignal];
    Ok(Field::new("", DataType::Struct(v)))
}

#[polars_expr(output_type_func=smi_output)]
fn smi(inputs: &[Series], kwargs: SmiKwargs) -> PolarsResult<Series> {
    let close = &mut cast_series_to_f64(&inputs[0])?;
    let high = &mut cast_series_to_f64(&inputs[1])?;
    let low = &mut cast_series_to_f64(&inputs[2])?;
    let (close_ptr, _close) = get_series_f64_ptr(close)?;
    let (high_ptr, _high) = get_series_f64_ptr(high)?;
    let (low_ptr, _low) = get_series_f64_ptr(low)?;
    let len = close.len();
    let res = ta_smi(high_ptr, low_ptr, close_ptr, len, &kwargs);
    match res {
        Ok((outsmi, outsmisignal)) => {
            let smi = Series::from_vec("smi", outsmi);
            let smisignal = Series::from_vec("smisignal", outsmisignal);
            let out = StructChunked::new("", &[smi, smisignal])?;
            Ok(out.into_series())
        }
        Err(ret_code) => ta_code2err(ret_code),
    }
}

#[polars_expr(output_type=Float64)]
fn tsi(inputs: &[Series], kwargs: TsiKwargs) -> PolarsResult<Series> {
    let real = &mut cast_series_to_f64(&inputs[0])?;
    let (real_ptr, _real) = get_series_f64_ptr(real)?;
    let len = real.len();
    let res = ta_tsi(real_ptr, len, &kwargs);
    match res {
        Ok(out) => Ok(Float64Chunked::from_vec("", out).into_series()),
        Err(ret_code) => ta_code2err(ret_code),
    }
}

#[polars_expr(output_type=Float64)]
fn vhf(inputs: &[Series], kwargs: TimePeriodKwargs) -> PolarsResult<Series> {
    let real = &mut cast_series_to_f64(&inputs[0])?;
    let (real_ptr, _real) = get_series_f64_ptr(real)?;
    let len = real.len();
    let res = ta_vhf(real_ptr, len, &kwargs);
    match res {
        Ok(out) => Ok(Float64Chunked::from_vec("", out).into_series()),
        Err(ret_code) => ta_code2err(ret_code),
    }
}

pub fn vortex_output(_: &[Field]) -> PolarsResult<Field> {
    let plusvi = Field::new("plusvi", DataType::Float64);
    let minusvi = Field::new("minusvi", DataType::Float64);
    let v: Vec<Field> = vec![plusvi, minusvi];
    Ok(Field::new("", DataType::Struct(v)))
}

#[polars_expr(output_type_func=vortex_output)]
fn vortex(inputs: &[Series], kwargs: TimePeriodKwargs) -> PolarsResult<Series> {
    let close = &mut cast_series_to_f64(&inputs[0])?;
    let high = &mut cast_series_to_f64(&inputs[1])?;
    let low = &mut cast_series_to_f64(&inputs[2])?;
    let (close_ptr, _close) = get_series_f64_ptr(close)?;
    let (high_ptr, _high) = get_series_f64_ptr(high)?;
    let (low_ptr, _low) = get_series_f64_ptr(low)?;
    let len = close.len();
    let res = ta_vortex(high_ptr, low_ptr, close_ptr, len, &kwargs);
    match res {
        Ok((outplusvi, outminusvi)) => {
            let plusvi = Series::from_vec("plusvi", outplusvi);
            let minusvi = Series::from_vec("minusvi", outminusvi);
            let out = StructChunked::new("", &[plusvi, minusvi])?;
            Ok(out.into_series())
        }
        Err(ret_code) => ta_code2err(ret_code),
    }
}

#[polars_expr(output_type=Float64)]
fn wad(inputs: &[Series]) -> PolarsResult<Series> {
    let close = &mut cast_series_to_f64(&inputs[0])?;
    let high = &mut cast_series_to_f64(&inputs[1])?;
    let low = &mut cast_series_to_f64(&inputs[2])?;
    let (close_ptr, _close) = get_series_f64_ptr(close)?;
    let (high_ptr, _high) = get_series_f64_ptr(high)?;
    let (low_ptr, _low) = get_series_f64_ptr(low)?;
    let len = close.len();
    let res = ta_wad(high_ptr, low_ptr, close_ptr, len);
    match res {
        Ok(out) => Ok(Float64Chunked::from_vec("", out).into_series()),
        Err(ret_code) => ta_code2err(ret_code),
    }
}
