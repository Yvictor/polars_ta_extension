"""Three-arm selected kernel comparison; candidate must be reviewed before activation."""
import argparse
import hashlib
import itertools
import json
import math
import os
from pathlib import Path
from sarext_window_codegen import inspect as inspect_normal_elf
import platform
import resource
import shutil
import statistics
import struct
import subprocess
import tarfile
import time

BASELINE = 'ccd3172940ed1d9daa4e7197f2265810852e8910'
CANDIDATE = 'da9dd99bc1780f569dfc24f35c09d4a25063162c'
ORIGINAL = '62021c1d14ef5499505af5547384cab509adf3fc'
ARMS = ('original', 'baseline', 'candidate')
MODES = ('typed',)
CASES = (*itertools.product(('sar','sarext'),('default','reversal'),(100,10000,1000000)), *((('add','default',n) for n in (100,10000,1000000))))
ORDERS = tuple(itertools.permutations(ARMS)) * 2
EDGES = ((0,0),(0,1),(0,2),(1,5),(2,5),(3,10),(17,63),(42,48),(63,63),(0,63))
CANARY = 0x7ff80000000055aa
IEEE_SHAPES = 17
EDGE_RECORDS = 180
ITERS = {100:1000,10000:10,1000000:1}
PROFILE = {'CARGO_PROFILE_RELEASE_OPT_LEVEL':'3','RUSTFLAGS':'','CARGO_ENCODED_RUSTFLAGS':'','CARGO_PROFILE_RELEASE_LTO':'thin','CARGO_PROFILE_RELEASE_CODEGEN_UNITS':'1','CARGO_PROFILE_RELEASE_DEBUG':'false','CFLAGS':'','CXXFLAGS':''}
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
    need(np.__version__=='2.5.3','NumPy2.5.3 required')
    folder=output/'fixtures';folder.mkdir(exist_ok=True);result={}
    close=100+np.cumsum(np.random.default_rng(260126).normal(0,.1,1000000))
    for name,n in itertools.product(('default','reversal'),(100,10000,1000000)):
        if name=='default':c=close[:n];o=c-.1;h=c+1;l=c-1
        else:
            c=np.resize(np.array([101.,100.,102.,98.,103.,97.,104.,96.]),n)
            o=c-.1;h=c+.5;l=c-.5
        need(all(np.isfinite(v).all() for v in (o,h,l,c)),'timed fixture must be finite')
        path=folder/f'{name}-{n}.bin';tag=name.encode()
        with path.open('wb') as f:
            f.write(b'SARDATA1'+struct.pack('<QQ',n,len(tag))+tag)
            for values in (o,h,l,c):f.write(values.astype('<f8').tobytes())
        result[f'{name}/{n}']={'path':str(path),'sha256':sha(path),'bytes':path.stat().st_size,'all_finite':True}
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
        paths=[p for folder in ('src','include') for p in (root/folder).rglob('*') if p.is_file() and p.suffix in ('.c','.h')]
        paths.extend(root/p for p in ['VERSION','CMakeLists.txt'])
    else:
        paths=[]
        for folder in ['ta_codegen/output/rust','ta_codegen/generator/src','ta_codegen/input/sar','ta_codegen/input/sarext','ta_codegen/input/add']:
            paths.extend(p for p in (root/folder).rglob('*') if p.is_file() and not {'target','.git'}.intersection(p.relative_to(root).parts) and p.suffix in ('.rs','.toml','.lock','.c','.h','.yaml','.yml'))
        paths.extend(root/p for p in ['ta_codegen/generator/Cargo.toml','ta_codegen/generator/Cargo.lock','VERSION','rust-toolchain.toml'])
    files={p.relative_to(root).as_posix():sha(p) for p in sorted(set(paths))}
    return {'commit':commit,'clean':True,'source_files':files,'source_sha256':hashlib.sha256(json.dumps(files,sort_keys=True,separators=(',',':')).encode()).hexdigest()}


