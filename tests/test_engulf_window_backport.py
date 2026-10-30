"""Checked Engulf windows preserve the ordinary native expression contract."""
import numpy as np
import polars as pl
import polars_talib as ta
import pytest
import talib

ROLES = ('open', 'high', 'low', 'close')


def expected(frame, grouped, ordered=False):
    groups = frame['g'].to_numpy() if grouped else np.zeros(frame.height, dtype=int)
    result = np.zeros(frame.height, dtype=np.int32)
    valid = np.ones(frame.height, dtype=bool)
    for group in np.unique(groups):
        indices = np.flatnonzero(groups == group)
        if ordered:
            indices = indices[np.argsort(frame['_row'].to_numpy()[indices])]
        columns = [frame[c].to_list() for c in ROLES]
        present = np.array([all(values[i] is not None for values in columns) for i in indices])
        arrays = [np.array([np.nan if values[i] is None else values[i] for i in indices]) for values in columns]
        begin = next((i for i in range(len(indices)) if present[i] and all(not np.isnan(v[i]) for v in arrays)), len(indices))
        if begin < len(indices):
            result[indices[begin:]] = talib.CDLENGULFING(*[v[begin:] for v in arrays])
            for at in np.flatnonzero(~present):
                if at > begin:
                    valid[indices[at:at + 3]] = False
    return pl.Series('expected', result, dtype=pl.Int32).set(pl.Series(~valid), None)


def check(frame, grouped, ordered=False):
    want = expected(frame, grouped, ordered)
    renamed = frame.rename({c: 'source_' + c for c in ROLES})
    names = ['source_' + c for c in ROLES]
    expressions = [
        ta.cdlengulfing(*names),
        ta.cdlengulfing(**dict(zip(ROLES, names))),
        pl.col(names[0]).ta.cdlengulfing(*names[1:]),
    ]
    for expression in expressions:
        if grouped:
            expression = expression.over('g', order_by='_row') if ordered else expression.over('g')
        for got in (renamed.select(expression).to_series(), renamed.lazy().select(expression).collect().to_series()):
            assert got.dtype == pl.Int32 and len(got) == frame.height
            np.testing.assert_array_equal(got.is_null().to_numpy(), want.is_null().to_numpy())
            np.testing.assert_array_equal(got.fill_null(0).to_numpy(), want.fill_null(0).to_numpy())


def data(n, pattern, layout):
    open_ = np.resize([100., 101., 100., 102., 98., 104., 0., -0., np.nan, 1., -np.inf, np.inf, -np.inf, 1., 100., 101.], n)
    close = np.resize([101., 100., 102., 99., 103., 97., -0., 0., 1., np.nan, np.inf, -np.inf, 1., -np.inf, 101., 100.], n)
    if pattern == 'alternating':
        open_ = np.resize([101., 99., 103., 100.], n)
        close = np.resize([100., 102., 98., 101.], n)
    groups = np.zeros(n, dtype=int) if layout == 'dense' else np.arange(n) % 4 if layout == 'interleaved' else np.minimum(np.arange(n) // max((n + 3) // 4, 1), 3)
    return pl.DataFrame({'open': open_, 'high': np.full(n, 1000.), 'low': np.full(n, -1000.), 'close': close, 'g': groups, '_row': np.arange(n)})


@pytest.mark.parametrize('n', [0, 1, 2, 3, 20, 257, 10000])
@pytest.mark.parametrize('pattern', ['alternating', 'ieee'])
@pytest.mark.parametrize('layout', ['dense', 'contiguous', 'interleaved'])
def test_native_public_forms_and_group_windows_remain_exact(n, pattern, layout):
    frame = data(n, pattern, layout)
    if n:
        frame = pl.concat([frame.slice(i, 17) for i in range(0, n, 17)], rechunk=False)
    check(frame, layout != 'dense')
    if layout != 'dense' and n:
        check(frame.reverse(), True, ordered=True)


@pytest.mark.parametrize('role', ROLES)
@pytest.mark.parametrize('missing', ['leading_null', 'leading_nan', 'internal_null', 'internal_nan', 'infinity', 'all_null'])
@pytest.mark.parametrize('layout', ['dense', 'interleaved'])
def test_unused_ohlc_missing_data_keep_mask_and_integer_padding(role, missing, layout):
    frame = data(100, 'alternating', layout)
    values = frame[role].to_list()
    if missing == 'all_null':
        values = [None] * len(values)
    else:
        positions = range(9) if missing.startswith('leading') else [37]
        value = None if missing.endswith('null') else np.nan if missing.endswith('nan') else np.inf
        for i in positions:
            values[i] = value
    frame = frame.with_columns(pl.Series(role, values, dtype=pl.Float64))
    frame = pl.concat([frame.slice(i, 13) for i in range(0, frame.height, 13)], rechunk=False)
    check(frame, layout != 'dense')
