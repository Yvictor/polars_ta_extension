"""Pinned three-arm paired-output experiment; fresh process for every timed case.

Full raw captures must match before any timing. The selected child independently
compares its one raw record to that golden before starting its clock. This is a
Rust adapter/kernel experiment, not a comparison against the old C consumer.
"""
import argparse
from dataclasses import dataclass
import gzip
import hashlib
import itertools
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
import time

PINS = {
    'before': '5bb1c74b25248f37a0764bc6d07dd673b4749cc6',
    'common': '8fa1647ed03f253c0396c2951c6053c9c796c153',
    'paired': 'ad75b44b97566594de7f37dcf28e0ee727e31f6c',
}
SIDES = tuple(PINS)
AFFECTED = ('supertrend', 'accbands', 'kvo', 'wavetrend')
CONTROLS = ('macd_control', 'macdfix_control', 'ema_control', 'sma_control')
FUNCTIONS = AFFECTED + CONTROLS
TIMED_CASES = {f'{f}/default/{n}' for f in AFFECTED for n in (100, 1000, 10000, 1000000)}
TIMED_CASES |= {f'{f}/default/{n}' for f in CONTROLS for n in (512, 10000, 1000000)}
PATTERNS = ('zero', 'negative_zero', 'constant', 'ramp', 'reverse', 'alternating',
            'head_nan', 'interior_nan', 'head_inf', 'interior_negative_inf')
ERRORS = ('invalid_param', 'short_input', 'empty_output', 'short_output',
          'invalid_range', 'start_overflow', 'end_overflow')
INDEX_MAX = 100_000_000
CANARY = 0x7ff80000000055aa
ICANARY = 0x55aa33cc
MAGIC = b'PAIRWIN1'
DEFAULT_LB = dict(zip(FUNCTIONS, (10, 19, 55, 41, 33, 33, 29, 29)))
MINIMUM_LB = dict(zip(FUNCTIONS, (2, 1, 2, 2, 1, 25, 0, 0)))
MAXFIRST_LB = dict(zip(FUNCTIONS, (100000, 99999, 100000, 200021, 100007, 100024, 99999, 99999)))
OUTPUTS = dict(zip(FUNCTIONS, ((1, 1), (3, 0), (2, 0), (2, 0), (3, 0), (3, 0), (1, 0), (1, 0))))
UNSTABLE_FACTOR = dict(zip(FUNCTIONS, (1, 0, 1, 3, 2, 2, 1, 0)))
FLAGS = {'RUSTFLAGS': '', 'CARGO_ENCODED_RUSTFLAGS': '', 'CARGO_PROFILE_RELEASE_LTO': 'thin',
         'CARGO_PROFILE_RELEASE_CODEGEN_UNITS': '1', 'CARGO_PROFILE_RELEASE_DEBUG': 'false'}
CLOSE_SHA = '36641b962b0f7d3ffa860a5dec2d507b4c6f5957275b0fb174cea8e8c32a7851'
BASE_COMMON_FILES = {
    'src/ta_func/ta_SUPERTREND.c', 'ta_codegen/input/supertrend/supertrend.c',
    'ta_codegen/output/csharp/library/src/Core_SUPERTREND.cs',
    'ta_codegen/output/java/fragments/Core_SUPERTREND.java',
    'ta_codegen/output/java/library/src/main/java/io/github/talib/BuildStamp.java',
    'ta_codegen/output/java/library/src/main/java/io/github/talib/Core.java',
    'ta_codegen/output/java/tools/TaCodegenServe.java',
    'ta_codegen/output/rust/library/src/ta_func/supertrend.rs',
}
POLICY_FILES = {'ta_codegen/generator/src/backends/rust_lang.rs',
                'ta_codegen/generator/src/backends/rust_window.rs',
                'ta_codegen/output/rust/library/tests/supertrend_output_windows.rs'}
POLICY_FILES |= {f'ta_codegen/output/rust/library/src/ta_func/{f}.rs' for f in AFFECTED}


@dataclass(frozen=True)
class Spec:
    function: str
    n: int
    start: int = 0
    end: int | None = None
    pattern: str = 'finite'
    param_variant: str = 'default'
    unstable: int = 0
    short_input: bool = False
    error: str | None = None
    capacity_variant: str = 'default'

    def expected(self):
        end = self.n - 1 if self.end is None else self.end
        lb = (MINIMUM_LB if self.param_variant == 'minimum' else
              MAXFIRST_LB if self.param_variant == 'maxfirst' else DEFAULT_LB)[self.function]
        lb += UNSTABLE_FACTOR[self.function] * self.unstable
        first = max(self.start, lb)
        count = max(self.n - first, 0)
        if self.error:
            status = {'invalid_range': 'OutOfRangeEndIndex', 'start_overflow': 'OutOfRangeStartIndex',
                      'end_overflow': 'OutOfRangeEndIndex'}.get(self.error, 'BadParam')
            beg = count = 0
        else:
            status = 'Success'
            beg = first if count else 0
        capacity = {'default': self.n + 7, 'empty': 0, 'short': 1,
                    'minimal': max(self.n - first, 0)}[self.capacity_variant]
        real, integer = OUTPUTS[self.function]
        return {'n': self.n, 'start': self.start, 'end': end, 'status': status,
                'beg': beg, 'count': count, 'real_outputs': real, 'integer_outputs': integer,
                'output_capacity': capacity, 'pattern': self.pattern, 'param_variant': self.param_variant,
                'unstable': self.unstable, 'short_input': self.short_input}


