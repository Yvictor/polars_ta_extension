import polars as pl
from polars.type_aliases import IntoExpr
from polars.utils.udfs import _get_shared_lib_location

# Boilerplate needed to inform Polars of the location of binary wheel.
lib = _get_shared_lib_location(__file__)



@pl.api.register_expr_namespace("ta")
class TAExpr:
    def __init__(self, expr: pl.Expr):
        self._expr = expr

    def ema(
        self,
        timeperiod: int,
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
            is_elementwise=True,
        )
    
    def ema2(
        self,
        timeperiod: int,
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
            symbol="ema2",
            is_elementwise=True,
        )

@pl.api.register_expr_namespace("language")
class Language:
    def __init__(self, expr: pl.Expr):
        self._expr = expr

    def pig_latinnify(self) -> pl.Expr:
        return self._expr.register_plugin(
            lib=lib,
            symbol="pig_latinnify",
            is_elementwise=True,
        )


@pl.api.register_expr_namespace("my_expr")
class MyCustomExpr:
    def __init__(self, expr: pl.Expr):
        self._expr = expr

    def append_args(
        self,
        float_arg: float,
        integer_arg: int,
        string_arg: str,
        boolean_arg: bool,
    ) -> pl.Expr:
        """
        This example shows how arguments other than `Series` can be used.
        """
        return self._expr.register_plugin(
            lib=lib,
            args=[],
            kwargs={
                "float_arg": float_arg,
                "integer_arg": integer_arg,
                "string_arg": string_arg,
                "boolean_arg": boolean_arg,
            },
            symbol="append_kwargs",
            is_elementwise=True,
        )
