use crate::utils::{cast_series_to_f64, get_series_f64_ptr, ta_code2err};
use polars::prelude::*;
use pyo3_polars::derive::polars_expr;
use talib::common::TimePeriodKwargs;
use talib::overlap::{
    ta_bbands, ta_dema, ta_ema, ta_ht_trendline, ta_kama, ta_ma, ta_mama, ta_mavp, ta_midpoint,
    ta_midprice, ta_sar, ta_sarext, ta_sma, ta_t3, ta_tema, ta_trima, ta_wma, BBANDSKwargs,
    MaKwargs, MamaKwargs, MavpKwargs, SarExtKwargs, SarKwargs, T3Kwargs,
};
use talib::overlap::{ta_accbands};
use talib::overlap::{ta_donchian};
use talib::overlap::{ta_hma};
use talib::overlap::{ta_kc, KcKwargs};
use talib::overlap::{ta_rma};
use talib::overlap::{ta_supertrend, SupertrendKwargs};
use talib::overlap::{ta_vwma};
use talib::overlap::{ta_zlema};

pub fn bbands_output(_: &[Field]) -> PolarsResult<Field> {
    let u = Field::new("upperband", DataType::Float64);
    let m = Field::new("middleband", DataType::Float64);
    let l = Field::new("lowerband", DataType::Float64);
    let v: Vec<Field> = vec![u, m, l];
    Ok(Field::new("", DataType::Struct(v)))
}

#[polars_expr(output_type_func=bbands_output)]
fn bbands(inputs: &[Series], kwargs: BBANDSKwargs) -> PolarsResult<Series> {
    let input = &mut cast_series_to_f64(&inputs[0])?;
    let (input_ptr, _input) = get_series_f64_ptr(input)?;
    let len = input.len();
    let res = ta_bbands(input_ptr, len, &kwargs);
    match res {
        Ok((outrealupperband, outrealmiddleband, outreallowerband)) => {
            let u = Series::from_vec("upperband", outrealupperband);
            let m = Series::from_vec("middleband", outrealmiddleband);
            let l = Series::from_vec("lowerband", outreallowerband);
            let out = StructChunked::new("", &[u, m, l])?;
            Ok(out.into_series())
        }
        Err(ret_code) => ta_code2err(ret_code),
    }
}

#[polars_expr(output_type=Float64)]
fn ema(inputs: &[Series], kwargs: TimePeriodKwargs) -> PolarsResult<Series> {
    let input = &mut cast_series_to_f64(&inputs[0])?;
    let (input_ptr, _input) = get_series_f64_ptr(input)?;
    let len = input.len();
    // println!("has_validity: {}", input.has_validity());
    // println!("len: {}", input.len());
    // println!("null_count: {}", input.null_count());
    let res = ta_ema(input_ptr, len, &kwargs);
    match res {
        Ok(out) => Ok(Float64Chunked::from_vec("", out).into_series()),
        Err(ret_code) => ta_code2err(ret_code),
    }
}

#[polars_expr(output_type=Float64)]
fn dema(inputs: &[Series], kwargs: TimePeriodKwargs) -> PolarsResult<Series> {
    let input = &mut cast_series_to_f64(&inputs[0])?;
    let (input_ptr, _input) = get_series_f64_ptr(input)?;
    let len = input.len();
    let res = ta_dema(input_ptr, len, &kwargs);
    match res {
        Ok(out) => Ok(Float64Chunked::from_vec("", out).into_series()),
        Err(ret_code) => ta_code2err(ret_code),
    }
}

#[polars_expr(output_type=Float64)]
fn ht_trendline(inputs: &[Series]) -> PolarsResult<Series> {
    let input = &mut cast_series_to_f64(&inputs[0])?;
    let (input_ptr, _input) = get_series_f64_ptr(input)?;
    let len = input.len();
    let res = ta_ht_trendline(input_ptr, len);
    match res {
        Ok(out) => Ok(Float64Chunked::from_vec("", out).into_series()),
        Err(ret_code) => ta_code2err(ret_code),
    }
}