def make_specs():
    specs = {}
    for name in TIMED_CASES:
        function, _, n = name.split('/')
        specs[name] = Spec(function, int(n))
    for function in FUNCTIONS:
        prefix = 'validation/' + function
        for n in (1, 2, 3, 10, 29, 30, 31, 64, 100, 1000):
            specs[f'{prefix}/finite/n{n}/start0'] = Spec(function, n)
        for start in (1, 19, 20, 25, 99, 100, 500, 999):
            specs[f'{prefix}/partial/n1000/start{start}'] = Spec(function, 1000, start)
        for pattern in PATTERNS:
            for start in (0, 25, 500):
                specs[f'{prefix}/{pattern}/n1000/start{start}'] = Spec(function, 1000, start, pattern=pattern)
        for error in ERRORS:
            start, end = (10, 9) if error == 'invalid_range' else (INDEX_MAX + 1, INDEX_MAX + 1) if error == 'start_overflow' else (0, INDEX_MAX + 1) if error == 'end_overflow' else (0, 999)
            capacity = 'empty' if error == 'empty_output' else 'short' if error == 'short_output' else 'default'
            specs[f'{prefix}/error/{error}'] = Spec(function, 1000, start, end,
                short_input=error == 'short_input', error=error, capacity_variant=capacity,
                param_variant='invalid' if error == 'invalid_param' else 'default')
        specs[f'{prefix}/minimal_output'] = Spec(function, 1000, capacity_variant='minimal')
        specs[f'{prefix}/error/empty_output_before_warmup'] = Spec(function, 1, error='empty_output', capacity_variant='empty')
        for variant in ('minimum', 'sentinels', 'maxfirst'):
            specs[f'{prefix}/params/{variant}'] = Spec(function, 250000 if variant == 'maxfirst' else 1000, param_variant=variant)
    for function, counts in [('supertrend', (1, 2, 10, 50)),
                             *((f, (1, 3)) for f in ('kvo', 'wavetrend', 'macd_control', 'macdfix_control', 'ema_control'))]:
        for count in counts:
            specs[f'validation/{function}/unstable/{count}'] = Spec(function, 1000, unstable=count)
    return specs


SPECS = make_specs()
VALIDATION_CASES = set(SPECS) - TIMED_CASES
assert len(TIMED_CASES) == 28 and len(VALIDATION_CASES) == 494


def sha256(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda: f.read(1048576), b''):
            digest.update(block)
    return digest.hexdigest()


def fnv1a64(data):
    value = 0xcbf29ce484222325
    for byte in data:
        value = ((value ^ byte) * 0x100000001b3) & 0xffffffffffffffff
    return f'{value:016x}'


def run_logged(command, log, cwd=None, env=None):
    command = list(map(str, command))
    with Path(log).open('a') as f:
        f.write(json.dumps(command) + '\n'); f.flush()
        subprocess.run(command, cwd=cwd, env=env, stdout=f, stderr=subprocess.STDOUT, check=True)


def git_record(root, expected):
    root = Path(root).resolve()
    commit = subprocess.check_output(['git', '-C', str(root), 'rev-parse', 'HEAD'], text=True).strip()
    if commit != expected or subprocess.check_output(['git', '-C', str(root), 'status', '--porcelain']):
        raise ValueError('source must be clean and match its immutable commit')
    tracked = subprocess.check_output(['git', '-C', str(root), 'ls-files', '-z'], text=True).split('\0')
    files = {}
    for name in tracked:
        if name and (name.startswith(('ta_codegen/output/', 'ta_codegen/generator/', 'ta_codegen/input/', 'src/ta_func/', 'include/'))):
            files[name] = sha256(root / name)
    required = {'ta_codegen/output/rust/Cargo.toml', 'ta_codegen/output/rust/library/Cargo.toml',
                'ta_codegen/generator/src/backends/rust_window.rs', 'ta_codegen/input/supertrend/supertrend.c'}
    if not required <= files.keys():
        raise ValueError('missing compiled upstream source')
    return {'commit': commit, 'clean': True, 'source_files': files,
            'source_sha256': hashlib.sha256(json.dumps(files, sort_keys=True, separators=(',', ':')).encode()).hexdigest()}


def verify_inventory(records):
    maps = {side: records[side]['source_files'] for side in SIDES}
    changed = lambda a, b: {p for p in maps[a].keys() | maps[b].keys() if maps[a].get(p) != maps[b].get(p)}
    if changed('before', 'common') != BASE_COMMON_FILES:
        raise ValueError('common-store-only source inventory differs')
    if changed('common', 'paired') != POLICY_FILES:
        raise ValueError('paired policy source inventory differs')
    for function in ('macd', 'macdfix', 'ema', 'sma'):
        path = f'ta_codegen/output/rust/library/src/ta_func/{function}.rs'
        if len({maps[side][path] for side in SIDES}) != 1:
            raise ValueError('unchanged control source differs')
    return {'before_vs_common': sorted(changed('before', 'common')),
            'common_vs_paired': sorted(changed('common', 'paired')),
            'controls_byte_identical': ['macd', 'macdfix', 'ema', 'sma']}


