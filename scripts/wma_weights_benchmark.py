"""Bounded WMA experiment: same-job Rust three-arm and separate generated-C pair."""
import argparse
import hashlib
import itertools
import json
import math
import os
from pathlib import Path
import platform
import shutil
import statistics
import struct
import subprocess
import sys
import time
import re

BASELINE = 'ccd3172940ed1d9daa4e7197f2265810852e8910'
CANDIDATE = '220eb7bafcc5f409799f7902809200c0479a12bb'
ORIGINAL = '62021c1d14ef5499505af5547384cab509adf3fc'
PRIMARY = ('original', 'baseline', 'candidate')
C_PAIR = ('baseline-c', 'candidate-c')
ARMS = PRIMARY + C_PAIR
CASES = tuple([('wma',p,1000000) for p in (2,3,14,30,200,1000)] + [('wma',14,n) for n in (100,10000)] + [('mavp',30,n) for n in (100,10000,1000000)] + [('stream',14,10000),('bank',30,10000),('ema',14,1000000),('add',0,1000000)])
ORDERS = tuple(itertools.permutations(PRIMARY))*2
C_ORDERS = (C_PAIR,C_PAIR[::-1])*6
CANARY = 0x7ff80000000055aa
HERE = Path(__file__).resolve().parent
PROOF = HERE.parent/'tests/data/wma-weights'


def need(v, why):
    if not v: raise ValueError(why)


def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''): h.update(b)
    return h.hexdigest()


def read_json(text):
    def pairs(items):
        d={}
        for k,v in items:
            need(k not in d,'duplicate JSON key');d[k]=v
        return d
    return json.loads(text,object_pairs_hook=pairs,parse_constant=lambda x:(_ for _ in ()).throw(ValueError('nonfinite JSON')))


def command(c,log,cwd=None,env=None,timeout=1800):
    c=list(map(str,c));Path(str(log)+'.command.json').write_text(json.dumps(c,indent=2)+'\n')
    with Path(log).open('w') as f: subprocess.run(c,cwd=cwd,env=env,stdout=f,stderr=subprocess.STDOUT,check=True,timeout=timeout)


def inventory(root):
    return {str(p):sha(p) for p in sorted(Path(root).rglob('*')) if p.is_file()}


def source(root,pin):
    need(subprocess.check_output(['git','-C',str(root),'rev-parse','HEAD'],text=True).strip()==pin,'source commit differs')
    need(not subprocess.check_output(['git','-C',str(root),'status','--porcelain']),'dirty source')
    return {'commit':pin,'tree':subprocess.check_output(['git','-C',str(root),'rev-parse','HEAD^{tree}'],text=True).strip()}


def source_scope(args):
    roots={a:getattr(args,a+'_source') for a in PRIMARY}
    records={a:source(roots[a],pin) for a,pin in zip(PRIMARY,(ORIGINAL,BASELINE,CANDIDATE))}
    frozen=read_json((PROOF/'source-freeze.json').read_text())
    need(frozen['commit']==CANDIDATE and frozen['base']==BASELINE,'freeze pins differ')
    changed=set(subprocess.check_output(['git','-C',str(roots['candidate']),'diff','--name-only',BASELINE,CANDIDATE],text=True).splitlines())
    need(changed==set(frozen['files']),'candidate scope differs')
    for name,digest in frozen['files'].items():need(sha(roots['candidate']/name)==digest,'candidate source hash differs')
    for name in ('ta_codegen/output/rust/library/src/ta_func/ema.rs','ta_codegen/output/rust/library/src/ta_func/add.rs','ta_codegen/output/rust/library/src/ta_func/mavp.rs','include/ta_func.h','src/ta_func/ta_func_stream_private.h','ABI.manifest','ABI.released'):
        need(sha(roots['baseline']/name)==sha(roots['candidate']/name),'unchanged control or ABI differs')
    return records


