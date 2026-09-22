
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


def test_macd_expr(benchmark, df_with_close: pl.DataFrame):
    @benchmark
    def macd_expr():
        df_with_close.select(pl.col("close").ta.macd(12, 26, 9))


def test_macd_talib(benchmark, df_with_close: pl.DataFrame):
    @benchmark
    def macd_talib():
        talib.MACD(df_with_close["close"], fastperiod=12, slowperiod=26, signalperiod=9)


def test_rsi_expr(benchmark, df_with_close: pl.DataFrame):
    @benchmark
    def rsi_expr():
        df_with_close.select(pl.col("close").ta.rsi(14))


def test_rsi_talib(benchmark, df_with_close: pl.DataFrame):
    @benchmark
    def rsi_talib():
        talib.RSI(df_with_close["close"], timeperiod=14)


def test_kdj_expr(benchmark, df_ohlc: pl.DataFrame):
    @benchmark
    def kdj_expr():
        df_ohlc.select(pl.col("close").ta.kdj(pl.col("high"), pl.col("low")))


def test_kdj_talib(benchmark, df_ohlc: pl.DataFrame):
    @benchmark
    def kdj_talib():
        talib.KDJ(df_ohlc["high"], df_ohlc["low"], df_ohlc["close"])


def test_supertrend_expr(benchmark, df_ohlc: pl.DataFrame):
    @benchmark
    def supertrend_expr():
        df_ohlc.select(pl.col("close").ta.supertrend(pl.col("high"), pl.col("low"), 10, 3.0))


def test_supertrend_talib(benchmark, df_ohlc: pl.DataFrame):
    @benchmark
    def supertrend_talib():
        talib.SUPERTREND(df_ohlc["high"], df_ohlc["low"], df_ohlc["close"], timeperiod=10, multiplier=3.0)


def test_cdlengulfing_expr(benchmark, df_ohlc: pl.DataFrame):
    @benchmark
    def cdlengulfing_expr():
        df_ohlc.select(pl.col("open").ta.cdlengulfing(pl.col("high"), pl.col("low"), pl.col("close")))


def test_cdlengulfing_talib(benchmark, df_ohlc: pl.DataFrame):
    @benchmark
    def cdlengulfing_talib():
        talib.CDLENGULFING(df_ohlc["open"], df_ohlc["high"], df_ohlc["low"], df_ohlc["close"])


def test_multi_symbol_pipeline_expr(benchmark, df_multi_symbol: pl.DataFrame):
    @benchmark
    def pipeline_expr():
        df_multi_symbol.select(
            pl.col("close").ta.sma(5).over("symbol").alias("sma5"),
            pl.col("close").ta.macd(12, 26, 9).over("symbol").alias("macd"),
            pl.col("close").ta.kdj(pl.col("high"), pl.col("low")).over("symbol").alias("kdj"),
            pl.col("close").ta.atr(pl.col("high"), pl.col("low"), 14).over("symbol").alias("atr"),
        )
