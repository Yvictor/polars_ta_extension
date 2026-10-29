"""Source-bound SAREXT stage diagnostic; never additive costs or product throughput."""
import argparse,platform,sys,hashlib,itertools,json,math,os,re,resource,shutil,statistics,struct,subprocess,time,collections
from pathlib import Path
from integer_init_provenance import sha256,source_record,identity,wheel_record,flags_record
from integer_init_stage_benchmark import native_dependency_records,mapper

HERE=Path(__file__).resolve().parent
NATIVE='56f6d5fb139031c20d86d7e818e7d267eb834295'
ORIGINAL='b2bbc26d41ec80823c8bffb0cc436a97f29911cc'
C_SHA='ec59ccd88c0c77f618587d858787c8f9d06c40460a09d66751926f6fd670f985'
KEYS=('startvalue','offsetonreverse','accelerationinitlong','accelerationlong','accelerationmaxlong','accelerationinitshort','accelerationshort','accelerationmaxshort')
LENGTHS=(100,1000,10000,1000000)
KERNEL=('c081','rust_typed','rust_generic','native_full')
ORDERS4=((0,1,3,2),(1,2,0,3),(2,3,1,0),(3,0,2,1))*3
ORDERS2=((0,1),(1,0))*6
GROUPS=tuple((f,n,KERNEL) for f in ('default','reversal') for n in LENGTHS)+tuple((f,0,('decode_old','decode_current')) for f in ('default','reversal','add'))+tuple((f,0,('setup_c','setup_current')) for f in ('default','reversal'))+tuple(('init',n,('init_nan','init_prefix')) for n in LENGTHS)
CELLS=tuple((f,n,m) for f,n,ms in GROUPS for m in ms)
ITERS={0:10000,100:1000,1000:100,10000:10,1000000:1}
CANARY=0x7ff80000000055aa
SCRIPTS=('sarext_profile_benchmark.py','sarext_profile_probe.rs','integer_init_provenance.py','integer_init_stage_benchmark.py','integer_init_benchmark.py','integer_init_cases.json','migration_ci_benchmark.py','SAREXT_DIAGNOSTIC.md')
VALID=re.compile(r'^VALIDATE fixture=(\w+) mode=(\w+) n=(\d+) golden_verified=(true|false) physical_tail=(true|false)$',re.M)
PROBE=re.compile(r'^PROBE iters=(\d+) warmups=5 samples=(\[[^\n]+\])$',re.M)
COUNTER=re.compile(r'^COUNTER counts=(\[[^\n]+\])$',re.M)
assert len(CELLS)==50 and len(set(CELLS))==50

def invoke(command,path,env=None):
    path=Path(path);path.with_suffix('.command.json').write_text(json.dumps(list(map(str,command)),indent=2)+'\n')
    with path.open('w') as log:subprocess.run(list(map(str,command)),env=env,stdout=log,stderr=subprocess.STDOUT,check=True)


def runtime_record():
    assert sys.platform=='linux' and platform.machine()=='x86_64'
    model=next(line.split(':',1)[1].strip() for line in Path('/proc/cpuinfo').read_text().splitlines() if line.startswith('model name'))
    assert all(os.environ.get(k,'')=='' for k in ('CFLAGS','CXXFLAGS'))
    return {'platform':platform.platform(),'machine':platform.machine(),'python':sys.version,'cpu':model,
            'CFLAGS':os.environ.get('CFLAGS',''),'CXXFLAGS':os.environ.get('CXXFLAGS','')}


def by_fingerprint(target,name,fingerprint):
    matches=[]
    for p in (target/'release/.fingerprint').glob('*/lib-'+name+'.json'):
        raw=p.with_suffix('');encoded=raw.read_text().strip();assert re.fullmatch('[0-9a-f]{16}',encoded);value=int.from_bytes(bytes.fromhex(encoded),'little')
        if value==fingerprint:
            lib=target/'release/deps'/('lib'+name+'-'+p.parent.name.rsplit('-',1)[1]+'.rlib');assert lib.exists();matches.append((lib,p))
    assert len(matches)==1,(name,'ambiguous or absent product dependency',matches)
    return matches[0]


