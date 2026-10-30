"""Pinned HMA maintainer follow-up; full exact validation before isolated batch timing."""
import argparse
import gzip
import hashlib
import json
import math
import os
from pathlib import Path
import platform
import re
import shutil
import statistics
import struct
import subprocess
import sys
import tarfile
import time

BASELINE = '5da9e8d43333c13b5f46f30efe8460de12b1f68b'
CANDIDATE = 'a4665da81c8df9a42cb956de8ba7edf063276a21'
DEV_MERGE = '6a4099c876bc1b4f28959df3f005bb9c9de10f35'
DEV_BASE = '1e9c7bc3cdc36f7336c6b9d977e8faa5c5002cb1'
TRIGGER = '6ac4c5d5695f3b9d3c1b3239fba9392804f74178'
C_COMMIT = 'b2bbc26d41ec80823c8bffb0cc436a97f29911cc'
C_ARCHIVE = 'talib-sys/vendor/ta-lib-0.8.1-src.tar.gz'
C_SHA = 'ec59ccd88c0c77f618587d858787c8f9d06c40460a09d66751926f6fd670f985'
REGISTRY = {'ta-lib': ('0.8.3', '4da552ae932721218c73cf1124610b0ce3d5f27cc1a62342debd370cd161d922'),
            'ta-lib-dispatch': ('0.1.2', '726f5cc1f53b7994288221583f9fb7ca535bae2b349b738a01adc75c3bd9ee41')}
SIDES = ('baseline', 'candidate')
BACKENDS = ('current', 'registry083', 'originalc081')
SIZES = (20, 100, 512, 1000, 10000, 1000000)
CASES = {f'{mode}/p20/{n}' for mode in ('hma','sma_control') for n in SIZES}
CASES |= {'hma/p2600/10000','hma/p2601/10000','hma/p2703/10000','hma/p2704/10000','hma/p100000/1000000'}
PERIODS = (1,2,3,4,5,6,7,8,9,10,15,16,17,20,25,26,81,82,100,101,2600,2601,2703,2704,99999,100000)
VALIDATION = {f'validation/hma/finite/p{p}/n{n}/start0' for p in PERIODS for n in (1,2,3,5,10,20,21,100,1000,10000,1000000)}
PATTERNS = ('zero','negative_zero','constant','ramp','reverse','alternating','head_nan','interior_nan','head_inf','interior_negative_inf')
VALIDATION |= {f'validation/hma/{pattern}/p{p}/n1000/start{start}' for pattern in PATTERNS for p in (1,2,3,4,5,6,7,8,20,100) for start in (0,25,500)}
VALIDATION |= {f'validation/hma/finite/p20/n1000/start{start}' for start in (1,19,20,25,99,100,500)}
VALIDATION |= {f'validation/hma/finite/p20/n{n}/start0' for n in (22,23,53,54,55,98,99,178,179,180)}
STREAM_PERIODS = (1,2,3,4,5,6,7,8,20,2600,2601,2703,2704,100000)
STREAM_PATTERNS = ('finite','zero','negative_zero','alternating')
VALIDATION |= {f'validation/stream/{pat}/p{period}/n{min(1000000, max(1000, 10*period))}/start0' for period in STREAM_PERIODS for pat in STREAM_PATTERNS}
TIMED_KEYS = {(backend,name) for backend in BACKENDS for name in CASES}
VALIDATION_KEYS = {(backend,name) for backend in BACKENDS for name in VALIDATION}
KEYS = TIMED_KEYS | VALIDATION_KEYS
HISTORY_BAD_BITS = (0x7ff8000000000000, 0x7ff0000000000000, 0xfff0000000000000)
OPENING_KEYS = {(backend,name,bits)for backend in BACKENDS[:2] for name in VALIDATION if name.startswith('validation/stream/') for bits in HISTORY_BAD_BITS}
CANARY = 0x7ff80000000055aa

FLAGS = {'RUSTFLAGS':'', 'CARGO_ENCODED_RUSTFLAGS':'', 'CARGO_PROFILE_RELEASE_LTO':'thin',
         'CARGO_PROFILE_RELEASE_CODEGEN_UNITS':'1', 'CARGO_PROFILE_RELEASE_DEBUG':'false', 'CFLAGS':'', 'CXXFLAGS':''}


def sha256(path):
    digest=hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda:f.read(1048576),b''): digest.update(block)
    return digest.hexdigest()


def run(command, log, cwd=None, env=None):
    with Path(log).open('a') as f:
        f.write(json.dumps(list(map(str,command)))+'\n');f.flush()
        subprocess.run(list(map(str,command)),cwd=cwd,env=env,stdout=f,stderr=subprocess.STDOUT,check=True)


GENERATED_CONFIG = 'ta_codegen/output/rust/.cargo/config.toml'
GENERATED_CONFIG_SHA = 'f55101801e5ff8e55fe1b9eea838587b1ceb9e33fcf66f7acfec3bca65e70e0e'


C_CONFIG_HEADER = 'include/ta_config.h'
C_CONFIG_TEMPLATE = 'include/ta_config.h.cmake'
C_CONFIG_WRITER = 'configure_file("${CMAKE_CURRENT_SOURCE_DIR}/include/ta_config.h.cmake" "${CMAKE_CURRENT_SOURCE_DIR}/include/ta_config.h")'


