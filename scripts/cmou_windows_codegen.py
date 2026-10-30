"""Fail-closed actual normal Linux CMOU output-loop bounds-guard evidence.

The source-bound compatibility kernel has two input and one output check per
iteration (alternative output branches may produce four static guard sites).
This is bounded CFG/source evidence, not a complete ISA/data-flow proof.
"""
import hashlib,json,re,struct,subprocess
from pathlib import Path
from cmou_windows_cfg import need,sha,function_names,relocs,parse_instructions,target,cfg

PREFIX='_ZN13_polars_talib6compat4cmou'


def select_symbols(text,segments):
    found=set()
    for line in text.splitlines():
        m=re.match(r'\s*\d+:\s+([0-9a-fA-F]+)\s+(\d+)\s+(?:FUNC|IFUNC)\s+\S+\s+\S+\s+(\S+)\s+(\S+)',line)
        if m and m[3]!='UND' and int(m[2]):found.add((int(m[1],16),int(m[2]),m[4]))
    selected=[x for x in found if x[2].startswith(PREFIX) and 'CompatCore'in x[2] and re.search(r'4cmou17h[0-9a-f]+E$',x[2])]
    need(len(selected)==1,'unique normal CompatCore CMOU kernel missing/inlined/ambiguous')
    start,size,name=selected[0]
    need(any(lo<=start<start+size<=hi for lo,hi in segments),'CMOU symbol outside executable segment')
    for a,b,_ in found:need(not(start<a+b and a<start+size) or(start,size)==(a,b),'partially overlapping CMOU function')
    return start,size,name


def guard_count(rows,analysis,loop):
    """Count guards on every productive exit/backedge; exclude only empty exits."""
    by={a:(op,args)for a,op,args in rows};addresses=list(by);nexts=dict(zip(addresses,addresses[1:]));graph={a:[]for a in addresses};bad={int(a,16)for a in analysis['panic_sites']};group={int(a,16)for a in loop['addresses']}
    for a,op,args in rows:
        dest=target(args);nxt=nexts.get(a)
        if op.startswith('j'):
            if dest in by:graph[a].append(dest)
            if op not in('jmp','jmpq')and nxt is not None:graph[a].append(nxt)
        elif op not in('ret','retq','ud2','int3')and a not in bad and nxt is not None:graph[a].append(nxt)
    def panic_exit(node):
        todo=[node];seen=set()
        while todo:
            a=todo.pop()
            if a in bad:return True
            if a in group or a in seen:continue
            seen.add(a);todo.extend(graph[a])
        return False
    def reachable(starts,links):
        seen=set();todo=list(starts)
        while todo:
            a=todo.pop()
            if a in seen:continue
            seen.add(a);todo.extend(links[a])
        return seen
    reverse={a:[]for a in graph}
    for a,edges in graph.items():
        for b in edges:reverse[b].append(a)
    returns={a for a,(op,_)in by.items()if op in('ret','retq')}
    header=min(group);normal=reachable([header],graph)&reachable(returns|{header},reverse)
    entry_normal=reachable([rows[0][0]],graph)&reachable(returns|{header},reverse)
    # Narrow source/ABI role proof: this frozen x86_64 Rust1.90 signature uses
    # entry RDI as the Result<OutRange, RetCode> sret pointer. It must remain
    # reserved: no normal-path call, register use/copy/clobber or LEA alias.
    # Only memory addressing may mention RDI. This is deliberately stricter
    # than general register dataflow and fails unknown compiler reshaping.
    for a in entry_normal:
        op,args=by[a];without_memory=re.sub(r'[^,\s]*\([^)]*\)','MEM',args)
        need(not op.startswith(('call','rep','stos','scas','ins','outs','cmps'))and op not in('movsb','movsw','movsl','movsq')and not(op=='movsd'and not args),'unknown CMOU normal-path instruction clobbers sret role')
        need(not re.search(r'%(?:rdi|edi|di|dil)\b',without_memory),'CMOU entry sret register copied/clobbered')
        need(not(op.startswith('lea')and re.search(r'%(?:rdi|edi|di|dil)\b',args)),'CMOU entry sret alias unsupported')
    guards={a for a in normal if by[a][0].startswith('j')and by[a][0]not in('jmp','jmpq')and any(b not in normal and panic_exit(b)for b in graph[a])}
    # Source-bound output forms in this recurrence: one scalar f64 store,
    # including the alternative immediate 64-bit zero store. Unknown nonstack
    # stores fail rather than being silently excluded from productive paths.
    stores=set();frame=any(op.startswith('mov')and re.fullmatch(r'%rsp,\s*%rbp',args)for _,op,args in rows)
    for a in normal:
        op,args=by[a]
        # Indexed operands contain commas, so match the complete trailing memory
        # operand rather than splitting the address components.
        memory=re.search(r',\s*([^,]*\([^)]*\))\s*$',args)
        if not memory or '%rsp'in memory[1]or(frame and'%rbp'in memory[1]):continue
        source=args[:memory.start()].strip()
        scalar=op in('movsd','vmovsd')and re.fullmatch(r'%xmm\d+',source)
        zero=op=='movq'and re.fullmatch(r'\$(?:0x)?0+',source)
        if scalar or zero:
            need(not re.search(r'%(?:rdi|edi|di|dil)\b',memory[1]),'CMOU output aliases entry sret pointer')
            stores.add(a)
        elif a in group or op.startswith(('movsd','vmovsd','movupd','vmovupd','movapd','vmovapd')):
            need(False,'unsupported CMOU nonstack output-store form')
        else:
            # Only typed Result<OutRange, RetCode> return metadata is allowed
            # outside the SCC: two usize fields at rdi+8/+16 and u16 status.
            metadata=(op=='movq'and re.fullmatch(r'%[a-z0-9]+',source)and re.fullmatch(r'0x(?:8|10)\(%rdi\)',memory[1]))or(op=='movw'and source=='%ax'and memory[1]=='(%rdi)')
            need(metadata,'unsupported CMOU outside-loop nonstack store')
    need(stores,'CMOU output-store inventory missing')
    cache={};visiting=set()
    def paths(a):
        if a in cache:return cache[a]
        need(a not in visiting,'unknown multiple-cycle CMOU output-loop shape')
        visiting.add(a);tails=set()
        for b in graph[a]:
            if b not in normal:continue
            if b==header:tails.add((0,0,'backedge'))
            else:tails.update(paths(b))
        if not graph[a]and by[a][0]in('ret','retq'):tails.add((0,0,'exit'))
        need(tails,'output iteration lacks normal successor')
        value={(g+int(a in guards),s+int(a in stores),end)for g,s,end in tails}
        need(len(value)<=32,'unsupported CMOU path-outcome expansion')
        visiting.remove(a);cache[a]=value;return value
    outcomes=paths(header)
    need(all(s==1 for _,s,end in outcomes if end=='backedge'),'CMOU backedge does not write exactly one scalar output')
    need(all(s<=1 for _,s,_ in outcomes),'CMOU path writes multiple scalar outputs')
    productive=[g for g,s,_ in outcomes if s==1];need(productive,'CMOU productive path inventory missing')
    return dict(static_guard_sites=[hex(a)for a in sorted(guards)],normal_iteration_guard_counts=[min(productive),max(productive)],
                output_stores=[hex(a)for a in sorted(stores)],sret_role='Entry RDI reserved for typed result metadata; no normal-path register use/copy/clobber/LEA alias or call',path_outcomes=[dict(bounds_guards=g,output_stores=s,end=end)for g,s,end in sorted(outcomes)],
                counted_paths='All one-store backedges and productive exits; only zero-store exits excluded')


