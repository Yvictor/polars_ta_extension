"""Build and validate the enabled VAR binary without invoking its timing mode."""
import argparse
import hashlib
import itertools
import json
import math
import os
from pathlib import Path
import platform
import re
import shutil
import struct
import subprocess
import sys

HERE = Path(__file__).resolve().parent
SPEC = HERE / 'var_windows_cases.json'
ARMS = ('original', 'baseline', 'candidate')
POISON = 0x7ff80000000055aa


def need(value, reason):
    if not value:
        raise ValueError(reason)


def read_json(text):
    def pairs(items):
        result = {}
        for key, value in items:
            need(key not in result, 'duplicate JSON key')
            result[key] = value
        return result
    return json.loads(text, object_pairs_hook=pairs,
                      parse_constant=lambda x: (_ for _ in ()).throw(ValueError('nonfinite JSON')))


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda: f.read(1048576), b''):
            h.update(block)
    return h.hexdigest()


def command(argv, log, cwd=None, env=None, timeout=1800):
    argv = list(map(str, argv))
    Path(str(log) + '.command.json').write_text(json.dumps(argv, indent=2) + '\n')
    with Path(log).open('w') as f:
        subprocess.run(argv, cwd=cwd, env=env, stdout=f, stderr=subprocess.STDOUT,
                       check=True, timeout=timeout)


def specification():
    spec = read_json(SPEC.read_text())
    cases = spec['cases']
    need(len(cases) == len({c['name'] for c in cases}) == 16, 'fixed16 inventory differs')
    expected = [(k, 'typed', p, 1000000, 'wave') for k in ('var', 'stddev') for p in (2, 5, 200)]
    expected += [(k, 'typed', 5, n, 'wave') for k in ('var', 'stddev') for n in (100, 10000)]
    expected += [(k, 'abstract', 5, 1000000, 'wave') for k in ('var', 'stddev')]
    expected += [('var', 'typed', 5, 1000000, 'flat'), ('stddev', 'typed', 5, 1000000, 'highoffset'),
                 ('ema', 'typed', 14, 1000000, 'wave'), ('add', 'typed', 0, 1000000, 'wave')]
    for c, (kind, api, period, n, pattern) in zip(cases, expected):
        need(c == dict(name=f'{kind}_{api}_{period}_{n}_{pattern}', function=kind, api=api,
                       period=period, rows=n, pattern=pattern,
                       iterations={100:1000, 10000:10, 1000000:1}[n]), 'case differs')
    need(spec['rounds'] == 12 and spec['samples'] == 31 and spec['warmups'] == 5, 'prospective protocol differs')
    need(spec['children_per_profile'] == 576 and spec['samples_per_profile'] == 17856, 'prospective counts differ')
    need(spec['public_contracts'] == 43324 and spec['persistent_C_goldens'] == 605, 'contract inventory differs')
    return spec


def pins(spec):
    values = [spec[k] for k in ('original_C083_commit', 'baseline_current_dev_commit', 'candidate_commit')]
    need(all(isinstance(x, str) and re.fullmatch('[0-9a-f]{40}', x) for x in values), 'Unreviewed/unset immutable source pin')
    need(len(set(values)) == 3, 'source arms must differ')
    return dict(zip(ARMS, values))


def snapshot(root):
    paths = subprocess.check_output(['git', '-C', root, 'ls-files'], text=True).splitlines()
    return {n:sha(root / n) for n in paths}


def source(root, expected):
    need(subprocess.check_output(['git', '-C', root, 'rev-parse', 'HEAD'], text=True).strip() == expected, 'wrong source commit')
    need(not subprocess.check_output(['git', '-C', root, 'status', '--porcelain']), 'dirty source')
    return dict(commit=expected, tree=subprocess.check_output(['git', '-C', root, 'rev-parse', 'HEAD^{tree}'], text=True).strip(), files=snapshot(root))


