use crate::missing::{Masked, NoParams};
use crate::utils::{cast_series_to_f64, get_series_f64_ptr, ta_code2err};
use polars::prelude::*;
use pyo3_polars::derive::polars_expr;
use talib::pattern::ta_cdlxsidegap3methods;
use talib::pattern::CDLKwargs;
use talib::pattern::{ta_cdl2crows, ta_cdl3blackcrows, ta_cdl3inside};
use talib::pattern::{ta_cdl3linestrike, ta_cdl3outside, ta_cdl3starsinsouth};
use talib::pattern::{ta_cdl3whitesoldiers, ta_cdlabandonedbaby, ta_cdladvanceblock};
use talib::pattern::{ta_cdlbelthold, ta_cdlbreakaway, ta_cdlclosingmarubozu};
use talib::pattern::{ta_cdlconcealbabyswall, ta_cdlcounterattack, ta_cdldarkcloudcover};
use talib::pattern::{ta_cdldoji, ta_cdldojistar, ta_cdldragonflydoji};
use talib::pattern::{ta_cdlengulfing, ta_cdlrisefall3methods};
use talib::pattern::{ta_cdleveningdojistar, ta_cdleveningstar};
use talib::pattern::{ta_cdlgapsidesidewhite, ta_cdlgravestonedoji, ta_cdlhammer};
use talib::pattern::{ta_cdlhangingman, ta_cdlharami, ta_cdlharamicross};
use talib::pattern::{ta_cdlhighwave, ta_cdlhikkake, ta_cdlhikkakemod};
use talib::pattern::{ta_cdlhomingpigeon, ta_cdlidentical3crows, ta_cdlinneck};
use talib::pattern::{ta_cdlinvertedhammer, ta_cdlkicking, ta_cdlkickingbylength};
use talib::pattern::{ta_cdlladderbottom, ta_cdllongleggeddoji, ta_cdllongline};
use talib::pattern::{ta_cdlmarubozu, ta_cdlmatchinglow, ta_cdlmathold};
use talib::pattern::{ta_cdlmorningdojistar, ta_cdlmorningstar, ta_cdlonneck};
use talib::pattern::{ta_cdlpiercing, ta_cdlrickshawman};
use talib::pattern::{ta_cdlseparatinglines, ta_cdlshootingstar, ta_cdlshortline};
use talib::pattern::{ta_cdlspinningtop, ta_cdlstalledpattern, ta_cdlsticksandwich};
use talib::pattern::{ta_cdltakuri, ta_cdltasukigap, ta_cdlthrusting};
use talib::pattern::{ta_cdltristar, ta_cdlunique3river, ta_cdlupsidegap2crows};

#[polars_expr(output_type=Int32)]
fn cdl2crows(inputs: &[Series], kwargs: Masked<NoParams>) -> PolarsResult<Series> {
    kwargs.apply(inputs, |_| cdl2crows_unmasked(inputs))
}

fn cdl2crows_unmasked(inputs: &[Series]) -> PolarsResult<Series> {
    let inputs = &crate::utils::broadcast_inputs(inputs)?;
    let open = &mut cast_series_to_f64(&inputs[0])?;
    let high = &mut cast_series_to_f64(&inputs[1])?;
    let low = &mut cast_series_to_f64(&inputs[2])?;
    let close = &mut cast_series_to_f64(&inputs[3])?;
    let (open_ptr, _open) = get_series_f64_ptr(open)?;
    let (high_ptr, _high) = get_series_f64_ptr(high)?;
    let (low_ptr, _low) = get_series_f64_ptr(low)?;
    let (close_ptr, _close) = get_series_f64_ptr(close)?;
    let len = close.len();
    let res = ta_cdl2crows(open_ptr, high_ptr, low_ptr, close_ptr, len);
    match res {
        Ok(out) => Ok(Int32Chunked::from_vec("", out).into_series()),
        Err(ret_code) => ta_code2err(ret_code),
    }
}

#[polars_expr(output_type=Int32)]
fn cdl3blackcrows(inputs: &[Series], kwargs: Masked<NoParams>) -> PolarsResult<Series> {
    kwargs.apply(inputs, |_| cdl3blackcrows_unmasked(inputs))
}

fn cdl3blackcrows_unmasked(inputs: &[Series]) -> PolarsResult<Series> {
    let inputs = &crate::utils::broadcast_inputs(inputs)?;
    let open = &mut cast_series_to_f64(&inputs[0])?;
    let high = &mut cast_series_to_f64(&inputs[1])?;
    let low = &mut cast_series_to_f64(&inputs[2])?;
    let close = &mut cast_series_to_f64(&inputs[3])?;
    let (open_ptr, _open) = get_series_f64_ptr(open)?;
    let (high_ptr, _high) = get_series_f64_ptr(high)?;
    let (low_ptr, _low) = get_series_f64_ptr(low)?;
    let (close_ptr, _close) = get_series_f64_ptr(close)?;
    let len = close.len();
    let res = ta_cdl3blackcrows(open_ptr, high_ptr, low_ptr, close_ptr, len);
    match res {
        Ok(out) => Ok(Int32Chunked::from_vec("", out).into_series()),
        Err(ret_code) => ta_code2err(ret_code),
    }
}

#[polars_expr(output_type=Int32)]
fn cdl3inside(inputs: &[Series], kwargs: Masked<NoParams>) -> PolarsResult<Series> {
    kwargs.apply(inputs, |_| cdl3inside_unmasked(inputs))
}

fn cdl3inside_unmasked(inputs: &[Series]) -> PolarsResult<Series> {
    let inputs = &crate::utils::broadcast_inputs(inputs)?;
    let open = &mut cast_series_to_f64(&inputs[0])?;
    let high = &mut cast_series_to_f64(&inputs[1])?;
    let low = &mut cast_series_to_f64(&inputs[2])?;
    let close = &mut cast_series_to_f64(&inputs[3])?;
    let (open_ptr, _open) = get_series_f64_ptr(open)?;
    let (high_ptr, _high) = get_series_f64_ptr(high)?;
    let (low_ptr, _low) = get_series_f64_ptr(low)?;
    let (close_ptr, _close) = get_series_f64_ptr(close)?;
    let len = close.len();
    let res = ta_cdl3inside(open_ptr, high_ptr, low_ptr, close_ptr, len);
    match res {
        Ok(out) => Ok(Int32Chunked::from_vec("", out).into_series()),
        Err(ret_code) => ta_code2err(ret_code),
    }
}

#[polars_expr(output_type=Int32)]
fn cdl3linestrike(inputs: &[Series], kwargs: Masked<NoParams>) -> PolarsResult<Series> {
    kwargs.apply(inputs, |_| cdl3linestrike_unmasked(inputs))
}

fn cdl3linestrike_unmasked(inputs: &[Series]) -> PolarsResult<Series> {
    let inputs = &crate::utils::broadcast_inputs(inputs)?;
    let open = &mut cast_series_to_f64(&inputs[0])?;
    let high = &mut cast_series_to_f64(&inputs[1])?;
    let low = &mut cast_series_to_f64(&inputs[2])?;
    let close = &mut cast_series_to_f64(&inputs[3])?;
    let (open_ptr, _open) = get_series_f64_ptr(open)?;
    let (high_ptr, _high) = get_series_f64_ptr(high)?;
    let (low_ptr, _low) = get_series_f64_ptr(low)?;
    let (close_ptr, _close) = get_series_f64_ptr(close)?;
    let len = close.len();
    let res = ta_cdl3linestrike(open_ptr, high_ptr, low_ptr, close_ptr, len);
    match res {
        Ok(out) => Ok(Int32Chunked::from_vec("", out).into_series()),
        Err(ret_code) => ta_code2err(ret_code),
    }
}

#[polars_expr(output_type=Int32)]
fn cdl3outside(inputs: &[Series], kwargs: Masked<NoParams>) -> PolarsResult<Series> {
    kwargs.apply(inputs, |_| cdl3outside_unmasked(inputs))
}

fn cdl3outside_unmasked(inputs: &[Series]) -> PolarsResult<Series> {
    let inputs = &crate::utils::broadcast_inputs(inputs)?;
    let open = &mut cast_series_to_f64(&inputs[0])?;
    let high = &mut cast_series_to_f64(&inputs[1])?;
    let low = &mut cast_series_to_f64(&inputs[2])?;
    let close = &mut cast_series_to_f64(&inputs[3])?;
    let (open_ptr, _open) = get_series_f64_ptr(open)?;
    let (high_ptr, _high) = get_series_f64_ptr(high)?;
    let (low_ptr, _low) = get_series_f64_ptr(low)?;
    let (close_ptr, _close) = get_series_f64_ptr(close)?;
    let len = close.len();
    let res = ta_cdl3outside(open_ptr, high_ptr, low_ptr, close_ptr, len);
    match res {
        Ok(out) => Ok(Int32Chunked::from_vec("", out).into_series()),
        Err(ret_code) => ta_code2err(ret_code),
    }
}

#[polars_expr(output_type=Int32)]
fn cdl3starsinsouth(inputs: &[Series], kwargs: Masked<NoParams>) -> PolarsResult<Series> {
    kwargs.apply(inputs, |_| cdl3starsinsouth_unmasked(inputs))
}

fn cdl3starsinsouth_unmasked(inputs: &[Series]) -> PolarsResult<Series> {
    let inputs = &crate::utils::broadcast_inputs(inputs)?;
    let open = &mut cast_series_to_f64(&inputs[0])?;
    let high = &mut cast_series_to_f64(&inputs[1])?;
    let low = &mut cast_series_to_f64(&inputs[2])?;
    let close = &mut cast_series_to_f64(&inputs[3])?;

    let (open_ptr, _open) = get_series_f64_ptr(open)?;
    let (high_ptr, _high) = get_series_f64_ptr(high)?;
    let (low_ptr, _low) = get_series_f64_ptr(low)?;
    let (close_ptr, _close) = get_series_f64_ptr(close)?;

    let len = close.len();
    let res = ta_cdl3starsinsouth(open_ptr, high_ptr, low_ptr, close_ptr, len);
    match res {
        Ok(out) => Ok(Int32Chunked::from_vec("", out).into_series()),
        Err(ret_code) => ta_code2err(ret_code),
    }
}

