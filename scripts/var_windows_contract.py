"""Untimed independent VAR/STDDEV public captures and released-C reference."""
from pathlib import Path
import ctypes as c,hashlib,json,math,struct
import numpy as np
ROOT=Path(__file__).parent
POISON=0x7ff80000000055aa

def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb')as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def prices(n,shape):
 i=np.arange(n);wave=64.+((i%37)-18)*.125
 if shape==0:x=wave
 elif shape==1:x=wave.copy();x[n//3]=1e9
 elif shape==2:x=np.where((i//41)%2==0,3.3,wave)
 elif shape==3:x=1e12+((i%37)-18)*.125
 elif shape==4:x=np.full(n,42.)
 elif shape==5:x=np.zeros(n)
 elif shape==6:x=np.full(n,-0.)
 elif shape==7:x=np.where(i%3==0,-0.,0.)
 elif shape==8:x=((i%7)+1).astype('<u8').view('<f8')
 elif shape in(9,10,11):
  x=wave.copy();x[n//3]=[np.array([0x7ff8000000001234],'<u8').view('<f8')[0],np.inf,-np.inf][shape-9]
 elif shape==12:x=np.where(i%2==0,1e200,-1e200)
 else:raise ValueError(shape)
 return x.astype('<f8')
def records(folder):
 lines=(folder/'index.tsv').read_text().splitlines();rows=[];offset=0
 for i,line in enumerate(lines):
  f=line.split('\t');assert len(f)==14
  row=list(map(int,f[:9]))+[int(f[9],16)]+list(map(int,f[10:]));assert row[0]==i and row[13]==offset
  offset+=row[6];rows.append(row)
 assert (folder/'outputs.bin').stat().st_size==offset*8
 return rows,np.memmap(folder/'outputs.bin',dtype='<u8',mode='r'),offset

class RawCWriter:
 """Lossless untimed C buffers plus native/C metadata; never infer from a summary."""
 fields=('native_id','input_rows','input_shape','period','start','end','capacity',
         'function','native_api','devbits_u64_decimal','native_code','native_beg',
         'native_count','native_word_offset','C_code','C_beg','C_count','C_word_offset')
 def __init__(self,directory):
  self.directory=Path(directory);self.directory.mkdir()
  self.index=self.directory.joinpath('index.tsv').open('x')
  self.words=self.directory.joinpath('outputs.bin').open('xb')
  self.rows=0;self.offset=0;self.closed=False
 def append(self,native_row,code,beg,count,out):
  assert not self.closed and len(native_row)==14
  assert all(type(v)is int for v in native_row) and all(type(v)is int for v in (code,beg,count))
  assert out.ndim==1 and out.dtype==np.dtype('<u8') and out.flags.c_contiguous
  assert len(out)==native_row[6]
  metadata=[*native_row,code,beg,count,self.offset]
  self.words.write(out.tobytes(order='C'))
  self.index.write('\t'.join(map(str,metadata))+'\n')
  self.offset+=len(out);self.rows+=1
 def finish(self):
  assert not self.closed
  self.words.close();self.index.close();self.closed=True
  words=self.directory/'outputs.bin';index=self.directory/'index.tsv'
  assert words.stat().st_size==self.offset*8
  return {'directory':str(self.directory),'fields':self.fields,'rows':self.rows,
          'buffer_words':self.offset,'index_sha256':sha(index),'outputs_sha256':sha(words),
          'word_format':'little-endian uint64 raw IEEE754 bits, full physical capacity including untouched canaries',
          'scope':'All C array calls admitted by independent lookback/input/capacity/range proof; metadata recorded before numerical assertions. Rejected native calls are not sent to C.'}

def checked_C_call(lib,name,data,period,dev,start,end,cap,beg,count):
 # Lookback has no array arguments. Its independent result must prove C pointer
 # capacity BEFORE allocating/calling outputs; tested native metadata is not proof.
 assert type(cap)is int and cap>=0 and type(start)is int and type(end)is int
 assert 0<=start<=end<len(data),('C input coverage',start,end,len(data))
 lookback=getattr(lib,name+'_Lookback')(period,dev)
 assert type(lookback)is int and lookback>=0,('C invalid lookback',lookback,period,dev)
 first=max(start,lookback);required=max(0,end-first+1)
 expected=(first,required)if required else(0,0)
 assert cap>=required,('C independent output capacity',cap,required)
 assert (beg,count)==expected,('native vs independent C range',(beg,count),expected)
 out=np.full(cap,POISON,dtype='<u8');begin=c.c_int(-777);number=c.c_int(-777)
 D=c.POINTER(c.c_double)
 ret=getattr(lib,name)(start,end,data.ctypes.data_as(D),period,dev,c.byref(begin),c.byref(number),out.view('<f8').ctypes.data_as(D))
 return ret,begin.value,number.value,out

def compare(base,new,libpath,destination):
 base=Path(base);new=Path(new);libpath=Path(libpath);destination=Path(destination)
 a,aw,words=records(base);b,bw,_=records(new);assert a==b
 assert len(a)==43324 and words==3608928
 mask_a=np.isnan(aw.view('<f8'));mask_b=np.isnan(bw.view('<f8'));assert np.array_equal(mask_a,mask_b)
 changed=aw!=bw;finite_changed=int((changed&~mask_a).sum());nan_changed=int((changed&mask_a).sum())
 assert finite_changed==0,('native nonNaN rawword changes',finite_changed)
 lib=c.CDLL(str(libpath));assert lib.TA_Initialize()==0
 D=c.POINTER(c.c_double);I=c.POINTER(c.c_int)
 for name in('TA_VAR','TA_STDDEV'):
  function=getattr(lib,name);function.argtypes=[c.c_int,c.c_int,D,c.c_int,c.c_double,I,I,D];function.restype=c.c_int
  lookback=getattr(lib,name+'_Lookback');lookback.argtypes=[c.c_int,c.c_double];lookback.restype=c.c_int
 raw_C=RawCWriter(destination.parent/'C083-public-raw')
 checked=elements=nan_deltas=0;failures=[];inputs={};tails=0
 for row in b:
  id,n,shape,period,start,end,cap,function,api,devbits,code,beg,count,offset=row
  actual=bw[offset:offset+cap];reference=aw[offset:offset+cap]
  if code:
   assert np.all(actual==POISON) and np.all(reference==POISON),('rejected output mutation',id)
   continue
  assert cap>0 and n>0 and 0<=start<=end<n and cap>=count
  assert np.all(actual[count:]==POISON) and np.all(reference[count:]==POISON),('native tail',id)
  key=(n,shape)
  if key not in inputs:inputs[key]=prices(n,shape)
  data=inputs[key]
  dev=struct.unpack('<d',struct.pack('<Q',devbits))[0]
  ret,Cbeg,Ccount,out=checked_C_call(lib,'TA_VAR'if function==0 else'TA_STDDEV',data,period,dev,start,end,cap,beg,count)
  raw_C.append(row,ret,Cbeg,Ccount,out)
  assert ret==code and(Cbeg,Ccount)==(beg,count),('C status/range',id,ret,Cbeg,Ccount)
  am=np.isnan(actual[:count].view('<f8'));cm=np.isnan(out[:count].view('<f8'));assert np.array_equal(am,cm),('C NaN positions',id)
  delta=actual[:count]!=out[:count];bad=np.flatnonzero(delta&~am)
  if len(bad):failures.append({'id':id,'words':len(bad),'first':int(bad[0]),'native':int(actual[bad[0]]),'C083':int(out[bad[0]])})
  nan_deltas+=int((delta&am).sum());assert np.array_equal(actual[count:],out[count:]),('C raw canary tail',id)
  checked+=1;elements+=count;tails+=cap-count
 lib.TA_Shutdown()
 live_C_raw=raw_C.finish()
 assert (checked,elements,tails)==(10894,2282098,79460),('C successful inventory',checked,elements,tails)
 assert live_C_raw['rows']==checked and live_C_raw['buffer_words']==elements+tails
 result={'live_C_raw':live_C_raw,'PASS':not failures,'native_calls':len(a),'native_output_buffer_words':words,'native_finite_signedzero_Inf_word_differences':finite_changed,'native_NaN_positions_exact':True,'native_NaN_word_differences_diagnostic':nan_changed,'C083_successful_public_calls':checked,'C083_written_values':elements,'physical_canary_words':tails,'C083_NaN_word_differences_diagnostic':nan_deltas,'C083_finite_signedzero_Inf_failures':failures,'C083_library_sha256':sha(libpath),'baseline_index_sha256':sha(base/'index.tsv'),'baseline_outputs_sha256':sha(base/'outputs.bin'),'candidate_index_sha256':sha(new/'index.tsv'),'candidate_outputs_sha256':sha(new/'outputs.bin'),'policy':'Native ranges/errors/metadata and NaN positions exact; finite/±0/Inf words exact; writtenNaN representation diagnostic only. Rejected/tailpoison words rawexact. C comparison onlysuccessfulRust calls withprovedrawCbufferbounds; all errors/shortbuffers checked versuscurrentdevnative. Untimed.'}
 destination.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2));assert result['PASS'];return result

if __name__=='__main__':
 import argparse
 p=argparse.ArgumentParser();p.add_argument('--baseline',required=True,type=Path);p.add_argument('--candidate',required=True,type=Path);p.add_argument('--C083-library',required=True,type=Path);p.add_argument('--output',required=True,type=Path)
 a=p.parse_args();compare(a.baseline,a.candidate,a.C083_library,a.output)
