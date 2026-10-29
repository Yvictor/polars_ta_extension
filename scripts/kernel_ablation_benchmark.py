"""Four native builds: exact and original C validation, then balanced ablations.

All effects describe these queries on one shared runner. Inner timing samples
are correlated; process envelopes are descriptive ranges, not confidence limits.
"""
import argparse
from collections import Counter
import hashlib
import itertools
import json
import math
import os
from pathlib import Path
import platform
import re
import statistics
import subprocess
import time
import zipfile

SIDES = ('base', 'utils', 'mmi', 'composed')
ORDERS = (('base', 'utils', 'composed', 'mmi'),
          ('utils', 'mmi', 'base', 'composed'),
          ('mmi', 'composed', 'utils', 'base'),
          ('composed', 'base', 'mmi', 'utils')) * 2
CASES = tuple(sorted((
    'cdldoji/1000000', 'grouped_cdldoji/100x10000',
    'minmaxindex/1000000', 'grouped_minmaxindex/100x10000',
    'grouped_minmaxindex/10000x100', 'grouped_minmaxindex/2000x100_interleaved',
    'stddev/1000000', 'grouped_stddev/100x10000',
    'grouped_ema/10000x100', 'grouped_add/10000x100',
    'control_cumsum/100x10000', 'control_cumsum/10000x100',
)))
CHECKED_VALUES = 14_400_000
RUNTIME_KEYS = ('python', 'polars', 'numpy', 'package', 'talib', 'platform')
RUN_KEYS = ('cpu', 'platform', 'python', 'polars', 'numpy', 'rust', 'profile',
            'threads', 'affinity', 'repeats', 'warmups', 'diagnostic',
            'checked_values', 'case_filters', 'exact_reference')
SCRIPT = Path(__file__).with_name('migration_benchmark.py').resolve()
PROBE = Path(__file__).with_name('migration_probe.py').resolve()
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


def validate_identities(identities):
    if set(identities) != set(SIDES):
        raise ValueError('exactly four named native builds required')
    normalized = [{key: row[key] for key in RUNTIME_KEYS} for row in identities.values()]
    if any(row != normalized[0] for row in normalized):
        raise ValueError('four installed runtimes must match')
    first = normalized[0]
    if not first['python'].startswith('3.12.') or first['polars'] != '1.44.2' or first['numpy'] != '2.5.3':
        raise ValueError('unexpected Python/Polars/NumPy version')
    if first['package'] != '0.2.1' or not first['talib'].startswith('0.8.3 (native Rust;'):
        raise ValueError('all four builds must be native Rust, not original C')
    return first


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
    return {'rustc': rustc, 'cargo': subprocess.check_output(['cargo', '--version'], text=True),
            'cc': subprocess.check_output(['cc', '--version'], text=True),
            'environment': {key: os.environ.get(key) for key in
                ('RUSTUP_TOOLCHAIN', 'RUSTFLAGS', 'CARGO_ENCODED_RUSTFLAGS',
                 'CARGO_PROFILE_RELEASE_DEBUG', 'CARGO_PROFILE_RELEASE_LTO',
                 'CARGO_PROFILE_RELEASE_CODEGEN_UNITS', 'CARGO_BUILD_JOBS', 'CARGO_TARGET_DIR')}}


def reference_build(args, runtime, expected=None):
    row = identity(args.original_python)
    for key in RUNTIME_KEYS:
        if key != 'talib' and row[key] != runtime[key]:
            raise ValueError('original reference runtime differs: ' + key)
    if not row['talib'].startswith('0.8.1 '):
        raise ValueError('original reference must be C0.8.1')
    build = {'source': source_record(args.original_source, args.original_commit),
             'identity': row, 'wheel': wheel_record(args.wheel_dir / 'original', row)}
    if expected is not None and expected != build:
        raise ValueError('original reference build changed')
    return build