def pickle_runtime(target,parent):
    deps={v[1]:v[3]for v in json.loads(parent.read_text())['deps']}
    polars,meta=by_fingerprint(target,'pyo3_polars',deps['pyo3_polars'])
    transitive={v[1]:v[3]for v in json.loads(meta.read_text())['deps']}
    lib,pickle_meta=by_fingerprint(target,'serde_pickle',transitive['serde_pickle'])
    assert {v[1]:v[3]for v in json.loads(pickle_meta.read_text())['deps']}['serde']==deps['serde']==transitive['serde']
    files={str(f):sha256(f) for f in (parent,parent.with_suffix(''),polars,meta,meta.with_suffix(''),lib,pickle_meta,pickle_meta.with_suffix(''))}
    return {'path':str(lib),'sha256':sha256(lib),'metadata':str(pickle_meta),'fingerprint':transitive['serde_pickle'],'serde_fingerprint':deps['serde'],'files':files}


def snapshot(args):
    folder=args.output/'linkage';folder.mkdir(parents=True,exist_ok=True)
    deps,evidence=native_dependency_records(args.target_dir,inventory_path=folder/'unfiltered-inventory.json')
    parents=[Path(p) for p in evidence if Path(p).name=='lib-_polars_talib.json'];assert len(parents)==1
    runtime_pickle=pickle_runtime(args.target_dir,parents[0]);evidence.update(runtime_pickle['files'])
    files={}
    for path,digest in evidence.items():
        source=Path(path);dest=folder/'fingerprints'/source.parent.name/source.name
        dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,dest);assert sha256(dest)==digest;files[str(dest)]=digest
    installed=identity(args.native_python);retained={}
    for source in [*deps.values(),*map(Path,installed['native_files'])]:
        dest=folder/'product-artifacts'/source.name;dest.parent.mkdir(exist_ok=True);shutil.copyfile(source,dest)
        retained[str(dest)]=sha256(source);assert sha256(dest)==retained[str(dest)]
    record={'runtime_pickle':runtime_pickle,'source':source_record(args.native_source,NATIVE),'identity':installed,'wheel':wheel_record(args.wheel_dir/'native',installed),
            'flags':flags_record(),'dependencies':{name:{'path':str(path),'sha256':sha256(path)} for name,path in deps.items()},
            'fingerprints':files,'retained':retained,'inventory_sha256':sha256(folder/'unfiltered-inventory.json')}
    (folder/'snapshot.json').write_text(json.dumps(record,indent=2)+'\n')


def find_rlib(target,name,serde_fingerprint):
    root=target/'release/.fingerprint';matches=[]
    for p in root.glob('*/lib-'+name+'.json'):
        meta=json.loads(p.read_text());deps={v[1]:v[3] for v in meta['deps']}
        if deps.get('serde')!=serde_fingerprint:continue
        r=target/'release/deps'/('lib'+name+'-'+p.parent.name.rsplit('-',1)[1]+'.rlib')
        if r.exists():matches.append((r,p,meta))
    assert len(matches)==1,(name,'must match actual product Serde crate identity',matches)
    return matches[0]


def serde_identity(args):
    r=json.loads((args.output/'linkage/snapshot.json').read_text())['dependencies']['serde']
    lib=Path(r['path']);p=args.target_dir/'release/.fingerprint'/('serde-'+lib.stem.split('-')[-1])/'lib-serde'
    assert sha256(lib)==r['sha256'];raw=p.read_text().strip();assert re.fullmatch('[0-9a-f]{16}',raw)
    return int.from_bytes(bytes.fromhex(raw),'little'),p


def snapshot_original(args):
    original=source_record(args.original_source,ORIGINAL);ident=identity(args.original_python)
    assert ident['talib'].startswith('0.8.1 ')
    fp,serde_file=serde_identity(args)
    parents=[p for p in (args.target_dir/'release/.fingerprint').glob('*/lib-_polars_talib.json') if 'talib' in {v[1]for v in json.loads(p.read_text())['deps']}];assert len(parents)==1
    direct={v[1]:v[3]for v in json.loads(parents[0].read_text())['deps']}
    lib,meta=by_fingerprint(args.target_dir,'talib',direct['talib']);contents=json.loads(meta.read_text())
    runtime_pickle=pickle_runtime(args.target_dir,parents[0]);assert runtime_pickle['fingerprint']==json.loads((args.output/'linkage/snapshot.json').read_text())['runtime_pickle']['fingerprint']
    assert any(v[1]=='serde' and v[3]==fp for v in contents['deps'])
    keep=args.output/'original-linkage';keep.mkdir(exist_ok=True);files={}
    for source in (lib,meta,meta.with_suffix(''),serde_file,serde_file.with_suffix('.json'),*map(Path,runtime_pickle['files'])):
        dest=keep/source.name;shutil.copyfile(source,dest);assert sha256(dest)==sha256(source);files[str(dest)]=sha256(source)
    for source in map(Path,ident['native_files']):
        dest=keep/source.name;shutil.copyfile(source,dest);files[str(dest)]=sha256(source)
    record={'runtime_pickle':runtime_pickle,'source':original,'identity':ident,'wheel':wheel_record(args.wheel_dir/'original',ident),'serde_fingerprint':fp,'talib_rlib':str(lib),'talib_sha256':sha256(lib),'metadata':str(meta),'metadata_sha256':sha256(meta),'retained':files}
    (keep/'snapshot.json').write_text(json.dumps(record,indent=2)+'\n')


