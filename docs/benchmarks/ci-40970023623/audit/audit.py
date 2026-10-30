"""Independent MAVP physical-input/three-golden artifact replay; never executes products/controllers."""
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
 result=core.arrays(old,new,old_null,new_null,**kwargs)
 # Finite C tolerance does not waive the sign when BOTH outputs are zero.
 # Zero versus tiny finite cancellation continues to use the declared policy.
 need(result['zero_sign_differences']==0,kwargs.get('where','arrays')+': signed-zero differences')
 return result

SIDES=('original','prior','combined','candidate');ORDERS=(('original','prior','combined','candidate'),('prior','candidate','original','combined'),('candidate','combined','prior','original'),('combined','original','candidate','prior'));PAIRS=tuple((a,b)for i,a in enumerate(SIDES)for b in SIDES[i+1:])

def name_shape(name):
 fam,shape=name.split('/');inter=shape.endswith('_interleaved');parts=shape.removesuffix('_interleaved').split('x');groups,bars=map(int,parts)if len(parts)==2 else(1,int(parts[0]));return fam,groups,bars,inter

def golden(path,names,expected):
 hashes={};keys=set();total=0
 with np.load(path,allow_pickle=False)as f:
  for name in names:
   family,n,g,b,inter,grouped,pattern=physical.shape(name);column='control'if pattern=='control'else family;schema="Schema({'"+column+"': Float64})";k=name+'_0';keys.update((name+'_schema',k,k+'_null'));arr=f[k];null=f[k+'_null'];need(f[name+'_schema'].shape==()and str(f[name+'_schema'])==schema,'fixed scalar schema');need(arr.shape==null.shape==(n,)and arr.dtype==np.dtype('float64')and null.dtype==np.dtype(bool)and not null.any(),'golden dtype/length/nulls');lookback=0 if pattern=='control'else 29;ordered=arr.reshape(b,g).T if inter else arr.reshape(g if grouped else 1,b if grouped else n);need(np.isnan(ordered[:,:lookback]).all()and np.isfinite(ordered[:,lookback:]).all(),'every-group warmup/finite range')
   if expected[name]is not None:arrays(expected[name],arr,np.zeros(n,bool),null,exact=pattern in('period1','control'),where='independent physical-input formula '+name)
   h=hashlib.sha256(schema.encode());h.update(arr.tobytes());h.update(null.tobytes());hashes[name]=h.hexdigest();total+=n
  need(set(f.files)==keys,'complete golden array inventory')
 return hashes,total

def compare_goldens(old,new,names,exact):
 metrics={};maximum=0.
 with np.load(old,allow_pickle=False)as a,np.load(new,allow_pickle=False)as b:
  for name in names:
   need(str(a[name+'_schema'])==str(b[name+'_schema']),'golden schema');k=name+'_0';r=arrays(a[k],b[k],a[k+'_null'],b[k+'_null'],exact=exact,where='retained own-arm golden '+name);maximum=max(maximum,r.pop('max_abs'))
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
  logpath=base/(side+'-build.log');log=logpath.read_text();source=str(ws/'sources'/side);paths=re.findall(r'^\s*Compiling polars_talib v0\.2\.1 \((.+)\)\s*$',log,re.M);need(paths and all(x==source for x in paths),'compile exact immutable source path');proof=proofmap.get(source);need(proof is not None and proof['log']==str(ws/'mavp-uniform-results'/(side+'-build.log'))and proof['log_sha256']==sha(logpath)and proof['product_compile_lines']==len(paths),'actual product compile proof binding');need('release'in log and'optimized'in log and'target-cpu=native'not in log and'-march=native'not in log,'actual release build')
 return out

