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

by_group(function, ..., by=keys)
  host Polars: exact composite-key dense IDs
  one plugin invocation
    plugin-local Polars thread pool: slices or gathers per group
      same masks and adapter
    concatenate; scatter only when source order requires it
```

Inputs borrow contiguous Float64 values where possible. Casts/rechunking and
null-to-NaN conversions own their buffers until the call finishes. Outputs are
initialized zeroed allocations; only warmup and unwritten rows are filled with
NaN. No uninitialized slice or raw C pointer reaches a kernel. Integer padding
stays zero. All returned ranges are checked before exposing results.

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
- Reviewed native release wheel: **5,714 Python tests passed**; **5 Rust unit tests passed**.
- On the same CPython 3.12 Mac wheel, the complete **5,714-test suite also passed
  separately on Polars 1.20.0 and 2.0.0**, in addition to benchmark runtime 1.44.2.
- Original-vs-native capture: **10,110 cases**, **2,041,958 checked values**, **0 failures**.
- All 201 functions are covered, including Float32/Float64, length and lookback
  boundaries, parameters and default sentinels, all existing MA modes, domain and
  tiny-scale inputs, constant/plateau/trend/high-offset/overflow inputs,
  nulls/NaNs/infinity, chunks, lazy queries, interleaved and ordered windows.
- New dispatcher tests compare exactly with `.over()` for all functions,
  multiple/interleaved/null keys, derived keys, nested key dtypes, scalar inputs,
  integer/Struct outputs and concurrent lifecycle calls.
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

## Group dispatcher recommendation

```python
import polars as pl
import polars_talib as ta