def read_cmake_cache(path):
    settings={}
    for line in Path(path).read_text().splitlines():
        if not line or line.startswith(('#','//'))or '='not in line:continue
        name,value=line.split('=',1)
        if name in settings:raise ValueError('duplicate CMake cache setting')
        settings[name]=value
    return settings


def generated_c_config(root,tree):
    # This sole ignored C header is an exact configure_file product of pinned
    # source plus recorded feature-test results; arbitrary generated files reject.
    inputs={}
    for name in ('CMakeLists.txt',C_CONFIG_TEMPLATE):
        data=(root/name).read_bytes();blob=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
        if name not in tree or tree[name][0]!='100644'or blob!=tree[name][1]:raise ValueError('generated C header requires pinned template/writer')
        inputs[name]={'git_blob':blob,'sha256':hashlib.sha256(data).hexdigest()}
    writer=(root/'CMakeLists.txt').read_text()
    if writer.splitlines().count(C_CONFIG_WRITER)!=1:raise ValueError('generated C header writer changed')
    for name,result in (('PTRDIFF_T','HAVE_PTRDIFF_T'),('SIZE_T','HAVE_SIZE_T')):
        lines=['if(HAVE_SIZEOF_'+name+')','set('+result+' 1)','else()','set('+result+' 0)']
        if name=='SIZE_T':lines.append('set(size_t "unsigned")')
        lines.append('endif()')
        normalized='\n'.join(line.strip()for line in writer.splitlines()if line.strip())
        if normalized.count('\n'.join(lines))!=1:raise ValueError('generated C header derived type logic changed')
    cache_path=root/'cmake-build/CMakeCache.txt';cache=read_cmake_cache(cache_path);values={};output=[]
    def boolean(name):
        value=cache.get(name+':INTERNAL')
        if value not in ('1','0','TRUE','FALSE',''):raise ValueError('missing/nonboolean C header feature result: '+name)
        return value,value not in ('0','FALSE','')
    for line in (root/C_CONFIG_TEMPLATE).read_text().splitlines(keepends=True):
        if not line.strip():output.append(line);continue
        match=re.fullmatch(r'#cmakedefine ([A-Za-z_][A-Za-z_0-9]*) \$\{\1\}\n',line)
        if match is None:raise ValueError('unsupported pinned C header template shape')
        name=match[1]
        if name in values:raise ValueError('duplicate C header template feature')
        if name in ('HAVE_PTRDIFF_T','HAVE_SIZE_T'):
            _,enabled=boolean('HAVE_SIZEOF_'+('PTRDIFF_T'if name=='HAVE_PTRDIFF_T'else'SIZE_T'));value='1'if enabled else'0'
        elif name=='size_t':
            _,has_size=boolean('HAVE_SIZEOF_SIZE_T');enabled=not has_size;value='unsigned'if enabled else''
        else:value,enabled=boolean(name)
        values[name]=value
        output.append('#define '+name+' '+value+'\n'if enabled else'/* #undef '+name+' */\n')
    expected=''.join(output).encode();actual=(root/C_CONFIG_HEADER).read_bytes()
    if actual!=expected:raise ValueError('generated C header differs from pinned template/cache')
    return {'header':C_CONFIG_HEADER,'header_sha256':hashlib.sha256(actual).hexdigest(),'inputs':inputs,'cache_sha256':sha256(cache_path),'values':values}


def git_record(root,expected,old_c=False):
    root=Path(root).resolve()
    commit=subprocess.check_output(['git','-C',str(root),'rev-parse','HEAD'],text=True).strip()
    if commit!=expected or subprocess.check_output(['git','-C',str(root),'status','--porcelain']):
        raise ValueError('source must be clean and match its immutable full commit pin')
    tree={}
    for record in subprocess.check_output(['git','-C',str(root),'ls-tree','-rz','HEAD']).split(b'\0'):
        if record:
            meta,name=record.split(b'\t',1);mode,kind,oid=meta.decode().split()
            if kind=='blob':tree[name.decode()]=(mode,oid)
    paths=set()
    if old_c:
        paths={C_ARCHIVE,'talib-sys/build.rs','Cargo.lock'}
    else:
        for folder in ('ta_codegen/output/rust','ta_codegen/generator/src','ta_codegen/input/hma','src/ta_func','src/tools/ta_regtest','ta_codegen/output/csharp/library','ta_codegen/output/java/library','ta_codegen/output/java/fragments','include','.cargo'):
            for path in (root/folder).rglob('*'):
                rel=path.relative_to(root)
                if path.is_file() and not {'target','.git','bin','obj'}.intersection(rel.parts) and path.suffix in ('.rs','.toml','.lock','.c','.h','.yaml','.yml','.cs','.java','.csproj','.json'):
                    paths.add(rel.as_posix())
        paths.update(('ta_codegen/generator/Cargo.toml','ta_codegen/generator/Cargo.lock'))
        if (root/'cmake-build/CMakeCache.txt').is_file()and C_CONFIG_TEMPLATE in tree and C_CONFIG_HEADER not in paths:raise ValueError('configured C header missing')
        if C_CONFIG_TEMPLATE in tree:paths.add(C_CONFIG_TEMPLATE)
        paths.update(n for n in ('global.json','CMakeLists.txt') if n in tree)
    generated={};c_config={};files={}
    for name in sorted(paths):
        path=root/name
        if path.is_symlink():raise ValueError('compiled source cannot be a symlink')
        data=path.read_bytes();digest=hashlib.sha256(data).hexdigest()
        if name not in tree:
            if name==C_CONFIG_HEADER:c_config=generated_c_config(root,tree)
            elif name==GENERATED_CONFIG and digest==GENERATED_CONFIG_SHA:generated[name]=digest
            else:raise ValueError('untracked compiled source/config: '+name)
        else:
            blob=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
            if tree[name][0]not in ('100644','100755')or blob!=tree[name][1]:raise ValueError('working source differs from pinned Git blob: '+name)
        if name in tree:files[name]=digest
    if not old_c and not {'ta_codegen/input/hma/hma.c','ta_codegen/output/rust/Cargo.toml','ta_codegen/output/rust/library/Cargo.toml'}<=files.keys():raise ValueError('missing HMA/compiled Rust source')
    return {'commit':commit,'clean':True,'source_files':files,'generated_empty_config':generated,'generated_c_config':c_config,
            'source_sha256':hashlib.sha256(json.dumps(files,sort_keys=True,separators=(',',':')).encode()).hexdigest()}


