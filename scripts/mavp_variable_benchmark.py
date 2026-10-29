"""Pinned upstream variable-MAVP A/B; exact primary captures precede timing."""
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
CANDIDATE = 'b3f0fa17d0e3485c39ed042d86fff7116c0430a4'
C_COMMIT = 'b2bbc26d41ec80823c8bffb0cc436a97f29911cc'
C_ARCHIVE = 'talib-sys/vendor/ta-lib-0.8.1-src.tar.gz'
C_SHA = 'ec59ccd88c0c77f618587d858787c8f9d06c40460a09d66751926f6fd670f985'
REGISTRY = {'ta-lib': ('0.8.3', '4da552ae932721218c73cf1124610b0ce3d5f27cc1a62342debd370cd161d922'),
            'ta-lib-dispatch': ('0.1.2', '726f5cc1f53b7994288221583f9fb7ca535bae2b349b738a01adc75c3bd9ee41')}
SIDES = ('baseline', 'candidate')
BACKENDS = ('current', 'registry083', 'originalc081')
SIZES = (100, 1000, 10000, 1000000)
CASES = {f'mavp/{pattern}/SMA/{n}' for n in SIZES for pattern in ('one','four','few','many','blocked','clamped')}
CASES |= {f'{name}/{ma}/{n}' for n in SIZES for name,ma in (('sma_control','SMA'),('mavp/four','EMA'),('mavp/four','WMA'))}
KEYS = {(backend,name) for backend in BACKENDS for name in CASES}
CANARY = 0x7ff80000000055aa
ITERATIONS = {100:1000, 1000:100, 10000:10, 1000000:1}
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
        for folder in ('ta_codegen/output/rust','ta_codegen/generator/src','ta_codegen/input/mavp'):
            for p in (root/folder).rglob('*'):
                rel=p.relative_to(root)
                if p.is_file() and not {'target','.git'}.intersection(rel.parts) and p.suffix in ('.rs','.toml','.lock','.c','.h','.yaml','.yml'):
                    paths.add(rel.as_posix())
        paths.update(('ta_codegen/generator/Cargo.toml','ta_codegen/generator/Cargo.lock'))
    files={name:sha256(root/name) for name in sorted(paths)}
    if not old_c and not {'ta_codegen/input/mavp/mavp.c','ta_codegen/output/rust/Cargo.toml','ta_codegen/output/rust/library/Cargo.toml'}<=files.keys():raise ValueError('missing MAVP/compiled Rust source')
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
    (helper/'Cargo.toml').write_text('[package]\nname="mavp-registry-reference"\nversion="0.0.0"\nedition="2021"\n[lib]\npath="lib.rs"\n[dependencies]\nta-lib="=0.8.3"\n[profile.release]\nlto="thin"\ncodegen-units=1\n')
    (helper/'lib.rs').write_text('pub fn reference_marker() {}\n')
    lock='version = 4\n\n[[package]]\nname = "mavp-registry-reference"\nversion = "0.0.0"\ndependencies = ["ta-lib"]\n'
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
    env=os.environ.copy();env.update(MAVP_CURRENT_VERSION='0.8.4',MAVP_REGISTRY_VERSION='0.8.3')
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
    execution={'capture_only','capture_written','scope','cases','backends','capture_records','selected_case','selected_backend'}
    return {key:value for key,value in metadata.items() if key not in execution}


def harness_command(binary,capture,case=None,backend=None,golden=None,capture_only=False):
    if capture is None:raise ValueError('every mode requires a capture path')
    selected=any(value is not None for value in (case,backend,golden))
    command=[str(binary),'31',str(capture)]
    if selected:
        if case not in CASES or backend not in BACKENDS or golden is None:raise ValueError('case/backend/golden selectors required together')
        command+=['--case',case,'--backend',backend,'--golden',str(golden)]
    elif not capture_only:raise ValueError('full-inventory timing is forbidden')
    if capture_only:command.append('--capture-only')
    return command


