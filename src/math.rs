use crate::utils::{get_series_f64_ptr, ta_code2err};
use polars::prelude::*;
use pyo3_polars::derive::polars_expr;
use talib::common::TimePeriodKwargs;
use talib::math::{
    ta_add, ta_div, ta_max, ta_maxindex, ta_min, ta_minindex, ta_minmax, ta_minmaxindex, ta_mult,
    ta_sub, ta_sum,
};

use talib::math::{
    ta_acos, ta_asin, ta_atan, ta_ceil, ta_cos, ta_cosh, ta_exp, ta_floor, ta_ln, ta_log10, ta_sin,
    ta_sinh, ta_sqrt, ta_tan, ta_tanh,
};

#[polars_expr(output_type=Float64)]
fn add(inputs: &[Series]) -> PolarsResult<Series> {
    let input1 = &mut inputs[0].to_float()?.rechunk();
    let input2 = &mut inputs[1].to_float()?.rechunk();
    let (input1_ptr, _input1) = get_series_f64_ptr(input1)?;
    let (input2_ptr, _input2) = get_series_f64_ptr(input2)?;
    let len = input1.len();
    let res = ta_add(input1_ptr, input2_ptr, len);
    match res {
        Ok(out) => Ok(Float64Chunked::from_vec("", out).into_series()),
        Err(ret_code) => ta_code2err(ret_code),
    }
}

#[polars_expr(output_type=Float64)]
fn div(inputs: &[Series]) -> PolarsResult<Series> {
    let input1 = &mut inputs[0].to_float()?.rechunk();
    let input2 = &mut inputs[1].to_float()?.rechunk();
    let (input1_ptr, _input1) = get_series_f64_ptr(input1)?;
    let (input2_ptr, _input2) = get_series_f64_ptr(input2)?;
    let len = input1.len();
    let res = ta_div(input1_ptr, input2_ptr, len);
    match res {
        Ok(out) => Ok(Float64Chunked::from_vec("", out).into_series()),
        Err(ret_code) => ta_code2err(ret_code),
    }
}

#[polars_expr(output_type=Float64)]
fn max(inputs: &[Series], kwargs: TimePeriodKwargs) -> PolarsResult<Series> {
    let input = &mut inputs[0].to_float()?.rechunk();
    let (input_ptr, _input) = get_series_f64_ptr(input)?;
    let len = input.len();
    let res = ta_max(input_ptr, len, &kwargs);
    match res {
        Ok(out) => Ok(Float64Chunked::from_vec("", out).into_series()),
        Err(ret_code) => ta_code2err(ret_code),
    }
}

#[polars_expr(output_type=Int32)]
fn maxindex(inputs: &[Series], kwargs: TimePeriodKwargs) -> PolarsResult<Series> {
    let input = &mut inputs[0].to_float()?.rechunk();
    let (input_ptr, _input) = get_series_f64_ptr(input)?;
    let len = input.len();
    let res = ta_maxindex(input_ptr, len, &kwargs);
    match res {
        Ok(out) => Ok(Int32Chunked::from_vec("", out).into_series()),
        Err(ret_code) => ta_code2err(ret_code),
    }
}

#[polars_expr(output_type=Float64)]
fn min(inputs: &[Series], kwargs: TimePeriodKwargs) -> PolarsResult<Series> {
    let input = &mut inputs[0].to_float()?.rechunk();
    let (input_ptr, _input) = get_series_f64_ptr(input)?;
    let len = input.len();
    let res = ta_min(input_ptr, len, &kwargs);
    match res {
        Ok(out) => Ok(Float64Chunked::from_vec("", out).into_series()),
        Err(ret_code) => ta_code2err(ret_code),
    }
}

#[polars_expr(output_type=Int32)]
fn minindex(inputs: &[Series], kwargs: TimePeriodKwargs) -> PolarsResult<Series> {
    let input = &mut inputs[0].to_float()?.rechunk();
    let (input_ptr, _input) = get_series_f64_ptr(input)?;
    let len = input.len();
    let res = ta_minindex(input_ptr, len, &kwargs);
    match res {
        Ok(out) => Ok(Int32Chunked::from_vec("", out).into_series()),
        Err(ret_code) => ta_code2err(ret_code),
    }
}

