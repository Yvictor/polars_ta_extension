"""Reject incomparable guard-fusion CI evidence before accepting measurements."""
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
bench=importlib.import_module('guard_fusion_benchmark')
query=importlib.import_module('guard_fusion_query')
prov=importlib.import_module('guard_fusion_provenance')


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
            'fixture_sha256':{name:'input'},'output_sha256':{name:'output-'+side},'final_output_checked':True,
            'case_filters':[name],'case_inventory':[name],'checked_values':bench.case_values(name),'exact_reference':True,
            'results':{name:{'samples_ms':[1.]*31,'median_ms':1.,'minor_faults':[0]*31,'major_faults':[0]*31}}}


def test_orders_balance_all_positions_and_directed_within_round_transitions():
    orders=bench.ORDERS*3
    assert len(orders)==12 and len(set(orders))==4
    for position in range(4):
        assert Counter(order[position] for order in orders)=={side:3 for side in bench.SIDES}
    transitions=Counter((a,b) for order in orders for a,b in zip(order,order[1:]))
    assert transitions=={(a,b):3 for a in bench.SIDES for b in bench.SIDES if a!=b}


def test_fixed_inventory_has_exact_values_and_no_broad_expansion():
    assert tuple(bench.requested_inventory())==query.CASE_NAMES
    assert len(bench.CASES)==len(set(bench.CASES))==22
    assert sum(bench.case_values(name) for name in bench.CASES)==32_400_000
    assert set(bench.CASES)=={'grouped_correl/2000x100_interleaved', 'grouped_macd/2000x100_interleaved', 'grouped_bbands/2000x100_interleaved', 'grouped_sma/10000x100', 'grouped_var/10000x100', 'grouped_stddev/100x10000', 'grouped_bbands/10000x100', 'grouped_correl/10000x100', 'correl/1000000', 'grouped_bbands/1000x1000', 'var/1000000', 'macd/1000000', 'grouped_var/100x10000', 'grouped_stddev/10000x100', 'bbands/1000000', 'grouped_correl/100x10000', 'grouped_macd/10000x100', 'control_cumsum/10000x100', 'control_cumsum_dense/1000000', 'grouped_macd/1000x1000', 'sma/1000000', 'stddev/1000000'}
    with pytest.raises(ValueError): bench.requested_inventory(True,[])
    with pytest.raises(ValueError): bench.requested_inventory(False,['*'])
    assert bench.PRIOR_COMMIT=='56f6d5fb139031c20d86d7e818e7d267eb834295'


def test_selector_constructs_only_the_selected_case(monkeypatch):
    names=[]
    def frame(rows,bars):
        names.append((rows,bars));return object()
    monkeypatch.setattr(query,'frame',frame)
    monkeypatch.setattr(query,'indicator',lambda name:SimpleNamespace(alias=lambda _:name))
    selected='stddev/1000000'
    rows=list(query.cases(filters=[selected]))
    assert len(rows)==1 and rows[0][0]==selected and names==[(1_000_000,1000)]


@pytest.mark.parametrize('change',['python','numpy','polars','old_c','missing'])
def test_runtime_gate_rejects_mixed_versions_or_arms(change):
    rows=identities()
    if change=='python': rows['candidate']['python']='3.12.14'
    elif change=='numpy': rows['candidate']['numpy']='2.5.4'
    elif change=='polars': rows['prior']['polars']='2.1.0'
    elif change=='old_c': rows['original']['talib']='0.8.3'
    else: del rows['candidate']
    with pytest.raises(ValueError): prov.validate_identities(rows)


@pytest.mark.parametrize('change',['pin','source','binary','numpy','affinity','rust','inventory','undercheck','no_exact','boolean','nan','count','median','fault','final_output'])
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
    elif change=='final_output': row['final_output_checked']=False
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
    for before,after in bench.PAIRS.values():
        exact=before!='original'
        row={'require_exact':exact,'cases':10624,'checked_values':2167654,'failures':[],
             'api_call_contract_match':True,'fields_with_bit_differences':0,'max_absolute_difference':0,
             'baseline':str(folder/(before+'.npz')),'candidate':str(folder/(after+'.npz')),
             'baseline_sha256':bench.sha256(folder/(before+'.npz')),'candidate_sha256':bench.sha256(folder/(after+'.npz'))}
        name=before+'-vs-'+after+('-exact' if exact else '')
        (folder/(name+'.json')).write_text(json.dumps(row))
    return folder


@pytest.mark.parametrize('change',['count','nonexact','failure','contract','capture'])
def test_full_corpus_gate_refuses_underchecks_changed_captures_and_integer_mismatch(tmp_path,change):
    folder=corpus_fixture(tmp_path);assert len(bench.corpus_gate(tmp_path))==6
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
    data={'results':{'1':{'comparisons':{'prior_vs_candidate':{'sma/1000000':row}}}}}
    bench.write_negatives(data,tmp_path)
    negatives=json.loads((tmp_path/'negative-cases.json').read_text())
    assert len(negatives)==1 and negatives[0]['case']=='sma/1000000'
    assert negatives[0]['after_faster_rounds']==0
    assert negatives[0]['case_role']=='ineligible_native_factory_overhead_control'
    assert negatives[0]['is_unchanged_timed_query'] is False