def runtime_record():
    rust = subprocess.check_output(['rustc', '--version', '--verbose'], text=True)
    if not rust.startswith('rustc 1.97.0 '):
        raise ValueError('Rust 1.97.0 required')
    if sys.platform != 'linux' or not platform.python_version().startswith('3.12.'):
        raise ValueError('Linux and Python 3.12 required for CI measurement')
    if any(os.environ.get(k) != v for k, v in FLAGS.items()):
        raise ValueError('portable thin-LTO/codegen1 flags required identically')
    cpu = next((s.split(':', 1)[1].strip() for s in Path('/proc/cpuinfo').read_text().splitlines() if s.startswith('model name')), 'unknown')
    return {'cpu': cpu, 'platform': platform.platform(), 'python': platform.python_version(), 'rustc': rust,
            'cargo': subprocess.check_output(['cargo', '--version'], text=True),
            'cc': subprocess.check_output(['cc', '--version'], text=True),
            'cmake': subprocess.check_output(['cmake', '--version'], text=True),
            'environment': {k: os.environ.get(k) for k in (*FLAGS, 'RUSTUP_TOOLCHAIN', 'CARGO_BUILD_JOBS')}}


def input_file(output):
    import numpy as np
    if np.__version__ != '2.5.3':
        raise ValueError('NumPy 2.5.3 required for CI-shaped close input')
    values = 100 + np.cumsum(np.random.default_rng(260126).normal(0, .1, 1000000))
    path = output / 'close-seed260126-f64le.bin'; values.astype('<f8').tofile(path)
    digest = sha256(path)
    return {'path': str(path), 'sha256': digest, 'bytes': path.stat().st_size,
            'mac_reference_sha256': CLOSE_SHA, 'matches_mac_reference': digest == CLOSE_SHA,
            'close_fnv1a64': fnv1a64(path.read_bytes()), 'numpy': np.__version__, 'seed': 260126,
            'description': 'CI-shaped close; high=close+1, low=close-1; KVO volume=100+((i*37)%901)'}


def build(args):
    runtime = runtime_record()
    sources = {s: git_record(getattr(args, s + '_source'), PINS[s]) for s in SIDES}
    inventory = verify_inventory(sources)
    inputs = input_file(args.output)
    (args.output / 'input-manifest.json').write_text(json.dumps(inputs, indent=2) + '\n')
    provenance = {'runtime': runtime, 'input': inputs, 'source_inventory': inventory,
                  'harness_sha256': sha256(args.harness), 'controller_sha256': sha256(__file__)}
    env = os.environ.copy(); env['PAIRED_VERSION'] = '0.8.4'
    for side in SIDES:
        root = getattr(args, side + '_source')
        target = args.output / ('target-' + side)
        binary = args.output / 'bin' / side; binary.parent.mkdir(exist_ok=True)
        metadata = json.loads(subprocess.check_output(['cargo', 'metadata', '--locked', '--no-deps', '--format-version=1',
                              '--manifest-path', str(root / 'ta_codegen/output/rust/Cargo.toml')], text=True))
        package = next(p for p in metadata['packages'] if p['name'] == 'ta-lib')
        if package['version'] != '0.8.4' or package['source'] is not None or Path(package['manifest_path']).resolve() != root / 'ta_codegen/output/rust/library/Cargo.toml':
            raise ValueError('upstream package identity differs')
        (args.output / (side + '-cargo-metadata.json')).write_text(json.dumps(metadata, indent=2) + '\n')
        commands = [
            ['cargo', 'build', '--release', '--locked', '-p', 'ta-lib', '--manifest-path', str(root / 'ta_codegen/output/rust/Cargo.toml'), '--target-dir', str(target)],
            ['rustc', '--edition=2021', '-Dwarnings', '--check-cfg=cfg(paired_alloc_probe,test)', '-O', '-C', 'lto=thin', '-C', 'codegen-units=1', str(args.harness),
             '-L', 'dependency=' + str(target / 'release/deps'), '--extern', 'ta_lib=' + str(target / 'release/libta_lib.rlib'), '-o', str(binary)],
        ]
        for command in commands:
            run_logged(command, args.output / (side + '-build.log'), cwd=root, env=env)
        if git_record(root, PINS[side]) != sources[side]:
            raise ValueError('source changed during build')
        diagnostic = args.output / 'bin' / (side + '-allocation')
        diagnostic_command = commands[1][:-2] + ['--cfg', 'paired_alloc_probe', '-o', str(diagnostic)]
        run_logged(diagnostic_command, args.output / (side + '-allocation-build.log'), cwd=root, env=env)
        if side == 'paired':
            diagnostic_test = args.output / 'bin/allocation-cli-tests'
            diagnostic_test_command = commands[1][:-2] + ['--cfg', 'paired_alloc_probe', '--test', '-o', str(diagnostic_test)]
            run_logged(diagnostic_test_command, args.output / 'allocation-cli-tests.log', cwd=root, env=env)
            run_logged([diagnostic_test, '--test-threads=1'], args.output / 'allocation-cli-tests.log', env=env)
            provenance['allocation_cli_tests'] = {'commands': [diagnostic_test_command, [str(diagnostic_test), '--test-threads=1']],
                                                 'binary_sha256': sha256(diagnostic_test)}
        if side == 'paired':
            test_binary = args.output / 'bin/harness-cli-tests'
            test_command = commands[1][:-2] + ['--test', '-o', str(test_binary)]
            run_logged(test_command, args.output / 'harness-cli-tests.log', cwd=root, env=env)
            run_logged([test_binary], args.output / 'harness-cli-tests.log', env=env)
            provenance['cli_tests'] = {'commands': [test_command, [str(test_binary)]], 'binary_sha256': sha256(test_binary)}
        linked_library = target / 'release/libta_lib.rlib'
        archive_dir = args.output / 'libraries'; archive_dir.mkdir(exist_ok=True)
        archived_library = archive_dir / (side + '-libta_lib.rlib'); shutil.copy2(linked_library, archived_library)
        if sha256(linked_library) != sha256(archived_library):
            raise ValueError('linked library archive differs')
        provenance[side] = {'source': sources[side], 'commands': commands, 'binary': str(binary),
                            'binary_sha256': sha256(binary), 'library': str(archived_library),
                            'library_sha256': sha256(archived_library), 'linked_library': str(linked_library),
                            'linked_library_sha256': sha256(linked_library), 'package_version': package['version'],
                            'diagnostic_binary': str(diagnostic), 'diagnostic_binary_sha256': sha256(diagnostic),
                            'diagnostic_command': diagnostic_command, 'primary_allocation_instrumentation': False}
    if sha256(args.harness) != provenance['harness_sha256']:
        raise ValueError('harness changed during build')
    (args.output / 'build-provenance.json').write_text(json.dumps(provenance, indent=2) + '\n')


