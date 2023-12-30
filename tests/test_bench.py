
import polars as pl
import polars_ta
import talib


def test_ema_expr(benchmark, df_with_close: pl.DataFrame):
    
    @benchmark
    def ema_expr():
        df_with_close.select(
            pl.col("close").ta.ema(3)
        )

def test_ema2_expr(benchmark, df_with_close: pl.DataFrame):
    
    @benchmark
    def ema2_expr():
        df_with_close.select(
            pl.col("close").ta.ema2(3)
        )



def test_ema_talib(benchmark, df_with_close: pl.DataFrame):
    
    @benchmark
    def ema_talib():
        df_with_close.select(
            talib.EMA(df_with_close["close"], timeperiod=3)
        )