def runtime(version):
    need(platform.system()=='Linux' and platform.machine()=='x86_64','Linux x86_64 required')
    need(version in ('1.90.0','1.97.0'),'unapproved compiler')
    rust=subprocess.check_output(['rustc','--version','--verbose'],text=True)
    need(rust.startswith('rustc '+version+' '),'wrong Rust version')
    expected={'CARGO_PROFILE_RELEASE_OPT_LEVEL':'3','CARGO_PROFILE_RELEASE_LTO':'false' if version=='1.90.0' else 'thin','CARGO_PROFILE_RELEASE_CODEGEN_UNITS':'16' if version=='1.90.0' else '1','CARGO_PROFILE_RELEASE_DEBUG':'false','RUSTFLAGS':'','CARGO_ENCODED_RUSTFLAGS':'','CFLAGS':'','CXXFLAGS':''}
    need(all(os.environ.get(k)==v for k,v in expected.items()),'release profile differs')
    return {'rustc':rust,'cc':subprocess.check_output(['cc','--version'],text=True),'cargo':subprocess.check_output(['cargo','--version'],text=True),'cmake':subprocess.check_output(['cmake','--version'],text=True),'cpuinfo_stable':sorted(set(x for x in Path('/proc/cpuinfo').read_text().splitlines() if x.startswith(('model name','vendor_id','cpu family','model\t','stepping','flags')))),'platform':platform.platform(),'python':sys.version,'profile':expected,'tool_paths':{k:shutil.which(k) for k in ('rustc','cargo','cc','cmake','objdump','nm')}}


GATE_LOGS=frozenset(('protocol-tests.log','generator-tests.log','generator-clippy.log','library-tests-and-docs.log','library-clippy.log','regen-check.log','server-build.log','all-indicator-regtests.log'))


def gate_bindings():
    return {'controller/'+name:HERE/name for name in ('wma_weights_benchmark.py','wma_weights_fixtures.py','bench_wma_weights.rs','WMA_WEIGHTS_CI.md')} | {'controller/test_wma_weights_benchmark.py':HERE.parent/'tests/test_wma_weights_benchmark.py','workflow.yml':HERE.parent/'.github/workflows/wma-weights.yml'}


def gate_record(out):
    p=out/'source-gates/source-gates.json';g=read_json(p.read_text())
    need(g['complete'] is True and g['candidate']==CANDIDATE and g['toolchain']=='1.97.0' and g['library_msrv']=='1.88','source gates incomplete/wrong pin or MSRV')
    need(g['source_files']==read_json((PROOF/'source-freeze.json').read_text())['files'],'gate source freeze differs')
    need(set(g['logs'])==GATE_LOGS,'source gate log inventory differs')
    for name,digest in g['logs'].items():
        need((p.parent/name).is_file() and (p.parent/name).stat().st_size>0,'source gate log missing/empty')
        need(sha(p.parent/name)==digest,'gate log changed')
    controller_commit=subprocess.check_output(['git','-C',str(HERE.parent),'rev-parse','HEAD'],text=True).strip()
    need((p.parent/'controller-commit.txt').read_text().strip()==controller_commit,'source gate controller commit differs')
    need((p.parent/'candidate-status.txt').is_file() and (p.parent/'candidate-status.txt').read_bytes()==b'','source gate candidate status missing/dirty')
    bindings={}
    for name,canonical in gate_bindings().items():
        need(sha(p.parent/name)==sha(canonical),'source gate controller/workflow bytes differ')
        bindings[name]=sha(canonical)
    return {'sha256':sha(p),'record':g,'controller_commit':controller_commit,'controller_bindings':bindings}


def fixture(out,n):
    # Exact dyadic physical input: independent of libm, RNG, and language.
    path=out/f'input-{n}.bin'
    arrays=([64.+((i%37)-18)*.125 for i in range(n)],[[2.,7.,14.,30.][i%4] for i in range(n)],[32.+((i%11)-5)*.0625 for i in range(n)])
    with path.open('wb') as f:
        f.write(b'WMAFIX01'+struct.pack('<Q',n))
        for a in arrays:
            for x in a:f.write(struct.pack('<d',x))
    return {'path':str(path),'sha256':sha(path),'bytes':path.stat().st_size,'finite':True,'period_cycle':[2,7,14,30]}


def assembly_scopes(assembly):
    sections={};name=None
    for line in assembly.splitlines():
        if line.endswith('>:'):
            name=line.split(' <',1)[-1][:-2]
            lower=name.lower()
            selected=('ta_lib::ta_func::wma::' in lower or 'core>::wma' in lower or 'wmastream>::' in lower or 'wmastream::' in lower or lower.startswith(('ta_wma','ta_mavp')))
            if selected:sections[name]=[]
            else:name=None
        if name is not None:sections[name].append(line)
    need(sections,'WMA scope missing from actual normal ELF')
    return sections


