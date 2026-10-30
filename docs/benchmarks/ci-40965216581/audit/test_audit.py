import copy,hashlib,json,statistics,tempfile,unittest
from pathlib import Path
from collections import Counter
import numpy as np
import polars as pl
import audit as a
import inputs as physical

class Arrays(unittest.TestCase):
 def test_exact_and_tolerant_zero_semantics(self):
  z=np.zeros(3,bool);x=np.array([0.,1.,np.nan]);a.arrays(x,x,z,z,exact=True)
  for exact in(False,True):
   with self.subTest(exact=exact),self.assertRaises(ValueError):a.arrays(x,np.array([-0.,1.,np.nan]),z,z,exact=exact)
  with self.assertRaises(ValueError):a.arrays(np.array([0.]),np.array([1e-15]),z[:1],z[:1],strict_zero=True)
  a.arrays(np.array([0.]),np.array([1e-15]),z[:1],z[:1],exact=False)
  with self.assertRaises(ValueError):a.arrays(np.array([1e-20]),np.array([1e-15]),z[:1],z[:1],tiny=True)
 def test_contract_corruptions(self):
  x=np.array([0.,2.,np.nan,np.inf,-np.inf]);mask=np.zeros(5,bool)
  for label,y,m in [('value',np.array([0.,2.001,np.nan,np.inf,-np.inf]),mask),('nan',np.array([0.,2.,0.,np.inf,-np.inf]),mask),('inf',np.array([0.,2.,np.nan,-np.inf,-np.inf]),mask),('null',x,np.array([0,1,0,0,0],bool)),('dtype',x.astype(np.float32),mask),('shape',x[:-1],mask[:-1])]:
   with self.subTest(label=label),self.assertRaises(ValueError):a.arrays(x,y,mask,m,exact=False)
  y=x.copy();y.view(np.uint64)[2]^=np.uint64(1<<63);a.arrays(x,y,mask,mask,exact=True)
 def test_strict_json_and_types(self):
  for s in ['{"a":1,"a":1}','{"a":NaN}']:
   with self.assertRaises(ValueError):a.core.decode(s)
  for got,want in [(True,1),(1,True),(1.0000000000001,1.),({'x':1,'y':2},{'x':1}),([1],[1,2])]:
   with self.subTest(got=got),self.assertRaises(ValueError):a.eq(got,want)

