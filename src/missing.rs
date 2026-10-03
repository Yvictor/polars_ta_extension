//! Missing-input handling shared by every indicator plugin.
//!
//! TA-Lib does not support non-finite inputs: a NaN inside an input array has
//! undefined results, and TA-Lib 0.8.1 turns it into finite values for several
//! indicators (for example RSI returns 0.0 for every later row, issue #42).
//! Leading missing rows are already skipped by the indicator wrappers. For any
//! later null, NaN or infinite input, every output row that can depend on it is
//! set to null:
//!
//! * recursive or path-dependent indicators: from the missing row to the end;
//! * window-bounded indicators: the missing row and the next `lookback` rows.
//!
//! Masking runs inside each indicator plugin, so under `.over(...)` or
//! `group_by(...).agg(...)` it sees one partition at a time and a missing
//! value never affects another partition. Inputs without missing values cost
//! one vectorised scan and are returned untouched.

use std::ffi::{CStr, CString};

use polars::export::arrow::array::PrimitiveArray;
use polars::export::arrow::bitmap::Bitmap;
use polars::prelude::*;
use polars_core::POOL;
use pyo3::exceptions::PyValueError;
use pyo3::types::PyDict;
use pyo3::{pyfunction, PyResult};
use rayon::prelude::*;
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
    /// Run the unmasked indicator, then null the rows that depend on missing inputs.
    pub fn apply(
        self,
        inputs: &[Series],
        indicator: impl FnOnce(K) -> PolarsResult<Series>,
    ) -> PolarsResult<Series> {
        // Scan before computing: the scan pulls the inputs into cache for TA-Lib
        // instead of re-reading them from memory afterwards.
        let mut any_missing = false;
        if self.lookback >= 0 {
            for s in inputs {
                any_missing |= has_missing(s)?;
            }
        }
        let output = indicator(self.params)?;
        if !any_missing {
            return Ok(output);
        }
        let Some(missing) = missing_rows(inputs, output.len())? else {
            return Ok(output);
        };
        match masked_rows(&missing, self.lookback as usize, self.recursive) {
            Some(valid) => apply_validity(&output, &valid),
            None => Ok(output),
        }
    }
}

/// Inputs at least this long are scanned in parallel on Polars' thread pool:
/// the scan is memory-bound, so spreading it over cores hides most of its cost.
const PARALLEL_SCAN: usize = 1 << 17;

macro_rules! all_finite {
    ($name:ident, $t:ty) => {
        fn $name(values: &[$t]) -> bool {
            // Branch-free per block so the inner loop vectorises.
            let block = |b: &[$t]| b.iter().fold(true, |ok, v| ok & v.is_finite());
            if values.len() >= PARALLEL_SCAN {
                POOL.install(|| values.par_chunks(1 << 15).all(block))
            } else {
                values.chunks(1024).all(block)
            }
        }
    };
}
all_finite!(all_finite_f64, f64);
all_finite!(all_finite_f32, f32);

fn has_missing(s: &Series) -> PolarsResult<bool> {
    if s.null_count() > 0 {
        return Ok(true);
    }
    Ok(match s.dtype() {
        DataType::Float64 => !s.f64()?.downcast_iter().all(|a| all_finite_f64(a.values())),
        DataType::Float32 => !s.f32()?.downcast_iter().all(|a| all_finite_f32(a.values())),
        _ => false,
    })
}

/// Per-row missing flags for inputs known to contain a missing value. Length-one
/// inputs are broadcast literals and apply to every row.
fn missing_rows(inputs: &[Series], len: usize) -> PolarsResult<Option<Vec<bool>>> {
    let mut missing = vec![false; len];
    for s in inputs {
        let values = match s.dtype() {
            DataType::Float64 => s.clone(),
            _ => s.cast(&DataType::Float64)?,
        };
        let values = values.f64()?;
        if values.len() == 1 && len != 1 {
            if !values.get(0).map_or(false, f64::is_finite) {
                missing.iter_mut().for_each(|m| *m = true);
            }
            continue;
        }
        polars_ensure!(
            values.len() == len,
            ShapeMismatch: "indicator output length differs from its inputs"
        );
        let mut row = 0;
        for arr in values.downcast_iter() {
            match arr.validity() {
                Some(validity) => {
                    for (v, ok) in arr.values().iter().zip(validity.iter()) {
                        missing[row] |= !(ok && v.is_finite());
                        row += 1;
                    }
                }
                None => {
                    for v in arr.values().iter() {
                        missing[row] |= !v.is_finite();
                        row += 1;
                    }
                }
            }
        }
    }
    Ok(Some(missing))
}

/// Validity after masking (false = null): missing inputs after the first
/// complete row, plus the rows that depend on them. Leading missing rows keep
/// the wrappers' warm-up output. None when nothing is masked.
fn masked_rows(missing: &[bool], lookback: usize, recursive: bool) -> Option<Bitmap> {
    let start = missing.iter().position(|m| !m)?;
    let first = start + 1 + missing[start + 1..].iter().position(|&m| m)?;
    let mut until = 0usize;
    let valid: Bitmap = missing
        .iter()
        .enumerate()
        .map(|(row, &m)| {
            if row >= first && m {
                until = if recursive {
                    usize::MAX
                } else {
                    until.max(row.saturating_add(lookback))
                };
            }
            !(row >= first && row <= until)
        })
        .collect();
    Some(valid)
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
    use super::masked_rows;

    fn nulls(missing: &[bool], lookback: usize, recursive: bool) -> Vec<bool> {
        masked_rows(missing, lookback, recursive)
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