def fingerprints(base,side):
 folder=base/'product-fingerprints'/side;need(folder.is_dir(),'retained Cargo snapshot');nodes={};roots=[]
 for meta in folder.glob('*/lib-*.json'):
  rawpath=meta.with_suffix('');need(rawpath.is_file(),'Cargo raw fingerprint');raw=rawpath.read_text().strip();need(re.fullmatch('[0-9a-f]{16}',raw)is not None,'Cargo raw16hex');fp=int.from_bytes(bytes.fromhex(raw),'little');r=js(meta);deps={}
  for edge in r['deps']:need(len(edge)==4 and edge[1]not in deps and type(edge[3])is int,'Cargo dependency metadata');deps[edge[1]]=edge[3]
  name=meta.stem.removeprefix('lib-');row={'name':name,'metadata_sha256':sha(meta),'raw_sha256':sha(rawpath),'fingerprint':fp,'deps':deps,'rustflags':r['rustflags'],'profile':r['profile']};nodes.setdefault((name,fp),[]).append(row)
  if name=='_polars_talib':roots.append(row)
 wanted=('talib','talib_sys','serde','polars','jemallocator','pyo3_polars')if side=='original'else('ta_lib','serde','polars','jemallocator','pyo3_polars')
 if side in('combined','candidate'):wanted+=('multiversion',)
 selected=[]
 for root in roots:
  if not set(wanted)<=set(root['deps']):continue
  need(root['rustflags']==[],'normal root portable flags');edges={}
  for name in wanted:
   found=nodes.get((name,root['deps'][name]),[]);need(found and len({r['metadata_sha256']for r in found})==1,'Cargo actual root edge '+name);need(all(r['rustflags']==[]for r in found),'dependency flags');edges[name]=found[0]
  selected.append({'root':root,'edges':edges})
 need(selected,'normal product family Cargo graph absent')
 if side in('combined','candidate'):need(any('multiversion'in row['root']['deps']for row in selected),'combined/candidate public multiversion root dependency')
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
 wanted=[str(ws/'envs'/side/'bin/python'),str(ws/'control-source/scripts/mavp_uniform_query.py'),'--source-root',str(ws/'sources'/side),'--output',str(ws/'mavp-uniform-results'/f'threads-{t}'/(label+'.json')),'--label',label,'--repeats','31',*extra]
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

def source_boundary(p,trust):
 maps=trust['source_file_sha256'];before,after=maps['combined'],maps['candidate'];changed=sorted(n for n in set(before)|set(after)if before.get(n)!=after.get(n));need(changed==['src/compat/mavp_sma.rs'],'only reviewed production helper changed');need(after[changed[0]]=='c90e922f7a2289e6408306409ce77edc582e5a25ee98d21138f74a2bbab23fd8','reviewed uniform helper bytes');required={'src/native.rs','src/compat.rs','src/compat/guarded.rs','src/generated.rs','src/params.rs','src/missing.rs','src/utils.rs','Cargo.toml','Cargo.lock'};expected={'changed_files':changed,'routing_sources':{n:before[n]for n in sorted(required)},'helper_before':before[changed[0]],'helper_after':after[changed[0]]};eq(p['native_source_boundary'],expected,'unchanged routing/source boundary');need(trust['candidate_git_changes']=={'src/compat/mavp_sma.rs':after[changed[0]],'tests/test_mavp_uniform_prefix.py':'d8659d98d81b231ce4699c0f6bfed9a3921e94952f247cd7fe5fdc97bf0b91c4'},'exact helper/public-test Git boundary');return expected

def build_commands(base,p,whl):
 ws=Path(p['flags']['environment']['CARGO_TARGET_DIR']).parent;commands=[core.decode(x)for x in(base/'build-commands.jsonl').read_text().splitlines()if x];need(len(commands)==4,'four explicit product build commands')
 for row,side in zip(commands,('prior','combined','candidate','original')):
  expected={'side':side,'command':[str(ws/'envs'/side/'bin/python'),'-m','maturin','build','--release','--locked','--interpreter',str(ws/'envs'/side/'bin/python'),'--out',str(ws/'wheels'/side)]};eq(row,expected,'exact native release build command')
  b=p['builds'][side];installed=list(b['identity']['native_files']);retained=list(b['retained_native_files']);need(len(installed)==len(retained)==1,'single installed/retained native');eq(b['product_elf'],[{'path':retained[0],'sha256':whl[side]['native_sha256'],'format':'ELF64 little-endian x86-64'}],'actual retained ELF format/hash')
 return commands