class Physical(unittest.TestCase):
 def fixture(self,root,names):
  records={}
  for name in names:
   cols=physical.regenerate(name);token=physical.digest(cols);path=root/(token+'.arrow');pl.DataFrame(cols).write_ipc(path,compression='zstd');records[name]={'file':path.name,'sha256':physical.sha(path),'bytes':path.stat().st_size,'fixture_sha256':token,'schema':str(physical.SCHEMA),'rows':len(cols['close'])}
  return records
 def test_exact_physical_seed_and_group_mapping(self):
  names=['sarext/100','sar/100','grouped_sarext_reversal/3x8_interleaved','grouped_sarext_longzero/3x8']
  with tempfile.TemporaryDirectory()as d:
   p=Path(d);records=self.fixture(p,names);expected,fixture,proof=physical.audit_inputs(p,records,names,3);self.assertEqual(len(proof),3);self.assertIsNone(expected[names[0]])
   for field in ['high','volume','symbol','periods']:
    with self.subTest(field=field):
     name=names[0];rec=records[name];path=p/rec['file'];cols=physical.regenerate(name);cols[field]=cols[field].copy();cols[field][4]+=1 if field=='symbol'else .001;token=physical.digest(cols);bad=p/(token+'.arrow');pl.DataFrame(cols).write_ipc(bad,compression='zstd');mut=copy.deepcopy(records);mut[name]={'file':bad.name,'sha256':physical.sha(bad),'bytes':bad.stat().st_size,'fixture_sha256':token,'schema':str(physical.SCHEMA),'rows':100}
     with self.assertRaises(ValueError):physical.audit_inputs(p,mut,names,3)
     bad.unlink()
   orphan=p/'orphan';orphan.write_text('x')
   with self.assertRaises(ValueError):physical.audit_inputs(p,records,names,3)
 def test_coverage_warmup_reversal_longzero(self):
  name='grouped_sarext_longzero/3x8_interleaved';chron=np.tile(np.arange(8,dtype=float),(3,1));chron[:,0]=np.nan;chron[:,1]=-0.;arr=chron.T.ravel();cov=physical.coverage(name,arr);self.assertEqual(cov['minimum_negative_zeros_per_group'],1)
  bad=arr.copy();bad.view(np.uint64)[4]=0
  with self.assertRaises(ValueError):physical.coverage(name,bad)
  bad=arr.copy();bad[0]=1
  with self.assertRaises(ValueError):physical.coverage(name,bad)
  name='grouped_sarext_reversal/3x8_interleaved';chron=np.tile(np.array([np.nan,1.,-1.,1.,-1.,1.,-1.,1.]),(3,1));physical.coverage(name,chron.T.ravel());chron[2,1:]=1
  with self.assertRaises(ValueError):physical.coverage(name,chron.T.ravel())
 def test_cumsum_scatter_and_uniform_fixed_operators(self):
  name='control_cumsum/3x8_interleaved';cols=physical.regenerate(name);out=physical.control(name,cols)
  for g in range(3):np.testing.assert_array_equal(out[cols['symbol']==g],np.cumsum(cols['close'][cols['symbol']==g]))
  n=100;rng=np.random.default_rng(260126);rng.normal(0,.1,n);wanted=100.+900.*rng.random(n);np.testing.assert_array_equal(physical.regenerate('sarext/100')['volume'].view(np.uint64),wanted.view(np.uint64))

class Ledger(unittest.TestCase):
 def test_complete_balanced_inventory(self):
  trust=json.loads((Path(__file__).parent/'trusted.json').read_text());names=trust['case_manifest']['cases'];rows=a.ledger(names);self.assertEqual(len(rows),672);self.assertEqual(len({r['report']for r in rows}),672);self.assertEqual(len(a.PAIRS),6)
  for name in names:
   selected=[r for r in rows if r['case']==name];self.assertEqual(Counter(x['side']for x in selected),{s:12 for s in a.SIDES})
   orders=[tuple(x['side']for x in selected[i:i+4])for i in range(0,48,4)];self.assertEqual(orders,list(a.ORDERS)*3)
   positions=Counter((side,index)for order in orders for index,side in enumerate(order));self.assertEqual(set(positions.values()),{3})
 def test_exact_command_own_arm_reference(self):
  ws=Path('/runner/work/repo');name='grouped_sarext/10000x100';cmd=a.cli_record(ws,4,'alternative','case-003-alternative-1',[name],['--reference',str(ws/'sarext-results/threads-4/alternative-reference.npz'),'--exact-reference'],name);self.assertEqual(cmd['argv'][-2:],['--case-filter',name]);self.assertEqual(cmd['side'],'alternative');self.assertIn('--exact-reference',cmd['argv'])
  bad=copy.deepcopy(cmd);bad['argv'][bad['argv'].index('--reference')+1]=str(ws/'sarext-results/threads-4/reference.npz')
  with self.assertRaises(ValueError):a.eq(bad,cmd)
 def test_timing_recomputes_sample_semantics(self):
  samples=list(range(1,32));name='sarext/1000000';row={'case_inventory':[name],'case_filters':[name],'checked_values':1000000,'exact_reference':True,'final_output_checked':True,'results':{name:{'rows':1000000,'output_fields':1,'samples_ms':samples,'median_ms':16.,'min_ms':1.,'minor_faults':[0]*31,'major_faults':[0]*31}}};a.timing(row,name)
  for key,value in [('checked_values',True),('final_output_checked',False),('case_filters',[]),('exact_reference',False)]:
   bad=copy.deepcopy(row);bad[key]=value
   with self.subTest(key=key),self.assertRaises(ValueError):a.timing(bad,name)
  for key,value in [('samples_ms',[1]*30),('samples_ms',[True]*31),('samples_ms',[float('inf')]*31),('median_ms',16.000000001),('min_ms',2),('rows',True),('minor_faults',[False]*31),('major_faults',[-1]*31)]:
   bad=copy.deepcopy(row);bad['results'][name][key]=value
   with self.subTest(key=key),self.assertRaises(ValueError):a.timing(bad,name)

