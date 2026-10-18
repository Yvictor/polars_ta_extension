//! Null-input handling shared by every indicator plugin.
//!
//! A Polars null marks a missing observation. TA-Lib has no notion of missing
//! values: the wrappers hand nulls to C as NaN, and TA-Lib's results for NaN
//! inputs are undefined; TA-Lib 0.8.1 turns them into finite values for several
//! indicators (RSI returned 0.0 for every later row, issue #42). Leading nulls
//! are already skipped by the indicator wrappers. For any later null input,
//! every output row that can depend on it is set to null:
//!
//! * recursive or path-dependent indicators: from the null row to the end;
//! * window-bounded indicators: the null row and the next `lookback` rows.
//!
//! NaN and infinity are ordinary floating-point values in Polars, so they are
//! passed to TA-Lib unchanged; callers who mean "missing" convert them with
//! `fill_nan(None)`. Masking runs inside each indicator plugin, so under
//! `.over(...)` or `group_by(...).agg(...)` it sees one partition at a time and
//! a null never affects another partition. Inputs without nulls are detected
//! from Polars' null counts, without reading their values.

use std::ffi::{CStr, CString};

use polars::export::arrow::array::PrimitiveArray;
use polars::export::arrow::bitmap::{Bitmap, MutableBitmap};
use polars::prelude::*;
use pyo3::exceptions::PyValueError;
use pyo3::types::PyDict;
use pyo3::{pyfunction, PyResult};
use serde::Deserialize;
use talib_sys::*;

/// Upstream lookback of `name` for the given optional parameters, using the
/// TA-Lib abstract interface. Parameter names follow the Python API
/// (`optInTimePeriod` -> `timeperiod`); omitted parameters keep upstream defaults.
#[pyfunction]
pub fn lookback(name: &str, params: Option<&PyDict>) -> PyResult<i32> {
    let bad = |what: String| PyValueError::new_err(format!("{name}: {what}"));
    let c_name = CString::new(name.to_uppercase()).map_err(|e| bad(e.to_string()))?;
    unsafe {
        let mut handle: *const TA_FuncHandle = std::ptr::null();
        if TA_GetFuncHandle(c_name.as_ptr(), &mut handle) != TA_RetCode::TA_SUCCESS {
            return Err(bad("unknown TA-Lib function".into()));
        }
        let mut info: *const TA_FuncInfo = std::ptr::null();
        if TA_GetFuncInfo(handle, &mut info) != TA_RetCode::TA_SUCCESS {
            return Err(bad("no function information".into()));
        }
        let mut holder: *mut TA_ParamHolder = std::ptr::null_mut();
        if TA_ParamHolderAlloc(handle, &mut holder) != TA_RetCode::TA_SUCCESS {
            return Err(bad("could not allocate parameters".into()));
        }
        let result = (|| -> PyResult<i32> {
            for index in 0..(*info).nbOptInput {
                let mut param: *const TA_OptInputParameterInfo = std::ptr::null();
                if TA_GetOptInputParameterInfo(handle, index, &mut param) != TA_RetCode::TA_SUCCESS
                {
                    return Err(bad(format!("no information for parameter {index}")));
                }
                let raw = CStr::from_ptr((*param).paramName).to_string_lossy();
                let key = raw.strip_prefix("optIn").unwrap_or(&raw).to_lowercase();
                let Some(value) = params.and_then(|p| p.get_item(key.as_str()).ok().flatten())
                else {
                    continue;
                };
                let is_real = (*param).type_ == TA_OptInputParameterType_TA_OptInput_RealRange
                    || (*param).type_ == TA_OptInputParameterType_TA_OptInput_RealList;
                let code = if is_real {
                    TA_SetOptInputParamReal(holder, index, value.extract::<f64>()?)
                } else {
                    TA_SetOptInputParamInteger(holder, index, value.extract::<i32>()?)
                };
                if code != TA_RetCode::TA_SUCCESS {
                    return Err(bad(format!("invalid value for {key}: {code:?}")));
                }
            }
            let mut out: TA_Integer = 0;
            match TA_GetLookback(holder, &mut out) {
                TA_RetCode::TA_SUCCESS => Ok(out),
                code => Err(bad(format!("invalid parameters: {code:?}"))),
            }
        })();
        TA_ParamHolderFree(holder);
        result
    }
}

/// Plugin kwargs: the indicator's own parameters plus its missing-input policy,
/// both supplied by `register_plugin` on the Python side.
#[derive(Deserialize)]
pub struct Masked<K> {
    pub params: K,
    /// Upstream lookback for these parameters; negative disables masking.
    pub lookback: i32,
    /// Whether a missing input affects every later row.
    pub recursive: bool,
}

/// Parameters of indicators that take none.
#[derive(Deserialize)]
pub struct NoParams {}

impl<K> Masked<K> {
    /// Run the unmasked indicator, then null the rows that depend on null inputs.
    pub fn apply(
        self,
        inputs: &[Series],
        indicator: impl FnOnce(K) -> PolarsResult<Series>,
    ) -> PolarsResult<Series> {
        let output = indicator(self.params)?;
        // Null counts are metadata: inputs without nulls cost nothing here.
        if self.lookback < 0 || inputs.iter().all(|s| s.null_count() == 0) {
            return Ok(output);
        }
        let (present, start) = presence(inputs, output.len())?;
        match masked_rows(&present, start, self.lookback as usize, self.recursive) {
            Some(valid) => apply_validity(&output, &valid),
            None => Ok(output),
        }
    }
}

