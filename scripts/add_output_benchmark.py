"""Original C / Native56 control / ADD initialized-output candidate comparison on one CI runner.

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
import shutil
import subprocess
import time

from migration_ci_benchmark import percentile, summarize
from add_output_inputs import validate as validate_inputs

SIDES = ('original', 'prior', 'candidate')
ORIGINAL_COMMIT = 'b2bbc26d41ec80823c8bffb0cc436a97f29911cc'
PRIOR_COMMIT = '56f6d5fb139031c20d86d7e818e7d267eb834295'
NATIVE_SIDES = ('prior', 'candidate')
LABELS = {'original':'Original C', 'prior':'Native56 control', 'candidate':'ADD initialized-output candidate'}
MANIFEST = Path(__file__).with_name('add_output_cases.json')
CASES = tuple(json.loads(MANIFEST.read_text())['cases'])
CHECKED_VALUES = 15_000_000
from add_output_provenance import sha256, source_record, identity, wheel_record, flags_record, validate_identities, elf_record
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
    if expected != 12 or repeats != 31 or any(len(runs[side]) != expected for side in SIDES):
        raise ValueError('exactly twelve matched rounds and 31 samples required for each build')
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


def requested_inventory(diagnostic=False, filters=()):
    manifest = json.loads(MANIFEST.read_text())
    names = manifest['cases']
    if diagnostic or filters or len(names) != 15 or len(set(names)) != 15 or manifest['checked_values'] != CHECKED_VALUES:
        raise ValueError('fixed reviewed 15-case inventory may not be filtered or expanded')
    return names


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


def run_setting(args, threads, affinity, *, prepare_only=False):
    out = args.output.resolve() / f'threads-{threads}'
    out.mkdir(parents=True, exist_ok=True)
    if affinity is not None:
        os.sched_setaffinity(0, sorted(affinity)[:threads])
    env = os.environ.copy()
    env.update(POLARS_MAX_THREADS=str(threads), OMP_NUM_THREADS='1',
               OPENBLAS_NUM_THREADS='1', MKL_NUM_THREADS='1')
    provenance = verify_build(args)
    script = Path(__file__).with_name('add_output_query.py').resolve()
    reference = out / 'reference.npz'
    commands = []

    def run(side, label, *extra, selected=None):
        # absolute() retains the virtualenv symlink and therefore sys.prefix.
        command = [str(getattr(args, side+'_python').absolute()), str(script),
                   '--source-root', str(getattr(args, side+'_source').resolve()),
                   '--output', str(out/(label+'.json')), '--label', label,
                   '--repeats', str(args.repeats), *map(str, extra)]
        for pattern in ([selected] if selected is not None else requested_inventory()):
            command += ['--case-filter', pattern]
        commands.append(command)
        with (out/'commands.jsonl').open('a') as log:
            log.write(json.dumps({'label': label, 'side': side, 'selected_case': selected,
                                  'argv': command, 'polars_threads': threads})+'\n')
        print(f'{time.strftime("%H:%M:%S")} threads={threads} {label} {selected or "validation"}', flush=True)
        with (out/(label+'.stdout.log')).open('w') as stdout, (out/(label+'.stderr.log')).open('w') as stderr:
            subprocess.run(command, env=env, check=True, stdout=stdout, stderr=stderr)
        result = json.loads((out/(label+'.json')).read_text())
        validate_report(result, side, threads, provenance, selected)
        return result

    prepared_path = out / 'prepared-validation.json'
    if prepare_only:
        reference_run = run('original', 'reference', '--check-only', '--write-reference', reference, '--save-inputs', args.output.resolve()/'inputs')
        validations = {side: run(side, f'validation-{side}', '--check-only', '--reference', reference)
                       for side in ('prior', 'candidate')}
        if reference_run['commit'] != ORIGINAL_COMMIT or validations['prior']['commit'] != PRIOR_COMMIT or validations['candidate']['commit'] != args.candidate_commit:
            raise ValueError('source commit differs from its immutable pin')
        if not reference_run['talib'].startswith('0.8.1'):
            raise ValueError('original runtime is not the pinned C0.8.1')
        for validation in validations.values():
            if validation['talib'] != '0.8.3 (native Rust; polars-talib compatibility)':
                raise ValueError('native runtime is not the pinned compatibility adapter')
        inventory = reference_run['case_inventory']
        if inventory != requested_inventory():
            raise ValueError('reference omitted or changed a reviewed workload')
        if not inventory or len(set(inventory)) != len(inventory):
            raise ValueError('empty or duplicate reference inventory')
        for validation in validations.values():
            if validation['fixture_sha256'] != reference_run['fixture_sha256']:
                raise ValueError('query input bytes differ across builds')
            if validation['case_inventory'] != inventory or validation['checked_values'] != CHECKED_VALUES:
                raise ValueError('reference validation omitted workloads')
        prior_reference = out / 'prior-reference.npz'
        run('prior', 'reference-prior', '--check-only', '--write-reference', prior_reference)
        exact_validation = run('candidate', 'validation-exact-prior', '--check-only',
                               '--reference', prior_reference, '--exact-reference')
        if (not exact_validation['exact_reference'] or exact_validation['checked_values'] != CHECKED_VALUES
                or exact_validation['case_inventory'] != inventory):
            raise ValueError('Native56 control vs candidate workload validation did not run exactly')
        # Retain both golden references. A failed later child must remain auditable.
        source_validations = {'original': reference_run, **validations}
        prepared = {'input_snapshots':reference_run['input_snapshots'],'source_validations': source_validations, 'inventory': inventory,
                    'exact_validation': exact_validation, 'commands': commands,
                    'threads': threads, 'reference_sha256': hashlib.sha256(reference.read_bytes()).hexdigest(),
                    'prior_reference_sha256': hashlib.sha256(prior_reference.read_bytes()).hexdigest()}
        verify_inputs(prepared,args.output)
        prepared_path.write_text(json.dumps(prepared, indent=2)+'\n')
        return prepared
    if not prepared_path.is_file():
        raise ValueError('all thread-setting references must be prepared before timing')
    prepared = json.loads(prepared_path.read_text())
    verify_inputs(prepared,args.output)
    if (prepared['threads'] != threads
            or prepared['reference_sha256'] != hashlib.sha256(reference.read_bytes()).hexdigest()
            or prepared['prior_reference_sha256'] != hashlib.sha256((out/'prior-reference.npz').read_bytes()).hexdigest()):
        raise ValueError('prepared reference or thread setting changed')
    commands.extend(prepared['commands'])
    source_validations = prepared['source_validations']
    validations = {side: source_validations[side] for side in ('prior', 'candidate')}
    inventory = prepared['inventory']
    exact_validation = prepared['exact_validation']
    prior_reference = out/'prior-reference.npz'
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
                golden = reference if side == 'original' else prior_reference
                child = run(side, label, '--reference', golden, '--exact-reference', selected=name)
                origin = source_validations[side]
                for key in ('fixture_sha256','output_sha256','fixture_coverage'):
                    if child[key] != {name:origin[key][name]}:
                        raise ValueError('selected child input/output digest differs: '+key)
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
             f"Each workload checked before timing: {first['checked_values']:,} numeric values; exact schema/null/NaN positions; original real-control tolerance rtol=atol=1e-10; all integer outputs compare exactly. Native56 control vs candidate workloads pass exact values/signed-zero checks; every timed child checks against its own arm golden before warmups and final collected output after samples.",
             '', '| Query | Original ms | Native56 control ms | ADD initialized-output candidate ms | Original C / candidate (envelope) | Native56 control / candidate (envelope) |',
             '| --- | ---: | ---: | ---: | --- | --- |']
    for name, pair in comparisons['original_vs_candidate'].items():
        zc = comparisons['prior_vs_candidate'][name]
        oz = comparisons['original_vs_prior'][name]
        lo, hi = pair['ratio_envelope']; zl, zh = zc['ratio_envelope']
        lines.append(f"| {name} | {pair['baseline_median_ms']:.4f} | {oz['candidate_median_ms']:.4f} | {pair['candidate_median_ms']:.4f} | {pair['median_paired_ratio']:.2f}x ({lo:.2f}–{hi:.2f}) | {zc['median_paired_ratio']:.2f}x ({zl:.2f}–{zh:.2f}) |")
    lines += ['', 'Process minor faults per query (median of process medians; includes Polars/Python/allocator activity, not allocator-only attribution):',
              '', '| Query | Original | Native56 control | ADD initialized-output candidate |', '| --- | ---: | ---: | ---: |']
    for name in comparisons['original_vs_candidate']:
        vals = [faults[name][side]['minor_faults'] for side in SIDES]
        lines.append('| '+name+' | '+' | '.join('unavailable' if v is None else str(v['median']) for v in vals)+' |')
    (out/'comparison.md').write_text('\n'.join(lines)+'\n')
    return metadata, lines


def run_all_settings(args, affinity):
    # validate-only prepared BOTH settings and full API corpus before any timer.
    verify_validation(args)
    reports = {}
    sections = []
    for threads in args.thread_counts:
        reports[str(threads)], lines = run_setting(args, threads, affinity)
        sections.extend(lines+[''])
    return reports, sections


def script_records():
    files = ('add_output_benchmark.py','add_output_provenance.py','add_output_inputs.py','add_output_query.py',
             'add_output_cases.json','migration_probe.py','migration_ci_benchmark.py','api.json')
    return {name: sha256(Path(__file__).with_name(name)) for name in files}


def record_build(args):
    if args.candidate_commit in (ORIGINAL_COMMIT, PRIOR_COMMIT):
        raise ValueError('the candidate must have its own immutable source pin')
    pins = {'original':ORIGINAL_COMMIT,'prior':PRIOR_COMMIT,'candidate':args.candidate_commit}
    identities = {side: identity(getattr(args, side+'_python')) for side in SIDES}
    runtime = validate_identities(identities)
    builds = {side: {'source': source_record(getattr(args,side+'_source'), pins[side]),
                     'identity':identities[side],
                     'wheel':wheel_record(args.wheel_dir/side, identities[side])} for side in SIDES}
    for side,build in builds.items():
        retained={}
        for name,digest in build['identity']['native_files'].items():
            destination=args.output/'actual-native'/side/Path(name).name
            destination.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(name,destination)
            if sha256(destination)!=digest: raise ValueError('actual native copy differs from measured wheel')
            retained[str(destination)]=digest
        build['retained_native_files']=retained
        build['product_elf']=[elf_record(path) for path in retained]
    result = {'builds':builds,'runtime':runtime,'flags':flags_record(),'scripts':script_records(),
              'cases':requested_inventory(),'orders':ORDERS,'rounds':12,
              'release_flags':'maturin build --release --locked; sequential portable builds, identical environment',
              'labels':LABELS}
    (args.output/'build-provenance.json').write_text(json.dumps(result,indent=2)+'\n')
    return result


def verify_build(args):
    result = json.loads((args.output/'build-provenance.json').read_text())
    if result['scripts'] != script_records() or result['flags'] != flags_record():
        raise ValueError('controller or release environment changed')
    pins = {'original':ORIGINAL_COMMIT,'prior':PRIOR_COMMIT,'candidate':args.candidate_commit}
    if result['cases'] != requested_inventory() or result['rounds'] != 12:
        raise ValueError('build inventory changed')
    for side, row in result['builds'].items():
        if row['source'] != source_record(getattr(args,side+'_source'), pins[side]):
            raise ValueError('source changed after build: '+side)
        if row['wheel'] != wheel_record(args.wheel_dir/side, row['identity']):
            raise ValueError('preserved wheel changed: '+side)
        if row['product_elf'] != [elf_record(path) for path in row['retained_native_files']]:
            raise ValueError('actual product ELF binding changed: '+side)
        if any(sha256(path) != digest for path,digest in {**row['identity']['native_files'],**row['retained_native_files']}.items()):
            raise ValueError('installed native extension changed: '+side)
    if set(result['builds']) != set(SIDES):
        raise ValueError('build arm inventory changed')
    validate_identities({side:row['identity'] for side,row in result['builds'].items()})
    return result


def corpus_gate(output):
    folder = output/'corpus'; reports = {}
    for name, exact in (('prior-vs-candidate-exact',True),('original-vs-prior',False),('original-vs-candidate',False)):
        report = json.loads((folder/(name+'.json')).read_text())
        if (report['require_exact'] != exact or report['cases'] != 10624 or report['checked_values'] != 2167654
                or report['failures'] or not report['api_call_contract_match']):
            raise ValueError('full API corpus failed or was underchecked: '+name)
        if exact and (report['fields_with_bit_differences'] or report['max_absolute_difference'] != 0):
            raise ValueError('Native56 control/candidate corpus is not exact')
        for arm in ('baseline','candidate'):
            if sha256(folder/Path(report[arm]).name) != report[arm+'_sha256']:
                raise ValueError('full corpus capture changed')
        reports[name] = report
    return reports


def case_values(name):
    family,layout=name.split('/')
    shape=layout.removesuffix('_interleaved')
    rows=math.prod(map(int,shape.split('x'))) if 'x' in shape else int(shape)
    return rows


def validate_report(row, side, threads, provenance, selected=None):
    build = provenance['builds'][side]
    if row['commit'] != build['source']['commit'] or row['source_sha256'] != build['source']['source_sha256']:
        raise ValueError('query source differs from pinned build')
    if row['native_binary_sha256'] not in build['identity']['native_files'].values():
        raise ValueError('query native binary differs from wheel')
    for key in ('python','platform','polars','numpy','package','talib'):
        if row[key] != build['identity'][key]:
            raise ValueError('query runtime changed: '+key)
    if (row['threads'] != threads or row['repeats'] != 31 or row['warmups'] != 5 or row['diagnostic']
            or len(set(row['affinity'])) != threads or row['rust'] != provenance['flags']['rustc'].splitlines()[0]
            or not row['integer_reference_exact']):
        raise ValueError('query protocol/runtime configuration changed')
    wanted = [selected] if selected else requested_inventory()
    if any(set(row.get(key,{}))!=set(wanted) for key in ('fixture_sha256','output_sha256','fixture_coverage')):
        raise ValueError('query input/output digest scope differs')
    if row['case_inventory'] != wanted or row['case_filters'] != wanted:
        raise ValueError('query inventory differs from exact selector')
    if selected:
        selected_inventory(row, wanted)
        if not row.get('final_output_checked'):
            raise ValueError('timed child must recheck final collected output')
        if not row['exact_reference'] or row['checked_values'] != case_values(selected):
            raise ValueError('timed child must check every value against its arm golden exactly')
        for entry in row['results'].values():
            samples=entry['samples_ms']
            if (len(samples)!=31 or any(isinstance(x,bool) or not isinstance(x,(int,float)) or not math.isfinite(x) or x<=0 for x in samples)
                    or entry['median_ms']!=statistics.median(samples)):
                raise ValueError('invalid raw latency samples or process median')
            for key in ('minor_faults','major_faults'):
                counters=entry[key]
                if len(counters)!=31 or any(isinstance(x,bool) or not isinstance(x,int) or x<0 for x in counters):
                    raise ValueError('invalid raw process fault samples')
    elif row['results']:
        raise ValueError('global validation must not time any queries')


def validate_all(args):
    provenance = verify_build(args); folder=args.output/'corpus';folder.mkdir(exist_ok=True)
    probe = Path(__file__).with_name('migration_probe.py').resolve()
    with (folder/'commands.jsonl').open('w') as commands:
        def execute(command, label):
            commands.write(json.dumps(command)+'\n');commands.flush()
            with (folder/(label+'.log')).open('w') as log:
                subprocess.run(command,check=True,stdout=log,stderr=subprocess.STDOUT)
        for side in SIDES:
            execute([str(getattr(args,side+'_python').absolute()),str(probe),'--capture',str(folder/(side+'.npz'))],side)
        for before,after,exact in (('prior','candidate',True),('original','prior',False),('original','candidate',False)):
            name=before+'-vs-'+after+('-exact' if exact else '')
            command=[str(args.candidate_python.absolute()),str(probe),'--compare',str(folder/(before+'.npz')),
                     str(folder/(after+'.npz')),'--report',str(folder/(name+'.json'))]
            if exact: command.append('--exact')
            execute(command,name)
    reports=corpus_gate(args.output)
    previous=set(os.sched_getaffinity(0));prepared={}
    try:
        for threads in (1,4):
            if len(previous)<threads: raise ValueError('insufficient CPU affinity')
            prepared[str(threads)]=run_setting(args,threads,previous,prepare_only=True)
    finally: os.sched_setaffinity(0,previous)
    verify_build(args)
    record={'all_checks_completed_before_any_timing':True,'corpus':reports,
            'prepared_sha256':{str(t):sha256(args.output/f'threads-{t}'/'prepared-validation.json') for t in (1,4)},
            'build_provenance_sha256':sha256(args.output/'build-provenance.json'),
            'cases':requested_inventory(),'checked_values_per_setting':CHECKED_VALUES}
    (args.output/'validation-complete.json').write_text(json.dumps(record,indent=2)+'\n')
    return record


def verify_inputs(prepared,output):
    expected=prepared['source_validations']['original']['fixture_sha256']
    if set(expected)!=set(requested_inventory()):raise ValueError('raw input scope differs')
    if validate_inputs(output/'inputs',prepared['input_snapshots'],expected)!=5:
        raise ValueError('exactly five physical layouts must be retained')


def verify_validation(args):
    verify_build(args); corpus_gate(args.output)
    record=json.loads((args.output/'validation-complete.json').read_text())
    if (not record['all_checks_completed_before_any_timing'] or record['cases'] != requested_inventory()
            or record['checked_values_per_setting'] != CHECKED_VALUES
            or record['build_provenance_sha256'] != sha256(args.output/'build-provenance.json')):
        raise ValueError('validation does not cover these builds/inventory')
    for threads in (1,4):
        folder=args.output/f'threads-{threads}'
        if sha256(folder/'prepared-validation.json') != record['prepared_sha256'][str(threads)]:
            raise ValueError('prepared query validation changed')
        prepared=json.loads((folder/'prepared-validation.json').read_text())
        verify_inputs(prepared,args.output)
        for name,key in (('reference.npz','reference_sha256'),('prior-reference.npz','prior_reference_sha256')):
            if sha256(folder/name) != prepared[key]: raise ValueError('query golden changed')
    return record


def write_negatives(metadata, output):
    negatives=[]
    for threads,data in metadata['results'].items():
        for comparison,rows in data['comparisons'].items():
            for case,row in rows.items():
                percent=(row['candidate_median_ms']/row['baseline_median_ms']-1)*100
                row['after_latency_percent']=percent
                row['after_faster_rounds']=sum(r>1 for r in row['paired_ratios'])
                if percent>0: negatives.append({'threads':int(threads),'comparison':comparison,'case':case,**row})
    (output/'negative-cases.json').write_text(json.dumps(negatives,indent=2)+'\n')
    lines=['# Every slower pairwise median','','All three pairwise comparisons and controls are included. Envelopes are descriptive, not confidence intervals.','',
           '| Threads | Comparison | Case | Latency increase | Before/after envelope | Faster rounds |',
           '| ---: | --- | --- | ---: | --- | ---: |']
    for row in sorted(negatives,key=lambda r:(r['threads'],-r['after_latency_percent'])):
        lo,hi=row['ratio_envelope']
        lines.append(f"| {row['threads']} | {row['comparison']} | {row['case']} | +{row['after_latency_percent']:.3f}% | {lo:.4f}–{hi:.4f} | {row['after_faster_rounds']}/12 |")
    (output/'negative-cases.md').write_text('\n'.join(lines)+'\n')
    (output/'summary.json').write_text(json.dumps(metadata,indent=2)+'\n')

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for side in SIDES:
        parser.add_argument(f'--{side}-python', type=Path, required=True)
        parser.add_argument(f'--{side}-source', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--thread-counts', nargs='+', type=int, default=[1, 4])
    parser.add_argument('--candidate-commit', required=True)
    parser.add_argument('--wheel-dir',type=Path,required=True)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--record-build',action='store_true')
    mode.add_argument('--validate-only',action='store_true')
    parser.add_argument('--rounds', type=int, default=12)
    parser.add_argument('--repeats', type=int, default=31)
    args = parser.parse_args()
    if args.rounds != 12 or args.repeats != 31 or args.thread_counts != [1,4]:
        parser.error('requires 12 rounds, 31 samples and exactly thread settings 1 4')
    if len(set(args.thread_counts)) != len(args.thread_counts):
        parser.error('thread settings must be unique')
    args.output = args.output.resolve(); args.wheel_dir = args.wheel_dir.resolve()
    args.output.mkdir(parents=True, exist_ok=True)
    if args.record_build:
        record_build(args); return
    if args.validate_only:
        validate_all(args); return
    verify_validation(args)
    affinity = set(os.sched_getaffinity(0)) if hasattr(os, 'sched_getaffinity') else None
    try:
        reports, sections = run_all_settings(args, affinity)
    finally:
        if affinity is not None:
            os.sched_setaffinity(0, affinity)
    env = os.environ
    metadata = {'run_url': f"{env.get('GITHUB_SERVER_URL','https://github.com')}/{env.get('GITHUB_REPOSITORY','local')}/actions/runs/{env.get('GITHUB_RUN_ID','local')}",
                'runner_image': env.get('ImageOS'), 'runner_image_version': env.get('ImageVersion'),
                'platform': platform.platform(), 'thread_counts': args.thread_counts,
                'results': reports}
    (args.output/'summary.json').write_text(json.dumps(metadata, indent=2)+'\n')
    metadata['build_provenance'] = verify_build(args)
    metadata['validation'] = verify_validation(args)
    (args.output/'summary.json').write_text(json.dumps(metadata, indent=2)+'\n')
    first = next(iter(reports.values()))
    lines = ['# Consumer ADD initialized-output construction', '',
             *[f'{side}: `{first["commits"][side]}`' for side in SIDES], '',
             f"{first['cpu']}; {first['platform']}; Python {first['python']}, Polars {first['polars']}, NumPy {first['numpy']}; {first['rust']}.",
             f'{args.rounds} fresh processes per CASE/build/thread setting; all six build-order permutations; {args.repeats} samples after five warmups. No sibling query runs before the selected case.',
             'Ratios use matched-round medians. Envelopes span min(before medians)/max(after medians) to max(before)/min(after).',
             'These are descriptive ranges, not confidence intervals. Shared-host contention, frequency and placement remain uncontrolled.',
             'getrusage counters are process totals sampled outside the latency interval; they do not isolate jemalloc or kernel faults.',
             'Only direct expressions and ordinary native Polars .over() are measured. No new grouping expression/list composition.',
             'The fixed inventory has five ADD workloads, five SUB and three MULT ineligible-path controls, and two pure Polars controls. No broader case expansion.', '',
             *sections]
    (args.output/'comparison.md').write_text('\n'.join(lines)+'\n')
    write_negatives(metadata, args.output)
    print('\n'.join(lines), flush=True)


if __name__ == '__main__':
    main()