def normal_elf(binary,out):
    """Retain the actual timed product ELF and scoped WMA assembly, never a probe build."""
    need(binary.read_bytes()[:4]==b'\x7fELF','normal product is not ELF')
    out.mkdir(parents=True,exist_ok=True)
    symbols=subprocess.check_output(['nm','-S','-C',str(binary)],text=True)
    assembly=subprocess.check_output(['objdump','-d','-C',str(binary)],text=True)
    (out/'symbols.txt').write_text(symbols);(out/'assembly.txt').write_text(assembly)
    sections=assembly_scopes(assembly)
    (out/'wma-scope.txt').write_text('\n'.join(line for lines in sections.values() for line in lines)+'\n')
    roles={name:{'assembly_lines':len(lines),'punpckldq':sum('punpckldq' in line for line in lines),'integer_to_double':sum(bool(re.search(r'\bcvtsi2sd',line)) for line in lines)} for name,lines in sections.items()}
    return {'binary_sha256':sha(binary),'files':inventory(out),'scoped_symbols':roles,'role':'actual normal timed product; static mechanism diagnostic, no throughput inference'}


def build(args):
    out=args.output;out.mkdir(parents=True,exist_ok=True)
    need(args.candidate_commit==CANDIDATE,'candidate pin differs')
    records=source_scope(args);rt=runtime(args.rust_version);gates=gate_record(out)
    shutil.copytree(PROOF,out/'proof')
    (out/'bin').mkdir(exist_ok=True);(out/'archives').mkdir(exist_ok=True)
    libs={};cconfigs={}
    for arm,source_arm in (('original','original'),('baseline-c','baseline'),('candidate-c','candidate')):
        b=out/(arm+'-build');install=out/(arm+'-install')
        commands=[['cmake','-S',getattr(args,source_arm+'_source'),'-B',b,'-DCMAKE_BUILD_TYPE=Release','-DBUILD_SHARED_LIBS=OFF','-DBUILD_STATIC_LIBS=ON','-DBUILD_DEV_TOOLS=OFF','-DCMAKE_POSITION_INDEPENDENT_CODE=ON','-DCMAKE_EXPORT_COMPILE_COMMANDS=ON','-DCMAKE_C_FLAGS_RELEASE=-O3 -DNDEBUG -ffp-contract=off','-DCMAKE_INSTALL_PREFIX='+str(install)],['cmake','--build',b,'--target','install','--parallel','4']]
        for i,c in enumerate(commands):command(c,out/f'{arm}-c-build-{i}.log')
        lib=install/'lib/libta-lib.a';need(lib.is_file(),'C static library missing');libs[arm]=lib
        cconfigs[arm]={'library':str(lib),'sha256':sha(lib),'cache':str(b/'CMakeCache.txt'),'cache_sha256':sha(b/'CMakeCache.txt'),'compile_commands':str(b/'compile_commands.json'),'compile_commands_sha256':sha(b/'compile_commands.json'),'commands':list(map(lambda c:list(map(str,c)),commands))}
    binaries={}
    common=['rustc','--edition=2021','-O','-C','lto='+('false' if args.rust_version=='1.90.0' else 'thin'),'-C','codegen-units='+('16' if args.rust_version=='1.90.0' else '1'),'-Dwarnings','--check-cfg=cfg(c_reference,test)',str(HERE/'bench_wma_weights.rs'),'-Csave-temps']
    for arm in ARMS:
        binary=out/'bin'/arm
        if arm in libs:
            c=common+['--cfg','c_reference','-L','native='+str(libs[arm].parent),'-l','static=ta-lib','-l','m','-o',str(binary)]
        else:
            target=out.parent/('wma-target-'+args.rust_version)/arm
            env=os.environ.copy();env['CARGO_BUILD_BUILD_DIR']=str(target/'build-dir')
            command(['cargo','build','--release','--locked','-vv','-p','ta-lib','--manifest-path',getattr(args,arm+'_source')/'ta_codegen/output/rust/Cargo.toml','--target-dir',target],out/(arm+'-cargo.log'),env=env)
            retained=out/'libraries'/arm;retained.mkdir(parents=True);lib=target/'release/libta_lib.rlib';shutil.copyfile(lib,retained/'libta_lib.rlib')
            shutil.copytree(target/'release/.fingerprint',retained/'fingerprints')
            # Keep library normal objects/provenance as well as timed executable.
            c=common+['-L','dependency='+str(target/'release/deps'),'-L','dependency='+str(target/'build-dir/release/deps'),'--extern','ta_lib='+str(retained/'libta_lib.rlib'),'-o',str(binary)]
        command(c,out/(arm+'-harness.log'))
        tc=c[:-2]+['--test','-o',str(binary)+'-tests'];command(tc,out/(arm+'-cli-build.log'));command([str(binary)+'-tests','--test-threads=1'],out/(arm+'-cli-tests.log'))
        description=read_json(subprocess.check_output([binary,'--describe'],text=True))
        need(description['c_reference']==(arm in libs),'harness implementation differs')
        if arm in libs:need(description['version'].startswith('0.8.3' if arm=='original' else '0.8.4'),'C version differs')
        binaries[arm]={'path':str(binary),'sha256':sha(binary),'test_path':str(binary)+'-tests','test_sha256':sha(str(binary)+'-tests'),'description':description,'command':c,'elf':normal_elf(binary,out/'normal-codegen'/arm)}
    inputs={str(n):fixture(out,n) for n in (100,10000,1000000)}
    for arm in PRIMARY:
        dest=out/'archives'/(arm+'.tar.gz');subprocess.run(['git','-C',str(getattr(args,arm+'_source')),'archive','--format=tar.gz','-o',str(dest),'HEAD'],check=True)
    p={'pins':{'original':ORIGINAL,'baseline':BASELINE,'candidate':CANDIDATE},'sources':records,'runtime':rt,'source_gates':gates,'binaries':binaries,'c_builds':cconfigs,'inputs':inputs,'retained_libraries':inventory(out/'libraries'),'archives':inventory(out/'archives'),'controller':{str(p):sha(p) for p in (HERE/'wma_weights_benchmark.py',HERE/'wma_weights_fixtures.py',HERE/'bench_wma_weights.rs')},'proof':inventory(out/'proof')}
    (out/'build-provenance.json').write_text(json.dumps(p,indent=2)+'\n')
    verify(args,p)


