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