def require_runtimes(folder):
    folder=Path(folder);reg=(folder/'full-four-language-regression.log').read_text();managed=(folder/'managed-libraries.log').read_text()
    for label in ('C','Rust','Java','C#'):
        if not re.search(r'│\s*'+re.escape(label)+r'\s*│\s*237\s*│\s*0\s*│',reg):raise ValueError('missing237 runtime rows '+label)
    if not re.search(r'StreamSmokeTest: ALL PASS \([1-9][0-9]* checks\)',managed):raise ValueError('Java stream runtime suite missing')
    if not re.search(r'TALib C# tests on \.NET 10\.',managed)or not re.search(r'All [1-9][0-9]* C# suite\(s\) passed\.',managed):raise ValueError('C# net10 runtime suite missing')
    if len(re.findall(r'BatchApiTest: ALL PASS \([1-9][0-9]* checks\)',managed))<2:raise ValueError('both managed batch suites must run')
    return {name:sha256(folder/name)for name in ('full-four-language-regression.log','managed-libraries.log','generator-tests.log','rust-tests.log','rust-doc-tests.log','generator-clippy.log','rust-clippy.log','regenerate.log','java-version.txt','dotnet-info.txt')}


def integration_proof(integration,production,folder,complete=False):
    integration=Path(integration).resolve();production=Path(production).resolve();folder=Path(folder).resolve();folder.mkdir(exist_ok=True)
    for root,pin in ((integration,DEV_MERGE),(production,CANDIDATE)):
        if subprocess.check_output(['git','-C',str(root),'rev-parse','HEAD'],text=True).strip()!=pin or subprocess.check_output(['git','-C',str(root),'status','--porcelain']):raise ValueError('immutable clean integration/source pins required')
    commit=subprocess.check_output(['git','-C',str(integration),'cat-file','-p','HEAD'],text=True)
    parents=[line.split()[1]for line in commit.splitlines()if line.startswith('parent ')]
    if set(parents)!={DEV_BASE,TRIGGER}or len(parents)!=2:raise ValueError('frozen dev merge parents changed')
    paths=['ta_codegen/input/hma/hma.c','src/ta_func/ta_HMA.c','ta_codegen/output/java/fragments/Core_HMA.java']
    for subtree,suffixes in (('ta_codegen/output/rust/library',{'.rs','.toml'}),('ta_codegen/output/java/library/src',{'.java'}),('ta_codegen/output/csharp/library',{'.cs','.csproj'})):
        candidates=[]
        for root in (integration,production):
            names=subprocess.check_output(['git','-C',str(root),'ls-tree','-r','--name-only','HEAD',subtree],text=True).splitlines();candidates.append({n for n in names if Path(n).suffix in suffixes})
        if candidates[0]!=candidates[1]or not candidates[0]:raise ValueError('compiled library source inventory differs')
        paths.extend(candidates[0])
    maps={}
    for root,label in ((integration,'dev_merge'),(production,'production_a466')):maps[label]={n:sha256(root/n)for n in sorted(set(paths))}
    if maps['dev_merge']!=maps['production_a466']:raise ValueError('HMA or compiled Rust/Java/C# library source differs between exact production and dev merge')
    proof={'dev_merge':DEV_MERGE,'dev_base':DEV_BASE,'trigger':TRIGGER,'production':CANDIDATE,'parents':parents,'library_source_maps':maps,'all_library_sources_identical':True,'correctness_only':True,'runtime_context':'All-four runtimes run on frozen dev merge; servers/build scripts/C headers may differ. Parent5da/a466 C/Rust batch/stream contracts separately bind performance products. No dev-merge throughput inference.'}
    destination=folder/'proof.json'
    if complete:
        prior=json.loads(destination.read_text())
        if prior!=proof:raise ValueError('integration source proof changed through gates')
        proof['runtime_logs']=require_runtimes(folder);proof['source_archive_sha256']=sha256(folder/'dev-merge-source.tar.gz');proof['complete_before_primary_build']=True
    destination.write_text(json.dumps(proof,indent=2)+'\n')
    return proof


