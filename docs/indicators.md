# Indicator catalog

Generated from the pinned TA-Lib 0.8.1 API. All 201 functions are available as
`polars_talib.<name>` and `pl.col(...).ta.<name>`. Use `inspect.signature`
for Python argument order and `get_functions_output_struct()` for Struct fields.

## Momentum Indicators

| Function | Description |
| --- | --- |
| `ac` | Accelerator/Decelerator Oscillator |
| `adx` | Average Directional Movement Index |
| `adxr` | Average Directional Movement Index Rating |
| `ao` | Awesome Oscillator |
| `apo` | Absolute Price Oscillator |
| `aroon` | Aroon |
| `aroonosc` | Aroon Oscillator |
| `bop` | Balance Of Power |
| `cci` | Commodity Channel Index |
| `cmo` | Chande Momentum Oscillator |
| `cmou` | Chande Momentum Oscillator (Unsmoothed) |
| `coppock` | Coppock Curve |
| `dpo` | Detrended Price Oscillator |
| `dx` | Directional Movement Index |
| `er` | Kaufman Efficiency Ratio |
| `eri` | Elder Ray Index (Bull Power / Bear Power) |
| `fosc` | Forecast Oscillator |
| `fractal` | Williams Fractal |
| `imi` | Intraday Momentum Index |
| `kdj` | KDJ Stochastic |
| `macd` | Moving Average Convergence/Divergence |
| `macdext` | MACD with controllable MA type |
| `macdfix` | Moving Average Convergence/Divergence Fix 12/26 |
| `mfi` | Money Flow Index |
| `minus_di` | Minus Directional Indicator |
| `minus_dm` | Minus Directional Movement |
| `mom` | Momentum |
| `plus_di` | Plus Directional Indicator |
| `plus_dm` | Plus Directional Movement |
| `ppo` | Percentage Price Oscillator |
| `qstick` | Qstick |
| `roc` | Rate of change : ((price/prevPrice)-1)*100 |
| `rocp` | Rate of change Percentage: (price-prevPrice)/prevPrice |
| `rocr` | Rate of change ratio: (price/prevPrice) |
| `rocr100` | Rate of change ratio 100 scale: (price/prevPrice)*100 |
| `rsi` | Relative Strength Index |
| `smi` | Stochastic Momentum Index |
| `stoch` | Stochastic |
| `stochf` | Stochastic Fast |
| `stochrsi` | Stochastic Relative Strength Index |
| `trix` | 1-day Rate-Of-Change (ROC) of a Triple Smooth EMA |
| `tsi` | True Strength Index |
| `ultosc` | Ultimate Oscillator |
| `vhf` | Vertical Horizontal Filter |
| `vortex` | Vortex Indicator |
| `wad` | Williams' Accumulation/Distribution |
| `willr` | Williams' %R |

## Overlap Studies

| Function | Description |
| --- | --- |
| `accbands` | Acceleration Bands |
| `bbands` | Bollinger Bands |
| `dema` | Double Exponential Moving Average |
| `donchian` | Donchian Channels |
| `ema` | Exponential Moving Average |
| `hma` | Hull Moving Average |
| `ht_trendline` | Hilbert Transform - Instantaneous Trendline |
| `kama` | Kaufman Adaptive Moving Average |
| `kc` | Keltner Channels |
| `ma` | Moving average |
| `mama` | MESA Adaptive Moving Average |
| `mavp` | Moving average with variable period |
| `midpoint` | MidPoint over period |
| `midprice` | Midpoint Price over period |
| `rma` | Wilder's Smoothed Moving Average |
| `sar` | Parabolic SAR |
| `sarext` | Parabolic SAR - Extended |
| `sma` | Simple Moving Average |
| `supertrend` | SuperTrend |
| `t3` | Triple Exponential Moving Average (T3) |
| `tema` | Triple Exponential Moving Average |
| `trima` | Triangular Moving Average |
| `vwma` | Volume Weighted Moving Average |
| `wma` | Weighted Moving Average |
| `zlema` | Zero-Lag Exponential Moving Average |

## Math Transform

| Function | Description |
| --- | --- |
| `acos` | Vector Trigonometric ACos |
| `asin` | Vector Trigonometric ASin |
| `atan` | Vector Trigonometric ATan |
| `ceil` | Vector Ceil |
| `cos` | Vector Trigonometric Cos |
| `cosh` | Vector Trigonometric Cosh |
| `exp` | Vector Arithmetic Exp |
| `floor` | Vector Floor |
| `ln` | Vector Log Natural |
| `log10` | Vector Log10 |
| `sin` | Vector Trigonometric Sin |
| `sinh` | Vector Trigonometric Sinh |
| `sqrt` | Vector Square Root |
| `tan` | Vector Trigonometric Tan |
| `tanh` | Vector Trigonometric Tanh |

## Volume Indicators

| Function | Description |
| --- | --- |
| `ad` | Chaikin A/D Line |
| `adosc` | Chaikin A/D Oscillator |
| `cmf` | Chaikin Money Flow |
| `efi` | Elder's Force Index |
| `marketfi` | Market Facilitation Index |
| `nvi` | Negative Volume Index |
| `obv` | On Balance Volume |
| `pvi` | Positive Volume Index |
| `pvo` | Percentage Volume Oscillator |
| `pvt` | Price Volume Trend |
| `rvol` | Relative Volume |
| `vwap` | Volume Weighted Average Price |

## Math Operators

