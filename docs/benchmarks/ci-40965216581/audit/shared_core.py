"""NEW independent recovery auditor; not byte-identical to inaccessible old files.
Reads artifacts only; never imports a repository controller or executes a wheel.
"""
from __future__ import annotations
import argparse,email,hashlib,json,math,re,statistics,struct,zipfile
from collections import Counter
from pathlib import Path
import numpy as np

SIDES=('original','prior','candidate')
PAIRS=(('original','prior'),('prior','candidate'),('original','candidate'))
ORDERS=(('original','prior','candidate'),('prior','candidate','original'),('candidate','original','prior'),('candidate','prior','original'),('prior','original','candidate'),('original','candidate','prior'))
EIGHT=('ema','rsi','macd','atr','adx','cci','stddev','ppo')
FAMILIES=EIGHT+('add','minmaxindex','cdldoji','hma','supertrend','vwma','mavp','bbands','sarext','var','correl','cmou','mavp_fixed')
PATTERNS=('constant','zero','trend','flat_then_move','move_then_flat','fraction_then_zero','tiny','all_null','all_nan','leading_null','leading_nan','null','nan','infinity','negative_infinity','leading_infinity','leading_negative_infinity','chunked','domain','high_offset','micro_offset','large_constant','large_finite','high_volume')
PROFILE='release (maturin --release --locked), portable CPU target'

def need(ok,msg):
    if not ok:raise ValueError(msg)
def decode(content):
    def pairs(rows):
        d={}
        for k,v in rows:need(k not in d,'duplicate JSON key '+k);d[k]=v
        return d
    def constant(token):raise ValueError('nonfinite JSON token '+token)
    return json.loads(content,object_pairs_hook=pairs,parse_constant=constant)
def js(path):return decode(Path(path).read_text())
def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb')as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()
def eq(a,b,where='value'):
    if isinstance(b,dict):
        need(isinstance(a,dict)and set(a)==set(b),where+': keys')
        for k in b:eq(a[k],b[k],where+'.'+k)
    elif isinstance(b,list):
        need(isinstance(a,list)and len(a)==len(b),where+': length')
        for i,(x,y)in enumerate(zip(a,b)):eq(x,y,where+f'[{i}]')
    elif isinstance(b,float):need(type(a)in(int,float)and(a==b or math.isclose(a,b,rel_tol=1e-12,abs_tol=1e-12)),f'{where}: {a} != {b}')
    else:need(type(a)is type(b)and a==b,f'{where}: {a!r} != {b!r}')
def pct(values,p):
    a=sorted(values);x=(len(a)-1)*p;i=math.floor(x)
    return a[i]+(a[min(i+1,len(a)-1)]-a[i])*(x-i)
def inventory(diagnostic):
    out=[]
    for n in(1000,1000000):out +=[f'{f}/{n}'for f in FAMILIES]+[f'mix8/{n}',f'control_cumsum_dense/{n}']
    layouts=[(100,10000,False),(1000,1000,False),(10000,100,False),(2000,100,True)]
    if diagnostic:layouts +=[(50000,20,False),(10,100000,False),(1,1000000,False)]
    for groups,bars,interleaved in layouts:
        ending=f'/{groups}x{bars}'+('_interleaved'if interleaved else'')
        funcs=FAMILIES+('mix8',)if bars in(100,1000,10000)else('ema','atr')
        out +=['grouped_'+f+ending for f in funcs]+['control_cumsum'+ending]
    need(len(out)==(147 if diagnostic else 138)and len(set(out))==len(out),'benchmark inventory')
    return out
def shape(name,api):
    family,layout=name.split('/');layout=layout.removesuffix('_interleaved');n=math.prod(map(int,layout.split('x')))
    family=family.removeprefix('grouped_')
    fields=1 if family.startswith('control_cumsum')else sum(len(api[f]['outputs'])for f in EIGHT)if family=='mix8'else len(api['mavp'if family=='mavp_fixed'else family]['outputs'])
    return n,fields
