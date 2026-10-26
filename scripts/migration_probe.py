"""Capture or compare the original and native installed release wheels.

Run this same file in separate environments; never import both plugin binaries
into one process. All input generation is deterministic and outside timing.
"""
from __future__ import annotations
import argparse
import hashlib
import inspect
import json
from pathlib import Path
import platform
import re
import numpy as np
import polars as pl
import polars_talib as ta

ROOT = Path(__file__).resolve().parents[1]
API = json.loads((ROOT / 'scripts/api.json').read_text())


def frame(n, pattern='random', dtype=pl.Float64):
    rng = np.random.default_rng(2601)
    close = 20 + np.cumsum(rng.normal(0, .2, n))
    if pattern == 'high_offset': close=1e9+np.sin(np.arange(n))
    if pattern == 'micro_offset': close=1e6+.001*np.sin(np.arange(n))
    if pattern == 'large_constant': close[:]=2e307
    if pattern == 'large_finite': close=1e307*(2+.1*np.sin(np.arange(n)))
    if pattern == 'constant': close[:] = 20
    if pattern == 'zero': close[:] = 0
    if pattern == 'trend': close = np.arange(n, dtype=float) / 100
    if pattern == 'flat_then_move': close = np.maximum(np.arange(n, dtype=float)-70, 0)
    if pattern == 'move_then_flat': close = np.minimum(np.arange(n, dtype=float), 10)
    if pattern == 'fraction_then_zero': close = np.where(np.arange(n)<30, close/10, 0)
    if pattern == 'tiny': close *= 1e-15
    if pattern == 'domain': close = rng.uniform(-.95,.95,n)
    spread = 1e-15 if pattern == 'tiny' else (.001 if pattern == 'micro_offset' else 1)
    df = pl.DataFrame({'open':close-.1*spread, 'high':close+spread,
                       'low':close-spread, 'close':close,
                       'volume':rng.integers(0, 2000, n).astype(float),
                       'periods':np.resize([2., 5., 8., 12.], n)})
    if pattern=='high_volume':df=df.with_columns(pl.Series('volume',1e9+np.sin(np.arange(n))))
    if pattern in ('constant','zero'):
        df = df.with_columns(pl.lit(20. if pattern == 'constant' else 0.).alias('volume'))
    if pattern in ('leading_null','leading_nan','null','nan','infinity','negative_infinity','leading_infinity','leading_negative_infinity'):
        value = None if 'null' in pattern else ((-float('inf') if 'negative' in pattern else float('inf')) if 'infinity' in pattern else float('nan'))
        condition = pl.int_range(pl.len()) < (1 if 'infinity' in pattern else 3) if pattern.startswith('leading') else pl.int_range(pl.len()).is_in([7, 85])
        df = df.with_columns(pl.when(condition).then(pl.lit(value,pl.Float64)).otherwise(pl.col(c)).alias(c)
                             for c in df.columns if c != 'periods')
    df = df.cast(dtype)
    if pattern == 'chunked':
        df = pl.concat([df.slice(i,17) for i in range(0,n,17)],rechunk=False)
    return df


def column(name): return {'real':'close','real0':'close','real1':'open'}.get(name,name)


def expression(spec, params):
    return getattr(ta,spec['name'])(*[pl.col(column(i)) for i in spec['inputs']],**params).alias('result')


def cases():
    for spec in API:
        name=spec['name']
        for n in (0,1,2,10,29,30,31,64,257):
            yield f'{name}/length/{n}', spec, frame(n), {}, None
        for pattern in ('constant','zero','trend','flat_then_move','move_then_flat','fraction_then_zero','tiny',
                        'leading_null','leading_nan','null','nan','infinity','negative_infinity','leading_infinity','leading_negative_infinity','chunked','domain','high_offset','micro_offset','large_constant','large_finite','high_volume'):
            yield f'{name}/{pattern}', spec, frame(192,pattern), {}, None
        from polars_talib._polars_talib import lookback
        lb=lookback(name,None)
        for delta in (-1,0,1):
            if lb>=0: yield f'{name}/warmup/{delta}',spec,frame(max(0,lb+delta)),{},None
        if any(p['name']=='timeperiod' for p in spec['params']):
            for period in (2,5,31):
                for pattern in ('nan','null','constant','flat_then_move'):
                    yield f'{name}/period_pattern/{period}/{pattern}',spec,frame(300,pattern),{'timeperiod':period},None
        yield f'{name}/float32', spec, frame(192,dtype=pl.Float32), {}, None
        # Groups are interleaved and unequal; rows within each group remain in
        # chronological order. Leading/internal nulls differ between groups.
        df=pl.concat([frame(n,p).with_columns(pl.lit(g).alias('g'),pl.int_range(pl.len()).alias('row'))
                      for g,(n,p) in enumerate(((1,'constant'),(47,'leading_null'),(192,'null'),(80,'random')))])
        df=df.sort('row','g').with_columns((pl.col('g')%2).alias('g2'))
        yield f'{name}/over',spec,df,{},['g','g2']
        yield f'{name}/over_ordered',spec,df.reverse(),{},['g','g2','ORDER']
        for param in spec['params']:
            key=param['name']
            if param['type']=='TA_MAType':
                values=(*range(16),-(2**31))
            elif key=='timeperiod':
                values=(1,2,5,31,-1,-(2**31))
            elif param['type']=='double':
                values=(0.,.3,1.) if 'penetration' in key or key in ('vfactor','percentile') else (.5,2.5)
            else:
                values=(1,3)
            for value in values:
                yield f'{name}/param/{key}/{value}',spec,frame(192),{key:value},None
            if param['type']=='TA_MAType':
                for pattern in ('high_offset','micro_offset','infinity','leading_negative_infinity'):
                    for value in range(14):
                        yield f'{name}/matype_pattern/{key}/{value}/{pattern}',spec,frame(192,pattern),{key:value},None
        if name in ('ppo','pvo'):
            for ma in (0,2,5,9):
                data=frame(400,'fraction_then_zero')
                if name=='pvo':data=data.with_columns(pl.col('close').alias('volume'))
                yield f'{name}/dead_window/{ma}',spec,data,{'matype':ma},None
    for name,params in [('percentile' ,{'timeperiod':10001}),('percentrank',{'timeperiod':10001}),
                         ('mavp',{'minperiod':2,'maxperiod':10001})]:
        spec=next(f for f in API if f['name']==name)
        yield f'{name}/legacy_max',spec,frame(10020),params,None


