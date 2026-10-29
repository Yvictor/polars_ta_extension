"""Four-mode, selected-fixture Engulf diagnostic; never product throughput."""
import argparse,platform,sys,hashlib,itertools,json,math,os,re,resource,shutil,statistics,struct,subprocess,time,collections
from pathlib import Path
from integer_init_provenance import sha256,source_record,identity,wheel_record,flags_record
from integer_init_stage_benchmark import native_dependency_records,mapper

HERE=Path(__file__).resolve().parent
NATIVE='6c3fb5fb44496c5739ee9f1d8dfa11f7b46dd473'
ORIGINAL='b2bbc26d41ec80823c8bffb0cc436a97f29911cc'
C_SHA='ec59ccd88c0c77f618587d858787c8f9d06c40460a09d66751926f6fd670f985'
MODES=('c081','rust_typed','rust_generic','native_full')
ORDERS=(('c081','rust_typed','native_full','rust_generic'),('rust_typed','rust_generic','c081','native_full'),
        ('rust_generic','native_full','rust_typed','c081'),('native_full','c081','rust_generic','rust_typed'))*3
FIXTURES=('white','alternating','equality_ieee')
LENGTHS=(100,10000,1000000)
CASES=tuple(itertools.product(FIXTURES,LENGTHS))
ITERS={100:1000,10000:10,1000000:1}
CANARY=0x5a5a5a5a
SCRIPTS=('engulf_profile_benchmark.py','engulf_profile_probe.rs','integer_init_provenance.py',
         'integer_init_stage_benchmark.py','integer_init_benchmark.py','integer_init_cases.json','migration_ci_benchmark.py')
VALID=re.compile(r'^VALIDATE fixture=(\w+) mode=(\w+) n=(\d+) beg=2 count=(\d+) record_tail=8 physical_tail_checked=(true|false) hits=(\[[^\n]+\]) exact_golden=(true|false)$',re.M)
PROBE=re.compile(r'^PROBE fixture=(\w+) mode=(\w+) n=(\d+) iters=(\d+) warmups=5 counts=(\[[^\n]+\]) ns=(\[[^\n]+\])$',re.M)


def invoke(command,path,env=None):
    path=Path(path);path.with_suffix('.command.json').write_text(json.dumps(list(map(str,command)),indent=2)+'\n')
    with path.open('w') as log:subprocess.run(list(map(str,command)),env=env,stdout=log,stderr=subprocess.STDOUT,check=True)


def runtime_record():
    assert sys.platform=='linux' and platform.machine()=='x86_64'
    model=next(line.split(':',1)[1].strip() for line in Path('/proc/cpuinfo').read_text().splitlines() if line.startswith('model name'))
    assert all(os.environ.get(k,'')=='' for k in ('CFLAGS','CXXFLAGS'))
    return {'platform':platform.platform(),'machine':platform.machine(),'python':sys.version,'cpu':model,
            'CFLAGS':os.environ.get('CFLAGS',''),'CXXFLAGS':os.environ.get('CXXFLAGS','')}


def snapshot(args):
    folder=args.output/'linkage';folder.mkdir(parents=True,exist_ok=True)
    deps,evidence=native_dependency_records(args.target_dir,inventory_path=folder/'unfiltered-inventory.json')
    files={}
    for path,digest in evidence.items():
        source=Path(path);dest=folder/'fingerprints'/source.parent.name/source.name
        dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,dest);assert sha256(dest)==digest;files[str(dest)]=digest
    installed=identity(args.native_python);retained={}
    for source in [*deps.values(),*map(Path,installed['native_files'])]:
        dest=folder/'product-artifacts'/source.name;dest.parent.mkdir(exist_ok=True);shutil.copyfile(source,dest)
        retained[str(dest)]=sha256(source);assert sha256(dest)==retained[str(dest)]
    record={'source':source_record(args.native_source,NATIVE),'identity':installed,'wheel':wheel_record(args.wheel_dir/'native',installed),
            'flags':flags_record(),'dependencies':{name:{'path':str(path),'sha256':sha256(path)} for name,path in deps.items()},
            'fingerprints':files,'retained':retained,'inventory_sha256':sha256(folder/'unfiltered-inventory.json')}
    (folder/'snapshot.json').write_text(json.dumps(record,indent=2)+'\n')


