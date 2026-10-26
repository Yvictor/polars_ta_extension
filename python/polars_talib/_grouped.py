"""Explicit whole-column dispatch for grouped indicators."""
from __future__ import annotations
import inspect
from pathlib import Path
from typing import Sequence
import polars as pl
from .utils import parse_into_expr, register_plugin
from ._grouped_abi import GROUPED_ABI


def by_group(function: str, *args, by: str | pl.Expr | Sequence[str | pl.Expr], **kwargs) -> pl.Expr:
    """Compute an indicator per key using a single native plugin invocation.

    ``by_group("atr", by="symbol", timeperiod=14)`` has the same input and
    parameter defaults as ``atr(...).over("symbol")``. Supports multiple keys,
    null keys, non-contiguous groups, integer and Struct outputs. Input row
    order is retained within each group; sort by timestamp first. This explicit
    dispatcher is separate from Polars' own ``Expr.over`` implementation.
    """
    from . import __dict__ as api
    function = function.lower()
    if function not in GROUPED_ABI:
        raise ValueError(f"unknown TA-Lib function: {function}")
    signature = inspect.signature(api[function])
    bound = signature.bind(*args, **kwargs)
    bound.apply_defaults()
    order, count = GROUPED_ABI[function]
    parameters = list(bound.arguments)
    # The original top-level positional order follows the indicator inventory;
    # plugins retain their historical namespace receiver permutation.
    values = [parse_into_expr(bound.arguments[p]) for p in parameters[:count]]
    inputs = [values[order.index(i)] for i in range(count)]
    params = {p: bound.arguments[p] for p in parameters[count:]}
    groups = [by] if isinstance(by, (str, pl.Expr)) else list(by)
    if not groups:
        raise ValueError("by_group requires at least one group key")
    keys = [parse_into_expr(key) for key in groups]
    return register_plugin(symbol=function, args=inputs, kwargs=params,
                           is_elementwise=False, lib=Path(__file__).parent, group_by=keys)