def source_scope(roots, expected):
    records = {arm:source(roots[arm], expected[arm]) for arm in ARMS}
    frozen = read_json((HERE.parent / 'tests/data/var-windows/source-freeze.json').read_text())
    need(frozen['base'] == expected['baseline'] and frozen['commit'] == expected['candidate'], 'source freeze pins differ')
    changed = subprocess.check_output(['git', '-C', roots['candidate'], 'diff', '--name-only', expected['baseline'], expected['candidate']], text=True).splitlines()
    need(set(changed) == set(frozen['files']) and len(changed) == 8, 'candidate eight-file source scope differs')
    for name, digest in frozen['files'].items():
        need(sha(roots['candidate'] / name) == digest, 'frozen source bytes differ')
    for name in ('ema', 'add', 'stddev'):
        n = f'ta_codegen/output/rust/library/src/ta_func/{name}.rs'
        need(sha(roots['candidate'] / n) == sha(roots['baseline'] / n), 'control source differs')
    for name in ('ABI.manifest', 'ABI.released', 'include/ta_func.h'):
        need(sha(roots['candidate'] / name) == sha(roots['baseline'] / name), 'ABI source differs')
    return records


def gate_record(out, expected):
    d = out / 'source-gates';record = read_json((d / 'source-gates.json').read_text())
    need(record['complete'] is True and record['timing_enabled'] is False, 'source gate incomplete or timers enabled')
    need(record['candidate'] == expected['candidate'] and record['baseline'] == expected['baseline'], 'source gate pins differ')
    frozen = read_json((HERE.parent / 'tests/data/var-windows/source-freeze.json').read_text())
    need(record['source_files'] == frozen['files'], 'source gate freeze differs')
    names = {'protocol-tests.log','generator-tests.log','generator-clippy.log','library-tests-and-docs.log','library-clippy.log','regen-check.log','server-build.log','all-indicator-regtests.log'}
    need(set(record['logs']) == names, 'source gate log inventory differs')
    for name, digest in record['logs'].items():
        need((d / name).is_file() and (d / name).stat().st_size > 0 and sha(d / name) == digest, 'source gate log missing/changed')
    need((d / 'candidate-status.txt').read_bytes() == b'', 'source gate candidate dirty')
    commit = subprocess.check_output(['git','-C',HERE.parent,'rev-parse','HEAD'],text=True).strip()
    need((d / 'controller-commit.txt').read_text().strip() == commit, 'source gate controller differs')
    sources = [p for p in HERE.glob('*var_windows*') if p.is_file()] + [HERE / 'VAR_WINDOWS_CI.md', HERE.parent / 'tests/test_var_windows_preflight.py', HERE.parent / 'tests/data/var-windows/source-freeze.json', HERE.parent / 'tests/data/var-windows/normal-codegen-reference.json', HERE.parent / 'tests/test_var_windows_codegen.py']
    for p in sources:
        need(sha(d / 'controller' / p.name) == sha(p), 'source gate controller bytes differ')
    workflow = HERE.parent / '.github/workflows/var-windows-preflight.yml'
    need(sha(d / 'workflow.yml') == sha(workflow), 'source gate workflow differs')
    return dict(record=record,sha256=sha(d / 'source-gates.json'),controller_commit=commit)


def runtime(version):
    need(platform.system() == 'Linux' and platform.machine() == 'x86_64', 'Linux x86_64 required')
    need(version in ('1.90.0', '1.97.0'), 'unapproved compiler')
    text = subprocess.check_output(['rustc', '--version', '--verbose'], text=True)
    need(text.startswith('rustc ' + version + ' ') and 'host: x86_64-unknown-linux-gnu' in text, 'wrong Rust compiler/host')
    profile = dict(CARGO_PROFILE_RELEASE_OPT_LEVEL='3', CARGO_PROFILE_RELEASE_LTO='false' if version == '1.90.0' else 'thin',
                   CARGO_PROFILE_RELEASE_CODEGEN_UNITS='16' if version == '1.90.0' else '1', CARGO_PROFILE_RELEASE_DEBUG='false',
                   RUSTFLAGS='', CARGO_ENCODED_RUSTFLAGS='', CFLAGS='', CXXFLAGS='')
    need(all(os.environ.get(k) == v for k, v in profile.items()), 'normal portable profile differs')
    return dict(rustc=text, profile=profile, platform=platform.platform(), python=sys.version,
                cc=subprocess.check_output(['cc', '--version'], text=True), cpuinfo=Path('/proc/cpuinfo').read_text(),
                allowed_cpus=sorted(os.sched_getaffinity(0)))