| Function | Description |
| --- | --- |
| `add` | Vector Arithmetic Add |
| `cumsum` | Cumulative Sum |
| `div` | Vector Arithmetic Div |
| `max` | Highest value over a specified period |
| `maxindex` | Index of highest value over a specified period |
| `min` | Lowest value over a specified period |
| `minindex` | Index of lowest value over a specified period |
| `minmax` | Lowest and highest values over a specified period |
| `minmaxindex` | Indexes of lowest and highest values over a specified period |
| `mult` | Vector Arithmetic Mult |
| `sub` | Vector Arithmetic Subtraction |
| `sum` | Summation |

## Volatility Indicators

| Function | Description |
| --- | --- |
| `adr` | Average Day Range |
| `atr` | Average True Range |
| `cvi` | Chaikin's Volatility |
| `massi` | Mass Index |
| `natr` | Normalized Average True Range |
| `rvi` | Relative Volatility Index |
| `trange` | True Range |

## Price Transform

| Function | Description |
| --- | --- |
| `avgdev` | Average Deviation |
| `avgprice` | Average Price |
| `ha` | Heikin-Ashi Candles |
| `medprice` | Median Price |
| `typprice` | Typical Price |
| `wclprice` | Weighted Close Price |

## Statistic Functions

| Function | Description |
| --- | --- |
| `beta` | Beta |
| `correl` | Pearson's Correlation Coefficient (r) |
| `linearreg` | Linear Regression |
| `linearreg_angle` | Linear Regression Angle |
| `linearreg_intercept` | Linear Regression Intercept |
| `linearreg_slope` | Linear Regression Slope |
| `percentile` | Percentile (nearest rank) |
| `percentrank` | Percent Rank |
| `stddev` | Standard Deviation |
| `tsf` | Time Series Forecast |
| `var` | Variance |

## Pattern Recognition

| Function | Description |
| --- | --- |
| `cdl2crows` | Two Crows |
| `cdl3blackcrows` | Three Black Crows |
| `cdl3inside` | Three Inside Up/Down |
| `cdl3linestrike` | Three-Line Strike |
| `cdl3outside` | Three Outside Up/Down |
| `cdl3starsinsouth` | Three Stars In The South |
| `cdl3whitesoldiers` | Three Advancing White Soldiers |
| `cdlabandonedbaby` | Abandoned Baby |
| `cdladvanceblock` | Advance Block |
| `cdlbelthold` | Belt-hold |
| `cdlbreakaway` | Breakaway |
| `cdlclosingmarubozu` | Closing Marubozu |
| `cdlconcealbabyswall` | Concealing Baby Swallow |
| `cdlcounterattack` | Counterattack |
| `cdldarkcloudcover` | Dark Cloud Cover |
| `cdldoji` | Doji |
| `cdldojistar` | Doji Star |
| `cdldragonflydoji` | Dragonfly Doji |
| `cdlengulfing` | Engulfing Pattern |
| `cdleveningdojistar` | Evening Doji Star |
| `cdleveningstar` | Evening Star |
| `cdlgapsidesidewhite` | Up/Down-gap side-by-side white lines |
| `cdlgravestonedoji` | Gravestone Doji |
| `cdlhammer` | Hammer |
| `cdlhangingman` | Hanging Man |
| `cdlharami` | Harami Pattern |
| `cdlharamicross` | Harami Cross Pattern |
| `cdlhighwave` | High-Wave Candle |
| `cdlhikkake` | Hikkake Pattern |
| `cdlhikkakemod` | Modified Hikkake Pattern |
| `cdlhomingpigeon` | Homing Pigeon |
| `cdlidentical3crows` | Identical Three Crows |
| `cdlinneck` | In-Neck Pattern |
| `cdlinvertedhammer` | Inverted Hammer |
| `cdlkicking` | Kicking |
| `cdlkickingbylength` | Kicking - bull/bear determined by the longer marubozu |
| `cdlladderbottom` | Ladder Bottom |
| `cdllongleggeddoji` | Long Legged Doji |
| `cdllongline` | Long Line Candle |
| `cdlmarubozu` | Marubozu |
| `cdlmatchinglow` | Matching Low |
| `cdlmathold` | Mat Hold |
| `cdlmorningdojistar` | Morning Doji Star |
| `cdlmorningstar` | Morning Star |
| `cdlonneck` | On-Neck Pattern |
| `cdlpiercing` | Piercing Pattern |
| `cdlrickshawman` | Rickshaw Man |
| `cdlrisefall3methods` | Rising/Falling Three Methods |
| `cdlseparatinglines` | Separating Lines |
| `cdlshootingstar` | Shooting Star |
| `cdlshortline` | Short Line Candle |
| `cdlspinningtop` | Spinning Top |
| `cdlstalledpattern` | Stalled Pattern |
| `cdlsticksandwich` | Stick Sandwich |
| `cdltakuri` | Takuri (Dragonfly Doji with very long lower shadow) |
| `cdltasukigap` | Tasuki Gap |
| `cdlthrusting` | Thrusting Pattern |
| `cdltristar` | Tristar Pattern |
| `cdlunique3river` | Unique 3 River |
| `cdlupsidegap2crows` | Upside Gap Two Crows |
| `cdlxsidegap3methods` | Upside/Downside Gap Three Methods |

## Cycle Indicators

| Function | Description |
| --- | --- |
| `ht_dcperiod` | Hilbert Transform - Dominant Cycle Period |
| `ht_dcphase` | Hilbert Transform - Dominant Cycle Phase |
| `ht_phasor` | Hilbert Transform - Phasor Components |
| `ht_sine` | Hilbert Transform - SineWave |
| `ht_trendmode` | Hilbert Transform - Trend vs Cycle Mode |

