"""Three-arm selected kernel comparison; candidate must be reviewed before activation."""
import argparse
import hashlib
import itertools
import json
import math
import os
from pathlib import Path
import platform
import resource
import shutil
import statistics
import struct
import subprocess
import tarfile
import time

BASELINE = '4334163d3a1f5019aa9051342316b936a4dfb994'
CANDIDATE = '2ea9da4c800244d3e09a8b7ef30b340913e03b38'
ORIGINAL = 'b2bbc26d41ec80823c8bffb0cc436a97f29911cc'
C_SHA = 'ec59ccd88c0c77f618587d858787c8f9d06c40460a09d66751926f6fd670f985'
ARMS = ('original', 'baseline', 'candidate')
MODES = ('typed', 'abstract')
CASES = tuple(itertools.product(('engulf','doji'), ('white','alternating','equality_ieee'), (100,10000,1000000)))
ORDERS = tuple(itertools.permutations(ARMS)) * 2
EDGES = ((0,0),(0,1),(0,2),(1,5),(2,5),(3,10),(17,63),(42,48),(63,63))
CANARY = 0x5a5a5a5a
ITERS = {100:1000,10000:10,1000000:1}
PROFILE = {'RUSTFLAGS':'','CARGO_ENCODED_RUSTFLAGS':'','CARGO_PROFILE_RELEASE_LTO':'thin','CARGO_PROFILE_RELEASE_CODEGEN_UNITS':'1','CARGO_PROFILE_RELEASE_DEBUG':'false','CFLAGS':'','CXXFLAGS':''}
HERE = Path(__file__).resolve().parent


def need(value, reason):
    if not value:
        raise ValueError(reason)


def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda:f.read(1024*1024),b''):h.update(block)
    return h.hexdigest()



def fixtures(output):
    import numpy as np
    assert np.__version__=='2.5.3'
    folder=output/'fixtures';folder.mkdir(exist_ok=True);result={}
    close=100+np.cumsum(np.random.default_rng(260126).normal(0,.1,1000000))
    for name,n in itertools.product(('white','alternating','equality_ieee'),(100,10000,1000000)):
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
        result[f'{name}/{n}']={'path':str(path),'sha256':sha(path),'bytes':path.stat().st_size,'initial_finite_bars':2}
    return result


def exact(value, expected):
    if type(value) is not type(expected):
        return False
    if isinstance(expected,dict):
        return value.keys()==expected.keys() and all(exact(value[k],v) for k,v in expected.items())
    if isinstance(expected,list):
        return len(value)==len(expected) and all(exact(a,b) for a,b in zip(value,expected))
    return value==expected


def read_json(text):
    def pairs(values):
        result={}
        for k,v in values:
            need(k not in result,'duplicate JSON key');result[k]=v
        return result
    return json.loads(text,object_pairs_hook=pairs,parse_constant=lambda _:(_ for _ in ()).throw(ValueError('nonfinite JSON')))


def pins(args):
    import re
    need(re.fullmatch('[0-9a-f]{40}',CANDIDATE) is not None,'candidate source is unset; builds and timing are blocked')
    need(args.candidate_commit==CANDIDATE,'candidate must match the reviewed full pin')
    need(CANDIDATE!=BASELINE,'candidate and baseline must differ')
    return {'original':ORIGINAL,'baseline':BASELINE,'candidate':CANDIDATE}


def source_record(root, pin, original=False):
    root=Path(root).resolve()
    commit=subprocess.check_output(['git','-C',str(root),'rev-parse','HEAD'],text=True).strip()
    need(commit==pin and not subprocess.check_output(['git','-C',str(root),'status','--porcelain']),'wrong or dirty source')
    if original:
        paths=[root/'talib-sys/vendor/ta-lib-0.8.1-src.tar.gz',root/'talib-sys/build.rs',root/'Cargo.lock']
    else:
        paths=[]
        for folder in ['ta_codegen/output/rust','ta_codegen/generator/src','ta_codegen/input/cdlengulfing','ta_codegen/input/cdldoji']:
            paths.extend(p for p in (root/folder).rglob('*') if p.is_file() and not {'target','.git'}.intersection(p.relative_to(root).parts) and p.suffix in ('.rs','.toml','.lock','.c','.h','.yaml','.yml'))
        paths.extend(root/p for p in ['ta_codegen/generator/Cargo.toml','ta_codegen/generator/Cargo.lock'])
    files={p.relative_to(root).as_posix():sha(p) for p in sorted(set(paths))}
    return {'commit':commit,'clean':True,'source_files':files,'source_sha256':hashlib.sha256(json.dumps(files,sort_keys=True,separators=(',',':')).encode()).hexdigest()}


