import copy,importlib.util,json,tempfile,unittest
from pathlib import Path
import numpy as np
HERE=Path(__file__).parent
spec=importlib.util.spec_from_file_location('a',HERE/'audit.py');a=importlib.util.module_from_spec(spec);spec.loader.exec_module(a)

class Boundaries(unittest.TestCase):
 def test_reviewed_candidate_source_boundary(self):
  trust=a.js(HERE/'trusted.json');maps=trust['source_file_sha256'];changed=['src/compat/mavp_sma.rs'];required={'src/native.rs','src/compat.rs','src/compat/guarded.rs','src/generated.rs','src/params.rs','src/missing.rs','src/utils.rs','Cargo.toml','Cargo.lock'}
  expected={'changed_files':changed,'routing_sources':{n:maps['combined'][n]for n in sorted(required)},'helper_before':maps['combined'][changed[0]],'helper_after':maps['candidate'][changed[0]]}
  self.assertEqual(a.source_boundary({'native_source_boundary':expected},trust),expected)
  for kind in('routing','helper','claimed_route','extra_source'):
   with self.subTest(kind=kind):
    t=copy.deepcopy(trust);p={'native_source_boundary':copy.deepcopy(expected)}
    if kind=='routing':t['source_file_sha256']['candidate']['src/native.rs']='changed'
    elif kind=='helper':t['source_file_sha256']['candidate'][changed[0]]='changed'
    elif kind=='extra_source':t['source_file_sha256']['candidate']['src/unreviewed.rs']='changed'
    else:p['native_source_boundary']['routing_sources']['src/native.rs']='changed'
    with self.assertRaises(ValueError):a.source_boundary(p,t)
 def test_three_arm_golden_raw_replay_and_native_signed_zero(self):
  name='mavp_period1/40';key=name+'_0';mask=key+'_null';schema=name+'_schema';base={key:np.r_[np.full(29,np.nan),np.arange(11,dtype=float)],mask:np.zeros(40,bool),schema:np.array("Schema({'mavp_period1': Float64})")}
  for kind in('exact','finite','zero','null','nan_position','infinity_sign','schema'):
   with self.subTest(kind=kind),tempfile.TemporaryDirectory()as d:
    folder=Path(d);other=copy.deepcopy(base)
    if kind=='finite':other[key][-1]+=1e-14
    elif kind=='zero':other[key][29]=-0.
    elif kind=='null':other[mask][-1]=True
    elif kind=='nan_position':other[key][29]=np.nan
    elif kind=='infinity_sign':base0=copy.deepcopy(base);base0[key][-1]=np.inf;other[key][-1]=-np.inf
    elif kind=='schema':other[schema]=np.array('WRONG')
    np.savez(folder/'old.npz',**(base0 if kind=='infinity_sign'else base));np.savez(folder/'new.npz',**other)
    args=(folder/'old.npz',folder/'new.npz',[name])
    if kind=='exact':self.assertEqual(a.compare_goldens(*args,exact=True)['different'],0)
    else:
     with self.assertRaises(ValueError):a.compare_goldens(*args,exact=True)
    if kind=='finite':self.assertEqual(a.compare_goldens(*args,exact=False)['different'],1)
    elif kind=='zero':
     with self.assertRaisesRegex(ValueError,'signed-zero'):a.compare_goldens(*args,exact=False)
 def test_tolerant_c_lane_preserves_both_zero_sign_but_allows_tiny_rounding(self):
  null=np.array([False]);zero=np.array([0.]);minuszero=np.array([-0.])
  for before,after in((zero,minuszero),(minuszero,zero)):
   with self.subTest(before=before,after=after),self.assertRaisesRegex(ValueError,'signed-zero'):
    a.arrays(before,after,null,null,exact=False)
  self.assertEqual(a.arrays(zero,np.array([1e-14]),null,null,exact=False)['different'],1)
  self.assertEqual(a.arrays(np.array([1.]),np.array([1.+1e-14]),null,null,exact=False)['different'],1)
  # Payload bits under nulls are outside the numerical contract.
  self.assertEqual(a.arrays(zero,minuszero,~null,~null,exact=False)['checked'],0)
 def test_linux_uniform_policy_is_globally_unfused_with_no_tolerance(self):
  from decimal import Decimal,localcontext
  unit=np.array([float.fromhex(x)for x in('0x1.a12436119be68p-4','0x1.e64fccd22326ep-2','0x1.d94dd22055248p-3')])
  expected=np.array([float.fromhex(x)for x in('0x1.7f5069c2bd02cp+7','0x1.07b611825872ap+9','0x1.33feb2d7356a8p+8')])
  unfused=100.+900.*unit
  with localcontext()as context:
   context.prec=100
   fused=np.array([float(Decimal(100)+Decimal(900)*Decimal.from_float(float(u)))for u in unit])
  np.testing.assert_array_equal(unfused.view('u8'),expected.view('u8'))
  self.assertTrue(np.all(fused.view('u8')!=unfused.view('u8')))
  mutated=expected+.001
  self.assertTrue(np.all(mutated.view('u8')!=unfused.view('u8'))and np.all(mutated.view('u8')!=fused.view('u8')))
 def test_json_comparison_has_no_tolerance_or_bool_equivalence(self):
  for before,after in((1.+5e-13,1.),(True,1),(True,1.),({'a':1},{'a':True}),([1],(1,))):
   with self.subTest(before=before,after=after),self.assertRaises(ValueError):a.eq(before,after)
 def test_control_oracle_respects_stable_interleaved_group_order(self):
  price=np.array([1.,100.,2.,200.,3.,300.]);symbol=np.array([0,1,0,1,0,1]);out=a.physical.oracle('control_cumsum/2x3_interleaved',{'close':price,'symbol':symbol},None)
  np.testing.assert_array_equal(out,[1.,100.,3.,300.,6.,600.])

if __name__=='__main__':unittest.main()
