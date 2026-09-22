# Polars Extension for Ta-Lib


## Getting Started

``` bash
pip install polars_talib
```

Wheels bundle TA-Lib **0.8.1** statically (Linux x86_64/aarch64, macOS
x86_64/arm64, Windows x86_64), so no system TA-Lib installation is required.
All 201 TA-Lib functions are exposed, including the 0.8.x additions
(KDJ, SuperTrend, VWAP, HMA, RMA, ZLEMA, Donchian/Keltner channels,
Heikin-Ashi, Vortex, TSI, SMI, ...).

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

### 0.2.0 (TA-Lib 0.8.1) vs 0.1.6 (TA-Lib 0.4.0)

Single expression on 50k rows, best of 7 runs (Linux x86_64, 4 cores), see
`tests/test_bench.py` for the CI benchmarks:

| expression | 0.1.6 | 0.2.0 | speedup |
|---|---|---|---|
| `macd()` | 0.541 ms | 0.156 ms | 3.5x |
| `tema(30)` | 0.487 ms | 0.137 ms | 3.6x |
| `trix(30)` | 0.514 ms | 0.152 ms | 3.4x |
| `atr(14)` | 0.584 ms | 0.174 ms | 3.4x |
| `natr(14)` | 0.559 ms | 0.186 ms | 3.0x |
| `dema(30)` | 0.354 ms | 0.149 ms | 2.4x |
| `rsi(14)` | 0.386 ms | 0.189 ms | 2.0x |
| `ema(30)` | 0.155 ms | 0.123 ms | 1.3x |
| `macd().over("symbol")` (50 symbols) | 1.677 ms | 1.355 ms | 1.2x |
| `kdj()` / `supertrend()` / `vwap()` | - | 0.85 / 0.67 / 0.26 ms | new |

The remaining functions are within measurement noise of 0.1.6.

## Supported Indicators and Functions

``` python
import polars_talib as plta

# list of functions
plta.get_functions()

# dict of functions by group
plta.get_function_groups()
```



### Indicator Groups

* Cycle Indicators
* Math Operators
* Math Transform
* Momentum Indicators
* Overlap Studies
* Pattern Recognition
* Price Transform
* Statistic Functions
* Volatility Indicators
* Volume Indicators

##### Cycle Indicators
```
ht_dcperiod          Hilbert Transform - Dominant Cycle Period
ht_dcphase           Hilbert Transform - Dominant Cycle Phase
ht_phasor            Hilbert Transform - Phasor Components
ht_sine              Hilbert Transform - SineWave
ht_trendmode         Hilbert Transform - Trend vs Cycle Mode
```

##### Math Operators
```
add                  Vector Arithmetic Add
cumsum               Cumulative Sum
div                  Vector Arithmetic Div
max                  Highest value over a specified period
maxindex             Index of highest value over a specified period
min                  Lowest value over a specified period
minindex             Index of lowest value over a specified period
minmax               Lowest and highest values over a specified period
minmaxindex          Indexes of lowest and highest values over a specified period
mult                 Vector Arithmetic Mult
sub                  Vector Arithmetic Subtraction
sum                  Summation
```

##### Math Transform
```
acos                 Vector Trigonometric ACos
asin                 Vector Trigonometric ASin
atan                 Vector Trigonometric ATan
ceil                 Vector Ceil
cos                  Vector Trigonometric Cos
cosh                 Vector Trigonometric Cosh
exp                  Vector Arithmetic Exp
floor                Vector Floor
ln                   Vector Log Natural
log10                Vector Log10
sin                  Vector Trigonometric Sin
sinh                 Vector Trigonometric Sinh
sqrt                 Vector Square Root
tan                  Vector Trigonometric Tan
tanh                 Vector Trigonometric Tanh
```

##### Momentum Indicators
```
ac                   Accelerator/Decelerator Oscillator
adx                  Average Directional Movement Index
adxr                 Average Directional Movement Index Rating
ao                   Awesome Oscillator
apo                  Absolute Price Oscillator
aroon                Aroon
aroonosc             Aroon Oscillator
bop                  Balance Of Power
cci                  Commodity Channel Index
cmo                  Chande Momentum Oscillator
cmou                 Chande Momentum Oscillator (Unsmoothed)
coppock              Coppock Curve
dpo                  Detrended Price Oscillator
dx                   Directional Movement Index
er                   Kaufman Efficiency Ratio
eri                  Elder Ray Index (Bull Power / Bear Power)
fosc                 Forecast Oscillator
fractal              Williams Fractal
imi                  Intraday Momentum Index
kdj                  KDJ Stochastic
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
qstick               Qstick
roc                  Rate of change : ((price/prevPrice)-1)*100
rocp                 Rate of change Percentage: (price-prevPrice)/prevPrice
rocr                 Rate of change ratio: (price/prevPrice)
rocr100              Rate of change ratio 100 scale: (price/prevPrice)*100
rsi                  Relative Strength Index
smi                  Stochastic Momentum Index
stoch                Stochastic
stochf               Stochastic Fast
stochrsi             Stochastic Relative Strength Index
trix                 1-day Rate-Of-Change (ROC) of a Triple Smooth EMA
tsi                  True Strength Index
ultosc               Ultimate Oscillator
vhf                  Vertical Horizontal Filter
vortex               Vortex Indicator
wad                  Williams' Accumulation/Distribution
willr                Williams' %R
```

