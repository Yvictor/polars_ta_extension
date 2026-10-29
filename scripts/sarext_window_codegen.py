"""Bounded x86 evidence for the frozen SAR/SAREXT batch source, not a decoder proof.

Only the scoped functions have one mutable f64 output and no local f64 arrays.
A non-stack f64-store SCC is therefore an output-loop candidate under that source
invariant. Public valid-prefix/dispatch proofs remain separate; SCCs do not prove
which path a call takes. No register value provenance is propagated across calls.
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


def cfg(rows,names,gots):
    by={a:(op,args) for a,op,args in rows};addresses=list(by);nexts=dict(zip(addresses,addresses[1:]));graph={a:[] for a in addresses};bad=set();unknown=set();calls={}
    for a,op,args in rows:
        nxt=nexts.get(a);dest=target(args)
        if op.startswith('loop') or (op in ('bnd','notrack','rep','repz','repnz') and re.match(r'(?:j|ret)',args)):unknown.add(a)
        if op.startswith('call'):
            named=names.get(dest,'') if dest is not None else ''
            if not named:
                m=re.search(r'#\s*(?:0x)?([0-9a-f]+)',args)
                named=gots.get(int(m[1],16),'') if m else ''
            if not named:
                label=re.search(r'<([^>]+)>',args);named=label[1].split('+0x')[0] if label else ''
            calls[a]=named or 'UNKNOWN'
            if panic(named):bad.add(a)
            elif not re.fullmatch(r'_?fma(?:@.*)?',named):unknown.add(a)
        if op.startswith('j'):
            if dest in by:graph[a].append(dest)
            elif dest is not None and panic(names.get(dest,'')):bad.add(a)
            else:unknown.add(a)
            if op not in ('jmp','jmpq') and nxt is not None:graph[a].append(nxt)
        elif op not in ('ret','retq','ud2','int3') and nxt is not None and a not in bad:graph[a].append(nxt)
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
    return {'cyclic_cfgs':loops,'panic_sites':[hex(a) for a in sorted(bad)],'unknown_sites':[hex(a) for a in sorted(unknown)],'calls':{hex(a):n for a,n in calls.items()}}


def inspect(binary,output,version,candidate=False):
    binary=Path(binary);output=Path(output);output.mkdir(parents=True,exist_ok=True)
    h=binary.read_bytes()[:20];need(len(h)==20 and h[:6]==b'\x7fELF\x02\x01' and struct.unpack('<H',h[16:18])[0]in(2,3) and struct.unpack('<H',h[18:20])[0]==62,'actual normal executable ELF64 x86_64 required')
    def run(name,command):
        text=subprocess.check_output(command,text=True);(output/name).write_text(text);return text
    syms=run('symbols.txt',['readelf','-sW',str(binary)]);ph=run('segments.txt',['readelf','-lW',str(binary)]);rr=run('relocations.txt',['readelf','-rW',str(binary)])
    segments=[]
    for line in ph.splitlines():
        fields=line.split()
        if fields and fields[0]=='LOAD' and 'E'in fields[6:-1]:segments.append((int(fields[2],16),int(fields[2],16)+int(fields[5],16)))
    names={}
    for line in syms.splitlines():
        m=re.match(r'\s*\d+:\s+([0-9a-f]+)\s+\d+\s+\S+\s+\S+\s+\S+\s+(\S+)\s+(\S+)',line)
        if m and m[2]!='UND':
            address=int(m[1],16)
            if address not in names or panic(m[3]):names[address]=m[3]
    functions=[];errors=[]
    try:selected=symbols(syms,segments)
    except ValueError as error:selected=[];errors.append(str(error))
    for start,size,name in selected:
        text=run(f'function-{len(functions)}.asm',['objdump','-d','-w','--disassemble='+name,str(binary)])
        try:rows=parse_instructions(text,start,size);analysis=cfg(rows,names,relocs(rr,names))
        except ValueError as error:
            errors.append(name+': '+str(error));analysis={'cyclic_cfgs':[],'scope_unknown':str(error)}
        functions.append({'symbol':name,'address':hex(start),'size':size,**analysis})
    slots={}
    for stem in ('sar_impl','sarext_impl'):
        for mode in ('generic','fma'):
            relevant=[f for f in functions if stem in f['symbol'] and ('_fma'in f['symbol'])==(mode=='fma')]
            loops=[loop for f in relevant for loop in f['cyclic_cfgs'] if loop['output_loop_candidate']]
            clean=[g for g in loops if not g['bounds_panic_reachable'] and not g['unknown_exit_or_call_reachable']]
            slots[stem+'/'+mode]={'functions':len(relevant),'output_loop_candidates':len(loops),'checkfree_candidates':len(clean)}
    gate=not errors and all(row['checkfree_candidates']==1 for row in slots.values())
    result={'binary':str(binary),'binary_sha256':sha(binary),'toolchain':version,'candidate':candidate,'functions':functions,'slots':slots,'scope_errors':errors,
      'candidate_197_mechanism_gate':gate if version=='1.97.0' and candidate else None,
      'scope':'Scoped source invariant + per-function SCC evidence only; not a register provenance or hot-path selection proof. Public valid-prefix/hardware dispatch proof is separate.'}
    (output/'report.json').write_text(json.dumps(result,indent=2)+'\n')
    if version=='1.97.0' and candidate:need(gate,'1.97 actual normal candidate CFG proof missing/unknown/not uniquely checkfree')
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--binary',required=True);p.add_argument('--output',required=True);p.add_argument('--version',choices=('1.90.0','1.97.0'),required=True);p.add_argument('--candidate',action='store_true');a=p.parse_args();inspect(a.binary,a.output,a.version,a.candidate)