def corpus_keys(api):
    keys=[]
    for f in api:
        n=f['name'];keys +=[f'{n}/length/{v}'for v in(0,1,2,10,29,30,31,64,257)]+[n+'/'+p for p in PATTERNS]+[f'{n}/warmup/{v}'for v in(-1,0,1)]
        if any(p['name']=='timeperiod'for p in f['params']):keys +=[f'{n}/period_pattern/{v}/{p}'for v in(2,5,31)for p in('nan','null','constant','flat_then_move')]
        keys +=[n+'/float32',n+'/over',n+'/over_ordered']
        for p in f['params']:
            k,t=p['name'],p['type']
            if t=='TA_MAType':values=(*range(16),-(2**31))
            elif k=='timeperiod':values=(1,2,5,31,-1,-(2**31))
            elif t=='double':values=(0.,.3,1.)if'penetration'in k or k in('vfactor','percentile')else(.5,2.5)
            else:values=(1,3)
            keys +=[f'{n}/param/{k}/{v}'for v in values]
            if t=='TA_MAType':keys +=[f'{n}/matype_pattern/{k}/{v}/{p}'for p in('high_offset','micro_offset','infinity','leading_negative_infinity')for v in range(14)]
        if n in('ppo','pvo'):keys +=[f'{n}/dead_window/{v}'for v in(0,2,5,9)]
    keys +=[f'mavp/output_init/{m}/{v}/{p}/{b}'for m in range(14)for v in(31,200)for p in('random','high_offset')for b in(False,True)]
    keys +=[f'{n}/legacy_max'for n in('percentile','percentrank','mavp')]
    need(len(keys)==len(set(keys)),'duplicate corpus key');return set(keys)
def arrays(old,new,om,nm,exact=False,tiny=False,where='arrays'):
    need(old.shape==new.shape and old.dtype==new.dtype,where+': shape/dtype')
    need(om.dtype==nm.dtype==np.dtype(bool)and om.shape==nm.shape==old.shape,where+': mask dtype/shape')
    need(np.array_equal(om,nm),where+': null positions');a,b=old[~om],new[~nm]
    for fn in(np.isnan,np.isposinf,np.isneginf):need(np.array_equal(fn(a),fn(b)),where+': NaN/infinity positions/sign')
    same=(a==b)&(np.signbit(a)==np.signbit(b))if a.dtype.kind=='f'else a==b
    same=same|np.isnan(a);atol=1e-10
    if tiny:atol=min(atol,float(np.max(np.abs(a[np.isfinite(a)])))*1e-10 if np.isfinite(a).any()else 0.)
    valid=same if exact or a.dtype.kind in'iu'else np.isclose(a,b,rtol=1e-10,atol=atol,equal_nan=True)
    need(bool(valid.all()),where+': values differ')
    finite=np.isfinite(a)&np.isfinite(b)
    with np.errstate(over='ignore',invalid='ignore'):maximum=float(np.max(np.abs(a[finite]-b[finite])))if finite.any()else 0.
    zeros=int(np.count_nonzero((a==0)&(b==0)&(np.signbit(a)!=np.signbit(b))))if a.dtype.kind=='f'else 0
    return {'checked':len(a),'different':int(not same.all()),'max_abs':maximum,'zero_sign_differences':zeros,'nan_values':int(np.isnan(a).sum()),'infinite_values':int(np.isinf(a).sum())}