def fixtures(output):
    import numpy as np
    assert np.__version__=='2.5.3'
    folder=output/'fixtures';folder.mkdir(exist_ok=True);result={}
    close=100+np.cumsum(np.random.default_rng(260126).normal(0,.1,1000000))
    for name,n in CASES:
        if name=='white':c=close[:n];o=c-.1;h=c+1;l=c-1
        elif name=='alternating':
            o=np.resize(np.array([101.,99.,103.,100.]),n);c=np.resize(np.array([100.,102.,98.,101.]),n)
            h=np.maximum(o,c)+1;l=np.minimum(o,c)-1
        else:
            o=np.resize(np.array([100.,101.,100.,102.,98.,104.,0.,-0.,np.nan,1.,-np.inf,np.inf,-np.inf,1.,100.,101.]),n)
            c=np.resize(np.array([101.,100.,102.,99.,103.,97.,-0.,0.,1.,np.nan,np.inf,-np.inf,1.,-np.inf,101.,100.]),n)
            h=np.full(n,1000.);l=np.full(n,-1000.)
        assert all(np.isfinite(v[:2]).all() for v in (o,h,l,c))
        path=folder/f'{name}-{n}.bin';tag=name.encode()
        with path.open('wb') as f:
            f.write(b'ENGDATA1'+struct.pack('<QQ',n,len(tag))+tag)
            for values in (o,h,l,c):f.write(values.astype('<f8').tobytes())
        result[f'{name}/{n}']={'path':str(path),'sha256':sha256(path),'bytes':path.stat().st_size,'initial_finite_bars':2}
    return result


