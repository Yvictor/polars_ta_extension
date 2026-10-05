"""Null inputs never become indicator values (issue #42).

A Polars null is a missing observation. Rows that can depend on a null input
after the first usable row are null: to the end of the partition for recursive
indicators, for `lookback` rows for window-bounded ones. Every other row is
unchanged. Under `.over(...)` and `group_by(...).agg(...)` this holds per
partition: a null in one partition never changes another partition. NaN and
infinity are ordinary float values and reach TA-Lib unchanged.
"""
import importlib.util
import json
from pathlib import Path

import numpy as np
import polars as pl
import polars_talib as ta
import pytest
import talib
import talib.abstract
from polars_talib._missing import WINDOW_BOUNDED
from polars_talib._polars_talib import lookback

ROOT = Path(__file__).parents[1]
API = json.loads((ROOT / 'scripts/api.json').read_text())
_spec = importlib.util.spec_from_file_location('classify_missing', ROOT / 'scripts/classify_missing.py')
classify = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(classify)
N, K = classify.N, classify.K


def run(df, name, **kwargs):
    args = [pl.col(classify.column(i, name)) for i in classify.API[name]['inputs']]
    s = df.select(getattr(ta, name)(*args, **kwargs).alias('r')).to_series()
    return [s.struct.field(f) for f in s.struct.fields] if isinstance(s.dtype, pl.Struct) else [s]


def expected_mask(name, kwargs=None, k=K, n=N):
    rows = np.arange(n)
    if name in WINDOW_BOUNDED:
        return (rows >= k) & (rows <= k + lookback(name, kwargs or None))
    return rows >= k


def same(a, b):
    a, b = (np.asarray(x.cast(pl.Float64).to_numpy(), dtype=float) for x in (a, b))
    return (np.isnan(a) & np.isnan(b)) | (a == b)


def test_issue_42_rsi_after_null():
    df = pl.DataFrame({'close': [100.0, 101.0, 103.0, None, 105.0, 107.0, 106.0]})
    out = df.select(ta.rsi(pl.col('close'), timeperiod=2)).to_series()
    assert out.is_null().to_list() == [False, False, False, True, True, True, True]
    assert out.head(3).to_numpy()[2] == 100.0 and np.isnan(out.head(2).to_numpy()).all()
    assert df.select(pl.col('close').ta.rsi(2)).to_series().equals(out)
    # NaN is a value, not a missing observation: it reaches TA-Lib unchanged...
    nan = df.with_columns(pl.col('close').fill_null(float('nan')))
    raw = nan.select(ta.rsi(pl.col('close'), timeperiod=2)).to_series()
    assert raw.null_count() == 0
    np.testing.assert_array_equal(raw.to_numpy(), talib.RSI(nan['close'].to_numpy(), timeperiod=2))
    # ...and `fill_nan(None)` declares it missing.
    assert nan.select(ta.rsi(pl.col('close').fill_nan(None), timeperiod=2)).to_series().equals(out)


def test_window_bounded_classification_is_current():
    import polars_talib.utils as utils
    try:
        measured = set(classify.classify())
    finally:
        utils.MASK_MISSING = True  # classify() measures raw TA-Lib output
    assert measured == set(WINDOW_BOUNDED), 'run scripts/classify_missing.py and review the change'


@pytest.mark.parametrize('spec', API, ids=lambda f: f['name'])
def test_lookback_matches_upstream(spec):
    name = spec['name']
    assert lookback(name, None) == talib.abstract.Function(name.upper()).lookback
    params = {p['name']: (5 if 'period' in p['name'] and p['type'] != 'double' else p['default'])
              for p in spec['params']}
    try:
        want = talib.abstract.Function(name.upper(), **params).lookback
    except Exception:
        return
    assert lookback(name, params) == want


