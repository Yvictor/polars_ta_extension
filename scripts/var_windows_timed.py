"""Exact16-case matched opaque public-call experiment; no clock mode before ELF gate."""
import argparse,gzip,itertools,json,math,os,statistics,time
from pathlib import Path
import var_windows_preflight as P
HERE=Path(__file__).resolve().parent
ARMS=('original','baseline','candidate')
ORDERS=tuple(itertools.permutations(ARMS))*2


def relative_file(out,name):
    p=Path(name)
    P.need(not p.is_absolute() and '..' not in p.parts,'unsafe gate relative file')
    result=(out/p).resolve();P.need(result.is_relative_to(out.resolve()),'gate file escapes output')
    return result


def require_gate(out,version,p):
    path=out/'enabled-elf-gate.json';g=P.read_json(path.read_text())
    P.need(g['timing_allowed'] is True,'actual enabled executable proof missing/rejected')
    P.need(g['rust_version']==version and g['preflight_sha256']==P.sha(out/'preflight.json'),'gate profile/preflight differs')
    P.need(g['source_commits']==p['pins'] and g['profile']==p['runtime']['profile'],'gate source/profile differs')
    P.need(g['binary_sha256']=={a:p['binaries'][a]['sha256'] for a in ARMS},'gate binary identities differ')
    P.need(g['codegen_module_sha256']==P.sha(HERE/'var_windows_codegen.py'),'gate module changed')
    P.need(g['reference_sha256']==P.sha(HERE.parent/'tests/data/var-windows/normal-codegen-reference.json'),'gate reference changed')
    P.need(isinstance(g['files'],dict) and bool(g['files']),'gate evidence inventory empty')
    for name,digest in g['files'].items():P.need(P.sha(relative_file(out,name))==digest,'gate evidence changed')
    for a in ARMS:
        P.need(P.sha(p['binaries'][a]['path'])==g['binary_sha256'][a],'enabled binary changed')
        d=p['binaries'][a]['description'];P.need(d['timing_enabled'] is True and d['opaque_fnptr'] is True and d['pointer_bytes']==8,'enabled matched pointer route differs')
    P.need(p['timer_body_compiled'] is True and p['timings_collected'] is False,'preflight is not before timers')
    return g,P.sha(path)


def stable_cpu(text):
    return sorted(set(line for line in text.splitlines() if line.startswith(('model name','vendor_id','cpu family','model\t','stepping','flags'))))


def verify_state(args,p):
    out=args.output;spec=P.specification();expected=P.pins(spec)
    roots={a:getattr(args,a+'_source').resolve() for a in ARMS}
    P.need(p['pins']==expected and p['sources']==P.source_scope(roots,expected),'source changed')
    current=P.runtime(args.rust_version)
    for key in ('rustc','profile','platform','python','cc'):P.need(current[key]==p['runtime'][key],'runtime/compiler profile changed')
    P.need(stable_cpu(current['cpuinfo'])==stable_cpu(p['runtime']['cpuinfo']),'CPU model/features changed')
    P.need(p['source_gates']==P.gate_record(out,expected),'source gates changed')
    for name,digest in p['controller'].items():P.need(P.sha(HERE/name)==digest,'controller changed')
    for name,digest in p['source_archives'].items():P.need(P.sha(out/'source-archives'/name)==digest,'source archive changed')
    for arm,b in p['builds'].items():
        if arm=='original':
            P.need(P.sha(b['archive'])==b['archive_sha256'] and P.sha(b['shared'])==b['shared_sha256'],'C083 build changed')
        else:P.need(P.sha(b['rlib'])==b['sha256'],'native library changed')
    for r in p['inputs'].values():P.need(P.sha(r['path'])==r['sha256'],'physical input changed')
    names=set()
    for c in spec['cases']:
        prior=None
        for arm in ARMS:
            name=c['name']+'-'+arm+'.bin';names.add(name);path=out/'goldens'/name
            P.need(P.sha(path)==p['goldens'][name],'golden changed')
            raw=P.capture(path,c)
            if prior is not None:P.need(raw==prior,'golden arms differ')
            prior=raw
    P.need(names==set(p['goldens']),'48 golden inventory differs')
    return spec


