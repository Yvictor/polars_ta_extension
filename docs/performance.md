# Performance measurements

The measured release wheel improves the main long-series indicators while keeping
native Polars execution. These are measurements on one Linux x86_64 machine, not
a claim of a globally optimal implementation or identical speedups on every CPU.

## Reproduce

Run `scripts/benchmark.py` in two isolated environments, one with the published
`polars-talib==0.1.6` wheel and one with the candidate 0.2.0 release wheel. Install
the same Polars and NumPy versions in both. The recorded runs use Python 3.12.7,
Polars 1.44.2, NumPy 2.5.3, 4 Polars threads, CPU affinity 28–31, seed 26,
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

## Implementation choices and regression checks

Most throughput gains come from the 0.8.1 C algorithms. The Polars wrapper borrows
contiguous Float64 buffers directly, and uses Polars' native null-fill kernel only
when nulls are present. A general iterator conversion was measured and rejected
because it slowed the null-heavy case. Chunked and cast inputs still need their
required materialization. Outputs transfer Rust vectors into Polars without a
Python per-row callback.

The published wheels retain portable CPU settings. We do not enable unsafe
floating-point fast-math, native-only instruction sets, or approximations to
improve a benchmark. The 201-indicator correctness suite remains the first gate.

CI compares the published 0.1.6 and candidate wheels on the same runner and retains
both JSON reports. It fails on >25% regressions in EMA, RSI, MACD, ATR, null RSI or
chunked EMA at 100k and 1M rows. All other cases are reported, including smaller
and grouped queries; those are not hard-gated because scheduler noise is large
relative to their execution time. This threshold detects substantial regressions,
not a proof that smaller regressions never occur.
