use polars::prelude::{PolarsResult, Series, Float64Chunked, IntoSeries};


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
