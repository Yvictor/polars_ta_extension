"""Machine-shape negative controls; synthetic ELF is not actual-product proof."""
import importlib
import json
from pathlib import Path
import struct
import sys
import pytest
sys.path.insert(0,str(Path(__file__).parents[1]/'scripts'))
cg=importlib.import_module('guard_fusion_codegen')


def elf(constant=0x7ff8000000000000):
    blob=bytearray(136);blob[:6]=b'\x7fELF\x02\x01'
    struct.pack_into('<Q',blob,32,64);struct.pack_into('<HH',blob,54,56,1)
    struct.pack_into('<IIQQQQQQ',blob,64,1,4,120,0x200,0x200,16,16,8)
    struct.pack_into('<QQ',blob,120,constant,constant)
    return bytes(blob)


FUSED='''
10: movapd 0x100(%rip),%xmm4 # 200 <qnan>
20: xorpd %xmm0,%xmm0
30: movupd (%rdi,%r8,8),%xmm5
40: andpd %xmm2,%xmm5
50: cmpnlepd %xmm3,%xmm5
60: orpd %xmm5,%xmm0
70: movups %xmm4,(%rsi,%r8,8)
80: add $4,%r8
90: cmp %r8,%rbx
a0: jne 30 <factory+0x20>
b0: ret
'''
CONTROL='''
10: movapd 0x100(%rip),%xmm4 # 200 <qnan>
20: movups %xmm4,(%rsi,%r8,8)
30: add $4,%r8
40: cmp %r8,%rbx
50: jne 20 <factory+0x10>
60: xorpd %xmm0,%xmm0
70: movupd (%rdi,%r8,8),%xmm5
80: andpd %xmm2,%xmm5
90: cmpnlepd %xmm3,%xmm5
a0: orpd %xmm5,%xmm0
b0: add $4,%r8
c0: cmp %r8,%rbx
d0: jne 70 <factory+0x60>
e0: ret
'''


def test_same_backedge_has_bound_input_compare_reduction_and_canonical_nan_stores():
    fused=cg.inspect(FUSED,elf());control=cg.inspect(CONTROL,elf())
    record=cg.check_shapes(fused,control)
    assert record=={'fused_backedges':[0xa0],'control_scan_backedges':[0xd0],'control_fill_backedges':[0x50]}
    proof=fused['loops'][0]['canonical_nan_stores'][0]
    assert proof['definition']==0x10 and proof['constant']==0x200


@pytest.mark.parametrize('kind',['fission','wrong_nan','clobbered_nan','ambiguous_definition','orphan_compare','no_load','no_reduce','call','inner_branch','unreachable','control_fused','self_or','clear_accumulator','call_clobber'])
def test_loop_gate_rejects_false_evidence_and_keeps_source_fission_negative(kind):
    fused=FUSED;control=CONTROL;blob=elf()
    if kind=='self_or':fused=fused.replace('orpd %xmm5,%xmm0','orpd %xmm5,%xmm5')
    elif kind=='clear_accumulator':fused=fused.replace('70: movups','65: pxor %xmm0,%xmm0\n70: movups')
    elif kind=='call_clobber':fused=fused.replace('20: xorpd','15: call 200 <other>\n20: xorpd')
    elif kind=='fission':fused=CONTROL
    elif kind=='wrong_nan':blob=elf(0x7ff8000000000001)
    elif kind=='clobbered_nan':fused=fused.replace('80: add','75: pxor %xmm4,%xmm4\n80: add')
    elif kind=='ambiguous_definition':fused=fused.replace('20: xorpd','15: jne 30 <factory+0x20>\n18: pxor %xmm4,%xmm4\n20: xorpd')
    elif kind=='orphan_compare':fused=fused.replace('60: orpd','55: pxor %xmm5,%xmm5\n60: orpd')
    elif kind=='no_load':fused=fused.replace('movupd (%rdi,%r8,8),%xmm5','movapd %xmm6,%xmm5')
    elif kind=='no_reduce':fused=fused.replace('orpd %xmm5,%xmm0','andpd %xmm5,%xmm0')
    elif kind=='call':fused=fused.replace('80: add','75: call 100 <other>\n80: add')
    elif kind=='inner_branch':fused=fused.replace('80: add','75: je b0 <exit>\n80: add')
    elif kind=='unreachable':fused='0: ret\n'+fused
    else:control=FUSED
    with pytest.raises(ValueError):cg.check_shapes(cg.inspect(fused,blob),cg.inspect(control,blob))


