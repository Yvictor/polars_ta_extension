import importlib.util,json,math,struct,subprocess,tomllib
from pathlib import Path
import pytest

spec=importlib.util.spec_from_file_location('isolated_mavp',Path(__file__).parents[1]/'scripts/mavp_variable_benchmark.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
CASE='mavp/four/SMA/100';BACKEND='current';SELECTION=(CASE,BACKEND)


def metadata(capture_only=True,selection=None):
    row={'kind':'metadata','format':2,'scope':'full','cases':36,'backends':list(m.BACKENDS),'capture_records':108,
         'canary_bits':'7ff80000000055aa','warmups':5,'repeats':31,'capture_only':capture_only,'capture_written':True,
         'registry_version':'0.8.3','current_version':'0.8.4','c_version':'0.8.1 (reference)','os':'linux','arch':'x86_64','tolerance_relative':4e-15,'tolerance_floor':'max_abs_input'}
    if selection is not None:
        case,backend=selection;row.update(scope='isolated',cases=1,backends=[backend],capture_records=1,selected_case=case,selected_backend=backend)
    return row


def records(timed=False,selection=None):
    rows=[metadata(not timed,selection)]
    if selection is None:
        for backend,case in sorted(m.KEYS):
            count=m.expected_range(case)[2]
            rows.append({'kind':'parity','case':case,'backend':backend,'count':count,'exact':count,'within_tolerance':0,'nonfinite_same':0,'signed_zero':0,'max_abs':0.,'max_scaled':0.})
    else:
        case,backend=selection;n,beg,count=m.expected_range(case)
        rows.append({'kind':'validation','case':case,'backend':backend,'n':n,'beg':beg,'count':count,'written_finite':count,'tail_canary':n+8-count,'golden_verified':True,'golden_bytes':8+4+len((backend+'/'+case).encode())+32+(n+8)*8})
        if timed:rows.append({'kind':'case','case':case,'backend':backend,'n':n,'beg':beg,'count':count,'iterations':m.ITERATIONS[n],'warmups':5,'samples_ns':[100.]*31})
    return rows


def encoded(rows):return '\n'.join(json.dumps(row)for row in rows)


def test_full_capture_and_single_child_inventories():
    assert len(m.CASES)==36 and len(m.KEYS)==108 and 36*3*2*12==2592
    assert len(m.parse_records(encoded(records()),True)['parity'])==108
    assert len(m.parse_records(encoded(records(selection=SELECTION)),True,SELECTION)['validation'])==1
    assert len(m.parse_records(encoded(records(True,SELECTION)),False,SELECTION)['cases'])==1


@pytest.mark.parametrize('field,value',[('format',1),('warmups',3),('repeats',29),('capture_only',1),('capture_written',False),('cases',True),('registry_version','0.8.4'),('current_version','0.8.3'),('c_version','0.8.10'),('scope','full'),('selected_backend','registry083'),('capture_records',108),('arch',0)])
def test_runtime_and_selection_gates(field,value):
    rows=records(True,SELECTION);rows[0][field]=value
    with pytest.raises(ValueError):m.parse_records(encoded(rows),False,SELECTION)


def test_full_timing_and_mixed_sibling_calls_are_forbidden():
    with pytest.raises(ValueError):m.parse_records(encoded(records()),False)
    for inserted in (records()[1],dict(records(True,SELECTION)[1],backend='registry083')):
        rows=records(True,SELECTION);rows.insert(1,inserted)
        with pytest.raises(ValueError):m.parse_records(encoded(rows),False,SELECTION)
    rows=records(True,SELECTION);rows[1]['case']='mavp/few/SMA/100'
    with pytest.raises(ValueError):m.parse_records(encoded(rows),False,SELECTION)


def test_golden_check_is_required_before_timing():
    rows=records(True,SELECTION)
    for bad in (rows[:1]+rows[2:],rows[:1]+list(reversed(rows[1:])),rows+[rows[1]]):
        with pytest.raises(ValueError):m.parse_records(encoded(bad),False,SELECTION)
    for field,value in [('golden_verified',False),('golden_bytes',1),('count',True),('tail_canary',0),('written_finite',0)]:
        bad=records(True,SELECTION);bad[1][field]=value
        with pytest.raises(ValueError):m.parse_records(encoded(bad),False,SELECTION)


@pytest.mark.parametrize('value',[0.,-1.,True,float('nan'),float('inf')])
def test_raw_samples_positive_finite_exact31(value):
    rows=records(True,SELECTION);rows[-1]['samples_ns'][0]=value
    with pytest.raises(ValueError):m.parse_records(encoded(rows),False,SELECTION)


def test_child_case_settings_and_exact_counts():
    rows=records(True,SELECTION);rows[-1]['samples_ns'].pop()
    with pytest.raises(ValueError):m.parse_records(encoded(rows),False,SELECTION)
    for field,value in [('iterations',1),('warmups',4),('beg',0)]:
        rows=records(True,SELECTION);rows[-1][field]=value
        with pytest.raises(ValueError):m.parse_records(encoded(rows),False,SELECTION)


@pytest.mark.parametrize('field,value',[('exact',0),('signed_zero',1),('nonfinite_same',1),('max_scaled',4.1e-15),('max_abs',float('nan'))])
def test_global_cross_version_gate_cannot_waive_primary(field,value):
    rows=records();rows[1][field]=value
    with pytest.raises(ValueError):m.parse_records(encoded(rows),True)


def test_global_capture_unique_complete_parity():
    rows=records()
    for bad in (rows[:-1],rows+[rows[1]]):
        with pytest.raises(ValueError):m.parse_records(encoded(bad),True)


def test_command_contract_requires_complete_selectors_and_golden():
    assert m.harness_command('binary','out',capture_only=True)==['binary','31','out','--capture-only']
    assert m.harness_command('binary','out',CASE,BACKEND,'golden')==['binary','31','out','--case',CASE,'--backend',BACKEND,'--golden','golden']
    for case,backend,golden in ((None,None,None),(CASE,None,'golden'),(None,BACKEND,'golden'),(CASE,BACKEND,None),('bad',BACKEND,'golden')):
        with pytest.raises(ValueError):m.harness_command('binary','out',case,backend,golden)
    with pytest.raises(ValueError):m.harness_command('binary',None,capture_only=True)


def test_normalizer_drops_execution_only_not_runtime():
    full=metadata();selected=metadata(False,SELECTION)
    assert m.stable_metadata(full)==m.stable_metadata(selected)
    assert m.stable_metadata(full)!=m.stable_metadata(dict(selected,arch='other'))


def fixture_capture(monkeypatch,tmp_path):
    monkeypatch.setattr(m,'KEYS',{(BACKEND,CASE)})
    name=BACKEND+'/'+CASE;n,beg,count=m.expected_range(CASE);outlen=n+8
    data=b'MAVPVC01'+struct.pack('<I',len(name))+name.encode()+struct.pack('<QQQQ',n,beg,count,outlen)
    data+=struct.pack('<d',100.)*count+struct.pack('<Q',m.CANARY)*(outlen-count)
    path=tmp_path/'full.bin';path.write_bytes(data);return path


def test_golden_split_is_full_selected_record(monkeypatch,tmp_path):
    full=fixture_capture(monkeypatch,tmp_path);records=m.split_goldens(full,tmp_path)
    golden=records[BACKEND+'/'+CASE];assert Path(golden['path']).read_bytes()==full.read_bytes()
    assert m.capture_record(golden['path'],SELECTION)['sha256']==golden['sha256']


def test_exact_child_deleted_only_after_persisted_hash_proof(monkeypatch,tmp_path):
    full=fixture_capture(monkeypatch,tmp_path);golden={'sha256':m.sha256(full),'bytes':full.stat().st_size}
    child=tmp_path/'child.bin';child.write_bytes(full.read_bytes());proof=tmp_path/'proof.json'
    result=m.finalize_child_capture(child,SELECTION,golden,{'label':'child'},proof)
    assert not child.exists()and proof.exists()and result['duplicate_deleted_after_sha_proof']
    child.write_bytes(full.read_bytes());data=bytearray(child.read_bytes());offset=8+4+len(BACKEND+'/'+CASE)+32;data[offset:offset+8]=struct.pack('<d',101.);child.write_bytes(data)
    with pytest.raises(ValueError):m.finalize_child_capture(child,SELECTION,golden,{},tmp_path/'badproof.json')
    assert child.exists()and not(tmp_path/'badproof.json').exists()


def test_failed_subprocess_keeps_command_stdout_stderr(monkeypatch,tmp_path):
    def failed(*args,**kwargs):return subprocess.CompletedProcess(args[0],2,'partialJSON','panic details')
    monkeypatch.setattr(m.subprocess,'run',failed);stem=tmp_path/'failed'
    with pytest.raises(subprocess.CalledProcessError):m.execute_harness(['binary','31'],stem,{})
    assert Path(str(stem)+'.jsonl').read_text()=='partialJSON'
    assert Path(str(stem)+'.stderr.log').read_text()=='panic details'
    assert json.loads(Path(str(stem)+'-command.json').read_text())==['binary','31']


def test_exact12_pairs_remain_primary_unit():
    def row(value):return {'cases':{'current/'+CASE:{'samples_ns':[value]*31}}}
    runs={'baseline':[row(v)for v in range(10,22)],'candidate':[row(v/2)for v in range(10,22)]}
    result=m.summarize(runs)['current/'+CASE];assert result['median_paired_ratio']==2 and result['candidate_faster_pairs']==12
    runs['candidate'].pop()
    with pytest.raises(ValueError):m.summarize(runs)


@pytest.mark.parametrize('flag,value',[('--pairs','10'),('--repeats','29')])
def test_cli_never_cuts_repetitions(tmp_path,flag,value):
    with pytest.raises(SystemExit):m.main(['--baseline-source',str(tmp_path),'--candidate-source',str(tmp_path),'--c-source',str(tmp_path),'--output',str(tmp_path),flag,value])
