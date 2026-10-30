"""Independent SAREXT physical-input/four-golden artifact replay; never executes products/controllers."""
import argparse,copy,hashlib,importlib.util,itertools,json,math,re,statistics,struct,zipfile
from pathlib import Path
import numpy as np
import inputs as physical
HERE=Path(__file__).parent
CORE_SHA='b8c0b004daac5d920835c7a316cf97919cc3a13633eeecd860fdd02ab669cba9'
need=lambda ok,msg:None if ok else (_ for _ in ()).throw(ValueError(msg))
need(hashlib.sha256((HERE/'shared_core.py').read_bytes()).hexdigest()==CORE_SHA,'approved independent core hash')
spec=importlib.util.spec_from_file_location('independent_shared',HERE/'shared_core.py');core=importlib.util.module_from_spec(spec);spec.loader.exec_module(core)
js,sha=core.js,core.sha
# Same-run JSON/derived values require exact equality; tolerance belongs only in arrays().
def eq(a,b,where='value'):
 if isinstance(b,dict):
  need(isinstance(a,dict)and set(a)==set(b),where+': keys')
  for k in b:eq(a[k],b[k],where+'.'+k)
 elif isinstance(b,list):
  need(isinstance(a,list)and len(a)==len(b),where+': length')
  for i,(x,y)in enumerate(zip(a,b)):eq(x,y,where+'['+str(i)+']')
 elif isinstance(b,float):need(type(a)in(int,float)and a==b,where+': exact same-run number')
 else:need(type(a)is type(b)and a==b,where+': value/type')
def arrays(old,new,old_null,new_null,**kwargs):
 strict_zero=kwargs.pop('strict_zero',False)
 if strict_zero:need(np.array_equal(old[~old_null]==0,new[~new_null]==0),kwargs.get('where','arrays')+': zero positions')
 result=core.arrays(old,new,old_null,new_null,**kwargs)
 # Finite C tolerance does not waive the sign when BOTH outputs are zero.
 # Zero versus tiny finite cancellation continues to use the declared policy.
 need(result['zero_sign_differences']==0,kwargs.get('where','arrays')+': signed-zero differences')
 return result

SIDES=('original','prior','candidate','alternative')
ORDERS=(('original','prior','candidate','alternative'),('prior','alternative','original','candidate'),('alternative','candidate','prior','original'),('candidate','original','alternative','prior'))
PAIRS=tuple((a,b)for i,a in enumerate(SIDES)for b in SIDES[i+1:])

def name_shape(name):
 fam,shape=name.split('/');inter=shape.endswith('_interleaved');parts=shape.removesuffix('_interleaved').split('x');groups,bars=map(int,parts)if len(parts)==2 else(1,int(parts[0]));return fam,groups,bars,inter

def golden(path,names,expected):
 hashes={};keys=set();total=0;cov={}
 with np.load(path,allow_pickle=False)as f:
  for name in names:
   family,n,g,b,inter,grouped,kind=physical.shape(name);column='control'if family.startswith('control')else family;schema="Schema({'"+column+"': Float64})";k=name+'_0';keys.update((name+'_schema',k,k+'_null'));arr=f[k];null=f[k+'_null'];need(f[name+'_schema'].shape==()and str(f[name+'_schema'])==schema,'fixed scalar schema');need(arr.shape==null.shape==(n,)and arr.dtype==np.dtype('float64')and null.dtype==np.dtype(bool)and not null.any(),'golden dtype/length/nulls')
   if not family.startswith('control'):
    ordered=arr.reshape(b,g).T if inter else arr.reshape(g if grouped else 1,b if grouped else n);need(np.isnan(ordered[:,:1]).all()and np.isfinite(ordered[:,1:]).all(),'every-group warmup/finite range')
   if expected[name]is not None:arrays(expected[name],arr,np.zeros(n,bool),null,exact=True,strict_zero=True,where='independent physical-input cumsum '+name)
   cov[name]=physical.coverage(name,arr)
   h=hashlib.sha256(schema.encode());h.update(arr.tobytes());h.update(null.tobytes());hashes[name]=h.hexdigest();total+=n
  need(set(f.files)==keys,'complete golden array inventory')
 return hashes,total,cov

def compare_goldens(old,new,names,exact):
 metrics={};maximum=0.
 with np.load(old,allow_pickle=False)as a,np.load(new,allow_pickle=False)as b:
  for name in names:
   need(str(a[name+'_schema'])==str(b[name+'_schema']),'golden schema');k=name+'_0';r=arrays(a[k],b[k],a[k+'_null'],b[k+'_null'],exact=exact,strict_zero=True,where='retained own-arm golden '+name);maximum=max(maximum,r.pop('max_abs'))
   for key,v in r.items():metrics[key]=metrics.get(key,0)+v
 return {**metrics,'max_abs':maximum}

