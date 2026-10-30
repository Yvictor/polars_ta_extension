import copy,hashlib,importlib.util,json,tempfile,unittest
from pathlib import Path
import numpy as np
import polars as pl
import inputs as physical
HERE=Path(__file__).parent
spec=importlib.util.spec_from_file_location('a',HERE/'audit.py');a=importlib.util.module_from_spec(spec);spec.loader.exec_module(a)
class Inputs(unittest.TestCase):
 def names(self):
  raw=a.js(HERE/'trusted.json')['case_manifest']['cases'];return [n.replace('/1000000','/4000').replace('/100x10000','/2x2000').replace('/10000x100','/40x100').replace('/2000x100_interleaved','/40x100_interleaved')for n in raw]
 def make(self,folder):
  records={};names=self.names()
  for name in names:
   family,n,g,b,inter,grouped,pattern=physical.shape(name);rows=np.arange(n);rng=np.random.default_rng(260126);close=100.+np.cumsum(rng.normal(0.,.1,n));volume=100.+900.*rng.random(n);within=rows%b if grouped else rows
   options={'four':[3.,5.,9.,14.],'ema':[3.,5.,9.,14.],'wma':[3.,5.,9.,14.],'control':[3.,5.,9.,14.],'few':[3.,14.],'fractional':[14.01,14.25,14.999],'clamped':[-0.,.75,1.,3.75,9.,31.,100.]}
   if pattern in options:
    values=options[pattern];periods=np.array([values[int(i)%len(values)]for i in(rows if pattern in('four','ema','wma','control')else within)])
   elif pattern=='one':periods=np.full(n,14.)
   elif pattern in('early','last'):
    periods=np.full(n,14.);periods[within==(30 if pattern=='early'else(b if grouped else n)-1)]=15.
   elif pattern=='period1':periods=np.full(n,1.)
   elif pattern=='many':periods=np.array([float(2+int(i)%29)for i in within])
   else:periods=np.array([[3.,5.,9.,14.][min(int(i)*4//(b if grouped else n),3)]for i in within])
   data=pl.DataFrame({'close':close,'open':close-.1,'high':close+1,'low':close-1,'volume':volume,'periods':periods,'symbol':rows//b})
   if inter:data=data[np.arange(n).reshape(g,b).T.ravel()]
   token=physical.digest(data);path=folder/(token+'.arrow')
   if not path.exists():data.write_ipc(path,compression='zstd')
   records[name]={'file':path.name,'sha256':physical.sha(path),'bytes':path.stat().st_size,'fixture_sha256':token,'schema':str(data.schema),'rows':n}
  return names,records
 def rewrite(self,folder,records,case,change):
  old=records[case]['file'];data=pl.read_ipc(folder/old,memory_map=False);data=change(data);token=physical.digest(data);path=folder/(token+'.arrow');data.write_ipc(path,compression='zstd');record={'file':path.name,'sha256':physical.sha(path),'bytes':path.stat().st_size,'fixture_sha256':token,'schema':str(data.schema),'rows':data.height}
  for name,row in list(records.items()):
   if row['file']==old:records[name]=copy.deepcopy(record)
  (folder/old).unlink()
 def test_all32_physical_mappings_24_ipcs_routes_and_independent_mean(self):
  with tempfile.TemporaryDirectory()as d:
   folder=Path(d);names,records=self.make(folder);expected,cov,hashes,proof=physical.audit_inputs(folder,records,names);self.assertEqual(len(proof),24);self.assertEqual(len(expected),32)
   for name,out in expected.items():
    family,n,g,b,inter,grouped,pattern=physical.shape(name)
    if pattern in('ema','wma'):self.assertIsNone(out);continue
    if pattern=='control':self.assertTrue(np.isfinite(out).all());continue
    data=pl.read_ipc(folder/records[name]['file'],memory_map=False);columns={c.name:c.to_numpy()for c in data};coverage,(prices,selected,order)=physical.route(name,columns);ordered=out[order].reshape(prices.shape);self.assertTrue(np.isnan(ordered[:,:29]).all())
    # Independent scalar bounded-window loop verifies the vectorized oracle.
    want=np.array([[sum(prices[i,j-int(selected[i,j])+1:j+1])/int(selected[i,j])for j in range(29,prices.shape[1])]for i in range(prices.shape[0])]);np.testing.assert_allclose(ordered[:,29:],want,rtol=1e-14,atol=1e-14)
    if pattern=='period1':np.testing.assert_array_equal(ordered[:,29:].view('u8'),prices[:,29:].view('u8'))
 def test_self_consistent_raw_file_corruption_still_rejected(self):
  for kind in('period_zero_sign','one_group','symbol','guard_price','wrong_dtype','seeded_volume','seeded_price'):
   with self.subTest(kind=kind),tempfile.TemporaryDirectory()as d:
    folder=Path(d);names,records=self.make(folder);case='grouped_mavp_clamped/2x2000'if kind=='period_zero_sign'else'grouped_mavp_four/2x2000'
    def change(data):
     if kind=='period_zero_sign':return data.with_columns(pl.when(pl.col('periods')==0.).then(pl.lit(0.)).otherwise(pl.col('periods')).alias('periods'))
     if kind=='one_group':return data.with_columns(pl.when(pl.col('symbol')==0).then(pl.lit(14.)).otherwise(pl.col('periods')).alias('periods'))
     if kind=='symbol':return data.with_columns((pl.col('symbol')+1).alias('symbol'))
     if kind=='guard_price':return data.with_columns((pl.col('close')+2000.).alias('close'))
     if kind=='seeded_volume':return data.with_columns((pl.col('volume')+.001).alias('volume'))
     if kind=='seeded_price':
      return data.with_columns((pl.col('close')+.001).alias('close')).with_columns((pl.col('close')-.1).alias('open'),(pl.col('close')+1.).alias('high'),(pl.col('close')-1.).alias('low'))
     return data.with_columns(pl.col('symbol').cast(pl.Float64))
    self.rewrite(folder,records,case,change)
    with self.assertRaises(ValueError):physical.audit_inputs(folder,records,names)
 def test_input_record_integrity_and_exact_inventory(self):
  for kind in('size','hash','path','missing','extra','symlink'):
   with self.subTest(kind=kind),tempfile.TemporaryDirectory()as d:
    folder=Path(d);names,records=self.make(folder);row=records[names[0]]
    if kind=='size':row['bytes']+=1
    elif kind=='hash':row['sha256']='0'*64
    elif kind=='path':row['file']='../escape.arrow'
    elif kind=='missing':del records[names[-1]]
    elif kind=='extra':(folder/'orphan').write_text('bad')
    else:
     file=folder/row['file'];target=folder/'target';file.rename(target);file.symlink_to(target)
    with self.assertRaises(ValueError):physical.audit_inputs(folder,records,names)
 def test_golden_schema_warmup_masks_values_and_exact_signedzero(self):
  name='mavp_period1/100';expected={name:np.r_[np.full(29,np.nan),np.arange(71,dtype=float)]};v={name+'_schema':np.array("Schema({'mavp_period1': Float64})"),name+'_0':expected[name].copy(),name+'_0_null':np.zeros(100,bool)}
  for change in(None,'padding','value','mask','schema','dtype','zero_sign'):
   with self.subTest(change=change),tempfile.TemporaryDirectory()as d:
    x=copy.deepcopy(v)
    if change=='padding':x[name+'_0'][0]=0.
    elif change=='value':x[name+'_0'][-1]+=1.
    elif change=='mask':x[name+'_0_null'][-1]=True
    elif change=='schema':x[name+'_schema']=np.array('WRONG')
    elif change=='dtype':x[name+'_0']=x[name+'_0'].astype('f4')
    elif change=='zero_sign':x[name+'_0'][29]=-0.
    path=Path(d)/'g.npz';np.savez_compressed(path,**x)
    if change:
     with self.assertRaises(ValueError):a.golden(path,[name],expected)
    else:self.assertEqual(a.golden(path,[name],expected)[1],100)
if __name__=='__main__':unittest.main()
