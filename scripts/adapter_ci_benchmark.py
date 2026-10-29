"""Original C / delivered native / optimized adapter comparison on one CI runner.

Builds happen in the workflow, never during measurements. Every thread setting
uses fresh processes, all six permutations of the three implementations, workload
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
        for key in ('commit', 'source_sha256'):
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

    def run(side, label, *extra):
        # absolute() retains the virtualenv symlink and therefore sys.prefix.
        command = [str(getattr(args, side+'_python').absolute()), str(script),
                   '--source-root', str(getattr(args, side+'_source').resolve()),
                   '--output', str(out/(label+'.json')), '--label', label,
                   '--repeats', str(args.repeats), *map(str, extra)]
        if threads == 1:
            command.append('--diagnostic')
        for pattern in args.case_filter:
            command += ['--case-filter',pattern]
        commands.append(command)
        print(f'{time.strftime("%H:%M:%S")} threads={threads} {label}', flush=True)
        subprocess.run(command, env=env, check=True)
        return json.loads((out/(label+'.json')).read_text())

    reference_run = run('original', 'reference', '--check-only', '--write-reference', reference)
    validations = {side: run(side, f'validation-{side}', '--check-only', '--reference', reference)
                   for side in ('prior', 'candidate')}
    prior_reference = out / 'prior-reference.npz'
    run('prior', 'reference-prior', '--check-only', '--write-reference', prior_reference)
    exact_validation = run('candidate', 'validation-exact-prior', '--check-only',
                           '--reference', prior_reference, '--exact-reference')
    if not exact_validation['exact_reference'] or exact_validation['checked_values'] <= 0:
        raise ValueError('delivered vs optimized workload validation did not run exactly')
    prior_reference.unlink()
    runs = {side: [] for side in SIDES}
    order = []
    for index in range(args.rounds):
        for side in ORDERS[index % len(ORDERS)]:
            label = f'{side}-{index+1}'
            order.append(label)
            runs[side].append(run(side, label, '--reference', reference))
    comparisons, faults = analyze(runs, args.repeats, threads)
    first = runs['candidate'][0]
    for side, validation in validations.items():
        if validation['commit'] != runs[side][0]['commit'] or validation['source_sha256'] != runs[side][0]['source_sha256']:
            raise ValueError(f'{side} validation source differs')
    if reference_run['commit'] != runs['original'][0]['commit'] or reference_run['source_sha256'] != runs['original'][0]['source_sha256']:
        raise ValueError('original reference source differs')
    metadata = {key: first[key] for key in ('cpu', 'platform', 'python', 'polars', 'numpy',
                'rust', 'threads', 'affinity', 'repeats', 'warmups', 'diagnostic', 'checked_values', 'case_filters')}
    metadata.update(commits={side: runs[side][0]['commit'] for side in SIDES},
                    source_sha256={side: runs[side][0]['source_sha256'] for side in SIDES},
                    rounds=args.rounds, order=order, commands=commands, exact_prior_validation=exact_validation['checked_values'],
                    reference_sha256=hashlib.sha256(reference.read_bytes()).hexdigest(),
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
    # The deterministic reference is regenerated for the other thread setting;
    # retain its hash, not multiple large untimed NPZ buffers on the runner.
    reference.unlink()
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
             f'{args.rounds} fresh processes per build/thread setting; all six build-order permutations; {args.repeats} samples after five warmups.',
             'Ratios use matched-round medians. Envelopes span min(before medians)/max(after medians) to max(before)/min(after).',
             'These are descriptive ranges, not confidence intervals. Shared-host contention, frequency and placement remain uncontrolled.',
             'getrusage counters are process totals sampled outside the latency interval; they do not isolate jemalloc or kernel faults.',
             'Only direct expressions and ordinary native Polars .over() are measured. No new grouping expression/list composition.',
             'The 1-thread sweep includes groups shorter than the default EMA warmup; workload deltas cannot isolate a pure fixed setup cost.', '',
             *sections]
    (args.output/'comparison.md').write_text('\n'.join(lines)+'\n')
    print('\n'.join(lines), flush=True)


if __name__ == '__main__':
    main()
