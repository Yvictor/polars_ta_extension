use crate::utils::{get_series_f64_ptr, ta_code2err};
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

#[polars_expr(output_type=Float64)]
fn adx(inputs: &[Series], kwargs: TimePeriodKwargs) -> PolarsResult<Series> {
    let high = &mut inputs[1].to_float()?.rechunk();
    let low = &mut inputs[2].to_float()?.rechunk();
    let close = &mut inputs[0].to_float()?.rechunk();
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
    let high = &mut inputs[1].to_float()?.rechunk();
    let low = &mut inputs[2].to_float()?.rechunk();
    let close = &mut inputs[0].to_float()?.rechunk();
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
    let input = &mut inputs[0].to_float()?.rechunk();
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
    let high = &mut inputs[0].to_float()?.rechunk();
    let low = &mut inputs[1].to_float()?.rechunk();
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
    let high = &mut inputs[0].to_float()?.rechunk();
    let low = &mut inputs[1].to_float()?.rechunk();
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
    let open = &mut inputs[0].to_float()?.rechunk();
    let high = &mut inputs[1].to_float()?.rechunk();
    let low = &mut inputs[2].to_float()?.rechunk();
    let close = &mut inputs[3].to_float()?.rechunk();
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
    let high = &mut inputs[1].to_float()?.rechunk();
    let low = &mut inputs[2].to_float()?.rechunk();
    let close = &mut inputs[0].to_float()?.rechunk();
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
    let input = &mut inputs[0].to_float()?.rechunk();
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
    let high = &mut inputs[1].to_float()?.rechunk();
    let low = &mut inputs[2].to_float()?.rechunk();
    let close = &mut inputs[0].to_float()?.rechunk();
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
    let input = &mut inputs[0].to_float()?.rechunk();
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
    let input = &mut inputs[0].to_float()?.rechunk();
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
    let input = &mut inputs[0].to_float()?.rechunk();
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
    let high = &mut inputs[1].to_float()?.rechunk();
    let low = &mut inputs[2].to_float()?.rechunk();
    let close = &mut inputs[0].to_float()?.rechunk();
    let volume = &mut inputs[3].to_float()?.rechunk();
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
    let high = &mut inputs[1].to_float()?.rechunk();
    let low = &mut inputs[2].to_float()?.rechunk();
    let close = &mut inputs[0].to_float()?.rechunk();
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
    let high = &mut inputs[0].to_float()?.rechunk();
    let low = &mut inputs[1].to_float()?.rechunk();
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
    let input = &mut inputs[0].to_float()?.rechunk();
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
    let high = &mut inputs[1].to_float()?.rechunk();
    let low = &mut inputs[2].to_float()?.rechunk();
    let close = &mut inputs[0].to_float()?.rechunk();
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
    let high = &mut inputs[0].to_float()?.rechunk();
    let low = &mut inputs[1].to_float()?.rechunk();
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
    let input = &mut inputs[0].to_float()?.rechunk();
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
    let input = &mut inputs[0].to_float()?.rechunk();
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
    let input = &mut inputs[0].to_float()?.rechunk();
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
    let input = &mut inputs[0].to_float()?.rechunk();
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
    let input = &mut inputs[0].to_float()?.rechunk();
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
    let input = &mut inputs[0].to_float()?.rechunk();
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
    let high = &mut inputs[1].to_float()?.rechunk();
    let low = &mut inputs[2].to_float()?.rechunk();
    let close = &mut inputs[0].to_float()?.rechunk();
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
    let high = &mut inputs[1].to_float()?.rechunk();
    let low = &mut inputs[2].to_float()?.rechunk();
    let close = &mut inputs[0].to_float()?.rechunk();
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
    let input = &mut inputs[0].to_float()?.rechunk();
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
    let input = &mut inputs[0].to_float()?.rechunk();
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
    let high = &mut inputs[1].to_float()?.rechunk();
    let low = &mut inputs[2].to_float()?.rechunk();
    let close = &mut inputs[0].to_float()?.rechunk();
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
    let high = &mut inputs[1].to_float()?.rechunk();
    let low = &mut inputs[2].to_float()?.rechunk();
    let close = &mut inputs[0].to_float()?.rechunk();
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
