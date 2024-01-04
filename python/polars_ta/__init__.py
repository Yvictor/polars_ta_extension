import atexit
import polars as pl
from polars.type_aliases import IntoExpr
from polars.utils.udfs import _get_shared_lib_location
from ._polars_ta import initialize, shutdown, version


__talib_version__ = version()

# Boilerplate needed to inform Polars of the location of binary wheel.
lib = _get_shared_lib_location(__file__)
initialize()
atexit.register(shutdown)

@pl.api.register_expr_namespace("ta")
class TAExpr:
    def __init__(self, expr: pl.Expr):
        self._expr = expr

    def bbands(
        self, timeperiod: int = 5, nbdevup: float = 2.0, nbdevdn: float = 2.0, ma_type: int = 0
    ) -> pl.Expr:
        """bbands"""
        return self._expr.register_plugin(
            lib=lib,
            args=[],
            kwargs={
                "timeperiod": timeperiod,
                "nbdevup": nbdevup,
                "nbdevdn": nbdevdn,
                "matype": ma_type,
            },
            symbol="bbands",
            is_elementwise=False,
        )

    def ema(
        self,
        timeperiod: int = 30,
    ) -> pl.Expr:
        """
        This example shows how arguments other than `Series` can be used.
        """
        return self._expr.register_plugin(
            lib=lib,
            args=[],
            kwargs={
                "timeperiod": timeperiod,
            },
            symbol="ema",
            is_elementwise=False,
        )

    def natr(
        self, high: IntoExpr = pl.col("high"), low: IntoExpr = pl.col("low"), timeperiod: int = 14
    ) -> pl.Expr:
        """Normalized Average True Range (Volatility Indicators)
        pl.col("close").ta.natr("high", "low", [, timeperiod=?])

        Inputs:
            prices: ['high', 'low', 'close']
        Parameters:
            timeperiod: 14
        Outputs:
            real
        """
        return self._expr.register_plugin(
            lib=lib,
            args=[high, low],
            kwargs={
                "timeperiod": timeperiod,
            },
            symbol="natr",
            is_elementwise=False,
        )

    def ht_dcperiod(self) -> pl.Expr:
        """Hilbert Transform - Dominant Cycle Period (Cycle Indicators)
        pl.col("close").ta.ht_dcperiod()

        Inputs:
            real: (any ndarray)
        Outputs:
            real
        """
        return self._expr.register_plugin(
            lib=lib,
            symbol="ht_dcperiod",
            is_elementwise=False,
        )

    def adx(
        self, high: IntoExpr = pl.col("high"), low: IntoExpr = pl.col("low"), timeperiod: int = 14
    ) -> pl.Expr:
        """Average Directional Movement Index (Momentum Indicators)
        pl.col("close").ta.adx("high", "low", [, timeperiod=?])

        Inputs:
            prices: ['high', 'low', 'close']
        Parameters:
            timeperiod: 14
        Outputs:
            real
        """
        return self._expr.register_plugin(
            lib=lib,
            args=[high, low],
            kwargs={
                "timeperiod": timeperiod,
            },
            symbol="adx",
            is_elementwise=False,
        )

    def aroon(self, low: IntoExpr = pl.col("low"), timeperiod: int = 14) -> pl.Expr:
        """Aroon (Momentum Indicators)
        pl.col("high").ta.aroon("low", [, timeperiod=?])
        Inputs:
            prices: ['high', 'low']
        Parameters:
            timeperiod: 14
        Outputs:
            aroondown
            aroonup
        """
        return self._expr.register_plugin(
            lib=lib,
            args=[low],
            kwargs={
                "timeperiod": timeperiod,
            },
            symbol="aroon",
            is_elementwise=False,
        )

    def cdl2crows(
        self,
        high: IntoExpr = pl.col("high"),
        low: IntoExpr = pl.col("low"),
        close: IntoExpr = pl.col("close"),
    ):
        """Two Crows (Pattern Recognition)
            pl.col("open").ta.cdl2crows(pl.col("high"), pl.col("low"), pl.col("close"))

        Inputs:
            prices: ['open', 'high', 'low', 'close']
        Outputs:
            integer (values are -100, 0 or 100)

        """
        return self._expr.register_plugin(
            lib=lib,
            args=[high, low, close],
            symbol="cdl2crows",
            is_elementwise=False,
        )

    def cdl3blackcrows(
        self,
        high: IntoExpr = pl.col("high"),
        low: IntoExpr = pl.col("low"),
        close: IntoExpr = pl.col("close"),
    ):
        """Three Black Crows (Pattern Recognition)
            pl.col("open").ta.cdl3blackcrows(pl.col("high"), pl.col("low"), pl.col("close"))

        Inputs:
            prices: ['open', 'high', 'low', 'close']
        Outputs:
            integer (values are -100, 0 or 100)

        """
        return self._expr.register_plugin(
            lib=lib,
            args=[high, low, close],
            symbol="cdl3blackcrows",
            is_elementwise=False,
        )

    def cdl3inside(
        self,
        high: IntoExpr = pl.col("high"),
        low: IntoExpr = pl.col("low"),
        close: IntoExpr = pl.col("close"),
    ):
        """Three Inside Up/Down (Pattern Recognition)
            pl.col("open").ta.cdl3inside(pl.col("high"), pl.col("low"), pl.col("close"))

        Inputs:
            prices: ['open', 'high', 'low', 'close']
        Outputs:
            integer (values are -100, 0 or 100)

        """
        return self._expr.register_plugin(
            lib=lib,
            args=[high, low, close],
            symbol="cdl3inside",
            is_elementwise=False,
        )

    def cdl3linestrike(
        self,
        high: IntoExpr = pl.col("high"),
        low: IntoExpr = pl.col("low"),
        close: IntoExpr = pl.col("close"),
    ):
        """Three-Line Strike  (Pattern Recognition)
            pl.col("open").ta.cdl3linestrike(pl.col("high"), pl.col("low"), pl.col("close"))

        Inputs:
            prices: ['open', 'high', 'low', 'close']
        Outputs:
            integer (values are -100, 0 or 100)

        """
        return self._expr.register_plugin(
            lib=lib,
            args=[high, low, close],
            symbol="cdl3linestrike",
            is_elementwise=False,
        )

    def cdl3outside(
        self,
        high: IntoExpr = pl.col("high"),
        low: IntoExpr = pl.col("low"),
        close: IntoExpr = pl.col("close"),
    ):
        """Three Outside Up/Down (Pattern Recognition)
            pl.col("open").ta.cdl3outside(pl.col("high"), pl.col("low"), pl.col("close"))

        Inputs:
            prices: ['open', 'high', 'low', 'close']
        Outputs:
            integer (values are -100, 0 or 100)

        """
        return self._expr.register_plugin(
            lib=lib,
            args=[high, low, close],
            symbol="cdl3outside",
            is_elementwise=False,
        )

    def cdl3starsinsouth(
        self,
        high: IntoExpr = pl.col("high"),
        low: IntoExpr = pl.col("low"),
        close: IntoExpr = pl.col("close"),
    ):
        """Three Stars In The South (Pattern Recognition)
            pl.col("open").ta.cdl3starsinsouth(pl.col("high"), pl.col("low"), pl.col("close"))

        Inputs:
            prices: ['open', 'high', 'low', 'close']
        Outputs:
            integer (values are -100, 0 or 100)

        """
        return self._expr.register_plugin(
            lib=lib,
            args=[high, low, close],
            symbol="cdl3starsinsouth",
            is_elementwise=False,
        )

    def cdl3whitesoldiers(
        self,
        high: IntoExpr = pl.col("high"),
        low: IntoExpr = pl.col("low"),
        close: IntoExpr = pl.col("close"),
    ):
        """Three Advancing White Soldiers (Pattern Recognition)
            pl.col("open").ta.cdl3whitesoldiers(pl.col("high"), pl.col("low"), pl.col("close"))

        Inputs:
            prices: ['open', 'high', 'low', 'close']
        Outputs:
            integer (values are -100, 0 or 100)

        """
        return self._expr.register_plugin(
            lib=lib,
            args=[high, low, close],
            symbol="cdl3whitesoldiers",
            is_elementwise=False,
        )

    def cdlabandonedbaby(
        self,
        high: IntoExpr = pl.col("high"),
        low: IntoExpr = pl.col("low"),
        close: IntoExpr = pl.col("close"),
        penetration: float = 0.3,
    ):
        """Abandoned Baby (Pattern Recognition)
            pl.col("open").ta.cdlabandonedbaby(pl.col("high"), pl.col("low"), pl.col("close"), penetration=0.3)

        Inputs:
            prices: ['open', 'high', 'low', 'close']
        Parameters:
            penetration: 0.3
        Outputs:
            integer (values are -100, 0 or 100)

        """
        return self._expr.register_plugin(
            lib=lib,
            args=[high, low, close],
            kwargs={
                "penetration": penetration,
            },
            symbol="cdlabandonedbaby",
            is_elementwise=False,
        )

    def cdladvanceblock(
        self,
        high: IntoExpr = pl.col("high"),
        low: IntoExpr = pl.col("low"),
        close: IntoExpr = pl.col("close"),
    ):
        """Advance Block (Pattern Recognition)
            pl.col("open").ta.cdladvanceblock(pl.col("high"), pl.col("low"), pl.col("close"))

        Inputs:
            prices: ['open', 'high', 'low', 'close']
        Outputs:
            integer (values are -100, 0 or 100)

        """
        return self._expr.register_plugin(
            lib=lib,
            args=[high, low, close],
            symbol="cdladvanceblock",
            is_elementwise=False,
        )

    def cdlbelthold(
        self,
        high: IntoExpr = pl.col("high"),
        low: IntoExpr = pl.col("low"),
        close: IntoExpr = pl.col("close"),
    ):
        """Belt-hold (Pattern Recognition)
            pl.col("open").ta.cdlbelthold(pl.col("high"), pl.col("low"), pl.col("close"))

        Inputs:
            prices: ['open', 'high', 'low', 'close']
        Outputs:
            integer (values are -100, 0 or 100)

        """
        return self._expr.register_plugin(
            lib=lib,
            args=[high, low, close],
            symbol="cdlbelthold",
            is_elementwise=False,
        )

    def cdlbreakaway(
        self,
        high: IntoExpr = pl.col("high"),
        low: IntoExpr = pl.col("low"),
        close: IntoExpr = pl.col("close"),
    ):
        """Breakaway (Pattern Recognition)
            pl.col("open").ta.cdlbreakaway(pl.col("high"), pl.col("low"), pl.col("close"))

        Inputs:
            prices: ['open', 'high', 'low', 'close']
        Outputs:
            integer (values are -100, 0 or 100)

        """
        return self._expr.register_plugin(
            lib=lib,
            args=[high, low, close],
            symbol="cdlbreakaway",
            is_elementwise=False,
        )

    def cdlclosingmarubozu(
        self,
        high: IntoExpr = pl.col("high"),
        low: IntoExpr = pl.col("low"),
        close: IntoExpr = pl.col("close"),
    ):
        """Closing Marubozu (Pattern Recognition)
            pl.col("open").ta.cdlclosingmarubozu(pl.col("high"), pl.col("low"), pl.col("close"))

        Inputs:
            prices: ['open', 'high', 'low', 'close']
        Outputs:
            integer (values are -100, 0 or 100)

        """
        return self._expr.register_plugin(
            lib=lib,
            args=[high, low, close],
            symbol="cdlclosingmarubozu",
            is_elementwise=False,
        )

    def cdlconcealbabyswall(
        self,
        high: IntoExpr = pl.col("high"),
        low: IntoExpr = pl.col("low"),
        close: IntoExpr = pl.col("close"),
    ):
        """Concealing Baby Swallow (Pattern Recognition)
            pl.col("open").ta.cdlconcealbabyswall(pl.col("high"), pl.col("low"), pl.col("close"))

        Inputs:
            prices: ['open', 'high', 'low', 'close']
        Outputs:
            integer (values are -100, 0 or 100)

        """
        return self._expr.register_plugin(
            lib=lib,
            args=[high, low, close],
            symbol="cdlconcealbabyswall",
            is_elementwise=False,
        )

    def cdlcounterattack(
        self,
        high: IntoExpr = pl.col("high"),
        low: IntoExpr = pl.col("low"),
        close: IntoExpr = pl.col("close"),
    ):
        """Counterattack (Pattern Recognition)
            pl.col("open").ta.cdlcounterattack(pl.col("high"), pl.col("low"), pl.col("close"))

        Inputs:
            prices: ['open', 'high', 'low', 'close']
        Outputs:
            integer (values are -100, 0 or 100)

        """
        return self._expr.register_plugin(
            lib=lib,
            args=[high, low, close],
            symbol="cdlcounterattack",
            is_elementwise=False,
        )

    def cdldarkcloudcover(
        self,
        high: IntoExpr = pl.col("high"),
        low: IntoExpr = pl.col("low"),
        close: IntoExpr = pl.col("close"),
        penetration: float = 0.3,
    ):
        """Dark Cloud Cover (Pattern Recognition)
            pl.col("open").ta.cdldarkcloudcover(pl.col("high"), pl.col("low"), pl.col("close"), penetration=0.3)

        Inputs:
            prices: ['open', 'high', 'low', 'close']
        Parameters:
            penetration: 0.5
        Outputs:
            integer (values are -100, 0 or 100)

        """
        return self._expr.register_plugin(
            lib=lib,
            args=[high, low, close],
            kwargs={
                "penetration": penetration,
            },
            symbol="cdldarkcloudcover",
            is_elementwise=False,
        )

    def cdldoji(
        self,
        high: IntoExpr = pl.col("high"),
        low: IntoExpr = pl.col("low"),
        close: IntoExpr = pl.col("close"),
    ):
        """Doji (Pattern Recognition)
            pl.col("open").ta.cdldoji(pl.col("high"), pl.col("low"), pl.col("close"))

        Inputs:
            prices: ['open', 'high', 'low', 'close']
        Outputs:
            integer (values are -100, 0 or 100)

        """
        return self._expr.register_plugin(
            lib=lib,
            args=[high, low, close],
            symbol="cdldoji",
            is_elementwise=False,
        )

    def cdldojistar(
        self,
        high: IntoExpr = pl.col("high"),
        low: IntoExpr = pl.col("low"),
        close: IntoExpr = pl.col("close"),
    ):
        """Doji Star (Pattern Recognition)
            pl.col("open").ta.cdldojistar(pl.col("high"), pl.col("low"), pl.col("close"))

        Inputs:
            prices: ['open', 'high', 'low', 'close']
        Outputs:
            integer (values are -100, 0 or 100)

        """
        return self._expr.register_plugin(
            lib=lib,
            args=[high, low, close],
            symbol="cdldojistar",
            is_elementwise=False,
        )

    def cdldragonflydoji(
        self,
        high: IntoExpr = pl.col("high"),
        low: IntoExpr = pl.col("low"),
        close: IntoExpr = pl.col("close"),
    ):
        """Dragonfly Doji (Pattern Recognition)
            pl.col("open").ta.cdldragonflydoji(pl.col("high"), pl.col("low"), pl.col("close"))

        Inputs:
            prices: ['open', 'high', 'low', 'close']
        Outputs:
            integer (values are -100, 0 or 100)

        """
        return self._expr.register_plugin(
            lib=lib,
            args=[high, low, close],
            symbol="cdldragonflydoji",
            is_elementwise=False,
        )

    def cdlengulfing(
        self,
        high: IntoExpr = pl.col("high"),
        low: IntoExpr = pl.col("low"),
        close: IntoExpr = pl.col("close"),
    ):
        """Engulfing Pattern (Pattern Recognition)
            pl.col("open").ta.cdlengulfing(pl.col("high"), pl.col("low"), pl.col("close"))

        Inputs:
            prices: ['open', 'high', 'low', 'close']
        Outputs:
            integer (values are -100, 0 or 100)

        """
        return self._expr.register_plugin(
            lib=lib,
            args=[high, low, close],
            symbol="cdlengulfing",
            is_elementwise=False,
        )

    def cdleveningdojistar(
        self,
        high: IntoExpr = pl.col("high"),
        low: IntoExpr = pl.col("low"),
        close: IntoExpr = pl.col("close"),
        penetration: float = 0.3,
    ):
        """Evening Doji Star (Pattern Recognition)
            pl.col("open").ta.cdleveningdojistar(pl.col("high"), pl.col("low"), pl.col("close"), penetration=0.3)

        Inputs:
            prices: ['open', 'high', 'low', 'close']
        Parameters:
            penetration: 0.3
        Outputs:
            integer (values are -100, 0 or 100)

        """
        return self._expr.register_plugin(
            lib=lib,
            args=[high, low, close],
            kwargs={
                "penetration": penetration,
            },
            symbol="cdleveningdojistar",
            is_elementwise=False,
        )

    def cdleveningstar(
        self,
        high: IntoExpr = pl.col("high"),
        low: IntoExpr = pl.col("low"),
        close: IntoExpr = pl.col("close"),
        penetration: float = 0.3,
    ):
        """Evening Star (Pattern Recognition)
            pl.col("open").ta.cdleveningstar(pl.col("high"), pl.col("low"), pl.col("close"), penetration=0.3)

        Inputs:
            prices: ['open', 'high', 'low', 'close']
        Parameters:
            penetration: 0.3
        Outputs:
            integer (values are -100, 0 or 100)

        """
        return self._expr.register_plugin(
            lib=lib,
            args=[high, low, close],
            kwargs={
                "penetration": penetration,
            },
            symbol="cdleveningstar",
            is_elementwise=False,
        )

    def cdlgapsidesidewhite(
        self,
        high: IntoExpr = pl.col("high"),
        low: IntoExpr = pl.col("low"),
        close: IntoExpr = pl.col("close"),
    ):
        """Up/Down-gap side-by-side white lines (Pattern Recognition)
            pl.col("open").ta.cdlgapsidesidewhite(pl.col("high"), pl.col("low"), pl.col("close"))

        Inputs:
            prices: ['open', 'high', 'low', 'close']
        Outputs:
            integer (values are -100, 0 or 100)

        """
        return self._expr.register_plugin(
            lib=lib,
            args=[high, low, close],
            symbol="cdlgapsidesidewhite",
            is_elementwise=False,
        )

    def cdlgravestonedoji(
        self,
        high: IntoExpr = pl.col("high"),
        low: IntoExpr = pl.col("low"),
        close: IntoExpr = pl.col("close"),
    ):
        """Gravestone Doji (Pattern Recognition)
            pl.col("open").ta.cdlgravestonedoji(pl.col("high"), pl.col("low"), pl.col("close"))

        Inputs:
            prices: ['open', 'high', 'low', 'close']
        Outputs:
            integer (values are -100, 0 or 100)

        """
        return self._expr.register_plugin(
            lib=lib,
            args=[high, low, close],
            symbol="cdlgravestonedoji",
            is_elementwise=False,
        )

    def cdlhammer(
        self,
        high: IntoExpr = pl.col("high"),
        low: IntoExpr = pl.col("low"),
        close: IntoExpr = pl.col("close"),
    ):
        """Hammer (Pattern Recognition)
            pl.col("open").ta.cdlhammer(pl.col("high"), pl.col("low"), pl.col("close"))

        Inputs:
            prices: ['open', 'high', 'low', 'close']
        Outputs:
            integer (values are -100, 0 or 100)

        """
        return self._expr.register_plugin(
            lib=lib,
            args=[high, low, close],
            symbol="cdlhammer",
            is_elementwise=False,
        )

    def cdlhangingman(
        self,
        high: IntoExpr = pl.col("high"),
        low: IntoExpr = pl.col("low"),
        close: IntoExpr = pl.col("close"),
    ):
        """Hanging Man (Pattern Recognition)
            pl.col("open").ta.cdlhangingman(pl.col("high"), pl.col("low"), pl.col("close"))

        Inputs:
            prices: ['open', 'high', 'low', 'close']
        Outputs:
            integer (values are -100, 0 or 100)

        """
        return self._expr.register_plugin(
            lib=lib,
            args=[high, low, close],
            symbol="cdlhangingman",
            is_elementwise=False,
        )

    def cdlharami(
        self,
        high: IntoExpr = pl.col("high"),
        low: IntoExpr = pl.col("low"),
        close: IntoExpr = pl.col("close"),
    ):
        """Harami Pattern (Pattern Recognition)
            pl.col("open").ta.cdlharami(pl.col("high"), pl.col("low"), pl.col("close"))

        Inputs:
            prices: ['open', 'high', 'low', 'close']
        Outputs:
            integer (values are -100, 0 or 100)

        """
        return self._expr.register_plugin(
            lib=lib,
            args=[high, low, close],
            symbol="cdlharami",
            is_elementwise=False,
        )

    def cdlharamicross(
        self,
        high: IntoExpr = pl.col("high"),
        low: IntoExpr = pl.col("low"),
        close: IntoExpr = pl.col("close"),
    ):
        """Harami Cross Pattern (Pattern Recognition)
            pl.col("open").ta.cdlharamicross(pl.col("high"), pl.col("low"), pl.col("close"))

        Inputs:
            prices: ['open', 'high', 'low', 'close']
        Outputs:
            integer (values are -100, 0 or 100)

        """
        return self._expr.register_plugin(
            lib=lib,
            args=[high, low, close],
            symbol="cdlharamicross",
            is_elementwise=False,
        )

    def cdlhighwave(
        self,
        high: IntoExpr = pl.col("high"),
        low: IntoExpr = pl.col("low"),
        close: IntoExpr = pl.col("close"),
    ):
        """High-Wave Candle (Pattern Recognition)
            pl.col("open").ta.cdlhighwave(pl.col("high"), pl.col("low"), pl.col("close"))

        Inputs:
            prices: ['open', 'high', 'low', 'close']
        Outputs:
            integer (values are -100, 0 or 100)

        """
        return self._expr.register_plugin(
            lib=lib,
            args=[high, low, close],
            symbol="cdlhighwave",
            is_elementwise=False,
        )

    def cdlhikkake(
        self,
        high: IntoExpr = pl.col("high"),
        low: IntoExpr = pl.col("low"),
        close: IntoExpr = pl.col("close"),
    ):
        """Hikkake Pattern (Pattern Recognition)
            pl.col("open").ta.cdlhikkake(pl.col("high"), pl.col("low"), pl.col("close"))

        Inputs:
            prices: ['open', 'high', 'low', 'close']
        Outputs:
            integer (values are -100, 0 or 100)

        """
        return self._expr.register_plugin(
            lib=lib,
            args=[high, low, close],
            symbol="cdlhikkake",
            is_elementwise=False,
        )

    def cdlhikkakemod(
        self,
        high: IntoExpr = pl.col("high"),
        low: IntoExpr = pl.col("low"),
        close: IntoExpr = pl.col("close"),
    ):
        """Modified Hikkake Pattern (Pattern Recognition)
            pl.col("open").ta.cdlhikkakemod(pl.col("high"), pl.col("low"), pl.col("close"))

        Inputs:
            prices: ['open', 'high', 'low', 'close']
        Outputs:
            integer (values are -100, 0 or 100)

        """
        return self._expr.register_plugin(
            lib=lib,
            args=[high, low, close],
            symbol="cdlhikkakemod",
            is_elementwise=False,
        )

    def cdlhomingpigeon(
        self,
        high: IntoExpr = pl.col("high"),
        low: IntoExpr = pl.col("low"),
        close: IntoExpr = pl.col("close"),
    ):
        """Homing Pigeon (Pattern Recognition)
            pl.col("open").ta.cdlhomingpigeon(pl.col("high"), pl.col("low"), pl.col("close"))

        Inputs:
            prices: ['open', 'high', 'low', 'close']
        Outputs:
            integer (values are -100, 0 or 100)

        """
        return self._expr.register_plugin(
            lib=lib,
            args=[high, low, close],
            symbol="cdlhomingpigeon",
            is_elementwise=False,
        )

    def cdlidentical3crows(
        self,
        high: IntoExpr = pl.col("high"),
        low: IntoExpr = pl.col("low"),
        close: IntoExpr = pl.col("close"),
    ):
        """Identical Three Crows (Pattern Recognition)
            pl.col("open").ta.cdlidentical3crows(pl.col("high"), pl.col("low"), pl.col("close"))

        Inputs:
            prices: ['open', 'high', 'low', 'close']
        Outputs:
            integer (values are -100, 0 or 100)

        """
        return self._expr.register_plugin(
            lib=lib,
            args=[high, low, close],
            symbol="cdlidentical3crows",
            is_elementwise=False,
        )

    def cdlinneck(
        self,
        high: IntoExpr = pl.col("high"),
        low: IntoExpr = pl.col("low"),
        close: IntoExpr = pl.col("close"),
    ):
        """In-Neck Pattern (Pattern Recognition)
            pl.col("open").ta.cdlinneck(pl.col("high"), pl.col("low"), pl.col("close"))

        Inputs:
            prices: ['open', 'high', 'low', 'close']
        Outputs:
            integer (values are -100, 0 or 100)

        """
        return self._expr.register_plugin(
            lib=lib,
            args=[high, low, close],
            symbol="cdlinneck",
            is_elementwise=False,
        )

    def cdlinvertedhammer(
        self,
        high: IntoExpr = pl.col("high"),
        low: IntoExpr = pl.col("low"),
        close: IntoExpr = pl.col("close"),
    ):
        """Inverted Hammer (Pattern Recognition)
            pl.col("open").ta.cdlinvertedhammer(pl.col("high"), pl.col("low"), pl.col("close"))

        Inputs:
            prices: ['open', 'high', 'low', 'close']
        Outputs:
            integer (values are -100, 0 or 100)

        """
        return self._expr.register_plugin(
            lib=lib,
            args=[high, low, close],
            symbol="cdlinvertedhammer",
            is_elementwise=False,
        )

    def cdlkicking(
        self,
        high: IntoExpr = pl.col("high"),
        low: IntoExpr = pl.col("low"),
        close: IntoExpr = pl.col("close"),
    ):
        """Kicking (Pattern Recognition)
            pl.col("open").ta.cdlkicking(pl.col("high"), pl.col("low"), pl.col("close"))

        Inputs:
            prices: ['open', 'high', 'low', 'close']
        Outputs:
            integer (values are -100, 0 or 100)

        """
        return self._expr.register_plugin(
            lib=lib,
            args=[high, low, close],
            symbol="cdlkicking",
            is_elementwise=False,
        )

    def cdlkickingbylength(
        self,
        high: IntoExpr = pl.col("high"),
        low: IntoExpr = pl.col("low"),
        close: IntoExpr = pl.col("close"),
    ):
        """Kicking - bull/bear determined by the longer marubozu (Pattern Recognition)
            pl.col("open").ta.cdlkickingbylength(pl.col("high"), pl.col("low"), pl.col("close"))

        Inputs:
            prices: ['open', 'high', 'low', 'close']
        Outputs:
            integer (values are -100, 0 or 100)

        """
        return self._expr.register_plugin(
            lib=lib,
            args=[high, low, close],
            symbol="cdlkickingbylength",
            is_elementwise=False,
        )

    def cdlladderbottom(
        self,
        high: IntoExpr = pl.col("high"),
        low: IntoExpr = pl.col("low"),
        close: IntoExpr = pl.col("close"),
    ):
        """Ladder Bottom (Pattern Recognition)
            pl.col("open").ta.cdlladderbottom(pl.col("high"), pl.col("low"), pl.col("close"))

        Inputs:
            prices: ['open', 'high', 'low', 'close']
        Outputs:
            integer (values are -100, 0 or 100)

        """
        return self._expr.register_plugin(
            lib=lib,
            args=[high, low, close],
            symbol="cdlladderbottom",
            is_elementwise=False,
        )

    def cdllongleggeddoji(
        self,
        high: IntoExpr = pl.col("high"),
        low: IntoExpr = pl.col("low"),
        close: IntoExpr = pl.col("close"),
    ):
        """Long Legged Doji (Pattern Recognition)
            pl.col("open").ta.cdllongleggeddoji(pl.col("high"), pl.col("low"), pl.col("close"))

        Inputs:
            prices: ['open', 'high', 'low', 'close']
        Outputs:
            integer (values are -100, 0 or 100)

        """
        return self._expr.register_plugin(
            lib=lib,
            args=[high, low, close],
            symbol="cdllongleggeddoji",
            is_elementwise=False,
        )

    def cdllongline(
        self,
        high: IntoExpr = pl.col("high"),
        low: IntoExpr = pl.col("low"),
        close: IntoExpr = pl.col("close"),
    ):
        """Long Line Candle (Pattern Recognition)
            pl.col("open").ta.cdllongline(pl.col("high"), pl.col("low"), pl.col("close"))

        Inputs:
            prices: ['open', 'high', 'low', 'close']
        Outputs:
            integer (values are -100, 0 or 100)

        """
        return self._expr.register_plugin(
            lib=lib,
            args=[high, low, close],
            symbol="cdllongline",
            is_elementwise=False,
        )

    def cdlmarubozu(
        self,
        high: IntoExpr = pl.col("high"),
        low: IntoExpr = pl.col("low"),
        close: IntoExpr = pl.col("close"),
    ):
        """Marubozu (Pattern Recognition)
            pl.col("open").ta.cdlmarubozu(pl.col("high"), pl.col("low"), pl.col("close"))

        Inputs:
            prices: ['open', 'high', 'low', 'close']
        Outputs:
            integer (values are -100, 0 or 100)

        """
        return self._expr.register_plugin(
            lib=lib,
            args=[high, low, close],
            symbol="cdlmarubozu",
            is_elementwise=False,
        )

    def cdlmatchinglow(
        self,
        high: IntoExpr = pl.col("high"),
        low: IntoExpr = pl.col("low"),
        close: IntoExpr = pl.col("close"),
    ):
        """Matching Low (Pattern Recognition)
            pl.col("open").ta.cdlmatchinglow(pl.col("high"), pl.col("low"), pl.col("close"))

        Inputs:
            prices: ['open', 'high', 'low', 'close']
        Outputs:
            integer (values are -100, 0 or 100)

        """
        return self._expr.register_plugin(
            lib=lib,
            args=[high, low, close],
            symbol="cdlmatchinglow",
            is_elementwise=False,
        )

    def cdlmathold(
        self,
        high: IntoExpr = pl.col("high"),
        low: IntoExpr = pl.col("low"),
        close: IntoExpr = pl.col("close"),
        penetration: float = 0.3,
    ):
        """Mat Hold (Pattern Recognition)
            pl.col("open").ta.cdlmathold(pl.col("high"), pl.col("low"), pl.col("close"), penetration=0.3)

        Inputs:
            prices: ['open', 'high', 'low', 'close']
        Parameters:
            penetration: 0.5
        Outputs:
            integer (values are -100, 0 or 100)

        """
        return self._expr.register_plugin(
            lib=lib,
            args=[high, low, close],
            kwargs={
                "penetration": penetration,
            },
            symbol="cdlmathold",
            is_elementwise=False,
        )

    def cdlmorningdojistar(
        self,
        high: IntoExpr = pl.col("high"),
        low: IntoExpr = pl.col("low"),
        close: IntoExpr = pl.col("close"),
        penetration: float = 0.3,
    ):
        """Morning Doji Star (Pattern Recognition)
            pl.col("open").ta.cdlmorningdojistar(pl.col("high"), pl.col("low"), pl.col("close"), penetration=0.3)

        Inputs:
            prices: ['open', 'high', 'low', 'close']
        Parameters:
            penetration: 0.3
        Outputs:
            integer (values are -100, 0 or 100)

        """
        return self._expr.register_plugin(
            lib=lib,
            args=[high, low, close],
            kwargs={
                "penetration": penetration,
            },
            symbol="cdlmorningdojistar",
            is_elementwise=False,
        )

    def cdlmorningstar(
        self,
        high: IntoExpr = pl.col("high"),
        low: IntoExpr = pl.col("low"),
        close: IntoExpr = pl.col("close"),
        penetration: float = 0.3,
    ):
        """Morning Star (Pattern Recognition)
            pl.col("open").ta.cdlmorningstar(pl.col("high"), pl.col("low"), pl.col("close"), penetration=0.3)

        Inputs:
            prices: ['open', 'high', 'low', 'close']
        Parameters:
            penetration: 0.3
        Outputs:
            integer (values are -100, 0 or 100)

        """
        return self._expr.register_plugin(
            lib=lib,
            args=[high, low, close],
            kwargs={
                "penetration": penetration,
            },
            symbol="cdlmorningstar",
            is_elementwise=False,
        )

    def cdlonneck(
        self,
        high: IntoExpr = pl.col("high"),
        low: IntoExpr = pl.col("low"),
        close: IntoExpr = pl.col("close"),
    ):
        """On-Neck Pattern (Pattern Recognition)
            pl.col("open").ta.cdlonneck(pl.col("high"), pl.col("low"), pl.col("close"))

        Inputs:
            prices: ['open', 'high', 'low', 'close']
        Outputs:
            integer (values are -100, 0 or 100)

        """
        return self._expr.register_plugin(
            lib=lib,
            args=[high, low, close],
            symbol="cdlonneck",
            is_elementwise=False,
        )

    def cdlpiercing(
        self,
        high: IntoExpr = pl.col("high"),
        low: IntoExpr = pl.col("low"),
        close: IntoExpr = pl.col("close"),
    ):
        """Piercing Pattern (Pattern Recognition)
            pl.col("open").ta.cdlpiercing(pl.col("high"), pl.col("low"), pl.col("close"))

        Inputs:
            prices: ['open', 'high', 'low', 'close']
        Outputs:
            integer (values are -100, 0 or 100)

        """
        return self._expr.register_plugin(
            lib=lib,
            args=[high, low, close],
            symbol="cdlpiercing",
            is_elementwise=False,
        )

    def cdlrickshawman(
        self,
        high: IntoExpr = pl.col("high"),
        low: IntoExpr = pl.col("low"),
        close: IntoExpr = pl.col("close"),
    ):
        """Rickshaw Man (Pattern Recognition)
            pl.col("open").ta.cdlrickshawman(pl.col("high"), pl.col("low"), pl.col("close"))

        Inputs:
            prices: ['open', 'high', 'low', 'close']
        Outputs:
            integer (values are -100, 0 or 100)

        """
        return self._expr.register_plugin(
            lib=lib,
            args=[high, low, close],
            symbol="cdlrickshawman",
            is_elementwise=False,
        )

    def cdlrisefall3methods(
        self,
        high: IntoExpr = pl.col("high"),
        low: IntoExpr = pl.col("low"),
        close: IntoExpr = pl.col("close"),
    ):
        """Rising/Falling Three Methods (Pattern Recognition)
            pl.col("open").ta.cdlrisefall3methods(pl.col("high"), pl.col("low"), pl.col("close"))

        Inputs:
            prices: ['open', 'high', 'low', 'close']
        Outputs:
            integer (values are -100, 0 or 100)

        """
        return self._expr.register_plugin(
            lib=lib,
            args=[high, low, close],
            symbol="cdlrisefall3methods",
            is_elementwise=False,
        )

    def cdlseparatinglines(
        self,
        high: IntoExpr = pl.col("high"),
        low: IntoExpr = pl.col("low"),
        close: IntoExpr = pl.col("close"),
    ):
        """Separating Lines (Pattern Recognition)
            pl.col("open").ta.cdlseparatinglines(pl.col("high"), pl.col("low"), pl.col("close"))

        Inputs:
            prices: ['open', 'high', 'low', 'close']
        Outputs:
            integer (values are -100, 0 or 100)

        """
        return self._expr.register_plugin(
            lib=lib,
            args=[high, low, close],
            symbol="cdlseparatinglines",
            is_elementwise=False,
        )

    def cdlshootingstar(
        self,
        high: IntoExpr = pl.col("high"),
        low: IntoExpr = pl.col("low"),
        close: IntoExpr = pl.col("close"),
    ):
        """Shooting Star (Pattern Recognition)
            pl.col("open").ta.cdlshootingstar(pl.col("high"), pl.col("low"), pl.col("close"))

        Inputs:
            prices: ['open', 'high', 'low', 'close']
        Outputs:
            integer (values are -100, 0 or 100)

        """
        return self._expr.register_plugin(
            lib=lib,
            args=[high, low, close],
            symbol="cdlshootingstar",
            is_elementwise=False,
        )

    def cdlshortline(
        self,
        high: IntoExpr = pl.col("high"),
        low: IntoExpr = pl.col("low"),
        close: IntoExpr = pl.col("close"),
    ):
        """Short Line Candle (Pattern Recognition)
            pl.col("open").ta.cdlshortline(pl.col("high"), pl.col("low"), pl.col("close"))

        Inputs:
            prices: ['open', 'high', 'low', 'close']
        Outputs:
            integer (values are -100, 0 or 100)

        """
        return self._expr.register_plugin(
            lib=lib,
            args=[high, low, close],
            symbol="cdlshortline",
            is_elementwise=False,
        )

    def cdlspinningtop(
        self,
        high: IntoExpr = pl.col("high"),
        low: IntoExpr = pl.col("low"),
        close: IntoExpr = pl.col("close"),
    ):
        """Spinning Top (Pattern Recognition)
            pl.col("open").ta.cdlspinningtop(pl.col("high"), pl.col("low"), pl.col("close"))

        Inputs:
            prices: ['open', 'high', 'low', 'close']
        Outputs:
            integer (values are -100, 0 or 100)

        """
        return self._expr.register_plugin(
            lib=lib,
            args=[high, low, close],
            symbol="cdlspinningtop",
            is_elementwise=False,
        )

    def cdlstalledpattern(
        self,
        high: IntoExpr = pl.col("high"),
        low: IntoExpr = pl.col("low"),
        close: IntoExpr = pl.col("close"),
    ):
        """Stalled Pattern (Pattern Recognition)
            pl.col("open").ta.cdlstalledpattern(pl.col("high"), pl.col("low"), pl.col("close"))

        Inputs:
            prices: ['open', 'high', 'low', 'close']
        Outputs:
            integer (values are -100, 0 or 100)

        """
        return self._expr.register_plugin(
            lib=lib,
            args=[high, low, close],
            symbol="cdlstalledpattern",
            is_elementwise=False,
        )

    def cdlsticksandwich(
        self,
        high: IntoExpr = pl.col("high"),
        low: IntoExpr = pl.col("low"),
        close: IntoExpr = pl.col("close"),
    ):
        """Stick Sandwich (Pattern Recognition)
            pl.col("open").ta.cdlsticksandwich(pl.col("high"), pl.col("low"), pl.col("close"))

        Inputs:
            prices: ['open', 'high', 'low', 'close']
        Outputs:
            integer (values are -100, 0 or 100)

        """
        return self._expr.register_plugin(
            lib=lib,
            args=[high, low, close],
            symbol="cdlsticksandwich",
            is_elementwise=False,
        )

    def cdltakuri(
        self,
        high: IntoExpr = pl.col("high"),
        low: IntoExpr = pl.col("low"),
        close: IntoExpr = pl.col("close"),
    ):
        """Takuri (Dragonfly Doji with very long lower shadow) (Pattern Recognition)
            pl.col("open").ta.cdltakuri(pl.col("high"), pl.col("low"), pl.col("close"))

        Inputs:
            prices: ['open', 'high', 'low', 'close']
        Outputs:
            integer (values are -100, 0 or 100)

        """
        return self._expr.register_plugin(
            lib=lib,
            args=[high, low, close],
            symbol="cdltakuri",
            is_elementwise=False,
        )

    def cdltasukigap(
        self,
        high: IntoExpr = pl.col("high"),
        low: IntoExpr = pl.col("low"),
        close: IntoExpr = pl.col("close"),
    ):
        """Tasuki Gap (Pattern Recognition)
            pl.col("open").ta.cdltasukigap(pl.col("high"), pl.col("low"), pl.col("close"))

        Inputs:
            prices: ['open', 'high', 'low', 'close']
        Outputs:
            integer (values are -100, 0 or 100)

        """
        return self._expr.register_plugin(
            lib=lib,
            args=[high, low, close],
            symbol="cdltasukigap",
            is_elementwise=False,
        )

    def cdlthrusting(
        self,
        high: IntoExpr = pl.col("high"),
        low: IntoExpr = pl.col("low"),
        close: IntoExpr = pl.col("close"),
    ):
        """Thrusting Pattern (Pattern Recognition)
            pl.col("open").ta.cdlthrusting(pl.col("high"), pl.col("low"), pl.col("close"))

        Inputs:
            prices: ['open', 'high', 'low', 'close']
        Outputs:
            integer (values are -100, 0 or 100)

        """
        return self._expr.register_plugin(
            lib=lib,
            args=[high, low, close],
            symbol="cdlthrusting",
            is_elementwise=False,
        )

    def cdltristar(
        self,
        high: IntoExpr = pl.col("high"),
        low: IntoExpr = pl.col("low"),
        close: IntoExpr = pl.col("close"),
    ):
        """Tristar Pattern (Pattern Recognition)
            pl.col("open").ta.cdltristar(pl.col("high"), pl.col("low"), pl.col("close"))

        Inputs:
            prices: ['open', 'high', 'low', 'close']
        Outputs:
            integer (values are -100, 0 or 100)

        """
        return self._expr.register_plugin(
            lib=lib,
            args=[high, low, close],
            symbol="cdltristar",
            is_elementwise=False,
        )

    def cdlunique3river(
        self,
        high: IntoExpr = pl.col("high"),
        low: IntoExpr = pl.col("low"),
        close: IntoExpr = pl.col("close"),
    ):
        """Unique 3 River (Pattern Recognition)
            pl.col("open").ta.cdlunique3river(pl.col("high"), pl.col("low"), pl.col("close"))

        Inputs:
            prices: ['open', 'high', 'low', 'close']
        Outputs:
            integer (values are -100, 0 or 100)

        """
        return self._expr.register_plugin(
            lib=lib,
            args=[high, low, close],
            symbol="cdlunique3river",
            is_elementwise=False,
        )

    def cdlupsidegap2crows(
        self,
        high: IntoExpr = pl.col("high"),
        low: IntoExpr = pl.col("low"),
        close: IntoExpr = pl.col("close"),
    ):
        """Upside Gap Two Crows (Pattern Recognition)
            pl.col("open").ta.cdlupsidegap2crows(pl.col("high"), pl.col("low"), pl.col("close"))

        Inputs:
            prices: ['open', 'high', 'low', 'close']
        Outputs:
            integer (values are -100, 0 or 100)

        """
        return self._expr.register_plugin(
            lib=lib,
            args=[high, low, close],
            symbol="cdlupsidegap2crows",
            is_elementwise=False,
        )

    def cdlxsidegap3methods(
        self,
        high: IntoExpr = pl.col("high"),
        low: IntoExpr = pl.col("low"),
        close: IntoExpr = pl.col("close"),
    ):
        """Upside/Downside Gap Three Methods (Pattern Recognition)
            pl.col("open").ta.cdlxsidegap3methods(pl.col("high"), pl.col("low"), pl.col("close"))

        Inputs:
            prices: ['open', 'high', 'low', 'close']
        Outputs:
            integer (values are -100, 0 or 100)

        """
        return self._expr.register_plugin(
            lib=lib,
            args=[high, low, close],
            symbol="cdlxsidegap3methods",
            is_elementwise=False,
        )

    def avgprice(
        self,
        high: IntoExpr = pl.col("high"),
        low: IntoExpr = pl.col("low"),
        close: IntoExpr = pl.col("close"),
    ):
        """Average Price (Price Transform)

        pl.col("close").ta.avgprice("high", "low", "close")

        Inputs:
            prices: ['open', 'high', 'low', 'close']
        Outputs:
            real
        """
        return self._expr.register_plugin(
            lib=lib,
            args=[high, low, close],
            symbol="avgprice",
            is_elementwise=False,
        )

    def medprice(self, low: IntoExpr = pl.col("low")):
        """Median Price (Price Transform)
        pl.col("high").ta.medprice("low")

        Inputs:
            prices: ['high', 'low']
        Outputs:
            real
        """
        return self._expr.register_plugin(
            lib=lib,
            args=[low],
            symbol="medprice",
            is_elementwise=False,
        )

    def typprice(self, high: IntoExpr = pl.col("high"), low: IntoExpr = pl.col("low")):
        """Typical Price (Price Transform)
        pl.col("close").ta.typprice("high", "low")

        Inputs:
            prices: ['high', 'low', 'close']
        Outputs:
            real
        """
        return self._expr.register_plugin(
            lib=lib,
            args=[high, low],
            symbol="typprice",
            is_elementwise=False,
        )

    def wclprice(self, high: IntoExpr = pl.col("high"), low: IntoExpr = pl.col("low")):
        """Weighted Close Price (Price Transform)
        pl.col("close").ta.wclprice("high", "low")

        Inputs:
            prices: ['high', 'low', 'close']
        Outputs:
            real
        """
        return self._expr.register_plugin(
            lib=lib,
            args=[high, low],
            symbol="wclprice",
            is_elementwise=False,
        )

    def beta(self, real: IntoExpr, timeperiod: int = 5):
        """Beta (Statistic Functions)
        pl.col("close").ta.beta(pl.col("high"), timeperiod=5)
        Inputs:
            real0
            real1
        Parameters:
            timeperiod: 5
        Outputs:
            real
        """
        return self._expr.register_plugin(
            lib=lib,
            args=[real],
            kwargs={
                "timeperiod": timeperiod,
            },
            symbol="beta",
            is_elementwise=False,
        )

    def correl(self, real: IntoExpr, timeperiod: int = 30):
        """Pearson's Correlation Coefficient (r) (Statistic Functions)
        pl.col("close").ta.correl(pl.col("high"), timeperiod=30)
        Inputs:
            real0
            real1
        Parameters:
            timeperiod: 30
        Outputs:
            real
        """
        return self._expr.register_plugin(
            lib=lib,
            args=[real],
            kwargs={
                "timeperiod": timeperiod,
            },
            symbol="correl",
            is_elementwise=False,
        )

    def linearreg(self, timeperiod: int = 14):
        """Linear Regression (Statistic Functions)
        pl.col("close").ta.linearreg(timeperiod=14)
        Inputs:
            real
        Parameters:
            timeperiod: 14
        Outputs:
            real
        """
        return self._expr.register_plugin(
            lib=lib,
            args=[],
            kwargs={
                "timeperiod": timeperiod,
            },
            symbol="linearreg",
            is_elementwise=False,
        )

    def linearreg_angle(self, timeperiod: int = 14):
        """Linear Regression Angle (Statistic Functions)
        pl.col("close").ta.linearreg_angle(timeperiod=14)
        Inputs:
            real
        Parameters:
            timeperiod: 14
        Outputs:
            real
        """
        return self._expr.register_plugin(
            lib=lib,
            args=[],
            kwargs={
                "timeperiod": timeperiod,
            },
            symbol="linearreg_angle",
            is_elementwise=False,
        )

    def linearreg_intercept(self, timeperiod: int = 14):
        """Linear Regression Intercept (Statistic Functions)
        pl.col("close").ta.linearreg_intercept(timeperiod=14)
        Inputs:
            real
        Parameters:
            timeperiod: 14
        Outputs:
            real
        """
        return self._expr.register_plugin(
            lib=lib,
            args=[],
            kwargs={
                "timeperiod": timeperiod,
            },
            symbol="linearreg_intercept",
            is_elementwise=False,
        )

    def linearreg_slope(self, timeperiod: int = 14):
        """Linear Regression Slope (Statistic Functions)
        pl.col("close").ta.linearreg_slope(timeperiod=14)
        Inputs:
            real
        Parameters:
            timeperiod: 14
        Outputs:
            real
        """
        return self._expr.register_plugin(
            lib=lib,
            args=[],
            kwargs={
                "timeperiod": timeperiod,
            },
            symbol="linearreg_slope",
            is_elementwise=False,
        )

    def stddev(self, timeperiod: int = 5, nbdev: float = 1.0):
        """Standard Deviation (Statistic Functions)
        pl.col("close").ta.stddev(timeperiod=5, nbdev=1.0)
        Inputs:
            real
        Parameters:
            timeperiod: 5
            nbdev: 1.0
        Outputs:
            real
        """
        return self._expr.register_plugin(
            lib=lib,
            args=[],
            kwargs={
                "timeperiod": timeperiod,
                "nbdev": nbdev,
            },
            symbol="stddev",
            is_elementwise=False,
        )

    def tsf(self, timeperiod: int = 14):
        """Time Series Forecast (Statistic Functions)
        pl.col("close").ta.tsf(timeperiod=14)
        Inputs:
            real
        Parameters:
            timeperiod: 14
        Outputs:
            real
        """
        return self._expr.register_plugin(
            lib=lib,
            args=[],
            kwargs={
                "timeperiod": timeperiod,
            },
            symbol="tsf",
            is_elementwise=False,
        )

    def var(self, timeperiod: int = 5, nbdev: float = 1.0):
        """Variance (Statistic Functions)
        pl.col("close").ta.var(timeperiod=5, nbdev=1.0)
        Inputs:
            real
        Parameters:
            timeperiod: 5
            nbdev: 1.0
        Outputs:
            real
        """
        return self._expr.register_plugin(
            lib=lib,
            args=[],
            kwargs={
                "timeperiod": timeperiod,
                "nbdev": nbdev,
            },
            symbol="var",
            is_elementwise=False,
        )

    def obv(self, volume: IntoExpr = pl.col("volume")):
        """OBV(close, volume)

        On Balance Volume (Volume Indicators)

        Inputs:
            prices: ['close', 'volume']
        Outputs:
            real
        """
        return self._expr.register_plugin(
            lib=lib,
            args=[volume],
            symbol="obv",
            is_elementwise=False,
        )

    def ad(
        self,
        high: IntoExpr = pl.col("high"),
        low: IntoExpr = pl.col("low"),
        volume: IntoExpr = pl.col("volume"),
    ):
        """Chaikin A/D Line (Volume Indicators)
        pl.col("close").ta.ad(pl.col("high"), pl.col("low"), pl.col("volume"))

        """
        return self._expr.register_plugin(
            lib=lib,
            args=[high, low, volume],
            symbol="ad",
            is_elementwise=False,
        )

    def adosc(
        self,
        high: IntoExpr = pl.col("high"),
        low: IntoExpr = pl.col("low"),
        volume: IntoExpr = pl.col("volume"),
        fastperiod: int = 3,
        slowperiod: int = 10,
    ):
        """Chaikin A/D Oscillator (Volume Indicators)
        pl.col("close").ta.adosc(pl.col("high"), pl.col("low"), pl.col("volume"), timeperiod=3)

        Parameters:
            fastperiod: 3
            slowperiod: 10
        Outputs:
            real
        """
        return self._expr.register_plugin(
            lib=lib,
            args=[high, low, volume],
            kwargs={
                "fastperiod": fastperiod,
                "slowperiod": slowperiod,
            },
            symbol="adosc",
            is_elementwise=False,
        )

    def atr(
        self, high: IntoExpr = pl.col("high"), low: IntoExpr = pl.col("low"), timeperiod: int = 14
    ):
        """Average True Range (Volatility Indicators)
        pl.col("close").ta.atr("high", "low", [, timeperiod=?])

        Inputs:
            prices: ['high', 'low', 'close']
        Parameters:
            timeperiod: 14
        Outputs:
            real
        """
        return self._expr.register_plugin(
            lib=lib,
            args=[high, low],
            kwargs={
                "timeperiod": timeperiod,
            },
            symbol="atr",
            is_elementwise=False,
        )

    def trange(self, high: IntoExpr = pl.col("high"), low: IntoExpr = pl.col("low")) -> pl.Expr:
        """True Range (Volatility Indicators)
        pl.col("close").ta.trange("high", "low")

        Inputs:
            prices: ['high', 'low', 'close']
        Outputs:
            real
        """
        return self._expr.register_plugin(
            lib=lib,
            args=[high, low],
            symbol="trange",
            is_elementwise=False,
        )
