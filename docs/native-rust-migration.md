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
        selected batch-only 0.8.1 compatibility kernels
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
through the same compatibility layer. The common native route remains 0.8.3.
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

- Original release wheel: **4,624 tests passed**, unchanged baseline suite.
- Reviewed native release wheel: **5,717 Python tests passed**; **5 Rust unit tests passed**.
- On the same CPython 3.12 Mac wheel, the complete **5,717-test suite also passed
  separately on Polars 1.20.0 and 2.0.0**, in addition to benchmark runtime 1.44.2.
- Original-vs-native capture: **10,110 cases**, **2,041,958 checked values**, **0 failures**.
- All 201 functions are covered, including Float32/Float64, length and lookback
  boundaries, parameters and default sentinels, all existing MA modes, domain and
  tiny-scale inputs, constant/plateau/trend/high-offset/overflow inputs,
  nulls/NaNs/infinity, chunks, lazy queries, interleaved and ordered windows.
- Standard `.over()` tests compare exactly against independent partition-local
  expression evaluation for all functions, multiple/interleaved/null keys, derived
  keys, nested key dtypes, scalar inputs, integer/Struct outputs and concurrent
  lifecycle calls. The original API has no added grouping expression.
- Differential comparison observed **653 output fields with bit differences**;
  maximum finite absolute difference was **2.1543655748246238e-11**. Those are
  measured corpus results, not worst-case bounds.

The [machine-readable differential report](benchmarks/native-rust/differential.json)
records capture hashes and runtime versions. CI rebuilds the fixed original
commit, captures both installed wheels and uploads the complete NPZ data and
report. Reference data are not generated from the candidate implementation.

Reproduce on separate installed-wheel environments:

```sh
POLARS_MAX_THREADS=4 /path/to/old/python scripts/migration_probe.py --capture baseline.npz
POLARS_MAX_THREADS=4 /path/to/new/python scripts/migration_probe.py --capture candidate.npz
/path/to/new/python scripts/migration_probe.py --compare baseline.npz candidate.npz --report differential.json
```

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
is claimed for the final implementation. No upstream PR or message was sent.

## Release-build performance: CI is the comparison source

The [allocation follow-up](output-allocation.md) extends this methodology to
three builds (original, delivered zero-init, current NaN-init), one- and
four-thread runs, the missing 100 × 10,000-row layout, Polars controls and
process page-fault samples. The earlier two-build results belong to delivered
commit `e626bf4`; do not attribute them to the current follow-up head.


The `Release benchmark / rebuilt baseline on same runner` job rebuilds both
commit `b2bbc26d41ec80823c8bffb0cc436a97f29911cc` and the exact pull-request head,
sequentially on one Ubuntu runner with Rust 1.90.0, portable `--release --locked`
flags and the same compiler/Python runtime. It installs separate wheels with
Polars 1.44.2 and NumPy 2.5.3. Four Polars threads are configured for both and
processes inherit the same available CPU affinity (up to four CPUs). Compiler,
CPU, memory, runtime/dependency versions, commit IDs and source fingerprints are
uploaded alongside raw measurements. Neither timings nor wheels from another
runner or a published baseline are used.

`scripts/migration_ci_benchmark.py` constructs an original-output reference and
validates candidate outputs before timing, then runs six fresh process pairs in
alternating AB/BA order, each with five warmups and 51 samples per query. Each
measured process also checks output null/NaN positions exactly and numeric values
with `rtol=atol=1e-10`. Full lazy `collect()` is timed; data generation, validation
and reference compression are excluded. Workloads include direct EMA/RSI/MACD/ATR
and an eight-indicator query at 1,000/1,000,000 rows, standard `.over()` at
1,000 groups × 1,000 bars and 10,000 × 100, plus 2,000 × 100 interleaved groups.

The report preserves every sample and process median, p10/p90 distributions,
paired original/native ratios, and a conservative envelope spanning all process
medians. It labels overlapping/small differences as noisy instead of claiming a
speedup. This envelope is descriptive, not a confidence interval. Shared-runner
contention, frequency and core placement remain uncontrolled; one run cannot
establish a universal speedup. Correctness is enforced; performance is reported
without a fixed release threshold.

The former Mac tables and removed dispatcher experiments have been withdrawn from
the current tree. Local measurements informed the compatible vectorizable input
scan and output-padding work, which also apply inside ordinary `.over()`, but
headline performance conclusions will use the corrected final-head CI artifact.
Use the [draft PR evidence](https://github.com/Yvictor/polars_ta_extension/pull/45)
for the exact tested head, CI status, benchmark table and raw
`migration-benchmark` artifact. Performance conclusions require that completed
same-runner report, not historical local timing.

Reproduce after building both wheels in separate environments:

```sh
python scripts/migration_ci_benchmark.py \
  --baseline-python /path/to/old/python --baseline-source /path/to/original-checkout \
  --candidate-python /path/to/new/python --candidate-source /path/to/candidate-checkout \
  --output benchmark-results --pairs 6 --repeats 51 --threads 4
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
