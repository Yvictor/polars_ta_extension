"""Focused ablation protocol rejection tests; never run a performance campaign."""
from collections import Counter
import copy,importlib,json,sys,zipfile,struct
from pathlib import Path
from types import SimpleNamespace
import numpy as np
import pytest
sys.path.insert(0,str(Path(__file__).parents[1]/'scripts'))
bench=importlib.import_module('add_shared_route_benchmark')
query=importlib.import_module('add_shared_route_query')
prov=importlib.import_module('add_shared_route_provenance')
def coverage(name):return {**bench.expected_coverage(name),'price_abs_max':101.}


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
            'fixture_coverage':{name:coverage(name)},'fixture_sha256':{name:'input'},'output_sha256':{name:'output-'+side},'input_snapshots':{},'final_output_checked':True,'final_output_sha256':{name:'output-'+side},
            'case_filters':[name],'case_inventory':[name],'checked_values':bench.case_values(name),'exact_reference':True,
            'results':{name:{'samples_ms':[1.]*31,'min_ms':1.,'median_ms':1.,'minor_faults':[0]*31,'major_faults':[0]*31}}}


def test_orders_balance_all_positions_and_directed_within_round_transitions():
    orders=bench.ORDERS*3
    assert len(orders)==12 and len(set(orders))==4
    for position in range(4):
        assert Counter(order[position] for order in orders)=={side:3 for side in bench.SIDES}
    transitions=Counter((a,b) for order in orders for a,b in zip(order,order[1:]))
    assert transitions=={(a,b):3 for a in bench.SIDES for b in bench.SIDES if a!=b}


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
    assert len(commands)==len(metadata['processes'])==1104
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
    monkeypatch.setattr(query,'fixture_coverage',lambda *a:coverage(name))
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


def test_raw_input_snapshots_roundtrip_signed_bits_and_deduplicate(tmp_path):
    import add_shared_route_inputs as inputs
    data=query.frame(200,100,True);key=inputs.digest_frame(data)
    record=inputs.preserve(data,tmp_path,key)
    assert inputs.preserve(data,tmp_path,key)==record
    assert inputs.validate(tmp_path,{'a':record,'b':record},{'a':key,'b':key})==1
    assert len(list(tmp_path.glob('*.arrow')))==1
    restored=query.pl.read_ipc(tmp_path/record['file'],memory_map=False)
    for actual,expected in zip(restored,data):assert actual.to_numpy().tobytes()==expected.to_numpy().tobytes()


@pytest.mark.parametrize('change',['bytes','schema','rows','file','sha','map','symlink'])
def test_raw_input_snapshots_reject_changed_or_unbound_material(tmp_path,change):
    import add_shared_route_inputs as inputs
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
    assert bench.script_records()['add_shared_route_inputs.py']==bench.sha256(Path(bench.__file__).with_name('add_shared_route_inputs.py'))


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
    text=(Path(__file__).parents[1]/'.github/workflows/add-shared-route.yml').read_text()
    # The candidate public regression module imports talib; this command creates
    # every fresh arm environment before that module runs.
    install=next(line for line in text.splitlines()if 'uv pip install --python "envs/$side"'in line and 'maturin=='in line)
    assert "'TA-Lib==0.8.1'"in install and "'numpy==2.5.3'"in install
    assert 'for side in prior combined candidate original; do'in text
    assert '--benchmark-disable' in text and '12479 passed' in text
    assert 'add_shared_route_benchmark.py --validate-only'in text


def test_fixed23_inventory_covers_each_prior_loss_and_retained_tradeoffs():
    m=json.loads(bench.MANIFEST.read_text());names=list(bench.CASES)
    expected_losses=['grouped_cmou/100x10000','grouped_ppo/10000x100','grouped_cmou/10000x100','grouped_ppo/2000x100_interleaved','grouped_ema/50000x20','mavp/1000000','cmou/1000000','grouped_mix8/10000x100','grouped_ema/2000x100_interleaved','grouped_atr/2000x100_interleaved','grouped_correl/2000x100_interleaved']
    assert m['primary_loss_queries']==expected_losses
    assert names==m['primary_loss_queries']+m['retained_positive_tradeoff_queries']+m['pure_Polars_controls']
    assert len(names)==len(set(names))==23 and len(m['retained_positive_tradeoff_queries'])==7 and len(m['pure_Polars_controls'])==5
    assert sum(bench.case_values(n)for n in names)==bench.CHECKED_VALUES==27200000
    assert m['timed_children']==23*4*12*2==2208 and m['timed_samples']==2208*31==68448
    assert list(bench.requested_inventory())==names
    for diagnostic,filters in [(True,[]),(False,['*'])]:
        with pytest.raises(ValueError):bench.requested_inventory(diagnostic,filters)