def analyze(rows,names,gots,side):
    need(side in('prior','combined','candidate'),'only native products have CompatCore CMOU proof')
    analysis=cfg(rows,names,gots);loops=[x for x in analysis['cyclic_cfgs']if x['output_loop_candidate']]
    need(len(loops)==1,'CMOU output loop not unique; no heuristic fallback')
    loop=loops[0];need(not loop['unknown_exit_or_call_reachable'],'unknown CMOU loop exit/call')
    guards=guard_count(rows,analysis,loop);expected=[0,0]if side=='candidate'else[3,3]
    need(guards['normal_iteration_guard_counts']==expected,'executed CMOU bounds guards differ from source-bound3→0 gate')
    need(loop['bounds_panic_reachable']==(side!='candidate'),'CMOU bounds-panic reachability differs')
    return {'analysis':analysis,'output_loop':loop,'guards':guards,'gate':True,'source_check_roles':'baseline2input+1output; alternativeoutputbranches may create4static sites','scope':'One source-bound nonstack-f64-store/arithmetic SCC; other entry/wrapper checks remain; not completeISA/data-flow proof'}


def inspect(binary,output,side):
    binary=Path(binary);output=Path(output);output.mkdir(parents=True,exist_ok=True);header=binary.read_bytes()[:20]
    need(len(header)==20 and header[:6]==b'\x7fELF\x02\x01'and struct.unpack('<H',header[16:18])[0]in(2,3)and struct.unpack('<H',header[18:20])[0]==62,'actual normal Linux ELF64 x86_64 required')
    def run(name,c):
        value=subprocess.check_output(c,text=True);(output/name).write_text(value);return value
    syms=run('symbols.txt',['readelf','-sW',str(binary)]);ph=run('segments.txt',['readelf','-lW',str(binary)]);rr=run('relocations.txt',['readelf','-rW',str(binary)]);segments=[]
    for line in ph.splitlines():
        f=line.split()
        if f and f[0]=='LOAD'and'E'in f[6:-1]:segments.append((int(f[2],16),int(f[2],16)+int(f[5],16)))
    start,size,name=select_symbols(syms,segments);text=run('cmou.asm',['objdump','-d','-w','-M','att,suffix','--disassemble='+name,str(binary)]);rows=parse_instructions(text,start,size);names=function_names(syms);result=analyze(rows,names,relocs(rr,names),side)
    result.update(binary=str(binary),binary_sha256=sha(binary),side=side,symbol=name,address=hex(start),size=size,instruction_count=len(rows),instruction_dump_sha256=sha(output/'cmou.asm'),profile='actual installed normal release wheel; no alternate build/no forced noinline')
    (output/'report.json').write_text(json.dumps(result,indent=2)+'\n');result['files']={str(p):sha(p)for p in sorted(output.iterdir())if p.is_file()};return result