/// Rows where every input is present (the AND of the inputs' validity), and the
/// first row where every input is present and not NaN: the wrappers skip the
/// rows before it as warm-up, whatever they hold. Length-one inputs are
/// broadcast literals and apply to every row.
fn presence(inputs: &[Series], len: usize) -> PolarsResult<(Bitmap, Option<usize>)> {
    let mut present: Bitmap = MutableBitmap::from_len_set(len).into();
    let mut floats = Vec::new();
    for s in inputs {
        if s.len() == 1 && len != 1 {
            let value = s.cast(&DataType::Float64)?.f64()?.get(0);
            match value {
                None => return Ok((MutableBitmap::from_len_zeroed(len).into(), None)),
                Some(v) if v.is_nan() => return Ok((present, None)),
                Some(_) => continue,
            }
        }
        polars_ensure!(
            s.len() == len,
            ShapeMismatch: "indicator output length differs from its inputs"
        );
        let s = s.rechunk();
        if let Some(validity) = s.chunks().first().and_then(|a| a.validity()) {
            present = &present & validity;
        }
        if s.dtype().is_float() {
            floats.push(s.cast(&DataType::Float64)?);
        }
    }
    let floats: Vec<&[f64]> = floats
        .iter()
        .map(|s| {
            Ok(s.f64()?
                .downcast_iter()
                .next()
                .map_or(&[][..], |a| a.values().as_slice()))
        })
        .collect::<PolarsResult<_>>()?;
    // Usually row 0: only the warm-up prefix is inspected.
    let start = (0..len)
        .find(|&row| present.get_bit(row) && floats.iter().all(|values| !values[row].is_nan()));
    Ok((present, start))
}

/// Validity after masking (false = null): null inputs after the first usable
/// row `start`, plus the rows that depend on them. Rows before `start` keep the
/// wrappers' warm-up output. None when nothing is masked.
fn masked_rows(
    present: &Bitmap,
    start: Option<usize>,
    lookback: usize,
    recursive: bool,
) -> Option<Bitmap> {
    let len = present.len();
    let first = present
        .iter()
        .enumerate()
        .skip(start? + 1)
        .find(|(_, ok)| !ok)?
        .0;
    let mut valid = MutableBitmap::with_capacity(len);
    valid.extend_constant(first, true);
    if recursive {
        valid.extend_constant(len - first, false);
    } else {
        let mut until = 0usize;
        for (row, ok) in present.iter().enumerate().skip(first) {
            if !ok {
                until = until.max(row.saturating_add(lookback));
            }
            valid.push(row > until);
        }
    }
    Some(valid.into())
}

fn with_validity<T: polars::datatypes::PolarsNumericType>(
    ca: &ChunkedArray<T>,
    valid: &Bitmap,
) -> ChunkedArray<T> {
    let ca = ca.rechunk();
    let arr: &PrimitiveArray<T::Native> = ca.downcast_iter().next().unwrap();
    let validity = match arr.validity() {
        Some(existing) => existing & valid,
        None => valid.clone(),
    };
    ChunkedArray::with_chunk(ca.name(), arr.clone().with_validity(Some(validity)))
}

fn apply_validity(series: &Series, valid: &Bitmap) -> PolarsResult<Series> {
    polars_ensure!(
        series.len() == valid.len(),
        ShapeMismatch: "indicator output length differs from its inputs"
    );
    Ok(match series.dtype() {
        DataType::Float64 => with_validity(series.f64()?, valid).into_series(),
        DataType::Int32 => with_validity(series.i32()?, valid).into_series(),
        DataType::Struct(_) => {
            let fields = series
                .struct_()?
                .fields()
                .iter()
                .map(|f| apply_validity(f, valid))
                .collect::<PolarsResult<Vec<_>>>()?;
            StructChunked::new(series.name(), &fields)?.into_series()
        }
        other => polars_bail!(ComputeError: "cannot mask indicator output of type {other}"),
    })
}

#[cfg(test)]
mod tests {
    use super::{masked_rows, Bitmap};

    fn nulls(missing: &[bool], lookback: usize, recursive: bool) -> Vec<bool> {
        let present: Bitmap = missing.iter().map(|m| !m).collect();
        let start = missing.iter().position(|m| !m);
        masked_rows(&present, start, lookback, recursive)
            .map(|valid| valid.iter().map(|v| !v).collect())
            .unwrap_or_else(|| vec![false; missing.len()])
    }

    #[test]
    fn leading_missing_rows_are_not_masked() {
        assert_eq!(nulls(&[true, true, false, false], 2, true), [false; 4]);
        assert_eq!(nulls(&[true, true, true], 2, true), [false; 3]);
        assert_eq!(nulls(&[], 2, true), Vec::<bool>::new());
    }

    #[test]
    fn nulls_inside_nan_warm_up_are_not_masked() {
        // [NaN, null, x, x, null, x]: the wrapper starts at row 2.
        let present: Bitmap = [true, false, true, true, false, true].into_iter().collect();
        let valid = masked_rows(&present, Some(2), 0, true).unwrap();
        let masked: Vec<bool> = valid.iter().map(|v| !v).collect();
        assert_eq!(masked, [false, false, false, false, true, true]);
        assert!(masked_rows(&present, None, 0, true).is_none());
    }

    #[test]
    fn recursive_masks_to_the_end() {
        let m = [true, false, false, true, false, false];
        assert_eq!(nulls(&m, 0, true), [false, false, false, true, true, true]);
    }

    #[test]
    fn window_masks_lookback_rows_and_merges_overlaps() {
        let m = [false, true, false, false, false, false, true, false, false];
        assert_eq!(
            nulls(&m, 2, false),
            [false, true, true, true, false, false, true, true, true]
        );
        assert_eq!(nulls(&m, 0, false), m);
        let close = [false, true, false, true, false, false, false];
        assert_eq!(
            nulls(&close, 2, false),
            [false, true, true, true, true, true, false]
        );
    }
}