def record_build(args):
    identities = {side: identity(getattr(args, side + '_python')) for side in SIDES}
    runtime = validate_identities(identities)
    builds = {side: {'source': source_record(getattr(args, side + '_source'), getattr(args, side + '_commit')),
                     'identity': identities[side],
                     'wheel': wheel_record(args.wheel_dir / side, identities[side])} for side in SIDES}
    result = {'builds': builds, 'runtime': runtime, 'flags': flags_record(),
              'scripts': {p.name: sha256(p) for p in (Path(__file__), SCRIPT, PROBE)},
              'reference_build': reference_build(args, runtime),
              'release_flags': 'maturin build --release --locked; all four builds sequential; no native CPU tuning',
              'cases': CASES, 'orders': ORDERS}
    (args.output / 'build-provenance.json').write_text(json.dumps(result, indent=2) + '\n')


def verify_build(args):
    provenance = json.loads((args.output / 'build-provenance.json').read_text())
    if provenance['flags'] != flags_record():
        raise ValueError('toolchain or release environment changed')
    if provenance['scripts'] != {p.name: sha256(p) for p in (Path(__file__), SCRIPT, PROBE)}:
        raise ValueError('controller, query harness or corpus probe changed')
    for side, build in provenance['builds'].items():
        if source_record(getattr(args, side + '_source'), getattr(args, side + '_commit')) != build['source']:
            raise ValueError('source changed after build')
        if wheel_record(args.wheel_dir / side, build['identity']) != build['wheel']:
            raise ValueError('preserved wheel changed')
        for name, digest in build['wheel']['native_files'].items():
            if sha256(name) != digest:
                raise ValueError('installed native module changed')
    reference_build(args, provenance['runtime'], expected=provenance['reference_build'])
    return provenance


def corpus_gate(path):
    reports = {}
    for side in SIDES[1:]:
        report = json.loads((path / ('base-vs-' + side + '-exact.json')).read_text())
        if (not report['require_exact'] or report['cases'] != 10624 or report['checked_values'] != 2167654
                or report['failures'] or not report['api_call_contract_match']
                or report['fields_with_bit_differences'] != 0 or report['max_absolute_difference'] != 0):
            raise ValueError('complete exact API corpus must pass before timing')
        for key in ('baseline', 'candidate'):
            if sha256(path / Path(report[key]).name) != report[key + '_sha256']:
                raise ValueError('corpus data changed')
        reports[side] = report
    return reports


def child(args, side, threads, label, extra):
    folder = args.output / f'threads-{threads}'; folder.mkdir(exist_ok=True)
    env = os.environ.copy(); env.update(POLARS_MAX_THREADS=str(threads), OMP_NUM_THREADS='1',
                                       OPENBLAS_NUM_THREADS='1', MKL_NUM_THREADS='1')
    command = [str(getattr(args, side + '_python').absolute()), str(SCRIPT),
               '--source-root', str(getattr(args, side + '_source').resolve()),
               '--output', str(folder / (label + '.json')), '--label', label,
               '--repeats', str(args.repeats), *map(str, extra)]
    for case in CASES:
        command += ['--case-filter', case]
    print(time.strftime('%H:%M:%S'), f'threads={threads}', label, flush=True)
    with (folder / (label + '.log')).open('w') as log:
        log.write(json.dumps(command) + '\n'); log.flush()
        subprocess.run(command, env=env, check=True, stdout=log, stderr=subprocess.STDOUT)
    return json.loads((folder / (label + '.json')).read_text())


def affinity_for(original, threads):
    if original is not None:
        if len(original) < threads:
            raise ValueError('runner has insufficient CPU affinity')
        os.sched_setaffinity(0, sorted(original)[:threads])


