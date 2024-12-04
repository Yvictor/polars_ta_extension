use crate::utils::{cast_series_to_f64, get_series_f64_ptr, ta_code2err};
use polars::prelude::*;
use talib::common::TimePeriodKwargs;
use talib::math::{
    ta_add, ta_div, ta_max, ta_maxindex, ta_min, ta_minindex, ta_minmax, ta_minmaxindex, ta_mult,
    ta_sub, ta_sum,
};

use talib::math::{
    ta_acos, ta_asin, ta_atan, ta_ceil, ta_cos, ta_cosh, ta_exp, ta_floor, ta_ln, ta_log10, ta_sin,
    ta_sinh, ta_sqrt, ta_tan, ta_tanh,
};

// #[polars_expr(output_type=Float64)]
pub fn add(inputs: &[Series]) -> PolarsResult<Series> {
    let input1 = &mut cast_series_to_f64(&inputs[0])?;
    let input2 = &mut cast_series_to_f64(&inputs[1])?;
    let (input1_ptr, _input1) = get_series_f64_ptr(input1)?;
    let (input2_ptr, _input2) = get_series_f64_ptr(input2)?;
    let len = input1.len();
    let res = ta_add(input1_ptr, input2_ptr, len);
    match res {
        Ok(out) => Ok(Float64Chunked::from_vec("".into(), out).into_series()),
        Err(ret_code) => ta_code2err(ret_code),
    }
}

// #[polars_expr(output_type=Float64)]
pub fn div(inputs: &[Series]) -> PolarsResult<Series> {
    let input1 = &mut cast_series_to_f64(&inputs[0])?;
    let input2 = &mut cast_series_to_f64(&inputs[1])?;
    let (input1_ptr, _input1) = get_series_f64_ptr(input1)?;
    let (input2_ptr, _input2) = get_series_f64_ptr(input2)?;
    let len = input1.len();
    let res = ta_div(input1_ptr, input2_ptr, len);
    match res {
        Ok(out) => Ok(Float64Chunked::from_vec("".into(), out).into_series()),
        Err(ret_code) => ta_code2err(ret_code),
    }
}

// #[polars_expr(output_type=Float64)]
pub fn max(inputs: &[Series], kwargs: TimePeriodKwargs) -> PolarsResult<Series> {
    let input = &mut cast_series_to_f64(&inputs[0])?;
    let (input_ptr, _input) = get_series_f64_ptr(input)?;
    let len = input.len();
    let res = ta_max(input_ptr, len, &kwargs);
    match res {
        Ok(out) => Ok(Float64Chunked::from_vec("".into(), out).into_series()),
        Err(ret_code) => ta_code2err(ret_code),
    }
}

// #[polars_expr(output_type=Int32)]
pub fn maxindex(inputs: &[Series], kwargs: TimePeriodKwargs) -> PolarsResult<Series> {
    let input = &mut cast_series_to_f64(&inputs[0])?;
    let (input_ptr, _input) = get_series_f64_ptr(input)?;
    let len = input.len();
    let res = ta_maxindex(input_ptr, len, &kwargs);
    match res {
        Ok(out) => Ok(Int32Chunked::from_vec("".into(), out).into_series()),
        Err(ret_code) => ta_code2err(ret_code),
    }
}

// #[polars_expr(output_type=Float64)]
pub fn min(inputs: &[Series], kwargs: TimePeriodKwargs) -> PolarsResult<Series> {
    let input = &mut cast_series_to_f64(&inputs[0])?;
    let (input_ptr, _input) = get_series_f64_ptr(input)?;
    let len = input.len();
    let res = ta_min(input_ptr, len, &kwargs);
    match res {
        Ok(out) => Ok(Float64Chunked::from_vec("".into(), out).into_series()),
        Err(ret_code) => ta_code2err(ret_code),
    }
}

