"""Reject incomparable integer-output CI evidence before accepting measurements."""
from collections import Counter
import copy
import importlib
import json
from pathlib import Path
import sys
from types import SimpleNamespace
import zipfile

import numpy as np
import pytest

sys.path.insert(0,str(Path(__file__).parents[1]/'scripts'))
bench=importlib.import_module('integer_init_benchmark')
query=importlib.import_module('integer_init_query')
prov=importlib.import_module('integer_init_provenance')
stages=importlib.import_module('integer_init_stage_benchmark')


def identities():
    rows={side:{'python':'3.12.15','platform':'Linux','polars':'1.44.2','numpy':'2.5.3','package':'0.2.1',
                'talib':'0.8.3 (native Rust; polars-talib compatibility)','native_files':{'/installed/'+side+'.so':side}}
          for side in bench.SIDES}
    rows['original']['talib']='0.8.1 (original C)'
    return rows


def provenance():
    return {'flags':{'rustc':'rustc 1.90.0 (test)\nbinary: rustc\n'},
            'builds':{side:{'source':{'commit':str(i+1)*40,'source_sha256':side},'identity':identities()[side]}
                      for i,side in enumerate(bench.SIDES)}}


def run(side='prior',name=None):
    name=name or bench.CASES[0]; build=provenance()['builds'][side]
    return {**build['identity'],**build['source'],'native_binary_sha256':side,'rust':'rustc 1.90.0 (test)',
            'threads':1,'affinity':[2],'repeats':31,'warmups':5,'diagnostic':False,'integer_reference_exact':True,
            'case_filters':[name],'case_inventory':[name],'checked_values':bench.case_values(name),'exact_reference':True,
            'results':{name:{'samples_ms':[1.]*31,'median_ms':1.,'minor_faults':[0]*31,'major_faults':[0]*31}}}


def test_orders_balance_all_positions_and_directed_within_round_transitions():
    orders=bench.ORDERS*2
    assert len(orders)==12 and len(set(orders))==6
    for position in range(3):
        assert Counter(order[position] for order in orders)=={side:4 for side in bench.SIDES}
    transitions=Counter((a,b) for order in orders for a,b in zip(order,order[1:]))
    assert transitions=={(a,b):4 for a in bench.SIDES for b in bench.SIDES if a!=b}


def test_fixed_inventory_has_exact_values_and_no_broad_expansion():
    assert tuple(bench.requested_inventory())==query.CASE_NAMES
    assert len(bench.CASES)==len(set(bench.CASES))==13
    assert sum(bench.case_values(name) for name in bench.CASES)==16_400_000
    assert set(bench.CASES)=={
        'cdldoji/1000000','grouped_cdldoji/100x10000','grouped_cdldoji/10000x100',
        'minmaxindex/1000000','grouped_minmaxindex/100x10000','grouped_minmaxindex/10000x100',
        'grouped_minmaxindex/2000x100_interleaved','ht_trendmode/1000000',
        'cdlengulfing/1000000','grouped_cdlengulfing/100x10000',
        'grouped_add/10000x100','control_cumsum/100x10000','supertrend/1000000'}
    with pytest.raises(ValueError): bench.requested_inventory(True,[])
    with pytest.raises(ValueError): bench.requested_inventory(False,['*'])
    assert bench.PRIOR_COMMIT=='78c3a1be1d3eeba24970ee20f66a33c10c74c327'


def test_selector_constructs_only_the_selected_case(monkeypatch):
    names=[]
    def frame(rows,bars):
        names.append((rows,bars));return object()
    monkeypatch.setattr(query,'frame',frame)
    monkeypatch.setattr(query,'indicator',lambda name:SimpleNamespace(alias=lambda _:name))
    selected='ht_trendmode/1000000'
    rows=list(query.cases(filters=[selected]))
    assert len(rows)==1 and rows[0][0]==selected and names==[(1_000_000,1000)]