def runtime(version):
    need(platform.system()=='Linux' and platform.machine()=='x86_64','Linux x86_64 evidence required')
    r=subprocess.check_output(['rustc','--version','--verbose'],text=True)
    need(version in ('1.90.0','1.97.0') and r.startswith('rustc '+version+' '),'exact job Rust toolchain required')
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
    key='ta_codegen/output/rust/library/src/ta_func/add.rs'
    need(sources['baseline']['source_files'][key]==sources['candidate']['source_files'][key],'ADD control source changed')
    a=sources['baseline']['source_files'];b=sources['candidate']['source_files']
    changed={k for k in set(a)|set(b) if a.get(k)!=b.get(k)}
    need(changed=={'ta_codegen/generator/src/backends/rust_window.rs','ta_codegen/generator/src/backends/rust_lang.rs','ta_codegen/output/rust/library/src/ta_func/sar.rs','ta_codegen/output/rust/library/src/ta_func/sarext.rs'},'source footprint differs from reviewed four files')


def check_codegen_proof(proof,sources):
    need(proof.is_dir(),'annotated source/static proof must be retained')
    manifest=read_json((proof/'manifest.json').read_text())
    need(manifest['baseline_commit']==BASELINE and manifest['candidate_commit']==CANDIDATE,'proof pins differ')
    need(set(manifest['files'])=={p.relative_to(proof).as_posix() for p in proof.rglob('*') if p.is_file() and p.name!='manifest.json'},'proof inventory differs')
    for name,digest in manifest['files'].items():need(sha(proof/name)==digest,'proof bytes differ')
    frozen=read_json((proof/'prefix-final-freeze.json').read_text())
    need(len(frozen)==4 and all(sources['candidate']['source_files'][k]==v for k,v in frozen.items()),'frozen source footprint differs')
    need(manifest['library_msrv']=='1.88' and manifest['development_toolchain']=='1.97.0','MSRV/toolchain qualification changed')



def source_gate_record(folder):
    folder=Path(folder);p=folder/'source-gates.json';need(p.is_file(),'full source gates missing')
    g=read_json(p.read_text());need(g.get('complete')is True and g.get('candidate')==CANDIDATE and g.get('toolchain')=='1.97.0' and g.get('library_msrv')=='1.88','source gate identity/qualification differs')
    need(g.get('logs') and all(sha(folder/name)==digest for name,digest in g['logs'].items()),'source gate logs changed')
    frozen=read_json((HERE.parent/'tests/data/sarext-window-codegen/prefix-final-freeze.json').read_text())
    need(g['source_files']==frozen,'source gate footprint differs')
    return {'record':g,'sha256':sha(p)}