#[polars_expr(output_type=Float64)]
fn kama(inputs: &[Series], kwargs: TimePeriodKwargs) -> PolarsResult<Series> {
    let input = &mut cast_series_to_f64(&inputs[0])?;
    let (input_ptr, _input) = get_series_f64_ptr(input)?;
    let len = input.len();
    let res = ta_kama(input_ptr, len, &kwargs);
    match res {
        Ok(out) => Ok(Float64Chunked::from_vec("", out).into_series()),
        Err(ret_code) => ta_code2err(ret_code),
    }
}

#[polars_expr(output_type=Float64)]
fn ma(inputs: &[Series], kwargs: MaKwargs) -> PolarsResult<Series> {
    let input = &mut cast_series_to_f64(&inputs[0])?;
    let (input_ptr, _input) = get_series_f64_ptr(input)?;
    let len = input.len();
    let res = ta_ma(input_ptr, len, &kwargs);
    match res {
        Ok(out) => Ok(Float64Chunked::from_vec("", out).into_series()),
        Err(ret_code) => ta_code2err(ret_code),
    }
}

pub fn mama_output(_: &[Field]) -> PolarsResult<Field> {
    let m = Field::new("mama", DataType::Float64);
    let f = Field::new("fama", DataType::Float64);
    let v: Vec<Field> = vec![m, f];
    Ok(Field::new("", DataType::Struct(v)))
}

#[polars_expr(output_type_func=mama_output)]
fn mama(inputs: &[Series], kwargs: MamaKwargs) -> PolarsResult<Series> {
    let input = &mut cast_series_to_f64(&inputs[0])?;
    let (input_ptr, _input) = get_series_f64_ptr(input)?;
    let len = input.len();
    let res = ta_mama(input_ptr, len, &kwargs);
    match res {
        Ok((outrealmama, outrealfama)) => {
            let m = Series::from_vec("mama", outrealmama);
            let f = Series::from_vec("fama", outrealfama);
            let out = StructChunked::new("", &[m, f])?;
            Ok(out.into_series())
        }
        Err(ret_code) => ta_code2err(ret_code),
    }
}

#[polars_expr(output_type=Float64)]
fn mavp(inputs: &[Series], kwargs: MavpKwargs) -> PolarsResult<Series> {
    let input = &mut cast_series_to_f64(&inputs[0])?;
    let in_time_period = &mut cast_series_to_f64(&inputs[1])?;
    let (input_ptr, _input) = get_series_f64_ptr(input)?;
    let (in_time_period_ptr, _in_time_period) = get_series_f64_ptr(in_time_period)?;
    let len = input.len();
    let res = ta_mavp(input_ptr, in_time_period_ptr, len, &kwargs);
    match res {
        Ok(out) => Ok(Float64Chunked::from_vec("", out).into_series()),
        Err(ret_code) => ta_code2err(ret_code),
    }
}

#[polars_expr(output_type=Float64)]
fn midpoint(inputs: &[Series], kwargs: TimePeriodKwargs) -> PolarsResult<Series> {
    let input = &mut cast_series_to_f64(&inputs[0])?;
    let (input_ptr, _input) = get_series_f64_ptr(input)?;
    let len = input.len();
    let res = ta_midpoint(input_ptr, len, &kwargs);
    match res {
        Ok(out) => Ok(Float64Chunked::from_vec("", out).into_series()),
        Err(ret_code) => ta_code2err(ret_code),
    }
}

#[polars_expr(output_type=Float64)]
fn midprice(inputs: &[Series], kwargs: TimePeriodKwargs) -> PolarsResult<Series> {
    let high = &mut cast_series_to_f64(&inputs[0])?;
    let low = &mut cast_series_to_f64(&inputs[1])?;
    let (high_ptr, _high) = get_series_f64_ptr(high)?;
    let (low_ptr, _low) = get_series_f64_ptr(low)?;
    let len = high.len();
    let res = ta_midprice(high_ptr, low_ptr, len, &kwargs);
    match res {
        Ok(out) => Ok(Float64Chunked::from_vec("", out).into_series()),
        Err(ret_code) => ta_code2err(ret_code),
    }
}

