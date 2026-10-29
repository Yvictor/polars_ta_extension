"""Actual normal-product ELF evidence for SAREXT's public multiversion route.

Only the selected B compatibility FMA clone is checked for inline FMA evidence.
Other functions and the portable fallback legitimately retain out-of-line fma
calls, including a locally linked compiler_builtins shim.
The generated resolver requires the complete feature closure, not FMA alone.
This is a focused source-bound preflight, not universal machine verification.
"""
import argparse
import json
from pathlib import Path
import re
import subprocess
from sarext_typed_provenance import sha256,elf_record

SIDES=('original','prior','candidate','alternative')
FMA_TAG='dispatched_scalar_avx_fma_sse_sse2_sse3_sse41_ssse3_version'


def analyze(text,relocations="",symbols=""):
    # A final cdylib can resolve LLVM's portable fma intrinsic to a local
    # compiler_builtins shim. Its GOT slot then has an R_X86_64_RELATIVE
    # addend, not a named dynamic relocation. Resolve only the exact addend
    # address to an exact defined text symbol; never use a nearest symbol or
    # treat arbitrary relative calls as fma.
    text_symbols={}
    for line in symbols.splitlines():
        fields=line.split()
        if len(fields)==3 and fields[1] in ('t','T') and re.fullmatch('[0-9a-fA-F]+',fields[0]):
            text_symbols.setdefault(int(fields[0],16),set()).add(fields[2])
    got={};resolutions={}
    for line in relocations.splitlines():
        fields=line.split()
        if len(fields)<4 or not re.fullmatch('[0-9a-fA-F]+',fields[0]):continue
        slot=int(fields[0],16)
        if fields[2]=='R_X86_64_RELATIVE':
            if len(fields)!=4 or not re.fullmatch('[0-9a-fA-F]+',fields[3]):continue
            target=int(fields[3],16)
            if 'fma' in text_symbols.get(target,set()):
                got[slot]='fma'
                resolutions[slot]={'kind':'exact_relative_text_symbol','slot':hex(slot),
                                   'target':hex(target),'symbol':'fma','relocation':line}
        elif len(fields)>=5:
            got[slot]=fields[4]
            resolutions[slot]={'kind':'named_dynamic_symbol','slot':hex(slot),
                               'symbol':fields[4],'relocation':line}
    lines=text.splitlines()
    calls=[s for s in lines if re.search(r'^\s*[0-9a-f]+:\s+call\w*\s',s)]
    transfers=[s for s in lines if re.search(r'^\s*[0-9a-f]+:\s+(?:call\w*|j\w*)\s',s)]
    fma=[s for s in lines if re.search(r'^\s*[0-9a-f]+:\s+vf(?:madd|msub|nmadd|nmsub)',s)]
    named=[];resolved_fma=[]
    for line in transfers:
        ref=re.search(r'#\s*(?:0x)?([0-9a-f]+)',line)
        resolved=got.get(int(ref[1],16),'') if ref else ''
        if re.search(r'(?<![A-Za-z_])fma(?:@|\b)',line) or re.match(r'^fma(?:@|$)',resolved):
            named.append(line)
            if ref and int(ref[1],16) in resolutions:
                resolved_fma.append({'instruction':line,**resolutions[int(ref[1],16)]})
    return {'inline_fma_instruction_lines':fma,'all_call_lines':calls,'named_libm_fma_call_lines':[line for line in named if line in calls],
            'libm_fma_control_transfer_lines':named,'all_control_transfer_lines':transfers,
            'resolved_fma_control_transfers':resolved_fma,
            'limit':'Unnamed indirect calls/jumps are retained for relocation inspection; counts are per function, never a whole-library fma-absence claim.'}


def symbol_roles(functions):
    # Matched R1.90 source evidence: portable scalar body is inlined into the
    # plain wrapper, not a separately invented default_version function.
    clones=[name for name in functions if FMA_TAG in name]
    wrappers=[name for name in functions if re.search(r'17dispatched_scalar17h[0-9a-f]+E(?:\..*)?$',name)]
    resolvers=[name for name in functions if 'dispatched_scalar14__detect_index8__detect' in name]
    if len(clones)!=1 or len(wrappers)!=1 or len(resolvers)!=1:
        raise ValueError('one FMA clone, plain portable/dispatch wrapper and feature resolver required')
    return {'fma_clone':clones[0],'portable_dispatch_wrapper':wrappers[0],'feature_resolver':resolvers[0]}


