//! The sole TA-Lib boundary: borrowed inputs, initialized outputs, immutable settings.
use crate::utils::{broadcast_inputs, cast_series_to_f64};
use polars::prelude::*;
use serde::Deserialize;
use std::{collections::BTreeMap, sync::OnceLock};
use ta_lib::{
    abstract_api::{FuncId, InputType, OptInputType, OutputType, ParamHolder},
    Core, RetCode,
};

static CORE: OnceLock<Core> = OnceLock::new();
pub fn core() -> &'static Core {
    CORE.get_or_init(Core::new)
}

#[derive(Debug, Deserialize)]
#[serde(untagged)]
pub enum Param {
    Int(i32),
    Real(f64),
}
pub type Params = BTreeMap<String, Param>;

pub fn bind_params(holder: &mut ParamHolder<'_>, params: &Params) -> Result<(), RetCode> {
    for (i, opt) in holder.info().opt_inputs.iter().enumerate() {
        let key = opt
            .param_name
            .strip_prefix("optIn")
            .unwrap_or(opt.param_name)
            .to_lowercase();
        if let Some(value) = params.get(&key) {
            if key.contains("matype")
                && matches!(value,Param::Int(v) if !(0..=13).contains(v) && !(*v==i32::MIN && matches!(holder.info().id,FuncId::PVO|FuncId::KDJ)))
            {
                return Err(RetCode::BadParam);
            }
            match (&opt.kind, value) {
                (
                    OptInputType::RealRange { .. } | OptInputType::RealList { .. },
                    Param::Real(v),
                ) => {
                    holder.set_opt_input(i, *v)?;
                }
                (OptInputType::RealRange { .. } | OptInputType::RealList { .. }, Param::Int(v)) => {
                    holder.set_opt_input(i, f64::from(*v))?;
                }
                (_, Param::Int(v)) => {
                    let value = if holder.info().id == FuncId::PERCENTILE
                        && key == "timeperiod"
                        && *v == i32::MIN
                    {
                        30
                    } else {
                        *v
                    };
                    holder.set_opt_input(i, value)?;
                }
                _ => return Err(RetCode::BadParam),
            }
        }
    }
    Ok(())
}

fn error(code: RetCode) -> PolarsError {
    PolarsError::ComputeError(
        format!(
            "Could not compute indicator, err: {}",
            if code == RetCode::BadParam {
                "TA_BAD_PARAM".to_owned()
            } else {
                format!("{code:?}")
            }
        )
        .into(),
    )
}

pub(crate) enum Output {
    Real(Vec<f64>),
    Integer(Vec<i32>),
}