def test_multioutput_and_short_empty_ranges_are_not_one_field_or_vacuous_writes():
    c=bench.expected_coverage('grouped_mix8/10000x100')
    assert c['output_fields']==10 and c['lookbacks']==[29,14,33,33,33,14,27,13,4,25]
    assert bench.case_values(c['case'])==10000000
    short=bench.expected_coverage('grouped_ema/50000x20')
    assert short['lookbacks']==[29]and short['written_values']==[0]
    assert bench.expected_coverage('cdlengulfing/1000000')['dtypes']==['Int32']


@pytest.mark.parametrize('selected,uniform',[('cmou/1000000',False),('add/1000000',False),('mavp_one/1000000',True)])
def test_selector_constructs_no_sibling_frame_or_indicator(monkeypatch,selected,uniform):
    seen=[];indicators=[]
    def frame(rows,bars,uniform=False):seen.append((rows,bars,uniform));return object()
    monkeypatch.setattr(query,'frame',frame)
    def indicator(n):indicators.append(n);return SimpleNamespace(alias=lambda _:n)
    monkeypatch.setattr(query,'indicator',indicator)
    results=list(query.cases(filters=[selected]))
    assert len(results)==1 and results[0][0]==selected
    assert seen==[(1000000,1000,uniform)]and indicators==[selected.split('/')[0]]


@pytest.mark.parametrize('field,value',[('output_fields',1),('lookbacks',[29]*10),('written_values',[0]*10),('groups',True),('uniform_period14',True),('price_abs_max',1024.1),('price_abs_max',float('nan'))])
def test_mixed_schema_range_and_guard_coverage_is_strict(field,value):
    name='grouped_mix8/10000x100';row=coverage(name);row[field]=value
    with pytest.raises(ValueError):bench.validate_coverage(name,row)


def elf_header():
    data=bytearray(64);data[:7]=b'\x7fELF\x02\x01\x01';struct.pack_into('<HHI',data,16,3,62,1);struct.pack_into('<H',data,52,64)
    return data


@pytest.mark.parametrize('change',['short','class','endian','version','kind','arch','ehsize'])
def test_actual_ELF_requires_full_native_x86_64_shared_header(tmp_path,change):
    p=tmp_path/'product.so';data=elf_header();p.write_bytes(data);assert prov.elf_record(p)['sha256']==prov.sha256(p)
    if change=='short':data=data[:20]
    elif change=='class':data[4]=1
    elif change=='endian':data[5]=2
    elif change=='version':data[6]=0
    elif change=='kind':struct.pack_into('<H',data,16,1)
    elif change=='arch':struct.pack_into('<H',data,18,183)
    else:struct.pack_into('<H',data,52,20)
    p.write_bytes(data)
    with pytest.raises(ValueError):prov.elf_record(p)


@pytest.mark.parametrize('change',['other_name','comment_name','ignored','failed','two_tests','no_list','twice_list'])
def test_cold_dispatch_gate_requires_actual_exact_full_namespace(tmp_path,change):
    listing=tmp_path/'list.log';runlog=tmp_path/'cold.log';name=prov.COLD_TEST
    listing.write_text(name+': test\n');text='running 1 test\ntest '+name+' ... ok\ntest result: ok. 1 passed; 0 failed; 0 ignored; 41 filtered out; finished in 0.01s\n'
    runlog.write_text(text);assert prov.require_cold_dispatch(listing,runlog)['exact_full_namespace']
    if change=='other_name':text=text.replace('test '+name+' ... ok','test unrelated ... ok')
    elif change=='comment_name':text=text.replace('test '+name+' ... ok','# test '+name+' ... ok')
    elif change=='ignored':text=text.replace('0 ignored','1 ignored')
    elif change=='failed':text=text.replace('0 failed','1 failed')
    elif change=='two_tests':text=text.replace('running 1 test','running 2 tests')
    elif change=='no_list':listing.write_text('other: test\n')
    else:listing.write_text((name+': test\n')*2)
    runlog.write_text(text)
    with pytest.raises(ValueError):prov.require_cold_dispatch(listing,runlog)


