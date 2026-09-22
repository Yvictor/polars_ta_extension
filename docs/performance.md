# Performance measurements

The measured release wheel improves the main long-series indicators while keeping
native Polars execution. These are measurements on one Linux x86_64 machine, not
a claim of a globally optimal implementation or identical speedups on every CPU.

## Reproduce

Run `scripts/benchmark.py` in two isolated environments, one with the published
`polars-talib==0.1.6` wheel and one with the candidate 0.2.0 release wheel. Install
the same Polars and NumPy versions in both. The recorded runs use Python 3.12.7,
AMD Ryzen 9 9950X 16-Core Processor, Polars 1.44.2, NumPy 2.5.3, 4 Polars threads,
CPU affinity 28–31, seed 26,
three warmups and 51 timed samples per query. Each measurement executes a lazy
query through `collect()` and consumes its output. Times are medians in milliseconds.

```sh
POLARS_MAX_THREADS=4 /path/to/baseline/python scripts/benchmark.py --output baseline.json --repeats 51 --pin-cpus 4
POLARS_MAX_THREADS=4 /path/to/candidate/python scripts/benchmark.py --output candidate.json --repeats 51 --pin-cpus 4
python scripts/compare_benchmarks.py baseline.json candidate.json
```

`--pin-cpus` is optional and Linux-specific. Raw samples and metadata are checked
in as [baseline JSON](benchmarks/0.1.6-linux-x64.json) and
[candidate JSON](benchmarks/0.2.0-linux-x64.json). CPU clocks and other workloads
can change results; the script records enough context to reject mismatched runs.

## Full comparison

| Query / rows | 0.1.6 median ms | 0.2.0 median ms | Speedup |
| --- | ---: | ---: | ---: |
| ema/1000 | 0.0118 | 0.0121 | 0.97x |
| rsi/1000 | 0.0139 | 0.0126 | 1.11x |
| macd/1000 | 0.0196 | 0.0163 | 1.20x |
| atr/1000 | 0.0266 | 0.0248 | 1.07x |
| multi/1000 | 0.0499 | 0.0434 | 1.15x |
| grouped_rsi/1000 | 0.0362 | 0.0410 | 0.88x |
| null_rsi/1000 | 0.0147 | 0.0128 | 1.15x |
| chunked_ema/1000 | 0.0142 | 0.0141 | 1.01x |
| ema/100000 | 0.1582 | 0.1397 | 1.13x |
| rsi/100000 | 0.4039 | 0.1950 | 2.07x |
| macd/100000 | 0.6713 | 0.1555 | 4.32x |
| atr/100000 | 0.4204 | 0.1035 | 4.06x |
| multi/100000 | 0.5564 | 0.2259 | 2.46x |
| grouped_rsi/100000 | 0.4349 | 0.3860 | 1.13x |
| null_rsi/100000 | 0.4515 | 0.2329 | 1.94x |
| chunked_ema/100000 | 0.1759 | 0.1585 | 1.11x |
| ema/1000000 | 2.3360 | 2.0926 | 1.12x |
| rsi/1000000 | 4.9425 | 2.6745 | 1.85x |
| macd/1000000 | 11.8420 | 4.4413 | 2.67x |
| atr/1000000 | 5.4118 | 2.0036 | 2.70x |
| multi/1000000 | 11.5009 | 6.5826 | 1.75x |
| grouped_rsi/1000000 | 5.4803 | 4.9722 | 1.10x |
| null_rsi/1000000 | 6.6573 | 4.3047 | 1.55x |
| chunked_ema/1000000 | 3.6456 | 3.4731 | 1.05x |

The candidate JSON additionally measures SuperTrend, VWAP, HMA and KDJ, which do
not exist in 0.1.6. There is no fabricated old-version ratio for these functions.

## Where the speedups come from: TA-Lib core versus the wrapper

The wrapper layer around the C calls is a fixed per-call cost (Polars expression
evaluation, casting/rechunking inputs, one output allocation); it does not scale
with the algorithm. To attribute the deltas, the same functions were timed on
50k-row data both through Polars (`df.select(...)`, best of 3×25 runs) and by
calling `TA_*` directly from a C program linked against the 0.4.0 library shipped
in 0.1.6 and the 0.8.1 library shipped here (Linux x86_64, one machine).

