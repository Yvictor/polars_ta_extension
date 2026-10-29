"""Public call forms, independent of numerical kernel-only coverage."""
import numpy as np
import polars as pl
import polars_talib as ta
import talib


def test_aroon_column_name_regression():
    x = np.arange(40, dtype=float)
    df = pl.DataFrame({'high': x + np.sin(x) + 2, 'low': x - np.cos(x)})
    # Exact reported call: both names are ordinary column arguments.
    expression = ta.aroon('high', 'low').alias('aroon')
    got = df.lazy().select(expression).collect().to_series()
    assert got.struct.fields == ['aroondown', 'aroonup']
    assert got.dtype == pl.Struct({'aroondown': pl.Float64, 'aroonup': pl.Float64})
    expected = talib.AROON(df['high'].to_numpy(), df['low'].to_numpy())
    for field, want in zip(got.struct.fields, expected):
        np.testing.assert_allclose(got.struct.field(field).to_numpy(), want, equal_nan=True)

import importlib.util
import inspect
import json
from pathlib import Path
import pytest
from talib import abstract

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = json.loads((ROOT/'scripts/public_api_coverage.json').read_text())
SPECS = MANIFEST['functions']


def usage_frame(scenario='finite'):
    rng = np.random.default_rng(2901)
    n = 0 if scenario == 'empty' else 3 if scenario == 'short' else 192
    x = 20 + rng.normal(0, .2, n).cumsum()
    df = pl.DataFrame({'open': x-.1, 'high': x+1, 'low': x-1, 'close': x,
                       'volume': rng.uniform(100, 1000, n), 'periods': np.resize([3., 5., 9.], n)})
    if scenario in ('leading_null', 'internal_null', 'internal_nan'):
        mask = pl.int_range(pl.len()) < 2 if scenario == 'leading_null' else pl.int_range(pl.len()) == 37
        value = float('nan') if scenario == 'internal_nan' else None
        df = df.with_columns(pl.when(mask).then(pl.lit(value, pl.Float64)).otherwise(pl.col(c)).alias(c)
                             for c in df.columns if c != 'periods')
    if scenario == 'chunked':
        df = pl.concat([df.slice(i, 13) for i in range(0, n, 13)], rechunk=False)
        assert df['close'].n_chunks() > 1
    return df


def role_columns(spec):
    return [{'real':'close', 'real0':'high', 'real1':'low'}.get(r, r) for r in spec['roles']]


def invocation(name, form, params, columns):
    spec = SPECS[name]; fn = getattr(ta, name)
    args = [pl.col(c) for c in columns]
    if form == 'positional_names': return fn(*columns, **params)
    if form == 'positional_exprs': return fn(*args, **params)
    if form.startswith('keyword_'):
        return fn(**dict(zip(spec['inputs'], columns if form.endswith('names') else args)), **params)
    if form == 'mixed': return fn(columns[0], *args[1:], **params)
    if form == 'positional_parameters':
        return fn(*columns, *[params.get(p['name'], p['default']) for p in spec['parameters']])
    if form == 'defaults': return fn(**params)
    order = spec['namespace_role_order']
    receiver = columns[order[0]]
    rest = [columns[i] for i in order[1:]]
    method = getattr(ta.col(receiver) if form == 'typed_col' else pl.col(receiver).ta, name)
    if form == 'namespace_positional_parameters':
        defaults = {p['name']:p['default'] for p in spec['parameters']}
        return method(*rest, *[params.get(k, defaults[k]) for k in spec['namespace_parameter_order']])
    if form == 'namespace_keywords': return method(**dict(zip(spec['namespace_inputs'], rest)), **params)
    return method(*rest, **params)


def series_fields(series):
    return [series.struct.field(f) for f in series.struct.fields] if isinstance(series.dtype, pl.Struct) else [series]


def assert_exact(got, want):
    assert got.dtype == want.dtype
    assert len(got) == len(want)
    if isinstance(got.dtype, pl.Struct):
        assert got.struct.fields == want.struct.fields
    for a, b in zip(series_fields(got), series_fields(want)):
        np.testing.assert_array_equal(a.is_null().to_numpy(), b.is_null().to_numpy())
        av, bv = a.fill_null(0).to_numpy(), b.fill_null(0).to_numpy()
        np.testing.assert_array_equal(av, bv)
        use = ~np.isnan(av)
        np.testing.assert_array_equal(np.signbit(av[use]), np.signbit(bv[use]))