def build(args):
    expected=pins(args); rt=runtime(args.rust_version); need(sha(args.harness)==sha(HERE/'bench_sarext_window.rs'),'harness override must match retained canonical source');out=args.output;out.mkdir(parents=True,exist_ok=True)
    source_gates=source_gate_record(out/'source-gates')
    sources={a:source_record(getattr(args,a+'_source'),pin,a=='original') for a,pin in expected.items()}
    check_codegen_proof(args.codegen_proof,sources)
    check_control_sources(sources)
    (out/'archives').mkdir(exist_ok=True)
    cbuild=out/'c-build'; install=out/'c-install'
    ccommands=[['cmake','-S',str(args.original_source),'-B',str(cbuild),'-DCMAKE_BUILD_TYPE=Release','-DBUILD_SHARED_LIBS=OFF','-DBUILD_STATIC_LIBS=ON','-DBUILD_DEV_TOOLS=OFF','-DCMAKE_POSITION_INDEPENDENT_CODE=ON','-DCMAKE_EXPORT_COMPILE_COMMANDS=ON','-DCMAKE_INSTALL_PREFIX='+str(install)],['cmake','--build',str(cbuild),'--target','install','--parallel','4']]
    for i,c in enumerate(ccommands):command_run(c,out/f'c-build-{i}.log')
    c_lib=install/'lib/libta-lib.a';need(c_lib.is_file(),'missing C static library')
    bins=out/'bin';bins.mkdir(exist_ok=True); records={}
    common=['rustc','--edition=2021','-O','-C','lto=thin','-C','codegen-units=1','-Dwarnings','--check-cfg=cfg(c_reference,test)',str(args.harness),'-Csave-temps']
    for a in ARMS:
        binary=bins/a
        if a=='original':
            command=common+['--cfg','c_reference','-L','native='+str(c_lib.parent),'-l','static=ta-lib','-l','m','-o',str(binary)]
            cargo=None;lib=None
        else:
            target=out.parent/('sarext-window-targets-'+args.rust_version)/a;cargo=['cargo','build','--release','--locked','-vv','-p','ta-lib','--manifest-path',str(getattr(args,a+'_source')/'ta_codegen/output/rust/Cargo.toml'),'--target-dir',str(target)]
            command_run(cargo,out/(a+'-cargo.log'));lib=target/'release/libta_lib.rlib'
            retained=out/'libraries'/(a+'-libta_lib.rlib');retained.parent.mkdir(exist_ok=True);shutil.copyfile(lib,retained);need(sha(lib)==sha(retained),'rlib copy changed')
            command=common+['-L','dependency='+str(target/'release/deps'),'--extern','ta_lib='+str(retained),'-o',str(binary)]
        command_run(command,out/(a+'-harness-build.log'))
        test_binary=bins/(a+'-cli-tests');test_command=command[:-2]+['--test','-o',str(test_binary)]
        command_run(test_command,out/(a+'-cli-build.log'));command_run([test_binary,'--test-threads=1'],out/(a+'-cli-tests.log'))
        codegen=inspect_normal_elf(binary,out/'normal-codegen'/a,args.rust_version,a=='candidate')
        records[a]={'normal_codegen':codegen,'source':sources[a],'binary':str(binary),'binary_sha256':sha(binary),'cargo_command':cargo,'rustc_command':command,'test_command':test_command,'test_binary':str(test_binary),'test_binary_sha256':sha(test_binary)}
        if lib is not None:
            fp=out/'product-fingerprints'/a;fp.parent.mkdir(exist_ok=True);shutil.copytree(target/'release/.fingerprint',fp)
            records[a].update(library=str(lib),library_sha256=sha(lib),retained_library=str(retained),retained_library_sha256=sha(retained),product_fingerprints=file_inventory(fp))
    inputs=fixtures(out)
    scripts={name:sha(HERE/name) for name in ['sarext_window_benchmark.py','bench_sarext_window.rs','sarext_window_codegen.py']}
    proof=args.codegen_proof
    proof_dest=out/'codegen-proof';shutil.copytree(proof,proof_dest)
    source_archives={}
    for arm in ARMS:
        dest=out/'archives'/(arm+'-source.tar.gz')
        subprocess.run(['git','-C',str(getattr(args,arm+'_source')),'archive','--format=tar.gz','-o',str(dest),'HEAD'],check=True)
        source_archives[str(dest)]=sha(dest)
    p={'source_gates':source_gates,'source_archives':source_archives,'runtime':rt,'pins':expected,'arms':records,'inputs':inputs,'scripts':scripts,'normal_codegen_files':file_inventory(out/'normal-codegen'),'harness_sha256':sha(args.harness),'c_library':str(c_lib),'c_library_sha256':sha(c_lib),'c_commands':ccommands,'c_config_sha256':sha(cbuild/'CMakeCache.txt'),'codegen_proof':file_inventory(proof_dest)}
    (out/'build-provenance.json').write_text(json.dumps(p,indent=2)+'\n');verify(args,p)


