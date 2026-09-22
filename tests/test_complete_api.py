"""Every upstream indicator is exercised against the official 0.8.1 wheel."""
import inspect
import json
from pathlib import Path

import numpy as np
import polars as pl
import polars_talib as ta
import pytest
import talib

API = json.loads((Path(__file__).parents[1]/'scripts/api.json').read_text())


def frame(n=512, dtype=pl.Float64):
    rng = np.random.default_rng(26)
    close = 100 + rng.normal(0, .5, n).cumsum()
    return pl.DataFrame({'open': close-.1, 'high': close+1, 'low': close-1,
                         'close': close, 'volume': rng.uniform(100, 1000, n),
                         'periods': np.full(n, 5.)}).cast(dtype)


def column(name):
    return {'real': 'close', 'real0': 'close', 'real1': 'open'}.get(name, name)


def expr(spec):
    return getattr(ta, spec['name'])(*[pl.col(column(i)) for i in spec['inputs']]).alias('result')


def arrays(result):
    s = result.to_series()
    if isinstance(s.dtype, pl.Struct):
        return [s.struct.field(f).to_numpy() for f in s.struct.fields]
    return [s.to_numpy()]


@pytest.mark.parametrize('spec', API, ids=lambda f:f['name'])
@pytest.mark.parametrize('dtype', [pl.Float64, pl.Float32])
def test_all_indicators_match_upstream(spec, dtype):
    df=frame(dtype=dtype)
    actual=arrays(df.select(expr(spec)))
    expected=getattr(talib, spec['name'].upper())(*[df[column(i)].cast(pl.Float64).to_numpy() for i in spec['inputs']])
    expected = list(expected) if isinstance(expected,tuple) else [expected]
    assert len(actual)==len(expected)
    for got,want in zip(actual,expected):
        # Explicit FMA/compiler dispatch may differ by a few ulps across platforms.
        np.testing.assert_allclose(got,want,rtol=1e-10,atol=1e-10,equal_nan=True)


@pytest.mark.parametrize('spec', API, ids=lambda f:f['name'])
@pytest.mark.parametrize('n', [0,1,2,10])
def test_short_and_empty_preserve_length(spec,n):
    out=frame(n).select(expr(spec))
    assert out.height==n
    if n:
        expected=getattr(talib, spec['name'].upper())(*[frame(n)[column(i)].to_numpy() for i in spec['inputs']])
        expected=list(expected) if isinstance(expected,tuple) else [expected]
        for got,want in zip(arrays(out),expected):
            np.testing.assert_allclose(got,want,rtol=1e-10,atol=1e-10,equal_nan=True)


@pytest.mark.parametrize('spec', API, ids=lambda f:f['name'])
@pytest.mark.parametrize('missing',[None, float('nan')])
def test_all_missing_preserve_length_and_padding(spec,missing):
    df=frame(7).select(pl.all().fill_nan(missing))
    df=pl.DataFrame({c:[missing]*7 for c in df.columns},schema={c:pl.Float64 for c in df.columns})
    out=df.select(expr(spec))
    assert out.height==7
    for a,o in zip(arrays(out),spec['outputs']):
        assert np.isnan(a).all() if o['type']=='double' else (a==0).all()


@pytest.mark.parametrize('spec', API, ids=lambda f:f['name'])
def test_leading_nulls_chunks_lazy_and_groups(spec):
    df=frame(128)
    nulls=pl.DataFrame({c:[None]*3 for c in df.columns},schema=df.schema)
    df=pl.concat([nulls,df],rechunk=False)
    direct=df.select(expr(spec))
    lazy=df.lazy().select(expr(spec)).collect()
    assert direct.equals(lazy)
    grouped=pl.concat([df.with_columns(pl.lit('a').alias('g')),df.with_columns(pl.lit('b').alias('g'))])
    result=grouped.select(expr(spec).over('g'))
    assert result.height==2*df.height
    assert result.slice(0,df.height).equals(direct)
    assert result.slice(df.height).equals(direct)
    for got,want in zip(arrays(direct),arrays(frame(128).select(expr(spec)))):
        # Index-valued indicators keep positions relative to the first valid row.
        np.testing.assert_allclose(got[3:],want,rtol=1e-10,atol=1e-10,equal_nan=True)


def test_inventory_and_defaults():
    assert len(ta.get_functions())==201
    assert set(ta.get_functions())=={n.lower() for n in talib.get_functions()}
    for f in API:
        assert hasattr(pl.col('close').ta,f['name'])
        sig=inspect.signature(getattr(ta,f['name']))
        for p in f['params']:
            assert sig.parameters[p['name']].default==p['default'], (f['name'],p['name'])


@pytest.mark.parametrize('matype',list(ta.MA_Type))
def test_all_ma_types(matype):
    df=frame()
    got=df.select(ta.ma(timeperiod=20,matype=matype)).to_series().to_numpy()
    want=talib.MA(df['close'].to_numpy(),timeperiod=20,matype=int(matype))
    np.testing.assert_allclose(got,want,rtol=1e-10,atol=1e-10,equal_nan=True)


@pytest.mark.parametrize('spec',[f for f in API if any(p['name']=='timeperiod' for p in f['params'])],ids=lambda f:f['name'])
def test_invalid_period_reports_error(spec):
    with pytest.raises(pl.exceptions.ComputeError):
        frame(10).select(getattr(ta,spec['name'])(*[pl.col(column(i)) for i in spec['inputs']],timeperiod=-1))


