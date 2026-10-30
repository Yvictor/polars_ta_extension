"""Independent retained IPC, selected-period routing and finite SMA/control oracle."""
import hashlib,re
from pathlib import Path
import numpy as np
import polars as pl

def need(ok,msg):
 if not ok:raise ValueError(msg)
def sha(path):
 h=hashlib.sha256()
 with path.open('rb')as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()
SCHEMA=pl.Schema({'close':pl.Float64,'open':pl.Float64,'high':pl.Float64,'low':pl.Float64,'volume':pl.Float64,'periods':pl.Float64,'symbol':pl.Int64})
def shape(name):
 family,layout=name.split('/');inter=layout.endswith('_interleaved');parts=layout.removesuffix('_interleaved').split('x');grouped=family.startswith('grouped_')or family=='control_cumsum'
 if grouped:g,b=map(int,parts);n=g*b
 else:n=int(parts[0]);g,b=1,1000
 pattern='control'if family.startswith('control_cumsum')else family.removeprefix('grouped_').removeprefix('mavp_')
 return family.removeprefix('grouped_'),n,g,b,inter,grouped,pattern

def digest(data):
 h=hashlib.sha256(str(data.schema).encode())
 for col in data:
  need(col.null_count()==0,'physical input null');h.update(col.name.encode());h.update(col.to_numpy().tobytes())
 return h.hexdigest()

