"""Keep semantic exceptions visible and independent of numeric tolerances."""
import importlib.util
import json
from pathlib import Path
import numpy as np
import polars as pl
import polars_talib as ta
import talib
import pytest

ROOT=Path(__file__).parents[1]
_spec=importlib.util.spec_from_file_location('migration_probe',ROOT/'scripts/migration_probe.py')
probe=importlib.util.module_from_spec(_spec);_spec.loader.exec_module(probe)
INFINITY=json.loads((ROOT/'tests/data/infinity-semantics.json').read_text())


def runs(values):
    code=np.where(np.isnan(values),1,np.where(np.isposinf(values),2,np.where(np.isneginf(values),3,0)))
    result=[]
    for i,v in enumerate(code.tolist()):
        if result and result[-1][2]==v:result[-1][1]=i+1
        else:result.append([i,i+1,v])
    return result


@pytest.mark.parametrize('name',INFINITY)
def test_original_infinity_semantics_are_preserved(name):
    spec=next(f for f in probe.API if f['name']==name)
    data=probe.frame(192,'infinity')
    got=data.select(probe.expression(spec,{})).to_series()
    actual=[got.struct.field(f).to_numpy() for f in got.struct.fields] if isinstance(got.dtype,pl.Struct) else [got.to_numpy()]
    expected=getattr(talib,name.upper())(*[data[probe.column(i)].to_numpy() for i in spec['inputs']])
    expected=list(expected) if isinstance(expected,tuple) else [expected]
    for old,new,known in zip(expected,actual,INFINITY[name]):
        assert runs(old)==known['old']
        assert runs(new)==known['old']
        np.testing.assert_allclose(new,old,rtol=1e-10,atol=1e-10,equal_nan=True)



@pytest.mark.parametrize('name',['rsi','stochrsi','cmou','percentile','maxindex','minindex','minmaxindex','var','stddev','correl'])
@pytest.mark.parametrize('pattern',['constant','flat_then_move','nan','null','tiny'])
@pytest.mark.parametrize('period',[2,5,31])
def test_compatibility_kernels_against_c(name,pattern,period):
    spec=next(f for f in probe.API if f['name']==name)
    data=probe.frame(300,pattern)
    got=data.select(probe.expression(spec,{'timeperiod':period})).to_series()
    fields=[got.struct.field(f) for f in got.struct.fields] if isinstance(got.dtype,pl.Struct) else [got]
    expected=getattr(talib,name.upper())(*[data[probe.column(i)].fill_null(float('nan')).to_numpy() for i in spec['inputs']],timeperiod=period)
    expected=list(expected) if isinstance(expected,tuple) else [expected]
    for actual,old in zip(fields,expected):
        valid=~actual.is_null().to_numpy()
        if actual.dtype.is_integer():np.testing.assert_array_equal(actual.to_numpy()[valid],old[valid])
        else:np.testing.assert_allclose(actual.to_numpy()[valid],old[valid],rtol=1e-10,atol=1e-10,equal_nan=True)


@pytest.mark.parametrize('name',['percentile','percentrank','mavp'])
@pytest.mark.parametrize('period',[10000,10001,100000])
def test_preserved_legacy_parameter_range(name,period):
    spec=next(f for f in probe.API if f['name']==name)
    data=probe.frame(period+2)
    params={'maxperiod':period} if name=='mavp' else {'timeperiod':period}
    got=data.select(probe.expression(spec,params)).to_series().to_numpy()
    old=getattr(talib,name.upper())(*[data[probe.column(i)].to_numpy() for i in spec['inputs']],**params)
    np.testing.assert_allclose(got,old,rtol=1e-10,atol=1e-10,equal_nan=True)


@pytest.mark.parametrize('name',['ppo','pvo'])
@pytest.mark.parametrize('matype',[0,2,5,9])
def test_zero_window_keeps_original_combine_rule(name,matype):
    data=probe.frame(400,'fraction_then_zero').with_columns(pl.col('close').alias('volume'))
    spec=next(f for f in probe.API if f['name']==name)
    got=data.select(probe.expression(spec,{'matype':matype})).to_series().to_numpy()
    old=getattr(talib,name.upper())(data['volume' if name=='pvo' else 'close'].to_numpy(),matype=matype)
    np.testing.assert_allclose(got,old,rtol=1e-10,atol=1e-10,equal_nan=True)


@pytest.mark.parametrize('name',['ppo','pvo'])
def test_integer_default_sentinel_uses_ema(name):
    data=probe.frame(192,'domain').with_columns(pl.col('close').alias('volume'))
    spec=next(f for f in probe.API if f['name']==name)
    if name=='ppo':
        # The original Polars wrapper rejected this raw enum sentinel; the C
        # function itself accepts it. Freeze the public expression behavior.
        with pytest.raises(pl.exceptions.ComputeError):data.select(probe.expression(spec,{'matype':-(2**31)}))
        return
    got=data.select(probe.expression(spec,{'matype':-(2**31)})).to_series().to_numpy()
    old=getattr(talib,name.upper())(data['volume' if name=='pvo' else 'close'].to_numpy(),matype=-(2**31))
    np.testing.assert_allclose(got,old,rtol=1e-10,atol=1e-10,equal_nan=True)


@pytest.mark.parametrize('name',['apo','macd','macdfix','macdext','eri','ema','ma','bbands','mavp','efi','kc','zlema'])
@pytest.mark.parametrize('pattern',['high_offset','micro_offset','large_constant','large_finite','leading_negative_infinity'])
def test_review_regressions_against_original(name,pattern):
    spec=next(f for f in probe.API if f['name']==name)
    data=probe.frame(192,pattern)
    got=data.select(probe.expression(spec,{})).to_series()
    fields=[got.struct.field(f) for f in got.struct.fields] if isinstance(got.dtype,pl.Struct) else [got]
    old=getattr(talib,name.upper())(*[data[probe.column(i)].to_numpy() for i in spec['inputs']])
    old=list(old) if isinstance(old,tuple) else [old]
    for actual,want in zip(fields,old):
        np.testing.assert_allclose(actual.to_numpy(),want,rtol=1e-10,atol=1e-10,equal_nan=True)


def test_adosc_cumulative_offset_regression():
    n=10000
    data=pl.DataFrame({'close':np.full(n,1000.),'high':np.full(n,1001.),'low':np.full(n,990.),'volume':np.where(np.arange(n)<5000,1000.,0.)})
    got=data.select(ta.adosc()).to_series().to_numpy()
    old=talib.ADOSC(*[data[c].to_numpy() for c in ('high','low','close','volume')])
    np.testing.assert_allclose(got,old,rtol=1e-10,atol=1e-10,equal_nan=True)


def test_future_large_observation_does_not_change_prefix_routing():
    close=20+np.sin(np.arange(192));close[85]=2000
    clean=pl.DataFrame({'close':close})
    missing=clean.with_columns(pl.when(pl.int_range(pl.len())==85).then(None).otherwise(pl.col('close')).alias('close'))
    assert clean.select(ta.macd()).head(85).equals(missing.select(ta.macd()).head(85))