def extract_struct(source,name):
    text=source.read_text();needle='#[derive(Deserialize)]\npub struct '+name
    assert text.count(needle)==1
    start=text.index(needle);opening=text.index('{',start);depth=1;end=opening+1
    while depth:
        depth+= (text[end]=='{')-(text[end]=='}');end+=1
    return text[start:end]+'\n'


def fixtures(args):
    import numpy as np,pickle
    assert np.__version__=='2.5.3'
    folder=args.output/'fixtures';folder.mkdir(exist_ok=True);result={}
    original=(args.native_source/'tests/data/kwargs-sarext-protocol5.pkl').read_bytes();default=pickle.loads(original)
    assert default=={'params':dict(zip(KEYS,(0.,0.,.02,.02,.2,.02,.02,.2))),'lookback':1,'recursive':True},default
    add=(args.native_source/'tests/data/kwargs-add-protocol5.pkl').read_bytes();assert pickle.loads(add)=={'params':{},'lookback':0,'recursive':False}
    pmap={'default':default,'reversal':{'params':dict(zip(KEYS,(-101.,.05,.03,.04,.3,.025,.035,.25))),'lookback':1,'recursive':True},'add':pickle.loads(add)}
    close=100+np.cumsum(np.random.default_rng(260126).normal(0,.1,1000000))
    for f in ('default','reversal','add','init'):
        shared=pmap.get(f,default)
        if f=='default':shared={**default,'params':{k:float(v)for k,v in default['params'].items()}}
        payload=add if f=='add' else pickle.dumps(shared,protocol=5)
        pk=folder/(f+'.pkl');pk.write_bytes(payload)
        values=list(pmap.get(f,default)['params'].values()) if f!='add' else [0.]*8
        if f=='reversal':values=[pmap[f]['params'][k] for k in KEYS]
        for n in sorted({n for name,n,_ in CELLS if name==f}):
            data=folder/(f+'-'+str(n)+'.bin')
            with data.open('wb') as out:
                out.write(b'SARINPUT'+struct.pack('<Q8d',n,*values))
                if f=='init':h=l=np.array([],dtype='f8')
                elif n and f=='default':h=close[:n]+1;l=close[:n]-1
                elif n:
                    center=np.resize(np.array([100.,110.,90.,115.,85.,120.,80.,100.]),n);h=center+1;l=center-1
                else:h=l=np.array([],dtype='f8')
                out.write(h.astype('<f8').tobytes());out.write(l.astype('<f8').tobytes())
            result[f'{f}/{n}']={'input':str(data),'input_sha256':sha256(data),'pickle':str(pk),'pickle_sha256':sha256(pk),'params':shared,'n':n}
    return result