def check_official(name, df, columns, params, got):
    spec = SPECS[name]
    fields = series_fields(got)
    if spec['struct_fields']:
        assert got.struct.fields == spec['struct_fields']
    expected_types = [pl.Float64 if o['type'] == 'double' else pl.Int32 for o in spec['outputs']]
    assert [s.dtype for s in fields] == expected_types
    assert len(got) == df.height
    if not df.height: return  # Python binding rejects empty arrays for some functions.
    values = [df[c].fill_null(float('nan')).to_numpy() for c in columns]
    begin = next((i for i in range(df.height) if all(not np.isnan(v[i]) for v in values)), df.height)
    if begin == df.height:
        expected = [np.full(df.height, np.nan if t == pl.Float64 else 0) for t in expected_types]
    else:
        expected = getattr(talib, name.upper())(*[v[begin:] for v in values], **params)
        expected = expected if isinstance(expected, tuple) else (expected,)
        expected = [np.concatenate([np.full(begin, np.nan if t == pl.Float64 else 0), a]) for a, t in zip(expected, expected_types)]
    for field, want in zip(fields, expected):
        actual = field.to_numpy(); valid = ~field.is_null().to_numpy()
        np.testing.assert_array_equal(np.isnan(actual[valid]), np.isnan(want[valid]))
        np.testing.assert_allclose(actual[valid], want[valid], rtol=1e-10, atol=1e-10, equal_nan=True)
        zeros = valid & (actual == 0) & (want == 0)
        np.testing.assert_array_equal(np.signbit(actual[zeros]), np.signbit(want[zeros]))


@pytest.mark.parametrize('name', sorted(SPECS))
@pytest.mark.parametrize('nondefault', [False, True], ids=['default_params','nondefault_params'])
@pytest.mark.parametrize('scenario', MANIFEST['functions']['aroon']['scenarios'])
def test_every_function_public_forms(name, nondefault, scenario):
    spec = SPECS[name]; params = spec['nondefault'] if nondefault else {}
    df = usage_frame(scenario)
    columns = role_columns(spec)
    if scenario == 'interleaved_over':
        # Unequal, interleaved groups; original row order within each group is preserved.
        df = df.with_columns((pl.int_range(pl.len()) % 5).alias('g'))
        expected = df.with_row_index('_row').partition_by('g', maintain_order=True)
        parts = [d.select('_row', invocation(name, 'positional_exprs', params, columns).alias('result')) for d in expected]
        reference = pl.concat(parts).sort('_row')['result']
    else:
        reference = df.select(invocation(name, 'positional_exprs', params, columns).alias('result'))['result']
        check_official(name, df, columns, params, reference)
    # Default column names may differ from explicit role columns (legacy price/price0/price1).
    # Verify defaults against the actual frozen default-column mapping separately.
    for form in spec['forms']:
        if form == 'defaults':
            call_df = df
            expression = invocation(name, form, params, columns)
            if scenario == 'interleaved_over':
                default_parts = [d.select('_row', invocation(name, 'positional_exprs', params, spec['default_columns']).alias('result')) for d in expected]
                want = pl.concat(default_parts).sort('_row')['result']
            else:
                want = df.select(invocation(name, 'positional_exprs', params, spec['default_columns']).alias('result'))['result']
                check_official(name, df, spec['default_columns'], params, want)
        else:
            # Rename columns to expose wrappers that accidentally use default names.
            renamed = {c: 'source_'+c for c in df.columns if c != 'g'}
            call_df = df.rename(renamed)
            expression = invocation(name, form, params, [renamed[c] for c in columns])
            want = reference
        expression = expression.alias('result')
        if scenario == 'interleaved_over': expression = expression.over('g')
        eager = call_df.select(expression)['result']
        lazy = call_df.lazy().select(expression).collect()['result']
        try:
            assert_exact(eager, want)
        except AssertionError as e:
            raise AssertionError(f"{name}/{scenario}/{form}/{params}: {e}") from e
        assert_exact(lazy, want)