##### Overlap Studies
```
accbands             Acceleration Bands
bbands               Bollinger Bands
dema                 Double Exponential Moving Average
donchian             Donchian Channels
ema                  Exponential Moving Average
hma                  Hull Moving Average
ht_trendline         Hilbert Transform - Instantaneous Trendline
kama                 Kaufman Adaptive Moving Average
kc                   Keltner Channels
ma                   Moving average
mama                 MESA Adaptive Moving Average
mavp                 Moving average with variable period
midpoint             MidPoint over period
midprice             Midpoint Price over period
rma                  Wilder's Smoothed Moving Average
sar                  Parabolic SAR
sarext               Parabolic SAR - Extended
sma                  Simple Moving Average
supertrend           SuperTrend
t3                   Triple Exponential Moving Average (T3)
tema                 Triple Exponential Moving Average
trima                Triangular Moving Average
vwma                 Volume Weighted Moving Average
wma                  Weighted Moving Average
zlema                Zero-Lag Exponential Moving Average
```

##### Pattern Recognition
```
cdl2crows            Two Crows
cdl3blackcrows       Three Black Crows
cdl3inside           Three Inside Up/Down
cdl3linestrike       Three-Line Strike
cdl3outside          Three Outside Up/Down
cdl3starsinsouth     Three Stars In The South
cdl3whitesoldiers    Three Advancing White Soldiers
cdlabandonedbaby     Abandoned Baby
cdladvanceblock      Advance Block
cdlbelthold          Belt-hold
cdlbreakaway         Breakaway
cdlclosingmarubozu   Closing Marubozu
cdlconcealbabyswall  Concealing Baby Swallow
cdlcounterattack     Counterattack
cdldarkcloudcover    Dark Cloud Cover
cdldoji              Doji
cdldojistar          Doji Star
cdldragonflydoji     Dragonfly Doji
cdlengulfing         Engulfing Pattern
cdleveningdojistar   Evening Doji Star
cdleveningstar       Evening Star
cdlgapsidesidewhite  Up/Down-gap side-by-side white lines
cdlgravestonedoji    Gravestone Doji
cdlhammer            Hammer
cdlhangingman        Hanging Man
cdlharami            Harami Pattern
cdlharamicross       Harami Cross Pattern
cdlhighwave          High-Wave Candle
cdlhikkake           Hikkake Pattern
cdlhikkakemod        Modified Hikkake Pattern
cdlhomingpigeon      Homing Pigeon
cdlidentical3crows   Identical Three Crows
cdlinneck            In-Neck Pattern
cdlinvertedhammer    Inverted Hammer
cdlkicking           Kicking
cdlkickingbylength   Kicking - bull/bear determined by the longer marubozu
cdlladderbottom      Ladder Bottom
cdllongleggeddoji    Long Legged Doji
cdllongline          Long Line Candle
cdlmarubozu          Marubozu
cdlmatchinglow       Matching Low
cdlmathold           Mat Hold
cdlmorningdojistar   Morning Doji Star
cdlmorningstar       Morning Star
cdlonneck            On-Neck Pattern
cdlpiercing          Piercing Pattern
cdlrickshawman       Rickshaw Man
cdlrisefall3methods  Rising/Falling Three Methods
cdlseparatinglines   Separating Lines
cdlshootingstar      Shooting Star
cdlshortline         Short Line Candle
cdlspinningtop       Spinning Top
cdlstalledpattern    Stalled Pattern
cdlsticksandwich     Stick Sandwich
cdltakuri            Takuri (Dragonfly Doji with very long lower shadow)
cdltasukigap         Tasuki Gap
cdlthrusting         Thrusting Pattern
cdltristar           Tristar Pattern
cdlunique3river      Unique 3 River
cdlupsidegap2crows   Upside Gap Two Crows
cdlxsidegap3methods  Upside/Downside Gap Three Methods
```