def validate_run(row, side, threads, repeats, provenance, timed):
    build = provenance['reference_build'] if side == 'original' else provenance['builds'][side]
    source = build['source']
    if row['commit'] != source['commit'] or row['source_sha256'] != source['source_sha256']:
        raise ValueError('measured source does not match immutable build')
    if row['threads'] != threads or row['repeats'] != repeats or row['warmups'] != 5 or row['diagnostic']:
        raise ValueError('unexpected timing configuration')
    if not isinstance(row['affinity'], list) or len(row['affinity']) != threads:
        raise ValueError('requested CPU affinity was not used')
    if row['rust'] != provenance['flags']['rustc'].splitlines()[0]:
        raise ValueError('measured Rust toolchain differs from build')
    if row['case_filters'] != list(CASES):
        raise ValueError('selected workload inventory changed')
    for key in ('python', 'polars', 'numpy', 'package', 'talib', 'platform'):
        if row[key] != build['identity'][key]:
            raise ValueError('measured runtime differs from installed build')
    if timed:
        if set(row['results']) != set(CASES) or row['checked_values'] != CHECKED_VALUES or not row['exact_reference']:
            raise ValueError('all 12 queries must pass exact checks before timing')
        for entry in row['results'].values():
            samples = entry['samples_ms']
            if len(samples) != repeats or any(isinstance(x, bool) or not isinstance(x, (int, float)) or not math.isfinite(x) or x <= 0 for x in samples):
                raise ValueError('invalid timing samples')
            if entry['median_ms'] != statistics.median(samples):
                raise ValueError('process median is inconsistent with raw samples')
            for counter in ('minor_faults', 'major_faults'):
                if len(entry[counter]) != repeats or any(isinstance(x, bool) or not isinstance(x, int) or x < 0 for x in entry[counter]):
                    raise ValueError('invalid fault counter samples')
    elif row['results']:
        raise ValueError('validation must not time queries')


def validate_all(args):
    provenance = verify_build(args); folder = args.output / 'corpus'; folder.mkdir(exist_ok=True)
    for side in (*SIDES, 'original'):
        command = [str(getattr(args, side + '_python').absolute()), str(PROBE), '--capture', str(folder / (side + '.npz'))]
        subprocess.run(command, check=True)
    for side in SIDES[1:]:
        subprocess.run([str(args.base_python.absolute()), str(PROBE), '--compare', str(folder / 'base.npz'),
                        str(folder / (side + '.npz')), '--exact', '--report', str(folder / ('base-vs-' + side + '-exact.json'))], check=True)
    original_reports = {}
    for side in SIDES:
        report_path = folder / ('original-vs-' + side + '.json')
        subprocess.run([str(args.base_python.absolute()), str(PROBE), '--compare', str(folder / 'original.npz'),
                        str(folder / (side + '.npz')), '--report', str(report_path)], check=True)
        original_reports[side] = json.loads(report_path.read_text())
        if (original_reports[side]['failures'] or original_reports[side]['cases'] != 10624
                or original_reports[side]['checked_values'] != 2167654):
            raise ValueError('original C full corpus compatibility failed or underchecked')
    corpus = corpus_gate(folder)
    original = set(os.sched_getaffinity(0)) if hasattr(os, 'sched_getaffinity') else None
    validations = {}
    try:
        for threads in (1, 4):
            affinity_for(original, threads)
            reference = args.output / f'threads-{threads}' / 'reference.npz'
            original_reference = reference.with_name('reference-original.npz')
            row = child(args, 'original', threads, 'reference-original', ['--check-only', '--write-reference', original_reference])
            validate_run(row, 'original', threads, args.repeats, provenance, False)
            for side in SIDES:
                row = child(args, side, threads, 'original-validation-' + side, ['--check-only', '--reference', original_reference])
                validate_run(row, side, threads, args.repeats, provenance, False)
                if row['checked_values'] != CHECKED_VALUES:
                    raise ValueError('original C query validation did not cover all values')
            base = child(args, 'base', threads, 'reference-base', ['--check-only', '--write-reference', reference])
            validate_run(base, 'base', threads, args.repeats, provenance, False)
            validations[str(threads)] = {'reference_sha256': sha256(reference), 'original_reference_sha256': sha256(original_reference), 'checked_values': CHECKED_VALUES, 'sides': {}}
            for side in SIDES[1:]:
                row = child(args, side, threads, 'validation-' + side, ['--check-only', '--reference', reference, '--exact-reference'])
                validate_run(row, side, threads, args.repeats, provenance, False)
                if row['checked_values'] != CHECKED_VALUES or not row['exact_reference']:
                    raise ValueError('exact workload validation did not complete')
                validations[str(threads)]['sides'][side] = row['checked_values']
    finally:
        if original is not None:
            os.sched_setaffinity(0, original)
    verify_build(args)
    (args.output / 'validation-complete.json').write_text(json.dumps(
        {'corpus': corpus, 'original_corpus': original_reports, 'workloads': validations, 'all_checks_completed_before_any_timing': True,
         'commits': {side: provenance['builds'][side]['source']['commit'] for side in SIDES}}, indent=2) + '\n')


