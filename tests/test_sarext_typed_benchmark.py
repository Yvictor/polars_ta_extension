"""Reject incomparable SAREXT CI evidence before accepting measurements."""
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
bench=importlib.import_module('sarext_typed_benchmark')
query=importlib.import_module('sarext_typed_query')
prov=importlib.import_module('sarext_typed_provenance')


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
            'fixture_coverage':{name:{'fixture':'test'}},'fixture_sha256':{name:'input'},'output_sha256':{name:'output-'+side},'final_output_checked':True,
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
    assert len(bench.CASES)==len(set(bench.CASES))==14
    assert sum(bench.case_values(name) for name in bench.CASES)==12_400_000
    assert set(bench.CASES)=={'control_cumsum_dense/1000000', 'sarext/1000000', 'grouped_sarext/2000x100_interleaved', 'grouped_sarext_reversal/100x10000', 'sarext_reversal/1000000', 'sarext_longzero/1000000', 'grouped_sarext_reversal/10000x100', 'control_cumsum/10000x100', 'grouped_sarext_longzero/10000x100', 'grouped_sarext_reversal/2000x100_interleaved', 'grouped_sar/10000x100', 'grouped_sarext/100x10000', 'sar/1000000', 'grouped_sarext/10000x100'}
    with pytest.raises(ValueError): bench.requested_inventory(True,[])
    with pytest.raises(ValueError): bench.requested_inventory(False,['*'])
    assert bench.PRIOR_COMMIT=='56f6d5fb139031c20d86d7e818e7d267eb834295'


def test_selector_constructs_only_the_selected_case(monkeypatch):
    names=[]
    def frame(rows,bars):
        names.append((rows,bars));return object()
    monkeypatch.setattr(query,'frame',frame)
    monkeypatch.setattr(query,'indicator',lambda name:SimpleNamespace(alias=lambda _:name))
    selected='sarext/1000000'
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
    data={'results':{'1':{'comparisons':{'prior_vs_candidate':{'sar/1000000':row}}}}}
    bench.write_negatives(data,tmp_path)
    negatives=json.loads((tmp_path/'negative-cases.json').read_text())
    assert len(negatives)==1 and negatives[0]['case']=='sar/1000000'
    assert negatives[0]['after_faster_rounds']==0
    assert negatives[0]['case_role']=='shared_generic_preparation_control'
    assert negatives[0]['is_unchanged_timed_query'] is False















def test_production_controller_issues_one_exact_arm_golden_child_per_case_and_round(tmp_path,monkeypatch):
    folder=tmp_path/'threads-1';folder.mkdir()
    for name in ('reference.npz','prior-reference.npz','candidate-reference.npz','alternative-reference.npz'): (folder/name).write_bytes(name.encode())
    sources={}
    for side in bench.SIDES:
        row=run(side);row.update(cpu='test CPU',profile='portable release')
        row.update(fixture_coverage={n:{'fixture':'test'} for n in bench.CASES},fixture_sha256={n:'input' for n in bench.CASES},output_sha256={n:'output-'+side for n in bench.CASES})
        row.update(case_inventory=list(bench.CASES),case_filters=list(bench.CASES),results={},checked_values=bench.CHECKED_VALUES)
        sources[side]=row
    prepared={'threads':1,'source_validations':sources,'inventory':list(bench.CASES),
              'arm_reference_sha256':{side:bench.sha256(folder/(side+'-reference.npz')) for side in ('candidate','alternative')},'exact_validation':sources['candidate'],'commands':[],
              'reference_sha256':bench.sha256(folder/'reference.npz'),
              'prior_reference_sha256':bench.sha256(folder/'prior-reference.npz')}
    (folder/'prepared-validation.json').write_text(json.dumps(prepared))
    monkeypatch.setattr(bench,'verify_build',lambda _:provenance())
    monkeypatch.setattr(bench,'verify_inputs',lambda *args:None)
    commands=[]
    def execute(command,**kwargs):
        selected=[command[i+1] for i,value in enumerate(command) if value=='--case-filter']
        assert len(selected)==1 and selected[0] in bench.CASES
        side=Path(command[0]).name.removesuffix('-python')
        golden=Path(command[command.index('--reference')+1]).name
        assert golden==('reference.npz' if side=='original' else 'prior-reference.npz' if side=='prior' else side+'-reference.npz')
        assert '--exact-reference' in command and '--diagnostic' not in command
        row=run(side,selected[0]);row.update(cpu='test CPU',profile='portable release')
        Path(command[command.index('--output')+1]).write_text(json.dumps(row))
        commands.append((side,selected[0]))
    monkeypatch.setattr(bench.subprocess,'run',execute)
    args=SimpleNamespace(output=tmp_path,repeats=31,rounds=12,candidate_commit='3'*40,alternative_commit='4'*40)
    for side in bench.SIDES:
        setattr(args,side+'_python',Path('/'+side+'-python'))
        setattr(args,side+'_source',tmp_path)
    metadata,_=bench.run_setting(args,1,None)
    assert len(commands)==len(metadata['processes'])==672
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








