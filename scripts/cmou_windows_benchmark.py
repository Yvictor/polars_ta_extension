"""Original C / delivered56 / finale79 / CMOU checked-windows candidate comparison on one CI runner.

Builds happen in the workflow, never during measurements. Every thread setting
uses one fresh process per case and round, balanced four-arm Williams orders, workload
correctness checks, raw samples and descriptive process-noise ranges.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import os
from pathlib import Path
import platform
import statistics
import shutil
import subprocess
import time

from migration_ci_benchmark import percentile, summarize
from cmou_windows_inputs import validate as validate_input_snapshots

SIDES = ('original', 'prior', 'combined', 'candidate')
COMBINED_COMMIT = 'e79ac0785436bbf3ba4c411d80936f8dd4ecfa24'
CANDIDATE_HELPER_SHA256 = 'eee8484a6079f910db657a3645b205edd78c9e0b0f17c7cfb0aadb771cceabaf'
BASELINE_HELPER_SHA256 = '9f6bba75ade6df5d05d68ad225f8855028260d475d591aa29723cd8f75f5b202'
PUBLIC_PROBE_SHA256 = '3766b64d0c9dc6fcc55d4648824b2b679ecbc96cc09f3d5ec086cba71e63398c'
ORIGINAL_COMMIT = 'b2bbc26d41ec80823c8bffb0cc436a97f29911cc'
PRIOR_COMMIT = '56f6d5fb139031c20d86d7e818e7d267eb834295'
NATIVE_SIDES = ('prior', 'combined', 'candidate')
LABELS = {'original':'Original C081', 'prior':'Delivered56', 'combined':'Finale79', 'candidate':'CMOU checked-windows candidate'}
MANIFEST = Path(__file__).with_name('cmou_windows_cases.json')
CASES = tuple(json.loads(MANIFEST.read_text())['cases'])
CHECKED_VALUES = 9_401_000
CANDIDATE_COMMIT = "36a6f5dfded2330fe6df550ac3570546882e01ca"
CHILD_TIMEOUT_SECONDS = 120
MEASUREMENT_BUDGET_SECONDS = 7200
from cmou_windows_provenance import sha256, source_record, identity, wheel_record, flags_record, validate_identities, elf_record
from cmou_windows_codegen import inspect as inspect_cmou_elf
ORDERS = (
    ('original','prior','combined','candidate'),
    ('prior','candidate','original','combined'),
    ('candidate','combined','prior','original'),
    ('combined','original','candidate','prior'),
)
PAIRS = {a+'_vs_'+b:(a,b) for i,a in enumerate(SIDES) for b in SIDES[i+1:]}


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
    comparisons = {key:summarize(runs[a],runs[b]) for key,(a,b) in PAIRS.items()}
    faults = {name: {side: {counter: fault_summary(runs[side], name, counter)
                            for counter in ('minor_faults', 'major_faults')}
                     for side in SIDES} for name in comparisons['original_vs_candidate']}
    return comparisons, faults


def requested_inventory(diagnostic=False, filters=()):
    manifest = json.loads(MANIFEST.read_text())
    names = manifest['cases']
    if diagnostic or filters or len(names) != 12 or len(set(names)) != 12 or manifest['checked_values'] != CHECKED_VALUES or manifest['timed_children'] != 1152 or manifest['timed_samples'] != 35712 or manifest['child_timeout_seconds'] != CHILD_TIMEOUT_SECONDS or manifest['measurement_budget_seconds'] != MEASUREMENT_BUDGET_SECONDS:
        raise ValueError('fixed reviewed 12-case inventory may not be filtered or expanded')
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
    out=args.output.resolve()/f'threads-{threads}';out.mkdir(parents=True,exist_ok=True)
    if affinity is not None:os.sched_setaffinity(0,sorted(affinity)[:threads])
    env=os.environ.copy();env.update(POLARS_MAX_THREADS=str(threads),OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1')
    provenance=verify_build(args);script=Path(__file__).with_name('cmou_windows_query.py').resolve();commands=[]
    golden={side:out/('reference.npz' if side=='original' else side+'-reference.npz') for side in SIDES}

    def run(side,label,*extra,selected=None):
        command=[str(getattr(args,side+'_python').absolute()),str(script),'--source-root',str(getattr(args,side+'_source').resolve()),
                 '--output',str(out/(label+'.json')),'--label',label,'--repeats',str(args.repeats),*map(str,extra)]
        for name in ([selected] if selected is not None else requested_inventory()):command+=['--case-filter',name]
        commands.append(command)
        with(out/'commands.jsonl').open('a')as f:f.write(json.dumps({'label':label,'side':side,'selected_case':selected,'argv':command,'polars_threads':threads})+'\n')
        print(f'{time.strftime("%H:%M:%S")} threads={threads} {label} {selected or "validation"}',flush=True)
        timeout=CHILD_TIMEOUT_SECONDS
        if selected is not None and getattr(args,'measurement_deadline',None)is not None:
            remaining=args.measurement_deadline-time.monotonic()
            if remaining<=0:raise ValueError('measurement budget exhausted; partial evidence is incomplete')
            timeout=min(timeout,remaining)
        with(out/(label+'.stdout.log')).open('w')as stdout,(out/(label+'.stderr.log')).open('w')as stderr:
            try:subprocess.run(command,env=env,check=True,stdout=stdout,stderr=stderr,timeout=timeout)
            except(subprocess.TimeoutExpired,subprocess.CalledProcessError)as failure:
                (out/(label+'-failure.json')).write_text(json.dumps({'label':label,'side':side,'case':selected,'argv':command,'timeout_seconds':timeout,'error':type(failure).__name__,'partial_logs_preserved':True,'partial_campaign_is_not_success':True},indent=2));raise
        result=json.loads((out/(label+'.json')).read_text());validate_report(result,side,threads,provenance,selected);return result

    prepared_path=out/'prepared-validation.json'
    if prepare_only:
        origins={};exact_validations={}
        for side in SIDES:
            extra=['--check-only','--write-reference',golden[side]]
            if side=='original' and threads==1:extra+=['--preserve-inputs',args.output/'raw-inputs']
            if side!='original':extra+=['--reference',golden['original']]
            origins[side]=run(side,'reference-'+side,*extra)
        reference=origins['original'];inventory=requested_inventory()
        for side,row in origins.items():
            if row['case_inventory']!=inventory or row['fixture_sha256']!=reference['fixture_sha256']:raise ValueError('global inventory or physical inputs differ')
            if side!='original' and row['checked_values']!=CHECKED_VALUES:raise ValueError('C query comparison omitted values')
        for key,(before,after)in PAIRS.items():
            if before=='original':continue
            row=run(after,'validation-exact-'+before+'-'+after,'--check-only','--reference',golden[before],'--exact-reference')
            if not row['exact_reference'] or row['checked_values']!=CHECKED_VALUES or row['case_inventory']!=inventory:raise ValueError('native exact query comparison incomplete')
            exact_validations[key]=row
        prepared={'source_validations':origins,'inventory':inventory,'exact_validations':exact_validations,'commands':commands,'threads':threads,
                  'golden_sha256':{side:sha256(path)for side,path in golden.items()}}
        prepared_path.write_text(json.dumps(prepared,indent=2)+'\n');return prepared
    if not prepared_path.is_file():raise ValueError('all thread-setting goldens must precede timing')
    prepared=json.loads(prepared_path.read_text())
    if prepared['threads']!=threads or prepared['inventory']!=requested_inventory() or prepared['golden_sha256']!={side:sha256(path)for side,path in golden.items()}:raise ValueError('prepared inventory/goldens/threads changed')
    origins=prepared['source_validations'];commands.extend(prepared['commands']);comparisons={key:{}for key in PAIRS};faults={};order=[];processes=[]
    for case_index,name in enumerate(prepared['inventory']):
        runs={side:[]for side in SIDES}
        for index in range(args.rounds):
            for side in ORDERS[index%len(ORDERS)]:
                label=f'case-{case_index+1:03d}-{side}-{index+1}';order.append(label)
                child=run(side,label,'--reference',golden[side],'--exact-reference',selected=name);origin=origins[side]
                for key in ('fixture_sha256','output_sha256','fixture_coverage'):
                    if child[key]!={name:origin[key][name]}:raise ValueError('selected input/output/coverage changed: '+key)
                for key in ('commit','source_sha256','native_binary_sha256','talib','python','platform','cpu','polars','numpy','rust','profile','threads','affinity'):
                    if child[key]!=origin[key]:raise ValueError('child source/runtime changed: '+key)
                runs[side].append(child);processes.append({'case':name,'side':side,'round':index+1,'report':label+'.json'})
        case_comparisons,case_faults=analyze(runs,args.repeats,threads)
        for key,values in case_comparisons.items():
            if set(values)!={name}or name in comparisons[key]:raise ValueError('case comparison inventory drift')
            comparisons[key].update(values)
        faults.update(case_faults)
    first=origins['candidate'];metadata={key:first[key]for key in('cpu','platform','python','polars','numpy','rust','threads','affinity','repeats','warmups','diagnostic','checked_values','case_filters')}
    metadata.update(commits={s:origins[s]['commit']for s in SIDES},source_sha256={s:origins[s]['source_sha256']for s in SIDES},native_binary_sha256={s:origins[s]['native_binary_sha256']for s in SIDES},
                    rounds=args.rounds,order=order,commands=commands,case_inventory=prepared['inventory'],process_isolation='one case per fresh process',processes=processes,golden_sha256=prepared['golden_sha256'],comparisons=comparisons,faults=faults)
    lines=[f'## {threads} thread(s)','',f"Each arm/thread golden contains {CHECKED_VALUES:,} values; C tolerance rtol=atol=1e-10 with strict both-zero signs; all native values/signs exact. Own-arm full outputs checked before warmups and after samples.",
           'All six pairwise comparisons and every control retained. Ratios/envelopes are before/after (>1 favors later arm); descriptive ranges, not confidence intervals.','',
           '| Query | Comparison | Before ms | After ms | Paired before/after | Envelope | Faster rounds |','| --- | --- | ---: | ---: | ---: | --- | ---: |']
    for name in prepared['inventory']:
        for key in PAIRS:
            row=comparisons[key][name];lo,hi=row['ratio_envelope']
            lines.append(f"| {name} | {key} | {row['baseline_median_ms']:.5f} | {row['candidate_median_ms']:.5f} | {row['median_paired_ratio']:.5f} | {lo:.5f}–{hi:.5f} | {sum(x>1 for x in row['paired_ratios'])}/12 |")
    (out/'summary.json').write_text(json.dumps(metadata,indent=2)+'\n');(out/'comparison.md').write_text('\n'.join(lines)+'\n');return metadata,lines


def run_all_settings(args, affinity):
    # validate-only prepared BOTH settings and full API corpus before any timer.
    verify_validation(args)
    args.measurement_deadline=time.monotonic()+MEASUREMENT_BUDGET_SECONDS
    reports = {}
    sections = []
    for threads in args.thread_counts:
        reports[str(threads)], lines = run_setting(args, threads, affinity)
        sections.extend(lines+[''])
    return reports, sections


def script_records():
    files = ('cmou_windows_benchmark.py','cmou_windows_provenance.py','cmou_windows_query.py',
             'cmou_windows_cases.json','cmou_windows_inputs.py','cmou_windows_codegen.py','cmou_windows_cfg.py','CMOU_WINDOWS_CI.md','migration_probe.py','migration_ci_benchmark.py','api.json')
    records={name:sha256(Path(__file__).with_name(name))for name in files}
    for relative in('tests/test_cmou_windows_benchmark.py','.github/workflows/cmou-windows.yml'):
        records[relative]=sha256(Path(__file__).resolve().parents[1]/relative)
    return records


def native_source_boundary(args):
    """This fixed candidate changes only the reviewed CMOU helper, never routing."""
    def records(root):
        root=Path(root).resolve();result={}
        for p in sorted(root.rglob('*')):
            if not p.is_file():continue
            rel=p.relative_to(root)
            if {'.git','target','.venv','__pycache__'}.intersection(rel.parts):continue
            if p.suffix not in ('.rs','.py') and p.name not in ('Cargo.toml','Cargo.lock'):continue
            if rel.parts[0] not in ('src','python') and len(rel.parts)>1:continue
            result[str(rel)]=sha256(p)
        return result
    before=records(args.combined_source);after=records(args.candidate_source)
    changed={name for name in set(before)|set(after) if before.get(name)!=after.get(name)}
    if changed!={'src/compat/cmou.rs'}:
        raise ValueError('candidate must change only the reviewed CMOU helper')
    required={'src/native.rs','src/compat.rs','src/compat/guarded.rs','src/generated.rs','src/params.rs','src/missing.rs','src/utils.rs','Cargo.toml','Cargo.lock'}
    if not required.issubset(before) or not required.issubset(after):
        raise ValueError('native routing source boundary is incomplete')
    if before['src/compat/cmou.rs']!=BASELINE_HELPER_SHA256:
        raise ValueError('e79 CMOU helper differs from the reviewed baseline')
    if after['src/compat/cmou.rs']!=CANDIDATE_HELPER_SHA256:
        raise ValueError('candidate CMOU helper differs from its independently reviewed source')
    return {'changed_files':sorted(changed),'routing_sources':{name:before[name] for name in sorted(required)},
            'helper_before':before['src/compat/cmou.rs'],'helper_after':after['src/compat/cmou.rs']}


def fixed_pins(candidate):
    if candidate!=CANDIDATE_COMMIT or not re.fullmatch('[0-9a-f]{40}',candidate) or not re.fullmatch('[0-9a-f]{64}',CANDIDATE_HELPER_SHA256) or not re.fullmatch('[0-9a-f]{64}',PUBLIC_PROBE_SHA256):
        raise ValueError('candidate commit/helper must match reviewed immutable pins')
    pins={'original':ORIGINAL_COMMIT,'prior':PRIOR_COMMIT,'combined':COMBINED_COMMIT,'candidate':candidate}
    if len(set(pins.values()))!=4:raise ValueError('four distinct immutable source pins required')
    return pins



def workflow_pins(environment):
    pins=fixed_pins(environment.get('CANDIDATE_COMMIT',''))
    if any(environment.get(side.upper()+'_COMMIT')!=pin for side,pin in pins.items()):
        raise ValueError('workflow product pins differ from frozen controller')
    if (environment.get('CANDIDATE_HELPER_SHA256')!=CANDIDATE_HELPER_SHA256
            or environment.get('PUBLIC_PROBE_SHA256')!=PUBLIC_PROBE_SHA256):
        raise ValueError('workflow helper/probe pins differ from frozen controller')
    return pins

def record_build(args):
    pins=fixed_pins(args.candidate_commit)
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
        build['cmou_codegen']=[inspect_cmou_elf(path,args.output/'normal-codegen'/side,side) for path in retained] if side!='original' else []
    result = {'builds':builds,'runtime':runtime,'flags':flags_record(),'scripts':script_records(),
              'native_source_boundary':native_source_boundary(args),
              'cases':requested_inventory(),'orders':ORDERS,'rounds':12,
              'release_flags':'maturin build --release --locked; sequential portable builds, identical environment',
              'labels':LABELS}
    (args.output/'build-provenance.json').write_text(json.dumps(result,indent=2)+'\n')
    return result



def verify_codegen_proof(proof,side,retained):
    expected=[0,0]if side=='candidate'else[3,3]
    if (side not in NATIVE_SIDES or proof.get('side')!=side or proof.get('gate')is not True
            or retained.get(proof.get('binary'))!=proof.get('binary_sha256')
            or proof['guards']['normal_iteration_guard_counts']!=expected
            or proof['output_loop']['bounds_panic_reachable']!=(side!='candidate')
            or proof['output_loop']['unknown_exit_or_call_reachable']
            or proof['output_loop']not in proof['analysis']['cyclic_cfgs']):
        raise ValueError('codegen proof not measured wheel or expected normal-loop gate')
    files=proof['files'];names={'symbols.txt','segments.txt','relocations.txt','cmou.asm','report.json'}
    if len(files)!=5 or {Path(p).name for p in files}!=names or len({str(Path(p).parent)for p in files})!=1:
        raise ValueError('retained codegen file scope differs')
    if any(Path(path).is_symlink()or sha256(path)!=digest for path,digest in files.items()):raise ValueError('retained codegen proof changed')
    report=next(Path(p)for p in files if Path(p).name=='report.json')
    if json.loads(report.read_text())!={k:v for k,v in proof.items()if k!='files'}:
        raise ValueError('retained codegen report metadata differs')

def verify_build(args):
    result = json.loads((args.output/'build-provenance.json').read_text())
    if result['native_source_boundary']!=native_source_boundary(args):
        raise ValueError('native routing source boundary changed')
    if result['scripts'] != script_records() or result['flags'] != flags_record():
        raise ValueError('controller or release environment changed')
    pins=fixed_pins(args.candidate_commit)
    if result['cases'] != requested_inventory() or result['rounds'] != 12:
        raise ValueError('build inventory changed')
    for side, row in result['builds'].items():
        if row['source'] != source_record(getattr(args,side+'_source'), pins[side]):
            raise ValueError('source changed after build: '+side)
        if row['wheel'] != wheel_record(args.wheel_dir/side, row['identity']):
            raise ValueError('preserved wheel changed: '+side)
        if row['product_elf'] != [elf_record(path) for path in row['retained_native_files']]:
            raise ValueError('actual product ELF binding changed: '+side)
        if side!='original':
            if len(row.get('cmou_codegen',[]))!=1:raise ValueError('CMOU normal codegen proof missing')
            verify_codegen_proof(row['cmou_codegen'][0],side,row['retained_native_files'])
        if any(sha256(path) != digest for path,digest in {**row['identity']['native_files'],**row['retained_native_files']}.items()):
            raise ValueError('installed native extension changed: '+side)
    if set(result['builds']) != set(SIDES):
        raise ValueError('build arm inventory changed')
    validate_identities({side:row['identity'] for side,row in result['builds'].items()})
    return result


def corpus_gate(output):
    folder = output/'corpus'; reports = {}
    for before,after in PAIRS.values():
        exact=before!='original'
        name=before+'-vs-'+after+('-exact' if exact else '')
        report = json.loads((folder/(name+'.json')).read_text())
        if (report['require_exact'] != exact or report['cases'] != 10624 or report['checked_values'] != 2167654
                or report['failures'] or not report['api_call_contract_match']):
            raise ValueError('full API corpus failed or was underchecked: '+name)
        if exact and (report['fields_with_bit_differences'] or report['max_absolute_difference'] != 0):
            raise ValueError('Native56 control/candidate corpus is not exact')
        for arm,side in [('baseline',before),('candidate',after)]:
            if Path(report[arm]).name!=side+'.npz' or sha256(folder/(side+'.npz')) != report[arm+'_sha256']:
                raise ValueError('full corpus capture changed')
        reports[name] = report
    return reports



def public_probe_gate(output,provenance):
    """Bind all public captures/comparisons to the frozen untimed source-owned probe."""
    import numpy as np
    folder=output/'cmou-public';probe=folder/'cmou_window_probe.py'
    if sha256(probe)!=PUBLIC_PROBE_SHA256:raise ValueError('frozen public probe changed')
    metadata={};reports={}
    for side in SIDES:
        with np.load(folder/(side+'.npz'),allow_pickle=False)as capture:
            row=json.loads(str(capture['metadata']));cases=row['cases']
            if len(cases)!=1984 or sum('error'in r for r in cases.values())!=408 or sum(r['rows']for r in cases.values()if'error'not in r)!=147220:
                raise ValueError('public CMOU capture inventory changed')
        identity=provenance['builds'][side]['identity']
        if row['native_sha256']not in identity['native_files'].values()or any(row[k]!=identity[k]for k in('polars','numpy','talib')):
            raise ValueError('public capture product/runtime differs')
        if set(row['input_sha256'])!=set(cases):raise ValueError('public input fingerprint scope differs')
        metadata[side]=row
    for before,after in PAIRS.values():
        exact=before!='original';name=before+'-vs-'+after+('-exact'if exact else'')
        row=json.loads((folder/(name+'.json')).read_text())
        if row['cases']!=1984 or row['checked_values']!=147220 or row['exact']is not exact or row['zero_sign_policy']!='both-zero exact' or row['nan_payload_policy']!='positions exact; NaN sign/payload excluded':
            raise ValueError('public CMOU comparison incomplete')
        difference=row['max_absolute_difference']
        if isinstance(difference,bool) or not isinstance(difference,(int,float)) or not math.isfinite(difference) or difference<0:raise ValueError('invalid public numerical comparison')
        if exact and difference!=0:raise ValueError('native public CMOU comparison is not exact')
        if metadata[before]['input_sha256']!=metadata[after]['input_sha256']:raise ValueError('public physical inputs differ')
        for key,side in(('baseline',before),('candidate',after)):
            if row[key]!=side or row[key+'_sha256']!=sha256(folder/(side+'.npz')):raise ValueError('public capture binding differs')
        reports[name]=row
    return reports


def run_public_validation(args,provenance):
    folder=args.output/'cmou-public';folder.mkdir(exist_ok=True)
    source=Path(args.candidate_source)/'tests/cmou_window_probe.py'
    if sha256(source)!=PUBLIC_PROBE_SHA256:raise ValueError('source-owned public probe differs from reviewed script')
    probe=folder/'cmou_window_probe.py';shutil.copyfile(source,probe)
    with(folder/'commands.jsonl').open('w')as commands:
        def execute(command,label):
            commands.write(json.dumps(command)+'\n');commands.flush()
            with(folder/(label+'.stdout.log')).open('w')as stdout,(folder/(label+'.stderr.log')).open('w')as stderr:
                subprocess.run(command,check=True,stdout=stdout,stderr=stderr,timeout=CHILD_TIMEOUT_SECONDS)
            return json.loads((folder/(label+'.stdout.log')).read_text().splitlines()[-1])
        for side in SIDES:
            result=execute([str(getattr(args,side+'_python').absolute()),str(probe),'--capture',str(folder/(side+'.npz'))],side)
            if result['cases']!=1984 or result['errors']!=408 or result['output_values']!=147220:raise ValueError('public capture process incomplete')
        for before,after in PAIRS.values():
            exact=before!='original';name=before+'-vs-'+after+('-exact'if exact else'')
            command=[str(args.candidate_python.absolute()),str(probe),'--compare',str(folder/(before+'.npz')),str(folder/(after+'.npz'))]
            if exact:command.append('--exact')
            result=execute(command,name)
            result.update(baseline=before,candidate=after,baseline_sha256=sha256(folder/(before+'.npz')),candidate_sha256=sha256(folder/(after+'.npz')))
            (folder/(name+'.json')).write_text(json.dumps(result,indent=2)+'\n')
    return public_probe_gate(args.output,provenance)

def case_values(name):
    family,layout=name.split('/')
    shape=layout.removesuffix('_interleaved')
    rows=math.prod(map(int,shape.split('x'))) if 'x' in shape else int(shape)
    return rows


def expected_coverage(name):
    family,layout=name.split('/')
    if family.startswith('control_cumsum'):
        return {'native56_route':'pure_polars','rows':case_values(name),'lookback':0}
    grouped=family.startswith('grouped_');kind=family.removeprefix('grouped_');shape=layout.removesuffix('_interleaved')
    groups,bars=map(int,shape.split('x')) if grouped else (1,int(shape))
    return {'native56_route':'compat_cmou' if kind=='cmou' else 'unchanged_cmo',
            'groups':groups,'bars':bars,'lookback':14,'first_valid_row':0,'timeperiod':14,
            'written_values':groups*(bars-14),'all_inputs_finite':True}


def validate_coverage(name,row):
    expected=expected_coverage(name)
    if any(type(row.get(k))is not type(v) or row.get(k)!=v for k,v in expected.items()):
        raise ValueError('selected fixture route/range/group coverage differs')
    if expected['native56_route']!='pure_polars':
        v=row.get('price_abs_max')
        if isinstance(v,bool) or not isinstance(v,(int,float)) or not math.isfinite(v) or not 0<=v<=1024:
            raise ValueError('fixture input range differs')


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
    for name in wanted:validate_coverage(name,row['fixture_coverage'][name])
    if selected:
        if row.get('input_snapshots')!={}:raise ValueError('timed child may not preserve raw inputs')
        if row.get('final_output_sha256') != row['output_sha256']:
            raise ValueError('final selected output bytes were not verified')
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
        for before,after in PAIRS.values():
            exact=before!='original'
            name=before+'-vs-'+after+('-exact' if exact else '')
            command=[str(args.candidate_python.absolute()),str(probe),'--compare',str(folder/(before+'.npz')),
                     str(folder/(after+'.npz')),'--report',str(folder/(name+'.json'))]
            if exact: command.append('--exact')
            execute(command,name)
    reports=corpus_gate(args.output)
    public_reports=run_public_validation(args,provenance)
    previous=set(os.sched_getaffinity(0));prepared={}
    try:
        for threads in (1,4):
            if len(previous)<threads: raise ValueError('insufficient CPU affinity')
            prepared[str(threads)]=run_setting(args,threads,previous,prepare_only=True)
    finally: os.sched_setaffinity(0,previous)
    verify_build(args)
    expected=prepared['1']['source_validations']['original']['fixture_sha256']
    if prepared['4']['source_validations']['original']['fixture_sha256']!=expected:
        raise ValueError('thread settings use different physical fixtures')
    snapshots=prepared['1']['source_validations']['original']['input_snapshots']
    dedup=validate_input_snapshots(args.output/'raw-inputs',snapshots,expected)
    if dedup!=6:raise ValueError('fixed physical input deduplication differs')
    record={'raw_input_snapshots':snapshots,'raw_input_fixture_sha256':expected,'raw_input_dedup':dedup,'all_checks_completed_before_any_timing':True,'corpus':reports,'cmou_public':public_reports,
            'prepared_sha256':{str(t):sha256(args.output/f'threads-{t}'/'prepared-validation.json') for t in (1,4)},
            'build_provenance_sha256':sha256(args.output/'build-provenance.json'),
            'cases':requested_inventory(),'checked_values_per_setting':CHECKED_VALUES}
    (args.output/'validation-complete.json').write_text(json.dumps(record,indent=2)+'\n')
    return record


def verify_validation(args):
    provenance=verify_build(args); corpus_gate(args.output)
    public_reports=public_probe_gate(args.output,provenance)
    record=json.loads((args.output/'validation-complete.json').read_text())
    if (record['cmou_public']!=public_reports or not record['all_checks_completed_before_any_timing'] or record['cases'] != requested_inventory()
            or record['checked_values_per_setting'] != CHECKED_VALUES
            or record['build_provenance_sha256'] != sha256(args.output/'build-provenance.json')):
        raise ValueError('validation does not cover these builds/inventory')
    for threads in (1,4):
        folder=args.output/f'threads-{threads}'
        if sha256(folder/'prepared-validation.json') != record['prepared_sha256'][str(threads)]:
            raise ValueError('prepared query validation changed')
        prepared=json.loads((folder/'prepared-validation.json').read_text())
        for side in SIDES:
            name='reference.npz' if side=='original' else side+'-reference.npz'
            if sha256(folder/name)!=prepared['golden_sha256'][side]:raise ValueError('query golden changed')
    if record['raw_input_dedup']!=6 or validate_input_snapshots(args.output/'raw-inputs',record['raw_input_snapshots'],record['raw_input_fixture_sha256'])!=6:
        raise ValueError('retained raw inputs differ')
    for threads in (1,4):
        prepared=json.loads((args.output/f'threads-{threads}'/'prepared-validation.json').read_text())
        if prepared['source_validations']['original']['fixture_sha256']!=record['raw_input_fixture_sha256']:
            raise ValueError('raw input case mapping differs from prepared fixtures')
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
    lines=['# Every slower pairwise median','','All six pairwise comparisons and controls are included. Envelopes are descriptive, not confidence intervals.','',
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
    fixed_pins(args.candidate_commit)
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
    lines = ['# Consumer CMOU checked-windows comparison', '',
             *[f'{side}: `{first["commits"][side]}`' for side in SIDES], '',
             f"{first['cpu']}; {first['platform']}; Python {first['python']}, Polars {first['polars']}, NumPy {first['numpy']}; {first['rust']}.",
             f'{args.rounds} fresh processes per CASE/build/thread setting; balanced four-arm Williams orders repeated3times; {args.repeats} samples after five warmups. No sibling query runs before the selected case.',
             'Ratios use matched-round medians. Envelopes span min(before medians)/max(after medians) to max(before)/min(after).',
             'These are descriptive ranges, not confidence intervals. Shared-host contention, frequency and placement remain uncontrolled.',
             'getrusage counters are process totals sampled outside the latency interval; they do not isolate jemalloc or kernel faults.',
             'Only direct expressions and ordinary native Polars .over() are measured. No new grouping expression/list composition.',
             'The fixed inventory has6 CMOU scenarios,4 unchanged CMO controls and2 pure Polars controls; all slower medians remain in raw reports.', '',
             *sections]
    (args.output/'comparison.md').write_text('\n'.join(lines)+'\n')
    write_negatives(metadata, args.output)
    print('\n'.join(lines), flush=True)


if __name__ == '__main__':
    main()
