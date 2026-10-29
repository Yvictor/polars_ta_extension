import collections,importlib.util,json,math,struct,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import sarext_profile_benchmark as s

class Protocol(unittest.TestCase):
 def test_fixed_inventory_and_samples(self):
  self.assertEqual((len(s.CELLS),len(set(s.CELLS))),(50,50));self.assertEqual(sum(len(ms)*12 for _,_,ms in s.GROUPS),600);self.assertEqual(600*31,18600)
  self.assertEqual(sum(m in s.KERNEL for _,_,m in s.CELLS),32)
 def test_four_mode_orders_balance_positions_and_predecessors(self):
  self.assertEqual(len(s.ORDERS4),12)
  for pos in range(4):self.assertEqual(collections.Counter(o[pos]for o in s.ORDERS4),{i:3 for i in range(4)})
  pairs=collections.Counter((o[i],o[i+1])for o in s.ORDERS4 for i in range(3));self.assertEqual(set(pairs.values()),{3});self.assertEqual(len(pairs),12)
 def test_two_mode_orders_balance(self):
  self.assertEqual(collections.Counter(s.ORDERS2),{(0,1):6,(1,0):6})
 def test_iters_exact(self):self.assertEqual(s.ITERS,{0:10000,100:1000,1000:100,10000:10,1000000:1})
 def text(self,mode='rust_typed',n=100,action='--golden'):
  out=f'C_VERSION 0.8.1 (test)\nVALIDATE fixture=default mode={mode} n={n} golden_verified={str(action!="--capture-only").lower()} physical_tail={str(mode in s.KERNEL and mode!="native_full").lower()}\n'
  if action=='--golden':out+='PROBE iters='+str(s.ITERS[n])+' warmups=5 samples='+json.dumps([1.]*31)+'\n'
  if action=='--counter':out+='COUNTER counts=[2,100,0,1]\n'
  return out
 def test_timing_parse(self):self.assertEqual(s.parse(self.text(),'default',100,'rust_typed','--golden')['median_ns'],1.)
 def test_capture_parse_no_timing(self):self.assertEqual(s.parse(self.text(action='--capture-only'),'default',100,'rust_typed','--capture-only'),{})
 def test_counter_separate_parse(self):self.assertEqual(s.parse(self.text(action='--counter'),'default',100,'rust_typed','--counter')['counts'],[2,100,0,1])
 def test_parse_negatives(self):
  text=self.text()
  for bad in (text.replace('0.8.1','0.8.3'),text.replace('warmups=5','warmups=4'),text.replace('golden_verified=true','golden_verified=false'),text.replace('physical_tail=true','physical_tail=false'),text+text,text.replace('iters=1000','iters=1'),text.replace('[1.0,','[NaN,'),text.replace('[1.0,','[true,'),text.replace('[1.0,','[-1.0,'),text.replace('1.0, ','',1),text+'COUNTER counts=[0,0,0,0]\n'):
   with self.subTest(bad=bad[:120]):
    with self.assertRaises(AssertionError):s.parse(bad,'default',100,'rust_typed','--golden')
 def test_counter_negative_values(self):
  for counts in ('[true,0,0,0]','[1,0,1,1]','[-1,0,0,0]','[0,0,0]'):
   with self.assertRaises(AssertionError):s.parse(self.text(action='--counter').replace('[2,100,0,1]',counts),'default',100,'rust_typed','--counter')
 def test_counter_cannot_smuggle_timing(self):
  with self.assertRaises(AssertionError):s.parse(self.text(action='--counter')+'PROBE iters=1000 warmups=5 samples='+json.dumps([1.]*31),'default',100,'rust_typed','--counter')
 def binary(self,path,words):path.write_bytes(b'SARDIAG1'+struct.pack('<Q',len(words))+struct.pack('<'+'Q'*len(words),*words))
 def test_full_kernel_capture_and_reversal(self):
  with tempfile.TemporaryDirectory()as d:
   p=Path(d)/'x';v=[1,99,0x7ff8000000000000]+[struct.unpack('<Q',struct.pack('<d',1. if i%2 else -1.))[0]for i in range(99)]+[s.CANARY]*8;self.binary(p,v)
   self.assertEqual(s.capture(p,'reversal',100,'c081',{})['facts']['count'],99)
   for offset,value in ((0,2),(1,98),(2,0),(len(v)-1,0)):
    w=v.copy();w[offset]=value;self.binary(p,w)
    with self.assertRaises(AssertionError):s.capture(p,'reversal',100,'c081',{})
 def test_reversal_not_vacuous(self):
  with tempfile.TemporaryDirectory()as d:
   p=Path(d)/'x';self.binary(p,[1,99,0x7ff8000000000000]+[0x3ff0000000000000]*99+[s.CANARY]*8)
   with self.assertRaises(AssertionError):s.capture(p,'reversal',100,'rust_typed',{})
 def test_init_different_lengths_are_explicit(self):
  with tempfile.TemporaryDirectory()as d:
   p=Path(d)/'x'
   for m,length in (('init_nan',100),('init_prefix',1)):
    self.binary(p,[length,100,0x7ff8000000000000]);s.capture(p,'init',100,m,{})
    with self.assertRaises(AssertionError):s.capture(p,'init',100,'init_prefix'if m=='init_nan'else'init_nan',{})
 def test_extra_capture_bytes_rejected(self):
  with tempfile.TemporaryDirectory()as d:
   p=Path(d)/'x';self.binary(p,[1]);p.write_bytes(p.read_bytes()+b'x')
   with self.assertRaises(AssertionError):s.capture(p,'default',0,'setup_c',{})
 def test_pickle_all_eight_and_policy_checked(self):
  with tempfile.TemporaryDirectory()as d:
   p=Path(d)/'x';values=dict(zip(s.KEYS,[0.,0.,.02,.02,.2,.02,.02,.2]));data={'fixtures':{'default/0':{'params':{'params':values,'lookback':1,'recursive':True}}}};w=[struct.unpack('<Q',struct.pack('<d',v))[0]for v in values.values()]+[1,1];self.binary(p,w);s.capture(p,'default',0,'decode_old',data)
   for i in range(10):
    bad=w.copy();bad[i]^=1;self.binary(p,bad)
    with self.assertRaises(AssertionError):s.capture(p,'default',0,'decode_current',data)
 def test_exact_struct_extraction_including_empty(self):
  with tempfile.TemporaryDirectory()as d:
   p=Path(d)/'x';p.write_text('#[derive(Deserialize)]\npub struct NoParams {}\nimpl X {fn never(){}}')
   self.assertEqual(s.extract_struct(p,'NoParams'),'#[derive(Deserialize)]\npub struct NoParams {}\n')
 def test_serde_identity_fail_closed(self):
  with tempfile.TemporaryDirectory()as d:
   t=Path(d);p=t/'release/.fingerprint/talib-ab';p.mkdir(parents=True);deps=t/'release/deps';deps.mkdir();(deps/'libtalib-ab.rlib').write_bytes(b'actual');(p/'lib-talib.json').write_text(json.dumps({'deps':[[0,'serde',0,42]]}))
   self.assertEqual(s.find_rlib(t,'talib',42)[0].name,'libtalib-ab.rlib')
   with self.assertRaises(AssertionError):s.find_rlib(t,'talib',43)
 def test_command_selects_counter_binary(self):
  p={'binary':'primary','counter_binary':'counter','fixtures':{'default/100':{'input':'i','pickle':'p'}}}
  self.assertEqual(s.command(p,'default',100,'rust_typed','out','--counter','g')[0],'counter')
  self.assertEqual(s.command(p,'default',100,'rust_typed','out','--golden','g')[0],'primary')
 def test_workflow_pins_and_gates(self):
  w=(ROOT/'.github/workflows/sarext-profile.yml').read_text();self.assertIn(s.NATIVE,w);self.assertIn(s.ORIGINAL,w);self.assertIn('timeout-minutes: 90',w);self.assertIn('cancel-in-progress: false',w)
  self.assertLess(w.index('--snapshot-native'),w.index('cargo test --release'));self.assertLess(w.index('--snapshot-original'),w.index('cargo test --release'));self.assertLess(w.index('--build\n'),w.index('--run\n'))
 def test_no_product_source_edits_and_no_initializer_unsafe_route(self):
  text=(ROOT/'scripts/sarext_profile_probe.rs').read_text();self.assertNotIn('set_len(',text);self.assertNotIn('get_unchecked',text);self.assertIn('black_box(v.as_slice())',text);self.assertIn('counter binary cannot time',text);self.assertIn('primary binary has no counter wrapper',text)