@pytest.mark.parametrize('spec', API, ids=lambda f: f['name'])
def test_null_input_nulls_exactly_the_dependent_rows(spec):
    name = spec['name']
    df = classify.frame()
    clean = run(df, name)
    missing = run(classify.with_row(df, value=None), name)
    dependent = [~(same(c, u) & same(c, d)) for c, u, d in
                 zip(clean, run(classify.with_row(df, 1.3), name), run(classify.with_row(df, 0.7), name))]
    mask = expected_mask(name)
    for c, m, dep in zip(clean, missing, dependent):
        assert m.is_null().to_numpy().tolist() == mask.tolist()
        assert not (dep & ~mask).any(), 'a row depending on the null input escaped the mask'
        assert same(c, m)[~mask].all(), 'a row outside the mask changed'


@pytest.mark.parametrize('kind', [float('nan'), float('inf'), float('-inf')], ids=['nan', 'inf', '-inf'])
@pytest.mark.parametrize('spec', API, ids=lambda f: f['name'])
def test_non_finite_values_reach_talib_unchanged(spec, kind):
    import polars_talib.utils as utils
    df = classify.with_row(classify.frame(), value=kind)
    masked = run(df, spec['name'])
    try:
        utils.MASK_MISSING = False
        raw = run(df, spec['name'])
    finally:
        utils.MASK_MISSING = True
    for m, r in zip(masked, raw):
        assert m.null_count() == 0 and m.equals(r)


@pytest.mark.parametrize('kind', [None, float('nan')], ids=['null', 'nan'])
@pytest.mark.parametrize('column', ['open', 'high', 'low', 'close', 'volume'])
def test_missing_value_in_any_single_input(column, kind):
    df = classify.frame().with_columns(
        pl.when(pl.int_range(pl.len()) == K).then(pl.lit(kind, pl.Float64)).otherwise(pl.col(column)).alias(column))
    for name in ('obv', 'atr', 'willr', 'supertrend', 'cdlengulfing', 'macd', 'ad'):
        inputs = {classify.column(i, name) for i in classify.API[name]['inputs']}
        expected = expected_mask(name) if kind is None and column in inputs else np.zeros(N, dtype=bool)
        for field in run(df, name):
            assert field.is_null().to_numpy().tolist() == expected.tolist(), (name, column)


def test_struct_outputs_mask_fields_not_rows():
    df = classify.with_row(classify.frame(), value=None)
    out = df.select(ta.macd().alias('m'), ta.supertrend().alias('s'))
    assert out['m'].is_null().sum() == 0 and out['s'].is_null().sum() == 0
    for col, field in (('m', 'macd'), ('m', 'macdsignal'), ('s', 'supertrend'), ('s', 'trend')):
        assert out[col].struct.field(field).is_null().to_numpy().tolist() == (np.arange(N) >= K).tolist()
    assert out['s'].struct.field('trend').dtype == pl.Int32


def test_leading_missing_rows_keep_warm_up_values():
    df = pl.DataFrame({'close': [None, float('nan'), 100.0, 101.0, 103.0, 102.0, 104.0]})
    out = df.select(ta.rsi(timeperiod=2)).to_series()
    assert out.null_count() == 0  # leading rows are warm-up NaN, as before
    values = out.to_numpy()
    assert np.isnan(values[:4]).all() and np.isfinite(values[4:]).all()


def test_all_missing_and_empty_inputs():
    assert pl.DataFrame({'close': [None] * 5}, schema={'close': pl.Float64}).select(ta.rsi(timeperiod=2)).height == 5
    assert pl.DataFrame({'close': []}, schema={'close': pl.Float64}).select(ta.rsi(timeperiod=2)).height == 0


# --- partitions -------------------------------------------------------------