def runtime():
    need(platform.system()=='Linux' and platform.machine()=='x86_64','Linux x86_64 evidence required')
    r=subprocess.check_output(['rustc','--version','--verbose'],text=True)
    need(r.startswith('rustc 1.97.0 '),'Rust1.97.0 required')
    need(all(os.environ.get(k)==v for k,v in PROFILE.items()),'portable identical release flags required')
    cpu=next(x.split(':',1)[1].strip() for x in Path('/proc/cpuinfo').read_text().splitlines() if x.startswith('model name'))
    return {'cpu':cpu,'platform':platform.platform(),'python':platform.python_version(),'rustc':r,'executable_paths':{name:shutil.which(name) for name in ('rustc','cargo','cc','cmake')},'cargo':subprocess.check_output(['cargo','--version'],text=True),'cc':subprocess.check_output(['cc','--version'],text=True),'numpy':__import__('numpy').__version__,'cmake':subprocess.check_output(['cmake','--version'],text=True),'environment':{k:os.environ.get(k) for k in (*PROFILE,'RUSTUP_TOOLCHAIN','CARGO_BUILD_JOBS')}}


def command_run(command, log, cwd=None):
    Path(str(log)+'.command.json').write_text(json.dumps(list(map(str,command)),indent=2)+'\n')
    with Path(log).open('w') as f:subprocess.run(list(map(str,command)),cwd=cwd,stdout=f,stderr=subprocess.STDOUT,check=True)


def file_inventory(folder):
    need(folder.is_dir(),'retained provenance directory missing')
    result={str(p):sha(p) for p in folder.rglob('*') if p.is_file()}
    need(result,'retained provenance directory empty')
    return result


def check_control_sources(sources):
    key='ta_codegen/output/rust/library/src/ta_func/cdldoji.rs'
    need(sources['baseline']['source_files'][key]==sources['candidate']['source_files'][key],'Doji control source changed')


def check_codegen_proof(proof,sources):
    need(proof.is_dir(),'annotated static codegen proof must be retained')
    manifest=read_json((proof/'manifest.json').read_text())
    need(manifest['baseline_commit']==BASELINE and manifest['candidate_commit']==CANDIDATE,'static proof source pins differ')
    need(set(manifest['files'])=={p.relative_to(proof).as_posix() for p in proof.rglob('*') if p.is_file() and p.name!='manifest.json'},'static proof file inventory differs')
    for name,digest in manifest['files'].items():need(sha(proof/name)==digest,'static proof bytes differ')
    cfg=read_json((proof/'expanded-cfg-proof.json').read_text())
    key='ta_codegen/output/rust/library/src/ta_func/cdlengulfing.rs'
    need(cfg['original_source_sha256']==sources['baseline']['source_files'][key] and cfg['candidate_source_sha256']==sources['candidate']['source_files'][key],'static proof generated source differs')
    gate=read_json((proof/'source-gates.json').read_text())
    need(all(sources['candidate']['source_files'][k]==v for k,v in gate['source_files'].items()),'static proof final generator/test scope differs')