def verify(args,p):
    need(p['source_gates']==source_gate_record(args.output/'source-gates'),'source gates changed')
    need(p['pins']==pins(args) and p['runtime']==runtime(args.rust_version),'source/runtime settings changed')
    check_codegen_proof(args.output/'codegen-proof',{a:r['source'] for a,r in p['arms'].items()})
    check_control_sources({a:r['source'] for a,r in p['arms'].items()})
    need(p['codegen_proof']==file_inventory(args.output/'codegen-proof'),'static proof inventory/hash changed')
    need(p['normal_codegen_files']==file_inventory(args.output/'normal-codegen'),'actual normal ELF CFG evidence changed')
    need(sha(args.harness)==p['harness_sha256'],'harness changed')
    for name,h in p['scripts'].items():need(sha(HERE/name)==h,'controller/support changed')
    for a,pin in p['pins'].items():
        r=p['arms'][a];need(source_record(getattr(args,a+'_source'),pin,a=='original')==r['source'],'source changed')
        for key in ['binary','test_binary']+([] if a=='original' else ['retained_library']):need(sha(r[key])==r[key+'_sha256'],'binary/library changed')
        if a!='original':need(r['product_fingerprints']==file_inventory(args.output/'product-fingerprints'/a),'wheel-time equivalent library fingerprints changed')
    for key in ['c_library']:need(sha(p[key])==p[key+'_sha256'],'C source/library changed')
    need(sha(args.output/'c-build/CMakeCache.txt')==p['c_config_sha256'],'C config changed')
    for f,h in p['codegen_proof'].items():need(sha(f)==h,'static proof changed')
    for f,h in p['source_archives'].items():need(sha(f)==h,'source archive changed')
    for r in p['inputs'].values():need(sha(r['path'])==r['sha256'],'fixture changed')


def shape(indicator,n,start=0,end=None):
    end=n-1 if end is None else end;b=max(start,0 if indicator=='add' else 1)
    return (0,0) if b>end else (b,end-b+1)


def record_specs(indicator,n,full):
    expected=[(64,*shape(indicator,64,s,e)) for _ in range(IEEE_SHAPES+1) for s,e in EDGES] if full else []
    return [*expected,(n,*shape(indicator,n))]


def capture(path,indicator,n,full):
    data=Path(path).read_bytes();at=0;selected=None;rows=[]
    for size,beg,count in record_specs(indicator,n,full):
        length=8*size+96;record=data[at:at+length]
        need(len(record)==length and record[:8]==b'SAROUT01','capture truncation/magic')
        need(struct.unpack('<QQQ',record[8:32])==(size,beg,count),'capture range differs')
        values=struct.unpack('<'+'Q'*(size+8),record[32:])
        need(values[count:]==(CANARY,)*(size+8-count),'physical tail overwritten (NaN bits remain raw)')
        rows.append({'n':size,'beg':beg,'count':count});selected=record;at+=length
    need(at==len(data),'capture extra records')
    return {'sha256':sha(path),'bytes':len(data),'records':len(rows),'ranges':rows,'selected':selected}


def compare_c_written(reference,actual,indicator,n,selection):
    """Only C/native WRITTEN NaNs may differ by representation; tails checked raw."""
    import numpy as np
    a=Path(reference).read_bytes();b=Path(actual).read_bytes();at=0;deltas=[]
    for index,(size,beg,count) in enumerate(record_specs(indicator,n,True)):
        length=8*size+96
        need(a[at:at+32]==b[at:at+32],'C/native header/range mismatch')
        av=np.frombuffer(a,dtype='<u8',count=count,offset=at+32)
        bv=np.frombuffer(b,dtype='<u8',count=count,offset=at+32)
        an=np.isnan(av.view('<f8'));bn=np.isnan(bv.view('<f8'))
        need(np.array_equal(an,bn),'C/native NaN positions differ')
        need(np.array_equal(av[~an],bv[~an]),'C/native finite/zero/Inf bits differ (no tolerance waiver)')
        for row in np.flatnonzero(an & (av!=bv)):
            deltas.append({'case':list(selection),'record':index,'out_index':int(row),'beg':beg,'count':count,
                           'C_bits':f'{int(av[row]):016x}','native_bits':f'{int(bv[row]):016x}'})
        # Even zero-count buffers and any NaN-tail poison remain raw exact.
        tail=at+32+count*8
        need(a[tail:at+length]==b[tail:at+length],'C/native raw tail mismatch')
        at+=length
    need(at==len(a)==len(b),'C/native record inventory differs')
    return deltas


