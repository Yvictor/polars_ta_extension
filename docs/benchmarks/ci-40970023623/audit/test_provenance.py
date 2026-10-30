import copy,importlib.util,json,tempfile,unittest
from pathlib import Path
import numpy as np
HERE=Path(__file__).parent
spec=importlib.util.spec_from_file_location('a',HERE/'audit.py');a=importlib.util.module_from_spec(spec);spec.loader.exec_module(a)

class Provenance(unittest.TestCase):
 def test_immutable_fourpins_exact_twofile_git_boundary(self):
  trust=a.js(HERE/'trusted.json');self.assertEqual(trust['run'],40970023623);self.assertEqual(trust['controller'],'5171ea5583f83766da05ef0d1f8bc69091063369');self.assertEqual(len(set(trust['pins'].values())),4);self.assertEqual(set(trust['candidate_git_changes']),{'src/compat/mavp_sma.rs','tests/test_mavp_uniform_prefix.py'})
  altered=copy.deepcopy(trust);altered['run']=True
  with tempfile.TemporaryDirectory()as d,self.assertRaisesRegex(ValueError,'fixed uniform'):a.audit(Path(d),altered)
 def test_public_build_commands_and_actual_elf_binding(self):
  ws=Path('/runner/ws');sides=('prior','combined','candidate','original');p={'flags':{'environment':{'CARGO_TARGET_DIR':str(ws/'mavp-uniform-target')}},'builds':{side:{'identity':{'native_files':{str(ws/'envs'/side/'module.so'):'digest:'+side}},'retained_native_files':{str(ws/'mavp-uniform-results/actual-native'/side/'module.so'):'digest:'+side},'product_elf':[{'path':str(ws/'mavp-uniform-results/actual-native'/side/'module.so'),'sha256':'digest:'+side,'format':'ELF64 little-endian x86-64'}]}for side in sides}};whl={side:{'native_sha256':'digest:'+side}for side in sides};commands=[{'side':side,'command':[str(ws/'envs'/side/'bin/python'),'-m','maturin','build','--release','--locked','--interpreter',str(ws/'envs'/side/'bin/python'),'--out',str(ws/'wheels'/side)]}for side in sides]
  for kind in('good','interpreter','release','order','elf_hash','elf_format'):
   with self.subTest(kind=kind),tempfile.TemporaryDirectory()as d:
    rows=copy.deepcopy(commands);proof=copy.deepcopy(p)
    if kind=='interpreter':rows[1]['command'][0]=str(ws/'envs/candidate/bin/python')
    elif kind=='release':rows[0]['command'].remove('--release')
    elif kind=='order':rows.reverse()
    elif kind=='elf_hash':proof['builds']['candidate']['product_elf'][0]['sha256']='WRONG'
    elif kind=='elf_format':proof['builds']['candidate']['product_elf'][0]['format']='ARM64'
    folder=Path(d);(folder/'build-commands.jsonl').write_text('\n'.join(json.dumps(r)for r in rows))
    if kind=='good':self.assertEqual(a.build_commands(folder,proof,whl),rows)
    else:
     with self.assertRaises(ValueError):a.build_commands(folder,proof,whl)
 def test_all_four_runtime_metadata_and_math_type_are_bound(self):
  trust=a.js(HERE/'trusted.json');p={'flags':{'rustc':'rustc 1.90.0 fixture'},'builds':{}};whl={}
  for side in a.SIDES:
   identity={'python':'3.12.15','platform':'Linux-x86_64','polars':'1.44.2','numpy':'2.5.3','package':'0.2.1','talib':'0.8.1 C'if side=='original'else'0.8.3 (native Rust; polars-talib compatibility)'};p['builds'][side]={'identity':identity};whl[side]={'native_sha256':side};row=dict(identity,commit=trust['pins'][side],source_sha256=trust['source_record'][side]['source_sha256'],native_binary_sha256=side,threads=4,repeats=31,warmups=5,diagnostic=False,integer_reference_exact=True,affinity=[0,1,2,3],rust='rustc 1.90.0 fixture',profile=a.core.PROFILE);a.metadata(row,side,4,trust,p,whl)
   for key,value in(('native_binary_sha256','wrong'),('commit',trust['pins']['prior'if side!='prior'else'combined']),('talib','wrong'),('threads',True),('affinity',[0,1,2,True]),('integer_reference_exact',1)):
    with self.subTest(side=side,key=key):
     changed=dict(row,**{key:value})
     with self.assertRaises(ValueError):a.metadata(changed,side,4,trust,p,whl)
 def test_native_root_multiversion_edge_and_portable_flags(self):
  for kind in('good','missing_multiversion','wrong_multiversion_fingerprint','root_flags','dependency_flags'):
   with self.subTest(kind=kind),tempfile.TemporaryDirectory()as d:
    base=Path(d);folder=base/'product-fingerprints/candidate';folder.mkdir(parents=True);wanted=('ta_lib','serde','polars','jemallocator','pyo3_polars','multiversion')
    for name in('_polars_talib',*wanted):
     child=folder/name;child.mkdir();meta=child/('lib-'+name+'.json');deps=[[0,n,False,0]for n in wanted]if name=='_polars_talib'else[]
     if name=='_polars_talib'and kind=='missing_multiversion':deps=[r for r in deps if r[1]!='multiversion']
     if name=='_polars_talib'and kind=='wrong_multiversion_fingerprint':deps[-1][-1]=123
     flags=['-Ctarget-cpu=native']if(kind=='root_flags'and name=='_polars_talib')or(kind=='dependency_flags'and name=='ta_lib')else[]
     meta.write_text(json.dumps({'deps':deps,'rustflags':flags,'profile':123}));meta.with_suffix('').write_text('0000000000000000')
    if kind=='good':self.assertEqual(len(a.fingerprints(base,'candidate')['matching_normal_roots']),1)
    else:
     with self.assertRaises(ValueError):a.fingerprints(base,'candidate')
 def test_split_and_fractional_routes_per_group(self):
  for pattern in('early','last','fractional'):
   name='grouped_mavp_'+pattern+'/2x100';n=200;symbol=np.repeat(np.arange(2),100);raw=a.physical.periods(pattern,n,100,True);cols={'close':np.linspace(100.,101.,n),'periods':raw,'symbol':symbol};cov,_=a.physical.route(name,cols)
   if pattern=='fractional':self.assertEqual(cov['raw_period_values'],[14.01,14.25,14.999])
   else:self.assertEqual(cov['normalized_first_difference'],1 if pattern=='early'else 70)
   altered={k:v.copy()for k,v in cols.items()}
   if pattern=='fractional':altered['periods'][30]=14.125
   else:altered['periods'][100:]=14.
   with self.assertRaises(ValueError):a.physical.route(name,altered)
if __name__=='__main__':unittest.main()