def test_all_four_arm_goldens_and_all_six_comparisons_are_required():
    assert set(bench.NATIVE_SIDES)=={'prior','candidate','alternative'}
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
    assert bench.case_role('grouped_sar/10000x100')=='shared_generic_preparation_control'


inputs=importlib.import_module('sarext_typed_inputs')


def test_raw_input_capture_is_preflight_only_and_reuses_identical_physical_layout(tmp_path):
    from sarext_typed_inputs import digest_frame,preserve
    data=query.frame(64,16);key=digest_frame(data)
    assert preserve(data,tmp_path,key)==preserve(data,tmp_path,key)
    assert len(list(tmp_path.iterdir()))==1
    source=Path(query.__file__).read_text()
    assert "args.check_only and args.write_reference" in source
    # The timed child command receives only golden references, never --save-inputs.
    source=Path(bench.__file__).read_text()
    assert "child = run(side, label, '--reference', golden, '--exact-reference', selected=name)" in source



@pytest.mark.parametrize('change',['bytes','schema','path','missing','values'])
def test_retained_physical_input_mutations_are_rejected(tmp_path,change):
    from sarext_typed_inputs import digest_frame,preserve,validate
    data=query.frame(64,16);key=digest_frame(data)
    record=preserve(data,tmp_path,key)
    assert validate(tmp_path,{'a':record},{'a':key})==1
    if change=='bytes':(tmp_path/record['file']).write_bytes(b'wrong physical file')
    elif change=='schema':record['schema']='wrong schema'
    elif change=='path':record['file']='../'+record['file']
    elif change=='missing':record['fixture_sha256']='0'*64
    else:
        other=data.with_columns((query.pl.col('close')+1.).alias('close'))
        with pytest.raises(ValueError,match='fixture digest'):preserve(other,tmp_path,key)
        return
    with pytest.raises(ValueError):validate(tmp_path,{'a':record},{'a':key})



@pytest.mark.parametrize('kind',['market','reversal','longzero'])
@pytest.mark.parametrize('grouped,interleaved',[(False,False),(True,False),(True,True)])
def test_real_fixture_calls_cover_no_replay_reversal_and_long_zero_each_group(kind,grouped,interleaved):
    bars=100;rows=200 if grouped else 257
    data=query.frame(rows,bars) if kind=='market' else query.specialized_frame(rows,bars,grouped,kind)
    if interleaved:
        data=data.with_row_index('_row').with_columns((query.pl.col('_row')%bars).alias('_within')).sort('_within','symbol').drop('_row','_within')
    family='sarext' if kind=='market' else 'sarext_'+kind
    expression=query.indicator(family)
    result=data.select((expression.over('symbol') if grouped else expression).alias('value'))
    facts=query.fixture_coverage(('grouped_' if grouped else '')+family+'/unit',data,result)
    assert facts['groups']==(2 if grouped else 1)
    if kind=='longzero':assert facts['minimum_negative_zeros_per_group']>=1
    else:assert facts['negative_zero_count']==0
    if kind=='reversal':assert facts['minimum_positive_per_group']>0 and facts['minimum_negative_per_group']>0


def test_long_zero_stress_resets_before_interleaving_and_cannot_pass_only_globally():
    data=query.specialized_frame(200,100,True,'longzero').with_row_index('_row').with_columns((query.pl.col('_row')%100).alias('_within')).sort('_within','symbol').drop('_row','_within')
    for group in (0,1):
        first=np.flatnonzero(data['symbol'].to_numpy()==group)[0]
        assert data['high'].to_numpy()[first]==2. and data['low'].to_numpy().view(np.uint64)[first]==0x8000000000000000
    result=data.select(query.indicator('sarext_longzero').over('symbol')).to_series().to_numpy().copy()
    result[(data['symbol'].to_numpy()==1)&(result==0)]=0.
    assert np.any(result.view(np.uint64)==0x8000000000000000)
    with pytest.raises(ValueError,match='chronological group'):
        query.fixture_coverage('grouped_sarext_longzero/unit',data,query.pl.DataFrame({'value':result}))