class IEEEProtocol(unittest.TestCase):
 def log(self,nan=True):
  lines=['C_VERSION 0.8.1 (fixture)'];selected=('0000000000000000',2,(0,63))
  for p,shape,region in s.itertools.product(('0000000000000000','c059400000000000'),range(10),((0,63),(1,63),(7,31),(0,0),(0,1))):
   start,end=region;beg=max(start,1);beg,count=(0,0)if beg>end else(beg,end-beg+1);d=int(nan and (p,shape,region)==selected)
   if d:lines.append(f'IEEE_NAN_DIFF pstart={p} shape={shape} start={start} end={end} index=16 c_bits=7ff8000000000000 rust_bits=fff8000000001234')
   lines.append(f'IEEE_ROW pstart={p} shape={shape} start={start} end={end} beg={beg} count={count} nan_bit_differences={d}')
  for p,opt,value in s.itertools.product(('0000000000000000','c059400000000000'),range(8),('7ff8000000000000','7ff0000000000000','fff0000000000000')):
   lines.append(f'OPTION_C_RESULT pstart={p} option={opt} value_bits={value} code=2 beg=0 count=0 core=BadParam raw_bits='+json.dumps([s.CANARY]*72))
  lines.append(f'IEEE_CONTRACTS comparisons=100 full=20 invalid_no_writes=68 nan_bit_differences={int(nan)} policy=nan_positions_other_bits_exact nonfinite_options_observed=48')
  return '\n'.join(lines)+'\n'
 def test_ieee_all_unique_rows_and_dynamic_details(self):
  p=s.parse_ieee(self.log());self.assertEqual(len(p['comparisons']),100);self.assertEqual(len(p['nan_bit_differences']),1);self.assertEqual(len(p['nonfinite_options']),48)
 def test_target_zero_nan_differences_allowed(self):self.assertEqual(s.parse_ieee(self.log(False))['nan_bit_differences'],[])
 def test_ieee_incomplete_duplicate_shifted_range_rejected(self):
  text=self.log();line=next(l for l in text.splitlines()if l.startswith('IEEE_ROW'))
  for bad in (text.replace(line+'\n','',1),text+line+'\n',text.replace('shape=0 start=0 end=63 beg=1','shape=0 start=0 end=63 beg=2',1),text.replace('index=16','index=63'),text.replace('nan_bit_differences=1 policy','nan_bit_differences=2 policy'),text.replace('comparisons=100','comparisons=99')):
   with self.assertRaises(AssertionError):s.parse_ieee(bad)
 def test_ieee_finite_zero_infinity_payloads_rejected(self):
  for bits in ('3ff0000000000000','3ff0000000000001','0000000000000000','8000000000000000','7ff0000000000000','fff0000000000000'):
   with self.subTest(bits=bits):
    with self.assertRaises(AssertionError):s.parse_ieee(self.log().replace('rust_bits=fff8000000001234','rust_bits='+bits))
 def test_duplicate_or_wrong_per_row_detail_rejected(self):
  text=self.log();line=next(l for l in text.splitlines()if l.startswith('IEEE_NAN_DIFF'))
  for bad in (text+line+'\n',text.replace('shape=2 start=0 end=63 index=16','shape=1 start=0 end=63 index=16'),text.replace('nan_bit_differences=1\n','nan_bit_differences=0\n')):
   with self.assertRaises(AssertionError):s.parse_ieee(bad)
 def test_unexpected_option_c_success_fails_before_timing(self):
  text=self.log();line=next(l for l in text.splitlines()if l.startswith('OPTION_C_RESULT'));new=line.replace('code=2 beg=0 count=0','code=0 beg=1 count=63');new=new[:new.index('raw_bits=')+9]+json.dumps([0]*63+[s.CANARY]*9)
  with self.assertRaises(AssertionError):s.parse_ieee(text.replace(line,new))
 def test_option_inventory_duplicates_and_canary_payload_rejected(self):
  text=self.log();line=next(l for l in text.splitlines()if l.startswith('OPTION_C_RESULT'))
  for bad in (text+line+'\n',text.replace(line+'\n','',1),text.replace(str(s.CANARY),str(0x7ff8000000000000),1)):
   with self.assertRaises(AssertionError):s.parse_ieee(bad)