#[polars_expr(output_type=Float64)]
fn sar(inputs: &[Series], kwargs: SarKwargs) -> PolarsResult<Series> {
    let high = &mut cast_series_to_f64(&inputs[0])?;
    let low = &mut cast_series_to_f64(&inputs[1])?;
    let (high_ptr, _high) = get_series_f64_ptr(high)?;
    let (low_ptr, _low) = get_series_f64_ptr(low)?;
    let len = high.len();
    let res = ta_sar(high_ptr, low_ptr, len, &kwargs);
    match res {
        Ok(out) => Ok(Float64Chunked::from_vec("", out).into_series()),
        Err(ret_code) => ta_code2err(ret_code),
    }
}

#[polars_expr(output_type=Float64)]
fn sarext(inputs: &[Series], kwargs: SarExtKwargs) -> PolarsResult<Series> {
    let high = &mut cast_series_to_f64(&inputs[0])?;
    let low = &mut cast_series_to_f64(&inputs[1])?;
    let (high_ptr, _high) = get_series_f64_ptr(high)?;
    let (low_ptr, _low) = get_series_f64_ptr(low)?;
    let len = high.len();
    let res = ta_sarext(high_ptr, low_ptr, len, &kwargs);
    match res {
        Ok(out) => Ok(Float64Chunked::from_vec("", out).into_series()),
        Err(ret_code) => ta_code2err(ret_code),
    }
}

#[polars_expr(output_type=Float64)]
fn sma(inputs: &[Series], kwargs: TimePeriodKwargs) -> PolarsResult<Series> {
    let input = &mut cast_series_to_f64(&inputs[0])?;
    let (in_real_ptr, _in_real) = get_series_f64_ptr(input)?;
    let len = input.len();
    let res = ta_sma(in_real_ptr, len, &kwargs);
    match res {
        Ok(out) => Ok(Float64Chunked::from_vec("", out).into_series()),
        Err(ret_code) => ta_code2err(ret_code),
    }
}

#[polars_expr(output_type=Float64)]
fn t3(inputs: &[Series], kwargs: T3Kwargs) -> PolarsResult<Series> {
    let input = &mut cast_series_to_f64(&inputs[0])?;
    let (in_real_ptr, _in_real) = get_series_f64_ptr(input)?;
    let len = input.len();
    let res = ta_t3(in_real_ptr, len, &kwargs);
    match res {
        Ok(out) => Ok(Float64Chunked::from_vec("", out).into_series()),
        Err(ret_code) => ta_code2err(ret_code),
    }
}

#[polars_expr(output_type=Float64)]
fn tema(inputs: &[Series], kwargs: TimePeriodKwargs) -> PolarsResult<Series> {
    let input = &mut cast_series_to_f64(&inputs[0])?;
    let (in_real_ptr, _in_real) = get_series_f64_ptr(input)?;
    let len = input.len();
    let res = ta_tema(in_real_ptr, len, &kwargs);
    match res {
        Ok(out) => Ok(Float64Chunked::from_vec("", out).into_series()),
        Err(ret_code) => ta_code2err(ret_code),
    }
}

#[polars_expr(output_type=Float64)]
fn trima(inputs: &[Series], kwargs: TimePeriodKwargs) -> PolarsResult<Series> {
    let input = &mut cast_series_to_f64(&inputs[0])?;
    let (in_real_ptr, _in_real) = get_series_f64_ptr(input)?;
    let len = input.len();
    let res = ta_trima(in_real_ptr, len, &kwargs);
    match res {
        Ok(out) => Ok(Float64Chunked::from_vec("", out).into_series()),
        Err(ret_code) => ta_code2err(ret_code),
    }
}

#[polars_expr(output_type=Float64)]
fn wma(inputs: &[Series], kwargs: TimePeriodKwargs) -> PolarsResult<Series> {
    let input = &mut cast_series_to_f64(&inputs[0])?;
    let (in_real_ptr, _in_real) = get_series_f64_ptr(input)?;
    let len = input.len();
    let res = ta_wma(in_real_ptr, len, &kwargs);
    match res {
        Ok(out) => Ok(Float64Chunked::from_vec("", out).into_series()),
        Err(ret_code) => ta_code2err(ret_code),
    }
}

