"""Frozen source, wheel, installed ELF and release-toolchain provenance."""
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import zipfile

IDENTITY_SCRIPT = r'''
import hashlib,json,platform
from pathlib import Path
from importlib.metadata import version
import numpy,polars,polars_talib
folder=Path(polars_talib.__file__).parent
files=[p for p in folder.iterdir() if p.suffix in ('.so','.pyd')]
assert len(files)==1,files
print(json.dumps({'python':platform.python_version(),'platform':platform.platform(),
 'polars':polars.__version__,'numpy':numpy.__version__,'package':version('polars-talib'),
 'talib':polars_talib.__talib_version__,'native_files':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}}))
'''


def sha256(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as source:
        for block in iter(lambda: source.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def source_record(path, expected):
    if not re.fullmatch(r'[0-9a-f]{40}', expected):
        raise ValueError('every source pin must be a full immutable SHA')
    path = Path(path).resolve()
    commit = subprocess.check_output(['git', '-C', str(path), 'rev-parse', 'HEAD'], text=True).strip()
    if commit != expected:
        raise ValueError(f'source pin mismatch: {commit} != {expected}')
    if subprocess.check_output(['git', '-C', str(path), 'status', '--porcelain']):
        raise ValueError('source checkout must be clean')
    digest = hashlib.sha256()
    for item in sorted(path.rglob('*')):
        relative = item.relative_to(path)
        if not item.is_file() or not (item.suffix in ('.rs', '.py') or item.name in ('Cargo.toml', 'Cargo.lock')):
            continue
        if {'target', '.venv', '.git', '__pycache__'}.intersection(relative.parts):
            continue
        if relative.parts[0] not in ('src', 'python', 'talib', 'talib-sys') and len(relative.parts) > 1:
            continue
        digest.update(str(relative).encode()); digest.update(item.read_bytes())
    return {'commit': commit, 'source_sha256': digest.hexdigest(), 'clean': True}


def identity(python):
    return json.loads(subprocess.check_output([str(Path(python).absolute()), '-c', IDENTITY_SCRIPT], text=True))



def wheel_record(path, installed):
    wheels = list(Path(path).glob('*.whl'))
    if len(wheels) != 1:
        raise ValueError('exactly one preserved wheel per build required')
    wheel = wheels[0]
    with zipfile.ZipFile(wheel) as archive:
        native = {Path(name).name: hashlib.sha256(archive.read(name)).hexdigest()
                  for name in archive.namelist() if name.endswith(('.so', '.pyd'))}
    actual = {Path(name).name: digest for name, digest in installed['native_files'].items()}
    if not native or actual != native:
        raise ValueError('installed native module does not match the preserved wheel')
    return {'path': str(wheel.resolve()), 'sha256': sha256(wheel), 'native_files': installed['native_files']}


def flags_record():
    rustc = subprocess.check_output(['rustc', '--version', '--verbose'], text=True)
    if not rustc.startswith('rustc 1.90.0 '):
        raise ValueError('Rust 1.90.0 required')
    expected = {'CARGO_PROFILE_RELEASE_OPT_LEVEL':'3', 'CARGO_PROFILE_RELEASE_LTO':'false',
                'CARGO_PROFILE_RELEASE_CODEGEN_UNITS':'16', 'RUSTFLAGS':'', 'CARGO_ENCODED_RUSTFLAGS':''}
    if any(os.environ.get(k) != v for k,v in expected.items()):
        raise ValueError('portable product Cargo release settings differ')
    return {'rustc': rustc, 'cargo': subprocess.check_output(['cargo', '--version'], text=True),
            'cc': subprocess.check_output(['cc', '--version'], text=True),
            'cmake': subprocess.check_output([os.environ.get('CMAKE','cmake'), '--version'], text=True),
            'environment': {key: os.environ.get(key) for key in
                ('RUSTUP_TOOLCHAIN', 'CFLAGS', 'CXXFLAGS', 'RUSTFLAGS', 'CARGO_ENCODED_RUSTFLAGS',
                 'CARGO_PROFILE_RELEASE_DEBUG', 'CARGO_PROFILE_RELEASE_OPT_LEVEL', 'CARGO_PROFILE_RELEASE_LTO',
                 'CARGO_PROFILE_RELEASE_CODEGEN_UNITS', 'CARGO_BUILD_JOBS', 'CARGO_TARGET_DIR', 'CARGO_BUILD_BUILD_DIR', 'CMAKE')}}



def validate_identities(identities):
    if set(identities) != {'original', 'prior', 'combined', 'candidate'}:
        raise ValueError('exactly the four pinned builds are required')
    keys = ('python','platform','polars','numpy','package')
    normalized = [{k: row[k] for k in keys} for row in identities.values()]
    if any(row != normalized[0] for row in normalized):
        raise ValueError('installed runtimes differ')
    first = normalized[0]
    if first['python'] != '3.12.15' or first['polars'] != '1.44.2' or first['numpy'] != '2.5.3' or first['package'] != '0.2.1':
        raise ValueError('unexpected pinned runtime')
    if not identities['original']['talib'].startswith('0.8.1 '):
        raise ValueError('original runtime must be C0.8.1')
    for side in ('prior','combined','candidate'):
        if identities[side]['talib'] != '0.8.3 (native Rust; polars-talib compatibility)':
            raise ValueError('native runtime must be the pinned compatibility adapter')
    return first


def require_product_compile(log, source):
    """Require an actual product compile from this exact resolved checkout."""
    source=Path(source).resolve()
    paths=[]
    for line in Path(log).read_text().splitlines():
        match=re.fullmatch(r'\s*Compiling polars_talib v0\.2\.1 \((.+)\)\s*',line)
        if match: paths.append(Path(match[1]).resolve())
    if not paths or any(path!=source for path in paths):
        raise ValueError('build log must compile polars_talib from exactly '+str(source))
    return {'log':str(Path(log).resolve()),'log_sha256':sha256(log),
            'product_source':str(source),'product_compile_lines':len(paths)}


if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser(description='Verify an actual source-pinned product compile without optional shell tools')
    parser.add_argument('--compile-log',type=Path,required=True)
    parser.add_argument('--source',type=Path,required=True)
    args=parser.parse_args()
    print(json.dumps(require_product_compile(args.compile_log,args.source)))


def elf_record(path):
    import struct
    path=Path(path)
    with path.open('rb')as source:header=source.read(64)
    if (len(header)!=64 or header[:7]!=b'\x7fELF\x02\x01\x01'
            or struct.unpack_from('<HHI',header,16)!=(3,62,1)
            or struct.unpack_from('<H',header,52)[0]!=64):
        raise ValueError('measured product must be a full ELF64 LE x86-64 ET_DYN header')
    return {'path':str(path),'sha256':sha256(path),'format':'ELF64 little-endian x86-64 ET_DYN'}

COLD_TEST='sarext_legacy::tests::cold_parallel_dispatch_matches_portable_scalar_without_shared_mutable_inputs'

def require_cold_dispatch(list_log,run_log):
    names=Path(list_log).read_text().splitlines();lines=Path(run_log).read_text().splitlines()
    if names.count(COLD_TEST+': test')!=1:
        raise ValueError('exact full namespace cold test missing/duplicated in actual list')
    if lines.count('running 1 test')!=1 or lines.count('test '+COLD_TEST+' ... ok')!=1:
        raise ValueError('fresh process did not pass exactly the required cold test')
    if sum(bool(re.fullmatch(r'test result: ok\. 1 passed; 0 failed; 0 ignored; .*',line))for line in lines)!=1:
        raise ValueError('cold test result must be exactly one passed, zero failed/ignored')
    return {'test':COLD_TEST,'list_log_sha256':sha256(list_log),'run_log_sha256':sha256(run_log),
            'exact_full_namespace':True,'fresh_alone_before_full_suite':True}


def require_public_test_dependencies(workflow):
    import shlex
    lines=[line.strip()for line in workflow.splitlines()if line.strip().startswith('uv pip install --python "envs/$side"')and 'maturin=='in line]
    if len(lines)!=1:
        raise ValueError('one reviewed fresh-arm dependency installation is required')
    tokens=set(shlex.split(lines[0]))
    if not {'pytest==8.4.2','pytest-benchmark==5.3.0','numpy==2.5.3','TA-Lib==0.8.1'}.issubset(tokens):
        raise ValueError('full public tests require the pinned benchmark fixture plugin and C oracle')
    return True


def require_private_arm_commands(records,workspace,*,contracts=False):
    """Bind actual recorded command/env paths to one private arm ownership."""
    workspace=Path(workspace).resolve()
    expected=[('combined','combined-cold-list'),('combined','combined-cold'),('candidate','candidate-cold-list'),('candidate','candidate-cold'),('prior','prior-rust-tests'),('combined','combined-rust-tests'),('candidate','candidate-rust-tests')]if contracts else[(s,None)for s in ('prior','combined','candidate','original')]
    actual=[(row.get('side'),row.get('label'))for row in records]
    if actual!=expected:raise ValueError('exact private arm command inventory/order required')
    for row,(side,label)in zip(records,expected):
        target=workspace/'add-shared-route-target'/side;python=workspace/'envs'/side/'bin/python'
        env=row.get('environment',{});wanted={'CARGO_TARGET_DIR':str(target),'CARGO_BUILD_BUILD_DIR':str(target),'PYO3_PYTHON':str(python)}
        if env!=wanted:raise ValueError('wheel/contract environment is not private to the requested arm')
        command=row['command'];config='build.build-dir="'+str(target)+'"'
        if contracts:
            expected_command=['cargo','--config',config,'test','--release','--lib','--locked','--target-dir',str(target),'--manifest-path',str(workspace/'sources'/side/'Cargo.toml')]
            if label.endswith('-cold-list'):expected_command+=['--','--list']
            elif label.endswith('-cold'):expected_command+=['--',COLD_TEST,'--exact','--nocapture','--test-threads=1']
        else:
            expected_command=[str(python),'-m','maturin','build','--config',config,'--target-dir',str(target),'--release','--locked','--interpreter',str(python),'--out',str(workspace/'wheels'/side)]
        if command!=expected_command:
            raise ValueError('actual wheel/contract full argv differs from its private arm/profile/filter')
    return {'commands':len(records),'private_per_arm':True,'records':records}