def expected_range(name):
    n=int(name.rsplit('/',1)[1]);beg=13 if name.startswith('sma_control/') else 29
    return n,beg,n-beg


def parse_records(content,capture_only,selection=None,expected_os="linux"):
    selected=selection is not None
    if not selected and not capture_only:raise ValueError('full-inventory timing is forbidden')
    if selected:
        case,backend=selection
        if case not in CASES or backend not in BACKENDS:raise ValueError('invalid selection')
    metadata=None;parity={};validation={};cases={};seen_timing=False
    for line in content.splitlines():
        if not line.strip():continue
        row=json.loads(line)
        if not isinstance(row,dict):raise ValueError('records must be JSON objects')
        kind=row.get('kind')
        if kind=='metadata':
            if metadata is not None:raise ValueError('duplicate metadata')
            metadata=row;continue
        if metadata is None:raise ValueError('metadata must precede every result')
        key=(row.get('backend'),row.get('case'))
        expected={(backend,case)} if selected else KEYS
        if key not in expected:raise ValueError('unexpected sibling case/backend')
        n,beg,count=expected_range(key[1])
        if kind=='parity' and not selected:
            if seen_timing or key in parity:raise ValueError('duplicate or late parity')
            if type(row.get('count'))is not int or row['count']!=count:raise ValueError('parity range mismatch')
            counters=[row.get(k) for k in ('exact','within_tolerance','nonfinite_same')]
            if any(type(x)is not int or x<0 for x in counters) or sum(counters)!=count or type(row.get('signed_zero'))is not int or row['signed_zero']!=0 or row.get('nonfinite_same')!=0:raise ValueError('invalid parity counters')
            if key[0]=='current' and counters!=[count,0,0]:raise ValueError('primary current parity must be exact')
            for field in ('max_abs','max_scaled'):
                if type(row.get(field))not in (int,float) or not math.isfinite(row[field]) or row[field]<0:raise ValueError('invalid differential')
            if row['max_scaled']>4e-15:raise ValueError('cross-version tolerance exceeded')
            parity[key]=row
        elif kind=='validation' and selected:
            if seen_timing or key in validation:raise ValueError('duplicate or late selected validation')
            expected_values={'n':n,'beg':beg,'count':count,'written_finite':count,'tail_canary':n+8-count,'golden_verified':True,'golden_bytes':8+4+len((backend+'/'+case).encode())+32+(n+8)*8}
            if any(type(row.get(k))is not type(v) or row[k]!=v for k,v in expected_values.items()):raise ValueError('selected golden/range/padding proof mismatch')
            validation[key]=row
        elif kind=='case' and selected:
            seen_timing=True
            if capture_only or set(validation)!={(backend,case)} or key in cases:raise ValueError('selected golden validation must precede timing')
            expected_values={'n':n,'beg':beg,'count':count,'iterations':ITERATIONS[n],'warmups':5}
            if any(type(row.get(k))is not int or row[k]!=v for k,v in expected_values.items()):raise ValueError('case timing settings drift')
            samples=row.get('samples_ns')
            if not isinstance(samples,list) or len(samples)!=31 or any(type(x)not in (int,float) or not math.isfinite(x) or x<=0 for x in samples):raise ValueError('31 finite positive samples required')
            cases[key]=row
        else:raise ValueError('mixed/full/unknown execution mode')
    expected_meta={'format':2,'scope':'isolated' if selected else 'full','cases':1 if selected else 36,'backends':[backend] if selected else list(BACKENDS),'capture_records':1 if selected else 108,'canary_bits':'7ff80000000055aa','warmups':5,'repeats':31,'capture_only':capture_only,'capture_written':True,'registry_version':'0.8.3','current_version':'0.8.4','tolerance_relative':4e-15,'tolerance_floor':'max_abs_input'}
    if selected:expected_meta.update(selected_case=case,selected_backend=backend)
    if metadata is None or any(type(metadata.get(k))is not type(v) or metadata[k]!=v for k,v in expected_meta.items()):raise ValueError('metadata/runtime/selection mismatch')
    if not selected and any(k in metadata for k in ('selected_case','selected_backend')):raise ValueError('global mode cannot carry selectors')
    if metadata.get('os')!=expected_os or type(metadata.get('arch'))is not str or not metadata['arch'] or type(metadata.get('c_version'))is not str or not(metadata['c_version']=='0.8.1' or metadata['c_version'].startswith('0.8.1 (')):raise ValueError('unexpected runtime')
    if selected:
        if set(validation)!={(backend,case)} or parity or set(cases)!=(set() if capture_only else {(backend,case)}):raise ValueError('exact single selected inventory required')
    elif set(parity)!=KEYS or validation or cases:raise ValueError('global capture must contain all108 parity rows only')
    return {'metadata':metadata,'parity':{b+'/'+c:v for (b,c),v in parity.items()},'validation':{b+'/'+c:v for (b,c),v in validation.items()},'cases':{b+'/'+c:v for (b,c),v in cases.items()}}


