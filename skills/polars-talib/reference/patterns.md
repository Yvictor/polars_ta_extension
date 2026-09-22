# polars_talib usage patterns

## Screener over many symbols (lazy)

```python
import polars as pl
import polars_talib as ta

signals = (
    pl.scan_parquet("prices.parquet")            # symbol, date, open, high, low, close, volume
    .sort("symbol", "date")
    .with_columns(
        ta.rsi(timeperiod=14).over("symbol").alias("rsi"),
        ta.ema(timeperiod=20).over("symbol").alias("ema20"),
        ta.ema(timeperiod=50).over("symbol").alias("ema50"),
        ta.atr(timeperiod=14).over("symbol").alias("atr"),
        ta.vwap().over("symbol").alias("vwap"),   # cumulative per group; reset sessions yourself
    )
    .with_columns(
        golden_cross=(pl.col("ema20") > pl.col("ema50"))
        & (pl.col("ema20").shift(1).over("symbol") <= pl.col("ema50").shift(1).over("symbol"))
    )
    .filter(pl.col("golden_cross") & (pl.col("rsi") < 70))
    .collect()
)
```

## Struct outputs

```python
df.with_columns(ta.bbands(timeperiod=20, nbdevup=2, nbdevdn=2).alias("bb")).unnest("bb")
df.with_columns(ta.kdj().struct.field("j").alias("kdj_j"))
df.with_columns(ta.ha().alias("ha")).unnest("ha")   # haopen, hahigh, halow, haclose
df.with_columns(ta.supertrend().alias("st")).unnest("st")  # supertrend (Float64), trend (Int32)
```

`ta.get_functions_output_struct()` lists every struct-producing function with its fields.

## Custom input columns

```python
# any numeric column can be the "real" input; Float32/Int columns are cast to Float64
pl.col("adj_close").ta.rsi(14)
ta.rsi(pl.col("adj_close"), timeperiod=14)

# two-input functions (beta, correl, add, ...): receiver first
pl.col("stock_ret").ta.beta(pl.col("index_ret"), timeperiod=60)
ta.correl(pl.col("a"), pl.col("b"), timeperiod=30)

# functions that need volume
pl.col("close").ta.obv(pl.col("volume"))
ta.mfi(timeperiod=14)                        # uses high/low/close/volume columns
ta.vwma(pl.col("close"), pl.col("volume"), timeperiod=20)

# a length-1 literal broadcasts to the frame length
ta.add(pl.col("close"), pl.lit(1.0))
```

## Candlestick patterns

Every `cdl*` function returns Int32 (`100` bullish, `-100` bearish, `0` none); the
namespace receiver is `open`.

```python
patterns = ta.get_function_groups()["Pattern Recognition"]
df.with_columns([getattr(ta, fn)().alias(fn) for fn in patterns])
```

## Rolling window helpers

```python
ta.max(timeperiod=20)          # highest close of the last 20 rows (TA-Lib MAX)
ta.minmaxindex(timeperiod=20)  # struct: minidx, maxidx
ta.percentrank(timeperiod=100)
ta.linearreg_slope(timeperiod=14)
```

## Errors

* Inputs of different lengths (other than length-1 literals) raise
  `ComputeError: indicator input lengths differ`.
* Invalid parameters (`timeperiod=0`, unknown `matype`) raise `ComputeError`
  mentioning `TA_BAD_PARAM`.

## Verifying against the Python talib package

```python
import talib
import numpy as np
expected = talib.RSI(df["close"].to_numpy(), timeperiod=14)
got = df.select(ta.rsi(timeperiod=14)).to_series().to_numpy()
np.testing.assert_allclose(got, expected, equal_nan=True)
```