def setting(base,t,trust,p,whl,expected,cov,fixture,records):
 folder=base/f'threads-{t}';s=js(folder/'summary.json');prep=js(folder/'prepared-validation.json');names=trust['case_manifest']['cases'];need(len(names)==32,'32queries');eq(s['case_inventory'],names,'summary inventory');eq(prep['inventory'],names,'prepared inventory');need(type(s['threads'])is type(prep['threads'])is int and s['threads']==prep['threads']==t and s['rounds']==12 and s['repeats']==31 and s['warmups']==5,'fixed protocol')
 commands=[core.decode(x)for x in(folder/'commands.jsonl').read_text().splitlines()if x];need(len(commands)==7+32*48,'seven pretime plus1536 selected commands');ws=Path(commands[0]['argv'][1]).parents[2];files={'original':'reference.npz',**{side:side+'-reference.npz'for side in SIDES[1:]}};hashes={};goldens={side:sha(folder/file)for side,file in files.items()};eq(s['golden_sha256'],goldens,'summary four golden hashes');eq(prep['golden_sha256'],goldens,'prepared four golden hashes')
 for side,file in files.items():hashes[side],count=golden(folder/file,names,expected);need(count==30400000,'all32 query values')
 comparisons={a+'_vs_'+b:compare_goldens(folder/files[a],folder/files[b],names,exact=a!='original')for a,b in PAIRS};origins=prep['source_validations'];need(set(origins)==set(SIDES),'all four pretime arms')
 for side,row in origins.items():
  metadata(row,side,t,trust,p,whl);eq(row['case_inventory'],names,'pretime inventory');eq(row['case_filters'],names,'pretime selector');need(not row['results']and type(row['checked_values'])is int and row['checked_values']==(0 if side=='original'else count),'pretime full checks/no timer');eq(row['fixture_sha256'],fixture,'retained physical digest');eq(row['output_sha256'],hashes[side],'retained own-arm golden digest');eq(row['fixture_coverage'],cov,'physical per-group route/split/fraction eligibility');eq(row['input_snapshots'],records if side=='original'and t==1 else{},'only1Toriginal preservesIPC');eq(js(folder/('reference-'+side+'.json')),row,'raw own-arm capture');need(row['correctness_reference']==(None if side=='original'else str(ws/'mavp-uniform-results'/f'threads-{t}'/'reference.npz'))and row['exact_reference']is False,'C preflight reference path')
 for key in('python','platform','cpu','polars','numpy','rust','profile','threads','affinity'):need(len({json.dumps(x[key])for x in origins.values()})==1,'same four-arm runtime '+key)
 for key in('cpu','platform','python','polars','numpy','rust','threads','affinity','repeats','warmups','diagnostic','checked_values','case_filters'):eq(s[key],origins['candidate'][key],'actual summary metadata '+key)
 eq(s['commits'],trust['pins'],'four source pins');eq(s['source_sha256'],{side:trust['source_record'][side]['source_sha256']for side in SIDES},'source digests');eq(s['native_binary_sha256'],{side:whl[side]['native_sha256']for side in SIDES},'all ELF hashes');need(s['process_isolation']=='one case per fresh process','single-case isolation')
 native_pairs=[(a,b)for a,b in PAIRS if a!='original'];exacts=prep['exact_validations'];need(set(exacts)=={a+'_vs_'+b for a,b in native_pairs},'all three exact native preflight comparisons')
 for before,after in native_pairs:
  row=exacts[before+'_vs_'+after];label='validation-exact-'+before+'-'+after;metadata(row,after,t,trust,p,whl);eq(row,js(folder/(label+'.json')),'raw exact validation');eq(row['output_sha256'],hashes[after],'exact own-arm digest');eq(row['fixture_sha256'],fixture,'exact physical input');eq(row['fixture_coverage'],cov,'exact per-group route/split');eq(row['case_inventory'],names,'exact inventory');eq(row['case_filters'],names,'exact selectors');eq(row['input_snapshots'],{},'no exact IPCwrite');need(row['exact_reference']is True and type(row['checked_values'])is int and row['checked_values']==count and not row['results']and row['correctness_reference']==str(ws/'mavp-uniform-results'/f'threads-{t}'/files[before]),'native exact preflight reference')
 prepares=[]
 for side in SIDES:
  extra=['--check-only','--write-reference',str(ws/'mavp-uniform-results'/f'threads-{t}'/files[side])]
  if side=='original'and t==1:extra+=['--preserve-inputs',str(ws/'mavp-uniform-results/raw-inputs')]
  if side!='original':extra+=['--reference',str(ws/'mavp-uniform-results'/f'threads-{t}'/'reference.npz')]
  prepares.append((side,'reference-'+side,extra))
 prepares.extend((after,'validation-exact-'+before+'-'+after,['--check-only','--reference',str(ws/'mavp-uniform-results'/f'threads-{t}'/files[before]),'--exact-reference'])for before,after in native_pairs)
 for command,(side,label,args)in zip(commands,prepares):eq(command,cli_record(ws,t,side,label,names,args),'exact four-arm preflight CLI')
 eq(prep['commands'],[c['argv']for c in commands[:7]],'prepared CLI');eq(s['commands'],[c['argv']for c in commands],'all actual CLI');manifest=ledger(names);runs={name:{side:[]for side in SIDES}for name in names};comps={a+'_vs_'+b:{}for a,b in PAIRS};faults={}
 for index,item in enumerate(manifest,7):
  name,side=item['case'],item['side'];label=item['report'][:-5];row=js(folder/item['report']);metadata(row,side,t,trust,p,whl);need(row['label']==label,'selected label');entry=timing(row,name);eq(row['fixture_sha256'],{name:fixture[name]},'selected physical input');eq(row['output_sha256'],{name:hashes[side][name]},'selected own-arm golden');eq(row['final_output_sha256'],row['output_sha256'],'selected final own-arm golden');eq(row['fixture_coverage'],{name:cov[name]},'selected normalized route/split');eq(row['input_snapshots'],{},'no timedIPC');eq(core.decode((folder/(label+'.stdout.log')).read_text()),{name:round(entry['median_ms'],4)},'raw stdout median');need((folder/(label+'.stderr.log')).is_file(),'raw stderr retained')
  for k in('cpu','platform','python','polars','numpy','rust','threads','affinity','profile'):eq(row[k],origins[side][k],'selected runtime drift '+k)
  reference=str(ws/'mavp-uniform-results'/f'threads-{t}'/files[side]);need(row['correctness_reference']==reference,'selected own-arm reference');eq(commands[index],cli_record(ws,t,side,label,names,['--reference',reference,'--exact-reference'],name),'selected exact own-armCLI');runs[name][side].append(entry)
 for name in names:
  for a,b in PAIRS:comps[a+'_vs_'+b][name]=core.comparison(runs[name][a],runs[name][b])
  faults[name]={}
  for side in SIDES:
   faults[name][side]={}
   for key in('minor_faults','major_faults'):
    vectors=[r[key]for r in runs[name][side]];medians=[statistics.median(x)for x in vectors];pool=[v for x in vectors for v in x];faults[name][side][key]={'median':statistics.median(medians),'process_medians':medians,'p10_p90':[core.pct(pool,p)for p in(.1,.9)]}
 eq(s['comparisons'],comps,'all six independent comparisons');eq(s['faults'],faults,'all fault summaries');eq(s['processes'],manifest,'all Williams processes');eq(s['order'],[x['report'][:-5]for x in manifest],'Williams execution order');need({x.name for x in folder.glob('case-*.json')}=={x['report']for x in manifest},'no missing/orphan selected report')
 return {'threads':t,'cases':32,'children':len(manifest),'samples':len(manifest)*31,'runtime':{key:origins['candidate'][key]for key in('cpu','platform','python','polars','numpy','rust','profile','affinity')},'comparisons':comps,'golden_comparisons':comparisons,'fixture_coverage':cov}

