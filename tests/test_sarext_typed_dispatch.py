"""SAREXT typed kwargs preserve original numerical/public window behavior."""
import numpy as np
import polars as pl
import polars_talib as ta
import pytest
import talib

KEYS = ('startvalue', 'offsetonreverse', 'accelerationinitlong', 'accelerationlong',
        'accelerationmaxlong', 'accelerationinitshort', 'accelerationshort', 'accelerationmaxshort')
PROFILES = [{}, dict(zip(KEYS, [-100., .01, .01, .03, .3, .04, .05, .4])),
            dict(zip(KEYS, [-100, 0, 1, 1, 1, 1, 1, 1])), dict.fromkeys(KEYS, -4e37)]


def expected(frame, params, grouped=False, ordered=False):
    groups = frame['g'].to_numpy() if grouped else np.zeros(frame.height, dtype=int)
    output = np.full(frame.height, np.nan)
    valid = np.ones(frame.height, dtype=bool)
    high, low = frame['high'].cast(pl.Float64).to_list(), frame['low'].cast(pl.Float64).to_list()
    for group in np.unique(groups):
        indices = np.flatnonzero(groups == group)
        if ordered:
            indices = indices[np.argsort(frame['_row'].to_numpy()[indices])]
        present = np.array([high[i] is not None and low[i] is not None for i in indices])
        a = np.array([np.nan if high[i] is None else high[i] for i in indices], dtype=np.float64)
        b = np.array([np.nan if low[i] is None else low[i] for i in indices], dtype=np.float64)
        begin = next((i for i in range(len(indices)) if present[i] and not np.isnan(a[i]) and not np.isnan(b[i])), len(indices))
        if begin < len(indices):
            output[indices[begin:]] = talib.SAREXT(a[begin:], b[begin:], **params)
            missing = np.flatnonzero(~present & (np.arange(len(indices)) > begin))
            if len(missing):
                valid[indices[missing[0]:]] = False
    return pl.Series('expected', output).set(pl.Series(~valid), None)


def assert_output(got, want):
    assert got.dtype == pl.Float64 and len(got) == len(want)
    np.testing.assert_array_equal(got.is_null().to_numpy(), want.is_null().to_numpy())
    a, b = got.fill_null(0).to_numpy(), want.fill_null(0).to_numpy()
    np.testing.assert_array_equal(np.isnan(a), np.isnan(b))
    np.testing.assert_array_equal(np.isposinf(a), np.isposinf(b))
    np.testing.assert_array_equal(np.isneginf(a), np.isneginf(b))
    finite = np.isfinite(b)
    np.testing.assert_allclose(a[finite], b[finite], rtol=1e-10, atol=1e-10)
    np.testing.assert_array_equal(a[b == 0].view(np.uint64), b[b == 0].view(np.uint64))


def check(frame, params, grouped=False, ordered=False):
    want = expected(frame, params, grouped, ordered)
    source = frame.rename({'high': 'source_high', 'low': 'source_low'})
    expressions = [ta.sarext('source_high', 'source_low', **params),
                   ta.sarext(pl.col('source_high'), pl.col('source_low'), **params),
                   ta.sarext(high='source_high', low='source_low', **params),
                   pl.col('source_high').ta.sarext('source_low', **params)]
    for expr in expressions:
        if grouped:
            expr = expr.over('g', order_by='_row') if ordered else expr.over('g')
        for result in [source.select(expr.alias('sar')).to_series(), source.lazy().select(expr.alias('sar')).collect().to_series()]:
            assert result.name == 'sar'
            assert_output(result, want)