def build(args):
    flags=flags_record();runtime=runtime_record();e=flags['environment']
    assert e['RUSTFLAGS']==e['CARGO_ENCODED_RUSTFLAGS']=='' and e['CARGO_PROFILE_RELEASE_LTO']=='false' and e['CARGO_PROFILE_RELEASE_CODEGEN_UNITS']=='16'
    snapshot_record=json.loads((args.output/'linkage/snapshot.json').read_text())
    sources={side:source_record(getattr(args,side+'_source'),pin) for side,pin in (('native',NATIVE),('original',ORIGINAL))}
    identities={side:identity(getattr(args,side+'_python')) for side in ('native','original')}
    for side in identities:
        assert identities[side]['polars']=='1.44.2' and identities[side]['numpy']=='2.5.3' and identities[side]['python'].startswith('3.12.')
    assert identities['native']['talib'].startswith('0.8.3') and identities['original']['talib'].startswith('0.8.1 ')
    assert snapshot_record['source']==sources['native'] and snapshot_record['identity']==identities['native'] and snapshot_record['flags']==flags
    wheels={side:wheel_record(args.wheel_dir/side,identities[side]) for side in identities}
    assert snapshot_record['wheel']==wheels['native']
    for field in ('fingerprints','retained'):
        for path,digest in snapshot_record[field].items():assert sha256(path)==digest
    assert sha256(args.output/'linkage/unfiltered-inventory.json')==snapshot_record['inventory_sha256']
    deps=snapshot_record['dependencies'];assert set(deps)=={'ta_lib','polars','serde','jemallocator'}
    for entry in deps.values():assert sha256(entry['path'])==entry['sha256']
    vendor=args.original_source/'talib-sys/vendor/ta-lib-0.8.1-src.tar.gz';assert sha256(vendor)==C_SHA
    archives=list(args.target_dir.glob('release/build/talib-sys-*/out/lib/libta-lib.a'));assert len(archives)==1
    c_lib=archives[0];native_paths=sorted(args.target_dir.glob('release/build/*/out/lib'))
    native_archives={str(p):sha256(p) for d in native_paths for p in d.glob('*.a')}
    (args.output/'native-library-inventory.json').write_text(json.dumps(native_archives,indent=2)+'\n')
    for name in {Path(path).name for path in native_archives}:
        matching={digest for path,digest in native_archives.items() if Path(path).name==name}
        assert len(matching)==1,'ambiguous native archive basename: '+name
    retained={}
    for side in identities:
        retained[side]={}
        for path,digest in identities[side]['native_files'].items():
            dest=args.output/'product-artifacts'/side/Path(path).name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(path,dest);assert sha256(dest)==digest;retained[side][str(dest)]=digest
    c_configuration={}
    for cache in c_lib.parent.parent.rglob('CMakeCache.txt'):
        dest=args.output/'c-configuration'/cache.relative_to(c_lib.parent.parent)
        dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(cache,dest);c_configuration[str(dest)]=sha256(dest)
    assert c_configuration,'actual original C CMake configuration required'
    folder=args.output/'probe';folder.mkdir(exist_ok=True)
    support=folder/'native-source/compat';shutil.copytree(args.native_source/'src/compat',support,dirs_exist_ok=True)
    shutil.copyfile(args.native_source/'src/compat.rs',support/'mod.rs')
    wrapper=folder/'probe.rs';body=(HERE/'engulf_profile_probe.rs').read_text().split('\n',1)[1]
    modules='#![allow(dead_code,unused_imports)]\n'
    for name,file in (('native','native.rs'),('compat','compat.rs'),('params','params.rs'),('utils','utils.rs')):
        source=support/'mod.rs' if name=='compat' else args.native_source/'src'/file
        modules+=f'#[path="{source}"] mod {name};\n'
    wrapper.write_text(modules+'mod generated {\n'+mapper(args.native_source)+'\n}\n'+body)
    binary=folder/'engulf-probe'
    command=['rustc','--edition=2021','-O','-C','codegen-units=16','-C','lto=off',str(wrapper),'-L','dependency='+str(args.target_dir/'release/deps')]
    for name,entry in deps.items():command+=['--extern',name+'='+entry['path']]
    for path in native_paths:command+=['-L','native='+str(path)]
    command+=['-l','static=ta-lib','-l','m','-o',str(binary)]
    invoke(command,folder/'build.log')
    test_binary=folder/'probe-tests';test_command=command[:-2]+['--cfg','engulf_probe_contracts','-o',str(test_binary)]
    invoke(test_command,folder/'test-build.log');invoke([test_binary],folder/'tests.log')
    data=fixtures(args.output)
    record={'runtime':runtime,'retained_product_artifacts':retained,'c_configuration':c_configuration,
            'linkage_snapshot_sha256':sha256(args.output/'linkage/snapshot.json'),
            'sources':sources,'identities':identities,'wheels':wheels,'flags':flags,'snapshot':snapshot_record,
            'binary':str(binary),'binary_sha256':sha256(binary),'command':command,'test_command':test_command,
            'contract_binary':str(test_binary),'contract_binary_sha256':sha256(test_binary),
            'wrapper':str(wrapper),'wrapper_sha256':sha256(wrapper),'support':{str(p):sha256(p) for p in support.rglob('*.rs')},
            'c_archive':str(c_lib),'c_archive_sha256':sha256(c_lib),'c_vendor_sha256':C_SHA,'native_archives':native_archives,
            'scripts':{name:sha256(HERE/name) for name in SCRIPTS},'fixtures':data,'modes':MODES,'orders':ORDERS,'cases':CASES,
            'allocator':'production Jemalloc behind diagnostic counting wrapper; actual product ELFs retained separately',
            'context':'Rust1.90 portable-O16CGU/noLTO; generic mode includes holder new/bind/call; native_full uses predecodedParams and outputallocation, not Python/Polars plugin overhead'}
    (args.output/'build-provenance.json').write_text(json.dumps(record,indent=2)+'\n')


