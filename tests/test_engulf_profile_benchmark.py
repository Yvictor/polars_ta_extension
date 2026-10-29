import collections,importlib.util,itertools,json,struct,subprocess
from pathlib import Path
from types import SimpleNamespace
import pytest

spec=importlib.util.spec_from_file_location('engulf_gate',Path(__file__).parents[1]/'scripts/engulf_profile_benchmark.py')
import sys
sys.path.insert(0,str(Path(__file__).parents[1]/'scripts'))
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)


def text(fixture='white',mode='rust_typed',n=100,timed=False):
    hits=m.expected_hits(fixture,n)
    result=f'C_VERSION 0.8.1 (reference)\nVALIDATE fixture={fixture} mode={mode} n={n} beg=2 count={n-2} record_tail=8 physical_tail_checked={str(mode!="native_full").lower()} hits={hits} exact_golden={str(timed).lower()}\n'
    if timed:result+=f'PROBE fixture={fixture} mode={mode} n={n} iters={m.ITERS[n]} warmups=5 counts=[0, 0, 0, 0] ns={[100.]*31}\n'
    return result


def test_four_modes_nine_cases_and_balanced_twelve_rounds():
    assert len(m.CASES)==9 and len(m.ORDERS)==12 and 9*4*12==432 and 432*31==13392
    for mode in m.MODES:
        assert [sum(order[i]==mode for order in m.ORDERS) for i in range(4)]==[3]*4
    for a,b in itertools.combinations(m.MODES,2):assert sum(order.index(a)<order.index(b) for order in m.ORDERS)==6
    assert set(m.MODES)=={'c081','rust_typed','rust_generic','native_full'}


@pytest.mark.parametrize('mode',m.MODES)
def test_selected_exact_capture_and_timing_metadata(mode):
    assert m.parse(text(mode=mode), 'white',mode,100,False)['hits']==[0,0,98,0,0]
    row=m.parse(text(mode=mode,timed=True),'white',mode,100,True)
    assert row['median_ns']==100 and len(row['samples_ns'])==31


@pytest.mark.parametrize('old,new',[
    ('C_VERSION 0.8.1','C_VERSION 0.8.4'),('fixture=white','fixture=alternating'),
    ('mode=rust_typed','mode=c081'),('count=98','count=97'),
    ('physical_tail_checked=true','physical_tail_checked=false'),('exact_golden=true','exact_golden=false'),
    ('warmups=5','warmups=4'),('iters=1000','iters=1'),('counts=[0, 0, 0, 0]','counts=[0, 0, 1, 0]'),
    ('100.0','-1.0'),('100.0','true'),('100.0','NaN')])
def test_protocol_drift_cannot_be_accepted(old,new):
    with pytest.raises((AssertionError,ValueError)):m.parse(text(timed=True).replace(old,new),'white','rust_typed',100,True)


def test_no_missing_duplicate_or_mixed_mode_results():
    value=text(timed=True)
    for changed in ('\n'.join(value.splitlines()[:-1]),value+value.splitlines()[-1]+'\n',value+text(mode='c081',timed=True)):
        with pytest.raises(AssertionError):m.parse(changed,'white','rust_typed',100,True)


def test_compact_capture_preserves_range_every_value_and_record_canary(tmp_path):
    path=tmp_path/'capture.bin';data=b'ENGOUT01'+struct.pack('<QQQ',100,2,98)+struct.pack('<'+'i'*108,*([0]*100+[m.CANARY]*8));path.write_bytes(data)
    assert m.capture(path,100)['hits']==[0,0,98,0,0]
    for position in (8,16,24,len(data)-1):
        changed=bytearray(data);changed[position]^=1;path.write_bytes(changed)
        with pytest.raises(AssertionError):m.capture(path,100)
    changed=bytearray(data);changed[32+4*8:32+4*9]=struct.pack('<i',7);path.write_bytes(changed)
    with pytest.raises(AssertionError):m.capture(path,100)


