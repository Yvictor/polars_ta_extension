"""Original C / delivered native / optimized adapter comparison on one CI runner.

Builds happen in the workflow, never during measurements. Every thread setting
uses one fresh process per case and round, all six permutations of the three implementations, workload
correctness checks, raw samples and descriptive process-noise ranges.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import platform
import statistics
import subprocess
import time

from migration_ci_benchmark import percentile, summarize

SIDES = ('original', 'prior', 'candidate')
ORIGINAL_COMMIT = 'b2bbc26d41ec80823c8bffb0cc436a97f29911cc'
PRIOR_COMMIT = 'c71cd6ecb4b48601ff409926fdb0a281505e9fec'
ORDERS = (
    ('original', 'prior', 'candidate'),
    ('prior', 'candidate', 'original'),
    ('candidate', 'original', 'prior'),
    ('candidate', 'prior', 'original'),
    ('prior', 'original', 'candidate'),
    ('original', 'candidate', 'prior'),
)


def fault_summary(runs, name, counter):
    samples = [r['results'][name][counter] for r in runs]
    if any(s is None for s in samples):
        return None
    if any(not s or len(s) != r['repeats'] or any(x < 0 for x in s)
           for s, r in zip(samples, runs)):
        raise ValueError('invalid process fault samples')
    medians = [statistics.median(s) for s in samples]
    pooled = [x for s in samples for x in s]
    return {'median': statistics.median(medians), 'process_medians': medians,
            'p10_p90': [percentile(pooled, p) for p in (.1, .9)]}


def analyze(runs, repeats, threads):
    all_runs = [r for side in SIDES for r in runs[side]]
    expected = len(runs['original'])
    if expected < 6 or any(len(runs[side]) != expected for side in SIDES):
        raise ValueError('at least six matched rounds required for each build')
    for side in SIDES:
        for key in ('commit', 'source_sha256', 'native_binary_sha256'):
            if len({r[key] for r in runs[side]}) != 1:
                raise ValueError(f'{side} source changed')
    for key in ('python', 'platform', 'cpu', 'polars', 'numpy', 'rust', 'profile',
                'threads', 'affinity', 'repeats', 'warmups', 'diagnostic', 'checked_values', 'case_filters'):
        if len({json.dumps(r[key]) for r in all_runs}) != 1:
            raise ValueError(f'incomparable runtime/validation: {key}')
    if all_runs[0]['threads'] != threads or all_runs[0]['repeats'] != repeats:
        raise ValueError('requested threads/repetitions not used')
    if all_runs[0]['checked_values'] <= 0:
        raise ValueError('no checked workload values')
    for r in all_runs:
        for entry in r['results'].values():
            if len(entry['samples_ms']) != repeats or any(not math.isfinite(x) or x <= 0 for x in entry['samples_ms']):
                raise ValueError('invalid timing samples')
    comparisons = {
        'original_vs_prior': summarize(runs['original'], runs['prior']),
        'prior_vs_candidate': summarize(runs['prior'], runs['candidate']),
        'original_vs_candidate': summarize(runs['original'], runs['candidate']),
    }
    faults = {name: {side: {counter: fault_summary(runs[side], name, counter)
                            for counter in ('minor_faults', 'major_faults')}
                     for side in SIDES} for name in comparisons['original_vs_candidate']}
    return comparisons, faults


def selected_inventory(report, expected):
    if report.get('case_inventory') != expected:
        raise ValueError('child case inventory differs from the requested selection')
    if not isinstance(expected, list) or not expected or len(set(expected)) != len(expected):
        raise ValueError('empty or duplicate case inventory')
    if set(report['results']) != set(expected):
        raise ValueError('timed child did not run exactly the requested cases')
    if report['case_filters'] != expected:
        raise ValueError('timed child selector differs')
    if report['checked_values'] <= 0:
        raise ValueError('timed child did not validate its selected workload')


def run_setting(args, threads, affinity):
    out = args.output.resolve() / f'threads-{threads}'
    out.mkdir(parents=True, exist_ok=True)
    if affinity is not None:
        os.sched_setaffinity(0, sorted(affinity)[:threads])
    env = os.environ.copy()
    env.update(POLARS_MAX_THREADS=str(threads), OMP_NUM_THREADS='1',
               OPENBLAS_NUM_THREADS='1', MKL_NUM_THREADS='1')
    script = Path(__file__).with_name('migration_benchmark.py').resolve()
    reference = out / 'reference.npz'
    commands = []

    def run(side, label, *extra, selected=None):
        # absolute() retains the virtualenv symlink and therefore sys.prefix.
        command = [str(getattr(args, side+'_python').absolute()), str(script),
                   '--source-root', str(getattr(args, side+'_source').resolve()),
                   '--output', str(out/(label+'.json')), '--label', label,
                   '--repeats', str(args.repeats), *map(str, extra)]
        if threads == 1:
            command.append('--diagnostic')
        for pattern in ([selected] if selected is not None else args.case_filter):
            command += ['--case-filter', pattern]
        commands.append(command)
        print(f'{time.strftime("%H:%M:%S")} threads={threads} {label} {selected or "validation"}', flush=True)
        subprocess.run(command, env=env, check=True)
        result = json.loads((out/(label+'.json')).read_text())
        if selected is not None:
            selected_inventory(result, [selected])
        return result

    reference_run = run('original', 'reference', '--check-only', '--write-reference', reference)
    validations = {side: run(side, f'validation-{side}', '--check-only', '--reference', reference)
                   for side in ('prior', 'candidate')}
    if reference_run['commit'] != ORIGINAL_COMMIT or validations['prior']['commit'] != PRIOR_COMMIT:
        raise ValueError('original or delivered source commit differs from its immutable pin')
    if not reference_run['talib'].startswith('0.8.1'):
        raise ValueError('original runtime is not the pinned C0.8.1')
    for validation in validations.values():
        if validation['talib'] != '0.8.3 (native Rust; polars-talib compatibility)':
            raise ValueError('native runtime is not the pinned compatibility adapter')
    inventory = reference_run['case_inventory']
    if not inventory or len(set(inventory)) != len(inventory):
        raise ValueError('empty or duplicate reference inventory')
    for validation in validations.values():
        if validation['case_inventory'] != inventory or validation['checked_values'] <= 0:
            raise ValueError('reference validation omitted workloads')
    prior_reference = out / 'prior-reference.npz'
    run('prior', 'reference-prior', '--check-only', '--write-reference', prior_reference)
    exact_validation = run('candidate', 'validation-exact-prior', '--check-only',
                           '--reference', prior_reference, '--exact-reference')
    if (not exact_validation['exact_reference'] or exact_validation['checked_values'] <= 0
            or exact_validation['case_inventory'] != inventory):
        raise ValueError('delivered vs optimized workload validation did not run exactly')
    # Retain both golden references. A failed later child must remain auditable.
    source_validations = {'original': reference_run, **validations}
    comparisons = {key: {} for key in ('original_vs_prior', 'prior_vs_candidate', 'original_vs_candidate')}
    faults = {}
    order = []
    process_manifest = []
    first = validations['candidate']
    for case_index, name in enumerate(inventory):
        runs = {side: [] for side in SIDES}
        for index in range(args.rounds):
            for side in ORDERS[index % len(ORDERS)]:
                label = f'case-{case_index+1:03d}-{side}-{index+1}'
                order.append(label)
                child = run(side, label, '--reference', reference, selected=name)
                origin = source_validations[side]
                for key in ('commit', 'source_sha256', 'native_binary_sha256', 'talib', 'python', 'platform', 'cpu',
                            'polars', 'numpy', 'rust', 'profile', 'threads', 'affinity'):
                    if child[key] != origin[key]:
                        raise ValueError(f'{side} child source/runtime changed: {key}')
                runs[side].append(child)
                process_manifest.append({'case': name, 'side': side, 'round': index+1,
                                         'report': label+'.json'})
        # Analyze one case at a time: every sample set has its OWN fresh process,
        # rather than a reused process carrying previous indicators' heap state.
        case_comparisons, case_faults = analyze(runs, args.repeats, threads)
        for key, values in case_comparisons.items():
            if set(values) != {name} or name in comparisons[key]:
                raise ValueError('case comparison inventory drift')
            comparisons[key].update(values)
        faults.update(case_faults)
    metadata = {key: first[key] for key in ('cpu', 'platform', 'python', 'polars', 'numpy',
                'rust', 'threads', 'affinity', 'repeats', 'warmups', 'diagnostic', 'checked_values', 'case_filters')}
    metadata.update(commits={side: source_validations[side]['commit'] for side in SIDES},
                    source_sha256={side: source_validations[side]['source_sha256'] for side in SIDES},
                    native_binary_sha256={side: source_validations[side]['native_binary_sha256'] for side in SIDES},
                    rounds=args.rounds, order=order, commands=commands,
                    case_inventory=inventory, process_isolation='one case per fresh process',
                    processes=process_manifest, exact_prior_validation=exact_validation['checked_values'],
                    reference_sha256=hashlib.sha256(reference.read_bytes()).hexdigest(),
                    prior_reference_sha256=hashlib.sha256(prior_reference.read_bytes()).hexdigest(),
                    comparisons=comparisons, faults=faults)
    (out/'summary.json').write_text(json.dumps(metadata, indent=2)+'\n')
    lines = [f'## {threads} thread(s)', '',
             f"Each workload checked before timing: {first['checked_values']:,} numeric values; exact schema/null/NaN positions; original tolerance rtol=atol=1e-10. Delivered native vs optimized adapter workloads also pass an untimed exact-value/signed-zero comparison.",
             '', '| Query | Original ms | Delivered native ms | Optimized adapter ms | Original / optimized (envelope) | Delivered / optimized (envelope) |',
             '| --- | ---: | ---: | ---: | --- | --- |']
    for name, pair in comparisons['original_vs_candidate'].items():
        zc = comparisons['prior_vs_candidate'][name]
        oz = comparisons['original_vs_prior'][name]
        lo, hi = pair['ratio_envelope']; zl, zh = zc['ratio_envelope']
        lines.append(f"| {name} | {pair['baseline_median_ms']:.4f} | {oz['candidate_median_ms']:.4f} | {pair['candidate_median_ms']:.4f} | {pair['median_paired_ratio']:.2f}x ({lo:.2f}–{hi:.2f}) | {zc['median_paired_ratio']:.2f}x ({zl:.2f}–{zh:.2f}) |")
    lines += ['', 'Process minor faults per query (median of process medians; includes Polars/Python/allocator activity, not allocator-only attribution):',
              '', '| Query | Original | Delivered native | Optimized adapter |', '| --- | ---: | ---: | ---: |']
    for name in comparisons['original_vs_candidate']:
        vals = [faults[name][side]['minor_faults'] for side in SIDES]
        lines.append('| '+name+' | '+' | '.join('unavailable' if v is None else str(v['median']) for v in vals)+' |')
    (out/'comparison.md').write_text('\n'.join(lines)+'\n')
    return metadata, lines


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for side in SIDES:
        parser.add_argument(f'--{side}-python', type=Path, required=True)
        parser.add_argument(f'--{side}-source', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--thread-counts', nargs='+', type=int, default=[1, 4])
    parser.add_argument('--case-filter',action='append',default=[],help='Optional workload glob for a local harness smoke run; CI runs all cases')
    parser.add_argument('--rounds', type=int, default=6)
    parser.add_argument('--repeats', type=int, default=51)
    args = parser.parse_args()
    if args.rounds < 6 or args.rounds % 6 or args.repeats < 5 or any(t < 1 for t in args.thread_counts):
        parser.error('requires a positive multiple of six rounds, >=5 samples and positive thread counts')
    if len(set(args.thread_counts)) != len(args.thread_counts):
        parser.error('thread settings must be unique')
    args.output.mkdir(parents=True, exist_ok=True)
    affinity = set(os.sched_getaffinity(0)) if hasattr(os, 'sched_getaffinity') else None
    reports = {}; sections = []
    try:
        for threads in args.thread_counts:
            reports[str(threads)], lines = run_setting(args, threads, affinity)
            sections.extend(lines+[''])
    finally:
        if affinity is not None:
            os.sched_setaffinity(0, affinity)
    env = os.environ
    metadata = {'run_url': f"{env.get('GITHUB_SERVER_URL','https://github.com')}/{env.get('GITHUB_REPOSITORY','local')}/actions/runs/{env.get('GITHUB_RUN_ID','local')}",
                'runner_image': env.get('ImageOS'), 'runner_image_version': env.get('ImageVersion'),
                'platform': platform.platform(), 'thread_counts': args.thread_counts,
                'results': reports}
    (args.output/'summary.json').write_text(json.dumps(metadata, indent=2)+'\n')
    first = next(iter(reports.values()))
    lines = ['# Three-build adapter follow-up', '',
             *[f'{side}: `{first["commits"][side]}`' for side in SIDES], '',
             f"{first['cpu']}; {first['platform']}; Python {first['python']}, Polars {first['polars']}, NumPy {first['numpy']}; {first['rust']}.",
             f'{args.rounds} fresh processes per CASE/build/thread setting; all six build-order permutations; {args.repeats} samples after five warmups. No sibling query runs before the selected case.',
             'Ratios use matched-round medians. Envelopes span min(before medians)/max(after medians) to max(before)/min(after).',
             'These are descriptive ranges, not confidence intervals. Shared-host contention, frequency and placement remain uncontrolled.',
             'getrusage counters are process totals sampled outside the latency interval; they do not isolate jemalloc or kernel faults.',
             'Only direct expressions and ordinary native Polars .over() are measured. No new grouping expression/list composition.',
             'The 1-thread sweep includes groups shorter than the default EMA warmup; workload deltas cannot isolate a pure fixed setup cost.', '',
             *sections]
    (args.output/'comparison.md').write_text('\n'.join(lines)+'\n')
    from regression_inventory import write_inventory
    write_inventory(args.output/'summary.json')
    print('\n'.join(lines), flush=True)


if __name__ == '__main__':
    main()