def audit(root,trust):
 need(type(trust['run'])is int and trust['run']==40970023623 and trust['controller']=='5171ea5583f83766da05ef0d1f8bc69091063369'and trust['pins']=={'original':'b2bbc26d41ec80823c8bffb0cc436a97f29911cc','prior':'56f6d5fb139031c20d86d7e818e7d267eb834295','combined':'0eb91280cf5d13095cbfdc6f8bcc477cfbcd1498','candidate':'916b0de68369df410559b6dc651731cf4c36b94c'},'fixed uniform campaign');root=Path(root);base=root/'mavp-uniform-results';need((base/'controller-commit.txt').read_text().strip()==trust['controller'],'actual controller head')
 for name,h in trust['controller_sha256'].items():
  if name.startswith('tests/'):continue
  path=base/'workflow.yml'if name.startswith('.github/')else base/'controller'/Path(name).name;need(sha(path)==h,'immutable controller '+name)
 p=js(base/'build-provenance.json');need(set(p['builds'])==set(SIDES)and p['flags']['rustc'].startswith('rustc 1.90.0 ')and'host: x86_64-unknown-linux-gnu'in p['flags']['rustc'],'four-arm normal toolchain');eq(p['cases'],trust['case_manifest']['cases'],'fixed32 cases');eq(p['orders'],[list(x)for x in ORDERS],'four balanced Williams orders');need(type(p['rounds'])is int and p['rounds']==12,'twelve rounds');eq(p['scripts'],{Path(n).name:h for n,h in trust['controller_sha256'].items()if n.startswith('scripts/')},'all bound controller scripts')
 for k,v in{'CARGO_PROFILE_RELEASE_DEBUG':'false','CARGO_PROFILE_RELEASE_OPT_LEVEL':'3','CARGO_PROFILE_RELEASE_LTO':'false','CARGO_PROFILE_RELEASE_CODEGEN_UNITS':'16','RUSTFLAGS':'','CARGO_ENCODED_RUSTFLAGS':'','CFLAGS':'','CXXFLAGS':''}.items():need(p['flags']['environment'][k]==v,'normal release profile '+k)
 boundary=source_boundary(p,trust);whl=wheels(root,base,trust,p);commands=build_commands(base,p,whl);graphs={side:fingerprints(base,side)for side in SIDES};corpus=all_corpus(base,trust);v=js(base/'validation-complete.json');need(v['all_checks_completed_before_any_timing']is True and v['build_provenance_sha256']==sha(base/'build-provenance.json')and type(v['checked_values_per_setting'])is int and v['checked_values_per_setting']==30400000 and type(v['raw_input_dedup'])is int and v['raw_input_dedup']==24,'pretime complete corpus/goldens/IPC gates');eq(v['cases'],trust['case_manifest']['cases'],'pretime inventory');need(set(v['corpus'])==set(corpus),'all six corpus pair reports')
 for label,row in v['corpus'].items():eq(row,js(base/'corpus'/(label+'.json')),'pretime corpus report')
 for t in(1,4):need(v['prepared_sha256'][str(t)]==sha(base/f'threads-{t}/prepared-validation.json'),'thread prepared binding')
 expected,cov,fixture,proof=physical.audit_inputs(base/'raw-inputs',v['raw_input_snapshots'],trust['case_manifest']['cases']);eq(v['raw_input_fixture_sha256'],fixture,'physicalIPC fixture mapping');results={str(t):setting(base,t,trust,p,whl,expected,cov,fixture,v['raw_input_snapshots'])for t in(1,4)};top=js(base/'summary.json');need(top['run_url']=='https://github.com/Yvictor/polars_ta_extension/actions/runs/40970023623'and top['thread_counts']==[1,4]and set(top['results'])=={'1','4'},'actual run/thread identity');eq(top['build_provenance'],p,'top build');eq(top['validation'],v,'top pretime gates');negative=[]
 for t in results:
  derived=copy.deepcopy(js(base/f'threads-{t}/summary.json'))
  for pair,cases in derived['comparisons'].items():
   for name,row in cases.items():
    change=(row['candidate_median_ms']/row['baseline_median_ms']-1)*100;row.update(after_latency_percent=change,after_faster_rounds=sum(x>1 for x in row['paired_ratios']))
    if change>0:negative.append({'threads':int(t),'comparison':pair,'case':name,**row})
  eq(top['results'][t],derived,'all top scenario statistics')
 eq(js(base/'negative-cases.json'),negative,'every slower median including controls')
 for key in('cpu','platform','python','polars','numpy','rust','profile'):eq(results['1']['runtime'][key],results['4']['runtime'][key],'same runner '+key)
 need(sum(x['children']for x in results.values())==3072 and sum(x['samples']for x in results.values())==95232,'complete child/sample protocol')
 return {'audit_pass':True,'run':trust['run'],'controller':trust['controller'],'pins':trust['pins'],'children':3072,'samples':95232,'wheels':whl,'build_commands':commands,'native_source_boundary':boundary,'corpus':corpus,'cargo_snapshots':graphs,'physical_inputs':proof,'results':results,'negative_comparisons':negative,'limits':trust['limits']+['The direct-window finite SMA oracle is independent of the rolling helper and uses declared C finite tolerance. EMA/WMA control arithmetic relies on retained original-C goldens; every native golden pair is exact including finite/signedzero/masks/NaN/Inf positions.','Explicit globally unfused100+900*random transform regenerates Linux volume bits; ARM Generator.uniform may fuse. This is exact input provenance, not numerical tolerance.']}
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('artifact',type=Path);ap.add_argument('--trust',type=Path,default=HERE/'trusted.json');ap.add_argument('--output',type=Path,required=True);args=ap.parse_args();r=audit(args.artifact,js(args.trust));args.output.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({k:r[k]for k in('audit_pass','run','controller','children','samples')},indent=2))