@pytest.mark.parametrize('change',['numpy','polars','old_c','missing'])
def test_runtime_gate_rejects_mixed_versions_or_arms(change):
    rows=identities()
    if change=='numpy': rows['candidate']['numpy']='2.5.4'
    elif change=='polars': rows['prior']['polars']='2.1.0'
    elif change=='old_c': rows['original']['talib']='0.8.3'
    else: del rows['candidate']
    with pytest.raises(ValueError): prov.validate_identities(rows)


@pytest.mark.parametrize('change',['pin','source','binary','numpy','affinity','rust','inventory','undercheck','no_exact','boolean','nan','count','median','fault'])
def test_child_gate_rejects_wrong_pin_runtime_scope_or_raw_samples(change):
    row=run();name=bench.CASES[0]
    if change=='pin': row['commit']='f'*40
    elif change=='source': row['source_sha256']='other'
    elif change=='binary': row['native_binary_sha256']='other'
    elif change=='numpy': row['numpy']='2.5.4'
    elif change=='affinity': row['affinity']=[2,3]
    elif change=='rust': row['rust']='rustc 1.97.0'
    elif change=='inventory': row['case_inventory']+=['cdlengulfing/1000000']
    elif change=='undercheck': row['checked_values']-=1
    elif change=='no_exact': row['exact_reference']=False
    elif change=='boolean': row['results'][name]['samples_ms'][0]=True
    elif change=='nan': row['results'][name]['samples_ms'][0]=float('nan')
    elif change=='count': row['results'][name]['samples_ms'].pop()
    elif change=='median': row['results'][name]['median_ms']=2.
    else: row['results'][name]['minor_faults'][0]=-1
    with pytest.raises(ValueError): bench.validate_report(row,'prior',1,provenance(),name)


def test_valid_child_and_integer_outputs_never_use_float_tolerance():
    row=run();bench.validate_report(row,'prior',1,provenance(),bench.CASES[0])
    old=np.array([0,1,100,1_000_000_000_000],dtype=np.int64)
    new=old.copy();new[-1]+=1
    # A tolerance check would accept this one-unit integer error.
    assert np.allclose(old,new,rtol=1e-10,atol=1e-10)
    with pytest.raises(AssertionError): query.compare_arrays(new,np.zeros(4,bool),old,np.zeros(4,bool))


@pytest.mark.parametrize('kind',['null','sign','nan','dtype','shape'])
def test_query_golden_checks_schema_nulls_signed_zero_and_nan_positions(kind):
    old=np.array([0.,1.,float('nan')]);new=old.copy();nulls=np.zeros(3,bool);expected_nulls=nulls.copy()
    if kind=='null': nulls[0]=True
    elif kind=='sign': new[0]=-0.
    elif kind=='nan': new[2]=2.
    elif kind=='dtype': new=new.astype(np.float32)
    else: new=new[:2]
    with pytest.raises((AssertionError,ValueError)):
        query.compare_arrays(new,nulls,old,expected_nulls,exact=True)


def test_wheel_native_bytes_must_match_installed_extension(tmp_path):
    with zipfile.ZipFile(tmp_path/'native.whl','w') as archive:
        archive.writestr('polars_talib/_polars_talib.abi3.so',b'real product bytes')
    with pytest.raises(ValueError,match='installed native module'):
        prov.wheel_record(tmp_path,{'native_files':{'/env/_polars_talib.abi3.so':'wrong'}})


def corpus_fixture(output):
    folder=output/'corpus';folder.mkdir()
    for side in bench.SIDES: (folder/(side+'.npz')).write_bytes(side.encode())
    for before,after,exact in [('prior','candidate',True),('original','prior',False),('original','candidate',False)]:
        row={'require_exact':exact,'cases':10624,'checked_values':2167654,'failures':[],
             'api_call_contract_match':True,'fields_with_bit_differences':0,'max_absolute_difference':0,
             'baseline':str(folder/(before+'.npz')),'candidate':str(folder/(after+'.npz')),
             'baseline_sha256':bench.sha256(folder/(before+'.npz')),'candidate_sha256':bench.sha256(folder/(after+'.npz'))}
        name=before+'-vs-'+after+('-exact' if exact else '')
        (folder/(name+'.json')).write_text(json.dumps(row))
    return folder


