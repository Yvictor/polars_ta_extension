"""Bounded same-runner kernel/adapter ablation; no builds during measurement."""
import argparse
import hashlib
import itertools
import json
import math
import os
from pathlib import Path
import re
import resource
import statistics
import shutil
import subprocess
import sys
import time

from integer_init_benchmark import NATIVE_SIDES as SIDES, verify_build
from integer_init_provenance import sha256, source_record, identity, wheel_record, flags_record
ORDERS = (('prior','candidate'),('candidate','prior')) * 6

LENGTHS = (1000, 10000, 1000000)
MODES = ('newcall','setup','kernel','ffi','full','materialize_zero','materialize_eager','init_zero_int','init_eager_int','init_zero_int_touch','init_eager_int_touch','init_nan_real')
HERE = Path(__file__).resolve().parent
PROBE = HERE / 'integer_init_stage_probe.rs'
PATTERN = re.compile(r'PROBE (doji|mmi)/(\w+)/(\d+) allocations=(\d+) bytes=(\d+) zeroed_requests=(\d+) realloc_requests=(\d+) holder_bytes=(\d+) ns=(\[[^\n]+\])')


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
    samples = json.loads(found[9])
    if len(samples) != 7 or any(isinstance(x, bool) or not isinstance(x, (int, float)) or not math.isfinite(x) or x <= 0 for x in samples):
        raise ValueError('invalid stage samples')
    return {'family': family, 'mode': mode, 'n': length, 'allocations': int(found[4]),
            'bytes': int(found[5]), 'zeroed_requests':int(found[6]), 'realloc_requests':int(found[7]), 'holder_bytes': int(found[8]), 'samples_ns': samples,
            'median_ns': statistics.median(samples), 'c_version': lines[0].removeprefix('C_VERSION ')}


def kernel_cases():
    return [(family, n, mode) for family in ('doji', 'mmi') for n in LENGTHS
            for mode in MODES]


def fingerprint_value(raw):
    if not re.fullmatch('[0-9a-f]{16}', raw):
        raise ValueError('invalid Cargo fingerprint')
    return int.from_bytes(bytes.fromhex(raw), 'little')


def cargo_inventory(target, expected_rustflags=()):
    root = target / 'release/.fingerprint'
    names = ('ta_lib', 'polars', 'serde', 'jemallocator')
    parents = []
    for pattern in ('*/lib-_polars_talib.json', '*/test-lib-_polars_talib.json'):
        for path in sorted(root.glob(pattern)):
            data = json.loads(path.read_text())
            deps = {entry[1]: entry[3] for entry in data['deps']}
            raw = path.with_suffix('')
            reasons = []
            if path.name.startswith('test-'): reasons.append('test artifact, not product cdylib')
            if not path.parent.name.startswith('polars_talib-'): reasons.append('different package')
            if not set(names) <= deps.keys(): reasons.append('missing native direct dependencies: ' + repr(sorted(set(names) - deps.keys())))
            if data['rustflags'] != list(expected_rustflags): reasons.append('rustflags differ: ' + repr(data['rustflags']))
            parents.append({'path': str(path), 'metadata': data, 'raw_fingerprint': raw.read_text().strip() if raw.exists() else None,
                            'selected': not reasons, 'filter_reasons': reasons})
    dependencies = []
    for name in names:
        for path in sorted(root.glob('*/lib-' + name + '.json')):
            raw = path.with_suffix('')
            dependencies.append({'name': name, 'path': str(path), 'metadata': json.loads(path.read_text()),
                                 'raw_fingerprint': raw.read_text().strip() if raw.exists() else None})
    return {'parents': parents, 'dependencies': dependencies, 'expected_rustflags': list(expected_rustflags)}


def native_dependency_records(target, expected_rustflags=(), inventory_path=None):
    """Select the current product graph immediately after its wheel build."""
    root = target / 'release/.fingerprint'
    names = ('ta_lib', 'polars', 'serde', 'jemallocator')
    inventory = cargo_inventory(target, expected_rustflags)
    if inventory_path is not None:
        inventory_path.write_text(json.dumps(inventory, indent=2) + '\n')
    parents = [(Path(row['path']), {name: {entry[1]: entry[3] for entry in row['metadata']['deps']}[name] for name in names})
               for row in inventory['parents'] if row['selected']]
    if not parents:
        raise ValueError('zero native product parents; unfiltered candidates=' + str(len(inventory['parents'])) + '; inventory=' + str(inventory_path))
    if any(deps != parents[0][1] for _, deps in parents):
        raise ValueError('native product parents disagree: ' + repr([(str(path), deps) for path, deps in parents]) + '; inventory=' + str(inventory_path))
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
            raise ValueError('native dependency fingerprint does not select exactly one artifact: ' + name + '; expected=' + str(expected) + '; matches=' + repr(matches))
        artifact, fingerprint, metadata = matches[0]
        resolved[name] = artifact
        evidence[str(fingerprint)] = sha256(fingerprint); evidence[str(metadata)] = sha256(metadata)
    return resolved, evidence