def parse_ieee(text):
    assert text.startswith('C_VERSION 0.8.1 ')
    pattern=r'^IEEE_CONTRACTS comparisons=100 full=20 invalid_no_writes=68 nan_bit_differences=(\d+) policy=nan_positions_other_bits_exact nonfinite_options_observed=48$'
    counts=re.findall(pattern,text,re.M);assert len(counts)==1
    row_pattern=r'^IEEE_ROW pstart=([0-9a-f]{16}) shape=(\d+) start=(\d+) end=(\d+) beg=(\d+) count=(\d+) nan_bit_differences=(\d+)$'
    raw_rows=re.findall(row_pattern,text,re.M);assert sum(line.startswith('IEEE_ROW')for line in text.splitlines())==len(raw_rows)==100
    expected=set(itertools.product(('0000000000000000','c059400000000000'),range(10),((0,63),(1,63),(7,31),(0,0),(0,1))))
    rows={}
    for p,shape,start,end,beg,count,nan in raw_rows:
        shape,start,end,beg,count,nan=map(int,(shape,start,end,beg,count,nan));key=(p,shape,(start,end));assert key in expected and key not in rows
        first=max(start,1);want=(0,0)if first>end else(first,end-first+1);assert (beg,count)==want and 0<=nan<=count
        rows[key]={'pstart_bits':p,'shape':shape,'start':start,'end':end,'beg':beg,'count':count,'nan_bit_differences':nan}
    assert set(rows)==expected
    detail=re.findall(r'^IEEE_NAN_DIFF pstart=([0-9a-f]{16}) shape=(\d+) start=(\d+) end=(\d+) index=(\d+) c_bits=([0-9a-f]{16}) rust_bits=([0-9a-f]{16})$',text,re.M)
    assert sum(line.startswith('IEEE_NAN_DIFF')for line in text.splitlines())==len(detail)==int(counts[0])==sum(r['nan_bit_differences']for r in rows.values())
    seen=set();records=[];perrow=collections.Counter()
    for p,shape,start,end,index,a,b in detail:
        shape,start,end,index=map(int,(shape,start,end,index));key=(p,shape,start,end,index);assert key not in seen;seen.add(key)
        rowkey=(p,shape,(start,end));assert rowkey in rows and 0<=index<rows[rowkey]['count'];perrow[rowkey]+=1
        x,y=(struct.unpack('<d',int(v,16).to_bytes(8,'little'))[0]for v in (a,b));assert math.isnan(x)and math.isnan(y)and a!=b
        records.append({'pstart_bits':p,'shape':shape,'start':start,'end':end,'index':index,'c_bits':a,'rust_bits':b})
    assert all(perrow[key]==row['nan_bit_differences']for key,row in rows.items())
    option_pattern=r'^OPTION_C_RESULT pstart=([0-9a-f]{16}) option=(\d+) value_bits=([0-9a-f]{16}) code=(\d+) beg=(\d+) count=(\d+) core=BadParam raw_bits=(\[[^\n]+\])$'
    options=re.findall(option_pattern,text,re.M);assert len(options)==sum(line.startswith('OPTION_C_RESULT')for line in text.splitlines())==48
    expected_options=set(itertools.product(('0000000000000000','c059400000000000'),range(8),('7ff8000000000000','7ff0000000000000','fff0000000000000')));option_rows={}
    for profile,opt,value,code,beg,count,bits in options:
        opt,code,beg,count=map(int,(opt,code,beg,count));key=(profile,opt,value);assert key in expected_options and key not in option_rows
        raw=json.loads(bits);assert len(raw)==72 and all(type(v)is int and 0<=v<2**64 for v in raw)
        assert (beg,count)==((1,63)if code==0 else(0,0));assert raw[count:]==[CANARY]*(72-count)
        option_rows[key]={'pstart_bits':profile,'option_index':opt,'option_name':KEYS[opt],'value_bits':value,'c_code':code,'beg':beg,'count':count,'core_code':'BadParam','raw_output_bits':raw}
    assert set(option_rows)==expected_options
    return {'policy':'NaN positions equal; finite/signed-zero/infinity bits exact; both physical tails raw canary; Core-to-full all bits exact','comparisons':list(rows.values()),'full_raw_exact':20,'invalid_no_writes':68,'nan_bit_differences':records,'nonfinite_options':list(option_rows.values())}


