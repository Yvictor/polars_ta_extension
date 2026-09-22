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

pub fn make_default_vec<T>(len: usize) -> Vec<T>
where
    T: Copy + CustomDefault,
{
    vec![T::default(); len]
}

pub fn cannot_produce_output(len: usize, lookback: i32) -> bool {
    lookback >= 0 && (lookback as usize) >= len
}

pub fn check_begin_idx1(len: usize, arr_ptr: *const f64) -> usize {
    let mut begin_idx = 0;
    for i in 0..len {
        if unsafe { (*arr_ptr.offset(i as isize)).is_nan() } {
            begin_idx = i + 1;
        } else {
            break;
        }
    }
    begin_idx
}

pub fn check_begin_idx2(len: usize, arr1_ptr: *const f64, arr2_ptr: *const f64) -> usize {
    let mut begin_idx = 0;
    for i in 0..len {
        if unsafe { (*arr1_ptr.offset(i as isize)).is_nan() }
            | unsafe { (*arr2_ptr.offset(i as isize)).is_nan() }
        {
            begin_idx = i + 1;
        } else {
            break;
        }
    }
    begin_idx
}

pub fn check_begin_idx3(
    len: usize,
    arr1_ptr: *const f64,
    arr2_ptr: *const f64,
    arr3_ptr: *const f64,
) -> usize {
    let mut begin_idx = 0;
    for i in 0..len {
        if unsafe { (*arr1_ptr.offset(i as isize)).is_nan() }
            | unsafe { (*arr2_ptr.offset(i as isize)).is_nan() }
            | unsafe { (*arr3_ptr.offset(i as isize)).is_nan() }
        {
            begin_idx = i + 1;
        } else {
            break;
        }
    }
    begin_idx
}

pub fn check_begin_idx4(
    len: usize,
    arr1_ptr: *const f64,
    arr2_ptr: *const f64,
    arr3_ptr: *const f64,
    arr4_ptr: *const f64,
) -> usize {
    let mut begin_idx = 0;
    for i in 0..len {
        if unsafe { (*arr1_ptr.offset(i as isize)).is_nan() }
            | unsafe { (*arr2_ptr.offset(i as isize)).is_nan() }
            | unsafe { (*arr3_ptr.offset(i as isize)).is_nan() }
            | unsafe { (*arr4_ptr.offset(i as isize)).is_nan() }
        {
            begin_idx = i + 1;
        } else {
            break;
        }
    }
    begin_idx
}

/// An output allocation whose initialized prefix is the warm-up padding.
/// C writes into spare capacity; only its reported initialized range is exposed.
pub(crate) struct OutputBuffer<T: Copy + CustomDefault> {
    values: Vec<T>,
    len: usize,
}

impl<T: Copy + CustomDefault> OutputBuffer<T> {
    pub(crate) fn new(len: usize, padding: usize) -> Self {
        assert!(padding <= len);
        let mut values = Vec::with_capacity(len);
        values.resize(padding, T::default());
        Self { values, len }
    }

    pub(crate) fn as_mut_ptr(&mut self) -> *mut T {
        // The one-past-initialized pointer is inside this allocation's capacity.
        unsafe { self.values.as_mut_ptr().add(self.values.len()) }
    }

    /// # Safety
    /// For valid output metadata after a successful TA-Lib call, `out_size` values starting at
    /// `as_mut_ptr()` must have been initialized. On a C error, drop the buffer
    /// instead: the Vec still exposes only the initialized padding.
    pub(crate) unsafe fn finish(
        mut self,
        out_begin: i32,
        out_size: i32,
        lookback: i32,
    ) -> Result<Vec<T>, talib_sys::TA_RetCode> {
        if out_begin != lookback || out_size < 0 || out_size as usize > self.len - self.values.len()
        {
            return Err(talib_sys::TA_RetCode::TA_INTERNAL_ERROR);
        }
        self.values.set_len(self.values.len() + out_size as usize);
        // Preserve padding if an upstream function writes fewer rows than expected.
        self.values.resize(self.len, T::default());
        Ok(self.values)
    }
}

#[cfg(test)]
mod output_tests {
    use super::OutputBuffer;
    use talib_sys::TA_RetCode;

    #[test]
    fn only_written_values_are_exposed_and_the_tail_is_padded() {
        let mut out = OutputBuffer::<f64>::new(5, 2);
        unsafe {
            out.as_mut_ptr().write(42.);
            let values = out.finish(2, 1, 2).unwrap();
            assert!(values[..2].iter().all(|v| v.is_nan()));
            assert_eq!(values[2], 42.);
            assert!(values[3..].iter().all(|v| v.is_nan()));
        }
        let out = OutputBuffer::<i32>::new(4, 1);
        assert_eq!(unsafe { out.finish(1, 0, 1) }.unwrap(), vec![0; 4]);
    }

    #[test]
    fn invalid_output_metadata_is_rejected_before_extending_length() {
        for (begin, size) in [(0, 0), (1, -1), (1, 4)] {
            let out = OutputBuffer::<i32>::new(4, 1);
            assert_eq!(
                unsafe { out.finish(begin, size, 1) },
                Err(TA_RetCode::TA_INTERNAL_ERROR)
            );
        }
    }
}