def collect(output):
    output=Path(output);p=output/'build-provenance.json';build=json.loads(p.read_text())
    record={'passed':False,'build_provenance_sha256':sha256(p),'inspector_sha256':sha256(__file__),'products':{},
            'feature_scope':'Public multiversion resolver checks AVX/FMA/SSE/SSE2/SSE3/SSE4.1/SSSE3 closure; not an FMA-alone guard.'}
    errors=[]
    for side in SIDES:
        folder=output/'product-elf'/side;folder.mkdir(parents=True,exist_ok=True)
        files=build['builds'][side]['retained_native_files']
        if len(files)!=1:errors.append(side+': missing unique retained actual ELF');continue
        path=Path(next(iter(files)))
        if sha256(path)!=files[str(path)]:errors.append(side+': retained product changed');continue
        product={'elf':elf_record(path),'commands':[],'files':{},'functions':{}}
        record['products'][side]=product
        try:
            for filename,cmd in (('header.txt',['readelf','-hW',str(path)]),('relocations.txt',['readelf','-rW',str(path)]),('symbols.txt',['nm','-an','--defined-only',str(path)])):
                product['commands'].append(cmd)
                with (folder/filename).open('w') as stream:subprocess.run(cmd,stdout=stream,stderr=subprocess.STDOUT,check=True)
                product['files'][str(folder/filename)]=sha256(folder/filename)
            nm=(folder/'symbols.txt').read_text()
            symbols=[s.split()[-1] for s in nm.splitlines() if re.search(r'\s[tT]\s',s) and 'polars_talib' in s and ('sarext_legacy' in s or 'dispatched_scalar' in s)]
            for index,symbol in enumerate(symbols):
                dest=folder/(f'function-{index:03d}.objdump')
                cmd=['objdump','-drw','--no-show-raw-insn','--disassemble='+symbol,str(path)];product['commands'].append(cmd)
                with dest.open('w') as stream:subprocess.run(cmd,stdout=stream,stderr=subprocess.STDOUT,check=True)
                product['files'][str(dest)]=sha256(dest)
                product['functions'][symbol]={'file':str(dest),**analyze(dest.read_text(),(folder/'relocations.txt').read_text(),nm)}
            if side=='alternative':
                roles=symbol_roles(product['functions']);product['role_symbols']=roles
                clone=product['functions'][roles['fma_clone']]
                portable=product['functions'][roles['portable_dispatch_wrapper']]
                if len(clone['inline_fma_instruction_lines'])!=4 or clone['libm_fma_control_transfer_lines']:
                    raise ValueError('B FMA clone must show four inline updates without named/relocated fma call/tail transfers')
                if not portable['libm_fma_control_transfer_lines']:
                    raise ValueError('plain wrapper does not expose the source-bound portable fma fallback')
        except Exception as e:errors.append(side+': '+str(e));product['error']=str(e)
    if errors:record['errors']=errors
    else:record['passed']=True
    (output/'product-elf-gate.json').write_text(json.dumps(record,indent=2)+'\n')
    if errors:raise ValueError('; '.join(errors))
    return record


def verify(output):
    output=Path(output);p=output/'build-provenance.json';build=json.loads(p.read_text());r=json.loads((output/'product-elf-gate.json').read_text())
    if not r['passed'] or set(r['products'])!=set(SIDES) or r['build_provenance_sha256']!=sha256(p) or r['inspector_sha256']!=sha256(__file__):raise ValueError('actual-product ELF preflight missing or changed')
    for side,row in r['products'].items():
        actual=build['builds'][side]['retained_native_files']
        if {row['elf']['path']:row['elf']['sha256']}!=actual:raise ValueError('ELF preflight not bound to measured product')
        if sha256(row['elf']['path'])!=row['elf']['sha256']:raise ValueError('measured ELF changed')
        if any(sha256(path)!=digest for path,digest in row['files'].items()):raise ValueError('ELF inspection evidence changed')
    return r


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True)
    print(json.dumps(collect(p.parse_args().output),indent=2))
