import polars as pl
from polars.type_aliases import IntoExpr
from polars.utils.udfs import _get_shared_lib_location

# Boilerplate needed to inform Polars of the location of binary wheel.
lib = _get_shared_lib_location(__file__)


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

    def cdlabandonedbaby(
        self,
        high: IntoExpr = pl.col("high"),
        low: IntoExpr = pl.col("low"),
        close: IntoExpr = pl.col("close"),
        penetration: float = 0.3,
    ):
        """CDLABANDONEDBABY(open, high, low, close[, penetration=?])

        Abandoned Baby (Pattern Recognition)

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
