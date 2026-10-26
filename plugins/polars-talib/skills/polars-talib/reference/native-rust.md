# Native Rust compatibility

The backend is the official `ta-lib = 0.8.3` crate. The public inventory, Python
signatures, defaults, input order, Struct fields, warmups and null masks stay at
the prior 201-function contract. Additional 0.8.3 indicators and MA types are a
separate API expansion.

Compatibility paths preserve RSI=0 on a constant prefix and after NaN poisoning,
STOCHRSI's legacy RSI dependency, extrema-index tie choices, selected window
recovery rules, PPO/PVO's former zero-window combine rule, and the previous
100000 period limits for PERCENTILE/PERCENTRANK/MAVP. EMA-derived functions use
legacy arithmetic for nonfinite, large-magnitude or long-period inputs; ADOSC
and CMOU retain legacy arithmetic throughout. The prefix before the first
trigger retains the normal arithmetic path so a later missing value cannot
change earlier results. The thresholds are empirical compatibility routing,
not a proof of equivalence for every Float64 input.

Finite floats may change in the last bits through arithmetic reordering; compare
at rtol/atol 1e-10 (use scale-sensitive absolute tolerance for tiny data). Keep
integer outputs, null masks and warmup positions exact. NaNs are values; nulls
mark missing observations and retain partition masking. Infinity is passed
through. Initial old/new infinity differences were found and fixed, and the
checked corpus includes both signs, leading/internal placement and MA types.
This coverage is not a general guarantee for arbitrary nonfinite inputs; explicitly
convert nonfinite values to null when they mean missing.

For performance, compare release wheels on identical data, versions and thread
counts with repeated measurements. `by_group` avoids per-group plugin calls,
but its exact key grouping and gather/scatter can cost more on some workloads.