def check_corpus(base,trust):
    directory=base/'corpus';paths={s:directory/(s+'.npz')for s in SIDES};data={s:np.load(p,allow_pickle=False)for s,p in paths.items()};meta={s:decode(str(d['metadata']))for s,d in data.items()}
    expected=corpus_keys(trust['api']);api={f['name']:f for f in trust['api']}
    for side,m in meta.items():
        need(set(m['cases'])==expected and set(m['api'])==set(m['api_call_contract'])==set(api),side+': corpus/API inventory')
        need(m['polars']=='1.44.2'and m['numpy']=='2.5.3',side+': corpus versions')
        need(m['talib'].startswith('0.8.1')if side=='original'else m['talib']=='0.8.3 (native Rust; polars-talib compatibility)',side+': TA-Lib runtime')
        names={'metadata'}
        for key,row in m['cases'].items():
            if'error'in row:need(set(row)=={'error'}and isinstance(row['error'],str),'corpus error schema');continue
            need(set(row)=={'schema','height','fields'}and len(row['fields'])==len(api[key.split('/')[0]]['outputs']),key+': field count')
            for field in row['fields']:
                names.update((field,field+'_null'));need(data[side][field].shape==(row['height'],),key+': raw shape')
        need(set(data[side].files)==names,side+': orphan/missing arrays')
    out={}
    for old,exact,file in(('original',False,'original-vs-candidate.json'),('prior',True,'prior-vs-candidate-exact.json')):
        a,b=meta[old],meta['candidate'];need(a['api_call_contract']==b['api_call_contract'],'call contracts differ');metrics=Counter();maximum=0.;errors=Counter()
        for key,row in a['cases'].items():
            other=b['cases'][key]
            if'error'in row or'error'in other:need(row==other,key+': error differs');errors[row['error']]+=1;continue
            need(row['schema']==other['schema']and row['height']==other['height']and len(row['fields'])==len(other['fields']),key+': schema/length/field order')
            for x,y in zip(row['fields'],other['fields']):
                r=arrays(data[old][x],data['candidate'][y],data[old][x+'_null'],data['candidate'][y+'_null'],exact=exact,tiny='/tiny'in key,where=key);maximum=max(maximum,r.pop('max_abs'));metrics.update(r)
        report=js(directory/file);values={'cases':len(expected),'checked_values':metrics['checked'],'require_exact':exact,'rtol':0. if exact else 1e-10,'atol':0. if exact else 1e-10,'api_signatures_match':a['api']==b['api'],'api_call_contract_match':True,'annotation_changed_functions':[n for n in a['api']if a['api'][n]!=b['api'].get(n)],'fields_with_bit_differences':metrics['different'],'max_absolute_difference':maximum,'failures':[],'baseline_sha256':sha(paths[old]),'candidate_sha256':sha(paths['candidate'])}
        for key,value in values.items():eq(report[key],value,'corpus '+key)
        out[old+'_vs_candidate']={'cases':len(expected),'exact_required':exact,**dict(metrics),'max_abs':maximum,'error_cases':dict(errors)}
    for d in data.values():d.close()
    return out
def comparison(old,new):
    a=[statistics.median(r['samples_ms'])for r in old];b=[statistics.median(r['samples_ms'])for r in new];ratios=[x/y for x,y in zip(a,b)];env=[min(a)/max(b),max(a)/min(b)]
    assessment='consistent faster on this runner'if env[0]>1.05 else'consistent slower on this runner'if env[1]<1/1.05 else'small or noisy difference'
    return {'baseline_median_ms':statistics.median(a),'candidate_median_ms':statistics.median(b),'baseline_process_medians_ms':a,'candidate_process_medians_ms':b,'paired_ratios':ratios,'median_paired_ratio':statistics.median(ratios),'ratio_envelope':env,'assessment':assessment,'baseline_sample_p10_p90_ms':[pct([v for r in old for v in r['samples_ms']],p)for p in(.1,.9)],'candidate_sample_p10_p90_ms':[pct([v for r in new for v in r['samples_ms']],p)for p in(.1,.9)]}
def faults(rows,key):
    values=[r[key]for r in rows]
    need(all(v is None or isinstance(v,list)and len(v)==51 and all(type(x)is int and x>=0 for x in v)for v in values),'fault samples')
    if any(v is None for v in values):return None
    med=[statistics.median(v)for v in values];return {'median':statistics.median(med),'process_medians':med,'p10_p90':[pct([x for v in values for x in v],p)for p in(.1,.9)]}
def elf_header(content):
    need(len(content)>=64 and content[:4]==b'\x7fELF','native library is not ELF')
    need(content[4:7]==bytes((2,1,1)),'native ELF class/endian/version')
    kind,machine,version=struct.unpack_from('<HHI',content,16)
    need(kind==3 and machine==62 and version==1 and struct.unpack_from('<H',content,52)[0]==64,'native ELF must be ELF64 x86_64 ET_DYN')
    return {'class':64,'endian':'little','machine':62,'type':'ET_DYN'}
def cli_options(argv):
    need(isinstance(argv,list)and len(argv)>=2 and all(type(x)is str for x in argv),'CLI vector types')
    values={'--source-root','--output','--label','--repeats','--reference','--write-reference','--case-filter'}
    booleans={'--diagnostic','--check-only','--exact-reference'};out={};i=2
    while i<len(argv):
        flag=argv[i];need(flag not in out and flag in values|booleans,'duplicate/unknown CLI option '+flag)
        if flag in values:
            need(i+1<len(argv)and not argv[i+1].startswith('--'),'CLI value missing');out[flag]=argv[i+1];i+=2
        else:out[flag]=True;i+=1
    return out