def build(args):
    flags=flags_record();runtime=runtime_record();e=flags['environment']
    assert e['RUSTFLAGS']==e['CARGO_ENCODED_RUSTFLAGS']=='' and e['CARGO_PROFILE_RELEASE_LTO']=='false' and e['CARGO_PROFILE_RELEASE_CODEGEN_UNITS']=='16'
    snap=json.loads((args.output/'linkage/snapshot.json').read_text());old=json.loads((args.output/'original-linkage/snapshot.json').read_text())
    assert snap['source']==source_record(args.native_source,NATIVE) and old['source']==source_record(args.original_source,ORIGINAL)
    assert snap['identity']==identity(args.native_python) and old['identity']==identity(args.original_python)
    assert snap['flags']==flags
    for record in (snap,old):
        for field in ('retained','fingerprints'):
            for p,digest in record.get(field,{}).items():assert sha256(p)==digest
    assert sha256(old['talib_rlib'])==old['talib_sha256']
    fp,serde_file=serde_identity(args);assert fp==old['serde_fingerprint']
    runtime_pickle=snap['runtime_pickle'];assert runtime_pickle['serde_fingerprint']==fp and runtime_pickle['fingerprint']==old['runtime_pickle']['fingerprint']
    pickle_lib=Path(runtime_pickle['path']);pickle_meta=Path(runtime_pickle['metadata']);assert sha256(pickle_lib)==runtime_pickle['sha256']
    deps=snap['dependencies'];assert set(deps)=={'ta_lib','polars','serde','jemallocator'}
    for record in deps.values():assert sha256(record['path'])==record['sha256']
    for ident in (snap['identity'],old['identity']):assert ident['polars']=='1.44.2' and ident['numpy']=='2.5.3' and ident['python'].startswith('3.12.')
    assert snap['identity']['talib'].startswith('0.8.3')
    vendor=args.original_source/'talib-sys/vendor/ta-lib-0.8.1-src.tar.gz';assert sha256(vendor)==C_SHA
    archives=list(args.target_dir.glob('release/build/talib-sys-*/out/lib/libta-lib.a'));assert len(archives)==1
    c_lib=archives[0];native_paths=sorted(args.target_dir.glob('release/build/*/out/lib'))
    native_archives={str(p):sha256(p) for d in native_paths for p in d.glob('*.a')}
    for name in {Path(p).name for p in native_archives}:assert len({d for p,d in native_archives.items() if Path(p).name==name})==1
    folder=args.output/'probe';folder.mkdir(exist_ok=True);support=folder/'source';support.mkdir(exist_ok=True)
    shutil.copytree(args.native_source/'src/compat',support/'compat',dirs_exist_ok=True)
    shutil.copyfile(args.native_source/'src/compat.rs',support/'compat/mod.rs')
    modules='#![allow(dead_code,unused_imports)]\n'
    for name,file in (('native','native.rs'),('compat','compat.rs'),('params','params.rs'),('utils','utils.rs')):
        path=support/'compat/mod.rs' if name=='compat' else support/file
        if name!='compat':shutil.copyfile(args.native_source/'src'/file,path)
        modules+=f'#[path="{path}"] mod {name};\n'
    for name,source in (('old_envelope',args.original_source/'src/missing.rs'),('new_envelope',args.native_source/'src/missing.rs')):
        text='use serde::Deserialize;\n'+extract_struct(source,'Masked<K>')
        if name=='old_envelope':text+=extract_struct(source,'NoParams')
        path=support/(name+'.rs');path.write_text(text);modules+=f'#[path="{path}"] mod {name};\n'
    modules+='mod generated {\n'+mapper(args.native_source)+'\n}\n'
    wrapper=folder/'probe.rs';wrapper.write_text(modules+(HERE/'sarext_profile_probe.rs').read_text().split('\n',1)[1])
    binary=folder/'sarext-probe';command=['rustc','--edition=2021','-O','-C','codegen-units=16','-C','lto=off',str(wrapper),'-L','dependency='+str(args.target_dir/'release/deps')]
    for name,r in {**deps,'serde_pickle':{'path':str(pickle_lib)},'talib_original':{'path':old['talib_rlib']}}.items():command+=['--extern',name+'='+r['path']]
    for p in native_paths:command+=['-L','native='+str(p)]
    command+=['-l','static=ta-lib','-l','m','-o',str(binary)];invoke(command,folder/'build.log')
    counter=folder/'sarext-counter';invoke(command[:-2]+['--cfg','sarext_counter','-o',str(counter)],folder/'counter-build.log')
    test=folder/'probe-tests';invoke(command[:-2]+['--cfg','sarext_probe_contracts','-o',str(test)],folder/'test-build.log');invoke([test],folder/'tests.log')
    test_counter=folder/'counter-probe-tests';invoke(command[:-2]+['--cfg','sarext_counter','--cfg','sarext_probe_contracts','-o',str(test_counter)],folder/'counter-test-build.log');invoke([test_counter],folder/'counter-tests.log')
    invoke([binary,'--ieee-contracts'],folder/'ieee.log')
    ieee=parse_ieee((folder/'ieee.log').read_text())
    data=fixtures(args)
    files={str(p):sha256(p) for p in support.rglob('*.rs')};files.update(native_archives);files[str(folder/'ieee.log')]=sha256(folder/'ieee.log')
    for proof in (test,test_counter,folder/'tests.log',folder/'counter-tests.log'):files[str(proof)]=sha256(proof)
    for root in (c_lib.parent.parent,):
        for p in root.rglob('CMakeCache.txt'):
            dest=folder/'c-configuration'/p.relative_to(root);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,dest);files[str(dest)]=sha256(dest)
    assert any('CMakeCache.txt' in p for p in files),'actual original C configuration required'
    for p in (pickle_lib,pickle_meta,pickle_meta.with_suffix(''),serde_file,serde_file.with_suffix('.json')):files[str(p)]=sha256(p)
    record={'runtime':runtime,'flags':flags,'ieee_gate':ieee,'snapshot':snap,'original_snapshot':old,'binary':str(binary),'binary_sha256':sha256(binary),'counter_binary':str(counter),'counter_binary_sha256':sha256(counter),'wrapper':str(wrapper),'wrapper_sha256':sha256(wrapper),'command':command,'support':files,'c_archive':str(c_lib),'c_archive_sha256':sha256(c_lib),'c_vendor_sha256':C_SHA,'scripts':{name:sha256(HERE/name) for name in SCRIPTS},'fixtures':data,'cells':CELLS,'groups':GROUPS,'orders4':ORDERS4,'orders2':ORDERS2,'codegen_caveat':'Primary probe uses direct actual Jemalloc; counter binary is separate. Diagnostic driver checks differ; source/library identity does not prove product machine-code identity. No check-count or dispatch attribution without actual ELF comparison.'}
    (args.output/'build-provenance.json').write_text(json.dumps(record,indent=2)+'\n')


