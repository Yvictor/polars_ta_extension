use polars::prelude::*;
use pyo3_polars::derive::polars_expr;
use serde::Deserialize;
use std::fmt::Write;
// use talib_sys::{TA_EMA_Lookback, TA_Integer, TA_MAType_TA_MAType_EMA, TA_Real, TA_RetCode, TA_MA};

// #[derive(Deserialize)]
// pub struct SMAKwargs {
//     timeperiod: i32,
// }

// #[polars_expr(output_type=Float64)]
// fn ema2(inputs: &[Series], kwargs: SMAKwargs) -> PolarsResult<Series> {
//     let input = &mut inputs[0].to_float()?.rechunk();
//     let mut out_begin: TA_Integer = 0;
//     let mut out_size: TA_Integer = 0;
//     let mut out: Vec<TA_Real> = Vec::with_capacity(input.len());
//     let input_ptr: *const f64 = if input.has_validity() {
//         let input: Vec<f64> = input
//             .f64()?
//             .into_iter()
//             .map(|x| x.unwrap_or(std::f64::NAN))
//             .collect();
//         input.as_ptr()
//     } else {
//         input.as_single_ptr()? as *const f64
//     };
//     let lookback = unsafe { TA_EMA_Lookback(kwargs.timeperiod) as usize };
//     for _ in 0..lookback {
//         out.push(std::f64::NAN);
//     }
//     let ret_code = unsafe {
//         TA_MA(
//             0,
//             input.len() as i32 - 1,
//             input_ptr,
//             kwargs.timeperiod,
//             TA_MAType_TA_MAType_EMA,
//             &mut out_begin,
//             &mut out_size,
//             out[lookback..].as_mut_ptr(),
//         )
//     };
//     match ret_code {
//         TA_RetCode::TA_SUCCESS => {
//             unsafe {
//                 out.set_len((out_begin + out_size) as usize);
//             }
//             let out_ser = Float64Chunked::from_vec("", out);
//             Ok(out_ser.into_series())
//         }
//         _ => Err(PolarsError::ComputeError(
//             format!("Could not compute indicator, err: {:?}", ret_code).into(),
//         )),
//     }
// }

// #[polars_expr(output_type=Float64)]
// fn ema(inputs: &[Series], kwargs: SMAKwargs) -> PolarsResult<Series> {
//     let input = &inputs[0];
//     let mut out_begin: TA_Integer = 0;
//     let mut out_size: TA_Integer = 0;
//     // real = check_array(real)
//     let mut out: Vec<TA_Real> = Vec::with_capacity(input.len());
//     // let mut out_vec: Vec<Option<f64>> = Vec::with_capacity(input.len());
//     let input_vec: Vec<f64> = if input.has_validity() {
//         input.f64()?.into_no_null_iter().collect()
//     } else {
//         input
//             .f64()?
//             .into_iter()
//             .map(|x| x.unwrap_or(std::f64::NAN))
//             .collect()
//     };
//     unsafe {
//         let lookback = TA_EMA_Lookback(kwargs.timeperiod) as usize;
//         for _ in 0..lookback {
//             // out_vec.push(None);
//             out.push(std::f64::NAN);
//         }

//         let ret_code = TA_MA(
//             0,                            // index of the first close to use
//             input.len() as i32 - 1,       // index of the last close to use
//             input_vec.as_ptr(),           // pointer to the first element of the vector
//             kwargs.timeperiod,            // period of the sma
//             TA_MAType_TA_MAType_EMA,     // type of the MA, here forced to sma
//             &mut out_begin,               // set to index of the first close to have an sma value
//             &mut out_size,                // set to number of sma values computed
//             out[lookback..].as_mut_ptr(), // pointer to the first element of the output vector
//         );
//         match ret_code {
//             // Indicator was computed correctly, since the vector was filled by TA-lib C library,
//             // Rust doesn't know what is the new length of the vector, so we set it manually
//             // to the number of values returned by the TA_MA call
//             TA_RetCode::TA_SUCCESS => {
//                 out.set_len((out_begin + out_size) as usize);
//                 // for v in out.into_iter() {
//                 //     out_vec.push(Some(v));
//                 // }
//                 // Fill None values up to out_begin
//                 // for (i, v) in (out_begin..out_size+out_begin).zip(out.into_iter()) {
//                 //     out_vec[i as usize] = Some(v);
//                 // }
//                 let out_ser = Float64Chunked::from_vec("", out);
//                 // let mut ser = Series::new_null("", input.len());
//                 // ser[lookback..] = out;
//                 // ser.append(other)
//                 // Ok(Series::new("", &out_vec))
//                 Ok(out_ser.into_series())
//             }
//             // An error occured
//             _ => Err(PolarsError::ComputeError(
//                 format!("Could not compute indicator, err: {:?}", ret_code).into(),
//             )),
//         }
//     }
// }

/// Provide your own kwargs struct with the proper schema and accept that type
/// in your plugin expression.
#[derive(Deserialize)]
pub struct MyKwargs {
    float_arg: f64,
    integer_arg: i64,
    string_arg: String,
    boolean_arg: bool,
}

fn pig_latin_str(value: &str, output: &mut String) {
    if let Some(first_char) = value.chars().next() {
        write!(output, "{}{}ay", &value[1..], first_char).unwrap()
    }
}

#[polars_expr(output_type=Utf8)]
fn pig_latinnify(inputs: &[Series]) -> PolarsResult<Series> {
    let ca = inputs[0].utf8()?;
    let out: Utf8Chunked = ca.apply_to_buffer(pig_latin_str);
    Ok(out.into_series())
}

/// If you want to accept `kwargs`. You define a `kwargs` argument
/// on the second position in you plugin. You can provide any custom struct that is deserializable
/// with the pickle protocol (on the Rust side).
#[polars_expr(output_type=Utf8)]
fn append_kwargs(input: &[Series], kwargs: MyKwargs) -> PolarsResult<Series> {
    let input = &input[0];
    let input = input.cast(&DataType::Utf8)?;
    let ca = input.utf8().unwrap();

    Ok(ca
        .apply_to_buffer(|val, buf| {
            write!(
                buf,
                "{}-{}-{}-{}-{}",
                val, kwargs.float_arg, kwargs.integer_arg, kwargs.string_arg, kwargs.boolean_arg
            )
            .unwrap()
        })
        .into_series())
}
