"""Pinned upstream HMA weights A/B; exact primary captures precede timing."""
import argparse
import gzip
import hashlib
import json
import math
import os
from pathlib import Path
import platform
import shutil
import statistics
import struct
import subprocess
import sys
import tarfile
import time

BASELINE = '4334163d3a1f5019aa9051342316b936a4dfb994'
CANDIDATE = '5da9e8d43333c13b5f46f30efe8460de12b1f68b'
C_COMMIT = 'b2bbc26d41ec80823c8bffb0cc436a97f29911cc'
C_ARCHIVE = 'talib-sys/vendor/ta-lib-0.8.1-src.tar.gz'
C_SHA = 'ec59ccd88c0c77f618587d858787c8f9d06c40460a09d66751926f6fd670f985'
REGISTRY = {'ta-lib': ('0.8.3', '4da552ae932721218c73cf1124610b0ce3d5f27cc1a62342debd370cd161d922'),
            'ta-lib-dispatch': ('0.1.2', '726f5cc1f53b7994288221583f9fb7ca535bae2b349b738a01adc75c3bd9ee41')}
SIDES = ('baseline', 'candidate')
BACKENDS = ('current', 'registry083', 'originalc081')
SIZES = (20, 100, 512, 1000, 10000, 1000000)
CASES = {f'{mode}/p20/{n}' for mode in ('hma','sma_control') for n in SIZES}
CASES |= {'hma/p2703/10000','hma/p2704/10000','hma/p100000/1000000'}
PERIODS = (1,2,3,4,9,10,15,16,17,20,25,26,81,82,100,101,2703,2704,99999,100000)
VALIDATION = {f'validation/hma/finite/p{p}/n{n}/start0' for p in PERIODS for n in (1,2,3,5,10,20,21,100,1000,10000,1000000)}
PATTERNS = ('zero','negative_zero','constant','ramp','reverse','alternating','head_nan','interior_nan','head_inf','interior_negative_inf')
VALIDATION |= {f'validation/hma/{pattern}/p{p}/n1000/start{start}' for pattern in PATTERNS for p in (1,2,3,4,20,100) for start in (0,25,500)}
VALIDATION |= {f'validation/hma/finite/p20/n1000/start{start}' for start in (1,19,20,25,99,100,500)}
VALIDATION |= {f'validation/hma/finite/p20/n{n}/start0' for n in (22,23,53,54,55,98,99,178,179,180)}
TIMED_KEYS = {(backend,name) for backend in BACKENDS for name in CASES}
VALIDATION_KEYS = {(backend,name) for backend in BACKENDS for name in VALIDATION}
KEYS = TIMED_KEYS | VALIDATION_KEYS
CANARY = 0x7ff80000000055aa

FLAGS = {'RUSTFLAGS':'', 'CARGO_ENCODED_RUSTFLAGS':'', 'CARGO_PROFILE_RELEASE_LTO':'thin',
         'CARGO_PROFILE_RELEASE_CODEGEN_UNITS':'1', 'CARGO_PROFILE_RELEASE_DEBUG':'false'}


def sha256(path):
    digest=hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda:f.read(1048576),b''): digest.update(block)
    return digest.hexdigest()


def run(command, log, cwd=None, env=None):
    with Path(log).open('a') as f:
        f.write(json.dumps(list(map(str,command)))+'\n');f.flush()
        subprocess.run(list(map(str,command)),cwd=cwd,env=env,stdout=f,stderr=subprocess.STDOUT,check=True)


