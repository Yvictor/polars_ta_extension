"""Compare two freshly built release wheels in alternating processes on one runner.

Correctness is a hard gate. Timings are informational: shared CI hosts cannot
support universal performance claims. Independent process medians, paired ratios
and a conservative envelope are reported instead of treating inner samples as
independent experiments.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import statistics
import subprocess
import sys
import time


def summarize(baseline, candidate):
    """Keep process-to-process spread separate from within-process samples."""
    if len(baseline) != len(candidate) or len(baseline) < 3:
        raise ValueError('at least three matched process pairs are required')
    cases=set(baseline[0]['results'])
    if not cases or any(set(run['results']) != cases for run in baseline+candidate):
        raise ValueError('benchmark case inventories differ')
    rows={}
    for name in sorted(cases):
        old=[r['results'][name]['median_ms'] for r in baseline]
        new=[r['results'][name]['median_ms'] for r in candidate]
        ratios=[a/b for a,b in zip(old,new)]
        envelope=[min(old)/max(new),max(old)/min(new)]
        # A deliberately conservative descriptive label, not a significance test.
        status=('consistent faster on this runner' if envelope[0]>1.05 else
                'consistent slower on this runner' if envelope[1]<1/1.05 else
                'small or noisy difference')
        rows[name]={'baseline_median_ms':statistics.median(old),
                    'candidate_median_ms':statistics.median(new),
                    'baseline_process_medians_ms':old,'candidate_process_medians_ms':new,
                    'paired_ratios':ratios,'median_paired_ratio':statistics.median(ratios),
                    'ratio_envelope':envelope,'assessment':status,
                    'baseline_sample_p10_p90_ms':[percentile([x for r in baseline for x in r['results'][name]['samples_ms']],p) for p in (.1,.9)],
                    'candidate_sample_p10_p90_ms':[percentile([x for r in candidate for x in r['results'][name]['samples_ms']],p) for p in (.1,.9)]}
    return rows


def percentile(values,p):
    values=sorted(values)
    at=(len(values)-1)*p
    lo=int(at);hi=min(lo+1,len(values)-1)
    return values[lo]+(values[hi]-values[lo])*(at-lo)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for side in ('baseline','candidate'):
        p.add_argument(f'--{side}-python',type=Path,required=True)
        p.add_argument(f'--{side}-source',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--pairs',type=int,default=6)
    p.add_argument('--repeats',type=int,default=51)
    p.add_argument('--threads',type=int,default=4)
    args=p.parse_args()
    if args.pairs<3 or args.repeats<5 or args.threads<1:p.error('requires >=3 pairs, >=5 samples and positive threads')
    out=args.output.resolve();out.mkdir(parents=True,exist_ok=True)
    env=os.environ.copy()
    env.update(POLARS_MAX_THREADS=str(args.threads),OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1')
    if hasattr(os,'sched_getaffinity'):
        selected=sorted(os.sched_getaffinity(0))[:args.threads]
        os.sched_setaffinity(0,selected)
    script=Path(__file__).with_name('migration_benchmark.py').resolve()
    reference=out/'reference.npz'
    commands=[];runs={'baseline':[],'candidate':[]}

    def run(side,label,*extra):
        # Preserve virtualenv interpreter symlinks: resolving them loses sys.prefix.
        command=[str(getattr(args,side+'_python').absolute()),str(script),'--source-root',str(getattr(args,side+'_source').resolve()),
                 '--output',str(out/(label+'.json')),'--label',label,'--repeats',str(args.repeats),*map(str,extra)]
        commands.append(command)
        print(f'{time.strftime("%H:%M:%S")} {label}',flush=True)
        subprocess.run(command,env=env,check=True)
        return json.loads((out/(label+'.json')).read_text())

    # Reference construction and validation are complete before any timed run.
    run('baseline','reference','--check-only','--write-reference',reference)
    validation=run('candidate','validation','--check-only','--reference',reference)
    if validation['checked_values']<=0:raise RuntimeError('no benchmark values checked')
    order=[]
    for pair in range(args.pairs):
        sides=('baseline','candidate') if pair%2==0 else ('candidate','baseline')
        for side in sides:
            label=f'{side}-{pair+1}';order.append(label)
            runs[side].append(run(side,label,'--reference',reference))
    # Keep pairing by round, irrespective of each round's AB/BA execution order.
    for side in runs:
        commits={r['commit'] for r in runs[side]}
        fingerprints={r['source_sha256'] for r in runs[side]}
        if len(commits)!=1 or len(fingerprints)!=1:raise RuntimeError(f'{side} source changed during measurements')
    for key in ('python','polars','numpy','threads','affinity','repeats','warmups'):
        if len({json.dumps(r[key]) for r in runs['baseline']+runs['candidate']})!=1:
            raise RuntimeError(f'runtime mismatch: {key}')
    if validation['threads']!=args.threads:raise RuntimeError('Polars did not use the requested thread count')
    rows=summarize(runs['baseline'],runs['candidate'])
    metadata={'baseline_commit':runs['baseline'][0]['commit'],'candidate_commit':runs['candidate'][0]['commit'],
              'platform':platform.platform(),'cpu':validation['cpu'],'logical_cpus':os.cpu_count(),
              'affinity':validation['affinity'],'python':validation['python'],'polars':validation['polars'],'numpy':validation['numpy'],
              'threads':args.threads,'pairs':args.pairs,'samples_per_process':args.repeats,'warmups':5,
              'order':order,'correctness_checked_values':validation['checked_values'],
              'reference_sha256':hashlib.sha256(reference.read_bytes()).hexdigest(),
              'run_url':f"{env.get('GITHUB_SERVER_URL','https://github.com')}/{env.get('GITHUB_REPOSITORY','local')}/actions/runs/{env.get('GITHUB_RUN_ID','local')}",
              'runner_image':env.get('ImageOS'),'runner_image_version':env.get('ImageVersion'),
              'commands':commands,'results':rows}
    (out/'summary.json').write_text(json.dumps(metadata,indent=2)+'\n')
    lines=['# Same-runner release comparison','',f"Baseline `{metadata['baseline_commit']}` → candidate `{metadata['candidate_commit']}`.",
           f"{metadata['cpu']}; {metadata['platform']}; Python {metadata['python']}, Polars {metadata['polars']}, NumPy {metadata['numpy']}.",
           f"{args.pairs} fresh process pairs in alternating AB/BA order; {args.repeats} samples after 5 warmups; {args.threads} threads; affinity {metadata['affinity']}.",
           f"Each timed workload checked before timing against the rebuilt original: {validation['checked_values']:,} numeric values, exact null/NaN locations, rtol=atol=1e-10.",
           '', 'Ratios are original / native, using paired process medians. Envelope = min(original medians)/max(native medians) to max(original)/min(native).',
           'This is a descriptive noise range, not a statistical confidence interval. Samples within a process are correlated. Shared-host contention, frequency and CPU placement remain uncontrolled.',
           'Only ordinary `.over()` and direct expressions are measured. Complete lazy `collect()` is timed; setup and correctness are excluded.',
           '', '| Query | Original ms | Native ms | Median paired ratio | Ratio envelope | Assessment |',
           '| --- | ---: | ---: | ---: | --- | --- |']
    for name,r in rows.items():
        a,b=r['ratio_envelope']
        lines.append(f"| {name} | {r['baseline_median_ms']:.4f} | {r['candidate_median_ms']:.4f} | {r['median_paired_ratio']:.2f}x | {a:.2f}–{b:.2f}x | {r['assessment']} |")
    (out/'comparison.md').write_text('\n'.join(lines)+'\n')
    print('\n'.join(lines),flush=True)


if __name__=='__main__':main()