def wheels(root,base,trust,p):
 out={};ws=Path(p['flags']['environment']['CARGO_TARGET_DIR']).parent;proofs=[core.decode(line)for line in(base/'product-compile-proof.jsonl').read_text().splitlines()if line];need(len(proofs)==4,'four actual product compile proofs');proofmap={row['product_source']:row for row in proofs};need(len(proofmap)==4,'distinct actual compile sources')
 for side in SIDES:
  build=p['builds'][side];eq(build['source'],trust['source_record'][side],'immutable source '+side);ident=build['identity'];need(ident['python']=='3.12.15'and ident['polars']=='1.44.2'and ident['numpy']=='2.5.3'and ident['package']=='0.2.1'and(ident['talib'].startswith('0.8.1 ')if side=='original'else ident['talib']=='0.8.3 (native Rust; polars-talib compatibility)'),'runtime identity')
  paths=list((root/'wheels'/side).glob('*.whl'));need(len(paths)==1,'one wheel perarm');path=paths[0];need(sha(path)==build['wheel']['sha256'],'wheel digest')
  with zipfile.ZipFile(path)as z:
   names=z.namelist();need(len(names)==len(set(names)),'wheel duplicate');py={n:hashlib.sha256(z.read(n)).hexdigest()for n in names if n.startswith('polars_talib/')and n.endswith('.py')};eq(py,trust['wheel_python_sha256'][side],'packaged Python');so=[n for n in names if Path(n).name.startswith('_polars_talib')and n.endswith('.abi3.so')];need(len(so)==1,'one ABI3 ELF');b=z.read(so[0]);core.elf_header(b);digest=hashlib.sha256(b).hexdigest();need(list(ident['native_files'].values())==[digest]and list(build['retained_native_files'].values())==[digest],'measured ELF hash');retained=base/'actual-native'/side/Path(so[0]).name;need(sha(retained)==digest,'retained ELF');out[side]={'wheel_sha256':sha(path),'native_sha256':digest}
  deps=(base/(side+'-dependencies.txt')).read_text().lower()
  for pin in('maturin==1.15.0','numpy==2.5.3','polars==1.44.2','cmake==4.4.4'):need(pin in deps,'dependency '+pin)
  logpath=base/(side+'-build.log');log=logpath.read_text();source=str(ws/'sources'/side);paths=re.findall(r'^\s*Compiling polars_talib v0\.2\.1 \((.+)\)\s*$',log,re.M);need(paths and all(x==source for x in paths),'compile exact immutable source path');proof=proofmap.get(source);need(proof is not None and proof['log']==str(ws/'sarext-results'/(side+'-build.log'))and proof['log_sha256']==sha(logpath)and proof['product_compile_lines']==len(paths),'actual product compile proof binding');need('release'in log and'optimized'in log and'target-cpu=native'not in log and'-march=native'not in log,'actual release build')
 return out

def fingerprints(base,side):
 folder=base/'product-fingerprints'/side;need(folder.is_dir(),'retained Cargo snapshot');nodes={};roots=[]
 for meta in folder.glob('*/lib-*.json'):
  rawpath=meta.with_suffix('');need(rawpath.is_file(),'Cargo raw fingerprint');raw=rawpath.read_text().strip();need(re.fullmatch('[0-9a-f]{16}',raw)is not None,'Cargo raw16hex');fp=int.from_bytes(bytes.fromhex(raw),'little');r=js(meta);deps={}
  for edge in r['deps']:need(len(edge)==4 and edge[1]not in deps and type(edge[3])is int,'Cargo dependency metadata');deps[edge[1]]=edge[3]
  name=meta.stem.removeprefix('lib-');row={'name':name,'metadata_sha256':sha(meta),'raw_sha256':sha(rawpath),'fingerprint':fp,'deps':deps,'rustflags':r['rustflags'],'profile':r['profile']};nodes.setdefault((name,fp),[]).append(row)
  if name=='_polars_talib':roots.append(row)
 wanted=('talib','talib_sys','serde','polars','jemallocator','pyo3_polars')if side=='original'else('ta_lib','serde','polars','jemallocator','pyo3_polars');selected=[]
 for root in roots:
  if not set(wanted)<=set(root['deps']):continue
  need(root['rustflags']==[],'normal root portable flags');edges={}
  for name in wanted:
   found=nodes.get((name,root['deps'][name]),[]);need(found and len({r['metadata_sha256']for r in found})==1,'Cargo actual root edge '+name);need(all(r['rustflags']==[]for r in found),'dependency flags');edges[name]=found[0]
  selected.append({'root':root,'edges':edges})
 need(selected,'normal product family Cargo graph absent')
 if side=='alternative':need(any('multiversion'in row['root']['deps']for row in selected),'B explicit public multiversion dependency')
 return {'matching_normal_roots':selected,'total_root_count':len(roots),'limit':'Shared target snapshots may retain prior roots. These metadata graphs are not independently mapped to a unique measured ELF or archived Rust rlibs. Actual source/ELF binding relies on immutable workflow, exact compile source path and installed/wheel bytes.'}

def metadata(row,side,t,trust,p,whl):
 need(row['commit']==trust['pins'][side]and row['source_sha256']==trust['source_record'][side]['source_sha256']and row['native_binary_sha256']==whl[side]['native_sha256'],'child source/ELF');ident=p['builds'][side]['identity']
 for k in('python','platform','polars','numpy','package','talib'):eq(row[k],ident[k],'installed identity '+k)
 need(all(type(row[k])is int for k in('threads','repeats','warmups'))and isinstance(row['affinity'],list)and all(type(x)is int and x>=0 for x in row['affinity']),'integer nonbool runtime metadata');need(row['threads']==t and row['repeats']==31 and row['warmups']==5 and row['diagnostic']is False and row['integer_reference_exact']is True and len(row['affinity'])==len(set(row['affinity']))==t,'thread/repeat/affinity');need(row['rust']==p['flags']['rustc'].splitlines()[0],'Rust version');need(row['profile']==core.PROFILE and 'Linux'in row['platform']and'x86_64'in row['platform'],'fixed portable profile/host')


