use crate::utils::{cast_series_to_f64, get_series_f64_ptr, ta_code2err};
use polars::prelude::*;
use talib::statistic::{
    ta_beta, ta_correl, ta_linearreg, ta_linearreg_angle, ta_linearreg_intercept,
    ta_linearreg_slope, ta_stddev, ta_tsf, ta_var, BetaKwargs, CorrelKwargs, LinearRegAngleKwargs,
    LinearRegInterceptKwargs, LinearRegKwargs, LinearRegSlopeKwargs, StdDevKwargs, TsfKwargs,
    VarKwargs,
};

// #[polars_expr(output_type=Float64)]
pub fn beta(inputs: &[Series], kwargs: BetaKwargs) -> PolarsResult<Series> {
    let real0 = &mut cast_series_to_f64(&inputs[0])?;
    let real1 = &mut cast_series_to_f64(&inputs[1])?;
    let (real0_ptr, _real0) = get_series_f64_ptr(real0)?;
    let (real1_ptr, _real1) = get_series_f64_ptr(real1)?;
    let len = real0.len();
    let res = ta_beta(real0_ptr, real1_ptr, len, &kwargs);
    match res {
        Ok(out) => Ok(Float64Chunked::from_vec("", out).into_series()),
        Err(ret_code) => ta_code2err(ret_code),
    }
}

// #[polars_expr(output_type=Float64)]
pub fn correl(inputs: &[Series], kwargs: CorrelKwargs) -> PolarsResult<Series> {
    let real0 = &mut cast_series_to_f64(&inputs[0])?;
    let real1 = &mut cast_series_to_f64(&inputs[1])?;
    let (real0_ptr, _real0) = get_series_f64_ptr(real0)?;
    let (real1_ptr, _real1) = get_series_f64_ptr(real1)?;
    let len = real0.len();
    let res = ta_correl(real0_ptr, real1_ptr, len, &kwargs);
    match res {
        Ok(out) => Ok(Float64Chunked::from_vec("", out).into_series()),
        Err(ret_code) => ta_code2err(ret_code),
    }
}

// #[polars_expr(output_type=Float64)]
pub fn linearreg(inputs: &[Series], kwargs: LinearRegKwargs) -> PolarsResult<Series> {
    let real = &mut cast_series_to_f64(&inputs[0])?;
    let (real_ptr, _real) = get_series_f64_ptr(real)?;
    let len = real.len();
    let res = ta_linearreg(real_ptr, len, &kwargs);
    match res {
        Ok(out) => Ok(Float64Chunked::from_vec("", out).into_series()),
        Err(ret_code) => ta_code2err(ret_code),
    }
}

// #[polars_expr(output_type=Float64)]
pub fn linearreg_angle(inputs: &[Series], kwargs: LinearRegAngleKwargs) -> PolarsResult<Series> {
    let real = &mut cast_series_to_f64(&inputs[0])?;
    let (real_ptr, _real) = get_series_f64_ptr(real)?;
    let len = real.len();
    let res = ta_linearreg_angle(real_ptr, len, &kwargs);
    match res {
        Ok(out) => Ok(Float64Chunked::from_vec("", out).into_series()),
        Err(ret_code) => ta_code2err(ret_code),
    }
}

// #[polars_expr(output_type=Float64)]
pub fn linearreg_intercept(
    inputs: &[Series],
    kwargs: LinearRegInterceptKwargs,
) -> PolarsResult<Series> {
    let real = &mut cast_series_to_f64(&inputs[0])?;
    let (real_ptr, _real) = get_series_f64_ptr(real)?;
    let len = real.len();
    let res = ta_linearreg_intercept(real_ptr, len, &kwargs);
    match res {
        Ok(out) => Ok(Float64Chunked::from_vec("", out).into_series()),
        Err(ret_code) => ta_code2err(ret_code),
    }
}

// #[polars_expr(output_type=Float64)]
pub fn linearreg_slope(inputs: &[Series], kwargs: LinearRegSlopeKwargs) -> PolarsResult<Series> {
    let real = &mut cast_series_to_f64(&inputs[0])?;
    let (real_ptr, _real) = get_series_f64_ptr(real)?;
    let len = real.len();
    let res = ta_linearreg_slope(real_ptr, len, &kwargs);
    match res {
        Ok(out) => Ok(Float64Chunked::from_vec("", out).into_series()),
        Err(ret_code) => ta_code2err(ret_code),
    }
}

// #[polars_expr(output_type=Float64)]
pub fn stddev(inputs: &[Series], kwargs: StdDevKwargs) -> PolarsResult<Series> {
    let real = &mut cast_series_to_f64(&inputs[0])?;
    let (real_ptr, _real) = get_series_f64_ptr(real)?;
    let len = real.len();
    let res = ta_stddev(real_ptr, len, &kwargs);
    match res {
        Ok(out) => {
            let out_ser = Float64Chunked::from_vec("", out);
            Ok(out_ser.into_series())
        }
        Err(ret_code) => ta_code2err(ret_code),
    }
}

// #[polars_expr(output_type=Float64)]
pub fn tsf(inputs: &[Series], kwargs: TsfKwargs) -> PolarsResult<Series> {
    let real = &mut cast_series_to_f64(&inputs[0])?;
    let (real_ptr, _real) = get_series_f64_ptr(real)?;
    let len = real.len();
    let res = ta_tsf(real_ptr, len, &kwargs);
    match res {
        Ok(out) => {
            let out_ser = Float64Chunked::from_vec("", out);
            Ok(out_ser.into_series())
        }
        Err(ret_code) => ta_code2err(ret_code),
    }
}

// #[polars_expr(output_type=Float64)]
pub fn var(inputs: &[Series], kwargs: VarKwargs) -> PolarsResult<Series> {
    let real = &mut cast_series_to_f64(&inputs[0])?;
    let (real_ptr, _real) = get_series_f64_ptr(real)?;
    let len = real.len();
    let res = ta_var(real_ptr, len, &kwargs);
    match res {
        Ok(out) => {
            let out_ser = Float64Chunked::from_vec("", out);
            Ok(out_ser.into_series())
        }
        Err(ret_code) => ta_code2err(ret_code),
    }
}
