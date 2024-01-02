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

