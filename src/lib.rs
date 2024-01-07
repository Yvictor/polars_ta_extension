mod cycle;
mod math;
mod momentum;
mod overlap;
mod pattern;
mod statistic;
mod transform;
mod utils;
mod volatility;
mod volume;
use pyo3::exceptions::PyRuntimeError;
use pyo3::{pyfunction, pymodule, types::PyModule, wrap_pyfunction, PyResult, Python};
use talib::common::{ta_initialize, ta_shutdown, ta_version};
// use talib_sys::{TA_Initialize, TA_Shutdown, TA_RetCode};

#[cfg(target_os = "linux")]
use jemallocator::Jemalloc;

#[global_allocator]
#[cfg(target_os = "linux")]
static ALLOC: Jemalloc = Jemalloc;

#[pyfunction]
fn initialize() -> PyResult<()> {
    match ta_initialize() {
        Ok(_) => Ok(()),
        Err(e) => Err(PyRuntimeError::new_err(format!(
            "Failed to initialize TA-Lib: {:?}",
            e
        ))),
    }
}

#[pyfunction]
fn shutdown() -> PyResult<()> {
    match ta_shutdown() {
        Ok(_) => Ok(()),
        Err(e) => {
            println!("Failed to shutdown TA-Lib: {:?}", e);
            Err(PyRuntimeError::new_err(format!(
                "Failed to initialize TA-Lib: {:?}",
                e
            )))
        }
    }
}

#[pyfunction]
fn version() -> PyResult<String> {
    Ok(ta_version())
}

/// A Python module implemented in Rust.
#[pymodule]
#[pyo3(name = "_polars_ta")]
fn polars_ta(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(initialize, m)?)?;
    m.add_function(wrap_pyfunction!(shutdown, m)?)?;
    m.add_function(wrap_pyfunction!(version, m)?)?;
    Ok(())
}