// #[polars_expr(output_type=Int32)]
pub fn minindex(inputs: &[Series], kwargs: TimePeriodKwargs) -> PolarsResult<Series> {
    let input = &mut cast_series_to_f64(&inputs[0])?;
    let (input_ptr, _input) = get_series_f64_ptr(input)?;
    let len = input.len();
    let res = ta_minindex(input_ptr, len, &kwargs);
    match res {
        Ok(out) => Ok(Int32Chunked::from_vec("".into(), out).into_series()),
        Err(ret_code) => ta_code2err(ret_code),
    }
}
// pub
pub fn minmax_output(_: &[Field]) -> PolarsResult<Field> {
    let min = Field::new("min".into(), DataType::Float64);
    let max = Field::new("max".into(), DataType::Float64);
    let v: Vec<Field> = vec![min, max];
    Ok(Field::new("".into(), DataType::Struct(v)))
}

// #[polars_expr(output_type_func=minmax_output)]
pub fn minmax(inputs: &[Series], kwargs: TimePeriodKwargs) -> PolarsResult<Series> {
    let input = &mut cast_series_to_f64(&inputs[0])?;
    let (input_ptr, _input) = get_series_f64_ptr(input)?;

    let len = input.len();
    let res = ta_minmax(input_ptr, len, &kwargs);
    match res {
        Ok((outmin, outmax)) => {
            let min = Series::from_vec("min".into(), outmin);
            let max = Series::from_vec("max".into(), outmax);
            let out = Series::new("min_max".into(), &[min, max]);
            Ok(out.into_series())
        }
        Err(ret_code) => ta_code2err(ret_code),
    }
}
// pub
pub fn minmaxindex_output(_: &[Field]) -> PolarsResult<Field> {
    let minidx = Field::new("minidx".into(), DataType::Int32);
    let maxidx = Field::new("maxidx".into(), DataType::Int32);
    let v: Vec<Field> = vec![minidx, maxidx];
    Ok(Field::new("".into(), DataType::Struct(v)))
}

// #[polars_expr(output_type_func=minmaxindex_output)]
pub fn minmaxindex(inputs: &[Series], kwargs: TimePeriodKwargs) -> PolarsResult<Series> {
    let input = &mut cast_series_to_f64(&inputs[0])?;
    let (input_ptr, _input) = get_series_f64_ptr(input)?;

    let len = input.len();
    let res = ta_minmaxindex(input_ptr, len, &kwargs);
    match res {
        Ok((outminidx, outmaxidx)) => {
            let minidx = Series::from_vec("minidx".into(), outminidx);
            let maxidx = Series::from_vec("maxidx".into(), outmaxidx);
            let out = Series::new("minidx_maxidx".into(), &[minidx, maxidx]);
            Ok(out.into_series())
        }
        Err(ret_code) => ta_code2err(ret_code),
    }
}

// #[polars_expr(output_type=Float64)]
pub fn mult(inputs: &[Series]) -> PolarsResult<Series> {
    let input1 = &mut cast_series_to_f64(&inputs[0])?;
    let input2 = &mut cast_series_to_f64(&inputs[1])?;
    let (input1_ptr, _input1) = get_series_f64_ptr(input1)?;
    let (input2_ptr, _input2) = get_series_f64_ptr(input2)?;
    let len = input1.len();
    let res = ta_mult(input1_ptr, input2_ptr, len);
    match res {
        Ok(out) => Ok(Float64Chunked::from_vec("".into(), out).into_series()),
        Err(ret_code) => ta_code2err(ret_code),
    }
}

// #[polars_expr(output_type=Float64)]
pub fn sub(inputs: &[Series]) -> PolarsResult<Series> {
    let input1 = &mut cast_series_to_f64(&inputs[0])?;
    let input2 = &mut cast_series_to_f64(&inputs[1])?;
    let (input1_ptr, _input1) = get_series_f64_ptr(input1)?;
    let (input2_ptr, _input2) = get_series_f64_ptr(input2)?;
    let len = input1.len();
    let res = ta_sub(input1_ptr, input2_ptr, len);
    match res {
        Ok(out) => Ok(Float64Chunked::from_vec("".into(), out).into_series()),
        Err(ret_code) => ta_code2err(ret_code),
    }
}

// #[polars_expr(output_type=Float64)]
pub fn sum(inputs: &[Series], kwargs: TimePeriodKwargs) -> PolarsResult<Series> {
    let input = &mut cast_series_to_f64(&inputs[0])?;
    let (input_ptr, _input) = get_series_f64_ptr(input)?;

    let len = input.len();
    let res = ta_sum(input_ptr, len, &kwargs);
    match res {
        Ok(out) => Ok(Float64Chunked::from_vec("".into(), out).into_series()),
        Err(ret_code) => ta_code2err(ret_code),
    }
}