def build(args):
    expected=pins(args); rt=runtime(); need(sha(args.harness)==sha(HERE/'bench_engulf_window.rs'),'harness override must match retained canonical source');out=args.output;out.mkdir(parents=True,exist_ok=True)
    sources={a:source_record(getattr(args,a+'_source'),pin,a=='original') for a,pin in expected.items()}
    check_codegen_proof(args.codegen_proof,sources)
    check_control_sources(sources)
    archive=args.original_source/'talib-sys/vendor/ta-lib-0.8.1-src.tar.gz';need(sha(archive)==C_SHA,'C archive must be original0.8.1')
    (out/'archives').mkdir(exist_ok=True);shutil.copyfile(archive,out/'archives/ta-lib-0.8.1-src.tar.gz')
    croot=out/'c-source';croot.mkdir(exist_ok=True)
    with tarfile.open(archive) as tar:tar.extractall(croot,filter='data')
    cbuild=out/'c-build'; install=out/'c-install'
    ccommands=[['cmake','-S',str(croot/'ta-lib-0.8.1'),'-B',str(cbuild),'-DCMAKE_BUILD_TYPE=Release','-DBUILD_SHARED_LIBS=OFF','-DBUILD_STATIC_LIBS=ON','-DBUILD_DEV_TOOLS=OFF','-DCMAKE_POSITION_INDEPENDENT_CODE=ON','-DCMAKE_EXPORT_COMPILE_COMMANDS=ON','-DCMAKE_INSTALL_PREFIX='+str(install)],['cmake','--build',str(cbuild),'--target','install','--parallel','4']]
    for i,c in enumerate(ccommands):command_run(c,out/f'c-build-{i}.log')
    c_lib=install/'lib/libta-lib.a';need(c_lib.is_file(),'missing C static library')
    bins=out/'bin';bins.mkdir(exist_ok=True); records={}
    common=['rustc','--edition=2021','-O','-C','lto=thin','-C','codegen-units=1','-Dwarnings','--check-cfg=cfg(c_reference,test)',str(args.harness)]
    for a in ARMS:
        binary=bins/a
        if a=='original':
            command=common+['--cfg','c_reference','-L','native='+str(c_lib.parent),'-l','static=ta-lib','-l','m','-o',str(binary)]
            cargo=None;lib=None
        else:
            target=out.parent/'engulf-window-targets'/a;cargo=['cargo','build','--release','--locked','-p','ta-lib','--manifest-path',str(getattr(args,a+'_source')/'ta_codegen/output/rust/Cargo.toml'),'--target-dir',str(target)]
            command_run(cargo,out/(a+'-cargo.log'));lib=target/'release/libta_lib.rlib'
            retained=out/'libraries'/(a+'-libta_lib.rlib');retained.parent.mkdir(exist_ok=True);shutil.copyfile(lib,retained);need(sha(lib)==sha(retained),'rlib copy changed')
            command=common+['-L','dependency='+str(target/'release/deps'),'--extern','ta_lib='+str(lib),'-o',str(binary)]
        command_run(command,out/(a+'-harness-build.log'))
        test_binary=bins/(a+'-cli-tests');test_command=command[:-2]+['--test','-o',str(test_binary)]
        command_run(test_command,out/(a+'-cli-build.log'));command_run([test_binary,'--test-threads=1'],out/(a+'-cli-tests.log'))
        records[a]={'source':sources[a],'binary':str(binary),'binary_sha256':sha(binary),'cargo_command':cargo,'rustc_command':command,'test_command':test_command,'test_binary':str(test_binary),'test_binary_sha256':sha(test_binary)}
        if lib is not None:records[a].update(library=str(lib),library_sha256=sha(lib),retained_library=str(retained),retained_library_sha256=sha(retained))
    inputs=fixtures(out)
    scripts={name:sha(HERE/name) for name in ['engulf_window_benchmark.py','bench_engulf_window.rs']}
    proof=args.codegen_proof
    proof_dest=out/'codegen-proof';shutil.copytree(proof,proof_dest)
    source_archives={}
    for arm in ARMS:
        dest=out/'archives'/(arm+'-source.tar.gz')
        subprocess.run(['git','-C',str(getattr(args,arm+'_source')),'archive','--format=tar.gz','-o',str(dest),'HEAD'],check=True)
        source_archives[str(dest)]=sha(dest)
    p={'source_archives':source_archives,'runtime':rt,'pins':expected,'arms':records,'inputs':inputs,'scripts':scripts,'harness_sha256':sha(args.harness),'c_archive':str(out/'archives/ta-lib-0.8.1-src.tar.gz'),'c_archive_sha256':C_SHA,'c_library':str(c_lib),'c_library_sha256':sha(c_lib),'c_commands':ccommands,'c_config_sha256':sha(cbuild/'CMakeCache.txt'),'codegen_proof':file_inventory(proof_dest)}
    (out/'build-provenance.json').write_text(json.dumps(p,indent=2)+'\n');verify(args,p)


def verify(args,p):
    need(p['pins']==pins(args) and p['runtime']==runtime(),'source/runtime settings changed')
    check_codegen_proof(args.output/'codegen-proof',{a:r['source'] for a,r in p['arms'].items()})
    check_control_sources({a:r['source'] for a,r in p['arms'].items()})
    need(p['codegen_proof']==file_inventory(args.output/'codegen-proof'),'static proof inventory/hash changed')
    need(sha(args.harness)==p['harness_sha256'],'harness changed')
    for name,h in p['scripts'].items():need(sha(HERE/name)==h,'controller/support changed')
    for a,pin in p['pins'].items():
        r=p['arms'][a];need(source_record(getattr(args,a+'_source'),pin,a=='original')==r['source'],'source changed')
        for key in ['binary','test_binary']+([] if a=='original' else ['library','retained_library']):need(sha(r[key])==r[key+'_sha256'],'binary/library changed')
    for key in ['c_archive','c_library']:need(sha(p[key])==p[key+'_sha256'],'C source/library changed')
    need(sha(args.output/'c-build/CMakeCache.txt')==p['c_config_sha256'],'C config changed')
    for f,h in p['codegen_proof'].items():need(sha(f)==h,'static proof changed')
    for f,h in p['source_archives'].items():need(sha(f)==h,'source archive changed')
    for r in p['inputs'].values():need(sha(r['path'])==r['sha256'],'fixture changed')