#[polars_expr(output_type=Int32)]
fn cdl3whitesoldiers(inputs: &[Series], kwargs: Masked<NoParams>) -> PolarsResult<Series> {
    kwargs.apply(inputs, |_| cdl3whitesoldiers_unmasked(inputs))
}

fn cdl3whitesoldiers_unmasked(inputs: &[Series]) -> PolarsResult<Series> {
    let inputs = &crate::utils::broadcast_inputs(inputs)?;
    let open = &mut cast_series_to_f64(&inputs[0])?;
    let high = &mut cast_series_to_f64(&inputs[1])?;
    let low = &mut cast_series_to_f64(&inputs[2])?;
    let close = &mut cast_series_to_f64(&inputs[3])?;

    let (open_ptr, _open) = get_series_f64_ptr(open)?;
    let (high_ptr, _high) = get_series_f64_ptr(high)?;
    let (low_ptr, _low) = get_series_f64_ptr(low)?;
    let (close_ptr, _close) = get_series_f64_ptr(close)?;

    let len = close.len();
    let res = ta_cdl3whitesoldiers(open_ptr, high_ptr, low_ptr, close_ptr, len);
    match res {
        Ok(out) => Ok(Int32Chunked::from_vec("", out).into_series()),
        Err(ret_code) => ta_code2err(ret_code),
    }
}

#[polars_expr(output_type=Int32)]
fn cdlabandonedbaby(inputs: &[Series], kwargs: Masked<CDLKwargs>) -> PolarsResult<Series> {
    kwargs.apply(inputs, |kwargs| cdlabandonedbaby_unmasked(inputs, kwargs))
}

fn cdlabandonedbaby_unmasked(inputs: &[Series], kwargs: CDLKwargs) -> PolarsResult<Series> {
    let inputs = &crate::utils::broadcast_inputs(inputs)?;
    let open = &mut cast_series_to_f64(&inputs[0])?;
    let high = &mut cast_series_to_f64(&inputs[1])?;
    let low = &mut cast_series_to_f64(&inputs[2])?;
    let close = &mut cast_series_to_f64(&inputs[3])?;
    let (open_ptr, _open) = get_series_f64_ptr(open)?;
    let (high_ptr, _high) = get_series_f64_ptr(high)?;
    let (low_ptr, _low) = get_series_f64_ptr(low)?;
    let (close_ptr, _close) = get_series_f64_ptr(close)?;
    let len = close.len();

    let res = ta_cdlabandonedbaby(open_ptr, high_ptr, low_ptr, close_ptr, len, &kwargs);
    match res {
        Ok(out) => Ok(Int32Chunked::from_vec("", out).into_series()),
        Err(ret_code) => ta_code2err(ret_code),
    }
}

#[polars_expr(output_type=Int32)]
fn cdladvanceblock(inputs: &[Series], kwargs: Masked<NoParams>) -> PolarsResult<Series> {
    kwargs.apply(inputs, |_| cdladvanceblock_unmasked(inputs))
}

fn cdladvanceblock_unmasked(inputs: &[Series]) -> PolarsResult<Series> {
    let inputs = &crate::utils::broadcast_inputs(inputs)?;
    let open = &mut cast_series_to_f64(&inputs[0])?;
    let high = &mut cast_series_to_f64(&inputs[1])?;
    let low = &mut cast_series_to_f64(&inputs[2])?;
    let close = &mut cast_series_to_f64(&inputs[3])?;

    let (open_ptr, _open) = get_series_f64_ptr(open)?;
    let (high_ptr, _high) = get_series_f64_ptr(high)?;
    let (low_ptr, _low) = get_series_f64_ptr(low)?;
    let (close_ptr, _close) = get_series_f64_ptr(close)?;

    let len = close.len();
    let res = ta_cdladvanceblock(open_ptr, high_ptr, low_ptr, close_ptr, len);
    match res {
        Ok(out) => Ok(Int32Chunked::new("", out).into_series()),
        Err(ret_code) => ta_code2err(ret_code),
    }
}

#[polars_expr(output_type=Int32)]
fn cdlbelthold(inputs: &[Series], kwargs: Masked<NoParams>) -> PolarsResult<Series> {
    kwargs.apply(inputs, |_| cdlbelthold_unmasked(inputs))
}

fn cdlbelthold_unmasked(inputs: &[Series]) -> PolarsResult<Series> {
    let inputs = &crate::utils::broadcast_inputs(inputs)?;
    let open = &mut cast_series_to_f64(&inputs[0])?;
    let high = &mut cast_series_to_f64(&inputs[1])?;
    let low = &mut cast_series_to_f64(&inputs[2])?;
    let close = &mut cast_series_to_f64(&inputs[3])?;

    let (open_ptr, _open) = get_series_f64_ptr(open)?;
    let (high_ptr, _high) = get_series_f64_ptr(high)?;
    let (low_ptr, _low) = get_series_f64_ptr(low)?;
    let (close_ptr, _close) = get_series_f64_ptr(close)?;

    let len = close.len();
    let res = ta_cdlbelthold(open_ptr, high_ptr, low_ptr, close_ptr, len);
    match res {
        Ok(out) => Ok(Int32Chunked::new("", out).into_series()),
        Err(ret_code) => ta_code2err(ret_code),
    }
}

#[polars_expr(output_type=Int32)]
fn cdlbreakaway(inputs: &[Series], kwargs: Masked<NoParams>) -> PolarsResult<Series> {
    kwargs.apply(inputs, |_| cdlbreakaway_unmasked(inputs))
}

fn cdlbreakaway_unmasked(inputs: &[Series]) -> PolarsResult<Series> {
    let inputs = &crate::utils::broadcast_inputs(inputs)?;
    let open = &mut cast_series_to_f64(&inputs[0])?;
    let high = &mut cast_series_to_f64(&inputs[1])?;
    let low = &mut cast_series_to_f64(&inputs[2])?;
    let close = &mut cast_series_to_f64(&inputs[3])?;

    let (open_ptr, _open) = get_series_f64_ptr(open)?;
    let (high_ptr, _high) = get_series_f64_ptr(high)?;
    let (low_ptr, _low) = get_series_f64_ptr(low)?;
    let (close_ptr, _close) = get_series_f64_ptr(close)?;

    let len = close.len();
    let res = ta_cdlbreakaway(open_ptr, high_ptr, low_ptr, close_ptr, len);
    match res {
        Ok(out) => Ok(Int32Chunked::new("", out).into_series()),
        Err(ret_code) => ta_code2err(ret_code),
    }
}

#[polars_expr(output_type=Int32)]
fn cdlclosingmarubozu(inputs: &[Series], kwargs: Masked<NoParams>) -> PolarsResult<Series> {
    kwargs.apply(inputs, |_| cdlclosingmarubozu_unmasked(inputs))
}

fn cdlclosingmarubozu_unmasked(inputs: &[Series]) -> PolarsResult<Series> {
    let inputs = &crate::utils::broadcast_inputs(inputs)?;
    let open = &mut cast_series_to_f64(&inputs[0])?;
    let high = &mut cast_series_to_f64(&inputs[1])?;
    let low = &mut cast_series_to_f64(&inputs[2])?;
    let close = &mut cast_series_to_f64(&inputs[3])?;

    let (open_ptr, _open) = get_series_f64_ptr(open)?;
    let (high_ptr, _high) = get_series_f64_ptr(high)?;
    let (low_ptr, _low) = get_series_f64_ptr(low)?;
    let (close_ptr, _close) = get_series_f64_ptr(close)?;

    let len = close.len();
    let res = ta_cdlclosingmarubozu(open_ptr, high_ptr, low_ptr, close_ptr, len);
    match res {
        Ok(out) => Ok(Int32Chunked::new("", out).into_series()),
        Err(ret_code) => ta_code2err(ret_code),
    }
}

#[polars_expr(output_type=Int32)]
fn cdlconcealbabyswall(inputs: &[Series], kwargs: Masked<NoParams>) -> PolarsResult<Series> {
    kwargs.apply(inputs, |_| cdlconcealbabyswall_unmasked(inputs))
}

fn cdlconcealbabyswall_unmasked(inputs: &[Series]) -> PolarsResult<Series> {
    let inputs = &crate::utils::broadcast_inputs(inputs)?;
    let open = &mut cast_series_to_f64(&inputs[0])?;
    let high = &mut cast_series_to_f64(&inputs[1])?;
    let low = &mut cast_series_to_f64(&inputs[2])?;
    let close = &mut cast_series_to_f64(&inputs[3])?;

    let (open_ptr, _open) = get_series_f64_ptr(open)?;
    let (high_ptr, _high) = get_series_f64_ptr(high)?;
    let (low_ptr, _low) = get_series_f64_ptr(low)?;
    let (close_ptr, _close) = get_series_f64_ptr(close)?;

    let len = close.len();
    let res = ta_cdlconcealbabyswall(open_ptr, high_ptr, low_ptr, close_ptr, len);
    match res {
        Ok(out) => Ok(Int32Chunked::new("", out).into_series()),
        Err(ret_code) => ta_code2err(ret_code),
    }
}

#[polars_expr(output_type=Int32)]
fn cdlcounterattack(inputs: &[Series], kwargs: Masked<NoParams>) -> PolarsResult<Series> {
    kwargs.apply(inputs, |_| cdlcounterattack_unmasked(inputs))
}

fn cdlcounterattack_unmasked(inputs: &[Series]) -> PolarsResult<Series> {
    let inputs = &crate::utils::broadcast_inputs(inputs)?;
    let open = &mut cast_series_to_f64(&inputs[0])?;
    let high = &mut cast_series_to_f64(&inputs[1])?;
    let low = &mut cast_series_to_f64(&inputs[2])?;
    let close = &mut cast_series_to_f64(&inputs[3])?;

    let (open_ptr, _open) = get_series_f64_ptr(open)?;
    let (high_ptr, _high) = get_series_f64_ptr(high)?;
    let (low_ptr, _low) = get_series_f64_ptr(low)?;
    let (close_ptr, _close) = get_series_f64_ptr(close)?;
    let len = close.len();

    let res = ta_cdlcounterattack(open_ptr, high_ptr, low_ptr, close_ptr, len);
    match res {
        Ok(out) => Ok(Int32Chunked::new("", out).into_series()),
        Err(ret_code) => ta_code2err(ret_code),
    }
}