def all_corpus(base,trust):
 from collections import Counter
 directory=base/'corpus';paths={s:directory/(s+'.npz')for s in SIDES};data={s:np.load(p,allow_pickle=False)for s,p in paths.items()};meta={s:core.decode(str(d['metadata']))for s,d in data.items()};expected=core.corpus_keys(trust['api']);api={f['name']:f for f in trust['api']};out={}
 try:
  for side,m in meta.items():
   need(set(m['cases'])==expected and set(m['api'])==set(m['api_call_contract'])==set(api),'complete corpus/API');need(m['polars']=='1.44.2'and m['numpy']=='2.5.3','corpus runtime');need(m['talib'].startswith('0.8.1')if side=='original'else m['talib']=='0.8.3 (native Rust; polars-talib compatibility)','corpus kernel');keys={'metadata'}
   for case_index,(name,row) in enumerate(m['cases'].items()):
    if 'error'in row:need(set(row)=={'error'}and isinstance(row['error'],str),'corpus error');continue
    need(set(row)=={'schema','height','fields'}and type(row['height'])is int and row['height']>=0 and row['fields']==[f'c{case_index}_{j}'for j in range(len(api[name.split('/')[0]]['outputs']))],'corpus field inventory/index/type')
    for f in row['fields']:keys.update((f,f+'_null'));need(data[side][f].shape==(row['height'],),'corpus length')
   need(set(data[side].files)==keys,'corpus orphan arrays')
  for before,after in PAIRS:
   a,b=meta[before],meta[after];exact=before!='original';need(a['api_call_contract']==b['api_call_contract'],'public call contracts');metrics=Counter();errors=Counter();maximum=0.
   for name,row in a['cases'].items():
    other=b['cases'][name]
    if 'error'in row or 'error'in other:need(row==other,'corpus errors differ');errors[row['error']]+=1;continue
    need(row['schema']==other['schema']and row['height']==other['height']and len(row['fields'])==len(other['fields']),'corpus schema/field order')
    for x,y in zip(row['fields'],other['fields']):
     r=arrays(data[before][x],data[after][y],data[before][x+'_null'],data[after][y+'_null'],exact=exact,tiny='/tiny'in name,where=name);maximum=max(maximum,r.pop('max_abs'));metrics.update(r)
   label=before+'-vs-'+after+('-exact'if exact else'');report=js(directory/(label+'.json'));values={'cases':len(expected),'checked_values':metrics['checked'],'require_exact':exact,'rtol':0. if exact else 1e-10,'atol':0. if exact else 1e-10,'api_signatures_match':a['api']==b['api'],'api_call_contract_match':True,'annotation_changed_functions':[n for n in a['api']if a['api'][n]!=b['api'].get(n)],'fields_with_bit_differences':metrics['different'],'max_absolute_difference':maximum,'failures':[],'baseline_sha256':sha(paths[before]),'candidate_sha256':sha(paths[after])}
   for key,v in values.items():eq(report[key],v,'all four corpus report '+key)
   need(len(expected)==10624 and metrics['checked']==2167654,'full corpus independent totals');out[label]={'cases':len(expected),'exact':exact,**dict(metrics),'max_abs':maximum,'errors':dict(errors)}
 finally:
  for d in data.values():d.close()
 return out

def cli_record(ws,t,side,label,names,extra,selected=None):
 wanted=[str(ws/'envs'/side/'bin/python'),str(ws/'control-source/scripts/sarext_typed_query.py'),'--source-root',str(ws/'sources'/side),'--output',str(ws/'sarext-results'/f'threads-{t}'/(label+'.json')),'--label',label,'--repeats','31',*extra]
 for name in([selected]if selected else names):wanted+=['--case-filter',name]
 return {'label':label,'side':side,'selected_case':selected,'argv':wanted,'polars_threads':t}

def ledger(names):
 return [{'case':name,'side':side,'round':rnd,'report':f'case-{index:03d}-{side}-{rnd}.json'}for index,name in enumerate(names,1)for rnd,order in enumerate(ORDERS*3,1)for side in order]

def timing(row,name):
 family,n,g,b,inter,grouped,kind=physical.shape(name)
 need(row['case_inventory']==row['case_filters']==[name]and type(row['checked_values'])is int and row['checked_values']==n and row['exact_reference']is True and row['final_output_checked']is True and set(row['results'])=={name},'selected exact pre/post query')
 entry=row['results'][name];a=entry['samples_ms'];need(type(entry['rows'])is type(entry['output_fields'])is int and all(type(entry[k])in(int,float)and math.isfinite(entry[k])and entry[k]>0 for k in('median_ms','min_ms')),'typed finite timing/shape');need(len(a)==31 and all(type(x)in(int,float)and math.isfinite(x)and x>0 for x in a),'raw31samples');need(entry['median_ms']==statistics.median(a)and entry['min_ms']==min(a)and entry['rows']==n and entry['output_fields']==1,'recomputed timing statistics/shape')
 for k in('minor_faults','major_faults'):need(len(entry[k])==31 and all(type(x)is int and x>=0 for x in entry[k]),'raw fault samples')
 return entry