# name -> (TA-Lib function, parameters, inputs, expression)
CASES = {
    'rsi': ('rsi', {'timeperiod': 5}, ['close'], lambda: ta.rsi(pl.col('close'), timeperiod=5)),       # recursive
    'ema': ('ema', {'timeperiod': 5}, ['close'], lambda: pl.col('close').ta.ema(5)),                   # namespace
    'willr': ('willr', {'timeperiod': 5}, ['high', 'low', 'close'], lambda: ta.willr(timeperiod=5)),   # window
    'obv': ('obv', {}, ['close', 'volume'], lambda: ta.obv()),                                         # path-dependent
    'macd': ('macd', {'fastperiod': 3, 'slowperiod': 6, 'signalperiod': 2}, ['close'],
             lambda: ta.macd(fastperiod=3, slowperiod=6, signalperiod=2)),                             # struct
    'aroon': ('aroon', {'timeperiod': 5}, ['high', 'low'], lambda: ta.aroon(timeperiod=5)),            # struct, window
    'supertrend': ('supertrend', {'timeperiod': 5}, ['high', 'low', 'close'],
                   lambda: ta.supertrend(timeperiod=5)),                                               # Float64 + Int32
    'cdlengulfing': ('cdlengulfing', {}, ['open', 'high', 'low', 'close'], lambda: ta.cdlengulfing()), # Int32 pattern
}
INDICATORS = {key: case[3] for key, case in CASES.items()}


def policy_nulls(part, key):
    """Independent restatement of the policy for one partition."""
    function, params, inputs, _ = CASES[key]
    null = part.select(pl.any_horizontal(pl.col(c).is_null() for c in inputs)).to_series().to_numpy()
    nan = part.select(pl.any_horizontal(pl.col(c).is_nan() for c in inputs)).to_series().fill_null(False).to_numpy()
    rows = np.arange(len(part))
    usable = np.nonzero(~null & ~nan)[0]  # the wrappers start here; earlier rows are warm-up
    nulls = np.zeros(len(part), dtype=bool)
    if not len(usable):
        return nulls
    lb = lookback(function, params or None)
    for k in rows[null & (rows > usable[0])]:
        nulls |= (rows >= k) if function not in WINDOW_BOUNDED else ((rows >= k) & (rows <= k + lb))
    return nulls


def null_rows(series):
    if isinstance(series.dtype, pl.Struct):
        fields = [series.struct.field(f).is_null().to_numpy() for f in series.struct.fields]
        assert all((f == fields[0]).all() for f in fields)
        return fields[0]
    return series.is_null().to_numpy()