def check_hits(selected,indicator,fixture,n,input_path):
    import numpy as np
    beg,count=shape(indicator,n);v=np.frombuffer(selected,dtype='<f8',count=count,offset=32)
    need(count>0 and np.isfinite(v).all(),'timed written range is empty/nonfinite')
    result={'written':count,'all_finite':True}
    if fixture=='reversal':
        if indicator=='sarext':
            need(np.any(v<0) and np.any(v>0),'reversal fixture lacks both SAREXT directions')
            result.update(negative=int(np.count_nonzero(v<0)),positive=int(np.count_nonzero(v>0)))
        elif indicator=='sar':
            d=Path(input_path).read_bytes();z=struct.unpack('<Q',d[16:24])[0]
            arrays=np.frombuffer(d,dtype='<f8',offset=24+z).reshape(4,n)
            low=arrays[2,beg:beg+count];high=arrays[1,beg:beg+count]
            long=v<=low;short=v>=high
            need(np.any(long) and np.any(short),'reversal fixture lacks SAR prices on both sides')
            result.update(long_side=int(long.sum()),short_side=int(short.sum()))
    return result


def parse(text,selection,arm,timed):
    rows=[read_json(l) for l in text.splitlines() if l.strip()];indicator,fixture,n,mode=selection
    need(len(rows)==(2 if timed else 1),'exact selected stdout inventory required')
    identity={'indicator':indicator,'fixture':fixture,'n':n,'mode':mode}
    for r in rows:need(all(type(r.get(k))is type(v) and r[k]==v for k,v in identity.items()),'selected metadata differs')
    need(type(rows[0].get('hardware_fma'))is bool,'hardware feature observation missing')
    if not timed:
        want={'kind':'capture',**identity,'edge_records':EDGE_RECORDS,'range_errors':3,
              'parameter_errors':{'sar':6,'sarext':24,'add':0}[indicator],
              'short_checks':0 if arm=='original' else 3,'hardware_fma':rows[0]['hardware_fma'],'timed':False}
        need(exact(rows[0],want),'untimed edges/invalid buffer coverage missing');return rows[0]
    need(exact(rows[0],{'kind':'validation',**identity,'beg':shape(indicator,n)[0],'count':shape(indicator,n)[1],
         'golden_verified':True,'hardware_fma':rows[0]['hardware_fma']}),'golden proof missing before timer')
    t=rows[1];need(set(t)=={'kind',*identity,'iterations','warmups','samples_ns'} and t['kind']=='case' and t['iterations']==ITERS[n] and type(t['iterations'])is int and t['warmups']==5 and type(t['warmups'])is int,'timing settings differ')
    samples=t['samples_ns'];need(isinstance(samples,list) and len(samples)==31 and all(type(x)in(int,float) and math.isfinite(x) and x>0 for x in samples),'31 finite positive samples required')
    return {**t,'hardware_fma':rows[0]['hardware_fma']}


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
    folder=args.output/'validation';folder.mkdir();goldens={};proofs=[];deltas=[];hardware=None
    for indicator,fixture,n in CASES:
        selection=(indicator,fixture,n,'typed');key='/'.join(map(str,selection));c_reference=None;native_reference=None;selected_reference=None
        for arm in ARMS:
            stem=folder/(key.replace('/','__')+'__'+arm);path=Path(str(stem)+'.bin')
            c=child_command(p,arm,selection,path);text,faults=execute(c,stem,30)
            parsed=parse(text,selection,arm,False);cap=capture(path,indicator,n,True)
            coverage=check_hits(cap['selected'],indicator,fixture,n,p['inputs'][f'{fixture}/{n}']['path'])
            if hardware is None:hardware=parsed['hardware_fma']
            need(parsed['hardware_fma']==hardware,'hardware dispatch observation changed')
            if arm=='original':
                c_reference=path;selected_reference=cap['selected']
                gold=args.output/'goldens'/(key.replace('/','__')+'.bin');gold.parent.mkdir(exist_ok=True);gold.write_bytes(selected_reference)
                goldens[key]={'path':str(gold),'sha256':sha(gold),'bytes':gold.stat().st_size}
            else:
                changes=compare_c_written(c_reference,path,indicator,n,selection)
                deltas.extend({'native_arm':arm,**row} for row in changes)
                if arm=='baseline':native_reference=(cap['sha256'],cap['bytes'])
                else:need((cap['sha256'],cap['bytes'])==native_reference,'full native before/candidate RAW capture mismatch')
            need(cap['selected']==selected_reference,'timed finite selected capture must be RAW C/native exact')
            cap.pop('selected');proofs.append({'arm':arm,'selection':selection,'command':c,'stdout':parsed,'capture':cap,'coverage':coverage,'whole_child_faults':faults})
    need(len(proofs)==45,'all45 global edge/main captures required')
    (args.output/'C-NaN-representation-deltas.json').write_text(json.dumps(deltas,indent=2)+'\n')
    record={'completed_before_any_timing':True,'checks':proofs,'goldens':goldens,'C_nan_representation_deltas':len(deltas),
            'C_policy':'written NaN positions exact; all nonNaN bits and all physical tails raw exact; native before/candidate fully raw exact',
            'hardware_fma':hardware}
    (args.output/'capture-validation.json').write_text(json.dumps(record,indent=2)+'\n');return record


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
                name=before+'_vs_'+after;row={'before_process_medians_ns':a,'after_process_medians_ns':b,'before_median_ns':statistics.median(a),'after_median_ns':statistics.median(b),'paired_ratios':[x/y for x,y in zip(a,b)],'median_paired_ratio':statistics.median(x/y for x,y in zip(a,b)),'ratio_envelope':[min(a)/max(b),max(a)/min(b)],'after_latency_percent':pct,'after_faster_rounds':sum(x>y for x,y in zip(a,b)),'is_add_control':indicator=='add','c_arm_is_direct_public_call':True}
                pairs[name]=row
                if pct>0:negative.append({'case_mode':key,'comparison':name,**row})
            results[key]=pairs
    return results,negative


