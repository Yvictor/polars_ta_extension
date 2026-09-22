---
name: polars-talib
description: Build and debug technical indicators in Polars using polars-talib expressions, including grouped time series, lazy queries, multi-output indicators, null handling, and migration to polars-talib 0.2.0.
---

# Polars TA-Lib expressions

Use `polars-talib` when the user wants TA-Lib indicators in a Polars pipeline. Import `polars_talib` to register `.ta`. The distribution name contains a hyphen; the import contains an underscore. Version 0.2.0 bundles TA-Lib 0.8.1 and exposes all 201 batch indicators. Its wheels do not need a system TA-Lib installation or the separate Python `TA-Lib` package.

Check the active interpreter and installed versions before changing dependencies. Install with that interpreter's package manager, for example `python -m pip install 'polars-talib==0.2.0'`. If 0.2.0 is not published yet, use the user's reviewed wheel or checkout; do not silently fall back to an older release. Python 3.10+ and Polars 1.20+ are required. Prefer a wheel for the user's platform; read the repository build documentation if no compatible wheel exists.

## Construct expressions

```python
import polars as pl
import polars_talib as ta

result = (
    bars.sort(["symbol", "timestamp"])
    .with_columns(
        ta.rsi(pl.col("close"), timeperiod=14).over("symbol").alias("rsi"),
        ta.macd(pl.col("close")).over("symbol").alias("macd"),
        ta.atr(pl.col("high"), pl.col("low"), pl.col("close"))
          .over("symbol").alias("atr"),
    )
    .unnest("macd")
)
```

- Sort chronologically within each instrument before computing. Use `.over("symbol")` to prevent history from one instrument leaking into another. Decide session boundaries explicitly for cumulative indicators such as VWAP; it does not reset at midnight automatically.
- Compose native expressions in `select`/`with_columns`, including lazy pipelines. Avoid Python `map_elements` or per-row loops. History-dependent indicators must see a complete ordered group; a streaming query is not the TA-Lib incremental streaming API.
- Use `pl.col(...)` for column arguments, especially legacy top-level functions. Namespace receiver conventions vary: RSI takes close, ATR's receiver is close with high/low arguments, and candlestick patterns use open. Inspect `inspect.signature(ta.<function>)` or the namespace method rather than guessing argument order.
- Multi-output indicators return a Struct. Use `.struct.field("macdhist")`, or alias then `unnest`. Discover names through `ta.get_functions_output_struct()`; SuperTrend's `trend` and Fractal outputs are integers, while price outputs are Float64.
- Discover functions using `ta.get_functions()` and `ta.get_function_groups()`. All 14 moving-average types are in `ta.MA_Type`, including HMA, RMA, ZLEMA, DISABLED and DEFAULT.

## Missing data and compatibility

Inputs cast to Float64. Nulls become NaN before calling TA-Lib. Leading missing rows and warm-up rows produce NaN for floating outputs, zero for integer outputs; they are not Polars nulls. Short groups retain their input length. Internal missing values follow each TA-Lib algorithm's propagation behavior; choose a fill/drop policy explicitly, because filling prices changes the indicator. Do not convert warm-up NaNs to zero without the user's intended semantics.

In 0.2.0, BBANDS defaults to period 20, and APO/PPO use EMA (`matype=1`). To reproduce older defaults, pass `timeperiod=5` for BBANDS and `matype=0` for APO/PPO. DARKCLOUDCOVER and MATHOLD use upstream `penetration=0.5`; older wrappers incorrectly defaulted to 0.3. Floating results can differ slightly because the newer core changes rounding and fixes algorithms. Use explicit parameters and tolerant numeric comparisons when migrating.

For a correctness check, compare the same Float64 input and explicit parameters with Python `TA-Lib==0.8.1`. Check output length, warm-up alignment, groups, and NaNs as well as numeric values. For performance work, benchmark release wheels on the same machine, data, Polars version and thread count. Measure the complete query and record medians; do not promise universal speedups or financial returns.