pub fn minmax_output(_: &[Field]) -> PolarsResult<Field> {
    let min = Field::new("min", DataType::Float64);
    let max = Field::new("max", DataType::Float64);
    let v: Vec<Field> = vec![min, max];
    Ok(Field::new("", DataType::Struct(v)))
}

#[polars_expr(output_type_func=minmax_output)]
fn minmax(inputs: &[Series], kwargs: TimePeriodKwargs) -> PolarsResult<Series> {
    let input = &mut inputs[0].to_float()?.rechunk();
    let (input_ptr, _input) = get_series_f64_ptr(input)?;

    let len = input.len();
    let res = ta_minmax(input_ptr, len, &kwargs);
    match res {
        Ok((outmin, outmax)) => {
            let min = Series::from_vec("min", outmin);
            let max = Series::from_vec("max", outmax);
            let out = StructChunked::new("", &[min, max])?;
            Ok(out.into_series())
        }
        Err(ret_code) => ta_code2err(ret_code),
    }
}

pub fn minmaxindex_output(_: &[Field]) -> PolarsResult<Field> {
    let minidx = Field::new("minidx", DataType::Int32);
    let maxidx = Field::new("maxidx", DataType::Int32);
    let v: Vec<Field> = vec![minidx, maxidx];
    Ok(Field::new("", DataType::Struct(v)))
}

#[polars_expr(output_type_func=minmaxindex_output)]
fn minmaxindex(inputs: &[Series], kwargs: TimePeriodKwargs) -> PolarsResult<Series> {
    let input = &mut inputs[0].to_float()?.rechunk();
    let (input_ptr, _input) = get_series_f64_ptr(input)?;

    let len = input.len();
    let res = ta_minmaxindex(input_ptr, len, &kwargs);
    match res {
        Ok((outminidx, outmaxidx)) => {
            let minidx = Series::from_vec("minidx", outminidx);
            let maxidx = Series::from_vec("maxidx", outmaxidx);
            let out = StructChunked::new("", &[minidx, maxidx])?;
            Ok(out.into_series())
        }
        Err(ret_code) => ta_code2err(ret_code),
    }
}

#[polars_expr(output_type=Float64)]
fn mult(inputs: &[Series]) -> PolarsResult<Series> {
    let input1 = &mut inputs[0].to_float()?.rechunk();
    let input2 = &mut inputs[1].to_float()?.rechunk();
    let (input1_ptr, _input1) = get_series_f64_ptr(input1)?;
    let (input2_ptr, _input2) = get_series_f64_ptr(input2)?;
    let len = input1.len();
    let res = ta_mult(input1_ptr, input2_ptr, len);
    match res {
        Ok(out) => Ok(Float64Chunked::from_vec("", out).into_series()),
        Err(ret_code) => ta_code2err(ret_code),
    }
}

#[polars_expr(output_type=Float64)]
fn sub(inputs: &[Series]) -> PolarsResult<Series> {
    let input1 = &mut inputs[0].to_float()?.rechunk();
    let input2 = &mut inputs[1].to_float()?.rechunk();
    let (input1_ptr, _input1) = get_series_f64_ptr(input1)?;
    let (input2_ptr, _input2) = get_series_f64_ptr(input2)?;
    let len = input1.len();
    let res = ta_sub(input1_ptr, input2_ptr, len);
    match res {
        Ok(out) => Ok(Float64Chunked::from_vec("", out).into_series()),
        Err(ret_code) => ta_code2err(ret_code),
    }
}

#[polars_expr(output_type=Float64)]
fn sum(inputs: &[Series], kwargs: TimePeriodKwargs) -> PolarsResult<Series> {
    let input = &mut inputs[0].to_float()?.rechunk();
    let (input_ptr, _input) = get_series_f64_ptr(input)?;

    let len = input.len();
    let res = ta_sum(input_ptr, len, &kwargs);
    match res {
        Ok(out) => Ok(Float64Chunked::from_vec("", out).into_series()),
        Err(ret_code) => ta_code2err(ret_code),
    }
}

