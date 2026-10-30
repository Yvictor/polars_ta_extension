"""Independent physical SAREXT fixtures and chronological group mapping."""
import hashlib,re
from pathlib import Path
import numpy as np
import polars as pl

def need(ok,msg):
 if not ok:raise ValueError(msg)
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb')as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()
SCHEMA=pl.Schema({'close':pl.Float64,'open':pl.Float64,'high':pl.Float64,'low':pl.Float64,'volume':pl.Float64,'periods':pl.Float64,'symbol':pl.Int64})
def shape(name):
 family,layout=name.split('/');inter=layout.endswith('_interleaved');grouped=family.startswith('grouped_')or family=='control_cumsum';token=layout.removesuffix('_interleaved')
 if grouped:g,b=map(int,token.split('x'));n=g*b
 else:n=int(token);g=1;b=1000
 kind='reversal'if'reversal'in family else'longzero'if'longzero'in family else'market'
 return family.removeprefix('grouped_'),n,g,b,inter,grouped,kind

def regenerate(name):
 family,n,g,b,inter,grouped,kind=shape(name)
 if kind=='market':
  rng=np.random.default_rng(260126);close=100+np.cumsum(rng.normal(0,.1,n));high=close+1;low=close-1;volume=100.+900.*rng.random(n)
 else:
  x=np.arange(n)%b if grouped else np.arange(n)
  if kind=='reversal':close=np.array([100.,110.,90.,115.,85.,120.,80.,100.])[x%8];high=close+1;low=close-1
  else:high=x.astype(float)+2;low=x.astype(float);low[x==0]=-0.;close=(high+low)/2
  volume=np.full(n,500.)
 cols={'close':close,'open':close-.1,'high':high,'low':low,'volume':volume,'periods':np.resize([3.,5.,9.,14.],n),'symbol':np.arange(n)//b}
 order=np.arange(n).reshape(g,b).T.ravel()if inter else np.arange(n)
 return {k:v[order]for k,v in cols.items()}

def digest(cols):
 h=hashlib.sha256(str(SCHEMA).encode())
 for name in SCHEMA:h.update(name.encode());h.update(cols[name].tobytes())
 return h.hexdigest()

def control(name,cols):
 family,n,g,b,inter,grouped,kind=shape(name)
 if not family.startswith('control'):return None
 if not grouped:return np.cumsum(cols['close'])
 order=np.argsort(cols['symbol'],kind='stable');out=np.empty(n);out[order]=np.cumsum(cols['close'][order].reshape(g,b),axis=1).ravel();return out

def coverage(name,arr):
 family,n,g,b,inter,grouped,kind=shape(name)
 need(arr.dtype==np.dtype('float64')and arr.shape==(n,),'golden scalar array')
 if family.startswith('control'):return {'fixture':'pure Polars cumsum','rows':n}
 if family=='sar':return {'fixture':'generic SAR shared preparation control','rows':n}
 order=np.arange(n).reshape(b,g).T.ravel()if inter else np.arange(n);bars=b if grouped else n;groups=g if grouped else 1;ordered=arr[order].reshape(groups,bars)
 need(np.isnan(ordered[:,:1]).all()and np.isfinite(ordered[:,1:]).all(),'SAREXT group warmup/range')
 negzero=ordered.view(np.uint64)==0x8000000000000000;zeros=negzero.sum(axis=1);pos=(ordered>0).sum(axis=1);neg=(ordered<0).sum(axis=1)
 if kind=='longzero':need(np.all(zeros>0),'every longzero group must retain legitimate negative zero')
 else:need(not zeros.any(),'ordinary no-negative-zero fixture')
 if kind=='reversal':need(np.all(pos>0)and np.all(neg>0),'every chronological group exercises both directions')
 return {'fixture':'legitimate long-zero stress'if kind=='longzero'else'ordinary no-written-negative-zero','groups':groups,'written':groups*(bars-1),'negative_zero_count':int(zeros.sum()),'minimum_negative_zeros_per_group':int(zeros.min()),'maximum_negative_zeros_per_group':int(zeros.max()),'minimum_positive_per_group':int(pos.min()),'minimum_negative_per_group':int(neg.min()),'replay_scope':'negative-zero trigger inferred from public words/source, not an instrumented branch count'}

def audit_inputs(folder,records,names,expected_unique=10):
 folder=Path(folder);need(set(records)==set(names),'physical input inventory');seen={};fixture={};oracles={}
 for name in names:
  record=records[name];need(set(record)=={'file','sha256','bytes','fixture_sha256','schema','rows'},'physical record keys');token=record['fixture_sha256'];need(re.fullmatch('[0-9a-f]{64}',token)is not None and record['file']==token+'.arrow','safe IPC path');path=folder/record['file'];need(path.is_file()and not path.is_symlink()and path.resolve().is_relative_to(folder.resolve()),'physical IPC file');need(type(record['bytes'])is int and path.stat().st_size==record['bytes']and sha(path)==record['sha256'],'physical IPC transport');want=regenerate(name);need(digest(want)==token,'independently regenerated fixture hash')
  if token not in seen:
   data=pl.read_ipc(path,memory_map=False);need(data.schema==SCHEMA and str(data.schema)==record['schema']and data.height==record['rows']==len(want['close']),'IPC schema/rows');need(not any(c.null_count()for c in data),'IPC no nulls')
   cols={c.name:c.to_numpy()for c in data}
   for col in SCHEMA:need(np.array_equal(cols[col].view(np.uint64),want[col].view(np.uint64)),'regenerated exact physical bytes '+col)
   seen[token]={'record':record,'rows':data.height,'sha256':sha(path)}
  else:need(seen[token]['record']==record,'shared IPC record consistency')
  fixture[name]=token;oracles[name]=control(name,want)
 need(len(seen)==expected_unique and {p.name for p in folder.iterdir()}=={k+'.arrow'for k in seen},'exact ten physical IPC files/no orphans')
 return oracles,fixture,seen
