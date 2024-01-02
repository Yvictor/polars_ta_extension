use polars::prelude::{Float64Chunked, IntoSeries, PolarsError, PolarsResult, Series};
use talib_sys::TA_RetCode;

pub fn get_series_f64_ptr(series: &mut Series) -> PolarsResult<(*const f64, Option<Series>)> {
    if series.has_validity() {
        let v: Float64Chunked = series
            .f64()?
            .apply_generic(|x| Some(x.unwrap_or(std::f64::NAN)));
        let mut ser = v.into_series();
        Ok((ser.as_single_ptr()? as *const f64, Some(ser)))
    } else {
        Ok((series.as_single_ptr()? as *const f64, None))
    }
}

pub fn ta_code2err(ret_code: TA_RetCode) -> PolarsResult<Series> {
    Err(PolarsError::ComputeError(
        format!("Could not compute indicator, err: {:?}", ret_code).into(),
    ))
}

// pub fn get_series_ptr(inputs: &[Series], idx: usize) -> PolarsResult<(*const f64, Option<Series>)> {
//     let mut series = inputs[idx].to_float()?.rechunk();
//     if series.has_validity() {
//         let v: Float64Chunked = series
//             .f64()?
//             .apply_generic(|x| Some(x.unwrap_or(std::f64::NAN)));
//         let mut ser = v.into_series();
//         Ok((ser.as_single_ptr()? as *const f64, Some(ser)))
//     } else {
//         Ok((series.as_single_ptr()? as *const f64, None))
//     }
// }

// TODO make this generic
// fn to_series<T>(out: Vec<<T as PolarsNumericType>::Native>) -> PolarsResult<Series>
// where
//     T: PolarsNumericType + 'static,
//     ChunkedArray<T>: Sized,
// {
//     let out_ser = ChunkedArray::<T>::from_vec("", out);
//     out_ser.into_series()
// }

// fn to_series<T>(out: Vec<<T as PolarsNumericType>::Native>) -> PolarsResult<Series>
// where
//     T: PolarsNumericType,
// {
//     let out_ser = ChunkedArray::<T>::from_vec("", out);
//     out_ser.into_series()
// }
