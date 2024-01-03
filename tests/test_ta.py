import pytest
import polars as pl
import polars_ta
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


def test_ema_eq(df_ohlc: pl.DataFrame):
    not_eq = df_ohlc.with_columns(
        pl.col("close").ta.ema(3).alias("ema3"),
        talib.EMA(df_ohlc["close"], timeperiod=3).alias("EMA3"),
    ).select(((pl.col("ema3") != pl.col("EMA3")).sum()).alias("not_eq"))["not_eq"][0]
    assert not_eq == 0


def test_natr_eq(df_ohlc: pl.DataFrame):
    not_eq = df_ohlc.with_columns(
        pl.col("close").ta.natr(pl.col("high"), pl.col("low"), 3).alias("expr"),
        talib.NATR(df_ohlc["high"], df_ohlc["low"], df_ohlc["close"], timeperiod=3).alias("talib"),
    ).select(((pl.col("expr") != pl.col("talib")).sum()).alias("not_eq"))["not_eq"][0]
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


def test_obv_eq(df_ohlc: pl.DataFrame):
    not_eq = df_ohlc.with_columns(
        pl.col("close").ta.obv(pl.col("volume")).alias("expr"),
        talib.OBV(df_ohlc["close"], df_ohlc["volume"]).alias("talib"),
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
        pl.col("close").ta.adosc(pl.col("high"), pl.col("low"), pl.col("volume"), fastperiod=3, slowperiod=10).alias("expr"),
        talib.ADOSC(df_ohlc["high"], df_ohlc["low"], df_ohlc["close"], df_ohlc["volume"], fastperiod=3, slowperiod=10).alias(
            "talib"
        ),
    ).select(((pl.col("expr") != pl.col("talib")).sum()).alias("not_eq"))["not_eq"][0]
    assert not_eq == 0