def wheels(artifact,base,trust):
    lines=[line.split()for line in(base/'wheel-sha256.txt').read_text().splitlines()if line.strip()];need(len(lines)==3,'three wheels required');out={}
    for digest,name in lines:
        parts=Path(name).parts;need(re.fullmatch(r'[0-9a-f]{64}',digest)is not None and len(parts)==2 and parts[0]in{s+'-dist'for s in SIDES}and '..'not in parts and not Path(name).is_absolute()and name.endswith('.whl'),'unsafe wheel checksum path/hash')
        need((artifact/name).resolve().is_relative_to(artifact.resolve()),'wheel path escapes artifact')
    for side in SIDES:
        matches=[(h,n)for h,n in lines if Path(n).parts[0]==side+'-dist'];need(len(matches)==1,'wheel side identity');h,name=matches[0];path=artifact/name;need(sha(path)==h,'wheel SHA differs')
        with zipfile.ZipFile(path)as z:
            names=z.namelist();need(len(names)==len(set(names)),'duplicate wheel files');native=[n for n in names if Path(n).name.startswith('_polars_talib')and n.endswith(('.so','.pyd'))];need(len(native)==1,'native extension count')
            py={n:hashlib.sha256(z.read(n)).hexdigest()for n in names if n.startswith('polars_talib/')and n.endswith('.py')};eq(py,trust['sources'][side]['wheel_python'],'wheel Python')
            md=[n for n in names if n.endswith('.dist-info/METADATA')];need(len(md)==1,'wheel metadata');m=email.message_from_bytes(z.read(md[0]));need(m['Name'].replace('_','-')=='polars-talib','package name')
            wm=[n for n in names if n.endswith('.dist-info/WHEEL')];need(len(wm)==1,'wheel ABI metadata');wm=email.message_from_bytes(z.read(wm[0]));tags=wm.get_all('Tag',[])
            need(wm['Root-Is-Purelib']=='false'and tags and all(re.fullmatch(r'cp310-abi3-[A-Za-z0-9_]+x86_64',tag)for tag in tags),'wheel ABI/platform tags')
            need(Path(native[0]).name.endswith('.abi3.so'),'native ABI filename');native_bytes=z.read(native[0]);abi=elf_header(native_bytes)
            out[side]={'wheel_sha256':h,'native_binary_sha256':hashlib.sha256(native_bytes).hexdigest(),'package_version':m['Version'],'abi_header':abi,'wheel_tags':tags,'embedded_libraries':{n:hashlib.sha256(z.read(n)).hexdigest()for n in names if n.endswith(('.so','.pyd','.dll','.dylib','.a','.rlib'))}}
        deps=(base/(side+'-dependencies.txt')).read_text().lower()
        for pin in('numpy==2.5.3','polars==1.44.2','maturin==1.15.0','cmake==4.4.4'):need(pin in deps,'dependency '+pin)
        log=(base/(side+'-build.log')).read_text();need('release'in log and'optimized'in log,'release log');need('target-cpu=native'not in log and'-march=native'not in log,'unexpected native CPU flag evidence')
        if side=='original':need('linking external TA-Lib'not in log,'external C override')
    for name,h in trust['controller_files'].items():need(sha(base/'controller'/name)==h,'controller differs '+name)
    toolchain=(base/'toolchain.txt').read_text();need(toolchain.startswith('rustc 1.90.0 ')and'cmake version 4.4.4'in toolchain,'toolchain differs');return out
