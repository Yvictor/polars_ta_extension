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

def test_ta_has_impl():
    pass


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
        talib.CCI(df_ohlc["high"], df_ohlc["low"], df_ohlc["close"], timeperiod=3).alias(
            "talib"
        ),
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
        talib.DX(df_ohlc["high"], df_ohlc["low"], df_ohlc["close"], timeperiod=3).alias(
            "talib"
        ),
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
        .struct.field("macd").alias("expr"),
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
        .struct.field("macdsignal").alias("expr"),
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
        .struct.field("macdhist").alias("expr"),
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
        talib.MFI(df_ohlc["high"], df_ohlc["low"], df_ohlc["close"], df_ohlc["volume"], timeperiod=3).alias(
            "talib"
        ),
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
        talib.MINUS_DM(df_ohlc["high"], df_ohlc["low"], timeperiod=3).alias(
            "talib"
        ),
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
        talib.PLUS_DM(df_ohlc["high"], df_ohlc["low"], timeperiod=3).alias(
            "talib"
        ),
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
        pl.col("close").ta.stochf(pl.col("high"), pl.col("low"), 3, 10, 0).struct.field("fastk").alias("expr"),
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
        pl.col("close").ta.stochf(pl.col("high"), pl.col("low"), 3, 10, 0).struct.field("fastd").alias("expr"),
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
        talib.WILLR(df_ohlc["high"], df_ohlc["low"], df_ohlc["close"], timeperiod=3).alias(
            "talib"
        ),
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


def test_ht_dcperiod_eq(df_ohlc: pl.DataFrame):
    not_eq = df_ohlc.with_columns(
        pl.col("close").ta.ht_dcperiod().alias("expr"),
        talib.HT_DCPERIOD(df_ohlc["close"]).alias("talib"),
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
