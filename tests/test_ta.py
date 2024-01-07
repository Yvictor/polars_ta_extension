import pytest
import polars as pl
import polars_ta as plta
import talib
from talib import abstract


@pytest.fixture
def df_ohlc():
    _open = [8688.0, 8718.0, 8840.0, 8781.0, 8949.0, 9340.0, 8951.0, 9190.0, 9161.0, 9175.0] * 5
    close = [8843.0, 8810.0, 8850.0, 8829.0, 9200.0, 8951.0, 9190.0, 9115.0, 9073.0, 9230.0] * 5
    high = [8939.0, 8870.0, 9005.0, 8870.0, 9200.0, 9340.0, 9190.0, 9195.0, 9190.0, 9230.0] * 5
    low = [8650.0, 8671.0, 8820.0, 8711.0, 8880.0, 8930.0, 8951.0, 9066.0, 8976.0, 9095.0] * 5
    volume = [8650.0, 8671.0, 8820.0, 8711.0, 8880.0, 8930.0, 8951.0, 9066.0, 8976.0, 9095.0] * 5
    close_series = pl.Series("close", close)
    high_series = pl.Series("high", high)
    low_series = pl.Series("low", low)
    open_series = pl.Series("open", _open)
    volume_series = pl.Series("volume", volume)
    return pl.DataFrame([close_series, high_series, low_series, open_series, volume_series])


def test_version():
    assert plta.__talib_version__[:5] == "0.4.0"


def test_ta_has_impl():
    for fn in talib.get_functions():
        assert hasattr(plta, fn.lower())


def test_get_functions():
    for plfn, fn in zip(plta.get_functions(), talib.get_functions()):
        assert plfn == fn.lower()


def test_get_function_groups():
    for pl_g, g in zip(plta.get_function_groups(), talib.get_function_groups()):
        assert pl_g == g
        for plfn, fn in zip(plta.get_function_groups()[pl_g], talib.get_function_groups()[g]):
            assert plfn == fn.lower()


def test_abstract_ht_dcperiod_eq(df_ohlc: pl.DataFrame):
    not_eq = df_ohlc.with_columns(
        plta.ht_dcperiod().alias("expr"),
        abstract.HT_DCPERIOD(df_ohlc).alias("talib"),
    ).select(((pl.col("expr") != pl.col("talib")).sum()).alias("not_eq"))["not_eq"][0]
    assert not_eq == 0


def test_abstract_ht_dcphase_eq(df_ohlc: pl.DataFrame):
    not_eq = df_ohlc.with_columns(
        plta.ht_dcphase().alias("expr"),
        abstract.HT_DCPHASE(df_ohlc).alias("talib"),
    ).select(((pl.col("expr") != pl.col("talib")).sum()).alias("not_eq"))["not_eq"][0]
    assert not_eq == 0


def test_abstract_ht_phasor_eq(df_ohlc: pl.DataFrame):
    not_eq = df_ohlc.with_columns(
        plta.ht_phasor().struct.field("inphase").alias("expr"),
        abstract.HT_PHASOR(df_ohlc)["inphase"].alias("talib"),
    ).select(((pl.col("expr") != pl.col("talib")).sum()).alias("not_eq"))["not_eq"][0]

    assert not_eq == 0

    not_eq = df_ohlc.with_columns(
        plta.ht_phasor().struct.field("quadrature").alias("expr"),
        abstract.HT_PHASOR(df_ohlc)["quadrature"].alias("talib"),
    ).select(((pl.col("expr") != pl.col("talib")).sum()).alias("not_eq"))["not_eq"][0]

    assert not_eq == 0


def test_abstract_ht_sine_eq(df_ohlc: pl.DataFrame):
    not_eq = df_ohlc.with_columns(
        plta.ht_sine().struct.field("sine").alias("expr"),
        abstract.HT_SINE(df_ohlc)["sine"].alias("talib"),
    ).select(((pl.col("expr") != pl.col("talib")).sum()).alias("not_eq"))["not_eq"][0]

    assert not_eq == 0

    not_eq = df_ohlc.with_columns(
        plta.ht_sine().struct.field("leadsine").alias("expr"),
        abstract.HT_SINE(df_ohlc)["leadsine"].alias("talib"),
    ).select(((pl.col("expr") != pl.col("talib")).sum()).alias("not_eq"))["not_eq"][0]

    assert not_eq == 0


def test_abstract_ht_trendmode_eq(df_ohlc: pl.DataFrame):
    not_eq = df_ohlc.with_columns(
        plta.ht_trendmode().alias("expr"),
        abstract.HT_TRENDMODE(df_ohlc).alias("talib"),
    ).select(((pl.col("expr") != pl.col("talib")).sum()).alias("not_eq"))["not_eq"][0]

    assert not_eq == 0


def test_abstract_add_eq(df_ohlc: pl.DataFrame):
    not_eq = df_ohlc.with_columns(
        plta.add().alias("expr"),
        abstract.ADD(df_ohlc).alias("talib"),
    ).select(((pl.col("expr") != pl.col("talib")).sum()).alias("not_eq"))["not_eq"][0]

    assert not_eq == 0


def test_abstract_div_eq(df_ohlc: pl.DataFrame):
    not_eq = df_ohlc.with_columns(
        plta.div().alias("expr"),
        abstract.DIV(df_ohlc).alias("talib"),
    ).select(((pl.col("expr") != pl.col("talib")).sum()).alias("not_eq"))["not_eq"][0]

    assert not_eq == 0


def test_abstract_max_eq(df_ohlc: pl.DataFrame):
    not_eq = df_ohlc.with_columns(
        plta.max().alias("expr"),
        abstract.MAX(df_ohlc).alias("talib"),
    ).select(((pl.col("expr") != pl.col("talib")).sum()).alias("not_eq"))["not_eq"][0]

    assert not_eq == 0


def test_abstract_maxindex_eq(df_ohlc: pl.DataFrame):
    not_eq = df_ohlc.with_columns(
        plta.maxindex().alias("expr"),
        abstract.MAXINDEX(df_ohlc).alias("talib"),
    ).select(((pl.col("expr") != pl.col("talib")).sum()).alias("not_eq"))["not_eq"][0]

    assert not_eq == 0


def test_abstract_min_eq(df_ohlc: pl.DataFrame):
    not_eq = df_ohlc.with_columns(
        plta.min().alias("expr"),
        abstract.MIN(df_ohlc).alias("talib"),
    ).select(((pl.col("expr") != pl.col("talib")).sum()).alias("not_eq"))["not_eq"][0]

    assert not_eq == 0


def test_abstract_minindex_eq(df_ohlc: pl.DataFrame):
    not_eq = df_ohlc.with_columns(
        plta.minindex().alias("expr"),
        abstract.MININDEX(df_ohlc).alias("talib"),
    ).select(((pl.col("expr") != pl.col("talib")).sum()).alias("not_eq"))["not_eq"][0]

    assert not_eq == 0


def test_abstract_minmax_eq(df_ohlc: pl.DataFrame):
    not_eq = df_ohlc.with_columns(
        plta.minmax().struct.field("min").alias("expr"),
        abstract.MINMAX(df_ohlc)["min"].alias("talib"),
    ).select(((pl.col("expr") != pl.col("talib")).sum()).alias("not_eq"))["not_eq"][0]

    assert not_eq == 0

    not_eq = df_ohlc.with_columns(
        plta.minmax().struct.field("max").alias("expr"),
        abstract.MINMAX(df_ohlc)["max"].alias("talib"),
    ).select(((pl.col("expr") != pl.col("talib")).sum()).alias("not_eq"))["not_eq"][0]

    assert not_eq == 0


def test_abstract_minmaxindex_eq(df_ohlc: pl.DataFrame):
    not_eq = df_ohlc.with_columns(
        plta.minmaxindex().struct.field("minidx").alias("expr"),
        abstract.MINMAXINDEX(df_ohlc)["minidx"].alias("talib"),
    ).select(((pl.col("expr") != pl.col("talib")).sum()).alias("not_eq"))["not_eq"][0]

    assert not_eq == 0

    not_eq = df_ohlc.with_columns(
        plta.minmaxindex().struct.field("maxidx").alias("expr"),
        abstract.MINMAXINDEX(df_ohlc)["maxidx"].alias("talib"),
    ).select(((pl.col("expr") != pl.col("talib")).sum()).alias("not_eq"))["not_eq"][0]

    assert not_eq == 0


def test_abstract_mult_eq(df_ohlc: pl.DataFrame):
    not_eq = df_ohlc.with_columns(
        plta.mult().alias("expr"),
        abstract.MULT(df_ohlc).alias("talib"),
    ).select(((pl.col("expr") != pl.col("talib")).sum()).alias("not_eq"))["not_eq"][0]

    assert not_eq == 0


def test_abstract_sub_eq(df_ohlc: pl.DataFrame):
    not_eq = df_ohlc.with_columns(
        plta.sub().alias("expr"),
        abstract.SUB(df_ohlc).alias("talib"),
    ).select(((pl.col("expr") != pl.col("talib")).sum()).alias("not_eq"))["not_eq"][0]

    assert not_eq == 0