def test_actual_fixture_bytes_keep_finite_prefix_and_ieee_controls(monkeypatch,tmp_path):
    np=pytest.importorskip('numpy');monkeypatch.setattr(np,'__version__','2.5.3')
    monkeypatch.setattr(m,'CASES',tuple(itertools.product(m.FIXTURES,(100,))))
    records=m.fixtures(tmp_path)
    assert len(records)==3
    arrays={}
    for name in m.FIXTURES:
        data=Path(records[name+'/100']['path']).read_bytes();assert data[:8]==b'ENGDATA1'
        n,size=struct.unpack('<QQ',data[8:24]);assert n==100 and data[24:24+size].decode()==name
        arrays[name]=np.frombuffer(data[24+size:],dtype='<f8').reshape(4,100)
        assert np.isfinite(arrays[name][:,:2]).all()
    assert (arrays['white'][3]>arrays['white'][0]).all()
    eq=arrays['equality_ieee'];assert np.isnan(eq[0,8]) and np.isnan(eq[3,9]) and np.isneginf(eq[0,10])
    assert np.signbit(eq[0,7]) and np.signbit(eq[3,6])
    assert arrays['alternating'][0,:4].tolist()==[101.,99.,103.,100.]


def test_every_full_capture_precedes_any_timer(monkeypatch,tmp_path):
    p={'binary':'probe','fixtures':{f'{name}/{n}':{'path':'input'} for name,n in m.CASES}}
    (tmp_path/'build-provenance.json').write_text('{}')
    args=SimpleNamespace(output=tmp_path);calls=[]
    def execute(command,stem,env,timeout=15):
        assert '--capture-only' in command and '--golden' not in command;calls.append(command)
        fixture,mode,n=command[1],command[2],int(command[3]);path=Path(command[6]);path.write_bytes(b'fixture')
        return text(fixture,mode,n),{'minor':0,'major':0}
    monkeypatch.setattr(m,'execute',execute)
    monkeypatch.setattr(m,'capture',lambda path,n:{'path':str(path),'sha256':'same','bytes':1,'hits':m.expected_hits(str(path).split('/')[-1].split('-')[0],n)})
    result=m.validate(args,p,{})
    assert result['all36completed_before_any_timer'] and len(result['checks'])==len(calls)==36
    for fixture,n in m.CASES:assert len([c for c in calls if c[1]==fixture and c[3]==str(n)])==4


def test_mismatch_stops_before_later_captures_or_any_measurement(monkeypatch,tmp_path):
    p={'binary':'probe','fixtures':{f'{name}/{n}':{'path':'input'} for name,n in m.CASES}}
    args=SimpleNamespace(output=tmp_path);calls=[]
    def execute(command,stem,env,timeout=15):
        calls.append(command);Path(command[6]).write_bytes(b'fixture')
        return text(command[1],command[2],int(command[3])),{'minor':0,'major':0}
    monkeypatch.setattr(m,'execute',execute)
    monkeypatch.setattr(m,'capture',lambda path,n:{'path':str(path),'sha256':'same' if 'c081' in str(path) else 'different','bytes':1,'hits':m.expected_hits(str(path).split('/')[-1].split('-')[0],n)})
    with pytest.raises(AssertionError):m.validate(args,p,{})
    assert len(calls)==2 and not(tmp_path/'validation-complete.json').exists()


def test_no_product_source_or_existing_protocol_files_are_changed():
    root=Path(__file__).parents[1]
    result=subprocess.check_output(['git','-C',str(root),'diff','--name-only'],text=True)
    assert not any(path.startswith(('src/','python/')) for path in result.splitlines())
    workflow=(root/'.github/workflows/engulf-profile.yml').read_text()
    assert 'rg ' not in workflow and 'touch "sources/$side/src/lib.rs"' in workflow
    assert workflow.index('--snapshot-native')<workflow.index('cargo test')
    assert 'include-hidden-files: true' in workflow and 'cancel-in-progress: false' in workflow
    assert m.NATIVE in workflow and m.ORIGINAL in workflow


def test_probe_contract_binary_does_not_enable_unrelated_imported_product_tests():
    source=(Path(__file__).parents[1]/'scripts/engulf_profile_benchmark.py').read_text()
    rust=(Path(__file__).parents[1]/'scripts/engulf_profile_probe.rs').read_text()
    assert "['--cfg','engulf_probe_contracts','-o'" in source and "['--test'" not in source
    assert '#[cfg(engulf_probe_contracts)]' in rust and 'PASS4 probe-only contract checks' in rust


def test_expected_branch_hit_counts_are_nonvacuous():
    assert m.expected_hits('white',100)==[0,0,98,0,0]
    assert m.expected_hits('alternating',100)==[25,0,49,0,24]
    assert m.expected_hits('equality_ieee',100)==[6,7,72,7,6]
    assert m.expected_hits('equality_ieee',1000000)==[62500,62500,749998,62500,62500]
    with pytest.raises(AssertionError):m.parse(text(fixture='alternating').replace('[25, 0, 49, 0, 24]','[0, 0, 98, 0, 0]'),'alternating','rust_typed',100,False)


