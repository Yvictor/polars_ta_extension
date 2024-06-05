# Polars Extension for Ta-Lib


## Getting Started

``` bash
pip install polars_talib
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

It's about 150x faster, see more detail in [basic.ipynb](./examples/basic.ipynb)

## Supported Indicators and Functions

``` python
import polars_talib as plta

# list of functions
plta.get_functions()

# dict of functions by group
plta.get_function_groups()
```



### Indicator Groups

* Overlap Studies
* Momentum Indicators
* Volume Indicators
* Volatility Indicators
* Price Transform
* Cycle Indicators
* Pattern Recognition

##### Overlap Studies
```
bbands               Bollinger Bands
dema                 Double Exponential Moving Average
ema                  Exponential Moving Average
ht_trendline         Hilbert Transform - Instantaneous Trendline
kama                 Kaufman Adaptive Moving Average
ma                   Moving average
mama                 MESA Adaptive Moving Average
mavp                 Moving average with variable period
midpoint             MidPoint over period
midprice             Midpoint Price over period
sar                  Parabolic SAR
sarext               Parabolic SAR - Extended
sma                  Simple Moving Average
t3                   Triple Exponential Moving Average (T3)
tema                 Triple Exponential Moving Average
trima                Triangular Moving Average
wma                  Weighted Moving Average
```

##### Momentum Indicators
```
adx                  Average Directional Movement Index
adxr                 Average Directional Movement Index Rating
apo                  Absolute Price Oscillator
aroon                Aroon
aroonosc             Aroon Oscillator
bop                  Balance Of Power
cci                  Commodity Channel Index
cmo                  Chande Momentum Oscillator
dx                   Directional Movement Index
macd                 Moving Average Convergence/Divergence
macdext              MACD with controllable MA type
macdfix              Moving Average Convergence/Divergence Fix 12/26
mfi                  Money Flow Index
minus_di             Minus Directional Indicator
minus_dm             Minus Directional Movement
mom                  Momentum
plus_di              Plus Directional Indicator
plus_dm              Plus Directional Movement
ppo                  Percentage Price Oscillator
roc                  Rate of change : ((price/prevPrice)-1)*100
rocp                 Rate of change Percentage: (price-prevPrice)/prevPrice
rocr                 Rate of change ratio: (price/prevPrice)
rocr100              Rate of change ratio 100 scale: (price/prevPrice)*100
rsi                  Relative Strength Index
stoch                Stochastic
stochf               Stochastic Fast
stochrsi             Stochastic Relative Strength Index
trix                 1-day Rate-Of-Change (ROC) of a Triple Smooth EMA
ultosc               Ultimate Oscillator
willr                Williams' %R
```

##### Volume Indicators
```
ad                   Chaikin A/D Line
adosc                Chaikin A/D Oscillator
obv                  On Balance Volume
```

##### Cycle Indicators
```
ht_dcperiod          Hilbert Transform - Dominant Cycle Period
ht_dcphase           Hilbert Transform - Dominant Cycle Phase
ht_phasor            Hilbert Transform - Phasor Components
ht_sine              Hilbert Transform - SineWave
ht_trendmode         Hilbert Transform - Trend vs Cycle Mode
```

##### Price Transform
```
avgprice             Average Price
medprice             Median Price
typprice             Typical Price
wclprice             Weighted Close Price
```

##### Volatility Indicators
```
atr                  Average True Range
natr                 Normalized Average True Range
trange               True Range
```

##### Pattern Recognition
```
cdl2crows            Two Crows
cdl3blackcrows       Three Black Crows
cdl3inside           Three Inside Up/Down
cdl3linestrike       Three-Line Strike
cdl3outside          Three Outside Up/Down
cdl3starsinsoutH     Three Stars In The South
cdl3whitesoldieRS    Three Advancing White Soldiers
cdlabandonedbabY     Abandoned Baby
cdladvanceblock      Advance Block
cdlbelthold          Belt-hold
cdlbreakaway         Breakaway
cdlclosingmarubOZU   Closing Marubozu
cdlconcealbabysWALL  Concealing Baby Swallow
cdlcounterattacK     Counterattack
cdldarkcloudcovER    Dark Cloud Cover
cdldoji              Doji
cdldojistar          Doji Star
cdldragonflydojI     Dragonfly Doji
cdlengulfing         Engulfing Pattern
cdleveningdojisTAR   Evening Doji Star
cdleveningstar       Evening Star
cdlgapsidesidewHITE  Up/Down-gap side-by-side white lines
cdlgravestonedoJI    Gravestone Doji
cdlhammer            Hammer
cdlhangingman        Hanging Man
cdlharami            Harami Pattern
cdlharamicross       Harami Cross Pattern
cdlhighwave          High-Wave Candle
cdlhikkake           Hikkake Pattern
cdlhikkakemod        Modified Hikkake Pattern
cdlhomingpigeon      Homing Pigeon
cdlidentical3crOWS   Identical Three Crows
cdlinneck            In-Neck Pattern
cdlinvertedhammER    Inverted Hammer
cdlkicking           Kicking
cdlkickingbylenGTH   Kicking - bull/bear determined by the longer marubozu
cdlladderbottom      Ladder Bottom
cdllongleggeddoJI    Long Legged Doji
cdllongline          Long Line Candle
cdlmarubozu          Marubozu
cdlmatchinglow       Matching Low
cdlmathold           Mat Hold
cdlmorningdojisTAR   Morning Doji Star
cdlmorningstar       Morning Star
cdlonneck            On-Neck Pattern
cdlpiercing          Piercing Pattern
cdlrickshawman       Rickshaw Man
cdlrisefall3metHODS  Rising/Falling Three Methods
cdlseparatingliNES   Separating Lines
cdlshootingstar      Shooting Star
cdlshortline         Short Line Candle
cdlspinningtop       Spinning Top
cdlstalledpatteRN    Stalled Pattern
cdlsticksandwicH     Stick Sandwich
cdltakuri            Takuri (Dragonfly Doji with very long lower shadow)
cdltasukigap         Tasuki Gap
cdlthrusting         Thrusting Pattern
cdltristar           Tristar Pattern
cdlunique3river      Unique 3 River
cdlupsidegap2crOWS   Upside Gap Two Crows
cdlxsidegap3metHODS  Upside/Downside Gap Three Methods
```

##### Statistic Functions
```
beta                 Beta
correl               Pearson's Correlation Coefficient (r)
linearreg            Linear Regression
linearreg_angle      Linear Regression Angle
linearreg_intercept  Linear Regression Intercept
linearreg_slope      Linear Regression Slope
stddev               Standard Deviation
tsf                  Time Series Forecast
var                  Variance
```