bars.sort(["symbol", "timestamp"]).with_columns(
    ta.by_group("atr", by="symbol", timeperiod=14).alias("atr"),
    ta.by_group("macd", by=["symbol", "session"]).alias("macd"),
)
```

`by_group` accepts the same positional/named indicator inputs and defaults as the
existing top-level function. It retains input order within each group. It does
not infer time ordering or session boundaries, and it does not replace Polars'
`Expr.over` implementation. Aliases make keys derived from the same column safe.

Key encoding deliberately stays in the host runtime. Sending raw new Polars
String/categorical/Array/small-integer layouts across this frozen plugin ABI
produced errors and an Array import abort during review. That experiment was
removed. Integer IDs preserve exact key equality without hash-collision shortcuts.
The plugin has its **own** statically linked Polars 0.36 thread pool, configured
by `POLARS_MAX_THREADS`; it is not the host Polars 1.x/2.x pool. Concurrent host
expressions and plugin work are not promised a single coordinated thread budget.

Upstream's [proposed dispatcher](https://github.com/TA-Lib/ta-lib/issues/414#issuecomment-6403888773)
is not shipped in 0.8.3. A TA-Lib-only dispatcher cannot remove Polars' per-group
plugin calls when the user still writes `.over()`. This in-repo whole-column path
moves that boundary explicitly. Keep it optional, benchmark the real group sizes,
and use ordinary `.over()` when key encoding/gather costs outweigh dispatch savings.
No upstream PR or maintainer message was sent.

## Release-build performance

Measurements use Apple M6 Mac Mini, 12 logical CPUs, 32 GiB RAM, macOS 27.0.1
arm64, CPython 3.12.14, Polars 1.44.2, NumPy 2.5.3 and Rust 1.90.0. The original
C baseline used Apple clang 21.0.0. Both wheels used portable release builds,
not native-CPU or fast-math flags; four threads were configured in both runtimes.
macOS CPU affinity was not pinned. No thermal/performance warning was recorded.

Final runs are separate processes ordered A1,B1,B2,A2,A3,B3, with 5 warmups and
31 timed samples per query in each process. Tables report the median of the three
per-process medians. No builds/corpus tests ran alongside measurements. Raw JSONs
retain every sample, load averages, runtime metadata and source fingerprints.
All timed outputs, including dispatcher results, are compared to the original
wheel's outputs before timing. Data generation, correctness checks and reference
compression are outside timing; the measured operation is complete lazy `collect()`.

The `initial/` measurements are an explicitly historical prototype comparison.
They preceded independent-review fixes and final tuning, and are not final-head
performance evidence. Ranking cost made the original dispatcher slower for some
longer groups. The safe tuning skips inverse scatter when grouped output already
matches source order. A diagnostic release scan benchmark (1M finite values, 101 calls) measured the
short-circuit predicate at 0.485 ms and a logically equivalent boolean reduction
at 0.198 ms. That prompted the reviewed vectorizable scan; an explicit empty/
NaN/infinity/threshold/random-bit property test checks equivalence. The
`pre-scan-tuning/` six runs retain the complete earlier query measurements.
Final measurements below include contiguous and interleaved
groups and all compatibility fixes; improvements are workload-specific.

| Query / rows or groups × bars | Original ms | Native `.over()` / direct ms | Old / native | Native `by_group` ms | Old / dispatcher |
| --- | ---: | ---: | ---: | ---: | ---: |
| ema/1000 | 0.0110 | 0.0114 | 0.96x | — | — |
| rsi/1000 | 0.0117 | 0.0119 | 0.98x | — | — |
| macd/1000 | 0.0152 | 0.0155 | 0.98x | — | — |
| atr/1000 | 0.0312 | 0.0273 | 1.14x | — | — |
| mix8/1000 | 0.0790 | 0.0798 | 0.99x | — | — |
| ema/1000000 | 1.1657 | 0.9861 | 1.18x | — | — |
| rsi/1000000 | 1.8754 | 1.8978 | 0.99x | — | — |
| macd/1000000 | 1.7969 | 1.6292 | 1.10x | — | — |
| atr/1000000 | 0.8424 | 0.8801 | 0.96x | — | — |
| mix8/1000000 | 7.6943 | 8.0327 | 0.96x | — | — |
| grouped_ema/1000x1000 | 4.9662 | 5.2379 | 0.95x | 9.3308 | 0.53x |
| grouped_atr/1000x1000 | 8.5399 | 9.0720 | 0.94x | 9.1635 | 0.93x |
| grouped_mix8/1000x1000 | 30.2307 | 31.2607 | 0.97x | 23.5448 | 1.28x |
| grouped_ema/10000x100 | 21.0140 | 20.6614 | 1.02x | 12.3106 | 1.71x |
| grouped_atr/10000x100 | 37.6504 | 39.2568 | 0.96x | 13.1017 | 2.87x |
| grouped_mix8/10000x100 | 158.7332 | 154.0135 | 1.03x | 51.4759 | 3.08x |
| grouped_ema/2000x100_interleaved | 3.5371 | 3.3381 | 1.06x | 5.5268 | 0.64x |
| grouped_atr/2000x100_interleaved | 6.8271 | 7.3856 | 0.92x | 5.7445 | 1.19x |
| grouped_mix8/2000x100_interleaved | 31.6015 | 28.5810 | 1.11x | 13.7514 | 2.30x |

Reproduce final raw runs with `scripts/migration_benchmark.py` in the same two
wheel environments, keeping `POLARS_MAX_THREADS` and dependencies identical:

```sh
POLARS_MAX_THREADS=4 /path/to/old/python scripts/migration_benchmark.py --label baseline-1 --source-root /path/to/baseline-checkout --repeats 31 --output baseline-1.json --write-reference benchmark-reference.npz
POLARS_MAX_THREADS=4 /path/to/new/python scripts/migration_benchmark.py --label candidate-1 --source-root /path/to/candidate-checkout --repeats 31 --output candidate-1.json --reference benchmark-reference.npz
```

Repeat in the alternating order above. The checked-in raw samples are specific
to this Mac. The existing CI benchmark is informational and compares the published
0.2.1 wheel on a shared Linux runner; the fixed-commit differential CI job is the
migration correctness gate. Cross-platform numerical and timing results depend
on compiler/math-library behavior and must be judged from final-head CI.

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