@pytest.mark.parametrize('change',['count','nonexact','failure','contract','capture'])
def test_full_corpus_gate_refuses_underchecks_changed_captures_and_integer_mismatch(tmp_path,change):
    folder=corpus_fixture(tmp_path);assert len(bench.corpus_gate(tmp_path))==3
    path=folder/'prior-vs-candidate-exact.json';row=json.loads(path.read_text())
    if change=='count': row['checked_values']-=1
    elif change=='nonexact': row['fields_with_bit_differences']=1
    elif change=='failure': row['failures']=[{'case':'ht_trendmode/1000000','reason':['integer differs']}]
    elif change=='contract': row['api_call_contract_match']=False
    else: (folder/'candidate.npz').write_bytes(b'changed')
    path.write_text(json.dumps(row))
    with pytest.raises(ValueError): bench.corpus_gate(tmp_path)


def test_source_pins_must_be_full_sha_and_match_checkout(tmp_path,monkeypatch):
    with pytest.raises(ValueError,match='immutable SHA'): prov.source_record(tmp_path,'main')
    monkeypatch.setattr(prov.subprocess,'check_output',lambda *a,**k:'a'*40+'\n')
    with pytest.raises(ValueError,match='source pin mismatch'): prov.source_record(tmp_path,'b'*40)


def test_no_setting_can_time_without_verified_all_setting_validation(monkeypatch,tmp_path):
    calls=[]
    monkeypatch.setattr(bench,'verify_validation',lambda _:(_ for _ in ()).throw(ValueError('both settings not ready')))
    monkeypatch.setattr(bench,'run_setting',lambda *a,**k:calls.append(a))
    with pytest.raises(ValueError): bench.run_all_settings(SimpleNamespace(thread_counts=[1,4],output=tmp_path),None)
    assert calls==[]


def test_negative_inventory_includes_small_overlap_and_controls(tmp_path):
    row={'baseline_median_ms':1.,'candidate_median_ms':1.001,'paired_ratios':[1/1.001]*12,'ratio_envelope':[.99,1.01]}
    data={'results':{'1':{'comparisons':{'prior_vs_candidate':{'control_cumsum/100x10000':row}}}}}
    bench.write_negatives(data,tmp_path)
    negatives=json.loads((tmp_path/'negative-cases.json').read_text())
    assert len(negatives)==1 and negatives[0]['case']=='control_cumsum/100x10000'
    assert negatives[0]['after_faster_rounds']==0


def test_stage_protocol_records_zeroed_requests_and_rejects_duplicates():
    text='C_VERSION 0.8.1 (test)\nPROBE doji/init_eager_int/1000 allocations=1 bytes=4000 zeroed_requests=0 realloc_requests=0 holder_bytes=4 ns=[1,2,3,4,5,6,7]\n'
    row=stages.parse_probe(text,'doji','init_eager_int',1000)
    assert row['zeroed_requests']==row['realloc_requests']==0 and row['median_ns']==4
    with pytest.raises(ValueError): stages.parse_probe(text+text,'doji','init_eager_int',1000)
    assert len(stages.kernel_cases())==72 and len(stages.ORDERS)==12
    assert {'init_zero_int','init_eager_int','init_zero_int_touch','init_eager_int_touch','materialize_zero','materialize_eager'}<=set(stages.MODES)


