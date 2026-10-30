"""Source-bound x86 CFG helper reused from reviewed SAR/SAREXT CI evidence.

Original module SHA256:
04c0fe905e476d0ff33a5a1adb28f9a899bd4390677730f7a64875615d75d409.
Only the existing instruction/CFG helpers are reused; the SAR symbol selector
is unused. This is bounded evidence, not a complete ISA/data-flow proof.
"""
import argparse,hashlib,json,re,struct,subprocess
from pathlib import Path


def need(ok,why):
    if not ok:raise ValueError(why)


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def symbols(text,segments):
    found=set()
    for line in text.splitlines():
        m=re.match(r'\s*\d+:\s+([0-9a-fA-F]+)\s+(\d+)\s+(?:FUNC|IFUNC)\s+\S+\s+\S+\s+(\S+)\s+(\S+)',line)
        if m and m[3]!='UND' and int(m[2]):found.add((int(m[1],16),int(m[2]),m[4]))
    selected=[r for r in found if any(stem in r[2] for stem in ('sar_impl','sarext_impl','TA_SAR')) and 'open' not in r[2]]
    for start,size,name in selected:
        need(any(lo<=start<start+size<=hi for lo,hi in segments),'symbol outside executable segment')
        for a,b,_ in found:
            need(not(start<a+ b and a<start+size) or (start,size)==(a,b),'partial/contained overlapping function bounds')
    return sorted(selected)


def function_names(syms):
    names={}
    for line in syms.splitlines():
        m=re.match(r'\s*\d+:\s+([0-9a-f]+)\s+\d+\s+(?:FUNC|IFUNC)\s+\S+\s+\S+\s+(\S+)\s+(\S+)',line)
        if m and m[2]!='UND':
            address=int(m[1],16)
            if address not in names or panic(m[3]):names[address]=m[3]
    return names


def relocs(text,names):
    result={}
    for line in text.splitlines():
        if 'R_X86_64_RELATIVE' in line:
            m=re.match(r'\s*([0-9a-f]+)\s+\S+\s+R_X86_64_RELATIVE\s+([0-9a-f]+)\s*$',line)
            if m:result[int(m[1],16)]=names.get(int(m[2],16),'address:'+m[2])
        else:
            m=re.match(r'\s*([0-9a-f]+)\s+\S+\s+R_X86_64_(?:GLOB_DAT|JUMP_SLOT)\s+[0-9a-f]+\s+(\S+)',line)
            if m:result[int(m[1],16)]=m[2]
    return result


def parse_instructions(text,start,size):
    rows=[];end=start
    for line in text.splitlines():
        raw=re.match(r'\s*([0-9a-f]+):',line)
        if not raw or not start<=int(raw[1],16)<start+size:continue
        m=re.match(r'\s*([0-9a-f]+):\s*((?:[0-9a-f]{2}\s+)+)\s*([a-z][a-z0-9.]*)\s*(.*?)\s*$',line)
        need(m is not None,'undecoded instruction in function scope')
        address=int(m[1],16);width=len(m[2].split())
        need(address==end and 1<=width<=15,'missing/duplicate/displaced instruction bytes')
        end=address+width;need(end<=start+size,'instruction extends beyond function scope')
        rows.append((address,m[3],m[4]))
    need(rows and end==start+size,'truncated function instruction bytes')
    return rows


def target(operand):
    m=re.match(r'(?:0x)?([0-9a-f]+)\b',operand)
    return int(m[1],16) if m else None


def panic(name):return any(x in name for x in ('panic_bounds_check','slice_end_index_len_fail','slice_start_index_len_fail','slice_index_order_fail','slice_end_index_overflow_fail'))


def sccs(graph):
    # Iterative Kosaraju keeps real optimized functions independent of Python's
    # recursion limit. Every graph destination is an instruction in this scope.
    visited=set();order=[]
    for root in graph:
        if root in visited:continue
        stack=[(root,False)]
        while stack:
            node,done=stack.pop()
            if done:order.append(node);continue
            if node in visited:continue
            visited.add(node);stack.append((node,True))
            stack.extend((x,False) for x in graph[node] if x not in visited)
    reverse={node:[] for node in graph}
    for node,edges in graph.items():
        for dest in edges:reverse[dest].append(node)
    visited=set();out=[]
    for root in reversed(order):
        if root in visited:continue
        group=[];stack=[root]
        while stack:
            node=stack.pop()
            if node in visited:continue
            visited.add(node);group.append(node);stack.extend(reverse[node])
        out.append(sorted(group))
    return out