def setting(base,t,trust,p,whl,expected,fixture,records):
 folder=base/f'threads-{t}';s=js(folder/'summary.json');prep=js(folder/'prepared-validation.json');names=trust['case_manifest']['cases'];need(len(names)==14,'14queries');eq(s['case_inventory'],names,'summary inventory');eq(prep['inventory'],names,'prepared inventory');need(type(s['threads'])is type(prep['threads'])is int and s['threads']==prep['threads']==t and s['rounds']==12 and s['repeats']==31 and s['warmups']==5,'fixed protocol');commands=[core.decode(x)for x in(folder/'commands.jsonl').read_text().splitlines()if x];need(len(commands)==7+14*48,'seven pretime plus672 selected commands');ws=Path(commands[0]['argv'][1]).parents[2];files={'original':'reference.npz',**{x:x+'-reference.npz'for x in SIDES[1:]}};hashes={};cov={}
 for side,file in files.items():
  key='reference_sha256'if side=='original'else side+'_reference_sha256'
  if side in('original','prior'):need(s[key]==prep[key]==sha(folder/file),'original/prior golden hash')
  else:need(prep['arm_reference_sha256'][side]==sha(folder/file),'A/B golden hash')
  hashes[side],count,cov[side]=golden(folder/file,names,expected);need(count==12400000,'all query values')
 goldcomp={a+'_vs_'+b:compare_goldens(folder/files[a],folder/files[b],names,exact=a!='original')for a,b in PAIRS};origins=prep['source_validations'];need(set(origins)==set(SIDES),'four pretime arms')
 for side,row in origins.items():
  metadata(row,side,t,trust,p,whl);eq(row['case_inventory'],names,'pretime inventory');eq(row['case_filters'],names,'pretime filters');need(not row['results']and type(row['checked_values'])is int and row['checked_values']==(0 if side=='original'else count),'pretime no timer/full checks');eq(row['fixture_sha256'],fixture,'physical IPC digest');eq(row['output_sha256'],hashes[side],'own-arm golden digest');eq(row['fixture_coverage'],cov[side],'independent group output coverage');eq(row['input_snapshots'],records if side=='original'else{},'preflight-only IPC snapshots');label='reference'if side=='original'else'validation-'+side;eq(js(folder/(label+'.json')),row,'raw validation report');need(row['correctness_reference']==(None if side=='original'else str(ws/'sarext-results'/f'threads-{t}'/'reference.npz'))and row['exact_reference']is False,'C preflight reference')
 for key in('python','platform','cpu','polars','numpy','rust','profile','threads','affinity'):need(len({json.dumps(v[key])for v in origins.values()})==1,'same runtime '+key)
 for key in('cpu','platform','python','polars','numpy','rust','threads','affinity','repeats','warmups','diagnostic','checked_values','case_filters'):eq(s[key],origins['candidate'][key],'summary actual metadata '+key)
 eq(s['commits'],trust['pins'],'source pins');eq(s['source_sha256'],{side:trust['source_record'][side]['source_sha256']for side in SIDES},'source fingerprints');eq(s['native_binary_sha256'],{side:whl[side]['native_sha256']for side in SIDES},'summary ELF');need(s['process_isolation']=='one case per fresh process'and type(s['exact_prior_validation'])is int and s['exact_prior_validation']==count,'summary exact validation')
 exacts=prep['exact_validations'];need(set(exacts)=={'candidate','alternative'},'both exact native validations');eq(prep['exact_validation'],exacts['candidate'],'candidate exact alias')
 for side,row in exacts.items():
  metadata(row,side,t,trust,p,whl);eq(row,js(folder/('validation-exact-prior-'+side+'.json')),'raw exact validation');eq(row['output_sha256'],hashes[side],'exact own-arm digest');eq(row['fixture_sha256'],fixture,'exact inputs');eq(row['fixture_coverage'],cov[side],'exact group coverage');eq(row['case_inventory'],names,'exact inventory');eq(row['case_filters'],names,'exact selector');need(row['exact_reference']is True and row['checked_values']==count and not row['results']and row['correctness_reference']==str(ws/'sarext-results'/f'threads-{t}'/'prior-reference.npz'),'native exact preflight')
  eq(row['input_snapshots'],{},'exact no IPC')
 prior=js(folder/'reference-prior.json');metadata(prior,'prior',t,trust,p,whl);eq(prior['output_sha256'],hashes['prior'],'prior retained own-arm digest');eq(prior['fixture_sha256'],fixture,'prior input');need(prior['checked_values']==0 and prior['correctness_reference']is None and not prior['results'],'prior capture-only')
 prepares=[('original','reference',['--check-only','--write-reference',str(ws/'sarext-results'/f'threads-{t}'/'reference.npz'),'--save-inputs',str(ws/'sarext-results/inputs')])]
 prepares.extend((side,'validation-'+side,['--check-only','--reference',str(ws/'sarext-results'/f'threads-{t}'/'reference.npz')])for side in('prior','alternative','candidate'))
 prepares.append(('prior','reference-prior',['--check-only','--write-reference',str(ws/'sarext-results'/f'threads-{t}'/'prior-reference.npz')]))
 prepares.extend((side,'validation-exact-prior-'+side,['--check-only','--reference',str(ws/'sarext-results'/f'threads-{t}'/'prior-reference.npz'),'--exact-reference','--write-reference',str(ws/'sarext-results'/f'threads-{t}'/(side+'-reference.npz'))])for side in('alternative','candidate'))
 for cmd,(side,label,extra)in zip(commands,prepares):eq(cmd,cli_record(ws,t,side,label,names,extra),'exact pretime CLI')
 eq(prep['commands'],[c['argv']for c in commands[:7]],'prepared CLI');eq(s['commands'],[c['argv']for c in commands],'all CLI')
 manifest=ledger(names);comps={a+'_vs_'+b:{}for a,b in PAIRS};faults={};runs={name:{side:[]for side in SIDES}for name in names}
 for index,item in enumerate(manifest,7):
  name,side=item['case'],item['side'];label=item['report'][:-5];row=js(folder/item['report']);metadata(row,side,t,trust,p,whl);need(row['label']==label,'selected label');entry=timing(row,name)
  eq(row['fixture_sha256'],{name:fixture[name]},'selected IPC');eq(row['output_sha256'],{name:hashes[side][name]},'selected own-arm golden');eq(row['fixture_coverage'],{name:cov[side][name]},'selected group coverage');eq(row['input_snapshots'],{},'no timed IPC');eq(core.decode((folder/(label+'.stdout.log')).read_text()),{name:round(entry['median_ms'],4)},'stdout median');need((folder/(label+'.stderr.log')).is_file(),'stderr retained')
  for k in('cpu','platform','python','polars','numpy','rust','threads','affinity','profile'):eq(row[k],origins[side][k],'child runtime '+k)
  reference=str(ws/'sarext-results'/f'threads-{t}'/files[side]);need(row['correctness_reference']==reference,'selected own-arm reference');eq(commands[index],cli_record(ws,t,side,label,names,['--reference',reference,'--exact-reference'],name),'selected exact CLI');runs[name][side].append(entry)
 for name in names:
  for a,b in PAIRS:comps[a+'_vs_'+b][name]=core.comparison(runs[name][a],runs[name][b])
  faults[name]={}
  for side in SIDES:
   faults[name][side]={}
   for k in('minor_faults','major_faults'):
    v=[r[k]for r in runs[name][side]];med=[statistics.median(x)for x in v];pool=[x for x in v for x in x];faults[name][side][k]={'median':statistics.median(med),'process_medians':med,'p10_p90':[core.pct(pool,p)for p in(.1,.9)]}
 eq(s['comparisons'],comps,'all six recomputed comparisons');eq(s['faults'],faults,'fault summaries');eq(s['processes'],manifest,'manifest');eq(s['order'],[x['report'][:-5]for x in manifest],'order');need({p.name for p in folder.glob('case-*.json')}=={x['report']for x in manifest},'no missing/orphan selected children')
 return {'threads':t,'cases':14,'children':len(manifest),'samples':len(manifest)*31,'runtime':{k:origins['candidate'][k]for k in('cpu','platform','python','polars','numpy','rust','profile','affinity')},'comparisons':comps,'golden_comparisons':goldcomp,'fixture_coverage':cov}