def verify(args):
    p=json.loads((args.output/'build-provenance.json').read_text());assert runtime_record()==p['runtime'] and flags_record()==p['flags']
    for key,source,pin,python in (('snapshot',args.native_source,NATIVE,args.native_python),('original_snapshot',args.original_source,ORIGINAL,args.original_python)):
        r=p[key];assert source_record(source,pin)==r['source'] and identity(python)==r['identity'];assert wheel_record(args.wheel_dir/('native' if key=='snapshot' else 'original'),r['identity'])==r['wheel']
        for field in ('retained','fingerprints'):
            for name,d in r.get(field,{}).items():assert sha256(name)==d
    files={p['counter_binary']:p['counter_binary_sha256'],p['binary']:p['binary_sha256'],p['wrapper']:p['wrapper_sha256'],p['c_archive']:p['c_archive_sha256'],**p['support']}
    files.update({r['path']:r['sha256'] for r in p['snapshot']['dependencies'].values()})
    files[p['original_snapshot']['talib_rlib']]=p['original_snapshot']['talib_sha256']
    for r in p['fixtures'].values():files[r['input']]=r['input_sha256'];files[r['pickle']]=r['pickle_sha256']
    for name,d in files.items():assert sha256(name)==d,name
    for name,d in p['scripts'].items():assert sha256(HERE/name)==d
    assert p['cells']==[list(c) for c in CELLS]
    return p

def capture(path,f,n,m,p):
    b=Path(path).read_bytes();assert b[:8]==b'SARDIAG1' and len(b)>=16
    size=struct.unpack('<Q',b[8:16])[0];assert len(b)==16+8*size
    words=struct.unpack('<'+'Q'*size,b[16:]);facts={}
    if m in KERNEL:
        assert len(words)==n+10 and words[:2]==(1,n-1) and words[-8:]==(CANARY,)*8
        values=struct.unpack('<'+'d'*n,b[32:32+8*n]);assert words[2]==0x7ff8000000000000
        assert all(math.isfinite(v) for v in values[1:]),'timed finite-price outputs must stay finite'
        if f=='reversal':assert any(v>0 for v in values[1:]) and any(v<0 for v in values[1:]),'reversal fixture is vacuous'
        facts={'positive':sum(v>0 for v in values[1:]),'negative':sum(v<0 for v in values[1:]),'beg':1,'count':n-1}
    elif m.startswith('decode_'):
        expected=p['fixtures'][f'{f}/0']['params'];v=expected['params']
        want=tuple(struct.unpack('<Q',struct.pack('<d',v[k]))[0] for k in KEYS) if f!='add' else ()
        assert words==want+(expected['lookback'],int(expected['recursive']))
    elif m.startswith('setup_'):assert words==(1,)
    else:assert words==((n if m=='init_nan' else 1),n,0x7ff8000000000000)
    return {'path':str(path),'sha256':sha256(path),'bytes':len(b),'facts':facts}