def verify(args,p):
    need(args.candidate_commit==CANDIDATE,'candidate differs')
    need(p['sources']==source_scope(args) and p['runtime']==runtime(args.rust_version),'source/runtime differs')
    need(p['source_gates']==gate_record(args.output),'source gates changed')
    need(p['retained_libraries']==inventory(args.output/'libraries') and p['archives']==inventory(args.output/'archives'),'retained products changed')
    need(p['proof']==inventory(args.output/'proof'),'retained proof changed')
    need({Path(k).name:v for k,v in p['proof'].items()}=={Path(k).name:v for k,v in inventory(PROOF).items()},'controller proof changed')
    for f,h in p['controller'].items():need(sha(f)==h,'controller changed')
    for r in p['binaries'].values():
        need(sha(r['path'])==r['sha256'] and sha(r['test_path'])==r['test_sha256'],'binary changed')
        for f,h in r['elf']['files'].items():need(sha(f)==h,'ELF evidence changed')
    for r in p['c_builds'].values():
        for f,h in [('library','sha256'),('cache','cache_sha256'),('compile_commands','compile_commands_sha256')]:need(sha(r[f])==r[h],'C product/config changed')
    for r in p['inputs'].values():need(sha(r['path'])==r['sha256'],'physical input changed')


def compare_words(a,b):
    need(len(a)==len(b) and len(a)%8==0,'word array length differs')
    deltas=0
    for at in range(0,len(a),8):
        if a[at:at+8]!=b[at:at+8]:
            av,bv=struct.unpack('<d',a[at:at+8])[0],struct.unpack('<d',b[at:at+8])[0]
            need(math.isnan(av) and math.isnan(bv),'finite/signed-zero/Inf bits or NaN positions differ')
            deltas+=1
    return deltas


def contract_compare(a,b):
    ai=(a/'index.tsv').read_bytes();need(ai==(b/'index.tsv').read_bytes(),'contract shape/index differs')
    rows=ai.decode().splitlines();need(len(rows)==1966,'contract inventory differs')
    deltas=0;words=0;events=0
    for line in rows:
        id,code,beg,count,size=line.split('\t');count=int(count);size=int(size)
        av=(a/(id+'.bin')).read_bytes();bv=(b/(id+'.bin')).read_bytes();need(len(av)==len(bv)==size*8,'contract size differs')
        ae=(a/(id+'.events')).read_bytes();need(ae==(b/(id+'.events')).read_bytes(),'stream events differ')
        if not ae:
            need(av[count*8:]==bv[count*8:]==struct.pack('<Q',CANARY)*(size-count),'contract tails differ')
            deltas+=compare_words(av[:count*8],bv[:count*8])
        else:
            deltas+=compare_words(av,bv);events+=len(ae.splitlines())
        words+=size
    return {'cases':len(rows),'words':words,'events':events,'NaN_representation_deltas':deltas,'finite_zero_Inf_tolerance':0}