##### Price Transform
```
avgdev               Average Deviation
avgprice             Average Price
ha                   Heikin-Ashi Candles
medprice             Median Price
typprice             Typical Price
wclprice             Weighted Close Price
```

##### Statistic Functions
```
beta                 Beta
correl               Pearson's Correlation Coefficient (r)
linearreg            Linear Regression
linearreg_angle      Linear Regression Angle
linearreg_intercept  Linear Regression Intercept
linearreg_slope      Linear Regression Slope
percentile           Percentile (nearest rank)
percentrank          Percent Rank
stddev               Standard Deviation
tsf                  Time Series Forecast
var                  Variance
```

##### Volatility Indicators
```
adr                  Average Day Range
atr                  Average True Range
cvi                  Chaikin's Volatility
massi                Mass Index
natr                 Normalized Average True Range
rvi                  Relative Volatility Index
trange               True Range
```

##### Volume Indicators
```
ad                   Chaikin A/D Line
adosc                Chaikin A/D Oscillator
cmf                  Chaikin Money Flow
efi                  Elder's Force Index
marketfi             Market Facilitation Index
nvi                  Negative Volume Index
obv                  On Balance Volume
pvi                  Positive Volume Index
pvo                  Percentage Volume Oscillator
pvt                  Price Volume Trend
rvol                 Relative Volume
vwap                 Volume Weighted Average Price
```

## TA-Lib version

`polars_talib` 0.2.0 bundles [TA-Lib 0.8.1](https://github.com/TA-Lib/ta-lib/releases/tag/v0.8.1).
`polars_talib.__talib_version__` reports the linked version at runtime.
Results are bit-for-bit identical to the Python `ta-lib` package built against the
same TA-Lib version; the test-suite checks every function against it.

Parameter defaults follow upstream 0.8.1, which changed a few of them compared
to 0.1.x: `bbands(timeperiod=20)` (was 5), `apo`/`ppo` `matype=1` (EMA, was SMA)
and `cdldarkcloudcover`/`cdlmathold` `penetration=0.5` (was 0.3). Pass the
parameters explicitly if you relied on the old values. New MA types are
available for every `matype` parameter: `9=HMA, 10=DISABLED, 11=DEFAULT,
12=ZLEMA, 13=RMA`.

## Building from source

Requirements: Rust, Python >= 3.9, `make` + a C compiler (Linux/macOS) or
CMake >= 3.30 + MSVC (Windows). `talib-sys/build.rs` downloads the TA-Lib
source tarball from GitHub and builds a static library into
`talib-sys/dependencies` on the first build.

``` bash
uv sync                       # build the extension in release mode and install dev deps
uv run pytest                 # run the test-suite (compares against the Python ta-lib package)
uv run pytest tests/test_bench.py --benchmark-only   # micro benchmarks
```

Environment variables understood by the build script:

| variable | purpose |
|---|---|
| `DEPS_PATH` | install prefix for the bundled TA-Lib build (default `talib-sys/dependencies`) |
| `TA_LIBRARY_PATH` / `TA_INCLUDE_PATH` | use an existing TA-Lib >= 0.6 static library / headers instead of building |
| `TA_LIB_SRC_ARCHIVE` | local `ta-lib-<ver>-src.tar.gz` for offline builds |
| `TA_LIB_SRC_URL` | alternative download URL |
| `TA_LIB_BUILD_SYSTEM` | `autotools` (Unix default) or `cmake` (Windows default) |
| `TA_LIB_CFLAGS` | extra C flags (default `-O3`) |

To upgrade the bundled TA-Lib: bump `TA_LIB_VER` in `talib-sys/build.rs`, run
`cargo build -p talib-sys --features bindgen` (needs libclang) to regenerate
`talib-sys/src/bindings.rs`, then `python scripts/gen_talib_functions.py --apply`
with the matching Python `ta-lib` installed to scaffold wrappers for new functions.

## AI assistant skill

[`skills/polars-talib`](./skills/polars-talib) is an
[Agent Skill](https://agentskills.io) that teaches coding assistants how to use
this package (call styles, `.over()` pipelines, struct outputs, NaN semantics and a
full function reference). Install it with the universal installer:

``` bash
npx skills add Yvictor/polars_ta_extension        # Claude Code, Codex, Cursor, Gemini CLI, ...
```

or copy the folder manually:

| tool | location |
|---|---|
| Claude Code | `~/.claude/skills/polars-talib/` (or `.claude/skills/` in a project) |
| OpenAI Codex | `~/.codex/skills/polars-talib/` (or `.codex/skills/` in a project) |
| Cursor | `.cursor/skills/polars-talib/` in a project |
| other tools | any directory the tool scans for `SKILL.md` files |
