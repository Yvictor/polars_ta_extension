import polars as pl
import polars_ta
import talib


def test_ema_eq():
    data = [8843.0, 8810.0, 8850.0, 8829.0, 9200.0, 8951.0, 9190.0, 9115.0, 9073.0, 9230.0]
    ser = pl.Series("close", data)
    df = pl.DataFrame([ser])
    not_eq = df.with_columns(
        pl.col("close").ta.ema(3).alias("ema3"),
        talib.EMA(df["close"], timeperiod=3).alias("EMA3"),
    ).select(((pl.col("ema3") != pl.col("EMA3")).sum()).alias("not_eq"))["not_eq"][0]
    assert not_eq == 0


def test_ema2_eq():
    data = [8843.0, 8810.0, 8850.0, 8829.0, 9200.0, 8951.0, 9190.0, 9115.0, 9073.0, 9230.0]
    ser = pl.Series("close", data)
    df = pl.DataFrame([ser])
    not_eq = df.with_columns(
        pl.col("close").ta.ema2(3).alias("ema3"),
        talib.EMA(df["close"], timeperiod=3).alias("EMA3"),
    ).select(((pl.col("ema3") != pl.col("EMA3")).sum()).alias("not_eq"))["not_eq"][0]
    assert not_eq == 0
