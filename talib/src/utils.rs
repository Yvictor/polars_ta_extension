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