import numpy as np
import polars as pl
import polars_talib as plta
import pytest


@pytest.mark.parametrize(
    "expr",
    [
        plta.max(pl.col("c"), 2),
        plta.min(pl.col("c"), 2),
        plta.sum(pl.col("c"), 2),
    ],
)
def test_float_math_over_short_null_and_nan_groups_preserves_length(expr: pl.Expr):
    df = pl.DataFrame({"c": [1, 2, 3, 4, 5.0, None, np.nan]}, strict=False)

    result = df.select(expr.over("c").alias("out"))

    assert result.height == df.height
    assert result["out"].is_nan().all()


@pytest.mark.parametrize(
    "expr",
    [
        plta.maxindex(pl.col("c"), 2),
        plta.minindex(pl.col("c"), 2),
    ],
)
def test_index_math_over_short_null_and_nan_groups_preserves_length(expr: pl.Expr):
    df = pl.DataFrame({"c": [1, 2, 3, 4, 5.0, None, np.nan]}, strict=False)

    result = df.select(expr.over("c").alias("out"))

    assert result.height == df.height
    assert result["out"].to_list() == [0] * df.height


def test_minmax_over_short_null_and_nan_groups_preserves_length():
    df = pl.DataFrame({"c": [1, 2, 3, 4, 5.0, None, np.nan]}, strict=False)

    result = df.select(plta.minmax(pl.col("c"), 2).over("c").alias("out")).unnest("out")

    assert result.height == df.height
    assert result.select(pl.all().is_nan().all()).row(0) == (True, True)


def test_minmaxindex_over_short_null_and_nan_groups_preserves_length():
    df = pl.DataFrame({"c": [1, 2, 3, 4, 5.0, None, np.nan]}, strict=False)

    result = df.select(plta.minmaxindex(pl.col("c"), 2).over("c").alias("out")).unnest("out")

    assert result.height == df.height
    assert result.rows() == [(0, 0)] * df.height


@pytest.mark.parametrize(
    "expr",
    [
        plta.max(pl.col("c"), 0),
        plta.maxindex(pl.col("c"), 0),
        plta.min(pl.col("c"), 0),
        plta.minindex(pl.col("c"), 0),
        plta.minmax(pl.col("c"), 0),
        plta.minmaxindex(pl.col("c"), 0),
        plta.sum(pl.col("c"), 0),
    ],
)
def test_invalid_timeperiod_still_raises_bad_param(expr: pl.Expr):
    df = pl.DataFrame({"c": [1.0, 2.0, 3.0]})

    with pytest.raises(pl.exceptions.ComputeError, match="TA_BAD_PARAM"):
        df.select(expr.alias("out"))


@pytest.mark.parametrize(
    "expr",
    [
        plta.macd(pl.col("close")),
        plta.macdext(pl.col("close")),
        plta.macdfix(pl.col("close")),
    ],
)
def test_macd_over_groups_shorter_than_lookback_preserves_length(expr: pl.Expr):
    df = pl.DataFrame(
        {
            "g": ["a", "a", "b", "b", "b"],
            "close": [1.0, 2.0, 3.0, 4.0, 5.0],
        }
    )

    result = df.select(expr.over("g").alias("macd")).unnest("macd")

    assert result.height == df.height
    assert result.select(pl.all().is_nan().all()).row(0) == (True, True, True)


@pytest.mark.parametrize(
    "func",
    ["kdj", "supertrend", "eri", "fractal", "smi", "vortex", "accbands", "donchian", "kc", "ha"],
)
def test_new_struct_functions_over_short_groups_preserve_length(func: str):
    df = pl.DataFrame(
        {
            "g": ["a", "a", "b", "b", "b"],
            "open": [1.0, 2.0, 3.0, 4.0, 5.0],
            "high": [1.5, 2.5, 3.5, 4.5, 5.5],
            "low": [0.5, 1.5, 2.5, 3.5, 4.5],
            "close": [1.2, 2.2, 3.2, 4.2, 5.2],
        }
    )

    result = df.select(getattr(plta, func)().over("g").alias("out")).unnest("out")

    assert result.height == df.height
    assert result.columns == plta.get_functions_output_struct()[func]


@pytest.mark.parametrize("func", ["vwap", "cmf", "efi", "rvol", "pvo", "vwma"])
def test_new_volume_functions_accept_int_volume(func: str):
    n = 60
    df = pl.DataFrame(
        {
            "high": [float(i) + 1.0 for i in range(n)],
            "low": [float(i) - 1.0 for i in range(n)],
            "close": [float(i) for i in range(n)],
            "volume": list(range(1000, 1000 + n)),
        }
    )

    result = df.select(getattr(plta, func)().alias("out"))

    assert result.height == n
    assert result["out"].dtype == pl.Float64
    assert result["out"].tail(1).is_nan().sum() == 0


def test_talib_version_and_function_count():
    assert plta.__talib_version__.startswith("0.8.1")
    assert len(plta.get_functions()) == 201
    assert "kdj" in plta.get_function_groups()["Momentum Indicators"]