class ZeroAndElf(unittest.TestCase):
 def zeroes(self):
  rows={s:{'cases':{}}for s in a.SIDES}
  for f in a.ZERO_FIXTURES:
   for inter in(False,True):
    name=f[0]+('/interleaved'if inter else'/dense');meta=a.zero_metadata(f,inter);x=np.arange(len(meta['nulls']),dtype=float)+1;x[np.array(meta['nan'])]=np.nan;x[meta['target_zero_positions']]=0.;words=x.view(np.uint64).tolist()
    for side in a.SIDES:
     wanted=words.copy()
     if side=='prior':
      for i in meta['target_zero_positions']:wanted[i]=1<<63
     rows[side]['cases'][name]={**copy.deepcopy(meta),'words':wanted}
  return rows
 def test_zero_waiver_cannot_escape_named_untimed_positions(self):
  rows=self.zeroes();got=a.zero_captures(rows);self.assertEqual(len(got),4)
  for side in a.SIDES:
   bad=copy.deepcopy(rows);name='short_cancellation/interleaved';bad[side]['cases'][name]['words'][-1]=123
   with self.subTest(side=side),self.assertRaises(ValueError):a.zero_captures(bad)
  for field,value in [('groups',True),('eager_lazy_raw_identity',1),('target_zero_positions',[0]),('symbol',[0]),('params',{})]:
   bad=copy.deepcopy(rows);bad['original']['cases']['short_cancellation/interleaved'][field]=value
   with self.subTest(field=field),self.assertRaises(ValueError):a.zero_captures(bad)
 def test_exact_relative_fma_scope_and_tail_calls(self):
  text=' 100: call *0x12(%rip) # 200\n 110: jmp *0x14(%rip) # 208\n 120: vfmadd213sd %xmm0,%xmm1,%xmm2\n';rel='00000200 0000 R_X86_64_RELATIVE 300\n00000208 0000 R_X86_64_GLOB_DAT 0000 fma@GLIBC_2.2.5 + 0';symbols='00000300 t fma\n';got=a.elf_lines(text,rel,symbols);self.assertEqual(len(got['inline_fma_instruction_lines']),1);self.assertEqual(len(got['libm_fma_control_transfer_lines']),2)
  for wrong in ['00000301 t fma\n','00000300 t my_fma\n','00000300 d fma\n']:
   self.assertEqual(len(a.elf_lines(text,rel,wrong)['libm_fma_control_transfer_lines']),1)
  self.assertEqual(len(a.elf_lines(text,rel.replace('R_X86_64_RELATIVE','R_UNKNOWN'),symbols)['libm_fma_control_transfer_lines']),1)
 def test_word_diagnostics_report_nan_sign_zero_and_position_separately(self):
  with tempfile.TemporaryDirectory()as d:
   p=Path(d);meta={'cases':{'sarext/test':{'fields':['v']}}};x=np.array([0.,np.nan,1e-15]);y=np.array([-0.,np.nan,0.]);y.view(np.uint64)[1]^=np.uint64(1<<63)
   for name,value in [('a',x),('b',y)]:np.savez(p/(name+'.npz'),metadata=np.array(json.dumps(meta)),v=value,v_null=np.zeros(3,bool))
   r=a.words_diagnostics(p/'a.npz',p/'b.npz');self.assertEqual(r['both_zero_sign_differences'],1);self.assertEqual(r['zero_position_differences'],1);self.assertEqual(r['nan_word_differences'],1);self.assertEqual(r['finite_word_differences'],2)
if __name__=='__main__':unittest.main()

