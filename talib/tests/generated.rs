use talib::common::ta_initialize;
use talib::generated::{ta_hma, ta_supertrend, HmaKwargs, SupertrendKwargs};
use talib_sys::TA_RetCode;

#[test]
fn slice_wrappers_validate_before_ffi_and_preserve_padding() {
    ta_initialize().unwrap();
    let hma = HmaKwargs { timeperiod: 20 };
    assert!(ta_hma(&[], &hma).unwrap().is_empty());
    assert!(ta_hma(&[1., 2.], &hma).unwrap().iter().all(|v| v.is_nan()));
    assert!(ta_hma(&[f64::NAN; 30], &hma).unwrap().iter().all(|v| v.is_nan()));
    assert_eq!(ta_hma(&[1., 2.], &HmaKwargs { timeperiod: -1 }), Err(TA_RetCode::TA_BAD_PARAM));
    let st = SupertrendKwargs { timeperiod: 10, multiplier: 3. };
    assert_eq!(ta_supertrend(&[2.; 20], &[1.], &[1.5; 20], &st), Err(TA_RetCode::TA_BAD_PARAM));
    let (price, direction) = ta_supertrend(&[2.; 20], &[1.; 20], &[1.5; 20], &st).unwrap();
    assert_eq!(price.len(), 20);
    assert_eq!(direction.len(), 20);
    assert!(price[..10].iter().all(|v| v.is_nan()));
    assert!(direction[..10].iter().all(|v| *v == 0));
    assert!(price[10..].iter().all(|v| v.is_finite()));
    assert!(direction[10..].iter().all(|v| v.abs() == 1));
}