def metadata(r,side,t,trust,whl,origin=None):
    for key in('threads','repeats','warmups'):need(type(r[key])is int,'metadata numeric types')
    need(type(r['diagnostic'])is bool and r['threads']==t and r['diagnostic']==(t==1)and r['repeats']==51 and r['warmups']==5,'thread/sample mode')
    need(r['commit']==trust['pins'][side]and r['source_sha256']==trust['sources'][side]['source_sha256'],'source identity')
    need(r['native_binary_sha256']==whl[side]['native_binary_sha256']and r['package']==whl[side]['package_version'],'wheel/native identity')
    need(r['polars']=='1.44.2'and r['numpy']=='2.5.3'and r['python'].startswith('3.12.')and r['rust'].startswith('rustc 1.90.0 '),'runtime versions')
    need('Linux'in r['platform']and r['profile']==PROFILE,'profile/platform');need(isinstance(r['affinity'],list)and len(r['affinity'])==len(set(r['affinity']))==t and all(type(v)is int and v>=0 for v in r['affinity']),'affinity')
    need(r['talib'].startswith('0.8.1')if side=='original'else r['talib']=='0.8.3 (native Rust; polars-talib compatibility)','C/Rust runtime')
    if origin:
        for k in('commit','source_sha256','native_binary_sha256','talib','python','platform','cpu','polars','numpy','rust','profile','threads','affinity','logical_cpus','package'):eq(r[k],origin[k],side+' runtime drift '+k)
def golden(path,names,api):
    total=0;expected=set()
    with np.load(path,allow_pickle=False)as f:
        for name in names:
            n,k=shape(name,api);key=name+'_schema';need(f[key].shape==(),'golden schema');expected.add(key)
            for i in range(k):
                slot=name+'_'+str(i);expected.update((slot,slot+'_null'));a,b=f[slot],f[slot+'_null'];need(a.shape==(n,)and a.dtype.kind in'fiu'and b.shape==(n,)and b.dtype==np.dtype(bool),'golden shape/type');total+=n
        need(set(f.files)==expected,'golden array inventory')
    return total
def golden_pair(old,new,names,api):
    out=Counter()
    with np.load(old,allow_pickle=False)as a,np.load(new,allow_pickle=False)as b:
        for name in names:
            need(str(a[name+'_schema'])==str(b[name+'_schema']),'golden schema/field order');_,k=shape(name,api)
            for i in range(k):
                slot=name+'_'+str(i);r=arrays(a[slot],b[slot],a[slot+'_null'],b[slot+'_null'],where=name);r.pop('max_abs');out.update(r)
    return dict(out)