def capture(path,case):
    kind,p,n=case;b=0 if kind=='add' else p-1;count=n-b
    d=Path(path).read_bytes();need(len(d)==32+8*(n+8) and d[:8]==b'WMAOUT01','capture shape/magic differs')
    need(struct.unpack('<QQQ',d[8:32])==(n,b,count),'range differs')
    need(d[32+count*8:]==struct.pack('<Q',CANARY)*(n+8-count),'raw tail differs')
    need(all(math.isfinite(x[0]) for x in struct.iter_unpack('<d',d[32:32+count*8])),'timed output is nonfinite')
    return d


def validate_sample(s,case):
    k,p,n=case;iters={100:1000,10000:10,1000000:1}[n]
    need(set(s)=={'case','n','iterations','repeats','warmups','checked_values','samples_ms'},'sample keys differ')
    need(type(s['n'])is int and s['n']==n and type(s['iterations'])is int and s['iterations']==iters,'sample inputs differ')
    need(s['case']==f'{k}_{p}_{n}' and type(s['repeats'])is int and s['repeats']==31 and type(s['warmups'])is int and s['warmups']==5,'sample protocol differs')
    need(type(s['checked_values'])is int and s['checked_values']==n-(0 if k=='add' else p-1),'sample values differ')
    need(isinstance(s['samples_ms'],list) and len(s['samples_ms'])==31 and all(type(x)in(int,float) and math.isfinite(x) and x>0 for x in s['samples_ms']),'invalid timing samples')


def distribution(v):
    s=sorted(v);return {'median':statistics.median(s),'min':s[0],'max':s[-1],'p10':s[int((len(s)-1)*.1)],'p90':s[int((len(s)-1)*.9)],'count':len(s)}


def report(records):
    results=[]
    for section,pairs in [('primary',(('baseline','original'),('candidate','baseline'),('candidate','original'))),('C-pair',(('candidate-c','baseline-c'),))]:
        for case in CASES:
            name='_'.join(map(str,case));rows=[r for r in records if r['section']==section and r['case']==name]
            for numerator,denominator in pairs:
                a=[r for r in rows if r['arm']==numerator];b=[r for r in rows if r['arm']==denominator]
                need(len(a)==len(b)==12,'process inventory incomplete')
                am={r['round']:statistics.median(r['samples_ms']) for r in a};bm={r['round']:statistics.median(r['samples_ms']) for r in b}
                ratios=[am[i]/bm[i] for i in range(12)];spread=distribution(ratios)
                # Conservative descriptive label, not an inferential significance claim.
                label='consistent slower' if spread['p10']>1.03 else 'consistent faster' if spread['p90']<.97 else 'noise/small or mixed'
                results.append({'section':section,'case':name,'ratio':numerator+'/'+denominator,'paired_process_median_ratios':ratios,'ratio_distribution':spread,'numerator_ms':distribution([x for r in a for x in r['samples_ms']]),'denominator_ms':distribution([x for r in b for x in r['samples_ms']]),'classification':label})
    return results


