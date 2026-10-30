"""Freeze SMA result bits and ordinary native window behavior against C0.8.1."""
import numpy as np
import polars as pl
import polars_talib as ta
import pytest
import talib


def assert_exact(actual, expected):
    np.testing.assert_array_equal(actual, expected)
    valid = ~np.isnan(expected)
    np.testing.assert_array_equal(np.signbit(actual[valid]), np.signbit(expected[valid]))


@pytest.mark.parametrize('pattern', ['one', 'four', 'few', 'many', 'blocked', 'clamped'])
@pytest.mark.parametrize('grouped', [False, True])
def test_sma_selected_outputs_match_c_in_native_windows(pattern, grouped):
    n = 513
    price = 100 + np.cumsum(np.random.default_rng(260126).normal(0, .1, n))
    periods = {
        'one': np.full(n, 14.),
        'four': np.resize([3., 5., 9., 14.], n),
        'few': np.resize([3., 14.], n),
        'many': 2. + np.arange(n) % 29,
        'blocked': np.array([3., 5., 9., 14.])[np.minimum(np.arange(n) * 4 // n, 3)],
        'clamped': np.resize([np.nan, -np.inf, 1., 3.75, 9., np.inf], n),
    }[pattern]
    minimum = 1 if pattern == 'clamped' else 2
    groups = np.arange(n) % 3 if grouped else np.zeros(n, dtype=np.int64)
    frame = pl.DataFrame({'close': price, 'periods': periods, 'g': groups})
    expr = ta.mavp('close', 'periods', minperiod=minimum, maxperiod=30, matype=0)
    if grouped:
        expr = expr.over('g')
    actual = frame.lazy().select(expr).collect().to_series()
    assert actual.dtype == pl.Float64 and actual.null_count() == 0 and len(actual) == n
    expected = np.empty(n)
    for group in np.unique(groups):
        indices = np.flatnonzero(groups == group)
        expected[indices] = talib.MAVP(price[indices], periods[indices], minperiod=minimum, maxperiod=30, matype=0)
    assert_exact(actual.to_numpy(), expected)


@pytest.mark.parametrize('pattern', ['signed_zero', 'leading_nan', 'internal_nan', 'infinity', 'high_offset', 'null'])
@pytest.mark.parametrize('grouped', [False, True])
def test_sma_guarded_and_missing_inputs_keep_existing_semantics(pattern, grouped):
    n = 513
    price = 100. + (np.arange(n) % 17) / 100.
    periods = np.resize([1., 3., 5., 9., 14.], n)
    if pattern == 'signed_zero':
        price = np.where(np.arange(n) % 2, 0., -0.)
    elif pattern == 'leading_nan':
        price[:9] = np.nan
    elif pattern in ('internal_nan', 'null'):
        price[200] = np.nan
    elif pattern == 'infinity':
        price[200] = np.inf
    elif pattern == 'high_offset':
        price += 1e9
    groups = np.arange(n) % 3 if grouped else np.zeros(n, dtype=np.int64)
    close = price.tolist()
    if pattern == 'null':
        close[200] = None
    frame = pl.DataFrame({'close': close, 'periods': periods, 'g': groups})
    expr = ta.mavp('close', 'periods', minperiod=1, maxperiod=30, matype=0)
    if grouped:
        expr = expr.over('g')
    actual = frame.select(expr).to_series()
    expected = np.empty(n)
    for group in np.unique(groups):
        indices = np.flatnonzero(groups == group)
        expected[indices] = talib.MAVP(price[indices], periods[indices], minperiod=1, maxperiod=30, matype=0)
    valid = ~actual.is_null().to_numpy()
    assert_exact(actual.to_numpy()[valid], expected[valid])
    if pattern == 'null':
        assert actual.is_null()[200]
        if grouped:
            assert not actual.filter(pl.Series(groups != groups[200])).is_null().any()
    else:
        assert actual.null_count() == 0


@pytest.mark.parametrize('minimum,maximum', [(0, 30), (30, 2), (2, 0), (2, 100001)])
def test_sma_rejections_keep_public_error_class(minimum, maximum):
    frame = pl.DataFrame({'close': [100.] * 64, 'periods': [14.] * 64})
    with pytest.raises(pl.exceptions.ComputeError, match='TA_BAD_PARAM'):
        frame.select(ta.mavp('close', 'periods', minperiod=minimum, maxperiod=maximum))


@pytest.mark.parametrize('mode', range(14))
@pytest.mark.parametrize('period', [2, 14, 128])
@pytest.mark.parametrize('grouped', [False, True])
def test_fixed_bounds_keep_every_public_ma_and_native_window_alignment(mode, period, grouped):
    n = 3072
    price = 100 + np.cumsum(np.random.default_rng(260126).normal(0, .01, n))
    periods = np.resize([-100., -0., 3.75, 1024.], n)
    groups = np.arange(n) % 3 if grouped else np.zeros(n, dtype=np.int64)
    frame = pl.DataFrame({'close': price, 'periods': periods, 'g': groups})
    expr = ta.mavp('close', 'periods', minperiod=period, maxperiod=period, matype=mode)
    if grouped:
        expr = expr.over('g')
    expected = np.empty(n)
    for group in np.unique(groups):
        ix = np.flatnonzero(groups == group)
        expected[ix] = talib.MAVP(price[ix], periods[ix], minperiod=period, maxperiod=period, matype=mode)
    for result in (frame.select(expr), frame.lazy().select(expr).collect()):
        actual = result.to_series()
        assert actual.dtype == pl.Float64 and actual.null_count() == 0 and len(actual) == n
        np.testing.assert_array_equal(np.isnan(actual.to_numpy()), np.isnan(expected))
        np.testing.assert_allclose(actual.to_numpy(), expected, rtol=1e-10, atol=1e-10, equal_nan=True)
        zeros = expected == 0
        np.testing.assert_array_equal(np.signbit(actual.to_numpy()[zeros]), np.signbit(expected[zeros]))
