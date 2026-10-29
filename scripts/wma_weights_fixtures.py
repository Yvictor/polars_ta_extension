from pathlib import Path
import struct,json,hashlib,math
import sys
p=Path(sys.argv[1]);p.mkdir(parents=True,exist_ok=True)
patterns=['wave','spike','highoffset','positivezero','negativezero','mixedzero','subnormal','nan','infinity','negativeinfinity']
def prices(pattern,n):
 for i in range(n):
  v=64.+((i%37)-18)*.125
  if pattern=='spike' and i==n//3:v=1e9
  elif pattern=='highoffset':v=1e12+((i%37)-18)*.125
  elif pattern=='positivezero':v=0.
  elif pattern=='negativezero':v=-0.
  elif pattern=='mixedzero':v=-0. if i%3==0 else 0.
  elif pattern=='subnormal':v=struct.unpack('<d',struct.pack('<Q',(i%7)+1))[0]
  elif pattern=='nan' and i==n//3:v=struct.unpack('<d',struct.pack('<Q',0x7ff8000000001234))[0]
  elif pattern=='infinity' and i==n//3:v=math.inf
  elif pattern=='negativeinfinity' and i==n//3:v=-math.inf
  yield v
written={};rows=[]
def file(pattern,n):
 name=f'{pattern}-{n}.f64'
 if name not in written:
  data=b''.join(struct.pack('<d',x)for x in prices(pattern,n));(p/name).write_bytes(data);written[name]=hashlib.sha256(data).hexdigest()
 return name
def periods(n):
 name=f'periods-{n}.f64'
 if name not in written:
  data=b''.join(struct.pack('<d',[2.,7.,14.,30.][i%4])for i in range(n));(p/name).write_bytes(data);written[name]=hashlib.sha256(data).hexdigest()
 return name
def add(mode,pattern,n,period,start=0,history=0):
 end=n-1;lb=29 if mode in ('mavp','bank')else max(0,period-1);count=max(0,end-max(start,lb)+1);cap=count+8
 key=f'c{len(rows):05d}'
 rows.append((key,mode,file(pattern,n),periods(n),start,end,period,cap,history))
for period in [1,2,3,7,14,30,50]:
 for n in [1,2,3,16,29,30,31,100,257,1000]:
  for pattern in patterns:
   for mode in ['wma','ma']:add(mode,pattern,n,period)
for period in [2,3,7,14,30,50,200,1000]:
 for pattern in ['wave','spike','highoffset','mixedzero']:
  for mode in ['wma','ma']:
   for start in [0,period-1,period,period+1,8*period-1,8*period,8*period+1]:add(mode,pattern,max(10000,9*period+3),period,start)
for period in [20000,46340,46341,100000]:
 for mode in ['wma','ma']:add(mode,'wave',9*period+3,period)
for pattern in patterns:
 for n in [100,1000,10000]:add('mavp',pattern,n,30)
 for period in [1,2,3,7,14,30,200]:add('stream',pattern,max(1024,9*period+3),period,history=max(period,1))
 add('bank',pattern,1024,30,history=30)
(p/'index.tsv').write_text(''.join('\t'.join(map(str,x))+'\n'for x in rows))
(p/'manifest.json').write_text(json.dumps({'schema_version':1,'source':'deterministic exact dyadic/IEEE inputs; original retained period cycle2,7,14,30','cases':len(rows),'files':written,'counts':{m:sum(x[1]==m for x in rows)for m in ['wma','ma','mavp','stream','bank']},'NaN_payload_policy':'raw diagnostic; numeric comparisons require NaN positions, finite and signed-zero words exact'},indent=2)+'\n')
print('fixturecases',len(rows))
