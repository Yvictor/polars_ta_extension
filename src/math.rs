use crate::missing::{Masked, NoParams};
use crate::utils::{cast_series_to_f64, get_series_f64_ptr, ta_code2err};
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
fn add(inputs: &[Series], kwargs: Masked<NoParams>) -> PolarsResult<Series> {
    kwargs.apply(inputs, |_| add_unmasked(inputs))
}

fn add_unmasked(inputs: &[Series]) -> PolarsResult<Series> {
    let inputs = &crate::utils::broadcast_inputs(inputs)?;
    let input1 = &mut cast_series_to_f64(&inputs[0])?;
    let input2 = &mut cast_series_to_f64(&inputs[1])?;
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
fn div(inputs: &[Series], kwargs: Masked<NoParams>) -> PolarsResult<Series> {
    kwargs.apply(inputs, |_| div_unmasked(inputs))
}

fn div_unmasked(inputs: &[Series]) -> PolarsResult<Series> {
    let inputs = &crate::utils::broadcast_inputs(inputs)?;
    let input1 = &mut cast_series_to_f64(&inputs[0])?;
    let input2 = &mut cast_series_to_f64(&inputs[1])?;
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
fn max(inputs: &[Series], kwargs: Masked<TimePeriodKwargs>) -> PolarsResult<Series> {
    kwargs.apply(inputs, |kwargs| max_unmasked(inputs, kwargs))
}

fn max_unmasked(inputs: &[Series], kwargs: TimePeriodKwargs) -> PolarsResult<Series> {
    let inputs = &crate::utils::broadcast_inputs(inputs)?;
    let input = &mut cast_series_to_f64(&inputs[0])?;
    let (input_ptr, _input) = get_series_f64_ptr(input)?;
    let len = input.len();
    let res = ta_max(input_ptr, len, &kwargs);
    match res {
        Ok(out) => Ok(Float64Chunked::from_vec("", out).into_series()),
        Err(ret_code) => ta_code2err(ret_code),
    }
}

#[polars_expr(output_type=Int32)]
fn maxindex(inputs: &[Series], kwargs: Masked<TimePeriodKwargs>) -> PolarsResult<Series> {
    kwargs.apply(inputs, |kwargs| maxindex_unmasked(inputs, kwargs))
}

fn maxindex_unmasked(inputs: &[Series], kwargs: TimePeriodKwargs) -> PolarsResult<Series> {
    let inputs = &crate::utils::broadcast_inputs(inputs)?;
    let input = &mut cast_series_to_f64(&inputs[0])?;
    let (input_ptr, _input) = get_series_f64_ptr(input)?;
    let len = input.len();
    let res = ta_maxindex(input_ptr, len, &kwargs);
    match res {
        Ok(out) => Ok(Int32Chunked::from_vec("", out).into_series()),
        Err(ret_code) => ta_code2err(ret_code),
    }
}

#[polars_expr(output_type=Float64)]
fn min(inputs: &[Series], kwargs: Masked<TimePeriodKwargs>) -> PolarsResult<Series> {
    kwargs.apply(inputs, |kwargs| min_unmasked(inputs, kwargs))
}

fn min_unmasked(inputs: &[Series], kwargs: TimePeriodKwargs) -> PolarsResult<Series> {
    let inputs = &crate::utils::broadcast_inputs(inputs)?;
    let input = &mut cast_series_to_f64(&inputs[0])?;
    let (input_ptr, _input) = get_series_f64_ptr(input)?;
    let len = input.len();
    let res = ta_min(input_ptr, len, &kwargs);
    match res {
        Ok(out) => Ok(Float64Chunked::from_vec("", out).into_series()),
        Err(ret_code) => ta_code2err(ret_code),
    }
}

#[polars_expr(output_type=Int32)]
fn minindex(inputs: &[Series], kwargs: Masked<TimePeriodKwargs>) -> PolarsResult<Series> {
    kwargs.apply(inputs, |kwargs| minindex_unmasked(inputs, kwargs))
}

fn minindex_unmasked(inputs: &[Series], kwargs: TimePeriodKwargs) -> PolarsResult<Series> {
    let inputs = &crate::utils::broadcast_inputs(inputs)?;
    let input = &mut cast_series_to_f64(&inputs[0])?;
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
fn minmax(inputs: &[Series], kwargs: Masked<TimePeriodKwargs>) -> PolarsResult<Series> {
    kwargs.apply(inputs, |kwargs| minmax_unmasked(inputs, kwargs))
}

fn minmax_unmasked(inputs: &[Series], kwargs: TimePeriodKwargs) -> PolarsResult<Series> {
    let inputs = &crate::utils::broadcast_inputs(inputs)?;
    let input = &mut cast_series_to_f64(&inputs[0])?;
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
fn minmaxindex(inputs: &[Series], kwargs: Masked<TimePeriodKwargs>) -> PolarsResult<Series> {
    kwargs.apply(inputs, |kwargs| minmaxindex_unmasked(inputs, kwargs))
}

fn minmaxindex_unmasked(inputs: &[Series], kwargs: TimePeriodKwargs) -> PolarsResult<Series> {
    let inputs = &crate::utils::broadcast_inputs(inputs)?;
    let input = &mut cast_series_to_f64(&inputs[0])?;
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
fn mult(inputs: &[Series], kwargs: Masked<NoParams>) -> PolarsResult<Series> {
    kwargs.apply(inputs, |_| mult_unmasked(inputs))
}

fn mult_unmasked(inputs: &[Series]) -> PolarsResult<Series> {
    let inputs = &crate::utils::broadcast_inputs(inputs)?;
    let input1 = &mut cast_series_to_f64(&inputs[0])?;
    let input2 = &mut cast_series_to_f64(&inputs[1])?;
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
fn sub(inputs: &[Series], kwargs: Masked<NoParams>) -> PolarsResult<Series> {
    kwargs.apply(inputs, |_| sub_unmasked(inputs))
}

fn sub_unmasked(inputs: &[Series]) -> PolarsResult<Series> {
    let inputs = &crate::utils::broadcast_inputs(inputs)?;
    let input1 = &mut cast_series_to_f64(&inputs[0])?;
    let input2 = &mut cast_series_to_f64(&inputs[1])?;
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
fn sum(inputs: &[Series], kwargs: Masked<TimePeriodKwargs>) -> PolarsResult<Series> {
    kwargs.apply(inputs, |kwargs| sum_unmasked(inputs, kwargs))
}

fn sum_unmasked(inputs: &[Series], kwargs: TimePeriodKwargs) -> PolarsResult<Series> {
    let inputs = &crate::utils::broadcast_inputs(inputs)?;
    let input = &mut cast_series_to_f64(&inputs[0])?;
    let (input_ptr, _input) = get_series_f64_ptr(input)?;

    let len = input.len();
    let res = ta_sum(input_ptr, len, &kwargs);
    match res {
        Ok(out) => Ok(Float64Chunked::from_vec("", out).into_series()),
        Err(ret_code) => ta_code2err(ret_code),
    }
}

#[polars_expr(output_type=Float64)]
fn acos(inputs: &[Series], kwargs: Masked<NoParams>) -> PolarsResult<Series> {
    kwargs.apply(inputs, |_| acos_unmasked(inputs))
}

fn acos_unmasked(inputs: &[Series]) -> PolarsResult<Series> {
    let inputs = &crate::utils::broadcast_inputs(inputs)?;
    let input = &mut cast_series_to_f64(&inputs[0])?;
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
fn asin(inputs: &[Series], kwargs: Masked<NoParams>) -> PolarsResult<Series> {
    kwargs.apply(inputs, |_| asin_unmasked(inputs))
}

fn asin_unmasked(inputs: &[Series]) -> PolarsResult<Series> {
    let inputs = &crate::utils::broadcast_inputs(inputs)?;
    let input = &mut cast_series_to_f64(&inputs[0])?;
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
fn atan(inputs: &[Series], kwargs: Masked<NoParams>) -> PolarsResult<Series> {
    kwargs.apply(inputs, |_| atan_unmasked(inputs))
}

fn atan_unmasked(inputs: &[Series]) -> PolarsResult<Series> {
    let inputs = &crate::utils::broadcast_inputs(inputs)?;
    let input = &mut cast_series_to_f64(&inputs[0])?;
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
fn ceil(inputs: &[Series], kwargs: Masked<NoParams>) -> PolarsResult<Series> {
    kwargs.apply(inputs, |_| ceil_unmasked(inputs))
}

fn ceil_unmasked(inputs: &[Series]) -> PolarsResult<Series> {
    let inputs = &crate::utils::broadcast_inputs(inputs)?;
    let input = &mut cast_series_to_f64(&inputs[0])?;
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
fn cos(inputs: &[Series], kwargs: Masked<NoParams>) -> PolarsResult<Series> {
    kwargs.apply(inputs, |_| cos_unmasked(inputs))
}

fn cos_unmasked(inputs: &[Series]) -> PolarsResult<Series> {
    let inputs = &crate::utils::broadcast_inputs(inputs)?;
    let input = &mut cast_series_to_f64(&inputs[0])?;
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
fn cosh(inputs: &[Series], kwargs: Masked<NoParams>) -> PolarsResult<Series> {
    kwargs.apply(inputs, |_| cosh_unmasked(inputs))
}

fn cosh_unmasked(inputs: &[Series]) -> PolarsResult<Series> {
    let inputs = &crate::utils::broadcast_inputs(inputs)?;
    let input = &mut cast_series_to_f64(&inputs[0])?;
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
fn exp(inputs: &[Series], kwargs: Masked<NoParams>) -> PolarsResult<Series> {
    kwargs.apply(inputs, |_| exp_unmasked(inputs))
}

fn exp_unmasked(inputs: &[Series]) -> PolarsResult<Series> {
    let inputs = &crate::utils::broadcast_inputs(inputs)?;
    let input = &mut cast_series_to_f64(&inputs[0])?;
    let (input_ptr, _input) = get_series_f64_ptr(input)?;

    let len = input.len();
    let res = ta_exp(input_ptr, len);
    match res {
        Ok(out) => Ok(Float64Chunked::from_vec("", out).into_series()),
        Err(ret_code) => ta_code2err(ret_code),
    }
}

#[polars_expr(output_type=Float64)]
fn floor(inputs: &[Series], kwargs: Masked<NoParams>) -> PolarsResult<Series> {
    kwargs.apply(inputs, |_| floor_unmasked(inputs))
}

fn floor_unmasked(inputs: &[Series]) -> PolarsResult<Series> {
    let inputs = &crate::utils::broadcast_inputs(inputs)?;
    let input = &mut cast_series_to_f64(&inputs[0])?;
    let (input_ptr, _input) = get_series_f64_ptr(input)?;

    let len = input.len();
    let res = ta_floor(input_ptr, len);
    match res {
        Ok(out) => Ok(Float64Chunked::from_vec("", out).into_series()),
        Err(ret_code) => ta_code2err(ret_code),
    }
}

#[polars_expr(output_type=Float64)]
fn ln(inputs: &[Series], kwargs: Masked<NoParams>) -> PolarsResult<Series> {
    kwargs.apply(inputs, |_| ln_unmasked(inputs))
}

fn ln_unmasked(inputs: &[Series]) -> PolarsResult<Series> {
    let inputs = &crate::utils::broadcast_inputs(inputs)?;
    let input = &mut cast_series_to_f64(&inputs[0])?;
    let (input_ptr, _input) = get_series_f64_ptr(input)?;

    let len = input.len();
    let res = ta_ln(input_ptr, len);
    match res {
        Ok(out) => Ok(Float64Chunked::from_vec("", out).into_series()),
        Err(ret_code) => ta_code2err(ret_code),
    }
}

#[polars_expr(output_type=Float64)]
fn log10(inputs: &[Series], kwargs: Masked<NoParams>) -> PolarsResult<Series> {
    kwargs.apply(inputs, |_| log10_unmasked(inputs))
}

fn log10_unmasked(inputs: &[Series]) -> PolarsResult<Series> {
    let inputs = &crate::utils::broadcast_inputs(inputs)?;
    let input = &mut cast_series_to_f64(&inputs[0])?;
    let (input_ptr, _input) = get_series_f64_ptr(input)?;

    let len = input.len();
    let res = ta_log10(input_ptr, len);
    match res {
        Ok(out) => Ok(Float64Chunked::from_vec("", out).into_series()),
        Err(ret_code) => ta_code2err(ret_code),
    }
}

#[polars_expr(output_type=Float64)]
fn sin(inputs: &[Series], kwargs: Masked<NoParams>) -> PolarsResult<Series> {
    kwargs.apply(inputs, |_| sin_unmasked(inputs))
}

fn sin_unmasked(inputs: &[Series]) -> PolarsResult<Series> {
    let inputs = &crate::utils::broadcast_inputs(inputs)?;
    let input = &mut cast_series_to_f64(&inputs[0])?;
    let (input_ptr, _input) = get_series_f64_ptr(input)?;

    let len = input.len();
    let res = ta_sin(input_ptr, len);
    match res {
        Ok(out) => Ok(Float64Chunked::from_vec("", out).into_series()),
        Err(ret_code) => ta_code2err(ret_code),
    }
}

#[polars_expr(output_type=Float64)]
fn sinh(inputs: &[Series], kwargs: Masked<NoParams>) -> PolarsResult<Series> {
    kwargs.apply(inputs, |_| sinh_unmasked(inputs))
}

fn sinh_unmasked(inputs: &[Series]) -> PolarsResult<Series> {
    let inputs = &crate::utils::broadcast_inputs(inputs)?;
    let input = &mut cast_series_to_f64(&inputs[0])?;
    let (input_ptr, _input) = get_series_f64_ptr(input)?;

    let len = input.len();
    let res = ta_sinh(input_ptr, len);
    match res {
        Ok(out) => Ok(Float64Chunked::from_vec("", out).into_series()),
        Err(ret_code) => ta_code2err(ret_code),
    }
}

#[polars_expr(output_type=Float64)]
fn sqrt(inputs: &[Series], kwargs: Masked<NoParams>) -> PolarsResult<Series> {
    kwargs.apply(inputs, |_| sqrt_unmasked(inputs))
}

fn sqrt_unmasked(inputs: &[Series]) -> PolarsResult<Series> {
    let inputs = &crate::utils::broadcast_inputs(inputs)?;
    let input = &mut cast_series_to_f64(&inputs[0])?;
    let (input_ptr, _input) = get_series_f64_ptr(input)?;

    let len = input.len();
    let res = ta_sqrt(input_ptr, len);
    match res {
        Ok(out) => Ok(Float64Chunked::from_vec("", out).into_series()),
        Err(ret_code) => ta_code2err(ret_code),
    }
}

#[polars_expr(output_type=Float64)]
fn tan(inputs: &[Series], kwargs: Masked<NoParams>) -> PolarsResult<Series> {
    kwargs.apply(inputs, |_| tan_unmasked(inputs))
}

fn tan_unmasked(inputs: &[Series]) -> PolarsResult<Series> {
    let inputs = &crate::utils::broadcast_inputs(inputs)?;
    let input = &mut cast_series_to_f64(&inputs[0])?;
    let (input_ptr, _input) = get_series_f64_ptr(input)?;

    let len = input.len();
    let res = ta_tan(input_ptr, len);
    match res {
        Ok(out) => Ok(Float64Chunked::from_vec("", out).into_series()),
        Err(ret_code) => ta_code2err(ret_code),
    }
}

#[polars_expr(output_type=Float64)]
fn tanh(inputs: &[Series], kwargs: Masked<NoParams>) -> PolarsResult<Series> {
    kwargs.apply(inputs, |_| tanh_unmasked(inputs))
}

fn tanh_unmasked(inputs: &[Series]) -> PolarsResult<Series> {
    let inputs = &crate::utils::broadcast_inputs(inputs)?;
    let input = &mut cast_series_to_f64(&inputs[0])?;
    let (input_ptr, _input) = get_series_f64_ptr(input)?;

    let len = input.len();
    let res = ta_tanh(input_ptr, len);
    match res {
        Ok(out) => Ok(Float64Chunked::from_vec("", out).into_series()),
        Err(ret_code) => ta_code2err(ret_code),
    }
}