def fma_register_calls(rows,graph,calls,gots,names):
    # SysV r12-r15 are preserved by the exact C-ABI fma target only. Unknown
    # calls and every other register mention kill tags, including subregisters.
    regs=('r12','r13','r14','r15');loads={};by={a:(op,args)for a,op,args in rows}
    is_fma=lambda n:re.fullmatch(r'fma(?:@.*)?',n)is not None
    for a,op,args in rows:
        m=re.fullmatch(r'[-+]?(?:0x)?[0-9a-f]*\(%rip\),\s*%(r1[2-5])\s*#\s*(?:0x)?([0-9a-f]+).*',args)
        if op in ('mov','movq')and m and is_fma(gots.get(int(m[2],16),'')) and gots[int(m[2],16)] in names.values():
            loads[a]=(m[1],int(m[2],16),gots[int(m[2],16)])
    # Empty is unreachable bottom, {False} unknown, {True} must-known FMA;
    # a union containing False cannot certify. Start only at function entry.
    states={a:[set()for _ in regs]for a in graph};entry=rows[0][0]
    states[entry]=[{False}for _ in regs];todo=[entry]
    while todo:
        a=todo.pop();op,args=by[a];incoming=states[a];out=[set(v)for v in incoming]
        if a in calls:
            m=re.fullmatch(r'\*%(r1[2-5])',args)
            known=is_fma(calls[a])or(m is not None and incoming[regs.index(m[1])]=={True})
            if not known:out=[{False}for _ in regs]
        else:
            for i,reg in enumerate(regs):
                if a in loads and loads[a][0]==reg:out[i]={True}
                elif re.search('%'+reg+r'(?:d|w|b)?\b',args.split('#',1)[0]):out[i]={False}
        for dest in graph[a]:
            merged=[old|new for old,new in zip(states[dest],out)]
            if merged!=states[dest]:states[dest]=merged;todo.append(dest)
    proven={}
    for a,name in calls.items():
        m=re.fullmatch(r'\*%(r1[2-5])',by[a][1])
        if m and states[a][regs.index(m[1])]=={True}:proven[a]=m[1]
    return proven,{'loads':{hex(a):{'register':r,'GOT':hex(g),'symbol':n}for a,(r,g,n)in loads.items()},
                   'calls':{hex(a):r for a,r in proven.items()},'unknown_calls_kill_all_tags':True,
                   'contract':'Exact resolved C-ABI fma only preserves r12-r15; all other mentions/calls kill. Empty=unreachable; any unknown incoming path rejects.'}


def cfg(rows,names,gots):
    by={a:(op,args) for a,op,args in rows};addresses=list(by);nexts=dict(zip(addresses,addresses[1:]));graph={a:[] for a in addresses};bad=set();unknown=set();calls={}
    for a,op,args in rows:
        nxt=nexts.get(a);dest=target(args)
        if op.startswith('loop') or (op in ('bnd','notrack','rep','repz','repnz') and re.match(r'(?:j|ret|call)',args)):unknown.add(a)
        if op in ('bnd','notrack','rep','repz','repnz')and re.match(r'call',args):calls[a]='UNKNOWN'
        if op.startswith('call'):
            named=names.get(dest,'') if dest is not None else ''
            if not named:
                m=re.search(r'#\s*(?:0x)?([0-9a-f]+)',args)
                named=gots.get(int(m[1],16),'') if m else ''
            if not named:
                label=re.search(r'<([^>]+)>',args);named=label[1].split('+0x')[0] if label else ''
            calls[a]=named or 'UNKNOWN'
            if panic(named):bad.add(a)
            elif not re.fullmatch(r'fma(?:@.*)?',named):unknown.add(a)
        if op.startswith('j'):
            if dest in by:graph[a].append(dest)
            elif dest is not None and panic(names.get(dest,'')):bad.add(a)
            else:unknown.add(a)
            if op not in ('jmp','jmpq') and nxt is not None:graph[a].append(nxt)
        elif op not in ('ret','retq','ud2','int3') and nxt is not None and a not in bad:graph[a].append(nxt)
    proven,fma_proof=fma_register_calls(rows,graph,calls,gots,names)
    for a in proven:calls[a]='fma';unknown.discard(a)
    def reachable(v,goals):
        todo=[v];seen=set()
        while todo:
            x=todo.pop()
            if x in goals:return True
            if x not in seen:seen.add(x);todo.extend(graph[x])
        return False
    loops=[];frame=any(op.startswith('mov') and re.fullmatch(r'%rsp,\s*%rbp',args) for _,op,args in rows)
    for group in sccs(graph):
        cyclic=len(group)>1 or (group and group[0] in graph[group[0]])
        if not cyclic:continue
        stores=[];arithmetic=[]
        for a in group:
            op,args=by[a]
            if re.match(r'(?:v?(?:add|sub|mul|div)sd|v?f[nm]*[as][du][db].*sd)',op):arithmetic.append(a)
            if re.match(r'(?:v?mov(?:sd|lpd|upd|apd|ups|aps)|movq)',op) and re.match(r'%xmm\d+,\s*[^#]*\(',args):
                if '%rsp' not in args and not(frame and '%rbp' in args):stores.append(a)
        loops.append({'addresses':[hex(a) for a in group],'edges':[[hex(a),hex(b)] for a in group for b in graph[a]],
          'fp_arithmetic':[hex(a) for a in arithmetic],'nonstack_f64_stores':[hex(a) for a in stores],
          'output_loop_candidate':bool(stores and arithmetic),'bounds_panic_reachable':any(reachable(a,bad) for a in group),
          'unknown_exit_or_call_reachable':any(reachable(a,unknown) for a in group),
          'instruction_sha256':hashlib.sha256(json.dumps([(a,*by[a]) for a in group]).encode()).hexdigest()})
    return {'fma_register_proof':fma_proof,'cyclic_cfgs':loops,'panic_sites':[hex(a) for a in sorted(bad)],'unknown_sites':[hex(a) for a in sorted(unknown)],'calls':{hex(a):n for a,n in calls.items()}}