@pytest.mark.parametrize('name', sorted(SPECS))
def test_each_public_signature_metadata_and_invalid_calls(name):
    spec = SPECS[name]; fn = getattr(ta, name); sig = inspect.signature(fn)
    assert list(sig.parameters) == spec['inputs'] + [p['name'] for p in spec['parameters']]
    assert list(inspect.signature(getattr(ta.TAExpr, name)).parameters) == ['self'] + spec['namespace_inputs'] + spec['namespace_parameter_order']
    for param in spec['parameters']:
        assert sig.parameters[param['name']].default == param['default']
    info = abstract.Function(name.upper()).info
    assert dict(info['parameters']) == {p['name']: p['default'] for p in spec['parameters']}
    roles = [v for value in info['input_names'].values() for v in (value if isinstance(value, list) else [value])]
    assert len(roles) == len(spec['roles'])
    assert info['output_names'] == (spec['struct_fields'] or [spec['outputs'][0]['name']])
    with pytest.raises(TypeError): fn(unknown_indicator_option=1)
    with pytest.raises(TypeError): fn(*([pl.col('close')] * (len(sig.parameters)+1)))
    with pytest.raises(pl.exceptions.ColumnNotFoundError):
        usage_frame().select(fn(*(['missing_column']*len(spec['inputs']))))
    if len(spec['inputs']) > 1:
        args = [pl.col(c) for c in role_columns(spec)]; args[-1] = args[-1].head(5)
        with pytest.raises(pl.exceptions.ComputeError, match='lengths differ'):
            usage_frame().select(fn(*args))
    for p in spec['parameters']:
        with pytest.raises((TypeError, ValueError)):
            usage_frame().select(fn(**{p['name']: 'invalid_numeric_parameter'}))


def test_public_coverage_inventory_cannot_silently_omit_exports():
    assert set(SPECS) == set(ta.get_functions()) == {n.lower() for n in talib.get_functions()}
    public = {n for n, v in vars(ta).items() if not n.startswith('_') and inspect.isfunction(v)}
    assert public - set(MANIFEST['helpers_excluded']) == set(SPECS)
    path = ROOT/'scripts/generate_usage_manifest.py'
    module_spec = importlib.util.spec_from_file_location('usage_generator', path)
    module = importlib.util.module_from_spec(module_spec); module_spec.loader.exec_module(module)
    assert module.generate() == MANIFEST
    for spec in SPECS.values():
        assert spec['forms'] == module.FORMS
        assert spec['scenarios'] == module.SCENARIOS


@pytest.mark.parametrize('name', sorted(SPECS))
def test_series_array_and_scalar_input_forms(name):
    df = usage_frame(); spec = SPECS[name]; columns = role_columns(spec)
    fn = getattr(ta, name)
    reference = df.select(invocation(name, 'positional_exprs', {}, columns).alias('result'))['result']
    for values in ([df[c] for c in columns], [df[c].to_numpy() for c in columns]):
        actual = df.select(fn(*values).alias('result'))['result']
        assert_exact(actual, reference)
    values = [pl.col(c) for c in columns]
    values[0] = pl.lit(20.)
    reference = df.select(fn(*values).alias('result'))['result']
    values[0] = 20.
    assert_exact(df.select(fn(*values).alias('result'))['result'], reference)


@pytest.mark.parametrize('name', sorted(SPECS))
def test_namespace_default_columns_and_invalid_call_forms(name):
    spec = SPECS[name]; df = usage_frame()
    receiver = role_columns(spec)[spec['namespace_role_order'][0]]
    method = getattr(pl.col(receiver).ta, name)
    # Namespace defaults are independently inspected; receiver conventions differ.
    sig = inspect.signature(getattr(ta.TAExpr, name))
    with pytest.raises(TypeError): method(unknown_indicator_option=1)
    with pytest.raises(TypeError): method(*([pl.col('close')] * len(sig.parameters)))
    if not spec['namespace_defaults_applicable']:
        with pytest.raises(TypeError): method()
        return
    columns = [receiver]
    for key in spec['namespace_inputs']:
        default = sig.parameters[key].default
        columns.extend(default.meta.root_names())
    native_order = [columns[i] for i in np.argsort(spec['namespace_role_order'])]
    reference = df.select(invocation(name, 'positional_exprs', {}, native_order).alias('result'))['result']
    actual = df.select(method().alias('result'))['result']
    assert_exact(actual, reference)
    check_official(name, df, native_order, {}, actual)
    with pytest.raises(TypeError): method(unknown_indicator_option=1)
    with pytest.raises(TypeError): method(*([pl.col('close')] * len(sig.parameters)))