class RuntimeBinding(unittest.TestCase):
 def library(self,target,name,tag,fp,deps):
  p=target/'release/.fingerprint'/(name+'-'+tag);p.mkdir(parents=True);r=target/'release/deps';r.mkdir(parents=True,exist_ok=True)
  meta=p/('lib-'+name+'.json');meta.write_text(json.dumps({'deps':[[0,k,0,v]for k,v in deps.items()]}));meta.with_suffix('').write_text(fp.to_bytes(8,'little').hex());(r/('lib'+name+'-'+tag+'.rlib')).write_bytes(tag.encode());return meta
 def test_actual_transitive_pickle_binding_and_wrong_serde(self):
  with tempfile.TemporaryDirectory()as d:
   t=Path(d);parent=t/'parent.json';parent.write_text(json.dumps({'deps':[[0,'serde',0,42],[0,'pyo3_polars',0,123]]}));parent.with_suffix('').write_text('0100000000000000')
   self.library(t,'pyo3_polars','aa',123,{'serde':42,'serde_pickle':456});pick=self.library(t,'serde_pickle','bb',456,{'serde':42})
   self.assertEqual(s.pickle_runtime(t,parent)['fingerprint'],456)
   pick.write_text(json.dumps({'deps':[[0,'serde',0,43]]}))
   with self.assertRaises(AssertionError):s.pickle_runtime(t,parent)
 def test_direct_fingerprint_rejects_ambiguity_and_malformed_marker(self):
  with tempfile.TemporaryDirectory()as d:
   t=Path(d);p=self.library(t,'talib','aa',123,{'serde':42});self.assertEqual(s.by_fingerprint(t,'talib',123)[0].name,'libtalib-aa.rlib');self.library(t,'talib','bb',123,{'serde':42})
   with self.assertRaises(AssertionError):s.by_fingerprint(t,'talib',123)
   p.with_suffix('').write_text('7b')
   with self.assertRaises(AssertionError):s.by_fingerprint(t,'talib',123)