| function | C core 0.4.0 ms | C core 0.8.1 ms | core speedup | Polars 0.1.6 ms | Polars 0.2.0 ms | e2e speedup |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| sma(30) | 0.065 | 0.059 | 1.10x | 0.093 | 0.090 | 1.04x |
| ema(30) | 0.132 | 0.103 | 1.29x | 0.169 | 0.125 | 1.35x |
| dema(30) | 0.439 | 0.121 | 3.63x | 0.384 | 0.143 | 2.69x |
| tema(30) | 0.582 | 0.114 | 5.10x | 0.557 | 0.138 | 4.04x |
| trix(30) | 0.503 | 0.139 | 3.61x | 0.569 | 0.161 | 3.54x |
| rsi(14) | 0.351 | 0.183 | 1.92x | 0.398 | 0.209 | 1.90x |
| macd() | 0.623 | 0.123 | 5.08x | 0.590 | 0.173 | 3.40x |
| atr(14) | 0.349 | 0.060 | 5.80x | 0.545 | 0.199 | 2.74x |
| natr(14) | 0.351 | 0.072 | 4.90x | 0.549 | 0.202 | 2.71x |
| bbands(20) | 0.256 | 0.193 | 1.33x | 0.356 | 0.282 | 1.26x |
| stoch() | 0.588 | 0.585 | 1.00x | 0.839 | 0.788 | 1.07x |
| adx(14) | 0.495 | 0.478 | 1.04x | 0.716 | 0.701 | 1.02x |
| cdlengulfing() | 0.296 | 0.318 | 0.93x | 0.442 | 0.478 | 0.92x |
| ht_trendline() | 3.177 | 4.326 | 0.73x | 3.664 | 4.482 | 0.82x |

Readings:

* Every large speedup (MACD, DEMA/TEMA/TRIX, ATR/NATR, RSI) is in the TA-Lib core:
  upstream 0.8.x rewrote those algorithms. The end-to-end gain is smaller than the
  core gain where the fixed wrapper cost now dominates the much shorter core time.
* Two functions are slower in upstream 0.8.1 itself: `ht_trendline` (0.73x) and
  `cdlengulfing` (0.93x). This is not a build-flag effect: `-O2`, `-O3` and forcing
  `-mfma` give the same numbers, and the `target_clones("default","fma")` runtime
  dispatch is active in the static library. Absolute cost stays below 5 ms per 50k rows.
* The wrapper cost itself is 0.02–0.05 ms for one input and 0.13–0.2 ms for three
  or four inputs on 50k rows, of the same order as Polars' own multi-column
  expression evaluation (`pl.col("high") + pl.col("low")` costs about 0.09 ms on the
  same frame). It does not copy inputs: single-chunk Float64 columns are borrowed.

## Implementation choices and regression checks

Most throughput gains come from the 0.8.1 C algorithms. The Polars wrapper borrows
contiguous Float64 buffers directly, and uses Polars' native null-fill kernel only
when nulls are present. A general iterator conversion was measured and rejected
because it slowed the null-heavy case. Chunked and cast inputs still need their
required materialization. Outputs transfer Rust vectors into Polars without a
Python per-row callback.

The published wheels retain portable CPU settings. MSVC explicitly receives
`/O2` because cmake-rs replaces the default Release flags for that generator. We do not enable unsafe
floating-point fast-math, native-only instruction sets, or approximations to
improve a benchmark. The 201-indicator correctness suite remains the first gate.

CI compares the published 0.1.6 and candidate wheels on the same runner and retains
both JSON reports. It fails on >25% regressions in EMA, RSI, MACD, ATR, null RSI or
chunked EMA at 100k and 1M rows. All other cases are reported, including smaller
and grouped queries; those are not hard-gated because scheduler noise is large
relative to their execution time. This threshold detects substantial regressions,
not a proof that smaller regressions never occur.