def verify(args):
    p=json.loads((args.output/'build-provenance.json').read_text())
    assert flags_record()==p['flags'] and runtime_record()==p['runtime']
    assert sha256(args.output/'linkage/snapshot.json')==p['linkage_snapshot_sha256']
    assert sha256(args.output/'linkage/unfiltered-inventory.json')==p['snapshot']['inventory_sha256']
    for side,pin in (('native',NATIVE),('original',ORIGINAL)):
        assert source_record(getattr(args,side+'_source'),pin)==p['sources'][side]
        assert identity(getattr(args,side+'_python'))==p['identities'][side]
        assert wheel_record(args.wheel_dir/side,p['identities'][side])==p['wheels'][side]
    files={p['contract_binary']:p['contract_binary_sha256'],p['binary']:p['binary_sha256'],p['wrapper']:p['wrapper_sha256'],p['c_archive']:p['c_archive_sha256'],**p['support'],**p['native_archives']}
    for field in ('fingerprints','retained'):files.update(p['snapshot'][field])
    files.update(p['c_configuration'])
    for record in p['retained_product_artifacts'].values():files.update(record)
    files.update({entry['path']:entry['sha256'] for entry in p['snapshot']['dependencies'].values()})
    files.update({entry['path']:entry['sha256'] for entry in p['fixtures'].values()})
    for path,digest in files.items():assert sha256(path)==digest
    for name,digest in p['scripts'].items():assert sha256(HERE/name)==digest
    return p


def capture(path,n):
    data=Path(path).read_bytes();assert len(data)==4*n+64 and data[:8]==b'ENGOUT01'
    assert struct.unpack('<QQQ',data[8:32])==(n,2,n-2)
    values=struct.unpack('<'+'i'*(n+8),data[32:]);assert values[:2]==(0,0) and values[-8:]==(CANARY,)*8
    counts=collections.Counter(values[2:n]);hits=[counts[k] for k in (-100,-80,0,80,100)];assert sum(hits)==n-2
    return {'path':str(Path(path)),'sha256':sha256(path),'bytes':len(data),'hits':hits,'physical_tail_note':'serialized8canaries normalize record shape; only preallocated modes check their physical10element tail'}


def expected_hits(fixture,n):
    if fixture=='white':return [0,0,n-2,0,0]
    if fixture=='alternating':return [n//4,0,n//2-1,0,n//4-1]
    if fixture=='equality_ieee':
        full=n//16;one_end=full+(1 if n%16==4 else 0)
        return [full,one_end,n-2-2*full-2*one_end,one_end,full]
    raise ValueError('unknown fixture')


def parse(text,fixture,mode,n,timed):
    assert text.startswith('C_VERSION 0.8.1 ')
    matches=VALID.findall(text);assert len(matches)==1
    found=matches[0];assert found[:4]==(fixture,mode,str(n),str(n-2))
    assert found[4]==('false' if mode=='native_full' else 'true') and found[6]==('true' if timed else 'false')
    hits=json.loads(found[5]);assert len(hits)==5 and all(type(v)is int and v>=0 for v in hits) and hits==expected_hits(fixture,n)
    probes=PROBE.findall(text)
    if not timed:assert not probes;return {'hits':hits}
    assert len(probes)==1;row=probes[0];assert row[:4]==(fixture,mode,str(n),str(ITERS[n]))
    counts=json.loads(row[4]);samples=json.loads(row[5]);assert len(counts)==4 and all(type(v)is int and v>=0 for v in counts)
    assert counts[2]+counts[3]<=counts[0]
    assert len(samples)==31 and all(type(v)in(int,float) and math.isfinite(v) and v>0 for v in samples)
    return {'hits':hits,'counts':counts,'samples_ns':samples,'median_ns':statistics.median(samples)}


def command(p,fixture,mode,n,path,golden=None):
    result=[p['binary'],fixture,mode,str(n),str(ITERS[n]),p['fixtures'][f'{fixture}/{n}']['path'],str(path)]
    return result+(['--capture-only'] if golden is None else ['--golden',str(golden)])


def execute(cmd,stem,env,timeout=15):
    Path(str(stem)+'-command.json').write_text(json.dumps(cmd,indent=2)+'\n')
    before=resource.getrusage(resource.RUSAGE_CHILDREN)
    try:
        result=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,env=env,timeout=timeout)
    except subprocess.TimeoutExpired as error:
        def decoded(value):return value.decode(errors='replace') if isinstance(value,bytes) else (value or '')
        Path(str(stem)+'.stdout').write_text(decoded(error.stdout));Path(str(stem)+'.stderr').write_text(decoded(error.stderr))
        Path(str(stem)+'-failure.json').write_text(json.dumps({'timed_out':True,'timeout':timeout,'command':cmd},indent=2)+'\n')
        raise
    after=resource.getrusage(resource.RUSAGE_CHILDREN)
    Path(str(stem)+'.stdout').write_text(result.stdout);Path(str(stem)+'.stderr').write_text(result.stderr);result.check_returncode()
    return result.stdout,{'minor':after.ru_minflt-before.ru_minflt,'major':after.ru_majflt-before.ru_majflt}