def verify_integration(args):
    folder=args.output/'dev-integration';proof=json.loads((folder/'proof.json').read_text())
    if proof['dev_merge']!=DEV_MERGE or proof['production']!=CANDIDATE or proof['dev_base']!=DEV_BASE or proof['trigger']!=TRIGGER or proof['all_library_sources_identical']is not True or proof['correctness_only']is not True or proof['complete_before_primary_build']is not True:raise ValueError('completed immutable dev integration evidence required')
    if proof['library_source_maps']['dev_merge']!=proof['library_source_maps']['production_a466']or not proof['library_source_maps']['dev_merge']:raise ValueError('integration library byte equality proof missing')
    if require_runtimes(folder)!=proof['runtime_logs']or sha256(folder/'dev-merge-source.tar.gz')!=proof['source_archive_sha256']:raise ValueError('integration runtime/source evidence modified')
    return {'proof':proof,'sha256':sha256(folder/'proof.json')}


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
    runtime=runtime_record()
    dev_proof=verify_integration(args)
    c_proof=c_contracts(args)
    if sha256(args.harness)!=sha256(Path(__file__).with_name('bench_hma_review.rs')):raise ValueError('canonical archived harness required')
    sources={s:git_record(getattr(args,s+'_source'),p) for s,p in zip(SIDES,(BASELINE,CANDIDATE))}
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
                'input':inputs,'dev_integration':dev_proof,'public_c_contracts':c_proof,'old_c':{'source':c_record,'archive_sha256':C_SHA,'commands':commands,'library':str(c_lib),'library_sha256':sha256(c_lib)},
                'registry':registry,'registry_lock_sha256':lock_before,'registry_library':str(registry_rlib),'registry_library_sha256':sha256(registry_rlib)}
    env=os.environ.copy();env.update(HMA_CURRENT_VERSION='0.8.4',HMA_REGISTRY_VERSION='0.8.3')
    for side in SIDES:
        root=getattr(args,side+'_source')
        source_archive=archives/(side+'-source.tar.gz')
        with source_archive.open('wb')as f:subprocess.run(['git','-C',str(root),'archive','--format=tar.gz','HEAD'],stdout=f,check=True)
        generated_configs={}
        for name,digest in sources[side]['generated_empty_config'].items():
            preserved=archives/(side+'-generated-config.toml');shutil.copy2(root/name,preserved)
            generated_configs[str(preserved)]=digest
        header=sources[side]['generated_c_config']
        if header:
            preserved=archives/(side+'-generated-ta_config.h');shutil.copy2(root/header['header'],preserved)
            generated_configs[str(preserved)]=header['header_sha256']
        out=args.output/('target-'+side);binary=args.output/'bin'/side;binary.parent.mkdir(exist_ok=True)
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
        provenance[side]={'source':sources[side],'source_archive':str(source_archive),'source_archive_sha256':sha256(source_archive),'generated_config_copies':generated_configs,'commands':commands,'binary':str(binary),'binary_sha256':sha256(binary),'library':str(out/'release/libta_lib.rlib'),'library_sha256':sha256(out/'release/libta_lib.rlib'),'package_version':package['version']}
    if sha256(args.harness)!=provenance['harness_sha256']:raise ValueError('harness changed during build')
    (args.output/'build-provenance.json').write_text(json.dumps(provenance,indent=2)+'\n')




def c_contract_capture(path):
    keys=set();written=0
    with Path(path).open('rb')as f:
        if f.read(8)!=b'HMARVC01':raise ValueError('C contract magic')
        while header:=f.read(56):
            if len(header)!=56:raise ValueError('C contract header')
            period,pattern,start,n,beg,count,capacity=struct.unpack('<7Q',header);key=(period,pattern,start)
            lb=period+math.isqrt(period)-2
            if period not in STREAM_PERIODS or pattern not in range(4)or start not in(0,lb+1,lb+25)or key in keys:raise ValueError('C contract inventory')
            if n!=min(1000000,max(1000,10*period))or beg!=max(lb,start)or count!=n-beg or not count or capacity!=n+8:raise ValueError('C contract range')
            body=f.read(capacity*8);guard=struct.pack('<Q',CANARY)
            if len(body)!=capacity*8 or body[:8]!=guard or body[(count+1)*8:]!=guard*(capacity-count-1):raise ValueError('C contract physical canary')
            for value, in struct.iter_unpack('<d',body[8:(count+1)*8]):
                if not math.isfinite(value):raise ValueError('C contract finite output')
            keys.add(key);written+=count
    expected={(p,pat,start)for p in STREAM_PERIODS for pat in range(4)for start in(0,p+math.isqrt(p)-1,p+math.isqrt(p)+23)}
    if keys!=expected:raise ValueError('C contract missing row')
    return {'sha256':sha256(path),'bytes':Path(path).stat().st_size,'cases':len(keys),'written':written}


