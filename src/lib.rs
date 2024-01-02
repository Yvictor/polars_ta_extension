
mod overlap;
mod volatility;
mod cycle;
mod momentum;
mod pattern;
mod utils;
mod volume;
use pyo3::{pymodule, types::PyModule, PyResult, Python};

#[cfg(target_os = "linux")]
use jemallocator::Jemalloc;

#[global_allocator]
#[cfg(target_os = "linux")]
static ALLOC: Jemalloc = Jemalloc;

// /// Formats the sum of two numbers as string.
// #[pyfunction]
// fn sum_as_string(a: usize, b: usize) -> PyResult<String> {
//     Ok((a + b).to_string())
// }

/// A Python module implemented in Rust.
#[pymodule]
#[pyo3(name = "_polars_ta")]
fn polars_ta(_py: Python, _m: &PyModule) -> PyResult<()> {
    // m.add_function(wrap_pyfunction!(sum_as_string, m)?)?;
    Ok(())
}
