import pytest
import polars as pl
import polars_talib as plta
import talib
from talib import abstract


@pytest.fixture
def df_ohlc():
    _open = [float("nan"), 8688.0,] + [
        8688.0,
        8718.0,
        8840.0,
        8781.0,
        8949.0,
        9340.0,
        8951.0,
        9190.0,
        9161.0,
        9175.0,
    ] * 5
    close = [float("nan"),  8843.0,] + [
        8843.0,
        8810.0,
        8850.0,
        8829.0,
        9200.0,
        8951.0,
        9190.0,
        9115.0,
        9073.0,
        9230.0,
    ] * 5
    high = [float("nan"), float("nan")] + [
        8939.0,
        8870.0,
        9005.0,
        8870.0,
        9200.0,
        9340.0,
        9190.0,
        9195.0,
        9190.0,
        9230.0,
    ] * 5
    low = [float("nan"), float("nan")] + [
        8650.0,
        8671.0,
        8820.0,
        8711.0,
        8880.0,
        8930.0,
        8951.0,
        9066.0,
        8976.0,
        9095.0,
    ] * 5
    volume = [float("nan"), float("nan")] + [
        8650.0,
        8671.0,
        8820.0,
        8711.0,
        8880.0,
        8930.0,
        8951.0,
        9066.0,
        8976.0,
        9095.0,
    ] * 5
    close_series = pl.Series("close", close)
    high_series = pl.Series("high", high)
    low_series = pl.Series("low", low)
    open_series = pl.Series("open", _open)
    volume_series = pl.Series("volume", volume)
    return pl.DataFrame([close_series, high_series, low_series, open_series, volume_series])


def test_ema_eq(df_ohlc: pl.DataFrame):
    not_eq = df_ohlc.with_columns(
        pl.col("close").ta.ema(3).alias("ema3"),
        talib.EMA(df_ohlc["close"], timeperiod=3).alias("EMA3"),
    ).select(((pl.col("ema3") != pl.col("EMA3")).sum()).alias("not_eq"))["not_eq"][0]
    assert not_eq == 0


def test_midprice_eq(df_ohlc: pl.DataFrame):
    not_eq = df_ohlc.with_columns(
        pl.col("high").ta.midprice(pl.col("low"), 3).alias("midprice3"),
        talib.MIDPRICE(df_ohlc["high"], df_ohlc["low"], timeperiod=3).alias("MIDPRICE3"),
    ).select(((pl.col("midprice3") != pl.col("MIDPRICE3")).sum()).alias("not_eq"))["not_eq"][0]
    assert not_eq == 0


def test_sar_eq(df_ohlc: pl.DataFrame):
    not_eq = df_ohlc.with_columns(
        pl.col("high").ta.sar(pl.col("low"), acceleration=0.02, maximum=0.2).alias("expr"),
        talib.SAR(df_ohlc["high"], df_ohlc["low"], acceleration=0.02, maximum=0.2).alias("talib"),
    ).select(((pl.col("expr") != pl.col("talib")).sum()).alias("not_eq"))["not_eq"][0]
    assert not_eq == 0


def test_adx_eq(df_ohlc: pl.DataFrame):
    not_eq = df_ohlc.with_columns(
        pl.col("close").ta.adx(pl.col("high"), pl.col("low"), 3).alias("expr"),
        talib.ADX(df_ohlc["high"], df_ohlc["low"], df_ohlc["close"], timeperiod=3).alias("talib"),
    ).select(((pl.col("expr") != pl.col("talib")).sum()).alias("not_eq"))["not_eq"][0]
    assert not_eq == 0


def test_mfi_eq(df_ohlc: pl.DataFrame):
    not_eq = df_ohlc.with_columns(
        pl.col("high").ta.mfi(pl.col("low"), pl.col("close"), pl.col("volume"), 3).alias("expr"),
        talib.MFI(
            df_ohlc["high"], df_ohlc["low"], df_ohlc["close"], df_ohlc["volume"], timeperiod=3
        ).alias("talib"),
    ).select(((pl.col("expr") != pl.col("talib")).sum()).alias("not_eq"))["not_eq"][0]

    assert not_eq == 0