def panel(nulls, n=40, interleave=False):
    """Three symbols; `nulls` maps symbol -> {column: [rows]} (None) or NaN via '<col>_nan'."""
    rng = np.random.default_rng(42)
    parts = []
    for sym in ('A', 'B', 'C'):
        close = 100 + rng.normal(0, 1, n).cumsum()
        open_ = np.r_[close[0], close[:-1]] + rng.normal(0, 0.5, n)
        part = pl.DataFrame({'sym': [sym] * n, 'day': np.arange(n), 'open': open_,
                             'high': np.maximum(open_, close) + 0.5, 'low': np.minimum(open_, close) - 0.5,
                             'close': close, 'volume': rng.uniform(100, 1000, n),
                             'session': np.arange(n) // 20})
        for column, rows in nulls.get(sym, {}).items():
            col, _, kind = column.partition('_')
            value = float('nan') if kind == 'nan' else None
            part = part.with_columns(pl.when(pl.col('day').is_in(rows)).then(pl.lit(value, pl.Float64))
                                     .otherwise(pl.col(col)).alias(col))
        parts.append(part)
    df = pl.concat(parts)
    return df.sort('day', 'sym') if interleave else df


def alone(df, make, keys=('sym',)):
    """Compute each partition on its own frame, then restore the panel's row order."""
    df = df.with_row_index('_row')
    parts = [g.select('_row', make().alias('v')) for _, g in df.group_by(list(keys), maintain_order=True)]
    return pl.concat(parts).sort('_row')['v']


NULL_LAYOUTS = {
    'interior': {'A': {'close': [10]}, 'C': {'high': [30], 'volume': [31]}},
    'nan-values-are-not-missing': {'A': {'close_nan': [12]}, 'B': {'low_nan': [25]}},
    'null-inside-nan-warm-up': {'A': {'close_nan': [0, 1], 'close': [2]}, 'C': {'close': [15]}},
    'last-row-before-next-partition': {'A': {'close': [39], 'high': [39], 'low': [39], 'open': [39]}},
    'leading-and-interior': {'A': {'close': [0, 1]}, 'B': {'close': [0, 20]}},
    'every-row-of-one-partition': {'B': {c: list(range(40)) for c in ('open', 'high', 'low', 'close', 'volume')}},
}


@pytest.mark.parametrize('interleave', [False, True], ids=['sorted', 'interleaved'])
@pytest.mark.parametrize('layout', NULL_LAYOUTS, ids=list(NULL_LAYOUTS))
@pytest.mark.parametrize('name', INDICATORS)
def test_over_masks_within_each_partition(name, layout, interleave):
    df = panel(NULL_LAYOUTS[layout], interleave=interleave)
    make = INDICATORS[name]
    over = df.select(make().over('sym').alias('v'))['v']
    assert over.equals(alone(df, make)), 'over() differs from computing each partition alone'
    clean = panel({}, interleave=interleave)
    clean_over = clean.select(make().over('sym').alias('v'))['v']
    untouched = ~df['sym'].is_in(list(NULL_LAYOUTS[layout]))
    assert over.filter(untouched).equals(clean_over.filter(untouched)), 'a null leaked into another partition'
    indexed = df.with_row_index('_row').with_columns(over.alias('v'))
    for _, part in indexed.group_by('sym', maintain_order=True):
        assert null_rows(part['v']).tolist() == policy_nulls(part, name).tolist()


@pytest.mark.parametrize('name', INDICATORS)
def test_group_by_agg_lazy_and_streaming_match_over(name):
    df = panel(NULL_LAYOUTS['interior'], interleave=True)
    make = INDICATORS[name]
    eager = df.select(make().over('sym').alias('v'))['v']
    query = df.lazy().select(make().over('sym').alias('v'))
    assert query.collect()['v'].equals(eager)
    try:
        streamed = query.collect(engine='streaming')
    except ValueError:  # Polars < 1.23 selects streaming with a flag
        streamed = query.collect(streaming=True)
    assert streamed['v'].equals(eager)
    agg = df.group_by('sym', maintain_order=True).agg(make().alias('v'), pl.col('day'))
    for sym, values, days in agg.iter_rows():
        part = df.filter(pl.col('sym') == sym)
        assert pl.Series('v', values, dtype=eager.dtype).equals(alone(part, make).rename('v'))
        assert days == part['day'].to_list()


@pytest.mark.parametrize('name', INDICATORS)
def test_over_multiple_keys_and_segment_restart(name):
    df = panel(NULL_LAYOUTS['interior'])
    make = INDICATORS[name]
    multi = df.select(make().over('sym', 'session').alias('v'))['v']
    assert multi.equals(alone(df, make, keys=('sym', 'session')))
    # Documented opt-in policy: restart the indicator after each gap.
    segment = pl.col('close').is_null().cum_sum()
    restarted = df.select(make().over('sym', segment).alias('v'))['v']
    keyed = df.with_columns(segment.over('sym').alias('_seg'))
    assert restarted.equals(alone(keyed, make, keys=('sym', '_seg')))


def test_readme_missing_values_example():
    import re
    block = re.search(r"### missing values.*?``` python\n(.*?)```", (ROOT / 'README.md').read_text(), re.S).group(1)
    df = panel(NULL_LAYOUTS['interior']).rename({'day': 'date', 'sym': 'symbol'})
    scope = {'pl': pl, 'df': df}
    exec(block, scope)
    out = scope['df']
    assert out.height == df.height
    for symbol, part in out.group_by('symbol', maintain_order=True):
        assert part['rsi_observed'].is_null().to_list() == part['close'].is_null().to_list()
        if symbol[0] == 'B':
            assert part['rsi_restart'].null_count() == 0