def validate(args,p,env):
    folder=args.output/'validation';folder.mkdir(exist_ok=True);rows=[];goldens={}
    for fixture,n in CASES:
        for mode in MODES:
            stem=folder/f'{fixture}-{n}-{mode}';path=Path(str(stem)+'.bin');cmd=command(p,fixture,mode,n,path)
            stdout,faults=execute(cmd,stem,env);row=parse(stdout,fixture,mode,n,False);record=capture(path,n);assert record['hits']==row['hits']
            key=f'{fixture}/{n}'
            if mode=='c081':goldens[key]=record
            assert (record['sha256'],record['bytes'])==(goldens[key]['sha256'],goldens[key]['bytes'])
            rows.append({'fixture':fixture,'n':n,'mode':mode,'command':cmd,'capture':record,'stdout':stdout,'whole_child_faults':faults})
    record={'all36completed_before_any_timer':True,'checks':rows,'goldens':goldens,'build_provenance_sha256':sha256(args.output/'build-provenance.json')}
    (args.output/'validation-complete.json').write_text(json.dumps(record,indent=2)+'\n');return record


def measure(args,p,validation,env):
    assert validation['all36completed_before_any_timer'] and len(validation['checks'])==36
    assert validation['build_provenance_sha256']==sha256(args.output/'build-provenance.json')
    folder=args.output/'children';folder.mkdir(exist_ok=True);rows=[];started=time.monotonic();deadline=started+90
    with (args.output/'raw.jsonl').open('w') as log:
        for fixture,n in CASES:
            golden=validation['goldens'][f'{fixture}/{n}'];assert sha256(golden['path'])==golden['sha256']
            for index,order in enumerate(ORDERS,1):
                for mode in order:
                    left=deadline-time.monotonic();assert left>0,'90s whole-stage cap; partial rows are not a completed comparison'
                    stem=folder/f'{fixture}-{n}-{index}-{mode}';path=Path(str(stem)+'.bin');cmd=command(p,fixture,mode,n,path,golden['path'])
                    stdout,faults=execute(cmd,stem,env,min(15,left));row=parse(stdout,fixture,mode,n,True);record=capture(path,n)
                    assert record['sha256']==golden['sha256'] and record['hits']==golden['hits']==row['hits']
                    proof={'round':index,'fixture':fixture,'n':n,'mode':mode,'command':cmd,'capture':record,'golden':golden,'whole_child_faults':faults,'stdout':stdout,**row}
                    Path(str(stem)+'-proof.json').write_text(json.dumps(proof,indent=2)+'\n');path.unlink();proof['duplicate_deleted_after_proof']=True
                    rows.append(proof);log.write(json.dumps(proof)+'\n');log.flush()
    assert len(rows)==432
    results={}
    for fixture,n in CASES:
        modes={}
        for mode in MODES:
            values=[r for r in rows if (r['fixture'],r['n'],r['mode'])==(fixture,n,mode)]
            assert len(values)==12 and [r['round'] for r in values]==list(range(1,13));assert len({tuple(r['counts']) for r in values})==1
            med=[r['median_ns'] for r in values];modes[mode]={'process_medians_ns':med,'median_ns':statistics.median(med),'counts':values[0]['counts']}
        comparisons={}
        for before,after in itertools.combinations(MODES,2):
            a=modes[before]['process_medians_ns'];b=modes[after]['process_medians_ns']
            comparisons[before+'_vs_'+after]={'paired_ratios':[x/y for x,y in zip(a,b)],'ratio_envelope':[min(a)/max(b),max(a)/min(b)],
                'after_latency_percent':100*(statistics.median(b)/statistics.median(a)-1),'after_faster_rounds':sum(y<x for x,y in zip(a,b))}
        results[f'{fixture}/{n}']={'modes':modes,'comparisons':comparisons,'hits':validation['goldens'][f'{fixture}/{n}']['hits']}
    report={'provenance':p,'validation':validation,'orders':ORDERS,'rows':rows,'results':results,'timed_children':432,'samples':13392,'elapsed_seconds':time.monotonic()-started,'affinity':sorted(os.sched_getaffinity(0)),'thread_environment':{key:env[key] for key in ('POLARS_MAX_THREADS','OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS')},
        'limitations':'Counter-instrumented diagnostic stages, not product throughput. Modes own only required buffers, so allocation lifetimes differ. Generic includes holder setup. Full uses predecodedParams, excludes plugin/Python/Polars query execution. Every selected child validates its full output before5warmups and after31samples; middle timed calls check range/shape and preallocated writes are black-boxed. Capture/golden I/O can warm allocator state. Faults cover whole child, counts are Rust request/realloc count+cumulative bytes excluding Cmalloc/dealloc/live/RSS. Pairwise modes are balanced within each fixture/length, case blocks sequential. Envelopes are extrema, not confidence intervals; no subtractive/additive cost attribution.'}
    assert report['elapsed_seconds']<=90,'90s whole-stage cap exceeded; raw rows retained without completed summary'
    (args.output/'summary.json').write_text(json.dumps(report,indent=2)+'\n')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    for side in ('native','original'):
        parser.add_argument('--'+side+'-source',type=Path,required=True);parser.add_argument('--'+side+'-python',type=Path,required=True)
    for key in ('output','target-dir','wheel-dir'):parser.add_argument('--'+key,type=Path,required=True)
    mode=parser.add_mutually_exclusive_group(required=True);mode.add_argument('--snapshot-native',action='store_true');mode.add_argument('--build',action='store_true');mode.add_argument('--run',action='store_true')
    args=parser.parse_args()
    for key,value in vars(args).copy().items():
        if isinstance(value,Path):setattr(args,key,value.resolve())
    args.output.mkdir(parents=True,exist_ok=True)
    if args.snapshot_native:snapshot(args)
    elif args.build:build(args)
    else:
        p=verify(args);previous=set(os.sched_getaffinity(0));assert previous
        env={**os.environ,'POLARS_MAX_THREADS':'1','OMP_NUM_THREADS':'1','OPENBLAS_NUM_THREADS':'1','MKL_NUM_THREADS':'1'}
        try:
            os.sched_setaffinity(0,{min(previous)});validation=validate(args,p,env);measure(args,p,validation,env);verify(args)
        finally:os.sched_setaffinity(0,previous)

if __name__=='__main__':main()
