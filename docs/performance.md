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

The following table was contributed in [PR #37's review](https://github.com/Yvictor/polars_ta_extension/pull/37)
using its implementation, not the current #38 wrapper. That author reported
50k-row Linux x86_64 measurements, best of 3×25 runs, comparing direct C calls
against Polars expressions. The C harness and raw samples for this table were
not committed, so these are attributed supporting observations rather than a
reproducible benchmark of this PR. The raw 51-sample reports above and current
CI artifacts are the reproducible evidence for this implementation.

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

The measurements support upstream C changes as a major source of the MACD,
DEMA/TEMA/TRIX, ATR/NATR and RSI gains. They also report slower HT_TRENDLINE and
CDLENGULFING on that configuration; those ratios are not platform-wide promises.
The accompanying compiler/FMA investigation has not been independently reproduced
here. Wrapper work is not a constant independent of input size: null filling,
casting, rechunking, scalar expansion and output initialization can scale with rows.
Do not attribute every end-to-end change to C or subtract measurements from
different runs to claim an exact wrapper cost.

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
both JSON reports and a job summary. Timing regressions above 25% in the selected
long-series cases produce warnings with `--report-only`, not release failures:
shared runners are noisy. Installation, execution, malformed data and incomparable
metadata still fail the benchmark job. The release depends on all correctness,
compatibility and source-build jobs, while benchmark results remain informational.
Without `--report-only`, the comparison script still enforces the threshold for
controlled local measurements. New indicators need direct before/after comparisons
because they do not exist in the 0.1.6 baseline.


## Follow-up: output allocation after review

The direct comparison of PRs #37/#38 found that #38's new SuperTrend wrapper was
slower despite passing numerical tests. The original generated wrappers filled
the entire output with padding before C overwrote the valid rows. The shared
`OutputBuffer` now initializes only warm-up rows, lets C write into spare capacity,
and exposes only the successful, validated output range. Any unwritten tail is
padded before returning; failed calls never expose uninitialized values.

We compared the local release wheel at `97b66f4` against the reviewed follow-up
implementation on the same Ryzen 9950X / Python 3.12.7 / Polars 1.44.2 / NumPy
2.5.3, with four threads pinned to CPUs 28–31. Each case uses three warmups and
51 samples. Round 1 ran before→after; round 2 ran after→before. The retained
reports include all measured cases, not only the improvements:
[before 1](benchmarks/review-followup/before-first.json),
[after 1](benchmarks/review-followup/after-first.json),
[before 2](benchmarks/review-followup/before-second.json),
[after 2](benchmarks/review-followup/after-second.json).

| 1M rows | Before / after, round 1 (ms) | Before / after, round 2 (ms) | Observation |
| --- | ---: | ---: | --- |
| SuperTrend | 4.0444 / 3.3861 | 4.0969 / 3.4031 | 1.19–1.20x speedup |
| KDJ | 12.6232 / 12.0319 | 12.6955 / 11.6715 | 1.05–1.09x speedup |
| HMA | 3.1996 / 3.1296 | 3.2115 / 3.1078 | 1.02–1.03x speedup |
| null RSI | 4.3842 / 4.4215 | 4.3761 / 4.3602 | Within 1% |
| multi | 6.7141 / 7.2854 | 6.8650 / 6.7024 | Variable; no stable gain |

These runs include the shared input-broadcasting changes as well as allocation
changes; they are not a controlled C-only attribution experiment. They address
the measured new-indicator overhead, not a proof of optimal performance for all
201 indicators or platforms. Correctness and bounds checks remain required.