def test_native_dependency_fingerprints_choose_actual_wheel_features_and_reject_conflicting_builds(tmp_path):
    root = tmp_path / 'release/.fingerprint'; deps = tmp_path / 'release/deps'; deps.mkdir(parents=True)
    parent = root / 'polars_talib-native'; parent.mkdir(parents=True)
    names = ('ta_lib', 'polars', 'serde', 'jemallocator')
    mapping = []
    for i, name in enumerate(names, 1):
        folder = root / (name + '-native'); folder.mkdir()
        (folder / ('lib-' + name)).write_text(i.to_bytes(8, 'little').hex())
        (folder / ('lib-' + name + '.json')).write_text('{}')
        (deps / ('lib' + name + '-native.rlib')).touch()
        mapping.append([i, name, False, i])
    (parent / 'lib-_polars_talib.json').write_text(json.dumps({'deps': mapping, 'rustflags': []}))
    (parent / 'lib-_polars_talib').write_text((100).to_bytes(8, 'little').hex())
    # The original C wheel's smaller Polars feature graph remains in the shared target.
    other = root / 'polars-original'; other.mkdir()
    (other / 'lib-polars').write_text((99).to_bytes(8, 'little').hex())
    (other / 'lib-polars.json').write_text('{}')
    (deps / 'libpolars-original.rlib').touch()
    found, evidence = stages.native_dependency_records(tmp_path)
    assert found['polars'].name == 'libpolars-native.rlib' and evidence
    conflict = root / 'polars_talib-conflict'; conflict.mkdir()
    mapping[1][-1] = 99
    (conflict / 'lib-_polars_talib.json').write_text(json.dumps({'deps': mapping, 'rustflags': []}))
    (conflict / 'lib-_polars_talib').write_text((101).to_bytes(8, 'little').hex())
    with pytest.raises(ValueError, match='disagree'):
        stages.native_dependency_records(tmp_path)



def test_raw_fingerprint_endianness_matches_actual_rust190_cargo_artifact():
    # Observed native-single-chunk Cargo parent deps entry for Polars:
    # [12302415943370065676, "polars", false, 12829913266768297537].
    # Its .fingerprint/polars-e3f1f97ac13c28e9/lib-polars file contains this raw hex.
    assert stages.fingerprint_value('41becbec23020db2') == 12829913266768297537



def test_zero_product_parent_retains_unfiltered_c_and_test_filter_reasons(tmp_path):
    root = tmp_path / 'release/.fingerprint/polars_talib-current'; root.mkdir(parents=True)
    (root / 'lib-_polars_talib.json').write_text(json.dumps({'deps': [[1, 'talib', False, 8]], 'rustflags': []}))
    (root / 'test-lib-_polars_talib.json').write_text(json.dumps({'deps': [[1, name, False, i] for i, name in enumerate(('polars', 'serde', 'ta_lib', 'jemallocator'))], 'rustflags': []}))
    inventory = tmp_path / 'ordinary-inventory.json'
    with pytest.raises(ValueError, match='zero native product parents; unfiltered candidates=2'):
        stages.native_dependency_records(tmp_path, inventory_path=inventory)
    data = json.loads(inventory.read_text())
    assert all(not p['selected'] for p in data['parents'])
    assert any('missing native' in reason for p in data['parents'] for reason in p['filter_reasons'])
    assert any('test artifact' in reason for p in data['parents'] for reason in p['filter_reasons'])



def test_snapshot_keeps_actual_wheel_elf_and_rlibs_before_shared_target_changes(tmp_path,monkeypatch):
    original=tmp_path/'original';original.mkdir()
    native=original/'_polars_talib.abi3.so';native.write_bytes(b'actual measured wheel ELF')
    dependencies={}
    for name in ('ta_lib','polars','serde','jemallocator'):
        path=original/('lib'+name+'.rlib');path.write_bytes(name.encode());dependencies[name]=path
    def records(target,inventory_path):
        inventory_path.write_text('{}');return dependencies,{}
    monkeypatch.setattr(stages,'native_dependency_records',records)
    monkeypatch.setattr(stages,'identity',lambda _: {'native_files':{str(native):stages.sha256(native)}})
    monkeypatch.setattr(stages,'source_record',lambda *a:{'commit':'a'*40})
    monkeypatch.setattr(stages,'wheel_record',lambda *a:{'sha256':'wheel'})
    monkeypatch.setattr(stages,'flags_record',lambda :{'rustc':'Rust1.90'})
    args=SimpleNamespace(output=tmp_path/'results',snapshot_side='prior',target_dir=original,
                         python=Path('/test/python'),source=original,commit='a'*40,wheel_dir=tmp_path)
    stages.snapshot(args)
    record=json.loads((args.output/'linkage/prior/product-linkage.json').read_text())
    assert len(record['retained_product_artifacts'])==5
    native.write_bytes(b'later target overwrite')
    for path,digest in record['retained_product_artifacts'].items():
        assert stages.sha256(path)==digest
    assert (args.output/'linkage/prior/product-artifacts/_polars_talib.abi3.so').read_bytes()==b'actual measured wheel ELF'


