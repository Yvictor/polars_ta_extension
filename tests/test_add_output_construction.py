"""ADD output construction preserves public values, masks and native windows."""
import numpy as np
import polars as pl
import polars_talib as ta
import pytest
import talib


def reference(frame, grouped=False, ordered=False):
    groups = frame['g'].to_numpy() if grouped else np.zeros(frame.height, dtype=np.int64)
    output = np.full(frame.height, np.nan)
    valid = np.ones(frame.height, dtype=bool)
    for group in np.unique(groups):
        indices = np.flatnonzero(groups == group)
        if ordered:
            indices = indices[np.argsort(frame['_row'].to_numpy()[indices])]
        left = frame['left'].cast(pl.Float64).to_list()
        right = frame['right'].cast(pl.Float64).to_list()
        present = np.array([left[i] is not None and right[i] is not None for i in indices])
        a = np.array([np.nan if left[i] is None else left[i] for i in indices], dtype=np.float64)
        b = np.array([np.nan if right[i] is None else right[i] for i in indices], dtype=np.float64)
        begin = next((i for i in range(len(indices)) if present[i] and not np.isnan(a[i]) and not np.isnan(b[i])), len(indices))
        if begin < len(indices):
            output[indices[begin:]] = talib.ADD(a[begin:], b[begin:])
            valid[indices[begin:]] = present[begin:]
    return pl.Series('expected', output).set(pl.Series(~valid), None)


def assert_output(got, want):
    assert got.dtype == pl.Float64 and len(got) == len(want)
    np.testing.assert_array_equal(got.is_null().to_numpy(), want.is_null().to_numpy())
    a, b = got.fill_null(0).to_numpy(), want.fill_null(0).to_numpy()
    np.testing.assert_array_equal(a, b)
    finite_or_inf = ~np.isnan(b)
    np.testing.assert_array_equal(a[finite_or_inf].view(np.uint64), b[finite_or_inf].view(np.uint64))


def check(frame, grouped=False, ordered=False):
    want = reference(frame, grouped, ordered)
    expressions = [ta.add('left', 'right'), ta.add(pl.col('left'), pl.col('right')),
                   ta.add(real0='left', real1='right'), pl.col('left').ta.add('right')]
    for expr in expressions:
        if grouped:
            expr = expr.over('g', order_by='_row') if ordered else expr.over('g')
        for result in [frame.select(expr.alias('sum')).to_series(), frame.lazy().select(expr.alias('sum')).collect().to_series()]:
            assert result.name == 'sum'
            assert_output(result, want)


def data(n, layout):
    left = np.resize([np.nan, np.nan, -0., 0., -0., 1., -1., np.inf, -np.inf, 1e308, -1e308, 5e-324, np.nan], n)
    right = np.resize([np.nan, 1., -0., -0., 0., -1., 1., -np.inf, np.inf, 1e308, -1e308, -5e-324, 2.], n)
    group = np.zeros(n, dtype=int) if layout == 'dense' else np.arange(n) % 4 if layout == 'interleaved' else np.minimum(np.arange(n) // max((n+3)//4, 1), 3)
    frame = pl.DataFrame({'left': left, 'right': right, 'g': group, '_row': np.arange(n)})
    return pl.concat([frame.slice(i, 17) for i in range(0, n, 17)], rechunk=False) if n else frame


@pytest.mark.parametrize('n', [0, 1, 2, 3, 33, 257, 10000])
@pytest.mark.parametrize('layout', ['dense', 'contiguous', 'interleaved'])
def test_ieee_values_public_forms_and_native_windows(n, layout):
    frame = data(n, layout)
    check(frame, layout != 'dense')
    if layout != 'dense' and n:
        check(frame.reverse(), True, ordered=True)


@pytest.mark.parametrize('role', ['left', 'right'])
@pytest.mark.parametrize('kind', ['leading_null', 'all_null', 'internal_null', 'leading_nan', 'all_nan', 'internal_nan'])
@pytest.mark.parametrize('layout', ['dense', 'interleaved'])
def test_null_mask_and_leading_prefix_are_preserved(role, kind, layout):
    frame = data(100, layout)
    values = frame[role].to_list()
    positions = range(100) if kind.startswith('all') else range(11) if kind.startswith('leading') else [39]
    for i in positions:
        values[i] = None if kind.endswith('null') else np.nan
    frame = frame.with_columns(pl.Series(role, values, dtype=pl.Float64))
    check(frame, layout != 'dense')


@pytest.mark.parametrize('scalar', [None, np.nan, -0., 0., np.inf, -np.inf, 3.])
@pytest.mark.parametrize('side', ['left', 'right'])
@pytest.mark.parametrize('n', [0, 1, 100])
def test_scalar_inputs_broadcast_with_the_same_prefix_and_null_policy(scalar, side, n):
    frame = data(n, 'dense')
    counterpart = 'right' if side == 'left' else 'left'
    expression = ta.add(pl.lit(scalar), counterpart) if side == 'left' else ta.add(counterpart, pl.lit(scalar))
    expanded = frame.with_columns(pl.lit(scalar, dtype=pl.Float64).alias(side))
    want = reference(expanded)
    assert_output(frame.select(expression).to_series(), want)
    assert_output(frame.lazy().select(expression).collect().to_series(), want)


@pytest.mark.parametrize('dtype', [pl.Int8, pl.Int16, pl.Int32, pl.Int64, pl.UInt8, pl.UInt16, pl.UInt32, pl.UInt64, pl.Float32, pl.Float64])
def test_cast_inputs_and_default_columns(dtype):
    if dtype.is_float():
        values = [0., -0., 1., -1., np.nan, np.inf]
    elif dtype in [pl.UInt8, pl.UInt16, pl.UInt32, pl.UInt64]:
        values = [0, 1, 2, 3, 100, 200]
        if dtype == pl.UInt64:
            values[-2:] = [2**53+1, 2**64-1]
    else:
        values = [0, 1, -1, -2, 100, -100]
        if dtype == pl.Int64:
            values[-2:] = [2**53+1, -2**63]
    frame = pl.DataFrame({'left': pl.Series(values, dtype=dtype), 'right': pl.Series(values[::-1], dtype=dtype), 'g': [0]*6, '_row': range(6)})
    check(frame)
    defaults = frame.rename({'left': 'high', 'right': 'low'})
    assert_output(defaults.select(ta.add()).to_series(), reference(frame))


def test_invalid_input_type_remains_an_error():
    with pytest.raises(pl.exceptions.ComputeError):
        pl.DataFrame({'left': ['a', 'b'], 'right': [1., 2.]}).select(ta.add('left', 'right'))