#[polars_expr(output_type=Int32)]
fn cdldarkcloudcover(inputs: &[Series], kwargs: Masked<CDLKwargs>) -> PolarsResult<Series> {
    kwargs.apply(inputs, |kwargs| cdldarkcloudcover_unmasked(inputs, kwargs))
}

fn cdldarkcloudcover_unmasked(inputs: &[Series], kwargs: CDLKwargs) -> PolarsResult<Series> {
    let inputs = &crate::utils::broadcast_inputs(inputs)?;
    let open = &mut cast_series_to_f64(&inputs[0])?;
    let high = &mut cast_series_to_f64(&inputs[1])?;
    let low = &mut cast_series_to_f64(&inputs[2])?;
    let close = &mut cast_series_to_f64(&inputs[3])?;
    let (open_ptr, _open) = get_series_f64_ptr(open)?;
    let (high_ptr, _high) = get_series_f64_ptr(high)?;
    let (low_ptr, _low) = get_series_f64_ptr(low)?;
    let (close_ptr, _close) = get_series_f64_ptr(close)?;
    let len = close.len();

    let res = ta_cdldarkcloudcover(open_ptr, high_ptr, low_ptr, close_ptr, len, &kwargs);
    match res {
        Ok(out) => Ok(Int32Chunked::new("", out).into_series()),
        Err(ret_code) => ta_code2err(ret_code),
    }
}

#[polars_expr(output_type=Int32)]
fn cdldoji(inputs: &[Series], kwargs: Masked<NoParams>) -> PolarsResult<Series> {
    kwargs.apply(inputs, |_| cdldoji_unmasked(inputs))
}

fn cdldoji_unmasked(inputs: &[Series]) -> PolarsResult<Series> {
    let inputs = &crate::utils::broadcast_inputs(inputs)?;
    let open = &mut cast_series_to_f64(&inputs[0])?;
    let high = &mut cast_series_to_f64(&inputs[1])?;
    let low = &mut cast_series_to_f64(&inputs[2])?;
    let close = &mut cast_series_to_f64(&inputs[3])?;

    let (open_ptr, _open) = get_series_f64_ptr(open)?;
    let (high_ptr, _high) = get_series_f64_ptr(high)?;
    let (low_ptr, _low) = get_series_f64_ptr(low)?;
    let (close_ptr, _close) = get_series_f64_ptr(close)?;

    let len = close.len();
    let res = ta_cdldoji(open_ptr, high_ptr, low_ptr, close_ptr, len);
    match res {
        Ok(out) => Ok(Int32Chunked::new("", out).into_series()),
        Err(ret_code) => ta_code2err(ret_code),
    }
}

#[polars_expr(output_type=Int32)]
fn cdldojistar(inputs: &[Series], kwargs: Masked<NoParams>) -> PolarsResult<Series> {
    kwargs.apply(inputs, |_| cdldojistar_unmasked(inputs))
}

fn cdldojistar_unmasked(inputs: &[Series]) -> PolarsResult<Series> {
    let inputs = &crate::utils::broadcast_inputs(inputs)?;
    let open = &mut cast_series_to_f64(&inputs[0])?;
    let high = &mut cast_series_to_f64(&inputs[1])?;
    let low = &mut cast_series_to_f64(&inputs[2])?;
    let close = &mut cast_series_to_f64(&inputs[3])?;
    let (open_ptr, _open) = get_series_f64_ptr(open)?;
    let (high_ptr, _high) = get_series_f64_ptr(high)?;
    let (low_ptr, _low) = get_series_f64_ptr(low)?;
    let (close_ptr, _close) = get_series_f64_ptr(close)?;
    let len = close.len();

    let res = ta_cdldojistar(open_ptr, high_ptr, low_ptr, close_ptr, len);
    match res {
        Ok(out) => Ok(Int32Chunked::new("", out).into_series()),
        Err(ret_code) => ta_code2err(ret_code),
    }
}

#[polars_expr(output_type=Int32)]
fn cdldragonflydoji(inputs: &[Series], kwargs: Masked<NoParams>) -> PolarsResult<Series> {
    kwargs.apply(inputs, |_| cdldragonflydoji_unmasked(inputs))
}

fn cdldragonflydoji_unmasked(inputs: &[Series]) -> PolarsResult<Series> {
    let inputs = &crate::utils::broadcast_inputs(inputs)?;
    let open = &mut cast_series_to_f64(&inputs[0])?;
    let high = &mut cast_series_to_f64(&inputs[1])?;
    let low = &mut cast_series_to_f64(&inputs[2])?;
    let close = &mut cast_series_to_f64(&inputs[3])?;
    let (open_ptr, _open) = get_series_f64_ptr(open)?;
    let (high_ptr, _high) = get_series_f64_ptr(high)?;
    let (low_ptr, _low) = get_series_f64_ptr(low)?;
    let (close_ptr, _close) = get_series_f64_ptr(close)?;
    let len = close.len();

    let res = ta_cdldragonflydoji(open_ptr, high_ptr, low_ptr, close_ptr, len);
    match res {
        Ok(out) => Ok(Int32Chunked::new("", out).into_series()),
        Err(ret_code) => ta_code2err(ret_code),
    }
}

#[polars_expr(output_type=Int32)]
fn cdlengulfing(inputs: &[Series], kwargs: Masked<NoParams>) -> PolarsResult<Series> {
    kwargs.apply(inputs, |_| cdlengulfing_unmasked(inputs))
}

fn cdlengulfing_unmasked(inputs: &[Series]) -> PolarsResult<Series> {
    let inputs = &crate::utils::broadcast_inputs(inputs)?;
    let open = &mut cast_series_to_f64(&inputs[0])?;
    let high = &mut cast_series_to_f64(&inputs[1])?;
    let low = &mut cast_series_to_f64(&inputs[2])?;
    let close = &mut cast_series_to_f64(&inputs[3])?;
    let (open_ptr, _open) = get_series_f64_ptr(open)?;
    let (high_ptr, _high) = get_series_f64_ptr(high)?;
    let (low_ptr, _low) = get_series_f64_ptr(low)?;
    let (close_ptr, _close) = get_series_f64_ptr(close)?;
    let len = close.len();

    let res = ta_cdlengulfing(open_ptr, high_ptr, low_ptr, close_ptr, len);
    match res {
        Ok(out) => Ok(Int32Chunked::new("", out).into_series()),
        Err(ret_code) => ta_code2err(ret_code),
    }
}

#[polars_expr(output_type=Int32)]
fn cdleveningdojistar(inputs: &[Series], kwargs: Masked<CDLKwargs>) -> PolarsResult<Series> {
    kwargs.apply(inputs, |kwargs| cdleveningdojistar_unmasked(inputs, kwargs))
}

fn cdleveningdojistar_unmasked(inputs: &[Series], kwargs: CDLKwargs) -> PolarsResult<Series> {
    let inputs = &crate::utils::broadcast_inputs(inputs)?;
    let open = &mut cast_series_to_f64(&inputs[0])?;
    let high = &mut cast_series_to_f64(&inputs[1])?;
    let low = &mut cast_series_to_f64(&inputs[2])?;
    let close = &mut cast_series_to_f64(&inputs[3])?;
    let (open_ptr, _open) = get_series_f64_ptr(open)?;
    let (high_ptr, _high) = get_series_f64_ptr(high)?;
    let (low_ptr, _low) = get_series_f64_ptr(low)?;
    let (close_ptr, _close) = get_series_f64_ptr(close)?;
    let len = close.len();

    let res = ta_cdleveningdojistar(open_ptr, high_ptr, low_ptr, close_ptr, len, &kwargs);
    match res {
        Ok(out) => Ok(Int32Chunked::new("", out).into_series()),
        Err(ret_code) => ta_code2err(ret_code),
    }
}

#[polars_expr(output_type=Int32)]
fn cdleveningstar(inputs: &[Series], kwargs: Masked<CDLKwargs>) -> PolarsResult<Series> {
    kwargs.apply(inputs, |kwargs| cdleveningstar_unmasked(inputs, kwargs))
}

fn cdleveningstar_unmasked(inputs: &[Series], kwargs: CDLKwargs) -> PolarsResult<Series> {
    let inputs = &crate::utils::broadcast_inputs(inputs)?;
    let open = &mut cast_series_to_f64(&inputs[0])?;
    let high = &mut cast_series_to_f64(&inputs[1])?;
    let low = &mut cast_series_to_f64(&inputs[2])?;
    let close = &mut cast_series_to_f64(&inputs[3])?;
    let (open_ptr, _open) = get_series_f64_ptr(open)?;
    let (high_ptr, _high) = get_series_f64_ptr(high)?;
    let (low_ptr, _low) = get_series_f64_ptr(low)?;
    let (close_ptr, _close) = get_series_f64_ptr(close)?;
    let len = close.len();

    let res = ta_cdleveningstar(open_ptr, high_ptr, low_ptr, close_ptr, len, &kwargs);
    match res {
        Ok(out) => Ok(Int32Chunked::new("", out).into_series()),
        Err(ret_code) => ta_code2err(ret_code),
    }
}

#[polars_expr(output_type=Int32)]
fn cdlgapsidesidewhite(inputs: &[Series], kwargs: Masked<NoParams>) -> PolarsResult<Series> {
    kwargs.apply(inputs, |_| cdlgapsidesidewhite_unmasked(inputs))
}