@pytest.mark.parametrize('spec',[f for f in API if any(p['name']=='timeperiod' for p in f['params'])],ids=lambda f:f['name'])
@pytest.mark.parametrize('period',[2,5,31])
def test_nondefault_period_and_internal_nan(spec,period):
    df=frame(300).with_columns(pl.when(pl.int_range(pl.len())==200).then(float('nan')).otherwise(pl.col('close')).alias('close'))
    args=[pl.col(column(i)) for i in spec['inputs']]
    actual=arrays(df.select(getattr(ta,spec['name'])(*args,timeperiod=period)))
    expected=getattr(talib,spec['name'].upper())(*[df[column(i)].to_numpy() for i in spec['inputs']],timeperiod=period)
    expected=list(expected) if isinstance(expected,tuple) else [expected]
    for got,want in zip(actual,expected):
        np.testing.assert_allclose(got,want,rtol=1e-10,atol=1e-10,equal_nan=True)


@pytest.mark.parametrize('spec',[f for f in API if getattr(ta,f['name']).__module__.endswith('._generated')],ids=lambda f:f['name'])
def test_new_namespace_and_struct_metadata(spec):
    inputs=spec['inputs']
    primary='close' if 'close' in inputs else inputs[0]
    expression=getattr(pl.col(column(primary)).ta,spec['name'])(**{i:pl.col(column(i)) for i in inputs if i!=primary})
    df=frame()
    expected=df.select(expr(spec))
    actual=df.select(expression.alias('result'))
    assert actual.equals(expected)
    if len(spec['outputs'])>1:
        assert actual.to_series().struct.fields==ta.get_functions_output_struct()[spec['name']]


def test_scalar_inputs_broadcast_for_generated_and_legacy_plugins():
    df=frame(32)
    out=df.select(ta.ao(pl.col('high'),pl.lit(99.)))
    want=talib.AO(df['high'].to_numpy(),np.full(32,99.))
    np.testing.assert_allclose(out.to_series().to_numpy(),want,equal_nan=True)
    out=df.select(ta.add(pl.col('close'),pl.lit(1.)))
    np.testing.assert_allclose(out.to_series().to_numpy(),df['close'].to_numpy()+1.,equal_nan=True)


def test_mismatched_input_lengths_raise_for_generated_and_legacy_plugins():
    df=frame(32)
    for fn in (ta.ao, ta.add):
        with pytest.raises(pl.exceptions.ComputeError, match="lengths differ"):
            df.select(fn(pl.col('high'),pl.col('low').head(5)))


def test_skill_example_pipeline():
    bars=frame(64).with_columns(pl.lit('A').alias('symbol'),pl.int_range(pl.len()).alias('timestamp'))
    result=(bars.sort(['symbol','timestamp']).with_columns(
        ta.rsi(pl.col('close'),timeperiod=14).over('symbol').alias('rsi'),
        ta.macd(pl.col('close')).over('symbol').alias('macd'),
        ta.atr(pl.col('high'),pl.col('low'),pl.col('close')).over('symbol').alias('atr'),
    ).unnest('macd'))
    assert result.height==64
    assert {'rsi','macd','macdsignal','macdhist','atr'}<=set(result.columns)


def test_installed_wheel_contains_upstream_license():
    from importlib.metadata import distribution
    dist=distribution('polars-talib')
    licenses=[f for f in dist.files if f.name=='TA-Lib-LICENSE']
    assert len(licenses)==1
    assert dist.locate_file(licenses[0]).read_bytes()==(Path(__file__).parents[1]/'talib-sys/vendor/TA-Lib-LICENSE').read_bytes()


@pytest.mark.parametrize('spec', [f for f in API if len(f['inputs']) > 1], ids=lambda f: f['name'])
@pytest.mark.parametrize('scalar_first', [False, True])
def test_empty_columns_broadcast_scalars_in_either_position(spec, scalar_first):
    args = [pl.col(column(i)) for i in spec['inputs']]
    args[0 if scalar_first else -1] = pl.lit(1.)
    query = frame(8).lazy().filter(pl.lit(False)).select(getattr(ta, spec['name'])(*args))
    assert query.collect().height == 0


@pytest.mark.parametrize('fn', [ta.ao, ta.add])
@pytest.mark.parametrize('lengths', [(0, 2), (2, 0), (2, 3), (3, 2)])
def test_non_scalar_length_mismatch_in_either_position(fn, lengths):
    with pytest.raises(pl.exceptions.ComputeError, match='lengths differ'):
        frame(8).select(fn(pl.col('high').head(lengths[0]), pl.col('low').head(lengths[1])))


@pytest.mark.parametrize('fn', [ta.ema, ta.hma])
@pytest.mark.parametrize('value', [14.0, '14', None, True])
def test_integer_parameters_report_clear_errors(fn, value):
    with pytest.raises(TypeError, match='timeperiod must be an integer'):
        fn(timeperiod=value)


@pytest.mark.parametrize('fn', [ta.ema, ta.hma])
def test_numpy_integer_parameters_are_supported(fn):
    assert frame().select(fn(timeperiod=np.int64(14))).equals(frame().select(fn(timeperiod=14)))
    with pytest.raises(ValueError, match='signed 32-bit integer'):
        fn(timeperiod=2**40)
