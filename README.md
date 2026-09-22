# Polars Extension for Ta-Lib

Version **0.2.0** bundles **TA-Lib 0.8.1**: all **201 batch indicators**,
including SuperTrend, VWAP, HMA, KDJ and Heikin-Ashi. Python 3.10+; Polars 1.20+.
Binary wheels include the C library.

- [Upgrade notes, platform matrix and source builds](docs/upgrade-0.2.0.md)
- [Install the skill for Codex, Claude Code or Cursor](docs/skills.md)
- [Reproducible performance results](docs/performance.md)


## Native AI plugin installation

The repository supports the same native marketplace/install flow as
[Shioaji](https://github.com/Sinotrade/Shioaji#ai-coding-agent-skills):

```sh
# Claude Code
claude plugin marketplace add Yvictor/polars_ta_extension
claude plugin install polars-talib@polars-ta-extension

# Codex
codex plugin marketplace add Yvictor/polars_ta_extension
codex plugin add polars-talib@polars-ta-extension
```

See [skill installation](docs/skills.md) for invocation, updates, local checkouts,
standalone installation, and Cursor support. The plugin supplies coding guidance;
install the Python library separately.

## Getting Started

``` bash
pip install 'polars-talib==0.2.0'
```

and

```
import polars
import polars_talib as plta
```

## Usage

### single symbol usage
``` python
df.with_columns(
    pl.col("close").ta.ema(5).alias("ema5"),
    pl.col("close").ta.macd(12, 26, 9).struct.field("macd"),
    pl.col("close").ta.macd(12, 26, 9).struct.field("macdsignal"),
    pl.col("open").ta.cdl2crows(pl.col("high"), pl.col("low"), pl.col("close")).alias("cdl2crows"),
    pl.col("close").ta.wclprice("high", "low").alias("wclprice"),
)
```

### multiple symbol usage using over syntax

Sort by symbol and timestamp before computing history-dependent indicators.
``` python
df.with_columns(
    pl.col("close").ta.ema(5).over("symbol").alias("ema5"),
    pl.col("close").ta.macd(12, 26, 9).over("symbol").struct.field("macd"),
    pl.col("close").ta.macd(12, 26, 9).over("symbol").struct.field("macdsignal"),
    pl.col("open").ta.cdl2crows(
        pl.col("high"), pl.col("low"), pl.col("close")
    ).over("symbol").alias("cdl2crows"),
    pl.col("close").ta.wclprice("high", "low").over("symbol").alias("wclprice"),
)
```

### usage just like talib.abstract with more flexible
``` python
df.with_columns(
    plta.ht_dcperiod(),
    plta.ht_dcperiod(pl.col("close")),
    plta.aroon(),
    plta.aroon(pl.col("high"), pl.col("low"), timeperiod=10),
    plta.wclprice(),
    plta.wclprice(
        pl.col("high"), pl.col("low"), pl.col("close"), 
        timeperiod=10
    ),
)
```
## Performance

See the [0.2.0 release benchmark](docs/performance.md) for a controlled comparison
against 0.1.6, raw samples and a reproducible script. The notebook comparison
below is historical and measures a different workload.

### Polars with polars_talib
``` python
%%timeit
df = p.with_columns(
    plta.sma(timeperiod=5).over("Symbol").alias("sma5"),
    plta.macd(fastperiod=10, slowperiod=20, signalperiod=5).over("Symbol").alias("macd"),
    plta.stoch(pl.col("high"), pl.col("low"), pl.col("close"), fastk_period=14, slowk_period=7, slowd_period=7).over("Symbol").alias("stoch"),
    plta.wclprice().over("Symbol").alias("wclprice"),
).with_columns(
    pl.col("macd").struct.field("macd"),
    pl.col("macd").struct.field("macdsignal"),
    pl.col("macd").struct.field("macdhist"),
    pl.col("stoch").struct.field("slowk"),
    pl.col("stoch").struct.field("slowd"),
).select(
    pl.exclude("stoch")
).filter(
    pl.col("Symbol") == "AAPL"
).collect()
```

135 ms ± 5.6 ms per loop (mean ± std. dev. of 7 runs, 1 loop each)

### Pandas with talib
```python
%%timeit
df["sma5"] = df.groupby("Ticker")["close"].transform(lambda x: ta.SMA(x, timeperiod=5))
df["macd"] = df.groupby("Ticker")["close"].transform(lambda x: ta.MACD(x, fastperiod=10, slowperiod=20, signalperiod=5)[0])
df["macdsignal"] = df.groupby("Ticker")["close"].transform(lambda x: ta.MACD(x, fastperiod=10, slowperiod=20, signalperiod=5)[1])
df["macdhist"] = df.groupby("Ticker")["close"].transform(lambda x: ta.MACD(x, fastperiod=10, slowperiod=20, signalperiod=5)[2])
df["slowk"] = df.groupby("Ticker").apply(lambda x: ta.STOCH(x, fastk_period=14, slowk_period=7, slowd_period=7)).droplevel(0)["slowk"] 
df["slowd"] = df.groupby("Ticker").apply(lambda x: ta.STOCH(x, fastk_period=14, slowk_period=7, slowd_period=7)).droplevel(0)["slowd"]
df["wclprice"] = df.groupby("Ticker").apply(lambda x: ta.WCLPRICE(x)).droplevel(0)
df.loc["AAPL"]
```
19.2 s ± 367 ms per loop (mean ± std. dev. of 7 runs, 1 loop each)

That historical notebook measured about 150x for this workload; see [basic.ipynb](./examples/basic.ipynb)

## Supported Indicators and Functions

``` python
import polars_talib as plta

# list of functions
plta.get_functions()

# dict of functions by group
plta.get_function_groups()
```



The complete [201-indicator catalog](docs/indicators.md) includes every function
in the pinned upstream release. New examples:

```python
df.with_columns(
    plta.supertrend().alias("supertrend"),
    plta.vwap().alias("vwap"),
    pl.col("close").ta.hma(timeperiod=20).alias("hma"),
    plta.kdj().alias("kdj"),
)
```

Multi-output indicators return Struct columns. For example,
`plta.supertrend().struct.field("trend")` returns the Int32 trend flag.
