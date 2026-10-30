# Output initialization follow-ups

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

## Integer output initialization: measured follow-up

Integer output buffers now use `Vec::with_capacity(len)` followed by `resize(len, 0)`.
Every element remains initialized, including empty and unwritten ranges. Real buffers
retain the same NaN initialization. The patch changes buffer construction and adds direct
integer/mixed-output tests; arithmetic, output layout, compatibility guards and ordinary
Polars `.over()` stay unchanged.

The [completed
experiment](https://github.com/Yvictor/polars_ta_extension/actions/runs/40881740228) used
these immutable sources:

| Build | Source |
| --- | --- |
| Original C 0.8.1 | `b2bbc26d41ec80823c8bffb0cc436a97f29911cc` |
| Native control | `78c3a1be1d3eeba24970ee20f66a33c10c74c327` |
| Integer candidate | `6c3fb5fb44496c5739ee9f1d8dfa11f7b46dd473` |

These measurements cover the `78c3a1b`/`6c3fb5f` experiment. The integration onto
`6d056da0f7e22744eeb78b2a68d158209fd33d80` has separate correctness gates; its final-head
performance remains to be measured.

All three portable release wheels were built on one AMD EPYC 7763 runner (four logical
CPUs), Linux 7/glibc 2.39, Rust 1.90.0, Python 3.12.15, Polars 1.44.2 and NumPy 2.5.3.
Actual product compile paths, wheel/native hashes, Cargo dependency graphs and
uninstrumented native binaries were retained before extra C/unit/stage builds could
overwrite cache metadata.

The 13 selected queries ran at one and four controlled threads. Each case/build/thread
setting used 12 fresh processes: all six build orders repeated twice, 31 samples after
five warmups. Selection happens before frame/expression construction; a timed process runs
one case. The full 10,624-case/2,167,654-value API corpus and both thread-setting query
goldens passed before any timing. Each setting checked 16,400,000 query output slots,
including 13,400,000 integer slots exactly. Native control/candidate comparisons use exact
values, signed zeros, schemas, null masks and NaN positions. C integer fields are exact; C
real fields retain the declared migration tolerance. The selected untimed collection is
checked before warmups; timed collections are not numerically rechecked inside their
latency interval.

Both independent audits passed: 936 fresh query processes/29,016 samples, and 1,728 stage
processes/12,096 samples with 12 exact C/kernel/adapter validation runs. The [raw artifact
12905591130](https://github.com/Yvictor/polars_ta_extension/actions/runs/40881740228/artifacts/12905591130)
has verified ZIP SHA-256
`8e44bce67836472390484b7b9ac7af6998303aa38fd8c60936bf3ab97001787b`.

### Full query results

Times below are medians of 12 process medians, in milliseconds. Negative change means
lower candidate latency. Envelopes span min(control medians)/max(candidate medians) to
max(control)/min(candidate); they are descriptive process ranges, not confidence
intervals. Inner samples are correlated and shared-host placement/frequency remain
uncontrolled.

| Threads | Query | C ms | Native control ms | Candidate ms | Change vs control | Faster pairs | Control/candidate envelope |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | --- |
| 1 | cdldoji/1000000 | 2.5376 | 4.2030 | 2.1509 | -48.824% | 12/12 | 1.8642–2.0198 |
| 1 | grouped_cdldoji/100x10000 | 14.9134 | 17.3088 | 14.6165 | -15.555% | 12/12 | 1.1476–1.2325 |
| 1 | grouped_cdldoji/10000x100 | 106.8622 | 102.8953 | 103.2586 | +0.353% | 4/12 | 0.9599–1.0201 |
| 1 | minmaxindex/1000000 | 9.3766 | 12.4776 | 9.9576 | -20.196% | 12/12 | 1.2118–1.3004 |
| 1 | grouped_minmaxindex/100x10000 | 20.9274 | 26.6316 | 21.5824 | -18.959% | 12/12 | 1.1680–1.2942 |
| 1 | grouped_minmaxindex/10000x100 | 147.8853 | 150.5363 | 149.4152 | -0.745% | 11/12 | 0.9726–1.0396 |
| 1 | grouped_minmaxindex/2000x100_interleaved | 27.1600 | 27.5528 | 26.9672 | -2.125% | 10/12 | 0.9669–1.0664 |
| 1 | ht_trendmode/1000000 | 572.7796 | 574.8441 | 571.1112 | -0.649% | 12/12 | 1.0047–1.0095 |
| 1 | cdlengulfing/1000000 | 1.3347 | 3.3260 | 1.4993 | -54.923% | 12/12 | 2.0548–2.2862 |
| 1 | grouped_cdlengulfing/100x10000 | 13.6052 | 16.3776 | 13.7708 | -15.917% | 12/12 | 1.1342–1.2330 |
| 1 | grouped_add/10000x100 | 78.6070 | 76.7605 | 77.0311 | +0.353% | 3/12 | 0.9667–1.0205 |
| 1 | control_cumsum/100x10000 | 14.4120 | 14.3913 | 14.3868 | -0.031% | 6/12 | 0.9545–1.0567 |
| 1 | supertrend/1000000 | 8.1516 | 9.2672 | 7.2840 | -21.400% | 12/12 | 1.2102–1.3064 |
| 4 | cdldoji/1000000 | 2.6651 | 4.2292 | 2.2401 | -47.032% | 12/12 | 1.8294–1.9564 |
| 4 | grouped_cdldoji/100x10000 | 14.8121 | 17.3554 | 14.1658 | -18.378% | 12/12 | 1.1470–1.3392 |
| 4 | grouped_cdldoji/10000x100 | 112.8137 | 109.3356 | 107.3992 | -1.771% | 10/12 | 0.9428–1.0721 |
| 4 | minmaxindex/1000000 | 9.3415 | 12.4817 | 9.9508 | -20.277% | 12/12 | 1.1999–1.2890 |
| 4 | grouped_minmaxindex/100x10000 | 13.9829 | 16.6235 | 14.3116 | -13.908% | 12/12 | 1.0649–1.2910 |
| 4 | grouped_minmaxindex/10000x100 | 86.0738 | 87.3821 | 88.4338 | +1.204% | 3/12 | 0.9542–1.0412 |
| 4 | grouped_minmaxindex/2000x100_interleaved | 15.0671 | 15.2118 | 15.4257 | +1.406% | 2/12 | 0.9463–1.0531 |
| 4 | ht_trendmode/1000000 | 572.9607 | 575.0271 | 571.4274 | -0.626% | 11/12 | 0.9920–1.0109 |
| 4 | cdlengulfing/1000000 | 1.4446 | 3.4431 | 1.6058 | -53.361% | 12/12 | 1.9752–2.3091 |
| 4 | grouped_cdlengulfing/100x10000 | 13.5596 | 16.7051 | 13.5689 | -18.774% | 12/12 | 1.1708–1.2835 |
| 4 | grouped_add/10000x100 | 83.8081 | 80.9272 | 80.0183 | -1.123% | 7/12 | 0.9436–1.1200 |
| 4 | control_cumsum/100x10000 | 11.1716 | 11.1475 | 11.2293 | +0.734% | 6/12 | 0.9591–1.0440 |
| 4 | supertrend/1000000 | 8.1421 | 9.2495 | 7.2862 | -21.226% | 12/12 | 1.2207–1.3179 |

Dense Doji, CDLENGULFING, MINMAXINDEX and mixed-output SUPERTREND improve in all 12 pairs
at both thread settings, with disjoint process ranges. The 100 × 10,000 group cases also
improve. Candidate dense Doji and SUPERTREND are faster than C on this runner. The dense
CDLENGULFING C gap remains 12.331%/11.164% (one/four threads), with all 12 candidate pairs
slower and disjoint ranges. Dense MINMAXINDEX retains a 6.197% C-relative median gap at
one thread (overlapping full ranges) and 6.522% at four threads (all 12 slower, disjoint
ranges). Other remaining C-relative slower medians remain in the linked data.

### Negative cases and controls

The candidate/control comparison has five slower medians. Every full process envelope
below overlaps 1. They remain recorded alongside the larger gains.

| Threads | Query | Candidate latency increase | Faster pairs | Control/candidate envelope |
| ---: | --- | ---: | ---: | --- |
| 1 | grouped_cdldoji/10000x100 | +0.353% | 4/12 | 0.9599–1.0201 |
| 1 | grouped_add/10000x100 | +0.353% | 3/12 | 0.9667–1.0205 |
| 4 | grouped_minmaxindex/10000x100 | +1.204% | 3/12 | 0.9542–1.0412 |
| 4 | grouped_minmaxindex/2000x100_interleaved | +1.406% | 2/12 | 0.9463–1.0531 |
| 4 | control_cumsum/100x10000 | +0.734% | 6/12 | 0.9591–1.0440 |

The ADD/cumsum controls span −1.123% to +0.734% candidate/control median changes; their
process ranges overlap. These observations do not establish a universal noise bound. The
[complete 26-scenario CSV](benchmarks/integer-output-init-40881740228.csv) includes every
C-relative gap, paired count and envelope. The [all-pairwise negative
CSV](benchmarks/integer-output-init-40881740228-negative.csv) retains all 37 slower
medians across C/control/candidate comparisons, including 12 candidate-versus-C rows (one
is the cumsum engine control). No aggregate hides a slower case.

### Allocation route and diagnostic limits

The actual Linux product ELFs, separately matched to their wheel bytes, show the integer
branches moving from Jemalloc ZERO 0x40/`calloc` routes to unflagged allocation plus an
explicit zero fill. Four constructor variants retain the real NaN fill; all ten former
integer ZERO-flag sites disappear. The compiler did not fold the candidate back into
calloc. The old/new native SHA-256 values are
`e8f05e3908d6084fc9756f349e2cb1ece6d6e249d572f2f947e78f5bf70775ba` and
`379beba7555a505cb28799b70ece92b0046527a2cdfe90391218b432f0b9bf99`.

Warmed allocation/reallocation request counts and requested bytes stay equal: full Doji
has 6 requests and full MMI has 36. Zeroed requests change 1 → 0 and 2 → 0 respectively.
Those counters exclude C malloc, deallocations, live/net memory and RSS.

Predecoded full Doji at 1m changes 4.002 → 1.942 ms; full MMI at 10k changes 114.090 →
72.097 µs. Full MMI at 1m is +0.291% with overlapping ranges despite the complete-query
improvement above. Unchanged stage controls also move: C Doji FFI 1m is +2.226% (all 12
slower, disjoint), while Rust Doji kernel 1k is −19.338% (all 12 faster, disjoint). Stage
subtraction, normalization by those shifts, and extrapolation from standalone one-output
controls are unsupported. The two-output eager MMI materialization control is about 3.64
ms and has a different lifetime/heap context.

Whole-child minor-fault medians for full Doji 1m change 44,281 → 20,820; full MMI 1m
remains about 62,869. They include process startup, fixtures, warmups, all timed batches
and the counted call. They are cumulative child observations, not per-call or
allocator-only attribution. Stage full omits Python/plugin decoding, window scheduling and
result mapping; its allocation-counter wrapper can alter code generation. The
uninstrumented product ELF establishes the actual allocation route separately. One shared
runner does not establish behavior across hardware or unmeasured integer families.