def run(args):
    out=args.output;p=read_json((out/'build-provenance.json').read_text());verify(args,p)
    cpu=min(os.sched_getaffinity(0));os.sched_setaffinity(0,{cpu});need(os.sched_getaffinity(0)=={cpu},'affinity failed')
    contract=out/'contract-fixtures';command([sys.executable,HERE/'wma_weights_fixtures.py',contract],out/'contract-fixtures.log')
    comparisons={}
    for arm in ARMS:
        command([p['binaries'][arm]['path'],'--contract',contract,out/('contract-'+arm)],out/(arm+'-contract.log'))
        comparisons[arm]=contract_compare(out/'contract-original',out/('contract-'+arm))
    (out/'correctness.json').write_text(json.dumps(comparisons,indent=2)+'\n')
    gold=out/'goldens';gold.mkdir(exist_ok=True)
    for case in CASES:
        name='_'.join(map(str,case))
        for arm in ARMS:
            path=gold/(name+'-'+arm+'.bin')
            command([p['binaries'][arm]['path'],name,p['inputs'][str(case[2])]['path'],path,'--capture-only','typed'],out/(name+'-'+arm+'-capture.log'))
            d=capture(path,case)
            if arm!='original':need(d==capture(gold/(name+'-original.bin'),case),'finite timed arms differ exactly')
    golden_hashes=inventory(gold);records=[];raw=out/'raw';raw.mkdir(exist_ok=True)
    deadline=time.monotonic()+3600
    for section,orders in [('primary',ORDERS),('C-pair',C_ORDERS)]:
        for round,order in enumerate(orders):
            for case in CASES:
                name='_'.join(map(str,case))
                for position,arm in enumerate(order):
                    need(time.monotonic()<deadline,'one-hour measurement deadline exceeded; partial raw evidence retained')
                    label=f'{section}-{round:02d}-{name}-{arm}';dest=raw/(label+'.bin');log=raw/(label+'.log');expected=gold/(name+'-'+arm+'.bin')
                    command([p['binaries'][arm]['path'],name,p['inputs'][str(case[2])]['path'],dest,'--golden',expected,'typed'],log,timeout=min(120,max(1,deadline-time.monotonic())))
                    sample=read_json(log.read_text());validate_sample(sample,case);need(dest.read_bytes()==expected.read_bytes(),'post-timing own-arm output differs')
                    r={**sample,'section':section,'round':round,'position':position,'arm':arm,'output_sha256':sha(dest),'golden_sha256':sha(expected),'input_sha256':p['inputs'][str(case[2])]['sha256'],'binary_sha256':p['binaries'][arm]['sha256']}
                    # Each child validates every sample; preserve one final output per child, not every array.
                    records.append(r);(raw/(label+'.json')).write_text(json.dumps(r,indent=2)+'\n')
            print(section,round+1,'/12 complete',flush=True)
    need(len(records)==900 and sum(len(r['samples_ms']) for r in records)==27900,'final child/sample inventory differs')
    need(inventory(gold)==golden_hashes,'golden changed');verify(args,p)
    result={'rust_version':args.rust_version,'affinity_cpu':cpu,'processes':len(records),'samples':27900,'cases':15,'correctness':comparisons,'goldens':golden_hashes,'rows':report(records),'limitations':['Kernel and real public stream update measurements only; no Polars over/query speed claim.','Stream open/clone/reset/drop allocations excluded for every arm; timed updates only.','Fresh process paired medians and descriptive noise labels; no independent-host inference.','Full output serialization and correctness checks occur between samples outside the timer; their cache and allocator effects are shared protocol costs.','One final raw output per child and own-arm golden; every timed sample validated in memory, arrays not duplicated per sample.','Java and C# generated source runtime/performance unverified.','Compiler profiles are separate experiments and must never be pooled.']}
    (out/'comparison.json').write_text(json.dumps(result,indent=2)+'\n')
    lines=[f'WMA exact-weight experiment: Rust {args.rust_version}', '', 'Ratio <1 means lower latency. All15 cases reported; descriptive spread is across12 paired fresh-process medians. Separate compiler jobs are not pooled.', '', '|Section|Case|Ratio|Median|p10–p90|min–max|Assessment|','|---|---|---|---:|---|---|---|']
    for r in result['rows']:
        s=r['ratio_distribution'];lines.append(f"|{r['section']}|{r['case']}|{r['ratio']}|{s['median']:.4f}|{s['p10']:.4f}–{s['p90']:.4f}|{s['min']:.4f}–{s['max']:.4f}|{r['classification']}|")
    lines.extend(['','Limitations:']+['- '+x for x in result['limitations']]);(out/'comparison.md').write_text('\n'.join(lines)+'\n')


def main():
    ap=argparse.ArgumentParser()
    for arm in PRIMARY:ap.add_argument('--'+arm+'-source',type=Path,required=True)
    ap.add_argument('--candidate-commit',required=True);ap.add_argument('--rust-version',required=True,choices=('1.90.0','1.97.0'));ap.add_argument('--output',type=Path,required=True);ap.add_argument('--build-only',action='store_true')
    args=ap.parse_args();args.output=args.output.resolve()
    for arm in PRIMARY:setattr(args,arm+'_source',getattr(args,arm+'_source').resolve())
    if args.build_only:build(args)
    else:run(args)

if __name__=='__main__':main()