class Provenance(unittest.TestCase):
 def test_metadata_requires_immutable_product_and_real_affinity(self):
  trust={'pins':{'candidate':'a'*40},'source_record':{'candidate':{'source_sha256':'b'*64}}};whl={'candidate':{'native_sha256':'c'*64}};identity={'python':'3.12.15','platform':'Linux-x86_64','polars':'1.44.2','numpy':'2.5.3','package':'0.2.1','talib':'0.8.3 (native Rust; polars-talib compatibility)'};p={'builds':{'candidate':{'identity':identity}},'flags':{'rustc':'rustc 1.90.0 (example)\nhost: x86_64-unknown-linux-gnu'}};row={**identity,'commit':'a'*40,'source_sha256':'b'*64,'native_binary_sha256':'c'*64,'threads':4,'repeats':31,'warmups':5,'affinity':[0,1,2,3],'diagnostic':False,'integer_reference_exact':True,'rust':'rustc 1.90.0 (example)','profile':a.core.PROFILE};a.metadata(row,'candidate',4,trust,p,whl)
  for key,value in [('commit','d'*40),('source_sha256','d'*64),('native_binary_sha256','d'*64),('package','0.3'),('threads',True),('repeats',True),('warmups',False),('affinity',[0,0,1,2]),('affinity',[0,1,2,True]),('diagnostic',0),('integer_reference_exact',1),('rust','rustc 1.97.0')]:
   bad=copy.deepcopy(row);bad[key]=value
   with self.subTest(key=key),self.assertRaises(ValueError):a.metadata(bad,'candidate',4,trust,p,whl)
 def test_cold_proof_rejects_zero_filtered_comment_or_wrong_test(self):
  name='sarext_legacy::tests::cold_parallel_dispatch_matches_portable_scalar_without_shared_mutable_inputs'
  with tempfile.TemporaryDirectory()as d:
   p=Path(d);inventory=p/'B-test-inventory.log';log=p/'B-cold-dispatch-first.log';inventory.write_text(name+': test\n');valid='running 1 test\ntest '+name+' ... ok\ntest result: ok. 1 passed; 0 failed; 0 ignored; 0 measured; 99 filtered out;\n';log.write_text(valid);a.cold_proof(p)
   for text in [valid.replace('1 passed','0 passed'),valid.replace('running 1 test','running 0 tests'),valid.replace('test '+name,'# test '+name),valid.replace(name,'other')]:
    log.write_text(text)
    with self.assertRaises(ValueError):a.cold_proof(p)
 def test_golden_schema_zero_masks_and_inventory(self):
  with tempfile.TemporaryDirectory()as d:
   p=Path(d);name='sarext/3';expected={name:None};x=np.array([np.nan,0.,1.]);values={name+'_schema':np.array("Schema({'sarext': Float64})"),name+'_0':x,name+'_0_null':np.zeros(3,bool)};np.savez(p/'a.npz',**values);a.golden(p/'a.npz',[name],expected)
   for kind in ['zero','tiny','schema','mask','orphan']:
    mut={k:v.copy()for k,v in values.items()}
    if kind=='zero':mut[name+'_0'][1]=-0.
    elif kind=='tiny':mut[name+'_0'][1]=1e-15
    elif kind=='schema':mut[name+'_schema']=np.array("Schema({'wrong': Float64})")
    elif kind=='mask':mut[name+'_0_null'][1]=True
    else:mut['unexpected']=np.array([1])
    np.savez(p/'b.npz',**mut)
    with self.subTest(kind=kind),self.assertRaises(ValueError):
     if kind=='orphan':a.golden(p/'b.npz',[name],expected)
     else:a.compare_goldens(p/'a.npz',p/'b.npz',[name],False)