def git_record(root,expected,old_c=False):
    root=Path(root).resolve()
    commit=subprocess.check_output(['git','-C',str(root),'rev-parse','HEAD'],text=True).strip()
    if commit!=expected or subprocess.check_output(['git','-C',str(root),'status','--porcelain']):
        raise ValueError('source must be clean and match its immutable full commit pin')
    paths=set()
    if old_c:
        paths={C_ARCHIVE,'talib-sys/build.rs','Cargo.lock'}
    else:
        for folder in ('ta_codegen/output/rust','ta_codegen/generator/src','ta_codegen/input/hma'):
            for p in (root/folder).rglob('*'):
                rel=p.relative_to(root)
                if p.is_file() and not {'target','.git'}.intersection(rel.parts) and p.suffix in ('.rs','.toml','.lock','.c','.h','.yaml','.yml'):
                    paths.add(rel.as_posix())
        paths.update(('ta_codegen/generator/Cargo.toml','ta_codegen/generator/Cargo.lock'))
    files={name:sha256(root/name) for name in sorted(paths)}
    if not old_c and not {'ta_codegen/input/hma/hma.c','ta_codegen/output/rust/Cargo.toml','ta_codegen/output/rust/library/Cargo.toml'}<=files.keys():raise ValueError('missing HMA/compiled Rust source')
    return {'commit':commit,'clean':True,'source_files':files,
            'source_sha256':hashlib.sha256(json.dumps(files,sort_keys=True,separators=(',',':')).encode()).hexdigest()}


def runtime_record():
    rust=subprocess.check_output(['rustc','--version','--verbose'],text=True)
    if not rust.startswith('rustc 1.97.0 '):raise ValueError('Rust 1.97.0 required')
    if not platform.python_version().startswith('3.12.') or sys.platform!='linux':raise ValueError('Linux/Python3.12 required')
    if any(os.environ.get(k)!=v for k,v in FLAGS.items()):raise ValueError('identical portable thin-LTO/codegen1 flags required')
    cpu=next((s.split(':',1)[1].strip() for s in Path('/proc/cpuinfo').read_text().splitlines() if s.startswith('model name')),'unknown')
    return {'cpu':cpu,'platform':platform.platform(),'python':platform.python_version(),'rustc':rust,
            'cargo':subprocess.check_output(['cargo','--version'],text=True),
            'cc':subprocess.check_output(['cc','--version'],text=True),
            'cmake':subprocess.check_output(['cmake','--version'],text=True),
            'environment':{k:os.environ.get(k) for k in (*FLAGS,'RUSTUP_TOOLCHAIN','CARGO_BUILD_JOBS')}}


def input_file(output):
    import numpy as np
    if np.__version__!='2.5.3':raise ValueError('NumPy 2.5.3 required for identical CI input')
    values=100+np.cumsum(np.random.default_rng(260126).normal(0,.1,1000000))
    path=output/'close-seed260126-f64le.bin';values.astype('<f8').tofile(path)
    return {'path':str(path),'sha256':sha256(path),'bytes':path.stat().st_size,'seed':260126,
            'numpy':np.__version__,'values':1000000,'dtype':'<f8','minimum':float(values.min()),'maximum':float(values.max())}


def registry_helper(output):
    helper=output/'registry-helper';helper.mkdir(exist_ok=True)
    (helper/'Cargo.toml').write_text('[package]\nname="hma-registry-reference"\nversion="0.0.0"\nedition="2021"\n[lib]\npath="lib.rs"\n[dependencies]\nta-lib="=0.8.3"\n[profile.release]\nlto="thin"\ncodegen-units=1\n')
    (helper/'lib.rs').write_text('pub fn reference_marker() {}\n')
    lock='version = 4\n\n[[package]]\nname = "hma-registry-reference"\nversion = "0.0.0"\ndependencies = ["ta-lib"]\n'
    for name,(version,digest) in REGISTRY.items():
        lock+=f'\n[[package]]\nname = "{name}"\nversion = "{version}"\nsource = "registry+https://github.com/rust-lang/crates.io-index"\nchecksum = "{digest}"\n'
        if name=='ta-lib':lock+='dependencies = ["ta-lib-dispatch"]\n'
    (helper/'Cargo.lock').write_text(lock)
    return helper



