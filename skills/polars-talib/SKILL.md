---
name: polars-talib
description: Compute TA-Lib technical indicators (SMA, EMA, RSI, MACD, KDJ, SuperTrend, VWAP, candlestick patterns and 190+ more) as native Polars expressions with the polars_talib extension. Use when the user works with OHLCV market data in Polars and asks for technical analysis, indicators, TA-Lib, multi-symbol (grouped) indicator pipelines, or when migrating pandas/talib code to Polars.
---

# polars_talib: TA-Lib indicators as Polars expressions

`polars_talib` wraps TA-Lib 0.8.1 (201 functions) as Polars expression plugins.
Indicators run in Rust/C on the whole column, work lazily, and combine with
`.over("symbol")` for multi-symbol data.

## Install

```bash
pip install polars_talib          # or: uv add polars_talib
```

```python
import polars as pl
import polars_talib as plta       # registers the `.ta` expression namespace

plta.__talib_version__            # bundled TA-Lib version, e.g. "0.8.1 (...)"
plta.get_functions()              # all 201 function names (lower case)
plta.get_function_groups()        # {"Momentum Indicators": [...], ...}
plta.get_functions_output_struct()  # struct field names of multi-output functions
```

## Two equivalent call styles

1. Expression namespace, primary input first:
   `pl.col("close").ta.rsi(timeperiod=14)`,
   `pl.col("close").ta.atr(pl.col("high"), pl.col("low"), timeperiod=14)`.
   Other inputs may be strings (`"high"`) or expressions.
2. Module functions mirroring `talib.abstract`, with column defaults
   `open/high/low/close/volume`:
   `plta.rsi()`, `plta.rsi(pl.col("adj_close"), timeperiod=7)`,
   `plta.atr(timeperiod=14)`, `plta.kdj(pl.col("high"), pl.col("low"), pl.col("close"))`.
   Positional inputs here must be `pl.Expr`, not strings.

Primary input rule (namespace style): `open` for OHLC pattern/candle
functions, `close` for functions that take close, otherwise the first input
(`high` for high/low functions, `volume` for volume-only functions).
See `reference/functions.md` for the exact inputs, parameters, defaults and
outputs of every function.

## Core patterns

```python
df = pl.DataFrame({...})  # columns: symbol, date, open, high, low, close, volume

out = df.with_columns(
    pl.col("close").ta.ema(20).alias("ema20"),
    plta.rsi(timeperiod=14).alias("rsi"),
    plta.macd(fastperiod=12, slowperiod=26, signalperiod=9).alias("macd"),
    plta.cdlengulfing().alias("engulfing"),        # Int32: 100 / 0 / -100
).unnest("macd")                                    # -> macd, macdsignal, macdhist
```

Multi-symbol data: sort by time inside each group, then use `.over()`.

```python
out = (
    df.sort("symbol", "date")
    .with_columns(
        plta.sma(timeperiod=5).over("symbol").alias("sma5"),
        plta.kdj().over("symbol").struct.field("k").alias("kdj_k"),
        plta.supertrend(timeperiod=10, multiplier=3.0).over("symbol").alias("st"),
    )
    .with_columns(pl.col("st").struct.field("supertrend"), pl.col("st").struct.field("trend"))
)
```

Lazy frames work the same way (`pl.scan_parquet(...).with_columns(...).collect()`).

## Semantics to remember

* Outputs are `Float64` (or `Int32` for patterns, `maxindex`, `fractal`, `supertrend.trend`, ...).
  The first `lookback` rows of every output are `NaN` (float) or `0` (int), exactly like TA-Lib.
* Nulls in inputs are treated as `NaN`; leading NaN rows are skipped so the
  indicator starts at the first complete row, matching the Python `talib` package.
* Inputs are cast to `Float64` automatically (Float32/Int columns are fine).
* A group shorter than the lookback returns an all-NaN/zero column of the same length.
* Invalid parameters raise `polars.exceptions.ComputeError` mentioning `TA_BAD_PARAM`.
* `matype` values: 0 SMA, 1 EMA, 2 WMA, 3 DEMA, 4 TEMA, 5 TRIMA, 6 KAMA, 7 MAMA, 8 T3,
  9 HMA, 10 DISABLED, 11 DEFAULT, 12 ZLEMA, 13 RMA (KDJ defaults to RMA).
* Parameter defaults follow upstream TA-Lib 0.8.1: `bbands(timeperiod=20)`,
  `apo`/`ppo` `matype=1` (EMA), `cdldarkcloudcover`/`cdlmathold` `penetration=0.5`.
  Pass parameters explicitly when reproducing older (0.1.x / TA-Lib 0.4) results.
* Struct outputs use TA-Lib's output names: e.g. `macd/macdsignal/macdhist`,
  `slowk/slowd`, `upperband/middleband/lowerband`, `k/d/j`, `supertrend/trend`,
  `haopen/hahigh/halow/haclose`, `plusvi/minusvi`, `bullpower/bearpower`.

## Functions added in 0.2.0 (TA-Lib 0.8.x)

Momentum: `ac ao cmou coppock dpo er eri fosc fractal imi kdj qstick smi tsi vhf vortex wad`.
Overlap: `accbands donchian hma kc rma supertrend vwma zlema`.
Volume: `cmf efi marketfi nvi pvi pvo pvt rvol vwap`.
Volatility: `adr cvi massi rvi`. Statistic: `percentile percentrank`.
Price transform: `avgdev ha` (Heikin-Ashi). Math: `cumsum`.

## Migrating from pandas + talib

| pandas / talib | polars_talib |
|---|---|
| `df.groupby("sym")["close"].transform(lambda x: ta.SMA(x, 5))` | `plta.sma(timeperiod=5).over("sym")` |
| `ta.MACD(df.close)[0]` | `plta.macd().struct.field("macd")` |
| `ta.STOCH(df.high, df.low, df.close)` | `plta.stoch().unnest()` or `.struct.field("slowk")` |
| `ta.CDLDOJI(o, h, l, c)` | `plta.cdldoji()` |
| `ta.MA(x, 20, matype=ta.MA_Type.EMA)` | `plta.ma(timeperiod=20, matype=1)` |

Numerical results are identical to the Python `talib` package built against the
same TA-Lib version (the test-suite asserts equality function by function).

## Building from source / contributing

`talib-sys/build.rs` downloads and statically builds TA-Lib (version in
`TA_LIB_VER`) into `talib-sys/dependencies`; `make dev-release` (maturin) builds
the extension. Useful env vars: `DEPS_PATH`, `TA_LIBRARY_PATH`, `TA_INCLUDE_PATH`,
`TA_LIB_SRC_ARCHIVE` (offline tarball), `TA_LIB_BUILD_SYSTEM=cmake|autotools`.
To expose new upstream functions run `python scripts/gen_talib_functions.py --apply`
(needs the matching Python `ta-lib` installed), then `cargo build -p talib-sys --features bindgen`
to refresh the FFI bindings.