@pytest.mark.parametrize(
    "func",
    [
        "acos",
        "asin",
        "atan",
        "ceil",
        "cos",
        "cosh",
        "exp",
        "floor",
        "ln",
        "log10",
        "sin",
        "sinh",
        "sqrt",
        "tan",
        "tanh",
    ],
)
def test_abstract_math_transform_eq(df_ohlc: pl.DataFrame, func: str):
    not_eq = df_ohlc.with_columns(
        getattr(plta, func)().alias("expr"),
        getattr(abstract, func.upper())(df_ohlc).alias("talib"),
    ).select(((pl.col("expr") != pl.col("talib")).sum()).alias("not_eq"))["not_eq"][0]

    assert not_eq == 0


@pytest.mark.parametrize(
    "func",
    [
        "adx",
        "adxr",
        "apo",
        "aroon",
        "aroonosc",
        "bop",
        "cci",
        "cmo",
        "dx",
        "macd",
        "macdext",
        "macdfix",
        "mfi",
        "minus_di",
        "minus_dm",
        "mom",
        "plus_di",
        "plus_dm",
        "ppo",
        "roc",
        "rocp",
        "rocr",
        "rocr100",
        "rsi",
        "stoch",
        "stochf",
        "stochrsi",
        "trix",
        "ultosc",
        "willr",
    ],
)
def test_abstract_momentum_eq(df_ohlc: pl.DataFrame, func: str):
    expected = getattr(abstract, func.upper())(df_ohlc)
    if isinstance(expected, pl.Series):
        not_eq = df_ohlc.with_columns(
            getattr(plta, func)().alias("expr"),
            expected.alias("talib"),
        ).select(((pl.col("expr") != pl.col("talib")).sum()).alias("not_eq"))["not_eq"][0]
        assert not_eq == 0
    else:
        res = df_ohlc.select(getattr(plta, func)().alias("expr")).unnest("expr")
        assert res.equals(expected)


@pytest.mark.parametrize(
    "func",
    [
        "bbands",
        "dema",
        "ema",
        "ht_trendline",
        "kama",
        "ma",
        "mama",
        "mavp",
        "midpoint",
        "midprice",
        "sar",
        "sarext",
        "sma",
        "t3",
        "tema",
        "trima",
        "wma",
    ],
)
def test_abstract_overlap_eq(df_ohlc: pl.DataFrame, func: str):
    if func == "mavp":
        expected = getattr(abstract, func.upper())(
            df_ohlc.with_columns(pl.col("volume").alias("periods"))
        )
        expr = getattr(plta, func)(periods=pl.col("volume"))
    else:
        expected = getattr(abstract, func.upper())(df_ohlc)
        expr = getattr(plta, func)()
    if isinstance(expected, pl.Series):
        not_eq = df_ohlc.with_columns(
            expr.alias("expr"),
            expected.alias("talib"),
        ).select(((pl.col("expr") != pl.col("talib")).sum()).alias("not_eq"))["not_eq"][0]
        assert not_eq == 0
    else:
        res = df_ohlc.select(getattr(plta, func)().alias("expr")).unnest("expr")
        assert res.equals(expected)


@pytest.mark.parametrize(
    "func",
    [
        "cdl2crows",
        "cdl3blackcrows",
        "cdl3inside",
        "cdl3linestrike",
        "cdl3outside",
        "cdl3starsinsouth",
        "cdl3whitesoldiers",
        "cdlabandonedbaby",
        "cdladvanceblock",
        "cdlbelthold",
        "cdlbreakaway",
        "cdlclosingmarubozu",
        "cdlconcealbabyswall",
        "cdlcounterattack",
        "cdldarkcloudcover",
        "cdldoji",
        "cdldojistar",
        "cdldragonflydoji",
        "cdlengulfing",
        "cdleveningdojistar",
        "cdleveningstar",
        "cdlgapsidesidewhite",
        "cdlgravestonedoji",
        "cdlhammer",
        "cdlhangingman",
        "cdlharami",
        "cdlharamicross",
        "cdlhighwave",
        "cdlhikkake",
        "cdlhikkakemod",
        "cdlhomingpigeon",
        "cdlidentical3crows",
        "cdlinneck",
        "cdlinvertedhammer",
        "cdlkicking",
        "cdlkickingbylength",
        "cdlladderbottom",
        "cdllongleggeddoji",
        "cdllongline",
        "cdlmarubozu",
        "cdlmatchinglow",
        "cdlmathold",
        "cdlmorningdojistar",
        "cdlmorningstar",
        "cdlonneck",
        "cdlpiercing",
        "cdlrickshawman",
        "cdlrisefall3methods",
        "cdlseparatinglines",
        "cdlshootingstar",
        "cdlshortline",
        "cdlspinningtop",
        "cdlstalledpattern",
        "cdlsticksandwich",
        "cdltakuri",
        "cdltasukigap",
        "cdlthrusting",
        "cdltristar",
        "cdlunique3river",
        "cdlupsidegap2crows",
        "cdlxsidegap3methods",
    ],
)
def test_abstract_pattern_eq(df_ohlc: pl.DataFrame, func: str):
    expected = getattr(abstract, func.upper())(df_ohlc)
    expr = getattr(plta, func)()
    if isinstance(expected, pl.Series):
        not_eq = df_ohlc.with_columns(
            expr.alias("expr"),
            expected.alias("talib"),
        ).select(((pl.col("expr") != pl.col("talib")).sum()).alias("not_eq"))["not_eq"][0]
        assert not_eq == 0
    else:
        res = df_ohlc.select(getattr(plta, func)().alias("expr")).unnest("expr")
        assert res.equals(expected)