def capture_record(path,selection=None):
    records={};written=0;expected=KEYS if selection is None else {(selection[1],selection[0])}
    with Path(path).open('rb') as f:
        if f.read(8)!=b'MAVPVC01':raise ValueError('capture magic mismatch')
        while length:=f.read(4):
            if len(length)!=4:raise ValueError('truncated capture name length')
            size=struct.unpack('<I',length)[0]
            if not 1<=size<=200:raise ValueError('invalid capture name length')
            name=f.read(size).decode();header=f.read(32)
            if len(header)!=32:raise ValueError('truncated capture header')
            n,beg,count,outlen=struct.unpack('<QQQQ',header)
            backend,case=name.split('/',1)
            if (backend,case)not in expected or name in records or (n,beg,count)!=expected_range(case) or outlen!=n+8:raise ValueError('capture inventory/range mismatch')
            body=f.read(outlen*8)
            if len(body)!=outlen*8:raise ValueError('truncated capture values')
            if body[count*8:]!=struct.pack('<Q',CANARY)*(outlen-count):raise ValueError('capture output padding modified')
            if any(not math.isfinite(value) for (value,) in struct.iter_unpack('<d',body[:count*8])):raise ValueError('capture written prefix contains nonfinite or unwritten canary')
            records[name]={'n':n,'beg':beg,'count':count,'outlen':outlen};written+=count
    if set(records)!={b+'/'+c for b,c in expected}:raise ValueError('capture missing backend/case')
    return {'sha256':sha256(path),'bytes':Path(path).stat().st_size,'records':len(records),'written_values':written,'all_padding_verified':True}


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
                   'is_reference_backend':not key.startswith('current/'),'is_unchanged_control':('/sma_control/' in key or '/EMA/' in key or '/WMA/' in key)}
    return rows



def split_goldens(full_capture,output):
    capture_record(full_capture)
    folder=output/'goldens';folder.mkdir(exist_ok=True);records={}
    with Path(full_capture).open('rb') as f:
        magic=f.read(8)
        while length:=f.read(4):
            size=struct.unpack('<I',length)[0];name_bytes=f.read(size);name=name_bytes.decode();header=f.read(32)
            n,beg,count,outlen=struct.unpack('<QQQQ',header);body=f.read(outlen*8)
            path=folder/(name.replace('/','__')+'.bin');path.write_bytes(magic+length+name_bytes+header+body)
            records[name]={'path':str(path.resolve()),'sha256':sha256(path),'bytes':path.stat().st_size,'n':n,'beg':beg,'count':count,'outlen':outlen}
    if set(records)!={b+'/'+c for b,c in KEYS}:raise ValueError('golden inventory incomplete')
    (output/'golden-records.json').write_text(json.dumps(records,indent=2)+'\n')
    return records


