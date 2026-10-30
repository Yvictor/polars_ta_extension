"""Same-runner EMA/MACD loop A/B with exact pre-timing captures.

Build first with --build-only, then measure without other builds or CPU jobs.
Process envelopes are descriptive ranges, not confidence intervals.
"""
import argparse
import gzip
import hashlib
import json
import math
import os
from pathlib import Path
import platform
import statistics
import subprocess
import sys
import time

SIDES = ('baseline', 'candidate')
SIZES = (20, 100, 512, 10_000, 1_000_000)
MODES = ('EMA', 'MACD', 'MACDFIX', 'ATR_control', 'SMA_control')
EXPECTED_CASES = {f'{mode}/{n}' for n in SIZES for mode in MODES
                  if not (n == 20 and mode.startswith('MACD'))}
PARITY_CASES = 8512
PARITY_VALUES = 2278720


def sha256(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as source:
        for block in iter(lambda: source.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def source_record(root):
    root = Path(root).resolve()
    paths = set()
    for directory in ('ta_codegen/output/rust', 'ta_codegen/generator/src'):
        for path in (root / directory).rglob('*'):
            relative = path.relative_to(root)
            if path.is_file() and not {'target', '.git'}.intersection(relative.parts):
                if path.suffix in ('.rs', '.toml', '.lock') or path.name == 'build.rs':
                    paths.add(relative.as_posix())
    for function in ('ema', 'macd', 'macdfix'):
        for path in (root / 'ta_codegen/input' / function).rglob('*'):
            if path.is_file() and path.suffix in ('.c', '.h', '.yaml', '.yml', '.md'):
                paths.add(path.relative_to(root).as_posix())
    for name in ('ta_codegen/generator/Cargo.toml', 'ta_codegen/generator/Cargo.lock'):
        if (root / name).is_file():
            paths.add(name)
    required = {'ta_codegen/output/rust/Cargo.toml',
                'ta_codegen/input/ema/ema.c',
                'ta_codegen/generator/src/backends/rust_window.rs'}
    if not required <= paths:
        raise ValueError('missing relevant upstream sources')
    files = {name: sha256(root / name) for name in sorted(paths)}
    digest = hashlib.sha256(json.dumps(files, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
    return {'commit': subprocess.check_output(['git', '-C', str(root), 'rev-parse', 'HEAD'], text=True).strip(),
            'source_sha256': digest, 'source_files': files,
            'dirty': bool(subprocess.check_output(['git', '-C', str(root), 'status', '--porcelain']))}


def parse_records(content, repeats, capture_only):
    metadata = parity = None
    cases = {}
    for line in content.splitlines():
        if not line.strip():
            continue
        entry = json.loads(line)
        if not isinstance(entry, dict):
            raise ValueError('JSONL records must be objects')
        kind = entry.get('kind')
        if kind == 'metadata':
            if metadata is not None:
                raise ValueError('duplicate metadata')
            metadata = entry
        elif kind == 'parity':
            if parity is not None:
                raise ValueError('duplicate parity')
            parity = entry
        elif kind is None and 'case' in entry:
            name = entry['case']
            if name in cases:
                raise ValueError('duplicate timed case')
            cases[name] = entry
        else:
            raise ValueError('unknown record kind')
    if metadata is None or parity is None:
        raise ValueError('metadata and parity records are required')
    if metadata.get('repeats') != repeats or metadata.get('capture_only') is not capture_only:
        raise ValueError('harness did not honor requested repeats/capture mode')
    if not metadata.get('arch') or not metadata.get('os'):
        raise ValueError('missing harness platform')
    if parity.get('cases') != PARITY_CASES or parity.get('written_values') != PARITY_VALUES:
        raise ValueError('parity corpus must contain 8512 cases and 2278720 written values')
    if set(cases) != (set() if capture_only else EXPECTED_CASES):
        raise ValueError('timed inventory must contain exactly all 23 requested cases')
    for name, entry in cases.items():
        n = int(name.rsplit('/', 1)[1])
        if entry.get('iterations') != max(2_000_000 // n, 3):
            raise ValueError('unexpected iterations')
        samples = entry.get('samples_ns')
        if not isinstance(samples, list) or len(samples) != repeats:
            raise ValueError('invalid sample count')
        if any(isinstance(x, bool) or not isinstance(x, (float, int)) or not math.isfinite(x) or x <= 0 for x in samples):
            raise ValueError('samples must be finite and positive')
    return {'metadata': metadata, 'parity': parity, 'cases': cases}


def validate_capture_pair(paths):
    sizes = {side: Path(paths[side]).stat().st_size for side in SIDES}
    hashes = {side: sha256(paths[side]) for side in SIDES}
    if not sizes['baseline'] or sizes['baseline'] != sizes['candidate'] or hashes['baseline'] != hashes['candidate']:
        raise ValueError('full output/range/padding capture differs or is empty before timing')
    return {'sha256': hashes, 'bytes': sizes}


def cpu_name():
    path = Path('/proc/cpuinfo')
    if path.exists():
        return next((line.split(':', 1)[1].strip() for line in path.read_text().splitlines()
                     if line.startswith('model name')), platform.processor())
    if sys.platform == 'darwin':
        return subprocess.check_output(['sysctl', '-n', 'machdep.cpu.brand_string'], text=True).strip()
    return platform.processor()


def runtime_record():
    return {'cpu': cpu_name(), 'platform': platform.platform(), 'python': platform.python_version(),
            'rustc': subprocess.check_output(['rustc', '--version', '--verbose'], text=True),
            'cc': subprocess.check_output(['cc', '--version'], text=True),
            'build_environment': {key: os.environ.get(key) for key in
                ('RUSTUP_TOOLCHAIN', 'RUSTFLAGS', 'CARGO_ENCODED_RUSTFLAGS', 'CARGO_PROFILE_RELEASE_DEBUG',
                 'CARGO_PROFILE_RELEASE_LTO', 'CARGO_PROFILE_RELEASE_CODEGEN_UNITS', 'CARGO_BUILD_JOBS')}}


def verify_sources(args, provenance=None):
    records = {}
    for side in SIDES:
        record = source_record(getattr(args, side + '_source'))
        expected = getattr(args, 'expected_' + side + '_commit')
        if expected is not None and record['commit'] != expected:
            raise ValueError(f'{side} source commit is not the requested pin')
        if record['dirty']:
            raise ValueError(f'{side} upstream source must be clean')
        if provenance is not None and record != provenance[side]['source']:
            raise ValueError(f'{side} source changed after build')
        records[side] = record
    return records


def build_binaries(args):
    sources = verify_sources(args)
    records = {'runtime': runtime_record(), 'harness': {'path': str(args.harness.resolve()),
                'sha256': sha256(args.harness)}}
    for side in SIDES:
        root = getattr(args, side + '_source').resolve()
        target = (args.output / ('target-' + side)).resolve()
        binary = getattr(args, side).absolute()
        binary.parent.mkdir(parents=True, exist_ok=True)
        commands = [
            ['cargo', 'build', '--release', '--locked', '-p', 'ta-lib', '--manifest-path',
             str(root / 'ta_codegen/output/rust/Cargo.toml'), '--target-dir', str(target)],
            ['rustc', '--edition=2021', '-O', '-C', 'lto=thin', '-C', 'codegen-units=1',
             str(args.harness.resolve()), '-L', 'dependency=' + str(target / 'release/deps'),
             '--extern', 'ta_lib=' + str(target / 'release/libta_lib.rlib'), '-o', str(binary)],
        ]
        with (args.output / (side + '-build.log')).open('w') as log:
            for command in commands:
                log.write(json.dumps(command) + '\n'); log.flush()
                subprocess.run(command, check=True, stdout=log, stderr=subprocess.STDOUT, cwd=root)
        if source_record(root) != sources[side] or sha256(args.harness) != records['harness']['sha256']:
            raise ValueError('source or harness changed during build')
        records[side] = {'source': sources[side], 'commands': commands,
                         'binary_sha256': sha256(binary),
                         'library_sha256': sha256(target / 'release/libta_lib.rlib')}
    (args.output / 'build-provenance.json').write_text(json.dumps(records, indent=2) + '\n')


def summarize(runs):
    if any(len(runs[side]) < 12 for side in SIDES) or len(runs['baseline']) != len(runs['candidate']):
        raise ValueError('at least 12 matched process pairs required')
    rows = {}
    for name in sorted(EXPECTED_CASES):
        old = [statistics.median(r['cases'][name]['samples_ns']) for r in runs['baseline']]
        new = [statistics.median(r['cases'][name]['samples_ns']) for r in runs['candidate']]
        ratios = [a / b for a, b in zip(old, new)]
        envelope = [min(old) / max(new), max(old) / min(new)]
        rows[name] = {'baseline_process_medians_ns': old, 'candidate_process_medians_ns': new,
                      'baseline_median_ns': statistics.median(old), 'candidate_median_ns': statistics.median(new),
                      'paired_ratios': ratios, 'median_paired_ratio': statistics.median(ratios),
                      'ratio_envelope': envelope, 'candidate_faster_pairs': sum(x > 1 for x in ratios),
                      'is_control': name.startswith(('ATR_control/', 'SMA_control/'))}
    return rows


def measure(args):
    provenance = json.loads((args.output / 'build-provenance.json').read_text())
    verify_sources(args, provenance)
    if runtime_record() != provenance['runtime']:
        raise ValueError('runtime/toolchain/build environment changed after build')
    if sha256(args.harness) != provenance['harness']['sha256']:
        raise ValueError('harness changed after build')
    for side in SIDES:
        if sha256(getattr(args, side)) != provenance[side]['binary_sha256']:
            raise ValueError('binary changed after build')
    original_affinity = set(os.sched_getaffinity(0)) if hasattr(os, 'sched_getaffinity') else None
    selected_affinity = sorted(original_affinity)[:1] if original_affinity else None
    runs = {side: [] for side in SIDES}; order = []; captures = {}; validations = {}; metadata = None
    try:
        if selected_affinity:
            os.sched_setaffinity(0, selected_affinity)
        for side in SIDES:
            capture = args.output / (side + '.bin'); captures[side] = capture
            command = [str(getattr(args, side).absolute()), str(args.repeats), str(capture.resolve()), '--capture-only']
            result = subprocess.run(command, check=True, capture_output=True, text=True)
            (args.output / (side + '-validation.jsonl')).write_text(result.stdout)
            validations[side] = parse_records(result.stdout, args.repeats, True)
            current = {k: v for k, v in validations[side]['metadata'].items() if k != 'capture_only'}
            if metadata is not None and current != metadata:
                raise ValueError('harness runtime differs between builds')
            metadata = current
        capture_gate = validate_capture_pair(captures)
        (args.output / 'capture-validation.json').write_text(json.dumps(
            {**capture_gate, 'records': validations, 'commands_completed_before_timing': True}, indent=2) + '\n')
        for pair in range(args.pairs):
            for side in (SIDES if pair % 2 == 0 else tuple(reversed(SIDES))):
                label = f'{side}-{pair + 1}'; order.append(label)
                print(time.strftime('%H:%M:%S'), label, flush=True)
                command = [str(getattr(args, side).absolute()), str(args.repeats)]
                result = subprocess.run(command, check=True, capture_output=True, text=True)
                (args.output / (label + '.jsonl')).write_text(result.stdout)
                data = parse_records(result.stdout, args.repeats, False)
                current = {k: v for k, v in data['metadata'].items() if k != 'capture_only'}
                if current != metadata:
                    raise ValueError('timed harness metadata changed')
                runs[side].append(data)
        verify_sources(args, provenance)
        for side in SIDES:
            if sha256(getattr(args, side)) != provenance[side]['binary_sha256']:
                raise ValueError('binary changed during measurements')
        if sha256(args.harness) != provenance['harness']['sha256']:
            raise ValueError('harness changed during measurements')
    finally:
        if original_affinity is not None:
            os.sched_setaffinity(0, original_affinity)
    rows = summarize(runs)
    report = {'run_url': f"{os.environ.get('GITHUB_SERVER_URL', 'https://github.com')}/{os.environ.get('GITHUB_REPOSITORY', 'local')}/actions/runs/{os.environ.get('GITHUB_RUN_ID', 'local')}",
              'runtime': provenance['runtime'], 'build_provenance': provenance,
              'runner_image': os.environ.get('ImageOS'), 'runner_image_version': os.environ.get('ImageVersion'),
              'pairs': args.pairs, 'samples_per_process': args.repeats, 'warmups': 5,
              'affinity': selected_affinity, 'order': order, 'harness_metadata': metadata,
              'parity': validations['candidate']['parity'], 'capture_validation': capture_gate, 'results': rows}
    (args.output / 'summary.json').write_text(json.dumps(report, indent=2) + '\n')
    for capture in captures.values():
        with capture.open('rb') as source, gzip.open(str(capture) + '.gz', 'wb') as dest:
            for block in iter(lambda: source.read(1024 * 1024), b''):
                dest.write(block)
        capture.unlink()
    lines = ['# Upstream EMA/MACD/MACDFIX loop comparison', '',
             f'{args.pairs} alternating fresh-process pairs; {args.repeats} samples/process; one-CPU affinity {selected_affinity}.',
             'Full output/range/padding captures are byte-identical and nonempty before timing. Parity: 8512 cases, 2278720 written values.',
             'Ratios are baseline/candidate paired process medians; envelopes are descriptive process ranges, not confidence intervals.',
             'ATR and SMA controls are unchanged. Shared-host dependence, frequency and placement remain limitations; these results do not establish universal speedups or formal significance.', '',
             '| Case | Baseline ns | Candidate ns | Paired ratio | Envelope | Faster pairs |',
             '| --- | ---: | ---: | ---: | --- | ---: |']
    for name, row in rows.items():
        lo, hi = row['ratio_envelope']
        lines.append(f"| {name} | {row['baseline_median_ns']:.1f} | {row['candidate_median_ns']:.1f} | {row['median_paired_ratio']:.3f} | {lo:.3f}–{hi:.3f} | {row['candidate_faster_pairs']}/{args.pairs} |")
    (args.output / 'comparison.md').write_text('\n'.join(lines) + '\n')
    print('\n'.join(lines), flush=True)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    for side in SIDES:
        parser.add_argument('--' + side, type=Path)
        parser.add_argument('--' + side + '-source', type=Path, required=True)
        parser.add_argument('--expected-' + side + '-commit')
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--harness', type=Path)
    parser.add_argument('--build-only', action='store_true')
    parser.add_argument('--pairs', type=int, default=12)
    parser.add_argument('--repeats', type=int, default=31)
    args = parser.parse_args(argv)
    if args.pairs < 12 or args.pairs % 2 or args.repeats < 5:
        parser.error('even >=12 pairs and >=5 samples required')
    args.output = args.output.resolve(); args.output.mkdir(parents=True, exist_ok=True)
    if args.harness is None:
        args.harness = args.candidate_source / 'scripts/bench_ema_windows.rs'
    for side in SIDES:
        if getattr(args, side) is None:
            setattr(args, side, args.output / 'bin' / side)
    if args.build_only:
        build_binaries(args)
    else:
        measure(args)


if __name__ == '__main__':
    main()