def test_production_controller_issues_one_exact_arm_golden_child_per_case_and_round(tmp_path,monkeypatch):
    folder=tmp_path/'threads-1';folder.mkdir()
    for name in ('reference.npz','prior-reference.npz'): (folder/name).write_bytes(name.encode())
    sources={}
    for side in bench.SIDES:
        row=run(side);row.update(cpu='test CPU',profile='portable release')
        row.update(case_inventory=list(bench.CASES),case_filters=list(bench.CASES),results={},checked_values=bench.CHECKED_VALUES)
        sources[side]=row
    prepared={'threads':1,'source_validations':sources,'inventory':list(bench.CASES),
              'exact_validation':sources['candidate'],'commands':[],
              'reference_sha256':bench.sha256(folder/'reference.npz'),
              'prior_reference_sha256':bench.sha256(folder/'prior-reference.npz')}
    (folder/'prepared-validation.json').write_text(json.dumps(prepared))
    monkeypatch.setattr(bench,'verify_build',lambda _:provenance())
    commands=[]
    def execute(command,**kwargs):
        selected=[command[i+1] for i,value in enumerate(command) if value=='--case-filter']
        assert len(selected)==1 and selected[0] in bench.CASES
        side=Path(command[0]).name.removesuffix('-python')
        golden=Path(command[command.index('--reference')+1]).name
        assert golden==('reference.npz' if side=='original' else 'prior-reference.npz')
        assert '--exact-reference' in command and '--diagnostic' not in command
        row=run(side,selected[0]);row.update(cpu='test CPU',profile='portable release')
        Path(command[command.index('--output')+1]).write_text(json.dumps(row))
        commands.append((side,selected[0]))
    monkeypatch.setattr(bench.subprocess,'run',execute)
    args=SimpleNamespace(output=tmp_path,repeats=31,rounds=12,candidate_commit='3'*40)
    for side in bench.SIDES:
        setattr(args,side+'_python',Path('/'+side+'-python'))
        setattr(args,side+'_source',tmp_path)
    metadata,_=bench.run_setting(args,1,None)
    assert len(commands)==len(metadata['processes'])==468
    assert Counter(commands)=={(side,case):12 for case in bench.CASES for side in bench.SIDES}
    for case_index,case in enumerate(bench.CASES):
        expected=[(side,case) for order in bench.ORDERS*2 for side in order]
        assert commands[case_index*36:(case_index+1)*36]==expected


@pytest.mark.parametrize('kind',['fresh','wrong_source','source_prefix','missing','mixed'])
def test_compile_log_guard_requires_actual_exact_source_compile(tmp_path,kind):
    source=tmp_path/'sources/prior';source.mkdir(parents=True)
    expected=f'   Compiling polars_talib v0.2.1 ({source})\n'
    if kind=='fresh': text=expected.replace('Compiling','Fresh')
    elif kind=='wrong_source': text=expected.replace('/prior)', '/candidate)')
    elif kind=='source_prefix': text=expected.replace('/prior)', '/prior-wrong-prefix)')
    elif kind=='missing': text='Finished release profile in 0.08s\n'
    else: text=expected+expected.replace('/prior)', '/candidate)')
    log=tmp_path/'build.log';log.write_text(text)
    with pytest.raises(ValueError,match='exactly'):
        prov.require_product_compile(log,source)


def test_compile_log_guard_cli_is_stdlib_and_records_exact_resolved_source(tmp_path):
    import subprocess
    source=tmp_path/'sources/prior';source.mkdir(parents=True)
    log=tmp_path/'build.log';log.write_text(f'   Compiling polars_talib v0.2.1 ({source})\n    Finished release profile\n')
    output=subprocess.check_output([sys.executable,prov.__file__,'--compile-log',str(log),'--source',str(source/'..'/'prior')],text=True)
    proof=json.loads(output)
    assert proof['product_source']==str(source.resolve()) and proof['log_sha256']==prov.sha256(log)
    assert proof['product_compile_lines']==1