def build_public_c_library(root,pin,output):
    root=Path(root);output=Path(output)
    source=git_record(root,pin)
    cache=root/'cmake-build/CMakeCache.txt'
    settings=read_cmake_cache(cache)
    if settings.get('CMAKE_BUILD_TYPE:STRING')!='Release'or settings.get('BUILD_SHARED_LIBS:BOOL')!='ON':raise ValueError('public C contracts require configured Release shared target')
    # ta_regtest and the language servers depend on ta-lib-static, not ta-lib.
    # Build the declared shared target explicitly rather than assuming all targets ran.
    command=['cmake','--build',str(root/'cmake-build'),'--target','ta-lib','--parallel','4']
    side='baseline'if pin==BASELINE else 'candidate'
    log=output/(side+'-public-c-shared-build.log');run(command,log)
    library=root/'cmake-build/libta-lib.so'
    if not library.is_file():raise ValueError('declared shared target did not produce public C library')
    if git_record(root,pin)!=source:raise ValueError('source changed during shared C build')
    shutil.copy2(cache,output/(side+'-public-c-CMakeCache.txt'))
    return {'source':source,'library':str(library),'cmake_cache_sha256':sha256(cache),'shared_build_command':command,'shared_build_log_sha256':sha256(log)}


def c_contracts(args):
    records={};driver=Path(__file__).with_name('check_hma_review.c')
    for side in SIDES:
        root=getattr(args,side+'_source');binary=args.output/'bin'/('public-c-'+side)
        c_build=build_public_c_library(root,BASELINE if side=='baseline'else CANDIDATE,args.output)
        library=Path(c_build['library']);source=c_build['source']
        command=['cc','-std=c11','-O2','-Wall','-Wextra','-Werror',str(driver),'-I'+str(root/'include'),'-L'+str(library.parent),'-Wl,-rpath,'+str(library.parent),'-lta-lib','-lm','-o',str(binary)]
        binary.parent.mkdir(exist_ok=True);run(command,args.output/(side+'-c-contract-build.log'))
        env=os.environ.copy();env['LD_LIBRARY_PATH']=str(library.parent)
        linked=subprocess.check_output(['ldd',str(binary)],text=True,env=env);(args.output/(side+'-c-contract-ldd.txt')).write_text(linked)
        resolved=[Path(line.split('=>',1)[1].strip().split()[0])for line in linked.splitlines()if re.match(r'\s*libta-lib\.so(?:\.[0-9]+)*\s+=>',line)]
        if len(resolved)!=1 or resolved[0].resolve()!=library.resolve()or sha256(resolved[0])!=sha256(library):raise ValueError('public C probe wrong library resolution')
        capture=args.output/(side+'-public-c.bin');result=subprocess.run([str(binary),str(capture)],check=True,capture_output=True,text=True,env=env)
        (args.output/(side+'-c-contract.jsonl')).write_text(result.stdout);(args.output/(side+'-c-contract.stderr.log')).write_text(result.stderr)
        expected={'format':1,'cases':168,'inplace_checks':168,'nonempty':168,'padding_checked':True,'maximum_period':100000}
        if strict_json(result.stdout)!=expected:raise ValueError('public C contract checks incomplete')
        records[side]={'source':source,'command':command,'run_command':[str(binary),str(capture)],'environment':{'LD_LIBRARY_PATH':env['LD_LIBRARY_PATH']},'resolved_library':str(resolved[0]),'cmake_cache_sha256':c_build['cmake_cache_sha256'],'shared_build_command':c_build['shared_build_command'],'shared_build_log_sha256':c_build['shared_build_log_sha256'],'binary_sha256':sha256(binary),'library':str(library),'library_sha256':sha256(library),'capture':c_contract_capture(capture),'driver_sha256':sha256(driver)}
    if records['baseline']['capture']!=records['candidate']['capture']:raise ValueError('new C source contract differs from parent; no waiver')
    (args.output/'public-c-contracts.json').write_text(json.dumps({'passed_before_any_timing':True,'products':records},indent=2)+'\n')
    return records


def stable_metadata(metadata):
    return {key:value for key,value in metadata.items() if key not in ('capture_only','capture_written')}


def harness_command(binary,capture=None,capture_only=False,*,selection=None,golden=None,actual=None):
    if capture_only:
        if capture is None or selection is not None:raise ValueError('capture-only requires one output and no selection')
        return [str(binary),'31',str(capture),'--capture-only']
    if capture is not None or selection not in TIMED_KEYS or golden is None or actual is None or Path(golden).resolve()==Path(actual).resolve():raise ValueError('timing requires fixed selected case/backend and distinct golden/actual paths')
    backend,name=selection
    return [str(binary),'31','--case',name,'--backend',backend,'--golden',str(golden),'--actual',str(actual)]


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