def sample_record(value,c):
    P.need(set(value)=={'case','n','iterations','repeats','warmups','checked_values','samples_ms'},'sample fields differ')
    P.need(value['case']==c['name'],'sample case differs')
    want={'n':c['rows'],'iterations':c['iterations'],'repeats':31,'warmups':5,'checked_values':c['rows']-(0 if c['function']=='add' else c['period']-1)}
    P.need(all(type(value[k]) is int and value[k]==v for k,v in want.items()),'sample metadata differs')
    v=value['samples_ms'];P.need(isinstance(v,list) and len(v)==31 and all(type(x)in(int,float) and math.isfinite(x) and x>0 for x in v),'invalid31-sample distribution')


def distribution(values):
    x=sorted(values);return dict(count=len(x),median=statistics.median(x),min=x[0],max=x[-1],p10=x[int((len(x)-1)*.1)],p90=x[int((len(x)-1)*.9)])


def comparisons(records,spec):
    result=[]
    for c in spec['cases']:
        rows=[r for r in records if r['case']==c['name']]
        for a,b in (('baseline','original'),('candidate','baseline'),('candidate','original')):
            aa={r['round']:r for r in rows if r['arm']==a};bb={r['round']:r for r in rows if r['arm']==b};P.need(set(aa)==set(bb)==set(range(12)),'incomplete paired rounds')
            ratios=[statistics.median(aa[i]['samples_ms'])/statistics.median(bb[i]['samples_ms']) for i in range(12)];spread=distribution(ratios)
            label='paired-ratio p10>1.03' if spread['p10']>1.03 else 'paired-ratio p90<0.97' if spread['p90']<.97 else 'small or mixed; inspect all pairs'
            result.append(dict(case=c['name'],ratio=a+'/'+b,paired_process_median_ratios=ratios,ratio_distribution=spread,faster_pairs=sum(v<1 for v in ratios),slower_pairs=sum(v>1 for v in ratios),numerator_process_medians_ms=[statistics.median(aa[i]['samples_ms']) for i in range(12)],denominator_process_medians_ms=[statistics.median(bb[i]['samples_ms']) for i in range(12)],numerator_process_distribution_ms=distribution([statistics.median(aa[i]['samples_ms']) for i in range(12)]),denominator_process_distribution_ms=distribution([statistics.median(bb[i]['samples_ms']) for i in range(12)]),duration_unit='whole iteration-batch milliseconds',iterations_per_sample=c['iterations'],numerator_pooled_sample_ms=distribution([v for r in aa.values() for v in r['samples_ms']]),denominator_pooled_sample_ms=distribution([v for r in bb.values() for v in r['samples_ms']]),description=label))
    P.need(len(result)==48,'all48 comparisons required')
    return result


def compress_complete(path,expected):
    raw=path.read_bytes();P.need(raw==expected,'post-timer output differs from own golden')
    compressed=path.with_suffix(path.suffix+'.gz');P.need(not compressed.exists(),'do not overwrite child output')
    compressed.write_bytes(gzip.compress(raw,compresslevel=6,mtime=0))
    P.need(gzip.decompress(compressed.read_bytes())==raw,'lossless output retention failed')
    record=dict(path=str(compressed),raw_bytes=len(raw),raw_sha256=P.sha(path),gzip_sha256=P.sha(compressed))
    path.unlink() # Only this just-created child duplicate; every byte remains in lossless gzip.
    return record


