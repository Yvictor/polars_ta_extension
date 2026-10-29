"""Fail-closed actual-product x86 loop-shape gate; no throughput estimate.

Recognizes only straight conditional-backedge loops. Vector NaN stores must
have one reaching definition loading canonical NaNs from the same ELF bytes.
A fused loop must also load input vectors, compare them unordered and reduce
those comparisons. Unknown/fissioned code generation stops before timers.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import struct
import subprocess


def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def operands(text):
    out=[];start=depth=0
    for i,c in enumerate(text):
        depth+=(c=='(')-(c==')')
        if c==',' and depth==0:out.append(text[start:i].strip());start=i+1
    return out+[text[start:].strip()] if text else []


def instructions(text):
    out=[]
    for line in text.splitlines():
        m=re.fullmatch(r'\s*([0-9a-f]+):\s+([a-z][a-z0-9.]*)\s*(.*)',line)
        if m:out.append({'address':int(m[1],16),'mnemonic':m[2],'operands':operands(m[3].split('#',1)[0].strip()),'raw':m[3],'line':line})
    if not out or len({x['address'] for x in out})!=len(out):raise ValueError('empty/ambiguous disassembly')
    return out


def target(x):
    m=re.match(r'^(?:0x)?([0-9a-f]+)(?:\s|$)',x['operands'][0]) if x['operands'] else None
    return int(m[1],16) if m else None


def vector(s):
    m=re.fullmatch(r'%[xyz]mm(\d+)',s)
    return int(m[1]) if m else None


def writes(x,r):
    # SysV x86-64 vector registers are caller-saved, including indirect calls.
    if x['mnemonic'].startswith('call'):return True
    a=x['operands'];return bool(a and vector(a[-1])==r and not x['mnemonic'].startswith(('ucom','comis','test','j','call')))


def reaching(ins,r):
    addresses={x['address'] for x in ins};succ={a:set() for a in addresses}
    for i,x in enumerate(ins):
        a=x['address'];m=x['mnemonic'];nxt=ins[i+1]['address'] if i+1<len(ins) else None
        if m.startswith('j'):
            t=target(x)
            if t is None:raise ValueError('indirect factory branch unsupported')
            if t in addresses:succ[a].add(t)
            if not m.startswith('jmp') and nxt is not None:succ[a].add(nxt)
        elif not m.startswith(('ret','ud2')) and nxt is not None:succ[a].add(nxt)
    seen=set();todo=[ins[0]['address']]
    while todo:
        a=todo.pop()
        if a not in seen:seen.add(a);todo.extend(succ[a])
    pred={a:set() for a in seen}
    for a in seen:
        for b in succ[a]:pred[b].add(a)
    before={a:set() for a in seen};after={a:set() for a in seen};changed=True
    while changed:
        changed=False
        for x in ins:
            a=x['address']
            if a not in seen:continue
            inc={-1} if a==ins[0]['address'] else set()
            for p in pred[a]:inc.update(after[p])
            out={a} if writes(x,r) else inc
            if before[a]!=inc or after[a]!=out:before[a]=inc;after[a]=out;changed=True
    return before


def elf_bytes(blob,addr,count):
    if len(blob)<64 or blob[:6]!=b'\x7fELF\x02\x01':raise ValueError('ELF64 little-endian required')
    start=struct.unpack_from('<Q',blob,32)[0];size,num=struct.unpack_from('<HH',blob,54)
    if size!=56 or start+size*num>len(blob):raise ValueError('invalid ELF program headers')
    matches=[]
    for i in range(num):
        kind,flags,offset,va,pa,filesz,memsz,align=struct.unpack_from('<IIQQQQQQ',blob,start+i*size)
        if kind==1 and va<=addr and addr+count<=va+filesz:
            pos=offset+addr-va
            if pos+count>len(blob):raise ValueError('truncated ELF segment')
            matches.append(blob[pos:pos+count])
    if len(matches)!=1:raise ValueError('constant lacks one file-backed ELF segment')
    return matches[0]


def canonical_store(x,ins,blob,cache):
    r=vector(x['operands'][0])
    if r not in cache:cache[r]=reaching(ins,r)
    definitions=cache[r].get(x['address'],set())
    if len(definitions)!=1:return None
    src=next((y for y in ins if y['address'] in definitions),None)
    if src is None or not re.fullmatch(r'v?mov(?:ap[ds]|up[ds]|dq[au])',src['mnemonic']):return None
    if len(src['operands'])!=2 or '(%rip)' not in src['operands'][0]:return None
    addr=re.search(r'#\s*(?:0x)?([0-9a-f]+)',src['raw'])
    if not addr:return None
    size=32 if src['operands'][-1].startswith('%ymm') else 16
    expected=struct.pack('<Q',0x7ff8000000000000)*(size//8)
    if elf_bytes(blob,int(addr[1],16),size)!=expected:return None
    return {'store':x['address'],'definition':src['address'],'constant':int(addr[1],16),'bytes':expected.hex()}


def inspect(text,blob):
    ins=instructions(text);addresses={x['address'] for x in ins};cache={};loops=[]
    reachable=reaching(ins,0)
    for end in ins:
        m=end['mnemonic'];start=target(end) if m.startswith('j') else None
        if m.startswith('jmp') or start not in addresses or start>=end['address'] or start not in reachable:continue
        body=[x for x in ins if start<=x['address']<=end['address']]
        if any(x['mnemonic'].startswith(('j','call','ret')) for x in body[:-1]):continue
        loads=[];stores=[];vector_stores=[];compares=[];reductions=[]
        for x in body:
            a=x['operands'];m=x['mnemonic']
            if len(a)==2 and re.fullmatch(r'v?mov(?:ap[ds]|up[ds]|dq[au])',m):
                if '(' in a[0] and '%rip' not in a[0] and vector(a[1]) is not None:loads.append(x)
                if vector(a[0]) is not None and '(' in a[1] and not any(r in a[1] for r in ('%rip','%rsp','%rbp')):
                    vector_stores.append(x['address'])
                    proof=canonical_store(x,ins,blob,cache)
                    if proof:stores.append(proof)
            if m=='cmpnlepd' and len(a)==2 and vector(a[-1]) is not None:
                prior=[y for y in body if y['address']<x['address'] and writes(y,vector(a[-1]))]
                load=next((y for y in reversed(prior) if y in loads),None)
                if load and all(y['mnemonic'] in ('andpd','pand') for y in prior if y['address']>load['address']):compares.append(x)
            if m in ('orpd','por') and len(a)==2:
                r=vector(a[0])
                if r is not None and vector(a[-1]) is not None and r!=vector(a[-1]):
                    if r not in cache:cache[r]=reaching(ins,r)
                    if any(y['address']<x['address'] and y['operands'][-1]==a[0] and cache[r].get(x['address'])=={y['address']} for y in compares):reductions.append(x)
        # Require a real loop-carried accumulator. The last OR must feed the
        # first OR of that accumulator on the next iteration, and no other
        # instruction in the loop may overwrite it (including a later clear).
        retained=[]
        for acc in {vector(x['operands'][-1]) for x in reductions}:
            chain=[x for x in reductions if vector(x['operands'][-1])==acc]
            chain_addresses={x['address'] for x in chain}
            if acc not in cache:cache[acc]=reaching(ins,acc)
            incoming=cache[acc].get(chain[0]['address'],set())
            if (-1 not in incoming and chain[-1]['address'] in incoming
                    and all(not writes(x,acc) or x['address'] in chain_addresses for x in body)):
                retained.extend(chain)
        reductions=retained
        loops.append({'header':start,'backedge':end['address'],'loads':[x['address'] for x in loads],
                      'compares':[x['address'] for x in compares],'reductions':[x['address'] for x in reductions],
                      'canonical_nan_stores':stores,'vector_stores':vector_stores,'instructions':[x['line'] for x in body]})
    return {'instruction_count':len(ins),'loops':loops}


def check_shapes(fused,control):
    combined=[l for l in fused['loops'] if l['loads'] and l['compares'] and l['reductions'] and l['canonical_nan_stores']]
    scans=[l for l in control['loops'] if l['loads'] and l['compares'] and l['reductions'] and not l['vector_stores']]
    fills=[l for l in control['loops'] if l['canonical_nan_stores'] and not l['compares']]
    candidate_scans=[l for l in fused['loops'] if l['loads'] and l['compares'] and l['reductions'] and not l['canonical_nan_stores']]
    if candidate_scans or not combined or not scans or not fills or any(l['compares'] and l['vector_stores'] for l in control['loops']):raise ValueError('actual fusion vs separate-fill/scan CFG shape not established')
    return {'fused_backedges':[l['backedge'] for l in combined],'control_scan_backedges':[l['backedge'] for l in scans],'control_fill_backedges':[l['backedge'] for l in fills]}


def extract(path,out):
    out.mkdir(parents=True,exist_ok=True)
    nm=subprocess.check_output(['nm','-an','--defined-only',str(path)],text=True);(out/'symbols.txt').write_text(nm)
    symbols=[s.split()[-1] for s in nm.splitlines() if re.search(r'\s[tT]\s',s) and '6compat7guarded17initialized_first' in s]
    cmd=['objdump','-d','--wide','--no-show-raw-insn',*(['--disassemble='+symbols[0]] if len(symbols)==1 else []),str(path)]
    text=subprocess.check_output(cmd,text=True);(out/'initialized-first.objdump').write_text(text)
    if len(symbols)!=1:raise ValueError('one actual initialized_first product symbol required; full product objdump retained')
    result=inspect(text,path.read_bytes());(out/'cfg.json').write_text(json.dumps(result,indent=2)+'\n')
    return {'elf':str(path),'elf_sha256':sha(path),'symbol':symbols[0],'argv':cmd,
            'objdump':str(out/'initialized-first.objdump'),'objdump_sha256':sha(out/'initialized-first.objdump'),
            'cfg':str(out/'cfg.json'),'cfg_sha256':sha(out/'cfg.json'),'analysis':result}


def build_gate(output):
    output=Path(output);p=output/'build-provenance.json';build=json.loads(p.read_text())
    record={'passed':False,'build_provenance_sha256':sha(p),'inspector_sha256':sha(__file__),'products':{}}
    try:
        errors=[]
        for side in ('initialization','candidate'):
            files=build['builds'][side]['retained_native_files']
            if len(files)!=1:raise ValueError('exactly one normal product required')
            path=Path(next(iter(files)))
            if sha(path)!=files[str(path)]:raise ValueError('actual product changed')
            try:record['products'][side]=extract(path,output/'codegen'/side)
            except Exception as e:
                record['products'][side]={'elf':str(path),'elf_sha256':sha(path),'error':str(e)};errors.append(side+': '+str(e))
        if errors:raise ValueError('; '.join(errors))
        record['shape']=check_shapes(record['products']['candidate']['analysis'],record['products']['initialization']['analysis']);record['passed']=True
    except Exception as e:record['error']=str(e);raise
    finally:(output/'codegen-gate.json').write_text(json.dumps(record,indent=2)+'\n')
    return record


def verify_codegen(output):
    output=Path(output);r=json.loads((output/'codegen-gate.json').read_text())
    if not r['passed'] or r['build_provenance_sha256']!=sha(output/'build-provenance.json') or r['inspector_sha256']!=sha(__file__):raise ValueError('normal product codegen gate missing or changed')
    for row in r['products'].values():
        for path,digest in ((row['elf'],row['elf_sha256']),(row['objdump'],row['objdump_sha256']),(row['cfg'],row['cfg_sha256'])):
            if sha(path)!=digest:raise ValueError('product static evidence changed')
    return r


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True)
    print(json.dumps(build_gate(p.parse_args().output),indent=2))
