"""Freeze independent expectations from immutable Git, before result access."""
import hashlib,io,json,subprocess,tarfile
from pathlib import Path
from datetime import datetime,timezone
HERE=Path(__file__).parent;REPO=HERE.parent/'sarext-typed-ci'
PINS={'original':'b2bbc26d41ec80823c8bffb0cc436a97f29911cc','prior':'56f6d5fb139031c20d86d7e818e7d267eb834295','candidate':'8a4fc7feacc45b28929b2e7e6d1ae9919623bd2b','alternative':'f7d800398ecd6dc79c5b346e7e151cf917272327'}
CONTROLLER='37a98e2326cdcdd3d8c3b8048b1b4143199e09c6'
def archive(pin):
 b=subprocess.check_output(['git','-C',str(REPO),'archive','--format=tar',pin])
 with tarfile.open(fileobj=io.BytesIO(b))as t:return {m.name:t.extractfile(m).read()for m in t if m.isfile()}
def selected(name):
 p=Path(name)
 return (p.suffix in('.rs','.py')or p.name in('Cargo.toml','Cargo.lock'))and not({'target','.venv','.git','__pycache__'}&set(p.parts))and(len(p.parts)==1 or p.parts[0]in('src','python','talib','talib-sys'))
def main():
 t={'run':40965216581,'controller':CONTROLLER,'frozen_at_utc':datetime.now(timezone.utc).isoformat(),'before_raw_artifact_access':True,'before_ci_measurements':True,'pins':PINS,'source_record':{},'source_file_sha256':{},'wheel_python_sha256':{}}
 for side,pin in PINS.items():
  files=archive(pin);subset={n:b for n,b in files.items()if selected(n)};h=hashlib.sha256()
  for n in sorted(subset,key=lambda p:Path(p).parts):h.update(n.encode());h.update(subset[n])
  t['source_record'][side]={'commit':pin,'source_sha256':h.hexdigest(),'clean':True};t['source_file_sha256'][side]={n:hashlib.sha256(b).hexdigest()for n,b in subset.items()};t['wheel_python_sha256'][side]={n.removeprefix('python/'):hashlib.sha256(b).hexdigest()for n,b in files.items()if n.startswith('python/polars_talib/')and n.endswith('.py')}
 c=archive(CONTROLLER);paths=['.github/workflows/sarext-typed.yml',*[f'scripts/sarext_typed_{p}'for p in('benchmark.py','provenance.py','inputs.py','query.py','cases.json','zero_regression.py','elf.py')],'scripts/migration_probe.py','scripts/migration_ci_benchmark.py','scripts/api.json','tests/test_sarext_typed_benchmark.py']
 t['controller_sha256']={p:hashlib.sha256(c[p]).hexdigest()for p in paths};t['case_manifest']=json.loads(c['scripts/sarext_typed_cases.json']);t['api']=json.loads(c['scripts/api.json']);t['shared_core_sha256']='b8c0b004daac5d920835c7a316cf97919cc3a13633eeecd860fdd02ab669cba9'
 t['protocol']={'cases_per_thread':14,'threads':[1,4],'rounds':12,'samples':31,'warmups':5,'children':1344,'raw_samples':41664,'checked_values_per_setting':12400000,'physical_input_snapshots':10}
 t['limits']=['Trust frozen before raw artifact access, after CI measurements began.','Raw physical IPC inputs and all four own-arm golden arrays are replayed independently. All four arms’ query golden arrays are retained at both thread settings and independently replayed. Timed final arrays are not duplicated: exact source-bound final checks/hashes are bound to each arm golden. All four complete corpus arrays are independently replayed.','C corpus uses historical tolerance1e-10, integer outputs exact; native corpus requires exact finite/signed-zero/masks/NaN positions. NaN sign/payload not a public guarantee.','Shared-target Cargo metadata/fingerprints/dependency edges/portable flags are inspected but are not a unique cryptographic ELF-to-linked-rlib bridge; source/wheel binding includes exact actual compile logs and immutable workflow execution.','Twelve process rounds and correlated inner samples are descriptive, not formal multiple-comparison significance; no pooling thread settings/runners.','Fault counters cover engine/Python/allocator activity across query threads, not allocator-only events.']
 (HERE/'trusted.json').write_text(json.dumps(t,indent=2)+'\n');print(json.dumps({'pins':PINS,'source_record':t['source_record'],'controller_files':len(paths),'protocol':t['protocol']},indent=2))
if __name__=='__main__':main()
