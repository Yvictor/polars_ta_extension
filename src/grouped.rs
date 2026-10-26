//! One plugin call for the whole column, reusing the plugin's Polars thread pool.
use crate::{
    missing::Masked,
    native::{compute, Params},
    utils::broadcast_inputs,
};
use polars::prelude::*;
use rayon::prelude::*;
use ta_lib::abstract_api::FuncId;

pub fn compute_grouped(
    id: FuncId,
    inputs: &[Series],
    kwargs: Masked<Params>,
    order: &[usize],
    names: &[&str],
) -> PolarsResult<Series> {
    polars_ensure!(inputs.len()==order.len()+1, ShapeMismatch: "grouped indicator input count differs");
    let aligned = broadcast_inputs(inputs)?;
    let (keys, inputs) = aligned.split_last().unwrap();
    let len = keys.len();
    polars_ensure!(len <= IdxSize::MAX as usize, ComputeError: "grouped input exceeds Polars index capacity");
    let keys = keys.u32()?;
    polars_ensure!(keys.null_count()==0, ComputeError: "group ids must be non-null");
    let max = keys.max().unwrap_or(0) as usize;
    polars_ensure!(max<=len, ComputeError: "group ids must be dense and bounded by row count");
    let mut groups = vec![Vec::<IdxSize>::new(); max + 1];
    for (row, key) in keys.into_no_null_iter().enumerate() {
        groups[key as usize].push(row as IdxSize);
    }
    groups.retain(|rows| !rows.is_empty());
    if groups.is_empty() {
        return compute(id, inputs, &kwargs.params, order, names);
    }
    let results = polars_core::POOL.install(|| {
        groups
            .par_iter()
            .map(|rows| {
                let start = rows[0] as usize;
                let contiguous = rows.last().copied().unwrap() as usize - start + 1 == rows.len();
                let local = if contiguous {
                    inputs
                        .iter()
                        .map(|s| s.slice(start as i64, rows.len()))
                        .collect::<Vec<_>>()
                } else {
                    let indices = IdxCa::from_vec("", rows.to_vec());
                    inputs
                        .iter()
                        .map(|s| s.take(&indices))
                        .collect::<PolarsResult<Vec<_>>>()?
                };
                Masked {
                    params: &kwargs.params,
                    lookback: kwargs.lookback,
                    recursive: kwargs.recursive,
                }
                .apply(&local, |params| compute(id, &local, params, order, names))
            })
            .collect::<PolarsResult<Vec<_>>>()
    })?;
    let mut next = 0;
    let in_order = groups.iter().all(|rows| {
        let contiguous = rows[0] as usize == next
            && rows.last().copied().unwrap() as usize == next + rows.len() - 1;
        next += rows.len();
        contiguous
    });
    let mut results = results.into_iter();
    let mut output = results.next().unwrap();
    for result in results {
        output.append(&result)?;
    }
    if in_order {
        return Ok(output.rechunk());
    }
    let mut inverse = vec![0 as IdxSize; len];
    let mut position = 0;
    for rows in &groups {
        for &row in rows.iter() {
            inverse[row as usize] = position;
            position += 1;
        }
    }
    output.rechunk().take(&IdxCa::from_vec("", inverse))
}
