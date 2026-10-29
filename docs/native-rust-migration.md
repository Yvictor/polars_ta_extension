# Native Rust migration

This branch replaces the bundled TA-Lib 0.8.1 C build with the official pinned
[`ta-lib = 0.8.3`](https://crates.io/crates/ta-lib/0.8.3) Rust crate. The comparison
target is repository commit `b2bbc26d41ec80823c8bffb0cc436a97f29911cc`, not C 0.8.3.
The public inventory remains 201 functions, with existing signatures, defaults,
namespace receiver order, Struct field names, dtypes, padding and null policies.
The extra upstream indicators and MA types are a separate API expansion.

## Architecture

```text
existing Python expressions
  generated fixed-ABI plugin symbols
    partition-local null masks
      safe native adapter
        immutable ta_lib::Core + per-call ParamHolder
        selected batch-only compatibility kernels and scoped SMA/HMA backports
```

Inputs borrow contiguous Float64 values where possible. Casts/rechunking and
null-to-NaN conversions own their buffers until the call finishes. Outputs are
initialized NaN allocations. Explicit warmup and unwritten-range NaN padding
is retained. The earlier delivered `e626bf4` used zeroed real allocations; the
[allocation follow-up](output-allocation.md) tests the allocator-sensitive change.
No uninitialized slice or raw C pointer reaches a kernel. Integer padding stays zero. All returned ranges are checked before exposing results.

The old `talib`/`talib-sys` subcrates, vendored C archive, CMake build and external
TA-Lib override path are removed. Rust/Python/linker tooling remains necessary;
allocator dependencies may still compile C. `initialize()` and `shutdown()` keep
their Python entrypoints but now use an immutable native Core with no global
lifecycle teardown. A concurrent shutdown cannot invalidate a call.

## Compatibility decisions

The [upstream changelog](https://github.com/TA-Lib/ta-lib/blob/v0.8.3/CHANGELOG.md)
is useful but insufficient as a differential specification. Testing and review
found additional changes beyond those release notes.

| Difference found | Compatibility handling |
| --- | --- |
| RSI constant prefix: 0 becomes 50; NaN poisoning also changes | Preserve original RSI batch arithmetic, including STOCHRSI's RSI dependency |
| MAXINDEX/MININDEX/MINMAXINDEX ties | Preserve original index-selection algorithm; integer values remain exact |
| CMOU/PERCENTILE recovery with NaNs | Preserve original batch behavior; CMOU always uses legacy arithmetic |
| PERCENTILE default 30 becomes 100; PERCENTILE/PERCENTRANK/MAVP maximum drops from 100000 to 10000 | Keep Python defaults and legacy default sentinels/ranges, including actual 100000-period tests |
| PPO/PVO zero-window fix after fractional values | Keep the original combine rule for windowed MA modes |
| EMA reordering changes high-offset oscillators and finite-overflow/nonfinite results | Route the affected EMA family through adapted legacy batch arithmetic for large magnitudes, nonfinite values or long periods |
| ADOSC cumulative state can grow large with small raw inputs | Always retain original ADOSC arithmetic |
| Future large/nonfinite observations could switch earlier rounding paths | Preserve normal native output before the first causal trigger; exact null-prefix tests remain enabled |
| Raw MA integer sentinel behavior differs between original wrappers and C | Preserve the original expression's success/error behavior, including the PVO/KDJ exceptions |

Compatibility kernels are batch-only adaptations of the official `v0.8.1` Rust
sources, retaining BSD attribution. Their composed EMA/MA dependencies resolve
through the same compatibility layer. The dependency remains pinned to0.8.3; explicit SMA-MAVP and HMA batch backports
are documented separately below. Other MA compositions retain the official crate.
The routing thresholds (`abs(input) > 1024`, period > 128) are conservative,
empirically tested choices, not a proof for every possible Float64 sequence.

NaN is an ordinary value; null is a missing observation with the existing
partition mask. Infinity is passed through as before. Initial infinity mismatches
were investigated and fixed, including leading negative infinity, both signs,
internal positions, and MA-mode combinations. There is **no infinity waiver**:
every mismatch in the final corpus fails the comparison. This finite corpus
still does not establish universal behavior for arbitrary extreme/nonfinite data.

Floating-point arithmetic reordering remains observable in last bits. Normal
comparisons use `rtol=1e-10, atol=1e-10`; tiny-data cases reduce absolute tolerance
to `min(1e-10, max(abs(finite_reference))*1e-10)`. Integer outputs, schemas,
null masks, group isolation and warmup alignment are checked exactly. We do not
claim bit equivalence or universal all-input equivalence.

## Correctness evidence

The [public usage inventory](public-api-validation.md) covers every one of the
201 exports and fails if an export is unaccounted for. It records applicable
column-name, expression, positional/keyword and namespace forms, eager/lazy and
ordinary `.over()` execution, defaults/nondefaults, Struct field order/dtypes,
missing/short/chunked inputs and invalid calls. Its matrix is systematic sampled
coverage, not every parameter combination or every possible input dtype.

The original unchanged release suite passed 4,624 tests. The expanded suite at
`8d14d0d` passed **11,425 tests in each of twelve CI Python/Polars combinations**
(Python 3.10/3.11/3.13/3.14; Polars 1.20/1.44/2.0). The full original-vs-native
corpus has **10,624 cases, 2,167,654 checked values and zero failures**, with maximum
observed finite absolute difference **2.5067947717616335e-11**. Exact native-vs-native
checks separately preserve signed zeros, schema, shape, padding and null/NaN
positions. See [CI40829706571](https://github.com/Yvictor/polars_ta_extension/actions/runs/40829706571)
for those correctness jobs; its broad timing job timed out, so the overall run
was not successful. Final-candidate results and artifact links belong in the
[draft PR evidence](https://github.com/Yvictor/polars_ta_extension/pull/45).

The corpus includes high-offset, finite-overflow, constant/plateau, tiny-scale,
nonfinite and MA-mode cases, long periods and partition-local reference checks.
NaN payloads and every possible Float64 sequence are not exhaustively proved.
The checked-in [earlier differential report](benchmarks/native-rust/differential.json)
is historical evidence for its recorded capture hashes and runtime, not the
expanded current corpus or a later head.

Reproduce using separate installed-wheel environments:

```sh
/path/to/old/python scripts/migration_probe.py --capture baseline.npz
/path/to/new/python scripts/migration_probe.py --capture candidate.npz
/path/to/new/python scripts/migration_probe.py --compare baseline.npz candidate.npz --report differential.json
```

## SMA MAVP backport

The explicit `matype=0` route uses the SMA-only algorithm from upstream
[`b3f0fa17d`](https://github.com/Yvictor/ta-lib-native/commit/b3f0fa17d0e3485c39ed042d86fff7116c0430a4),
`ta_codegen/input/mavp/mavp.c`, after existing parameter binding, lookback and
input guards succeed. It retains SMA's start anchor and add/subtract order,
copies period-one values, and stores only selected results. Single-period
inputs delegate to the released `Core::ma`. The private helper preserves Core's
parameter and buffer checks, including rejection of empty output buffers when
the input is shorter than lookback.

Existing guards continue to select legacy arithmetic for nonfinite inputs,
absolute values above 1024, or supplied period parameters above 128. Those
routes retain prefix restoration. The new normal SMA route reuses the guard's
proof and skips that second scan. `DEFAULT`, other MA types and extended period
ranges retain their previous routes. Padding, null masks and ordinary Polars
`.over(...)` remain in the shared adapter.

## Independent review

A separate reviewer found and reproduced high-offset/overflow/nonfinite and
MA-mode gaps, an ADOSC cumulative-state error, sentinel-validation differences,
duplicate derived-key names, an overbroad infinity waiver, and future-input
rounding causality. All findings were fixed and affected checks rerun. Final
focused review passed 14 tests plus exact prefix/order checks and found no
remaining actionable correctness, ownership, bounds or concurrency defect.
The reviewer explicitly did not certify universal numerical equivalence.

## Native Polars windows and transparent group batching

Users continue to write native expressions with ordinary `.over(...)`:

```python
bars.sort(["symbol", "timestamp"]).with_columns(
    ta.atr(timeperiod=14).over("symbol").alias("atr"),
    ta.macd().over(["symbol", "session"]).alias("macd"),
)
```

The earlier draft introduced a separate `by_group` expression; that was a scope
misunderstanding and has been removed along with its plugin symbols, dependencies,
recommendations and performance claims. It was not transparent `.over()` batching.
The current Python API and `.over()` registration semantics remain unchanged.

The plugin retains `is_elementwise=False`: indicators need complete ordered
partitions and cannot truthfully request the scalar elementwise fast path. The
adapter borrows the Arrow Float64 buffer it receives; that does **not** imply
host `.over()` grouping is zero-copy. The engine owns the group positions,
materialization, scheduling and result mapping before and after the callback.

A bounded list-composition prototype was investigated and removed. It batched
ordinary `.over()` on newer hosts but failed the supported Polars 1.20 planner,
and had unresolved scalar and overlapping-window scope. Arrow ListArray means
an offsets buffer plus a child array, not zero-copy by definition. The source
analysis, copy/allocation table, reproducible host probe and proposed native
group-position capability are in [ordinary `.over()` dispatch](over-dispatch.md).
No alternate expression or list wrapper ships, and no grouped-batching speedup
is claimed for the final implementation. No Polars upstream PR or message was sent for this dispatch investigation.

## Release-build performance: CI is the comparison source

The current CI job rebuilds three immutable sources on **one runner**:

| Build | Source |
| --- | --- |
| Original C0.8.1 | `b2bbc26d41ec80823c8bffb0cc436a97f29911cc` |
| Delivered native NaN-init | `c71cd6ecb4b48601ff409926fdb0a281505e9fec` |
| Candidate | Exact PR head recorded in every raw report |

All portable release wheels use Rust1.90, the same compiler/Python runtime,
Polars1.44.2 and NumPy2.5.3. Builds, corpus gates and setup diagnostics finish
before query timing. `adapter_ci_benchmark.py` uses all six build-order
permutations, six fresh processes per case/build/thread setting, five warmups and
51 samples per query. No sibling indicator runs before a selected case: filtering occurs before frame
construction, and that child validates only its selected query. This prevents
earlier functions from changing later cases through allocator history. Both
golden query references are retained. One- and four-thread settings run sequentially with the
same CPU affinity within each setting. There is no cross-runner comparison or
reuse of local timing as a CI result.

`migration_benchmark.py` covers twenty families plus the eight-function query:
dense1k/1m rows; ordinary `.over()` with100×10k,1000×1000,10k×100 and interleaved
2k×100 layouts. VAR/CORREL/CMOU are included to check the removed redundant scans.
The one-thread diagnostic adds EMA/ATR at50k×20,10×100k and1×1m plus Polars-only
cumsum controls. The20-row groups are shorter than default EMA warmup and cannot
be interpreted as a pure setup-cost estimate.

Every workload is checked against original output before timing; a separate
untimed reference checks candidate vs delivered native values and signed zeros
exactly. Original numerical tolerances are explicit. The full lazy `collect()`
is timed; construction, comparison, compression and fault-counter reads are
outside the latency timer. Raw samples, process medians, p10/p90, paired ratios,
source/wheel hashes, hardware/runtime, commands and all slower-case inventory
rows are artifacts. Process envelopes are descriptive, not confidence intervals
or multiple-comparison significance. Shared-host contention, placement and
frequency remain limits. `getrusage` faults include engine/Python/allocator work;
they do not by themselves identify allocator or kernel causality.

The first broad run at8d14d0d preserved a complete one-thread block, but timed out
after only two four-thread rounds. Its partial artifact is useful for identifying
MAVP, MINMAXINDEX, CDLDOJI, STDDEV and SUPERTREND regressions, not a complete
four-thread conclusion. The CI budget is now330minutes to retain the full scope
and repetitions, including fresh Python starts for every timed case. The [PR](https://github.com/Yvictor/polars_ta_extension/pull/45)
links the exact final head, terminal job status and complete artifact; do not
attribute earlier results to unmeasured source changes.

The [initialization report](output-allocation.md) describes the historical
zero-init→NaN-init comparison. Later allocation-map ablations did not establish
broad throughput gains and are not shipped. Single-chunk wrapper removal avoids
metadata work, and fixed-arity output fields avoid a descriptor allocation;
neither is a new borrowed Arrow-buffer path or a standalone speedup claim.

```sh
python scripts/adapter_ci_benchmark.py \
  --original-python /path/to/C/python --original-source /path/to/C-checkout \
  --prior-python /path/to/delivered/python --prior-source /path/to/delivered-checkout \
  --candidate-python /path/to/candidate/python --candidate-source /path/to/candidate-checkout \
  --output benchmark-results --rounds 6 --repeats 51 --thread-counts 1 4
```

## Build and remaining limits

```sh
maturin build --release --locked --out dist
python -m pip install dist/*.whl
```

The wheel and sdist were built locally; generators and Rust formatting were
checked. The final-head CI matrix validates other CPUs/OSes, Python versions and
Polars 1.20/1.44/2.x. Passing sampled coverage does not prove every parameter
combination, every finite value, or every future Polars ABI. No release, merge,
deployment or credential/security change is part of this draft.

## HMA weights-only backport

The explicit HMA expression uses a BSD-attributed copy of the pinned0.8.3 batch
method with multiplier-only weights kept as exactly representable floating-point
integers. Indices, rings, validations, arithmetic order and signatures stay the
same. Renamed internal helpers prevent this route from shadowing HMA calls inside
other MA compositions. All inputs use this exact-operation path, so it does not
need finite-prefix restoration.

[Upstream draft565](https://github.com/TA-Lib/ta-lib/pull/565) contains the canonical
change and [completed kernel CI](https://github.com/Yvictor/polars_ta_extension/actions/runs/40859198225).
The default-period1m kernel improves7.86% on that runner, with remaining C and
control caveats in the draft. Those Rust1.97 kernel results do not establish the
effect of this Rust1.90 Polars backport; the final three-build query CI measures
that separately. Local exact checks cover period2703/2704,100000, IEEE values,
output guards and ordinary native windows. The public API and missing-value
contract are unchanged.