def words_diagnostics(old,new):
 a=np.load(old,allow_pickle=False);b=np.load(new,allow_pickle=False);ma=core.decode(str(a['metadata']));mb=core.decode(str(b['metadata']));rows=[];checked=0
 try:
  for name,entry in ma['cases'].items():
   other=mb['cases'][name]
   if 'error'in entry or'error'in other:continue
   need(len(entry['fields'])==len(other['fields']),'word field count')
   for left,right in zip(entry['fields'],other['fields']):
    x=a[left];y=b[right];mask=a[left+'_null'];need(x.shape==y.shape and x.dtype==y.dtype and np.array_equal(mask,b[right+'_null']),'word shape/mask');x=x[~mask];y=y[~mask];checked+=len(x)
    for pred in(np.isnan,np.isposinf,np.isneginf):need(np.array_equal(pred(x),pred(y)),'word NaN/infinity positions/sign')
    xp=x.view('u'+str(x.dtype.itemsize));yp=y.view('u'+str(y.dtype.itemsize));delta=xp!=yp;finite=np.isfinite(x)&np.isfinite(y);nan=np.isnan(x)&np.isnan(y);position=(x==0)!=(y==0);sign=(x==0)&(y==0)&(np.signbit(x)!=np.signbit(y));nf=int((delta&finite).sum());nn=int((delta&nan).sum())
    if nf or nn:
     indices=np.flatnonzero(position|sign)[:8];rows.append({'case':name,'field':left,'finite_word_differences':nf,'nan_word_differences':nn,'zero_position_differences':int(position.sum()),'both_zero_sign_differences':int(sign.sum()),'maximum_absolute_finite_difference':float(np.max(np.abs(x[finite]-y[finite])))if finite.any()else 0.,'reference_scale':float(np.max(np.abs(x[np.isfinite(x)])))if np.isfinite(x).any()else 0.,'zero_examples':[{'valid_index':int(i),'before':float(x[i]),'after':float(y[i]),'before_word':hex(int(xp[i])),'after_word':hex(int(yp[i]))}for i in indices]})
 finally:a.close();b.close()
 return {'checked_values':checked,'null_nan_inf_contract':'strict','global_C_zero_policy':'diagnostic; inherited finite/tiny-lane tolerance unchanged. Exact zero/sign requirements apply to timed queries/new C-target regressions; native full-corpus exact comparison remains mandatory.','finite_numeric_policy':'separately gated by existing declared C tolerance or exact native comparison','nan_payload_policy':'diagnostic only; no payload/sign gate','finite_word_differences':sum(x['finite_word_differences']for x in rows),'zero_position_differences':sum(x['zero_position_differences']for x in rows),'both_zero_sign_differences':sum(x['both_zero_sign_differences']for x in rows),'nan_word_differences':sum(x['nan_word_differences']for x in rows),'changed_fields':rows}

