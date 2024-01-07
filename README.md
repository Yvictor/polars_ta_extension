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
BBANDS               Bollinger Bands
DEMA                 Double Exponential Moving Average
EMA                  Exponential Moving Average
HT_TRENDLINE         Hilbert Transform - Instantaneous Trendline
KAMA                 Kaufman Adaptive Moving Average
MA                   Moving average
MAMA                 MESA Adaptive Moving Average
MAVP                 Moving average with variable period
MIDPOINT             MidPoint over period
MIDPRICE             Midpoint Price over period
SAR                  Parabolic SAR
SAREXT               Parabolic SAR - Extended
SMA                  Simple Moving Average
T3                   Triple Exponential Moving Average (T3)
TEMA                 Triple Exponential Moving Average
TRIMA                Triangular Moving Average
WMA                  Weighted Moving Average
```

##### Momentum Indicators
```
ADX                  Average Directional Movement Index
ADXR                 Average Directional Movement Index Rating
APO                  Absolute Price Oscillator
AROON                Aroon
AROONOSC             Aroon Oscillator
BOP                  Balance Of Power
CCI                  Commodity Channel Index
CMO                  Chande Momentum Oscillator
DX                   Directional Movement Index
MACD                 Moving Average Convergence/Divergence
MACDEXT              MACD with controllable MA type
MACDFIX              Moving Average Convergence/Divergence Fix 12/26
MFI                  Money Flow Index
MINUS_DI             Minus Directional Indicator
MINUS_DM             Minus Directional Movement
MOM                  Momentum
PLUS_DI              Plus Directional Indicator
PLUS_DM              Plus Directional Movement
PPO                  Percentage Price Oscillator
ROC                  Rate of change : ((price/prevPrice)-1)*100
ROCP                 Rate of change Percentage: (price-prevPrice)/prevPrice
ROCR                 Rate of change ratio: (price/prevPrice)
ROCR100              Rate of change ratio 100 scale: (price/prevPrice)*100
RSI                  Relative Strength Index
STOCH                Stochastic
STOCHF               Stochastic Fast
STOCHRSI             Stochastic Relative Strength Index
TRIX                 1-day Rate-Of-Change (ROC) of a Triple Smooth EMA
ULTOSC               Ultimate Oscillator
WILLR                Williams' %R
```

##### Volume Indicators
```
AD                   Chaikin A/D Line
ADOSC                Chaikin A/D Oscillator
OBV                  On Balance Volume
```

##### Cycle Indicators
```
HT_DCPERIOD          Hilbert Transform - Dominant Cycle Period
HT_DCPHASE           Hilbert Transform - Dominant Cycle Phase
HT_PHASOR            Hilbert Transform - Phasor Components
HT_SINE              Hilbert Transform - SineWave
HT_TRENDMODE         Hilbert Transform - Trend vs Cycle Mode
```

##### Price Transform
```
AVGPRICE             Average Price
MEDPRICE             Median Price
TYPPRICE             Typical Price
WCLPRICE             Weighted Close Price
```

##### Volatility Indicators
```
ATR                  Average True Range
NATR                 Normalized Average True Range
TRANGE               True Range
```

##### Pattern Recognition
```
CDL2CROWS            Two Crows
CDL3BLACKCROWS       Three Black Crows
CDL3INSIDE           Three Inside Up/Down
CDL3LINESTRIKE       Three-Line Strike
CDL3OUTSIDE          Three Outside Up/Down
CDL3STARSINSOUTH     Three Stars In The South
CDL3WHITESOLDIERS    Three Advancing White Soldiers
CDLABANDONEDBABY     Abandoned Baby
CDLADVANCEBLOCK      Advance Block
CDLBELTHOLD          Belt-hold
CDLBREAKAWAY         Breakaway
CDLCLOSINGMARUBOZU   Closing Marubozu
CDLCONCEALBABYSWALL  Concealing Baby Swallow
CDLCOUNTERATTACK     Counterattack
CDLDARKCLOUDCOVER    Dark Cloud Cover
CDLDOJI              Doji
CDLDOJISTAR          Doji Star
CDLDRAGONFLYDOJI     Dragonfly Doji
CDLENGULFING         Engulfing Pattern
CDLEVENINGDOJISTAR   Evening Doji Star
CDLEVENINGSTAR       Evening Star
CDLGAPSIDESIDEWHITE  Up/Down-gap side-by-side white lines
CDLGRAVESTONEDOJI    Gravestone Doji
CDLHAMMER            Hammer
CDLHANGINGMAN        Hanging Man
CDLHARAMI            Harami Pattern
CDLHARAMICROSS       Harami Cross Pattern
CDLHIGHWAVE          High-Wave Candle
CDLHIKKAKE           Hikkake Pattern
CDLHIKKAKEMOD        Modified Hikkake Pattern
CDLHOMINGPIGEON      Homing Pigeon
CDLIDENTICAL3CROWS   Identical Three Crows
CDLINNECK            In-Neck Pattern
CDLINVERTEDHAMMER    Inverted Hammer
CDLKICKING           Kicking
CDLKICKINGBYLENGTH   Kicking - bull/bear determined by the longer marubozu
CDLLADDERBOTTOM      Ladder Bottom
CDLLONGLEGGEDDOJI    Long Legged Doji
CDLLONGLINE          Long Line Candle
CDLMARUBOZU          Marubozu
CDLMATCHINGLOW       Matching Low
CDLMATHOLD           Mat Hold
CDLMORNINGDOJISTAR   Morning Doji Star
CDLMORNINGSTAR       Morning Star
CDLONNECK            On-Neck Pattern
CDLPIERCING          Piercing Pattern
CDLRICKSHAWMAN       Rickshaw Man
CDLRISEFALL3METHODS  Rising/Falling Three Methods
CDLSEPARATINGLINES   Separating Lines
CDLSHOOTINGSTAR      Shooting Star
CDLSHORTLINE         Short Line Candle
CDLSPINNINGTOP       Spinning Top
CDLSTALLEDPATTERN    Stalled Pattern
CDLSTICKSANDWICH     Stick Sandwich
CDLTAKURI            Takuri (Dragonfly Doji with very long lower shadow)
CDLTASUKIGAP         Tasuki Gap
CDLTHRUSTING         Thrusting Pattern
CDLTRISTAR           Tristar Pattern
CDLUNIQUE3RIVER      Unique 3 River
CDLUPSIDEGAP2CROWS   Upside Gap Two Crows
CDLXSIDEGAP3METHODS  Upside/Downside Gap Three Methods
```

##### Statistic Functions
```
BETA                 Beta
CORREL               Pearson's Correlation Coefficient (r)
LINEARREG            Linear Regression
LINEARREG_ANGLE      Linear Regression Angle
LINEARREG_INTERCEPT  Linear Regression Intercept
LINEARREG_SLOPE      Linear Regression Slope
STDDEV               Standard Deviation
TSF                  Time Series Forecast
VAR                  Variance
```