def measure(args,p,validation):
    need(validation['completed_before_any_timing'] and len(validation['checks'])==45,'all correctness gates must precede timing')
    folder=args.output/'children';folder.mkdir();rows=[];started=time.monotonic()
    for indicator,fixture,n in CASES:
        for mode in MODES:
            selection=(indicator,fixture,n,mode);key='/'.join(map(str,selection));golden=validation['goldens'][key];need(sha(golden['path'])==golden['sha256'],'golden changed')
            for index,order in enumerate(ORDERS,1):
                for arm in order:
                    need(time.monotonic()-started<600,'600s measurement budget exceeded; partial data retained')
                    stem=folder/(key.replace('/','__')+f'__{index}__{arm}');path=Path(str(stem)+'.bin');c=child_command(p,arm,selection,path,golden['path']);text,faults=execute(c,stem,30);r=parse(text,selection,arm,True);cap=capture(path,indicator,n,False);cap.pop('selected');need(r['hardware_fma']==validation['hardware_fma'],'runtime dispatch feature changed');need(cap['sha256']==golden['sha256'] and cap['bytes']==golden['bytes'],'selected bytes differ')
                    proof={'key':key,'arm':arm,'round':index,'command':c,'capture':cap,'golden':golden,'whole_child_faults':faults,'samples_ns':r['samples_ns']};Path(str(stem)+'-proof.json').write_text(json.dumps(proof,indent=2)+'\n');path.unlink();proof['duplicate_deleted_after_proof']=True;rows.append(proof)
                    with (args.output/'completed-children.jsonl').open('a') as ledger:ledger.write(json.dumps(proof)+'\n')
    need(time.monotonic()-started<=600,'600s measurement budget exceeded')
    need(len(rows)==540 and sum(len(r['samples_ns'])for r in rows)==16740,'complete540children/16740samples required');results,negatives=summarize(rows)
    return {'rows':rows,'results':results,'negative_cases':negatives,'orders':ORDERS,'children':540,'samples':16740,'elapsed_seconds':time.monotonic()-started,'limits':['This job alone compares C0.8.3 with development Rust0.8.4 baseline CCD/candidate at its recorded compiler/profile. No ratios are pooled across1.90/1.97 jobs.','Library MSRV1.88 performance is unverified; root development toolchain pin1.97 is not an MSRV claim.','Public typed calls only; no abstract/Python/Polars adapter arm is measured.','Normal runtime hardware dispatch is preserved; no private scalar/FMA entry or force knob is used. Scalar codegen evidence is not a scalar runtime speed claim.','All calls include selected driver dispatch and range assertions. Fresh selected processes isolate sibling workloads, not allocator/golden I/O history.','C/native written NaN positions are strict; payload/sign deltas are all retained. NonNaN bits, signedzero/Inf/ranges/tails and ALL native before/candidate bits remain exact.','One-CPU sampled envelopes are descriptive, not confidence intervals; inner samples correlate and shared-runner effects remain.','Whole-child faults include startup/fixtures/golden I/O/warmups, not allocator-only events.','All slower medians, ADD controls and both toolchain outcomes remain reportable; no automatic publication or retention.']}


