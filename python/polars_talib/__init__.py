import atexit
from pathlib import Path
import polars as pl
from polars._typing import IntoExpr
from polars.plugins import register_plugin_function
from ._polars_talib import initialize, shutdown, version


__talib_version__ = version()

# Initialize and register shutdown
initialize()
atexit.register(shutdown)

# Get the path to the plugin
plugin_path = Path(__file__).parent


__function_groups__ = {
    "Cycle Indicators": ["ht_dcperiod", "ht_dcphase", "ht_phasor", "ht_sine", "ht_trendmode"],
    "Math Operators": [
        "add",
        "div",
        "max",
        "maxindex",
        "min",
        "minindex",
        "minmax",
        "minmaxindex",
        "mult",
        "sub",
        "sum",
    ],
    "Math Transform": [
        "acos",
        "asin",
        "atan",
        "ceil",
        "cos",
        "cosh",
        "exp",
        "floor",
        "ln",
        "log10",
        "sin",
        "sinh",
        "sqrt",
        "tan",
        "tanh",
    ],
    "Momentum Indicators": [
        "adx",
        "adxr",
        "apo",
        "aroon",
        "aroonosc",
        "bop",
        "cci",
        "cmo",
        "dx",
        "macd",
        "macdext",
        "macdfix",
        "mfi",
        "minus_di",
        "minus_dm",
        "mom",
        "plus_di",
        "plus_dm",
        "ppo",
        "roc",
        "rocp",
        "rocr",
        "rocr100",
        "rsi",
        "stoch",
        "stochf",
        "stochrsi",
        "trix",
        "ultosc",
        "willr",
    ],
    "Overlap Studies": [
        "bbands",
        "dema",
        "ema",
        "ht_trendline",
        "kama",
        "ma",
        "mama",
        "mavp",
        "midpoint",
        "midprice",
        "sar",
        "sarext",
        "sma",
        "t3",
        "tema",
        "trima",
        "wma",
    ],
    "Pattern Recognition": [
        "cdl2crows",
        "cdl3blackcrows",
        "cdl3inside",
        "cdl3linestrike",
        "cdl3outside",
        "cdl3starsinsouth",
        "cdl3whitesoldiers",
        "cdlabandonedbaby",
        "cdladvanceblock",
        "cdlbelthold",
        "cdlbreakaway",
        "cdlclosingmarubozu",
        "cdlconcealbabyswall",
        "cdlcounterattack",
        "cdldarkcloudcover",
        "cdldoji",
        "cdldojistar",
        "cdldragonflydoji",
        "cdlengulfing",
        "cdleveningdojistar",
        "cdleveningstar",
        "cdlgapsidesidewhite",
        "cdlgravestonedoji",
        "cdlhammer",
        "cdlhangingman",
        "cdlharami",
        "cdlharamicross",
        "cdlhighwave",
        "cdlhikkake",
        "cdlhikkakemod",
        "cdlhomingpigeon",
        "cdlidentical3crows",
        "cdlinneck",
        "cdlinvertedhammer",
        "cdlkicking",
        "cdlkickingbylength",
        "cdlladderbottom",
        "cdllongleggeddoji",
        "cdllongline",
        "cdlmarubozu",
        "cdlmatchinglow",
        "cdlmathold",
        "cdlmorningdojistar",
        "cdlmorningstar",
        "cdlonneck",
        "cdlpiercing",
        "cdlrickshawman",
        "cdlrisefall3methods",
        "cdlseparatinglines",
        "cdlshootingstar",
        "cdlshortline",
        "cdlspinningtop",
        "cdlstalledpattern",
        "cdlsticksandwich",
        "cdltakuri",
        "cdltasukigap",
        "cdlthrusting",
        "cdltristar",
        "cdlunique3river",
        "cdlupsidegap2crows",
        "cdlxsidegap3methods",
    ],
    "Price Transform": ["avgprice", "medprice", "typprice", "wclprice"],
    "Statistic Functions": [
        "beta",
        "correl",
        "linearreg",
        "linearreg_angle",
        "linearreg_intercept",
        "linearreg_slope",
        "stddev",
        "tsf",
        "var",
    ],
    "Volatility Indicators": ["atr", "natr", "trange"],
    "Volume Indicators": ["ad", "adosc", "obv"],
}


def get_functions():
    """
    Returns a list of all the functions supported by TALIB
    """
    return [fn for group in __function_groups__ for fn in __function_groups__[group]]


def get_function_groups():
    """
    Returns a dict with keys of function-group names and values of lists
    of function names ie {'group_names': ['function_names']}
    """
    return __function_groups__.copy()