def parse(text,f,n,m,action):
    assert text.startswith('C_VERSION 0.8.1 ')
    rows=VALID.findall(text);assert len(rows)==1
    assert rows[0]==(f,m,str(n),'false' if action=='--capture-only' else 'true','true' if m in KERNEL and m!='native_full' else 'false')
    probes=PROBE.findall(text);counts=COUNTER.findall(text)
    if action=='--golden':
        assert len(probes)==1 and not counts and probes[0][0]==str(ITERS[n])
        values=json.loads(probes[0][1]);assert len(values)==31 and all(type(v) in (float,int) and math.isfinite(v) and v>0 for v in values)
        return {'samples_ns':values,'median_ns':statistics.median(values)}
    assert not probes
    if action=='--counter':
        assert len(counts)==1;values=json.loads(counts[0]);assert len(values)==4 and all(type(v)is int and v>=0 for v in values)
        assert values[2]+values[3]<=values[0];return {'counts':values}
    assert not counts;return {}


def command(p,f,n,m,path,action,golden=None):
    r=p['fixtures'][f'{f}/{n}'];v=[p['counter_binary'] if action=='--counter' else p['binary'],f,str(n),m,r['input'],r['pickle'],str(path),action]
    if action!='--capture-only':assert golden;v+=[str(golden)]
    return v


def execute(cmd,stem,env,timeout=30):
    Path(str(stem)+'-command.json').write_text(json.dumps(cmd,indent=2)+'\n');before=resource.getrusage(resource.RUSAGE_CHILDREN)
    try:r=subprocess.run(cmd,env=env,capture_output=True,text=True,timeout=timeout)
    except subprocess.TimeoutExpired as e:
        Path(str(stem)+'-failure.json').write_text(json.dumps({'timeout':timeout,'command':cmd}));raise
    after=resource.getrusage(resource.RUSAGE_CHILDREN);Path(str(stem)+'.stdout').write_text(r.stdout);Path(str(stem)+'.stderr').write_text(r.stderr);r.check_returncode()
    return r.stdout,{'minor':after.ru_minflt-before.ru_minflt,'major':after.ru_majflt-before.ru_majflt}


def validate(args,p,env):
    folder=args.output/'validation';folder.mkdir(exist_ok=True);rows=[];goldens={}
    for f,n,m in CELLS:
        stem=folder/f'{f}-{n}-{m}';path=Path(str(stem)+'.bin');cmd=command(p,f,n,m,path,'--capture-only')
        text,faults=execute(cmd,stem,env);parse(text,f,n,m,'--capture-only');r=capture(path,f,n,m,p)
        group=f'{f}/{n}/'+('kernel' if m in KERNEL else 'decode' if m.startswith('decode') else 'setup' if m.startswith('setup') else m)
        if group in goldens:assert r['sha256']==goldens[group]['sha256'],group
        else:goldens[group]=r
        rows.append({'fixture':f,'n':n,'mode':m,'capture':r,'command':cmd,'whole_child_faults':faults,'group':group})
    assert len(rows)==50
    counters=[]
    for r in rows:
        f,n,m=r['fixture'],r['n'],r['mode'];golden=goldens[r['group']];stem=folder/f'counter-{f}-{n}-{m}';path=Path(str(stem)+'.bin');cmd=command(p,f,n,m,path,'--counter',golden['path'])
        text,faults=execute(cmd,stem,env);counts=parse(text,f,n,m,'--counter');actual=capture(path,f,n,m,p);assert actual['sha256']==golden['sha256'];path.unlink();counters.append({**r,**counts,'command':cmd,'whole_child_faults':faults,'duplicate_deleted_after_hash':True})
    record={'all50_captures_and50_counter_children_before_any_timer':True,'checks':rows,'counters':counters,'goldens':goldens,'build_provenance_sha256':sha256(args.output/'build-provenance.json')}
    (args.output/'validation-complete.json').write_text(json.dumps(record,indent=2)+'\n');return record