def write_report(output,report):
    lines=['# SAR/SAREXT public kernel comparison (one compiler job)','',*report['limits'],'','|Case/mode|Comparison|Before ns|After ns|After latency %|Paired before/after (>1 faster)|Descriptive before/after envelope|Faster rounds|','|---|---|---:|---:|---:|---:|---|---:|']
    for case,pairs in report['results'].items():
        for name,r in pairs.items():
            lines.append(f"|{case}|{name}|{r['before_median_ns']:.3f}|{r['after_median_ns']:.3f}|{r['after_latency_percent']:+.3f}|{r['median_paired_ratio']:.5f}|{r['ratio_envelope']}|{r['after_faster_rounds']}/12|")
    (output/'comparison.md').write_text('\n'.join(lines)+'\n')


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    for a in ARMS:parser.add_argument('--'+a+'-source',type=Path,required=True)
    parser.add_argument('--rust-version',choices=('1.90.0','1.97.0'),required=True);parser.add_argument('--candidate-commit',required=True);parser.add_argument('--output',type=Path,required=True);parser.add_argument('--codegen-proof',type=Path,required=True);parser.add_argument('--harness',type=Path,default=HERE/'bench_sarext_window.rs');parser.add_argument('--build-only',action='store_true');a=parser.parse_args(argv);pins(a)
    for key,v in vars(a).copy().items():
        if isinstance(v,Path):setattr(a,key,v.resolve())
    a.output.mkdir(parents=True,exist_ok=True)
    if a.build_only:build(a);return
    p=read_json((a.output/'build-provenance.json').read_text());verify(a,p);previous=set(os.sched_getaffinity(0));need(previous,'CPU affinity required')
    try:
        os.sched_setaffinity(0,{min(previous)});validation=prepare(a,p);report=measure(a,p,validation);verify(a,p);report.update(provenance=p,validation=validation,affinity=sorted(os.sched_getaffinity(0)));(a.output/'summary.json').write_text(json.dumps(report,indent=2)+'\n');(a.output/'negative-cases.json').write_text(json.dumps(report['negative_cases'],indent=2)+'\n');write_report(a.output,report)
    finally:os.sched_setaffinity(0,previous)

if __name__=='__main__':main()