@pytest.mark.parametrize('extra',['src/compat/cmou.rs','src/params.rs','src/sarext_legacy.rs','Cargo.toml'])
def test_source_boundary_allows_only_the_reviewed_native_adapter(tmp_path,monkeypatch,extra):
    roots=[tmp_path/'before',tmp_path/'after'];required=['src/native.rs','src/compat.rs','src/compat/guarded.rs','src/generated.rs','src/params.rs','src/missing.rs','src/utils.rs','Cargo.toml','Cargo.lock','src/compat/cmou.rs','src/sarext_legacy.rs']
    for root in roots:
        for name in required:(root/name).parent.mkdir(parents=True,exist_ok=True);(root/name).write_text(name)
    (roots[1]/'src/native.rs').write_text('reviewed native change')
    monkeypatch.setattr(bench,'BASELINE_HELPER_SHA256',bench.sha256(roots[0]/'src/native.rs'))
    monkeypatch.setattr(bench,'CANDIDATE_HELPER_SHA256',bench.sha256(roots[1]/'src/native.rs'))
    args=SimpleNamespace(combined_source=roots[0],candidate_source=roots[1]);assert bench.native_source_boundary(args)['changed_files']==['src/native.rs']
    (roots[1]/extra).write_text('unreviewed extra change')
    with pytest.raises(ValueError):bench.native_source_boundary(args)


def test_workflow_has_no_CMOU_mechanism_gate_and_only_reviewed_immutable_pins():
    text=(Path(__file__).parents[1]/'.github/workflows/add-shared-route.yml').read_text()
    assert 'CANDIDATE_COMMIT: '+bench.CANDIDATE_COMMIT in text and 'CANDIDATE_HELPER_SHA256: '+bench.CANDIDATE_HELPER_SHA256 in text
    assert 'cmou_windows_codegen'not in text and 'normal-codegen'not in text
    assert 'cancel-in-progress: false'in text and 'timeout-minutes: 180'in text
    assert '--exact --nocapture --test-threads=1'in text and '--benchmark-disable'in text
    assert bench.fixed_pins(bench.CANDIDATE_COMMIT)['candidate']==bench.CANDIDATE_COMMIT
    assert len(bench.CANDIDATE_COMMIT)==40 and len(bench.CANDIDATE_HELPER_SHA256)==64
    assert 'CARGO_INCREMENTAL'in text and 'src/lib.rs'in text

@pytest.mark.parametrize('change',['missing_plugin','unpinned_plugin','comment_only','missing_pytest'])
def test_public_test_dependency_gate_rejects_fresh_environment_without_plugin(change):
    text=(Path(__file__).parents[1]/'.github/workflows/add-shared-route.yml').read_text()
    assert prov.require_public_test_dependencies(text)
    if change=='missing_plugin':text=text.replace("'pytest-benchmark==5.3.0'",'')
    elif change=='unpinned_plugin':text=text.replace('pytest-benchmark==5.3.0','pytest-benchmark>=5')
    elif change=='missing_pytest':text=text.replace("'pytest-benchmark==5.3.0' pytest","'pytest-benchmark==5.3.0'")
    else:text=text.replace("'pytest-benchmark==5.3.0'",'')+'\n# pytest-benchmark==5.3.0\n'
    with pytest.raises(ValueError):prov.require_public_test_dependencies(text)


@pytest.mark.parametrize('key,value',[('threads',True),('repeats',True),('warmups',True),('affinity',[True])])
def test_protocol_integer_metadata_rejects_booleans(key,value):
    row=run();row[key]=value
    with pytest.raises(ValueError):bench.validate_report(row,'prior',1,provenance(),bench.CASES[0])