def measure(args,p,v,env):
    assert v['all50_captures_and50_counter_children_before_any_timer'] and len(v['checks'])==len(v['counters'])==50
    assert v['build_provenance_sha256']==sha256(args.output/'build-provenance.json')
    folder=args.output/'children';folder.mkdir(exist_ok=True);rows=[];start=time.monotonic();deadline=start+300
    lookup={(r['fixture'],r['n'],r['mode']):r for r in v['checks']}
    with (args.output/'raw.jsonl').open('w') as log:
        for f,n,modes in GROUPS:
            orders=ORDERS4 if len(modes)==4 else ORDERS2
            for round,order in enumerate(orders,1):
                for index in order:
                    m=modes[index];left=deadline-time.monotonic();assert left>0,'300s timing budget exceeded; partial rows are not a complete result'
                    baseline=lookup[f,n,m];golden=v['goldens'][baseline['group']];assert sha256(golden['path'])==golden['sha256']
                    stem=folder/f'{f}-{n}-{round}-{m}';path=Path(str(stem)+'.bin');cmd=command(p,f,n,m,path,'--golden',golden['path'])
                    text,faults=execute(cmd,stem,env,min(30,left));data=parse(text,f,n,m,'--golden');actual=capture(path,f,n,m,p);assert actual['sha256']==golden['sha256']
                    r={'fixture':f,'n':n,'mode':m,'round':round,'command':cmd,'capture':actual,'golden':golden,'whole_child_faults':faults,**data}
                    Path(str(stem)+'-proof.json').write_text(json.dumps(r,indent=2)+'\n');path.unlink();r['duplicate_deleted_after_hash']=True;rows.append(r);log.write(json.dumps(r)+'\n');log.flush()
    assert len(rows)==600 and sum(len(r['samples_ns'])for r in rows)==18600
    result={};comparisons={}
    for f,n,modes in GROUPS:
        values={}
        for m in modes:
            found=[r for r in rows if (r['fixture'],r['n'],r['mode'])==(f,n,m)];assert len(found)==12 and [r['round']for r in found]==list(range(1,13))
            med=[r['median_ns']for r in found];values[m]={'process_medians_ns':med,'median_ns':statistics.median(med)}
        result[f'{f}/{n}/'+modes[0]]=values
        for a,b in itertools.combinations(modes,2):
            x=values[a]['process_medians_ns'];y=values[b]['process_medians_ns'];comparisons[f'{f}/{n}/{a}_vs_{b}']={'after_latency_percent':100*(statistics.median(y)/statistics.median(x)-1),'paired_ratios':[i/j for i,j in zip(x,y)],'after_faster_rounds':sum(j<i for i,j in zip(x,y)),'ratio_envelope':[min(x)/max(y),max(x)/min(y)]}
    report={'provenance':p,'validation':v,'rows':rows,'results':result,'comparisons':comparisons,'timed_children':600,'samples':18600,'elapsed_seconds':time.monotonic()-start,'affinity':sorted(os.sched_getaffinity(0)),
    'limitations':'Stage diagnostics, not additive/exclusive attribution or product throughput. Counterpass runs in separate children; counts cover Rust Jemalloc request/cumulativebytes/realloc/zeroed only, not Cmalloc/dealloc/live/RSS. Primary binary uses direct Jemalloc, separate counter binary has cfg-only allocator wrapper and cannot enter timed mode. Full is native::compute with predecoded Params, excludes pickle/missing.apply/plugin/Python/query overhead. Synthetic reserve+prefix materializes only initialized prefix and never calls kernel/reads capacity. Selected validation/golden can warm allocator/cache. Whole-child faults include input/capture and are not kernel faults. Probe codegen not asserted equal to product; library/ELF hashes retained. Case blocks sequential; extrema envelopes not confidence intervals. All negatives retained.'}
    assert report['elapsed_seconds']<=300
    (args.output/'summary.json').write_text(json.dumps(report,indent=2)+'\n')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    for side in ('native','original'):
        parser.add_argument('--'+side+'-source',type=Path,required=True);parser.add_argument('--'+side+'-python',type=Path,required=True)
    for k in ('output','target-dir','wheel-dir'):parser.add_argument('--'+k,type=Path,required=True)
    mode=parser.add_mutually_exclusive_group(required=True)
    for k in ('snapshot-native','snapshot-original','build','run'):mode.add_argument('--'+k,action='store_true')
    args=parser.parse_args()
    for key,value in vars(args).copy().items():
        if isinstance(value,Path):setattr(args,key,value.absolute()if key.endswith('_python')else value.resolve())
    args.output.mkdir(parents=True,exist_ok=True)
    if args.snapshot_native:snapshot(args)
    elif args.snapshot_original:snapshot_original(args)
    elif args.build:build(args)
    else:
        p=verify(args);previous=set(os.sched_getaffinity(0));assert previous
        env={**os.environ,**{k:'1'for k in ('POLARS_MAX_THREADS','OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS')}}
        try:os.sched_setaffinity(0,{min(previous)});v=validate(args,p,env);measure(args,p,v,env);verify(args)
        finally:os.sched_setaffinity(0,previous)

if __name__=='__main__':main()