def capture(path):
    meta={'python':platform.python_version(),'polars':pl.__version__,'numpy':np.__version__,
          'talib':ta.__talib_version__, 'cases':{}, 'api':{}}
    for f in API:
        meta['api'][f['name']]=re.sub(r' at 0x[0-9A-Fa-f]+', '', str(inspect.signature(getattr(ta,f['name']))))
    values={}
    for index,(key,spec,df,params,groups) in enumerate(cases()):
        try:
            expr=expression(spec,params)
            if groups:
                if groups[-1]=='ORDER': expr=expr.over(groups[:-1],order_by='row')
                else: expr=expr.over(groups)
            result=df.lazy().select(expr).collect().to_series()
            fields=[result.struct.field(f) for f in result.struct.fields] if isinstance(result.dtype,pl.Struct) else [result]
            entry={'schema':str(result.dtype),'height':len(result),'fields':[]}
            for j,s in enumerate(fields):
                slot=f'c{index}_{j}'
                # Keep null masks independent: null and NaN are different API values.
                values[slot]=s.fill_null(0).to_numpy()
                values[slot+'_null']=s.is_null().to_numpy()
                entry['fields'].append(slot)
            meta['cases'][key]=entry
        except Exception as e:
            meta['cases'][key]={'error':type(e).__name__}
    values['metadata']=np.array(json.dumps(meta))
    path.parent.mkdir(parents=True,exist_ok=True)
    np.savez_compressed(path,**values)
    print(json.dumps({'cases':len(meta['cases']),'talib':ta.__talib_version__,'path':str(path)},indent=2))


def compare(baseline,candidate,report):
    old=np.load(baseline,allow_pickle=False); new=np.load(candidate,allow_pickle=False)
    om=json.loads(str(old['metadata'])); nm=json.loads(str(new['metadata']))
    failures=[]; bit_different=0; max_abs=0.; checked=0
    for key,a in om['cases'].items():
        b=nm['cases'].get(key)
        reason=[]; detail=[]
        if b is None: reason.append('missing case')
        elif 'error' in a or 'error' in b:
            if a!=b: reason.append(f'error mismatch: {a} vs {b}')
        elif (a['schema'],a['height'])!=(b['schema'],b['height']): reason.append('schema/length mismatch')
        else:
            for ak,bk in zip(a['fields'],b['fields']):
                av=old[ak];bv=new[bk];mask=old[ak+'_null'];bm=new[bk+'_null']
                if not np.array_equal(mask,bm): reason.append('null mask mismatch')
                valid=~mask
                av=av[valid];bv=bv[valid];checked+=len(av)
                exact=np.array_equal(av,bv,equal_nan=True)
                if not exact: bit_different+=1
                finite=np.isfinite(av)&np.isfinite(bv)
                if finite.any(): max_abs=max(max_abs,float(np.max(np.abs(av[finite]-bv[finite]))))
                atol=1e-10
                if '/tiny' in key:
                    scale=float(np.max(np.abs(av[np.isfinite(av)]))) if np.isfinite(av).any() else 0.
                    atol=min(atol,scale*1e-10)
                equal=(av==bv) if av.dtype.kind in 'iu' else np.isclose(av,bv,rtol=1e-10,atol=atol,equal_nan=True)
                if not equal.all():
                    reason.append('values differ')
                    indices=np.flatnonzero(~equal)[:5]
                    detail.append({'old':av[indices].tolist(),'new':bv[indices].tolist(),'bad_count':int((~equal).sum())})
        if reason: failures.append({'case':key,'reason':reason,'detail':detail})
    api_match=om['api']==nm['api']
    result={'baseline':str(baseline),'candidate':str(candidate),
            'baseline_sha256':hashlib.sha256(baseline.read_bytes()).hexdigest(),
            'candidate_sha256':hashlib.sha256(candidate.read_bytes()).hexdigest(),
            'baseline_runtime':{k:v for k,v in om.items() if k not in ('cases','api')},
            'candidate_runtime':{k:v for k,v in nm.items() if k not in ('cases','api')},
            'rtol':1e-10,'atol':1e-10,'tiny_case_atol':'min(1e-10, max_abs_finite_reference * 1e-10)','cases':len(om['cases']),'checked_values':checked,
            'api_signatures_match':api_match,'fields_with_bit_differences':bit_different,
            'max_absolute_difference':max_abs,'failures':failures}
    report.parent.mkdir(parents=True,exist_ok=True);report.write_text(json.dumps(result,indent=2,allow_nan=True)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='failures'},indent=2))
    print('failures:',len(failures)); print(json.dumps(failures[:20],indent=2))
    return bool(failures) or not api_match


def main():
    p=argparse.ArgumentParser();p.add_argument('--capture',type=Path)
    p.add_argument('--compare',nargs=2,type=Path);p.add_argument('--report',type=Path)
    args=p.parse_args()
    if args.capture: capture(args.capture)
    else: raise SystemExit(compare(*args.compare,args.report))


if __name__=='__main__': main()
