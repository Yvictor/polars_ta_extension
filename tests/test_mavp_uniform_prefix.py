"""MAVP uniform normalized periods and the first nonuniform boundary.

The assertions cover the public adapter, including its full-input compatibility
routing. The allocation diagnostic separately exercises the selected SMA helper.
NaN payload/sign are excluded; finite values, signed zeros, padding and schema
are compared exactly to the installed original C0.8.1 reference.
"""
import numpy as np
import polars as pl
import polars_talib as ta
import pytest
import talib

PATTERNS = ("one", "fractional", "lower", "upper", "late", "blocked")


def arrays(n, pattern, price_shape):
    price = 100. + np.arange(n, dtype=float) % 17 / 100.
    if price_shape == "zero":
        price = np.resize(np.array([-0., 0.]), n)
    elif price_shape == "large":
        price += 1025.
    elif n > 1 and price_shape in ("nan", "inf"):
        price[n // 2] = np.nan if price_shape == "nan" else np.inf
    periods = np.full(n, 14.)
    if pattern == "fractional":
        periods = np.resize(np.array([14.01, 14.25, 14.999]), n)
    elif pattern == "lower":
        periods = np.resize(np.array([-0., 0.75, 1.]), n)
    elif pattern == "upper":
        periods = np.resize(np.array([31., 100., 255.25]), n)
    elif pattern == "late" and n:
        periods[-1] = 3.
    elif pattern == "blocked" and n:
        periods = np.array([3., 5., 9., 14.])[np.minimum(np.arange(n) * 4 // n, 3)]
    return price, periods


def assert_output(actual, expected):
    assert actual.dtype == pl.Float64
    assert actual.null_count() == 0
    assert len(actual) == len(expected)
    values = actual.to_numpy()
    np.testing.assert_array_equal(np.isnan(values), np.isnan(expected))
    valid = ~np.isnan(expected)
    np.testing.assert_array_equal(values[valid].view(np.uint64), expected[valid].view(np.uint64))


@pytest.mark.parametrize("n", [0, 1, 29, 30, 31, 64, 257])
@pytest.mark.parametrize("pattern", PATTERNS)
@pytest.mark.parametrize("minimum", [1, 2])
@pytest.mark.parametrize("price_shape", ["finite", "zero", "nan", "inf", "large"])
def test_uniform_and_first_difference_public_eager_lazy(n, pattern, minimum, price_shape):
    price, periods = arrays(n, pattern, price_shape)
    frame = pl.DataFrame({"close": price, "periods": periods})
    expected = talib.MAVP(price, periods, minperiod=minimum, maxperiod=30, matype=0)
    expression = ta.mavp("close", "periods", minperiod=minimum, maxperiod=30)
    assert_output(frame.select(expression).to_series(), expected)
    assert_output(frame.lazy().select(expression).collect().to_series(), expected)


@pytest.mark.parametrize("n", [31, 64, 257])
@pytest.mark.parametrize("pattern", PATTERNS)
@pytest.mark.parametrize("interleaved", [False, True])
@pytest.mark.parametrize("minimum", [1, 2])
def test_uniform_and_first_difference_native_over(n, pattern, interleaved, minimum):
    frames = []
    expected = []
    for group in range(3):
        price, periods = arrays(n, pattern, "zero" if group == 1 else "finite")
        values = talib.MAVP(price, periods, minperiod=minimum, maxperiod=30, matype=0)
        frames.append(pl.DataFrame({"close": price, "periods": periods,
                                    "symbol": np.full(n, group), "within": np.arange(n)}))
        expected.append(values)
    frame = pl.concat(frames, rechunk=False)
    values = np.concatenate(expected)
    if interleaved:
        frame = frame.sort("within", "symbol")
        values = np.stack(expected, axis=1).reshape(-1)
    expression = pl.col("close").ta.mavp(pl.col("periods"), minperiod=minimum, maxperiod=30).over("symbol")
    assert_output(frame.lazy().select(expression).collect().to_series(), values)


@pytest.mark.parametrize("pattern", PATTERNS)
def test_uniform_prefix_chunked_input_preserves_exact_bits(pattern):
    price, periods = arrays(257, pattern, "finite")
    frame = pl.DataFrame({"close": price, "periods": periods})
    frame = pl.concat([frame[:31], frame[31:128], frame[128:]], rechunk=False)
    assert frame["close"].n_chunks() == 3
    expected = talib.MAVP(price, periods, minperiod=1, maxperiod=30, matype=0)
    assert_output(frame.select(ta.mavp("close", "periods", minperiod=1)).to_series(), expected)


@pytest.mark.parametrize("kwargs", [{"minperiod": 0}, {"maxperiod": 0},
                                    {"minperiod": 31, "maxperiod": 30}])
def test_uniform_prefix_invalid_parameters_remain_errors(kwargs):
    frame = pl.DataFrame({"close": [100.] * 64, "periods": [14.] * 64})
    with pytest.raises(pl.exceptions.ComputeError):
        frame.select(ta.mavp("close", "periods", **kwargs))