def test_abstract_sum_eq(df_ohlc: pl.DataFrame):
    not_eq = df_ohlc.with_columns(
        plta.sum().alias("expr"),
        abstract.SUM(df_ohlc).alias("talib"),
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


def test_ht_dcperiod_eq(df_ohlc: pl.DataFrame):
    not_eq = df_ohlc.with_columns(
        pl.col("close").ta.ht_dcperiod().alias("expr"),
        talib.HT_DCPERIOD(df_ohlc["close"]).alias("talib"),
    ).select(((pl.col("expr") != pl.col("talib")).sum()).alias("not_eq"))["not_eq"][0]
    assert not_eq == 0


def test_ht_dcphase_eq(df_ohlc: pl.DataFrame):
    not_eq = df_ohlc.with_columns(
        pl.col("close").ta.ht_dcphase().alias("expr"),
        talib.HT_DCPHASE(df_ohlc["close"]).alias("talib"),
    ).select(((pl.col("expr") != pl.col("talib")).sum()).alias("not_eq"))["not_eq"][0]
    assert not_eq == 0


def test_ht_phasor_eq(df_ohlc: pl.DataFrame):
    not_eq = df_ohlc.with_columns(
        pl.col("close").ta.ht_phasor().struct.field("inphase").alias("expr"),
        talib.HT_PHASOR(df_ohlc["close"])[0].alias("talib"),
    ).select(((pl.col("expr") != pl.col("talib")).sum()).alias("not_eq"))["not_eq"][0]

    assert not_eq == 0

    not_eq = df_ohlc.with_columns(
        pl.col("close").ta.ht_phasor().struct.field("quadrature").alias("expr"),
        talib.HT_PHASOR(df_ohlc["close"])[1].alias("talib"),
    ).select(((pl.col("expr") != pl.col("talib")).sum()).alias("not_eq"))["not_eq"][0]

    assert not_eq == 0


def test_ht_sine_eq(df_ohlc: pl.DataFrame):
    not_eq = df_ohlc.with_columns(
        pl.col("close").ta.ht_sine().struct.field("sine").alias("expr"),
        talib.HT_SINE(df_ohlc["close"])[0].alias("talib"),
    ).select(((pl.col("expr") != pl.col("talib")).sum()).alias("not_eq"))["not_eq"][0]

    assert not_eq == 0

    not_eq = df_ohlc.with_columns(
        pl.col("close").ta.ht_sine().struct.field("leadsine").alias("expr"),
        talib.HT_SINE(df_ohlc["close"])[1].alias("talib"),
    ).select(((pl.col("expr") != pl.col("talib")).sum()).alias("not_eq"))["not_eq"][0]

    assert not_eq == 0


def test_ht_trendmode_eq(df_ohlc: pl.DataFrame):
    not_eq = df_ohlc.with_columns(
        pl.col("close").ta.ht_trendmode().alias("expr"),
        talib.HT_TRENDMODE(df_ohlc["close"]).alias("talib"),
    ).select(((pl.col("expr") != pl.col("talib")).sum()).alias("not_eq"))["not_eq"][0]

    assert not_eq == 0


def test_add_eq(df_ohlc: pl.DataFrame):
    not_eq = df_ohlc.with_columns(
        pl.col("close").ta.add(pl.col("open")).alias("expr"),
        talib.ADD(df_ohlc["close"], df_ohlc["open"]).alias("talib"),
    ).select(((pl.col("expr") != pl.col("talib")).sum()).alias("not_eq"))["not_eq"][0]
    assert not_eq == 0


def test_div_eq(df_ohlc: pl.DataFrame):
    not_eq = df_ohlc.with_columns(
        pl.col("close").ta.div(pl.col("open")).alias("expr"),
        talib.DIV(df_ohlc["close"], df_ohlc["open"]).alias("talib"),
    ).select(((pl.col("expr") != pl.col("talib")).sum()).alias("not_eq"))["not_eq"][0]
    assert not_eq == 0


def test_max_eq(df_ohlc: pl.DataFrame):
    not_eq = df_ohlc.with_columns(
        pl.col("close").ta.max(timeperiod=30).alias("expr"),
        talib.MAX(df_ohlc["close"], timeperiod=30).alias("talib"),
    ).select(((pl.col("expr") != pl.col("talib")).sum()).alias("not_eq"))["not_eq"][0]
    assert not_eq == 0


def test_maxindex_eq(df_ohlc: pl.DataFrame):
    not_eq = df_ohlc.with_columns(
        pl.col("close").ta.maxindex(timeperiod=30).alias("expr"),
        talib.MAXINDEX(df_ohlc["close"], timeperiod=30).alias("talib"),
    ).select(((pl.col("expr") != pl.col("talib")).sum()).alias("not_eq"))["not_eq"][0]
    assert not_eq == 0


def test_min_eq(df_ohlc: pl.DataFrame):
    not_eq = df_ohlc.with_columns(
        pl.col("close").ta.min(timeperiod=30).alias("expr"),
        talib.MIN(df_ohlc["close"], timeperiod=30).alias("talib"),
    ).select(((pl.col("expr") != pl.col("talib")).sum()).alias("not_eq"))["not_eq"][0]
    assert not_eq == 0


def test_minindex_eq(df_ohlc: pl.DataFrame):
    not_eq = df_ohlc.with_columns(
        pl.col("close").ta.minindex(timeperiod=30).alias("expr"),
        talib.MININDEX(df_ohlc["close"], timeperiod=30).alias("talib"),
    ).select(((pl.col("expr") != pl.col("talib")).sum()).alias("not_eq"))["not_eq"][0]
    assert not_eq == 0


def test_minmax_eq(df_ohlc: pl.DataFrame):
    not_eq = df_ohlc.with_columns(
        pl.col("close").ta.minmax(timeperiod=30).struct.field("min").alias("expr"),
        talib.MINMAX(df_ohlc["close"], timeperiod=30)[0].alias("talib"),
    ).select(((pl.col("expr") != pl.col("talib")).sum()).alias("not_eq"))["not_eq"][0]

    assert not_eq == 0

    not_eq = df_ohlc.with_columns(
        pl.col("close").ta.minmax(timeperiod=30).struct.field("max").alias("expr"),
        talib.MINMAX(df_ohlc["close"], timeperiod=30)[1].alias("talib"),
    ).select(((pl.col("expr") != pl.col("talib")).sum()).alias("not_eq"))["not_eq"][0]

    assert not_eq == 0


def test_minmaxindex_eq(df_ohlc: pl.DataFrame):
    not_eq = df_ohlc.with_columns(
        pl.col("close").ta.minmaxindex(timeperiod=30).struct.field("minidx").alias("expr"),
        talib.MINMAXINDEX(df_ohlc["close"], timeperiod=30)[0].alias("talib"),
    ).select(((pl.col("expr") != pl.col("talib")).sum()).alias("not_eq"))["not_eq"][0]

    assert not_eq == 0

    not_eq = df_ohlc.with_columns(
        pl.col("close").ta.minmaxindex(timeperiod=30).struct.field("maxidx").alias("expr"),
        talib.MINMAXINDEX(df_ohlc["close"], timeperiod=30)[1].alias("talib"),
    ).select(((pl.col("expr") != pl.col("talib")).sum()).alias("not_eq"))["not_eq"][0]

    assert not_eq == 0


def test_mult_eq(df_ohlc: pl.DataFrame):
    not_eq = df_ohlc.with_columns(
        pl.col("close").ta.mult(pl.col("open")).alias("expr"),
        talib.MULT(df_ohlc["close"], df_ohlc["open"]).alias("talib"),
    ).select(((pl.col("expr") != pl.col("talib")).sum()).alias("not_eq"))["not_eq"][0]
    assert not_eq == 0


def test_sub_eq(df_ohlc: pl.DataFrame):
    not_eq = df_ohlc.with_columns(
        pl.col("close").ta.sub(pl.col("open")).alias("expr"),
        talib.SUB(df_ohlc["close"], df_ohlc["open"]).alias("talib"),
    ).select(((pl.col("expr") != pl.col("talib")).sum()).alias("not_eq"))["not_eq"][0]
    assert not_eq == 0


def test_sum_eq(df_ohlc: pl.DataFrame):
    not_eq = df_ohlc.with_columns(
        pl.col("close").ta.sum(timeperiod=30).alias("expr"),
        talib.SUM(df_ohlc["close"], timeperiod=30).alias("talib"),
    ).select(((pl.col("expr") != pl.col("talib")).sum()).alias("not_eq"))["not_eq"][0]
    assert not_eq == 0


def test_acos_eq(df_ohlc: pl.DataFrame):
    not_eq = df_ohlc.with_columns(
        pl.col("close").ta.acos().alias("expr"),
        talib.ACOS(df_ohlc["close"]).alias("talib"),
    ).select(((pl.col("expr") != pl.col("talib")).sum()).alias("not_eq"))["not_eq"][0]

    assert not_eq == 0


def test_asin_eq(df_ohlc: pl.DataFrame):
    not_eq = df_ohlc.with_columns(
        pl.col("close").ta.asin().alias("expr"),
        talib.ASIN(df_ohlc["close"]).alias("talib"),
    ).select(((pl.col("expr") != pl.col("talib")).sum()).alias("not_eq"))["not_eq"][0]

    assert not_eq == 0


def test_atan_eq(df_ohlc: pl.DataFrame):
    not_eq = df_ohlc.with_columns(
        pl.col("close").ta.atan().alias("expr"),
        talib.ATAN(df_ohlc["close"]).alias("talib"),
    ).select(((pl.col("expr") != pl.col("talib")).sum()).alias("not_eq"))["not_eq"][0]

    assert not_eq == 0


def test_ceil_eq(df_ohlc: pl.DataFrame):
    not_eq = df_ohlc.with_columns(
        pl.col("close").ta.ceil().alias("expr"),
        talib.CEIL(df_ohlc["close"]).alias("talib"),
    ).select(((pl.col("expr") != pl.col("talib")).sum()).alias("not_eq"))["not_eq"][0]

    assert not_eq == 0


def test_cos_eq(df_ohlc: pl.DataFrame):
    not_eq = df_ohlc.with_columns(
        pl.col("close").ta.cos().alias("expr"),
        talib.COS(df_ohlc["close"]).alias("talib"),
    ).select(((pl.col("expr") != pl.col("talib")).sum()).alias("not_eq"))["not_eq"][0]

    assert not_eq == 0


def test_cosh_eq(df_ohlc: pl.DataFrame):
    not_eq = df_ohlc.with_columns(
        pl.col("close").ta.cosh().alias("expr"),
        talib.COSH(df_ohlc["close"]).alias("talib"),
    ).select(((pl.col("expr") != pl.col("talib")).sum()).alias("not_eq"))["not_eq"][0]

    assert not_eq == 0


def test_exp_eq(df_ohlc: pl.DataFrame):
    not_eq = df_ohlc.with_columns(
        pl.col("close").ta.exp().alias("expr"),
        talib.EXP(df_ohlc["close"]).alias("talib"),
    ).select(((pl.col("expr") != pl.col("talib")).sum()).alias("not_eq"))["not_eq"][0]

    assert not_eq == 0


def test_floor_eq(df_ohlc: pl.DataFrame):
    not_eq = df_ohlc.with_columns(
        pl.col("close").ta.floor().alias("expr"),
        talib.FLOOR(df_ohlc["close"]).alias("talib"),
    ).select(((pl.col("expr") != pl.col("talib")).sum()).alias("not_eq"))["not_eq"][0]

    assert not_eq == 0


def test_ln_eq(df_ohlc: pl.DataFrame):
    not_eq = df_ohlc.with_columns(
        pl.col("close").ta.ln().alias("expr"),
        talib.LN(df_ohlc["close"]).alias("talib"),
    ).select(((pl.col("expr") != pl.col("talib")).sum()).alias("not_eq"))["not_eq"][0]

    assert not_eq == 0


def test_log10_eq(df_ohlc: pl.DataFrame):
    not_eq = df_ohlc.with_columns(
        pl.col("close").ta.log10().alias("expr"),
        talib.LOG10(df_ohlc["close"]).alias("talib"),
    ).select(((pl.col("expr") != pl.col("talib")).sum()).alias("not_eq"))["not_eq"][0]

    assert not_eq == 0


def test_sin_eq(df_ohlc: pl.DataFrame):
    not_eq = df_ohlc.with_columns(
        pl.col("close").ta.sin().alias("expr"),
        talib.SIN(df_ohlc["close"]).alias("talib"),
    ).select(((pl.col("expr") != pl.col("talib")).sum()).alias("not_eq"))["not_eq"][0]

    assert not_eq == 0


def test_sinh_eq(df_ohlc: pl.DataFrame):
    not_eq = df_ohlc.with_columns(
        pl.col("close").ta.sinh().alias("expr"),
        talib.SINH(df_ohlc["close"]).alias("talib"),
    ).select(((pl.col("expr") != pl.col("talib")).sum()).alias("not_eq"))["not_eq"][0]

    assert not_eq == 0


def test_sqrt_eq(df_ohlc: pl.DataFrame):
    not_eq = df_ohlc.with_columns(
        pl.col("close").ta.sqrt().alias("expr"),
        talib.SQRT(df_ohlc["close"]).alias("talib"),
    ).select(((pl.col("expr") != pl.col("talib")).sum()).alias("not_eq"))["not_eq"][0]

    assert not_eq == 0


def test_tan_eq(df_ohlc: pl.DataFrame):
    not_eq = df_ohlc.with_columns(
        pl.col("close").ta.tan().alias("expr"),
        talib.TAN(df_ohlc["close"]).alias("talib"),
    ).select(((pl.col("expr") != pl.col("talib")).sum()).alias("not_eq"))["not_eq"][0]

    assert not_eq == 0


def test_tanh_eq(df_ohlc: pl.DataFrame):
    not_eq = df_ohlc.with_columns(
        pl.col("close").ta.tanh().alias("expr"),
        talib.TANH(df_ohlc["close"]).alias("talib"),
    ).select(((pl.col("expr") != pl.col("talib")).sum()).alias("not_eq"))["not_eq"][0]

    assert not_eq == 0


def test_adx_eq(df_ohlc: pl.DataFrame):
    not_eq = df_ohlc.with_columns(
        pl.col("close").ta.adx(pl.col("high"), pl.col("low"), 3).alias("expr"),
        talib.ADX(df_ohlc["high"], df_ohlc["low"], df_ohlc["close"], timeperiod=3).alias("talib"),
    ).select(((pl.col("expr") != pl.col("talib")).sum()).alias("not_eq"))["not_eq"][0]
    assert not_eq == 0


def test_adxr_eq(df_ohlc: pl.DataFrame):
    not_eq = df_ohlc.with_columns(
        pl.col("close").ta.adxr(pl.col("high"), pl.col("low"), 3).alias("expr"),
        talib.ADXR(df_ohlc["high"], df_ohlc["low"], df_ohlc["close"], timeperiod=3).alias("talib"),
    ).select(((pl.col("expr") != pl.col("talib")).sum()).alias("not_eq"))["not_eq"][0]

    assert not_eq == 0


def test_apo_eq(df_ohlc: pl.DataFrame):
    not_eq = df_ohlc.with_columns(
        pl.col("close").ta.apo(3, 10, 0).alias("apo3"),
        talib.APO(df_ohlc["close"], fastperiod=3, slowperiod=10, matype=0).alias("APO3"),
    ).select(((pl.col("apo3") != pl.col("APO3")).sum()).alias("not_eq"))["not_eq"][0]
    assert not_eq == 0


def test_aroon_eq(df_ohlc: pl.DataFrame):
    not_eq = df_ohlc.with_columns(
        pl.col("high").ta.aroon(pl.col("low"), 3).struct.field("aroondown").alias("expr"),
        talib.AROON(df_ohlc["high"], df_ohlc["low"], timeperiod=3)[0].alias("talib"),
    ).select(((pl.col("expr") != pl.col("talib")).sum()).alias("not_eq"))["not_eq"][0]
    assert not_eq == 0

    not_eq = df_ohlc.with_columns(
        pl.col("high").ta.aroon(pl.col("low"), 3).struct.field("aroonup").alias("expr"),
        talib.AROON(df_ohlc["high"], df_ohlc["low"], timeperiod=3)[1].alias("talib"),
    ).select(((pl.col("expr") != pl.col("talib")).sum()).alias("not_eq"))["not_eq"][0]
    assert not_eq == 0


def test_aroonosc_eq(df_ohlc: pl.DataFrame):
    not_eq = df_ohlc.with_columns(
        pl.col("high").ta.aroonosc(pl.col("low"), 3).alias("expr"),
        talib.AROONOSC(df_ohlc["high"], df_ohlc["low"], timeperiod=3).alias("talib"),
    ).select(((pl.col("expr") != pl.col("talib")).sum()).alias("not_eq"))["not_eq"][0]

    assert not_eq == 0


def test_bop_eq(df_ohlc: pl.DataFrame):
    not_eq = df_ohlc.with_columns(
        pl.col("open").ta.bop(pl.col("high"), pl.col("low"), pl.col("close")).alias("expr"),
        talib.BOP(df_ohlc["open"], df_ohlc["high"], df_ohlc["low"], df_ohlc["close"]).alias(
            "talib"
        ),
    ).select(((pl.col("expr") != pl.col("talib")).sum()).alias("not_eq"))["not_eq"][0]

    assert not_eq == 0


def test_cci_eq(df_ohlc: pl.DataFrame):
    not_eq = df_ohlc.with_columns(
        pl.col("high").ta.cci(pl.col("low"), pl.col("close"), 3).alias("expr"),
        talib.CCI(df_ohlc["high"], df_ohlc["low"], df_ohlc["close"], timeperiod=3).alias("talib"),
    ).select(((pl.col("expr") != pl.col("talib")).sum()).alias("not_eq"))["not_eq"][0]

    assert not_eq == 0


def test_cmo_eq(df_ohlc: pl.DataFrame):
    not_eq = df_ohlc.with_columns(
        pl.col("close").ta.cmo(3).alias("cmo3"),
        talib.CMO(df_ohlc["close"], timeperiod=3).alias("CMO3"),
    ).select(((pl.col("cmo3") != pl.col("CMO3")).sum()).alias("not_eq"))["not_eq"][0]
    assert not_eq == 0


def test_dx_eq(df_ohlc: pl.DataFrame):
    not_eq = df_ohlc.with_columns(
        pl.col("close").ta.dx(pl.col("high"), pl.col("low"), 3).alias("expr"),
        talib.DX(df_ohlc["high"], df_ohlc["low"], df_ohlc["close"], timeperiod=3).alias("talib"),
    ).select(((pl.col("expr") != pl.col("talib")).sum()).alias("not_eq"))["not_eq"][0]

    assert not_eq == 0


def test_macd_eq(df_ohlc: pl.DataFrame):
    not_eq = df_ohlc.with_columns(
        pl.col("close").ta.macd(3, 10, 16).struct.field("macd").alias("expr"),
        talib.MACD(df_ohlc["close"], fastperiod=3, slowperiod=10, signalperiod=16)[0].alias(
            "talib"
        ),
    ).select(((pl.col("expr") != pl.col("talib")).sum()).alias("not_eq"))["not_eq"][0]

    assert not_eq == 0

    not_eq = df_ohlc.with_columns(
        pl.col("close").ta.macd(3, 10, 16).struct.field("macdsignal").alias("expr"),
        talib.MACD(df_ohlc["close"], fastperiod=3, slowperiod=10, signalperiod=16)[1].alias(
            "talib"
        ),
    ).select(((pl.col("expr") != pl.col("talib")).sum()).alias("not_eq"))["not_eq"][0]

    assert not_eq == 0

    not_eq = df_ohlc.with_columns(
        pl.col("close").ta.macd(3, 10, 16).struct.field("macdhist").alias("expr"),
        talib.MACD(df_ohlc["close"], fastperiod=3, slowperiod=10, signalperiod=16)[2].alias(
            "talib"
        ),
    ).select(((pl.col("expr") != pl.col("talib")).sum()).alias("not_eq"))["not_eq"][0]

    assert not_eq == 0


def test_macdext_eq(df_ohlc: pl.DataFrame):
    not_eq = df_ohlc.with_columns(
        pl.col("close")
        .ta.macdext(
            3,
            10,
            16,
            fastmatype=0,
            slowmatype=0,
            signalmatype=0,
        )
        .struct.field("macd")
        .alias("expr"),
        talib.MACDEXT(
            df_ohlc["close"],
            fastperiod=3,
            fastmatype=0,
            slowperiod=10,
            slowmatype=0,
            signalperiod=16,
            signalmatype=0,
        )[0].alias("talib"),
    ).select(((pl.col("expr") != pl.col("talib")).sum()).alias("not_eq"))["not_eq"][0]

    assert not_eq == 0

    not_eq = df_ohlc.with_columns(
        pl.col("close")
        .ta.macdext(
            3,
            10,
            16,
            fastmatype=0,
            slowmatype=0,
            signalmatype=0,
        )
        .struct.field("macdsignal")
        .alias("expr"),
        talib.MACDEXT(
            df_ohlc["close"],
            fastperiod=3,
            fastmatype=0,
            slowperiod=10,
            slowmatype=0,
            signalperiod=16,
            signalmatype=0,
        )[1].alias("talib"),
    ).select(((pl.col("expr") != pl.col("talib")).sum()).alias("not_eq"))["not_eq"][0]

    assert not_eq == 0

    not_eq = df_ohlc.with_columns(
        pl.col("close")
        .ta.macdext(
            3,
            10,
            16,
            fastmatype=0,
            slowmatype=0,
            signalmatype=0,
        )
        .struct.field("macdhist")
        .alias("expr"),
        talib.MACDEXT(
            df_ohlc["close"],
            fastperiod=3,
            fastmatype=0,
            slowperiod=10,
            slowmatype=0,
            signalperiod=16,
            signalmatype=0,
        )[2].alias("talib"),
    ).select(((pl.col("expr") != pl.col("talib")).sum()).alias("not_eq"))["not_eq"][0]
    assert not_eq == 0


def test_macdfix_eq(df_ohlc: pl.DataFrame):
    not_eq = df_ohlc.with_columns(
        pl.col("close").ta.macdfix(3).struct.field("macd").alias("expr"),
        talib.MACDFIX(df_ohlc["close"], signalperiod=3)[0].alias("talib"),
    ).select(((pl.col("expr") != pl.col("talib")).sum()).alias("not_eq"))["not_eq"][0]

    assert not_eq == 0

    not_eq = df_ohlc.with_columns(
        pl.col("close").ta.macdfix(3).struct.field("macdsignal").alias("expr"),
        talib.MACDFIX(df_ohlc["close"], signalperiod=3)[1].alias("talib"),
    ).select(((pl.col("expr") != pl.col("talib")).sum()).alias("not_eq"))["not_eq"][0]

    assert not_eq == 0

    not_eq = df_ohlc.with_columns(
        pl.col("close").ta.macdfix(3).struct.field("macdhist").alias("expr"),
        talib.MACDFIX(df_ohlc["close"], signalperiod=3)[2].alias("talib"),
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


def test_minus_di_eq(df_ohlc: pl.DataFrame):
    not_eq = df_ohlc.with_columns(
        pl.col("close").ta.minus_di(pl.col("high"), pl.col("low"), 3).alias("expr"),
        talib.MINUS_DI(df_ohlc["high"], df_ohlc["low"], df_ohlc["close"], timeperiod=3).alias(
            "talib"
        ),
    ).select(((pl.col("expr") != pl.col("talib")).sum()).alias("not_eq"))["not_eq"][0]

    assert not_eq == 0


def test_minus_dm_eq(df_ohlc: pl.DataFrame):
    not_eq = df_ohlc.with_columns(
        pl.col("high").ta.minus_dm(pl.col("low"), 3).alias("expr"),
        talib.MINUS_DM(df_ohlc["high"], df_ohlc["low"], timeperiod=3).alias("talib"),
    ).select(((pl.col("expr") != pl.col("talib")).sum()).alias("not_eq"))["not_eq"][0]

    assert not_eq == 0


def test_mom_eq(df_ohlc: pl.DataFrame):
    not_eq = df_ohlc.with_columns(
        pl.col("close").ta.mom(3).alias("mom3"),
        talib.MOM(df_ohlc["close"], timeperiod=3).alias("MOM3"),
    ).select(((pl.col("mom3") != pl.col("MOM3")).sum()).alias("not_eq"))["not_eq"][0]

    assert not_eq == 0


def test_plus_di_eq(df_ohlc: pl.DataFrame):
    not_eq = df_ohlc.with_columns(
        pl.col("close").ta.plus_di(pl.col("high"), pl.col("low"), 3).alias("expr"),
        talib.PLUS_DI(df_ohlc["high"], df_ohlc["low"], df_ohlc["close"], timeperiod=3).alias(
            "talib"
        ),
    ).select(((pl.col("expr") != pl.col("talib")).sum()).alias("not_eq"))["not_eq"][0]

    assert not_eq == 0


def test_plus_dm_eq(df_ohlc: pl.DataFrame):
    not_eq = df_ohlc.with_columns(
        pl.col("high").ta.plus_dm(pl.col("low"), 3).alias("expr"),
        talib.PLUS_DM(df_ohlc["high"], df_ohlc["low"], timeperiod=3).alias("talib"),
    ).select(((pl.col("expr") != pl.col("talib")).sum()).alias("not_eq"))["not_eq"][0]

    assert not_eq == 0


def test_ppo_eq(df_ohlc: pl.DataFrame):
    not_eq = df_ohlc.with_columns(
        pl.col("close").ta.ppo(3, 10, 0).alias("ppo3"),
        talib.PPO(df_ohlc["close"], fastperiod=3, slowperiod=10, matype=0).alias("PPO3"),
    ).select(((pl.col("ppo3") != pl.col("PPO3")).sum()).alias("not_eq"))["not_eq"][0]

    assert not_eq == 0


def test_roc_eq(df_ohlc: pl.DataFrame):
    not_eq = df_ohlc.with_columns(
        pl.col("close").ta.roc(3).alias("roc3"),
        talib.ROC(df_ohlc["close"], timeperiod=3).alias("ROC3"),
    ).select(((pl.col("roc3") != pl.col("ROC3")).sum()).alias("not_eq"))["not_eq"][0]

    assert not_eq == 0


def test_rocp_eq(df_ohlc: pl.DataFrame):
    not_eq = df_ohlc.with_columns(
        pl.col("close").ta.rocp(3).alias("rocp3"),
        talib.ROCP(df_ohlc["close"], timeperiod=3).alias("ROCP3"),
    ).select(((pl.col("rocp3") != pl.col("ROCP3")).sum()).alias("not_eq"))["not_eq"][0]

    assert not_eq == 0


def test_rocr_eq(df_ohlc: pl.DataFrame):
    not_eq = df_ohlc.with_columns(
        pl.col("close").ta.rocr(3).alias("rocr3"),
        talib.ROCR(df_ohlc["close"], timeperiod=3).alias("ROCR3"),
    ).select(((pl.col("rocr3") != pl.col("ROCR3")).sum()).alias("not_eq"))["not_eq"][0]

    assert not_eq == 0


def test_rocr100_eq(df_ohlc: pl.DataFrame):
    not_eq = df_ohlc.with_columns(
        pl.col("close").ta.rocr100(3).alias("rocr1003"),
        talib.ROCR100(df_ohlc["close"], timeperiod=3).alias("ROCR1003"),
    ).select(((pl.col("rocr1003") != pl.col("ROCR1003")).sum()).alias("not_eq"))["not_eq"][0]

    assert not_eq == 0


def test_rsi_eq(df_ohlc: pl.DataFrame):
    not_eq = df_ohlc.with_columns(
        pl.col("close").ta.rsi(3).alias("rsi3"),
        talib.RSI(df_ohlc["close"], timeperiod=3).alias("RSI3"),
    ).select(((pl.col("rsi3") != pl.col("RSI3")).sum()).alias("not_eq"))["not_eq"][0]

    assert not_eq == 0


def test_stoch_eq(df_ohlc: pl.DataFrame):
    not_eq = df_ohlc.with_columns(
        pl.col("close").ta.stoch(pl.col("high"), pl.col("low")).struct.field("slowk").alias("expr"),
        talib.STOCH(
            df_ohlc["high"],
            df_ohlc["low"],
            df_ohlc["close"],
        )[0].alias("talib"),
    ).select(((pl.col("expr") != pl.col("talib")).sum()).alias("not_eq"))["not_eq"][0]

    assert not_eq == 0

    not_eq = df_ohlc.with_columns(
        pl.col("close").ta.stoch(pl.col("high"), pl.col("low")).struct.field("slowd").alias("expr"),
        talib.STOCH(
            df_ohlc["high"],
            df_ohlc["low"],
            df_ohlc["close"],
        )[1].alias("talib"),
    ).select(((pl.col("expr") != pl.col("talib")).sum()).alias("not_eq"))["not_eq"][0]

    assert not_eq == 0


def test_stochf_eq(df_ohlc: pl.DataFrame):
    not_eq = df_ohlc.with_columns(
        pl.col("close")
        .ta.stochf(pl.col("high"), pl.col("low"), 3, 10, 0)
        .struct.field("fastk")
        .alias("expr"),
        talib.STOCHF(
            df_ohlc["high"],
            df_ohlc["low"],
            df_ohlc["close"],
            fastk_period=3,
            fastd_period=10,
            fastd_matype=0,
        )[0].alias("talib"),
    ).select(((pl.col("expr") != pl.col("talib")).sum()).alias("not_eq"))["not_eq"][0]

    assert not_eq == 0

    not_eq = df_ohlc.with_columns(
        pl.col("close")
        .ta.stochf(pl.col("high"), pl.col("low"), 3, 10, 0)
        .struct.field("fastd")
        .alias("expr"),
        talib.STOCHF(
            df_ohlc["high"],
            df_ohlc["low"],
            df_ohlc["close"],
            fastk_period=3,
            fastd_period=10,
            fastd_matype=0,
        )[1].alias("talib"),
    ).select(((pl.col("expr") != pl.col("talib")).sum()).alias("not_eq"))["not_eq"][0]

    assert not_eq == 0


def test_stochrsi_eq(df_ohlc: pl.DataFrame):
    not_eq = df_ohlc.with_columns(
        pl.col("close").ta.stochrsi(3, 5, 3, 0).struct.field("fastk").alias("expr"),
        talib.STOCHRSI(
            df_ohlc["close"],
            timeperiod=3,
            fastk_period=5,
            fastd_period=3,
            fastd_matype=0,
        )[0].alias("talib"),
    ).select(((pl.col("expr") != pl.col("talib")).sum()).alias("not_eq"))["not_eq"][0]

    assert not_eq == 0

    not_eq = df_ohlc.with_columns(
        pl.col("close").ta.stochrsi(3, 5, 3, 0).struct.field("fastd").alias("expr"),
        talib.STOCHRSI(
            df_ohlc["close"],
            timeperiod=3,
            fastk_period=5,
            fastd_period=3,
            fastd_matype=0,
        )[1].alias("talib"),
    ).select(((pl.col("expr") != pl.col("talib")).sum()).alias("not_eq"))["not_eq"][0]

    assert not_eq == 0


def test_trix_eq(df_ohlc: pl.DataFrame):
    not_eq = df_ohlc.with_columns(
        pl.col("close").ta.trix(3).alias("trix3"),
        talib.TRIX(df_ohlc["close"], timeperiod=3).alias("TRIX3"),
    ).select(((pl.col("trix3") != pl.col("TRIX3")).sum()).alias("not_eq"))["not_eq"][0]

    assert not_eq == 0


def test_ultosc_eq(df_ohlc: pl.DataFrame):
    not_eq = df_ohlc.with_columns(
        pl.col("close").ta.ultosc(pl.col("high"), pl.col("low"), 3, 6, 12).alias("expr"),
        talib.ULTOSC(
            df_ohlc["high"],
            df_ohlc["low"],
            df_ohlc["close"],
            timeperiod1=3,
            timeperiod2=6,
            timeperiod3=12,
        ).alias("talib"),
    ).select(((pl.col("expr") != pl.col("talib")).sum()).alias("not_eq"))["not_eq"][0]

    assert not_eq == 0


def test_willr_eq(df_ohlc: pl.DataFrame):
    not_eq = df_ohlc.with_columns(
        pl.col("close").ta.willr(pl.col("high"), pl.col("low"), 3).alias("expr"),
        talib.WILLR(df_ohlc["high"], df_ohlc["low"], df_ohlc["close"], timeperiod=3).alias("talib"),
    ).select(((pl.col("expr") != pl.col("talib")).sum()).alias("not_eq"))["not_eq"][0]

    assert not_eq == 0


def test_bbands_eq(df_ohlc: pl.DataFrame):
    not_eq = df_ohlc.with_columns(
        pl.col("close").ta.bbands(3).struct.field("upperband").alias("expr"),
        talib.BBANDS(df_ohlc["close"], timeperiod=3, nbdevup=2, nbdevdn=2)[0].alias("talib"),
    ).select(((pl.col("expr") != pl.col("talib")).sum()).alias("not_eq"))["not_eq"][0]

    assert not_eq == 0

    not_eq = df_ohlc.with_columns(
        pl.col("close").ta.bbands(3).struct.field("middleband").alias("expr"),
        talib.BBANDS(df_ohlc["close"], timeperiod=3, nbdevup=2, nbdevdn=2)[1].alias("talib"),
    ).select(((pl.col("expr") != pl.col("talib")).sum()).alias("not_eq"))["not_eq"][0]

    assert not_eq == 0

    not_eq = df_ohlc.with_columns(
        pl.col("close").ta.bbands(3).struct.field("lowerband").alias("expr"),
        talib.BBANDS(df_ohlc["close"], timeperiod=3, nbdevup=2, nbdevdn=2)[2].alias("talib"),
    ).select(((pl.col("expr") != pl.col("talib")).sum()).alias("not_eq"))["not_eq"][0]

    assert not_eq == 0


def test_ema_eq(df_ohlc: pl.DataFrame):
    not_eq = df_ohlc.with_columns(
        pl.col("close").ta.ema(3).alias("ema3"),
        talib.EMA(df_ohlc["close"], timeperiod=3).alias("EMA3"),
    ).select(((pl.col("ema3") != pl.col("EMA3")).sum()).alias("not_eq"))["not_eq"][0]
    assert not_eq == 0


def test_dema_eq(df_ohlc: pl.DataFrame):
    not_eq = df_ohlc.with_columns(
        pl.col("close").ta.dema(3).alias("dema3"),
        talib.DEMA(df_ohlc["close"], timeperiod=3).alias("DEMA3"),
    ).select(((pl.col("dema3") != pl.col("DEMA3")).sum()).alias("not_eq"))["not_eq"][0]
    assert not_eq == 0


def test_ht_trendline_eq(df_ohlc: pl.DataFrame):
    not_eq = df_ohlc.with_columns(
        pl.col("close").ta.ht_trendline().alias("expr"),
        talib.HT_TRENDLINE(df_ohlc["close"]).alias("talib"),
    ).select(((pl.col("expr") != pl.col("talib")).sum()).alias("not_eq"))["not_eq"][0]

    assert not_eq == 0


def test_kama_eq(df_ohlc: pl.DataFrame):
    not_eq = df_ohlc.with_columns(
        pl.col("close").ta.kama(3).alias("kama3"),
        talib.KAMA(df_ohlc["close"], timeperiod=3).alias("KAMA3"),
    ).select(((pl.col("kama3") != pl.col("KAMA3")).sum()).alias("not_eq"))["not_eq"][0]
    assert not_eq == 0


def test_ma_eq(df_ohlc: pl.DataFrame):
    not_eq = df_ohlc.with_columns(
        pl.col("close").ta.ma(3).alias("ma3"),
        talib.MA(df_ohlc["close"], timeperiod=3, matype=0).alias("MA3"),
    ).select(((pl.col("ma3") != pl.col("MA3")).sum()).alias("not_eq"))["not_eq"][0]
    assert not_eq == 0


def test_mama_eq(df_ohlc: pl.DataFrame):
    not_eq = df_ohlc.with_columns(
        pl.col("close").ta.mama().struct.field("mama").alias("expr"),
        talib.MAMA(df_ohlc["close"])[0].alias("talib"),
    ).select(((pl.col("expr") != pl.col("talib")).sum()).alias("not_eq"))["not_eq"][0]

    assert not_eq == 0

    not_eq = df_ohlc.with_columns(
        pl.col("close").ta.mama().struct.field("fama").alias("expr"),
        talib.MAMA(df_ohlc["close"])[1].alias("talib"),
    ).select(((pl.col("expr") != pl.col("talib")).sum()).alias("not_eq"))["not_eq"][0]

    assert not_eq == 0


def test_mavp_eq(df_ohlc: pl.DataFrame):
    not_eq = df_ohlc.with_columns(
        pl.col("close")
        .ta.mavp(
            (pl.col("volume") / pl.col("volume").max()) * 10, minperiod=2, maxperiod=30, matype=0
        )
        .alias("mavp3"),
        talib.MAVP(
            df_ohlc["close"],
            (df_ohlc["volume"] / df_ohlc["volume"].max()) * 10,
            minperiod=2,
            maxperiod=30,
            matype=0,
        ).alias("MAVP3"),
    ).select(((pl.col("mavp3") != pl.col("MAVP3")).sum()).alias("not_eq"))["not_eq"][0]
    assert not_eq == 0


def test_midpoint_eq(df_ohlc: pl.DataFrame):
    not_eq = df_ohlc.with_columns(
        pl.col("close").ta.midpoint(3).alias("midpoint3"),
        talib.MIDPOINT(df_ohlc["close"], timeperiod=3).alias("MIDPOINT3"),
    ).select(((pl.col("midpoint3") != pl.col("MIDPOINT3")).sum()).alias("not_eq"))["not_eq"][0]
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


def test_sarext_eq(df_ohlc: pl.DataFrame):
    not_eq = df_ohlc.with_columns(
        pl.col("high")
        .ta.sarext(
            pl.col("low"),
            startvalue=0.0,
            offsetonreverse=0.0,
            accelerationinitlong=0.02,
            accelerationlong=0.02,
            accelerationmaxlong=0.2,
            accelerationinitshort=0.02,
            accelerationshort=0.02,
            accelerationmaxshort=0.2,
        )
        .alias("expr"),
        talib.SAREXT(
            df_ohlc["high"],
            df_ohlc["low"],
            startvalue=0.0,
            offsetonreverse=0.0,
            accelerationinitlong=0.02,
            accelerationlong=0.02,
            accelerationmaxlong=0.2,
            accelerationinitshort=0.02,
            accelerationshort=0.02,
            accelerationmaxshort=0.2,
        ).alias("talib"),
    ).select(((pl.col("expr") != pl.col("talib")).sum()).alias("not_eq"))["not_eq"][0]

    assert not_eq == 0


def test_sma_eq(df_ohlc: pl.DataFrame):
    not_eq = df_ohlc.with_columns(
        pl.col("close").ta.sma(3).alias("sma3"),
        talib.SMA(df_ohlc["close"], timeperiod=3).alias("SMA3"),
    ).select(((pl.col("sma3") != pl.col("SMA3")).sum()).alias("not_eq"))["not_eq"][0]
    assert not_eq == 0


def test_t3_eq(df_ohlc: pl.DataFrame):
    not_eq = df_ohlc.with_columns(
        pl.col("close").ta.t3(timeperiod=3, vfactor=0).alias("t33"),
        talib.T3(df_ohlc["close"], timeperiod=3, vfactor=0).alias("T33"),
    ).select(((pl.col("t33") != pl.col("T33")).sum()).alias("not_eq"))["not_eq"][0]
    assert not_eq == 0


def test_tema_eq(df_ohlc: pl.DataFrame):
    not_eq = df_ohlc.with_columns(
        pl.col("close").ta.tema(3).alias("tema3"),
        talib.TEMA(df_ohlc["close"], timeperiod=3).alias("TEMA3"),
    ).select(((pl.col("tema3") != pl.col("TEMA3")).sum()).alias("not_eq"))["not_eq"][0]
    assert not_eq == 0


def test_trima_eq(df_ohlc: pl.DataFrame):
    not_eq = df_ohlc.with_columns(
        pl.col("close").ta.trima(3).alias("trima3"),
        talib.TRIMA(df_ohlc["close"], timeperiod=3).alias("TRIMA3"),
    ).select(((pl.col("trima3") != pl.col("TRIMA3")).sum()).alias("not_eq"))["not_eq"][0]
    assert not_eq == 0


def test_wma_eq(df_ohlc: pl.DataFrame):
    not_eq = df_ohlc.with_columns(
        pl.col("close").ta.wma(3).alias("wma3"),
        talib.WMA(df_ohlc["close"], timeperiod=3).alias("WMA3"),
    ).select(((pl.col("wma3") != pl.col("WMA3")).sum()).alias("not_eq"))["not_eq"][0]
    assert not_eq == 0


def test_cdlabandonedbaby_eq(df_ohlc: pl.DataFrame):
    not_eq = df_ohlc.with_columns(
        pl.col("open")
        .ta.cdlabandonedbaby(pl.col("high"), pl.col("low"), pl.col("close"), penetration=0.3)
        .alias("expr"),
        talib.CDLABANDONEDBABY(
            df_ohlc["open"], df_ohlc["high"], df_ohlc["low"], df_ohlc["close"], penetration=0.3
        ).alias("talib"),
    ).select(((pl.col("expr") != pl.col("talib")).sum()).alias("not_eq"))["not_eq"][0]
    assert not_eq == 0


def test_avgprice_eq(df_ohlc: pl.DataFrame):
    not_eq = df_ohlc.with_columns(
        pl.col("open").ta.avgprice(pl.col("high"), pl.col("low"), pl.col("close")).alias("expr"),
        talib.AVGPRICE(df_ohlc["open"], df_ohlc["high"], df_ohlc["low"], df_ohlc["close"]).alias(
            "talib"
        ),
    ).select(((pl.col("expr") != pl.col("talib")).sum()).alias("not_eq"))["not_eq"][0]
    assert not_eq == 0


def test_medprice_eq(df_ohlc: pl.DataFrame):
    not_eq = df_ohlc.with_columns(
        pl.col("high").ta.medprice(pl.col("low")).alias("expr"),
        talib.MEDPRICE(df_ohlc["high"], df_ohlc["low"]).alias("talib"),
    ).select(((pl.col("expr") != pl.col("talib")).sum()).alias("not_eq"))["not_eq"][0]
    assert not_eq == 0


def test_typprice_eq(df_ohlc: pl.DataFrame):
    not_eq = df_ohlc.with_columns(
        pl.col("close").ta.typprice(pl.col("high"), pl.col("low")).alias("expr"),
        talib.TYPPRICE(df_ohlc["high"], df_ohlc["low"], df_ohlc["close"]).alias("talib"),
    ).select(((pl.col("expr") != pl.col("talib")).sum()).alias("not_eq"))["not_eq"][0]
    assert not_eq == 0


def test_wclprice_eq(df_ohlc: pl.DataFrame):
    not_eq = df_ohlc.with_columns(
        pl.col("close").ta.wclprice(pl.col("high"), pl.col("low")).alias("expr"),
        talib.WCLPRICE(df_ohlc["high"], df_ohlc["low"], df_ohlc["close"]).alias("talib"),
    ).select(((pl.col("expr") != pl.col("talib")).sum()).alias("not_eq"))["not_eq"][0]
    assert not_eq == 0


def test_beta_eq(df_ohlc: pl.DataFrame):
    not_eq = df_ohlc.with_columns(
        pl.col("close").ta.beta(pl.col("high"), 3).alias("expr"),
        talib.BETA(df_ohlc["close"], df_ohlc["high"], timeperiod=3).alias("talib"),
    ).select(((pl.col("expr") != pl.col("talib")).sum()).alias("not_eq"))["not_eq"][0]

    assert not_eq == 0


def test_correl_eq(df_ohlc: pl.DataFrame):
    not_eq = df_ohlc.with_columns(
        pl.col("close").ta.correl(pl.col("high"), 3).alias("expr"),
        talib.CORREL(df_ohlc["close"], df_ohlc["high"], timeperiod=3).alias("talib"),
    ).select(((pl.col("expr") != pl.col("talib")).sum()).alias("not_eq"))["not_eq"][0]

    assert not_eq == 0


def test_linearreg_eq(df_ohlc: pl.DataFrame):
    not_eq = df_ohlc.with_columns(
        pl.col("close").ta.linearreg(3).alias("expr"),
        talib.LINEARREG(df_ohlc["close"], timeperiod=3).alias("talib"),
    ).select(((pl.col("expr") != pl.col("talib")).sum()).alias("not_eq"))["not_eq"][0]

    assert not_eq == 0


def test_linearreg_angle_eq(df_ohlc: pl.DataFrame):
    not_eq = df_ohlc.with_columns(
        pl.col("close").ta.linearreg_angle(3).alias("expr"),
        talib.LINEARREG_ANGLE(df_ohlc["close"], timeperiod=3).alias("talib"),
    ).select(((pl.col("expr") != pl.col("talib")).sum()).alias("not_eq"))["not_eq"][0]

    assert not_eq == 0


def test_linearreg_intercept_eq(df_ohlc: pl.DataFrame):
    not_eq = df_ohlc.with_columns(
        pl.col("close").ta.linearreg_intercept(3).alias("expr"),
        talib.LINEARREG_INTERCEPT(df_ohlc["close"], timeperiod=3).alias("talib"),
    ).select(((pl.col("expr") != pl.col("talib")).sum()).alias("not_eq"))["not_eq"][0]

    assert not_eq == 0


def test_linearreg_slope_eq(df_ohlc: pl.DataFrame):
    not_eq = df_ohlc.with_columns(
        pl.col("close").ta.linearreg_slope(3).alias("expr"),
        talib.LINEARREG_SLOPE(df_ohlc["close"], timeperiod=3).alias("talib"),
    ).select(((pl.col("expr") != pl.col("talib")).sum()).alias("not_eq"))["not_eq"][0]

    assert not_eq == 0


def test_stddev_eq(df_ohlc: pl.DataFrame):
    not_eq = df_ohlc.with_columns(
        pl.col("close").ta.stddev(3).alias("expr"),
        talib.STDDEV(df_ohlc["close"], timeperiod=3, nbdev=1).alias("talib"),
    ).select(((pl.col("expr") != pl.col("talib")).sum()).alias("not_eq"))["not_eq"][0]

    assert not_eq == 0


def test_var_eq(df_ohlc: pl.DataFrame):
    not_eq = df_ohlc.with_columns(
        pl.col("close").ta.var(3).alias("expr"),
        talib.VAR(df_ohlc["close"], timeperiod=3, nbdev=1).alias("talib"),
    ).select(((pl.col("expr") != pl.col("talib")).sum()).alias("not_eq"))["not_eq"][0]

    assert not_eq == 0


def test_tsf_eq(df_ohlc: pl.DataFrame):
    not_eq = df_ohlc.with_columns(
        pl.col("close").ta.tsf(3).alias("expr"),
        talib.TSF(df_ohlc["close"], timeperiod=3).alias("talib"),
    ).select(((pl.col("expr") != pl.col("talib")).sum()).alias("not_eq"))["not_eq"][0]

    assert not_eq == 0


def test_atr_eq(df_ohlc: pl.DataFrame):
    not_eq = df_ohlc.with_columns(
        pl.col("close").ta.atr(pl.col("high"), pl.col("low"), 3).alias("expr"),
        talib.ATR(df_ohlc["high"], df_ohlc["low"], df_ohlc["close"], timeperiod=3).alias("talib"),
    ).select(((pl.col("expr") != pl.col("talib")).sum()).alias("not_eq"))["not_eq"][0]
    assert not_eq == 0


def test_trange_eq(df_ohlc: pl.DataFrame):
    not_eq = df_ohlc.with_columns(
        pl.col("close").ta.trange(pl.col("high"), pl.col("low")).alias("expr"),
        talib.TRANGE(df_ohlc["high"], df_ohlc["low"], df_ohlc["close"]).alias("talib"),
    ).select(((pl.col("expr") != pl.col("talib")).sum()).alias("not_eq"))["not_eq"][0]

    assert not_eq == 0


def test_natr_eq(df_ohlc: pl.DataFrame):
    not_eq = df_ohlc.with_columns(
        pl.col("close").ta.natr(pl.col("high"), pl.col("low"), 3).alias("expr"),
        talib.NATR(df_ohlc["high"], df_ohlc["low"], df_ohlc["close"], timeperiod=3).alias("talib"),
    ).select(((pl.col("expr") != pl.col("talib")).sum()).alias("not_eq"))["not_eq"][0]
    assert not_eq == 0


def test_ad_eq(df_ohlc: pl.DataFrame):
    not_eq = df_ohlc.with_columns(
        pl.col("close").ta.ad(pl.col("high"), pl.col("low"), pl.col("volume")).alias("expr"),
        talib.AD(df_ohlc["high"], df_ohlc["low"], df_ohlc["close"], df_ohlc["volume"]).alias(
            "talib"
        ),
    ).select(((pl.col("expr") != pl.col("talib")).sum()).alias("not_eq"))["not_eq"][0]
    assert not_eq == 0


def test_ta_adosc_eq(df_ohlc: pl.DataFrame):
    not_eq = df_ohlc.with_columns(
        pl.col("close")
        .ta.adosc(pl.col("high"), pl.col("low"), pl.col("volume"), fastperiod=3, slowperiod=10)
        .alias("expr"),
        talib.ADOSC(
            df_ohlc["high"],
            df_ohlc["low"],
            df_ohlc["close"],
            df_ohlc["volume"],
            fastperiod=3,
            slowperiod=10,
        ).alias("talib"),
    ).select(((pl.col("expr") != pl.col("talib")).sum()).alias("not_eq"))["not_eq"][0]
    assert not_eq == 0


def test_obv_eq(df_ohlc: pl.DataFrame):
    not_eq = df_ohlc.with_columns(
        pl.col("close").ta.obv(pl.col("volume")).alias("expr"),
        talib.OBV(df_ohlc["close"], df_ohlc["volume"]).alias("talib"),
    ).select(((pl.col("expr") != pl.col("talib")).sum()).alias("not_eq"))["not_eq"][0]
    assert not_eq == 0


def test_cdl2crows_eq(df_ohlc: pl.DataFrame):
    not_eq = df_ohlc.with_columns(
        pl.col("open").ta.cdl2crows(pl.col("high"), pl.col("low"), pl.col("close")).alias("expr"),
        talib.CDL2CROWS(df_ohlc["open"], df_ohlc["high"], df_ohlc["low"], df_ohlc["close"]).alias(
            "talib"
        ),
    ).select(((pl.col("expr") != pl.col("talib")).sum()).alias("not_eq"))["not_eq"][0]
    assert not_eq == 0


def test_cdl3blackcrows_eq(df_ohlc: pl.DataFrame):
    not_eq = df_ohlc.with_columns(
        pl.col("open")
        .ta.cdl3blackcrows(pl.col("high"), pl.col("low"), pl.col("close"))
        .alias("expr"),
        talib.CDL3BLACKCROWS(
            df_ohlc["open"], df_ohlc["high"], df_ohlc["low"], df_ohlc["close"]
        ).alias("talib"),
    ).select(((pl.col("expr") != pl.col("talib")).sum()).alias("not_eq"))["not_eq"][0]
    assert not_eq == 0


def test_cdl3inside_eq(df_ohlc: pl.DataFrame):
    not_eq = df_ohlc.with_columns(
        pl.col("open").ta.cdl3inside(pl.col("high"), pl.col("low"), pl.col("close")).alias("expr"),
        talib.CDL3INSIDE(df_ohlc["open"], df_ohlc["high"], df_ohlc["low"], df_ohlc["close"]).alias(
            "talib"
        ),
    ).select(((pl.col("expr") != pl.col("talib")).sum()).alias("not_eq"))["not_eq"][0]
    assert not_eq == 0


def test_cdl3linestrike_eq(df_ohlc: pl.DataFrame):
    not_eq = df_ohlc.with_columns(
        pl.col("open")
        .ta.cdl3linestrike(pl.col("high"), pl.col("low"), pl.col("close"))
        .alias("expr"),
        talib.CDL3LINESTRIKE(
            df_ohlc["open"], df_ohlc["high"], df_ohlc["low"], df_ohlc["close"]
        ).alias("talib"),
    ).select(((pl.col("expr") != pl.col("talib")).sum()).alias("not_eq"))["not_eq"][0]
    assert not_eq == 0


def test_cdl3outside_eq(df_ohlc: pl.DataFrame):
    not_eq = df_ohlc.with_columns(
        pl.col("open").ta.cdl3outside(pl.col("high"), pl.col("low"), pl.col("close")).alias("expr"),
        talib.CDL3OUTSIDE(df_ohlc["open"], df_ohlc["high"], df_ohlc["low"], df_ohlc["close"]).alias(
            "talib"
        ),
    ).select(((pl.col("expr") != pl.col("talib")).sum()).alias("not_eq"))["not_eq"][0]
    assert not_eq == 0


def test_cdl3starsinsouth_eq(df_ohlc: pl.DataFrame):
    not_eq = df_ohlc.with_columns(
        pl.col("open")
        .ta.cdl3starsinsouth(pl.col("high"), pl.col("low"), pl.col("close"))
        .alias("expr"),
        talib.CDL3STARSINSOUTH(
            df_ohlc["open"], df_ohlc["high"], df_ohlc["low"], df_ohlc["close"]
        ).alias("talib"),
    ).select(((pl.col("expr") != pl.col("talib")).sum()).alias("not_eq"))["not_eq"][0]
    assert not_eq == 0


def test_cdl3whitesoldiers_eq(df_ohlc: pl.DataFrame):
    not_eq = df_ohlc.with_columns(
        pl.col("open")
        .ta.cdl3whitesoldiers(pl.col("high"), pl.col("low"), pl.col("close"))
        .alias("expr"),
        talib.CDL3WHITESOLDIERS(
            df_ohlc["open"], df_ohlc["high"], df_ohlc["low"], df_ohlc["close"]
        ).alias("talib"),
    ).select(((pl.col("expr") != pl.col("talib")).sum()).alias("not_eq"))["not_eq"][0]
    assert not_eq == 0


def test_cdladvanceblock_eq(df_ohlc: pl.DataFrame):
    not_eq = df_ohlc.with_columns(
        pl.col("open")
        .ta.cdladvanceblock(pl.col("high"), pl.col("low"), pl.col("close"))
        .alias("expr"),
        talib.CDLADVANCEBLOCK(
            df_ohlc["open"], df_ohlc["high"], df_ohlc["low"], df_ohlc["close"]
        ).alias("talib"),
    ).select(((pl.col("expr") != pl.col("talib")).sum()).alias("not_eq"))["not_eq"][0]
    assert not_eq == 0


def test_cdlbelthold_eq(df_ohlc: pl.DataFrame):
    not_eq = df_ohlc.with_columns(
        pl.col("open").ta.cdlbelthold(pl.col("high"), pl.col("low"), pl.col("close")).alias("expr"),
        talib.CDLBELTHOLD(df_ohlc["open"], df_ohlc["high"], df_ohlc["low"], df_ohlc["close"]).alias(
            "talib"
        ),
    ).select(((pl.col("expr") != pl.col("talib")).sum()).alias("not_eq"))["not_eq"][0]
    assert not_eq == 0


def test_cdlbreakaway_eq(df_ohlc: pl.DataFrame):
    not_eq = df_ohlc.with_columns(
        pl.col("open")
        .ta.cdlbreakaway(pl.col("high"), pl.col("low"), pl.col("close"))
        .alias("expr"),
        talib.CDLBREAKAWAY(
            df_ohlc["open"], df_ohlc["high"], df_ohlc["low"], df_ohlc["close"]
        ).alias("talib"),
    ).select(((pl.col("expr") != pl.col("talib")).sum()).alias("not_eq"))["not_eq"][0]
    assert not_eq == 0


def test_cdlclosingmarubozu_eq(df_ohlc: pl.DataFrame):
    not_eq = df_ohlc.with_columns(
        pl.col("open")
        .ta.cdlclosingmarubozu(pl.col("high"), pl.col("low"), pl.col("close"))
        .alias("expr"),
        talib.CDLCLOSINGMARUBOZU(
            df_ohlc["open"], df_ohlc["high"], df_ohlc["low"], df_ohlc["close"]
        ).alias("talib"),
    ).select(((pl.col("expr") != pl.col("talib")).sum()).alias("not_eq"))["not_eq"][0]
    assert not_eq == 0


def test_cdlconcealbabyswall_eq(df_ohlc: pl.DataFrame):
    not_eq = df_ohlc.with_columns(
        pl.col("open")
        .ta.cdlconcealbabyswall(pl.col("high"), pl.col("low"), pl.col("close"))
        .alias("expr"),
        talib.CDLCONCEALBABYSWALL(
            df_ohlc["open"], df_ohlc["high"], df_ohlc["low"], df_ohlc["close"]
        ).alias("talib"),
    ).select(((pl.col("expr") != pl.col("talib")).sum()).alias("not_eq"))["not_eq"][0]
    assert not_eq == 0


def test_cdlcounterattack_eq(df_ohlc: pl.DataFrame):
    not_eq = df_ohlc.with_columns(
        pl.col("open")
        .ta.cdlcounterattack(pl.col("high"), pl.col("low"), pl.col("close"))
        .alias("expr"),
        talib.CDLCOUNTERATTACK(
            df_ohlc["open"], df_ohlc["high"], df_ohlc["low"], df_ohlc["close"]
        ).alias("talib"),
    ).select(((pl.col("expr") != pl.col("talib")).sum()).alias("not_eq"))["not_eq"][0]
    assert not_eq == 0


def test_cdldarkcloudcover_eq(df_ohlc: pl.DataFrame):
    not_eq = df_ohlc.with_columns(
        pl.col("open")
        .ta.cdldarkcloudcover(pl.col("high"), pl.col("low"), pl.col("close"))
        .alias("expr"),
        talib.CDLDARKCLOUDCOVER(
            df_ohlc["open"], df_ohlc["high"], df_ohlc["low"], df_ohlc["close"]
        ).alias("talib"),
    ).select(((pl.col("expr") != pl.col("talib")).sum()).alias("not_eq"))["not_eq"][0]
    assert not_eq == 0


def test_cdldoji_eq(df_ohlc: pl.DataFrame):
    not_eq = df_ohlc.with_columns(
        pl.col("open").ta.cdldoji(pl.col("high"), pl.col("low"), pl.col("close")).alias("expr"),
        talib.CDLDOJI(df_ohlc["open"], df_ohlc["high"], df_ohlc["low"], df_ohlc["close"]).alias(
            "talib"
        ),
    ).select(((pl.col("expr") != pl.col("talib")).sum()).alias("not_eq"))["not_eq"][0]
    assert not_eq == 0


def test_cdldojistar_eq(df_ohlc: pl.DataFrame):
    not_eq = df_ohlc.with_columns(
        pl.col("open").ta.cdldojistar(pl.col("high"), pl.col("low"), pl.col("close")).alias("expr"),
        talib.CDLDOJISTAR(df_ohlc["open"], df_ohlc["high"], df_ohlc["low"], df_ohlc["close"]).alias(
            "talib"
        ),
    ).select(((pl.col("expr") != pl.col("talib")).sum()).alias("not_eq"))["not_eq"][0]
    assert not_eq == 0


def test_cdldragonflydoji_eq(df_ohlc: pl.DataFrame):
    not_eq = df_ohlc.with_columns(
        pl.col("open")
        .ta.cdldragonflydoji(pl.col("high"), pl.col("low"), pl.col("close"))
        .alias("expr"),
        talib.CDLDRAGONFLYDOJI(
            df_ohlc["open"], df_ohlc["high"], df_ohlc["low"], df_ohlc["close"]
        ).alias("talib"),
    ).select(((pl.col("expr") != pl.col("talib")).sum()).alias("not_eq"))["not_eq"][0]
    assert not_eq == 0


def test_cdlengulfing_eq(df_ohlc: pl.DataFrame):
    not_eq = df_ohlc.with_columns(
        pl.col("open")
        .ta.cdlengulfing(pl.col("high"), pl.col("low"), pl.col("close"))
        .alias("expr"),
        talib.CDLENGULFING(
            df_ohlc["open"], df_ohlc["high"], df_ohlc["low"], df_ohlc["close"]
        ).alias("talib"),
    ).select(((pl.col("expr") != pl.col("talib")).sum()).alias("not_eq"))["not_eq"][0]
    assert not_eq == 0


def test_cdleveningdojistar_eq(df_ohlc: pl.DataFrame):
    not_eq = df_ohlc.with_columns(
        pl.col("open")
        .ta.cdleveningdojistar(pl.col("high"), pl.col("low"), pl.col("close"))
        .alias("expr"),
        talib.CDLEVENINGDOJISTAR(
            df_ohlc["open"], df_ohlc["high"], df_ohlc["low"], df_ohlc["close"]
        ).alias("talib"),
    ).select(((pl.col("expr") != pl.col("talib")).sum()).alias("not_eq"))["not_eq"][0]
    assert not_eq == 0


def test_cdleveningstar_eq(df_ohlc: pl.DataFrame):
    not_eq = df_ohlc.with_columns(
        pl.col("open")
        .ta.cdleveningstar(pl.col("high"), pl.col("low"), pl.col("close"))
        .alias("expr"),
        talib.CDLEVENINGSTAR(
            df_ohlc["open"], df_ohlc["high"], df_ohlc["low"], df_ohlc["close"]
        ).alias("talib"),
    ).select(((pl.col("expr") != pl.col("talib")).sum()).alias("not_eq"))["not_eq"][0]
    assert not_eq == 0


def test_cdlgapsidesidewhite_eq(df_ohlc: pl.DataFrame):
    not_eq = df_ohlc.with_columns(
        pl.col("open")
        .ta.cdlgapsidesidewhite(pl.col("high"), pl.col("low"), pl.col("close"))
        .alias("expr"),
        talib.CDLGAPSIDESIDEWHITE(
            df_ohlc["open"], df_ohlc["high"], df_ohlc["low"], df_ohlc["close"]
        ).alias("talib"),
    ).select(((pl.col("expr") != pl.col("talib")).sum()).alias("not_eq"))["not_eq"][0]
    assert not_eq == 0


def test_cdlgravestonedoji_eq(df_ohlc: pl.DataFrame):
    not_eq = df_ohlc.with_columns(
        pl.col("open")
        .ta.cdlgravestonedoji(pl.col("high"), pl.col("low"), pl.col("close"))
        .alias("expr"),
        talib.CDLGRAVESTONEDOJI(
            df_ohlc["open"], df_ohlc["high"], df_ohlc["low"], df_ohlc["close"]
        ).alias("talib"),
    ).select(((pl.col("expr") != pl.col("talib")).sum()).alias("not_eq"))["not_eq"][0]
    assert not_eq == 0


def test_cdlhammer_eq(df_ohlc: pl.DataFrame):
    not_eq = df_ohlc.with_columns(
        pl.col("open").ta.cdlhammer(pl.col("high"), pl.col("low"), pl.col("close")).alias("expr"),
        talib.CDLHAMMER(df_ohlc["open"], df_ohlc["high"], df_ohlc["low"], df_ohlc["close"]).alias(
            "talib"
        ),
    ).select(((pl.col("expr") != pl.col("talib")).sum()).alias("not_eq"))["not_eq"][0]
    assert not_eq == 0


def test_cdlhangingman_eq(df_ohlc: pl.DataFrame):
    not_eq = df_ohlc.with_columns(
        pl.col("open")
        .ta.cdlhangingman(pl.col("high"), pl.col("low"), pl.col("close"))
        .alias("expr"),
        talib.CDLHANGINGMAN(
            df_ohlc["open"], df_ohlc["high"], df_ohlc["low"], df_ohlc["close"]
        ).alias("talib"),
    ).select(((pl.col("expr") != pl.col("talib")).sum()).alias("not_eq"))["not_eq"][0]
    assert not_eq == 0


def test_cdlharami_eq(df_ohlc: pl.DataFrame):
    not_eq = df_ohlc.with_columns(
        pl.col("open").ta.cdlharami(pl.col("high"), pl.col("low"), pl.col("close")).alias("expr"),
        talib.CDLHARAMI(df_ohlc["open"], df_ohlc["high"], df_ohlc["low"], df_ohlc["close"]).alias(
            "talib"
        ),
    ).select(((pl.col("expr") != pl.col("talib")).sum()).alias("not_eq"))["not_eq"][0]
    assert not_eq == 0


def test_cdlharamicross_eq(df_ohlc: pl.DataFrame):
    not_eq = df_ohlc.with_columns(
        pl.col("open")
        .ta.cdlharamicross(pl.col("high"), pl.col("low"), pl.col("close"))
        .alias("expr"),
        talib.CDLHARAMICROSS(
            df_ohlc["open"], df_ohlc["high"], df_ohlc["low"], df_ohlc["close"]
        ).alias("talib"),
    ).select(((pl.col("expr") != pl.col("talib")).sum()).alias("not_eq"))["not_eq"][0]
    assert not_eq == 0


def test_cdlhighwave_eq(df_ohlc: pl.DataFrame):
    not_eq = df_ohlc.with_columns(
        pl.col("open").ta.cdlhighwave(pl.col("high"), pl.col("low"), pl.col("close")).alias("expr"),
        talib.CDLHIGHWAVE(df_ohlc["open"], df_ohlc["high"], df_ohlc["low"], df_ohlc["close"]).alias(
            "talib"
        ),
    ).select(((pl.col("expr") != pl.col("talib")).sum()).alias("not_eq"))["not_eq"][0]
    assert not_eq == 0


def test_cdlhikkake_eq(df_ohlc: pl.DataFrame):
    not_eq = df_ohlc.with_columns(
        pl.col("open").ta.cdlhikkake(pl.col("high"), pl.col("low"), pl.col("close")).alias("expr"),
        talib.CDLHIKKAKE(df_ohlc["open"], df_ohlc["high"], df_ohlc["low"], df_ohlc["close"]).alias(
            "talib"
        ),
    ).select(((pl.col("expr") != pl.col("talib")).sum()).alias("not_eq"))["not_eq"][0]
    assert not_eq == 0


def test_cdlhikkakemod_eq(df_ohlc: pl.DataFrame):
    not_eq = df_ohlc.with_columns(
        pl.col("open")
        .ta.cdlhikkakemod(pl.col("high"), pl.col("low"), pl.col("close"))
        .alias("expr"),
        talib.CDLHIKKAKEMOD(
            df_ohlc["open"], df_ohlc["high"], df_ohlc["low"], df_ohlc["close"]
        ).alias("talib"),
    ).select(((pl.col("expr") != pl.col("talib")).sum()).alias("not_eq"))["not_eq"][0]
    assert not_eq == 0


def test_cdlhomingpigeon_eq(df_ohlc: pl.DataFrame):
    not_eq = df_ohlc.with_columns(
        pl.col("open")
        .ta.cdlhomingpigeon(pl.col("high"), pl.col("low"), pl.col("close"))
        .alias("expr"),
        talib.CDLHOMINGPIGEON(
            df_ohlc["open"], df_ohlc["high"], df_ohlc["low"], df_ohlc["close"]
        ).alias("talib"),
    ).select(((pl.col("expr") != pl.col("talib")).sum()).alias("not_eq"))["not_eq"][0]
    assert not_eq == 0


def test_cdlidentical3crows_eq(df_ohlc: pl.DataFrame):
    not_eq = df_ohlc.with_columns(
        pl.col("open")
        .ta.cdlidentical3crows(pl.col("high"), pl.col("low"), pl.col("close"))
        .alias("expr"),
        talib.CDLIDENTICAL3CROWS(
            df_ohlc["open"], df_ohlc["high"], df_ohlc["low"], df_ohlc["close"]
        ).alias("talib"),
    ).select(((pl.col("expr") != pl.col("talib")).sum()).alias("not_eq"))["not_eq"][0]
    assert not_eq == 0


def test_cdlinneck_eq(df_ohlc: pl.DataFrame):
    not_eq = df_ohlc.with_columns(
        pl.col("open").ta.cdlinneck(pl.col("high"), pl.col("low"), pl.col("close")).alias("expr"),
        talib.CDLINNECK(df_ohlc["open"], df_ohlc["high"], df_ohlc["low"], df_ohlc["close"]).alias(
            "talib"
        ),
    ).select(((pl.col("expr") != pl.col("talib")).sum()).alias("not_eq"))["not_eq"][0]
    assert not_eq == 0


def test_cdlinvertedhammer_eq(df_ohlc: pl.DataFrame):
    not_eq = df_ohlc.with_columns(
        pl.col("open")
        .ta.cdlinvertedhammer(pl.col("high"), pl.col("low"), pl.col("close"))
        .alias("expr"),
        talib.CDLINVERTEDHAMMER(
            df_ohlc["open"], df_ohlc["high"], df_ohlc["low"], df_ohlc["close"]
        ).alias("talib"),
    ).select(((pl.col("expr") != pl.col("talib")).sum()).alias("not_eq"))["not_eq"][0]
    assert not_eq == 0


def test_cdlkicking_eq(df_ohlc: pl.DataFrame):
    not_eq = df_ohlc.with_columns(
        pl.col("open").ta.cdlkicking(pl.col("high"), pl.col("low"), pl.col("close")).alias("expr"),
        talib.CDLKICKING(df_ohlc["open"], df_ohlc["high"], df_ohlc["low"], df_ohlc["close"]).alias(
            "talib"
        ),
    ).select(((pl.col("expr") != pl.col("talib")).sum()).alias("not_eq"))["not_eq"][0]
    assert not_eq == 0


def test_cdlkickingbylength_eq(df_ohlc: pl.DataFrame):
    not_eq = df_ohlc.with_columns(
        pl.col("open")
        .ta.cdlkickingbylength(pl.col("high"), pl.col("low"), pl.col("close"))
        .alias("expr"),
        talib.CDLKICKINGBYLENGTH(
            df_ohlc["open"], df_ohlc["high"], df_ohlc["low"], df_ohlc["close"]
        ).alias("talib"),
    ).select(((pl.col("expr") != pl.col("talib")).sum()).alias("not_eq"))["not_eq"][0]
    assert not_eq == 0


def test_cdlladderbottom_eq(df_ohlc: pl.DataFrame):
    not_eq = df_ohlc.with_columns(
        pl.col("open")
        .ta.cdlladderbottom(pl.col("high"), pl.col("low"), pl.col("close"))
        .alias("expr"),
        talib.CDLLADDERBOTTOM(
            df_ohlc["open"], df_ohlc["high"], df_ohlc["low"], df_ohlc["close"]
        ).alias("talib"),
    ).select(((pl.col("expr") != pl.col("talib")).sum()).alias("not_eq"))["not_eq"][0]
    assert not_eq == 0


def test_cdllongleggeddoji_eq(df_ohlc: pl.DataFrame):
    not_eq = df_ohlc.with_columns(
        pl.col("open")
        .ta.cdllongleggeddoji(pl.col("high"), pl.col("low"), pl.col("close"))
        .alias("expr"),
        talib.CDLLONGLEGGEDDOJI(
            df_ohlc["open"], df_ohlc["high"], df_ohlc["low"], df_ohlc["close"]
        ).alias("talib"),
    ).select(((pl.col("expr") != pl.col("talib")).sum()).alias("not_eq"))["not_eq"][0]
    assert not_eq == 0


def test_cdllongline_eq(df_ohlc: pl.DataFrame):
    not_eq = df_ohlc.with_columns(
        pl.col("open").ta.cdllongline(pl.col("high"), pl.col("low"), pl.col("close")).alias("expr"),
        talib.CDLLONGLINE(df_ohlc["open"], df_ohlc["high"], df_ohlc["low"], df_ohlc["close"]).alias(
            "talib"
        ),
    ).select(((pl.col("expr") != pl.col("talib")).sum()).alias("not_eq"))["not_eq"][0]
    assert not_eq == 0


def test_cdlmarubozu_eq(df_ohlc: pl.DataFrame):
    not_eq = df_ohlc.with_columns(
        pl.col("open").ta.cdlmarubozu(pl.col("high"), pl.col("low"), pl.col("close")).alias("expr"),
        talib.CDLMARUBOZU(df_ohlc["open"], df_ohlc["high"], df_ohlc["low"], df_ohlc["close"]).alias(
            "talib"
        ),
    ).select(((pl.col("expr") != pl.col("talib")).sum()).alias("not_eq"))["not_eq"][0]
    assert not_eq == 0


def test_cdlmatchinglow_eq(df_ohlc: pl.DataFrame):
    not_eq = df_ohlc.with_columns(
        pl.col("open")
        .ta.cdlmatchinglow(pl.col("high"), pl.col("low"), pl.col("close"))
        .alias("expr"),
        talib.CDLMATCHINGLOW(
            df_ohlc["open"], df_ohlc["high"], df_ohlc["low"], df_ohlc["close"]
        ).alias("talib"),
    ).select(((pl.col("expr") != pl.col("talib")).sum()).alias("not_eq"))["not_eq"][0]
    assert not_eq == 0


def test_cdlmathold_eq(df_ohlc: pl.DataFrame):
    not_eq = df_ohlc.with_columns(
        pl.col("open").ta.cdlmathold(pl.col("high"), pl.col("low"), pl.col("close")).alias("expr"),
        talib.CDLMATHOLD(df_ohlc["open"], df_ohlc["high"], df_ohlc["low"], df_ohlc["close"]).alias(
            "talib"
        ),
    ).select(((pl.col("expr") != pl.col("talib")).sum()).alias("not_eq"))["not_eq"][0]
    assert not_eq == 0


def test_cdlmorningdojistar_eq(df_ohlc: pl.DataFrame):
    not_eq = df_ohlc.with_columns(
        pl.col("open")
        .ta.cdlmorningdojistar(pl.col("high"), pl.col("low"), pl.col("close"))
        .alias("expr"),
        talib.CDLMORNINGDOJISTAR(
            df_ohlc["open"], df_ohlc["high"], df_ohlc["low"], df_ohlc["close"]
        ).alias("talib"),
    ).select(((pl.col("expr") != pl.col("talib")).sum()).alias("not_eq"))["not_eq"][0]
    assert not_eq == 0


def test_cdlmorningstar_eq(df_ohlc: pl.DataFrame):
    not_eq = df_ohlc.with_columns(
        pl.col("open")
        .ta.cdlmorningstar(pl.col("high"), pl.col("low"), pl.col("close"))
        .alias("expr"),
        talib.CDLMORNINGSTAR(
            df_ohlc["open"], df_ohlc["high"], df_ohlc["low"], df_ohlc["close"]
        ).alias("talib"),
    ).select(((pl.col("expr") != pl.col("talib")).sum()).alias("not_eq"))["not_eq"][0]
    assert not_eq == 0


def test_cdlonneck_eq(df_ohlc: pl.DataFrame):
    not_eq = df_ohlc.with_columns(
        pl.col("open").ta.cdlonneck(pl.col("high"), pl.col("low"), pl.col("close")).alias("expr"),
        talib.CDLONNECK(df_ohlc["open"], df_ohlc["high"], df_ohlc["low"], df_ohlc["close"]).alias(
            "talib"
        ),
    ).select(((pl.col("expr") != pl.col("talib")).sum()).alias("not_eq"))["not_eq"][0]
    assert not_eq == 0


def test_cdlpiercing_eq(df_ohlc: pl.DataFrame):
    not_eq = df_ohlc.with_columns(
        pl.col("open").ta.cdlpiercing(pl.col("high"), pl.col("low"), pl.col("close")).alias("expr"),
        talib.CDLPIERCING(df_ohlc["open"], df_ohlc["high"], df_ohlc["low"], df_ohlc["close"]).alias(
            "talib"
        ),
    ).select(((pl.col("expr") != pl.col("talib")).sum()).alias("not_eq"))["not_eq"][0]
    assert not_eq == 0


def test_cdlrickshawman_eq(df_ohlc: pl.DataFrame):
    not_eq = df_ohlc.with_columns(
        pl.col("open")
        .ta.cdlrickshawman(pl.col("high"), pl.col("low"), pl.col("close"))
        .alias("expr"),
        talib.CDLRICKSHAWMAN(
            df_ohlc["open"], df_ohlc["high"], df_ohlc["low"], df_ohlc["close"]
        ).alias("talib"),
    ).select(((pl.col("expr") != pl.col("talib")).sum()).alias("not_eq"))["not_eq"][0]
    assert not_eq == 0


def test_cdlrisefall3methods_eq(df_ohlc: pl.DataFrame):
    not_eq = df_ohlc.with_columns(
        pl.col("open")
        .ta.cdlrisefall3methods(pl.col("high"), pl.col("low"), pl.col("close"))
        .alias("expr"),
        talib.CDLRISEFALL3METHODS(
            df_ohlc["open"], df_ohlc["high"], df_ohlc["low"], df_ohlc["close"]
        ).alias("talib"),
    ).select(((pl.col("expr") != pl.col("talib")).sum()).alias("not_eq"))["not_eq"][0]
    assert not_eq == 0


def test_cdlseparatinglines_eq(df_ohlc: pl.DataFrame):
    not_eq = df_ohlc.with_columns(
        pl.col("open")
        .ta.cdlseparatinglines(pl.col("high"), pl.col("low"), pl.col("close"))
        .alias("expr"),
        talib.CDLSEPARATINGLINES(
            df_ohlc["open"], df_ohlc["high"], df_ohlc["low"], df_ohlc["close"]
        ).alias("talib"),
    ).select(((pl.col("expr") != pl.col("talib")).sum()).alias("not_eq"))["not_eq"][0]
    assert not_eq == 0


def test_cdlshootingstar_eq(df_ohlc: pl.DataFrame):
    not_eq = df_ohlc.with_columns(
        pl.col("open")
        .ta.cdlshootingstar(pl.col("high"), pl.col("low"), pl.col("close"))
        .alias("expr"),
        talib.CDLSHOOTINGSTAR(
            df_ohlc["open"], df_ohlc["high"], df_ohlc["low"], df_ohlc["close"]
        ).alias("talib"),
    ).select(((pl.col("expr") != pl.col("talib")).sum()).alias("not_eq"))["not_eq"][0]
    assert not_eq == 0


def test_cdlshortline_eq(df_ohlc: pl.DataFrame):
    not_eq = df_ohlc.with_columns(
        pl.col("open")
        .ta.cdlshortline(pl.col("high"), pl.col("low"), pl.col("close"))
        .alias("expr"),
        talib.CDLSHORTLINE(
            df_ohlc["open"], df_ohlc["high"], df_ohlc["low"], df_ohlc["close"]
        ).alias("talib"),
    ).select(((pl.col("expr") != pl.col("talib")).sum()).alias("not_eq"))["not_eq"][0]
    assert not_eq == 0


def test_cdlspinningtop_eq(df_ohlc: pl.DataFrame):
    not_eq = df_ohlc.with_columns(
        pl.col("open")
        .ta.cdlspinningtop(pl.col("high"), pl.col("low"), pl.col("close"))
        .alias("expr"),
        talib.CDLSPINNINGTOP(
            df_ohlc["open"], df_ohlc["high"], df_ohlc["low"], df_ohlc["close"]
        ).alias("talib"),
    ).select(((pl.col("expr") != pl.col("talib")).sum()).alias("not_eq"))["not_eq"][0]
    assert not_eq == 0


def test_cdlstalledpattern_eq(df_ohlc: pl.DataFrame):
    not_eq = df_ohlc.with_columns(
        pl.col("open")
        .ta.cdlstalledpattern(pl.col("high"), pl.col("low"), pl.col("close"))
        .alias("expr"),
        talib.CDLSTALLEDPATTERN(
            df_ohlc["open"], df_ohlc["high"], df_ohlc["low"], df_ohlc["close"]
        ).alias("talib"),
    ).select(((pl.col("expr") != pl.col("talib")).sum()).alias("not_eq"))["not_eq"][0]
    assert not_eq == 0


def test_cdlsticksandwich_eq(df_ohlc: pl.DataFrame):
    not_eq = df_ohlc.with_columns(
        pl.col("open")
        .ta.cdlsticksandwich(pl.col("high"), pl.col("low"), pl.col("close"))
        .alias("expr"),
        talib.CDLSTICKSANDWICH(
            df_ohlc["open"], df_ohlc["high"], df_ohlc["low"], df_ohlc["close"]
        ).alias("talib"),
    ).select(((pl.col("expr") != pl.col("talib")).sum()).alias("not_eq"))["not_eq"][0]
    assert not_eq == 0


def test_cdltakuri_eq(df_ohlc: pl.DataFrame):
    not_eq = df_ohlc.with_columns(
        pl.col("open").ta.cdltakuri(pl.col("high"), pl.col("low"), pl.col("close")).alias("expr"),
        talib.CDLTAKURI(df_ohlc["open"], df_ohlc["high"], df_ohlc["low"], df_ohlc["close"]).alias(
            "talib"
        ),
    ).select(((pl.col("expr") != pl.col("talib")).sum()).alias("not_eq"))["not_eq"][0]
    assert not_eq == 0


def test_cdltasukigap_eq(df_ohlc: pl.DataFrame):
    not_eq = df_ohlc.with_columns(
        pl.col("open")
        .ta.cdltasukigap(pl.col("high"), pl.col("low"), pl.col("close"))
        .alias("expr"),
        talib.CDLTASUKIGAP(
            df_ohlc["open"], df_ohlc["high"], df_ohlc["low"], df_ohlc["close"]
        ).alias("talib"),
    ).select(((pl.col("expr") != pl.col("talib")).sum()).alias("not_eq"))["not_eq"][0]
    assert not_eq == 0


def test_cdlthrusting_eq(df_ohlc: pl.DataFrame):
    not_eq = df_ohlc.with_columns(
        pl.col("open")
        .ta.cdlthrusting(pl.col("high"), pl.col("low"), pl.col("close"))
        .alias("expr"),
        talib.CDLTHRUSTING(
            df_ohlc["open"], df_ohlc["high"], df_ohlc["low"], df_ohlc["close"]
        ).alias("talib"),
    ).select(((pl.col("expr") != pl.col("talib")).sum()).alias("not_eq"))["not_eq"][0]
    assert not_eq == 0


def test_cdltristar_eq(df_ohlc: pl.DataFrame):
    not_eq = df_ohlc.with_columns(
        pl.col("open").ta.cdltristar(pl.col("high"), pl.col("low"), pl.col("close")).alias("expr"),
        talib.CDLTRISTAR(df_ohlc["open"], df_ohlc["high"], df_ohlc["low"], df_ohlc["close"]).alias(
            "talib"
        ),
    ).select(((pl.col("expr") != pl.col("talib")).sum()).alias("not_eq"))["not_eq"][0]
    assert not_eq == 0


def test_cdlunique3river_eq(df_ohlc: pl.DataFrame):
    not_eq = df_ohlc.with_columns(
        pl.col("open")
        .ta.cdlunique3river(pl.col("high"), pl.col("low"), pl.col("close"))
        .alias("expr"),
        talib.CDLUNIQUE3RIVER(
            df_ohlc["open"], df_ohlc["high"], df_ohlc["low"], df_ohlc["close"]
        ).alias("talib"),
    ).select(((pl.col("expr") != pl.col("talib")).sum()).alias("not_eq"))["not_eq"][0]
    assert not_eq == 0


def test_cdlupsidegap2crows_eq(df_ohlc: pl.DataFrame):
    not_eq = df_ohlc.with_columns(
        pl.col("open")
        .ta.cdlupsidegap2crows(pl.col("high"), pl.col("low"), pl.col("close"))
        .alias("expr"),
        talib.CDLUPSIDEGAP2CROWS(
            df_ohlc["open"], df_ohlc["high"], df_ohlc["low"], df_ohlc["close"]
        ).alias("talib"),
    ).select(((pl.col("expr") != pl.col("talib")).sum()).alias("not_eq"))["not_eq"][0]
    assert not_eq == 0


def test_cdlxsidegap3methods_eq(df_ohlc: pl.DataFrame):
    not_eq = df_ohlc.with_columns(
        pl.col("open")
        .ta.cdlxsidegap3methods(pl.col("high"), pl.col("low"), pl.col("close"))
        .alias("expr"),
        talib.CDLXSIDEGAP3METHODS(
            df_ohlc["open"], df_ohlc["high"], df_ohlc["low"], df_ohlc["close"]
        ).alias("talib"),
    ).select(((pl.col("expr") != pl.col("talib")).sum()).alias("not_eq"))["not_eq"][0]
    assert not_eq == 0
