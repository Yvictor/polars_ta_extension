import copy
import importlib.util
import json
from pathlib import Path
import struct
import subprocess
import sys
import tomllib

import pytest

spec=importlib.util.spec_from_file_location('hma_weights_benchmark',Path(__file__).parents[1]/'scripts/hma_weights_benchmark.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)


def records(timed=False):
    result=[{'kind':'metadata','format':1,'cases':15,'validation_cases':417,'backends':list(m.BACKENDS),
             'canary_bits':'7ff80000000055aa','output_prefix':1,'warmups':5,'repeats':31,'capture_only':not timed,
             'registry_version':'0.8.3','current_version':'0.8.4','c_version':'0.8.1 (reference)',
             'os':'linux','arch':'x86_64','capture_written':not timed,'capture_records':1296,
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
    assert len(m.CASES)==15 and len(m.VALIDATION)==417 and len(m.KEYS)==1296
    assert m.expected_range('hma/p20/20')==(20,0,0)
    assert m.expected_range('hma/p20/100')==(100,22,78)
    assert m.expected_range('sma_control/p20/20')==(20,19,1)
    assert m.expected_range('validation/hma/finite/p20/n1000/start500')==(1000,500,500)
    assert m.parse_records(encoded(records()),True)['cases']=={}
    assert len(m.parse_records(encoded(records(True)),False)['cases'])==45


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
    with pytest.raises(ValueError,match='samples'):m.parse_records(encoded(rows),False)


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
    assert m.harness_command('/bin/probe')==['/bin/probe','31']
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