def periods(pattern,n,b,grouped):
 x=np.arange(n)%b if grouped else np.arange(n)
 if pattern in('four','ema','wma','control'):return np.resize(np.array([3.,5.,9.,14.]),n)
 if pattern=='one':return np.full(n,14.)
 if pattern=='period1':return np.ones(n)
 if pattern=='fractional':return np.array([14.01,14.25,14.999])[x%3]
 if pattern in('early','last'):
  values=np.full(n,14.);values[x==(30 if pattern=='early'else(b if grouped else n)-1)]=15.;return values
 if pattern=='few':return np.array([3.,14.])[x%2]
 if pattern=='many':return (2.+x%29).astype(np.float64)
 if pattern=='blocked':return np.array([3.,5.,9.,14.])[np.minimum(x*4//(b if grouped else n),3)]
 if pattern=='clamped':return np.array([-0.,.75,1.,3.75,9.,31.,100.])[x%7]
 raise ValueError('unreviewed pattern')

def route(name,columns):
 family,n,g,b,inter,grouped,pattern=shape(name);price=columns['close'];raw=columns['periods'];symbol=columns['symbol'];route='pure_polars'if pattern=='control'else'native_mavp_non_sma'if pattern in('ema','wma')else'core_ma_one_period'if pattern in('one','period1','fractional')else'selected_sma_iterator';need(np.isfinite(price).all()and np.isfinite(raw).all()and np.abs(price).max()<=1024 and np.abs(raw).max()<=1024,'compatibility guard eligibility')
 if route=='pure_polars':return {'fixture':'legacy seed260126','native56_route':route,'rows':n,'lookback':0},None
 order=np.argsort(symbol,kind='stable')if grouped else np.arange(n);bars=b if grouped else n;groups=g if grouped else 1;minimum=1 if pattern in('clamped','period1')else 2
 raw=raw[order].reshape(groups,bars);selected=np.trunc(np.clip(raw,minimum,30)).astype(np.int32);written=selected[:,29:];widths=np.zeros(groups,dtype=np.int64)
 for period in range(1,31):widths+=np.any(written==period,axis=1)
 distinct={'four':4,'one':1,'period1':1,'few':2,'many':29,'blocked':4,'clamped':4,'ema':4,'wma':4,'early':2,'last':2,'fractional':1}[pattern];need(np.all(widths==distinct),'every chronological group must contain selected periods')
 split=None
 if pattern in('early','last'):
  expected_split=1 if pattern=='early'else bars-30
  difference=written!=written[:,0,None]
  need(np.all(np.any(difference,axis=1))and np.all(np.argmax(difference,axis=1)==expected_split)and np.all(written[:,0]==14)and np.all(written[np.arange(groups),expected_split]==15),'exact normalized first-difference split in every group')
  split=expected_split
 if pattern=='fractional':
  wanted=np.array([14.01,14.25,14.999]);need(all(np.array_equal(np.unique(row).view(np.uint64),wanted.view(np.uint64))for row in raw[:,29:])and np.all(written==14),'three exact raw fractional levels and uniform normalized14')
 cov={'fixture':'legacy seed260126 with fixed period pattern','native56_route':route,'pattern':pattern,'groups':groups,'bars':bars,'lookback':29,'first_valid_row':0,'written_values':groups*(bars-29),'minperiod':minimum,'maxperiod':30,'matype':{'ema':1,'wma':2}.get(pattern,0),'distinct_periods_min':int(widths.min()),'distinct_periods_max':int(widths.max()),'normalized_min':int(written.min()),'normalized_max':int(written.max()),'normalized_sha256':hashlib.sha256(written.tobytes()).hexdigest(),'price_abs_max':float(np.abs(price).max()),'period_abs_max':float(np.abs(columns['periods']).max()),'all_inputs_finite':True,'guard_forced_long_period':False}
 if split is not None:cov['normalized_first_difference']=split
 if pattern=='fractional':cov['raw_period_values']=[14.01,14.25,14.999]
 return cov,(price[order].reshape(groups,bars),selected,order)

def oracle(name,columns,eligibility):
 family,n,g,b,inter,grouped,pattern=shape(name);price=columns['close'];symbol=columns['symbol']
 if pattern in('ema','wma'):return None
 if pattern=='control':
  if not grouped:return np.cumsum(price,dtype=np.float64)
  order=np.argsort(symbol,kind='stable');out=np.empty(n);out[order]=np.cumsum(price[order].reshape(g,b),axis=1,dtype=np.float64).ravel();return out
 prices,selected,order=eligibility;expected=np.full(prices.shape,np.nan)
 # Independent finite mathematical SMA: direct bounded windows, not the adapter's rolling recurrence.
 for period in np.unique(selected[:,29:]):
  k=int(period);means=np.lib.stride_tricks.sliding_window_view(prices,k,axis=1).sum(axis=-1,dtype=np.float64)/k;mask=selected[:,k-1:]==k;mask[:,:max(0,29-(k-1))]=False;target=expected[:,k-1:];target[mask]=means[mask]
 out=np.empty(n);out[order]=expected.ravel();return out

def audit_inputs(folder,records,names,expected_unique=24):
 folder=Path(folder);need(set(records)==set(names),'all32 physical input mappings');parsed={};layouts={};markets={};proof={};expected={};coverage={};fixture={}
 for name in names:
  family,n,g,b,inter,grouped,pattern=shape(name);key=(n,b,inter,grouped,'four'if pattern in('ema','wma','control')else pattern);record=records[name];need(set(record)=={'file','sha256','bytes','fixture_sha256','schema','rows'},'input record fields');token=record['fixture_sha256'];filename=record['file'];need(re.fullmatch('[0-9a-f]{64}',token)is not None and filename==token+'.arrow','safe physical input filename');path=folder/filename;need(not path.is_symlink()and path.is_file()and path.resolve().is_relative_to(folder.resolve()),'physical input path');need(type(record['bytes'])is int and path.stat().st_size==record['bytes']and sha(path)==record['sha256'],'physical IPC size/hash')
  if key in layouts:need(layouts[key]==filename and parsed[filename]['record']==record,'same physical layout identity')
  else:
   need(filename not in parsed,'unrelated physical patterns share IPC');layouts[key]=filename;data=pl.read_ipc(path,memory_map=False);need(data.schema==SCHEMA and str(data.schema)==record['schema']==str(SCHEMA)and data.height==record['rows']==n and digest(data)==token,'physical IPC dtype/schema/values');cols={c.name:c.to_numpy()for c in data};need(all(np.isfinite(x).all()for x in cols.values()),'finite physical inputs');permutation=np.arange(n).reshape(g,b).T.ravel()if inter else np.arange(n);want_symbol=np.tile(np.arange(g,dtype=np.int64),b)if inter else np.arange(n,dtype=np.int64)//b;need(np.array_equal(cols['symbol'],want_symbol),'physical chronological group order');raw=periods(pattern,n,b,grouped)[permutation];need(np.array_equal(cols['periods'].view(np.uint64),raw.view(np.uint64)),'raw period bits/pattern/reset/clamping')
   need(np.array_equal(cols['open'].view(np.uint64),(cols['close']-.1).view(np.uint64))and np.array_equal(cols['high'],cols['close']+1.)and np.array_equal(cols['low'],cols['close']-1.),'physical OHLC relations');need(np.all((cols['volume']>=100)&(cols['volume']<=1000)),'physical volume domain');inverse=np.argsort(permutation)
   market={k:cols[k][inverse]for k in('close','open','high','low','volume')}
   rng=np.random.default_rng(260126);seeded_close=100.+np.cumsum(rng.normal(0.,.1,n));seeded_volume=100.+900.*rng.random(n)
   need(np.array_equal(market['close'].view(np.uint64),seeded_close.view(np.uint64))and np.array_equal(market['volume'].view(np.uint64),seeded_volume.view(np.uint64)),'exact historical seeded price/volume bytes')
   if n in markets:
    for k in market:need(np.array_equal(market[k].view(np.uint64),markets[n][k].view(np.uint64)),'same market bytes across period/layout patterns')
   else:markets[n]=market
   parsed[filename]={'record':record,'columns':cols};proof[filename]={'sha256':sha(path),'fixture_sha256':token,'rows':n,'schema':str(SCHEMA)}
  cols=parsed[filename]['columns'];cov,eligibility=route(name,cols);coverage[name]=cov;expected[name]=oracle(name,cols,eligibility);fixture[name]=token
 need(len(parsed)==len(layouts)==expected_unique and{p.name for p in folder.iterdir()}==set(parsed),'exact24 physical snapshots/no orphans')
 sizes=sorted(markets)
 for small,large in zip(sizes,sizes[1:]):need(np.array_equal(markets[small]['close'].view(np.uint64),markets[large]['close'][:small].view(np.uint64)),'same seeded chronological price prefix')
 return expected,coverage,fixture,proof
