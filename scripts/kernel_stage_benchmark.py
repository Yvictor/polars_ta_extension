"""Bounded same-runner kernel/adapter ablation; no builds during measurement."""
import argparse
import hashlib
import itertools
import json
import math
import os
from pathlib import Path
import re
import statistics
import shutil
import subprocess
import time

from kernel_ablation_benchmark import SIDES, ORDERS, sha256, verify_build

LENGTHS = (1000, 10000, 1000000)
MODES = ('newcall', 'setup', 'kernel', 'ffi', 'materialize', 'full', 'init_zero_int', 'init_nan_real')
HERE = Path(__file__).resolve().parent
PROBE = HERE / 'kernel_stage_probe.rs'
PATTERN = re.compile(r'PROBE (doji|mmi)/(\w+)/(\d+) allocations=(\d+) bytes=(\d+) holder_bytes=(\d+) ns=(\[[^\n]+\])')


def parse_probe(text, family, mode, length):
    lines = text.splitlines()
    if not lines or not lines[0].startswith('C_VERSION 0.8.1 '):
        raise ValueError('C0.8.1 runtime was not asserted')
    matches = list(PATTERN.finditer(text))
    if len(matches) != 1:
        raise ValueError('missing or duplicate stage result')
    found = matches[0]
    if found.group(1, 2, 3) != (family, mode, str(length)):
        raise ValueError('stage identity mismatch')
    samples = json.loads(found[7])
    if len(samples) != 7 or any(isinstance(x, bool) or not isinstance(x, (int, float)) or not math.isfinite(x) or x <= 0 for x in samples):
        raise ValueError('invalid stage samples')
    return {'family': family, 'mode': mode, 'n': length, 'allocations': int(found[4]),
            'bytes': int(found[5]), 'holder_bytes': int(found[6]), 'samples_ns': samples,
            'median_ns': statistics.median(samples), 'c_version': lines[0].removeprefix('C_VERSION ')}


def kernel_cases():
    return [(family, n, mode) for family in ('doji', 'mmi') for n in LENGTHS
            for mode in (*MODES, *(('modern', 'abstract') if family == 'mmi' else ())) ]


def fingerprint_value(raw):
    if not re.fullmatch('[0-9a-f]{16}', raw):
        raise ValueError('invalid Cargo fingerprint')
    return int.from_bytes(bytes.fromhex(raw), 'little')


def native_dependency_records(target, expected_rustflags=()):
    """Follow actual native cdylib Cargo dependency fingerprints, never a global rlib glob."""
    root = target / 'release/.fingerprint'
    names = ('ta_lib', 'polars', 'serde', 'jemallocator')
    parents = []
    for path in root.glob('polars_talib-*/lib-_polars_talib.json'):
        data = json.loads(path.read_text())
        deps = {entry[1]: entry[3] for entry in data['deps']}
        if set(names) <= deps.keys() and data['rustflags'] == list(expected_rustflags):
            parents.append((path, {name: deps[name] for name in names}))
    if not parents or any(deps != parents[0][1] for _, deps in parents):
        raise ValueError('native wheel dependency fingerprints missing or disagree')
    resolved = {}; evidence = {}
    for path, _ in parents:
        raw_parent = path.with_suffix('')
        fingerprint_value(raw_parent.read_text().strip())
        evidence[str(path)] = sha256(path); evidence[str(raw_parent)] = sha256(raw_parent)
    for name, expected in parents[0][1].items():
        matches = []
        for path in root.glob('*/lib-' + name):
            raw = path.read_text().strip()
            if re.fullmatch('[0-9a-f]{16}', raw) and fingerprint_value(raw) == expected:
                artifact_hash = path.parent.name.rsplit('-', 1)[1]
                artifact = target / 'release/deps' / ('lib' + name + '-' + artifact_hash + '.rlib')
                metadata = path.with_name(path.name + '.json')
                if artifact.is_file() and metadata.is_file():
                    matches.append((artifact, path, metadata))
        if len(matches) != 1:
            raise ValueError('native dependency fingerprint does not select exactly one artifact: ' + name)
        artifact, fingerprint, metadata = matches[0]
        resolved[name] = artifact
        evidence[str(fingerprint)] = sha256(fingerprint); evidence[str(metadata)] = sha256(metadata)
    return resolved, evidence


def mapper(source):
    text = (source / 'src/generated.rs').read_text()
    start = text.index('pub(crate) fn option_key(')
    begin = text.index('{', start); level = 1; end = begin + 1
    while level:
        level += (text[end] == '{') - (text[end] == '}'); end += 1
    return text[start:end]