def thread_audit(base,t,trust,whl):
    directory=base/f'threads-{t}';s=js(directory/'summary.json');p=js(directory/'prepared-validation.json');names=inventory(t==1);api={f['name']:f for f in trust['api']}
    eq(names,trust['benchmark_manifest']['diagnostic'if t==1 else'standard'],'independent reviewed inventory');eq(s['case_inventory'],names);eq(p['inventory'],names)
    need(s['rounds']==6 and s['repeats']==51 and s['warmups']==5 and s['process_isolation']=='one case per fresh process','protocol')
    need(set(s['comparisons'])=={a+'_vs_'+b for a,b in PAIRS}and all(set(v)==set(names)for v in s['comparisons'].values()),'comparison inventory');eq(s['commits'],trust['pins'])
    for key,file in(('reference_sha256','reference.npz'),('prior_reference_sha256','prior-reference.npz')):need(s[key]==p[key]==sha(directory/file),'golden hash')
    count=golden(directory/'reference.npz',names,api);need(golden(directory/'prior-reference.npz',names,api)==count,'prior golden inventory');gcomp=golden_pair(directory/'reference.npz',directory/'prior-reference.npz',names,api)
    need(p['threads']==t and s['threads']==t and s['diagnostic']==(t==1)and s['case_filters']==[]and s['checked_values']==count,'full validation config')
    origins=p['source_validations'];need(set(origins)==set(SIDES),'preparation sides')
    for side,r in origins.items():
        metadata(r,side,t,trust,whl);label='reference'if side=='original'else'validation-'+side;eq(js(directory/(label+'.json')),r,'retained validation')
        need(r['case_inventory']==names and r['case_filters']==[]and not r['results']and not r['exact_reference']and r['checked_values']==(0 if side=='original'else count),'preparation workload checks')
    exact=p['exact_validation'];metadata(exact,'candidate',t,trust,whl,origins['candidate']);eq(js(directory/'validation-exact-prior.json'),exact)
    need(exact['exact_reference']and exact['checked_values']==count and exact['case_inventory']==names and not exact['results']and s['exact_prior_validation']==count,'exact prior check')
    prior=js(directory/'reference-prior.json');metadata(prior,'prior',t,trust,whl,origins['prior']);need(prior['checked_values']==0 and prior['case_inventory']==names and not prior['results'],'prior golden report')
    common=('python','platform','cpu','polars','numpy','rust','profile','threads','affinity','repeats','warmups','diagnostic')
    for side in SIDES:
        for key in common:eq(origins[side][key],origins['candidate'][key],'cross-side '+key)
        need(s['source_sha256'][side]==origins[side]['source_sha256']and s['native_binary_sha256'][side]==origins[side]['native_binary_sha256'],'summary fingerprints')
    commands=[decode(v)for v in(directory/'commands.jsonl').read_text().splitlines()if v.strip()];need(len(commands)==5+len(names)*18,'command count');eq(s['commands'],[v['argv']for v in commands]);eq(p['commands'],[v['argv']for v in commands[:5]])
    prep=(('original','reference','--write-reference','reference.npz'),('prior','validation-prior','--reference','reference.npz'),('candidate','validation-candidate','--reference','reference.npz'),('prior','reference-prior','--write-reference','prior-reference.npz'),('candidate','validation-exact-prior','--reference','prior-reference.npz'))
    for cmd,(side,label,flag,file)in zip(commands,prep):
        v=cmd['argv'];need(cmd['side']==side and cmd['label']==label and cmd['selected_case']is None and cmd['polars_threads']==t,'preparation command')
        need('--check-only'in v and'--case-filter'not in v and v[v.index(flag)+1].endswith(f'/threads-{t}/'+file)and(('--exact-reference'in v)==(label=='validation-exact-prior')),'preparation reference/exact CLI')
    workspace=None
    prep_map={label:(side,flag,file)for side,label,flag,file in prep}
    for cmd in commands:
        argv,side,label=cmd['argv'],cmd['side'],cmd['label'];options=cli_options(argv)
        need(side in SIDES and type(label)is str,'command side/label type')
        if cmd['selected_case']is None:need(label in prep_map,'unsafe preparation label')
        else:
            match=re.fullmatch(r'case-(\d{3})-(original|prior|candidate)-([1-6])',label)
            need(match is not None and match.group(2)==side and 1<=int(match.group(1))<=len(names)and cmd['selected_case']in names,'unsafe selected command label/case')
        root=Path(argv[0]).parents[2]
        if workspace is None:workspace=root
        need(root==workspace and root.is_absolute(),'mixed CLI workspace roots')
        need(argv[0]==str(root/(side+'-env')/'bin/python')and argv[1]==str(root/'candidate-source/scripts/migration_benchmark.py'),'interpreter/controller CLI')
        common_flags={'--source-root','--output','--label','--repeats'}|({'--diagnostic'}if t==1 else set())
        selected=cmd['selected_case']
        if selected is None:
            need(label in prep_map,'unknown preparation label');expected_side,flag,file=prep_map[label]
            expected_flags=common_flags|{'--check-only',flag}|({'--exact-reference'}if label=='validation-exact-prior'else set())
            need(side==expected_side and set(options)==expected_flags and options[flag]==str(root/f'benchmark-results/threads-{t}'/file),'preparation CLI inventory/reference')
        else:
            need(set(options)==common_flags|{'--reference','--case-filter'}and options['--case-filter']==selected,'selected CLI inventory')
            need(options['--reference']==str(root/f'benchmark-results/threads-{t}/reference.npz'),'selected golden CLI')
        need(options['--source-root']==str(root/(side+'-source'))and options['--output']==str(root/f'benchmark-results/threads-{t}'/(label+'.json'))and options['--label']==label and options['--repeats']=='51','source/output/mode CLI')
        report=js(directory/(label+'.json'))
        need(report['label']==label and report['correctness_reference']==options.get('--reference')and report['exact_reference']==bool(options.get('--exact-reference',False)),'actual report reference/exact flag differs from CLI')
    manifest=[];comps={a+'_vs_'+b:{}for a,b in PAIRS};all_faults={}
    for index,name in enumerate(names,1):
        runs={side:[]for side in SIDES};n,k=shape(name,api)
        for round_,order in enumerate(ORDERS,1):
            for side in order:
                label=f'case-{index:03d}-{side}-{round_}';manifest.append({'case':name,'side':side,'round':round_,'report':label+'.json'});r=js(directory/(label+'.json'));metadata(r,side,t,trust,whl,origins[side])
                need(r['label']==label and r['case_inventory']==r['case_filters']==[name]and set(r['results'])=={name},label+': selected-only case')
                need(r['checked_values']==n*k and not r['exact_reference'],label+': checked values');row=r['results'][name];vals=row['samples_ms']
                need(len(vals)==51 and all(type(v)in(int,float)and math.isfinite(v)and v>0 for v in vals),'sample vector');need(row['rows']==n and row['output_fields']==k,'output shape');eq(row['median_ms'],statistics.median(vals));eq(row['min_ms'],min(vals))
                cmd=commands[len(manifest)+4];v=cmd['argv'];need(cmd['label']==label and cmd['side']==side and cmd['selected_case']==name and cmd['polars_threads']==t,'command order/side')
                need(v.count('--case-filter')==1 and v[v.index('--case-filter')+1]==name and'--check-only'not in v and v[v.index('--reference')+1].endswith(f'/threads-{t}/reference.npz'),'selected/reference CLI');runs[side].append(row)
        for old,new in PAIRS:
            key=old+'_vs_'+new;value=comparison(runs[old],runs[new]);eq(s['comparisons'][key][name],value,f'{t}/{key}/{name}');comps[key][name]=value
        all_faults[name]={side:{key:faults(runs[side],key)for key in('minor_faults','major_faults')}for side in SIDES}
    eq(s['faults'],all_faults);eq(s['processes'],manifest);eq(s['order'],[r['report'].removesuffix('.json')for r in manifest]);need({f.name for f in directory.glob('case-*.json')}=={r['report']for r in manifest},'unexpected/missing child files')
    return {'threads':t,'cases':len(names),'children':len(manifest),'samples':len(manifest)*51,'runtime':{k:origins['candidate'][k]for k in common},'comparisons':comps,'golden_comparison':gcomp,'checked_values_per_full_validation':count}