#[polars_expr(output_type=Float64)]
fn acos(inputs: &[Series]) -> PolarsResult<Series> {
    let input = &mut inputs[0].to_float()?.rechunk();
    let (input_ptr, _input) = get_series_f64_ptr(input)?;

    let len = input.len();
    let res = ta_acos(input_ptr, len);
    match res {
        Ok(out) => Ok(Float64Chunked::from_vec("", out).into_series()),
        Err(ret_code) => {
            println!("ret_code: {:?}", ret_code);
            ta_code2err(ret_code)
        }
    }
}

#[polars_expr(output_type=Float64)]
fn asin(inputs: &[Series]) -> PolarsResult<Series> {
    let input = &mut inputs[0].to_float()?.rechunk();
    let (input_ptr, _input) = get_series_f64_ptr(input)?;

    let len = input.len();
    let res = ta_asin(input_ptr, len);
    match res {
        Ok(out) => Ok(Float64Chunked::from_vec("", out).into_series()),
        Err(ret_code) => {
            println!("ret_code: {:?}", ret_code);
            ta_code2err(ret_code)
        }
    }
}

#[polars_expr(output_type=Float64)]
fn atan(inputs: &[Series]) -> PolarsResult<Series> {
    let input = &mut inputs[0].to_float()?.rechunk();
    let (input_ptr, _input) = get_series_f64_ptr(input)?;

    let len = input.len();
    let res = ta_atan(input_ptr, len);
    match res {
        Ok(out) => Ok(Float64Chunked::from_vec("", out).into_series()),
        Err(ret_code) => {
            println!("ret_code: {:?}", ret_code);
            ta_code2err(ret_code)
        }
    }
}

#[polars_expr(output_type=Float64)]
fn ceil(inputs: &[Series]) -> PolarsResult<Series> {
    let input = &mut inputs[0].to_float()?.rechunk();
    let (input_ptr, _input) = get_series_f64_ptr(input)?;

    let len = input.len();
    let res = ta_ceil(input_ptr, len);
    match res {
        Ok(out) => Ok(Float64Chunked::from_vec("", out).into_series()),
        Err(ret_code) => {
            println!("ret_code: {:?}", ret_code);
            ta_code2err(ret_code)
        }
    }
}

#[polars_expr(output_type=Float64)]
fn cos(inputs: &[Series]) -> PolarsResult<Series> {
    let input = &mut inputs[0].to_float()?.rechunk();
    let (input_ptr, _input) = get_series_f64_ptr(input)?;

    let len = input.len();
    let res = ta_cos(input_ptr, len);
    match res {
        Ok(out) => Ok(Float64Chunked::from_vec("", out).into_series()),
        Err(ret_code) => {
            println!("ret_code: {:?}", ret_code);
            ta_code2err(ret_code)
        }
    }
}

#[polars_expr(output_type=Float64)]
fn cosh(inputs: &[Series]) -> PolarsResult<Series> {
    let input = &mut inputs[0].to_float()?.rechunk();
    let (input_ptr, _input) = get_series_f64_ptr(input)?;

    let len = input.len();
    let res = ta_cosh(input_ptr, len);
    match res {
        Ok(out) => Ok(Float64Chunked::from_vec("", out).into_series()),
        Err(ret_code) => {
            println!("ret_code: {:?}", ret_code);
            ta_code2err(ret_code)
        }
    }
}

#[polars_expr(output_type=Float64)]
fn exp(inputs: &[Series]) -> PolarsResult<Series> {
    let input = &mut inputs[0].to_float()?.rechunk();
    let (input_ptr, _input) = get_series_f64_ptr(input)?;

    let len = input.len();
    let res = ta_exp(input_ptr, len);
    match res {
        Ok(out) => Ok(Float64Chunked::from_vec("", out).into_series()),
        Err(ret_code) => ta_code2err(ret_code),
    }
}