def test_existing_C_finite_tolerance_does_not_hide_bit_diagnostics_or_native_difference():
    old=np.array([1.,2.]);new=old.copy();new[0]=np.nextafter(old[0],np.inf);nulls=np.zeros(2,bool)
    query.compare_arrays(new,nulls,old,nulls,exact=False)
    assert query.bit_diagnostics(new,old)['finite_word_differences']==1
    with pytest.raises(AssertionError):query.compare_arrays(new,nulls,old,nulls,exact=True)


@pytest.mark.parametrize('kind',['zero_sign','zero_position','nan','positive_inf','negative_inf'])
def test_C_finite_tolerance_keeps_zero_nan_and_inf_semantics_strict(kind):
    old=np.array([0.,1.,np.nan,np.inf,-np.inf]);new=old.copy();nulls=np.zeros(5,bool)
    if kind=='zero_sign':new[0]=-0.
    elif kind=='zero_position':new[0]=1e-15
    elif kind=='nan':new[2]=1.
    elif kind=='positive_inf':new[3]=1e300
    else:new[4]=np.inf
    with pytest.raises(AssertionError):query.compare_arrays(new,nulls,old,nulls,exact=False)


def zero_contract_rows():
    import sarext_typed_zero_regression as zero
    reference=json.loads(Path(__file__).with_name('data').joinpath('sarext-typed-zero-contract.json').read_text())
    return zero,{'original':{'cases':copy.deepcopy(reference['C'])},'prior':{'cases':copy.deepcopy(reference['native56'])},
                 'candidate':{'cases':copy.deepcopy(reference['C'])},'alternative':{'cases':copy.deepcopy(reference['C'])}}


def test_untimed_public_C_target_boundary_never_becomes_a_timing_waiver():
    zero,rows=zero_contract_rows();result=zero.validate(rows)
    assert len(result)==4 and all(r['A_B_C_raw_identity'] and not r['timed_waiver'] for r in result.values())
    assert np.array([zero.FIXTURES[0][1][0]]).view(np.uint64)[0]==0


@pytest.mark.parametrize('kind',['missing','A_sign','B_sign','prior_not_reproduced','outside_boundary','mask','input','group'])
def test_C_target_gate_rejects_wrong_sign_or_broader_semantic_waivers(kind):
    zero,rows=zero_contract_rows();case='short_cancellation/interleaved';x=rows['original']['cases'][case]
    if kind=='missing':del rows['alternative']['cases'][case]
    elif kind in ('A_sign','B_sign'):
        side='candidate' if kind=='A_sign' else 'alternative';rows[side]['cases'][case]['words'][x['target_zero_positions'][0]]=0x8000000000000000
    elif kind=='prior_not_reproduced':rows['prior']['cases'][case]['words'][x['target_zero_positions'][0]]=0
    elif kind=='outside_boundary':rows['prior']['cases'][case]['words'][-1]^=1
    elif kind=='mask':rows['candidate']['cases'][case]['nulls'][0]=True
    elif kind=='input':rows['alternative']['cases'][case]['high_words'][0]^=1
    else:rows['candidate']['cases'][case]['groups']+=1
    with pytest.raises(ValueError):zero.validate(rows)


def test_normal_product_FMA_evidence_is_per_function_and_resolves_GOT_calls():
    import sarext_typed_elf as elf
    clone='''
10: vfmadd132sd %xmm0,%xmm1,%xmm2
20: vfmadd213sd %xmm0,%xmm1,%xmm2
30: vfmadd231sd %xmm0,%xmm1,%xmm2
40: vfmadd132sd %xmm0,%xmm1,%xmm2
50: ret
'''
    good=elf.analyze(clone)
    assert len(good['inline_fma_instruction_lines'])==4 and good['named_libm_fma_call_lines']==[]
    # The portable fallback/other Core functions may legitimately call fma.
    fallback='10: call 200 <fma@plt>\n20: ret\n'
    assert len(elf.analyze(fallback)['named_libm_fma_call_lines'])==1
    assert elf.analyze(clone)['named_libm_fma_call_lines']==[]
    indirect='10: call *0x100(%rip) # 200 <unlabelled_got>\n20: ret\n'
    reloc='0000000000000200 0000000100000006 R_X86_64_GLOB_DAT 0000000000000000 fma@GLIBC_2.2.5 + 0\n'
    assert len(elf.analyze(indirect,reloc)['named_libm_fma_call_lines'])==1


