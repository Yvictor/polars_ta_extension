"""Release-wheel A/B measurements with correctness checks on the timed data.

Run sequentially in fresh baseline/candidate processes, alternate their order,
and keep POLARS_MAX_THREADS identical. No build or corpus job may run alongside.
"""
from __future__ import annotations
import argparse
import gc
import hashlib
from importlib.metadata import version
import json
import os
from pathlib import Path
import platform
import statistics
import subprocess
import time
import numpy as np
import polars as pl
import polars_talib as ta


FUNCTIONS = ('ema','rsi','macd','atr','adx','cci','stddev','ppo')


def frame(rows,bars):
    rng=np.random.default_rng(260126)
    close=100+np.cumsum(rng.normal(0,.1,rows))
    return pl.DataFrame({'close':close,'open':close-.1,'high':close+1,'low':close-1,
                         'volume':rng.uniform(100,1000,rows),'symbol':np.arange(rows)//bars})


def cases():
    for n in (1000,1_000_000):
        data=frame(n,1000)
        for f in ('ema','rsi','macd','atr'):
            yield f'{f}/{n}',data,[getattr(ta,f)().alias(f)]
        yield f'mix8/{n}',data,[getattr(ta,f)().alias(f) for f in FUNCTIONS]
    for groups,bars,interleaved in ((1000,1000,False),(10000,100,False),(2000,100,True)):
        data=frame(groups*bars,bars)
        if interleaved:
            data=data.with_row_index('_row').with_columns((pl.col('_row')%bars).alias('_within')).sort('_within','symbol').drop('_row','_within')
        for functions in (('ema',),('atr',),FUNCTIONS):
            label=functions[0] if len(functions)==1 else 'mix8'
            key=f'grouped_{label}/{groups}x{bars}'+('_interleaved' if interleaved else '')
            yield key,data,[getattr(ta,f)().over('symbol').alias(f) for f in functions]


def flatten(result):
    columns=[]
    for s in result:
        if isinstance(s.dtype,pl.Struct):columns.extend(s.struct.field(f) for f in s.struct.fields)
        else:columns.append(s)
    return columns


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output',type=Path,required=True);p.add_argument('--repeats',type=int,default=31)
    p.add_argument('--reference',type=Path);p.add_argument('--write-reference',type=Path)
    p.add_argument('--source-root',type=Path,required=True);p.add_argument('--label',required=True)
    p.add_argument('--check-only',action='store_true')
    args=p.parse_args()
    if args.repeats<5:p.error('at least five repetitions required')
    reference=np.load(args.reference,allow_pickle=False) if args.reference else None
    values={};results={};load_start=os.getloadavg();checked_values=0
    for name,data,exprs in cases():
        query=data.lazy().select(exprs)
        result=query.collect()
        if reference is not None:
            assert str(result.schema)==str(reference[name+'_schema']), f'{name}: schema differs'
        if args.write_reference:values[name+'_schema']=np.array(str(result.schema))
        columns=flatten(result)
        for i,column in enumerate(columns):
            slot=name+f'_{i}'
            numeric=column.fill_null(0).to_numpy();nulls=column.is_null().to_numpy()
            if reference is not None:
                np.testing.assert_array_equal(nulls,reference[slot+'_null'])
                np.testing.assert_array_equal(np.isnan(numeric),np.isnan(reference[slot]))
                np.testing.assert_allclose(numeric,reference[slot],rtol=1e-10,atol=1e-10,equal_nan=True,err_msg=name)
                checked_values+=len(numeric)
            if args.write_reference:
                values[slot]=numeric;values[slot+'_null']=nulls
        if args.check_only:continue
        for _ in range(5):query.collect()
        samples=[]
        gc.disable()
        try:
            for _ in range(args.repeats):
                start=time.perf_counter_ns();result=query.collect();elapsed=time.perf_counter_ns()-start
                assert result.height==data.height
                samples.append(elapsed/1e6)
        finally:gc.enable()
        results[name]={'median_ms':statistics.median(samples),'min_ms':min(samples),'samples_ms':samples,
                       'rows':data.height,'output_fields':len(columns)}
    if args.write_reference:np.savez_compressed(args.write_reference,**values)
    source=hashlib.sha256()
    for path in sorted(args.source_root.rglob('*')):
        if path.is_file() and (path.suffix in ('.rs','.py') or path.name in ('Cargo.toml','Cargo.lock')):
            relative=path.relative_to(args.source_root)
            if any(part in ('target','.venv','.git','__pycache__') for part in relative.parts):continue
            if relative.parts[0] not in ('src','python','talib','talib-sys') and len(relative.parts)>1:continue
            source.update(str(relative).encode());source.update(path.read_bytes())
    cpu=platform.processor();memory=None
    if platform.system()=='Darwin':
        try:
            cpu=subprocess.check_output(['sysctl','-n','machdep.cpu.brand_string'],text=True,stderr=subprocess.DEVNULL).strip()
            memory=int(subprocess.check_output(['sysctl','-n','hw.memsize'],text=True,stderr=subprocess.DEVNULL))
        except (subprocess.CalledProcessError,OSError):pass
    elif Path('/proc/cpuinfo').is_file():
        cpu=next((s.split(':',1)[1].strip() for s in Path('/proc/cpuinfo').read_text().splitlines() if s.startswith('model name')),cpu)
    commit=subprocess.check_output(['git','-C',str(args.source_root),'rev-parse','HEAD'],text=True).strip()
    payload={'label':args.label,'commit':commit,'cpu':cpu,'memory_bytes':memory,'logical_cpus':os.cpu_count(),
             'python':platform.python_version(),'platform':platform.platform(),'polars':pl.__version__,
             'numpy':np.__version__,'package':version('polars-talib'),'talib':ta.__talib_version__,
             'rust':subprocess.check_output(['rustc','--version'],text=True).strip(),
             'profile':'release (maturin --release --locked), portable CPU target',
             'threads':pl.thread_pool_size(),'repeats':args.repeats,'warmups':5,
             'load_start':load_start,'load_end':os.getloadavg(),'source_sha256':source.hexdigest(),
             'correctness_reference':str(args.reference) if args.reference else None,
             'checked_values':checked_values,'affinity':sorted(os.sched_getaffinity(0)) if hasattr(os,'sched_getaffinity') else None,
             'results':results}
    args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(payload,indent=2)+'\n')
    print(json.dumps({n:round(r['median_ms'],4) for n,r in results.items()},indent=2))


if __name__=='__main__':main()