def shape(indicator,n,start=0,end=None):
    end=n-1 if end is None else end;b=max(start,2 if indicator=='engulf' else 10)
    return (0,0) if b>end else (b,end-b+1)


def capture(path,indicator,n,full):
    data=Path(path).read_bytes();expected=[(64,*shape(indicator,64,s,e)) for s,e in EDGES] if full else []
    expected.append((n,*shape(indicator,n)));at=0;selected=None;rows=[]
    for size,beg,count in expected:
        length=4*size+64;record=data[at:at+length];need(len(record)==length and record[:8]==b'ENGOUT01','capture truncation/magic')
        need(struct.unpack('<QQQ',record[8:32])==(size,beg,count),'capture range differs')
        values=struct.unpack('<'+'i'*(size+8),record[32:]);need(values[:beg]==(0,)*beg,'leading zero padding differs')
        need(values[beg+count:]==(CANARY,)*(size+8-beg-count),'physical/serialized tail differs')
        need(all(x in (-100,-80,0,80,100) for x in values[beg:beg+count]),'invalid integer output')
        if indicator=='doji':need(all(x in (0,100) for x in values[beg:beg+count]),'Doji control output domain differs')
        rows.append({'n':size,'beg':beg,'count':count});selected=record;at+=length
    need(at==len(data),'capture extra records')
    return {'sha256':sha(path),'bytes':len(data),'records':len(rows),'ranges':rows,'selected':selected}


def check_hits(selected,indicator,fixture,n):
    values=struct.unpack('<'+'i'*(n+8),selected[32:]);beg,count=shape(indicator,n);hits=set(values[beg:beg+count])
    if indicator=='engulf':need(hits=={'white':{0},'alternating':{-100,0,100},'equality_ieee':{-100,-80,0,80,100}}[fixture],'expected fixture hit classes absent')
    if indicator=='doji' and fixture=='white':need(hits=={100},'Doji positive control is vacuous')


def parse(text,selection,arm,timed):
    rows=[read_json(l) for l in text.splitlines() if l.strip()];indicator,fixture,n,mode=selection
    need(len(rows)==(2 if timed else 1),'exact selected stdout inventory required')
    identity={'indicator':indicator,'fixture':fixture,'n':n,'mode':mode}
    for r in rows:need(all(type(r.get(k))is type(v) and r[k]==v for k,v in identity.items()),'selected metadata differs')
    if not timed:
        want={'kind':'capture',**identity,'edge_records':9,'range_errors':3,'short_checks':0 if arm=='original' else 5,'timed':False}
        need(exact(rows[0],want),'untimed edges/invalid buffer coverage missing');return rows[0]
    need(exact(rows[0],{'kind':'validation',**identity,'beg':shape(indicator,n)[0],'count':shape(indicator,n)[1],'golden_verified':True}),'golden proof missing before timer')
    t=rows[1];need(set(t)=={'kind',*identity,'iterations','warmups','samples_ns'} and t['kind']=='case' and t['iterations']==ITERS[n] and type(t['iterations'])is int and t['warmups']==5 and type(t['warmups'])is int,'timing settings differ')
    samples=t['samples_ns'];need(isinstance(samples,list) and len(samples)==31 and all(type(x)in(int,float) and math.isfinite(x) and x>0 for x in samples),'31 finite positive samples required');return t


def child_command(p,arm,selection,path,golden=None):
    indicator,fixture,n,mode=selection
    c=[p['arms'][arm]['binary'],indicator,fixture,mode,str(n),str(ITERS[n]),p['inputs'][f'{fixture}/{n}']['path'],str(path)]
    return c+(['--capture-only'] if golden is None else ['--golden',str(golden)])