def run(args):
    out=args.output;p=P.read_json((out/'preflight.json').read_text());P.need(not (out/'comparison.json').exists(),'refuse completed output overwrite')
    gate,gate_hash=require_gate(out,args.rust_version,p) # Must precede any clock-mode argv.
    cpu=p['affinity_cpu'];P.need(type(cpu) is int and cpu in os.sched_getaffinity(0),'affinity CPU unavailable')
    os.sched_setaffinity(0,{cpu});P.need(os.sched_getaffinity(0)=={cpu},'affinity failed')
    spec=verify_state(args,p);raw=out/'timed-raw';raw.mkdir();records=[];deadline=time.monotonic()+5400
    for round,order in enumerate(ORDERS):
        for c in spec['cases']:
            key=f"{c['rows']}-{c['pattern']}";input=p['inputs'][key]
            for position,arm in enumerate(order):
                P.need(time.monotonic()<deadline,'90-minute bound exceeded; partial raw records retained')
                label=f"{round:02d}-{c['name']}-{arm}";dest=raw/(label+'.bin');log=raw/(label+'.log');golden=out/'goldens'/(c['name']+'-'+arm+'.bin')
                # Same enabled executable verified above, fresh child selected case before prewarmup.
                P.command([p['binaries'][arm]['path'],c['name'],input['path'],dest,'--golden',golden],log,timeout=min(120,max(1,deadline-time.monotonic())))
                value=P.read_json(log.read_text());sample_record(value,c);capture=compress_complete(dest,golden.read_bytes())
                row={**value,'round':round,'position':position,'arm':arm,'input_sha256':input['sha256'],'golden_sha256':p['goldens'][golden.name],'binary_sha256':p['binaries'][arm]['sha256'],'gate_sha256':gate_hash,'capture':capture}
                (raw/(label+'.json')).write_text(json.dumps(row,indent=2)+'\n');records.append(row)
        print(f'balanced round{round+1}/12 complete',flush=True)
    P.need(len(records)==576 and sum(len(x['samples_ms'])for x in records)==17856,'576 children/17856 samples required')
    P.need(require_gate(out,args.rust_version,p)==(gate,gate_hash),'actual ELF gate changed');verify_state(args,p)
    rows=comparisons(records,spec)
    limitations=['Raw durations are whole iteration batches:100 rows=1000 calls/sample,10000 rows=10,1000000 rows=1; per-call latency requires division by iterations.','Matched opaque public VAR/STDDEV function-pointer experiment; not a guarantee for direct/inlinable callers or Polars over.','Opaque SampleFn dispatch is outside Instant; actual enabled timer-loop/call graph is gated.','Existing uncast static artifacts remain valid numerics; they did not prove this controlled pointer route.','Both runtime profiles are separate experiments; no CPU/compiler pooling or compiler-only causal inference.','Preallocated buffers: allocation/initialization excluded from kernel interval; every sample fills poison before Instant.','Fresh child has own-arm exact prewarmup/final checks only; no intersample array serialization.','Every full final child array retained losslessly in gzip; all31 raw timing samples and commands retained.','Descriptive process-pair envelopes/counts only; no inferential confidence claim or ignored small losses.','Core text growth and newly guarded reseed scans remain possible costs; static check removal alone is not speed evidence.','C0.8.3 reference is distinct from consumer original C0.8.1.']
    result=dict(rust_version=args.rust_version,pins=p['pins'],runtime=p['runtime'],affinity_cpu=cpu,children=576,samples=17856,cases=16,gate_sha256=gate_hash,gate=gate,rows=rows,limitations=limitations)
    (out/'comparison.json').write_text(json.dumps(result,indent=2)+'\n')
    lines=[f"VAR matched opaque-call experiment Rust{args.rust_version}",'','Every case and C-relative loss is retained; ratio<1 means lower latency. Twelve paired process medians, not independent-host confidence.','','|Case|Ratio|Median|p10–p90|min–max|Faster/slower pairs|Description|','|---|---|---:|---|---|---:|---|']
    for r in rows:
        d=r['ratio_distribution'];lines.append(f"|{r['case']}|{r['ratio']}|{d['median']:.6f}|{d['p10']:.6f}–{d['p90']:.6f}|{d['min']:.6f}–{d['max']:.6f}|{r['faster_pairs']}/{r['slower_pairs']}|{r['description']}|")
    lines+=['','Limits:']+['- '+x for x in limitations];(out/'comparison.md').write_text('\n'.join(lines)+'\n')


def main():
    parser=argparse.ArgumentParser()
    for arm in ARMS:parser.add_argument('--'+arm+'-source',required=True,type=Path)
    parser.add_argument('--output',required=True,type=Path);parser.add_argument('--rust-version',required=True,choices=('1.90.0','1.97.0'))
    args=parser.parse_args();args.output=args.output.resolve();run(args)
if __name__=='__main__':main()