def regression(results):
    rows=[]
    for t,data in results.items():
        for name,v in data['comparisons']['original_vs_candidate'].items():
            prior=data['comparisons']['original_vs_prior'][name];now=data['comparisons']['prior_vs_candidate'][name];change=v['candidate_median_ms']/v['baseline_median_ms']-1;lo,hi=v['ratio_envelope']
            category='consistent slower >5% on this runner'if hi<1/1.05 else'consistent small slower on this runner'if hi<1 else'slow median, process ranges overlap'if change>0 else'not slower by median'
            control=('control_cumsum/'if name.startswith('grouped_')else'control_cumsum_dense/')+name.split('/',1)[1];cv=data['comparisons']['original_vs_candidate'].get(control)
            rows.append({'threads':int(t),'case':name,'category':category,'original_median_ms':v['baseline_median_ms'],'delivered_median_ms':prior['candidate_median_ms'],'candidate_median_ms':v['candidate_median_ms'],'candidate_vs_C_percent':change*100,'original_over_candidate_paired_ratio':v['median_paired_ratio'],'original_over_candidate_envelope':[lo,hi],'delivered_over_candidate_paired_ratio':now['median_paired_ratio'],'delivered_over_candidate_envelope':now['ratio_envelope'],'original_process_medians_ms':v['baseline_process_medians_ms'],'candidate_process_medians_ms':v['candidate_process_medians_ms'],'matching_polars_control':control if cv else None,'control_ratio_envelope':cv['ratio_envelope']if cv else None})
    return sorted(rows,key=lambda r:(r['threads'],-r['candidate_vs_C_percent']))