def execute(command,stem,timeout):
    Path(str(stem)+'-command.json').write_text(json.dumps(command,indent=2)+'\n');before=resource.getrusage(resource.RUSAGE_CHILDREN)
    try:r=subprocess.run(command,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,check=False,timeout=timeout)
    except subprocess.TimeoutExpired as e:
        Path(str(stem)+'.stdout').write_text(e.stdout.decode(errors='replace') if isinstance(e.stdout,bytes) else(e.stdout or ''));Path(str(stem)+'.stderr').write_text(e.stderr.decode(errors='replace') if isinstance(e.stderr,bytes) else(e.stderr or ''));Path(str(stem)+'-failure.json').write_text(json.dumps({'timeout':timeout,'command':command}));raise
    after=resource.getrusage(resource.RUSAGE_CHILDREN);Path(str(stem)+'.stdout').write_text(r.stdout);Path(str(stem)+'.stderr').write_text(r.stderr);
    if r.returncode:
        Path(str(stem)+'-failure.json').write_text(json.dumps({'returncode':r.returncode,'command':command}));r.check_returncode()
    need(not r.stderr.strip(),'unexpected child stderr')
    return r.stdout,{'minor':after.ru_minflt-before.ru_minflt,'major':after.ru_majflt-before.ru_majflt}


def prepare(args,p):
    folder=args.output/'validation';folder.mkdir();goldens={};proofs=[]
    for indicator,fixture,n in CASES:
        for mode in MODES:
            selection=(indicator,fixture,n,mode);key='/'.join(map(str,selection));reference=None
            for arm in ARMS:
                stem=folder/(key.replace('/','__')+'__'+arm);path=Path(str(stem)+'.bin');c=child_command(p,arm,selection,path);text,faults=execute(c,stem,30);parsed=parse(text,selection,arm,False);cap=capture(path,indicator,n,True)
                check_hits(cap['selected'],indicator,fixture,n)
                if arm=='original':
                    reference=(cap['sha256'],cap['bytes']);gold=args.output/'goldens'/(key.replace('/','__')+'.bin');gold.parent.mkdir(exist_ok=True);gold.write_bytes(cap['selected']);goldens[key]={'path':str(gold),'sha256':sha(gold),'bytes':gold.stat().st_size}
                need((cap['sha256'],cap['bytes'])==reference,'full C/baseline/candidate capture mismatch before timing')
                cap.pop('selected');proofs.append({'arm':arm,'selection':selection,'command':c,'stdout':parsed,'capture':cap,'whole_child_faults':faults})
    need(len(proofs)==108,'all108 global edge/main captures required')
    record={'completed_before_any_timing':True,'checks':proofs,'goldens':goldens};(args.output/'capture-validation.json').write_text(json.dumps(record,indent=2)+'\n');return record


def summarize(rows):
    results={};negative=[]
    for indicator,fixture,n in CASES:
        for mode in MODES:
            key='/'.join(map(str,(indicator,fixture,n,mode)));med={}
            for arm in ARMS:
                selected=[r for r in rows if r['key']==key and r['arm']==arm];need(len(selected)==12 and [r['round'] for r in selected]==list(range(1,13)),'missing/duplicate rounds');med[arm]=[statistics.median(r['samples_ns']) for r in selected]
            pairs={}
            for before,after in itertools.combinations(ARMS,2):
                a,b=med[before],med[after];pct=(statistics.median(b)/statistics.median(a)-1)*100
                name=before+'_vs_'+after;row={'before_process_medians_ns':a,'after_process_medians_ns':b,'before_median_ns':statistics.median(a),'after_median_ns':statistics.median(b),'paired_ratios':[x/y for x,y in zip(a,b)],'median_paired_ratio':statistics.median(x/y for x,y in zip(a,b)),'ratio_envelope':[min(a)/max(b),max(a)/min(b)],'after_latency_percent':pct,'after_faster_rounds':sum(x>y for x,y in zip(a,b)),'is_doji_control':indicator=='doji','c_arm_is_direct_public_call':True}
                pairs[name]=row
                if pct>0:negative.append({'case_mode':key,'comparison':name,**row})
            results[key]=pairs
    return results,negative