fn cdlgapsidesidewhite_unmasked(inputs: &[Series]) -> PolarsResult<Series> {
    let inputs = &crate::utils::broadcast_inputs(inputs)?;
    let open = &mut cast_series_to_f64(&inputs[0])?;
    let high = &mut cast_series_to_f64(&inputs[1])?;
    let low = &mut cast_series_to_f64(&inputs[2])?;
    let close = &mut cast_series_to_f64(&inputs[3])?;
    let (open_ptr, _open) = get_series_f64_ptr(open)?;
    let (high_ptr, _high) = get_series_f64_ptr(high)?;
    let (low_ptr, _low) = get_series_f64_ptr(low)?;
    let (close_ptr, _close) = get_series_f64_ptr(close)?;
    let len = close.len();

    let res = ta_cdlgapsidesidewhite(open_ptr, high_ptr, low_ptr, close_ptr, len);
    match res {
        Ok(out) => Ok(Int32Chunked::new("", out).into_series()),
        Err(ret_code) => ta_code2err(ret_code),
    }
}

#[polars_expr(output_type=Int32)]
fn cdlgravestonedoji(inputs: &[Series], kwargs: Masked<NoParams>) -> PolarsResult<Series> {
    kwargs.apply(inputs, |_| cdlgravestonedoji_unmasked(inputs))
}

fn cdlgravestonedoji_unmasked(inputs: &[Series]) -> PolarsResult<Series> {
    let inputs = &crate::utils::broadcast_inputs(inputs)?;
    let open = &mut cast_series_to_f64(&inputs[0])?;
    let high = &mut cast_series_to_f64(&inputs[1])?;
    let low = &mut cast_series_to_f64(&inputs[2])?;
    let close = &mut cast_series_to_f64(&inputs[3])?;
    let (open_ptr, _open) = get_series_f64_ptr(open)?;
    let (high_ptr, _high) = get_series_f64_ptr(high)?;
    let (low_ptr, _low) = get_series_f64_ptr(low)?;
    let (close_ptr, _close) = get_series_f64_ptr(close)?;
    let len = close.len();

    let res = ta_cdlgravestonedoji(open_ptr, high_ptr, low_ptr, close_ptr, len);
    match res {
        Ok(out) => Ok(Int32Chunked::new("", out).into_series()),
        Err(ret_code) => ta_code2err(ret_code),
    }
}

#[polars_expr(output_type=Int32)]
fn cdlhammer(inputs: &[Series], kwargs: Masked<NoParams>) -> PolarsResult<Series> {
    kwargs.apply(inputs, |_| cdlhammer_unmasked(inputs))
}

fn cdlhammer_unmasked(inputs: &[Series]) -> PolarsResult<Series> {
    let inputs = &crate::utils::broadcast_inputs(inputs)?;
    let open = &mut cast_series_to_f64(&inputs[0])?;
    let high = &mut cast_series_to_f64(&inputs[1])?;
    let low = &mut cast_series_to_f64(&inputs[2])?;
    let close = &mut cast_series_to_f64(&inputs[3])?;
    let (open_ptr, _open) = get_series_f64_ptr(open)?;
    let (high_ptr, _high) = get_series_f64_ptr(high)?;
    let (low_ptr, _low) = get_series_f64_ptr(low)?;
    let (close_ptr, _close) = get_series_f64_ptr(close)?;
    let len = close.len();

    let res = ta_cdlhammer(open_ptr, high_ptr, low_ptr, close_ptr, len);
    match res {
        Ok(out) => Ok(Int32Chunked::new("", out).into_series()),
        Err(ret_code) => ta_code2err(ret_code),
    }
}

#[polars_expr(output_type=Int32)]
fn cdlhangingman(inputs: &[Series], kwargs: Masked<NoParams>) -> PolarsResult<Series> {
    kwargs.apply(inputs, |_| cdlhangingman_unmasked(inputs))
}

fn cdlhangingman_unmasked(inputs: &[Series]) -> PolarsResult<Series> {
    let inputs = &crate::utils::broadcast_inputs(inputs)?;
    let open = &mut cast_series_to_f64(&inputs[0])?;
    let high = &mut cast_series_to_f64(&inputs[1])?;
    let low = &mut cast_series_to_f64(&inputs[2])?;
    let close = &mut cast_series_to_f64(&inputs[3])?;
    let (open_ptr, _open) = get_series_f64_ptr(open)?;
    let (high_ptr, _high) = get_series_f64_ptr(high)?;
    let (low_ptr, _low) = get_series_f64_ptr(low)?;
    let (close_ptr, _close) = get_series_f64_ptr(close)?;
    let len = close.len();

    let res = ta_cdlhangingman(open_ptr, high_ptr, low_ptr, close_ptr, len);
    match res {
        Ok(out) => Ok(Int32Chunked::new("", out).into_series()),
        Err(ret_code) => ta_code2err(ret_code),
    }
}

#[polars_expr(output_type=Int32)]
fn cdlharami(inputs: &[Series], kwargs: Masked<NoParams>) -> PolarsResult<Series> {
    kwargs.apply(inputs, |_| cdlharami_unmasked(inputs))
}

fn cdlharami_unmasked(inputs: &[Series]) -> PolarsResult<Series> {
    let inputs = &crate::utils::broadcast_inputs(inputs)?;
    let open = &mut cast_series_to_f64(&inputs[0])?;
    let high = &mut cast_series_to_f64(&inputs[1])?;
    let low = &mut cast_series_to_f64(&inputs[2])?;
    let close = &mut cast_series_to_f64(&inputs[3])?;
    let (open_ptr, _open) = get_series_f64_ptr(open)?;
    let (high_ptr, _high) = get_series_f64_ptr(high)?;
    let (low_ptr, _low) = get_series_f64_ptr(low)?;
    let (close_ptr, _close) = get_series_f64_ptr(close)?;
    let len = close.len();

    let res = ta_cdlharami(open_ptr, high_ptr, low_ptr, close_ptr, len);
    match res {
        Ok(out) => Ok(Int32Chunked::new("", out).into_series()),
        Err(ret_code) => ta_code2err(ret_code),
    }
}

#[polars_expr(output_type=Int32)]
fn cdlharamicross(inputs: &[Series], kwargs: Masked<NoParams>) -> PolarsResult<Series> {
    kwargs.apply(inputs, |_| cdlharamicross_unmasked(inputs))
}

fn cdlharamicross_unmasked(inputs: &[Series]) -> PolarsResult<Series> {
    let inputs = &crate::utils::broadcast_inputs(inputs)?;
    let open = &mut cast_series_to_f64(&inputs[0])?;
    let high = &mut cast_series_to_f64(&inputs[1])?;
    let low = &mut cast_series_to_f64(&inputs[2])?;
    let close = &mut cast_series_to_f64(&inputs[3])?;
    let (open_ptr, _open) = get_series_f64_ptr(open)?;
    let (high_ptr, _high) = get_series_f64_ptr(high)?;
    let (low_ptr, _low) = get_series_f64_ptr(low)?;
    let (close_ptr, _close) = get_series_f64_ptr(close)?;
    let len = close.len();

    let res = ta_cdlharamicross(open_ptr, high_ptr, low_ptr, close_ptr, len);
    match res {
        Ok(out) => Ok(Int32Chunked::new("", out).into_series()),
        Err(ret_code) => ta_code2err(ret_code),
    }
}

#[polars_expr(output_type=Int32)]
fn cdlhighwave(inputs: &[Series], kwargs: Masked<NoParams>) -> PolarsResult<Series> {
    kwargs.apply(inputs, |_| cdlhighwave_unmasked(inputs))
}

fn cdlhighwave_unmasked(inputs: &[Series]) -> PolarsResult<Series> {
    let inputs = &crate::utils::broadcast_inputs(inputs)?;
    let open = &mut cast_series_to_f64(&inputs[0])?;
    let high = &mut cast_series_to_f64(&inputs[1])?;
    let low = &mut cast_series_to_f64(&inputs[2])?;
    let close = &mut cast_series_to_f64(&inputs[3])?;
    let (open_ptr, _open) = get_series_f64_ptr(open)?;
    let (high_ptr, _high) = get_series_f64_ptr(high)?;
    let (low_ptr, _low) = get_series_f64_ptr(low)?;
    let (close_ptr, _close) = get_series_f64_ptr(close)?;
    let len = close.len();

    let res = ta_cdlhighwave(open_ptr, high_ptr, low_ptr, close_ptr, len);
    match res {
        Ok(out) => Ok(Int32Chunked::new("", out).into_series()),
        Err(ret_code) => ta_code2err(ret_code),
    }
}

#[polars_expr(output_type=Int32)]
fn cdlhikkake(inputs: &[Series], kwargs: Masked<NoParams>) -> PolarsResult<Series> {
    kwargs.apply(inputs, |_| cdlhikkake_unmasked(inputs))
}

fn cdlhikkake_unmasked(inputs: &[Series]) -> PolarsResult<Series> {
    let inputs = &crate::utils::broadcast_inputs(inputs)?;
    let open = &mut cast_series_to_f64(&inputs[0])?;
    let high = &mut cast_series_to_f64(&inputs[1])?;
    let low = &mut cast_series_to_f64(&inputs[2])?;
    let close = &mut cast_series_to_f64(&inputs[3])?;
    let (open_ptr, _open) = get_series_f64_ptr(open)?;
    let (high_ptr, _high) = get_series_f64_ptr(high)?;
    let (low_ptr, _low) = get_series_f64_ptr(low)?;
    let (close_ptr, _close) = get_series_f64_ptr(close)?;
    let len = close.len();

    let res = ta_cdlhikkake(open_ptr, high_ptr, low_ptr, close_ptr, len);
    match res {
        Ok(out) => Ok(Int32Chunked::new("", out).into_series()),
        Err(ret_code) => ta_code2err(ret_code),
    }
}

#[polars_expr(output_type=Int32)]
fn cdlhikkakemod(inputs: &[Series], kwargs: Masked<NoParams>) -> PolarsResult<Series> {
    kwargs.apply(inputs, |_| cdlhikkakemod_unmasked(inputs))
}