def get_functions_output_struct():
    """
    Returns a dict with keys of function names and keys of the output struct
    """
    return {
        "ht_phasor": ["inphase", "quadrature"],
        "ht_sine": ["sine", "leadsine"],
        "minmax": ["min", "max"],
        "minmaxindex": ["minidx", "maxidx"],
        "aroon": ["aroondown", "aroonup"],
        "macd": ["macd", "macdsignal", "macdhist"],
        "macdext": ["macd", "macdsignal", "macdhist"],
        "macdfix": ["macd", "macdsignal", "macdhist"],
        "stoch": ["slowk", "slowd"],
        "stochf": ["fastk", "fastd"],
        "stochrsi": ["fastk", "fastd"],
        "bbands": ["upperband", "middleband", "lowerband"],
        "mama": ["mama", "fama"],
    }


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
        return register_plugin_function(
            plugin_path=plugin_path,
            function_name="ht_dcperiod",
            args=self._expr,
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
        return register_plugin_function(
            plugin_path=plugin_path,
            function_name="ht_dcphase",
            args=self._expr,
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
        return register_plugin_function(
            plugin_path=plugin_path,
            function_name="ht_phasor",
            args=self._expr,
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
        return register_plugin_function(
            plugin_path=plugin_path,
            function_name="ht_sine",
            args=self._expr,
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
        return register_plugin_function(
            plugin_path=plugin_path,
            function_name="ht_trendmode",
            args=self._expr,
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
        return register_plugin_function(
            plugin_path=plugin_path,
            function_name="add",
            args=[self._expr, b],
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
        return register_plugin_function(
            plugin_path=plugin_path,
            function_name="div",
            args=[self._expr, b],
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
        return register_plugin_function(
            plugin_path=plugin_path,
            function_name="max",
            args=self._expr,
            kwargs={"timeperiod": timeperiod},
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
        return register_plugin_function(
            plugin_path=plugin_path,
            function_name="maxindex",
            args=self._expr,
            kwargs={"timeperiod": timeperiod},
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
        return register_plugin_function(
            plugin_path=plugin_path,
            function_name="min",
            args=self._expr,
            kwargs={"timeperiod": timeperiod},
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
        return register_plugin_function(
            plugin_path=plugin_path,
            function_name="minindex",
            args=self._expr,
            kwargs={"timeperiod": timeperiod},
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
        return register_plugin_function(
            plugin_path=plugin_path,
            function_name="minmax",
            args=self._expr,
            kwargs={"timeperiod": timeperiod},
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
        return register_plugin_function(
            plugin_path=plugin_path,
            function_name="minmaxindex",
            args=self._expr,
            kwargs={"timeperiod": timeperiod},
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
        return register_plugin_function(
            plugin_path=plugin_path,
            function_name="mult",
            args=[self._expr, b],
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
        return register_plugin_function(
            plugin_path=plugin_path,
            function_name="sub",
            args=[self._expr, b],
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
        return register_plugin_function(
            plugin_path=plugin_path,
            function_name="sum",
            args=self._expr,
            kwargs={"timeperiod": timeperiod},
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
        return register_plugin_function(
            plugin_path=plugin_path,
            function_name="acos",
            args=self._expr,
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
        return register_plugin_function(
            plugin_path=plugin_path,
            function_name="asin",
            args=self._expr,
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
        return register_plugin_function(
            plugin_path=plugin_path,
            function_name="atan",
            args=self._expr,
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
        return register_plugin_function(
            plugin_path=plugin_path,
            function_name="ceil",
            args=self._expr,
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
        return register_plugin_function(
            plugin_path=plugin_path,
            function_name="cos",
            args=self._expr,
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
        return register_plugin_function(
            plugin_path=plugin_path,
            function_name="cosh",
            args=self._expr,
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
        return register_plugin_function(
            plugin_path=plugin_path,
            function_name="exp",
            args=self._expr,
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
        return register_plugin_function(
            plugin_path=plugin_path,
            function_name="floor",
            args=self._expr,
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
        return register_plugin_function(
            plugin_path=plugin_path,
            function_name="ln",
            args=self._expr,
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
        return register_plugin_function(
            plugin_path=plugin_path,
            function_name="log10",
            args=self._expr,
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
        return register_plugin_function(
            plugin_path=plugin_path,
            function_name="sin",
            args=self._expr,
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
        return register_plugin_function(
            plugin_path=plugin_path,
            function_name="sinh",
            args=self._expr,
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
        return register_plugin_function(
            plugin_path=plugin_path,
            function_name="sqrt",
            args=self._expr,
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
        return register_plugin_function(
            plugin_path=plugin_path,
            function_name="tan",
            args=self._expr,
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
        return register_plugin_function(
            plugin_path=plugin_path,
            function_name="tanh",
            args=self._expr,
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
        return register_plugin_function(
            plugin_path=plugin_path,
            function_name="adx",
            args=[self._expr, high, low],
            kwargs={"timeperiod": timeperiod},
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
        return register_plugin_function(
            plugin_path=plugin_path,
            function_name="adxr",
            args=[self._expr, high, low],
            kwargs={"timeperiod": timeperiod},
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
        return register_plugin_function(
            plugin_path=plugin_path,
            function_name="apo",
            args=self._expr,
            kwargs={
                "fastperiod": fastperiod,
                "slowperiod": slowperiod,
                "matype": matype,
            },
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
        return register_plugin_function(
            plugin_path=plugin_path,
            function_name="aroon",
            args=[self._expr, low],
            kwargs={"timeperiod": timeperiod},
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
        return register_plugin_function(
            plugin_path=plugin_path,
            function_name="aroonosc",
            args=[self._expr, low],
            kwargs={"timeperiod": timeperiod},
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
        return register_plugin_function(
            plugin_path=plugin_path,
            function_name="bop",
            args=[self._expr, high, low, close],
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
        return register_plugin_function(
            plugin_path=plugin_path,
            function_name="cci",
            args=[self._expr, high, low],
            kwargs={"timeperiod": timeperiod},
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
        return register_plugin_function(
            plugin_path=plugin_path,
            function_name="cmo",
            args=self._expr,
            kwargs={"timeperiod": timeperiod},
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
        return register_plugin_function(
            plugin_path=plugin_path,
            function_name="dx",
            args=[self._expr, high, low],
            kwargs={"timeperiod": timeperiod},
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
        return register_plugin_function(
            plugin_path=plugin_path,
            function_name="macd",
            args=self._expr,
            kwargs={
                "fastperiod": fastperiod,
                "slowperiod": slowperiod,
                "signalperiod": signalperiod,
            },
            is_elementwise=False,
        )

    def macdext(
            self,
            fastperiod: int = 12,
            fastmatype: int = 0,
            slowperiod: int = 26,
            slowmatype: int = 0,
            signalperiod: int = 9,
            signalmatype: int = 0,
    ) -> pl.Expr:
        """MACD with controllable MA type (Momentum Indicators)
        pl.col("close").ta.macdext(fastperiod=12, slowperiod=26, signalperiod=9, fastmatype=0, slowmatype=0, signalmatype=0)

        Inputs:
            prices: ['close']
        Parameters:
            fastperiod: 12
            fastmatype: 0
            slowperiod: 26
            slowmatype: 0
            signalperiod: 9
            signalmatype: 0
        Outputs:
            macd
            macdsignal
            macdhist
        """
        return register_plugin_function(
            plugin_path=plugin_path,
            function_name="macdext",
            args=self._expr,
            kwargs={
                "fastperiod": fastperiod,
                "fastmatype": fastmatype,
                "slowperiod": slowperiod,
                "slowmatype": slowmatype,
                "signalperiod": signalperiod,
                "signalmatype": signalmatype,
            },
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
        return register_plugin_function(
            plugin_path=plugin_path,
            function_name="macdfix",
            args=self._expr,
            kwargs={"signalperiod": signalperiod},
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
        return register_plugin_function(
            plugin_path=plugin_path,
            function_name="mfi",
            args=[self._expr, high, low, volume],
            kwargs={"timeperiod": timeperiod},
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
        return register_plugin_function(
            plugin_path=plugin_path,
            function_name="minus_di",
            args=[self._expr, high, low],
            kwargs={"timeperiod": timeperiod},
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
        return register_plugin_function(
            plugin_path=plugin_path,
            function_name="minus_dm",
            args=[self._expr, low],
            kwargs={"timeperiod": timeperiod},
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
        return register_plugin_function(
            plugin_path=plugin_path,
            function_name="mom",
            args=self._expr,
            kwargs={"timeperiod": timeperiod},
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
        return register_plugin_function(
            plugin_path=plugin_path,
            function_name="plus_di",
            args=[self._expr, high, low],
            kwargs={"timeperiod": timeperiod},
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
        return register_plugin_function(
            plugin_path=plugin_path,
            function_name="plus_dm",
            args=[self._expr, low],
            kwargs={"timeperiod": timeperiod},
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
        return register_plugin_function(
            plugin_path=plugin_path,
            function_name="ppo",
            args=self._expr,
            kwargs={"fastperiod": fastperiod, "slowperiod": slowperiod, "matype": matype},
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
        return register_plugin_function(
            plugin_path=plugin_path,
            function_name="roc",
            args=self._expr,
            kwargs={"timeperiod": timeperiod},
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
        return register_plugin_function(
            plugin_path=plugin_path,
            function_name="rocp",
            args=self._expr,
            kwargs={"timeperiod": timeperiod},
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
        return register_plugin_function(
            plugin_path=plugin_path,
            function_name="rocr",
            args=self._expr,
            kwargs={"timeperiod": timeperiod},
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
        return register_plugin_function(
            plugin_path=plugin_path,
            function_name="rocr100",
            args=self._expr,
            kwargs={"timeperiod": timeperiod},
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
        return register_plugin_function(
            plugin_path=plugin_path,
            function_name="rsi",
            args=self._expr,
            kwargs={"timeperiod": timeperiod},
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
        return register_plugin_function(
            plugin_path=plugin_path,
            function_name="stoch",
            args=[self._expr, high, low],
            kwargs={
                "fastk_period": fastk_period,
                "slowk_period": slowk_period,
                "slowk_matype": slowk_matype,
                "slowd_period": slowd_period,
                "slowd_matype": slowd_matype,
            },
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
        return register_plugin_function(
            plugin_path=plugin_path,
            function_name="stochf",
            args=[self._expr, high, low],
            kwargs={
                "fastk_period": fastk_period,
                "fastd_period": fastd_period,
                "fastd_matype": fastd_matype,
            },
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
        return register_plugin_function(
            plugin_path=plugin_path,
            function_name="stochrsi",
            args=self._expr,
            kwargs={
                "timeperiod": timeperiod,
                "fastk_period": fastk_period,
                "fastd_period": fastd_period,
                "fastd_matype": fastd_matype,
            },
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
        return register_plugin_function(
            plugin_path=plugin_path,
            function_name="trix",
            args=self._expr,
            kwargs={"timeperiod": timeperiod},
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
            prices: ['high', 'low', 'close']
        Parameters:
            timeperiod1: 7
            timeperiod2: 14
            timeperiod3: 28
        Outputs:
            real
        """
        return register_plugin_function(
            plugin_path=plugin_path,
            function_name="ultosc",
            args=[self._expr, high, low],
            kwargs={
                "timeperiod1": timeperiod1,
                "timeperiod2": timeperiod2,
                "timeperiod3": timeperiod3,
            },
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
        return register_plugin_function(
            plugin_path=plugin_path,
            function_name="willr",
            args=[self._expr, high, low],
            kwargs={"timeperiod": timeperiod},
            is_elementwise=False,
        )

    def bbands(
            self, timeperiod: int = 5, nbdevup: float = 2.0, nbdevdn: float = 2.0, matype: int = 0
    ) -> pl.Expr:
        """Bollinger Bands (Overlap Studies)
        ta.pol("close").ta.bbands(timeperiod=5, nbdevup=2.0, nbdevdn=2.0, matype=0)

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
        return register_plugin_function(
            plugin_path=plugin_path,
            function_name="bbands",
            args=self._expr,
            kwargs={
                "timeperiod": timeperiod,
                "nbdevup": nbdevup,
                "nbdevdn": nbdevdn,
                "matype": matype,
            },
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
        return register_plugin_function(
            plugin_path=plugin_path,
            function_name="dema",
            args=self._expr,
            kwargs={"timeperiod": timeperiod},
            is_elementwise=False,
        )

    def ema(self, timeperiod: int = 30) -> pl.Expr:
        """Exponential Moving Average (Overlap Studies)
        ta.pol("close").ta.ema(timeperiod=30)

        Inputs:
            real: (any ndarray)
        Parameters:
            timeperiod: 30
        Outputs:
            real
        """
        return register_plugin_function(
            plugin_path=plugin_path,
            function_name="ema",
            args=self._expr,
            kwargs={"timeperiod": timeperiod},
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
        return register_plugin_function(
            plugin_path=plugin_path,
            function_name="ht_trendline",
            args=self._expr,
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
        return register_plugin_function(
            plugin_path=plugin_path,
            function_name="kama",
            args=self._expr,
            kwargs={"timeperiod": timeperiod},
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
        return register_plugin_function(
            plugin_path=plugin_path,
            function_name="ma",
            args=self._expr,
            kwargs={"timeperiod": timeperiod, "matype": matype},
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
        return register_plugin_function(
            plugin_path=plugin_path,
            function_name="mama",
            args=self._expr,
            kwargs={"fastlimit": fastlimit, "slowlimit": slowlimit},
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
        return register_plugin_function(
            plugin_path=plugin_path,
            function_name="mavp",
            args=[self._expr, periods],
            kwargs={"minperiod": minperiod, "maxperiod": maxperiod, "matype": matype},
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
        return register_plugin_function(
            plugin_path=plugin_path,
            function_name="midpoint",
            args=self._expr,
            kwargs={"timeperiod": timeperiod},
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
        return register_plugin_function(
            plugin_path=plugin_path,
            function_name="midprice",
            args=[self._expr, low],
            kwargs={"timeperiod": timeperiod},
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
        return register_plugin_function(
            plugin_path=plugin_path,
            function_name="sar",
            args=[self._expr, low],
            kwargs={"acceleration": acceleration, "maximum": maximum},
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
        return register_plugin_function(
            plugin_path=plugin_path,
            function_name="sarext",
            args=[self._expr, low],
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
        return register_plugin_function(
            plugin_path=plugin_path,
            function_name="sma",
            args=self._expr,
            kwargs={"timeperiod": timeperiod},
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
        return register_plugin_function(
            plugin_path=plugin_path,
            function_name="t3",
            args=self._expr,
            kwargs={"timeperiod": timeperiod, "vfactor": vfactor},
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
        return register_plugin_function(
            plugin_path=plugin_path,
            function_name="tema",
            args=self._expr,
            kwargs={"timeperiod": timeperiod},
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
        return register_plugin_function(
            plugin_path=plugin_path,
            function_name="trima",
            args=self._expr,
            kwargs={"timeperiod": timeperiod},
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
        return register_plugin_function(
            plugin_path=plugin_path,
            function_name="wma",
            args=self._expr,
            kwargs={"timeperiod": timeperiod},
            is_elementwise=False,
        )

    def cdl2crows(
            self,
            high: IntoExpr = pl.col("high"),
            low: IntoExpr = pl.col("low"),
            close: IntoExpr = pl.col("close"),
    ) -> pl.Expr:
        """Two Crows (Pattern Recognition)
            pl.col("open").ta.cdl2crows(pl.col("high"), pl.col("low"), pl.col("close"))

        Inputs:
            prices: ['open', 'high', 'low', 'close']
        Outputs:
            integer (values are -100, 0 or 100)
        """
        return register_plugin_function(
            plugin_path=plugin_path,
            function_name="cdl2crows",
            args=[self._expr, high, low, close],
            is_elementwise=False,
        )

    def cdl3blackcrows(
            self,
            high: IntoExpr = pl.col("high"),
            low: IntoExpr = pl.col("low"),
            close: IntoExpr = pl.col("close"),
    ) -> pl.Expr:
        """Three Black Crows (Pattern Recognition)
            pl.col("open").ta.cdl3blackcrows(pl.col("high"), pl.col("low"), pl.col("close"))

        Inputs:
            prices: ['open', 'high', 'low', 'close']
        Outputs:
            integer (values are -100, 0 or 100)
        """
        return register_plugin_function(
            plugin_path=plugin_path,
            function_name="cdl3blackcrows",
            args=[self._expr, high, low, close],
            is_elementwise=False,
        )

    def cdl3inside(
            self,
            high: IntoExpr = pl.col("high"),
            low: IntoExpr = pl.col("low"),
            close: IntoExpr = pl.col("close"),
    ) -> pl.Expr:
        """Three Inside Up/Down (Pattern Recognition)
            pl.col("open").ta.cdl3inside(pl.col("high"), pl.col("low"), pl.col("close"))

        Inputs:
            prices: ['open', 'high', 'low', 'close']
        Outputs:
            integer (values are -100, 0 or 100)
        """
        return register_plugin_function(
            plugin_path=plugin_path,
            function_name="cdl3inside",
            args=[self._expr, high, low, close],
            is_elementwise=False,
        )

    def cdl3linestrike(
            self,
            high: IntoExpr = pl.col("high"),
            low: IntoExpr = pl.col("low"),
            close: IntoExpr = pl.col("close"),
    ) -> pl.Expr:
        """Three-Line Strike  (Pattern Recognition)
            pl.col("open").ta.cdl3linestrike(pl.col("high"), pl.col("low"), pl.col("close"))

        Inputs:
            prices: ['open', 'high', 'low', 'close']
        Outputs:
            integer (values are -100, 0 or 100)
        """
        return register_plugin_function(
            plugin_path=plugin_path,
            function_name="cdl3linestrike",
            args=[self._expr, high, low, close],
            is_elementwise=False,
        )

    def cdl3outside(
            self,
            high: IntoExpr = pl.col("high"),
            low: IntoExpr = pl.col("low"),
            close: IntoExpr = pl.col("close"),
    ) -> pl.Expr:
        """Three Outside Up/Down (Pattern Recognition)
            pl.col("open").ta.cdl3outside(pl.col("high"), pl.col("low"), pl.col("close"))

        Inputs:
            prices: ['open', 'high', 'low', 'close']
        Outputs:
            integer (values are -100, 0 or 100)
        """
        return register_plugin_function(
            plugin_path=plugin_path,
            function_name="cdl3outside",
            args=[self._expr, high, low, close],
            is_elementwise=False,
        )

    def cdl3starsinsouth(
            self,
            high: IntoExpr = pl.col("high"),
            low: IntoExpr = pl.col("low"),
            close: IntoExpr = pl.col("close"),
    ) -> pl.Expr:
        """Three Stars In The South (Pattern Recognition)
            pl.col("open").ta.cdl3starsinsouth(pl.col("high"), pl.col("low"), pl.col("close"))

        Inputs:
            prices: ['open', 'high', 'low', 'close']
        Outputs:
            integer (values are -100, 0 or 100)
        """
        return register_plugin_function(
            plugin_path=plugin_path,
            function_name="cdl3starsinsouth",
            args=[self._expr, high, low, close],
            is_elementwise=False,
        )

    def cdl3whitesoldiers(
            self,
            high: IntoExpr = pl.col("high"),
            low: IntoExpr = pl.col("low"),
            close: IntoExpr = pl.col("close"),
    ) -> pl.Expr:
        """Three Advancing White Soldiers (Pattern Recognition)
            pl.col("open").ta.cdl3whitesoldiers(pl.col("high"), pl.col("low"), pl.col("close"))

        Inputs:
            prices: ['open', 'high', 'low', 'close']
        Outputs:
            integer (values are -100, 0 or 100)
        """
        return register_plugin_function(
            plugin_path=plugin_path,
            function_name="cdl3whitesoldiers",
            args=[self._expr, high, low, close],
            is_elementwise=False,
        )

    def cdlabandonedbaby(
            self,
            high: IntoExpr = pl.col("high"),
            low: IntoExpr = pl.col("low"),
            close: IntoExpr = pl.col("close"),
            penetration: float = 0.3,
    ) -> pl.Expr:
        """Abandoned Baby (Pattern Recognition)
            pl.col("open").ta.cdlabandonedbaby(pl.col("high"), pl.col("low"), pl.col("close"), penetration=0.3)

        Inputs:
            prices: ['open', 'high', 'low', 'close']
        Parameters:
            penetration: 0.3
        Outputs:
            integer (values are -100, 0 or 100)
        """
        return register_plugin_function(
            plugin_path=plugin_path,
            function_name="cdlabandonedbaby",
            args=[self._expr, high, low, close],
            kwargs={"penetration": penetration},
            is_elementwise=False,
        )

    def cdladvanceblock(
            self,
            high: IntoExpr = pl.col("high"),
            low: IntoExpr = pl.col("low"),
            close: IntoExpr = pl.col("close"),
    ) -> pl.Expr:
        """Advance Block (Pattern Recognition)
            pl.col("open").ta.cdladvanceblock(pl.col("high"), pl.col("low"), pl.col("close"))

        Inputs:
            prices: ['open', 'high', 'low', 'close']
        Outputs:
            integer (values are -100, 0 or 100)
        """
        return register_plugin_function(
            plugin_path=plugin_path,
            function_name="cdladvanceblock",
            args=[self._expr, high, low, close],
            is_elementwise=False,
        )

    def cdlbelthold(
            self,
            high: IntoExpr = pl.col("high"),
            low: IntoExpr = pl.col("low"),
            close: IntoExpr = pl.col("close"),
    ) -> pl.Expr:
        """Belt-hold (Pattern Recognition)
            pl.col("open").ta.cdlbelthold(pl.col("high"), pl.col("low"), pl.col("close"))

        Inputs:
            prices: ['open', 'high', 'low', 'close']
        Outputs:
            integer (values are -100, 0 or 100)
        """
        return register_plugin_function(
            plugin_path=plugin_path,
            function_name="cdlbelthold",
            args=[self._expr, high, low, close],
            is_elementwise=False,
        )

    def cdlbreakaway(
            self,
            high: IntoExpr = pl.col("high"),
            low: IntoExpr = pl.col("low"),
            close: IntoExpr = pl.col("close"),
    ) -> pl.Expr:
        """Breakaway (Pattern Recognition)
            pl.col("open").ta.cdlbreakaway(pl.col("high"), pl.col("low"), pl.col("close"))

        Inputs:
            prices: ['open', 'high', 'low', 'close']
        Outputs:
            integer (values are -100, 0 or 100)
        """
        return register_plugin_function(
            plugin_path=plugin_path,
            function_name="cdlbreakaway",
            args=[self._expr, high, low, close],
            is_elementwise=False,
        )

    def cdlclosingmarubozu(
            self,
            high: IntoExpr = pl.col("high"),
            low: IntoExpr = pl.col("low"),
            close: IntoExpr = pl.col("close"),
    ) -> pl.Expr:
        """Closing Marubozu (Pattern Recognition)
            pl.col("open").ta.cdlclosingmarubozu(pl.col("high"), pl.col("low"), pl.col("close"))

        Inputs:
            prices: ['open', 'high', 'low', 'close']
        Outputs:
            integer (values are -100, 0 or 100)
        """
        return register_plugin_function(
            plugin_path=plugin_path,
            function_name="cdlclosingmarubozu",
            args=[self._expr, high, low, close],
            is_elementwise=False,
        )

    def cdlconcealbabyswall(
            self,
            high: IntoExpr = pl.col("high"),
            low: IntoExpr = pl.col("low"),
            close: IntoExpr = pl.col("close"),
    ) -> pl.Expr:
        """Concealing Baby Swallow (Pattern Recognition)
            pl.col("open").ta.cdlconcealbabyswall(pl.col("high"), pl.col("low"), pl.col("close"))

        Inputs:
            prices: ['open', 'high', 'low', 'close']
        Outputs:
            integer (values are -100, 0 or 100)
        """
        return register_plugin_function(
            plugin_path=plugin_path,
            function_name="cdlconcealbabyswall",
            args=[self._expr, high, low, close],
            is_elementwise=False,
        )

    def cdlcounterattack(
            self,
            high: IntoExpr = pl.col("high"),
            low: IntoExpr = pl.col("low"),
            close: IntoExpr = pl.col("close"),
    ) -> pl.Expr:
        """Counterattack (Pattern Recognition)
            pl.col("open").ta.cdlcounterattack(pl.col("high"), pl.col("low"), pl.col("close"))

        Inputs:
            prices: ['open', 'high', 'low', 'close']
        Outputs:
            integer (values are -100, 0 or 100)
        """
        return register_plugin_function(
            plugin_path=plugin_path,
            function_name="cdlcounterattack",
            args=[self._expr, high, low, close],
            is_elementwise=False,
        )

    def cdldarkcloudcover(
            self,
            high: IntoExpr = pl.col("high"),
            low: IntoExpr = pl.col("low"),
            close: IntoExpr = pl.col("close"),
            penetration: float = 0.5,
    ) -> pl.Expr:
        """Dark Cloud Cover (Pattern Recognition)
            pl.col("open").ta.cdldarkcloudcover(pl.col("high"), pl.col("low"), pl.col("close"), penetration=0.5)

        Inputs:
            prices: ['open', 'high', 'low', 'close']
        Parameters:
            penetration: 0.5
        Outputs:
            integer (values are -100, 0 or 100)
        """
        return register_plugin_function(
            plugin_path=plugin_path,
            function_name="cdldarkcloudcover",
            args=[self._expr, high, low, close],
            kwargs={"penetration": penetration},
            is_elementwise=False,
        )

    def cdldoji(
            self,
            high: IntoExpr = pl.col("high"),
            low: IntoExpr = pl.col("low"),
            close: IntoExpr = pl.col("close"),
    ) -> pl.Expr:
        """Doji (Pattern Recognition)
            pl.col("open").ta.cdldoji(pl.col("high"), pl.col("low"), pl.col("close"))

        Inputs:
            prices: ['open', 'high', 'low', 'close']
        Outputs:
            integer (values are -100, 0 or 100)
        """
        return register_plugin_function(
            plugin_path=plugin_path,
            function_name="cdldoji",
            args=[self._expr, high, low, close],
            is_elementwise=False,
        )

    def cdldojistar(
            self,
            high: IntoExpr = pl.col("high"),
            low: IntoExpr = pl.col("low"),
            close: IntoExpr = pl.col("close"),
    ) -> pl.Expr:
        """Doji Star (Pattern Recognition)
            pl.col("open").ta.cdldojistar(pl.col("high"), pl.col("low"), pl.col("close"))

        Inputs:
            prices: ['open', 'high', 'low', 'close']
        Outputs:
            integer (values are -100, 0 or 100)
        """
        return register_plugin_function(
            plugin_path=plugin_path,
            function_name="cdldojistar",
            args=[self._expr, high, low, close],
            is_elementwise=False,
        )

    def cdldragonflydoji(
            self,
            high: IntoExpr = pl.col("high"),
            low: IntoExpr = pl.col("low"),
            close: IntoExpr = pl.col("close"),
    ) -> pl.Expr:
        """Dragonfly Doji (Pattern Recognition)
            pl.col("open").ta.cdldragonflydoji(pl.col("high"), pl.col("low"), pl.col("close"))

        Inputs:
            prices: ['open', 'high', 'low', 'close']
        Outputs:
            integer (values are -100, 0 or 100)
        """
        return register_plugin_function(
            plugin_path=plugin_path,
            function_name="cdldragonflydoji",
            args=[self._expr, high, low, close],
            is_elementwise=False,
        )

    def cdlengulfing(
            self,
            high: IntoExpr = pl.col("high"),
            low: IntoExpr = pl.col("low"),
            close: IntoExpr = pl.col("close"),
    ) -> pl.Expr:
        """Engulfing Pattern (Pattern Recognition)
            pl.col("open").ta.cdlengulfing(pl.col("high"), pl.col("low"), pl.col("close"))

        Inputs:
            prices: ['open', 'high', 'low', 'close']
        Outputs:
            integer (values are -100, 0 or 100)
        """
        return register_plugin_function(
            plugin_path=plugin_path,
            function_name="cdlengulfing",
            args=[self._expr, high, low, close],
            is_elementwise=False,
        )

    def cdleveningdojistar(
            self,
            high: IntoExpr = pl.col("high"),
            low: IntoExpr = pl.col("low"),
            close: IntoExpr = pl.col("close"),
            penetration: float = 0.3,
    ) -> pl.Expr:
        """Evening Doji Star (Pattern Recognition)
            pl.col("open").ta.cdleveningdojistar(pl.col("high"), pl.col("low"), pl.col("close"), penetration=0.3)

        Inputs:
            prices: ['open', 'high', 'low', 'close']
        Parameters:
            penetration: 0.3
        Outputs:
            integer (values are -100, 0 or 100)
        """
        return register_plugin_function(
            plugin_path=plugin_path,
            function_name="cdleveningdojistar",
            args=[self._expr, high, low, close],
            kwargs={"penetration": penetration},
            is_elementwise=False,
        )

    def cdleveningstar(
            self,
            high: IntoExpr = pl.col("high"),
            low: IntoExpr = pl.col("low"),
            close: IntoExpr = pl.col("close"),
            penetration: float = 0.3,
    ) -> pl.Expr:
        """Evening Star (Pattern Recognition)
            pl.col("open").ta.cdleveningstar(pl.col("high"), pl.col("low"), pl.col("close"), penetration=0.3)

        Inputs:
            prices: ['open', 'high', 'low', 'close']
        Parameters:
            penetration: 0.3
        Outputs:
            integer (values are -100, 0 or 100)
        """
        return register_plugin_function(
            plugin_path=plugin_path,
            function_name="cdleveningstar",
            args=[self._expr, high, low, close],
            kwargs={"penetration": penetration},
            is_elementwise=False,
        )

    def cdlgapsidesidewhite(
            self,
            high: IntoExpr = pl.col("high"),
            low: IntoExpr = pl.col("low"),
            close: IntoExpr = pl.col("close"),
    ) -> pl.Expr:
        """Up/Down-gap side-by-side white lines (Pattern Recognition)
            pl.col("open").ta.cdlgapsidesidewhite(pl.col("high"), pl.col("low"), pl.col("close"))

        Inputs:
            prices: ['open', 'high', 'low', 'close']
        Outputs:
            integer (values are -100, 0 or 100)
        """
        return register_plugin_function(
            plugin_path=plugin_path,
            function_name="cdlgapsidesidewhite",
            args=[self._expr, high, low, close],
            is_elementwise=False,
        )

    def cdlgravestonedoji(
            self,
            high: IntoExpr = pl.col("high"),
            low: IntoExpr = pl.col("low"),
            close: IntoExpr = pl.col("close"),
    ) -> pl.Expr:
        """Gravestone Doji (Pattern Recognition)
            pl.col("open").ta.cdlgravestonedoji(pl.col("high"), pl.col("low"), pl.col("close"))

        Inputs:
            prices: ['open', 'high', 'low', 'close']
        Outputs:
            integer (values are -100, 0 or 100)
        """
        return register_plugin_function(
            plugin_path=plugin_path,
            function_name="cdlgravestonedoji",
            args=[self._expr, high, low, close],
            is_elementwise=False,
        )

    def cdlhammer(
            self,
            high: IntoExpr = pl.col("high"),
            low: IntoExpr = pl.col("low"),
            close: IntoExpr = pl.col("close"),
    ) -> pl.Expr:
        """Hammer (Pattern Recognition)
            pl.col("open").ta.cdlhammer(pl.col("high"), pl.col("low"), pl.col("close"))

        Inputs:
            prices: ['open', 'high', 'low', 'close']
        Outputs:
            integer (values are -100, 0 or 100)
        """
        return register_plugin_function(
            plugin_path=plugin_path,
            function_name="cdlhammer",
            args=[self._expr, high, low, close],
            is_elementwise=False,
        )

    def cdlhangingman(
            self,
            high: IntoExpr = pl.col("high"),
            low: IntoExpr = pl.col("low"),
            close: IntoExpr = pl.col("close"),
    ) -> pl.Expr:
        """Hanging Man (Pattern Recognition)
            pl.col("open").ta.cdlhangingman(pl.col("high"), pl.col("low"), pl.col("close"))

        Inputs:
            prices: ['open', 'high', 'low', 'close']
        Outputs:
            integer (values are -100, 0 or 100)
        """
        return register_plugin_function(
            plugin_path=plugin_path,
            function_name="cdlhangingman",
            args=[self._expr, high, low, close],
            is_elementwise=False,
        )

    def cdlharami(
            self,
            high: IntoExpr = pl.col("high"),
            low: IntoExpr = pl.col("low"),
            close: IntoExpr = pl.col("close"),
    ) -> pl.Expr:
        """Harami Pattern (Pattern Recognition)
            pl.col("open").ta.cdlharami(pl.col("high"), pl.col("low"), pl.col("close"))

        Inputs:
            prices: ['open', 'high', 'low', 'close']
        Outputs:
            integer (values are -100, 0 or 100)
        """
        return register_plugin_function(
            plugin_path=plugin_path,
            function_name="cdlharami",
            args=[self._expr, high, low, close],
            is_elementwise=False,
        )

    def cdlharamicross(
            self,
            high: IntoExpr = pl.col("high"),
            low: IntoExpr = pl.col("low"),
            close: IntoExpr = pl.col("close"),
    ) -> pl.Expr:
        """Harami Cross Pattern (Pattern Recognition)
            pl.col("open").ta.cdlharamicross(pl.col("high"), pl.col("low"), pl.col("close"))

        Inputs:
            prices: ['open', 'high', 'low', 'close']
        Outputs:
            integer (values are -100, 0 or 100)
        """
        return register_plugin_function(
            plugin_path=plugin_path,
            function_name="cdlharamicross",
            args=[self._expr, high, low, close],
            is_elementwise=False,
        )

    def cdlhighwave(
            self,
            high: IntoExpr = pl.col("high"),
            low: IntoExpr = pl.col("low"),
            close: IntoExpr = pl.col("close"),
    ) -> pl.Expr:
        """High-Wave Candle (Pattern Recognition)
            pl.col("open").ta.cdlhighwave(pl.col("high"), pl.col("low"), pl.col("close"))

        Inputs:
            prices: ['open', 'high', 'low', 'close']
        Outputs:
            integer (values are -100, 0 or 100)
        """
        return register_plugin_function(
            plugin_path=plugin_path,
            function_name="cdlhighwave",
            args=[self._expr, high, low, close],
            is_elementwise=False,
        )

    def cdlhikkake(
            self,
            high: IntoExpr = pl.col("high"),
            low: IntoExpr = pl.col("low"),
            close: IntoExpr = pl.col("close"),
    ) -> pl.Expr:
        """Hikkake Pattern (Pattern Recognition)
            pl.col("open").ta.cdlhikkake(pl.col("high"), pl.col("low"), pl.col("close"))

        Inputs:
            prices: ['open', 'high', 'low', 'close']
        Outputs:
            integer (values are -100, 0 or 100)
        """
        return register_plugin_function(
            plugin_path=plugin_path,
            function_name="cdlhikkake",
            args=[self._expr, high, low, close],
            is_elementwise=False,
        )

    def cdlhikkakemod(
            self,
            high: IntoExpr = pl.col("high"),
            low: IntoExpr = pl.col("low"),
            close: IntoExpr = pl.col("close"),
    ) -> pl.Expr:
        """Modified Hikkake Pattern (Pattern Recognition)
            pl.col("open").ta.cdlhikkakemod(pl.col("high"), pl.col("low"), pl.col("close"))

        Inputs:
            prices: ['open', 'high', 'low', 'close']
        Outputs:
            integer (values are -100, 0 or 100)
        """
        return register_plugin_function(
            plugin_path=plugin_path,
            function_name="cdlhikkakemod",
            args=[self._expr, high, low, close],
            is_elementwise=False,
        )

    def cdlhomingpigeon(
            self,
            high: IntoExpr = pl.col("high"),
            low: IntoExpr = pl.col("low"),
            close: IntoExpr = pl.col("close"),
    ) -> pl.Expr:
        """Homing Pigeon (Pattern Recognition)
            pl.col("open").ta.cdlhomingpigeon(pl.col("high"), pl.col("low"), pl.col("close"))

        Inputs:
            prices: ['open', 'high', 'low', 'close']
        Outputs:
            integer (values are -100, 0 or 100)
        """
        return register_plugin_function(
            plugin_path=plugin_path,
            function_name="cdlhomingpigeon",
            args=[self._expr, high, low, close],
            is_elementwise=False,
        )

    def cdlidentical3crows(
            self,
            high: IntoExpr = pl.col("high"),
            low: IntoExpr = pl.col("low"),
            close: IntoExpr = pl.col("close"),
    ) -> pl.Expr:
        """Identical Three Crows (Pattern Recognition)
            pl.col("open").ta.cdlidentical3crows(pl.col("high"), pl.col("low"), pl.col("close"))

        Inputs:
            prices: ['open', 'high', 'low', 'close']
        Outputs:
            integer (values are -100, 0 or 100)
        """
        return register_plugin_function(
            plugin_path=plugin_path,
            function_name="cdlidentical3crows",
            args=[self._expr, high, low, close],
            is_elementwise=False,
        )

    def cdlinneck(
            self,
            high: IntoExpr = pl.col("high"),
            low: IntoExpr = pl.col("low"),
            close: IntoExpr = pl.col("close"),
    ) -> pl.Expr:
        """In-Neck Pattern (Pattern Recognition)
            pl.col("open").ta.cdlinneck(pl.col("high"), pl.col("low"), pl.col("close"))

        Inputs:
            prices: ['open', 'high', 'low', 'close']
        Outputs:
            integer (values are -100, 0 or 100)
        """
        return register_plugin_function(
            plugin_path=plugin_path,
            function_name="cdlinneck",
            args=[self._expr, high, low, close],
            is_elementwise=False,
        )

    def cdlinvertedhammer(
            self,
            high: IntoExpr = pl.col("high"),
            low: IntoExpr = pl.col("low"),
            close: IntoExpr = pl.col("close"),
    ) -> pl.Expr:
        """Inverted Hammer (Pattern Recognition)
            pl.col("open").ta.cdlinvertedhammer(pl.col("high"), pl.col("low"), pl.col("close"))

        Inputs:
            prices: ['open', 'high', 'low', 'close']
        Outputs:
            integer (values are -100, 0 or 100)
        """
        return register_plugin_function(
            plugin_path=plugin_path,
            function_name="cdlinvertedhammer",
            args=[self._expr, high, low, close],
            is_elementwise=False,
        )

    def cdlkicking(
            self,
            high: IntoExpr = pl.col("high"),
            low: IntoExpr = pl.col("low"),
            close: IntoExpr = pl.col("close"),
    ) -> pl.Expr:
        """Kicking (Pattern Recognition)
            pl.col("open").ta.cdlkicking(pl.col("high"), pl.col("low"), pl.col("close"))

        Inputs:
            prices: ['open', 'high', 'low', 'close']
        Outputs:
            integer (values are -100, 0 or 100)
        """
        return register_plugin_function(
            plugin_path=plugin_path,
            function_name="cdlkicking",
            args=[self._expr, high, low, close],
            is_elementwise=False,
        )

    def cdlkickingbylength(
            self,
            high: IntoExpr = pl.col("high"),
            low: IntoExpr = pl.col("low"),
            close: IntoExpr = pl.col("close"),
    ) -> pl.Expr:
        """Kicking - bull/bear determined by the longer marubozu (Pattern Recognition)
            pl.col("open").ta.cdlkickingbylength(pl.col("high"), pl.col("low"), pl.col("close"))

        Inputs:
            prices: ['open', 'high', 'low', 'close']
        Outputs:
            integer (values are -100, 0 or 100)
        """
        return register_plugin_function(
            plugin_path=plugin_path,
            function_name="cdlkickingbylength",
            args=[self._expr, high, low, close],
            is_elementwise=False,
        )

    def cdlladderbottom(
            self,
            high: IntoExpr = pl.col("high"),
            low: IntoExpr = pl.col("low"),
            close: IntoExpr = pl.col("close"),
    ) -> pl.Expr:
        """Ladder Bottom (Pattern Recognition)
            pl.col("open").ta.cdlladderbottom(pl.col("high"), pl.col("low"), pl.col("close"))

        Inputs:
            prices: ['open', 'high', 'low', 'close']
        Outputs:
            integer (values are -100, 0 or 100)
        """
        return register_plugin_function(
            plugin_path=plugin_path,
            function_name="cdlladderbottom",
            args=[self._expr, high, low, close],
            is_elementwise=False,
        )

    def cdllongleggeddoji(
            self,
            high: IntoExpr = pl.col("high"),
            low: IntoExpr = pl.col("low"),
            close: IntoExpr = pl.col("close"),
    ) -> pl.Expr:
        """Long Legged Doji (Pattern Recognition)
            pl.col("open").ta.cdllongleggeddoji(pl.col("high"), pl.col("low"), pl.col("close"))

        Inputs:
            prices: ['open', 'high', 'low', 'close']
        Outputs:
            integer (values are -100, 0 or 100)
        """
        return register_plugin_function(
            plugin_path=plugin_path,
            function_name="cdllongleggeddoji",
            args=[self._expr, high, low, close],
            is_elementwise=False,
        )

    def cdllongline(
            self,
            high: IntoExpr = pl.col("high"),
            low: IntoExpr = pl.col("low"),
            close: IntoExpr = pl.col("close"),
    ) -> pl.Expr:
        """Long Line Candle (Pattern Recognition)
            pl.col("open").ta.cdllongline(pl.col("high"), pl.col("low"), pl.col("close"))

        Inputs:
            prices: ['open', 'high', 'low', 'close']
        Outputs:
            integer (values are -100, 0 or 100)
        """
        return register_plugin_function(
            plugin_path=plugin_path,
            function_name="cdllongline",
            args=[self._expr, high, low, close],
            is_elementwise=False,
        )

    def cdlmarubozu(
            self,
            high: IntoExpr = pl.col("high"),
            low: IntoExpr = pl.col("low"),
            close: IntoExpr = pl.col("close"),
    ) -> pl.Expr:
        """Marubozu (Pattern Recognition)
            pl.col("open").ta.cdlmarubozu(pl.col("high"), pl.col("low"), pl.col("close"))

        Inputs:
            prices: ['open', 'high', 'low', 'close']
        Outputs:
            integer (values are -100, 0 or 100)
        """
        return register_plugin_function(
            plugin_path=plugin_path,
            function_name="cdlmarubozu",
            args=[self._expr, high, low, close],
            is_elementwise=False,
        )

    def cdlmatchinglow(
            self,
            high: IntoExpr = pl.col("high"),
            low: IntoExpr = pl.col("low"),
            close: IntoExpr = pl.col("close"),
    ) -> pl.Expr:
        """Matching Low (Pattern Recognition)
            pl.col("open").ta.cdlmatchinglow(pl.col("high"), pl.col("low"), pl.col("close"))

        Inputs:
            prices: ['open', 'high', 'low', 'close']
        Outputs:
            integer (values are -100, 0 or 100)
        """
        return register_plugin_function(
            plugin_path=plugin_path,
            function_name="cdlmatchinglow",
            args=[self._expr, high, low, close],
            is_elementwise=False,
        )

    def cdlmathold(
            self,
            high: IntoExpr = pl.col("high"),
            low: IntoExpr = pl.col("low"),
            close: IntoExpr = pl.col("close"),
            penetration: float = 0.5,
    ) -> pl.Expr:
        """Mat Hold (Pattern Recognition)
            pl.col("open").ta.cdlmathold(pl.col("high"), pl.col("low"), pl.col("close"), penetration=0.5)

        Inputs:
            prices: ['open', 'high', 'low', 'close']
        Parameters:
            penetration: 0.5
        Outputs:
            integer (values are -100, 0 or 100)
        """
        return register_plugin_function(
            plugin_path=plugin_path,
            function_name="cdlmathold",
            args=[self._expr, high, low, close],
            kwargs={"penetration": penetration},
            is_elementwise=False,
        )

    def cdlmorningdojistar(
            self,
            high: IntoExpr = pl.col("high"),
            low: IntoExpr = pl.col("low"),
            close: IntoExpr = pl.col("close"),
            penetration: float = 0.3,
    ) -> pl.Expr:
        """Morning Doji Star (Pattern Recognition)
            pl.col("open").ta.cdlmorningdojistar(pl.col("high"), pl.col("low"), pl.col("close"), penetration=0.3)

        Inputs:
            prices: ['open', 'high', 'low', 'close']
        Parameters:
            penetration: 0.3
        Outputs:
            integer (values are -100, 0 or 100)
        """
        return register_plugin_function(
            plugin_path=plugin_path,
            function_name="cdlmorningdojistar",
            args=[self._expr, high, low, close],
            kwargs={"penetration": penetration},
            is_elementwise=False,
        )

    def cdlmorningstar(
            self,
            high: IntoExpr = pl.col("high"),
            low: IntoExpr = pl.col("low"),
            close: IntoExpr = pl.col("close"),
            penetration: float = 0.3,
    ) -> pl.Expr:
        """Morning Star (Pattern Recognition)
            pl.col("open").ta.cdlmorningstar(pl.col("high"), pl.col("low"), pl.col("close"), penetration=0.3)

        Inputs:
            prices: ['open', 'high', 'low', 'close']
        Parameters:
            penetration: 0.3
        Outputs:
            integer (values are -100, 0 or 100)
        """
        return register_plugin_function(
            plugin_path=plugin_path,
            function_name="cdlmorningstar",
            args=[self._expr, high, low, close],
            kwargs={"penetration": penetration},
            is_elementwise=False,
        )

    def cdlonneck(
            self,
            high: IntoExpr = pl.col("high"),
            low: IntoExpr = pl.col("low"),
            close: IntoExpr = pl.col("close"),
    ) -> pl.Expr:
        """On-Neck Pattern (Pattern Recognition)
            pl.col("open").ta.cdlonneck(pl.col("high"), pl.col("low"), pl.col("close"))

        Inputs:
            prices: ['open', 'high', 'low', 'close']
        Outputs:
            integer (values are -100, 0 or 100)
        """
        return register_plugin_function(
            plugin_path=plugin_path,
            function_name="cdlonneck",
            args=[self._expr, high, low, close],
            is_elementwise=False,
        )

    def cdlpiercing(
            self,
            high: IntoExpr = pl.col("high"),
            low: IntoExpr = pl.col("low"),
            close: IntoExpr = pl.col("close"),
    ) -> pl.Expr:
        """Piercing Pattern (Pattern Recognition)
            pl.col("open").ta.cdlpiercing(pl.col("high"), pl.col("low"), pl.col("close"))

        Inputs:
            prices: ['open', 'high', 'low', 'close']
        Outputs:
            integer (values are -100, 0 or 100)
        """
        return register_plugin_function(
            plugin_path=plugin_path,
            function_name="cdlpiercing",
            args=[self._expr, high, low, close],
            is_elementwise=False,
        )

    def cdlrickshawman(
            self,
            high: IntoExpr = pl.col("high"),
            low: IntoExpr = pl.col("low"),
            close: IntoExpr = pl.col("close"),
    ) -> pl.Expr:
        """Rickshaw Man (Pattern Recognition)
            pl.col("open").ta.cdlrickshawman(pl.col("high"), pl.col("low"), pl.col("close"))

        Inputs:
            prices: ['open', 'high', 'low', 'close']
        Outputs:
            integer (values are -100, 0 or 100)
        """
        return register_plugin_function(
            plugin_path=plugin_path,
            function_name="cdlrickshawman",
            args=[self._expr, high, low, close],
            is_elementwise=False,
        )

    def cdlrisefall3methods(
            self,
            high: IntoExpr = pl.col("high"),
            low: IntoExpr = pl.col("low"),
            close: IntoExpr = pl.col("close"),
    ) -> pl.Expr:
        """Rising/Falling Three Methods (Pattern Recognition)
            pl.col("open").ta.cdlrisefall3methods(pl.col("high"), pl.col("low"), pl.col("close"))

        Inputs:
            prices: ['open', 'high', 'low', 'close']
        Outputs:
            integer (values are -100, 0 or 100)
        """
        return register_plugin_function(
            plugin_path=plugin_path,
            function_name="cdlrisefall3methods",
            args=[self._expr, high, low, close],
            is_elementwise=False,
        )

    def cdlseparatinglines(
            self,
            high: IntoExpr = pl.col("high"),
            low: IntoExpr = pl.col("low"),
            close: IntoExpr = pl.col("close"),
    ) -> pl.Expr:
        """Separating Lines (Pattern Recognition)
            pl.col("open").ta.cdlseparatinglines(pl.col("high"), pl.col("low"), pl.col("close"))

        Inputs:
            prices: ['open', 'high', 'low', 'close']
        Outputs:
            integer (values are -100, 0 or 100)
        """
        return register_plugin_function(
            plugin_path=plugin_path,
            function_name="cdlseparatinglines",
            args=[self._expr, high, low, close],
            is_elementwise=False,
        )

    def cdlshootingstar(
            self,
            high: IntoExpr = pl.col("high"),
            low: IntoExpr = pl.col("low"),
            close: IntoExpr = pl.col("close"),
    ) -> pl.Expr:
        """Shooting Star (Pattern Recognition)
            pl.col("open").ta.cdlshootingstar(pl.col("high"), pl.col("low"), pl.col("close"))

        Inputs:
            prices: ['open', 'high', 'low', 'close']
        Outputs:
            integer (values are -100, 0 or 100)
        """
        return register_plugin_function(
            plugin_path=plugin_path,
            function_name="cdlshootingstar",
            args=[self._expr, high, low, close],
            is_elementwise=False,
        )

    def cdlshortline(
            self,
            high: IntoExpr = pl.col("high"),
            low: IntoExpr = pl.col("low"),
            close: IntoExpr = pl.col("close"),
    ) -> pl.Expr:
        """Short Line Candle (Pattern Recognition)
            pl.col("open").ta.cdlshortline(pl.col("high"), pl.col("low"), pl.col("close"))

        Inputs:
            prices: ['open', 'high', 'low', 'close']
        Outputs:
            integer (values are -100, 0 or 100)
        """
        return register_plugin_function(
            plugin_path=plugin_path,
            function_name="cdlshortline",
            args=[self._expr, high, low, close],
            is_elementwise=False,
        )

    def cdlspinningtop(
            self,
            high: IntoExpr = pl.col("high"),
            low: IntoExpr = pl.col("low"),
            close: IntoExpr = pl.col("close"),
    ) -> pl.Expr:
        """Spinning Top (Pattern Recognition)
            pl.col("open").ta.cdlspinningtop(pl.col("high"), pl.col("low"), pl.col("close"))

        Inputs:
            prices: ['open', 'high', 'low', 'close']
        Outputs:
            integer (values are -100, 0 or 100)
        """
        return register_plugin_function(
            plugin_path=plugin_path,
            function_name="cdlspinningtop",
            args=[self._expr, high, low, close],
            is_elementwise=False,
        )

    def cdlstalledpattern(
            self,
            high: IntoExpr = pl.col("high"),
            low: IntoExpr = pl.col("low"),
            close: IntoExpr = pl.col("close"),
    ) -> pl.Expr:
        """Stalled Pattern (Pattern Recognition)
            pl.col("open").ta.cdlstalledpattern(pl.col("high"), pl.col("low"), pl.col("close"))

        Inputs:
            prices: ['open', 'high', 'low', 'close']
        Outputs:
            integer (values are -100, 0 or 100)
        """
        return register_plugin_function(
            plugin_path=plugin_path,
            function_name="cdlstalledpattern",
            args=[self._expr, high, low, close],
            is_elementwise=False,
        )

    def cdlsticksandwich(
            self,
            high: IntoExpr = pl.col("high"),
            low: IntoExpr = pl.col("low"),
            close: IntoExpr = pl.col("close"),
    ) -> pl.Expr:
        """Stick Sandwich (Pattern Recognition)
            pl.col("open").ta.cdlsticksandwich(pl.col("high"), pl.col("low"), pl.col("close"))

        Inputs:
            prices: ['open', 'high', 'low', 'close']
        Outputs:
            integer (values are -100, 0 or 100)
        """
        return register_plugin_function(
            plugin_path=plugin_path,
            function_name="cdlsticksandwich",
            args=[self._expr, high, low, close],
            is_elementwise=False,
        )

    def cdltakuri(
            self,
            high: IntoExpr = pl.col("high"),
            low: IntoExpr = pl.col("low"),
            close: IntoExpr = pl.col("close"),
    ) -> pl.Expr:
        """Takuri (Dragonfly Doji with very long lower shadow) (Pattern Recognition)
            pl.col("open").ta.cdltakuri(pl.col("high"), pl.col("low"), pl.col("close"))

        Inputs:
            prices: ['open', 'high', 'low', 'close']
        Outputs:
            integer (values are -100, 0 or 100)
        """
        return register_plugin_function(
            plugin_path=plugin_path,
            function_name="cdltakuri",
            args=[self._expr, high, low, close],
            is_elementwise=False,
        )

    def cdltasukigap(
            self,
            high: IntoExpr = pl.col("high"),
            low: IntoExpr = pl.col("low"),
            close: IntoExpr = pl.col("close"),
    ) -> pl.Expr:
        """Tasuki Gap (Pattern Recognition)
            pl.col("open").ta.cdltasukigap(pl.col("high"), pl.col("low"), pl.col("close"))

        Inputs:
            prices: ['open', 'high', 'low', 'close']
        Outputs:
            integer (values are -100, 0 or 100)
        """
        return register_plugin_function(
            plugin_path=plugin_path,
            function_name="cdltasukigap",
            args=[self._expr, high, low, close],
            is_elementwise=False,
        )

    def cdlthrusting(
            self,
            high: IntoExpr = pl.col("high"),
            low: IntoExpr = pl.col("low"),
            close: IntoExpr = pl.col("close"),
    ) -> pl.Expr:
        """Thrusting Pattern (Pattern Recognition)
            pl.col("open").ta.cdlthrusting(pl.col("high"), pl.col("low"), pl.col("close"))

        Inputs:
            prices: ['open', 'high', 'low', 'close']
        Outputs:
            integer (values are -100, 0 or 100)
        """
        return register_plugin_function(
            plugin_path=plugin_path,
            function_name="cdlthrusting",
            args=[self._expr, high, low, close],
            is_elementwise=False,
        )

    def cdltristar(
            self,
            high: IntoExpr = pl.col("high"),
            low: IntoExpr = pl.col("low"),
            close: IntoExpr = pl.col("close"),
    ) -> pl.Expr:
        """Tristar Pattern (Pattern Recognition)
            pl.col("open").ta.cdltristar(pl.col("high"), pl.col("low"), pl.col("close"))

        Inputs:
            prices: ['open', 'high', 'low', 'close']
        Outputs:
            integer (values are -100, 0 or 100)
        """
        return register_plugin_function(
            plugin_path=plugin_path,
            function_name="cdltristar",
            args=[self._expr, high, low, close],
            is_elementwise=False,
        )

    def cdlunique3river(
            self,
            high: IntoExpr = pl.col("high"),
            low: IntoExpr = pl.col("low"),
            close: IntoExpr = pl.col("close"),
    ) -> pl.Expr:
        """Unique 3 River (Pattern Recognition)
            pl.col("open").ta.cdlunique3river(pl.col("high"), pl.col("low"), pl.col("close"))

        Inputs:
            prices: ['open', 'high', 'low', 'close']
        Outputs:
            integer (values are -100, 0 or 100)
        """
        return register_plugin_function(
            plugin_path=plugin_path,
            function_name="cdlunique3river",
            args=[self._expr, high, low, close],
            is_elementwise=False,
        )

    def cdlupsidegap2crows(
            self,
            high: IntoExpr = pl.col("high"),
            low: IntoExpr = pl.col("low"),
            close: IntoExpr = pl.col("close"),
    ) -> pl.Expr:
        """Upside Gap Two Crows (Pattern Recognition)
            pl.col("open").ta.cdlupsidegap2crows(pl.col("high"), pl.col("low"), pl.col("close"))

        Inputs:
            prices: ['open', 'high', 'low', 'close']
        Outputs:
            integer (values are -100, 0 or 100)
        """
        return register_plugin_function(
            plugin_path=plugin_path,
            function_name="cdlupsidegap2crows",
            args=[self._expr, high, low, close],
            is_elementwise=False,
        )

    def cdlxsidegap3methods(
            self,
            high: IntoExpr = pl.col("high"),
            low: IntoExpr = pl.col("low"),
            close: IntoExpr = pl.col("close"),
    ) -> pl.Expr:
        """Upside/Downside Gap Three Methods (Pattern Recognition)
            pl.col("open").ta.cdlxsidegap3methods(pl.col("high"), pl.col("low"), pl.col("close"))

        Inputs:
            prices: ['open', 'high', 'low', 'close']
        Outputs:
            integer (values are -100, 0 or 100)
        """
        return register_plugin_function(
            plugin_path=plugin_path,
            function_name="cdlxsidegap3methods",
            args=[self._expr, high, low, close],
            is_elementwise=False,
        )

    def avgprice(
            self,
            high: IntoExpr = pl.col("high"),
            low: IntoExpr = pl.col("low"),
            close: IntoExpr = pl.col("close"),
    ) -> pl.Expr:
        """Average Price (Price Transform)

        pl.col("open").ta.avgprice("high", "low", "close")

        Inputs:
            prices: ['open', 'high', 'low', 'close']
        Outputs:
            real
        """
        return register_plugin_function(
            plugin_path=plugin_path,
            function_name="avgprice",
            args=[self._expr, high, low, close],
            is_elementwise=False,
        )

    def medprice(self, low: IntoExpr = pl.col("low")) -> pl.Expr:
        """Median Price (Price Transform)
        pl.col("high").ta.medprice("low")

        Inputs:
            prices: ['high', 'low']
        Outputs:
            real
        """
        return register_plugin_function(
            plugin_path=plugin_path,
            function_name="medprice",
            args=[self._expr, low],
            is_elementwise=False,
        )

    def typprice(self, high: IntoExpr = pl.col("high"), low: IntoExpr = pl.col("low")) -> pl.Expr:
        """Typical Price (Price Transform)
        pl.col("close").ta.typprice("high", "low")

        Inputs:
            prices: ['high', 'low', 'close']
        Outputs:
            real
        """
        return register_plugin_function(
            plugin_path=plugin_path,
            function_name="typprice",
            args=[self._expr, high, low],
            is_elementwise=False,
        )

    def wclprice(self, high: IntoExpr = pl.col("high"), low: IntoExpr = pl.col("low")) -> pl.Expr:
        """Weighted Close Price (Price Transform)
        pl.col("close").ta.wclprice("high", "low")

        Inputs:
            prices: ['high', 'low', 'close']
        Outputs:
            real
        """
        return register_plugin_function(
            plugin_path=plugin_path,
            function_name="wclprice",
            args=[self._expr, high, low],
            is_elementwise=False,
        )

    def beta(self, real: IntoExpr, timeperiod: int = 5) -> pl.Expr:
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
        return register_plugin_function(
            plugin_path=plugin_path,
            function_name="beta",
            args=[self._expr, real],
            kwargs={"timeperiod": timeperiod},
            is_elementwise=False,
        )

    def correl(self, real: IntoExpr, timeperiod: int = 30) -> pl.Expr:
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
        return register_plugin_function(
            plugin_path=plugin_path,
            function_name="correl",
            args=[self._expr, real],
            kwargs={"timeperiod": timeperiod},
            is_elementwise=False,
        )

    def linearreg(self, timeperiod: int = 14) -> pl.Expr:
        """Linear Regression (Statistic Functions)
        pl.col("close").ta.linearreg(timeperiod=14)
        Inputs:
            real
        Parameters:
            timeperiod: 14
        Outputs:
            real
        """
        return register_plugin_function(
            plugin_path=plugin_path,
            function_name="linearreg",
            args=self._expr,
            kwargs={"timeperiod": timeperiod},
            is_elementwise=False,
        )

    def linearreg_angle(self, timeperiod: int = 14) -> pl.Expr:
        """Linear Regression Angle (Statistic Functions)
        pl.col("close").ta.linearreg_angle(timeperiod=14)
        Inputs:
            real
        Parameters:
            timeperiod: 14
        Outputs:
            real
        """
        return register_plugin_function(
            plugin_path=plugin_path,
            function_name="linearreg_angle",
            args=self._expr,
            kwargs={"timeperiod": timeperiod},
            is_elementwise=False,
        )

    def linearreg_intercept(self, timeperiod: int = 14) -> pl.Expr:
        """Linear Regression Intercept (Statistic Functions)
        pl.col("close").ta.linearreg_intercept(timeperiod=14)
        Inputs:
            real
        Parameters:
            timeperiod: 14
        Outputs:
            real
        """
        return register_plugin_function(
            plugin_path=plugin_path,
            function_name="linearreg_intercept",
            args=self._expr,
            kwargs={"timeperiod": timeperiod},
            is_elementwise=False,
        )

    def linearreg_slope(self, timeperiod: int = 14) -> pl.Expr:
        """Linear Regression Slope (Statistic Functions)
        pl.col("close").ta.linearreg_slope(timeperiod=14)
        Inputs:
            real
        Parameters:
            timeperiod: 14
        Outputs:
            real
        """
        return register_plugin_function(
            plugin_path=plugin_path,
            function_name="linearreg_slope",
            args=self._expr,
            kwargs={"timeperiod": timeperiod},
            is_elementwise=False,
        )

    def stddev(self, timeperiod: int = 5, nbdev: float = 1.0) -> pl.Expr:
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
        return register_plugin_function(
            plugin_path=plugin_path,
            function_name="stddev",
            args=self._expr,
            kwargs={"timeperiod": timeperiod, "nbdev": nbdev},
            is_elementwise=False,
        )

    def tsf(self, timeperiod: int = 14) -> pl.Expr:
        """Time Series Forecast (Statistic Functions)
        pl.col("close").ta.tsf(timeperiod=14)
        Inputs:
            real
        Parameters:
            timeperiod: 14
        Outputs:
            real
        """
        return register_plugin_function(
            plugin_path=plugin_path,
            function_name="tsf",
            args=self._expr,
            kwargs={"timeperiod": timeperiod},
            is_elementwise=False,
        )

    def var(self, timeperiod: int = 5, nbdev: float = 1.0) -> pl.Expr:
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
        return register_plugin_function(
            plugin_path=plugin_path,
            function_name="var",
            args=self._expr,
            kwargs={"timeperiod": timeperiod, "nbdev": nbdev},
            is_elementwise=False,
        )

    def atr(
            self, high: IntoExpr = pl.col("high"), low: IntoExpr = pl.col("low"), timeperiod: int = 14
    ) -> pl.Expr:
        """Average True Range (Volatility Indicators)
        pl.col("close").ta.atr("high", "low", [, timeperiod=?])

        Inputs:
            prices: ['high', 'low', 'close']
        Parameters:
            timeperiod: 14
        Outputs:
            real
        """
        return register_plugin_function(
            plugin_path=plugin_path,
            function_name="atr",
            args=[self._expr, high, low],
            kwargs={"timeperiod": timeperiod},
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
        return register_plugin_function(
            plugin_path=plugin_path,
            function_name="natr",
            args=[self._expr, high, low],
            kwargs={"timeperiod": timeperiod},
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
        return register_plugin_function(
            plugin_path=plugin_path,
            function_name="trange",
            args=[self._expr, high, low],
            is_elementwise=False,
        )

    def ad(
            self,
            high: IntoExpr = pl.col("high"),
            low: IntoExpr = pl.col("low"),
            volume: IntoExpr = pl.col("volume"),
    ) -> pl.Expr:
        """Chaikin A/D Line (Volume Indicators)
        pl.col("close").ta.ad(pl.col("high"), pl.col("low"), pl.col("volume"))

        """
        return register_plugin_function(
            plugin_path=plugin_path,
            function_name="ad",
            args=[self._expr, high, low, volume],
            is_elementwise=False,
        )

    def adosc(
            self,
            high: IntoExpr = pl.col("high"),
            low: IntoExpr = pl.col("low"),
            volume: IntoExpr = pl.col("volume"),
            fastperiod: int = 3,
            slowperiod: int = 10,
    ) -> pl.Expr:
        """Chaikin A/D Oscillator (Volume Indicators)
        pl.col("close").ta.adosc(pl.col("high"), pl.col("low"), pl.col("volume"), fastperiod=3, slowperiod=10)

        Parameters:
            fastperiod: 3
            slowperiod: 10
        Outputs:
            real
        """
        return register_plugin_function(
            plugin_path=plugin_path,
            function_name="adosc",
            args=[self._expr, high, low, volume],
            kwargs={"fastperiod": fastperiod, "slowperiod": slowperiod},
            is_elementwise=False,
        )

    def obv(self, volume: IntoExpr = pl.col("volume")) -> pl.Expr:
        """On Balance Volume (Volume Indicators)
        pl.col("close").ta.obv(pl.col("volume"))

        Inputs:
            prices: ['close', 'volume']
        Outputs:
            real
        """
        return register_plugin_function(
            plugin_path=plugin_path,
            function_name="obv",
            args=[self._expr, volume],
            is_elementwise=False,
        )

def ht_dcperiod(real: IntoExpr = pl.col("close")) -> pl.Expr:
    """Hilbert Transform - Dominant Cycle Period (Cycle Indicators)
    pl.col("close").ta.ht_dcperiod()

    Inputs:
        real
    Outputs:
        real
    """
    return real.ta.ht_dcperiod()


def ht_dcphase(real: IntoExpr = pl.col("close")) -> pl.Expr:
    """Hilbert Transform - Dominant Cycle Phase (Cycle Indicators)
    pl.col("close").ta.ht_dcphase()

    Inputs:
        real
    Outputs:
        real
    """
    return real.ta.ht_dcphase()


def ht_phasor(real: IntoExpr = pl.col("close")) -> pl.Expr:
    """Hilbert Transform - Phasor Components (Cycle Indicators)
    pl.col("close").ta.ht_phasor()

    Inputs:
        real
    Outputs:
        inphase, quadrature
    """
    return real.ta.ht_phasor()


def ht_sine(real: IntoExpr = pl.col("close")) -> pl.Expr:
    """Hilbert Transform - SineWave (Cycle Indicators)
    pl.col("close").ta.ht_sine()

    Inputs:
        real
    Outputs:
        sine, leadsine
    """
    return real.ta.ht_sine()


def ht_trendmode(real: IntoExpr = pl.col("close")) -> pl.Expr:
    """Hilbert Transform - Trend vs Cycle Mode (Cycle Indicators)
    pl.col("close").ta.ht_trendmode()

    Inputs:
        real
    Outputs:
        integer
    """
    return real.ta.ht_trendmode()


def add(
    real0: IntoExpr = pl.col("high"),
    real1: IntoExpr = pl.col("low"),
) -> pl.Expr:
    """Vector Arithmetic Add (Math Operators)
    pl.col("high").ta.add(pl.col("low"))

    Inputs:
        real0
        real1
    Outputs:
        real
    """
    return real0.ta.add(real1)


def div(
    real0: IntoExpr = pl.col("high"),
    real1: IntoExpr = pl.col("low"),
) -> pl.Expr:
    """Vector Arithmetic Div (Math Operators)
    pl.col("high").ta.div(pl.col("low"))

    Inputs:
        real0
        real1
    Outputs:
        real
    """
    return real0.ta.div(real1)


def max(
    real: IntoExpr = pl.col("close"),
    timeperiod: int = 30,
) -> pl.Expr:
    """Highest value over a specified period (Math Operators)
    pl.col("close").ta.max(timeperiod=30)

    Inputs:
        prices: ['close']
    Parameters:
        timeperiod: 30
    Outputs:
        real
    """
    return real.ta.max(timeperiod=timeperiod)


def maxindex(
    real: IntoExpr = pl.col("close"),
    timeperiod: int = 30,
) -> pl.Expr:
    """Index of highest value over a specified period (Math Operators)
    pl.col("close").ta.maxindex(timeperiod=30)

    Inputs:
        prices: ['close']
    Parameters:
        timeperiod: 30
    Outputs:
        integer
    """
    return real.ta.maxindex(timeperiod=timeperiod)


def min(
    real: IntoExpr = pl.col("close"),
    timeperiod: int = 30,
) -> pl.Expr:
    """Lowest value over a specified period (Math Operators)
    pl.col("close").ta.min(timeperiod=30)

    Inputs:
        prices: ['close']
    Parameters:
        timeperiod: 30
    Outputs:
        real
    """
    return real.ta.min(timeperiod=timeperiod)


def minindex(
    real: IntoExpr = pl.col("close"),
    timeperiod: int = 30,
) -> pl.Expr:
    """Index of lowest value over a specified period (Math Operators)
    pl.col("close").ta.minindex(timeperiod=30)

    Inputs:
        prices: ['close']
    Parameters:
        timeperiod: 30
    Outputs:
        integer
    """
    return real.ta.minindex(timeperiod=timeperiod)


def minmax(
    real: IntoExpr = pl.col("close"),
    timeperiod: int = 30,
) -> pl.Expr:
    """Lowest and highest values over a specified period (Math Operators)
    pl.col("close").ta.minmax(timeperiod=30)

    Inputs:
        prices: ['close']
    Parameters:
        timeperiod: 30
    Outputs:
        min, max
    """
    return real.ta.minmax(timeperiod=timeperiod)


def minmaxindex(
    real: IntoExpr = pl.col("close"),
    timeperiod: int = 30,
) -> pl.Expr:
    """Indexes of lowest and highest values over a specified period (Math Operators)
    pl.col("close").ta.minmaxindex(timeperiod=30)

    Inputs:
        prices: ['close']
    Parameters:
        timeperiod: 30
    Outputs:
        minidx, maxidx
    """
    return real.ta.minmaxindex(timeperiod=timeperiod)


def mult(
    real0: IntoExpr = pl.col("high"),
    real1: IntoExpr = pl.col("low"),
) -> pl.Expr:
    """Vector Arithmetic Mult (Math Operators)
    pl.col("high").ta.mult(pl.col("low"))

    Inputs:
        real0
        real1
    Outputs:
        real
    """
    return real0.ta.mult(real1)


def sub(
    real0: IntoExpr = pl.col("high"),
    real1: IntoExpr = pl.col("low"),
) -> pl.Expr:
    """Vector Arithmetic Substraction (Math Operators)
    pl.col("high").ta.sub(pl.col("low"))

    Inputs:
        real0
        real1
    Outputs:
        real
    """
    return real0.ta.sub(real1)


def sum(
    real: IntoExpr = pl.col("close"),
    timeperiod: int = 30,
) -> pl.Expr:
    """Summation (Math Operators)
    pl.col("close").ta.sum(timeperiod=30)

    Inputs:
        prices: ['close']
    Parameters:
        timeperiod: 30
    Outputs:
        real
    """
    return real.ta.sum(timeperiod=timeperiod)


def acos(
    real: IntoExpr = pl.col("close"),
) -> pl.Expr:
    """Vector Trigonometric ACos (Math Operators)
    pl.col("close").ta.acos()

    Inputs:
        real
    Outputs:
        real
    """
    return real.ta.acos()


def asin(
    real: IntoExpr = pl.col("close"),
) -> pl.Expr:
    """Vector Trigonometric ASin (Math Operators)
    pl.col("close").ta.asin()

    Inputs:
        real
    Outputs:
        real
    """
    return real.ta.asin()


def atan(
    real: IntoExpr = pl.col("close"),
) -> pl.Expr:
    """Vector Trigonometric ATan (Math Operators)
    pl.col("close").ta.atan()

    Inputs:
        real
    Outputs:
        real
    """
    return real.ta.atan()


def ceil(
    real: IntoExpr = pl.col("close"),
) -> pl.Expr:
    """Vector Ceil (Math Operators)
    pl.col("close").ta.ceil()

    Inputs:
        real
    Outputs:
        real
    """
    return real.ta.ceil()


def cos(
    real: IntoExpr = pl.col("close"),
) -> pl.Expr:
    """Vector Trigonometric Cos (Math Operators)
    pl.col("close").ta.cos()

    Inputs:
        real
    Outputs:
        real
    """
    return real.ta.cos()


def cosh(
    real: IntoExpr = pl.col("close"),
) -> pl.Expr:
    """Vector Trigonometric Cosh (Math Operators)
    pl.col("close").ta.cosh()

    Inputs:
        real
    Outputs:
        real
    """
    return real.ta.cosh()


def exp(
    real: IntoExpr = pl.col("close"),
) -> pl.Expr:
    """Vector Arithmetic Exp (Math Operators)
    pl.col("close").ta.exp()

    Inputs:
        real
    Outputs:
        real
    """
    return real.ta.exp()


def floor(
    real: IntoExpr = pl.col("close"),
) -> pl.Expr:
    """Vector Floor (Math Operators)
    pl.col("close").ta.floor()

    Inputs:
        real
    Outputs:
        real
    """
    return real.ta.floor()


def ln(
    real: IntoExpr = pl.col("close"),
) -> pl.Expr:
    """Vector Log Natural (Math Operators)
    pl.col("close").ta.ln()

    Inputs:
        real
    Outputs:
        real
    """
    return real.ta.ln()


def log10(
    real: IntoExpr = pl.col("close"),
) -> pl.Expr:
    """Vector Log10 (Math Operators)
    pl.col("close").ta.log10()

    Inputs:
        real
    Outputs:
        real
    """
    return real.ta.log10()


def sin(
    real: IntoExpr = pl.col("close"),
) -> pl.Expr:
    """Vector Trigonometric Sin (Math Operators)
    pl.col("close").ta.sin()

    Inputs:
        real
    Outputs:
        real
    """
    return real.ta.sin()


def sinh(
    real: IntoExpr = pl.col("close"),
) -> pl.Expr:
    """Vector Trigonometric Sinh (Math Operators)
    pl.col("close").ta.sinh()

    Inputs:
        real
    Outputs:
        real
    """
    return real.ta.sinh()


def sqrt(
    real: IntoExpr = pl.col("close"),
) -> pl.Expr:
    """Vector Square Root (Math Operators)
    pl.col("close").ta.sqrt()

    Inputs:
        real
    Outputs:
        real
    """
    return real.ta.sqrt()


def tan(
    real: IntoExpr = pl.col("close"),
) -> pl.Expr:
    """Vector Trigonometric Tan (Math Operators)
    pl.col("close").ta.tan()

    Inputs:
        real
    Outputs:
        real
    """
    return real.ta.tan()


def tanh(
    real: IntoExpr = pl.col("close"),
) -> pl.Expr:
    """Vector Trigonometric Tanh (Math Operators)
    pl.col("close").ta.tanh()

    Inputs:
        real
    Outputs:
        real
    """
    return real.ta.tanh()


def adx(
    high: IntoExpr = pl.col("high"),
    low: IntoExpr = pl.col("low"),
    close: IntoExpr = pl.col("close"),
    timeperiod: int = 14,
) -> pl.Expr:
    """Average Directional Movement Index (Momentum Indicators)
    pl.col("close").ta.adx(pl.col("high"), pl.col("low"), timeperiod=14)

    Inputs:
        prices: ['high', 'low', 'close']
    Parameters:
        timeperiod: 14
    Outputs:
        real
    """
    return close.ta.adx(high, low, timeperiod=timeperiod)


def adxr(
    high: IntoExpr = pl.col("high"),
    low: IntoExpr = pl.col("low"),
    close: IntoExpr = pl.col("close"),
    timeperiod: int = 14,
) -> pl.Expr:
    """Average Directional Movement Index Rating (Momentum Indicators)
    pl.col("close").ta.adxr(pl.col("high"), pl.col("low"), timeperiod=14)

    Inputs:
        prices: ['high', 'low', 'close']
    Parameters:
        timeperiod: 14
    Outputs:
        real
    """
    return close.ta.adxr(high, low, timeperiod=timeperiod)


def apo(
    real: IntoExpr = pl.col("close"),
    fastperiod: int = 12,
    slowperiod: int = 26,
    matype: int = 0,
) -> pl.Expr:
    """Absolute Price Oscillator (Momentum Indicators)
    pl.col("close").ta.apo(timeperiod=12, matype=0)

    Inputs:
        real
    Parameters:
        fastperiod: 12
        slowperiod: 26
        matype: 0
    Outputs:
        real
    """
    return real.ta.apo(fastperiod=fastperiod, slowperiod=slowperiod, matype=matype)


def aroon(
    high: IntoExpr = pl.col("high"),
    low: IntoExpr = pl.col("low"),
    timeperiod: int = 14,
) -> pl.Expr:
    """Aroon (Momentum Indicators)
    pl.col("close").ta.aroon(pl.col("high"), pl.col("low"), timeperiod=14)

    Inputs:
        prices: ['high', 'low']
    Parameters:
        timeperiod: 14
    Outputs:
        aroondown, aroonup
    """
    return high.ta.aroon(low, timeperiod=timeperiod)


def aroonosc(
    high: IntoExpr = pl.col("high"),
    low: IntoExpr = pl.col("low"),
    timeperiod: int = 14,
) -> pl.Expr:
    """Aroon Oscillator (Momentum Indicators)
    pl.col("close").ta.aroonosc(pl.col("high"), pl.col("low"), timeperiod=14)

    Inputs:
        prices: ['high', 'low']
    Parameters:
        timeperiod: 14
    Outputs:
        real
    """
    return high.ta.aroonosc(low, timeperiod=timeperiod)


def bop(
    open: IntoExpr = pl.col("open"),
    high: IntoExpr = pl.col("high"),
    low: IntoExpr = pl.col("low"),
    close: IntoExpr = pl.col("close"),
) -> pl.Expr:
    """Balance Of Power (Momentum Indicators)
    pl.col("open").ta.bop(pl.col("high"), pl.col("low"), pl.col("close"))

    Inputs:
        prices: ['open', 'high', 'low', 'close']
    Outputs:
        real
    """
    return open.ta.bop(high, low, close)


def cci(
    high: IntoExpr = pl.col("high"),
    low: IntoExpr = pl.col("low"),
    close: IntoExpr = pl.col("close"),
    timeperiod: int = 14,
) -> pl.Expr:
    """Commodity Channel Index (Momentum Indicators)
    pl.col("close").ta.cci(pl.col("high"), pl.col("low"), timeperiod=14)

    Inputs:
        prices: ['high', 'low', 'close']
    Parameters:
        timeperiod: 14
    Outputs:
        real
    """
    return close.ta.cci(high, low, timeperiod=timeperiod)


def cmo(
    real: IntoExpr = pl.col("close"),
    timeperiod: int = 14,
) -> pl.Expr:
    """Chande Momentum Oscillator (Momentum Indicators)
    pl.col("close").ta.cmo(timeperiod=14)

    Inputs:
        real
    Parameters:
        timeperiod: 14
    Outputs:
        real
    """
    return real.ta.cmo(timeperiod=timeperiod)


def dx(
    high: IntoExpr = pl.col("high"),
    low: IntoExpr = pl.col("low"),
    close: IntoExpr = pl.col("close"),
    timeperiod: int = 14,
) -> pl.Expr:
    """Directional Movement Index (Momentum Indicators)
    pl.col("close").ta.dx(pl.col("high"), pl.col("low"), timeperiod=14)

    Inputs:
        prices: ['high', 'low', 'close']
    Parameters:
        timeperiod: 14
    Outputs:
        real
    """
    return close.ta.dx(high, low, timeperiod=timeperiod)


def macd(
    real: IntoExpr = pl.col("close"),
    fastperiod: int = 12,
    slowperiod: int = 26,
    signalperiod: int = 9,
) -> pl.Expr:
    """Moving Average Convergence/Divergence (Momentum Indicators)
    pl.col("close").ta.macd(timeperiod=12, signalperiod=9)

    Inputs:
        real
    Parameters:
        fastperiod: 12
        slowperiod: 26
        signalperiod: 9
    Outputs:
        macd, macdsignal, macdhist
    """
    return real.ta.macd(fastperiod=fastperiod, slowperiod=slowperiod, signalperiod=signalperiod)


def macdext(
    real: IntoExpr = pl.col("close"),
    fastperiod: int = 12,
    fastmatype: int = 0,
    slowperiod: int = 26,
    slowmatype: int = 0,
    signalperiod: int = 9,
    signalmatype: int = 0,
) -> pl.Expr:
    """MACD with controllable MA type (Momentum Indicators)
    pl.col("close").ta.macdext(timeperiod=12, signalperiod=9)

    Inputs:
        real
    Parameters:
        fastperiod: 12
        fastmatype: 0
        slowperiod: 26
        slowmatype: 0
        signalperiod: 9
        signalmatype: 0
    Outputs:
        macd, macdsignal, macdhist
    """
    return real.ta.macdext(
        fastperiod=fastperiod,
        fastmatype=fastmatype,
        slowperiod=slowperiod,
        slowmatype=slowmatype,
        signalperiod=signalperiod,
        signalmatype=signalmatype,
    )


def macdfix(real: IntoExpr = pl.col("close"), signalperiod: int = 9) -> pl.Expr:
    """Moving Average Convergence/Divergence Fix 12/26 (Momentum Indicators)
    pl.col("close").ta.macdfix(signalperiod=9)

    Inputs:
        real
    Parameters:
        signalperiod: 9
    Outputs:
        macd, macdsignal, macdhist
    """
    return real.ta.macdfix(signalperiod=signalperiod)


def mfi(
    high: IntoExpr = pl.col("high"),
    low: IntoExpr = pl.col("low"),
    close: IntoExpr = pl.col("close"),
    volume: IntoExpr = pl.col("volume"),
    timeperiod: int = 14,
) -> pl.Expr:
    """Money Flow Index (Momentum Indicators)
    pl.col("close").ta.mfi(pl.col("high"), pl.col("low"), pl.col("volume"), timeperiod=14)

    Inputs:
        prices: ['high', 'low', 'close']
        volume
    Parameters:
        timeperiod: 14
    Outputs:
        real
    """
    return close.ta.mfi(high, low, volume, timeperiod=timeperiod)


def minus_di(
    high: IntoExpr = pl.col("high"),
    low: IntoExpr = pl.col("low"),
    close: IntoExpr = pl.col("close"),
    timeperiod: int = 14,
) -> pl.Expr:
    """Minus Directional Indicator (Momentum Indicators)
    pl.col("close").ta.minus_di(pl.col("high"), pl.col("low"), timeperiod=14)

    Inputs:
        prices: ['high', 'low', 'close']
    Parameters:
        timeperiod: 14
    Outputs:
        real
    """
    return close.ta.minus_di(high, low, timeperiod=timeperiod)


def minus_dm(
    high: IntoExpr = pl.col("high"),
    low: IntoExpr = pl.col("low"),
    timeperiod: int = 14,
) -> pl.Expr:
    """Minus Directional Movement (Momentum Indicators)
    pl.col("high").ta.minus_dm("low", timeperiod=14)

    Inputs:
        prices: ['high', 'low']
    Parameters:
        timeperiod: 14
    Outputs:
        real
    """
    return high.ta.minus_dm(low, timeperiod=timeperiod)


def mom(
    real: IntoExpr = pl.col("close"),
    timeperiod: int = 10,
) -> pl.Expr:
    """Momentum (Momentum Indicators)
    pl.col("close").ta.mom(timeperiod=10)

    Inputs:
        real
    Parameters:
        timeperiod: 10
    Outputs:
        real
    """
    return real.ta.mom(timeperiod=timeperiod)


def plus_di(
    high: IntoExpr = pl.col("high"),
    low: IntoExpr = pl.col("low"),
    close: IntoExpr = pl.col("close"),
    timeperiod: int = 14,
) -> pl.Expr:
    """Plus Directional Indicator (Momentum Indicators)
    pl.col("close").ta.plus_di(pl.col("high"), pl.col("low"), timeperiod=14)

    Inputs:
        prices: ['high', 'low', 'close']
    Parameters:
        timeperiod: 14
    Outputs:
        real
    """
    return close.ta.plus_di(high, low, timeperiod=timeperiod)


def plus_dm(
    high: IntoExpr = pl.col("high"),
    low: IntoExpr = pl.col("low"),
    timeperiod: int = 14,
) -> pl.Expr:
    """Plus Directional Movement (Momentum Indicators)
    pl.col("high").ta.plus_dm("low", timeperiod=14)

    Inputs:
        prices: ['high', 'low']
    Parameters:
        timeperiod: 14
    Outputs:
        real
    """
    return high.ta.plus_dm(low, timeperiod=timeperiod)


def ppo(
    real: IntoExpr = pl.col("close"),
    fastperiod: int = 12,
    slowperiod: int = 26,
    matype: int = 0,
) -> pl.Expr:
    """Percentage Price Oscillator (Momentum Indicators)
    pl.col("close").ta.ppo(timeperiod=12, matype=0)

    Inputs:
        real
    Parameters:
        fastperiod: 12
        slowperiod: 26
        matype: 0
    Outputs:
        real
    """
    return real.ta.ppo(fastperiod=fastperiod, slowperiod=slowperiod, matype=matype)


def roc(
    real: IntoExpr = pl.col("close"),
    timeperiod: int = 10,
) -> pl.Expr:
    """Rate of change : ((price/prevPrice)-1)*100 (Momentum Indicators)
    pl.col("close").ta.roc(timeperiod=10)

    Inputs:
        real
    Parameters:
        timeperiod: 10
    Outputs:
        real
    """
    return real.ta.roc(timeperiod=timeperiod)


def rocp(
    real: IntoExpr = pl.col("close"),
    timeperiod: int = 10,
) -> pl.Expr:
    """Rate of change Percentage: (price-prevPrice)/prevPrice (Momentum Indicators)
    pl.col("close").ta.rocp(timeperiod=10)

    Inputs:
        real
    Parameters:
        timeperiod: 10
    Outputs:
        real
    """
    return real.ta.rocp(timeperiod=timeperiod)


def rocr(
    real: IntoExpr = pl.col("close"),
    timeperiod: int = 10,
) -> pl.Expr:
    """Rate of change ratio: (price/prevPrice) (Momentum Indicators)
    pl.col("close").ta.rocr(timeperiod=10)

    Inputs:
        real
    Parameters:
        timeperiod: 10
    Outputs:
        real
    """
    return real.ta.rocr(timeperiod=timeperiod)


def rocr100(
    real: IntoExpr = pl.col("close"),
    timeperiod: int = 10,
) -> pl.Expr:
    """Rate of change ratio 100 scale: (price/prevPrice)*100 (Momentum Indicators)
    pl.col("close").ta.rocr100(timeperiod=10)

    Inputs:
        real
    Parameters:
        timeperiod: 10
    Outputs:
        real
    """
    return real.ta.rocr100(timeperiod=timeperiod)


def rsi(
    real: IntoExpr = pl.col("close"),
    timeperiod: int = 14,
) -> pl.Expr:
    """Relative Strength Index (Momentum Indicators)
    pl.col("close").ta.rsi(timeperiod=14)

    Inputs:
        real
    Parameters:
        timeperiod: 14
    Outputs:
        real
    """
    return real.ta.rsi(timeperiod=timeperiod)


def stoch(
    high: IntoExpr = pl.col("high"),
    low: IntoExpr = pl.col("low"),
    close: IntoExpr = pl.col("close"),
    fastk_period: int = 5,
    slowk_period: int = 3,
    slowk_matype: int = 0,
    slowd_period: int = 3,
    slowd_matype: int = 0,
) -> pl.Expr:
    """Stochastic (Momentum Indicators)
    pl.col("close").ta.stoch(pl.col("high"), pl.col("low"), timeperiod=5)

    Inputs:
        prices: ['high', 'low', 'close']
    Parameters:
        fastk_period: 5
        slowk_period: 3
        slowk_matype: 0
        slowd_period: 3
        slowd_matype: 0
    Outputs:
        slowk, slowd
    """
    return close.ta.stoch(
        high,
        low,
        fastk_period=fastk_period,
        slowk_period=slowk_period,
        slowk_matype=slowk_matype,
        slowd_period=slowd_period,
        slowd_matype=slowd_matype,
    )


def stochf(
    high: IntoExpr = pl.col("high"),
    low: IntoExpr = pl.col("low"),
    close: IntoExpr = pl.col("close"),
    fastk_period: int = 5,
    fastd_period: int = 3,
    fastd_matype: int = 0,
) -> pl.Expr:
    """Stochastic Fast (Momentum Indicators)
    pl.col("close").ta.stochf(pl.col("high"), pl.col("low"), timeperiod=5)

    Inputs:
        prices: ['high', 'low', 'close']
    Parameters:
        fastk_period: 5
        fastd_period: 3
        fastd_matype: 0
    Outputs:
        fastk, fastd
    """
    return close.ta.stochf(
        high, low, fastk_period=fastk_period, fastd_period=fastd_period, fastd_matype=fastd_matype
    )


def stochrsi(
    close: IntoExpr = pl.col("close"),
    timeperiod: int = 14,
    fastk_period: int = 5,
    fastd_period: int = 3,
    fastd_matype: int = 0,
) -> pl.Expr:
    """Stochastic Relative Strength Index (Momentum Indicators)
    pl.col("close").ta.stochrsi(timeperiod=14)

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
    return close.ta.stochrsi(
        timeperiod=timeperiod,
        fastk_period=fastk_period,
        fastd_period=fastd_period,
        fastd_matype=fastd_matype,
    )


def trix(price: IntoExpr = pl.col("close"), timeperiod: int = 30) -> pl.Expr:
    """1-day Rate-Of-Change (ROC) of a Triple Smooth EMA (Momentum Indicators)
    pl.col("close").ta.trix(timeperiod=30)

    Inputs:
        prices: ['close']
    Parameters:
        timeperiod: 30
    Outputs:
        real
    """
    return price.ta.trix(timeperiod=timeperiod)


def ultosc(
    high: IntoExpr = pl.col("high"),
    low: IntoExpr = pl.col("low"),
    close: IntoExpr = pl.col("close"),
    timeperiod1: int = 7,
    timeperiod2: int = 14,
    timeperiod3: int = 28,
) -> pl.Expr:
    """Ultimate Oscillator (Momentum Indicators)
    pl.col("close").ta.ultosc(pl.col("high"), pl.col("low"), timeperiod1=7, timeperiod2=14, timeperiod3=28)

    Inputs:
        prices: ['high', 'low', 'close']
    Parameters:
        timeperiod1: 7
        timeperiod2: 14
        timeperiod3: 28
    Outputs:
        real
    """
    return close.ta.ultosc(
        high, low, timeperiod1=timeperiod1, timeperiod2=timeperiod2, timeperiod3=timeperiod3
    )


def willr(
    high: IntoExpr = pl.col("high"),
    low: IntoExpr = pl.col("low"),
    close: IntoExpr = pl.col("close"),
    timeperiod: int = 14,
) -> pl.Expr:
    """Williams' %R (Momentum Indicators)
    pl.col("close").ta.willr(pl.col("high"), pl.col("low"), timeperiod=14)

    Inputs:
        prices: ['high', 'low', 'close']
    Parameters:
        timeperiod: 14
    Outputs:
        real
    """
    return close.ta.willr(high, low, timeperiod=timeperiod)


def bbands(
    real: IntoExpr = pl.col("close"),
    timeperiod: int = 5,
    nbdevup: float = 2.0,
    nbdevdn: float = 2.0,
    matype: int = 0,
) -> pl.Expr:
    """Bollinger Bands (Overlap Studies)
    pl.col("close").ta.bbands(timeperiod=5, nbdevup=2.0, nbdevdn=2.0, matype=0)

    Inputs:
        real
    Parameters:
        timeperiod: 5
        nbdevup: 2.0
        nbdevdn: 2.0
        matype: 0
    Outputs:
        upperband, middleband, lowerband
    """
    return real.ta.bbands(timeperiod=timeperiod, nbdevup=nbdevup, nbdevdn=nbdevdn, matype=matype)


def dema(
    real: IntoExpr = pl.col("close"),
    timeperiod: int = 30,
) -> pl.Expr:
    """Double Exponential Moving Average (Overlap Studies)
    pl.col("close").ta.dema(timeperiod=30)

    Inputs:
        real
    Parameters:
        timeperiod: 30
    Outputs:
        real
    """
    return real.ta.dema(timeperiod=timeperiod)


def ema(
    real: IntoExpr = pl.col("close"),
    timeperiod: int = 30,
) -> pl.Expr:
    """Exponential Moving Average (Overlap Studies)
    pl.col("close").ta.ema(timeperiod=30)

    Inputs:
        real
    Parameters:
        timeperiod: 30
    Outputs:
        real
    """
    return real.ta.ema(timeperiod=timeperiod)


def ht_trendline(
    real: IntoExpr = pl.col("close"),
) -> pl.Expr:
    """Hilbert Transform - Instantaneous Trendline (Overlap Studies)
    pl.col("close").ta.ht_trendline()

    Inputs:
        real
    Outputs:
        real
    """
    return real.ta.ht_trendline()


def kama(
    real: IntoExpr = pl.col("close"),
    timeperiod: int = 30,
) -> pl.Expr:
    """Kaufman Adaptive Moving Average (Overlap Studies)
    pl.col("close").ta.kama(timeperiod=30)

    Inputs:
        real
    Parameters:
        timeperiod: 30
    Outputs:
        real
    """
    return real.ta.kama(timeperiod=timeperiod)


def mama(
    real: IntoExpr = pl.col("close"),
    fastlimit: float = 0.5,
    slowlimit: float = 0.05,
) -> pl.Expr:
    """MESA Adaptive Moving Average (Overlap Studies)
    pl.col("close").ta.mama(fastlimit=0.5, slowlimit=0.05)

    Inputs:
        real
    Parameters:
        fastlimit: 0.5
        slowlimit: 0.05
    Outputs:
        mama, fama
    """
    return real.ta.mama(fastlimit=fastlimit, slowlimit=slowlimit)


def mavp(
    real: IntoExpr = pl.col("close"),
    periods: IntoExpr = pl.col("periods"),
    minperiod: int = 2,
    maxperiod: int = 30,
    matype: int = 0,
) -> pl.Expr:
    """Moving average with variable period (Overlap Studies)
    pl.col("close").ta.mavp(pl.col("periods"), minperiod=2, maxperiod=30, matype=0)

    Inputs:
        real
        periods
    Parameters:
        minperiod: 2
        maxperiod: 30
        matype: 0
    Outputs:
        real
    """
    return real.ta.mavp(periods, minperiod=minperiod, maxperiod=maxperiod, matype=matype)


def midpoint(
    real: IntoExpr = pl.col("close"),
    timeperiod: int = 14,
) -> pl.Expr:
    """MidPoint over period (Overlap Studies)
    pl.col("close").ta.midpoint(timeperiod=14)

    Inputs:
        real
    Parameters:
        timeperiod: 14
    Outputs:
        real
    """
    return real.ta.midpoint(timeperiod=timeperiod)


def midprice(
    high: IntoExpr = pl.col("high"),
    low: IntoExpr = pl.col("low"),
    timeperiod: int = 14,
) -> pl.Expr:
    """Midpoint Price over period (Overlap Studies)
    pl.col("high").ta.midprice("low", timeperiod=14)

    Inputs:
        prices: ['high', 'low']
    Parameters:
        timeperiod: 14
    Outputs:
        real
    """
    return high.ta.midprice(low, timeperiod=timeperiod)


def sar(
    high: IntoExpr = pl.col("high"),
    low: IntoExpr = pl.col("low"),
    acceleration: float = 0.02,
    maximum: float = 0.2,
) -> pl.Expr:
    """Parabolic SAR (Overlap Studies)
    pl.col("high").ta.sar("low", acceleration=0.02, maximum=0.2)

    Inputs:
        prices: ['high', 'low']
    Parameters:
        acceleration: 0.02
        maximum: 0.2
    Outputs:
        real
    """
    return high.ta.sar(low, acceleration=acceleration, maximum=maximum)


def sarext(
    high: IntoExpr = pl.col("high"),
    low: IntoExpr = pl.col("low"),
    startvalue: float = 0,
    offsetonreverse: float = 0,
    accelerationinitlong: float = 0.02,
    accelerationlong: float = 0.02,
    accelerationmaxlong: float = 0.2,
    accelerationinitshort: float = 0.02,
    accelerationshort: float = 0.02,
    accelerationmaxshort: float = 0.2,
) -> pl.Expr:
    """Parabolic SAR - Extended (Overlap Studies)
    pl.col("high").ta.sarext("low", startvalue=0, offsetonreverse=0, accelerationinitlong=0.02, accelerationlong=0.02, accelerationmaxlong=0.2, accelerationinitshort=0.02, accelerationshort=0.02, accelerationmaxshort=0.2)

    Inputs:
        prices: ['high', 'low']
    Parameters:
        startvalue: 0
        offsetonreverse: 0
        accelerationinitlong: 0.02
        accelerationlong: 0.02
        accelerationmaxlong: 0.2
        accelerationinitshort: 0.02
        accelerationshort: 0.02
        accelerationmaxshort: 0.2
    Outputs:
        real
    """
    return high.ta.sarext(
        low,
        startvalue=startvalue,
        offsetonreverse=offsetonreverse,
        accelerationinitlong=accelerationinitlong,
        accelerationlong=accelerationlong,
        accelerationmaxlong=accelerationmaxlong,
        accelerationinitshort=accelerationinitshort,
        accelerationshort=accelerationshort,
        accelerationmaxshort=accelerationmaxshort,
    )


def sma(real: IntoExpr = pl.col("close"), timeperiod: int = 30) -> pl.Expr:
    """Simple Moving Average (Overlap Studies)
    pl.col("close").ta.sma(timeperiod=30)

    Inputs:
        real
    Parameters:
        timeperiod: 30
    Outputs:
        real
    """
    return real.ta.sma(timeperiod=timeperiod)


def ma(
    real: IntoExpr = pl.col("close"),
    timeperiod: int = 30,
    matype: int = 0,
) -> pl.Expr:
    """Moving average (Overlap Studies)
    pl.col("close").ta.ma(timeperiod=30, matype=0)

    Inputs:
        real
    Parameters:
        timeperiod: 30
        matype: 0
    Outputs:
        real
    """
    return real.ta.ma(timeperiod=timeperiod, matype=matype)


def t3(
    real: IntoExpr = pl.col("close"),
    timeperiod: int = 5,
    vfactor: float = 0.7,
) -> pl.Expr:
    """Triple Exponential Moving Average (Overlap Studies)
    pl.col("close").ta.t3(timeperiod=5, vfactor=0.7)

    Inputs:
        real
    Parameters:
        timeperiod: 5
        vfactor: 0.7
    Outputs:
        real
    """
    return real.ta.t3(timeperiod=timeperiod, vfactor=vfactor)


def tema(
    real: IntoExpr = pl.col("close"),
    timeperiod: int = 30,
) -> pl.Expr:
    """Triple Exponential Moving Average (Overlap Studies)
    pl.col("close").ta.tema(timeperiod=30)

    Inputs:
        real
    Parameters:
        timeperiod: 30
    Outputs:
        real
    """
    return real.ta.tema(timeperiod=timeperiod)


def trima(
    real: IntoExpr = pl.col("close"),
    timeperiod: int = 30,
) -> pl.Expr:
    """Triangular Moving Average (Overlap Studies)
    pl.col("close").ta.trima(timeperiod=30)

    Inputs:
        real
    Parameters:
        timeperiod: 30
    Outputs:
        real
    """
    return real.ta.trima(timeperiod=timeperiod)


def wma(
    real: IntoExpr = pl.col("close"),
    timeperiod: int = 30,
) -> pl.Expr:
    """Weighted Moving Average (Overlap Studies)
    pl.col("close").ta.wma(timeperiod=30)

    Inputs:
        real
    Parameters:
        timeperiod: 30
    Outputs:
        real
    """
    return real.ta.wma(timeperiod=timeperiod)


def cdl2crows(
    open: IntoExpr = pl.col("open"),
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
    return open.ta.cdl2crows(high, low, close)


def cdl3blackcrows(
    open: IntoExpr = pl.col("open"),
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
    return open.ta.cdl3blackcrows(high, low, close)


def cdl3inside(
    open: IntoExpr = pl.col("open"),
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
    return open.ta.cdl3inside(high, low, close)


def cdl3linestrike(
    open: IntoExpr = pl.col("open"),
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
    return open.ta.cdl3linestrike(high, low, close)


def cdl3outside(
    open: IntoExpr = pl.col("open"),
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
    return open.ta.cdl3outside(high, low, close)


def cdl3starsinsouth(
    open: IntoExpr = pl.col("open"),
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
    return open.ta.cdl3starsinsouth(high, low, close)


def cdl3whitesoldiers(
    open: IntoExpr = pl.col("open"),
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
    return open.ta.cdl3whitesoldiers(high, low, close)


def cdlabandonedbaby(
    open: IntoExpr = pl.col("open"),
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
    return open.ta.cdlabandonedbaby(high, low, close, penetration=penetration)


def cdladvanceblock(
    open: IntoExpr = pl.col("open"),
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
    return open.ta.cdladvanceblock(high, low, close)


def cdlbelthold(
    open: IntoExpr = pl.col("open"),
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
    return open.ta.cdlbelthold(high, low, close)


def cdlbreakaway(
    open: IntoExpr = pl.col("open"),
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
    return open.ta.cdlbreakaway(high, low, close)


def cdlclosingmarubozu(
    open: IntoExpr = pl.col("open"),
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
    return open.ta.cdlclosingmarubozu(high, low, close)


def cdlconcealbabyswall(
    open: IntoExpr = pl.col("open"),
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
    return open.ta.cdlconcealbabyswall(high, low, close)


def cdlcounterattack(
    open: IntoExpr = pl.col("open"),
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
    return open.ta.cdlcounterattack(high, low, close)


def cdldarkcloudcover(
    open: IntoExpr = pl.col("open"),
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
    return open.ta.cdldarkcloudcover(high, low, close, penetration=penetration)


def cdldoji(
    open: IntoExpr = pl.col("open"),
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
    return open.ta.cdldoji(high, low, close)


def cdldojistar(
    open: IntoExpr = pl.col("open"),
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
    return open.ta.cdldojistar(high, low, close)


def cdldragonflydoji(
    open: IntoExpr = pl.col("open"),
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
    return open.ta.cdldragonflydoji(high, low, close)


def cdlengulfing(
    open: IntoExpr = pl.col("open"),
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
    return open.ta.cdlengulfing(high, low, close)


def cdleveningdojistar(
    open: IntoExpr = pl.col("open"),
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
    return open.ta.cdleveningdojistar(high, low, close, penetration=penetration)


def cdleveningstar(
    open: IntoExpr = pl.col("open"),
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
    return open.ta.cdleveningstar(high, low, close, penetration=penetration)


def cdlgapsidesidewhite(
    open: IntoExpr = pl.col("open"),
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
    return open.ta.cdlgapsidesidewhite(high, low, close)


def cdlgravestonedoji(
    open: IntoExpr = pl.col("open"),
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
    return open.ta.cdlgravestonedoji(high, low, close)


def cdlhammer(
    open: IntoExpr = pl.col("open"),
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
    return open.ta.cdlhammer(high, low, close)


def cdlhangingman(
    open: IntoExpr = pl.col("open"),
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
    return open.ta.cdlhangingman(high, low, close)


def cdlharami(
    open: IntoExpr = pl.col("open"),
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
    return open.ta.cdlharami(high, low, close)


def cdlharamicross(
    open: IntoExpr = pl.col("open"),
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
    return open.ta.cdlharamicross(high, low, close)


def cdlhighwave(
    open: IntoExpr = pl.col("open"),
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
    return open.ta.cdlhighwave(high, low, close)


def cdlhikkake(
    open: IntoExpr = pl.col("open"),
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
    return open.ta.cdlhikkake(high, low, close)


def cdlhikkakemod(
    open: IntoExpr = pl.col("open"),
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
    return open.ta.cdlhikkakemod(high, low, close)


def cdlhomingpigeon(
    open: IntoExpr = pl.col("open"),
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
    return open.ta.cdlhomingpigeon(high, low, close)


def cdlidentical3crows(
    open: IntoExpr = pl.col("open"),
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
    return open.ta.cdlidentical3crows(high, low, close)


def cdlinneck(
    open: IntoExpr = pl.col("open"),
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
    return open.ta.cdlinneck(high, low, close)


def cdlinvertedhammer(
    open: IntoExpr = pl.col("open"),
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
    return open.ta.cdlinvertedhammer(high, low, close)


def cdlkicking(
    open: IntoExpr = pl.col("open"),
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
    return open.ta.cdlkicking(high, low, close)


def cdlkickingbylength(
    open: IntoExpr = pl.col("open"),
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
    return open.ta.cdlkickingbylength(high, low, close)


def cdlladderbottom(
    open: IntoExpr = pl.col("open"),
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
    return open.ta.cdlladderbottom(high, low, close)


def cdllongleggeddoji(
    open: IntoExpr = pl.col("open"),
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
    return open.ta.cdllongleggeddoji(high, low, close)


def cdllongline(
    open: IntoExpr = pl.col("open"),
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
    return open.ta.cdllongline(high, low, close)


def cdlmarubozu(
    open: IntoExpr = pl.col("open"),
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
    return open.ta.cdlmarubozu(high, low, close)


def cdlmatchinglow(
    open: IntoExpr = pl.col("open"),
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
    return open.ta.cdlmatchinglow(high, low, close)


def cdlmathold(
    open: IntoExpr = pl.col("open"),
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
    return open.ta.cdlmathold(high, low, close, penetration=penetration)


def cdlmorningdojistar(
    open: IntoExpr = pl.col("open"),
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
    return open.ta.cdlmorningdojistar(high, low, close, penetration=penetration)


def cdlmorningstar(
    open: IntoExpr = pl.col("open"),
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
    return open.ta.cdlmorningstar(high, low, close, penetration=penetration)


def cdlonneck(
    open: IntoExpr = pl.col("open"),
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
    return open.ta.cdlonneck(high, low, close)


def cdlpiercing(
    open: IntoExpr = pl.col("open"),
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
    return open.ta.cdlpiercing(high, low, close)


def cdlrickshawman(
    open: IntoExpr = pl.col("open"),
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
    return open.ta.cdlrickshawman(high, low, close)


def cdlrisefall3methods(
    open: IntoExpr = pl.col("open"),
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
    return open.ta.cdlrisefall3methods(high, low, close)


def cdlseparatinglines(
    open: IntoExpr = pl.col("open"),
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
    return open.ta.cdlseparatinglines(high, low, close)


def cdlshootingstar(
    open: IntoExpr = pl.col("open"),
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
    return open.ta.cdlshootingstar(high, low, close)


def cdlshortline(
    open: IntoExpr = pl.col("open"),
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
    return open.ta.cdlshortline(high, low, close)


def cdlspinningtop(
    open: IntoExpr = pl.col("open"),
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
    return open.ta.cdlspinningtop(high, low, close)


def cdlstalledpattern(
    open: IntoExpr = pl.col("open"),
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
    return open.ta.cdlstalledpattern(high, low, close)


def cdlsticksandwich(
    open: IntoExpr = pl.col("open"),
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
    return open.ta.cdlsticksandwich(high, low, close)


def cdltakuri(
    open: IntoExpr = pl.col("open"),
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
    return open.ta.cdltakuri(high, low, close)


def cdltasukigap(
    open: IntoExpr = pl.col("open"),
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
    return open.ta.cdltasukigap(high, low, close)


def cdlthrusting(
    open: IntoExpr = pl.col("open"),
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
    return open.ta.cdlthrusting(high, low, close)


def cdltristar(
    open: IntoExpr = pl.col("open"),
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
    return open.ta.cdltristar(high, low, close)


def cdlunique3river(
    open: IntoExpr = pl.col("open"),
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
    return open.ta.cdlunique3river(high, low, close)


def cdlupsidegap2crows(
    open: IntoExpr = pl.col("open"),
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
    return open.ta.cdlupsidegap2crows(high, low, close)


def cdlxsidegap3methods(
    open: IntoExpr = pl.col("open"),
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
    return open.ta.cdlxsidegap3methods(high, low, close)


def avgprice(
    open: IntoExpr = pl.col("open"),
    high: IntoExpr = pl.col("high"),
    low: IntoExpr = pl.col("low"),
    close: IntoExpr = pl.col("close"),
):
    """Average Price
    pl.col("open").ta.avgprice(pl.col("high"), pl.col("low"), pl.col("close"))

    Inputs:
        prices: ['open', 'high', 'low', 'close']
    Outputs:
        avgprice

    """
    return open.ta.avgprice(high, low, close)


def medprice(
    high: IntoExpr = pl.col("high"),
    low: IntoExpr = pl.col("low"),
):
    """Median Price
    pl.col("high").ta.medprice(pl.col("low"))

    Inputs:
        prices: ['high', 'low']
    Outputs:
        medprice

    """
    return high.ta.medprice(low)


def typprice(
    high: IntoExpr = pl.col("high"),
    low: IntoExpr = pl.col("low"),
    close: IntoExpr = pl.col("close"),
):
    """Typical Price
    pl.col("high").ta.typprice(pl.col("low"), pl.col("close"))

    Inputs:
        prices: ['high', 'low', 'close']
    Outputs:
        typprice

    """
    return high.ta.typprice(low, close)


def wclprice(
    high: IntoExpr = pl.col("high"),
    low: IntoExpr = pl.col("low"),
    close: IntoExpr = pl.col("close"),
):
    """Weighted Close Price
    pl.col("high").ta.wclprice(pl.col("low"), pl.col("close"))

    Inputs:
        prices: ['high', 'low', 'close']
    Outputs:
        wclprice

    """
    return close.ta.wclprice(high, low)


def beta(
    price0: IntoExpr = pl.col("high"),
    price1: IntoExpr = pl.col("low"),
    timeperiod: int = 5,
):
    """Beta
    pl.col("high").ta.beta(pl.col("low"), timeperiod=5)

    Inputs:
        prices: ['high', 'low']
    Parameters:
        timeperiod: 5
    Outputs:
        beta
    """
    return price0.ta.beta(price1, timeperiod=timeperiod)


def correl(
    price0: IntoExpr = pl.col("high"),
    price1: IntoExpr = pl.col("low"),
    timeperiod: int = 30,
):
    """Pearson's Correlation Coefficient (r)
    pl.col("high").ta.correl(pl.col("low"), timeperiod=30)

    Inputs:
        prices: ['high', 'low']
    Parameters:
        timeperiod: 30
    Outputs:
        correl
    """
    return price0.ta.correl(price1, timeperiod=timeperiod)


def linearreg(
    price: IntoExpr = pl.col("close"),
    timeperiod: int = 14,
):
    """Linear Regression
    pl.col("close").ta.linearreg(timeperiod=14)

    Inputs:
        prices: ['close']
    Parameters:
        timeperiod: 14
    Outputs:
        linearreg
    """
    return price.ta.linearreg(timeperiod=timeperiod)


def linearreg_angle(
    price: IntoExpr = pl.col("close"),
    timeperiod: int = 14,
):
    """Linear Regression Angle
    pl.col("close").ta.linearreg_angle(timeperiod=14)

    Inputs:
        prices: ['close']
    Parameters:
        timeperiod: 14
    Outputs:
        linearreg_angle
    """
    return price.ta.linearreg_angle(timeperiod=timeperiod)


def linearreg_intercept(
    price: IntoExpr = pl.col("close"),
    timeperiod: int = 14,
):
    """Linear Regression Intercept
    pl.col("close").ta.linearreg_intercept(timeperiod=14)

    Inputs:
        prices: ['close']
    Parameters:
        timeperiod: 14
    Outputs:
        linearreg_intercept
    """
    return price.ta.linearreg_intercept(timeperiod=timeperiod)


def linearreg_slope(
    price: IntoExpr = pl.col("close"),
    timeperiod: int = 14,
):
    """Linear Regression Slope
    pl.col("close").ta.linearreg_slope(timeperiod=14)

    Inputs:
        prices: ['close']
    Parameters:
        timeperiod: 14
    Outputs:
        linearreg_slope
    """
    return price.ta.linearreg_slope(timeperiod=timeperiod)


def stddev(
    price: IntoExpr = pl.col("close"),
    timeperiod: int = 5,
    nbdev: float = 1,
):
    """Standard Deviation
    pl.col("close").ta.stddev(timeperiod=5, nbdev=1)

    Inputs:
        prices: ['close']
    Parameters:
        timeperiod: 5
        nbdev: 1
    Outputs:
        stddev
    """
    return price.ta.stddev(timeperiod=timeperiod, nbdev=nbdev)


def tsf(
    price: IntoExpr = pl.col("close"),
    timeperiod: int = 14,
):
    """Time Series Forecast
    pl.col("close").ta.tsf(timeperiod=14)

    Inputs:
        prices: ['close']
    Parameters:
        timeperiod: 14
    Outputs:
        tsf
    """
    return price.ta.tsf(timeperiod=timeperiod)


def var(
    price: IntoExpr = pl.col("close"),
    timeperiod: int = 5,
    nbdev: float = 1,
):
    """Variance
    pl.col("close").ta.var(timeperiod=5, nbdev=1)

    Inputs:
        prices: ['close']
    Parameters:
        timeperiod: 5
        nbdev: 1
    Outputs:
        var
    """
    return price.ta.var(timeperiod=timeperiod, nbdev=nbdev)


def atr(
    high: IntoExpr = pl.col("high"),
    low: IntoExpr = pl.col("low"),
    close: IntoExpr = pl.col("close"),
    timeperiod: int = 14,
):
    """Average True Range (Volatility Indicators)
    pl.col("close").ta.atr(pl.col("high"), pl.col("low"), timeperiod=14)

    Inputs:
        prices: ['high', 'low', 'close']
    Parameters:
        timeperiod: 14
    Outputs:
        atr
    """
    return close.ta.atr(high, low, timeperiod=timeperiod)


def natr(
    high: IntoExpr = pl.col("high"),
    low: IntoExpr = pl.col("low"),
    close: IntoExpr = pl.col("close"),
    timeperiod: int = 14,
):
    """Normalized Average True Range (Volatility Indicators)
    pl.col("close").ta.natr(pl.col("high"), pl.col("low"), timeperiod=14)

    Inputs:
        prices: ['high', 'low', 'close']
    Parameters:
        timeperiod: 14
    Outputs:
        natr
    """
    return close.ta.natr(high, low, timeperiod=timeperiod)


def trange(
    high: IntoExpr = pl.col("high"),
    low: IntoExpr = pl.col("low"),
    close: IntoExpr = pl.col("close"),
):
    """True Range (Volatility Indicators)
    pl.col("close").ta.trange(pl.col("high"), pl.col("low"))

    Inputs:
        prices: ['high', 'low', 'close']
    Outputs:
        trange
    """
    return close.ta.trange(high, low)


def ad(
    high: IntoExpr = pl.col("high"),
    low: IntoExpr = pl.col("low"),
    close: IntoExpr = pl.col("close"),
    volume: IntoExpr = pl.col("volume"),
):
    """Chaikin A/D Line (Volume Indicators)
    pl.col("close").ta.ad(pl.col("high"), pl.col("low"), pl.col("volume"))

    Inputs:
        prices: ['high', 'low', 'close', 'volume']
    Outputs:
        ad
    """
    return close.ta.ad(high, low, volume)


def adosc(
    high: IntoExpr = pl.col("high"),
    low: IntoExpr = pl.col("low"),
    close: IntoExpr = pl.col("close"),
    volume: IntoExpr = pl.col("volume"),
    fastperiod: int = 3,
    slowperiod: int = 10,
):
    """Chaikin A/D Oscillator (Volume Indicators)
    pl.col("close").ta.adosc(pl.col("high"), pl.col("low"), pl.col("volume"), fastperiod=3, slowperiod=10)

    Inputs:
        prices: ['high', 'low', 'close', 'volume']
    Parameters:
        fastperiod: 3
        slowperiod: 10
    Outputs:
        adosc
    """
    return close.ta.adosc(high, low, volume, fastperiod=fastperiod, slowperiod=slowperiod)


def obv(
    close: IntoExpr = pl.col("close"),
    volume: IntoExpr = pl.col("volume"),
):
    """On Balance Volume (Volume Indicators)
    pl.col("close").ta.obv(pl.col("volume"))

    Inputs:
        prices: ['close', 'volume']
    Outputs:
        obv
    """
    return close.ta.obv(volume)