def build(args):
    provenance = verify_build(args)
    folder = args.output / 'stages'; folder.mkdir(exist_ok=True)
    archives = list(args.target_dir.glob('release/build/talib-sys-*/out/lib/libta-lib.a'))
    if len(archives) != 1:
        raise ValueError('exactly one original C archive required: ' + repr(archives))
    archive = archives[0]
    dependencies, dependency_fingerprints = native_dependency_records(args.target_dir)
    command = [str(args.base_python.absolute()), '-c',
               'import sys;sys.path.insert(0,sys.argv[1]);from migration_benchmark import frame;frame(1000000,1000)["close"].to_numpy().astype("<f8").tofile(sys.argv[2])',
               str(HERE), str(folder / 'input.bin')]
    subprocess.run(command, check=True)
    native_paths = sorted(args.target_dir.glob('release/build/*/out/lib'))
    native_archives = {str(p): sha256(p) for d in native_paths for p in d.glob('*.a')}
    records = {}
    body = PROBE.read_text().split('\n', 1)[1]
    for side in SIDES:
        source = getattr(args, side + '_source').resolve()
        support = folder / (side + '-source') / 'compat'
        shutil.copytree(source / 'src/compat', support, dirs_exist_ok=True)
        shutil.copyfile(source / 'src/compat.rs', support / 'mod.rs')
        support_files = {str(p): sha256(p) for p in support.rglob('*.rs')}
        wrapper = folder / (side + '.rs')
        modules = '#![allow(dead_code,unused_imports)]\n'
        for name, relative in (('native', 'native.rs'), ('compat', 'compat.rs'), ('params', 'params.rs'), ('utils', 'utils.rs')):
            module_path = support / 'mod.rs' if name == 'compat' else source / 'src' / relative
            modules += f'#[path="{module_path}"] mod {name};\n'
        modules += 'mod generated {\n' + mapper(source) + '\n}\n'
        wrapper.write_text(modules + body)
        binary = folder / ('probe-' + side)
        command = ['rustc', '--edition=2021', '-O', '-C', 'codegen-units=16', '-C', 'lto=off', str(wrapper),
                   '-L', 'dependency=' + str(args.target_dir / 'release/deps')]
        for name, path in dependencies.items():
            command += ['--extern', name + '=' + str(path)]
        for path in native_paths:
            command += ['-L', 'native=' + str(path)]
        command += ['-l', 'static=ta-lib', '-l', 'm', '-o', str(binary)]
        with (folder / (side + '-build.log')).open('w') as log:
            subprocess.run(command, check=True, stdout=log, stderr=subprocess.STDOUT)
        records[side] = {'command': command, 'wrapper': str(wrapper), 'wrapper_sha256': sha256(wrapper),
                         'binary': str(binary), 'binary_sha256': sha256(binary),
                         'source': provenance['builds'][side]['source'], 'support_source_files': support_files}
    record = {'builds': records, 'production_allocator': 'jemallocator::Jemalloc',
              'context': 'Rust1.90 portable -O 16CGU no LTO, same dependency artifacts as release wheels',
              'dependencies': {str(path): sha256(path) for path in dependencies.values()},
              'dependency_fingerprints': dependency_fingerprints,
              'native_archives': native_archives, 'c_archive': str(archive), 'c_archive_sha256': sha256(archive),
              'input_sha256': sha256(folder / 'input.bin'),
              'probe_source_sha256': sha256(PROBE), 'controller_sha256': sha256(__file__),
              'cases': kernel_cases(), 'iters_by_n': {1000: 100, 10000: 30, 1000000: 3},
              'limitation': 'full means native::compute with predecoded Params, not Python/plugin deserialization; initialization controls have different element widths; counting wrapper adds a disabled atomic check around allocation calls during timings'}
    (folder / 'build-provenance.json').write_text(json.dumps(record, indent=2) + '\n')


def verify(args):
    overall = verify_build(args)
    folder = args.output / 'stages'
    record = json.loads((folder / 'build-provenance.json').read_text())
    files = {**record['dependencies'], **record['dependency_fingerprints'], **record['native_archives'], str(folder / 'input.bin'): record['input_sha256'],
             str(PROBE): record['probe_source_sha256'], str(Path(__file__)): record['controller_sha256']}
    for entry in record['builds'].values():
        files[entry['wrapper']] = entry['wrapper_sha256']; files[entry['binary']] = entry['binary_sha256']
        files.update(entry['support_source_files'])
    if any(sha256(path) != digest for path, digest in files.items()):
        raise ValueError('stage source, input, binary or library changed')
    for side in SIDES:
        if record['builds'][side]['source'] != overall['builds'][side]['source']:
            raise ValueError('stage source differs from measured wheel')
    return record


def validate(args):
    record = verify(args); folder = args.output / 'stages'; results = []
    # Full API and both thread settings must finish before even this untimed kernel gate.
    checks = json.loads((args.output / 'validation-complete.json').read_text())
    if not checks['all_checks_completed_before_any_timing']:
        raise ValueError('full correctness gate incomplete')
    for side in SIDES:
        for family in ('doji', 'mmi'):
            for n in LENGTHS:
                command = [record['builds'][side]['binary'], family, 'validate', str(n), '1', str(folder / 'input.bin')]
                output = subprocess.check_output(command, text=True, stderr=subprocess.STDOUT)
                if not output.startswith('C_VERSION 0.8.1 ') or 'direct_C_and_adapter_exact=true' not in output:
                    raise ValueError('kernel / C / adapter validation incomplete')
                results.append({'side': side, 'family': family, 'n': n, 'command': command, 'output': output})
    (folder / 'validation-complete.json').write_text(json.dumps({'checks': results, 'provenance_sha256': sha256(folder / 'build-provenance.json'),
        'query_validation_sha256': sha256(args.output / 'validation-complete.json')}, indent=2) + '\n')