fn cdlhikkakemod_unmasked(inputs: &[Series]) -> PolarsResult<Series> {
    let inputs = &crate::utils::broadcast_inputs(inputs)?;
    let open = &mut cast_series_to_f64(&inputs[0])?;
    let high = &mut cast_series_to_f64(&inputs[1])?;
    let low = &mut cast_series_to_f64(&inputs[2])?;
    let close = &mut cast_series_to_f64(&inputs[3])?;
    let (open_ptr, _open) = get_series_f64_ptr(open)?;
    let (high_ptr, _high) = get_series_f64_ptr(high)?;
    let (low_ptr, _low) = get_series_f64_ptr(low)?;
    let (close_ptr, _close) = get_series_f64_ptr(close)?;
    let len = close.len();

    let res = ta_cdlhikkakemod(open_ptr, high_ptr, low_ptr, close_ptr, len);
    match res {
        Ok(out) => Ok(Int32Chunked::new("", out).into_series()),
        Err(ret_code) => ta_code2err(ret_code),
    }
}

#[polars_expr(output_type=Int32)]
fn cdlhomingpigeon(inputs: &[Series], kwargs: Masked<NoParams>) -> PolarsResult<Series> {
    kwargs.apply(inputs, |_| cdlhomingpigeon_unmasked(inputs))
}

fn cdlhomingpigeon_unmasked(inputs: &[Series]) -> PolarsResult<Series> {
    let inputs = &crate::utils::broadcast_inputs(inputs)?;
    let open = &mut cast_series_to_f64(&inputs[0])?;
    let high = &mut cast_series_to_f64(&inputs[1])?;
    let low = &mut cast_series_to_f64(&inputs[2])?;
    let close = &mut cast_series_to_f64(&inputs[3])?;
    let (open_ptr, _open) = get_series_f64_ptr(open)?;
    let (high_ptr, _high) = get_series_f64_ptr(high)?;
    let (low_ptr, _low) = get_series_f64_ptr(low)?;
    let (close_ptr, _close) = get_series_f64_ptr(close)?;
    let len = close.len();

    let res = ta_cdlhomingpigeon(open_ptr, high_ptr, low_ptr, close_ptr, len);
    match res {
        Ok(out) => Ok(Int32Chunked::new("", out).into_series()),
        Err(ret_code) => ta_code2err(ret_code),
    }
}

#[polars_expr(output_type=Int32)]
fn cdlidentical3crows(inputs: &[Series], kwargs: Masked<NoParams>) -> PolarsResult<Series> {
    kwargs.apply(inputs, |_| cdlidentical3crows_unmasked(inputs))
}

fn cdlidentical3crows_unmasked(inputs: &[Series]) -> PolarsResult<Series> {
    let inputs = &crate::utils::broadcast_inputs(inputs)?;
    let open = &mut cast_series_to_f64(&inputs[0])?;
    let high = &mut cast_series_to_f64(&inputs[1])?;
    let low = &mut cast_series_to_f64(&inputs[2])?;
    let close = &mut cast_series_to_f64(&inputs[3])?;
    let (open_ptr, _open) = get_series_f64_ptr(open)?;
    let (high_ptr, _high) = get_series_f64_ptr(high)?;
    let (low_ptr, _low) = get_series_f64_ptr(low)?;
    let (close_ptr, _close) = get_series_f64_ptr(close)?;
    let len = close.len();

    let res = ta_cdlidentical3crows(open_ptr, high_ptr, low_ptr, close_ptr, len);
    match res {
        Ok(out) => Ok(Int32Chunked::new("", out).into_series()),
        Err(ret_code) => ta_code2err(ret_code),
    }
}

#[polars_expr(output_type=Int32)]
fn cdlinneck(inputs: &[Series], kwargs: Masked<NoParams>) -> PolarsResult<Series> {
    kwargs.apply(inputs, |_| cdlinneck_unmasked(inputs))
}

fn cdlinneck_unmasked(inputs: &[Series]) -> PolarsResult<Series> {
    let inputs = &crate::utils::broadcast_inputs(inputs)?;
    let open = &mut cast_series_to_f64(&inputs[0])?;
    let high = &mut cast_series_to_f64(&inputs[1])?;
    let low = &mut cast_series_to_f64(&inputs[2])?;
    let close = &mut cast_series_to_f64(&inputs[3])?;
    let (open_ptr, _open) = get_series_f64_ptr(open)?;
    let (high_ptr, _high) = get_series_f64_ptr(high)?;
    let (low_ptr, _low) = get_series_f64_ptr(low)?;
    let (close_ptr, _close) = get_series_f64_ptr(close)?;
    let len = close.len();

    let res = ta_cdlinneck(open_ptr, high_ptr, low_ptr, close_ptr, len);
    match res {
        Ok(out) => Ok(Int32Chunked::new("", out).into_series()),
        Err(ret_code) => ta_code2err(ret_code),
    }
}

#[polars_expr(output_type=Int32)]
fn cdlinvertedhammer(inputs: &[Series], kwargs: Masked<NoParams>) -> PolarsResult<Series> {
    kwargs.apply(inputs, |_| cdlinvertedhammer_unmasked(inputs))
}

fn cdlinvertedhammer_unmasked(inputs: &[Series]) -> PolarsResult<Series> {
    let inputs = &crate::utils::broadcast_inputs(inputs)?;
    let open = &mut cast_series_to_f64(&inputs[0])?;
    let high = &mut cast_series_to_f64(&inputs[1])?;
    let low = &mut cast_series_to_f64(&inputs[2])?;
    let close = &mut cast_series_to_f64(&inputs[3])?;
    let (open_ptr, _open) = get_series_f64_ptr(open)?;
    let (high_ptr, _high) = get_series_f64_ptr(high)?;
    let (low_ptr, _low) = get_series_f64_ptr(low)?;
    let (close_ptr, _close) = get_series_f64_ptr(close)?;
    let len = close.len();

    let res = ta_cdlinvertedhammer(open_ptr, high_ptr, low_ptr, close_ptr, len);
    match res {
        Ok(out) => Ok(Int32Chunked::new("", out).into_series()),
        Err(ret_code) => ta_code2err(ret_code),
    }
}

#[polars_expr(output_type=Int32)]
fn cdlkicking(inputs: &[Series], kwargs: Masked<NoParams>) -> PolarsResult<Series> {
    kwargs.apply(inputs, |_| cdlkicking_unmasked(inputs))
}

fn cdlkicking_unmasked(inputs: &[Series]) -> PolarsResult<Series> {
    let inputs = &crate::utils::broadcast_inputs(inputs)?;
    let open = &mut cast_series_to_f64(&inputs[0])?;
    let high = &mut cast_series_to_f64(&inputs[1])?;
    let low = &mut cast_series_to_f64(&inputs[2])?;
    let close = &mut cast_series_to_f64(&inputs[3])?;
    let (open_ptr, _open) = get_series_f64_ptr(open)?;
    let (high_ptr, _high) = get_series_f64_ptr(high)?;
    let (low_ptr, _low) = get_series_f64_ptr(low)?;
    let (close_ptr, _close) = get_series_f64_ptr(close)?;
    let len = close.len();

    let res = ta_cdlkicking(open_ptr, high_ptr, low_ptr, close_ptr, len);
    match res {
        Ok(out) => Ok(Int32Chunked::new("", out).into_series()),
        Err(ret_code) => ta_code2err(ret_code),
    }
}

#[polars_expr(output_type=Int32)]
fn cdlkickingbylength(inputs: &[Series], kwargs: Masked<NoParams>) -> PolarsResult<Series> {
    kwargs.apply(inputs, |_| cdlkickingbylength_unmasked(inputs))
}

fn cdlkickingbylength_unmasked(inputs: &[Series]) -> PolarsResult<Series> {
    let inputs = &crate::utils::broadcast_inputs(inputs)?;
    let open = &mut cast_series_to_f64(&inputs[0])?;
    let high = &mut cast_series_to_f64(&inputs[1])?;
    let low = &mut cast_series_to_f64(&inputs[2])?;
    let close = &mut cast_series_to_f64(&inputs[3])?;
    let (open_ptr, _open) = get_series_f64_ptr(open)?;
    let (high_ptr, _high) = get_series_f64_ptr(high)?;
    let (low_ptr, _low) = get_series_f64_ptr(low)?;
    let (close_ptr, _close) = get_series_f64_ptr(close)?;
    let len = close.len();

    let res = ta_cdlkickingbylength(open_ptr, high_ptr, low_ptr, close_ptr, len);
    match res {
        Ok(out) => Ok(Int32Chunked::new("", out).into_series()),
        Err(ret_code) => ta_code2err(ret_code),
    }
}

#[polars_expr(output_type=Int32)]
fn cdlladderbottom(inputs: &[Series], kwargs: Masked<NoParams>) -> PolarsResult<Series> {
    kwargs.apply(inputs, |_| cdlladderbottom_unmasked(inputs))
}

fn cdlladderbottom_unmasked(inputs: &[Series]) -> PolarsResult<Series> {
    let inputs = &crate::utils::broadcast_inputs(inputs)?;
    let open = &mut cast_series_to_f64(&inputs[0])?;
    let high = &mut cast_series_to_f64(&inputs[1])?;
    let low = &mut cast_series_to_f64(&inputs[2])?;
    let close = &mut cast_series_to_f64(&inputs[3])?;
    let (open_ptr, _open) = get_series_f64_ptr(open)?;
    let (high_ptr, _high) = get_series_f64_ptr(high)?;
    let (low_ptr, _low) = get_series_f64_ptr(low)?;
    let (close_ptr, _close) = get_series_f64_ptr(close)?;
    let len = close.len();

    let res = ta_cdlladderbottom(open_ptr, high_ptr, low_ptr, close_ptr, len);
    match res {
        Ok(out) => Ok(Int32Chunked::new("", out).into_series()),
        Err(ret_code) => ta_code2err(ret_code),
    }
}

#[polars_expr(output_type=Int32)]
fn cdllongleggeddoji(inputs: &[Series], kwargs: Masked<NoParams>) -> PolarsResult<Series> {
    kwargs.apply(inputs, |_| cdllongleggeddoji_unmasked(inputs))
}

