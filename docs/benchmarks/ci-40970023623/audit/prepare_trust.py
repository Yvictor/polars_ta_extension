"""Freeze independent Git expectations before accessing uniform-MAVP raw artifacts."""
import argparse,hashlib,io,json,subprocess,tarfile
from pathlib import Path
from datetime import datetime,timezone
HERE=Path(__file__).parent;REPO=HERE.parent/'mavp-uniform-ci'
PINS={'original':'b2bbc26d41ec80823c8bffb0cc436a97f29911cc','prior':'56f6d5fb139031c20d86d7e818e7d267eb834295','combined':'0eb91280cf5d13095cbfdc6f8bcc477cfbcd1498','candidate':'916b0de68369df410559b6dc651731cf4c36b94c'}
CONTROLLER='5171ea5583f83766da05ef0d1f8bc69091063369'
HELPER='c90e922f7a2289e6408306409ce77edc582e5a25ee98d21138f74a2bbab23fd8'
def archive(pin):
 b=subprocess.check_output(['git','-C',str(REPO),'archive','--format=tar',pin])
 with tarfile.open(fileobj=io.BytesIO(b))as z:return {m.name:z.extractfile(m).read()for m in z if m.isfile()}
def selected(name):
 p=Path(name);return(p.suffix in('.rs','.py')or p.name in('Cargo.toml','Cargo.lock'))and not({'target','.venv','.git','__pycache__'}&set(p.parts))and(len(p.parts)==1 or p.parts[0]in('src','python','talib','talib-sys'))
def main(run):
 need=lambda ok,msg:None if ok else(_ for _ in()).throw(ValueError(msg))
 need(type(run)is int and run>0,'actual workflow run ID required')
 trust={'run':run,'controller':CONTROLLER,'pins':PINS,'frozen_at_utc':datetime.now(timezone.utc).isoformat(),'before_raw_artifact_access':True,'source_record':{},'source_file_sha256':{},'wheel_python_sha256':{}};allfiles={}
 for side,pin in PINS.items():
  files=archive(pin);allfiles[side]=files;subset={n:b for n,b in files.items()if selected(n)};h=hashlib.sha256()
  for n in sorted(subset,key=lambda x:Path(x).parts):h.update(n.encode());h.update(subset[n])
  trust['source_record'][side]={'commit':pin,'source_sha256':h.hexdigest(),'clean':True};trust['source_file_sha256'][side]={n:hashlib.sha256(b).hexdigest()for n,b in subset.items()};trust['wheel_python_sha256'][side]={n.removeprefix('python/'):hashlib.sha256(b).hexdigest()for n,b in files.items()if n.startswith('python/polars_talib/')and n.endswith('.py')}
 changed=sorted(n for n in set(allfiles['combined'])|set(allfiles['candidate'])if allfiles['combined'].get(n)!=allfiles['candidate'].get(n));need(changed==['src/compat/mavp_sma.rs','tests/test_mavp_uniform_prefix.py'],'exact two-file product change')
 trust['candidate_git_changes']={n:hashlib.sha256(allfiles['candidate'][n]).hexdigest()for n in changed};need(trust['candidate_git_changes']['src/compat/mavp_sma.rs']==HELPER,'reviewed helper bytes')
 c=archive(CONTROLLER);paths=['.github/workflows/mavp-uniform.yml',*[f'scripts/mavp_uniform_{n}'for n in('benchmark.py','provenance.py','inputs.py','query.py','cases.json')],'scripts/MAVP_UNIFORM_CI.md','scripts/migration_probe.py','scripts/migration_ci_benchmark.py','scripts/api.json','tests/test_mavp_uniform_benchmark.py']
 trust['controller_sha256']={n:hashlib.sha256(c[n]).hexdigest()for n in paths};trust['case_manifest']=json.loads(c['scripts/mavp_uniform_cases.json']);trust['api']=json.loads(c['scripts/api.json']);trust['shared_core_sha256']='b8c0b004daac5d920835c7a316cf97919cc3a13633eeecd860fdd02ab669cba9'
 trust['protocol']={'cases_per_thread':32,'threads':[1,4],'rounds':12,'samples':31,'warmups':5,'children':3072,'raw_samples':95232,'checked_values_per_setting':30400000,'physical_snapshots':24,'pair_rows':384}
 trust['limits']=['Trust frozen from immutable Git before any uniform-MAVP raw artifact/results access.','All24physical IPC inputs, all8own-arm/thread query goldens and4full corpora are retained. Timedfinal arrays are checked/hashed against each arm golden but not duplicated for every child.','Shared-target Cargo snapshots bind selected dependency edges/flags but may include old roots; no unique measuredELF-to-linkedrlib bridge is claimed. Source/wheel/actualELF compile and byte identities are checked.','Twelve process rounds and correlated31inner samples are descriptive; process ranges are not confidence intervals or multiple-comparison significance. No pooling runners or thread settings.','Fault counters are whole-process engine/Python/allocator/thread activity, not allocator-only causation. Zero-allocation evidence is separate from latency.','C finite differences use declared1e-10 policy with tighter tiny absolute tolerance; both-zero signs are strict. Native finite/signedzero/null/NaN/Inf positions are exact. NaNpayload/sign are outside the exact contract.','Actual normal-wheel bounds removal or cold-dispatch speedups are not established by source labels. Source route/early-split proofs are eligibility, not branch instrumentation.']
 (HERE/'trusted.json').write_text(json.dumps(trust,indent=2)+'\n');print(json.dumps({k:trust[k]for k in('run','controller','pins','source_record','candidate_git_changes','protocol')},indent=2))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--run',type=int,required=True);main(p.parse_args().run)
