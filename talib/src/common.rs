use std::ffi::CStr;
use serde::Deserialize;
use talib_sys::{
    // TA_GetCompatibility,
    // TA_GetUnstablePeriod,
    TA_Initialize,
    TA_RetCode,
    // TA_SetCompatibility,
    // TA_SetUnstablePeriod,
    TA_GetVersionString,
    TA_Shutdown, //TA_SetCandleSettings, TA_ResetCandleSettings,
};

pub fn ta_initialize() -> Result<(), TA_RetCode> {
    let ret_code = unsafe { TA_Initialize() };
    match ret_code {
        TA_RetCode::TA_SUCCESS => Ok(()),
        _ => Err(ret_code),
    }
}

pub fn ta_shutdown() -> Result<(), TA_RetCode> {
    let ret_code = unsafe { TA_Shutdown() };
    match ret_code {
        TA_RetCode::TA_SUCCESS => Ok(()),
        _ => Err(ret_code),
    }
}

pub fn ta_version() -> String {
    let version = unsafe { TA_GetVersionString() };
    let version = unsafe { CStr::from_ptr(version) };
    version.to_string_lossy().into_owned()
}


#[derive(Deserialize)]
pub struct TimePeriodKwargs {
    pub timeperiod: i32,
}