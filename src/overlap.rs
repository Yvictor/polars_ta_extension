use crate::utils::{cast_series_to_f64, get_series_f64_ptr, ta_code2err};
use polars::prelude::*;
use talib::common::TimePeriodKwargs;
use talib::overlap::{
    ta_bbands, ta_dema, ta_ema, ta_ht_trendline, ta_kama, ta_ma, ta_mama, ta_mavp, ta_midpoint,
    ta_midprice, ta_sar, ta_sarext, ta_sma, ta_t3, ta_tema, ta_trima, ta_wma, BBANDSKwargs,
    MaKwargs, MamaKwargs, MavpKwargs, SarExtKwargs, SarKwargs, T3Kwargs,
};
// pub 
pub fn bbands_output(_: &[Field]) -> PolarsResult<Field> {
    let u = Field::new("upperband".into(), DataType::Float64);
    let m = Field::new("middleband".into(), DataType::Float64);
    let l = Field::new("lowerband".into(), DataType::Float64);
    let v: Vec<Field> = vec![u, m, l];
    Ok(Field::new("".into(), DataType::Struct(v)))
}

// #[polars_expr(output_type_func=bbands_output)]
pub fn bbands(inputs: &[Series], kwargs: BBANDSKwargs) -> PolarsResult<Series> {
    let input = &mut cast_series_to_f64(&inputs[0])?;
    let (input_ptr, _input) = get_series_f64_ptr(input)?;
    let len = input.len();
    let res = ta_bbands(input_ptr, len, &kwargs);
    match res {
        Ok((outrealupperband, outrealmiddleband, outreallowerband)) => {
            let u = Series::from_vec("upperband".into(), outrealupperband);
            let m = Series::from_vec("middleband".into(), outrealmiddleband);
            let l = Series::from_vec("lowerband".into(), outreallowerband);
            let out = Series::new("upperband_middleband_lowerband".into(), &[u, m, l]);
            Ok(out.into_series())
        }
        Err(ret_code) => ta_code2err(ret_code),
    }
}

// #[polars_expr(output_type=Float64)]
pub fn ema(inputs: &[Series], kwargs: TimePeriodKwargs) -> PolarsResult<Series> {
    let input = &mut cast_series_to_f64(&inputs[0])?;
    let (input_ptr, _input) = get_series_f64_ptr(input)?;
    let len = input.len();
    // println!("has_validity: {}".into(), input.has_validity());
    // println!("len: {}".into(), input.len());
    // println!("null_count: {}".into(), input.null_count());
    let res = ta_ema(input_ptr, len, &kwargs);
    match res {
        Ok(out) => Ok(Float64Chunked::from_vec("".into(), out).into_series()),
        Err(ret_code) => ta_code2err(ret_code),
    }
}

// #[polars_expr(output_type=Float64)]
pub fn dema(inputs: &[Series], kwargs: TimePeriodKwargs) -> PolarsResult<Series> {
    let input = &mut cast_series_to_f64(&inputs[0])?;
    let (input_ptr, _input) = get_series_f64_ptr(input)?;
    let len = input.len();
    let res = ta_dema(input_ptr, len, &kwargs);
    match res {
        Ok(out) => Ok(Float64Chunked::from_vec("".into(), out).into_series()),
        Err(ret_code) => ta_code2err(ret_code),
    }
}

// #[polars_expr(output_type=Float64)]
pub fn ht_trendline(inputs: &[Series]) -> PolarsResult<Series> {
    let input = &mut cast_series_to_f64(&inputs[0])?;
    let (input_ptr, _input) = get_series_f64_ptr(input)?;
    let len = input.len();
    let res = ta_ht_trendline(input_ptr, len);
    match res {
        Ok(out) => Ok(Float64Chunked::from_vec("".into(), out).into_series()),
        Err(ret_code) => ta_code2err(ret_code),
    }
}

// #[polars_expr(output_type=Float64)]
pub fn kama(inputs: &[Series], kwargs: TimePeriodKwargs) -> PolarsResult<Series> {
    let input = &mut cast_series_to_f64(&inputs[0])?;
    let (input_ptr, _input) = get_series_f64_ptr(input)?;
    let len = input.len();
    let res = ta_kama(input_ptr, len, &kwargs);
    match res {
        Ok(out) => Ok(Float64Chunked::from_vec("".into(), out).into_series()),
        Err(ret_code) => ta_code2err(ret_code),
    }
}