pub fn compute(
    id: FuncId,
    inputs: &[Series],
    params: &Params,
    order: &[usize],
    names: &[&str],
) -> PolarsResult<Series> {
    polars_ensure!(inputs.len() == order.len(), ShapeMismatch: "indicator input count differs");
    let aligned = broadcast_inputs(inputs)?;
    let prepared = order
        .iter()
        .map(|&i| cast_series_to_f64(&aligned[i]))
        .collect::<PolarsResult<Vec<_>>>()?;
    // A null conversion owns its memory until the safe TA-Lib call returns.
    let prepared = prepared
        .into_iter()
        .map(|s| {
            if s.null_count() == 0 {
                Ok(s)
            } else {
                Ok(s.f64()?.fill_null_with_values(f64::NAN)?.into_series())
            }
        })
        .collect::<PolarsResult<Vec<_>>>()?;
    let slices = prepared
        .iter()
        .map(|s| s.f64()?.cont_slice())
        .collect::<PolarsResult<Vec<_>>>()?;
    let len = slices.first().map_or(0, |s| s.len());
    polars_ensure!(len <= Core::INDEX_MAX + 1, ComputeError: "indicator input too long");
    let mut holder = id.new_call(core());
    bind_params(&mut holder, params).map_err(error)?;
    let lookback = crate::compat::lookback(id, params)
        .unwrap_or_else(|| holder.lookback())
        .map_err(error)?;
    let begin = (0..len)
        .find(|&row| slices.iter().all(|s| !s[row].is_nan()))
        .unwrap_or(len);
    let offset = begin.saturating_add(lookback).min(len);
    let mut outputs = id
        .info()
        .outputs
        .iter()
        .map(|o| match o.kind {
            // Use initialized NaNs rather than the allocator's zeroed/calloc path.
            // Zeroed allocations can have different page-fault costs in grouped calls.
            // Keep explicit range padding below; integer warmups remain zero.
            OutputType::Real => Output::Real(vec![f64::NAN; len]),
            OutputType::Integer => Output::Integer(vec![0; len]),
        })
        .collect::<Vec<_>>();
    let mut written = 0;
    if offset < len {
        let shifted = slices.iter().map(|s| &s[begin..]).collect::<Vec<_>>();
        if let Some(result) = crate::compat::call(id, &shifted, params, &mut outputs, offset) {
            let range = result.map_err(error)?;
            polars_ensure!(range.beg_idx == lookback && range.count <= len-offset, ComputeError: "unexpected compatibility output range");
            written = range.count;
            // A later nonfinite value must not change any earlier row's
            // rounding path. Preserve the normal crate result on that prefix.
            if let Some(prefix) = crate::compat::native_prefix(id, &shifted, params) {
                if prefix > lookback {
                    let prefix_values = shifted.iter().map(|s| &s[..prefix]).collect::<Vec<_>>();
                    let range =
                        native_range(holder, id, &prefix_values, &mut outputs, offset, prefix - 1)?;
                    polars_ensure!(range.beg_idx==lookback && range.count==prefix-lookback, ComputeError: "unexpected prefix output range");
                }
            }
        } else {
            let range = native_range(holder, id, &shifted, &mut outputs, offset, len - begin - 1)?;
            polars_ensure!(range.beg_idx==lookback && range.count<=len-offset, ComputeError: "unexpected TA-Lib output range");
            written = range.count;
        }
    }
    let fields = outputs
        .into_iter()
        .enumerate()
        .map(|(i, out)| {
            let name = names.get(i).copied().unwrap_or("");
            match out {
                Output::Real(mut v) => {
                    v[..offset].fill(f64::NAN);
                    v[offset + written..].fill(f64::NAN);
                    Series::from_vec(name, v)
                }
                Output::Integer(v) => Series::from_vec(name, v),
            }
        })
        .collect::<Vec<_>>();
    if fields.len() == 1 {
        Ok(fields.into_iter().next().unwrap())
    } else {
        Ok(StructChunked::new("", &fields)?.into_series())
    }
}

fn native_range<'a>(
    mut holder: ParamHolder<'a>,
    id: FuncId,
    values: &[&'a [f64]],
    outputs: &'a mut [Output],
    offset: usize,
    end: usize,
) -> PolarsResult<ta_lib::OutRange> {
    let mut input = 0;
    for (slot, info) in id.info().inputs.iter().enumerate() {
        match info.kind {
            InputType::Real => {
                holder.set_input(slot, values[input]).map_err(error)?;
                input += 1;
            }
            InputType::Price => {
                let mut price = [None; 6];
                for (bit, value) in price.iter_mut().enumerate() {
                    if info.flags.0 & (1 << bit) != 0 {
                        *value = Some(values[input]);
                        input += 1;
                    }
                }
                holder
                    .set_price_input(
                        slot, price[0], price[1], price[2], price[3], price[4], price[5],
                    )
                    .map_err(error)?;
            }
            _ => return Err(error(RetCode::BadParam)),
        }
    }
    for (i, out) in outputs.iter_mut().enumerate() {
        match out {
            Output::Real(v) => {
                holder.set_output(i, &mut v[offset..]).map_err(error)?;
            }
            Output::Integer(v) => {
                holder.set_int_output(i, &mut v[offset..]).map_err(error)?;
            }
        }
    }
    let range = holder.call(0, end).map_err(error)?;
    Ok(range)
}
