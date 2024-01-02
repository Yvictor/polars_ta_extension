use polars::prelude::{PolarsResult, Series, Float64Chunked, IntoSeries};

pub trait CustomDefault {
    fn default() -> Self;
}

impl CustomDefault for f64 {
    fn default() -> Self {
        std::f64::NAN
    }
}

impl CustomDefault for i32 {
    fn default() -> Self {
        0
    }
}

pub fn make_vec<T>(len: usize, lookback: i32) -> (Vec<T>, *mut T)
where
    T: Copy + CustomDefault,
{
    let mut vec = Vec::with_capacity(len);
    for _ in 0..lookback {
        vec.push(T::default());
    }
    let ptr = vec[lookback as usize..].as_mut_ptr();
    (vec, ptr)
}


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