fn cdllongleggeddoji_unmasked(inputs: &[Series]) -> PolarsResult<Series> {
    let inputs = &crate::utils::broadcast_inputs(inputs)?;
    let open = &mut cast_series_to_f64(&inputs[0])?;
    let high = &mut cast_series_to_f64(&inputs[1])?;
    let low = &mut cast_series_to_f64(&inputs[2])?;
    let close = &mut cast_series_to_f64(&inputs[3])?;
    let (open_ptr, _open) = get_series_f64_ptr(open)?;
    let (high_ptr, _high) = get_series_f64_ptr(high)?;
    let (low_ptr, _low) = get_series_f64_ptr(low)?;
    let (close_ptr, _close) = get_series_f64_ptr(close)?;
    let len = close.len();

    let res = ta_cdllongleggeddoji(open_ptr, high_ptr, low_ptr, close_ptr, len);
    match res {
        Ok(out) => Ok(Int32Chunked::new("", out).into_series()),
        Err(ret_code) => ta_code2err(ret_code),
    }
}

#[polars_expr(output_type=Int32)]
fn cdllongline(inputs: &[Series], kwargs: Masked<NoParams>) -> PolarsResult<Series> {
    kwargs.apply(inputs, |_| cdllongline_unmasked(inputs))
}

fn cdllongline_unmasked(inputs: &[Series]) -> PolarsResult<Series> {
    let inputs = &crate::utils::broadcast_inputs(inputs)?;
    let open = &mut cast_series_to_f64(&inputs[0])?;
    let high = &mut cast_series_to_f64(&inputs[1])?;
    let low = &mut cast_series_to_f64(&inputs[2])?;
    let close = &mut cast_series_to_f64(&inputs[3])?;
    let (open_ptr, _open) = get_series_f64_ptr(open)?;
    let (high_ptr, _high) = get_series_f64_ptr(high)?;
    let (low_ptr, _low) = get_series_f64_ptr(low)?;
    let (close_ptr, _close) = get_series_f64_ptr(close)?;
    let len = close.len();

    let res = ta_cdllongline(open_ptr, high_ptr, low_ptr, close_ptr, len);
    match res {
        Ok(out) => Ok(Int32Chunked::new("", out).into_series()),
        Err(ret_code) => ta_code2err(ret_code),
    }
}

#[polars_expr(output_type=Int32)]
fn cdlmarubozu(inputs: &[Series], kwargs: Masked<NoParams>) -> PolarsResult<Series> {
    kwargs.apply(inputs, |_| cdlmarubozu_unmasked(inputs))
}

fn cdlmarubozu_unmasked(inputs: &[Series]) -> PolarsResult<Series> {
    let inputs = &crate::utils::broadcast_inputs(inputs)?;
    let open = &mut cast_series_to_f64(&inputs[0])?;
    let high = &mut cast_series_to_f64(&inputs[1])?;
    let low = &mut cast_series_to_f64(&inputs[2])?;
    let close = &mut cast_series_to_f64(&inputs[3])?;
    let (open_ptr, _open) = get_series_f64_ptr(open)?;
    let (high_ptr, _high) = get_series_f64_ptr(high)?;
    let (low_ptr, _low) = get_series_f64_ptr(low)?;
    let (close_ptr, _close) = get_series_f64_ptr(close)?;
    let len = close.len();

    let res = ta_cdlmarubozu(open_ptr, high_ptr, low_ptr, close_ptr, len);
    match res {
        Ok(out) => Ok(Int32Chunked::new("", out).into_series()),
        Err(ret_code) => ta_code2err(ret_code),
    }
}

#[polars_expr(output_type=Int32)]
fn cdlmatchinglow(inputs: &[Series], kwargs: Masked<NoParams>) -> PolarsResult<Series> {
    kwargs.apply(inputs, |_| cdlmatchinglow_unmasked(inputs))
}

fn cdlmatchinglow_unmasked(inputs: &[Series]) -> PolarsResult<Series> {
    let inputs = &crate::utils::broadcast_inputs(inputs)?;
    let open = &mut cast_series_to_f64(&inputs[0])?;
    let high = &mut cast_series_to_f64(&inputs[1])?;
    let low = &mut cast_series_to_f64(&inputs[2])?;
    let close = &mut cast_series_to_f64(&inputs[3])?;
    let (open_ptr, _open) = get_series_f64_ptr(open)?;
    let (high_ptr, _high) = get_series_f64_ptr(high)?;
    let (low_ptr, _low) = get_series_f64_ptr(low)?;
    let (close_ptr, _close) = get_series_f64_ptr(close)?;
    let len = close.len();

    let res = ta_cdlmatchinglow(open_ptr, high_ptr, low_ptr, close_ptr, len);
    match res {
        Ok(out) => Ok(Int32Chunked::new("", out).into_series()),
        Err(ret_code) => ta_code2err(ret_code),
    }
}

#[polars_expr(output_type=Int32)]
fn cdlmathold(inputs: &[Series], kwargs: Masked<CDLKwargs>) -> PolarsResult<Series> {
    kwargs.apply(inputs, |kwargs| cdlmathold_unmasked(inputs, kwargs))
}

fn cdlmathold_unmasked(inputs: &[Series], kwargs: CDLKwargs) -> PolarsResult<Series> {
    let inputs = &crate::utils::broadcast_inputs(inputs)?;
    let open = &mut cast_series_to_f64(&inputs[0])?;
    let high = &mut cast_series_to_f64(&inputs[1])?;
    let low = &mut cast_series_to_f64(&inputs[2])?;
    let close = &mut cast_series_to_f64(&inputs[3])?;
    let (open_ptr, _open) = get_series_f64_ptr(open)?;
    let (high_ptr, _high) = get_series_f64_ptr(high)?;
    let (low_ptr, _low) = get_series_f64_ptr(low)?;
    let (close_ptr, _close) = get_series_f64_ptr(close)?;
    let len = close.len();

    let res = ta_cdlmathold(open_ptr, high_ptr, low_ptr, close_ptr, len, &kwargs);
    match res {
        Ok(out) => Ok(Int32Chunked::new("", out).into_series()),
        Err(ret_code) => ta_code2err(ret_code),
    }
}

#[polars_expr(output_type=Int32)]
fn cdlmorningdojistar(inputs: &[Series], kwargs: Masked<CDLKwargs>) -> PolarsResult<Series> {
    kwargs.apply(inputs, |kwargs| cdlmorningdojistar_unmasked(inputs, kwargs))
}

fn cdlmorningdojistar_unmasked(inputs: &[Series], kwargs: CDLKwargs) -> PolarsResult<Series> {
    let inputs = &crate::utils::broadcast_inputs(inputs)?;
    let open = &mut cast_series_to_f64(&inputs[0])?;
    let high = &mut cast_series_to_f64(&inputs[1])?;
    let low = &mut cast_series_to_f64(&inputs[2])?;
    let close = &mut cast_series_to_f64(&inputs[3])?;
    let (open_ptr, _open) = get_series_f64_ptr(open)?;
    let (high_ptr, _high) = get_series_f64_ptr(high)?;
    let (low_ptr, _low) = get_series_f64_ptr(low)?;
    let (close_ptr, _close) = get_series_f64_ptr(close)?;
    let len = close.len();

    let res = ta_cdlmorningdojistar(open_ptr, high_ptr, low_ptr, close_ptr, len, &kwargs);
    match res {
        Ok(out) => Ok(Int32Chunked::new("", out).into_series()),
        Err(ret_code) => ta_code2err(ret_code),
    }
}

#[polars_expr(output_type=Int32)]
fn cdlmorningstar(inputs: &[Series], kwargs: Masked<CDLKwargs>) -> PolarsResult<Series> {
    kwargs.apply(inputs, |kwargs| cdlmorningstar_unmasked(inputs, kwargs))
}

fn cdlmorningstar_unmasked(inputs: &[Series], kwargs: CDLKwargs) -> PolarsResult<Series> {
    let inputs = &crate::utils::broadcast_inputs(inputs)?;
    let open = &mut cast_series_to_f64(&inputs[0])?;
    let high = &mut cast_series_to_f64(&inputs[1])?;
    let low = &mut cast_series_to_f64(&inputs[2])?;
    let close = &mut cast_series_to_f64(&inputs[3])?;
    let (open_ptr, _open) = get_series_f64_ptr(open)?;
    let (high_ptr, _high) = get_series_f64_ptr(high)?;
    let (low_ptr, _low) = get_series_f64_ptr(low)?;
    let (close_ptr, _close) = get_series_f64_ptr(close)?;
    let len = close.len();

    let res = ta_cdlmorningstar(open_ptr, high_ptr, low_ptr, close_ptr, len, &kwargs);
    match res {
        Ok(out) => Ok(Int32Chunked::new("", out).into_series()),
        Err(ret_code) => ta_code2err(ret_code),
    }
}

#[polars_expr(output_type=Int32)]
fn cdlonneck(inputs: &[Series], kwargs: Masked<NoParams>) -> PolarsResult<Series> {
    kwargs.apply(inputs, |_| cdlonneck_unmasked(inputs))
}

fn cdlonneck_unmasked(inputs: &[Series]) -> PolarsResult<Series> {
    let inputs = &crate::utils::broadcast_inputs(inputs)?;
    let open = &mut cast_series_to_f64(&inputs[0])?;
    let high = &mut cast_series_to_f64(&inputs[1])?;
    let low = &mut cast_series_to_f64(&inputs[2])?;
    let close = &mut cast_series_to_f64(&inputs[3])?;
    let (open_ptr, _open) = get_series_f64_ptr(open)?;
    let (high_ptr, _high) = get_series_f64_ptr(high)?;
    let (low_ptr, _low) = get_series_f64_ptr(low)?;
    let (close_ptr, _close) = get_series_f64_ptr(close)?;
    let len = close.len();

    let res = ta_cdlonneck(open_ptr, high_ptr, low_ptr, close_ptr, len);
    match res {
        Ok(out) => Ok(Int32Chunked::new("", out).into_series()),
        Err(ret_code) => ta_code2err(ret_code),
    }
}

#[polars_expr(output_type=Int32)]
fn cdlpiercing(inputs: &[Series], kwargs: Masked<NoParams>) -> PolarsResult<Series> {
    kwargs.apply(inputs, |_| cdlpiercing_unmasked(inputs))
}

