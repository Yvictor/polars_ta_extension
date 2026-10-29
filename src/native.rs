//! The sole TA-Lib boundary: borrowed inputs, initialized outputs, immutable settings.
use crate::generated::option_key;
use crate::utils::{broadcast_inputs, cast_series_to_f64};
use polars::prelude::*;
use std::{collections::BTreeMap, sync::OnceLock};
use ta_lib::{
    abstract_api::{FuncId, InputType, OptInputType, OutputType, ParamHolder},
    Core, RetCode,
};

static CORE: OnceLock<Core> = OnceLock::new();
pub fn core() -> &'static Core {
    CORE.get_or_init(Core::new)
}

pub use crate::params::Param;
pub type Params = BTreeMap<String, Param>;

pub fn bind_params(holder: &mut ParamHolder<'_>, params: &Params) -> Result<(), RetCode> {
    for (i, opt) in holder.info().opt_inputs.iter().enumerate() {
        let key = option_key(opt.param_name);
        if let Some(value) = params.get(key.as_ref()) {
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

pub fn compute<const INPUTS: usize, const OUTPUTS: usize>(
    id: FuncId,
    inputs: &[Series],
    params: &Params,
    order: &[usize],
    names: &[&str],
) -> PolarsResult<Series> {
    polars_ensure!(inputs.len() == order.len(), ShapeMismatch: "indicator input count differs");
    let aligned = broadcast_inputs(inputs)?;
    // Series clones share Arrow storage; only casts, rechunks and null fills
    // materialize numeric input buffers. Keep owners alive through the call.
    // Arity is frozen by the generated plugin entry point. Keep the owners and
    // borrowed slice descriptors on the stack instead of allocating two Vecs
    // for every partition of a native Polars `.over()` expression.
    polars_ensure!(order.len() == INPUTS && id.info().outputs.len() == OUTPUTS,
        ShapeMismatch: "indicator metadata arity differs");
    let mut prepared: [Option<Series>; INPUTS] = std::array::from_fn(|_| None);
    for (slot, &i) in prepared.iter_mut().zip(order) {
        let s = cast_series_to_f64(&aligned[i])?;
        *slot = Some(if s.null_count() == 0 {
            s
        } else {
            s.f64()?.fill_null_with_values(f64::NAN)?.into_series()
        });
    }
    let mut slices: [&[f64]; INPUTS] = [&[]; INPUTS];
    for (slice, s) in slices.iter_mut().zip(&prepared) {
        *slice = s.as_ref().unwrap().f64()?.cont_slice()?;
    }
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
    let first_input = slices.first().copied();
    let mut first_class = None;
    let mut outputs: [Output; OUTPUTS] = std::array::from_fn(|i| match id.info().outputs[i].kind {
        // Use initialized NaNs rather than the allocator's zeroed/calloc path.
        // Zeroed allocations can have different page-fault costs in grouped calls.
        // Keep explicit range padding below; integer warmups remain zero.
        OutputType::Real => {
            if i == 0 {
                if let Some((values, class)) = first_input.and_then(|values| {
                    crate::compat::initialized_first(id, values, params, begin, offset)
                }) {
                    first_class = Some(class);
                    return Output::Real(values);
                }
            }
            Output::Real(vec![f64::NAN; len])
        }
        OutputType::Integer => {
            // Upstream receives a fully initialized slice, including warm-up padding.
            let mut values = Vec::with_capacity(len);
            values.resize(len, 0);
            Output::Integer(values)
        }
    });
    let mut written = 0;
    if offset < len {
        // Reuse descriptors after recording the original length and offset.
        for values in &mut slices {
            *values = &values[begin..];
        }
        let shifted = &slices;
        if let Some(call) = crate::compat::call_with_class(
            id, shifted, params, &mut outputs, offset, first_class,
        ) {
            let range = call.result.map_err(error)?;
            polars_ensure!(range.beg_idx == lookback && range.count <= len-offset, ComputeError: "unexpected compatibility output range");
            written = range.count;
            // A later nonfinite value must not change any earlier row's
            // rounding path. Preserve the normal crate result on that prefix.
            if let Some(prefix) = call
                .restore_native_prefix
                .then(|| crate::compat::native_prefix(id, shifted, params))
                .flatten()
            {
                if prefix > lookback {
                    let prefix_values = shifted.iter().map(|s| &s[..prefix]).collect::<Vec<_>>();
                    let range =
                        native_range(holder, id, &prefix_values, &mut outputs, offset, prefix - 1)?;
                    polars_ensure!(range.beg_idx==lookback && range.count==prefix-lookback, ComputeError: "unexpected prefix output range");
                }
            }
        } else {
            let range = native_range(holder, id, shifted, &mut outputs, offset, len - begin - 1)?;
            polars_ensure!(range.beg_idx==lookback && range.count<=len-offset, ComputeError: "unexpected TA-Lib output range");
            written = range.count;
        }
    }
    // Most indicators have one output; avoid collecting a one-element fields Vec.
    if outputs.len() == 1 {
        return Ok(output_series(
            outputs.into_iter().next().unwrap(),
            names.first().copied().unwrap_or(""),
            offset,
            written,
        ));
    }
    // StructChunked borrows this slice while constructing its owned fields.
    // The frozen output arity lets us avoid a descriptor Vec per partition.
    let mut names = names.iter().copied();
    let fields = outputs.map(|out| output_series(out, names.next().unwrap_or(""), offset, written));
    Ok(StructChunked::new("", &fields)?.into_series())
}

pub(crate) fn output_series(out: Output, name: &str, offset: usize, written: usize) -> Series {
    match out {
        Output::Real(mut v) => {
            v[..offset].fill(f64::NAN);
            v[offset + written..].fill(f64::NAN);
            Series::from_vec(name, v)
        }
        Output::Integer(v) => Series::from_vec(name, v),
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

#[cfg(test)]
mod integer_output_tests {
    use super::*;

    #[test]
    fn empty_and_warmup_only_integer_results_keep_zero_padding() {
        for len in [0, 1, 10] {
            let inputs = [
                Series::from_vec("open", vec![99.9; len]),
                Series::from_vec("high", vec![101.; len]),
                Series::from_vec("low", vec![99.; len]),
                Series::from_vec("close", vec![100.; len]),
            ];
            let output =
                compute::<4, 1>(FuncId::CDLDOJI, &inputs, &Params::new(), &[0, 1, 2, 3], &[])
                    .unwrap();
            assert_eq!(output.i32().unwrap().cont_slice().unwrap(), vec![0; len]);
        }
        for len in [0, 1, 20, 63] {
            let close = Series::from_vec("close", vec![100.; len]);
            let output =
                compute::<1, 1>(FuncId::HT_TRENDMODE, &[close], &Params::new(), &[0], &[]).unwrap();
            assert_eq!(output.i32().unwrap().cont_slice().unwrap(), vec![0; len]);
        }
    }

    #[test]
    fn sliced_nullable_prices_keep_integer_warmup_and_written_values() {
        let price = |name: &str, shift: f64| {
            let values: Vec<Option<f64>> = (0..22)
                .map(|i| {
                    if i < 2 {
                        Some(-999.)
                    } else if i < 5 {
                        None
                    } else {
                        Some(100. + (i - 5) as f64 + shift)
                    }
                })
                .collect();
            Series::new(name, values).slice(2, 20)
        };
        let inputs = [
            price("open", -0.1),
            price("high", 1.),
            price("low", -1.),
            price("close", 0.),
        ];
        let output =
            compute::<4, 1>(FuncId::CDLDOJI, &inputs, &Params::new(), &[0, 1, 2, 3], &[]).unwrap();
        let result = output.i32().unwrap().cont_slice().unwrap();
        assert_eq!(&result[..13], &[0; 13]);
        assert_eq!(&result[13..], &[100; 7]);
        assert_eq!(output.null_count(), 0);
    }

    #[test]
    fn two_integer_outputs_preserve_leading_padding_and_legacy_index_ties() {
        let close = Series::from_vec(
            "close",
            vec![f64::NAN, f64::NAN, 0., 5., 5., 1., 1., 1., 7., 7., 0.],
        );
        let params = Params::from([("timeperiod".into(), Param::Int(3))]);
        let output = compute::<1, 2>(
            FuncId::MINMAXINDEX,
            &[close],
            &params,
            &[0],
            &["minidx", "maxidx"],
        )
        .unwrap();
        let fields = output.struct_().unwrap().fields();
        assert_eq!(fields[0].name(), "minidx");
        assert_eq!(fields[1].name(), "maxidx");
        assert_eq!(
            fields[0].i32().unwrap().cont_slice().unwrap(),
            &[0, 0, 0, 0, 0, 3, 4, 5, 5, 5, 8]
        );
        assert_eq!(
            fields[1].i32().unwrap().cont_slice().unwrap(),
            &[0, 0, 0, 0, 1, 1, 2, 3, 6, 7, 7]
        );
    }

    #[test]
    fn mixed_real_and_integer_outputs_keep_distinct_warmup_values() {
        let close: Vec<f64> = (0..64)
            .map(|i| if i < 2 { f64::NAN } else { 100. + i as f64 })
            .collect();
        let inputs = [
            Series::from_vec("high", close.iter().map(|v| v + 1.).collect::<Vec<_>>()),
            Series::from_vec("low", close.iter().map(|v| v - 1.).collect::<Vec<_>>()),
            Series::from_vec("close", close),
        ];
        let lookback = FuncId::SUPERTREND.new_call(core()).lookback().unwrap();
        let offset = 2 + lookback;
        let output = compute::<3, 2>(
            FuncId::SUPERTREND,
            &inputs,
            &Params::new(),
            &[0, 1, 2],
            &["supertrend", "trend"],
        )
        .unwrap();
        let fields = output.struct_().unwrap().fields();
        let real = fields[0].f64().unwrap().cont_slice().unwrap();
        let integer = fields[1].i32().unwrap().cont_slice().unwrap();
        assert!(real[..offset].iter().all(|v| v.is_nan()));
        assert_eq!(&integer[..offset], vec![0; offset]);
        assert!(real[offset..].iter().all(|v| v.is_finite()));
        assert!(integer[offset..].iter().all(|v| matches!(v, -1 | 1)));
    }
}