def data(n, layout):
    high = 100. + np.resize([3., 1., 5., -1., 7., -3., 9., -5.], n)
    low = high - np.resize([2., 1., 4., 3., 2.], n)
    groups = np.zeros(n, dtype=int) if layout == 'dense' else np.arange(n) % 4 if layout == 'interleaved' else np.minimum(np.arange(n) // max((n+3)//4, 1), 3)
    frame = pl.DataFrame({'high': high, 'low': low, 'g': groups, '_row': np.arange(n)})
    return pl.concat([frame.slice(i, 17) for i in range(0, n, 17)], rechunk=False) if n else frame


@pytest.mark.parametrize('n', [0, 1, 2, 3, 33, 257, 10000])
@pytest.mark.parametrize('layout', ['dense', 'contiguous', 'interleaved'])
@pytest.mark.parametrize('params', PROFILES)
def test_all_defaults_nondefault_real_integer_and_sentinel_options_in_native_windows(n, layout, params):
    frame = data(n, layout)
    check(frame, params, layout != 'dense')
    if layout != 'dense' and n:
        check(frame.reverse(), params, True, ordered=True)


@pytest.mark.parametrize('role', ['high', 'low'])
@pytest.mark.parametrize('kind', ['leading_null', 'internal_null', 'all_null', 'leading_nan', 'internal_nan', 'all_nan', 'infinity', 'negative_infinity'])
@pytest.mark.parametrize('layout', ['dense', 'interleaved'])
def test_missing_and_ieee_inputs_preserve_masks_and_c_positions(role, kind, layout):
    frame = data(100, layout)
    values = frame[role].to_list()
    positions = range(100) if kind.startswith('all') else range(11) if kind.startswith('leading') else [39]
    value = None if kind.endswith('null') else np.nan if kind.endswith('nan') else -np.inf if kind.startswith('negative') else np.inf
    for i in positions:
        values[i] = value
    check(frame.with_columns(pl.Series(role, values, dtype=pl.Float64)), PROFILES[1], layout != 'dense')


@pytest.mark.parametrize('scalar', [None, np.nan, -0., 0., np.inf, -np.inf, 100.])
@pytest.mark.parametrize('role', ['high', 'low'])
@pytest.mark.parametrize('n', [0, 1, 100])
def test_scalar_inputs_keep_broadcast_prefix_and_recursive_masking(scalar, role, n):
    frame = data(n, 'dense')
    expression = ta.sarext(pl.lit(scalar), 'low') if role == 'high' else ta.sarext('high', pl.lit(scalar))
    expanded = frame.with_columns(pl.lit(scalar, dtype=pl.Float64).alias(role))
    want = expected(expanded, {})
    assert_output(frame.select(expression).to_series(), want)
    assert_output(frame.lazy().select(expression).collect().to_series(), want)


@pytest.mark.parametrize('dtype', [pl.Int8, pl.Int16, pl.Int32, pl.Int64, pl.UInt8, pl.UInt16, pl.UInt32, pl.UInt64, pl.Float32, pl.Float64])
def test_cast_inputs_and_default_expression(dtype):
    frame = data(100, 'dense').with_columns(pl.col('high').cast(dtype), pl.col('low').cast(dtype))
    check(frame, {})
    assert_output(frame.select(ta.sarext()).to_series(), expected(frame, {}))


def test_zero_store_compatibility_preserves_long_sign_and_cancellation_without_zero_inputs():
    fixtures = [
        ([2., 3., 4.], [-0., 1., 2.], {}),
        ([-0., -1., -2.], [-1., -2., -3.], {}),
        ([-1., -1., -1., -1.], [-2., -2., -2., -2.],
         {'startvalue': -2., 'accelerationinitshort': .5, 'accelerationshort': 0., 'accelerationmaxshort': .5}),
    ]
    for high, low, params in fixtures:
        frame = pl.DataFrame({'high': high, 'low': low, 'g': [0]*len(high), '_row': range(len(high))})
        check(frame, params)
    # This legitimate long output must remain negative zero after the fallback.
    got = pl.DataFrame({'high': fixtures[0][0], 'low': fixtures[0][1]}).select(ta.sarext()).to_series()
    assert got[1] == 0 and np.signbit(got[1])
    assert all(v != 0 for v in fixtures[2][0] + fixtures[2][1])
    got = pl.DataFrame({'high': fixtures[2][0], 'low': fixtures[2][1]}).select(ta.sarext(**fixtures[2][2])).to_series()
    assert got[2] == 0 and not np.signbit(got[2])


def test_all_three_bar_signed_zero_and_small_integer_states_match_c081_zero_signs():
    from itertools import product
    values = [-1., -0., 0., 1.]
    for inputs in product(values, repeat=6):
        high, low = np.array(inputs[:3]), np.array(inputs[3:])
        frame = pl.DataFrame({'high': high, 'low': low})
        expected = talib.SAREXT(high, low)
        result = frame.select(ta.sarext()).to_series()
        assert_output(result, pl.Series('expected', expected))


def test_compatibility_copy_retains_the_frozen_scalar_tokens_except_two_declared_stores():
    import hashlib
    import json
    import re
    from pathlib import Path
    root = Path(__file__).resolve().parents[1]
    manifest = json.loads((root/'scripts/sarext_legacy_provenance.json').read_text())
    source = (root/'src/sarext_legacy.rs').read_text()
    start = source.index('fn scalar(')
    end = source.index('{', start) + 1
    depth = 1
    while depth:
        depth += (source[end] == '{') - (source[end] == '}')
        end += 1
    scalar = source[start:end].replace('fn scalar(', 'fn sarext_impl_scalar(', 1).replace('core: &Core,', '&self,', 1).replace('Core::', 'Self::')
    scalar = re.sub(r'\bcore\s*\.', 'self.', scalar)
    assert scalar.count('outReal[outIdx] = 0.0 - sar;') == 2
    scalar = scalar.replace('outReal[outIdx] = 0.0 - sar;', 'outReal[outIdx] = -sar;')
    scalar = re.sub(r'/\*.*?\*/|//[^\n]*', '', scalar, flags=re.S)
    tokens = re.findall(r'"(?:\\.|[^"\\])*"|[A-Za-z_][A-Za-z_0-9]*|\d+(?:\.\d*)?(?:[eE][+-]?\d+)?|::|->|=>|==|!=|<=|>=|\+=|-=|&&|\|\||[^\s]', scalar)
    tokens = [value for i, value in enumerate(tokens) if not (value == ',' and i+1 < len(tokens) and tokens[i+1] in [')', ']', '}'])]
    assert len(tokens) == manifest['scalar_source_token_count']
    assert hashlib.sha256(json.dumps(tokens, separators=(',', ':')).encode()).hexdigest() == manifest['scalar_source_token_sha256']
    assert manifest['official_commit'] == '62021c1d14ef5499505af5547384cab509adf3fc'
    assert manifest['crate_checksum'] == '4da552ae932721218c73cf1124610b0ce3d5f27cc1a62342debd370cd161d922'