def reference_comparisons(runs):
    result={};negatives=[]
    for side in SIDES:
        result[side]={}
        for backend in BACKENDS[1:]:
            rows={}
            for case in sorted(CASES):
                current=[statistics.median(r['cases']['current/'+case]['samples_ns'])for r in runs[side]]
                reference=[statistics.median(r['cases'][backend+'/'+case]['samples_ns'])for r in runs[side]]
                value={'current_process_medians_ns':current,'reference_process_medians_ns':reference,
                       'current_median_ns':statistics.median(current),'reference_median_ns':statistics.median(reference),
                       'reference_over_current_ratio_of_medians':statistics.median(reference)/statistics.median(current),
                       'reference_over_current_envelope':[min(reference)/max(current),max(reference)/min(current)],
                       'current_latency_percent':(statistics.median(current)/statistics.median(reference)-1)*100}
                rows[case]=value
                if value['current_latency_percent']>0:negatives.append({'side':side,'reference':backend,'case':case,**value})
            result[side][backend]=rows
    return result,negatives



def execute_harness(command,stem,env):
    Path(str(stem)+'-command.json').write_text(json.dumps(command,indent=2)+'\n')
    response=subprocess.run(command,capture_output=True,text=True,env=env)
    Path(str(stem)+'.jsonl').write_text(response.stdout)
    Path(str(stem)+'.stderr.log').write_text(response.stderr)
    response.check_returncode()
    return response.stdout


def finalize_child_capture(path,selection,golden,proof,proof_path):
    actual=capture_record(path,selection)
    if actual['sha256']!=golden['sha256'] or actual['bytes']!=golden['bytes']:raise ValueError('selected child differs from own baseline golden')
    proof={**proof,'golden':golden,'capture':actual,'duplicate_deleted_after_sha_proof':True}
    Path(proof_path).write_text(json.dumps(proof,indent=2)+'\n')
    Path(path).unlink()
    return proof


