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
try:
    import resource
except ImportError:
    resource = None
from sarext_typed_inputs import digest_frame, preserve
import numpy as np
import polars as pl
import polars_talib as ta


MANIFEST = json.loads(Path(__file__).with_name('sarext_typed_cases.json').read_text())
CASE_NAMES = tuple(MANIFEST['cases'])
INTEGER_FAMILIES = tuple(MANIFEST['integer_families'])


def indicator(name):
    if name in ('sarext','sarext_reversal','sarext_longzero'):
        profile='reversal' if name.endswith('_reversal') else 'longzero' if name.endswith('_longzero') else 'default'
        return ta.sarext(pl.col('high'),pl.col('low'),**MANIFEST['profiles'][profile])
    if name=='sar':return ta.sar(pl.col('high'),pl.col('low'))
    raise ValueError('unexpected fixed SAREXT/SAR case '+name)


def frame(rows, bars):
    rng = np.random.default_rng(260126)
    close = 100 + np.cumsum(rng.normal(0, .1, rows))
    return pl.DataFrame({'close': close, 'open': close-.1, 'high': close+1, 'low': close-1,
                         'volume': rng.uniform(100,1000,rows), 'periods': np.resize([3.,5.,9.,14.],rows),
                         'symbol': np.arange(rows)//bars})



def specialized_frame(rows,bars,grouped,kind):
    within=np.arange(rows)%bars if grouped else np.arange(rows)
    if kind=='reversal':
        center=np.array([100.,110.,90.,115.,85.,120.,80.,100.])[within%8]
        high=center+1.;low=center-1.;close=center
    elif kind=='longzero':
        high=within.astype(float)+2.;low=within.astype(float);low[within==0]=-0.;close=(high+low)/2.
    else:raise ValueError('unknown fixed fixture')
    return pl.DataFrame({'close':close,'open':close-.1,'high':high,'low':low,'volume':np.full(rows,500.),
                         'periods':np.resize([3.,5.,9.,14.],rows),'symbol':np.arange(rows)//bars})


def fixture_coverage(name,data,result):
    if result.height!=data.height or result.width!=1:raise ValueError('fixture shape differs')
    if name.startswith('control_'):return {'fixture':'pure Polars cumsum','rows':data.height}
    if name.startswith(('sar/','grouped_sar/')):return {'fixture':'generic SAR shared preparation control','rows':data.height}
    values=result.to_series().fill_null(float('nan')).to_numpy();written=np.isfinite(values)
    if np.any(np.isinf(values)):raise ValueError('finite-price timing output overflowed')
    groups=data['symbol'].to_numpy() if name.startswith('grouped_') else np.zeros(data.height,dtype=np.int64)
    count=int(groups.max())+1
    per_group=np.bincount(groups[written],minlength=count)
    if not np.all(per_group==np.bincount(groups,minlength=count)-1):raise ValueError('SAREXT written/lookback coverage differs')
    negative_zero=written&(values.view(np.uint64)==0x8000000000000000)
    zeros=np.bincount(groups[negative_zero],minlength=count)
    if 'longzero' in name:
        if np.any(zeros==0):raise ValueError('legitimate long -0 stress missing in a chronological group')
    elif np.any(zeros):raise ValueError('ordinary no-replay fixture unexpectedly contains written -0')
    positive=np.bincount(groups[written&(values>0)],minlength=count)
    negative=np.bincount(groups[written&(values<0)],minlength=count)
    if 'reversal' in name and (np.any(positive==0) or np.any(negative==0)):raise ValueError('reversal fixture is vacuous in a chronological group')
    return {'fixture':'legitimate long-zero stress' if 'longzero' in name else 'ordinary no-written-negative-zero',
            'groups':count,'written':int(written.sum()),'negative_zero_count':int(negative_zero.sum()),
            'minimum_negative_zeros_per_group':int(zeros.min()),'maximum_negative_zeros_per_group':int(zeros.max()),
            'minimum_positive_per_group':int(positive.min()),'minimum_negative_per_group':int(negative.min()),
            'replay_scope':'negative-zero trigger inferred from public words/source, not an instrumented branch count'}


def case_specs(diagnostic=False):
    if diagnostic:
        raise ValueError('the focused SAREXT inventory has no diagnostic expansion')
    for name in CASE_NAMES:
        family, layout = name.split('/')
        grouped = family.startswith('grouped_') or family == 'control_cumsum'
        interleaved = layout.endswith('_interleaved')
        shape = layout.removesuffix('_interleaved')
        if grouped:
            groups, bars = map(int, shape.split('x'))
            rows = groups*bars
        else:
            rows, bars = int(shape), 1000
        functions = () if family.startswith('control_cumsum') else (family.removeprefix('grouped_'),)
        yield name, rows, bars, grouped, interleaved, functions


def cases(diagnostic=False, filters=()):
    # Select BEFORE allocation: a selected-case subprocess must not inherit the
    # allocation history of any earlier layout or sibling indicator.
    previous = None
    data = None
    for name, rows, bars, grouped, interleaved, functions in case_specs(diagnostic):
        if filters and name not in filters:
            continue
        kind='reversal' if 'reversal' in name else 'longzero' if 'longzero' in name else 'market'
        layout = (rows,bars,grouped,interleaved,kind)
        if layout != previous:
            data = frame(rows,bars) if kind=='market' else specialized_frame(rows,bars,grouped,kind)
            if interleaved:
                data = data.with_row_index('_row').with_columns((pl.col('_row')%bars).alias('_within')).sort('_within','symbol').drop('_row','_within')
            previous = layout
        if functions:
            expressions = [(indicator(f).over('symbol') if grouped else indicator(f)).alias(f) for f in functions]
        else:
            value = pl.col('close').cum_sum()
            expressions = [(value.over('symbol') if grouped else value).alias('control')]
        yield name, data, expressions


def flatten(result):
    columns=[]
    for s in result:
        if isinstance(s.dtype,pl.Struct):columns.extend(s.struct.field(f) for f in s.struct.fields)
        else:columns.append(s)
    return columns


def compare_arrays(numeric, nulls, expected, expected_nulls, *, exact=False, name='query'):
    if numeric.dtype != expected.dtype or numeric.shape != expected.shape:
        raise ValueError(name+': dtype or output length differs')
    np.testing.assert_array_equal(nulls,expected_nulls,err_msg=name)
    np.testing.assert_array_equal(np.isnan(numeric),np.isnan(expected),err_msg=name)
    np.testing.assert_array_equal(np.isposinf(numeric),np.isposinf(expected),err_msg=name)
    np.testing.assert_array_equal(np.isneginf(numeric),np.isneginf(expected),err_msg=name)
    np.testing.assert_array_equal(numeric==0,expected==0,err_msg=name)
    np.testing.assert_array_equal(np.signbit(numeric[expected==0]),np.signbit(expected[expected==0]),err_msg=name)
    if exact or numeric.dtype.kind in 'iu':
        np.testing.assert_array_equal(numeric,expected,err_msg=name)
        finite_nan_mask=~np.isnan(numeric)
        np.testing.assert_array_equal(np.signbit(numeric[finite_nan_mask]),np.signbit(expected[finite_nan_mask]),err_msg=name)
    else:
        np.testing.assert_allclose(numeric,expected,rtol=1e-10,atol=1e-10,equal_nan=True,err_msg=name)


def bit_diagnostics(numeric,expected):
    words=numeric.view(np.uint64);want=expected.view(np.uint64);different=words!=want
    finite=np.isfinite(numeric)&np.isfinite(expected)
    return {'all_word_differences':int(different.sum()),'finite_word_differences':int((different&finite).sum()),
            'nan_word_differences':int((different&np.isnan(numeric)&np.isnan(expected)).sum()),
            'maximum_absolute_finite_difference':float(np.max(np.abs(numeric[finite]-expected[finite]))) if np.any(finite) else 0.}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output',type=Path,required=True);p.add_argument('--repeats',type=int,default=31)
    p.add_argument('--save-inputs',type=Path,help='Preflight reference only: retain deduplicated physical input IPC files')
    p.add_argument('--reference',type=Path);p.add_argument('--write-reference',type=Path)
    p.add_argument('--source-root',type=Path,required=True);p.add_argument('--label',required=True)
    p.add_argument('--check-only',action='store_true')
    p.add_argument('--diagnostic',action='store_true',help='Add the one-thread fixed-row-count group-size sweep')
    p.add_argument('--exact-reference',action='store_true',help='Compare numeric values and signed zeros without tolerance; NaNs compare equal')
    p.add_argument('--case-filter',action='append',default=[],choices=CASE_NAMES,help='Exact reviewed case ID; timing requires exactly one')
    args=p.parse_args()
    if args.save_inputs and not(args.check_only and args.write_reference):p.error('input snapshots are only allowed during check-only reference creation')
    if args.repeats != 31: p.error('exactly 31 samples required')
    if not args.check_only and len(args.case_filter) != 1: p.error('timing requires one exact selected case')
    if len(set(args.case_filter)) != len(args.case_filter): p.error('duplicate selected case')
    reference=np.load(args.reference,allow_pickle=False) if args.reference else None
    values={};results={};load_start=os.getloadavg();checked_values=0;case_inventory=[];fixture_sha256={};output_sha256={};coverage={};input_snapshots={};reference_bit_diagnostics={}
    for name,data,exprs in cases(args.diagnostic, args.case_filter):
        case_inventory.append(name)
        fixture_sha256[name]=digest_frame(data)
        if args.save_inputs:input_snapshots[name]=preserve(data,args.save_inputs,fixture_sha256[name])
        query=data.lazy().select(exprs)
        result=query.collect()
        if reference is not None:
            assert str(result.schema)==str(reference[name+'_schema']), f'{name}: schema differs'
        if args.write_reference:values[name+'_schema']=np.array(str(result.schema))
        coverage[name]=fixture_coverage(name,data,result)
        columns=flatten(result)
        output_digest=hashlib.sha256(str(result.schema).encode())
        for i,column in enumerate(columns):
            slot=name+f'_{i}'
            numeric=column.fill_null(0).to_numpy();nulls=column.is_null().to_numpy()
            output_digest.update(numeric.tobytes());output_digest.update(nulls.tobytes())
            if reference is not None:
                compare_arrays(numeric,nulls,reference[slot],reference[slot+'_null'],exact=args.exact_reference,name=name)
                reference_bit_diagnostics[slot]=bit_diagnostics(numeric,reference[slot])
                checked_values+=len(numeric)
            if args.write_reference:
                values[slot]=numeric;values[slot+'_null']=nulls
        output_sha256[name]=output_digest.hexdigest()
        if args.check_only:continue
        for _ in range(5):query.collect()
        samples=[];minor=[];major=[]
        gc.disable()
        try:
            for _ in range(args.repeats):
                before=resource.getrusage(resource.RUSAGE_SELF) if resource is not None else None
                start=time.perf_counter_ns();result=query.collect();elapsed=time.perf_counter_ns()-start
                after=resource.getrusage(resource.RUSAGE_SELF) if resource is not None else None
                assert result.height==data.height
                samples.append(elapsed/1e6)
                if before is not None:
                    minor.append(after.ru_minflt-before.ru_minflt)
                    major.append(after.ru_majflt-before.ru_majflt)
        finally:gc.enable()
        # Recheck the final collected output against the same arm golden after timers.
        if reference is not None:
            assert str(result.schema)==str(reference[name+'_schema']), name+': final schema differs'
            for i,column in enumerate(flatten(result)):
                slot=name+f'_{i}'
                compare_arrays(column.fill_null(0).to_numpy(),column.is_null().to_numpy(),
                               reference[slot],reference[slot+'_null'],exact=args.exact_reference,name=name+' final')
        results[name]={'median_ms':statistics.median(samples),'min_ms':min(samples),'samples_ms':samples,
                       'rows':data.height,'output_fields':len(columns),
                       'minor_faults':minor if resource is not None else None,
                       'major_faults':major if resource is not None else None}
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
    native_files = list(Path(ta.__file__).parent.glob('_polars_talib*.so')) + list(Path(ta.__file__).parent.glob('_polars_talib*.pyd'))
    if len(native_files) != 1:
        raise ValueError('installed native extension is missing or ambiguous')
    native_sha256 = hashlib.sha256(native_files[0].read_bytes()).hexdigest()
    commit=subprocess.check_output(['git','-C',str(args.source_root),'rev-parse','HEAD'],text=True).strip()
    payload={'input_snapshots':input_snapshots,'label':args.label,'commit':commit,'cpu':cpu,'memory_bytes':memory,'logical_cpus':os.cpu_count(),
             'python':platform.python_version(),'platform':platform.platform(),'polars':pl.__version__,
             'numpy':np.__version__,'package':version('polars-talib'),'talib':ta.__talib_version__,
             'rust':subprocess.check_output(['rustc','--version'],text=True).strip(),
             'profile':'release (maturin --release --locked), portable CPU target',
             'threads':pl.thread_pool_size(),'repeats':args.repeats,'warmups':5,'diagnostic':args.diagnostic,
             'fault_counter':'getrusage(RUSAGE_SELF), process counters across query threads including engine/Python/allocator activity between reads' if resource is not None else None,
             'native_binary_sha256':native_sha256,'load_start':load_start,'load_end':os.getloadavg(),'source_sha256':source.hexdigest(),
             'correctness_reference':str(args.reference) if args.reference else None,'exact_reference':args.exact_reference,'integer_reference_exact':True,
             'reference_bit_diagnostics':reference_bit_diagnostics,'fixture_coverage':coverage,'fixture_sha256':fixture_sha256,'output_sha256':output_sha256,'final_output_checked':not args.check_only and reference is not None,
             'case_filters':args.case_filter,'case_inventory':case_inventory,'checked_values':checked_values,'affinity':sorted(os.sched_getaffinity(0)) if hasattr(os,'sched_getaffinity') else None,
             'results':results}
    args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(payload,indent=2)+'\n')
    print(json.dumps({n:round(r['median_ms'],4) for n,r in results.items()},indent=2))


if __name__=='__main__':main()