def registry_source_record(source,archive,expected,prefix):
    if sha256(archive)!=expected:raise ValueError('registry archive checksum mismatch')
    files={}
    with tarfile.open(archive) as tar:
        for entry in tar:
            path=Path(entry.name)
            if path.is_absolute() or '..' in path.parts or not path.parts or path.parts[0]!=prefix:raise ValueError('invalid registry archive path')
            if entry.isdir():continue
            if not entry.isfile():raise ValueError('registry archive must contain ordinary source files')
            relative=Path(*path.parts[1:])
            if not relative.parts:raise ValueError('invalid registry source file')
            digest=hashlib.sha256(tar.extractfile(entry).read()).hexdigest()
            if sha256(source/relative)!=digest:raise ValueError('registry source modified: '+str(relative))
            files[relative.as_posix()]=digest
    if not {'Cargo.toml','src/lib.rs'}<=files.keys():raise ValueError('registry archive lacks compiled source')
    return files


def build(args):
    runtime=runtime_record(); sources={s:git_record(getattr(args,s+'_source'),p) for s,p in zip(SIDES,(BASELINE,CANDIDATE))}
    c_record=git_record(args.c_source,C_COMMIT,True);archive=args.c_source/C_ARCHIVE
    if sha256(archive)!=C_SHA:raise ValueError('old-C vendor archive checksum mismatch')
    archives=args.output/'archives';archives.mkdir(exist_ok=True);shutil.copy2(archive,archives/archive.name)
    croot=args.output/'old-c-source';croot.mkdir(exist_ok=True)
    with tarfile.open(archive) as tar:tar.extractall(croot,filter='data')
    extracted=croot/'ta-lib-0.8.1';cbuild=args.output/'old-c-build';install=args.output/'old-c-install'
    commands=[['cmake','-S',str(extracted),'-B',str(cbuild),'-DCMAKE_BUILD_TYPE=Release','-DBUILD_SHARED_LIBS=OFF','-DBUILD_STATIC_LIBS=ON','-DBUILD_DEV_TOOLS=OFF','-DCMAKE_POSITION_INDEPENDENT_CODE=ON','-DCMAKE_EXPORT_COMPILE_COMMANDS=ON','-DCMAKE_INSTALL_PREFIX='+str(install)],
              ['cmake','--build',str(cbuild),'--target','install','--parallel','4']]
    for cmd in commands:run(cmd,args.output/'old-c-build.log')
    c_lib=install/'lib/libta-lib.a'
    if not c_lib.is_file():raise ValueError('old C static archive missing')
    shutil.copy2(cbuild/'CMakeCache.txt',args.output/'old-c-cmake-cache.txt')
    shutil.copy2(cbuild/'compile_commands.json',args.output/'old-c-compile-commands.json')
    helper=registry_helper(args.output);lock_before=sha256(helper/'Cargo.lock');target=args.output/'target-registry'
    run(['cargo','build','--locked','--release','--manifest-path',helper/'Cargo.toml','--target-dir',target],args.output/'registry-build.log')
    if sha256(helper/'Cargo.lock')!=lock_before:raise ValueError('registry dependency lock changed')
    metadata=json.loads(subprocess.check_output(['cargo','metadata','--locked','--format-version=1','--manifest-path',str(helper/'Cargo.toml')],text=True))
    registry={}
    for name,(version,digest) in REGISTRY.items():
        package=next(p for p in metadata['packages'] if p['name']==name)
        if package['version']!=version or package['source']!='registry+https://github.com/rust-lang/crates.io-index':raise ValueError('registry package identity mismatch')
        source=Path(package['manifest_path']).parent
        cached=list((source.parents[2]/'cache').glob('*/'+name+'-'+version+'.crate'))
        if len(cached)!=1:raise ValueError('registry archive missing or ambiguous')
        files=registry_source_record(source,cached[0],digest,name+'-'+version)
        shutil.copy2(cached[0],archives/cached[0].name)
        registry[name]={'version':version,'archive_sha256':digest,'source_files':files}
    (args.output/'registry-metadata.json').write_text(json.dumps(metadata,indent=2)+'\n')
    registry_rlibs=list((target/'release/deps').glob('libta_lib-*.rlib'))
    if len(registry_rlibs)!=1:raise ValueError('ambiguous registry library')
    registry_rlib=registry_rlibs[0];inputs=input_file(args.output)
    provenance={'runtime':runtime,'harness_sha256':sha256(args.harness),'controller_sha256':sha256(__file__),
                'input':inputs,'old_c':{'source':c_record,'archive_sha256':C_SHA,'commands':commands,'library':str(c_lib),'library_sha256':sha256(c_lib)},
                'registry':registry,'registry_lock_sha256':lock_before,'registry_library':str(registry_rlib),'registry_library_sha256':sha256(registry_rlib)}
    env=os.environ.copy();env.update(HMA_CURRENT_VERSION='0.8.4',HMA_REGISTRY_VERSION='0.8.3')
    for side in SIDES:
        root=getattr(args,side+'_source');out=args.output/('target-'+side);binary=args.output/'bin'/side;binary.parent.mkdir(exist_ok=True)
        metadata=json.loads(subprocess.check_output(['cargo','metadata','--locked','--no-deps','--format-version=1','--manifest-path',str(root/'ta_codegen/output/rust/Cargo.toml')],text=True))
        package=next(p for p in metadata['packages'] if p['name']=='ta-lib')
        if package['version']!='0.8.4' or package['source']is not None or Path(package['manifest_path']).resolve()!=root/'ta_codegen/output/rust/library/Cargo.toml':raise ValueError('current upstream crate runtime identity mismatch')
        (args.output/(side+'-cargo-metadata.json')).write_text(json.dumps(metadata,indent=2)+'\n')
        commands=[['cargo','build','--release','--locked','-p','ta-lib','--manifest-path',str(root/'ta_codegen/output/rust/Cargo.toml'),'--target-dir',str(out)],
                  ['rustc','--edition=2021','-O','-C','lto=thin','-C','codegen-units=1',str(args.harness),'-L','dependency='+str(out/'release/deps'),'-L','dependency='+str(target/'release/deps'),
                   '--extern','ta_lib='+str(out/'release/libta_lib.rlib'),'--extern','ta_lib_registry='+str(registry_rlib),'-L','native='+str(c_lib.parent),'-l','static=ta-lib','-l','m','-o',str(binary)]]
        for cmd in commands:run(cmd,args.output/(side+'-build.log'),cwd=root,env=env)
        if git_record(root,BASELINE if side=='baseline' else CANDIDATE)!=sources[side]:raise ValueError('upstream source changed during build')
        if side=='candidate':
            test_binary=args.output/'bin/harness-cli-tests'
            test_command=commands[1][:-2]+['--test','-o',str(test_binary)]
            run(test_command,args.output/'harness-cli-tests.log',cwd=root,env=env)
            run([test_binary],args.output/'harness-cli-tests.log')
            provenance['cli_tests']={'commands':[test_command,[str(test_binary)]],'binary':str(test_binary),'binary_sha256':sha256(test_binary)}
        provenance[side]={'source':sources[side],'commands':commands,'binary':str(binary),'binary_sha256':sha256(binary),'library':str(out/'release/libta_lib.rlib'),'library_sha256':sha256(out/'release/libta_lib.rlib'),'package_version':package['version']}
    if sha256(args.harness)!=provenance['harness_sha256']:raise ValueError('harness changed during build')
    (args.output/'build-provenance.json').write_text(json.dumps(provenance,indent=2)+'\n')