#[polars_expr(output_type=Float64)]
fn floor(inputs: &[Series]) -> PolarsResult<Series> {
    let input = &mut inputs[0].to_float()?.rechunk();
    let (input_ptr, _input) = get_series_f64_ptr(input)?;

    let len = input.len();
    let res = ta_floor(input_ptr, len);
    match res {
        Ok(out) => Ok(Float64Chunked::from_vec("", out).into_series()),
        Err(ret_code) => ta_code2err(ret_code),
    }
}

#[polars_expr(output_type=Float64)]
fn ln(inputs: &[Series]) -> PolarsResult<Series> {
    let input = &mut inputs[0].to_float()?.rechunk();
    let (input_ptr, _input) = get_series_f64_ptr(input)?;

    let len = input.len();
    let res = ta_ln(input_ptr, len);
    match res {
        Ok(out) => Ok(Float64Chunked::from_vec("", out).into_series()),
        Err(ret_code) => ta_code2err(ret_code),
    }
}

#[polars_expr(output_type=Float64)]
fn log10(inputs: &[Series]) -> PolarsResult<Series> {
    let input = &mut inputs[0].to_float()?.rechunk();
    let (input_ptr, _input) = get_series_f64_ptr(input)?;

    let len = input.len();
    let res = ta_log10(input_ptr, len);
    match res {
        Ok(out) => Ok(Float64Chunked::from_vec("", out).into_series()),
        Err(ret_code) => ta_code2err(ret_code),
    }
}

#[polars_expr(output_type=Float64)]
fn sin(inputs: &[Series]) -> PolarsResult<Series> {
    let input = &mut inputs[0].to_float()?.rechunk();
    let (input_ptr, _input) = get_series_f64_ptr(input)?;

    let len = input.len();
    let res = ta_sin(input_ptr, len);
    match res {
        Ok(out) => Ok(Float64Chunked::from_vec("", out).into_series()),
        Err(ret_code) => ta_code2err(ret_code),
    }
}

#[polars_expr(output_type=Float64)]
fn sinh(inputs: &[Series]) -> PolarsResult<Series> {
    let input = &mut inputs[0].to_float()?.rechunk();
    let (input_ptr, _input) = get_series_f64_ptr(input)?;

    let len = input.len();
    let res = ta_sinh(input_ptr, len);
    match res {
        Ok(out) => Ok(Float64Chunked::from_vec("", out).into_series()),
        Err(ret_code) => ta_code2err(ret_code),
    }
}

#[polars_expr(output_type=Float64)]
fn sqrt(inputs: &[Series]) -> PolarsResult<Series> {
    let input = &mut inputs[0].to_float()?.rechunk();
    let (input_ptr, _input) = get_series_f64_ptr(input)?;

    let len = input.len();
    let res = ta_sqrt(input_ptr, len);
    match res {
        Ok(out) => Ok(Float64Chunked::from_vec("", out).into_series()),
        Err(ret_code) => ta_code2err(ret_code),
    }
}

#[polars_expr(output_type=Float64)]
fn tan(inputs: &[Series]) -> PolarsResult<Series> {
    let input = &mut inputs[0].to_float()?.rechunk();
    let (input_ptr, _input) = get_series_f64_ptr(input)?;

    let len = input.len();
    let res = ta_tan(input_ptr, len);
    match res {
        Ok(out) => Ok(Float64Chunked::from_vec("", out).into_series()),
        Err(ret_code) => ta_code2err(ret_code),
    }
}

#[polars_expr(output_type=Float64)]
fn tanh(inputs: &[Series]) -> PolarsResult<Series> {
    let input = &mut inputs[0].to_float()?.rechunk();
    let (input_ptr, _input) = get_series_f64_ptr(input)?;

    let len = input.len();
    let res = ta_tanh(input_ptr, len);
    match res {
        Ok(out) => Ok(Float64Chunked::from_vec("", out).into_series()),
        Err(ret_code) => ta_code2err(ret_code),
    }
}
