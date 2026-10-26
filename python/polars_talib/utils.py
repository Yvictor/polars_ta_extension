from __future__ import annotations

from enum import IntEnum
from numbers import Integral, Real
from ._missing import WINDOW_BOUNDED
from ._param_types import INTEGER_PARAMETERS
from pathlib import Path
import re
from typing import Any, Sequence

import polars as pl
from polars._typing import IntoExpr, PolarsDataType
from polars.plugins import register_plugin_function


def parse_version(version: Sequence[str | int]) -> tuple[int, ...]:
    if isinstance(version, str):
        version = version.split('.')
    return tuple(int(re.sub(r'\D', '', str(v))) for v in version)


def parse_into_expr(expr: IntoExpr, *, str_as_lit: bool = False,
                    list_as_lit: bool = True, dtype: PolarsDataType | None = None) -> pl.Expr:
    if isinstance(expr, pl.Expr):
        return expr
    if isinstance(expr, str) and not str_as_lit:
        return pl.col(expr)
    if isinstance(expr, list) and not list_as_lit:
        return pl.lit(pl.Series(expr), dtype=dtype)
    return pl.lit(expr, dtype=dtype)


def register_plugin(*, symbol: str, is_elementwise: bool,
                    kwargs: dict[str, Any] | None = None, args: list[IntoExpr],
                    lib: str | Path, returns_scalar: bool = False) -> pl.Expr:
    if kwargs:
        kwargs = dict(kwargs)
        for key in INTEGER_PARAMETERS.get(symbol, ()):
            if key in kwargs:
                value = kwargs[key]
                if isinstance(value, bool) or not isinstance(value, Real):
                    raise TypeError(f"{symbol}: {key} must be an integer, got {type(value).__name__}")
                if not isinstance(value, Integral):
                    # Whole-number floats such as 14.0 are accepted like upstream TA-Lib;
                    # fractional periods are rejected instead of silently truncated.
                    if not float(value).is_integer():
                        raise ValueError(f"{symbol}: {key} must be a whole number, got {value!r}")
                    value = int(value)
                if not -(2**31) <= value < 2**31:
                    raise ValueError(f"{symbol}: {key} must fit a signed 32-bit integer")
                kwargs[key] = int(value)
        kwargs = {key: int(value) if isinstance(value, IntEnum) else value
                  for key, value in kwargs.items()}
    # A null input is a missing observation; TA-Lib would see it as NaN, whose
    # results are undefined (issue #42). Each plugin nulls the output rows that
    # depend on a null input after the first usable row: to the end for
    # recursive indicators, for `lookback` rows otherwise. NaN and infinity are
    # ordinary float values and reach TA-Lib unchanged. Plugins evaluate one
    # `.over(...)` partition at a time, so the mask never crosses partitions.
    policy = {
        "params": kwargs or {},
        "lookback": _lookback(symbol, kwargs) if MASK_MISSING else -1,
        "recursive": symbol not in WINDOW_BOUNDED,
    }
    return register_plugin_function(
        args=args, plugin_path=lib, function_name=symbol, kwargs=policy,
        is_elementwise=is_elementwise, returns_scalar=returns_scalar,
    )


# Internal switch for scripts that study raw TA-Lib output; never disable it in
# user code, because unmasked results can contain values computed from nulls.
MASK_MISSING = True


def _lookback(symbol: str, kwargs: dict[str, Any] | None) -> int:
    from ._polars_talib import lookback
    return lookback(symbol, kwargs or None)
