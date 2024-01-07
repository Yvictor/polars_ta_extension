
import polars as pl
import polars_talib
import talib


def test_ema_expr(benchmark, df_with_close: pl.DataFrame):
    
    @benchmark
    def ema_expr():
        df_with_close.select(
            pl.col("close").ta.ema(3)
        )


def test_ema_talib(benchmark, df_with_close: pl.DataFrame):
    
    @benchmark
    def ema_talib():
        df_with_close.select(
            talib.EMA(df_with_close["close"], timeperiod=3)
        )



def test_natr_expr(benchmark, df_ohlc: pl.DataFrame):
    
    @benchmark
    def natr():
        df_ohlc.select(
            pl.col("close").ta.natr(pl.col("high"), pl.col("low"), 3)
        )

def test_natr_talib(benchmark, df_ohlc: pl.DataFrame):
    @benchmark
    def natr():
        df_ohlc.select(
            talib.NATR(df_ohlc["high"], df_ohlc["low"], df_ohlc["close"], timeperiod=3)
        )

def test_natr_expr_with_null(benchmark, df_ohlc: pl.DataFrame):
    df_ohlc = df_ohlc.with_columns(
        pl.when(pl.col("close") > 0).then(pl.col("close")).otherwise(None).alias("close")
    )
    assert (df_ohlc.filter(
        pl.col("close").is_null()
    ).is_empty()) is False

    @benchmark
    def natr():
        df_ohlc.select(
            pl.col("close").ta.natr(pl.col("high"), pl.col("low"), 3)
        )
