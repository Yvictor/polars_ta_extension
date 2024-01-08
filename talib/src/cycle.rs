use crate::utils::{check_begin_idx1, make_vec};
use talib_sys::{TA_HT_DCPERIOD_Lookback, TA_Integer, TA_RetCode, TA_HT_DCPERIOD};
use talib_sys::{TA_HT_DCPHASE_Lookback, TA_HT_DCPHASE};
use talib_sys::{TA_HT_PHASOR_Lookback, TA_HT_PHASOR};
use talib_sys::{TA_HT_SINE_Lookback, TA_HT_SINE};
use talib_sys::{TA_HT_TRENDMODE_Lookback, TA_HT_TRENDMODE};

pub fn ta_ht_dcperiod(real_ptr: *const f64, len: usize) -> Result<Vec<f64>, TA_RetCode> {
    let mut out_begin: TA_Integer = 0;
    let mut out_size: TA_Integer = 0;
    let begin_idx = check_begin_idx1(len, real_ptr) as i32;
    let end_idx = len as i32 - begin_idx - 1;
    let lookback = begin_idx + unsafe { TA_HT_DCPERIOD_Lookback() };
    let (mut out, ptr) = make_vec(len, lookback);
    let ret_code = unsafe {
        TA_HT_DCPERIOD(
            0,
            end_idx,
            real_ptr.offset(begin_idx as isize),
            &mut out_begin,
            &mut out_size,
            ptr,
        )
    };
    let out_size_begin = (begin_idx + out_begin + out_size) as usize;
    match ret_code {
        TA_RetCode::TA_SUCCESS => {
            if out_size != 0 {
                unsafe {
                    out.set_len(out_size_begin);
                }
            } else {
                unsafe {
                    out.set_len(len);
                }
            }
            Ok(out)
        }
        _ => Err(ret_code),
    }
}

pub fn ta_ht_dcphase(real_ptr: *const f64, len: usize) -> Result<Vec<f64>, TA_RetCode> {
    let mut out_begin: TA_Integer = 0;
    let mut out_size: TA_Integer = 0;
    let begin_idx = check_begin_idx1(len, real_ptr) as i32;
    let end_idx = len as i32 - begin_idx - 1;
    let lookback = begin_idx + unsafe { TA_HT_DCPHASE_Lookback() };
    let (mut out, ptr) = make_vec(len, lookback);
    let ret_code = unsafe {
        TA_HT_DCPHASE(
            0,
            end_idx,
            real_ptr.offset(begin_idx as isize),
            &mut out_begin,
            &mut out_size,
            ptr,
        )
    };
    let out_size_begin = (begin_idx + out_begin + out_size) as usize;
    match ret_code {
        TA_RetCode::TA_SUCCESS => {
            if out_size != 0 {
                unsafe {
                    out.set_len(out_size_begin);
                }
            } else {
                unsafe {
                    out.set_len(len);
                }
            }
            Ok(out)
        }
        _ => Err(ret_code),
    }
}

pub fn ta_ht_phasor(real_ptr: *const f64, len: usize) -> Result<(Vec<f64>, Vec<f64>), TA_RetCode> {
    let mut out_begin: TA_Integer = 0;
    let mut out_size: TA_Integer = 0;
    let begin_idx = check_begin_idx1(len, real_ptr) as i32;
    let end_idx = len as i32 - begin_idx - 1;
    let lookback = begin_idx + unsafe { TA_HT_PHASOR_Lookback() };
    let (mut out_in_phase, ptr_in_phase) = make_vec(len, lookback);
    let (mut out_quadrature, ptr_quadrature) = make_vec(len, lookback);
    let ret_code = unsafe {
        TA_HT_PHASOR(
            0,
            end_idx,
            real_ptr.offset(begin_idx as isize),
            &mut out_begin,
            &mut out_size,
            ptr_in_phase,
            ptr_quadrature,
        )
    };
    let out_size_begin = (begin_idx + out_begin + out_size) as usize;
    match ret_code {
        TA_RetCode::TA_SUCCESS => {
            if out_size != 0 {
                unsafe {
                    out_in_phase.set_len(out_size_begin);
                    out_quadrature.set_len(out_size_begin);
                }
            } else {
                unsafe {
                    out_in_phase.set_len(len);
                    out_quadrature.set_len(len);
                }
            }
            Ok((out_in_phase, out_quadrature))
        }
        _ => Err(ret_code),
    }
}