def test_replay_stress_reporting_keeps_both_cases_and_slower_results(tmp_path):
    names=['sarext_longzero/1000000','grouped_sarext_longzero/10000x100']
    rows={n:{'baseline_median_ms':1.,'candidate_median_ms':1.1,'paired_ratios':[1/1.1]*12,'ratio_envelope':[.85,.95]} for n in names}
    data={'results':{'1':{'comparisons':{'candidate_vs_alternative':rows}}}}
    bench.write_negatives(data,tmp_path)
    saved=json.loads((tmp_path/'replay-stress.json').read_text())
    assert {r['case'] for r in saved}==set(names) and all(r['after_latency_percent']>0 for r in saved)
    assert all(r['after_faster_rounds']==0 for r in saved)


@pytest.mark.parametrize('kind',['ok','wrong_name','zero_filtered','ignored','failure'])
def test_exact_cold_dispatch_proof_cannot_pass_a_zero_test_filter(tmp_path,kind):
    inventory=tmp_path/'list.log';log=tmp_path/'cold.log'
    inventory.write_text(prov.COLD_TEST+': test\n')
    text='running 1 test\ntest '+prov.COLD_TEST+' ... ok\ntest result: ok. 1 passed; 0 failed; 0 ignored; 0 measured; 32 filtered out;\n'
    if kind=='wrong_name':inventory.write_text('another_test: test\n')
    elif kind=='zero_filtered':text=text.replace('running 1 test','running 0 tests').replace('1 passed','0 passed')
    elif kind=='ignored':text=text.replace('1 passed; 0 failed; 0 ignored','0 passed; 0 failed; 1 ignored')
    elif kind=='failure':text=text.replace('1 passed; 0 failed','0 passed; 1 failed')
    log.write_text(text)
    if kind=='ok':assert prov.require_cold_dispatch(log,inventory)['test']==prov.COLD_TEST
    else:
        with pytest.raises(ValueError):prov.require_cold_dispatch(log,inventory)


def test_full_corpus_NaN_words_and_finite_zero_rounding_are_reported_not_normalized(tmp_path):
    meta={'cases':{'stochrsi/param/fastd_matype/12':{'fields':['value']}}}
    old=np.array([np.nan,0.,-0.,1.]);new=np.array([-np.nan,4.440892098500626e-16,-0.,1.])
    left=tmp_path/'left.npz';right=tmp_path/'right.npz'
    np.savez(left,metadata=np.array(json.dumps(meta)),value=old,value_null=np.zeros(4,bool))
    np.savez(right,metadata=np.array(json.dumps(meta)),value=new,value_null=np.zeros(4,bool))
    result=bench.corpus_word_diagnostics(left,right)
    assert result['nan_word_differences']==1 and result['zero_position_differences']==1
    assert result['both_zero_sign_differences']==0
    assert result['changed_fields'][0]['zero_examples'][0]['after_word']=='0x3cc0000000000000'


def test_cold_proof_rejects_namespace_in_comment_plus_an_unrelated_passing_test(tmp_path):
    inventory=tmp_path/'list.log';log=tmp_path/'cold.log'
    inventory.write_text(prov.COLD_TEST+': test\n')
    log.write_text('# intended '+prov.COLD_TEST+'\nrunning 1 test\ntest unrelated_test ... ok\ntest result: ok. 1 passed; 0 failed; 0 ignored;\n')
    with pytest.raises(ValueError):prov.require_cold_dispatch(log,inventory)


def test_ELF_fma_tail_transfers_are_not_misreported_as_zero_libm_calls():
    import sarext_typed_elf as elf
    indirect='10: jmp *0x100(%rip) # 200 <unlabelled_got>\n'
    reloc='0000000000000200 0000000100000006 R_X86_64_GLOB_DAT 0000000000000000 fma@GLIBC_2.2.5 + 0\n'
    result=elf.analyze(indirect,reloc)
    assert len(result['libm_fma_control_transfer_lines'])==1 and result['named_libm_fma_call_lines']==[]
    assert elf.analyze('10: je 200 <fma@plt>\n')['libm_fma_control_transfer_lines']


