import pytest
import polars as pl
import polars_ta as plta
import talib


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

def test_ema_eq(df_ohlc: pl.DataFrame):
    not_eq = df_ohlc.with_columns(
        pl.col("close").ta.ema(3).alias("ema3"),
        talib.EMA(df_ohlc["close"], timeperiod=3).alias("EMA3"),
    ).select(((pl.col("ema3") != pl.col("EMA3")).sum()).alias("not_eq"))["not_eq"][0]
    assert not_eq == 0


def test_ht_dcperiod_eq(df_ohlc: pl.DataFrame):
    not_eq = df_ohlc.with_columns(
        pl.col("close").ta.ht_dcperiod().alias("expr"),
        talib.HT_DCPERIOD(df_ohlc["close"]).alias("talib"),
    ).select(((pl.col("expr") != pl.col("talib")).sum()).alias("not_eq"))["not_eq"][0]
    assert not_eq == 0


def test_adx_eq(df_ohlc: pl.DataFrame):
    not_eq = df_ohlc.with_columns(
        pl.col("close").ta.adx(pl.col("high"), pl.col("low"), 3).alias("expr"),
        talib.ADX(df_ohlc["high"], df_ohlc["low"], df_ohlc["close"], timeperiod=3).alias("talib"),
    ).select(((pl.col("expr") != pl.col("talib")).sum()).alias("not_eq"))["not_eq"][0]
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
        pl.col("high").ta.ad(pl.col("low"), pl.col("close"), pl.col("volume")).alias("expr"),
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