def measure(args):
    record = verify(args); folder = args.output / 'stages'
    validation = json.loads((folder / 'validation-complete.json').read_text())
    if validation['provenance_sha256'] != sha256(folder / 'build-provenance.json') or validation['query_validation_sha256'] != sha256(args.output / 'validation-complete.json'):
        raise ValueError('stage validation no longer covers these builds')
    deadline = time.monotonic() + 90
    rows = []
    with (folder / 'raw.jsonl').open('w') as log:
        for round_index, sides in enumerate(ORDERS):
            for side in sides:
                binary = record['builds'][side]['binary']
                if sha256(binary) != record['builds'][side]['binary_sha256']:
                    raise ValueError('stage binary changed')
                for family, n, mode in kernel_cases():
                    remaining = deadline - time.monotonic()
                    if remaining <= 0:
                        raise TimeoutError('90second stage budget exceeded; partial data is not a completed comparison')
                    iters = record['iters_by_n'][str(n)]
                    command = [binary, family, mode, str(n), str(iters), str(folder / 'input.bin')]
                    output = subprocess.check_output(command, text=True, stderr=subprocess.STDOUT, timeout=min(10, remaining),
                        env={**os.environ, 'POLARS_MAX_THREADS': '1', 'OMP_NUM_THREADS': '1', 'OPENBLAS_NUM_THREADS': '1', 'MKL_NUM_THREADS': '1'})
                    row = {'side': side, 'round': round_index + 1, 'iters': iters, 'command': command, 'raw_stdout': output,
                           **parse_probe(output, family, mode, n)}
                    rows.append(row); log.write(json.dumps(row) + '\n'); log.flush()
    summaries = {}
    for family, n, mode in kernel_cases():
        key = f'{family}/{mode}/{n}'
        sides = {side: [r for r in rows if (r['side'], r['family'], r['mode'], r['n']) == (side, family, mode, n)] for side in SIDES}
        summaries[key] = {'builds': {}, 'comparisons': {}}
        for side, values in sides.items():
            medians = [row['median_ns'] for row in values]
            counts = {(row['allocations'], row['bytes'], row['holder_bytes']) for row in values}
            if len(medians) != 8 or len(counts) != 1:
                raise ValueError('inconsistent stage repetitions or allocation counts')
            summaries[key]['builds'][side] = {'process_medians_ns': medians, 'median_ns': statistics.median(medians),
                                             'allocations_bytes_holder': list(counts.pop())}
        for before, after in itertools.combinations(SIDES, 2):
            a = summaries[key]['builds'][before]['process_medians_ns']; b = summaries[key]['builds'][after]['process_medians_ns']
            summaries[key]['comparisons'][before + '_vs_' + after] = {'paired_ratios': [x / y for x, y in zip(a, b)],
                'ratio_envelope': [min(a) / max(b), max(a) / min(b)], 'after_faster_rounds': sum(y < x for x, y in zip(a, b))}
    report = {'provenance': record, 'validation': validation, 'rounds': len(ORDERS), 'orders': ORDERS,
              'affinity': sorted(os.sched_getaffinity(0)), 'polars_max_threads': 1,
              'allocation_counter_scope': 'Rust allocation and reallocation request count and cumulative requested bytes for one warmed call; excludes C malloc, deallocations, net/live memory and RSS',
              'query_summary_sha256': sha256(args.output / 'summary.json'),
              'elapsed_seconds': 90 - max(0, deadline - time.monotonic()), 'rows': rows, 'results': summaries,
              'limitations': 'Local stages are nonadditive. Shared AMD runner, placement/frequency and binary-layout effects remain. C kernel is the unchanged control in every binary; compare its shifts too.'}
    (folder / 'summary.json').write_text(json.dumps(report, indent=2) + '\n')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for side in (*SIDES, 'original'):
        parser.add_argument('--' + side + '-python', type=Path, required=True)
        parser.add_argument('--' + side + '-source', type=Path, required=True)
        parser.add_argument('--' + side + '-commit', required=True)
    parser.add_argument('--wheel-dir', type=Path, required=True)
    parser.add_argument('--target-dir', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--build', action='store_true'); mode.add_argument('--validate-only', action='store_true'); mode.add_argument('--measure', action='store_true')
    args = parser.parse_args()
    args.output = args.output.resolve(); args.wheel_dir = args.wheel_dir.resolve(); args.target_dir = args.target_dir.resolve()
    if args.build: build(args)
    elif args.validate_only: validate(args)
    else:
        previous = set(os.sched_getaffinity(0))
        if not previous:
            raise ValueError('no CPU available for stage diagnostics')
        try:
            os.sched_setaffinity(0, [min(previous)])
            measure(args)
        finally:
            os.sched_setaffinity(0, previous)


if __name__ == '__main__':
    main()
