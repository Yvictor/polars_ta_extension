"""Thin presentation of an already-approved independent SAREXT audit result."""
from pathlib import Path
import argparse,csv,hashlib,json,math
HERE=Path(__file__).parent
AUDITOR='761c29f8242cebc41a89627ccb7e758b610336ac5fb3c5c4cc9a187ca86b7e33'

def generate(result,folder):
 assert result['audit_pass']is True and result['children']==1344 and result['samples']==41664
 trust=json.loads((HERE/'trusted.json').read_text());assert result['pins']==trust['pins']and result['controller']==trust['controller']and result['run']==trust['run'];names=trust['case_manifest']['cases'];assert len(names)==14 and set(result['results'])=={'1','4'}
 assert hashlib.sha256((HERE/'audit.py').read_bytes()).hexdigest()==AUDITOR
 folder=Path(folder);folder.mkdir(exist_ok=True);rows=[];four=[]
 pairs=[a+'_vs_'+b for i,a in enumerate(('original','prior','candidate','alternative'))for b in ('original','prior','candidate','alternative')[i+1:]]
 for thread in ('1','4'):
  comparisons=result['results'][thread]['comparisons'];assert set(comparisons)==set(pairs)
  for pair in pairs:
   assert set(comparisons[pair])==set(names)
   for name in names:
    r=comparisons[pair][name];lo,hi=r['ratio_envelope'];change=(r['candidate_median_ms']/r['baseline_median_ms']-1)*100
    assert all(math.isfinite(x)for x in (lo,hi,change))and len(r['paired_ratios'])==12
    status='disjoint faster process ranges'if lo>1 else'disjoint slower process ranges'if hi<1 else'overlapping process ranges'
    rows.append({'threads':int(thread),'case':name,'role':trust['case_manifest']['case_roles'][name],'comparison':pair,'before_median_ms':r['baseline_median_ms'],'after_median_ms':r['candidate_median_ms'],'after_latency_percent':change,'before_over_after_low':lo,'before_over_after_high':hi,'after_faster_rounds':sum(x>1 for x in r['paired_ratios']),'status':status})
  for name in names:
   four.append({'threads':int(thread),'case':name,'C_ms':comparisons['original_vs_prior'][name]['baseline_median_ms'],'56_ms':comparisons['original_vs_prior'][name]['candidate_median_ms'],'A_ms':comparisons['original_vs_candidate'][name]['candidate_median_ms'],'B_ms':comparisons['original_vs_alternative'][name]['candidate_median_ms']})
 assert len(rows)==168 and len(four)==28
 outputs={'all168-pairwise-comparisons.csv':rows,'all28-four-arm-medians.csv':four,'all-slower-medians.csv':[r for r in rows if r['after_latency_percent']>0],'all-Polars-controls.csv':[r for r in rows if r['role']=='pure_polars_drift_control'],'all-replay-stress.csv':[r for r in rows if r['role']=='legitimate_long_zero_replay_stress']}
 for name,data in outputs.items():
  with(folder/name).open('w',newline='')as f:
   w=csv.DictWriter(f,fieldnames=list((data or rows)[0]),lineterminator='\n');w.writeheader();w.writerows(data)
 lines=['# Audited four-arm SAREXT comparison','',f'CI: https://github.com/Yvictor/polars_ta_extension/actions/runs/{result["run"]}',f'Controller: `{result["controller"]}`','',*[f'{key}: `{pin}`'for key,pin in result['pins'].items()],'','The same runner built all four release arms with Rust1.90, portable CPU flags and identical runtime settings. Each of14 selected queries has12 fresh processes per arm and thread setting,31 samples after5 warmups;1,344 children/41,664 samples. The one/four thread settings remain separate.','', 'All168 pairwise rows,28 four-arm median rows, every slower median, pure-Polars control and legitimate long-negative-zero replay stress are retained in CSV. A is typed Core plus scan/replay; B is the once-dispatched compatibility kernel. No means across workloads are used.','','| Threads | Case | C ms | 56 ms | A ms | B ms |','| ---: | --- | ---: | ---: | ---: | ---: |']
 for r in four:lines.append(f'| {r["threads"]} | {r["case"]} | {r["C_ms"]:.6f} | {r["56_ms"]:.6f} | {r["A_ms"]:.6f} | {r["B_ms"]:.6f} |')
 lines+=['','Process envelopes are descriptive observed ranges, not confidence intervals or a multiple-comparison significance test. Overlap limits speedup/regression conclusions; matched rounds and unchanged controls must be inspected. No ratios are pooled across runs, runners or thread settings. Positive latency change means the later arm is slower.','', 'Strict numerical gates and the explicitly scoped untimed C-target short-zero correction are independent of timing acceptance. Legitimate long-side negative zero is preserved. Process-wide fault counters do not isolate allocator costs. Raw final timed arrays are not archived separately; immutable source checks the final output against retained own-arm goldens.','', 'A local source/code-generation mechanism can motivate a change, but these consumer measurements do not isolate every setup/kernel/engine contribution. Remaining slower-than-C scenarios must be reported with their full distributions and noise status.']
 (folder/'REPORT.md').write_text('\n'.join(lines)+'\n')
 return {'rows':len(rows),'four_arm_rows':len(four),'slower_medians':len(outputs['all-slower-medians.csv']),'disjoint_slower':sum(r['status']=='disjoint slower process ranges'for r in rows),'disjoint_faster':sum(r['status']=='disjoint faster process ranges'for r in rows)}

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('result',type=Path);p.add_argument('--output',type=Path,required=True);a=p.parse_args();print(json.dumps(generate(json.loads(a.result.read_text()),a.output),indent=2))