pub fn ta_ht_sine(real_ptr: *const f64, len: usize) -> Result<(Vec<f64>, Vec<f64>), TA_RetCode> {
    let mut out_begin: TA_Integer = 0;
    let mut out_size: TA_Integer = 0;
    let begin_idx = check_begin_idx1(len, real_ptr) as i32;
    let end_idx = len as i32 - begin_idx - 1;
    let lookback = begin_idx + unsafe { TA_HT_SINE_Lookback() };
    let (mut out_sine, ptr_sine) = make_vec(len, lookback);
    let (mut out_leadsine, ptr_leadsine) = make_vec(len, lookback);
    let ret_code = unsafe {
        TA_HT_SINE(
            0,
            end_idx,
            real_ptr.offset(begin_idx as isize),
            &mut out_begin,
            &mut out_size,
            ptr_sine,
            ptr_leadsine,
        )
    };
    let out_size_begin = (begin_idx + out_begin + out_size) as usize;
    match ret_code {
        TA_RetCode::TA_SUCCESS => {
            if out_size != 0 {
                unsafe {
                    out_sine.set_len(out_size_begin);
                    out_leadsine.set_len(out_size_begin);
                }
            } else {
                unsafe {
                    out_sine.set_len(len);
                    out_leadsine.set_len(len);
                }
            }
            Ok((out_sine, out_leadsine))
        }
        _ => Err(ret_code),
    }
}

pub fn ta_ht_trendmode(real_ptr: *const f64, len: usize) -> Result<Vec<i32>, TA_RetCode> {
    let mut out_begin: TA_Integer = 0;
    let mut out_size: TA_Integer = 0;
    let begin_idx = check_begin_idx1(len, real_ptr) as i32;
    let end_idx = len as i32 - begin_idx - 1;
    let lookback = begin_idx + unsafe { TA_HT_TRENDMODE_Lookback() };
    let (mut out, ptr) = make_vec(len, lookback);
    let ret_code = unsafe {
        TA_HT_TRENDMODE(
            0,
            end_idx,
            real_ptr.offset(begin_idx as isize),
            &mut out_begin,
            &mut out_size,
            ptr,
        )
    };
    let out_size_begin = (begin_idx + out_begin + out_size) as usize;
    match ret_code {
        TA_RetCode::TA_SUCCESS => {
            if out_size != 0 {
                unsafe {
                    out.set_len(out_size_begin);
                }
            } else {
                unsafe {
                    out.set_len(len);
                }
            }
            Ok(out)
        }
        _ => Err(ret_code),
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::f64::NAN;

    #[test]
    fn test_ta_ht_dcperiod() {
        // Test case 1
        let input1 = vec![
            8843.0, 8810.0, 8850.0, 8829.0, 9200.0, 8951.0, 9190.0, 9115.0, 9073.0, 9230.0, 9300.0,
            9278.0, 9185.0, 9269.0, 9350.0, 9498.0, 9452.0, 9722.0, 9730.0, 9800.0, 9759.0, 9867.0,
            10030.0, 10149.0, 10145.0, 10167.0, 9980.0, 9988.0, 10090.0, 10293.0, 10160.0, 10286.0,
            10020.0, 9875.0, 9701.0, 9740.0, 9602.0, 9630.0, 9845.0, 9693.0, 9760.0, 9675.0,
            9525.0, 9565.0, 9520.0, 9687.0, 9520.0, 8854.0, 8848.0, 8590.0,
        ];
        let expected_output1 = vec![
            NAN, NAN, NAN, NAN, NAN, NAN, NAN, NAN, NAN, NAN, NAN, NAN, NAN, NAN, NAN, NAN, NAN,
            NAN, NAN, NAN, NAN, NAN, NAN, NAN, NAN, NAN, NAN, NAN, NAN, NAN, NAN, NAN, 15.6467,
            17.2118, 18.9332, 20.8267, 22.8463, 25.0886, 27.5691, 30.307, 33.0743, 34.5043,
            34.6477, 33.9828, 32.8265, 31.7664, 30.7812, 29.7826, 28.7928, 27.8388,
        ];
        let res = ta_ht_dcperiod(input1.as_ptr(), input1.len()).unwrap();
        // let res_round: Vec<f64> = res
        //     .unwrap()
        //     .into_iter()
        //     .map(|x| (x * 10000.0).round() / 10000.0)
        //     .collect();
        for (i, v) in res.iter().enumerate() {
            if v.is_nan() {
                assert!(expected_output1[i].is_nan());
            } else {
                assert_eq!((v * 10000.0).round() / 10000.0, expected_output1[i]);
            }
        }
        // assert_eq!(res_round, expected_output1);
    }
}