def measure(args,p,validation):
    need(validation['completed_before_any_timing'] and len(validation['checks'])==108,'all correctness gates must precede timing')
    folder=args.output/'children';folder.mkdir();rows=[];started=time.monotonic()
    for indicator,fixture,n in CASES:
        for mode in MODES:
            selection=(indicator,fixture,n,mode);key='/'.join(map(str,selection));golden=validation['goldens'][key];need(sha(golden['path'])==golden['sha256'],'golden changed')
            for index,order in enumerate(ORDERS,1):
                for arm in order:
                    need(time.monotonic()-started<600,'600s measurement budget exceeded; partial data retained')
                    stem=folder/(key.replace('/','__')+f'__{index}__{arm}');path=Path(str(stem)+'.bin');c=child_command(p,arm,selection,path,golden['path']);text,faults=execute(c,stem,30);r=parse(text,selection,arm,True);cap=capture(path,indicator,n,False);cap.pop('selected');need(cap['sha256']==golden['sha256'] and cap['bytes']==golden['bytes'],'selected bytes differ')
                    proof={'key':key,'arm':arm,'round':index,'command':c,'capture':cap,'golden':golden,'whole_child_faults':faults,'samples_ns':r['samples_ns']};Path(str(stem)+'-proof.json').write_text(json.dumps(proof,indent=2)+'\n');path.unlink();proof['duplicate_deleted_after_proof']=True;rows.append(proof)
                    with (args.output/'completed-children.jsonl').open('a') as ledger:ledger.write(json.dumps(proof)+'\n')
    need(time.monotonic()-started<=600,'600s measurement budget exceeded')
    need(len(rows)==1296 and sum(len(r['samples_ns'])for r in rows)==40176,'complete1296children/40176samples required');results,negatives=summarize(rows)
    return {'rows':rows,'results':results,'negative_cases':negatives,'orders':ORDERS,'children':1296,'samples':40176,'elapsed_seconds':time.monotonic()-started,'limits':['Arms are original C0.8.1 and development Rust0.8.4 at433/window; no registry0.8.3 or full adapter arm is measured.','Primary attribution is baseline_vs_candidate within the same selected Rust mode; C081 comparisons provide context.', 'Kernel diagnostics, not Polars query speed; raw f64 NaN/Inf/signed-zero inputs do not represent Polars null masking.','C direct public calls are repeated under typed/abstract block labels; no C abstract binding is measured.','All mode calls include driver dispatch/range assertions; abstract includes holder new/bind/call.','Fresh selected processes isolate sibling workloads, not allocator activity from golden I/O.','Observed envelopes are descriptive, not confidence intervals; correlated inner samples and shared-runner effects remain.','Whole-child faults include startup/fixtures/golden I/O/warmups, not allocator-only events.','No local or cross-run ratios are multiplied; all slower medians and Doji controls are retained.']}


def write_report(output,report):
    lines=['# Engulf and Doji kernel comparison','',*report['limits'],'','|Case/mode|Comparison|Before ns|After ns|After latency %|Paired ratio|Descriptive envelope|Faster rounds|','|---|---|---:|---:|---:|---:|---|---:|']
    for case,pairs in report['results'].items():
        for name,r in pairs.items():
            lines.append(f"|{case}|{name}|{r['before_median_ns']:.3f}|{r['after_median_ns']:.3f}|{r['after_latency_percent']:+.3f}|{r['median_paired_ratio']:.5f}|{r['ratio_envelope']}|{r['after_faster_rounds']}/12|")
    (output/'comparison.md').write_text('\n'.join(lines)+'\n')


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    for a in ARMS:parser.add_argument('--'+a+'-source',type=Path,required=True)
    parser.add_argument('--candidate-commit',required=True);parser.add_argument('--output',type=Path,required=True);parser.add_argument('--codegen-proof',type=Path,required=True);parser.add_argument('--harness',type=Path,default=HERE/'bench_engulf_window.rs');parser.add_argument('--build-only',action='store_true');a=parser.parse_args(argv);pins(a)
    for key,v in vars(a).copy().items():
        if isinstance(v,Path):setattr(a,key,v.resolve())
    a.output.mkdir(parents=True,exist_ok=True)
    if a.build_only:build(a);return
    p=read_json((a.output/'build-provenance.json').read_text());verify(a,p);previous=set(os.sched_getaffinity(0));need(previous,'CPU affinity required')
    try:
        os.sched_setaffinity(0,{min(previous)});validation=prepare(a,p);report=measure(a,p,validation);verify(a,p);report.update(provenance=p,validation=validation,affinity=sorted(os.sched_getaffinity(0)));(a.output/'summary.json').write_text(json.dumps(report,indent=2)+'\n');(a.output/'negative-cases.json').write_text(json.dumps(report['negative_cases'],indent=2)+'\n');write_report(a.output,report)
    finally:os.sched_setaffinity(0,previous)

if __name__=='__main__':main()