ZERO_FIXTURES=(('short_zero',[0.,-1.,-2.],[-1.,-2.,-3.],{},1),('short_cancellation',[-1.,-1.,-1.,-1.],[-2.,-2.,-2.,-2.],{'startvalue':-2.,'accelerationinitshort':.5,'accelerationshort':0.,'accelerationmaxshort':.5},2))
def zero_metadata(fixture,interleaved):
 name,high,low,params,target=fixture;g=3 if interleaved else 1;b=len(high);order=np.arange(g*b).reshape(g,b).T.ravel()if interleaved else np.arange(g*b);symbol=np.repeat(np.arange(g),b)[order];within=np.tile(np.arange(b),g)[order];hi=np.tile(high,g)[order];lo=np.tile(low,g)[order]
 return {'params':params,'schema':'Float64','nulls':[False]*(g*b),'nan':(within==0).tolist(),'target_zero_positions':np.flatnonzero(within==target).tolist(),'groups':g,'high_words':[int(x)for x in hi.view(np.uint64)],'low_words':[int(x)for x in lo.view(np.uint64)],'symbol':symbol.tolist(),'within':within.tolist(),'eager_lazy_raw_identity':True}

def zero_captures(rows,trust=None,p=None):
 need(set(rows)==set(SIDES),'four zero captures');names={n+'/'+layout for n,*_ in ZERO_FIXTURES for layout in('dense','interleaved')};result={}
 for side,row in rows.items():
  need(set(row['cases'])==names,'zero case inventory')
  if trust is not None:eq(row['source'],trust['source_record'][side],'zero source');eq(row['identity'],p['builds'][side]['identity'],'zero wheel/runtime')
 for fixture in ZERO_FIXTURES:
  for inter in(False,True):
   name=fixture[0]+('/interleaved'if inter else'/dense');meta=zero_metadata(fixture,inter);reference=rows['original']['cases'][name];need(set(reference)==set(meta)|{'words'},'zero capture fields')
   for k,v in meta.items():eq(reference[k],v,'independent zero metadata '+k)
   words=reference['words'];need(len(words)==len(meta['nulls'])and all(type(x)is int and 0<=x<2**64 for x in words),'uint64 zero words');numeric=np.array(words,np.uint64).view(np.float64);need(np.array_equal(np.isnan(numeric),meta['nan'])and np.isfinite(numeric[~np.array(meta['nan'])]).all(),'zero NaN masks/finite written values');need(all(words[i]==0 for i in meta['target_zero_positions']),'original C positive zero boundary')
   for side in SIDES[1:]:
    got=rows[side]['cases'][name];need(set(got)==set(reference),'zero record inventory')
    for k,v in meta.items():eq(got[k],v,'zero metadata '+side+'/'+k)
    wanted=list(words)
    if side=='prior':
     for i in meta['target_zero_positions']:wanted[i]=0x8000000000000000
    eq(got['words'],wanted,'only the declared untimed C-target zero boundary '+side)
   result[name]={'C_target_words':words,'known56_negative_zero_positions':meta['target_zero_positions'],'A_B_C_raw_identity':True,'timed_waiver':False}
 return result

def cold_proof(base):
 name='sarext_legacy::tests::cold_parallel_dispatch_matches_portable_scalar_without_shared_mutable_inputs';log=base/'B-cold-dispatch-first.log';inventory=base/'B-test-inventory.log';text=log.read_text();need(name+': test'in inventory.read_text().splitlines(),'cold exact test inventory');need(re.search(r'^test '+re.escape(name)+r' \.\.\. ok\s*$',text,re.M)is not None and re.search(r'\brunning 1 test\b',text)is not None and re.search(r'test result: ok\. 1 passed; 0 failed; 0 ignored;',text)is not None,'cold fresh single actual test')
 return {'test':name,'log_sha256':sha(log),'inventory_sha256':sha(inventory),'scope':'Fresh cargo test process, exact filter alone before full suite. Local ARM portable tests do not establish x86 resolver behavior.'}

def remap(path,base,p):
 ws=Path(p['flags']['environment']['CARGO_TARGET_DIR']).parent;path=Path(path);need(path.is_absolute()and path.is_relative_to(ws/'sarext-results'),'retained diagnostic path outside source-bound artifact');rel=path.relative_to(ws/'sarext-results');need('..'not in rel.parts,'unsafe diagnostic path');q=base/rel;need(q.is_file()and not q.is_symlink()and q.resolve().is_relative_to(base.resolve()),'missing/unsafe diagnostic');return q

def elf_lines(text,relocs,symbols):
 targets=set()
 for line in symbols.splitlines():
  cells=line.split()
  if len(cells)==3 and cells[1]in('t','T')and cells[2]=='fma'and re.fullmatch('[0-9a-fA-F]+',cells[0]):targets.add(int(cells[0],16))
 slots=set()
 for line in relocs.splitlines():
  cells=line.split()
  if len(cells)<4 or not re.fullmatch('[0-9a-fA-F]+',cells[0]):continue
  if cells[2]=='R_X86_64_RELATIVE':
   if len(cells)==4 and re.fullmatch('[0-9a-fA-F]+',cells[3])and int(cells[3],16)in targets:slots.add(int(cells[0],16))
  elif len(cells)>=5 and re.match(r'^fma(?:@|$)',cells[4]):slots.add(int(cells[0],16))
 inline=[];calls=[];transfers=[];fma=[]
 for line in text.splitlines():
  if re.search(r'^\s*[0-9a-f]+:\s+vf(?:madd|msub|nmadd|nmsub)',line):inline.append(line)
  if re.search(r'^\s*[0-9a-f]+:\s+call\w*\s',line):calls.append(line)
  if not re.search(r'^\s*[0-9a-f]+:\s+(?:call\w*|j\w*)\s',line):continue
  transfers.append(line);m=re.search(r'#\s*(?:0x)?([0-9a-f]+)',line)
  if re.search(r'(?<![A-Za-z_])fma(?:@|\b)',line)or(m and int(m[1],16)in slots):fma.append(line)
 return {'inline_fma_instruction_lines':inline,'all_call_lines':calls,'all_control_transfer_lines':transfers,'libm_fma_control_transfer_lines':fma,'named_libm_fma_call_lines':[x for x in fma if x in calls]}