def snapshot(args):
    folder = args.output / 'linkage' / args.snapshot_side; folder.mkdir(parents=True, exist_ok=True)
    inventory_path = folder / 'unfiltered-cargo-inventory.json'
    dependencies, files = native_dependency_records(args.target_dir, inventory_path=inventory_path)
    copies = {}
    for original, digest in files.items():
        source = Path(original)
        destination = folder / 'cargo-fingerprints' / source.parent.name / source.name
        destination.parent.mkdir(parents=True, exist_ok=True); shutil.copyfile(source, destination)
        if sha256(destination) != digest: raise ValueError('fingerprint snapshot copy changed')
        copies[str(destination)] = digest
    installed = identity(args.python)
    retained={}
    for source in [*dependencies.values(),*(Path(p) for p in installed['native_files'])]:
        destination=folder/'product-artifacts'/source.name
        destination.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,destination)
        digest=sha256(source)
        if sha256(destination)!=digest: raise ValueError('actual product artifact copy changed')
        retained[str(destination)]=digest
    record = {'side': args.snapshot_side, 'source': source_record(args.source, args.commit),
              'identity': installed, 'wheel': wheel_record(args.wheel_dir / args.snapshot_side, installed),
              'flags': flags_record(), 'dependencies': {name: {'path': str(path), 'sha256': sha256(path)} for name, path in dependencies.items()},
              'fingerprint_files': copies,'retained_product_artifacts':retained, 'inventory_path': str(inventory_path), 'inventory_sha256': sha256(inventory_path)}
    (folder / 'product-linkage.json').write_text(json.dumps(record, indent=2) + '\n')