// #[polars_expr(output_type=Float64)]
pub fn ma(inputs: &[Series], kwargs: MaKwargs) -> PolarsResult<Series> {
    let input = &mut cast_series_to_f64(&inputs[0])?;
    let (input_ptr, _input) = get_series_f64_ptr(input)?;
    let len = input.len();
    let res = ta_ma(input_ptr, len, &kwargs);
    match res {
        Ok(out) => Ok(Float64Chunked::from_vec("".into(), out).into_series()),
        Err(ret_code) => ta_code2err(ret_code),
    }
}
// pub 
pub fn mama_output(_: &[Field]) -> PolarsResult<Field> {
    let m = Field::new("mama".into(), DataType::Float64);
    let f = Field::new("fama".into(), DataType::Float64);
    let v: Vec<Field> = vec![m, f];
    Ok(Field::new("".into(), DataType::Struct(v)))
}

// #[polars_expr(output_type_func=mama_output)]
pub fn mama(inputs: &[Series], kwargs: MamaKwargs) -> PolarsResult<Series> {
    let input = &mut cast_series_to_f64(&inputs[0])?;
    let (input_ptr, _input) = get_series_f64_ptr(input)?;
    let len = input.len();
    let res = ta_mama(input_ptr, len, &kwargs);
    match res {
        Ok((outrealmama, outrealfama)) => {
            let m = Series::from_vec("mama".into(), outrealmama);
            let f = Series::from_vec("fama".into(), outrealfama);
            // TODO 后面升级从 Polars 0.43.0 开始，Series::from_vec 被替代为 Series::new
            // let out = StructChunked::new(<&str as Into<T>>::into(""), &[m, f])?;
            let out = Series::new("mama_fama".into(), &[m, f]);
            Ok(out.into_series())
        }
        Err(ret_code) => ta_code2err(ret_code),
    }
}

// #[polars_expr(output_type=Float64)]
pub fn mavp(inputs: &[Series], kwargs: MavpKwargs) -> PolarsResult<Series> {
    let input = &mut cast_series_to_f64(&inputs[0])?;
    let in_time_period = &mut cast_series_to_f64(&inputs[1])?;
    let (input_ptr, _input) = get_series_f64_ptr(input)?;
    let (in_time_period_ptr, _in_time_period) = get_series_f64_ptr(in_time_period)?;
    let len = input.len();
    let res = ta_mavp(input_ptr, in_time_period_ptr, len, &kwargs);
    match res {
        Ok(out) => Ok(Float64Chunked::from_vec("".into(), out).into_series()),
        Err(ret_code) => ta_code2err(ret_code),
    }
}

// #[polars_expr(output_type=Float64)]
pub fn midpoint(inputs: &[Series], kwargs: TimePeriodKwargs) -> PolarsResult<Series> {
    let input = &mut cast_series_to_f64(&inputs[0])?;
    let (input_ptr, _input) = get_series_f64_ptr(input)?;
    let len = input.len();
    let res = ta_midpoint(input_ptr, len, &kwargs);
    match res {
        Ok(out) => Ok(Float64Chunked::from_vec("".into(), out).into_series()),
        Err(ret_code) => ta_code2err(ret_code),
    }
}

// #[polars_expr(output_type=Float64)]
pub fn midprice(inputs: &[Series], kwargs: TimePeriodKwargs) -> PolarsResult<Series> {
    let high = &mut cast_series_to_f64(&inputs[0])?;
    let low = &mut cast_series_to_f64(&inputs[1])?;
    let (high_ptr, _high) = get_series_f64_ptr(high)?;
    let (low_ptr, _low) = get_series_f64_ptr(low)?;
    let len = high.len();
    let res = ta_midprice(high_ptr, low_ptr, len, &kwargs);
    match res {
        Ok(out) => Ok(Float64Chunked::from_vec("".into(), out).into_series()),
        Err(ret_code) => ta_code2err(ret_code),
    }
}

