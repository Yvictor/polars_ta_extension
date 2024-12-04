mod cycle;
mod math;
pub mod momentum;
pub mod overlap;
pub mod pattern;
pub mod statistic;
pub mod transform;
pub mod utils;
pub mod volatility;
pub mod volume;
use talib::common::{ta_initialize, ta_shutdown, ta_version};
// use talib_sys::{TA_Initialize, TA_Shutdown, TA_RetCode};
pub use polars::prelude::*;

#[cfg(target_os = "linux")]
use jemallocator::Jemalloc;

#[global_allocator]
#[cfg(target_os = "linux")]
static ALLOC: Jemalloc = Jemalloc;

// #[pyfunction]
// fn initialize() -> PyResult<()> {
//     match ta_initialize() {
//         Ok(_) => Ok(()),
//         Err(e) => Err(PyRuntimeError::new_err(format!(
//             "Failed to initialize TA-Lib: {:?}",
//             e
//         ))),
//     }
// }
