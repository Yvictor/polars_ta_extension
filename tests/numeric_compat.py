"""TA-Lib 0.8.3 reorders floating arithmetic; discrete outputs remain exact."""
import polars as pl
from polars.testing import assert_frame_equal, assert_series_equal


def different(a: pl.Expr, b: pl.Expr) -> pl.Expr:
    # Equal NaNs are warmup/domain values. Finite comparisons use the same
    # tolerance as the complete-API differential tests, never decimal rounding.
    equal = (a == b) | (a.is_nan() & b.is_nan())
    close = (a-b).abs() <= 1e-10 + 1e-10*b.abs()
    return ~(equal | close)


def assert_compatible(actual, expected):
    compare = assert_frame_equal if isinstance(actual, pl.DataFrame) else assert_series_equal
    compare(actual, expected, check_exact=False, rel_tol=1e-10, abs_tol=1e-10)
