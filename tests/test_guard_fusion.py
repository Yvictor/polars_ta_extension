"""Causality at the guarded-call boundary, independent of its scan strategy."""
import numpy as np
import polars as pl
import polars_talib as ta
import pytest


def exact_fields(got, want):
    assert got.dtype == want.dtype
    assert len(got) == len(want)
    if isinstance(got.dtype, pl.Struct):
        assert got.struct.fields == want.struct.fields
        pairs = [(got.struct.field(f), want.struct.field(f)) for f in got.struct.fields]
    else:
        pairs = [(got, want)]
    for a, b in pairs:
        np.testing.assert_array_equal(a.is_null().to_numpy(), b.is_null().to_numpy())
        av, bv = a.fill_null(0).to_numpy(), b.fill_null(0).to_numpy()
        np.testing.assert_array_equal(np.isnan(av), np.isnan(bv))
        finite = ~np.isnan(av)
        np.testing.assert_array_equal(av[finite].view(np.uint64), bv[finite].view(np.uint64))


@pytest.mark.parametrize('name', ['var', 'stddev', 'correl', 'bbands', 'macd'])
@pytest.mark.parametrize('trigger', [2000., float('inf'), -float('inf'), float('nan')],
                         ids=['large', 'inf', 'negative_inf', 'nan'])
@pytest.mark.parametrize('grouped', [False, True], ids=['direct', 'native_over'])
@pytest.mark.parametrize('leading_missing', [False, True], ids=['finite_prefix', 'leading_null'])
def test_future_trigger_preserves_exact_completed_prefix(name, trigger, grouped, leading_missing):
    # Comparing with the independently evaluated truncated frame tests causality:
    # a future trigger must not switch the arithmetic of any earlier result.
    n = 192
    row = np.arange(n)
    x = 20. + np.sin(row) + row / 200.
    frame = pl.DataFrame({'row': row, 'close': x, 'open': x + np.cos(row) / 10.})
    if grouped:
        frame = pl.concat([frame.with_columns(pl.lit(g).alias('g')) for g in [0, 1]])
        frame = frame.sort('row', 'g')
    if leading_missing:
        frame = frame.with_columns(
            pl.when(pl.col('row') < 2).then(pl.lit(None, pl.Float64))
            .otherwise(pl.col(c)).alias(c) for c in ['close', 'open']
        )
    expression = getattr(ta, name)('close', 'open') if name == 'correl' else getattr(ta, name)('close')
    if grouped:
        expression = expression.over('g')
    expression = expression.alias('result')
    # CORREL's second input is an independent trigger path; all other families
    # have one input. Keep other groups finite to expose scatter/order mistakes.
    for column in ['close', 'open'] if name == 'correl' else ['close']:
        mask = pl.col('row') == 85
        if grouped:
            mask = mask & (pl.col('g') == 0)
        changed = frame.with_columns(
            pl.when(mask).then(pl.lit(trigger, pl.Float64))
            .otherwise(pl.col(column)).alias(column)
        )
        completed = changed['row'] < 85
        want = changed.filter(completed).select(expression)['result']
        got = changed.lazy().select(expression).collect()['result'].filter(completed)
        exact_fields(got, want)