@pytest.mark.parametrize('kind',['truncated','wrong_segment','missing_segment','duplicate_segment'])
def test_nan_constant_must_bind_exact_file_backed_elf_bytes(kind):
    blob=bytearray(elf())
    if kind=='truncated':blob=blob[:125]
    elif kind=='wrong_segment':struct.pack_into('<Q',blob,80,0x300)
    elif kind=='missing_segment':struct.pack_into('<I',blob,64,0)
    else:struct.pack_into('<HH',blob,54,56,2)
    with pytest.raises(ValueError):cg.inspect(FUSED,bytes(blob))


def test_guarded_gate_refuses_stale_or_missing_codegen_before_measurements(tmp_path):
    (tmp_path/'build-provenance.json').write_text('{}')
    record={'passed':False,'build_provenance_sha256':cg.sha(tmp_path/'build-provenance.json'),'inspector_sha256':cg.sha(cg.__file__)}
    (tmp_path/'codegen-gate.json').write_text(json.dumps(record))
    with pytest.raises(ValueError):cg.verify_codegen(tmp_path)



SECOND_LOOP = """
b0: xorpd %xmm0,%xmm0
c0: movupd (%rdi,%r8,8),%xmm5
d0: andpd %xmm2,%xmm5
e0: cmpnlepd %xmm3,%xmm5
f0: orpd %xmm5,%xmm0
100: movups %xmm4,(%rsi,%r8,8)
110: add $4,%r8
120: cmp %r8,%rbx
130: jne c0 <factory+0xb0>
140: ret
"""


def test_every_backedge_remains_in_the_inventory_after_an_accumulator_chain():
    text=FUSED.replace('b0: ret',SECOND_LOOP)
    result=cg.inspect(text,elf())
    assert [l['header'] for l in result['loops']]==[0x30,0xc0]
    assert all(l['canonical_nan_stores'] and l['reductions'] for l in result['loops'])
    assert cg.check_shapes(result,cg.inspect(CONTROL,elf()))['fused_backedges']==[0xa0,0x130]


def test_combined_plus_later_separate_classification_is_not_fusion_proof():
    text=FUSED.replace('b0: ret',SECOND_LOOP.replace('100: movups %xmm4,(%rsi,%r8,8)','100: nop'))
    result=cg.inspect(text,elf())
    assert len(result['loops'])==2 and result['loops'][1]['reductions']
    with pytest.raises(ValueError):cg.check_shapes(result,cg.inspect(CONTROL,elf()))


def test_control_later_combined_loop_is_not_silently_skipped():
    tail="""
e0: xorpd %xmm0,%xmm0
f0: movupd (%rdi,%r8,8),%xmm5
100: andpd %xmm2,%xmm5
110: cmpnlepd %xmm3,%xmm5
120: orpd %xmm5,%xmm0
130: movups %xmm4,(%rsi,%r8,8)
140: add $4,%r8
150: cmp %r8,%rbx
160: jne f0 <factory+0xe0>
170: ret
"""
    control=cg.inspect(CONTROL.replace('e0: ret',tail),elf())
    assert len(control['loops'])==3 and control['loops'][2]['canonical_nan_stores']
    with pytest.raises(ValueError):cg.check_shapes(cg.inspect(FUSED,elf()),control)