def test_production_controller_issues_one_exact_arm_golden_child_per_case_and_round(tmp_path,monkeypatch):
    folder=tmp_path/'threads-1';folder.mkdir()
    for name in ('reference.npz','prior-reference.npz'): (folder/name).write_bytes(name.encode())
    sources={}
    for side in bench.SIDES:
        row=run(side);row.update(cpu='test CPU',profile='portable release')
        row.update(fixture_sha256={n:'input' for n in bench.CASES},output_sha256={n:'output-'+side for n in bench.CASES})
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
    args=SimpleNamespace(output=tmp_path,repeats=31,rounds=12,candidate_commit='4'*40,initialization_commit='3'*40)
    for side in bench.SIDES:
        setattr(args,side+'_python',Path('/'+side+'-python'))
        setattr(args,side+'_source',tmp_path)
    metadata,_=bench.run_setting(args,1,None)
    assert len(commands)==len(metadata['processes'])==1056
    assert Counter(commands)=={(side,case):12 for case in bench.CASES for side in bench.SIDES}
    for case_index,case in enumerate(bench.CASES):
        expected=[(side,case) for order in bench.ORDERS*3 for side in order]
        assert commands[case_index*48:(case_index+1)*48]==expected


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


@pytest.mark.parametrize('change',['opt','lto','cgu','flags','encoded'])
def test_product_profile_is_exact_without_llvm_lto_override(monkeypatch,change):
    values={'CARGO_PROFILE_RELEASE_OPT_LEVEL':'3','CARGO_PROFILE_RELEASE_LTO':'false',
            'CARGO_PROFILE_RELEASE_CODEGEN_UNITS':'16','RUSTFLAGS':'','CARGO_ENCODED_RUSTFLAGS':''}
    for key,value in values.items(): monkeypatch.setenv(key,value)
    monkeypatch.setattr(prov.subprocess,'check_output',lambda command,**kwargs: 'rustc 1.90.0 (test)\n' if command[0]=='rustc' else 'test')
    assert prov.flags_record()['environment']['CARGO_PROFILE_RELEASE_LTO']=='false'
    key={'opt':'CARGO_PROFILE_RELEASE_OPT_LEVEL','lto':'CARGO_PROFILE_RELEASE_LTO',
         'cgu':'CARGO_PROFILE_RELEASE_CODEGEN_UNITS','flags':'RUSTFLAGS','encoded':'CARGO_ENCODED_RUSTFLAGS'}[change]
    monkeypatch.setenv(key,'different')
    with pytest.raises(ValueError,match='Cargo release'): prov.flags_record()


def test_measured_product_elf_header_architecture_is_bound(tmp_path):
    path=tmp_path/'actual.so';header=bytearray(20);header[:6]=b'\x7fELF\x02\x01';header[18:20]=(62).to_bytes(2,'little')
    path.write_bytes(header);assert prov.elf_record(path)['sha256']==prov.sha256(path)
    header[18:20]=(183).to_bytes(2,'little');path.write_bytes(header)
    with pytest.raises(ValueError,match='x86-64'): prov.elf_record(path)






@pytest.mark.parametrize('change',['none','parent','paths','diff','source','patch'])
def test_initialization_control_is_an_immutable_reviewed_derivation(tmp_path,monkeypatch,change):
    expected=json.loads(Path(bench.__file__).with_name('guard_fusion_sources.json').read_text())
    # Actual source and patch digests are covered by source_record/sha256;
    # this fixture isolates the parent/path/diff binding orchestration.
    candidate=tmp_path/'candidate';initialization=tmp_path/'initialization'
    args=SimpleNamespace(candidate_commit=expected['candidate_commit'],initialization_commit=expected['initialization_commit'],
                         candidate_source=candidate,initialization_source=initialization,output=tmp_path)
    patch=bench.frozen_patch()
    diff=b'exact frozen init-only diff'
    class BoundHash:
        def __init__(self,data):self.data=data
        def hexdigest(self):
            if self.data==patch:return 'changed' if change=='patch' else expected['patch_sha256']
            return expected['git_diff_sha256'] if change!='diff' else 'changed'
    monkeypatch.setattr(bench.hashlib,'sha256',BoundHash)
    def output(command,**kwargs):
        if 'rev-parse' in command:return ('bad-parent' if change=='parent' else expected['initialization_parent'])+'\n'
        if '--name-only' in command:return 'src/compat/guarded.rs\n'+('src/native.rs\n' if change=='paths' else '')
        return diff
    monkeypatch.setattr(bench.subprocess,'check_output',output)
    def digest(path):
        path=Path(path)
        return ('changed' if change=='source' else expected['candidate_guard_sha256']) if candidate in path.parents else expected['initialization_guard_sha256']
    monkeypatch.setattr(bench,'sha256',digest)
    if change=='none':
        assert bench.source_relation(args)==expected
        assert (tmp_path/'initialization-only-bound.diff').read_bytes()==diff
    else:
        with pytest.raises(ValueError):bench.source_relation(args)


def test_all_four_arm_goldens_and_all_six_comparisons_are_required():
    assert set(bench.NATIVE_SIDES)=={'prior','initialization','candidate'}
    assert len(bench.PAIRS)==6
    assert set(bench.PAIRS.values())=={(a,b) for i,a in enumerate(bench.SIDES) for b in bench.SIDES[i+1:]}



def test_pure_polars_controls_never_invoke_ta_factory_and_keep_native_over(monkeypatch):
    data=query.pl.DataFrame({'close':[1.,2.,3.,4.],'symbol':[0,0,1,1]})
    monkeypatch.setattr(query,'frame',lambda *args:data)
    monkeypatch.setattr(query,'indicator',lambda *args:(_ for _ in ()).throw(AssertionError('TA factory invoked')))
    dense,grouped=list(query.cases(filters=['control_cumsum_dense/1000000','control_cumsum/10000x100']))
    assert dense[1].select(dense[2]).to_series().to_list()==[1.,3.,6.,10.]
    assert grouped[1].select(grouped[2]).to_series().to_list()==[1.,3.,3.,7.]
    assert bench.case_role('control_cumsum_dense/1000000')=='pure_polars_drift_control'
    assert bench.case_role('grouped_sma/10000x100')=='ineligible_native_factory_overhead_control'
