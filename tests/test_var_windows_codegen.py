"""Pure codegen gate tests; no products, compiler builds or timers are executed."""
import copy
import json
from pathlib import Path
import struct
import sys
import unittest

sys.path.insert(0, str(Path(__file__).parents[1] / 'scripts'))
import var_windows_codegen as G


def row(address, data, assembly):
    data = bytes.fromhex(data) if isinstance(data, str) else data
    op, *args = assembly.split('#', 1)[0].strip().split(None, 1)
    return dict(address=address, bytes=data, op=op, args=args[0] if args else '',
                assembly=assembly, next=address + len(data))


def lea(address, target):
    data = b'\x48\x8d\x05' + (target - address - 7).to_bytes(4, 'little', signed=True)
    return row(address, data, f'lea 0x{target-address-7:x}(%rip),%rax # {target:x}')


def call(address, target):
    return row(address, b'\xe8' + (target-address-5).to_bytes(4, 'little', signed=True), f'call {target:x}')


def carrier():
    rows = [lea(0x1000, 0x2000),
            row(0x1007, '48 89 44 24 20', 'mov %rax,0x20(%rsp)'),
            row(0x100c, '48 8d 44 24 20', 'lea 0x20(%rsp),%rax'),
            row(0x1011, '48 8b 44 24 20', 'mov 0x20(%rsp),%rax'),
            row(0x1016, 'ff d0', 'call *%rax')]
    return {r['address']: r for r in rows}


class FakeELF:
    def __init__(self):
        self.storage = {}
        self.symbols = []
        self.relocations = {}
        self.pointers = {}

    def put(self, address, data):
        for i, byte in enumerate(data):
            self.storage[address+i] = byte

    def read(self, address, count):
        try:
            return bytes(self.storage[address+i] for i in range(count))
        except KeyError as error:
            raise G.GateError('synthetic physical read extent') from error

    def functions_at(self, address):
        return sorted({s['name'] for s in self.symbols if s['address'] == address})

    def pointer(self, address):
        return self.pointers[address]

    def code_target(self, address):
        names = self.functions_at(address)
        G.need(names, 'synthetic unbound target')
        return {'functions': names}


def timed_graph():
    elf = FakeELF()
    functions = {
        0x100: ('bench_var_windows::main', [lea(0x100, 0x300), row(0x107, 'ff d0', 'call *%rax'),
            lea(0x109, 0x300), row(0x110, 'ff d0', 'call *%rax'), row(0x112, 'c3', 'ret')]),
        0x300: ('bench_var_windows::sample', [call(0x300, 0x900), call(0x305, 0x500),
            row(0x30a, 'ff c9', 'dec %ecx'), row(0x30c, '75 f7', 'jne 305'),
            call(0x30e, 0x920), row(0x313, 'c3', 'ret')]),
        0x500: ('bench_var_windows::Engine::batch', [lea(0x500, 0x1000), row(0x507, 'ff d0', 'call *%rax'),
            lea(0x509, 0x2000), row(0x510, 'ff d0', 'call *%rax'), row(0x512, 'c3', 'ret')])}
    rows, text = [], []
    for address, (name, items) in functions.items():
        elf.symbols.append(dict(address=address, size=items[-1]['next']-address, name=name))
        text.append(f'{address:016x} <{name}>:')
        rows.extend(items)
        for item in items:
            elf.put(item['address'], item['bytes'])
    elf.symbols += [dict(address=0x900, size=1, name='std::time::Instant::now'),
                    dict(address=0x920, size=1, name='std::time::Instant::elapsed')]
    scopes = {'var': {'address': 0x1000}, 'stddev': {'address': 0x2000}}
    return elf, rows, scopes, '\n'.join(text)