// #[polars_expr(output_type=Float64)]
pub fn acos(inputs: &[Series]) -> PolarsResult<Series> {
    let input = &mut cast_series_to_f64(&inputs[0])?;
    let (input_ptr, _input) = get_series_f64_ptr(input)?;

    let len = input.len();
    let res = ta_acos(input_ptr, len);
    match res {
        Ok(out) => Ok(Float64Chunked::from_vec("".into(), out).into_series()),
        Err(ret_code) => {
            println!("ret_code: {:?}", ret_code);
            ta_code2err(ret_code)
        }
    }
}

// #[polars_expr(output_type=Float64)]
pub fn asin(inputs: &[Series]) -> PolarsResult<Series> {
    let input = &mut cast_series_to_f64(&inputs[0])?;
    let (input_ptr, _input) = get_series_f64_ptr(input)?;

    let len = input.len();
    let res = ta_asin(input_ptr, len);
    match res {
        Ok(out) => Ok(Float64Chunked::from_vec("".into(), out).into_series()),
        Err(ret_code) => {
            println!("ret_code: {:?}", ret_code);
            ta_code2err(ret_code)
        }
    }
}

// #[polars_expr(output_type=Float64)]
pub fn atan(inputs: &[Series]) -> PolarsResult<Series> {
    let input = &mut cast_series_to_f64(&inputs[0])?;
    let (input_ptr, _input) = get_series_f64_ptr(input)?;

    let len = input.len();
    let res = ta_atan(input_ptr, len);
    match res {
        Ok(out) => Ok(Float64Chunked::from_vec("".into(), out).into_series()),
        Err(ret_code) => {
            println!("ret_code: {:?}", ret_code);
            ta_code2err(ret_code)
        }
    }
}

// #[polars_expr(output_type=Float64)]
pub fn ceil(inputs: &[Series]) -> PolarsResult<Series> {
    let input = &mut cast_series_to_f64(&inputs[0])?;
    let (input_ptr, _input) = get_series_f64_ptr(input)?;

    let len = input.len();
    let res = ta_ceil(input_ptr, len);
    match res {
        Ok(out) => Ok(Float64Chunked::from_vec("".into(), out).into_series()),
        Err(ret_code) => {
            println!("ret_code: {:?}", ret_code);
            ta_code2err(ret_code)
        }
    }
}

// #[polars_expr(output_type=Float64)]
pub fn cos(inputs: &[Series]) -> PolarsResult<Series> {
    let input = &mut cast_series_to_f64(&inputs[0])?;
    let (input_ptr, _input) = get_series_f64_ptr(input)?;

    let len = input.len();
    let res = ta_cos(input_ptr, len);
    match res {
        Ok(out) => Ok(Float64Chunked::from_vec("".into(), out).into_series()),
        Err(ret_code) => {
            println!("ret_code: {:?}", ret_code);
            ta_code2err(ret_code)
        }
    }
}

// #[polars_expr(output_type=Float64)]
pub fn cosh(inputs: &[Series]) -> PolarsResult<Series> {
    let input = &mut cast_series_to_f64(&inputs[0])?;
    let (input_ptr, _input) = get_series_f64_ptr(input)?;

    let len = input.len();
    let res = ta_cosh(input_ptr, len);
    match res {
        Ok(out) => Ok(Float64Chunked::from_vec("".into(), out).into_series()),
        Err(ret_code) => {
            println!("ret_code: {:?}", ret_code);
            ta_code2err(ret_code)
        }
    }
}

// #[polars_expr(output_type=Float64)]
pub fn exp(inputs: &[Series]) -> PolarsResult<Series> {
    let input = &mut cast_series_to_f64(&inputs[0])?;
    let (input_ptr, _input) = get_series_f64_ptr(input)?;

    let len = input.len();
    let res = ta_exp(input_ptr, len);
    match res {
        Ok(out) => Ok(Float64Chunked::from_vec("".into(), out).into_series()),
        Err(ret_code) => ta_code2err(ret_code),
    }
}

