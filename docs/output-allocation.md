# Real-output initialization follow-up

The real-output allocation now uses `vec![f64::NAN; len]` instead of the zeroed
allocation delivered in `e626bf485a0b4957c034fd85dc0520b6c3b76a01`. Both are fully
initialized safe buffers. Integer outputs still start at zero. Explicit prefix
and suffix NaN padding, output-range checks, null masks and compatibility routing
are unchanged. Kernels write their reported range; caller zeros are not recurrence
seeds, including the composed MA and MAVP output-readback paths.

This follows [mario4tier's two-host report](https://github.com/Yvictor/polars_ta_extension/pull/45#issuecomment-6454841789).
He distinguished a Linux allocation/page-fault effect near 10,000 rows per group
from additional per-call overhead in short groups. His Intel and Apple dense
results also differ from the earlier CI host. These are useful external
measurements, not results independently reproduced by this repository merely by
quoting them. NaN initialization can change allocator behavior without changing
computed values; whether it improves a given workload is measured below.

## Correctness gates

The same expanded corpus is run in separate installed-wheel processes for all
three builds. It includes 10,624 cases, all 201 expressions, nulls/NaNs/infinity,
empty/all-missing inputs, warmup boundaries, integer/Struct outputs, grouped and
ordered windows, guarded legacy/native-prefix cases, and extra constant/varying
MAVP periods across all existing MA modes and long/high-offset paths.

- Original C versus candidate retains the documented migration tolerance.
- Delivered zero-init versus candidate uses **exact numeric and signed-zero
  equality**, exact null/schema/shape/error checks and NaN equality. No floating
  tolerance hides an output change caused by initialization.
- Every timed workload is checked against the original before timing; a separate
  untimed zero-init reference also checks candidate values exactly. This does
  not mean every timed collection is numerically rechecked inside its timer.

The exact comparison establishes evidence for the tested inputs, not a universal
proof about all Float64 sequences or third-party kernels.

## Same-runner three-build experiment

CI checks out these immutable sources:

| Build | Commit |
| --- | --- |
| Original C | `b2bbc26d41ec80823c8bffb0cc436a97f29911cc` |
| Delivered native zero-init | `e626bf485a0b4957c034fd85dc0520b6c3b76a01` |
| Native NaN-init | Exact PR head, recorded in every raw process report |

All three portable release wheels are built sequentially in one Ubuntu job using
Rust 1.90.0, the same compiler/Python/runtime and dependency pins. No local timing,
published baseline wheel or other runner's build is substituted. The job retains
build logs, wheel hashes, dependencies, CPU/memory/toolchain metadata and source
fingerprints.

The job runs one-thread and controlled four-thread measurements sequentially on
that runner. Each setting uses six fresh processes per build, one round for each
of the six build-order permutations, five warmups and 51 samples per query.
Each build occupies every position twice. The same available CPU set is used
for all builds at a given thread setting; it is restored between settings.

Workloads retain dense EMA/RSI/MACD/ATR and the eight-indicator query, contiguous
1,000 × 1,000 and 10,000 × 100 groups, and 2,000 × 100 interleaved groups. They add
100 × 10,000 groups for EMA/ATR/the mix, and matching Polars-only
`cum_sum().over()` controls. The one-thread diagnostic also sweeps 20, 100,
1,000, 10,000, 100,000 and 1,000,000 bars at a fixed million rows, using EMA/ATR
and controls. Default EMA warmup exceeds 20 bars: these workload differences
must not be presented as a direct measurement of pure plugin setup cost.

Full lazy `collect()` is timed. Construction, correctness checks, compression and
counter reads are outside the latency timer. `getrusage(RUSAGE_SELF)` records
minor/major faults between reads around each query. Those are process-level
counters, including engine/Python/allocator activity; they do **not** isolate
jemalloc, prove kernel attribution, or measure instructions per group. Major
faults, minor faults, process medians and p10/p90 spreads remain in raw data.

The report compares original/zero, zero/NaN and original/NaN, using matched-round
median ratios and the conservative process-median envelope. The envelope is a
descriptive range, not a confidence interval; correlated samples, shared-host
contention and frequency/placement remain limits. The final PR evidence links
its exact head, completed CI job and full raw artifact. Dense gains and page-fault
improvements must not be generalized across machines from one runner.

## Remaining short-group cost

This change does not remove the per-call parameter decode/binding and temporary
collections in the native adapter, or Polars' grouping, Arrow export and result
mapping. Any remaining short-group regression is reported even if the allocation
case improves. Fewer per-call collections or parameter specialization are future
profiling candidates, not improvements established by this one-line change.
Ordinary `.over()` stays unchanged; no new grouping expression, list composition,
private ABI access or upstream communication is part of this follow-up.

Reproduce after building and installing the three wheels in separate environments:

```sh
python scripts/allocation_ci_benchmark.py \
  --original-python /path/to/original/python --original-source /path/to/original \
  --zero-python /path/to/zero/python --zero-source /path/to/zero \
  --candidate-python /path/to/candidate/python --candidate-source /path/to/candidate \
  --output benchmark-results --rounds 6 --repeats 51 --thread-counts 1 4
```

For a bounded local harness smoke test only, add `--case-filter ema/1000
--repeats 5`. CI leaves the filter unset and runs the full inventory. Local smoke
results do not establish performance conclusions.