@pytest.mark.parametrize(
    "func",
    [
        "beta",
        "correl",
        "linearreg",
        "linearreg_angle",
        "linearreg_intercept",
        "linearreg_slope",
        "stddev",
        "tsf",
        "var",
    ],
)
def test_abstract_statistic_eq(df_ohlc: pl.DataFrame, func: str):
    expected = getattr(abstract, func.upper())(df_ohlc)
    expr = getattr(plta, func)()
    if isinstance(expected, pl.Series):
        not_eq = df_ohlc.with_columns(
            expr.alias("expr"),
            expected.alias("talib"),
        ).select(((pl.col("expr") != pl.col("talib")).sum()).alias("not_eq"))["not_eq"][0]
        assert not_eq == 0
    else:
        res = df_ohlc.select(getattr(plta, func)().alias("expr")).unnest("expr")
        assert res.equals(expected)


@pytest.mark.parametrize("func", ["avgprice", "medprice", "typprice", "wclprice"])
def test_abstract_price_transform_eq(df_ohlc: pl.DataFrame, func: str):
    expected = getattr(abstract, func.upper())(df_ohlc)
    expr = getattr(plta, func)()
    if isinstance(expected, pl.Series):
        not_eq = df_ohlc.with_columns(
            expr.alias("expr"),
            expected.alias("talib"),
        ).select(((pl.col("expr") != pl.col("talib")).sum()).alias("not_eq"))["not_eq"][0]
        assert not_eq == 0
    else:
        res = df_ohlc.select(getattr(plta, func)().alias("expr")).unnest("expr")
        assert res.equals(expected)


@pytest.mark.parametrize(
    "func",
    ["atr", "natr", "trange"],
)
def test_abstract_volatility_eq(df_ohlc: pl.DataFrame, func: str):
    expected = getattr(abstract, func.upper())(df_ohlc)
    expr = getattr(plta, func)()
    if isinstance(expected, pl.Series):
        not_eq = df_ohlc.with_columns(
            expr.alias("expr"),
            expected.alias("talib"),
        ).select(((pl.col("expr") != pl.col("talib")).sum()).alias("not_eq"))["not_eq"][0]
        assert not_eq == 0
    else:
        res = df_ohlc.select(getattr(plta, func)().alias("expr")).unnest("expr")
        assert res.equals(expected)


@pytest.mark.parametrize(
    "func",
    ["ad", "adosc", "obv"],
)
def test_abstract_volume_eq(df_ohlc: pl.DataFrame, func: str):
    expected = getattr(abstract, func.upper())(df_ohlc)
    expr = getattr(plta, func)()
    if isinstance(expected, pl.Series):
        not_eq = df_ohlc.with_columns(
            expr.alias("expr"),
            expected.alias("talib"),
        ).select(((pl.col("expr") != pl.col("talib")).sum()).alias("not_eq"))["not_eq"][0]
        assert not_eq == 0
    else:
        res = df_ohlc.select(getattr(plta, func)().alias("expr")).unnest("expr")
        assert res.equals(expected)
