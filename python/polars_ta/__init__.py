import polars as pl
from polars.type_aliases import IntoExpr
from polars.utils.udfs import _get_shared_lib_location

# Boilerplate needed to inform Polars of the location of binary wheel.
lib = _get_shared_lib_location(__file__)


@pl.api.register_expr_namespace("ta")
class TAExpr:
    def __init__(self, expr: pl.Expr):
        self._expr = expr

    def bbands(self, timeperiod: int = 5, nbdevup: float = 2.0, nbdevdn: float = 2.0, ma_type: int = 0) -> pl.Expr:
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
            is_elementwise=True,
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

    def natr(self, high: IntoExpr, low: IntoExpr, timeperiod: int) -> pl.Expr:
        """ natr
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
