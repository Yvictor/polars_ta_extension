"""List every candidate-vs-C case, including small/noisy slow medians.

Envelopes describe process spread. Six balanced rounds do not establish formal
statistical significance across this many comparisons; flagged cases are leads
for paired confirmation and profiling, never universal speed claims.
"""
import json
from pathlib import Path


def inventory(report):
    rows = []
    for threads, data in report['results'].items():
        for name, values in data['comparisons']['original_vs_candidate'].items():
            prior = data['comparisons']['original_vs_prior'][name]
            delivered = data['comparisons']['prior_vs_candidate'][name]
            change = values['candidate_median_ms']/values['baseline_median_ms']-1
            lo, hi = values['ratio_envelope']
            category = ('consistent slower >5% on this runner' if hi < 1/1.05 else
                        'consistent small slower on this runner' if hi < 1 else
                        'slow median, process ranges overlap' if change > 0 else
                        'not slower by median')
            control = ('control_cumsum/'+name.split('/',1)[1] if name.startswith('grouped_') else
                       'control_cumsum_dense/'+name.split('/',1)[1])
            ctrl = data['comparisons']['original_vs_candidate'].get(control)
            rows.append({'threads':int(threads),'case':name,'category':category,
                         'original_median_ms':values['baseline_median_ms'],
                         'delivered_median_ms':prior['candidate_median_ms'],
                         'candidate_median_ms':values['candidate_median_ms'],
                         'candidate_vs_C_percent':change*100,
                         'original_over_candidate_paired_ratio':values['median_paired_ratio'],
                         'original_over_candidate_envelope':[lo,hi],
                         'delivered_over_candidate_paired_ratio':delivered['median_paired_ratio'],
                         'delivered_over_candidate_envelope':delivered['ratio_envelope'],
                         'original_process_medians_ms':values['baseline_process_medians_ms'],
                         'candidate_process_medians_ms':values['candidate_process_medians_ms'],
                         'matching_polars_control':control if ctrl else None,
                         'control_ratio_envelope':ctrl['ratio_envelope'] if ctrl else None})
    return sorted(rows,key=lambda r:(r['threads'],-r['candidate_vs_C_percent']))


def write_inventory(path):
    report = json.loads(path.read_text()); rows = inventory(report)
    result = {'commits':next(iter(report['results'].values()))['commits'],
              'limitation':'Descriptive process ranges, not confidence intervals or multiple-comparison significance. Every median slower than C is listed, even if noisy.',
              'rows':rows}
    (path.parent/'regression-inventory.json').write_text(json.dumps(result,indent=2)+'\n')
    lines=['# Per-scenario C regression inventory','',result['limitation'],'',
           '| Threads | Case | C ms | Delivered ms | Candidate ms | Candidate vs C | C/candidate envelope | Assessment |',
           '| ---: | --- | ---: | ---: | ---: | ---: | --- | --- |']
    for row in rows:
        if row['candidate_vs_C_percent'] <= 0: continue
        lo,hi=row['original_over_candidate_envelope']
        lines.append(f"| {row['threads']} | {row['case']} | {row['original_median_ms']:.4f} | {row['delivered_median_ms']:.4f} | {row['candidate_median_ms']:.4f} | {row['candidate_vs_C_percent']:+.2f}% | {lo:.3f}–{hi:.3f} | {row['category']} |")
    (path.parent/'regression-inventory.md').write_text('\n'.join(lines)+'\n')
    return rows


if __name__ == '__main__':
    import sys
    write_inventory(Path(sys.argv[1]))