pub fn accbands_output(_: &[Field]) -> PolarsResult<Field> {
    let upperband = Field::new("upperband", DataType::Float64);
    let middleband = Field::new("middleband", DataType::Float64);
    let lowerband = Field::new("lowerband", DataType::Float64);
    let v: Vec<Field> = vec![upperband, middleband, lowerband];
    Ok(Field::new("", DataType::Struct(v)))
}

#[polars_expr(output_type_func=accbands_output)]
fn accbands(inputs: &[Series], kwargs: TimePeriodKwargs) -> PolarsResult<Series> {
    let close = &mut cast_series_to_f64(&inputs[0])?;
    let high = &mut cast_series_to_f64(&inputs[1])?;
    let low = &mut cast_series_to_f64(&inputs[2])?;
    let (close_ptr, _close) = get_series_f64_ptr(close)?;
    let (high_ptr, _high) = get_series_f64_ptr(high)?;
    let (low_ptr, _low) = get_series_f64_ptr(low)?;
    let len = close.len();
    let res = ta_accbands(high_ptr, low_ptr, close_ptr, len, &kwargs);
    match res {
        Ok((outupperband, outmiddleband, outlowerband)) => {
            let upperband = Series::from_vec("upperband", outupperband);
            let middleband = Series::from_vec("middleband", outmiddleband);
            let lowerband = Series::from_vec("lowerband", outlowerband);
            let out = StructChunked::new("", &[upperband, middleband, lowerband])?;
            Ok(out.into_series())
        }
        Err(ret_code) => ta_code2err(ret_code),
    }
}

pub fn donchian_output(_: &[Field]) -> PolarsResult<Field> {
    let upperband = Field::new("upperband", DataType::Float64);
    let middleband = Field::new("middleband", DataType::Float64);
    let lowerband = Field::new("lowerband", DataType::Float64);
    let v: Vec<Field> = vec![upperband, middleband, lowerband];
    Ok(Field::new("", DataType::Struct(v)))
}

#[polars_expr(output_type_func=donchian_output)]
fn donchian(inputs: &[Series], kwargs: TimePeriodKwargs) -> PolarsResult<Series> {
    let high = &mut cast_series_to_f64(&inputs[0])?;
    let low = &mut cast_series_to_f64(&inputs[1])?;
    let (high_ptr, _high) = get_series_f64_ptr(high)?;
    let (low_ptr, _low) = get_series_f64_ptr(low)?;
    let len = high.len();
    let res = ta_donchian(high_ptr, low_ptr, len, &kwargs);
    match res {
        Ok((outupperband, outmiddleband, outlowerband)) => {
            let upperband = Series::from_vec("upperband", outupperband);
            let middleband = Series::from_vec("middleband", outmiddleband);
            let lowerband = Series::from_vec("lowerband", outlowerband);
            let out = StructChunked::new("", &[upperband, middleband, lowerband])?;
            Ok(out.into_series())
        }
        Err(ret_code) => ta_code2err(ret_code),
    }
}

#[polars_expr(output_type=Float64)]
fn hma(inputs: &[Series], kwargs: TimePeriodKwargs) -> PolarsResult<Series> {
    let real = &mut cast_series_to_f64(&inputs[0])?;
    let (real_ptr, _real) = get_series_f64_ptr(real)?;
    let len = real.len();
    let res = ta_hma(real_ptr, len, &kwargs);
    match res {
        Ok(out) => Ok(Float64Chunked::from_vec("", out).into_series()),
        Err(ret_code) => ta_code2err(ret_code),
    }
}

pub fn kc_output(_: &[Field]) -> PolarsResult<Field> {
    let upperband = Field::new("upperband", DataType::Float64);
    let middleband = Field::new("middleband", DataType::Float64);
    let lowerband = Field::new("lowerband", DataType::Float64);
    let v: Vec<Field> = vec![upperband, middleband, lowerband];
    Ok(Field::new("", DataType::Struct(v)))
}