class CodegenTests(unittest.TestCase):
    def test_frozen_reference_profiles_and_role_domains(self):
        ref = G.load(G.REFERENCE)
        self.assertEqual(ref['source_commits'], G.PINS)
        self.assertEqual(set(ref['profiles']), {'1.90.0', '1.97.0'})
        for version, arms in ref['profiles'].items():
            self.assertEqual(set(arms), set(G.ARMS))
            for arm, functions in arms.items():
                self.assertEqual(set(functions), {'var', 'stddev'})
                for fn in functions.values():
                    offset = 0
                    for item in fn['schema']:
                        self.assertEqual(item['offset'], offset)
                        offset += len(bytes.fromhex(item['bytes']))
                    self.assertEqual(offset, fn['bytes'])
                if arm != 'original':
                    role = functions['var']['roles']
                    for kind in ('ordinary_continuation', 'ordinary_final_exit'):
                        self.assertEqual(len(role[kind]['conditional_bounds_guards']), 3 if arm == 'baseline' else 0)
                    self.assertEqual([len(x['bounds_guards']) for x in role['reseed_reanchor_subloops']],
                                     [0, 0, 0] if arm == 'baseline' else [1, 1, 1])

    def test_opaque_stack_roundtrip(self):
        result = G.carrier_path(carrier(), 0x1000, 0x2000)
        self.assertEqual(result['call'], 0x1016)
        self.assertTrue(result['stack_carrier_observed'])

    def test_register_roundtrip(self):
        items = [lea(0x1000, 0x2000), row(0x1007, '48 89 c3', 'mov %rax,%rbx'),
                 row(0x100a, 'ff d3', 'call *%rbx')]
        self.assertEqual(G.carrier_path({r['address']: r for r in items}, 0x1000, 0x2000)['call'], 0x100a)

    def test_partial_register_clobber(self):
        items = [lea(0x1000, 0x2000), row(0x1007, '31 c0', 'xor %eax,%eax'), row(0x1009, 'ff d0', 'call *%rax')]
        with self.assertRaises(G.GateError):
            G.carrier_path({r['address']: r for r in items}, 0x1000, 0x2000)

    def test_untracked_rsp_lea_rewrite_rejects(self):
        model = carrier()
        model[0x100c] = row(0x100c, '48 8d 64 24 08', 'lea 0x8(%rsp),%rsp')
        with self.assertRaisesRegex(G.GateError, 'stack pointer'):
            G.carrier_path(model, 0x1000, 0x2000)

    def test_esp_alias_rewrite_rejects(self):
        items = [lea(0x1000, 0x2000),
                 row(0x1007, '48 89 44 24 20', 'mov %rax,0x20(%rsp)'),
                 row(0x100c, '89 cc', 'mov %ecx,%esp'),
                 row(0x100e, '48 8b 44 24 20', 'mov 0x20(%rsp),%rax'),
                 row(0x1013, 'ff d0', 'call *%rax')]
        with self.assertRaisesRegex(G.GateError, 'stack pointer'):
            G.carrier_path({r['address']: r for r in items}, 0x1000, 0x2000)

    def test_unknown_implicit_clobber(self):
        items = [lea(0x1000, 0x2000), row(0x1007, '48 0f b1 cb', 'cmpxchg %rcx,%rbx'), row(0x100b, 'ff d0', 'call *%rax')]
        with self.assertRaisesRegex(G.GateError, 'unknown'):
            G.carrier_path({r['address']: r for r in items}, 0x1000, 0x2000)

    def test_direct_call_cannot_substitute(self):
        items = [lea(0x1000, 0x2000), call(0x1007, 0x2000)]
        with self.assertRaises(G.GateError):
            G.carrier_path({r['address']: r for r in items}, 0x1000, 0x2000)

    def test_wrong_indirect_register_bytes(self):
        item = row(0, 'ff d3', 'call *%rax')
        with self.assertRaises(G.GateError):
            G.indirect_operand(item)

    def test_stack_indirect_zero_displacement(self):
        self.assertEqual(G.indirect_operand(row(0, 'ff 14 24', 'call *(%rsp)')), '(%rsp)')

    def test_wrong_pointer_move_register(self):
        with self.assertRaises(G.GateError):
            G.checked_pointer_move(row(0, '48 89 c3', 'mov %rax,%rcx'))

    def test_partial_stack_overlap_rejects(self):
        model = carrier()
        model[0x100c] = row(0x100c, 'c7 44 24 24 00 00 00 00', 'movl $0x0,0x24(%rsp)')
        with self.assertRaisesRegex(G.GateError, 'overwritten'):
            G.carrier_path(model, 0x1000, 0x2000)

    def test_conditional_between_literal_and_call_rejects(self):
        model = carrier()
        model[0x100c] = row(0x100c, '75 00', 'jne 100e')
        with self.assertRaisesRegex(G.GateError, 'conditional'):
            G.carrier_path(model, 0x1000, 0x2000)

    def test_indirect_carrier_with_unknown_memory_alias_rejects(self):
        model = carrier()
        model[0x100c] = row(0x100c, '0f 11 03', 'movups %xmm0,(%rbx)')
        with self.assertRaisesRegex(G.GateError, 'alias'):
            G.carrier_path(model, 0x1000, 0x2000)

    def test_literal_destination_is_physical(self):
        elf = FakeELF();item = lea(0x1000, 0x2000)
        self.assertEqual(G.literal_target(elf, item, {0x2000}), 0x2000)
        item['args'] = item['args'].replace('%rax', '%rbx')
        with self.assertRaises(G.GateError):
            G.literal_target(elf, item, {0x2000})

    def test_branch_targets_bind_opcode(self):
        item = row(0x1000, '75 fe', 'jne 1000')
        self.assertEqual(G.branch_target(item), (0x1000, 1))
        item['args'] = '1001'
        with self.assertRaises(G.GateError):
            G.branch_target(item)

    def test_numeric_constant_and_instruction_bytes_bind(self):
        elf = FakeELF();address = 0x1000;target = 0x2000
        data = b'\xf2\x0f\x10\x05' + (target-address-8).to_bytes(4, 'little', signed=True)
        item = row(address, data, f'movsd 0xff8(%rip),%xmm0 # {target:x}')
        elf.put(address, data);elf.put(target, struct.pack('<d', 1e-6))
        before = G.normalized_scope(elf, [item], address, len(data))
        elf.put(target, struct.pack('<d', 1e-5))
        self.assertNotEqual(before, G.normalized_scope(elf, [item], address, len(data)))
        elf.put(address, b'\x90' + data[1:])
        with self.assertRaisesRegex(G.GateError, 'GNU bytes'):
            G.normalized_scope(elf, [item], address, len(data))

    def test_unknown_rip_operation_rejects(self):
        elf = FakeELF();item = row(0x1000, '48 8b 05 f9 0f 00 00', 'mov 0xff9(%rip),%rax # 2000')
        elf.put(0x1000, item['bytes'])
        with self.assertRaisesRegex(G.GateError, 'unknown constant'):
            G.normalized_scope(elf, [item], 0x1000, 7)

    def test_actual_timed_graph_positive(self):
        elf, rows, scopes, text = timed_graph()
        result = G.verify_routes(elf, rows, scopes, 'candidate', text)
        self.assertEqual({r['kind'] for r in result['verified_typed_timed_routes']}, {'var', 'stddev'})

    def test_missing_main_sample_literal_rejects(self):
        elf, rows, scopes, text = timed_graph()
        # Keep actual bytes valid but change one sample literal to a different target.
        changed = lea(0x109, 0x400)
        rows = [changed if r['address'] == 0x109 else r for r in rows];elf.put(0x109, changed['bytes'])
        with self.assertRaisesRegex(G.GateError, 'both warmup'):
            G.verify_routes(elf, rows, scopes, 'candidate', text)

    def test_fake_capture_only_graph_is_not_timing_proof(self):
        elf, rows, scopes, text = timed_graph()
        changed = call(0x305, 0x700)
        rows = [changed if r['address'] == 0x305 else r for r in rows];elf.put(0x305, changed['bytes'])
        with self.assertRaisesRegex(G.GateError, 'timer-root graph'):
            G.verify_routes(elf, rows, scopes, 'candidate', text)

    def test_missing_timer_call_rejects(self):
        elf, rows, scopes, text = timed_graph()
        elf.symbols = [s for s in elf.symbols if s['address'] != 0x920]
        with self.assertRaisesRegex(G.GateError, 'timer-call'):
            G.verify_routes(elf, rows, scopes, 'candidate', text)

    def test_edited_full_dump_byte_rejects(self):
        elf, rows, scopes, text = timed_graph()
        elf.put(0x300, b'\x90')
        with self.assertRaisesRegex(G.GateError, 'byte gap/mismatch'):
            G.verify_routes(elf, rows, scopes, 'candidate', text)

    def test_invalid_elf_header_rejects(self):
        with self.assertRaises(G.GateError):
            G.ELF(b'not ELF')


if __name__ == '__main__':
    unittest.main()