def stable_metadata(metadata):
    return {key:value for key,value in metadata.items() if key not in ('capture_only','capture_written')}


def harness_command(binary,capture=None,capture_only=False):
    if capture_only and capture is None:raise ValueError('capture-only mode requires an output path')
    command=[str(binary),'31']
    if capture is not None:command.append(str(capture))
    if capture_only:command.append('--capture-only')
    return command


def expected_case(name):
    parts=name.split('/')
    if name in VALIDATION:
        pattern=parts[2];period=int(parts[3][1:]);n=int(parts[4][1:]);start=int(parts[5][5:]);sma=False
    elif name in CASES:
        pattern='finite';period=int(parts[1][1:]);n=int(parts[2]);start=0;sma=parts[0]=='sma_control'
    else:raise ValueError('unknown fixed HMA case')
    lookback=period-1 if sma else period+math.isqrt(period)-2
    beg=max(start,lookback)
    if beg>=n:beg=count=0
    else:count=n-beg
    return {'n':n,'beg':beg,'count':count,'period':period,'start':start,'pattern':pattern,'sma_control':sma}


def expected_range(name):
    case=expected_case(name)
    return case['n'],case['beg'],case['count']


def parse_records(content,capture_only,expected_os="linux"):
    metadata=None;parity={};validation={};cases={};seen_timing=False
    for line in content.splitlines():
        if not line.strip():continue
        row=json.loads(line)
        if not isinstance(row,dict):raise ValueError('records must be JSON objects')
        kind=row.get('kind')
        if kind=='metadata':
            if metadata is not None:raise ValueError('duplicate metadata')
            metadata=row;continue
        if metadata is None:raise ValueError('metadata must precede validation/parity/timing')
        key=(row.get('backend'),row.get('case'))
        if key not in KEYS:raise ValueError('unexpected fixed case/backend')
        case=expected_case(key[1]);n,beg,count=(case[k] for k in ('n','beg','count'))
        if kind in ('parity','validation'):
            table=parity if kind=='parity' else validation
            expected=TIMED_KEYS if kind=='parity' else VALIDATION_KEYS
            if key not in expected or seen_timing or key in table:raise ValueError('unique fixed validation/parity must precede timing')
            if type(row.get('count'))is not int or row['count']!=count:raise ValueError('parity range count mismatch')
            counters=[row.get(k) for k in ('exact','within_tolerance','nonfinite_same')]
            if any(type(x)is not int or x<0 for x in counters) or sum(counters)!=count or type(row.get('signed_zero'))is not int or row['signed_zero']!=0:raise ValueError('invalid parity counters or signed zero mismatch')
            if key[0]=='current' and counters!=[count,0,0]:raise ValueError('current parity must be exact')
            if kind=='parity' and counters[2]!=0:raise ValueError('finite timed inputs produced nonfinite differences')
            for field in ('max_abs','max_scaled'):
                if type(row.get(field))not in (int,float) or not math.isfinite(row[field]) or row[field]<0:raise ValueError('invalid differential magnitude')
            if row['max_scaled']>4e-15:raise ValueError('reference tolerance exceeded')
            table[key]=row
        elif kind=='case':
            seen_timing=True
            if capture_only or key not in TIMED_KEYS or set(parity)!=TIMED_KEYS or set(validation)!=VALIDATION_KEYS or key in cases:raise ValueError('all fixed validation/parity must finish before timing')
            expected={'n':n,'beg':beg,'count':count,'period':case['period'],'start':case['start'],'iterations':max(100000//n,1),'warmups':5,'empty_range_control':count==0}
            if any(type(row.get(k))is not type(v) or row[k]!=v for k,v in expected.items()):raise ValueError('unexpected case settings')
            samples=row.get('samples_ns')
            if not isinstance(samples,list) or len(samples)!=31 or any(type(x)not in (int,float) or not math.isfinite(x) or x<=0 for x in samples):raise ValueError('31 positive finite samples required')
            cases[key]=row
        else:raise ValueError('unknown record kind')
    expected={'format':1,'cases':15,'validation_cases':417,'backends':list(BACKENDS),'canary_bits':'7ff80000000055aa','output_prefix':1,'warmups':5,'repeats':31,'capture_only':capture_only,'capture_written':capture_only,'registry_version':'0.8.3','current_version':'0.8.4','capture_records':1296,'tolerance_relative':4e-15,'tolerance_floor':'max_abs_finite_input'}
    if metadata is None or any(type(metadata.get(k))is not type(v) or metadata[k]!=v for k,v in expected.items()):raise ValueError('metadata/runtime/fixed inventory mismatch')
    if metadata.get('os')!=expected_os or type(metadata.get('arch'))is not str or not metadata['arch'] or type(metadata.get('c_version'))is not str or not (metadata['c_version']=='0.8.1' or metadata['c_version'].startswith('0.8.1 (')):raise ValueError('unexpected platform or C runtime')
    if set(parity)!=TIMED_KEYS or set(validation)!=VALIDATION_KEYS or set(cases)!=(set() if capture_only else TIMED_KEYS):raise ValueError('complete fixed backend/case inventories required')
    return {'metadata':metadata,'validation':{b+'/'+c:v for (b,c),v in validation.items()},'parity':{b+'/'+c:v for (b,c),v in parity.items()},'cases':{b+'/'+c:v for (b,c),v in cases.items()}}


def capture_record(path):
    records={};written=0
    with Path(path).open('rb') as f:
        if f.read(8)!=b'HMAWGT01':raise ValueError('capture magic mismatch')
        while length:=f.read(4):
            if len(length)!=4:raise ValueError('truncated capture name length')
            size=struct.unpack('<I',length)[0]
            if not 1<=size<=200:raise ValueError('invalid capture name length')
            name=f.read(size).decode();header=f.read(32)
            if len(header)!=32:raise ValueError('truncated capture header')
            n,beg,count,outlen=struct.unpack('<QQQQ',header);backend,case_name=name.split('/',1)
            if (backend,case_name)not in KEYS or name in records or (n,beg,count)!=expected_range(case_name) or outlen!=n+8:raise ValueError('capture inventory/range mismatch')
            body=f.read(outlen*8)
            if len(body)!=outlen*8:raise ValueError('truncated capture values')
            guard=struct.pack('<Q',CANARY)
            if body[:8]!=guard or body[(1+count)*8:]!=guard*(outlen-1-count):raise ValueError('capture prefix/tail guard modified')
            case=expected_case(case_name)
            finite_required=case['pattern'] not in ('head_nan','interior_nan','head_inf','interior_negative_inf')
            for (bits,) in struct.iter_unpack('<Q',body[8:(1+count)*8]):
                if bits==CANARY:raise ValueError('written prefix contains unwritten canary')
                if finite_required and bits&0x7ff0000000000000==0x7ff0000000000000:raise ValueError('finite-input case has nonfinite written output')
            records[name]={'n':n,'beg':beg,'count':count,'outlen':outlen};written+=count
    if set(records)!={b+'/'+c for b,c in KEYS}:raise ValueError('capture missing backend/case')
    return {'sha256':sha256(path),'bytes':Path(path).stat().st_size,'records':len(records),'written_values':written,'output_prefix':1,'all_prefix_tail_guards_verified':True,'written_canary_absence_verified':True}


def verify(args,p):
    if runtime_record()!=p['runtime'] or sha256(args.harness)!=p['harness_sha256'] or sha256(__file__)!=p['controller_sha256']:raise ValueError('runtime/harness/controller changed')
    for side,pin in zip(SIDES,(BASELINE,CANDIDATE)):
        r=p[side]
        if git_record(getattr(args,side+'_source'),pin)!=r['source']:raise ValueError('source changed')
        for key in ('binary','library'):
            if sha256(r[key])!=r[key+'_sha256']:raise ValueError('primary binary/library changed')
    if git_record(args.c_source,C_COMMIT,True)!=p['old_c']['source']:raise ValueError('old C source changed')
    for path,digest in ((p['input']['path'],p['input']['sha256']),(p['old_c']['library'],p['old_c']['library_sha256']),(p['registry_library'],p['registry_library_sha256'])):
        if sha256(path)!=digest:raise ValueError('shared input/reference library changed')


def summarize(runs):
    if any(len(runs[s])!=12 for s in SIDES):raise ValueError('exact12 paired processes required')
    rows={}
    for key in sorted(runs['baseline'][0]['cases']):
        old=[statistics.median(r['cases'][key]['samples_ns']) for r in runs['baseline']]
        new=[statistics.median(r['cases'][key]['samples_ns']) for r in runs['candidate']]
        ratios=[a/b for a,b in zip(old,new)]
        rows[key]={'baseline_process_medians_ns':old,'candidate_process_medians_ns':new,'baseline_median_ns':statistics.median(old),'candidate_median_ns':statistics.median(new),
                   'paired_ratios':ratios,'median_paired_ratio':statistics.median(ratios),'ratio_envelope':[min(old)/max(new),max(old)/min(new)],
                   'candidate_latency_percent':(statistics.median(new)/statistics.median(old)-1)*100,'candidate_faster_pairs':sum(x>1 for x in ratios),
                   'is_reference_backend':not key.startswith('current/'),'is_unchanged_control':('/sma_control/' in key or expected_case(key.split('/',1)[1])['count']==0)}
    return rows



def reference_comparisons(runs):
    result={}
    for side in SIDES:
        result[side]={}
        for reference in BACKENDS[1:]:
            cases={}
            for name in sorted(CASES):
                current=[statistics.median(r['cases']['current/'+name]['samples_ns']) for r in runs[side]]
                control=[statistics.median(r['cases'][reference+'/'+name]['samples_ns']) for r in runs[side]]
                ratios=[a/b for a,b in zip(control,current)]
                cases[name]={'current_process_medians_ns':current,'reference_process_medians_ns':control,
                             'current_median_ns':statistics.median(current),'reference_median_ns':statistics.median(control),
                             'reference_over_current_paired_ratios':ratios,'median_paired_ratio':statistics.median(ratios),
                             'reference_over_current_envelope':[min(control)/max(current),max(control)/min(current)],
                             'current_latency_percent':(statistics.median(current)/statistics.median(control)-1)*100,
                             'current_faster_processes':sum(x>1 for x in ratios)}
            result[side][reference]=cases
    return result


def measure(args):
    p=json.loads((args.output/'build-provenance.json').read_text());verify(args,p)
    original=set(os.sched_getaffinity(0));affinity=sorted(original)[:1]
    if not affinity:raise ValueError('one CPU affinity required')
    env=os.environ.copy();env['HMA_CLOSE_BIN']=p['input']['path'];runs={s:[] for s in SIDES};captures={};order=[];validations={};metadata=None
    try:
        os.sched_setaffinity(0,affinity)
        for side in SIDES:
            path=args.output/(side+'.bin');captures[side]=path
            result=subprocess.run(harness_command(p[side]['binary'],path,True),check=True,capture_output=True,text=True,env=env)
            (args.output/(side+'-validation.jsonl')).write_text(result.stdout)
            row=parse_records(result.stdout,True);validations[side]={'records':row,'capture':capture_record(path)}
            current=stable_metadata(row['metadata'])
            if metadata is not None and current!=metadata:raise ValueError('capture runtime differs between primary builds')
            metadata=current
        a,b=[validations[s]['capture'] for s in SIDES]
        if not a['bytes'] or a['bytes']!=b['bytes'] or a['sha256']!=b['sha256']:raise ValueError('primary full capture differs; no tolerance waiver')
        (args.output/'capture-validation.json').write_text(json.dumps({'completed_before_any_timing':True,'primary_exact':True,'validation':validations},indent=2)+'\n')
        for pair in range(12):
            for side in SIDES if pair%2==0 else reversed(SIDES):
                label=f'{side}-{pair+1}';order.append(label);print(time.strftime('%H:%M:%S'),label,flush=True)
                result=subprocess.run(harness_command(p[side]['binary']),check=True,capture_output=True,text=True,env=env)
                (args.output/(label+'.jsonl')).write_text(result.stdout);row=parse_records(result.stdout,False)
                if stable_metadata(row['metadata'])!=metadata:raise ValueError('timed runtime changed')
                runs[side].append(row)
        verify(args,p)
    finally:os.sched_setaffinity(0,original)
    rows=summarize(runs);negatives={k:v for k,v in rows.items() if v['candidate_latency_percent']>0};references=reference_comparisons(runs)
    reference_negatives=[{'side':side,'reference':reference,'case':name,**value} for side,groups in references.items() for reference,cases in groups.items() for name,value in cases.items() if value['current_latency_percent']>0]
    report={'run_url':f"https://github.com/{os.environ.get('GITHUB_REPOSITORY','local')}/actions/runs/{os.environ.get('GITHUB_RUN_ID','local')}",
            'build_provenance':p,'pairs':12,'samples_per_process':31,'warmups':5,'affinity':affinity,'order':order,'harness_metadata':metadata,
            'source_scope':'Scalar weight multiplier temporaries change from usize to f64; no HmaStreamState layout, storage, or signature change is claimed.','capture_validation':validations,'results':rows,'negative_cases':negatives,'reference_comparisons':references,'reference_slower_cases':reference_negatives,
            'limitations':'Primary comparison is before433 vs candidate5da within one runner. Registry083 and C081 references are unchanged and timed inside each process, not extra independent primary samples. Cross-version tolerance is separate from mandatory exact primary capture. Inner samples are correlated; ranges are descriptive, not confidence intervals. No formal multiplicity-adjusted inference or allocator attribution. Reference backends run in fixed current/registry/C order inside each process: their ratios are diagnostic Core comparisons, not consumer Polars speedups or fully counterbalanced cross-backend comparisons.'}
    (args.output/'summary.json').write_text(json.dumps(report,indent=2)+'\n')
    lines=['# HMA weights same-runner comparison','',report['limitations'],'','| Backend/case | Before ns | After ns | Latency change | Paired ratio | Envelope | Faster pairs |','| --- | ---: | ---: | ---: | ---: | --- | ---: |']
    for name,r in rows.items():
        lo,hi=r['ratio_envelope'];lines.append(f"| {name} | {r['baseline_median_ns']:.2f} | {r['candidate_median_ns']:.2f} | {r['candidate_latency_percent']:+.3f}% | {r['median_paired_ratio']:.5f} | {lo:.5f}–{hi:.5f} | {r['candidate_faster_pairs']}/12 |")
    (args.output/'comparison.md').write_text('\n'.join(lines)+'\n')
    (args.output/'negative-cases.json').write_text(json.dumps({'before_after':negatives,'current_slower_than_references':reference_negatives},indent=2)+'\n')
    reference_lines=['# Same-process Core reference comparisons','','Fixed backend order is current, registry083, originalc081. These diagnostic Core ratios do not measure Polars adapter/grouping costs.','','| Primary side | Reference | Case | Current latency change | Reference/current paired ratio | Range | Current faster processes |','| --- | --- | --- | ---: | ---: | --- | ---: |']
    for side,groups in references.items():
        for reference,cases in groups.items():
            for name,r in cases.items():
                lo,hi=r['reference_over_current_envelope'];reference_lines.append(f"| {side} | {reference} | {name} | {r['current_latency_percent']:+.3f}% | {r['median_paired_ratio']:.5f} | {lo:.5f}–{hi:.5f} | {r['current_faster_processes']}/12 |")
    (args.output/'reference-comparisons.md').write_text('\n'.join(reference_lines)+'\n')
    for path in captures.values():
        with path.open('rb') as source,gzip.open(str(path)+'.gz','wb') as dest:shutil.copyfileobj(source,dest)
        path.unlink()
    print('\n'.join(lines),flush=True)


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    for side in SIDES:parser.add_argument('--'+side+'-source',type=Path,required=True)
    parser.add_argument('--c-source',type=Path,required=True);parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--harness',type=Path,default=Path(__file__).with_name('bench_hma_weights.rs'))
    parser.add_argument('--build-only',action='store_true');parser.add_argument('--pairs',type=int,default=12);parser.add_argument('--repeats',type=int,default=31)
    args=parser.parse_args(argv)
    if args.pairs!=12 or args.repeats!=31:parser.error('exact12 pairs and31 samples required; do not cut repetitions')
    for key in ('baseline_source','candidate_source','c_source','output','harness'):setattr(args,key,getattr(args,key).resolve())
    args.output.mkdir(parents=True,exist_ok=True)
    if args.build_only:build(args)
    else:measure(args)

if __name__=='__main__':main()