def strict_json(line):
    def object_pairs(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError('duplicate JSON key')
            result[key] = value
        return result
    def invalid_constant(value):
        raise ValueError('nonfinite JSON constant: ' + value)
    return json.loads(line, object_pairs_hook=object_pairs, parse_constant=invalid_constant)


METADATA_FIELDS = {'kind', 'format', 'mode', 'selected_case', 'cases', 'validation_cases', 'capture_records',
                   'warmups', 'repeats', 'arch', 'os', 'version', 'input_bytes', 'close_fnv1a64',
                   'selected_validated', 'actual_capture_written', 'selected_record_bytes'}
COMMON_FIELDS = {'case', 'n', 'start', 'end', 'status', 'beg', 'count', 'real_outputs', 'integer_outputs',
                 'output_capacity', 'pattern', 'param_variant', 'unstable', 'short_input', 'record_bytes'}


def stable_metadata(metadata):
    # First validate mode-specific values; only these declared mode fields differ.
    ignored = {'mode', 'selected_case', 'capture_records', 'selected_validated', 'selected_record_bytes'}
    return {k: v for k, v in metadata.items() if k not in ignored}


def parse_records(content, mode, selected=None, close_fnv=None, expected_os='linux', expected_arch='x86_64'):
    if mode not in ('capture-full', 'capture-case', 'bench'):
        raise ValueError('unknown capture mode')
    if (mode == 'capture-full') != (selected is None) or selected is not None and selected not in TIMED_CASES:
        raise ValueError('invalid selected case')
    metadata = None; rows = {}
    expected_cases = set(SPECS) if mode == 'capture-full' else {selected}
    for line in content.splitlines():
        if not line.strip():
            continue
        row = strict_json(line)
        if not isinstance(row, dict):
            raise ValueError('JSONL records must be objects')
        if row.get('kind') == 'metadata':
            if metadata is not None or rows or set(row) != METADATA_FIELDS:
                raise ValueError('exactly one initial metadata record required')
            metadata = row
            expected = {'kind': 'metadata', 'format': 1, 'mode': mode, 'selected_case': selected,
                        'cases': len(TIMED_CASES), 'validation_cases': len(VALIDATION_CASES),
                        'capture_records': len(expected_cases), 'warmups': 5, 'repeats': 31,
                        'arch': expected_arch, 'os': expected_os, 'version': '0.8.4', 'input_bytes': 8000000,
                        'selected_validated': mode == 'bench', 'actual_capture_written': True}
            for field, value in expected.items():
                if type(row.get(field)) is not type(value) or row[field] != value:
                    raise ValueError('metadata mismatch: ' + field)
            fnv = row['close_fnv1a64']
            if not isinstance(fnv, str) or len(fnv) != 16 or any(c not in '0123456789abcdef' for c in fnv) or close_fnv is not None and fnv != close_fnv:
                raise ValueError('input fingerprint differs')
            nbytes = row['selected_record_bytes']
            if type(nbytes) is not int or (nbytes != 0 if mode == 'capture-full' else nbytes <= len(MAGIC)):
                raise ValueError('invalid selected record bytes')
            continue
        if metadata is None:
            raise ValueError('metadata must precede all records')
        name = row.get('case')
        if name not in expected_cases or name in rows:
            raise ValueError('unknown, missing-mode or duplicate case')
        fields = COMMON_FIELDS | {'kind'} | ({'iterations', 'warmups', 'samples_ns'} if mode == 'bench' else set())
        if set(row) != fields or row['kind'] != ('case' if mode == 'bench' else 'capture'):
            raise ValueError('unexpected record schema or timing in capture mode')
        for field, value in SPECS[name].expected().items():
            if type(row.get(field)) is not type(value) or row[field] != value:
                raise ValueError(f'{name}: semantic mismatch in {field}: {row.get(field)!r} != {value!r}')
        if type(row['record_bytes']) is not int or row['record_bytes'] <= 8:
            raise ValueError('invalid raw record byte count')
        if mode == 'bench':
            if type(row['iterations']) is not int or row['iterations'] != max(100000 // SPECS[name].n, 1):
                raise ValueError('iteration policy differs')
            if type(row['warmups']) is not int or row['warmups'] != 5:
                raise ValueError('warmups must remain five')
            samples = row['samples_ns']
            if not isinstance(samples, list) or len(samples) != 31 or any(type(x) not in (int, float) or not math.isfinite(x) or x <= 0 for x in samples):
                raise ValueError('31 finite positive samples required')
        rows[name] = row
    if metadata is None or set(rows) != expected_cases:
        raise ValueError('full unique fixed inventory required')
    if selected is not None and metadata['selected_record_bytes'] != rows[selected]['record_bytes'] + len(MAGIC):
        raise ValueError('metadata/record byte count differs')
    return {'metadata': metadata, 'cases': rows}


class Reader:
    def __init__(self, payload):
        self.data = memoryview(payload); self.offset = 0

    def take(self, n):
        if n < 0 or self.offset + n > len(self.data):
            raise ValueError('truncated capture record')
        result = self.data[self.offset:self.offset + n]; self.offset += n
        return result

    def integer(self, code):
        return struct.unpack('<' + code, self.take(struct.calcsize('<' + code)))[0]

    def string(self):
        size = self.integer('I')
        if size > 4096:
            raise ValueError('capture string too long')
        return bytes(self.take(size)).decode('utf8')


def read_capture(path, expected_names=None, golden_dir=None):
    """Validate real bytes, shape, order, ranges and untouched physical guards."""
    expected_names = set(SPECS) if expected_names is None else set(expected_names)
    rows = {}; total_values = 0
    with Path(path).open('rb') as f:
        if f.read(8) != MAGIC:
            raise ValueError('capture magic differs')
        while True:
            offset = f.tell(); length_bytes = f.read(8)
            if not length_bytes:
                break
            if len(length_bytes) != 8:
                raise ValueError('truncated record length')
            size = struct.unpack('<Q', length_bytes)[0]
            if size < 64 or size > 200_000_000:
                raise ValueError('invalid raw record size')
            payload = f.read(size)
            if len(payload) != size:
                raise ValueError('truncated raw record')
            r = Reader(payload); name = r.string(); status = r.string()
            if name not in expected_names or name in rows:
                raise ValueError('duplicate or unknown raw case')
            spec = SPECS[name]; expected = spec.expected()
            fields = dict(zip(('n', 'start', 'end', 'beg', 'count', 'real_outputs', 'integer_outputs'), (r.integer('Q') for _ in range(7))))
            fields['status'] = status
            if any(fields[k] != expected[k] for k in fields):
                raise ValueError('raw shape/status/range differs: ' + name)
            count = fields['count']; field_hashes = []
            for kind, number, unit, code, canary in [('real', fields['real_outputs'], 8, 'Q', CANARY),
                                                      ('integer', fields['integer_outputs'], 4, 'i', ICANARY)]:
                for _ in range(number):
                    length = r.integer('Q')
                    if length != spec.n + 8:
                        raise ValueError('physical output length differs')
                    values = r.take(length * unit); guard = struct.pack('<' + code, canary)
                    if values[:unit] != guard or values[(count + 1) * unit:] != guard * (length - count - 1):
                        raise ValueError('prefix/tail output guard differs: ' + name)
                    if name in TIMED_CASES and kind == 'real':
                        if any(((v[0] >> 52) & 0x7ff) == 0x7ff for v in struct.iter_unpack('<Q', values[unit:(count + 1) * unit])):
                            raise ValueError('timed finite input produced nonfinite output')
                    total_values += length
                    field_hashes.append(hashlib.sha256(values).hexdigest())
            if r.offset != len(payload):
                raise ValueError('unexpected raw payload suffix')
            record = length_bytes + payload
            row = {'offset': offset, 'record_bytes': len(record), 'record_sha256': hashlib.sha256(record).hexdigest(),
                   'field_sha256': field_hashes, **fields}
            if golden_dir is not None and name in TIMED_CASES:
                golden = Path(golden_dir) / (name.replace('/', '-') + '.bin')
                golden.write_bytes(MAGIC + record)
                row['golden_path'] = str(golden); row['golden_sha256'] = sha256(golden)
            rows[name] = row
    if set(rows) != expected_names:
        raise ValueError('raw capture inventory incomplete')
    return {'sha256': sha256(path), 'bytes': Path(path).stat().st_size, 'records': rows,
            'physical_values_checked': total_values, 'all_guards_checked': True}


def validate_capture_pair(paths):
    records = {side: read_capture(paths[side]) for side in SIDES}
    if len({r['sha256'] for r in records.values()}) != 1 or len({r['bytes'] for r in records.values()}) != 1:
        raise ValueError('full primary raw bits/status/range/padding differ before timing')
    return records


def verify_provenance(args):
    provenance = json.loads((args.output / 'build-provenance.json').read_text())
    if runtime_record() != provenance['runtime'] or sha256(__file__) != provenance['controller_sha256'] or sha256(args.harness) != provenance['harness_sha256']:
        raise ValueError('runtime, controller or harness changed after build')
    sources = {s: git_record(getattr(args, s + '_source'), PINS[s]) for s in SIDES}
    verify_inventory(sources)
    for side in SIDES:
        if sources[side] != provenance[side]['source']:
            raise ValueError('source changed after build')
        for kind in ('binary', 'library', 'linked_library', 'diagnostic_binary'):
            if sha256(provenance[side][kind]) != provenance[side][kind + '_sha256']:
                raise ValueError(kind + ' changed after build')
    path = args.output / 'close-seed260126-f64le.bin'
    if str(path) != provenance['input']['path'] or sha256(path) != provenance['input']['sha256'] or path.stat().st_size != 8000000:
        raise ValueError('input changed after build')
    return provenance


def verify_input(record):
    path = Path(record['path'])
    if path.stat().st_size != 8000000 or sha256(path) != record['sha256']:
        raise ValueError('immutable same-runner input changed')
    return record['sha256']


def case_slug(name):
    if name not in TIMED_CASES:
        raise ValueError('unknown timed case')
    return name.replace('/', '-')


def child_run(command, stdout_path, stderr_path, env, ledger, context=None):
    """Persist failed children too; no shell, partial replay or silent retry."""
    command = list(map(str, command))
    entry = {'command': command, 'stdout': str(stdout_path), 'stderr': str(stderr_path),
             'started_utc': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}
    entry.update(context or {})
    ledger.append(entry)
    result = subprocess.run(command, capture_output=True, text=True, env=env)
    Path(stdout_path).write_text(result.stdout); Path(stderr_path).write_text(result.stderr)
    entry['returncode'] = result.returncode
    if result.returncode:
        raise subprocess.CalledProcessError(result.returncode, command, result.stdout, result.stderr)
    return result.stdout


def write_goldens(capture, index, directory):
    directory.mkdir()
    result = {}
    with Path(capture).open('rb') as f:
        for name in sorted(TIMED_CASES):
            record = index['records'][name]
            f.seek(record['offset']); data = f.read(record['record_bytes'])
            if len(data) != record['record_bytes'] or hashlib.sha256(data).hexdigest() != record['record_sha256']:
                raise ValueError('golden source record changed')
            path = directory / (case_slug(name) + '.bin')
            with path.open('xb') as output:
                output.write(MAGIC); output.write(data)
            result[name] = {'path': str(path), 'sha256': sha256(path), 'bytes': path.stat().st_size,
                            'record_sha256': record['record_sha256']}
    return result


ALLOCATION_COUNTERS = ('alloc_requests', 'alloc_requested_bytes', 'realloc_requests', 'realloc_requested_bytes',
                       'dealloc_requests', 'dealloc_requested_bytes')
ALLOCATION_CAVEAT = ('These are requested Rust GlobalAlloc counts/bytes, not live bytes, RSS or C malloc calls. '
                     'Observable diagnostic counters can change optimizer allocation elision; equal counts support '
                     'but do not prove the primary machine code has the same allocation footprint.')


def parse_allocation(content, selected, close_fnv, expected_os='linux', expected_arch='x86_64'):
    lines = [line for line in content.splitlines() if line.strip()]
    if selected not in TIMED_CASES or len(lines) != 1:
        raise ValueError('one selected allocation record required')
    row = strict_json(lines[0])
    fields = {'kind', 'format', 'case', 'n', 'start', 'end', 'status', 'beg', 'count', 'version', 'arch', 'os',
              'input_bytes', 'close_fnv1a64'} | set(ALLOCATION_COUNTERS)
    if not isinstance(row, dict) or set(row) != fields:
        raise ValueError('allocation record schema differs')
    expected = SPECS[selected].expected()
    values = {k: expected[k] for k in ('n', 'start', 'end', 'status', 'beg', 'count')}
    values.update(kind='allocation', format=1, case=selected, version='0.8.4', arch=expected_arch,
                  os=expected_os, input_bytes=8000000, close_fnv1a64=close_fnv)
    if any(type(row[k]) is not type(v) or row[k] != v for k, v in values.items()):
        raise ValueError('allocation metadata/status/range differs')
    if any(type(row[k]) is not int or not 0 <= row[k] <= 0xffffffffffffffff for k in ALLOCATION_COUNTERS):
        raise ValueError('allocation counters must be nonnegative u64 values')
    for prefix in ('alloc', 'realloc', 'dealloc'):
        if row[prefix + '_requests'] == 0 and row[prefix + '_requested_bytes'] != 0:
            raise ValueError('allocation byte count without a request')
    return row


def allocation_audit(args, provenance, env, ledger):
    directory = args.output / 'allocation-audit'; directory.mkdir()
    cases = {}
    for name in sorted(TIMED_CASES):
        cases[name] = {}
        for side in SIDES:
            input_sha = verify_input(provenance['input'])
            command = [provenance[side]['diagnostic_binary'], '--allocation-case', name]
            stem = case_slug(name) + '-' + side
            content = child_run(command, directory / (stem + '.jsonl'), directory / (stem + '.stderr'), env, ledger,
                                {'phase': 'allocation', 'case': name, 'side': side, 'input_sha256': input_sha})
            row = parse_allocation(content, name, provenance['input']['close_fnv1a64'])
            cases[name][side] = row
    equal = {}
    for name, records in cases.items():
        equal[name] = len({tuple(records[side][k] for k in ALLOCATION_COUNTERS) for side in SIDES}) == 1
    report = {'cases': cases, 'all_counter_vectors_equal': all(equal.values()), 'counter_vectors_equal': equal,
              'children': len(cases) * len(SIDES), 'primary_instrumented': False, 'caveat': ALLOCATION_CAVEAT}
    (args.output / 'allocation-audit.json').write_text(json.dumps(report, indent=2) + '\n')
    lines = ['# Untimed allocation diagnostic', '', ALLOCATION_CAVEAT, '',
             '| Case | Before alloc requests/bytes | Common alloc requests/bytes | Paired alloc requests/bytes | All six counters equal |',
             '|---|---:|---:|---:|---:|']
    for name, rows in cases.items():
        cells = [f"{rows[side]['alloc_requests']}/{rows[side]['alloc_requested_bytes']}" for side in SIDES]
        lines.append('| ' + name + ' | ' + ' | '.join(cells) + ' | ' + str(equal[name]) + ' |')
    lines += ['', 'Raw JSON retains separate realloc and dealloc request counts and cumulative requested bytes for every case/arm.']
    (args.output / 'allocation-audit.md').write_text('\n'.join(lines) + '\n')
    return report


def order_for_round(round_index):
    if type(round_index) is not int or not 0 <= round_index < 12:
        raise ValueError('exactly twelve balanced rounds required')
    return tuple(itertools.permutations(SIDES))[round_index % 6]


def measure(args):
    provenance = verify_provenance(args)
    captures_dir = args.output / 'captures'; captures_dir.mkdir()
    runs_dir = args.output / 'runs'; runs_dir.mkdir()
    ledger = []; validations = {}; metadata = None
    runs = {s: {name: [] for name in TIMED_CASES} for s in SIDES}
    affinity = set(os.sched_getaffinity(0)) if hasattr(os, 'sched_getaffinity') else None
    if not affinity:
        raise ValueError('Linux CPU affinity is required for this experiment')
    selected_cpu = min(affinity)
    env = os.environ.copy(); env['PAIRED_CLOSE_BIN'] = provenance['input']['path']
    env['PAIRED_VERSION'] = '0.8.4'
    capture_paths = {s: captures_dir / (s + '.bin') for s in SIDES}
    try:
        os.sched_setaffinity(0, {selected_cpu})
        # All three FULL corpora pass before any selected timed child may start.
        for side in SIDES:
            input_sha = verify_input(provenance['input'])
            command = [provenance[side]['binary'], '--capture-full', capture_paths[side]]
            text = child_run(command, captures_dir / (side + '.jsonl'), captures_dir / (side + '.stderr'), env, ledger, {'phase': 'capture-full', 'side': side, 'input_sha256': input_sha})
            parsed = parse_records(text, 'capture-full', close_fnv=provenance['input']['close_fnv1a64'])
            stable = stable_metadata(parsed['metadata'])
            if metadata is not None and stable != metadata:
                raise ValueError('full-capture runtime metadata differs between arms')
            metadata = stable; validations[side] = parsed
        capture_gate = validate_capture_pair(capture_paths)
        for side in SIDES:
            for name, raw in capture_gate[side]['records'].items():
                if raw['record_bytes'] != validations[side]['cases'][name]['record_bytes']:
                    raise ValueError('JSON/raw record byte count differs')
        (args.output / 'capture-validation.json').write_text(json.dumps(capture_gate, indent=2) + '\n')
        goldens = write_goldens(capture_paths['before'], capture_gate['before'], args.output / 'goldens')
        (args.output / 'goldens.json').write_text(json.dumps(goldens, indent=2) + '\n')
        audit = allocation_audit(args, provenance, env, ledger)
        for round_index in range(12):
            arm_order = order_for_round(round_index)
            names = sorted(TIMED_CASES, reverse=bool(round_index % 2))
            round_dir = runs_dir / f'round-{round_index + 1:02d}'; round_dir.mkdir()
            for name in names:
                golden = goldens[name]
                if sha256(golden['path']) != golden['sha256']:
                    raise ValueError('prevalidated golden changed')
                for position, side in enumerate(arm_order):
                    stem = case_slug(name) + '-' + side
                    actual = round_dir / (stem + '.bin')
                    if actual.exists():
                        raise ValueError('refuse to overwrite a selected child capture')
                    input_sha = verify_input(provenance['input'])
                    command = [provenance[side]['binary'], '--bench', name, golden['path'], actual]
                    text = child_run(command, round_dir / (stem + '.jsonl'), round_dir / (stem + '.stderr'), env, ledger, {'phase': 'bench', 'round': round_index + 1, 'case': name, 'side': side, 'position': position, 'input_sha256': input_sha})
                    parsed = parse_records(text, 'bench', name, provenance['input']['close_fnv1a64'])
                    if stable_metadata(parsed['metadata']) != metadata:
                        raise ValueError('selected child runtime metadata differs')
                    actual_size = actual.stat().st_size; actual_sha = sha256(actual)
                    if actual_size != golden['bytes'] or actual_sha != golden['sha256']:
                        raise ValueError('selected child raw bytes differ from globally validated golden')
                    if parsed['metadata']['selected_record_bytes'] != actual_size:
                        raise ValueError('selected metadata/raw bytes differ')
                    ledger[-1].update(round=round_index + 1, case=name, side=side, position=position,
                                      selected_capture_sha256=actual_sha, selected_capture_bytes=actual_size,
                                      golden_sha256=golden['sha256'], selected_validated_before_clock=True,
                                      identical_capture_deleted=True)
                    runs[side][name].append(parsed['cases'][name])
                    # Preserve golden + validation hash/JSON/command, delete only proven duplicates.
                    actual.unlink()
                    (args.output / 'execution-order.json').write_text(json.dumps(ledger, indent=2) + '\n')
        verify_provenance(args)
        for name, record in goldens.items():
            if sha256(record['path']) != record['sha256']:
                raise ValueError('golden changed during measurement')
        summary = summarize(runs)
        summary['allocation_diagnostic'] = {'audit_sha256': sha256(args.output / 'allocation-audit.json'),
                                             'all_counter_vectors_equal': audit['all_counter_vectors_equal'],
                                             'children': audit['children'], 'caveat': ALLOCATION_CAVEAT}
        summary['provenance'] = {'source_commits': dict(PINS), 'build_provenance_sha256': sha256(args.output / 'build-provenance.json'),
                                 'binary_sha256': {side: provenance[side]['binary_sha256'] for side in SIDES},
                                 'input_sha256': provenance['input']['sha256'], 'runtime': provenance['runtime']}
        summary['protocol'] = {'rounds': 12, 'samples_per_child': 31, 'warmups': 5, 'timed_children': len(TIMED_CASES) * 3 * 12,
                               'fresh_process_per_case': True, 'all_full_capture_gates_before_any_timing': True,
                               'internal_selected_raw_validation_before_clock': True, 'cpu_affinity': [selected_cpu],
                               'arm_orders': [list(order_for_round(i)) for i in range(12)],
                               'capture_sha256': capture_gate['before']['sha256'], 'case_order_alternates': True}
        (args.output / 'summary.json').write_text(json.dumps(summary, indent=2) + '\n')
        write_report(args.output / 'comparison.md', summary)
    finally:
        (args.output / 'execution-order.json').write_text(json.dumps(ledger, indent=2) + '\n')
        os.sched_setaffinity(0, affinity)


def summarize(runs):
    if set(runs) != set(SIDES) or any(set(runs[s]) != TIMED_CASES for s in SIDES):
        raise ValueError('all three arms and fixed cases required')
    cases = {}
    for name in sorted(TIMED_CASES):
        medians = {}
        raw = {}
        for side in SIDES:
            children = runs[side][name]
            if len(children) != 12:
                raise ValueError('exactly twelve matched selected children per arm required')
            values = [r['samples_ns'] for r in children]
            if any(len(samples) != 31 or any(type(x) not in (int, float) or not math.isfinite(x) or x <= 0 for x in samples) for samples in values):
                raise ValueError('raw samples incomplete or invalid')
            raw[side] = values; medians[side] = [statistics.median(samples) for samples in values]
        pairs = {}
        for old, new in (('before', 'common'), ('common', 'paired'), ('before', 'paired')):
            ratios = [a / b for a, b in zip(medians[old], medians[new])]
            envelope = [min(medians[old]) / max(medians[new]), max(medians[old]) / min(medians[new])]
            pairs[old + '_vs_' + new] = {'ratios': ratios, 'median_ratio': statistics.median(ratios),
                'ratio_envelope': envelope, 'new_faster_pairs': sum(x > 1 for x in ratios),
                'new_slower_pairs': sum(x < 1 for x in ratios), 'ranges_disjoint': envelope[0] > 1 or envelope[1] < 1,
                'new_change_percent': (statistics.median(medians[new]) / statistics.median(medians[old]) - 1) * 100}
        cases[name] = {'is_control': name.split('/')[0] in CONTROLS, 'process_medians_ns': medians,
                       'median_ns': {s: statistics.median(v) for s, v in medians.items()},
                       'process_ranges_ns': {s: [min(v), max(v)] for s, v in medians.items()},
                       'raw_samples_ns': raw, 'comparisons': pairs}
    return {'cases': cases, 'warning': 'Process ranges are descriptive envelopes, not confidence intervals. Controls and all negative/noisy cases remain visible. This primary experiment does not establish old-C parity.'}


def write_report(path, summary):
    lines = ['# Paired output windows: same-runner three-arm experiment', '',
             'Full raw bits/status/range/padding captures were exact across all three builds before timing. '
             'Each timed child called only its selected fixture and checked its raw record against that golden before its clock. '
             '12 balanced rounds, 31 samples and 5 warmups per child; one CPU. Portable Rust1.97 thin LTO/codegen1.', '',
             'Source pins: before `' + PINS['before'] + '`, common `' + PINS['common'] + '`, paired `' + PINS['paired'] + '`. Full hashes, commands and environment are archived in build-provenance.json.', '',
             'Ratios are old/new (above1 means the new arm is faster). Envelopes use complete process-median ranges, '
             'not confidence intervals; small or overlapping differences are inconclusive. '
             'Common-vs-paired isolates the cost-policy extension; before-vs-common includes canonical common-store effects. '
             'This is not a comparison to the original C consumer.', '',
             '| Case | Before ms | Common ms | Paired ms | Before/common | Common/paired | Before/paired | Common/paired envelope | Faster pairs |',
             '|---|---:|---:|---:|---:|---:|---:|---:|---:|']
    for name, row in summary['cases'].items():
        pair = row['comparisons']; cp = pair['common_vs_paired']
        label = name + (' (unchanged control)' if row['is_control'] else '')
        lines.append(f"| {label} | {row['median_ns']['before']/1e6:.6f} | {row['median_ns']['common']/1e6:.6f} | {row['median_ns']['paired']/1e6:.6f} | {pair['before_vs_common']['median_ratio']:.5f} | {cp['median_ratio']:.5f} | {pair['before_vs_paired']['median_ratio']:.5f} | {cp['ratio_envelope'][0]:.5f}–{cp['ratio_envelope'][1]:.5f} | {cp['new_faster_pairs']}/12 |")
    lines += ['', summary['warning'], '',
              'The source policy changes four families relative to existing draft#564; MACD/MACDFIX/EMA/SMA source files are byte-identical controls. '
              'Kernel-internal allocation and any residual within-case allocator behavior remain part of the measured operation; '
              'fresh case processes prevent the known sibling-kernel allocator-history coupling. '
              'Native Polars `.over()` and C comparisons require the separate consumer CI evidence.', '',
              '[Untimed allocation audit](allocation-audit.md): ' + ALLOCATION_CAVEAT]
    Path(path).write_text('\n'.join(lines) + '\n')


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    for side in SIDES:
        parser.add_argument('--' + side + '-source', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--harness', type=Path, default=Path(__file__).with_name('bench_paired_windows.rs'))
    parser.add_argument('--build-only', action='store_true')
    args = parser.parse_args(argv)
    for side in SIDES:
        setattr(args, side + '_source', getattr(args, side + '_source').resolve())
    args.output = args.output.resolve(); args.output.mkdir(parents=True, exist_ok=True)
    args.harness = args.harness.resolve()
    if args.build_only:
        build(args)
    else:
        measure(args)


if __name__ == '__main__':
    main()
