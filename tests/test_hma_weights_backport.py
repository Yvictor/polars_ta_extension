"""HMA's bounded weight backport preserves C0.8.1 expression results."""
import numpy as np
import polars as pl
import polars_talib as ta
import pytest
import talib


def assert_exact(actual, expected):
    np.testing.assert_array_equal(actual, expected)
    valid = ~np.isnan(expected)
    np.testing.assert_array_equal(np.signbit(actual[valid]), np.signbit(expected[valid]))


def expected_groups(price, groups, period):
    expected = np.empty(len(price))
    for group in np.unique(groups):
        indices = np.flatnonzero(groups == group)
        expected[indices] = talib.HMA(price[indices], timeperiod=period)
    return expected


@pytest.mark.parametrize('period', [1, 2, 3, 4, 20, 2703, 2704, 100000])
@pytest.mark.parametrize('grouped', [False, True])
def test_hma_period_boundaries_remain_exact_in_native_expressions(period, grouped):
    bars = period + int(np.sqrt(period)) + 180
    n = bars * (3 if grouped else 1)
    price = 100. + np.cumsum(np.random.default_rng(260126).normal(0, .1, n))
    groups = np.arange(n) % 3 if grouped else np.zeros(n, dtype=np.int64)
    frame = pl.DataFrame({'close': price, 'g': groups})
    frame = pl.concat([frame.slice(i, 257) for i in range(0, n, 257)], rechunk=False)
    expr = ta.hma('close', timeperiod=period)
    if grouped:
        expr = expr.over('g')
    expected = expected_groups(price, groups, period)
    for actual in [frame.select(expr).to_series(), frame.lazy().select(expr).collect().to_series()]:
        assert actual.dtype == pl.Float64 and len(actual) == n and actual.null_count() == 0
        assert_exact(actual.to_numpy(), expected)


@pytest.mark.parametrize('pattern', ['zero', 'negative_zero', 'alternating', 'leading_nan',
                                     'internal_nan', 'head_inf', 'interior_negative_inf', 'null'])
@pytest.mark.parametrize('grouped', [False, True])
def test_hma_ieee_and_missing_inputs_keep_frozen_results(pattern, grouped):
    n = 1000
    price = 100. + np.sin(np.arange(n) * .13)
    if pattern == 'zero':
        price.fill(0.)
    elif pattern == 'negative_zero':
        price.fill(-0.)
    elif pattern == 'alternating':
        price = np.where(np.arange(n) % 2, -1e100, 1e100)
    elif pattern == 'leading_nan':
        price[:9] = np.nan
    elif pattern in ('internal_nan', 'null'):
        price[200] = np.nan
    elif pattern == 'head_inf':
        price[0] = np.inf
    elif pattern == 'interior_negative_inf':
        price[500] = -np.inf
    groups = np.arange(n) % 3 if grouped else np.zeros(n, dtype=np.int64)
    close = price.tolist()
    if pattern == 'null':
        close[200] = None
    frame = pl.DataFrame({'close': close, 'g': groups})
    expr = ta.hma(pl.col('close'), timeperiod=20)
    if grouped:
        expr = expr.over('g')
    actual = frame.lazy().select(expr).collect().to_series()
    expected = expected_groups(price, groups, 20)
    valid = ~actual.is_null().to_numpy()
    assert_exact(actual.to_numpy()[valid], expected[valid])
    if pattern == 'null':
        assert actual.is_null()[200]
        if grouped:
            assert not actual.filter(pl.Series(groups != groups[200])).is_null().any()
    else:
        assert actual.null_count() == 0


@pytest.mark.parametrize('period', [0, 100001])
def test_hma_invalid_periods_keep_public_error_class(period):
    frame = pl.DataFrame({'close': [100.] * 64})
    with pytest.raises(pl.exceptions.ComputeError, match='TA_BAD_PARAM'):
        frame.select(ta.hma('close', timeperiod=period))
