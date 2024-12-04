use polars::datatypes::DataType;
use polars::prelude::{ChunkFillNullValue, Float64Chunked, IntoSeries, PolarsError, PolarsResult, Series};
use talib_sys::TA_RetCode;

pub fn cast_series_to_f64(series: &Series) -> PolarsResult<Series> {
    Ok(match series.dtype() {
        DataType::Float64 => Ok(series.clone()),
        _ => series.cast(&DataType::Float64),
    }?
    .rechunk())
}

// pub fn get_series_f64_ptr(series: &mut Series) -> PolarsResult<(*const f64, Option<Series>)> {
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

pub fn get_series_f64_ptr(series: &mut Series) -> PolarsResult<(*const f64, Option<Series>)> {
    if series.null_count() > 0 {
        // 如果包含无效值，将其转换为 NaN
        let v: Float64Chunked = series
            .f64()?
            .fill_null_with_values(std::f64::NAN)?;
        let mut ser = v.into_series();
        Ok((ser.as_single_ptr()? as *const f64, Some(ser)))
    } else {
        // 没有无效值，直接返回原始数据的指针
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