// #[polars_expr(output_type=Float64)]
pub fn floor(inputs: &[Series]) -> PolarsResult<Series> {
    let input = &mut cast_series_to_f64(&inputs[0])?;
    let (input_ptr, _input) = get_series_f64_ptr(input)?;

    let len = input.len();
    let res = ta_floor(input_ptr, len);
    match res {
        Ok(out) => Ok(Float64Chunked::from_vec("".into(), out).into_series()),
        Err(ret_code) => ta_code2err(ret_code),
    }
}

// #[polars_expr(output_type=Float64)]
pub fn ln(inputs: &[Series]) -> PolarsResult<Series> {
    let input = &mut cast_series_to_f64(&inputs[0])?;
    let (input_ptr, _input) = get_series_f64_ptr(input)?;

    let len = input.len();
    let res = ta_ln(input_ptr, len);
    match res {
        Ok(out) => Ok(Float64Chunked::from_vec("".into(), out).into_series()),
        Err(ret_code) => ta_code2err(ret_code),
    }
}

// #[polars_expr(output_type=Float64)]
pub fn log10(inputs: &[Series]) -> PolarsResult<Series> {
    let input = &mut cast_series_to_f64(&inputs[0])?;
    let (input_ptr, _input) = get_series_f64_ptr(input)?;

    let len = input.len();
    let res = ta_log10(input_ptr, len);
    match res {
        Ok(out) => Ok(Float64Chunked::from_vec("".into(), out).into_series()),
        Err(ret_code) => ta_code2err(ret_code),
    }
}

// #[polars_expr(output_type=Float64)]
pub fn sin(inputs: &[Series]) -> PolarsResult<Series> {
    let input = &mut cast_series_to_f64(&inputs[0])?;
    let (input_ptr, _input) = get_series_f64_ptr(input)?;

    let len = input.len();
    let res = ta_sin(input_ptr, len);
    match res {
        Ok(out) => Ok(Float64Chunked::from_vec("".into(), out).into_series()),
        Err(ret_code) => ta_code2err(ret_code),
    }
}

// #[polars_expr(output_type=Float64)]
pub fn sinh(inputs: &[Series]) -> PolarsResult<Series> {
    let input = &mut cast_series_to_f64(&inputs[0])?;
    let (input_ptr, _input) = get_series_f64_ptr(input)?;

    let len = input.len();
    let res = ta_sinh(input_ptr, len);
    match res {
        Ok(out) => Ok(Float64Chunked::from_vec("".into(), out).into_series()),
        Err(ret_code) => ta_code2err(ret_code),
    }
}

// #[polars_expr(output_type=Float64)]
pub fn sqrt(inputs: &[Series]) -> PolarsResult<Series> {
    let input = &mut cast_series_to_f64(&inputs[0])?;
    let (input_ptr, _input) = get_series_f64_ptr(input)?;

    let len = input.len();
    let res = ta_sqrt(input_ptr, len);
    match res {
        Ok(out) => Ok(Float64Chunked::from_vec("".into(), out).into_series()),
        Err(ret_code) => ta_code2err(ret_code),
    }
}

// #[polars_expr(output_type=Float64)]
pub fn tan(inputs: &[Series]) -> PolarsResult<Series> {
    let input = &mut cast_series_to_f64(&inputs[0])?;
    let (input_ptr, _input) = get_series_f64_ptr(input)?;

    let len = input.len();
    let res = ta_tan(input_ptr, len);
    match res {
        Ok(out) => Ok(Float64Chunked::from_vec("".into(), out).into_series()),
        Err(ret_code) => ta_code2err(ret_code),
    }
}

// #[polars_expr(output_type=Float64)]
pub fn tanh(inputs: &[Series]) -> PolarsResult<Series> {
    let input = &mut cast_series_to_f64(&inputs[0])?;
    let (input_ptr, _input) = get_series_f64_ptr(input)?;

    let len = input.len();
    let res = ta_tanh(input_ptr, len);
    match res {
        Ok(out) => Ok(Float64Chunked::from_vec("".into(), out).into_series()),
        Err(ret_code) => ta_code2err(ret_code),
    }
}