def opening_observation(row):
    expected={'kind','case','backend','history_len','bad_index','bad_bits','open','fill','fill_bits','policy'}
    if type(row)is not dict or set(row)!=expected:raise ValueError('opening observation exact schema')
    key=(row.get('backend'),row.get('case'),row.get('bad_bits'))
    if type(row['bad_bits'])is not int or key not in OPENING_KEYS:raise ValueError('opening observation inventory')
    case=expected_case(key[1]);lb=case['beg'];history=min(case['n'],lb+26)
    fixed={'kind':'opening_history_observation','history_len':history,'bad_index':history//2,'policy':'undefined-opening-history-observation-only'}
    if any(type(row.get(k))is not type(v)or row[k]!=v for k,v in fixed.items()):raise ValueError('opening observation fixture/policy')
    def word(value):return type(value)is int and 0<=value<2**64
    for name in ('open','fill'):
        result=row[name]
        if type(result)is not dict:raise ValueError('opening result schema')
        if result.get('status')=='error':
            if set(result)!={'status','error'}or type(result['error'])is not str or not 1<=len(result['error'])<=200:raise ValueError('opening error observation')
        elif result.get('status')=='ok':
            keys={'status','beg','count','value_bits','state_value_bits'}if name=='open'else{'status','beg','count','state_beg','state_count','state_value_bits'}
            if set(result)!=keys or not all(word(result[k])for k in keys-{'status'}):raise ValueError('opening successful observation')
        else:raise ValueError('opening result status')
    if type(row['fill_bits'])is not list or len(row['fill_bits'])!=history-lb+8 or not all(word(v)for v in row['fill_bits']):raise ValueError('opening physical fill-word observation')
    return key


def opening_key(key):
    return key[0]+'/'+key[1]+'/'+format(key[2],'016x')


def compare_opening_observations(before,after):
    if set(before)!=set(after)or set(before)!={opening_key(k)for k in OPENING_KEYS}:raise ValueError('complete opening observation comparison inventory')
    differences={key:{'baseline':before[key],'candidate':after[key]}for key in sorted(before)if not typed_equal(before[key],after[key])}
    return {'policy':'Undefined opening-history observations only; differences are retained and are not a finite-input compatibility or performance gate.','records_per_source':len(OPENING_KEYS),'identical':not differences,'differences':differences,'baseline':before,'candidate':after}


def parse_records(content,capture_only,expected_os="linux"):
    metadata=None;parity={};validation={};cases={};observations={};seen_timing=False
    for line in content.splitlines():
        if not line.strip():continue
        row=strict_json(line)
        if not isinstance(row,dict):raise ValueError('records must be JSON objects')
        kind=row.get('kind')
        if kind=='metadata':
            if metadata is not None:raise ValueError('duplicate metadata')
            metadata=row;continue
        if metadata is None:raise ValueError('metadata must precede validation/parity/timing')
        if kind=='opening_history_observation':
            if seen_timing:raise ValueError('opening observations must precede timing')
            obs_key=opening_observation(row)
            if obs_key in observations:raise ValueError('duplicate opening observation')
            observations[obs_key]=row;continue
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
    expected={'format':1,'cases':len(CASES),'validation_cases':len(VALIDATION),'opening_history_observations':len(OPENING_KEYS),'backends':list(BACKENDS),'canary_bits':'7ff80000000055aa','output_prefix':1,'warmups':5,'repeats':31,'capture_only':capture_only,'capture_written':capture_only,'registry_version':'0.8.3','current_version':'0.8.4','capture_records':len(KEYS),'tolerance_relative':4e-15,'tolerance_floor':'max_abs_finite_input'}
    if metadata is None or any(type(metadata.get(k))is not type(v) or metadata[k]!=v for k,v in expected.items()):raise ValueError('metadata/runtime/fixed inventory mismatch')
    if metadata.get('os')!=expected_os or type(metadata.get('arch'))is not str or not metadata['arch'] or type(metadata.get('c_version'))is not str or not (metadata['c_version']=='0.8.1' or metadata['c_version'].startswith('0.8.1 (')):raise ValueError('unexpected platform or C runtime')
    if set(observations)!=OPENING_KEYS or set(parity)!=TIMED_KEYS or set(validation)!=VALIDATION_KEYS or set(cases)!=(set() if capture_only else TIMED_KEYS):raise ValueError('complete fixed backend/case inventories required')
    return {'metadata':metadata,'opening_history_observations':{opening_key(k):v for k,v in observations.items()},'validation':{b+'/'+c:v for (b,c),v in validation.items()},'parity':{b+'/'+c:v for (b,c),v in parity.items()},'cases':{b+'/'+c:v for (b,c),v in cases.items()}}


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
    if sha256(args.harness)!=sha256(Path(__file__).with_name('bench_hma_review.rs')):raise ValueError('canonical archived harness required')
    if verify_integration(args)!=p['dev_integration']:raise ValueError('dev integration proof changed')
    if runtime_record()!=p['runtime'] or sha256(args.harness)!=p['harness_sha256'] or sha256(__file__)!=p['controller_sha256']:raise ValueError('runtime/harness/controller changed')
    for side,pin in zip(SIDES,(BASELINE,CANDIDATE)):
        r=p[side]
        if git_record(getattr(args,side+'_source'),pin)!=r['source']:raise ValueError('source changed')
        for key in ('binary','library','source_archive'):
            if sha256(r[key])!=r[key+'_sha256']:raise ValueError('primary binary/library changed')
        for path,digest in r['generated_config_copies'].items():
            if sha256(path)!=digest:raise ValueError('generated empty config evidence changed')
    for side,record in p['public_c_contracts'].items():
        if sha256(record['library'])!=record['library_sha256']:raise ValueError('public C library changed')
        if sha256(args.output/(side+'-public-c-shared-build.log'))!=record['shared_build_log_sha256']or sha256(args.output/(side+'-public-c-CMakeCache.txt'))!=record['cmake_cache_sha256']:raise ValueError('shared C build evidence changed')
    if sha256(Path(__file__).with_name('check_hma_review.c'))!=p['public_c_contracts']['candidate']['driver_sha256']:raise ValueError('C contract driver changed')
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


def typed_equal(left,right):
    if type(left)is not type(right):return False
    if isinstance(left,dict):return left.keys()==right.keys() and all(typed_equal(left[k],right[k])for k in left)
    if isinstance(left,list):return len(left)==len(right)and all(typed_equal(a,b)for a,b in zip(left,right))
    return left==right


def strict_json(text):
    def pairs(rows):
        out={}
        for k,v in rows:
            if k in out:raise ValueError('duplicate JSON key')
            out[k]=v
        return out
    return json.loads(text,object_pairs_hook=pairs,parse_constant=lambda x:(_ for _ in ()).throw(ValueError('nonfinite JSON')))


def selected_records(text,key,metadata):
    rows=[strict_json(x)for x in text.splitlines()if x.strip()]
    if len(rows)!=2 or rows[0].get('kind')!='metadata' or rows[1].get('kind')!='case':raise ValueError('one selected result and metadata required')
    m,row=rows
    if m.get('capture_only')is not False or m.get('capture_written')is not False or not typed_equal(stable_metadata(m),metadata):raise ValueError('selected runtime metadata drift')
    backend,name=key;c=expected_case(name)
    fields={'backend':backend,'case':name,'n':c['n'],'beg':c['beg'],'count':c['count'],'period':c['period'],'start':c['start'],'iterations':max(100000//c['n'],1),'warmups':5,'empty_range_control':c['count']==0,'pre_output_checked':True,'final_output_checked':True}
    if any(type(row.get(k))is not type(v)or row[k]!=v for k,v in fields.items()):raise ValueError('selected identity/range/pre-final check mismatch')
    samples=row.get('samples_ns')
    if not isinstance(samples,list)or len(samples)!=31 or any(type(x)not in(int,float)or not math.isfinite(x)or x<=0 for x in samples):raise ValueError('31 positive selected samples required')
    return {'metadata':m,'cases':{backend+'/'+name:row}}


def split_goldens(path,folder):
    folder.mkdir(exist_ok=True);records={}
    with path.open('rb')as f:
        if f.read(8)!=b'HMAWGT01':raise ValueError('capture magic')
        while word:=f.read(4):
            if len(word)!=4:raise ValueError('short capture')
            length=struct.unpack('<I',word)[0]
            if not 1<=length<=200:raise ValueError('capture name length')
            key=f.read(length);header=f.read(32)
            if len(header)!=32:raise ValueError('capture header')
            n,beg,count,outlen=struct.unpack('<QQQQ',header);body=f.read(outlen*8)
            if len(body)!=outlen*8:raise ValueError('capture body')
            label=key.decode();selection=tuple(label.split('/',1))
            if selection in TIMED_KEYS:
                if label in records:raise ValueError('duplicate golden')
                payload=b'HMAWGT01'+word+key+header+body
                destination=folder/(hashlib.sha256(label.encode()).hexdigest()+'.bin');destination.write_bytes(payload)
                records[label]={'path':str(destination),'sha256':sha256(destination),'bytes':len(payload),'case':selection[1],'backend':selection[0]}
    if set(records)!={b+'/'+n for b,n in TIMED_KEYS}:raise ValueError('complete selected golden inventory required')
    return records


def execute(command,label,args,env):
    with (args.output/'commands.jsonl').open('a')as f:f.write(json.dumps({'label':label,'argv':list(map(str,command))})+'\n')
    try:result=subprocess.run(list(map(str,command)),check=True,capture_output=True,text=True,env=env,timeout=180)
    except (subprocess.CalledProcessError,subprocess.TimeoutExpired)as exc:
        for suffix,value in [('stdout',exc.stdout),('stderr',exc.stderr)]:
            (args.output/(label+'.'+suffix+'.log')).write_text(value.decode(errors='replace')if isinstance(value,bytes)else value or '')
        (args.output/(label+'.failure.json')).write_text(json.dumps({'command':list(map(str,command)),'type':type(exc).__name__,'returncode':getattr(exc,'returncode',None)})+'\n')
        raise
    (args.output/(label+'.jsonl')).write_text(result.stdout);(args.output/(label+'.stderr.log')).write_text(result.stderr)
    return result.stdout


def measure(args):
    p=json.loads((args.output/'build-provenance.json').read_text());verify(args,p)
    original=set(os.sched_getaffinity(0));affinity=sorted(original)[:1]
    if not affinity:raise ValueError('one CPU affinity required')
    env=os.environ.copy();env['HMA_CLOSE_BIN']=p['input']['path'];runs={s:[]for s in SIDES};validations={};metadata=None;ledger=[];goldens={};selected={side:{}for side in SIDES}
    try:
        os.sched_setaffinity(0,affinity)
        for side in SIDES:
            path=args.output/(side+'.bin')
            text=execute(harness_command(p[side]['binary'],path,True),side+'-validation',args,env)
            row=parse_records(text,True);validations[side]={'records':row,'capture':capture_record(path)}
            current=stable_metadata(row['metadata'])
            if metadata is not None and current!=metadata:raise ValueError('capture runtime differs')
            metadata=current
        first,last=[validations[s]['capture']for s in SIDES]
        if not first['bytes']or first['bytes']!=last['bytes']or first['sha256']!=last['sha256']:raise ValueError('full primary captures differ; no waiver')
        opening=compare_opening_observations(*[validations[s]['records']['opening_history_observations']for s in SIDES])
        (args.output/'opening-history-observations.json').write_text(json.dumps(opening,indent=2)+'\n')
        goldens=split_goldens(args.output/'baseline.bin',args.output/'goldens')
        gate={'completed_before_any_timing':True,'primary_exact':True,'validation':validations,'goldens':goldens}
        (args.output/'capture-validation.json').write_text(json.dumps(gate,indent=2)+'\n')
        for idx,key in enumerate(sorted(TIMED_KEYS),1):
            label_key='/'.join(key);golden=goldens[label_key];per={s:[]for s in SIDES}
            for pair in range(12):
                for side in SIDES if pair%2==0 else reversed(SIDES):
                    label=f'selected-{idx:03d}-{side}-{pair+1}';actual=args.output/(label+'.bin')
                    if sha256(golden['path'])!=golden['sha256']:raise ValueError('golden changed before child')
                    command=harness_command(p[side]['binary'],selection=key,golden=golden['path'],actual=actual)
                    text=execute(command,label,args,env);row=selected_records(text,key,metadata)
                    if sha256(actual)!=golden['sha256']or actual.stat().st_size!=golden['bytes']:raise ValueError('selected actual differs after child')
                    ledger.append({'label':label,'selection':list(key),'side':side,'pair':pair+1,'actual_path':str(actual),'actual_sha256':sha256(actual),'golden_sha256':golden['sha256'],'actual_deleted_after_exact_sha':True})
                    actual.unlink();per[side].append(row)
            for side in SIDES:selected[side][label_key]=per[side]
        verify(args,p)
    finally:os.sched_setaffinity(0,original)
    # Reconstruct pair-matched rows from the isolated per-selection children.
    for side in SIDES:
        for pair in range(12):runs[side].append({'cases':{key:rows[pair]['cases'][key]for key,rows in selected[side].items()}})
    rows=summarize(runs);negatives={k:v for k,v in rows.items()if v['candidate_latency_percent']>0}
    report={'run_url':f"https://github.com/{os.environ.get('GITHUB_REPOSITORY','local')}/actions/runs/{os.environ.get('GITHUB_RUN_ID','local')}",'build_provenance':p,'pairs':12,'samples_per_process':31,'warmups':5,'affinity':affinity,'order':ledger,'children':len(ledger),'samples':len(ledger)*31,'harness_metadata':metadata,'opening_history_observations':opening,'capture_validation':validations,'goldens':goldens,'results':rows,'negative_cases':negatives,
        'source_scope':'HMA parent5da vs maintainera466: on-demand departing reads, sqrt(n)ring, subHalf local and unlikely reseeds. Private stream storage changes. Stream finite-input checks are validation-only; undefined opening-history records are retained as observations, not rejection guarantees.',
        'limitations':'Fresh process per selected batch case/backend/build/round. Twelve matched AB/BA pairs,31 inner correlated samples after5warmups. Envelopes are descriptive, not confidence intervals. Unchanged registry083/C081 arms are negative controls across the two linked-source binaries. No cross-backend ratio is presented as a counterbalanced comparison; no Polars/consumer claim or reuse/pooling of the old433→5da results. Actual C# stream performance remains tracked in upstream567; this job does not measure it.'}
    if len(ledger)!=1224:raise ValueError('complete17x3x2x12 children required')
    (args.output/'summary.json').write_text(json.dumps(report,indent=2)+'\n');(args.output/'negative-cases.json').write_text(json.dumps(negatives,indent=2)+'\n')
    lines=['# HMA maintainer follow-up: same-runner batch comparison','',report['limitations'],'','| Backend/case | Before ns | After ns | Latency change | Paired ratio | Envelope | Faster pairs |','| --- | ---: | ---: | ---: | ---: | --- | ---: |']
    for name,r in rows.items():
        lo,hi=r['ratio_envelope'];lines.append(f"| {name} | {r['baseline_median_ns']:.2f} | {r['candidate_median_ns']:.2f} | {r['candidate_latency_percent']:+.3f}% | {r['median_paired_ratio']:.5f} | {lo:.5f}–{hi:.5f} | {r['candidate_faster_pairs']}/12 |")
    (args.output/'comparison.md').write_text('\n'.join(lines)+'\n')
    print('\n'.join(lines),flush=True)

def main(argv=None):
    argv=list(sys.argv[1:]if argv is None else argv)
    if '--integration-root'in argv:
        special=argparse.ArgumentParser();special.add_argument('--integration-root',type=Path,required=True);special.add_argument('--production-root',type=Path,required=True);special.add_argument('--integration-output',type=Path,required=True);special.add_argument('--complete',action='store_true');a=special.parse_args(argv);integration_proof(a.integration_root,a.production_root,a.integration_output,a.complete);return
    parser=argparse.ArgumentParser(description=__doc__)
    for side in SIDES:parser.add_argument('--'+side+'-source',type=Path,required=True)
    parser.add_argument('--c-source',type=Path,required=True);parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--harness',type=Path,default=Path(__file__).with_name('bench_hma_review.rs'))
    parser.add_argument('--build-only',action='store_true');parser.add_argument('--pairs',type=int,default=12);parser.add_argument('--repeats',type=int,default=31)
    args=parser.parse_args(argv)
    if args.pairs!=12 or args.repeats!=31:parser.error('exact12 pairs and31 samples required; do not cut repetitions')
    for key in ('baseline_source','candidate_source','c_source','output','harness'):setattr(args,key,getattr(args,key).resolve())
    args.output.mkdir(parents=True,exist_ok=True)
    if args.build_only:build(args)
    else:measure(args)

if __name__=='__main__':main()