fn cdlpiercing_unmasked(inputs: &[Series]) -> PolarsResult<Series> {
    let inputs = &crate::utils::broadcast_inputs(inputs)?;
    let open = &mut cast_series_to_f64(&inputs[0])?;
    let high = &mut cast_series_to_f64(&inputs[1])?;
    let low = &mut cast_series_to_f64(&inputs[2])?;
    let close = &mut cast_series_to_f64(&inputs[3])?;
    let (open_ptr, _open) = get_series_f64_ptr(open)?;
    let (high_ptr, _high) = get_series_f64_ptr(high)?;
    let (low_ptr, _low) = get_series_f64_ptr(low)?;
    let (close_ptr, _close) = get_series_f64_ptr(close)?;
    let len = close.len();

    let res = ta_cdlpiercing(open_ptr, high_ptr, low_ptr, close_ptr, len);
    match res {
        Ok(out) => Ok(Int32Chunked::new("", out).into_series()),
        Err(ret_code) => ta_code2err(ret_code),
    }
}

#[polars_expr(output_type=Int32)]
fn cdlrickshawman(inputs: &[Series], kwargs: Masked<NoParams>) -> PolarsResult<Series> {
    kwargs.apply(inputs, |_| cdlrickshawman_unmasked(inputs))
}

fn cdlrickshawman_unmasked(inputs: &[Series]) -> PolarsResult<Series> {
    let inputs = &crate::utils::broadcast_inputs(inputs)?;
    let open = &mut cast_series_to_f64(&inputs[0])?;
    let high = &mut cast_series_to_f64(&inputs[1])?;
    let low = &mut cast_series_to_f64(&inputs[2])?;
    let close = &mut cast_series_to_f64(&inputs[3])?;
    let (open_ptr, _open) = get_series_f64_ptr(open)?;
    let (high_ptr, _high) = get_series_f64_ptr(high)?;
    let (low_ptr, _low) = get_series_f64_ptr(low)?;
    let (close_ptr, _close) = get_series_f64_ptr(close)?;
    let len = close.len();

    let res = ta_cdlrickshawman(open_ptr, high_ptr, low_ptr, close_ptr, len);
    match res {
        Ok(out) => Ok(Int32Chunked::new("", out).into_series()),
        Err(ret_code) => ta_code2err(ret_code),
    }
}

#[polars_expr(output_type=Int32)]
fn cdlrisefall3methods(inputs: &[Series], kwargs: Masked<NoParams>) -> PolarsResult<Series> {
    kwargs.apply(inputs, |_| cdlrisefall3methods_unmasked(inputs))
}

fn cdlrisefall3methods_unmasked(inputs: &[Series]) -> PolarsResult<Series> {
    let inputs = &crate::utils::broadcast_inputs(inputs)?;
    let open = &mut cast_series_to_f64(&inputs[0])?;
    let high = &mut cast_series_to_f64(&inputs[1])?;
    let low = &mut cast_series_to_f64(&inputs[2])?;
    let close = &mut cast_series_to_f64(&inputs[3])?;
    let (open_ptr, _open) = get_series_f64_ptr(open)?;
    let (high_ptr, _high) = get_series_f64_ptr(high)?;
    let (low_ptr, _low) = get_series_f64_ptr(low)?;
    let (close_ptr, _close) = get_series_f64_ptr(close)?;
    let len = close.len();

    let res = ta_cdlrisefall3methods(open_ptr, high_ptr, low_ptr, close_ptr, len);
    match res {
        Ok(out) => Ok(Int32Chunked::new("", out).into_series()),
        Err(ret_code) => ta_code2err(ret_code),
    }
}

#[polars_expr(output_type=Int32)]
fn cdlseparatinglines(inputs: &[Series], kwargs: Masked<NoParams>) -> PolarsResult<Series> {
    kwargs.apply(inputs, |_| cdlseparatinglines_unmasked(inputs))
}

fn cdlseparatinglines_unmasked(inputs: &[Series]) -> PolarsResult<Series> {
    let inputs = &crate::utils::broadcast_inputs(inputs)?;
    let open = &mut cast_series_to_f64(&inputs[0])?;
    let high = &mut cast_series_to_f64(&inputs[1])?;
    let low = &mut cast_series_to_f64(&inputs[2])?;
    let close = &mut cast_series_to_f64(&inputs[3])?;
    let (open_ptr, _open) = get_series_f64_ptr(open)?;
    let (high_ptr, _high) = get_series_f64_ptr(high)?;
    let (low_ptr, _low) = get_series_f64_ptr(low)?;
    let (close_ptr, _close) = get_series_f64_ptr(close)?;
    let len = close.len();

    let res = ta_cdlseparatinglines(open_ptr, high_ptr, low_ptr, close_ptr, len);
    match res {
        Ok(out) => Ok(Int32Chunked::new("", out).into_series()),
        Err(ret_code) => ta_code2err(ret_code),
    }
}

#[polars_expr(output_type=Int32)]
fn cdlshootingstar(inputs: &[Series], kwargs: Masked<NoParams>) -> PolarsResult<Series> {
    kwargs.apply(inputs, |_| cdlshootingstar_unmasked(inputs))
}

fn cdlshootingstar_unmasked(inputs: &[Series]) -> PolarsResult<Series> {
    let inputs = &crate::utils::broadcast_inputs(inputs)?;
    let open = &mut cast_series_to_f64(&inputs[0])?;
    let high = &mut cast_series_to_f64(&inputs[1])?;
    let low = &mut cast_series_to_f64(&inputs[2])?;
    let close = &mut cast_series_to_f64(&inputs[3])?;
    let (open_ptr, _open) = get_series_f64_ptr(open)?;
    let (high_ptr, _high) = get_series_f64_ptr(high)?;
    let (low_ptr, _low) = get_series_f64_ptr(low)?;
    let (close_ptr, _close) = get_series_f64_ptr(close)?;
    let len = close.len();

    let res = ta_cdlshootingstar(open_ptr, high_ptr, low_ptr, close_ptr, len);
    match res {
        Ok(out) => Ok(Int32Chunked::new("", out).into_series()),
        Err(ret_code) => ta_code2err(ret_code),
    }
}

#[polars_expr(output_type=Int32)]
fn cdlshortline(inputs: &[Series], kwargs: Masked<NoParams>) -> PolarsResult<Series> {
    kwargs.apply(inputs, |_| cdlshortline_unmasked(inputs))
}

fn cdlshortline_unmasked(inputs: &[Series]) -> PolarsResult<Series> {
    let inputs = &crate::utils::broadcast_inputs(inputs)?;
    let open = &mut cast_series_to_f64(&inputs[0])?;
    let high = &mut cast_series_to_f64(&inputs[1])?;
    let low = &mut cast_series_to_f64(&inputs[2])?;
    let close = &mut cast_series_to_f64(&inputs[3])?;
    let (open_ptr, _open) = get_series_f64_ptr(open)?;
    let (high_ptr, _high) = get_series_f64_ptr(high)?;
    let (low_ptr, _low) = get_series_f64_ptr(low)?;
    let (close_ptr, _close) = get_series_f64_ptr(close)?;
    let len = close.len();

    let res = ta_cdlshortline(open_ptr, high_ptr, low_ptr, close_ptr, len);
    match res {
        Ok(out) => Ok(Int32Chunked::new("", out).into_series()),
        Err(ret_code) => ta_code2err(ret_code),
    }
}

#[polars_expr(output_type=Int32)]
fn cdlspinningtop(inputs: &[Series], kwargs: Masked<NoParams>) -> PolarsResult<Series> {
    kwargs.apply(inputs, |_| cdlspinningtop_unmasked(inputs))
}

fn cdlspinningtop_unmasked(inputs: &[Series]) -> PolarsResult<Series> {
    let inputs = &crate::utils::broadcast_inputs(inputs)?;
    let open = &mut cast_series_to_f64(&inputs[0])?;
    let high = &mut cast_series_to_f64(&inputs[1])?;
    let low = &mut cast_series_to_f64(&inputs[2])?;
    let close = &mut cast_series_to_f64(&inputs[3])?;
    let (open_ptr, _open) = get_series_f64_ptr(open)?;
    let (high_ptr, _high) = get_series_f64_ptr(high)?;
    let (low_ptr, _low) = get_series_f64_ptr(low)?;
    let (close_ptr, _close) = get_series_f64_ptr(close)?;
    let len = close.len();

    let res = ta_cdlspinningtop(open_ptr, high_ptr, low_ptr, close_ptr, len);
    match res {
        Ok(out) => Ok(Int32Chunked::new("", out).into_series()),
        Err(ret_code) => ta_code2err(ret_code),
    }
}

#[polars_expr(output_type=Int32)]
fn cdlstalledpattern(inputs: &[Series], kwargs: Masked<NoParams>) -> PolarsResult<Series> {
    kwargs.apply(inputs, |_| cdlstalledpattern_unmasked(inputs))
}

fn cdlstalledpattern_unmasked(inputs: &[Series]) -> PolarsResult<Series> {
    let inputs = &crate::utils::broadcast_inputs(inputs)?;
    let open = &mut cast_series_to_f64(&inputs[0])?;
    let high = &mut cast_series_to_f64(&inputs[1])?;
    let low = &mut cast_series_to_f64(&inputs[2])?;
    let close = &mut cast_series_to_f64(&inputs[3])?;
    let (open_ptr, _open) = get_series_f64_ptr(open)?;
    let (high_ptr, _high) = get_series_f64_ptr(high)?;
    let (low_ptr, _low) = get_series_f64_ptr(low)?;
    let (close_ptr, _close) = get_series_f64_ptr(close)?;
    let len = close.len();

    let res = ta_cdlstalledpattern(open_ptr, high_ptr, low_ptr, close_ptr, len);
    match res {
        Ok(out) => Ok(Int32Chunked::new("", out).into_series()),
        Err(ret_code) => ta_code2err(ret_code),
    }
}