def fixture(path, n, pattern):
    need(type(n) is int and n in (100, 10000, 1000000), 'rows differ')
    need(pattern in ('wave', 'flat', 'highoffset'), 'pattern differs')
    with Path(path).open('wb') as f:
        f.write(b'VARFIX01' + struct.pack('<Q', n))
        for i in range(n):
            value = 3.3 if pattern == 'flat' else (2.0**40 if pattern == 'highoffset' else 64.0) + ((i % 37) - 18) * .125
            f.write(struct.pack('<d', value))
        for i in range(n):
            f.write(struct.pack('<d', 32.0 + ((i % 11) - 5) * .0625))
    return dict(path=str(path), sha256=sha(path), bytes=16 + n * 16, rows=n, pattern=pattern)


def capture(path, c):
    d = Path(path).read_bytes()
    n = c['rows']; b = 0 if c['function'] == 'add' else c['period'] - 1; count = n - b
    need(len(d) == 32 + 8 * (n + 8) and d[:8] == b'VAROUT01', 'capture shape/magic differs')
    need(struct.unpack('<QQQ', d[8:32]) == (n, b, count), 'range differs')
    need(d[32 + count * 8:] == struct.pack('<Q', POISON) * (n + 8 - count), 'tail differs')
    need(all(math.isfinite(v[0]) for v in struct.iter_unpack('<d', d[32:32 + count * 8])), 'timed scenario output nonfinite')
    return d


def elf_scope(binary, destination, arm):
    need(binary.read_bytes()[:4] == b'\x7fELF', 'normal product not ELF')
    destination.mkdir(parents=True)
    raw = subprocess.check_output(['nm', '-S', '-C', '--defined-only', binary], text=True)
    (destination / 'symbols.txt').write_text(raw)
    selected = {}
    for line in raw.splitlines():
        f = line.split(None, 3)
        if len(f) != 4 or f[2].lower() != 't':
            continue
        name = f[3]
        role = None
        if arm == 'original':
            if name in ('TA_VAR', 'TA_STDDEV'):role = name[3:].lower()
        else:
            for function in ('var', 'stddev'):
                if ('Core>::' + function in name or 'Core::' + function in name) and name.endswith('::' + function):role = function
        if role:
            need(role not in selected, 'ambiguous normal public function symbol')
            start, size = int(f[0], 16), int(f[1], 16);need(size > 0, 'empty function symbol')
            argv = ['objdump', '-d', '-r', '-C', '--start-address=' + str(start), '--stop-address=' + str(start + size), binary]
            asm = subprocess.check_output(argv, text=True);p = destination / (role + '.asm');p.write_text(asm)
            selected[role] = dict(symbol=name, address=start, bytes=size, assembly=str(p), sha256=sha(p), command=list(map(str, argv)))
    need(set(selected) == {'var', 'stddev'}, 'normal public VAR/STDDEV symbol missing or inlined')
    return dict(binary_sha256=sha(binary), symbols_sha256=sha(destination / 'symbols.txt'), scopes=selected,
                proof_status='UNREVIEWED actual fast-loop/fallback/reseed CFG; timing blocked')


