import copy,importlib.util,json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
HERE=Path(__file__).parent
spec=importlib.util.spec_from_file_location('a',HERE/'audit.py');a=importlib.util.module_from_spec(spec);spec.loader.exec_module(a)

class Ledger(unittest.TestCase):
 def fixture(self,base,mutate=None,t=1):
  trust=a.js(HERE/'trusted.json');names=trust['case_manifest']['cases'];ws=Path('/runner/ws');folder=base/f'threads-{t}';folder.mkdir();identity={'python':'3.12.15','platform':'Linux-x86_64','polars':'1.44.2','numpy':'2.5.3','package':'0.2.1','talib':'0.8.3 (native Rust; polars-talib compatibility)','cpu':'CPU','profile':a.core.PROFILE,'affinity':list(range(t)),'rust':'rustc 1.90.0 test'};p={'builds':{side:{'identity':dict(identity,talib='0.8.1 C'if side=='original'else identity['talib'])}for side in a.SIDES},'flags':{'rustc':'rustc 1.90.0 test\n'}};whl={side:{'native_sha256':side}for side in a.SIDES};hashes={side:{n:'hash:'+side+':'+n for n in names}for side in a.SIDES};cov={n:{}for n in names};fixture={n:'fixture:'+n for n in names};records={n:{'file':'fixture'}for n in names};rows={};commands=[];files={'original':'reference.npz',**{side:side+'-reference.npz'for side in a.SIDES[1:]}}
  def row(side,label):return dict(p['builds'][side]['identity'],commit=trust['pins'][side],source_sha256=trust['source_record'][side]['source_sha256'],native_binary_sha256=side,threads=t,repeats=31,warmups=5,diagnostic=False,integer_reference_exact=True,label=label,case_inventory=names,case_filters=names,results={},checked_values=0 if side=='original'else 30400000,fixture_coverage=cov,input_snapshots={},fixture_sha256=fixture,output_sha256=hashes[side],correctness_reference=None,exact_reference=False)
  def command(side,label,args,selected=None):
   argv=[str(ws/'envs'/side/'bin/python'),str(ws/'control-source/scripts/mavp_uniform_query.py'),'--source-root',str(ws/'sources'/side),'--output',str(ws/'mavp-uniform-results'/f'threads-{t}'/(label+'.json')),'--label',label,'--repeats','31',*args]
   for name in([selected]if selected else names):argv+=['--case-filter',name]
   commands.append({'label':label,'side':side,'selected_case':selected,'argv':argv,'polars_threads':t})
  origins={}
  for side in a.SIDES:
   label='reference-'+side;r=row(side,label);r['input_snapshots']=records if side=='original'and t==1 else{};args=['--check-only','--write-reference',str(ws/'mavp-uniform-results'/f'threads-{t}'/files[side])]
   if side=='original'and t==1:args+=['--preserve-inputs',str(ws/'mavp-uniform-results/raw-inputs')]
   if side!='original':r['correctness_reference']=str(ws/'mavp-uniform-results'/f'threads-{t}'/'reference.npz');args+=['--reference',r['correctness_reference']]
   rows[label+'.json']=r;origins[side]=r;command(side,label,args)
  exacts={}
  for before,after in a.PAIRS:
   if before=='original':continue
   label='validation-exact-'+before+'-'+after;r=row(after,label);r.update(exact_reference=True,correctness_reference=str(ws/'mavp-uniform-results'/f'threads-{t}'/files[before]));rows[label+'.json']=r;exacts[before+'_vs_'+after]=r;command(after,label,['--check-only','--reference',r['correctness_reference'],'--exact-reference'])
  prep={'inventory':names,'threads':t,'golden_sha256':{side:'HASH'for side in a.SIDES},'source_validations':origins,'exact_validations':exacts,'commands':[c['argv']for c in commands]};comps={x+'_vs_'+y:{}for x,y in a.PAIRS};faults={};manifest=[]
  for idx,name in enumerate(names,1):
   n=a.name_shape(name)[1]*a.name_shape(name)[2];runs={side:[]for side in a.SIDES}
   for rnd,order in enumerate(a.ORDERS*3,1):
    for side in order:
     label=f'case-{idx:03d}-{side}-{rnd}';r=row(side,label);r.update(case_inventory=[name],case_filters=[name],checked_values=n,exact_reference=True,final_output_checked=True,results={name:{'samples_ms':[1.]*31,'median_ms':1.,'min_ms':1.,'rows':n,'output_fields':1,'minor_faults':[0]*31,'major_faults':[0]*31}},fixture_sha256={name:fixture[name]},output_sha256={name:hashes[side][name]},fixture_coverage={name:cov[name]},final_output_sha256={name:hashes[side][name]},correctness_reference=str(ws/'mavp-uniform-results'/f'threads-{t}'/files[side]));rows[label+'.json']=r;command(side,label,['--reference',r['correctness_reference'],'--exact-reference'],name);manifest.append({'case':name,'side':side,'round':rnd,'report':label+'.json'});runs[side].append(r['results'][name]);(folder/(label+'.json')).touch();(folder/(label+'.stdout.log')).write_text(json.dumps({name:1.}));(folder/(label+'.stderr.log')).write_text('')
   for x,y in a.PAIRS:comps[x+'_vs_'+y][name]=a.core.comparison(runs[x],runs[y])
   faults[name]={side:{k:{'median':0.,'process_medians':[0]*12,'p10_p90':[0.,0.]}for k in('minor_faults','major_faults')}for side in a.SIDES}
  summary={'case_inventory':names,'threads':t,'rounds':12,'repeats':31,'warmups':5,'golden_sha256':{side:'HASH'for side in a.SIDES},'commands':[r['argv']for r in commands],'comparisons':comps,'faults':faults,'processes':manifest,'order':[r['report'][:-5]for r in manifest],'commits':trust['pins'],'source_sha256':{side:trust['source_record'][side]['source_sha256']for side in a.SIDES},'native_binary_sha256':{side:side for side in a.SIDES},'process_isolation':'one case per fresh process'};summary.update({k:origins['candidate'][k]for k in('cpu','platform','python','polars','numpy','rust','threads','affinity','repeats','warmups','diagnostic','checked_values','case_filters')});rows.update({'summary.json':summary,'prepared-validation.json':prep});(folder/'commands.jsonl').write_text('\n'.join(json.dumps(c)for c in commands))
  if mutate:mutate(rows,commands)
  def fakegold(path,*_):return hashes['original'if Path(path).name=='reference.npz'else Path(path).name.removesuffix('-reference.npz')],30400000
  with patch.object(a,'js',lambda path:copy.deepcopy(rows[Path(path).name])),patch.object(a,'sha',lambda p:'HASH'),patch.object(a,'golden',side_effect=fakegold),patch.object(a,'compare_goldens',return_value={}):return a.setting(base,t,trust,p,whl,{},cov,fixture,records)
 def test_complete_fourarm_32case_ledger_both_settings(self):
  for t in(1,4):
   with self.subTest(threads=t),tempfile.TemporaryDirectory()as d:self.assertEqual(self.fixture(Path(d),t=t)['children'],1536)
 def test_ownarm_golden_checks_and_exact_native_pair_scope(self):
  cases=[('case-001-candidate-1.json','correctness_reference','/runner/ws/mavp-uniform-results/threads-1/combined-reference.npz'),('case-001-candidate-1.json','output_sha256',{'mavp_four/1000000':'wrong'}),('case-001-candidate-1.json','final_output_sha256',{'mavp_four/1000000':'wrong'}),('case-001-candidate-1.json','exact_reference',False),('case-001-candidate-1.json','final_output_checked',False),('validation-exact-combined-candidate.json','correctness_reference','/runner/ws/mavp-uniform-results/threads-1/prior-reference.npz'),('validation-exact-prior-combined.json','output_sha256',{'WRONG':'hash'}),('reference-combined.json','input_snapshots',{'FORBIDDEN':{}}),('summary.json','golden_sha256',{})]
  for file,key,value in cases:
   with self.subTest(file=file,key=key),tempfile.TemporaryDirectory()as d:
    with self.assertRaises((ValueError,KeyError)):self.fixture(Path(d),lambda rows,_:rows[file].__setitem__(key,value))
 def test_numeric_protocol_bool_shape_stats_and_source_rejections(self):
  for key,value in(('threads',True),('repeats',True),('affinity',[True]),('native_binary_sha256','WRONG'),('source_sha256','WRONG'),('commit','WRONG'),('profile','WRONG'),('checked_values',True),('fixture_coverage',{})):
   with self.subTest(key=key),tempfile.TemporaryDirectory()as d:
    with self.assertRaises(ValueError):self.fixture(Path(d),lambda rows,_:rows['case-001-candidate-1.json'].__setitem__(key,value))
  for key,value in(('median_ms',1.+5e-13),('min_ms',True),('rows',True),('output_fields',True),('samples_ms',[1.]*30),('major_faults',[-1]*31)):
   with self.subTest(key=key),tempfile.TemporaryDirectory()as d:
    with self.assertRaises(ValueError):self.fixture(Path(d),lambda rows,_:rows['case-001-candidate-1.json']['results']['mavp_four/1000000'].__setitem__(key,value))
 def test_all_six_pairings_and_three_exact_preflight_records_required(self):
  for kind in('drop_pair','drop_exact','drop_process','tiny_stat'):
   with self.subTest(kind=kind),tempfile.TemporaryDirectory()as d:
    def mutate(rows,_):
     if kind=='drop_pair':rows['summary.json']['comparisons'].pop('combined_vs_candidate')
     elif kind=='drop_exact':rows['prepared-validation.json']['exact_validations'].pop('combined_vs_candidate')
     elif kind=='drop_process':rows['summary.json']['processes'].pop()
     else:rows['summary.json']['comparisons']['combined_vs_candidate']['mavp_four/1000000']['candidate_median_ms']+=5e-13
    with self.assertRaises(ValueError):self.fixture(Path(d),mutate)
if __name__=='__main__':unittest.main()