def product_dependency_records(args, provenance):
    """Use retained wheel-time graphs even after Cargo has replaced current parent metadata."""
    dependencies = None; hashes = None; evidence = {}
    for side in SIDES:
        path = args.output / 'linkage' / side / 'product-linkage.json'
        record = json.loads(path.read_text())
        build = provenance['builds'][side]
        if (record['side'] != side or record['source'] != build['source'] or record['identity'] != build['identity']
                or record['wheel'] != build['wheel'] or record['flags'] != provenance['flags']):
            raise ValueError('product linkage snapshot does not cover measured wheel: ' + side)
        files = {**record['fingerprint_files'],**record['retained_product_artifacts'], record['inventory_path']: record['inventory_sha256']}
        if any(sha256(name) != digest for name, digest in files.items()):
            raise ValueError('product fingerprint snapshot changed: ' + side)
        actual = {name: entry['sha256'] for name, entry in record['dependencies'].items()}
        paths = {name: Path(entry['path']) for name, entry in record['dependencies'].items()}
        if set(actual) != {'ta_lib', 'polars', 'serde', 'jemallocator'}:
            raise ValueError('product direct dependency inventory changed')
        if any(sha256(paths[name]) != digest for name, digest in actual.items()):
            raise ValueError('product rlib changed: ' + side)
        if dependencies is not None and (paths != dependencies or actual != hashes):
            raise ValueError('native product wheel dependency graphs disagree')
        dependencies = paths; hashes = actual
        evidence.update(files); evidence[str(path)] = sha256(path)
    return dependencies, evidence


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
    (folder / 'post-contract-cargo-inventory.json').write_text(json.dumps(cargo_inventory(args.target_dir), indent=2) + '\n')
    dependencies, dependency_fingerprints = product_dependency_records(args, provenance)
    command = [str(args.prior_python.absolute()), '-c',
               'import sys;sys.path.insert(0,sys.argv[1]);from integer_init_query import frame;frame(1000000,1000)["close"].to_numpy().astype("<f8").tofile(sys.argv[2])',
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
              'limitation': 'full means native::compute with predecoded Params, not Python/plugin deserialization; initialization controls have different element widths; counting wrapper adds a disabled atomic check around allocation calls during timings and can inhibit calloc folding; use the archived uninstrumented product binaries to establish the actual route'}
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
                    before_faults=resource.getrusage(resource.RUSAGE_CHILDREN)
                    output = subprocess.check_output(command, text=True, stderr=subprocess.STDOUT, timeout=min(10, remaining),
                        env={**os.environ, 'POLARS_MAX_THREADS': '1', 'OMP_NUM_THREADS': '1', 'OPENBLAS_NUM_THREADS': '1', 'MKL_NUM_THREADS': '1'})
                    after_faults=resource.getrusage(resource.RUSAGE_CHILDREN)
                    row = {'child_minor_faults':after_faults.ru_minflt-before_faults.ru_minflt,
                           'child_major_faults':after_faults.ru_majflt-before_faults.ru_majflt, 'side': side, 'round': round_index + 1, 'iters': iters, 'command': command, 'raw_stdout': output,
                           **parse_probe(output, family, mode, n)}
                    rows.append(row); log.write(json.dumps(row) + '\n'); log.flush()
    summaries = {}
    for family, n, mode in kernel_cases():
        key = f'{family}/{mode}/{n}'
        sides = {side: [r for r in rows if (r['side'], r['family'], r['mode'], r['n']) == (side, family, mode, n)] for side in SIDES}
        summaries[key] = {'builds': {}, 'comparisons': {}}
        for side, values in sides.items():
            medians = [row['median_ns'] for row in values]
            counts = {(row['allocations'], row['bytes'], row['zeroed_requests'], row['realloc_requests'], row['holder_bytes']) for row in values}
            if len(medians) != 12 or len(counts) != 1:
                raise ValueError('inconsistent stage repetitions or allocation counts')
            summaries[key]['builds'][side] = {'process_medians_ns': medians, 'median_ns': statistics.median(medians),
                                             'allocations_bytes_zeroed_realloc_holder': list(counts.pop())}
        for before, after in itertools.combinations(SIDES, 2):
            a = summaries[key]['builds'][before]['process_medians_ns']; b = summaries[key]['builds'][after]['process_medians_ns']
            summaries[key]['comparisons'][before + '_vs_' + after] = {'paired_ratios': [x / y for x, y in zip(a, b)],
                'ratio_envelope': [min(a) / max(b), max(a) / min(b)], 'after_faster_rounds': sum(y < x for x, y in zip(a, b))}
    report = {'provenance': record, 'validation': validation, 'rounds': len(ORDERS), 'orders': ORDERS,
              'affinity': sorted(os.sched_getaffinity(0)), 'polars_max_threads': 1,
              'allocation_counter_scope': 'Rust allocation and reallocation request count and cumulative requested bytes for one warmed call; excludes C malloc, deallocations, net/live memory and RSS',
              'query_summary_sha256': sha256(args.output / 'summary.json'),
              'fault_counter_scope':'RUSAGE_CHILDREN deltas for the whole child including startup, fixtures, validation, warmups, timing and count call; not allocator-only first-touch proof',
              'elapsed_seconds': 90 - max(0, deadline - time.monotonic()), 'rows': rows, 'results': summaries,
              'limitations': 'Local stages are nonadditive. Shared AMD runner, placement/frequency and binary-layout effects remain. C kernel is the unchanged control in every binary; compare its shifts too.'}
    (folder / 'summary.json').write_text(json.dumps(report, indent=2) + '\n')


def main():
    if '--snapshot-side' in sys.argv:
        parser = argparse.ArgumentParser(description='Snapshot the exact product dependency graph immediately after a native wheel build')
        parser.add_argument('--snapshot-side', choices=SIDES, required=True)
        for name in ('source', 'python', 'wheel-dir', 'target-dir', 'output'):
            parser.add_argument('--' + name, type=Path, required=True)
        parser.add_argument('--commit', required=True)
        args = parser.parse_args()
        for name in ('source', 'wheel_dir', 'target_dir', 'output'):
            setattr(args, name, getattr(args, name).resolve())
        snapshot(args)
        return
    parser = argparse.ArgumentParser(description=__doc__)
    for side in ('original','prior','candidate'):
        parser.add_argument('--' + side + '-python', type=Path, required=True)
        parser.add_argument('--' + side + '-source', type=Path, required=True)
    parser.add_argument('--candidate-commit', required=True)
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