class TimeoutEvidence(unittest.TestCase):
 def test_timeout_preserves_partial_stdout_stderr_before_raising(self):
  from unittest.mock import patch
  for stdout,stderr in ((b'partial stdout\xff',b'partial stderr'),('text stdout','text stderr'),(None,None)):
   with tempfile.TemporaryDirectory()as d:
    stem=Path(d)/'child';error=s.subprocess.TimeoutExpired(['probe','selected'],1,output=stdout,stderr=stderr)
    with patch.object(s.subprocess,'run',side_effect=error):
     with self.assertRaises(s.subprocess.TimeoutExpired):s.execute(['probe','selected'],stem,{},timeout=1)
    def decoded(value):return value.decode(errors='replace')if isinstance(value,bytes)else(value or '')
    self.assertEqual(Path(str(stem)+'.stdout').read_text(),decoded(stdout));self.assertEqual(Path(str(stem)+'.stderr').read_text(),decoded(stderr));self.assertTrue(json.loads(Path(str(stem)+'-failure.json').read_text())['timed_out'])
 def test_other_option_status_or_shape_fails(self):
  text=IEEEProtocol().log()
  for bad in (text.replace('code=2 beg=0 count=0','code=3 beg=0 count=0',1),text.replace('code=2 beg=0 count=0','code=2 beg=1 count=0',1),text.replace('code=2 beg=0 count=0','code=2 beg=0 count=1',1)):
   with self.assertRaises(AssertionError):s.parse_ieee(bad)

if __name__=='__main__':unittest.main()