def function_header(text,symbol,symbols):
 headers=re.findall(r'^\s*([0-9a-fA-F]+)\s+<([^>]+)>:\s*$',text,re.M)
 need(len(headers)==1 and headers[0][1]==symbol,'actual single disassembly symbol header')
 defined=[]
 for line in symbols.splitlines():
  cells=line.split()
  if len(cells)==3 and cells[1]in('t','T')and re.fullmatch('[0-9a-fA-F]+',cells[0]):defined.append((int(cells[0],16),cells[2]))
 need((int(headers[0][0],16),symbol)in defined,'exact defined actual text symbol/address')

def elf_roles(functions):
 tag='dispatched_scalar_avx_fma_sse_sse2_sse3_sse41_ssse3_version'
 categories={'fma_clone':[s for s in functions if tag in s],'portable_dispatch_wrapper':[s for s in functions if re.search(r'17dispatched_scalar17h[0-9a-f]+E(?:\..*)?$',s)],'feature_resolver':[s for s in functions if'dispatched_scalar14__detect_index8__detect'in s]}
 need(all(len(v)==1 for v in categories.values()),'exactly one actual clone/wrapper/resolver symbol')
 result={key:values[0]for key,values in categories.items()};need(len(set(result.values()))==3,'distinct actual ELF symbol roles');return result

def elf_proof(base,p,trust,whl):
 r=js(base/'product-elf-gate.json');need(r['passed']is True and not r.get('errors')and r['build_provenance_sha256']==sha(base/'build-provenance.json')and r['inspector_sha256']==trust['controller_sha256']['scripts/sarext_typed_elf.py']and set(r['products'])==set(SIDES),'exact successful actual ELF source-bound proof')
 for side,row in r['products'].items():
  eq({row['elf']['path']:row['elf']['sha256']},p['builds'][side]['retained_native_files'],'ELF measured binding');need(row['elf']['sha256']==whl[side]['native_sha256']and sha(remap(row['elf']['path'],base,p))==row['elf']['sha256'],'actual product bytes')
  for path,h in row['files'].items():need(sha(remap(path,base,p))==h,'actual ELF diagnostic hash')
  relocs=remap(next(path for path in row['files']if path.endswith('/relocations.txt')),base,p).read_text();symbols=remap(next(path for path in row['files']if path.endswith('/symbols.txt')),base,p).read_text()
  for symbol,fn in row['functions'].items():
   need(fn['file']in row['files'],'disassembly hash inventory');text=remap(fn['file'],base,p).read_text();function_header(text,symbol,symbols);replayed=elf_lines(text,relocs,symbols)
   for k,v in replayed.items():eq(fn[k],v,'independent actual ELF classification '+symbol+'/'+k)
 b=r['products']['alternative'];roles=elf_roles(b['functions']);eq(b['role_symbols'],roles,'independently derived actual B symbol roles');clone=b['functions'][roles['fma_clone']];portable=b['functions'][roles['portable_dispatch_wrapper']];need(len(clone['inline_fma_instruction_lines'])==4 and not clone['libm_fma_control_transfer_lines']and portable['libm_fma_control_transfer_lines'],'B inline FMA and actual portable fallback')
 return r