def diagnostic(base,trust):
    path=base/'rust-cost-probe.log';text=path.read_text();expected={f'{f}/{n}/{mode}':10000 if mode=='setup_lookback'else{100:2000,10000:50,1000000:3}[n]for f in('EMA','ATR')for n in(100,10000,1000000)for mode in('setup_lookback','abstract_kernel','preallocated_kernel','complete_adapter')}
    expected.update({f'{f}/{mode}':10000 for f in('ADD','EMA','ATR','MACD','BBANDS','MACDEXT','SAREXT')for mode in('kwargs_pickle_old','kwargs_pickle_current')});expected.update({f'MACD/{n}/{mode}':2000 for n in(0,100,1000)for mode in('fields_vec','fields_array')});rows={}
    for name,it,raw in re.findall(r'COST_PROBE (\S+) iterations=(\d+) ns_per_call=(\[[^\n]*\])',text):
        need(name not in rows and name in expected and int(it)==expected[name],'diagnostic inventory/iterations');vals=decode(raw);need(len(vals)==9 and all(type(v)in(int,float)and math.isfinite(v)and v>0 for v in vals),'diagnostic samples');rows[name]={'iterations':int(it),'samples_ns':vals,'median_ns':statistics.median(vals)}
    need(set(rows)==set(expected)and len(rows)==44,'diagnostic 44 rows');counts=re.findall(r'COST_PROBE metadata_functions=(\d+)',text);names=re.findall(r'COST_PROBE metadata_names=(\[[^\n]*\])',text);need(len(counts)==len(names)==1,'diagnostic metadata');functions=decode(names[0]);need(len(functions)==int(counts[0])==len(set(functions))and{f['name'].upper()for f in trust['api']}<=set(functions),'metadata coverage');need('1 passed; 0 failed'in text,'diagnostic test failed')
    return {'sha256':sha(path),'rows':rows,'metadata_functions':len(functions),'limit':'Candidate-only ignored-test executable, 9 samples per stage in one process; nonadditive, not the release-wheel comparison or independent speedup proof.'}
def audit(artifact,trust):
    need(trust['run']==40914827113 and trust['pins']['candidate']=='56f6d5fb139031c20d86d7e818e7d267eb834295','final 56 target binding')
    base=artifact/'benchmark-results'if(artifact/'benchmark-results/summary.json').exists()else artifact;need((base/'summary.json').is_file(),'complete benchmark summary missing')
    whl=wheels(artifact,base,trust);corpus=check_corpus(base,trust);diag=diagnostic(base,trust);s=js(base/'summary.json');need(s['run_url']=='https://github.com/Yvictor/polars_ta_extension/actions/runs/40914827113'and s['thread_counts']==[1,4]and set(s['results'])=={'1','4'},'run/thread identity')
    results={}
    for t in(1,4):results[str(t)]=thread_audit(base,t,trust,whl);eq(s['results'][str(t)],js(base/f'threads-{t}/summary.json'),'top/thread summary')
    need(sum(v['children']for v in results.values())==5130 and sum(v['samples']for v in results.values())==261630,'full child/sample inventory')
    for key in('cpu','platform','python','polars','numpy','rust','profile'):eq(results['1']['runtime'][key],results['4']['runtime'][key],'same runner '+key)
    need(set(results['1']['runtime']['affinity'])<=set(results['4']['runtime']['affinity']),'affinity placement');rows=regression(results);stored=js(base/'regression-inventory.json');eq(stored['commits'],trust['pins']);eq(stored['rows'],rows,'all regression rows')
    return {'audit_pass':True,'recovery':trust['recovery'],'historical_only':'Final 56 comparison; integer-output initialization integration','run':trust['run'],'pins':trust['pins'],'children':5130,'raw_samples':261630,'wheels':whl,'corpus':corpus,'diagnostic':diag,'results':results,'regression_rows':rows,'limits':['Six rounds and correlated inner samples; descriptive ranges are not confidence intervals or multiple-comparison significance.','Original/prior query goldens and child self-check reports are retained; candidate query arrays are not. Separate full candidate corpus is replayed independently.','Immutable local Git objects verify source fingerprints; external dependency archives and separately linked consumer Rust rlibs are not archived. Wheel native libraries and Python sources are directly hashed.','Profile evidence comes from workflow/source, release logs and self-reports, not a complete captured process environment or assembly audit.','No pooling across thread counts/runners. Fault counters are process-wide, not allocator-only.','Full NPZ corpus metadata has no commit/native ELF hash. Corpus-to-wheel binding relies on immutable workflow/CI execution provenance, not a per-capture ELF identity field.','Original C comparison uses its historical tolerance policy; any C-to-native signed-zero differences are explicitly counted, not silently claimed identical. Prior-to-candidate signed zeros remain strict.']}
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('artifact',type=Path);p.add_argument('--trust',type=Path,default=Path(__file__).with_name('trusted.json'));p.add_argument('--output',type=Path,required=True);args=p.parse_args();result=audit(args.artifact.resolve(),js(args.trust));args.output.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:result[k]for k in('audit_pass','recovery','historical_only','run','pins','children','raw_samples','corpus','limits')},indent=2))
