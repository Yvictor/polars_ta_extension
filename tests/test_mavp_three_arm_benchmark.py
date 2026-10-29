import importlib.util,json,math,struct,subprocess,tomllib
from pathlib import Path
import pytest

spec=importlib.util.spec_from_file_location('three_arm_mavp',Path(__file__).parents[1]/'scripts/mavp_three_arm_benchmark.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
CASE='mavp/four/SMA/100';BACKEND='current';SELECTION=(CASE,BACKEND)


def metadata(capture_only=True,selection=None):
    row={'kind':'metadata','format':2,'scope':'full','cases':38,'backends':list(m.BACKENDS),'capture_records':114,
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
    assert len(m.CASES)==38 and len(m.KEYS)==114 and 38*3*3*12==4104 and m.TIMED_CHILDREN==4104
    assert len(m.parse_records(encoded(records()),True)['parity'])==114
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
    runs={'baseline':[row(v)for v in range(10,22)],'control':[row(v*.75)for v in range(10,22)],'candidate':[row(v/2)for v in range(10,22)]}
    results=m.summarize(runs);result=results['baseline_vs_candidate']['current/'+CASE];assert result['median_paired_ratio']==2 and result['after_faster_rounds']==12
    assert set(results)=={'baseline_vs_control','baseline_vs_candidate','control_vs_candidate'}
    runs['candidate'].pop()
    with pytest.raises(ValueError):m.summarize(runs)


@pytest.mark.parametrize('flag,value',[('--pairs','10'),('--repeats','29')])
def test_cli_never_cuts_repetitions(tmp_path,flag,value):
    with pytest.raises(SystemExit):m.main(['--candidate-commit',m.CANDIDATE,'--baseline-source',str(tmp_path),'--control-source',str(tmp_path),'--candidate-source',str(tmp_path),'--c-source',str(tmp_path),'--output',str(tmp_path),flag,value])


def test_all_six_orders_twice_balance_every_arm_position_and_relative_order():
    import collections,itertools
    assert len(m.ORDERS)==12
    assert collections.Counter(m.ORDERS)=={order:2 for order in itertools.permutations(m.SIDES)}
    for side in m.SIDES:
        assert [sum(order[position]==side for order in m.ORDERS) for position in range(3)]==[4,4,4]
    for a,b in itertools.combinations(m.SIDES,2):
        assert sum(order.index(a)<order.index(b) for order in m.ORDERS)==6


@pytest.mark.parametrize('pin',['','1'*40,'1'*39,'A'*40,m.BASELINE,m.CONTROL])
def test_unselected_or_aliased_candidate_pin_is_rejected(pin):
    from types import SimpleNamespace
    with pytest.raises(ValueError):m.arm_pins(SimpleNamespace(candidate_commit=pin))


def test_exact_three_immutable_arms_are_separate_from_runtime_backends(monkeypatch):
    monkeypatch.setattr(m,"CANDIDATE","a"*40)
    from types import SimpleNamespace
    assert m.arm_pins(SimpleNamespace(candidate_commit=m.CANDIDATE))=={'baseline':m.BASELINE,'control':m.CONTROL,'candidate':m.CANDIDATE}
    assert m.SIDES==('baseline','control','candidate')
    assert m.BACKENDS==('current','registry083','originalc081')
    assert m.TIMED_CHILDREN*31==127224


def test_every_arm_round_must_keep_the_same_case_inventory():
    def row():return {'cases':{'current/'+CASE:{'samples_ns':[100.]*31}}}
    runs={side:[row() for _ in m.ORDERS] for side in m.SIDES}
    runs['control'][5]['cases'].clear()
    with pytest.raises(ValueError):m.summarize(runs)


def test_workflow_pins_reviewed_candidate_and_preserves_three_sources():
    text=(Path(__file__).parents[1]/'.github/workflows/mavp-mama-controls.yml').read_text()
    assert "MAVP_CANDIDATE_COMMIT: '"+m.CANDIDATE+"'" in text
    assert '--control-source control' in text and '--candidate-commit "$MAVP_CANDIDATE_COMMIT"' in text
    assert 'ref: '+m.BASELINE in text and 'ref: '+m.CONTROL in text
    assert 'target-control/release/libta_lib.rlib' in text
    assert 'timeout-minutes: 120' in text and 'cancel-in-progress: false' in text


@pytest.mark.parametrize('bad_side',[None,'candidate'])
def test_all_three_full_capture_gates_precede_any_isolated_command(monkeypatch,tmp_path,bad_side):
    from types import SimpleNamespace
    args=SimpleNamespace(output=tmp_path,harness=Path('unused'),candidate_commit=m.CANDIDATE)
    provenance={'input':{'path':'input.bin'},**{side:{'binary':side+'-binary'} for side in m.SIDES}}
    (tmp_path/'build-provenance.json').write_text(json.dumps(provenance))
    monkeypatch.setattr(m,'verify',lambda *_:None)
    monkeypatch.setattr(m.os,'sched_getaffinity',lambda *_:{3,4},raising=False)
    monkeypatch.setattr(m.os,'sched_setaffinity',lambda *_:None,raising=False)
    commands=[]
    def execute(command,stem,env):
        commands.append(command)
        assert '--capture-only' in command and '--case' not in command and '--backend' not in command
        Path(command[2]).write_bytes(b'fixture')
        return command[0]
    monkeypatch.setattr(m,'execute_harness',execute)
    monkeypatch.setattr(m,'parse_records',lambda *_:{'metadata':metadata()})
    def capture(path):return {'bytes':7,'sha256':'bad' if Path(path).stem==bad_side else 'same'}
    monkeypatch.setattr(m,'capture_record',capture)
    class AllFullGatesPassed(Exception):pass
    def split(*_):
        assert [command[0] for command in commands]==[side+'-binary' for side in m.SIDES]
        raise AllFullGatesPassed
    monkeypatch.setattr(m,'split_goldens',split)
    with pytest.raises(AllFullGatesPassed if bad_side is None else ValueError):m.measure(args)
    assert len(commands)==3
    assert not(tmp_path/'children').exists()


def test_actual_controller_runs_all_orders_with_each_case_backend_in_its_own_child(monkeypatch,tmp_path):
    monkeypatch.setattr(m,"CANDIDATE","a"*40)
    from types import SimpleNamespace
    monkeypatch.setattr(m,'CASES',{CASE})
    monkeypatch.setattr(m,'KEYS',{(backend,CASE) for backend in m.BACKENDS})
    monkeypatch.setattr(m,'TIMED_CHILDREN',108)
    args=SimpleNamespace(output=tmp_path,harness=Path('unused'),candidate_commit=m.CANDIDATE)
    provenance={'input':{'path':'input.bin'},**{side:{'binary':side+'-binary'} for side in m.SIDES}}
    (tmp_path/'build-provenance.json').write_text(json.dumps(provenance))
    monkeypatch.setattr(m,'verify',lambda *_:None)
    monkeypatch.setattr(m.os,'sched_getaffinity',lambda *_:{3,4},raising=False)
    monkeypatch.setattr(m.os,'sched_setaffinity',lambda *_:None,raising=False)
    commands=[]
    def execute(command,stem,env):
        commands.append(command)
        Path(command[2]).write_bytes(b'full' if '--capture-only' in command else b'golden')
        if '--capture-only' in command:return encoded(records())
        assert len(commands)>3 and all('--capture-only' in c for c in commands[:3])
        assert '--case' in command and '--backend' in command and '--golden' in command
        selection=(command[command.index('--case')+1],command[command.index('--backend')+1])
        return encoded(records(True,selection))
    monkeypatch.setattr(m,'execute_harness',execute)
    monkeypatch.setattr(m,'capture_record',lambda path,*_:{'sha256':m.sha256(path),'bytes':Path(path).stat().st_size})
    def split(*_):
        result={}
        for backend in m.BACKENDS:
            path=tmp_path/(backend+'-golden.bin');path.write_bytes(b'golden')
            result[backend+'/'+CASE]={'path':str(path),'sha256':m.sha256(path),'bytes':6}
        return result
    monkeypatch.setattr(m,'split_goldens',split)
    m.measure(args)
    report=json.loads((tmp_path/'summary.json').read_text())
    assert len(commands)==111 and report['timed_child_count']==108
    assert report['arm_orders']==[list(order) for order in m.ORDERS]
    for offset,backend in enumerate(m.BACKENDS):
        selected=commands[3+offset*36:3+(offset+1)*36]
        assert [c[0] for c in selected]==[side+'-binary' for order in m.ORDERS for side in order]
        assert all(c[c.index('--backend')+1]==backend and c[c.index('--case')+1]==CASE for c in selected)
    assert set(report['results'])=={'baseline_vs_control','baseline_vs_candidate','control_vs_candidate'}
    assert len(report['child_capture_proofs'])==108


def test_shared_period_preparation_keeps_ema_wma_as_affected_workloads():
    keys=('current/mavp/four/EMA/100','current/mavp/four/WMA/100','current/sma_control/SMA/100',
          'registry083/mavp/four/EMA/100','originalc081/mavp/four/WMA/100')
    runs={side:[{'cases':{key:{'samples_ns':[100.]*31} for key in keys}} for _ in m.ORDERS] for side in m.SIDES}
    for rows in m.summarize(runs).values():
        for key in keys[:2]:
            assert not rows[key]['is_unchanged_control'] and rows[key]['is_other_ma_workload']
        assert rows[keys[2]]['is_unchanged_control'] and not rows[keys[2]]['is_other_ma_workload']
        assert all(rows[key]['is_reference_backend'] for key in keys[3:])

def test_canonical_floor_pin_is_selected_and_placeholder_still_blocks(tmp_path,monkeypatch):
    from types import SimpleNamespace
    assert m.CANDIDATE == '08ae6a75ad32c91e7ffe8c10d00460d73589819a'
    assert m.arm_pins(SimpleNamespace(candidate_commit=m.CANDIDATE))['candidate'] == m.CANDIDATE
    monkeypatch.setattr(m,'CANDIDATE','UNSELECTED_SOURCE_PIN_DO_NOT_RUN')
    for pin in [m.CANDIDATE, "a"*40, "9f66a5b075f6f2b578118f9b913a5f5ca5540a69"]:
        with pytest.raises(ValueError, match="unselected"):
            m.arm_pins(SimpleNamespace(candidate_commit=pin))
    with pytest.raises(ValueError, match="unselected"):
        m.main(['--candidate-commit',m.CANDIDATE,'--baseline-source',str(tmp_path),
                '--control-source',str(tmp_path),'--candidate-source',str(tmp_path),
                '--c-source',str(tmp_path),'--output',str(tmp_path),"--build-only"])

def test_exactly_two_direct_mama_controls_extend_the_original_inventory():
    previous = {f'mavp/{pattern}/SMA/{n}' for n in m.SIZES
                for pattern in ('one','four','few','many','blocked','clamped')}
    previous |= {f'{name}/{ma}/{n}' for n in m.SIZES
                 for name,ma in (('sma_control','SMA'),('mavp/four','EMA'),('mavp/four','WMA'))}
    assert len(previous) == 36 and previous < m.CASES
    assert m.CASES - previous == {'ma_control/MAMA/100','ma_control/MAMA/1000000'}
    for case in m.CASES - previous:
        n,beg,count=m.expected_range(case)
        assert beg == 32 and count == n-32
        for backend in m.BACKENDS:
            selected=(case,backend)
            assert len(m.parse_records(encoded(records(True,selected)),False,selected)['cases']) == 1

def test_managed_library_and_source_gates_precede_every_timer():
    text=(Path(__file__).parents[1]/'.github/workflows/mavp-mama-controls.yml').read_text()
    assert "java-version: '21'" in text
    assert 'global-json-file: candidate/global.json' in text
    assert '10.0.112' in text and text.index('Verify pinned managed SDK contract') < text.index('actions/setup-dotnet')
    assert text.index('Verify canonical floor-elision') < text.index('actions/checkout')
    assert text.index('libraries --language=java,csharp') < text.index('Build identical primary')
    assert text.index('full-c-rust-regression.log') < text.index('measure 4104')
    assert 'measure 3888' not in text
    assert text.index('managed_runtime_proof') < text.index('Build identical primary')
    log = ('Running Java BatchApiTest (on the jar)... BatchApiTest: ALL PASS (1494 checks)\nOK\n'
           'Running C# tests (net10.0)... TALib C# tests on .NET 10.0.3\n'
           'BatchApiTest: ALL PASS (1494 checks)\nAll 11 C# suite(s) passed.\n')
    proof=m.managed_runtime_proof(log)
    assert proof['matrix_minimum_checks']==1345 and proof['java_batch_checks']==1494
    assert proof['csharp_net10_suite_executed']
    for bad in [log.replace('1494','149'),log.replace('BatchApiTest: ALL PASS','BatchApiTest compiled'),
                log.replace('net10.0','net9.0'),log.replace('Running Java BatchApiTest','Built Java BatchApiTest'),
                log.replace('All 11 C# suite(s) passed.','SKIPPED no runtime')]:
        with pytest.raises(ValueError):m.managed_runtime_proof(bad)

@pytest.mark.parametrize('case',['ma_control/MAMA/100','ma_control/MAMA/1000000'])
@pytest.mark.parametrize('backend',m.BACKENDS)
def test_mama_capture_range_prefix_and_canaries_are_independent(case,backend,tmp_path):
    n,beg,count=m.expected_range(case);name=backend+'/'+case
    header=b'MAVPVC01'+struct.pack('<I',len(name))+name.encode()
    body=struct.pack('<d',100.)*count+struct.pack('<Q',m.CANARY)*(n+8-count)
    path=tmp_path/'mama.bin'
    path.write_bytes(header+struct.pack('<QQQQ',n,beg,count,n+8)+body)
    assert m.capture_record(path,(case,backend))['written_values']==count
    path.write_bytes(header+struct.pack('<QQQQ',n,29,count,n+8)+body)
    with pytest.raises(ValueError,match='range'):m.capture_record(path,(case,backend))
    path.write_bytes(header+struct.pack('<QQQQ',n,beg,count,n+8)+body[:-8]+struct.pack('<d',0.))
    with pytest.raises(ValueError,match='padding'):m.capture_record(path,(case,backend))

def test_mama_rows_are_zero_constructor_controls_not_mavp_preparation():
    keys=['current/ma_control/MAMA/100','current/ma_control/MAMA/1000000']
    runs={side:[{'cases':{key:{'samples_ns':[100.]*31}for key in keys}}for _ in m.ORDERS]for side in m.SIDES}
    for rows in m.summarize(runs).values():
        for row in rows.values():
            assert not row['is_unchanged_control'] and row['is_shared_f64_zero_constructor_control']
            assert not row['is_other_ma_workload']