def measure(args):
    provenance=json.loads((args.output/'build-provenance.json').read_text());verify(args,provenance)
    original=set(os.sched_getaffinity(0));affinity=sorted(original)[:1]
    if not affinity:raise ValueError('oneCPU affinity required')
    env=os.environ.copy();env['MAVP_CLOSE_BIN']=provenance['input']['path']
    captures={};validations={};metadata=None;order=[];proofs=[]
    runs={side:[{'cases':{}}for _ in range(12)]for side in SIDES}
    try:
        os.sched_setaffinity(0,affinity)
        for side in SIDES:
            path=args.output/(side+'.bin');captures[side]=path
            command=harness_command(provenance[side]['binary'],path,capture_only=True)
            stdout=execute_harness(command,args.output/(side+'-validation'),env)
            row=parse_records(stdout,True);current=stable_metadata(row['metadata'])
            if metadata is not None and current!=metadata:raise ValueError('global capture runtime drift')
            metadata=current;validations[side]={'records':row,'capture':capture_record(path),'command':command}
        before,after=(validations[side]['capture']for side in SIDES)
        if before!=after or not before['bytes']:raise ValueError('global full108 capture differs; no tolerance waiver')
        goldens=split_goldens(captures['baseline'],args.output)
        (args.output/'capture-validation.json').write_text(json.dumps({'completed_before_any_timing':True,'primary_exact':True,'validation':validations,'goldens':goldens},indent=2)+'\n')
        children=args.output/'children';children.mkdir(exist_ok=True)
        for case in sorted(CASES):
            for backend in BACKENDS:
                key=backend+'/'+case;golden=goldens[key]
                if sha256(golden['path'])!=golden['sha256']:raise ValueError('baseline golden changed')
                for pair in range(12):
                    for side in SIDES if pair%2==0 else reversed(SIDES):
                        label=key.replace('/','__')+'__'+side+'-'+str(pair+1);order.append(label)
                        path=children/(label+'.bin')
                        command=harness_command(provenance[side]['binary'],path,case,backend,golden['path'])
                        print(time.strftime('%H:%M:%S'),label,flush=True)
                        stdout=execute_harness(command,children/label,env)
                        row=parse_records(stdout,False,(case,backend))
                        if stable_metadata(row['metadata'])!=metadata:raise ValueError('isolated child runtime drift')
                        identity={'label':label,'side':side,'case':case,'backend':backend,'pair':pair+1,'command':command}
                        proof=finalize_child_capture(path,(case,backend),golden,identity,children/(label+'-proof.json'))
                        proofs.append(proof);runs[side][pair]['cases'][key]=row['cases'][key]
        if len(proofs)!=2592:raise ValueError('exact2592 isolated timed children required')
        verify(args,provenance)
    finally:os.sched_setaffinity(0,original)
    rows=summarize(runs);negatives={k:v for k,v in rows.items()if v['candidate_latency_percent']>0};references,reference_negatives=reference_comparisons(runs)
    report={'run_url':f"https://github.com/{os.environ.get('GITHUB_REPOSITORY','local')}/actions/runs/{os.environ.get('GITHUB_RUN_ID','local')}",
            'build_provenance':provenance,'execution':'freshprocess_per_case_backend','timed_child_count':2592,'pairs_per_case_backend':12,'samples_per_process':31,'warmups':5,'affinity':affinity,'order':order,
            'harness_metadata':metadata,'capture_validation':validations,'golden_records':goldens,'child_capture_proofs':proofs,'results':rows,'negative_cases':negatives,
            'reference_comparisons':references,'reference_slower_cases':reference_negatives,
            'limitations':'Every timed PID constructs and calls only its selected case/backend, verifies its full record against its own baseline backend golden before warmups, then runs5warmups/31samples. Primary before/after pairs alternateAB/BA. Reference/current comparisons are separate process distributions from sequential backend blocks, not same-process or temporally paired ratios. Inner samples are correlated; envelopes are extrema, not confidence limits. Exactness applies to the selected untimed record before warmups; timed calls check ranges, finiteness and tails rather than all values per sample. Golden I/O precedes warmups and can warm allocator state: this isolates sibling workloads, not a pristine allocator. No pooling with old mixed-process evidence or allocator-hypothesis normalization; no consumer Polars performance claim.'}
    (args.output/'summary.json').write_text(json.dumps(report,indent=2)+'\n')
    lines=['# Isolated variable MAVP comparison','',report['limitations'],'','| Backend/case | Before ns | After ns | Latency change | Paired ratio | Range | Faster pairs |','| --- | ---: | ---: | ---: | ---: | --- | ---: |']
    for name,row in rows.items():
        lo,hi=row['ratio_envelope'];lines.append(f"| {name} | {row['baseline_median_ns']:.2f} | {row['candidate_median_ns']:.2f} | {row['candidate_latency_percent']:+.3f}% | {row['median_paired_ratio']:.5f} | {lo:.5f}–{hi:.5f} | {row['candidate_faster_pairs']}/12 |")
    (args.output/'comparison.md').write_text('\n'.join(lines)+'\n')
    (args.output/'negative-cases.json').write_text(json.dumps({'before_after':negatives,'current_slower_than_reference':reference_negatives},indent=2)+'\n')
    for path in captures.values():
        with path.open('rb')as source,gzip.open(str(path)+'.gz','wb')as dest:shutil.copyfileobj(source,dest)
        path.unlink()
    print('\n'.join(lines),flush=True)


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    for side in SIDES:parser.add_argument('--'+side+'-source',type=Path,required=True)
    parser.add_argument('--c-source',type=Path,required=True);parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--harness',type=Path,default=Path(__file__).with_name('bench_mavp_variable.rs'))
    parser.add_argument('--build-only',action='store_true');parser.add_argument('--pairs',type=int,default=12);parser.add_argument('--repeats',type=int,default=31)
    args=parser.parse_args(argv)
    if args.pairs!=12 or args.repeats!=31:parser.error('exact12 pairs and31 samples required; do not cut repetitions')
    for key in ('baseline_source','candidate_source','c_source','output','harness'):setattr(args,key,getattr(args,key).resolve())
    args.output.mkdir(parents=True,exist_ok=True)
    if args.build_only:build(args)
    else:measure(args)

if __name__=='__main__':main()
