mod compat;
mod generated;
mod missing;
mod native;
mod utils;
use pyo3::{pyfunction, pymodule, types::PyModule, wrap_pyfunction, PyResult, Python};

#[cfg(target_os = "linux")]
use jemallocator::Jemalloc;
#[global_allocator]
#[cfg(target_os = "linux")]
static ALLOC: Jemalloc = Jemalloc;

// Kept for Python API compatibility. Native Core settings are immutable and
// require no process-global lifecycle; shutdown cannot invalidate active calls.
#[pyfunction]
fn initialize() {
    let _ = native::core();
}
#[pyfunction]
fn shutdown() {}
#[pyfunction]
fn version() -> &'static str {
    "0.8.3 (native Rust; polars-talib compatibility)"
}

#[pymodule]
#[pyo3(name = "_polars_talib")]
fn polars_ta(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(initialize, m)?)?;
    m.add_function(wrap_pyfunction!(shutdown, m)?)?;
    m.add_function(wrap_pyfunction!(version, m)?)?;
    m.add_function(wrap_pyfunction!(missing::lookback, m)?)?;
    Ok(())
}

#[cfg(test)]
mod cost_probe;