// #[polars_expr(output_type=Float64)]
pub fn sar(inputs: &[Series], kwargs: SarKwargs) -> PolarsResult<Series> {
    let high = &mut cast_series_to_f64(&inputs[0])?;
    let low = &mut cast_series_to_f64(&inputs[1])?;
    let (high_ptr, _high) = get_series_f64_ptr(high)?;
    let (low_ptr, _low) = get_series_f64_ptr(low)?;
    let len = high.len();
    let res = ta_sar(high_ptr, low_ptr, len, &kwargs);
    match res {
        Ok(out) => Ok(Float64Chunked::from_vec("".into(), out).into_series()),
        Err(ret_code) => ta_code2err(ret_code),
    }
}

// #[polars_expr(output_type=Float64)]
pub fn sarext(inputs: &[Series], kwargs: SarExtKwargs) -> PolarsResult<Series> {
    let high = &mut cast_series_to_f64(&inputs[0])?;
    let low = &mut cast_series_to_f64(&inputs[1])?;
    let (high_ptr, _high) = get_series_f64_ptr(high)?;
    let (low_ptr, _low) = get_series_f64_ptr(low)?;
    let len = high.len();
    let res = ta_sarext(high_ptr, low_ptr, len, &kwargs);
    match res {
        Ok(out) => Ok(Float64Chunked::from_vec("".into(), out).into_series()),
        Err(ret_code) => ta_code2err(ret_code),
    }
}

// #[polars_expr(output_type=Float64)]
pub fn sma(inputs: &[Series], kwargs: TimePeriodKwargs) -> PolarsResult<Series> {
    let input = &mut cast_series_to_f64(&inputs[0])?;
    let (in_real_ptr, _in_real) = get_series_f64_ptr(input)?;
    let len = input.len();
    let res = ta_sma(in_real_ptr, len, &kwargs);
    match res {
        Ok(out) => Ok(Float64Chunked::from_vec("".into(), out).into_series()),
        Err(ret_code) => ta_code2err(ret_code),
    }
}

// #[polars_expr(output_type=Float64)]
pub fn t3(inputs: &[Series], kwargs: T3Kwargs) -> PolarsResult<Series> {
    let input = &mut cast_series_to_f64(&inputs[0])?;
    let (in_real_ptr, _in_real) = get_series_f64_ptr(input)?;
    let len = input.len();
    let res = ta_t3(in_real_ptr, len, &kwargs);
    match res {
        Ok(out) => Ok(Float64Chunked::from_vec("".into(), out).into_series()),
        Err(ret_code) => ta_code2err(ret_code),
    }
}

// #[polars_expr(output_type=Float64)]
pub fn tema(inputs: &[Series], kwargs: TimePeriodKwargs) -> PolarsResult<Series> {
    let input = &mut cast_series_to_f64(&inputs[0])?;
    let (in_real_ptr, _in_real) = get_series_f64_ptr(input)?;
    let len = input.len();
    let res = ta_tema(in_real_ptr, len, &kwargs);
    match res {
        Ok(out) => Ok(Float64Chunked::from_vec("".into(), out).into_series()),
        Err(ret_code) => ta_code2err(ret_code),
    }
}

// #[polars_expr(output_type=Float64)]
pub fn trima(inputs: &[Series], kwargs: TimePeriodKwargs) -> PolarsResult<Series> {
    let input = &mut cast_series_to_f64(&inputs[0])?;
    let (in_real_ptr, _in_real) = get_series_f64_ptr(input)?;
    let len = input.len();
    let res = ta_trima(in_real_ptr, len, &kwargs);
    match res {
        Ok(out) => Ok(Float64Chunked::from_vec("".into(), out).into_series()),
        Err(ret_code) => ta_code2err(ret_code),
    }
}

// #[polars_expr(output_type=Float64)]
pub fn wma(inputs: &[Series], kwargs: TimePeriodKwargs) -> PolarsResult<Series> {
    let input = &mut cast_series_to_f64(&inputs[0])?;
    let (in_real_ptr, _in_real) = get_series_f64_ptr(input)?;
    let len = input.len();
    let res = ta_wma(in_real_ptr, len, &kwargs);
    match res {
        Ok(out) => Ok(Float64Chunked::from_vec("".into(), out).into_series()),
        Err(ret_code) => ta_code2err(ret_code),
    }
}
