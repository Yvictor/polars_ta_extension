"""Regenerate real pickle compatibility fixtures without collapsing duplicate keys.

Primitive programs come from Python's Pickler. Strip only framing/memo writes;
there are no memo reads in the assembled atoms. Every assembled map is also
accepted by Python's Unpickler before it becomes a Rust decoder oracle fixture.
"""
import argparse
import pickle
import pickletools
from pathlib import Path

def atom(value, protocol):
    data=pickle.dumps(value,protocol=protocol)
    ops=list(pickletools.genops(data)); chunks=[]
    for i,(op,arg,pos) in enumerate(ops):
        if op.name in {'PROTO','FRAME','STOP','MEMOIZE','PUT','BINPUT','LONG_BINPUT'}: continue
        assert op.name not in {'GET','BINGET','LONG_BINGET'}, (value,op.name)
        end=ops[i+1][2] if i+1<len(ops) else len(data)
        chunks.append(data[pos:end])
    return b''.join(chunks)

def wire(pairs, protocol):
    data=(b'\x80'+bytes([protocol]) if protocol>=2 else b'')+(b'(d' if protocol==0 else b'}')
    return data+b''.join(atom(k,protocol)+atom(v,protocol)+b's' for k,v in pairs)+b'.'


def fixtures():
    lines=['# Real Python pickle programs; duplicate dict keys retained in wire order.']
    for protocol in range(6):
        cases=[]
        for n in [0,1,8,9,11,64]: cases.append((f'distinct-{n}',[(f'key{i}',float(i) if i%2 else i) for i in range(n)]))
        cases += [
          ('duplicate-inline', [('a',1),('a',-0.0)]),
          ('duplicates-through-spill',[(f'key{i}',i) for i in range(11)]+[('key0',-0.0),('key9',float('inf'))]),
          ('many-items-few-distinct',[(f'key{i%3}',i) for i in range(64)]),
          ('unknown-numeric',[('unknown',3),('signed_zero',-0.0),('nan',float('nan'))]),
          ('unknown-nonnumeric',[('unknown','bad')]),
          ('invalid-earlier-duplicate',[('a','bad'),('a',2)]),
          ('invalid-later-duplicate',[('a',2),('a',None)]),
          ('first-error-wire-order',[('z',True),('a',{})]),
          ('invalid-integer-key',[(7,1)]),
          ('invalid-tuple-key',[((1,2),1)]),
          ('invalid-nested',[('nested',[1,{'x':2}])]),
        ]
        for label,pairs in cases:
            data=wire(pairs,protocol); pickle.loads(data)
            lines.append(f'p{protocol}-{label}\t{data.hex()}')
            if label=='distinct-11': lines.append(f'p{protocol}-truncated\t{data[:-3].hex()}')
        for label,value in [('root-none',None),('root-list',[1,2]),('root-real',1.5),('memo-value',{'z':'same','a':'same'})]:
            lines.append(f'p{protocol}-{label}\t{pickle.dumps(value,protocol=protocol).hex()}')
    envelopes=['# Plugin envelope maps, generated with duplicate outer fields in wire order.']
    for protocol in range(6):
        normal=[('params',{'timeperiod':14}),('lookback',13),('recursive',True)]
        cases=[('valid',normal),('unknown-outer',normal+[('unknown',{'nested':['ignored',1]})]),
               ('missing-params',normal[1:]),('null-params',[('params',None)]+normal[1:]),
               ('duplicate-params',normal+[('params','invalid-but-duplicate-first')]),
               ('duplicate-lookback',normal+[('lookback','bad')]),
               ('bad-lookback',[normal[0],('lookback','bad'),normal[2]]),
               ('spill-params',[('params',{f'key{i}':i for i in range(64)})]+normal[1:])]
        for label,pairs in cases: envelopes.append(f'p{protocol}-{label}\t{wire(pairs,protocol).hex()}')
    return {'param-maps-pickle.hex': '\n'.join(lines)+'\n',
            'param-map-envelopes-pickle.hex': '\n'.join(envelopes)+'\n'}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args=parser.parse_args()
    root=Path(__file__).resolve().parents[1]/'tests/data'
    for name, text in fixtures().items():
        path=root/name
        if args.check:
            if path.read_text()!=text:
                raise SystemExit(f'{path}: regenerate pickle fixtures')
        else:
            path.write_text(text)
    print('132 map and 48 envelope fixtures verified' if args.check else 'fixtures regenerated')


if __name__=='__main__':
    main()