#[polars_expr(output_type_func=kc_output)]
fn kc(inputs: &[Series], kwargs: KcKwargs) -> PolarsResult<Series> {
    let close = &mut cast_series_to_f64(&inputs[0])?;
    let high = &mut cast_series_to_f64(&inputs[1])?;
    let low = &mut cast_series_to_f64(&inputs[2])?;
    let (close_ptr, _close) = get_series_f64_ptr(close)?;
    let (high_ptr, _high) = get_series_f64_ptr(high)?;
    let (low_ptr, _low) = get_series_f64_ptr(low)?;
    let len = close.len();
    let res = ta_kc(high_ptr, low_ptr, close_ptr, len, &kwargs);
    match res {
        Ok((outupperband, outmiddleband, outlowerband)) => {
            let upperband = Series::from_vec("upperband", outupperband);
            let middleband = Series::from_vec("middleband", outmiddleband);
            let lowerband = Series::from_vec("lowerband", outlowerband);
            let out = StructChunked::new("", &[upperband, middleband, lowerband])?;
            Ok(out.into_series())
        }
        Err(ret_code) => ta_code2err(ret_code),
    }
}

#[polars_expr(output_type=Float64)]
fn rma(inputs: &[Series], kwargs: TimePeriodKwargs) -> PolarsResult<Series> {
    let real = &mut cast_series_to_f64(&inputs[0])?;
    let (real_ptr, _real) = get_series_f64_ptr(real)?;
    let len = real.len();
    let res = ta_rma(real_ptr, len, &kwargs);
    match res {
        Ok(out) => Ok(Float64Chunked::from_vec("", out).into_series()),
        Err(ret_code) => ta_code2err(ret_code),
    }
}

pub fn supertrend_output(_: &[Field]) -> PolarsResult<Field> {
    let supertrend = Field::new("supertrend", DataType::Float64);
    let trend = Field::new("trend", DataType::Int32);
    let v: Vec<Field> = vec![supertrend, trend];
    Ok(Field::new("", DataType::Struct(v)))
}

#[polars_expr(output_type_func=supertrend_output)]
fn supertrend(inputs: &[Series], kwargs: SupertrendKwargs) -> PolarsResult<Series> {
    let close = &mut cast_series_to_f64(&inputs[0])?;
    let high = &mut cast_series_to_f64(&inputs[1])?;
    let low = &mut cast_series_to_f64(&inputs[2])?;
    let (close_ptr, _close) = get_series_f64_ptr(close)?;
    let (high_ptr, _high) = get_series_f64_ptr(high)?;
    let (low_ptr, _low) = get_series_f64_ptr(low)?;
    let len = close.len();
    let res = ta_supertrend(high_ptr, low_ptr, close_ptr, len, &kwargs);
    match res {
        Ok((outsupertrend, outtrend)) => {
            let supertrend = Series::from_vec("supertrend", outsupertrend);
            let trend = Series::from_vec("trend", outtrend);
            let out = StructChunked::new("", &[supertrend, trend])?;
            Ok(out.into_series())
        }
        Err(ret_code) => ta_code2err(ret_code),
    }
}

#[polars_expr(output_type=Float64)]
fn vwma(inputs: &[Series], kwargs: TimePeriodKwargs) -> PolarsResult<Series> {
    let real = &mut cast_series_to_f64(&inputs[0])?;
    let volume = &mut cast_series_to_f64(&inputs[1])?;
    let (real_ptr, _real) = get_series_f64_ptr(real)?;
    let (volume_ptr, _volume) = get_series_f64_ptr(volume)?;
    let len = real.len();
    let res = ta_vwma(real_ptr, volume_ptr, len, &kwargs);
    match res {
        Ok(out) => Ok(Float64Chunked::from_vec("", out).into_series()),
        Err(ret_code) => ta_code2err(ret_code),
    }
}

#[polars_expr(output_type=Float64)]
fn zlema(inputs: &[Series], kwargs: TimePeriodKwargs) -> PolarsResult<Series> {
    let real = &mut cast_series_to_f64(&inputs[0])?;
    let (real_ptr, _real) = get_series_f64_ptr(real)?;
    let len = real.len();
    let res = ta_zlema(real_ptr, len, &kwargs);
    match res {
        Ok(out) => Ok(Float64Chunked::from_vec("", out).into_series()),
        Err(ret_code) => ta_code2err(ret_code),
    }
}
