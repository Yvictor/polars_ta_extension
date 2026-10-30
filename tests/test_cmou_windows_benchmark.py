"""Reject incomparable consumer CMOU checked-window CI evidence before accepting measurements."""
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
bench=importlib.import_module('cmou_windows_benchmark')
query=importlib.import_module('cmou_windows_query')
prov=importlib.import_module('cmou_windows_provenance')


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


def coverage(name):
    row=bench.expected_coverage(name).copy()
    if row['native56_route']!='pure_polars':
        row.update(price_abs_max=101.)
    return row


def run(side='prior',name=None):
    name=name or bench.CASES[0]; build=provenance()['builds'][side]
    return {**build['identity'],**build['source'],'native_binary_sha256':side,'rust':'rustc 1.90.0 (test)',
            'threads':1,'affinity':[2],'repeats':31,'warmups':5,'diagnostic':False,'integer_reference_exact':True,
            'fixture_coverage':{name:coverage(name)},'fixture_sha256':{name:'input'},'output_sha256':{name:'output-'+side},'input_snapshots':{},'final_output_checked':True,'final_output_sha256':{name:'output-'+side},
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
    assert len(bench.CASES)==len(set(bench.CASES))==12
    assert sum(bench.case_values(name) for name in bench.CASES)==9_401_000
    expected=['cmou/1000000','cmou/1000','grouped_cmou/100x10000','grouped_cmou/1000x1000','grouped_cmou/10000x100','grouped_cmou/2000x100_interleaved','cmo/1000000','grouped_cmo/100x10000','grouped_cmo/10000x100','grouped_cmo/2000x100_interleaved','control_cumsum_dense/1000000','control_cumsum/10000x100']
    assert list(bench.CASES)==expected
    with pytest.raises(ValueError):bench.requested_inventory(True,[])
    with pytest.raises(ValueError):bench.requested_inventory(False,['*'])
    assert bench.PRIOR_COMMIT=='56f6d5fb139031c20d86d7e818e7d267eb834295'
    assert bench.COMBINED_COMMIT=='e79ac0785436bbf3ba4c411d80936f8dd4ecfa24'


def test_selector_constructs_only_the_selected_case(monkeypatch):
    names=[]
    def frame(rows,bars,grouped):
        names.append((rows,bars,grouped));return object()
    monkeypatch.setattr(query,'frame',frame)
    monkeypatch.setattr(query,'indicator',lambda name:SimpleNamespace(alias=lambda _:name))
    selected='cmou/1000000'
    rows=list(query.cases(filters=[selected]))
    assert len(rows)==1 and rows[0][0]==selected and names==[(1_000_000,1000,False)]


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
    elif change=='inventory': row['case_inventory']+=['cmou/1000000']
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
    data={'results':{'1':{'comparisons':{'prior_vs_candidate':{'control_cumsum/100x10000':row}}}}}
    bench.write_negatives(data,tmp_path)
    negatives=json.loads((tmp_path/'negative-cases.json').read_text())
    assert len(negatives)==1 and negatives[0]['case']=='control_cumsum/100x10000'
    assert negatives[0]['after_faster_rounds']==0















def test_production_controller_issues_one_exact_arm_golden_child_per_case_and_round(tmp_path,monkeypatch):
    folder=tmp_path/'threads-1';folder.mkdir()
    for name in ('reference.npz','prior-reference.npz','combined-reference.npz','candidate-reference.npz'): (folder/name).write_bytes(name.encode())
    sources={}
    for side in bench.SIDES:
        row=run(side);row.update(cpu='test CPU',profile='portable release')
        row.update(fixture_coverage={n:coverage(n) for n in bench.CASES},fixture_sha256={n:'input' for n in bench.CASES},output_sha256={n:'output-'+side for n in bench.CASES})
        row.update(case_inventory=list(bench.CASES),case_filters=list(bench.CASES),results={},checked_values=bench.CHECKED_VALUES)
        sources[side]=row
    prepared={'threads':1,'source_validations':sources,'inventory':list(bench.CASES),
              'exact_validations':{},'commands':[],
              'golden_sha256':{side:bench.sha256(folder/('reference.npz'if side=='original'else side+'-reference.npz'))for side in bench.SIDES}}
    (folder/'prepared-validation.json').write_text(json.dumps(prepared))
    monkeypatch.setattr(bench,'verify_build',lambda _:provenance())
    commands=[]
    def execute(command,**kwargs):
        selected=[command[i+1] for i,value in enumerate(command) if value=='--case-filter']
        assert len(selected)==1 and selected[0] in bench.CASES
        side=Path(command[0]).name.removesuffix('-python')
        golden=Path(command[command.index('--reference')+1]).name
        assert golden==('reference.npz' if side=='original' else side+'-reference.npz')
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
    assert len(commands)==len(metadata['processes'])==576
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


@pytest.mark.parametrize('kind',['cmou','cmo'])
@pytest.mark.parametrize('interleaved',[False,True])
def test_fixture_proves_chronological_groups_using_synthetic_outputs(kind,interleaved):
    bars=100;data=query.frame(2*bars,bars,True)
    values=np.tile(np.r_[np.full(14,np.nan),np.linspace(-99,99,bars-14)],2)
    if interleaved:
        order=np.arange(2*bars).reshape(2,bars).T.ravel();data=data[order];values=values[order]
    result=query.pl.DataFrame({'value':values})
    name='grouped_'+kind+'/2x100'+('_interleaved'if interleaved else'')
    row=query.fixture_coverage(name,data,result);bench.validate_coverage(name,row)
    assert row['groups']==2 and row['written_values']==172
    broken=values.copy();broken[np.flatnonzero(np.isfinite(values))[0]]=np.nan
    with pytest.raises(ValueError,match='warmup'):query.fixture_coverage(name,data,query.pl.DataFrame({'value':broken}))


@pytest.mark.parametrize('field,value',[('price_abs_max',1024.0000001),('price_abs_max',float('nan')),('groups',99),('written_values',0),('timeperiod',13),('all_inputs_finite',False)])
def test_route_gate_rejects_vacuous_or_wrong_input_metadata(field,value):
    name='grouped_cmou/100x10000';row=coverage(name);row[field]=value
    with pytest.raises(ValueError):bench.validate_coverage(name,row)


def test_legacy_price_fixture_is_byte_identical_to_historical_generator():
    rows,bars=1000,100;data=query.frame(rows,bars,True)
    rng=np.random.default_rng(260126);close=100+np.cumsum(rng.normal(0,.1,rows))
    expected=query.pl.DataFrame({'close':close,'open':close-.1,'high':close+1,'low':close-1,'volume':rng.uniform(100,1000,rows),'periods':np.full(rows,14.),'symbol':np.arange(rows)//bars})
    assert data.schema==expected.schema
    for actual,wanted in zip(data,expected):assert actual.to_numpy().tobytes()==wanted.to_numpy().tobytes()
    assert query.frame(rows,bars,False)['symbol'].to_list()==[0]*rows


def test_controller_workflow_pin_budget_and_native_scope():
    assert bench.CHILD_TIMEOUT_SECONDS==120 and bench.MEASUREMENT_BUDGET_SECONDS==7200
    manifest=json.loads(bench.MANIFEST.read_text())
    assert manifest['timed_children']==12*4*12*2==1152
    assert manifest['timed_samples']==1152*31==35712
    text=(Path(__file__).parents[1]/'.github/workflows/cmou-windows.yml').read_text()
    assert 'timeout-minutes: 180' in text
    assert bench.CANDIDATE_COMMIT in text
    assert 'codex/cmou-windows-ci' in text


def prepared_args(tmp_path,monkeypatch):
    folder=tmp_path/'threads-1';folder.mkdir()
    for name in ('reference.npz','prior-reference.npz','combined-reference.npz','candidate-reference.npz'):(folder/name).write_bytes(name.encode())
    sources={}
    for side in bench.SIDES:
        row=run(side);row.update(cpu='test CPU',profile='portable release')
        row.update(fixture_coverage={n:coverage(n) for n in bench.CASES},fixture_sha256={n:'input' for n in bench.CASES},output_sha256={n:'output-'+side for n in bench.CASES},case_inventory=list(bench.CASES),case_filters=list(bench.CASES),results={},checked_values=bench.CHECKED_VALUES)
        sources[side]=row
    prepared={'threads':1,'source_validations':sources,'inventory':list(bench.CASES),'exact_validations':{},'commands':[],
      'golden_sha256':{side:bench.sha256(folder/('reference.npz'if side=='original'else side+'-reference.npz'))for side in bench.SIDES}}
    (folder/'prepared-validation.json').write_text(json.dumps(prepared))
    monkeypatch.setattr(bench,'verify_build',lambda _:provenance())
    args=SimpleNamespace(output=tmp_path,repeats=31,rounds=12,candidate_commit='3'*40)
    for side in bench.SIDES:
        setattr(args,side+'_python',Path('/'+side+'-python'));setattr(args,side+'_source',tmp_path)
    return args,folder


def test_timeout_preserves_partial_logs_and_refuses_partial_campaign(tmp_path,monkeypatch):
    args,folder=prepared_args(tmp_path,monkeypatch)
    def timeout(command,**kwargs):
        assert kwargs['timeout']==120
        kwargs['stdout'].write('partial child output\n');kwargs['stderr'].write('partial child failure\n')
        raise bench.subprocess.TimeoutExpired(command,120)
    monkeypatch.setattr(bench.subprocess,'run',timeout)
    with pytest.raises(bench.subprocess.TimeoutExpired):bench.run_setting(args,1,None)
    label='case-001-original-1'
    assert (folder/(label+'.stdout.log')).read_text()=='partial child output\n'
    assert (folder/(label+'.stderr.log')).read_text()=='partial child failure\n'
    assert json.loads((folder/(label+'-failure.json')).read_text())['partial_campaign_is_not_success']
    assert not (folder/'summary.json').exists()


def test_exhausted_measurement_budget_starts_no_child(tmp_path,monkeypatch):
    args,folder=prepared_args(tmp_path,monkeypatch);args.measurement_deadline=1
    monkeypatch.setattr(bench.time,'monotonic',lambda:2)
    calls=[];monkeypatch.setattr(bench.subprocess,'run',lambda *a,**k:calls.append(a))
    with pytest.raises(ValueError,match='budget exhausted'):bench.run_setting(args,1,None)
    assert not calls and not (folder/'summary.json').exists()


@pytest.mark.parametrize('options',[[],['--exact-reference'],['--reference','golden.npz']])
def test_timed_cli_requires_exact_own_golden_before_allocating(tmp_path,monkeypatch,options):
    argv=['probe','--output',str(tmp_path/'out.json'),'--source-root',str(tmp_path),'--label','test','--case-filter',bench.CASES[0],*options]
    monkeypatch.setattr(query.sys if hasattr(query,'sys') else sys,'argv',argv)
    calls=[];monkeypatch.setattr(query,'cases',lambda *a,**k:calls.append(a))
    with pytest.raises(SystemExit):query.main()
    assert not calls


def test_wrong_finite_golden_aborts_before_any_timer_or_warmup(tmp_path,monkeypatch):
    data=query.frame(64,1000,False);values=np.arange(64,dtype=float);values[:14]=np.nan;expected=query.pl.DataFrame({'value':values})
    # A pure Polars expression makes this a controller-only gate; no product kernel runs.
    index=query.pl.int_range(0,query.pl.len());expr=query.pl.when(index<14).then(query.pl.lit(float('nan'))).otherwise(index.cast(query.pl.Float64)).alias('value')
    numeric=expected.to_series().to_numpy().copy();numeric[-1]+=1.
    name=bench.CASES[0];golden=tmp_path/'bad.npz'
    np.savez_compressed(golden,**{name+'_schema':np.array(str(expected.schema)),name+'_0':numeric,name+'_0_null':np.zeros(64,bool)})
    monkeypatch.setattr(sys,'argv',['probe','--output',str(tmp_path/'out.json'),'--source-root',str(tmp_path),'--label','test','--case-filter',name,'--reference',str(golden),'--exact-reference'])
    monkeypatch.setattr(query,'cases',lambda *a,**k:iter([(name,data,[expr])]))
    calls=[]
    def forbidden():calls.append(True);raise AssertionError('timer must not run')
    monkeypatch.setattr(query.time,'perf_counter_ns',forbidden)
    with pytest.raises(AssertionError):query.main()
    assert not calls


def test_final_raw_hash_is_required_independently_of_final_flag():
    row=run();row['final_output_sha256']={bench.CASES[0]:'changed'}
    with pytest.raises(ValueError,match='final selected'):bench.validate_report(row,'prior',1,provenance(),bench.CASES[0])


def test_unset_or_wrong_candidate_pin_aborts_before_runtime_queries(monkeypatch):
    monkeypatch.setattr(bench,'identity',lambda *_:(_ for _ in ()).throw(AssertionError('runtime must not load')))
    for pin in ['UNSET_CANDIDATE_CMOU_ZIP','main','a'*40]:
        if pin==bench.CANDIDATE_COMMIT and len(pin)==40:continue
        with pytest.raises(ValueError,match='reviewed immutable pins'):bench.record_build(SimpleNamespace(candidate_commit=pin))


def test_source_boundary_rejects_other_changes_and_unreviewed_helper(tmp_path,monkeypatch):
    roots=[tmp_path/'before',tmp_path/'after']
    names=['src/native.rs','src/compat.rs','src/compat/guarded.rs','src/generated.rs','src/params.rs','src/missing.rs','src/utils.rs','Cargo.toml','Cargo.lock','src/compat/cmou.rs']
    for root in roots:
        for name in names:(root/name).parent.mkdir(parents=True,exist_ok=True);(root/name).write_text(name)
    (roots[1]/names[-1]).write_text('changed helper')
    args=SimpleNamespace(combined_source=roots[0],candidate_source=roots[1])
    with pytest.raises(ValueError,match='reviewed baseline'):bench.native_source_boundary(args)
    monkeypatch.setattr(bench,'BASELINE_HELPER_SHA256',bench.sha256(roots[0]/names[-1]))
    real_sha=bench.sha256
    monkeypatch.setattr(bench,'sha256',lambda p:bench.CANDIDATE_HELPER_SHA256 if Path(p)==roots[1]/names[-1] else real_sha(p))
    assert bench.native_source_boundary(args)['changed_files']==['src/compat/cmou.rs']
    (roots[1]/'src/native.rs').write_text('wrong route')
    with pytest.raises(ValueError,match='only the reviewed'):bench.native_source_boundary(args)


def test_raw_input_snapshots_roundtrip_signed_bits_and_deduplicate(tmp_path):
    import cmou_windows_inputs as inputs
    data=query.frame(200,100,True);key=inputs.digest_frame(data)
    record=inputs.preserve(data,tmp_path,key)
    assert inputs.preserve(data,tmp_path,key)==record
    assert inputs.validate(tmp_path,{'a':record,'b':record},{'a':key,'b':key})==1
    assert len(list(tmp_path.glob('*.arrow')))==1
    restored=query.pl.read_ipc(tmp_path/record['file'],memory_map=False)
    for actual,expected in zip(restored,data):assert actual.to_numpy().tobytes()==expected.to_numpy().tobytes()


@pytest.mark.parametrize('change',['bytes','schema','rows','file','sha','map','symlink'])
def test_raw_input_snapshots_reject_changed_or_unbound_material(tmp_path,change):
    import cmou_windows_inputs as inputs
    data=query.frame(100,100,False);key=inputs.digest_frame(data)
    record=inputs.preserve(data,tmp_path,key);expected={'a':key};records={'a':copy.deepcopy(record)}
    if change=='bytes':records['a']['bytes']+=1
    elif change=='schema':records['a']['schema']='wrong'
    elif change=='rows':records['a']['rows']-=1
    elif change=='file':records['a']['file']='../escape.arrow'
    elif change=='sha':records['a']['sha256']='f'*64
    elif change=='map':expected['a']='e'*64
    else:
        path=tmp_path/record['file'];target=tmp_path/'target';path.rename(target);path.symlink_to(target)
    with pytest.raises(ValueError):inputs.validate(tmp_path,records,expected)


def test_timed_child_is_forbidden_to_write_raw_inputs():
    row=run();row['input_snapshots']={bench.CASES[0]:{'file':'not allowed'}}
    with pytest.raises(ValueError,match='timed child'):bench.validate_report(row,'prior',1,provenance(),bench.CASES[0])


def test_raw_input_helper_is_bound_to_controller_provenance():
    assert bench.script_records()['cmou_windows_inputs.py']==bench.sha256(Path(bench.__file__).with_name('cmou_windows_inputs.py'))


def test_tolerant_C_query_comparison_still_rejects_both_zero_sign_change():
    with pytest.raises(AssertionError):
        query.compare_arrays(np.array([-0.]),np.array([False]),np.array([0.]),np.array([False]),exact=False)


def test_all_four_own_goldens_and_three_native_pairs_prepare_without_timer(tmp_path,monkeypatch):
    monkeypatch.setattr(bench,'verify_build',lambda _:provenance());commands=[]
    def execute(command,**kwargs):
        side=Path(command[0]).name.removesuffix('-python');names=[command[i+1]for i,x in enumerate(command)if x=='--case-filter']
        assert names==list(bench.CASES) and '--check-only'in command
        row=run(side);row.update(cpu='test CPU',profile='portable release',case_inventory=names,case_filters=names,results={},
              fixture_sha256={n:'sameinput'for n in names},output_sha256={n:'output-'+side for n in names},fixture_coverage={n:coverage(n)for n in names},
              checked_values=bench.CHECKED_VALUES if '--reference'in command else 0,exact_reference='--exact-reference'in command,
              input_snapshots={},final_output_checked=False,final_output_sha256={})
        if '--write-reference'in command:Path(command[command.index('--write-reference')+1]).write_bytes(('own-'+side).encode())
        Path(command[command.index('--output')+1]).write_text(json.dumps(row));commands.append(command)
    monkeypatch.setattr(bench.subprocess,'run',execute)
    args=SimpleNamespace(output=tmp_path,repeats=31,rounds=12,candidate_commit='a'*40)
    for side in bench.SIDES:
        setattr(args,side+'_python',Path('/'+side+'-python'));setattr(args,side+'_source',tmp_path)
    prepared=bench.run_setting(args,1,None,prepare_only=True)
    assert len(commands)==7 and list(prepared['golden_sha256'])==list(bench.SIDES)
    assert [Path(c[0]).name.removesuffix('-python')for c in commands[:4]]==list(bench.SIDES)
    assert all('--write-reference'in c for c in commands[:4]) and all('--exact-reference'in c for c in commands[4:])
    assert set(prepared['exact_validations'])=={'prior_vs_combined','prior_vs_candidate','combined_vs_candidate'}


def test_corpus_pair_identity_cannot_be_satisfied_by_wrong_reference_arm(tmp_path):
    folder=corpus_fixture(tmp_path);path=folder/'original-vs-candidate.json';row=json.loads(path.read_text())
    row['baseline']=str(folder/'prior.npz');row['baseline_sha256']=bench.sha256(folder/'prior.npz');path.write_text(json.dumps(row))
    with pytest.raises(ValueError,match='capture changed'):bench.corpus_gate(tmp_path)


def test_fresh_workflow_envs_include_public_test_C_oracle_and_fixed_numpy():
    text=(Path(__file__).parents[1]/'.github/workflows/cmou-windows.yml').read_text()
    # The candidate public regression module imports talib; this command creates
    # every fresh arm environment before that module runs.
    install=next(line for line in text.splitlines()if 'uv pip install --python "envs/$side"'in line and 'maturin=='in line)
    assert "'TA-Lib==0.8.1'"in install and "'numpy==2.5.3'"in install
    assert 'for side in prior combined candidate original; do'in text
    assert 'candidate-uniform-public-tests'not in text
    assert 'cmou_windows_benchmark.py --validate-only'in text


def test_cfg_counter_requires_three_guards_before_and_zero_after():
    import cmou_windows_codegen as codegen
    # A source-like normal iteration has two input checks and one output check.
    baseline=[(0x10,'cmp','%rax,%rbx'),(0x11,'jae','40'),(0x12,'addsd','%xmm1,%xmm0'),(0x13,'cmp','%rax,%rcx'),(0x14,'jae','40'),(0x15,'subsd','%xmm2,%xmm0'),(0x16,'cmp','%rax,%rdx'),(0x17,'jae','40'),(0x18,'movsd','%xmm0,(%rsi)'),(0x19,'inc','%rax'),(0x1a,'jne','10'),(0x1b,'ret',''),(0x40,'call','60 <panic_bounds_check>')]
    candidate=[(0x10,'addsd','%xmm1,%xmm0'),(0x11,'subsd','%xmm2,%xmm0'),(0x12,'movsd','%xmm0,(%rsi)'),(0x13,'inc','%rax'),(0x14,'jne','10'),(0x15,'ret','')]
    assert codegen.analyze(baseline,{0x60:'panic_bounds_check'},{},'prior')['guards']['normal_iteration_guard_counts']==[3,3]
    assert codegen.analyze(candidate,{},{} ,'candidate')['guards']['normal_iteration_guard_counts']==[0,0]
    for rows,side in ((baseline,'candidate'),(candidate,'combined')):
        with pytest.raises(ValueError,match='bounds guards'):codegen.analyze(rows,{0x60:'panic_bounds_check'},{},side)
    unknown=candidate.copy();unknown[1]=(0x11,'call','99 <unknown_target>')
    with pytest.raises(ValueError):codegen.analyze(unknown,{},{} ,'candidate')
    with pytest.raises(ValueError,match='not unique'):codegen.analyze([(1,'ret','')],{},{} ,'candidate')


def test_cfg_alternative_output_branches_count_one_not_two():
    import cmou_windows_codegen as codegen
    rows=[(0x10,'cmp','%rax,%rbx'),(0x11,'jae','70'),(0x12,'addsd','%xmm1,%xmm0'),(0x13,'cmp','%rax,%rcx'),(0x14,'jae','70'),(0x15,'test','%r8,%r8'),(0x16,'je','20'),(0x17,'cmp','%rax,%rdx'),(0x18,'jae','70'),(0x19,'movsd','%xmm0,(%rsi)'),(0x1a,'jmp','24'),(0x20,'cmp','%rax,%rdx'),(0x21,'jae','70'),(0x22,'movsd','%xmm1,(%rsi)'),(0x23,'jmp','24'),(0x24,'inc','%rax'),(0x25,'jne','10'),(0x26,'ret',''),(0x70,'call','90 <panic_bounds_check>')]
    result=codegen.analyze(rows,{0x90:'panic_bounds_check'},{},'combined')
    assert len(result['guards']['static_guard_sites'])==4 and result['guards']['normal_iteration_guard_counts']==[3,3]


def test_codegen_symbol_requires_real_unique_compat_kernel():
    import cmou_windows_codegen as codegen
    name=codegen.PREFIX+'17implCompatCore4cmou17h012abcE'
    row=f'  1: 0000000000000010 64 FUNC LOCAL DEFAULT 1 {name}\n'
    assert codegen.select_symbols(row,[(0x10,0x90)])==(0x10,64,name)
    wrong=row.replace(codegen.PREFIX,'_ZN6ta_lib7ta_func4cmou')
    for text,segments in ((wrong,[(0,1000)]),(row,[(0x20,0x90)]),(row+row.replace('0010','0080'),[(0,1000)]),(row+' 2: 0000000000000020 64 FUNC LOCAL DEFAULT 1 other\n',[(0,1000)])):
        with pytest.raises(ValueError):codegen.select_symbols(text,segments)


def test_codegen_rejects_non_linux_and_instruction_gaps(tmp_path):
    import cmou_windows_codegen as codegen
    from cmou_windows_cfg import parse_instructions
    bad=tmp_path/'arm.so';bad.write_bytes(b'not a Linux ELF object')
    with pytest.raises(ValueError,match='actual normal Linux'):codegen.inspect(bad,tmp_path/'out','candidate')
    with pytest.raises(ValueError,match='instruction bytes'):parse_instructions(' 10: 90 nop\n 12: c3 ret',0x10,3)


def public_fixture(tmp_path,monkeypatch):
    folder=tmp_path/'cmou-public';folder.mkdir();script=folder/'cmou_window_probe.py';script.write_text('frozen probe')
    monkeypatch.setattr(bench,'PUBLIC_PROBE_SHA256',bench.sha256(script))
    # Only metadata is synthetic here; the frozen source-owned child performs
    # the actual numerical comparisons in CI before these report bindings pass.
    successes={str(i):{'rows':93+(i<652),'schema':'Float64','key':str(i)}for i in range(1576)}
    # 1576*93+652=147220.
    cases={**successes,**{'error'+str(i):{'error':'ComputeError'}for i in range(408)}}
    for side in bench.SIDES:
        ident=identities()[side]
        metadata={'cases':cases,'input_sha256':{name:'input'for name in cases},'native_sha256':side,'polars':ident['polars'],'numpy':ident['numpy'],'talib':ident['talib']}
        np.savez_compressed(folder/(side+'.npz'),metadata=np.array(json.dumps(metadata)))
    for before,after in bench.PAIRS.values():
        exact=before!='original';name=before+'-vs-'+after+('-exact'if exact else'')
        row={'cases':1984,'checked_values':147220,'exact':exact,'max_absolute_difference':0.,'zero_sign_policy':'both-zero exact','nan_payload_policy':'positions exact; NaN sign/payload excluded','baseline':before,'candidate':after,'baseline_sha256':bench.sha256(folder/(before+'.npz')),'candidate_sha256':bench.sha256(folder/(after+'.npz'))}
        (folder/(name+'.json')).write_text(json.dumps(row))
    return folder


def test_public_probe_accepts_only_full_bound_four_arm_six_pair_inventory(tmp_path,monkeypatch):
    public_fixture(tmp_path,monkeypatch)
    assert len(bench.public_probe_gate(tmp_path,provenance()))==6


@pytest.mark.parametrize('change',['script','count','nonexact','binding','signedzero','nanpolicy','missingpair','capture'])
def test_public_probe_negative_bindings(tmp_path,monkeypatch,change):
    folder=public_fixture(tmp_path,monkeypatch);path=folder/'prior-vs-candidate-exact.json';row=json.loads(path.read_text())
    if change=='script':(folder/'cmou_window_probe.py').write_text('different source')
    elif change=='count':row['checked_values']-=1
    elif change=='nonexact':row['max_absolute_difference']=1e-16
    elif change=='binding':row['baseline']='combined'
    elif change=='signedzero':row['zero_sign_policy']='tolerance'
    elif change=='nanpolicy':row['nan_payload_policy']='ignore'
    elif change=='missingpair':(folder/'original-vs-prior.json').unlink()
    else:
        with np.load(folder/'candidate.npz',allow_pickle=False)as capture:metadata=json.loads(str(capture['metadata']))
        metadata['native_sha256']='wrong';np.savez_compressed(folder/'candidate.npz',metadata=np.array(json.dumps(metadata)))
    path.write_text(json.dumps(row))
    with pytest.raises((ValueError,FileNotFoundError)):bench.public_probe_gate(tmp_path,provenance())


def codegen_proof_fixture(tmp_path):
    folder=tmp_path/'codegen';folder.mkdir();binary=tmp_path/'actual.so';binary.write_bytes(b'actual ELF fixture')
    loop={'bounds_panic_reachable':False,'unknown_exit_or_call_reachable':False}
    proof={'side':'candidate','gate':True,'binary':str(binary),'binary_sha256':bench.sha256(binary),'guards':{'normal_iteration_guard_counts':[0,0]},'output_loop':loop,'analysis':{'cyclic_cfgs':[loop]}}
    for name in('symbols.txt','segments.txt','relocations.txt','cmou.asm'):(folder/name).write_text(name)
    (folder/'report.json').write_text(json.dumps(proof));proof['files']={str(p):bench.sha256(p)for p in folder.iterdir()}
    return proof,{str(binary):bench.sha256(binary)}


def test_normal_codegen_metadata_and_all_retained_files_bound(tmp_path):
    proof,retained=codegen_proof_fixture(tmp_path);bench.verify_codegen_proof(proof,'candidate',retained)


@pytest.mark.parametrize('change',['binary','side','guards','gate','panic','unknown','missing','substitute','bytes','metadata','symlink'])
def test_codegen_proof_negative_bindings(tmp_path,change):
    proof,retained=codegen_proof_fixture(tmp_path)
    if change=='binary':proof['binary']=str(tmp_path/'different.so')
    elif change=='side':proof['side']='prior'
    elif change=='guards':proof['guards']['normal_iteration_guard_counts']=[1,1]
    elif change=='gate':proof['gate']=False
    elif change=='panic':proof['output_loop']['bounds_panic_reachable']=True
    elif change=='unknown':proof['output_loop']['unknown_exit_or_call_reachable']=True
    elif change=='missing':proof['files'].pop(next(p for p in proof['files']if p.endswith('symbols.txt')))
    elif change=='substitute':
        proof['files'].pop(next(p for p in proof['files']if p.endswith('symbols.txt')));p=tmp_path/'other.txt';p.write_text('fake');proof['files'][str(p)]=bench.sha256(p)
    elif change=='bytes':next(Path(p)for p in proof['files']if p.endswith('cmou.asm')).write_text('changed')
    elif change=='metadata':proof['extra']='not in the retained report'
    else:
        p=next(Path(p)for p in proof['files']if p.endswith('cmou.asm'));target=p.with_name('target');p.rename(target);p.symlink_to(target)
    with pytest.raises(ValueError):bench.verify_codegen_proof(proof,'candidate',retained)


def frozen_pin_fixture(monkeypatch):
    monkeypatch.setattr(bench,'CANDIDATE_COMMIT','a'*40)
    monkeypatch.setattr(bench,'CANDIDATE_HELPER_SHA256','b'*64)
    monkeypatch.setattr(bench,'PUBLIC_PROBE_SHA256','c'*64)
    return {**{side.upper()+'_COMMIT':pin for side,pin in bench.fixed_pins('a'*40).items()},'CANDIDATE_HELPER_SHA256':'b'*64,'PUBLIC_PROBE_SHA256':'c'*64}


def test_workflow_prebuild_pins_match_frozen_controller(monkeypatch):
    env=frozen_pin_fixture(monkeypatch);assert bench.workflow_pins(env)==bench.fixed_pins('a'*40)


@pytest.mark.parametrize('key',['ORIGINAL_COMMIT','PRIOR_COMMIT','COMBINED_COMMIT','CANDIDATE_COMMIT','CANDIDATE_HELPER_SHA256','PUBLIC_PROBE_SHA256'])
def test_wrong_workflow_hex_pin_fails_even_if_well_formed(monkeypatch,key):
    env=frozen_pin_fixture(monkeypatch);env[key]='d'*len(env[key])
    with pytest.raises(ValueError):bench.workflow_pins(env)


def test_workflow_and_synthetic_gates_bound_in_controller_record():
    records=bench.script_records();root=Path(bench.__file__).resolve().parents[1]
    for relative in('tests/test_cmou_windows_benchmark.py','.github/workflows/cmou-windows.yml'):
        assert records[relative]==bench.sha256(root/relative)
    workflow=(root/'.github/workflows/cmou-windows.yml').read_text()
    assert workflow.index('workflow_pins(os.environ)')<workflow.index('path: sources/prior')


def test_real_shape_top_exit_does_not_count_as_completed_output_iteration():
    import cmou_windows_codegen as codegen
    # Historical actual normal56 enters the SCC at a top-of-loop count/exit
    # prelude. Its direct return path writes no output and is not an iteration.
    rows=[(0x10,'cmp','%rax,%r8'),(0x11,'je','50'),(0x12,'cmp','%rax,%rbx'),(0x13,'jae','70'),(0x14,'addsd','%xmm1,%xmm0'),(0x15,'cmp','%rax,%rcx'),(0x16,'jae','70'),(0x17,'subsd','%xmm2,%xmm0'),(0x18,'cmp','%rax,%rdx'),(0x19,'jae','70'),(0x1a,'movsd','%xmm0,(%rsi)'),(0x1b,'inc','%rax'),(0x1c,'jmp','10'),(0x50,'ret',''),(0x70,'call','90 <panic_bounds_check>')]
    result=codegen.analyze(rows,{0x90:'panic_bounds_check'},{},'prior')
    assert result['guards']['normal_iteration_guard_counts']==[3,3]
    # A productive backedge path which bypasses the first check must still fail.
    bypass=rows.copy();bypass[1]=(0x11,'je','14')
    with pytest.raises(ValueError,match='bounds guards'):codegen.analyze(bypass,{0x90:'panic_bounds_check'},{},'prior')


def test_productive_final_exit_with_two_guards_is_rejected():
    import cmou_windows_codegen as codegen
    rows=[(0x10,'cmp','%rax,%rbx'),(0x11,'jae','70'),(0x12,'addsd','%xmm1,%xmm0'),(0x13,'cmp','%rax,%rcx'),(0x14,'jae','70'),(0x15,'test','%r8,%r8'),(0x16,'je','40'),(0x17,'cmp','%rax,%rdx'),(0x18,'jae','70'),(0x19,'movsd','%xmm0,(%rsi)'),(0x1a,'jmp','10'),(0x40,'movsd','%xmm0,(%rsi)'),(0x41,'ret',''),(0x70,'call','90 <panic_bounds_check>')]
    # The final productive exit is outside the SCC. The instruction-scoped
    # verifier must count its store and two guards too, never waive that path.
    with pytest.raises(ValueError):codegen.analyze(rows,{0x90:'panic_bounds_check'},{},'prior')


@pytest.mark.parametrize('change',['zero_backedge','multiple_stores','unsupported_store'])
def test_unproductive_or_multiple_output_backedge_is_not_accepted(change):
    import cmou_windows_codegen as codegen
    rows=[(0x10,'addsd','%xmm1,%xmm0'),(0x11,'test','%rax,%rax'),(0x12,'je','17'),(0x13,'movsd','%xmm0,(%rsi)'),(0x14,'subsd','%xmm2,%xmm0'),(0x15,'jmp','17'),(0x17,'jne','10'),(0x18,'ret','')]
    if change=='multiple_stores':rows[1]=(0x11,'movq','$0x0,(%rsi)')
    elif change=='unsupported_store':rows[3]=(0x13,'movupd','%xmm0,(%rsi)')
    with pytest.raises(ValueError):codegen.analyze(rows,{},{} ,'candidate')


@pytest.mark.parametrize('kind',['copy_sret','clobber_sret','lea_sret','swapped_output','unknown_store','narrow_zero','implicit_string'])
def test_result_metadata_role_is_not_a_generic_address_exemption(kind):
    import cmou_windows_codegen as codegen
    rows=[(0x10,'addsd','%xmm1,%xmm0'),(0x11,'movsd','%xmm0,(%rsi)'),(0x12,'jne','10'),(0x13,'movq','%rax,0x8(%rdi)'),(0x14,'movq','%rcx,0x10(%rdi)'),(0x15,'movw','%ax,(%rdi)'),(0x16,'ret','')]
    assert codegen.analyze(rows,{},{} ,'candidate')['guards']['normal_iteration_guard_counts']==[0,0]
    replacement={'copy_sret':('movq','%rdi,%rax'),'clobber_sret':('movq','%rsi,%rdi'),'lea_sret':('leaq','0x8(%rdi),%rax'),'swapped_output':('movsd','%xmm0,(%rdi)'),'unknown_store':('movq','%rax,(%rsi)'),'narrow_zero':('movl','$0x0,(%rsi)'),'implicit_string':('stosq','')}[kind]
    rows.insert(-1,(0x15_1,*replacement))
    # Keep addresses strictly ordered to model real instruction decoding.
    rows=[(i+0x10,op,args)for i,(_,op,args)in enumerate(rows)]
    # The backedge address is the unchanged first instruction at0x10.
    with pytest.raises(ValueError):codegen.analyze(rows,{},{} ,'candidate')


def test_outside_guard_with_productive_successor_is_fully_traversed():
    import cmou_windows_codegen as codegen
    rows=[(0x10,'cmp','%rax,%rbx'),(0x11,'jae','70'),(0x12,'addsd','%xmm1,%xmm0'),(0x13,'cmp','%rax,%rcx'),(0x14,'jae','70'),(0x15,'test','%r8,%r8'),(0x16,'je','40'),(0x17,'cmp','%rax,%rdx'),(0x18,'jae','70'),(0x19,'movsd','%xmm0,(%rsi)'),(0x1a,'jmp','10'),(0x40,'cmp','%rax,%rdx'),(0x41,'jae','70'),(0x42,'movsd','%xmm0,(%rsi)'),(0x43,'ret',''),(0x70,'call','90 <panic_bounds_check>')]
    proof=codegen.analyze(rows,{0x90:'panic_bounds_check'},{},'prior')
    assert proof['guards']['normal_iteration_guard_counts']==[3,3]
    assert {'bounds_guards':3,'output_stores':1,'end':'exit'}in proof['guards']['path_outcomes']


def test_actual_objdump_command_requests_explicit_att_widths_and_retains_bytes(tmp_path,monkeypatch):
    import cmou_windows_codegen as codegen
    binary=tmp_path/'actual.so';header=bytearray(20);header[:6]=b'\x7fELF\x02\x01';header[16:18]=(3).to_bytes(2,'little');header[18:20]=(62).to_bytes(2,'little');binary.write_bytes(header)
    name=codegen.PREFIX+'17implCompatCore4cmou17h012abcE'
    symbols=f' 1: 0000000000000010 22 FUNC LOCAL DEFAULT 1 {name}\n'
    asm=''' 10: f2 0f 58 c1 addsd %xmm1,%xmm0
 14: f2 0f 11 06 movsd %xmm0,(%rsi)
 18: 75 f6 jne 10
 1a: 48 89 47 08 movq %rax,0x8(%rdi)
 1e: 48 89 4f 10 movq %rcx,0x10(%rdi)
 22: 66 89 07 movw %ax,(%rdi)
 25: c3 retq
'''
    commands=[]
    def execute(command,**kwargs):
        commands.append(command)
        if command[:2]==['readelf','-sW']:return symbols
        if command[:2]==['readelf','-lW']:return ' LOAD 0x0 0x10 0x10 0x16 0x16 R E 0x1000\n'
        if command[:2]==['readelf','-rW']:return ''
        assert command==['objdump','-d','-w','-M','att,suffix','--disassemble='+name,str(binary)]
        return asm
    monkeypatch.setattr(codegen.subprocess,'check_output',execute)
    proof=codegen.inspect(binary,tmp_path/'codegen','candidate')
    assert proof['instruction_count']==7 and proof['size']==22
    assert (tmp_path/'codegen/cmou.asm').read_text()==asm
    assert proof['guards']['path_outcomes']==[{'bounds_guards':0,'output_stores':1,'end':'backedge'},{'bounds_guards':0,'output_stores':1,'end':'exit'}]
    # Same known instruction bytes, rendered without explicit widths, must not
    # broaden the source-role detector through ad-hoc mnemonic inference.
    rows=codegen.parse_instructions(asm.replace('movq','mov').replace('movw','mov'),0x10,22)
    with pytest.raises(ValueError,match='outside-loop nonstack store'):codegen.analyze(rows,{},{} ,'candidate')
    # Raw byte coverage remains strict even with the requested format flag.
    with pytest.raises(ValueError,match='instruction bytes'):codegen.parse_instructions(asm.replace('66 89 07','66 89'),0x10,22)