#[polars_expr(output_type=Int32)]
fn cdlsticksandwich(inputs: &[Series], kwargs: Masked<NoParams>) -> PolarsResult<Series> {
    kwargs.apply(inputs, |_| cdlsticksandwich_unmasked(inputs))
}

fn cdlsticksandwich_unmasked(inputs: &[Series]) -> PolarsResult<Series> {
    let inputs = &crate::utils::broadcast_inputs(inputs)?;
    let open = &mut cast_series_to_f64(&inputs[0])?;
    let high = &mut cast_series_to_f64(&inputs[1])?;
    let low = &mut cast_series_to_f64(&inputs[2])?;
    let close = &mut cast_series_to_f64(&inputs[3])?;
    let (open_ptr, _open) = get_series_f64_ptr(open)?;
    let (high_ptr, _high) = get_series_f64_ptr(high)?;
    let (low_ptr, _low) = get_series_f64_ptr(low)?;
    let (close_ptr, _close) = get_series_f64_ptr(close)?;
    let len = close.len();

    let res = ta_cdlsticksandwich(open_ptr, high_ptr, low_ptr, close_ptr, len);
    match res {
        Ok(out) => Ok(Int32Chunked::new("", out).into_series()),
        Err(ret_code) => ta_code2err(ret_code),
    }
}

#[polars_expr(output_type=Int32)]
fn cdltakuri(inputs: &[Series], kwargs: Masked<NoParams>) -> PolarsResult<Series> {
    kwargs.apply(inputs, |_| cdltakuri_unmasked(inputs))
}

fn cdltakuri_unmasked(inputs: &[Series]) -> PolarsResult<Series> {
    let inputs = &crate::utils::broadcast_inputs(inputs)?;
    let open = &mut cast_series_to_f64(&inputs[0])?;
    let high = &mut cast_series_to_f64(&inputs[1])?;
    let low = &mut cast_series_to_f64(&inputs[2])?;
    let close = &mut cast_series_to_f64(&inputs[3])?;
    let (open_ptr, _open) = get_series_f64_ptr(open)?;
    let (high_ptr, _high) = get_series_f64_ptr(high)?;
    let (low_ptr, _low) = get_series_f64_ptr(low)?;
    let (close_ptr, _close) = get_series_f64_ptr(close)?;
    let len = close.len();

    let res = ta_cdltakuri(open_ptr, high_ptr, low_ptr, close_ptr, len);
    match res {
        Ok(out) => Ok(Int32Chunked::new("", out).into_series()),
        Err(ret_code) => ta_code2err(ret_code),
    }
}

#[polars_expr(output_type=Int32)]
fn cdltasukigap(inputs: &[Series], kwargs: Masked<NoParams>) -> PolarsResult<Series> {
    kwargs.apply(inputs, |_| cdltasukigap_unmasked(inputs))
}

fn cdltasukigap_unmasked(inputs: &[Series]) -> PolarsResult<Series> {
    let inputs = &crate::utils::broadcast_inputs(inputs)?;
    let open = &mut cast_series_to_f64(&inputs[0])?;
    let high = &mut cast_series_to_f64(&inputs[1])?;
    let low = &mut cast_series_to_f64(&inputs[2])?;
    let close = &mut cast_series_to_f64(&inputs[3])?;
    let (open_ptr, _open) = get_series_f64_ptr(open)?;
    let (high_ptr, _high) = get_series_f64_ptr(high)?;
    let (low_ptr, _low) = get_series_f64_ptr(low)?;
    let (close_ptr, _close) = get_series_f64_ptr(close)?;
    let len = close.len();

    let res = ta_cdltasukigap(open_ptr, high_ptr, low_ptr, close_ptr, len);
    match res {
        Ok(out) => Ok(Int32Chunked::new("", out).into_series()),
        Err(ret_code) => ta_code2err(ret_code),
    }
}

#[polars_expr(output_type=Int32)]
fn cdlthrusting(inputs: &[Series], kwargs: Masked<NoParams>) -> PolarsResult<Series> {
    kwargs.apply(inputs, |_| cdlthrusting_unmasked(inputs))
}

fn cdlthrusting_unmasked(inputs: &[Series]) -> PolarsResult<Series> {
    let inputs = &crate::utils::broadcast_inputs(inputs)?;
    let open = &mut cast_series_to_f64(&inputs[0])?;
    let high = &mut cast_series_to_f64(&inputs[1])?;
    let low = &mut cast_series_to_f64(&inputs[2])?;
    let close = &mut cast_series_to_f64(&inputs[3])?;
    let (open_ptr, _open) = get_series_f64_ptr(open)?;
    let (high_ptr, _high) = get_series_f64_ptr(high)?;
    let (low_ptr, _low) = get_series_f64_ptr(low)?;
    let (close_ptr, _close) = get_series_f64_ptr(close)?;
    let len = close.len();

    let res = ta_cdlthrusting(open_ptr, high_ptr, low_ptr, close_ptr, len);
    match res {
        Ok(out) => Ok(Int32Chunked::new("", out).into_series()),
        Err(ret_code) => ta_code2err(ret_code),
    }
}

#[polars_expr(output_type=Int32)]
fn cdltristar(inputs: &[Series], kwargs: Masked<NoParams>) -> PolarsResult<Series> {
    kwargs.apply(inputs, |_| cdltristar_unmasked(inputs))
}

fn cdltristar_unmasked(inputs: &[Series]) -> PolarsResult<Series> {
    let inputs = &crate::utils::broadcast_inputs(inputs)?;
    let open = &mut cast_series_to_f64(&inputs[0])?;
    let high = &mut cast_series_to_f64(&inputs[1])?;
    let low = &mut cast_series_to_f64(&inputs[2])?;
    let close = &mut cast_series_to_f64(&inputs[3])?;
    let (open_ptr, _open) = get_series_f64_ptr(open)?;
    let (high_ptr, _high) = get_series_f64_ptr(high)?;
    let (low_ptr, _low) = get_series_f64_ptr(low)?;
    let (close_ptr, _close) = get_series_f64_ptr(close)?;
    let len = close.len();

    let res = ta_cdltristar(open_ptr, high_ptr, low_ptr, close_ptr, len);
    match res {
        Ok(out) => Ok(Int32Chunked::new("", out).into_series()),
        Err(ret_code) => ta_code2err(ret_code),
    }
}

#[polars_expr(output_type=Int32)]
fn cdlunique3river(inputs: &[Series], kwargs: Masked<NoParams>) -> PolarsResult<Series> {
    kwargs.apply(inputs, |_| cdlunique3river_unmasked(inputs))
}

fn cdlunique3river_unmasked(inputs: &[Series]) -> PolarsResult<Series> {
    let inputs = &crate::utils::broadcast_inputs(inputs)?;
    let open = &mut cast_series_to_f64(&inputs[0])?;
    let high = &mut cast_series_to_f64(&inputs[1])?;
    let low = &mut cast_series_to_f64(&inputs[2])?;
    let close = &mut cast_series_to_f64(&inputs[3])?;
    let (open_ptr, _open) = get_series_f64_ptr(open)?;
    let (high_ptr, _high) = get_series_f64_ptr(high)?;
    let (low_ptr, _low) = get_series_f64_ptr(low)?;
    let (close_ptr, _close) = get_series_f64_ptr(close)?;
    let len = close.len();

    let res = ta_cdlunique3river(open_ptr, high_ptr, low_ptr, close_ptr, len);
    match res {
        Ok(out) => Ok(Int32Chunked::new("", out).into_series()),
        Err(ret_code) => ta_code2err(ret_code),
    }
}

#[polars_expr(output_type=Int32)]
fn cdlupsidegap2crows(inputs: &[Series], kwargs: Masked<NoParams>) -> PolarsResult<Series> {
    kwargs.apply(inputs, |_| cdlupsidegap2crows_unmasked(inputs))
}

fn cdlupsidegap2crows_unmasked(inputs: &[Series]) -> PolarsResult<Series> {
    let inputs = &crate::utils::broadcast_inputs(inputs)?;
    let open = &mut cast_series_to_f64(&inputs[0])?;
    let high = &mut cast_series_to_f64(&inputs[1])?;
    let low = &mut cast_series_to_f64(&inputs[2])?;
    let close = &mut cast_series_to_f64(&inputs[3])?;
    let (open_ptr, _open) = get_series_f64_ptr(open)?;
    let (high_ptr, _high) = get_series_f64_ptr(high)?;
    let (low_ptr, _low) = get_series_f64_ptr(low)?;
    let (close_ptr, _close) = get_series_f64_ptr(close)?;
    let len = close.len();

    let res = ta_cdlupsidegap2crows(open_ptr, high_ptr, low_ptr, close_ptr, len);
    match res {
        Ok(out) => Ok(Int32Chunked::new("", out).into_series()),
        Err(ret_code) => ta_code2err(ret_code),
    }
}

#[polars_expr(output_type=Int32)]
fn cdlxsidegap3methods(inputs: &[Series], kwargs: Masked<NoParams>) -> PolarsResult<Series> {
    kwargs.apply(inputs, |_| cdlxsidegap3methods_unmasked(inputs))
}

fn cdlxsidegap3methods_unmasked(inputs: &[Series]) -> PolarsResult<Series> {
    let inputs = &crate::utils::broadcast_inputs(inputs)?;
    let open = &mut cast_series_to_f64(&inputs[0])?;
    let high = &mut cast_series_to_f64(&inputs[1])?;
    let low = &mut cast_series_to_f64(&inputs[2])?;
    let close = &mut cast_series_to_f64(&inputs[3])?;
    let (open_ptr, _open) = get_series_f64_ptr(open)?;
    let (high_ptr, _high) = get_series_f64_ptr(high)?;
    let (low_ptr, _low) = get_series_f64_ptr(low)?;
    let (close_ptr, _close) = get_series_f64_ptr(close)?;
    let len = close.len();

    let res = ta_cdlxsidegap3methods(open_ptr, high_ptr, low_ptr, close_ptr, len);
    match res {
        Ok(out) => Ok(Int32Chunked::new("", out).into_series()),
        Err(ret_code) => ta_code2err(ret_code),
    }
}
