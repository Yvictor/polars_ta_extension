"""Every independent four-arm comparison and remaining regression; no pooling runners."""
import csv,json
from collections import Counter
from pathlib import Path
HERE=Path(__file__).parent

def role(name):
 family=name.split('/')[0].removeprefix('grouped_').removeprefix('mavp_')
 return'uniform fast path'if family in('one','period1','fractional')else'unchanged EMA/WMA or Polars control'if family in('ema','wma')or family.startswith('control_cumsum')else'nonuniform fallback regression guard'
def main():
 r=json.loads((HERE/'audit-result.json').read_text());assert r['audit_pass']and r['run']==40970023623 and r['children']==3072 and r['samples']==95232;rows=[]
 for t,setting in r['results'].items():
  for pair,cases in setting['comparisons'].items():
   for name,x in cases.items():
    env=x['ratio_envelope'];rows.append({'threads':int(t),'comparison':pair,'case':name,'role':role(name),'after_latency_percent':(x['candidate_median_ms']/x['baseline_median_ms']-1)*100,'range_class':'disjoint faster'if env[0]>1 else'disjoint slower'if env[1]<1 else'overlap','after_faster_rounds':sum(v>1 for v in x['paired_ratios']),'paired_median_latency_percent':(1/x['median_paired_ratio']-1)*100,**x})
 assert len(rows)==384 and len({(x['threads'],x['comparison'],x['case'])for x in rows})==384
 for name,data in [('all-384-comparisons.csv',rows),('all-slower-medians.csv',[x for x in rows if x['after_latency_percent']>0])]:
  with(HERE/name).open('w',newline='')as f:
   w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows({k:json.dumps(v,separators=(',',':'))if isinstance(v,list)else v for k,v in x.items()}for x in data)
 negative=[x for x in rows if x['after_latency_percent']>0];(HERE/'all-slower-medians.json').write_text(json.dumps(negative,indent=2)+'\n');inventory={}
 for pair in r['results']['1']['comparisons']:
  inventory[pair]={}
  for group in('all','uniform fast path','nonuniform fallback regression guard','unchanged EMA/WMA or Polars control'):
   filtered=[x for x in rows if x['comparison']==pair and(group=='all'or x['role']==group)];inventory[pair][group]={'observations':len(filtered),'slower_medians':sum(x['after_latency_percent']>0 for x in filtered),'ranges':dict(Counter(x['range_class']for x in filtered)),'latency_percent_minmax':[min(x['after_latency_percent']for x in filtered),max(x['after_latency_percent']for x in filtered)]}
 (HERE/'comparison-inventory.json').write_text(json.dumps(inventory,indent=2)+'\n');print(json.dumps({'inventory':inventory,'combined_vs_candidate':[{k:x[k]for k in('threads','case','role','after_latency_percent','range_class','after_faster_rounds','paired_median_latency_percent')}for x in rows if x['comparison']=='combined_vs_candidate'],'remaining_C_slower':[x for x in negative if x['comparison']=='original_vs_candidate'],'runtime':{t:x['runtime']for t,x in r['results'].items()},'corpus':r['corpus']},indent=2))
if __name__=='__main__':main()