def main():
    parser = argparse.ArgumentParser()
    for arm in ARMS:parser.add_argument('--' + arm + '-source', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True);parser.add_argument('--rust-version', choices=('1.90.0', '1.97.0'), required=True)
    args = parser.parse_args();out = args.output.resolve();out.mkdir(parents=True, exist_ok=True)
    need(not (out / 'preflight.json').exists(), 'do not overwrite completed preflight')
    spec = specification();expected = pins(spec);roots = {arm:getattr(args, arm + '_source').resolve() for arm in ARMS}
    records = source_scope(roots, expected);rt = runtime(args.rust_version);gates = gate_record(out, expected)
    cpu = min(os.sched_getaffinity(0));os.sched_setaffinity(0, {cpu});need(os.sched_getaffinity(0) == {cpu}, 'CPU affinity failed')
    common = ['rustc', '--edition=2021', '-O', '-C', 'lto=' + rt['profile']['CARGO_PROFILE_RELEASE_LTO'], '-C', 'codegen-units=' + rt['profile']['CARGO_PROFILE_RELEASE_CODEGEN_UNITS'], '-Dwarnings', '--check-cfg=cfg(c_reference,test)']
    builds = {};bins = {};libpaths = {}
    for arm in ARMS:
        binary = out / arm
        if arm == 'original':
            b = out / 'C083-build';install = out / 'C083-install'
            command(['cmake', '-S', roots[arm], '-B', b, '-DCMAKE_BUILD_TYPE=Release', '-DBUILD_STATIC_LIBS=ON', '-DBUILD_SHARED_LIBS=ON', '-DBUILD_DEV_TOOLS=OFF', '-DCMAKE_EXPORT_COMPILE_COMMANDS=ON', '-DCMAKE_C_FLAGS_RELEASE=-O3 -DNDEBUG -ffp-contract=off', '-DCMAKE_INSTALL_PREFIX=' + str(install)], out / 'original-configure.log')
            command(['cmake', '--build', b, '--target', 'install', '--parallel', '1'], out / 'original-build.log')
            lib = install / 'lib/libta-lib.a';need(lib.is_file(), 'C083 archive missing')
            libs = list((install / 'lib').glob('libta-lib.so.*'));need(libs, 'C083 shared oracle missing');shared = min(libs, key=lambda p:len(p.name))
            builds[arm] = dict(archive=str(lib), archive_sha256=sha(lib), shared=str(shared), shared_sha256=sha(shared), cache_sha256=sha(b / 'CMakeCache.txt'), compile_commands_sha256=sha(b / 'compile_commands.json'))
            argv = common + [str(HERE / 'bench_var_windows.rs'), '--cfg', 'c_reference', '-L', 'native=' + str(lib.parent), '-l', 'static=ta-lib', '-l', 'm', '-o', binary]
        else:
            target = out / ('target-' + arm);build = out / ('build-' + arm);env = os.environ.copy();env.update(CARGO_TARGET_DIR=str(target), CARGO_BUILD_BUILD_DIR=str(build))
            command(['cargo', 'build', '--release', '--locked', '-vv', '-p', 'ta-lib', '--manifest-path', roots[arm] / 'ta_codegen/output/rust/Cargo.toml'], out / (arm + '-cargo.log'), env=env)
            text = (out / (arm + '-cargo.log')).read_text();plain = re.sub(r'\x1b\[[0-9;]*m', '', text)
            package = re.escape(str(roots[arm] / 'ta_codegen/output/rust/library'))
            need(len(re.findall(r'Compiling ta-lib v[^\n]+ \(' + package + r'\)', plain)) == 1, 'fresh exact primary source compile not proved')
            lib = target / 'release/libta_lib.rlib';need(lib.is_file(), 'normal rlib missing')
            retained = out / ('libraries-' + arm);retained.mkdir();shutil.copyfile(lib, retained / lib.name)
            fp = (target if args.rust_version == '1.90.0' else build) / 'release/.fingerprint';need(fp.is_dir(), 'Cargo fingerprints missing');shutil.copytree(fp, retained / 'fingerprints')
            builds[arm] = dict(rlib=str(retained / lib.name), sha256=sha(retained / lib.name), target=str(target), build=str(build), primary_log_sha256=sha(out / (arm + '-cargo.log')))
            libpaths[arm] = lib
            argv = common + [str(HERE / 'bench_var_windows.rs'), '-L', 'dependency=' + str(target / 'release/deps'), '-L', 'dependency=' + str(build / 'release/deps'), '--extern', 'ta_lib=' + str(lib), '-o', binary]
            pub = out / (arm + '-public');command(common + [str(HERE / 'var_windows_public.rs'), '-L', 'dependency=' + str(target / 'release/deps'), '-L', 'dependency=' + str(build / 'release/deps'), '--extern', 'ta_lib=' + str(lib), '-o', pub], out / (arm + '-public-build.log'))
            command([pub, out / (arm + '-contracts')], out / (arm + '-contracts.log'))
            test = out / (arm + '-605-tests');test_source = roots['candidate'] / 'ta_codegen/output/rust/library/tests/var_checked_windows.rs'
            command(common + [str(test_source), '--test', '-L', 'dependency=' + str(target / 'release/deps'), '-L', 'dependency=' + str(build / 'release/deps'), '--extern', 'ta_lib=' + str(lib), '-o', test], out / (arm + '-605-build.log'))
            command([test, '--test-threads=1'], out / (arm + '-605.log'))
        command(argv, out / (arm + '-build.log'))
        test = out / (arm + '-harness-tests');command(argv[:-2] + ['--test', '-o', test], out / (arm + '-harness-test-build.log'));command([test, '--test-threads=1'], out / (arm + '-harness-tests.log'))
        description = read_json(subprocess.check_output([binary, '--describe'], text=True))
        need(description['timing_enabled'] is True and description['opaque_fnptr'] is True and type(description['pointer_bytes']) is int and description['pointer_bytes'] == 8 and description['cases'] == 16 and description['c_reference'] is (arm == 'original'), 'enabled-body/explicit pointer route or implementation differs')
        if arm == 'original':need(description['version'].startswith('0.8.3'), 'wrong C oracle version')
        bins[arm] = dict(path=str(binary), sha256=sha(binary), description=description, command=list(map(str, argv)), elf=elf_scope(binary, out / ('normal-elf-' + arm), arm))
    command([sys.executable, HERE / 'var_windows_contract.py', '--baseline', out / 'baseline-contracts', '--candidate', out / 'candidate-contracts', '--C083-library', shared, '--output', out / 'public-contracts.json'], out / 'public-contracts.log')
    inputs = {};goldens = out / 'goldens';goldens.mkdir()
    for c in spec['cases']:
        key = f"{c['rows']}-{c['pattern']}"
        if key not in inputs:inputs[key] = fixture(out / (key + '.input'), c['rows'], c['pattern'])
        prior = None
        for arm in ARMS:
            dest = goldens / (c['name'] + '-' + arm + '.bin')
            command([bins[arm]['path'], c['name'], inputs[key]['path'], dest, '--capture-only'], out / (c['name'] + '-' + arm + '-capture.log'))
            raw = capture(dest, c)
            if prior is not None:need(raw == prior, 'selected finite range/output/zero/tail differs across arms')
            prior = raw
    need(records == source_scope(roots, expected), 'sources changed during preflight')
    need(gates == gate_record(out, expected), 'source gate changed during preflight')
    archives = out / 'source-archives';archives.mkdir()
    for arm in ARMS:
        subprocess.run(['git','-C',roots[arm],'archive','--format=tar.gz','-o',archives / (arm + '.tar.gz'),'HEAD'],check=True)
    result = dict(source_archives={p.name:sha(p) for p in archives.iterdir()}, pins=expected, sources=records, runtime=rt, source_gates=gates, affinity_cpu=cpu, builds=builds, binaries=bins, inputs=inputs,
                  goldens={p.name:sha(p) for p in sorted(goldens.iterdir())}, public_contracts=read_json((out / 'public-contracts.json').read_text()),
                  controller={p.name:sha(p) for p in HERE.glob('*var_windows*') if p.is_file()}, timing_enabled=False, timer_body_compiled=True, timings_collected=False,
                  prospective_children=576, prospective_samples=17856, static_status='UNREVIEWED: actual fast-loop/fallback/reseed proof required before timers',
                  limits=['No timings collected.', 'C083 upstream oracle differs from consumer C081.', 'Actual normal ELF retained; symbol extraction alone proves no hot-loop guard removal.', 'Private targets/builds and retained rlib/fingerprints; ELF-to-rlib linkage is command/hash/source provenance, not independent linker reconstruction.'])
    (out / 'preflight.json').write_text(json.dumps(result, indent=2) + '\n')
    print('ENABLED_BINARY_PREFLIGHT_PASS_NO_TIMERS_EXECUTED', flush=True)


if __name__ == '__main__':
    main()