def test_timeout_keeps_partial_stdout_stderr_and_command(monkeypatch,tmp_path):
    def timeout(*a,**k):raise subprocess.TimeoutExpired(a[0],1,output=b'partial capture',stderr=b'error detail')
    monkeypatch.setattr(m.subprocess,'run',timeout);stem=tmp_path/'timeout'
    with pytest.raises(subprocess.TimeoutExpired):m.execute(['probe'],stem,{},1)
    assert Path(str(stem)+'.stdout').read_text()=='partial capture'
    assert Path(str(stem)+'.stderr').read_text()=='error detail'
    assert json.loads(Path(str(stem)+'-failure.json').read_text())['timed_out']
    assert json.loads(Path(str(stem)+'-command.json').read_text())==['probe']


def test_real_measure_orchestration_runs_all_modes_orders_and_preserves_proof_before_delete(monkeypatch,tmp_path):
    args=SimpleNamespace(output=tmp_path);(tmp_path/'build-provenance.json').write_text('{}')
    p={'binary':'probe','fixtures':{f'{name}/{n}':{'path':'input'} for name,n in m.CASES}}
    golden=tmp_path/'golden';golden.write_bytes(b'golden');digest=m.sha256(golden)
    goldens={f'{name}/{n}':{'path':str(golden),'sha256':digest,'bytes':6,'hits':m.expected_hits(name,n)} for name,n in m.CASES}
    validation={'all36completed_before_any_timer':True,'checks':[{}]*36,'goldens':goldens,'build_provenance_sha256':m.sha256(tmp_path/'build-provenance.json')}
    commands=[]
    def execute(cmd,stem,env,timeout=15):
        assert '--golden' in cmd and '--capture-only' not in cmd;commands.append(cmd);Path(cmd[6]).write_bytes(b'golden')
        return text(cmd[1],cmd[2],int(cmd[3]),True),{'minor':0,'major':0}
    monkeypatch.setattr(m,'execute',execute)
    def capture(path,n):
        fixture=Path(path).name.split('-')[0]
        return {'path':str(path),'sha256':digest,'bytes':6,'hits':m.expected_hits(fixture,n)}
    monkeypatch.setattr(m,'capture',capture);monkeypatch.setattr(m.os,'sched_getaffinity',lambda *_:{3},raising=False)
    m.measure(args,p,validation,{key:'1' for key in ('POLARS_MAX_THREADS','OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS')})
    report=json.loads((tmp_path/'summary.json').read_text());assert len(commands)==report['timed_children']==432
    for offset,(fixture,n) in enumerate(m.CASES):
        assert [cmd[2] for cmd in commands[offset*48:(offset+1)*48]]==[mode for order in m.ORDERS for mode in order]
        assert len(report['results'][f'{fixture}/{n}']['comparisons'])==6
    assert len(list((tmp_path/'children').glob('*-proof.json')))==432
    assert not list((tmp_path/'children').glob('*.bin'))


def test_real_symlinked_venv_launcher_keeps_its_prefix_and_private_modules(tmp_path):
    env=tmp_path/'isolated-venv'
    subprocess.run([sys.executable,'-m','venv','--without-pip','--symlinks',str(env)],check=True)
    python=env/'bin/python';assert python.is_symlink()
    report='import json,sys,sysconfig;print(json.dumps({"prefix":sys.prefix,"purelib":sysconfig.get_path("purelib")}))'
    initial=json.loads(subprocess.check_output([str(python),'-c',report],text=True))
    assert Path(initial['prefix'])==env
    Path(initial['purelib'],'engulf_venv_marker.py').write_text('MARKER = "venv-only"\n')
    args=m.normalize_paths(SimpleNamespace(native_python=python,original_python=python,native_source=env/'bin/..'))
    assert args.native_python==args.original_python==python.absolute() and args.native_source==env.resolve()
    query='import json,sys,engulf_venv_marker;print(json.dumps({"prefix":sys.prefix,"marker":engulf_venv_marker.MARKER}))'
    actual=json.loads(subprocess.check_output([str(args.native_python),'-c',query],text=True))
    assert Path(actual['prefix'])==env and actual['marker']=='venv-only'
    # The exact old normalization reproduces the missing-dependency failure.
    broken=subprocess.run([str(python.resolve()),'-c',query],capture_output=True,text=True)
    assert broken.returncode!=0 and 'ModuleNotFoundError' in broken.stderr