def audit(root,trust):
 need(trust['pins']=={'original':'b2bbc26d41ec80823c8bffb0cc436a97f29911cc','prior':'56f6d5fb139031c20d86d7e818e7d267eb834295','candidate':'8a4fc7feacc45b28929b2e7e6d1ae9919623bd2b','alternative':'f7d800398ecd6dc79c5b346e7e151cf917272327'},'exact four frozen products');root=Path(root);base=root/'sarext-results';need((base/'controller-commit.txt').read_text().strip()==trust['controller'],'controller head')
 for name,h in trust['controller_sha256'].items():
  if name.startswith('tests/'):continue
  path=base/'workflow.yml'if name.startswith('.github/')else base/'controller'/Path(name).name;need(sha(path)==h,'immutable controller '+name)
 p=js(base/'build-provenance.json');need(set(p['builds'])==set(SIDES)and p['flags']['rustc'].startswith('rustc 1.90.0 ')and'host: x86_64-unknown-linux-gnu'in p['flags']['rustc'],'normal four-arm toolchain');eq(p['cases'],trust['case_manifest']['cases'],'cases');eq(p['orders'],[list(x)for x in ORDERS],'Williams orders');need(p['rounds']==12,'twelve rounds');eq(p['scripts'],{Path(k).name:v for k,v in trust['controller_sha256'].items()if k.startswith('scripts/')},'all bound scripts')
 for k,v in{'CARGO_PROFILE_RELEASE_DEBUG':'false','CARGO_PROFILE_RELEASE_OPT_LEVEL':'3','CARGO_PROFILE_RELEASE_LTO':'false','CARGO_PROFILE_RELEASE_CODEGEN_UNITS':'16','RUSTFLAGS':'','CARGO_ENCODED_RUSTFLAGS':'','CFLAGS':'','CXXFLAGS':''}.items():need(p['flags']['environment'][k]==v,'portable product profile '+k)
 whl=wheels(root,base,trust,p);graphs={s:fingerprints(base,s)for s in SIDES};elf=elf_proof(base,p,trust,whl);corpus=all_corpus(base,trust);word={a+'_vs_'+b:words_diagnostics(base/'corpus'/(a+'.npz'),base/'corpus'/(b+'.npz'))for a,b in PAIRS};eq(js(base/'corpus/word-diagnostics.json'),word,'all six full corpus raw word diagnostics')
 v=js(base/'validation-complete.json');need(v['all_checks_completed_before_any_timing']is True and v['build_provenance_sha256']==sha(base/'build-provenance.json')and v['checked_values_per_setting']==12400000,'all pretime validation');eq(v['cases'],trust['case_manifest']['cases'],'validation inventory');eq(v['cold_dispatch'],cold_proof(base),'actual Linux cold resolver');need(set(v['corpus'])==set(corpus)and v['corpus_word_diagnostics_sha256']==sha(base/'corpus/word-diagnostics.json'),'full corpus report binding')
 for label,row in v['corpus'].items():eq(row,js(base/'corpus'/(label+'.json')),'complete corpus report')
 rows={side:js(base/'zero-regressions'/(side+'.json'))for side in SIDES};zero=js(base/'zero-regressions/validated.json');eq(zero['validated'],zero_captures(rows,trust,p),'independent explicit legacy zero contract');eq(zero['capture_sha256'],{side:sha(base/'zero-regressions'/(side+'.json'))for side in SIDES},'zero capture hashes');need(zero['timed_waiver']is False and v['zero_regression_sha256']==sha(base/'zero-regressions/validated.json'),'no timed/corpus waiver')
 results={};inputs=None
 for t in(1,4):
  folder=base/f'threads-{t}';need(v['prepared_sha256'][str(t)]==sha(folder/'prepared-validation.json'),'prepared thread binding');prep=js(folder/'prepared-validation.json');expected,fixture,proof=physical.audit_inputs(base/'inputs',prep['input_snapshots'],trust['case_manifest']['cases'])
  if inputs is not None:eq(proof,inputs,'same physical inputs at both thread settings')
  inputs=proof;results[str(t)]=setting(base,t,trust,p,whl,expected,fixture,prep['input_snapshots'])
 top=js(base/'summary.json');need(top['run_url']==f'https://github.com/Yvictor/polars_ta_extension/actions/runs/{trust["run"]}'and top['thread_counts']==[1,4],'run/thread identity');eq(top['build_provenance'],p,'top build');eq(top['validation'],v,'top gates');neg=[];stress=[]
 for t in results:
  copy_setting=copy.deepcopy(js(base/f'threads-{t}/summary.json'))
  for comparison,records in copy_setting['comparisons'].items():
   for name,row in records.items():
    role=trust['case_manifest']['case_roles'][name];change=(row['candidate_median_ms']/row['baseline_median_ms']-1)*100;row.update(case_role=role,is_unchanged_timed_query=role=='pure_polars_drift_control',after_latency_percent=change,after_faster_rounds=sum(x>1 for x in row['paired_ratios']))
    full={'threads':int(t),'comparison':comparison,'case':name,**row}
    if change>0:neg.append(full)
    if role=='legitimate_long_zero_replay_stress':stress.append(full)
  eq(top['results'][t],copy_setting,'top all scenarios')
 eq(js(base/'negative-cases.json'),neg,'all six pairwise slower cases');eq(js(base/'replay-stress.json'),stress,'all legitimate long-zero stress comparisons')
 for k in('cpu','platform','python','polars','numpy','rust','profile'):eq(results['1']['runtime'][k],results['4']['runtime'][k],'same runner '+k)
 need(sum(x['children']for x in results.values())==1344 and sum(x['samples']for x in results.values())==41664,'complete child/sample matrix')
 return {'audit_pass':True,'run':trust['run'],'controller':trust['controller'],'pins':trust['pins'],'children':1344,'samples':41664,'wheels':whl,'corpus':corpus,'word_diagnostics':word,'zero_contract':zero['validated'],'elf_proof':elf,'cargo_snapshots':graphs,'physical_inputs':inputs,'results':results,'negative_comparisons':neg,'replay_stress':stress,'limits':trust['limits']+['SAREXT numerical outputs are compared against retained immutable original C/public native goldens; no separate reimplementation of the SAR kernel is executed by this auditor. Physical inputs, grouping, warmups, C-target zero boundary, pure Polars controls and all distributions are independently reconstructed.','Timed final output arrays are not duplicated; immutable child source performs exact final checks against own-arm goldens, with retained pre-timer output hashes and final_output_checked flag. No timing-loop instrumentation or allocator-only attribution.']}

if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('artifact',type=Path);ap.add_argument('--output',type=Path,required=True);ap.add_argument('--trust',type=Path,default=HERE/'trusted.json');a=ap.parse_args();r=audit(a.artifact,js(a.trust));a.output.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({k:r[k]for k in('audit_pass','run','children','samples')},indent=2))
