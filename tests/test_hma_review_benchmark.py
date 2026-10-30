import copy
import importlib.util
import json
from pathlib import Path
import struct
import subprocess
import sys
import tomllib

import pytest

spec=importlib.util.spec_from_file_location('hma_review_benchmark',Path(__file__).parents[1]/'scripts/hma_review_benchmark.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)


def records(timed=False):
    result=[{'kind':'metadata','format':1,'cases':len(m.CASES),'validation_cases':len(m.VALIDATION),'backends':list(m.BACKENDS),
             'canary_bits':'7ff80000000055aa','output_prefix':1,'warmups':5,'repeats':31,'capture_only':not timed,
             'registry_version':'0.8.3','current_version':'0.8.4','c_version':'0.8.1 (reference)',
             'os':'linux','arch':'x86_64','capture_written':not timed,'capture_records':len(m.KEYS),
             'tolerance_relative':4e-15,'tolerance_floor':'max_abs_finite_input'}]
    for kind,keys in (('validation',m.VALIDATION_KEYS),('parity',m.TIMED_KEYS)):
        for backend,name in sorted(keys):
            n,beg,count=m.expected_range(name)
            result.append({'kind':kind,'backend':backend,'case':name,'count':count,'exact':count,
                           'within_tolerance':0,'nonfinite_same':0,'signed_zero':0,'max_abs':0.,'max_scaled':0.})
    if timed:
        for backend,name in sorted(m.TIMED_KEYS):
            case=m.expected_case(name);n,beg,count=(case[k] for k in ('n','beg','count'))
            result.append({'kind':'case','backend':backend,'case':name,'n':n,'beg':beg,'count':count,
                           'period':case['period'],'start':case['start'],'empty_range_control':count==0,
                           'iterations':max(100000//n,1),'warmups':5,'samples_ns':[100.]*31})
    return result


def encoded(rows):return '\n'.join(json.dumps(r) for r in rows)


def test_fixed_workload_scope():
    assert len(m.CASES)==17 and len(m.VALIDATION)==659 and len(m.KEYS)==2028
    assert m.expected_range('hma/p20/20')==(20,0,0)
    assert m.expected_range('hma/p20/100')==(100,22,78)
    assert m.expected_range('sma_control/p20/20')==(20,19,1)
    assert m.expected_range('validation/hma/finite/p20/n1000/start500')==(1000,500,500)
    assert m.parse_records(encoded(records()),True)['cases']=={}
    assert len(m.parse_records(encoded(records(True)),False)['cases'])==51


@pytest.mark.parametrize('field,value', [('warmups',3),('repeats',30),('format',True),('capture_only',1),
    ('registry_version','0.8.4'),('current_version','0.8.3'),('c_version','0.8.10'),
    ('backends',['current','originalc081']),('os','darwin'),('arch',0),('tolerance_relative',1e-10)])
def test_metadata_gates(field,value):
    rows=records();rows[0][field]=value
    with pytest.raises(ValueError):m.parse_records(encoded(rows),True)


def test_no_timing_before_all_parity():
    rows=records(True);rows.insert(1,rows.pop())
    with pytest.raises(ValueError,match='before timing'):m.parse_records(encoded(rows),False)


def test_complete_unique_parity_and_timing_inventory():
    rows=records(True)
    for bad in (rows[:-1],rows+[rows[-1]],rows[:1]+rows[2:],rows+[rows[1]]):
        with pytest.raises(ValueError):m.parse_records(encoded(bad),False)


@pytest.mark.parametrize('field,value', [('count',True),('exact',0),('signed_zero',1),('nonfinite_same',1),('max_scaled',4.1e-15),('max_abs',float('nan'))])
def test_cross_version_parity_is_not_a_waiver(field,value):
    rows=records();row=next(r for r in rows[1:] if r['backend']=='originalc081');row[field]=value
    with pytest.raises(ValueError):m.parse_records(encoded(rows),True)


def test_primary_current_parity_requires_exact_values():
    rows=records();row=next(r for r in rows[1:] if r['backend']=='current')
    row['exact']-=1;row['within_tolerance']=1
    with pytest.raises(ValueError,match='current parity'):m.parse_records(encoded(rows),True)


@pytest.mark.parametrize('sample', [0.,-1.,float('nan'),float('inf'),True])
def test_invalid_raw_samples(sample):
    rows=records(True);rows[-1]['samples_ns'][0]=sample
    with pytest.raises(ValueError):m.parse_records(encoded(rows),False)


def test_iterations_and_sample_count_cannot_be_cut():
    rows=records(True);rows[-1]['samples_ns'].pop()
    with pytest.raises(ValueError):m.parse_records(encoded(rows),False)
    rows=records(True);rows[-1]['iterations']=True
    with pytest.raises(ValueError):m.parse_records(encoded(rows),False)


def small_capture(monkeypatch,tmp_path):
    name='sma_control/p20/100';backend='current';key=backend+'/'+name
    monkeypatch.setattr(m,'KEYS',{(backend,name)})
    n,beg,count=m.expected_range(name);outlen=n+8
    payload=struct.pack('<I',len(key))+key.encode()+struct.pack('<QQQQ',n,beg,count,outlen)
    payload+=struct.pack('<Q',m.CANARY)+struct.pack('<d',100.)*count+struct.pack('<Q',m.CANARY)*(outlen-1-count)
    path=tmp_path/'capture.bin';path.write_bytes(b'HMAWGT01'+payload)
    return path,payload


def test_capture_checks_actual_tail_bytes(monkeypatch,tmp_path):
    path,_=small_capture(monkeypatch,tmp_path)
    result=m.capture_record(path)
    assert result['records']==1 and result['written_values']==81 and result['all_prefix_tail_guards_verified']
    data=bytearray(path.read_bytes());data[-1]^=1;path.write_bytes(data)
    with pytest.raises(ValueError,match='guard'):m.capture_record(path)


def test_capture_rejects_missing_duplicate_and_truncation(monkeypatch,tmp_path):
    path,payload=small_capture(monkeypatch,tmp_path)
    for data in (b'HMAWGT01',b'HMAWGT01'+payload+payload,b'HMAWGT01'+payload[:-1],b'BADMAGIC'+payload):
        path.write_bytes(data)
        with pytest.raises(ValueError):m.capture_record(path)


def test_pinned_registry_lock_has_no_polars_dependencies(tmp_path):
    helper=m.registry_helper(tmp_path)
    lock=tomllib.loads((helper/'Cargo.lock').read_text())
    packages={p['name']:p for p in lock['package']}
    assert set(packages)=={'hma-registry-reference','ta-lib','ta-lib-dispatch'}
    assert packages['ta-lib']['version']=='0.8.3'
    for name,(version,digest) in m.REGISTRY.items():
        assert packages[name]['version']==version and packages[name]['checksum']==digest


def test_pinned_git_source_and_dirty_rejection(tmp_path):
    for name in ('ta_codegen/input/hma/hma.c','ta_codegen/output/rust/Cargo.toml',
                 'ta_codegen/output/rust/library/Cargo.toml','ta_codegen/generator/Cargo.toml','ta_codegen/generator/Cargo.lock'):
        p=tmp_path/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text('fixture')
    subprocess.run(['git','init','-q',str(tmp_path)],check=True)
    subprocess.run(['git','-C',str(tmp_path),'add','.'],check=True)
    subprocess.run(['git','-C',str(tmp_path),'-c','user.name=CI Gate Test','-c','user.email=ci@example.invalid','commit','-qm','fixture'],check=True)
    pin=subprocess.check_output(['git','-C',str(tmp_path),'rev-parse','HEAD'],text=True).strip()
    assert m.git_record(tmp_path,pin)['clean']
    with pytest.raises(ValueError):m.git_record(tmp_path,'0'*40)
    (tmp_path/'ta_codegen/input/hma/hma.c').write_text('changed')
    with pytest.raises(ValueError):m.git_record(tmp_path,pin)


def test_fixed_primary_sample_pairing():
    def row(v):return {'cases':{'current/hma/p20/100':{'samples_ns':[v]*31}}}
    runs={'baseline':[row(v) for v in range(10,22)],'candidate':[row(v/2) for v in range(10,22)]}
    result=m.summarize(runs)['current/hma/p20/100']
    assert result['candidate_faster_pairs']==12 and result['median_paired_ratio']==2
    assert result['candidate_latency_percent']==-50
    runs['candidate'].pop()
    with pytest.raises(ValueError):m.summarize(runs)


@pytest.mark.parametrize('argument,value', [('--pairs','10'),('--repeats','29')])
def test_cli_never_cuts_processes_or_samples(tmp_path,argument,value):
    with pytest.raises(SystemExit):m.main(['--baseline-source',str(tmp_path),'--candidate-source',str(tmp_path),'--c-source',str(tmp_path),'--output',str(tmp_path),argument,value])


def test_capture_written_prefix_cannot_be_unwritten_canary(monkeypatch,tmp_path):
    path,payload=small_capture(monkeypatch,tmp_path)
    offset=8+4+len('current/sma_control/p20/100')+32+8
    data=bytearray(path.read_bytes());data[offset:offset+8]=struct.pack('<Q',m.CANARY);path.write_bytes(data)
    with pytest.raises(ValueError,match='unwritten canary'):m.capture_record(path)


def test_reference_ratios_are_separate_from_primary_ab():
    row=m.parse_records(encoded(records(True)),False)
    for key,entry in row['cases'].items():
        entry['samples_ns']=[{'current':400.,'registry083':200.,'originalc081':100.}[key.split('/',1)[0]]]*31
    runs={side:[row]*12 for side in m.SIDES}
    result=m.reference_comparisons(runs)
    case='hma/p20/100'
    assert result['candidate']['originalc081'][case]['median_paired_ratio']==.25
    assert result['candidate']['originalc081'][case]['current_latency_percent']==300
    assert result['candidate']['originalc081'][case]['current_faster_processes']==0
    assert m.summarize(runs)['current/'+case]['candidate_latency_percent']==0


def test_metadata_precedes_every_result():
    rows=records();rows.append(rows.pop(0))
    with pytest.raises(ValueError,match='metadata must precede'):m.parse_records(encoded(rows),True)


def test_registry_archive_and_extracted_sources_must_both_match(tmp_path):
    import io,tarfile
    source=tmp_path/'source';source.mkdir()
    archive=tmp_path/'registry.crate'
    with tarfile.open(archive,'w:gz') as tar:
        for name,content in {'Cargo.toml':b'[package]','src/lib.rs':b'pub fn marker() {}'}.items():
            path=source/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(content)
            entry=tarfile.TarInfo('fixture-0.8.3/'+name);entry.size=len(content);tar.addfile(entry,io.BytesIO(content))
    digest=m.sha256(archive)
    assert len(m.registry_source_record(source,archive,digest,'fixture-0.8.3'))==2
    with pytest.raises(ValueError,match='checksum'):m.registry_source_record(source,archive,'0'*64,'fixture-0.8.3')
    (source/'src/lib.rs').write_text('tampered')
    with pytest.raises(ValueError,match='source modified'):m.registry_source_record(source,archive,digest,'fixture-0.8.3')


def test_external_cli_contract_for_both_production_modes():
    with pytest.raises(ValueError):m.harness_command('/bin/probe')
    key=('current','hma/p20/100')
    assert m.harness_command('/bin/probe',selection=key,golden='g',actual='a')==['/bin/probe','31','--case',key[1],'--backend',key[0],'--golden','g','--actual','a']
    assert m.harness_command('/bin/probe','capture.bin',True)==['/bin/probe','31','capture.bin','--capture-only']
    with pytest.raises(ValueError):m.harness_command('/bin/probe',capture_only=True)


def test_local_protocol_smoke_does_not_relax_ci_os_gate():
    rows=records();rows[0]['os']='macos'
    with pytest.raises(ValueError):m.parse_records(encoded(rows),True)
    assert m.parse_records(encoded(rows),True,expected_os='macos')['metadata']['os']=='macos'


def test_capture_written_mode_cannot_drift():
    rows=records(True);rows[0]['capture_written']=True
    with pytest.raises(ValueError):m.parse_records(encoded(rows),False)


def test_production_metadata_normalizer_compares_capture_and_timed_modes():
    capture=m.parse_records(encoded(records()),True)['metadata']
    timed=m.parse_records(encoded(records(True)),False)['metadata']
    assert capture['capture_only'] and capture['capture_written']
    assert not timed['capture_only'] and not timed['capture_written']
    assert m.stable_metadata(capture)==m.stable_metadata(timed)
    changed=dict(timed,arch='other')
    assert m.stable_metadata(capture)!=m.stable_metadata(changed)


def test_validation_nan_payload_policy_cannot_relax_timed_or_primary_checks():
    rows=records();row=next(r for r in rows[1:] if r['backend']=='originalc081' and r['case']=='validation/hma/head_nan/p20/n1000/start0')
    row['exact']-=1;row['nonfinite_same']=1
    assert m.parse_records(encoded(rows),True)['validation']
    row['backend']='current'
    with pytest.raises(ValueError):m.parse_records(encoded(rows),True)
    rows=records(True);row=next(r for r in rows if r.get('kind')=='parity' and r['backend']=='originalc081' and r['case']=='hma/p20/100')
    row['exact']-=1;row['nonfinite_same']=1
    with pytest.raises(ValueError):m.parse_records(encoded(rows),False)


def test_capture_prefix_guard_is_checked_separately(monkeypatch,tmp_path):
    path,_=small_capture(monkeypatch,tmp_path)
    offset=8+4+len('current/sma_control/p20/100')+32
    data=bytearray(path.read_bytes());data[offset:offset+8]=struct.pack('<d',0.);path.write_bytes(data)
    with pytest.raises(ValueError,match='prefix/tail guard'):m.capture_record(path)


@pytest.mark.parametrize('value',[float('inf'),float('-inf'),float('nan')])
def test_finite_input_capture_rejects_other_nonfinite_outputs(monkeypatch,tmp_path,value):
    path,_=small_capture(monkeypatch,tmp_path)
    offset=8+4+len('current/sma_control/p20/100')+32+8
    data=bytearray(path.read_bytes());data[offset:offset+8]=struct.pack('<d',value);path.write_bytes(data)
    with pytest.raises(ValueError,match='finite-input'):m.capture_record(path)


def selected_rows(key=('current','hma/p20/100')):
    meta=records(True)[0];c=m.expected_case(key[1])
    row=dict(kind='case',backend=key[0],case=key[1],**{k:c[k] for k in ('n','beg','count','period','start')},iterations=max(100000//c['n'],1),warmups=5,empty_range_control=c['count']==0,pre_output_checked=True,final_output_checked=True,samples_ns=[100.]*31)
    return [meta,row]


def test_selected_cli_and_strict_typed_record_rejections():
    key=('current','hma/p20/100');rows=selected_rows(key);meta=m.stable_metadata(rows[0])
    assert list(m.selected_records(encoded(rows),key,meta)['cases'])==['current/hma/p20/100']
    for index,field,value in [(0,'output_prefix',True),(0,'warmups',5.),(0,'capture_only',True),(1,'backend','registry083'),(1,'count',True),(1,'n',100.),(1,'pre_output_checked',False),(1,'final_output_checked',False),(1,'iterations',1),(1,'samples_ns',[100.]*30),(1,'samples_ns',[True]*31)]:
        bad=copy.deepcopy(rows);bad[index][field]=value
        with pytest.raises(ValueError):m.selected_records(encoded(bad),key,meta)
    for bad in [rows+rows[-1:],rows[1:],rows[::-1]]:
        with pytest.raises(ValueError):m.selected_records(encoded(bad),key,meta)
    with pytest.raises(ValueError,match='duplicate'):m.selected_records(encoded(rows).replace('"n": 100','"n": 100,"n":100'),key,meta)
    for selection in [('wrong',key[1]),('current','validation/hma/finite/p20/n1000/start0')]:
        with pytest.raises(ValueError):m.harness_command('bin',selection=selection,golden='g',actual='a')
    with pytest.raises(ValueError):m.harness_command('bin',selection=key,golden='a',actual='./a')


def test_split_exact_selected_goldens_and_missing_inventory(monkeypatch,tmp_path):
    path,payload=small_capture(monkeypatch,tmp_path)
    monkeypatch.setattr(m,'TIMED_KEYS',m.KEYS)
    result=m.split_goldens(path,tmp_path/'goldens');entry=result['current/sma_control/p20/100']
    assert Path(entry['path']).read_bytes()==b'HMAWGT01'+payload
    monkeypatch.setattr(m,'TIMED_KEYS',m.KEYS|{('registry083','sma_control/p20/100')})
    with pytest.raises(ValueError,match='inventory'):m.split_goldens(path,tmp_path/'other')


def c_fixture(path):
    result=bytearray(b'HMARVC01');p=4;lb=4;n=1000;cap=n+8
    for pattern in range(4):
        for start in (0,lb+1,lb+25):
            beg=max(lb,start);count=n-beg
            result+=struct.pack('<7Q',p,pattern,start,n,beg,count,cap)
            result+=struct.pack('<Q',m.CANARY)+struct.pack('<d',-0. if pattern==2 else 10.)*count+struct.pack('<Q',m.CANARY)*(cap-count-1)
    path.write_bytes(result);return result


def test_c_alias_contract_capture_guards_ranges_and_complete_inventory(monkeypatch,tmp_path):
    monkeypatch.setattr(m,'STREAM_PERIODS',(4,));path=tmp_path/'c.bin';data=c_fixture(path)
    assert m.c_contract_capture(path)['cases']==12
    for offset in (0,8+6*8,8+7*8,8+7*8+1008*8-1):
        bad=data.copy();bad[offset]^=1;path.write_bytes(bad)
        with pytest.raises(ValueError):m.c_contract_capture(path)
    for bad in [data[:-1],data[:8],data+data[8:]]:
        path.write_bytes(bad)
        with pytest.raises(ValueError):m.c_contract_capture(path)


def runtime_logs(folder):
    folder.mkdir(exist_ok=True)
    logs=('full-four-language-regression.log','managed-libraries.log','generator-tests.log','rust-tests.log','rust-doc-tests.log','generator-clippy.log','rust-clippy.log','regenerate.log','java-version.txt','dotnet-info.txt')
    for log in logs:(folder/log).write_text('passed\n')
    reg='\n'.join(f'│ {label} │ 237 │ 0 │'for label in ('C','Rust','Java','C#'))
    managed='StreamSmokeTest: ALL PASS (99 checks)\nBatchApiTest: ALL PASS (77 checks)\nTALib C# tests on .NET 10.0.1\nBatchApiTest: ALL PASS (88 checks)\nAll 3 C# suite(s) passed.\n'
    (folder/logs[0]).write_text(reg);(folder/logs[1]).write_text(managed)
    return reg,managed


def test_all_four_actual_runtime_logs_required(tmp_path):
    reg,managed=runtime_logs(tmp_path)
    assert len(m.require_runtimes(tmp_path))==10
    for name,good,bad in [('full-four-language-regression.log',reg,reg.replace('Java │ 237','Java │ 236')),('managed-libraries.log',managed,managed.replace('StreamSmokeTest: ALL PASS','StreamSmokeTest: SKIP')),('managed-libraries.log',managed,managed.replace('TALib C# tests on .NET 10.','TALib C# tests on .NET 9.')),('managed-libraries.log',managed,'compiled java and C# successfully')]:
        (tmp_path/name).write_text(bad)
        with pytest.raises(ValueError):m.require_runtimes(tmp_path)
        (tmp_path/name).write_text(good)


def test_generated_ignored_config_is_only_pinned_empty_config(monkeypatch,tmp_path):
    test_pinned_git_source_and_dirty_rejection(tmp_path)
    # Restore the fixture to its pinned Git bytes after that test's dirty assertion.
    subprocess.run(['git','-C',str(tmp_path),'restore','.'],check=True)
    pin=subprocess.check_output(['git','-C',str(tmp_path),'rev-parse','HEAD'],text=True).strip()
    config=tmp_path/m.GENERATED_CONFIG;config.parent.mkdir(parents=True);config.write_text('[build]\n')
    # Simulate ignored output as Cargo regeneration does, without weakening the content rule.
    (tmp_path/'.git/info/exclude').write_text('/'+m.GENERATED_CONFIG+'\n')
    with pytest.raises(ValueError,match='untracked'):m.git_record(tmp_path,pin)
    monkeypatch.setattr(m,'GENERATED_CONFIG_SHA',m.sha256(config))
    assert m.git_record(tmp_path,pin)['generated_empty_config']=={m.GENERATED_CONFIG:m.sha256(config)}
    config.write_text('[build]\nrustflags=["-Ctarget-cpu=native"]\n')
    with pytest.raises(ValueError):m.git_record(tmp_path,pin)


def test_integration_full_library_identity_and_runtime_sealing(monkeypatch,tmp_path):
    dev=tmp_path/'dev';prod=tmp_path/'prod';logs=tmp_path/'logs'
    roots=(dev,prod)
    names=['ta_codegen/input/hma/hma.c','src/ta_func/ta_HMA.c','ta_codegen/output/java/fragments/Core_HMA.java','ta_codegen/output/rust/library/src/lib.rs','ta_codegen/output/java/library/src/Core.java','ta_codegen/output/csharp/library/Core.cs']
    for root in roots:
        for name in names:
            path=root/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_text('identical')
    def git(cmd,**kwargs):
        root=Path(cmd[2]);tail=cmd[3:]
        if tail==['rev-parse','HEAD']:return m.DEV_MERGE if root==dev else m.CANDIDATE
        if tail==['status','--porcelain']:return b''
        if tail==['cat-file','-p','HEAD']:return 'parent '+m.DEV_BASE+'\nparent '+m.TRIGGER+'\n'
        if tail[:4]==['ls-tree','-r','--name-only','HEAD']:return '\n'.join(n for n in names if n.startswith(tail[4]+'/'))
        raise AssertionError(cmd)
    monkeypatch.setattr(m.subprocess,'check_output',git)
    assert m.integration_proof(dev,prod,logs)['all_library_sources_identical']
    with pytest.raises(FileNotFoundError):m.integration_proof(dev,prod,logs,True)
    runtime_logs(logs);(logs/'dev-merge-source.tar.gz').write_bytes(b'fake archived dev source')
    complete=m.integration_proof(dev,prod,logs,True)
    assert complete['complete_before_primary_build']
    args=type('A',(),{'output':tmp_path})()
    (tmp_path/'dev-integration').symlink_to(logs,target_is_directory=True)
    assert m.verify_integration(args)['proof']==complete
    (prod/names[-1]).write_text('changed compiled library')
    with pytest.raises(ValueError,match='differs'):m.integration_proof(dev,prod,logs)


def test_isolated_measure_orchestration_all1224_children_and_global_gate(monkeypatch,tmp_path,capsys):
    args=type('A',(),{'output':tmp_path})();p={'input':{'path':'input'},**{s:{'binary':s}for s in m.SIDES}}
    (tmp_path/'build-provenance.json').write_text(json.dumps(p));events=[]
    monkeypatch.setattr(m,'verify',lambda *a:None)
    monkeypatch.setattr(m.os,'sched_getaffinity',lambda p:{2,3},raising=False)
    affinity=[];monkeypatch.setattr(m.os,'sched_setaffinity',lambda p,x:affinity.append(set(x)),raising=False)
    captures={s:m.parse_records(encoded(records()),True)for s in m.SIDES}
    goldens={}
    def split(path,folder):
        folder.mkdir()
        for b,n in m.TIMED_KEYS:
            dest=folder/(m.hashlib.sha256((b+'/'+n).encode()).hexdigest()+'.bin');dest.write_bytes((b+'/'+n).encode())
            goldens[b+'/'+n]={'path':str(dest),'sha256':m.sha256(dest),'bytes':dest.stat().st_size,'case':n,'backend':b}
        return goldens
    monkeypatch.setattr(m,'split_goldens',split)
    monkeypatch.setattr(m,'capture_record',lambda p:{'sha256':m.sha256(p),'bytes':p.stat().st_size})
    def execute(command,label,args,env):
        events.append((label,command))
        if '--capture-only'in command:
            Path(command[2]).write_bytes(b'identical full capture')
            return encoded(records())
        assert [x[0]for x in events[:2]]==['baseline-validation','candidate-validation']
        name=command[3];backend=command[5];golden=Path(command[7]);actual=Path(command[9])
        assert golden==Path(goldens[backend+'/'+name]['path'])
        actual.write_bytes(golden.read_bytes());return encoded(selected_rows((backend,name)))
    monkeypatch.setattr(m,'execute',execute)
    m.measure(args);capsys.readouterr()
    summary=json.loads((tmp_path/'summary.json').read_text())
    assert len(events)==1226 and summary['children']==1224 and summary['samples']==37944
    assert len(summary['results'])==51 and all(r['median_paired_ratio']==1 for r in summary['results'].values())
    for offset in range(2,len(events),24):
        side_order=[row[1][0]for row in events[offset:offset+24]]
        assert side_order==['baseline','candidate','candidate','baseline']*6
    assert affinity==[{2},{2,3}]and not list(tmp_path.glob('selected-*.bin'))
    # A mismatch in the second full capture must abort before any selected child.
    events.clear();original=execute
    def mismatch(command,label,args,env):
        text=original(command,label,args,env)
        if label=='candidate-validation':Path(command[2]).write_bytes(b'different full capture')
        return text
    monkeypatch.setattr(m,'execute',mismatch)
    with pytest.raises(ValueError,match='full primary captures differ'):m.measure(args)
    assert len(events)==2 and affinity[-1]=={2,3}


@pytest.mark.parametrize('partial',[b'partial output','partial output',None])
def test_timeout_preserves_failed_command_and_partial_logs(monkeypatch,tmp_path,partial):
    def fail(*args,**kwargs):raise subprocess.TimeoutExpired(args[0],180,output=partial,stderr=b'partial error')
    monkeypatch.setattr(m.subprocess,'run',fail)
    args=type('A',(),{'output':tmp_path})()
    with pytest.raises(subprocess.TimeoutExpired):m.execute(['probe','31'],'child',args,{})
    assert (tmp_path/'child.stdout.log').read_text()==(''if partial is None else 'partial output')
    assert (tmp_path/'child.stderr.log').read_text()=='partial error'
    assert json.loads((tmp_path/'child.failure.json').read_text())['type']=='TimeoutExpired'
    assert json.loads((tmp_path/'commands.jsonl').read_text())['argv']==['probe','31']


def test_protocol_workflow_pins_and_correctness_dependency():
    workflow=(Path(__file__).parents[1]/'.github/workflows/hma-review.yml').read_text()
    for pin in (m.BASELINE,m.CANDIDATE,m.DEV_MERGE,m.C_COMMIT):assert pin in workflow
    assert 'needs: dev-context-correctness'in workflow
    assert './ta_regtest --codegen --language=c,rust,java,csharp'in workflow
    assert 'global-json-file: integration/global.json'in workflow
    assert '--integration-output hma-review-dev --complete'in workflow
    assert 'java,csharp'in workflow and 'managed-libraries.log'in workflow
    assert 'libta_lib.rlib'in workflow and 'dev-integration/'in workflow
    assert '--pairs 12 --repeats 31'in workflow
