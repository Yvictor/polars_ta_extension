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

    def ht_dcphase(self) -> pl.Expr:
        """Hilbert Transform - Dominant Cycle Phase (Cycle Indicators)
        pl.col("close").ta.ht_dcphase()

        Inputs:
            real: (any ndarray)
        Outputs:
            real
        """
        return self._expr.register_plugin(
            lib=lib,
            symbol="ht_dcphase",
            is_elementwise=False,
        )

    def ht_phasor(self) -> pl.Expr:
        """Hilbert Transform - Phasor Components (Cycle Indicators)
        pl.col("close").ta.ht_phasor()

        Inputs:
            real: (any ndarray)
        Outputs:
            inphase
            quadrature
        """
        return self._expr.register_plugin(
            lib=lib,
            symbol="ht_phasor",
            is_elementwise=False,
        )

    def ht_sine(self) -> pl.Expr:
        """Hilbert Transform - SineWave (Cycle Indicators)
        pl.col("close").ta.ht_sine()

        Inputs:
            real: (any ndarray)
        Outputs:
            sine
            leadsine
        """
        return self._expr.register_plugin(
            lib=lib,
            symbol="ht_sine",
            is_elementwise=False,
        )

    def ht_trendmode(self) -> pl.Expr:
        """Hilbert Transform - Trend vs Cycle Mode (Cycle Indicators)
        pl.col("close").ta.ht_trendmode()

        Inputs:
            real: (any ndarray)
        Outputs:
            integer
        """
        return self._expr.register_plugin(
            lib=lib,
            symbol="ht_trendmode",
            is_elementwise=False,
        )

    def add(self, b: IntoExpr) -> pl.Expr:
        """Vectorized addition
        pl.col("a").ta.add(pl.col("b"))

        Inputs:
            a: (any ndarray)
            b: (any ndarray)
        Outputs:
            real
        """
        return self._expr.register_plugin(
            lib=lib,
            args=[b],
            symbol="add",
            is_elementwise=False,
        )

    def div(self, b: IntoExpr) -> pl.Expr:
        """Vectorized division
        pl.col("a").ta.div(pl.col("b"))

        Inputs:
            a: (any ndarray)
            b: (any ndarray)
        Outputs:
            real
        """
        return self._expr.register_plugin(
            lib=lib,
            args=[b],
            symbol="div",
            is_elementwise=False,
        )

    def max(self, timeperiod: int = 30) -> pl.Expr:
        """Highest value over a specified period (Math Operators)
        pl.col("close").ta.max(timeperiod=30)

        Inputs:
            prices: ['close']
        Parameters:
            timeperiod: 30
        Outputs:
            real
        """
        return self._expr.register_plugin(
            lib=lib,
            args=[],
            kwargs={"timeperiod": timeperiod},
            symbol="max",
            is_elementwise=False,
        )

    def maxindex(self, timeperiod: int = 30) -> pl.Expr:
        """Index of highest value over a specified period (Math Operators)
        pl.col("close").ta.maxindex(timeperiod=30)

        Inputs:
            prices: ['close']
        Parameters:
            timeperiod: 30
        Outputs:
            integer
        """
        return self._expr.register_plugin(
            lib=lib,
            args=[],
            kwargs={"timeperiod": timeperiod},
            symbol="maxindex",
            is_elementwise=False,
        )

    def min(self, timeperiod: int = 30) -> pl.Expr:
        """Lowest value over a specified period (Math Operators)
        pl.col("close").ta.min(timeperiod=30)

        Inputs:
            prices: ['close']
        Parameters:
            timeperiod: 30
        Outputs:
            real
        """
        return self._expr.register_plugin(
            lib=lib,
            args=[],
            kwargs={"timeperiod": timeperiod},
            symbol="min",
            is_elementwise=False,
        )

    def minindex(self, timeperiod: int = 30) -> pl.Expr:
        """Index of lowest value over a specified period (Math Operators)
        pl.col("close").ta.minindex(timeperiod=30)

        Inputs:
            prices: ['close']
        Parameters:
            timeperiod: 30
        Outputs:
            integer
        """
        return self._expr.register_plugin(
            lib=lib,
            args=[],
            kwargs={"timeperiod": timeperiod},
            symbol="minindex",
            is_elementwise=False,
        )

    def minmax(self, timeperiod: int = 30) -> pl.Expr:
        """Lowest and highest values over a specified period (Math Operators)
        pl.col("close").ta.minmax(timeperiod=30)

        Inputs:
            prices: ['close']
        Parameters:
            timeperiod: 30
        Outputs:
            min
            max
        """
        return self._expr.register_plugin(
            lib=lib,
            args=[],
            kwargs={"timeperiod": timeperiod},
            symbol="minmax",
            is_elementwise=False,
        )

    def minmaxindex(self, timeperiod: int = 30) -> pl.Expr:
        """Indexes of lowest and highest values over a specified period (Math Operators)
        pl.col("close").ta.minmaxindex(timeperiod=30)

        Inputs:
            prices: ['close']
        Parameters:
            timeperiod: 30
        Outputs:
            minidx
            maxidx
        """
        return self._expr.register_plugin(
            lib=lib,
            args=[],
            kwargs={"timeperiod": timeperiod},
            symbol="minmaxindex",
            is_elementwise=False,
        )

    def mult(self, b: IntoExpr) -> pl.Expr:
        """Vectorized multiplication
        pl.col("a").ta.mult(pl.col("b"))

        Inputs:
            a: (any ndarray)
            b: (any ndarray)
        Outputs:
            real
        """
        return self._expr.register_plugin(
            lib=lib,
            args=[b],
            symbol="mult",
            is_elementwise=False,
        )

    def sub(self, b: IntoExpr) -> pl.Expr:
        """Vectorized subtraction
        pl.col("a").ta.sub(pl.col("b"))

        Inputs:
            a: (any ndarray)
            b: (any ndarray)
        Outputs:
            real
        """
        return self._expr.register_plugin(
            lib=lib,
            args=[b],
            symbol="sub",
            is_elementwise=False,
        )

    def sum(self, timeperiod: int = 30) -> pl.Expr:
        """Summation (Math Operators)
        pl.col("close").ta.sum(timeperiod=30)

        Inputs:
            prices: ['close']
        Parameters:
            timeperiod: 30
        Outputs:
            real
        """
        return self._expr.register_plugin(
            lib=lib,
            args=[],
            kwargs={"timeperiod": timeperiod},
            symbol="sum",
            is_elementwise=False,
        )

    def acos(self) -> pl.Expr:
        """Vectorized acos
        pl.col("a").ta.acos()

        Inputs:
            a: (any ndarray)
        Outputs:
            real
        """
        return self._expr.register_plugin(
            lib=lib,
            symbol="acos",
            is_elementwise=False,
        )

    def asin(self) -> pl.Expr:
        """Vectorized asin
        pl.col("a").ta.asin()

        Inputs:
            a: (any ndarray)
        Outputs:
            real
        """
        return self._expr.register_plugin(
            lib=lib,
            symbol="asin",
            is_elementwise=False,
        )

    def atan(self) -> pl.Expr:
        """Vectorized atan
        pl.col("a").ta.atan()

        Inputs:
            a: (any ndarray)
        Outputs:
            real
        """
        return self._expr.register_plugin(
            lib=lib,
            symbol="atan",
            is_elementwise=False,
        )

    def ceil(self) -> pl.Expr:
        """Vectorized ceil
        pl.col("a").ta.ceil()

        Inputs:
            a: (any ndarray)
        Outputs:
            real
        """
        return self._expr.register_plugin(
            lib=lib,
            symbol="ceil",
            is_elementwise=False,
        )

    def cos(self) -> pl.Expr:
        """Vectorized cos
        pl.col("a").ta.cos()

        Inputs:
            a: (any ndarray)
        Outputs:
            real
        """
        return self._expr.register_plugin(
            lib=lib,
            symbol="cos",
            is_elementwise=False,
        )

    def cosh(self) -> pl.Expr:
        """Vectorized cosh
        pl.col("a").ta.cosh()

        Inputs:
            a: (any ndarray)
        Outputs:
            real
        """
        return self._expr.register_plugin(
            lib=lib,
            symbol="cosh",
            is_elementwise=False,
        )

    def exp(self) -> pl.Expr:
        """Vectorized exp
        pl.col("a").ta.exp()

        Inputs:
            a: (any ndarray)
        Outputs:
            real
        """
        return self._expr.register_plugin(
            lib=lib,
            symbol="exp",
            is_elementwise=False,
        )

    def floor(self) -> pl.Expr:
        """Vectorized floor
        pl.col("a").ta.floor()

        Inputs:
            a: (any ndarray)
        Outputs:
            real
        """
        return self._expr.register_plugin(
            lib=lib,
            symbol="floor",
            is_elementwise=False,
        )

    def ln(self) -> pl.Expr:
        """Vectorized ln
        pl.col("a").ta.ln()

        Inputs:
            a: (any ndarray)
        Outputs:
            real
        """
        return self._expr.register_plugin(
            lib=lib,
            symbol="ln",
            is_elementwise=False,
        )

    def log10(self) -> pl.Expr:
        """Vectorized log10
        pl.col("a").ta.log10()

        Inputs:
            a: (any ndarray)
        Outputs:
            real
        """
        return self._expr.register_plugin(
            lib=lib,
            symbol="log10",
            is_elementwise=False,
        )

    def sin(self) -> pl.Expr:
        """Vectorized sin
        pl.col("a").ta.sin()

        Inputs:
            a: (any ndarray)
        Outputs:
            real
        """
        return self._expr.register_plugin(
            lib=lib,
            symbol="sin",
            is_elementwise=False,
        )

    def sinh(self) -> pl.Expr:
        """Vectorized sinh
        pl.col("a").ta.sinh()

        Inputs:
            a: (any ndarray)
        Outputs:
            real
        """
        return self._expr.register_plugin(
            lib=lib,
            symbol="sinh",
            is_elementwise=False,
        )

    def sqrt(self) -> pl.Expr:
        """Vectorized sqrt
        pl.col("a").ta.sqrt()

        Inputs:
            a: (any ndarray)
        Outputs:
            real
        """
        return self._expr.register_plugin(
            lib=lib,
            symbol="sqrt",
            is_elementwise=False,
        )

    def tan(self) -> pl.Expr:
        """Vectorized tan
        pl.col("a").ta.tan()

        Inputs:
            a: (any ndarray)
        Outputs:
            real
        """
        return self._expr.register_plugin(
            lib=lib,
            symbol="tan",
            is_elementwise=False,
        )

    def tanh(self) -> pl.Expr:
        """Vectorized tanh
        pl.col("a").ta.tanh()

        Inputs:
            a: (any ndarray)
        Outputs:
            real
        """
        return self._expr.register_plugin(
            lib=lib,
            symbol="tanh",
            is_elementwise=False,
        )

    def adx(
        self, high: IntoExpr = pl.col("high"), low: IntoExpr = pl.col("low"), timeperiod: int = 14
    ) -> pl.Expr:
        """Average Directional Movement Index (Momentum Indicators)
        pl.col("close").ta.adx("high", "low", timeperiod=14)

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

    def adxr(
        self, high: IntoExpr = pl.col("high"), low: IntoExpr = pl.col("low"), timeperiod: int = 14
    ) -> pl.Expr:
        """Average Directional Movement Index Rating (Momentum Indicators)
        pl.col("close").ta.adxr("high", "low", timeperiod=14)

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
            symbol="adxr",
            is_elementwise=False,
        )

    def apo(self, fastperiod: int = 12, slowperiod: int = 26, matype: int = 0) -> pl.Expr:
        """Absolute Price Oscillator (Momentum Indicators)
        pl.col("close").ta.apo(fastperiod=12, slowperiod=26, matype=0)

        Inputs:
            prices: ['close']
        Parameters:
            fastperiod: 12
            slowperiod: 26
            matype: 0
        Outputs:
            real
        """
        return self._expr.register_plugin(
            lib=lib,
            args=[],
            kwargs={
                "fastperiod": fastperiod,
                "slowperiod": slowperiod,
                "matype": matype,
            },
            symbol="apo",
            is_elementwise=False,
        )

    def aroon(self, low: IntoExpr = pl.col("low"), timeperiod: int = 14) -> pl.Expr:
        """Aroon (Momentum Indicators)
        pl.col("high").ta.aroon("low", timeperiod=14)
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

    def aroonosc(self, low: IntoExpr = pl.col("low"), timeperiod: int = 14) -> pl.Expr:
        """Aroon Oscillator (Momentum Indicators)
        pl.col("high").ta.aroonosc("low", timeperiod=14)

        Inputs:
            prices: ['high', 'low']
        Parameters:
            timeperiod: 14
        Outputs:
            real
        """
        return self._expr.register_plugin(
            lib=lib,
            args=[low],
            kwargs={
                "timeperiod": timeperiod,
            },
            symbol="aroonosc",
            is_elementwise=False,
        )

    def bop(
        self,
        high: IntoExpr = pl.col("high"),
        low: IntoExpr = pl.col("low"),
        close: IntoExpr = pl.col("close"),
    ) -> pl.Expr:
        """Balance Of Power (Momentum Indicators)
        pl.col("open").ta.bop("high", "low", "close")

        Inputs:
            prices: ['open', 'high', 'low', 'close']
        Outputs:
            real
        """
        return self._expr.register_plugin(
            lib=lib,
            args=[high, low, close],
            symbol="bop",
            is_elementwise=False,
        )

    def cci(
        self, high: IntoExpr = pl.col("high"), low: IntoExpr = pl.col("low"), timeperiod: int = 14
    ) -> pl.Expr:
        """Commodity Channel Index (Momentum Indicators)
        pl.col("close").ta.cci("high", "low", timeperiod=14)

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
            symbol="cci",
            is_elementwise=False,
        )

    def cmo(self, timeperiod: int = 14) -> pl.Expr:
        """Chande Momentum Oscillator (Momentum Indicators)
        pl.col("close").ta.cmo(timeperiod=14)

        Inputs:
            prices: ['close']
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
            symbol="cmo",
            is_elementwise=False,
        )

    def dx(
        self, high: IntoExpr = pl.col("high"), low: IntoExpr = pl.col("low"), timeperiod: int = 14
    ) -> pl.Expr:
        """Directional Movement Index (Momentum Indicators)
        pl.col("close").ta.dx("high", "low", timeperiod=14)

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
            symbol="dx",
            is_elementwise=False,
        )

    def macd(self, fastperiod: int = 12, slowperiod: int = 26, signalperiod: int = 9) -> pl.Expr:
        """Moving Average Convergence/Divergence (Momentum Indicators)
        pl.col("close").ta.macd(fastperiod=12, slowperiod=26, signalperiod=9)

        Inputs:
            prices: ['close']
        Parameters:
            fastperiod: 12
            slowperiod: 26
            signalperiod: 9
        Outputs:
            macd
            macdsignal
            macdhist
        """
        return self._expr.register_plugin(
            lib=lib,
            args=[],
            kwargs={
                "fastperiod": fastperiod,
                "slowperiod": slowperiod,
                "signalperiod": signalperiod,
            },
            symbol="macd",
            is_elementwise=False,
        )

    def macdext(
        self,
        fastperiod: int = 12,
        slowperiod: int = 26,
        signalperiod: int = 9,
        fastmatype: int = 0,
        slowmatype: int = 0,
        signalmatype: int = 0,
    ) -> pl.Expr:
        """MACD with controllable MA type (Momentum Indicators)
        pl.col("close").ta.macdext(fastperiod=12, slowperiod=26, signalperiod=9, fastmatype=0, slowmatype=0, signalmatype=0)

        Inputs:
            prices: ['close']
        Parameters:
            fastperiod: 12
            slowperiod: 26
            signalperiod: 9
            fastmatype: 0
            slowmatype: 0
            signalmatype: 0
        Outputs:
            macd
            macdsignal
            macdhist
        """
        return self._expr.register_plugin(
            lib=lib,
            args=[],
            kwargs={
                "fastperiod": fastperiod,
                "slowperiod": slowperiod,
                "signalperiod": signalperiod,
                "fastmatype": fastmatype,
                "slowmatype": slowmatype,
                "signalmatype": signalmatype,
            },
            symbol="macdext",
            is_elementwise=False,
        )

    def macdfix(self, signalperiod: int = 9) -> pl.Expr:
        """Moving Average Convergence/Divergence Fix 12/26 (Momentum Indicators)
        pl.col("close").ta.macdfix(signalperiod=9)

        Inputs:
            prices: ['close']
        Parameters:
            signalperiod: 9
        Outputs:
            macd
            macdsignal
            macdhist
        """
        return self._expr.register_plugin(
            lib=lib,
            args=[],
            kwargs={
                "signalperiod": signalperiod,
            },
            symbol="macdfix",
            is_elementwise=False,
        )

    def mfi(
        self,
        high: IntoExpr = pl.col("high"),
        low: IntoExpr = pl.col("low"),
        volume: IntoExpr = pl.col("volume"),
        timeperiod: int = 14,
    ) -> pl.Expr:
        """Money Flow Index (Momentum Indicators)
        pl.col("close").ta.mfi("high", "low", "volume", timeperiod=14)

        Inputs:
            prices: ['high', 'low', 'close', 'volume']
        Parameters:
            timeperiod: 14
        Outputs:
            real
        """
        return self._expr.register_plugin(
            lib=lib,
            args=[high, low, volume],
            kwargs={
                "timeperiod": timeperiod,
            },
            symbol="mfi",
            is_elementwise=False,
        )

    def minus_di(
        self, high: IntoExpr = pl.col("high"), low: IntoExpr = pl.col("low"), timeperiod: int = 14
    ) -> pl.Expr:
        """Minus Directional Indicator (Momentum Indicators)
        pl.col("close").ta.minus_di("high", "low", timeperiod=14)

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
            symbol="minus_di",
            is_elementwise=False,
        )

    def minus_dm(self, low: IntoExpr = pl.col("low"), timeperiod: int = 14) -> pl.Expr:
        """Minus Directional Movement (Momentum Indicators)
        pl.col("high").ta.minus_dm("low", timeperiod=14)

        Inputs:
            prices: ['high', 'low']
        Parameters:
            timeperiod: 14
        Outputs:
            real
        """
        return self._expr.register_plugin(
            lib=lib,
            args=[low],
            kwargs={
                "timeperiod": timeperiod,
            },
            symbol="minus_dm",
            is_elementwise=False,
        )

    def mom(self, timeperiod: int = 10) -> pl.Expr:
        """Momentum (Momentum Indicators)
        pl.col("close").ta.mom(timeperiod=10)

        Inputs:
            prices: ['close']
        Parameters:
            timeperiod: 10
        Outputs:
            real
        """
        return self._expr.register_plugin(
            lib=lib,
            args=[],
            kwargs={
                "timeperiod": timeperiod,
            },
            symbol="mom",
            is_elementwise=False,
        )

    def plus_di(
        self, high: IntoExpr = pl.col("high"), low: IntoExpr = pl.col("low"), timeperiod: int = 14
    ) -> pl.Expr:
        """Plus Directional Indicator (Momentum Indicators)
        pl.col("close").ta.plus_di("high", "low", timeperiod=14)

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
            symbol="plus_di",
            is_elementwise=False,
        )

    def plus_dm(self, low: IntoExpr = pl.col("low"), timeperiod: int = 14) -> pl.Expr:
        """Plus Directional Movement (Momentum Indicators)
        pl.col("high").ta.plus_dm("low", timeperiod=14)

        Inputs:
            prices: ['high', 'low']
        Parameters:
            timeperiod: 14
        Outputs:
            real
        """
        return self._expr.register_plugin(
            lib=lib,
            args=[low],
            kwargs={
                "timeperiod": timeperiod,
            },
            symbol="plus_dm",
            is_elementwise=False,
        )

    def ppo(self, fastperiod: int = 12, slowperiod: int = 26, matype: int = 0) -> pl.Expr:
        """Percentage Price Oscillator (Momentum Indicators)
        pl.col("close").ta.ppo(fastperiod=12, slowperiod=26, matype=0)

        Inputs:
            prices: ['close']
        Parameters:
            fastperiod: 12
            slowperiod: 26
            matype: 0
        Outputs:
            real
        """
        return self._expr.register_plugin(
            lib=lib,
            args=[],
            kwargs={
                "fastperiod": fastperiod,
                "slowperiod": slowperiod,
                "matype": matype,
            },
            symbol="ppo",
            is_elementwise=False,
        )

    def roc(self, timeperiod: int = 10) -> pl.Expr:
        """Rate of change : ((price/prevPrice)-1)*100 (Momentum Indicators)
        pl.col("close").ta.roc(timeperiod=10)

        Inputs:
            prices: ['close']
        Parameters:
            timeperiod: 10
        Outputs:
            real
        """
        return self._expr.register_plugin(
            lib=lib,
            args=[],
            kwargs={
                "timeperiod": timeperiod,
            },
            symbol="roc",
            is_elementwise=False,
        )

    def rocp(self, timeperiod: int = 10) -> pl.Expr:
        """Rate of change Percentage: (price-prevPrice)/prevPrice (Momentum Indicators)
        pl.col("close").ta.rocp(timeperiod=10)

        Inputs:
            prices: ['close']
        Parameters:
            timeperiod: 10
        Outputs:
            real
        """
        return self._expr.register_plugin(
            lib=lib,
            args=[],
            kwargs={
                "timeperiod": timeperiod,
            },
            symbol="rocp",
            is_elementwise=False,
        )

    def rocr(self, timeperiod: int = 10) -> pl.Expr:
        """Rate of change ratio: (price/prevPrice) (Momentum Indicators)
        pl.col("close").ta.rocr(timeperiod=10)

        Inputs:
            prices: ['close']
        Parameters:
            timeperiod: 10
        Outputs:
            real
        """
        return self._expr.register_plugin(
            lib=lib,
            args=[],
            kwargs={
                "timeperiod": timeperiod,
            },
            symbol="rocr",
            is_elementwise=False,
        )

    def rocr100(self, timeperiod: int = 10) -> pl.Expr:
        """Rate of change ratio 100 scale: (price/prevPrice)*100 (Momentum Indicators)
        pl.col("close").ta.rocr100(timeperiod=10)

        Inputs:
            prices: ['close']
        Parameters:
            timeperiod: 10
        Outputs:
            real
        """
        return self._expr.register_plugin(
            lib=lib,
            args=[],
            kwargs={
                "timeperiod": timeperiod,
            },
            symbol="rocr100",
            is_elementwise=False,
        )

    def rsi(self, timeperiod: int = 14) -> pl.Expr:
        """Relative Strength Index (Momentum Indicators)
        pl.col("close").ta.rsi(timeperiod=14)

        Inputs:
            prices: ['close']
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
            symbol="rsi",
            is_elementwise=False,
        )

    def stoch(
        self,
        high: IntoExpr = pl.col("high"),
        low: IntoExpr = pl.col("low"),
        fastk_period: int = 5,
        slowk_period: int = 3,
        slowk_matype: int = 0,
        slowd_period: int = 3,
        slowd_matype: int = 0,
    ) -> pl.Expr:
        """Stochastic (Momentum Indicators)
        pl.col("close").ta.stoch("high", "low", fastk_period=5, slowk_period=3, slowk_matype=0, slowd_period=3, slowd_matype=0)

        Inputs:
            prices: ['high', 'low', 'close']
        Parameters:
            fastk_period: 5
            slowk_period: 3
            slowk_matype: 0
            slowd_period: 3
            slowd_matype: 0
        Outputs:
            slowk
            slowd
        """
        return self._expr.register_plugin(
            lib=lib,
            args=[high, low],
            kwargs={
                "fastk_period": fastk_period,
                "slowk_period": slowk_period,
                "slowk_matype": slowk_matype,
                "slowd_period": slowd_period,
                "slowd_matype": slowd_matype,
            },
            symbol="stoch",
            is_elementwise=False,
        )

    def stochf(
        self,
        high: IntoExpr = pl.col("high"),
        low: IntoExpr = pl.col("low"),
        fastk_period: int = 5,
        fastd_period: int = 3,
        fastd_matype: int = 0,
    ) -> pl.Expr:
        """Stochastic Fast (Momentum Indicators)
        pl.col("close").ta.stochf("high", "low", fastk_period=5, fastd_period=3, fastd_matype=0)

        Inputs:
            prices: ['high', 'low', 'close']
        Parameters:
            fastk_period: 5
            fastd_period: 3
            fastd_matype: 0
        Outputs:
            fastk
            fastd
        """
        return self._expr.register_plugin(
            lib=lib,
            args=[high, low],
            kwargs={
                "fastk_period": fastk_period,
                "fastd_period": fastd_period,
                "fastd_matype": fastd_matype,
            },
            symbol="stochf",
            is_elementwise=False,
        )

    def stochrsi(
        self,
        timeperiod: int = 14,
        fastk_period: int = 5,
        fastd_period: int = 3,
        fastd_matype: int = 0,
    ) -> pl.Expr:
        """Stochastic Relative Strength Index (Momentum Indicators)
        pl.col("close").ta.stochrsi(timeperiod=14, fastk_period=5, fastd_period=3, fastd_matype=0)

        Inputs:
            prices: ['close']
        Parameters:
            timeperiod: 14
            fastk_period: 5
            fastd_period: 3
            fastd_matype: 0
        Outputs:
            fastk
            fastd
        """
        return self._expr.register_plugin(
            lib=lib,
            args=[],
            kwargs={
                "timeperiod": timeperiod,
                "fastk_period": fastk_period,
                "fastd_period": fastd_period,
                "fastd_matype": fastd_matype,
            },
            symbol="stochrsi",
            is_elementwise=False,
        )

    def trix(self, timeperiod: int = 30) -> pl.Expr:
        """1-day Rate-Of-Change (ROC) of a Triple Smooth EMA (Momentum Indicators)
        pl.col("close").ta.trix(timeperiod=30)

        Inputs:
            prices: ['close']
        Parameters:
            timeperiod: 30
        Outputs:
            real
        """
        return self._expr.register_plugin(
            lib=lib,
            args=[],
            kwargs={
                "timeperiod": timeperiod,
            },
            symbol="trix",
            is_elementwise=False,
        )

    def ultosc(
        self,
        high: IntoExpr = pl.col("high"),
        low: IntoExpr = pl.col("low"),
        timeperiod1: int = 7,
        timeperiod2: int = 14,
        timeperiod3: int = 28,
    ) -> pl.Expr:
        """Ultimate Oscillator (Momentum Indicators)
        pl.col("close").ta.ultosc("high", "low", timeperiod1=7, timeperiod2=14, timeperiod3=28)

        Inputs:
            prices: ['open', 'high', 'low', 'close']
        Parameters:
            timeperiod1: 7
            timeperiod2: 14
            timeperiod3: 28
        Outputs:
            real
        """
        return self._expr.register_plugin(
            lib=lib,
            args=[high, low],
            kwargs={
                "timeperiod1": timeperiod1,
                "timeperiod2": timeperiod2,
                "timeperiod3": timeperiod3,
            },
            symbol="ultosc",
            is_elementwise=False,
        )

    def willr(
        self, high: IntoExpr = pl.col("high"), low: IntoExpr = pl.col("low"), timeperiod: int = 14
    ) -> pl.Expr:
        """Williams' %R (Momentum Indicators)
        pl.col("close").ta.willr("high", "low", timeperiod=14)

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
            symbol="willr",
            is_elementwise=False,
        )

    def bbands(
        self, timeperiod: int = 5, nbdevup: float = 2.0, nbdevdn: float = 2.0, ma_type: int = 0
    ) -> pl.Expr:
        """Bollinger Bands (Overlap Studies)
        ta.pol("close").ta.bbands(timeperiod=5, nbdevup=2.0, nbdevdn=2.0, ma_type=0)

        Inputs:
            real: (any ndarray)
        Parameters:
            timeperiod: 5
            nbdevup: 2.0
            nbdevdn: 2.0
            ma_type: 0
        Outputs:
            upperband: real
            middleband: real
            lowerband: real
        """
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
        """Double Exponential Moving Average (Overlap Studies)
        ta.pol("close").ta.ema(timeperiod=30)

        Inputs:
            real: (any ndarray)
        Parameters:
            timeperiod: 30
        Outputs:
            real
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

    def dema(self, timeperiod: int = 30) -> pl.Expr:
        """Double Exponential Moving Average (Overlap Studies)
        ta.pol("close").ta.dema(timeperiod=30)

        Inputs:
            real: (any ndarray)
        Parameters:
            timeperiod: 30
        Outputs:
            real
        """
        return self._expr.register_plugin(
            lib=lib,
            args=[],
            kwargs={
                "timeperiod": timeperiod,
            },
            symbol="dema",
            is_elementwise=False,
        )

    def ht_trendline(self) -> pl.Expr:
        """Hilbert Transform - Instantaneous Trendline (Overlap Studies)
        ta.pol("close").ta.ht_trendline()

        Inputs:
            real: (any ndarray)
        Outputs:
            real
        """
        return self._expr.register_plugin(
            lib=lib,
            symbol="ht_trendline",
            is_elementwise=False,
        )

    def kama(self, timeperiod: int = 30) -> pl.Expr:
        """Kaufman Adaptive Moving Average (Overlap Studies)
        ta.pol("close").ta.kama(timeperiod=30)

        Inputs:
            real: (any ndarray)
        Parameters:
            timeperiod: 30
        Outputs:
            real
        """
        return self._expr.register_plugin(
            lib=lib,
            args=[],
            kwargs={
                "timeperiod": timeperiod,
            },
            symbol="kama",
            is_elementwise=False,
        )

    def ma(self, timeperiod: int = 30, matype: int = 0) -> pl.Expr:
        """Moving average (Overlap Studies)
        ta.pol("close").ta.ma(timeperiod=30, matype=0)

        Inputs:
            real: (any ndarray)
        Parameters:
            timeperiod: 30
            matype: 0
        Outputs:
            real
        """
        return self._expr.register_plugin(
            lib=lib,
            args=[],
            kwargs={
                "timeperiod": timeperiod,
                "matype": matype,
            },
            symbol="ma",
            is_elementwise=False,
        )

    def mama(self, fastlimit: float = 0.5, slowlimit: float = 0.05) -> pl.Expr:
        """MESA Adaptive Moving Average (Overlap Studies)
        ta.pol("close").ta.mama(fastlimit=0.5, slowlimit=0.05)

        Inputs:
            real: (any ndarray)
        Parameters:
            fastlimit: 0.5
            slowlimit: 0.05
        Outputs:
            mama: real
            fama: real
        """
        return self._expr.register_plugin(
            lib=lib,
            args=[],
            kwargs={
                "fastlimit": fastlimit,
                "slowlimit": slowlimit,
            },
            symbol="mama",
            is_elementwise=False,
        )

    def mavp(
        self, periods: IntoExpr, minperiod: int = 2, maxperiod: int = 30, matype: int = 0
    ) -> pl.Expr:
        """Moving average with variable period (Overlap Studies)
        ta.pol("close").ta.mavp(periods, minperiod=2, maxperiod=30, matype=0)

        Inputs:
            real: (any ndarray)
            periods: (any ndarray)
        Parameters:
            minperiod: 2
            maxperiod: 30
            matype: 0
        Outputs:
            real
        """
        return self._expr.register_plugin(
            lib=lib,
            args=[periods],
            kwargs={
                "minperiod": minperiod,
                "maxperiod": maxperiod,
                "matype": matype,
            },
            symbol="mavp",
            is_elementwise=False,
        )

    def midpoint(self, timeperiod: int = 14) -> pl.Expr:
        """MidPoint over period (Overlap Studies)
        ta.pol("close").ta.midpoint(timeperiod=14)

        Inputs:
            real: (any ndarray)
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
            symbol="midpoint",
            is_elementwise=False,
        )

    def midprice(self, low: IntoExpr = pl.col("low"), timeperiod: int = 14) -> pl.Expr:
        """Midpoint Price over period (Overlap Studies)
        ta.pol("high").ta.midprice(pl.col("low"), timeperiod=14)

        Inputs:
            high: (any ndarray)
            low: (any ndarray)
        Parameters:
            timeperiod: 14
        Outputs:
            real
        """
        return self._expr.register_plugin(
            lib=lib,
            args=[low],
            kwargs={
                "timeperiod": timeperiod,
            },
            symbol="midprice",
            is_elementwise=False,
        )

    def sar(
        self, low: IntoExpr = pl.col("low"), acceleration: float = 0.02, maximum: float = 0.2
    ) -> pl.Expr:
        """Parabolic SAR (Overlap Studies)
        ta.pol("high").ta.sar(pl.col("low"), acceleration=0.02, maximum=0.2)

        Inputs:
            high: (any ndarray)
            low: (any ndarray)
        Parameters:
            acceleration: 0.02
            maximum: 0.2
        Outputs:
            real
        """
        return self._expr.register_plugin(
            lib=lib,
            args=[low],
            kwargs={
                "acceleration": acceleration,
                "maximum": maximum,
            },
            symbol="sar",
            is_elementwise=False,
        )

    def sarext(
        self,
        low: IntoExpr = pl.col("low"),
        startvalue: float = 0.0,
        offsetonreverse: float = 0.0,
        accelerationinitlong: float = 0.02,
        accelerationlong: float = 0.02,
        accelerationmaxlong: float = 0.2,
        accelerationinitshort: float = 0.02,
        accelerationshort: float = 0.02,
        accelerationmaxshort: float = 0.2,
    ) -> pl.Expr:
        """Parabolic SAR - Extended (Overlap Studies)
        ta.pol("high").ta.sarext(pl.col("low"), accelerationinitlong=0.02, accelerationlong=0.02)

        Inputs:
            high: (any ndarray)
            low: (any ndarray)
        Parameters:
            startvalue: 0.0
            offsetonreverse: 0.0
            accelerationinitlong: 0.02
            accelerationlong: 0.02
            accelerationmaxlong: 0.2
            accelerationinitshort: 0.02
            accelerationshort: 0.02
            accelerationmaxshort: 0.2
        Outputs:
            real
        """
        return self._expr.register_plugin(
            lib=lib,
            args=[low],
            kwargs={
                "startvalue": startvalue,
                "offsetonreverse": offsetonreverse,
                "accelerationinitlong": accelerationinitlong,
                "accelerationlong": accelerationlong,
                "accelerationmaxlong": accelerationmaxlong,
                "accelerationinitshort": accelerationinitshort,
                "accelerationshort": accelerationshort,
                "accelerationmaxshort": accelerationmaxshort,
            },
            symbol="sarext",
            is_elementwise=False,
        )

    def sma(self, timeperiod: int = 30) -> pl.Expr:
        """Simple Moving Average (Overlap Studies)
        ta.pol("close").ta.sma(timeperiod=30)

        Inputs:
            real: (any ndarray)
        Parameters:
            timeperiod: 30
        Outputs:
            real
        """
        return self._expr.register_plugin(
            lib=lib,
            args=[],
            kwargs={
                "timeperiod": timeperiod,
            },
            symbol="sma",
            is_elementwise=False,
        )

    def t3(self, timeperiod: int = 5, vfactor: float = 0.7) -> pl.Expr:
        """Triple Exponential Moving Average T3 (Overlap Studies)
        ta.pol("close").ta.t3(timeperiod=5, vfactor=0.7)

        Inputs:
            real: (any ndarray)
        Parameters:
            timeperiod: 5
            vfactor: 0.7
        Outputs:
            real
        """
        return self._expr.register_plugin(
            lib=lib,
            args=[],
            kwargs={
                "timeperiod": timeperiod,
                "vfactor": vfactor,
            },
            symbol="t3",
            is_elementwise=False,
        )

    def tema(self, timeperiod: int = 30) -> pl.Expr:
        """Triple Exponential Moving Average (Overlap Studies)
        ta.pol("close").ta.tema(timeperiod=30)

        Inputs:
            real: (any ndarray)
        Parameters:
            timeperiod: 30
        Outputs:
            real
        """
        return self._expr.register_plugin(
            lib=lib,
            args=[],
            kwargs={
                "timeperiod": timeperiod,
            },
            symbol="tema",
            is_elementwise=False,
        )

    def trima(self, timeperiod: int = 30) -> pl.Expr:
        """Triangular Moving Average (Overlap Studies)
        ta.pol("close").ta.trima(timeperiod=30)

        Inputs:
            real: (any ndarray)
        Parameters:
            timeperiod: 30
        Outputs:
            real
        """
        return self._expr.register_plugin(
            lib=lib,
            args=[],
            kwargs={
                "timeperiod": timeperiod,
            },
            symbol="trima",
            is_elementwise=False,
        )

    def wma(self, timeperiod: int = 30) -> pl.Expr:
        """Weighted Moving Average (Overlap Studies)
        ta.pol("close").ta.wma(timeperiod=30)

        Inputs:
            real: (any ndarray)
        Parameters:
            timeperiod: 30
        Outputs:
            real
        """
        return self._expr.register_plugin(
            lib=lib,
            args=[],
            kwargs={
                "timeperiod": timeperiod,
            },
            symbol="wma",
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
