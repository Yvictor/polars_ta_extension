use crate::utils::{cast_series_to_f64, get_series_f64_ptr, ta_code2err};
use polars::prelude::*;
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

// #[polars_expr(output_type=Int32)]
pub fn cdl2crows(inputs: &[Series]) -> PolarsResult<Series> {
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

// #[polars_expr(output_type=Int32)]
pub fn cdl3blackcrows(inputs: &[Series]) -> PolarsResult<Series> {
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

// #[polars_expr(output_type=Int32)]
pub fn cdl3inside(inputs: &[Series]) -> PolarsResult<Series> {
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

// #[polars_expr(output_type=Int32)]
pub fn cdl3linestrike(inputs: &[Series]) -> PolarsResult<Series> {
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

// #[polars_expr(output_type=Int32)]
pub fn cdl3outside(inputs: &[Series]) -> PolarsResult<Series> {
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

// #[polars_expr(output_type=Int32)]
pub fn cdl3starsinsouth(inputs: &[Series]) -> PolarsResult<Series> {
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

// #[polars_expr(output_type=Int32)]
pub fn cdl3whitesoldiers(inputs: &[Series]) -> PolarsResult<Series> {
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

// #[polars_expr(output_type=Int32)]
pub fn cdlabandonedbaby(inputs: &[Series], kwargs: CDLKwargs) -> PolarsResult<Series> {
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

// #[polars_expr(output_type=Int32)]
pub fn cdladvanceblock(inputs: &[Series]) -> PolarsResult<Series> {
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

// #[polars_expr(output_type=Int32)]
pub fn cdlbelthold(inputs: &[Series]) -> PolarsResult<Series> {
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

// #[polars_expr(output_type=Int32)]
pub fn cdlbreakaway(inputs: &[Series]) -> PolarsResult<Series> {
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

// #[polars_expr(output_type=Int32)]
pub fn cdlclosingmarubozu(inputs: &[Series]) -> PolarsResult<Series> {
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

// #[polars_expr(output_type=Int32)]
pub fn cdlconcealbabyswall(inputs: &[Series]) -> PolarsResult<Series> {
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

// #[polars_expr(output_type=Int32)]
pub fn cdlcounterattack(inputs: &[Series]) -> PolarsResult<Series> {
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

// #[polars_expr(output_type=Int32)]
pub fn cdldarkcloudcover(inputs: &[Series], kwargs: CDLKwargs) -> PolarsResult<Series> {
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

// #[polars_expr(output_type=Int32)]
pub fn cdldoji(inputs: &[Series]) -> PolarsResult<Series> {
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

// #[polars_expr(output_type=Int32)]
pub fn cdldojistar(inputs: &[Series]) -> PolarsResult<Series> {
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

// #[polars_expr(output_type=Int32)]
pub fn cdldragonflydoji(inputs: &[Series]) -> PolarsResult<Series> {
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

// #[polars_expr(output_type=Int32)]
pub fn cdlengulfing(inputs: &[Series]) -> PolarsResult<Series> {
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

// #[polars_expr(output_type=Int32)]
pub fn cdleveningdojistar(inputs: &[Series], kwargs: CDLKwargs) -> PolarsResult<Series> {
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

// #[polars_expr(output_type=Int32)]
pub fn cdleveningstar(inputs: &[Series], kwargs: CDLKwargs) -> PolarsResult<Series> {
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

// #[polars_expr(output_type=Int32)]
pub fn cdlgapsidesidewhite(inputs: &[Series]) -> PolarsResult<Series> {
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

// #[polars_expr(output_type=Int32)]
pub fn cdlgravestonedoji(inputs: &[Series]) -> PolarsResult<Series> {
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

// #[polars_expr(output_type=Int32)]
pub fn cdlhammer(inputs: &[Series]) -> PolarsResult<Series> {
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

// #[polars_expr(output_type=Int32)]
pub fn cdlhangingman(inputs: &[Series]) -> PolarsResult<Series> {
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

// #[polars_expr(output_type=Int32)]
pub fn cdlharami(inputs: &[Series]) -> PolarsResult<Series> {
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

// #[polars_expr(output_type=Int32)]
pub fn cdlharamicross(inputs: &[Series]) -> PolarsResult<Series> {
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

// #[polars_expr(output_type=Int32)]
pub fn cdlhighwave(inputs: &[Series]) -> PolarsResult<Series> {
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

// #[polars_expr(output_type=Int32)]
pub fn cdlhikkake(inputs: &[Series]) -> PolarsResult<Series> {
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

// #[polars_expr(output_type=Int32)]
pub fn cdlhikkakemod(inputs: &[Series]) -> PolarsResult<Series> {
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

// #[polars_expr(output_type=Int32)]
pub fn cdlhomingpigeon(inputs: &[Series]) -> PolarsResult<Series> {
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

// #[polars_expr(output_type=Int32)]
pub fn cdlidentical3crows(inputs: &[Series]) -> PolarsResult<Series> {
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

// #[polars_expr(output_type=Int32)]
pub fn cdlinneck(inputs: &[Series]) -> PolarsResult<Series> {
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

// #[polars_expr(output_type=Int32)]
pub fn cdlinvertedhammer(inputs: &[Series]) -> PolarsResult<Series> {
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

// #[polars_expr(output_type=Int32)]
pub fn cdlkicking(inputs: &[Series]) -> PolarsResult<Series> {
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

// #[polars_expr(output_type=Int32)]
pub fn cdlkickingbylength(inputs: &[Series]) -> PolarsResult<Series> {
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

// #[polars_expr(output_type=Int32)]
pub fn cdlladderbottom(inputs: &[Series]) -> PolarsResult<Series> {
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

// #[polars_expr(output_type=Int32)]
pub fn cdllongleggeddoji(inputs: &[Series]) -> PolarsResult<Series> {
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

// #[polars_expr(output_type=Int32)]
pub fn cdllongline(inputs: &[Series]) -> PolarsResult<Series> {
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

// #[polars_expr(output_type=Int32)]
pub fn cdlmarubozu(inputs: &[Series]) -> PolarsResult<Series> {
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

// #[polars_expr(output_type=Int32)]
pub fn cdlmatchinglow(inputs: &[Series]) -> PolarsResult<Series> {
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

// #[polars_expr(output_type=Int32)]
pub fn cdlmathold(inputs: &[Series], kwargs: CDLKwargs) -> PolarsResult<Series> {
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

// #[polars_expr(output_type=Int32)]
pub fn cdlmorningdojistar(inputs: &[Series], kwargs: CDLKwargs) -> PolarsResult<Series> {
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

// #[polars_expr(output_type=Int32)]
pub fn cdlmorningstar(inputs: &[Series], kwargs: CDLKwargs) -> PolarsResult<Series> {
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

// #[polars_expr(output_type=Int32)]
pub fn cdlonneck(inputs: &[Series]) -> PolarsResult<Series> {
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

// #[polars_expr(output_type=Int32)]
pub fn cdlpiercing(inputs: &[Series]) -> PolarsResult<Series> {
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

// #[polars_expr(output_type=Int32)]
pub fn cdlrickshawman(inputs: &[Series]) -> PolarsResult<Series> {
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

// #[polars_expr(output_type=Int32)]
pub fn cdlrisefall3methods(inputs: &[Series]) -> PolarsResult<Series> {
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

// #[polars_expr(output_type=Int32)]
pub fn cdlseparatinglines(inputs: &[Series]) -> PolarsResult<Series> {
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

// #[polars_expr(output_type=Int32)]
pub fn cdlshootingstar(inputs: &[Series]) -> PolarsResult<Series> {
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

// #[polars_expr(output_type=Int32)]
pub fn cdlshortline(inputs: &[Series]) -> PolarsResult<Series> {
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

// #[polars_expr(output_type=Int32)]
pub fn cdlspinningtop(inputs: &[Series]) -> PolarsResult<Series> {
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

// #[polars_expr(output_type=Int32)]
pub fn cdlstalledpattern(inputs: &[Series]) -> PolarsResult<Series> {
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

// #[polars_expr(output_type=Int32)]
pub fn cdlsticksandwich(inputs: &[Series]) -> PolarsResult<Series> {
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

// #[polars_expr(output_type=Int32)]
pub fn cdltakuri(inputs: &[Series]) -> PolarsResult<Series> {
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

// #[polars_expr(output_type=Int32)]
pub fn cdltasukigap(inputs: &[Series]) -> PolarsResult<Series> {
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

// #[polars_expr(output_type=Int32)]
pub fn cdlthrusting(inputs: &[Series]) -> PolarsResult<Series> {
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

// #[polars_expr(output_type=Int32)]
pub fn cdltristar(inputs: &[Series]) -> PolarsResult<Series> {
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

// #[polars_expr(output_type=Int32)]
pub fn cdlunique3river(inputs: &[Series]) -> PolarsResult<Series> {
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

// #[polars_expr(output_type=Int32)]
pub fn cdlupsidegap2crows(inputs: &[Series]) -> PolarsResult<Series> {
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

// #[polars_expr(output_type=Int32)]
pub fn cdlxsidegap3methods(inputs: &[Series]) -> PolarsResult<Series> {
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