@pytest.mark.parametrize('missing',[None,'fma','wrapper','resolver'])
def test_B_actual_product_role_gate_requires_real_plain_wrapper_clone_and_resolver(missing):
    import sarext_typed_elf as elf
    prefix='_ZN13_polars_talib13sarext_legacy17dispatched_scalar'
    names={'fma':prefix+'59'+elf.FMA_TAG+'17habcE','wrapper':prefix+'17hdefE',
           'resolver':prefix+'14__detect_index8__detect17h123E'}
    functions={name:{} for key,name in names.items() if key!=missing}
    # A random non-FMA dispatched symbol cannot stand in for either role.
    functions[prefix+'14unrelated_name17h456E']={}
    if missing is None:assert elf.symbol_roles(functions)['portable_dispatch_wrapper']==names['wrapper']
    else:
        with pytest.raises(ValueError):elf.symbol_roles(functions)


@pytest.mark.parametrize('opcode',['call','jmp'])
def test_actual_linux_relative_GOT_fma_shim_is_resolved_by_exact_text_symbol(opcode):
    import sarext_typed_elf as elf
    # CI40962602117 actual wheel: the portable wrapper calls this local
    # compiler_builtins fma shim. Symbol names are absent in objdump's GOT
    # annotation because the ELF relocation is RELATIVE rather than GLOB_DAT.
    instruction='  54ba0d: '+opcode+' *0xc44f95(%rip) # 11909a8 <_DYNAMIC+0x5b0>\n'
    reloc='00000000011909a8 0000000000000008 R_X86_64_RELATIVE 1127290\n'
    symbols='0000000001127290 t fma\n'
    result=elf.analyze(instruction,reloc,symbols)
    assert result['libm_fma_control_transfer_lines']==[instruction.rstrip('\n')]
    assert result['resolved_fma_control_transfers']==[{
        'instruction':instruction.rstrip('\n'),'kind':'exact_relative_text_symbol',
        'slot':'0x11909a8','target':'0x1127290','symbol':'fma','relocation':reloc.rstrip('\n')}]
    assert len(result['named_libm_fma_call_lines'])==(opcode=='call')


@pytest.mark.parametrize('change',['missing_symbols','wrong_address','nearby_address','wrong_name','nontext',
                                   'wrong_slot','wrong_relocation','invalid_addend','extra_addend'])
def test_relative_GOT_fma_resolution_refuses_ambiguous_or_unrelated_evidence(change):
    import sarext_typed_elf as elf
    instruction='54ba0d: call *0xc44f95(%rip) # 11909a8 <_DYNAMIC+0x5b0>\n'
    reloc='00000000011909a8 0000000000000008 R_X86_64_RELATIVE 1127290\n'
    symbols='0000000001127290 t fma\n'
    if change=='missing_symbols':symbols=''
    elif change=='wrong_address':symbols=symbols.replace('1127290','2127290')
    elif change=='nearby_address':symbols=symbols.replace('1127290','112728f')
    elif change=='wrong_name':symbols=symbols.replace('fma','not_fma')
    elif change=='nontext':symbols=symbols.replace(' t ',' d ')
    elif change=='wrong_slot':reloc=reloc.replace('11909a8','11909a0')
    elif change=='wrong_relocation':reloc=reloc.replace('R_X86_64_RELATIVE','R_X86_64_IRELATIVE')
    elif change=='invalid_addend':reloc=reloc.replace('1127290','-1127290')
    else:reloc=reloc.rstrip('\n')+' + 8\n'
    result=elf.analyze(instruction,reloc,symbols)
    assert result['libm_fma_control_transfer_lines']==[]
    assert result['resolved_fma_control_transfers']==[]


def test_relative_GOT_fma_transfer_in_hardware_clone_is_not_hidden_by_inline_updates():
    import sarext_typed_elf as elf
    text='\n'.join(str(i*10)+': vfmadd132sd %xmm0,%xmm1,%xmm2' for i in range(1,5))
    text+='\n54ba0d: jmp *0xc44f95(%rip) # 11909a8 <_DYNAMIC+0x5b0>\n'
    result=elf.analyze(text,'00000000011909a8 0000000000000008 R_X86_64_RELATIVE 1127290\n',
                       '0000000001127290 t fma\n')
    assert len(result['inline_fma_instruction_lines'])==4
    # collect() must reject this clone despite its four fused instructions.
    assert len(result['libm_fma_control_transfer_lines'])==1
