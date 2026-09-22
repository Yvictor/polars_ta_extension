# polars_talib usage patterns

## Screener over many symbols (lazy)

```python
import polars as pl
import polars_talib as plta

signals = (
    pl.scan_parquet("prices.parquet")            # symbol, date, open, high, low, close, volume
    .sort("symbol", "date")
    .with_columns(
        plta.rsi(timeperiod=14).over("symbol").alias("rsi"),
        plta.ema(timeperiod=20).over("symbol").alias("ema20"),
        plta.ema(timeperiod=50).over("symbol").alias("ema50"),
        plta.atr(timeperiod=14).over("symbol").alias("atr"),
        plta.vwap().over("symbol").alias("vwap"),
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
df.with_columns(plta.bbands(timeperiod=20, nbdevup=2, nbdevdn=2).alias("bb")).unnest("bb")
df.with_columns(plta.kdj().struct.field("j").alias("kdj_j"))
df.with_columns(plta.ha().alias("ha")).unnest("ha")   # haopen, hahigh, halow, haclose
```

`plta.get_functions_output_struct()` lists every struct producing function with its fields.

## Custom input columns

```python
# any numeric column can be the "real" input
pl.col("adj_close").ta.rsi(14)
plta.rsi(pl.col("adj_close"), timeperiod=14)

# two-input functions (beta, correl, add, ...): primary input first
pl.col("stock_ret").ta.beta(pl.col("index_ret"), timeperiod=60)
plta.correl(pl.col("a"), pl.col("b"), timeperiod=30)

# functions that need volume
pl.col("close").ta.obv(pl.col("volume"))
plta.mfi(timeperiod=14)                 # uses high/low/close/volume columns
plta.vwma(pl.col("close"), pl.col("volume"), timeperiod=20)
```

## Candlestick patterns

Every `cdl*` function returns `Int32` (`100` bullish, `-100` bearish, `0` none).

```python
patterns = [fn for fn in plta.get_function_groups()["Pattern Recognition"]]
df.with_columns([getattr(plta, fn)().alias(fn) for fn in patterns])
```

## Rolling window helpers

```python
plta.max(timeperiod=20)          # highest close of the last 20 rows (TA-Lib MAX)
plta.minmaxindex(timeperiod=20)  # struct: minidx, maxidx
plta.percentrank(timeperiod=100)
plta.linearreg_slope(timeperiod=14)
```

## Verifying against the Python talib package

```python
import talib
import numpy as np
expected = talib.RSI(df["close"].to_numpy(), timeperiod=14)
got = df.select(plta.rsi(timeperiod=14))["close"].to_numpy()
np.testing.assert_allclose(got, expected, equal_nan=True)
```