class ElfRoles(unittest.TestCase):
 def test_roles_require_exact_unique_source_bound_names(self):
  clone='_ZN12polars_talib13sarext_legacy68dispatched_scalar_avx_fma_sse_sse2_sse3_sse41_ssse3_version17h0123E';wrapper='_ZN12polars_talib13sarext_legacy17dispatched_scalar17h0123E';resolver='_ZN12polars_talib13sarext_legacy17dispatched_scalar14__detect_index8__detect17h0123E';functions={clone:{},wrapper:{},resolver:{}};roles={'fma_clone':clone,'portable_dispatch_wrapper':wrapper,'feature_resolver':resolver};a.eq(a.elf_roles(functions),roles)
  swapped={**roles,'fma_clone':wrapper,'portable_dispatch_wrapper':clone}
  with self.assertRaises(ValueError):a.eq(swapped,a.elf_roles(functions))
  for symbol in functions:
   missing={k:v for k,v in functions.items()if k!=symbol}
   with self.subTest(mode='missing',symbol=symbol),self.assertRaises(ValueError):a.elf_roles(missing)
   duplicate={**functions,symbol.replace('0123','abcd'):{}}
   with self.subTest(mode='duplicate',symbol=symbol),self.assertRaises(ValueError):a.elf_roles(duplicate)
  wrong={clone.replace('avx_fma','avx_fmz'):{},wrapper:{},resolver:{}}
  with self.assertRaises(ValueError):a.elf_roles(wrong)


class ElfHeaderBinding(unittest.TestCase):
 def test_exact_single_function_header_and_defined_text_symbol(self):
  text='Disassembly of section .text:\n00000000000100 <function_A>:\n 100: ret\n';symbols='00000100 t function_A\n';a.function_header(text,'function_A',symbols)
  for wrong in [text.replace('function_A','function_B'),'no header\n',text+'00000120 <function_B>:\n 120: ret\n',text+'00000100 <function_A>:\n 100: ret\n']:
   with self.subTest(text=wrong),self.assertRaises(ValueError):a.function_header(wrong,'function_A',symbols)
  for wrong in ['00000101 t function_A\n','00000100 d function_A\n','00000101 t function_B\n','00000100 t prefix_function_A_suffix\n']:
   with self.subTest(symbols=wrong),self.assertRaises(ValueError):a.function_header(text,'function_A',wrong)

class ProducerDiagnosticPaths(unittest.TestCase):
 def test_only_exact_recorded_absolute_or_producer_relative_paths_same_arm(self):
  p={'flags':{'environment':{'CARGO_TARGET_DIR':'/runner/work/repo/sarext-target'}}}
  with tempfile.TemporaryDirectory()as directory:
   base=Path(directory)/'sarext-results';dest=base/'product-elf/alternative/header.txt';dest.parent.mkdir(parents=True);dest.write_text('actual');native=base/'actual-native/alternative/product.so';native.parent.mkdir(parents=True);native.write_text('binary');args={'area':'product-elf','side':'alternative'}
   for path in ['/runner/work/repo/sarext-results/product-elf/alternative/header.txt','sarext-results/product-elf/alternative/header.txt']:
    self.assertEqual(a.remap(path,base,p,**args),dest)
   self.assertEqual(a.remap('/runner/work/repo/sarext-results/actual-native/alternative/product.so',base,p,area='actual-native',side='alternative'),native)
   for path in ['product-elf/alternative/header.txt','other-results/product-elf/alternative/header.txt','/other/work/repo/sarext-results/product-elf/alternative/header.txt','sarext-results/product-elf/prior/header.txt','sarext-results/actual-native/alternative/product.so','sarext-results/product-elf/alternative/../alternative/header.txt','sarext-results/product-elf/alternative/missing.txt','sarext-results\\product-elf\\alternative\\header.txt']:
    with self.subTest(path=path),self.assertRaises(ValueError):a.remap(path,base,p,**args)
   link=dest.parent/'link.txt';link.symlink_to(dest)
   with self.assertRaises(ValueError):a.remap('sarext-results/product-elf/alternative/link.txt',base,p,**args)
   other=base/'product-elf/prior';other.mkdir();(other/'header.txt').write_text('other');parent_link=dest.parent/'crossarm';parent_link.symlink_to(other,target_is_directory=True)
   with self.assertRaises(ValueError):a.remap('sarext-results/product-elf/alternative/crossarm/header.txt',base,p,**args)