def pair_summary(before, after, name):
    old = [statistics.median(row['results'][name]['samples_ms']) for row in before]
    new = [statistics.median(row['results'][name]['samples_ms']) for row in after]
    ratios = [a / b for a, b in zip(old, new)]
    return {'before_process_medians_ms': old, 'after_process_medians_ms': new,
            'before_median_ms': statistics.median(old), 'after_median_ms': statistics.median(new),
            'paired_ratios': ratios, 'median_paired_ratio': statistics.median(ratios),
            'ratio_envelope': [min(old) / max(new), max(old) / min(new)],
            'after_latency_percent': (statistics.median(new) / statistics.median(old) - 1) * 100,
            'after_faster_rounds': sum(r > 1 for r in ratios)}


def measure(args):
    provenance = verify_build(args); validation = json.loads((args.output / 'validation-complete.json').read_text())
    corpus_gate(args.output / 'corpus')
    expected_commits = {side: provenance['builds'][side]['source']['commit'] for side in SIDES}
    if not validation['all_checks_completed_before_any_timing'] or validation['commits'] != expected_commits:
        raise ValueError('validation does not cover these builds')
    for threads in (1, 4):
        if sha256(args.output / f'threads-{threads}' / 'reference.npz') != validation['workloads'][str(threads)]['reference_sha256']:
            raise ValueError('exact workload reference changed')
    for threads in (1, 4):
        reference = args.output / f'threads-{threads}' / 'reference-original.npz'
        if sha256(reference) != validation['workloads'][str(threads)]['original_reference_sha256']:
            raise ValueError('original workload reference changed')
    for side, report in validation['original_corpus'].items():
        if report['failures']:
            raise ValueError('original corpus did not pass')
        for label in ('baseline', 'candidate'):
            if sha256(args.output / 'corpus' / Path(report[label]).name) != report[label + '_sha256']:
                raise ValueError('original corpus capture changed')
    original = set(os.sched_getaffinity(0)) if hasattr(os, 'sched_getaffinity') else None
    settings = {}; negatives = []; lines = ['# Native allocation ablations', '',
        'All four native wheels use the same locked release flags, runtime and unchanged query harness. Full API and both thread settings pass exact-value/signed-zero workload checks before any timing.',
        'Eight fresh processes/build/thread setting; Williams ABDC/BCAD/CDBA/DACB orders repeated twice; 31 samples after five warmups.',
        'Positions and within-round directed carryover are balanced; adjacency across round boundaries is not perfectly balanced.',
        'Ratios use matched process medians. Envelopes are descriptive ranges, not confidence intervals. Inner samples are correlated; host contention/frequency remain uncontrolled. Pairwise improvements need not add.', '']
    try:
        for threads in (1, 4):
            affinity_for(original, threads); verify_build(args)
            runs = {side: [] for side in SIDES}; order = []
            for round_index, sides in enumerate(ORDERS):
                for side in sides:
                    for path, digest in provenance['builds'][side]['wheel']['native_files'].items():
                        if sha256(path) != digest:
                            raise ValueError('native module changed before process')
                    label = f'{side}-{round_index + 1}'; order.append(label)
                    row = child(args, side, threads, label,
                                ['--reference', args.output / f'threads-{threads}' / 'reference.npz', '--exact-reference'])
                    validate_run(row, side, threads, args.repeats, provenance, True)
                    runs[side].append(row)
            all_runs = [row for side in SIDES for row in runs[side]]
            for key in RUN_KEYS:
                if len({json.dumps(row[key], sort_keys=True) for row in all_runs}) != 1:
                    raise ValueError('incomparable process metadata: ' + key)
            comparisons = {before + '_vs_' + after: {name: pair_summary(runs[before], runs[after], name) for name in CASES}
                           for before, after in itertools.combinations(SIDES, 2)}
            faults = {name: {side: {counter: {'median': statistics.median([statistics.median(row['results'][name][counter]) for row in runs[side]]),
                    'process_medians': [statistics.median(row['results'][name][counter]) for row in runs[side]]}
                    for counter in ('minor_faults', 'major_faults')} for side in SIDES} for name in CASES}
            data = {'threads': threads, 'affinity': all_runs[0]['affinity'], 'checked_values': CHECKED_VALUES,
                    'orders': order, 'comparisons': comparisons, 'faults': faults,
                    'runtime': {key: all_runs[0][key] for key in RUN_KEYS}}
            settings[str(threads)] = data
            (args.output / f'threads-{threads}' / 'summary.json').write_text(json.dumps(data, indent=2) + '\n')
            lines += [f'## {threads} thread(s)', '', '| Case | Base ms | Utils ms | MMI ms | Composed ms | Base/composed envelope |',
                      '| --- | ---: | ---: | ---: | ---: | --- |']
            for name in CASES:
                medians = [statistics.median([row['results'][name]['median_ms'] for row in runs[side]]) for side in SIDES]
                lo, hi = comparisons['base_vs_composed'][name]['ratio_envelope']
                lines.append('| ' + name + ' | ' + ' | '.join(f'{x:.5f}' for x in medians) + f' | {lo:.3f}–{hi:.3f} |')
            for comparison, values in comparisons.items():
                for name, value in values.items():
                    if value['after_latency_percent'] > 0:
                        negatives.append({'threads': threads, 'comparison': comparison, 'case': name, **value})
    finally:
        if original is not None:
            os.sched_setaffinity(0, original)
    verify_build(args)
    report = {'run_url': f"{os.environ.get('GITHUB_SERVER_URL', 'https://github.com')}/{os.environ.get('GITHUB_REPOSITORY', 'local')}/actions/runs/{os.environ.get('GITHUB_RUN_ID', 'local')}",
              'build_provenance': provenance, 'validation': validation, 'rounds': 8, 'samples_per_process': args.repeats,
              'orders': ORDERS, 'cases': CASES, 'results': settings, 'negative_cases': negatives,
              'fault_limitation': 'Process getrusage totals include engine/Python/allocator; not allocator-only attribution.'}
    (args.output / 'summary.json').write_text(json.dumps(report, indent=2) + '\n')
    (args.output / 'comparison.md').write_text('\n'.join(lines) + '\n')
    negative_lines = ['# Every slower pairwise median', '', 'All six pairwise comparisons are included, controls too. Ranges are descriptive, not significance tests.', '',
                      '| Threads | Comparison | Case | Latency increase | Before/after envelope | Faster rounds |', '| ---: | --- | --- | ---: | --- | ---: |']
    for row in sorted(negatives, key=lambda row: (row['threads'], -row['after_latency_percent'])):
        lo, hi = row['ratio_envelope']
        negative_lines.append(f"| {row['threads']} | {row['comparison']} | {row['case']} | +{row['after_latency_percent']:.3f}% | {lo:.3f}–{hi:.3f} | {row['after_faster_rounds']}/8 |")
    (args.output / 'negative-cases.md').write_text('\n'.join(negative_lines) + '\n')
    print('\n'.join(lines), flush=True)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    for side in (*SIDES, 'original'):
        parser.add_argument('--' + side + '-python', type=Path, required=True)
        parser.add_argument('--' + side + '-source', type=Path, required=True)
        parser.add_argument('--' + side + '-commit', required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--wheel-dir', type=Path, required=True)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--record-build', action='store_true')
    mode.add_argument('--validate-only', action='store_true')
    parser.add_argument('--repeats', type=int, default=31)
    args = parser.parse_args(argv)
    if args.repeats != 31:
        parser.error('31 samples are required for this fixed ablation campaign')
    args.output = args.output.resolve(); args.wheel_dir = args.wheel_dir.resolve()
    args.output.mkdir(parents=True, exist_ok=True)
    if args.record_build:
        record_build(args)
    elif args.validate_only:
        validate_all(args)
    else:
        measure(args)


if __name__ == '__main__':
    main()
