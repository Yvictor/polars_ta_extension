"""Fail-closed codegen gate for the two reviewed Linux VAR profiles.

This reads normal enabled executables; it never executes a product or a timer.
The frozen schemas cover standalone public functions, not arbitrary x86 programs.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import struct
import subprocess

REFERENCE = Path(__file__).parents[1] / 'tests/data/var-windows/normal-codegen-reference.json'
ARMS = ('original', 'baseline', 'candidate')
PINS = {'original': '62021c1d14ef5499505af5547384cab509adf3fc',
        'baseline': 'b0a97ddb1fa26fc8ed8b58832442db9319c40296',
        'candidate': '4f73a88c554e8482fc566c2f351bca94b45946ab'}


class GateError(ValueError):
    pass


def need(value, reason):
    if not value:
        raise GateError(reason)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def file_sha(path):
    return digest(Path(path).read_bytes())


def load(path):
    def unique(items):
        result = {}
        for key, value in items:
            need(key not in result, 'duplicate JSON key')
            result[key] = value
        return result
    return json.loads(Path(path).read_text(), object_pairs_hook=unique,
                      parse_constant=lambda _: (_ for _ in ()).throw(GateError('nonfinite JSON')))


class ELF:
    """Only ELF64 little-endian x86-64, physical symbols and RELA are supported."""
    def __init__(self, data):
        self.data = data
        need(data[:7] == b'\x7fELF\x02\x01\x01' and len(data) >= 64, 'ELF64 LE required')
        h = self.unpack('<HHIQQQIHHHHHH', 16)
        typ, machine, version, _, po, so, _, hs, pe, pn, se, sn, _ = h
        need(typ in (2, 3) and machine == 62 and version == 1 and hs == 64 and pe == 56 and se == 64, 'ELF ABI')
        self.segments = [self.unpack('<II6Q', po + i * pe) for i in range(pn)]
        sections = [self.unpack('<II4QII2Q', so + i * se) for i in range(sn)]
        for p in self.segments:
            need(p[2] + p[5] <= len(data) and p[5] <= p[6], 'ELF segment extent')
        tables = {}
        self.symbols = []
        for i, s in enumerate(sections):
            if s[1] not in (2, 11):
                continue
            need(s[9] == 24 and s[6] < len(sections), 'ELF symbol table')
            st = sections[s[6]]
            strings = self.bytes(st[4], st[5])
            table = []
            for n in range(s[5] // 24):
                name, info, _, section, address, size = self.unpack('<IBBHQQ', s[4] + n * 24)
                need(name < len(strings), 'ELF symbol name extent')
                end = strings.find(b'\0', name)
                need(end >= name, 'ELF symbol name termination')
                item = dict(name=strings[name:end].decode('utf-8'), type=info & 15,
                            section=section, address=address, size=size)
                table.append(item)
                if item['type'] == 2 and size and section not in (0, 0xfff1, 0xfff2):
                    need(section < len(sections), 'ELF function section')
                    sec = sections[section]
                    need(sec[2] & 4 and sec[3] <= address and address + size <= sec[3] + sec[5], 'ELF function extent')
                    self.symbols.append(item)
            tables[i] = table
        self.relocations = {}
        for s in sections:
            if s[1] != 4:
                continue
            need(s[9] == 24 and s[6] in tables, 'ELF RELA table')
            for i in range(s[5] // 24):
                address, info, addend = self.unpack('<QQq', s[4] + i * 24)
                index = info >> 32
                need(index < len(tables[s[6]]) and address not in self.relocations, 'ELF RELA index/duplicate')
                self.relocations[address] = dict(type=info & 0xffffffff,
                    symbol=tables[s[6]][index], addend=addend)

    def bytes(self, offset, count):
        need(0 <= offset <= offset + count <= len(self.data), 'ELF file read extent')
        return self.data[offset:offset + count]

    def unpack(self, fmt, offset):
        return struct.unpack(fmt, self.bytes(offset, struct.calcsize(fmt)))

    def read(self, address, count):
        matches = [p for p in self.segments if p[0] == 1 and p[3] <= address and address + count <= p[3] + p[5]]
        need(len(matches) == 1, 'ELF virtual read is ambiguous or outside file')
        p = matches[0]
        return self.bytes(p[2] + address - p[3], count)

    def functions_at(self, address):
        return sorted({s['name'] for s in self.symbols if s['address'] == address})

    def pointer(self, address):
        r = self.relocations.get(address)
        if r:
            if r['type'] == 8:
                return r['addend'], None
            if r['type'] in (6, 7):
                return r['symbol']['address'] or None, r['symbol']['name']
            raise GateError('unsupported pointer relocation')
        return struct.unpack('<Q', self.read(address, 8))[0], None

    def code_target(self, address):
        names = self.functions_at(address)
        if names:
            return {'functions': names}
        # The only accepted PLT shape is the physical RIP-indirect jump stub.
        code = self.read(address, 6)
        if code[:2] == b'\xff\x25':
            slot = address + 6 + int.from_bytes(code[2:], 'little', signed=True)
            target, external = self.pointer(slot)
            if external:
                return {'external': external}
            need(target is not None and self.functions_at(target), 'unknown PLT target')
            return {'functions': self.functions_at(target)}
        raise GateError('unbound code target')


def instructions(text):
    """GNU objdump rows, including wrapped instruction bytes; no LLVM dialect."""
    result = []
    for line in text.splitlines():
        fields = line.strip().split('\t')
        if len(fields) < 2 or not re.fullmatch('[0-9a-f]+:', fields[0]):
            continue
        address = int(fields[0][:-1], 16)
        try:
            data = bytes.fromhex(fields[1])
        except ValueError as error:
            raise GateError('unparsed GNU instruction bytes') from error
        if len(fields) < 3 or not fields[2].strip():
            need(result and address == result[-1]['address'] + len(result[-1]['bytes']), 'orphan GNU byte continuation')
            result[-1]['bytes'] += data
            continue
        assembly = ' '.join(fields[2:]).strip()
        code = assembly.split('#', 1)[0].strip()
        pieces = code.split(None, 1)
        result.append(dict(address=address, bytes=data, op=pieces[0],
                           args=pieces[1] if len(pieces) > 1 else '', assembly=assembly))
    need(result, 'no GNU instructions')
    for item in result:
        item['next'] = item['address'] + len(item['bytes'])
    return result


def branch_target(item):
    data = item['bytes']
    conditions = ('jo', 'jno', 'jb', 'jae', 'je', 'jne', 'jbe', 'ja', 'js', 'jns', 'jp', 'jnp', 'jl', 'jge', 'jle', 'jg')
    if data[0] in (0xe9, 0xeb):
        width, op, delta = (4 if data[0] == 0xe9 else 1), 'jmp', data[1:]
    elif 0x70 <= data[0] <= 0x7f:
        width, op, delta = 1, conditions[data[0] - 0x70], data[1:]
    elif data[:1] == b'\x0f' and len(data) > 1 and 0x80 <= data[1] <= 0x8f:
        width, op, delta = 4, conditions[data[1] - 0x80], data[2:]
    else:
        raise GateError('unknown branch encoding')
    need(len(delta) == width and item['op'] == op, 'branch bytes/mnemonic')
    target = item['next'] + int.from_bytes(delta, 'little', signed=True)
    need(re.match(r'^[0-9a-f]+\b', item['args']) and target == int(item['args'].split()[0], 16), 'branch physical target')
    return target, width


def rip_target(item):
    match = re.search(r'#\s*([0-9a-f]+)\b', item['assembly'])
    need(match and '(%rip)' in item['args'], 'RIP target comment missing')
    data = item['bytes']
    # All frozen instructions put disp32 last; opcode/ModRM remain unmasked.
    need(len(data) >= 6, 'short RIP instruction')
    target = item['next'] + int.from_bytes(data[-4:], 'little', signed=True)
    need(target == int(match[1], 16), 'RIP bytes/comment mismatch')
    return target


def diagnostic_constant(elf, address):
    """Normalize pointer relocations in the fixed diagnostic object, not numbers."""
    data = bytearray(elf.read(address, 24))
    links = []
    for offset in (0, 8, 16):
        if address + offset in elf.relocations:
            target, external = elf.pointer(address + offset)
            need(target is not None and external is None, 'unknown diagnostic relocation')
            data[offset:offset + 8] = bytes(8)
            links.append(dict(offset=offset, bytes=elf.read(target, 24).hex()))
    return dict(bytes=bytes(data).hex(), pointer_targets=links)


def normalized_scope(elf, rows, start, size):
    selected = [r for r in rows if start <= r['address'] < start + size]
    need(selected and selected[0]['address'] == start, 'scope start missing')
    position = start
    result = []
    for item in selected:
        need(item['address'] == position and item['next'] <= start + size, 'scope byte gap/overlap')
        need(elf.read(position, len(item['bytes'])) == item['bytes'], 'GNU bytes differ from normal ELF')
        position = item['next']
        data = bytearray(item['bytes'])
        reference = None
        if item['op'].startswith('j'):
            target, width = branch_target(item)
            need(start <= target < start + size, 'branch outside frozen function')
            data[-width:] = bytes(width)
            reference = {'branch_offset': target - start}
        elif item['op'] == 'call' and re.match(r'^[0-9a-f]+\b', item['args']):
            need(data[:1] == b'\xe8' and len(data) == 5, 'direct call encoding')
            target = item['next'] + int.from_bytes(data[1:], 'little', signed=True)
            need(target == int(item['args'].split()[0], 16), 'direct call target')
            data[1:] = bytes(4)
            reference = {'call': elf.code_target(target)}
        elif '(%rip)' in item['args']:
            target = rip_target(item)
            data[-4:] = bytes(4)
            if item['op'] == 'call':
                need(item['bytes'][:2] == b'\xff\x15', 'GOT call encoding')
                value, external = elf.pointer(target)
                reference = {'call': {'external': external} if external else elf.code_target(value)}
            elif item['op'] == 'lea':
                reference = {'diagnostic': diagnostic_constant(elf, target)}
            else:
                widths = {'movsd': 8, 'ucomisd': 8, 'comisd': 8, 'movapd': 16, 'andpd': 16}
                need(item['op'] in widths, 'unknown constant memory operation')
                reference = {'constant': elf.read(target, widths[item['op']]).hex()}
        elif item['op'] == 'call':
            raise GateError('unknown call in frozen public scope')
        result.append(dict(offset=item['address'] - start, bytes=bytes(data).hex(), reference=reference))
    need(position == start + size, 'scope end missing')
    return result


def operands(text):
    result, depth, begin = [], 0, 0
    for i, char in enumerate(text):
        if char == '(':
            depth += 1
        elif char == ')':
            depth -= 1
        elif char == ',' and depth == 0:
            result.append(text[begin:i].strip()); begin = i + 1
    need(depth == 0, 'operand parentheses')
    return result + [text[begin:].strip()]


def register(value, full=True):
    if re.fullmatch(r'%(?:r(?:ax|bx|cx|dx|si|di|bp|sp|[89]|1[0-5]))', value):
        return value[1:]
    if not full:
        aliases = {'eax': 'rax', 'ax': 'rax', 'al': 'rax', 'ah': 'rax',
                   'ebx': 'rbx', 'bx': 'rbx', 'bl': 'rbx', 'bh': 'rbx',
                   'ecx': 'rcx', 'cx': 'rcx', 'cl': 'rcx', 'ch': 'rcx',
                   'edx': 'rdx', 'dx': 'rdx', 'dl': 'rdx', 'dh': 'rdx',
                   'esi': 'rsi', 'si': 'rsi', 'sil': 'rsi',
                   'edi': 'rdi', 'di': 'rdi', 'dil': 'rdi',
                   'ebp': 'rbp', 'bp': 'rbp', 'bpl': 'rbp',
                   'esp': 'rsp', 'sp': 'rsp', 'spl': 'rsp'}
        name = value.removeprefix('%')
        if name in aliases:
            return aliases[name]
        match = re.fullmatch(r'(r(?:[89]|1[0-5]))[dwb]', name)
        if match:
            return match[1]
    return None


def stack_slot(value, delta):
    match = re.fullmatch(r'(?:(-?0x[0-9a-f]+|-?[0-9]+))?\(%rsp\)', value)
    return delta + int(match[1] or '0', 0) if match else None


def indirect_operand(item):
    """Bind the limited register/RSP indirect call syntax to its opcode/ModRM."""
    data = item['bytes']
    rex = 0
    if data and 0x40 <= data[0] <= 0x4f:
        rex, data = data[0], data[1:]
    need(len(data) >= 2 and data[0] == 0xff and ((data[1] >> 3) & 7) == 2,
         'indirect call must be physical FF /2')
    mod, rm = data[1] >> 6, data[1] & 7
    names = ('rax', 'rcx', 'rdx', 'rbx', 'rsp', 'rbp', 'rsi', 'rdi')
    operand = item['args'].split('#', 1)[0].strip()
    need(operand.startswith('*'), 'indirect call syntax')
    operand = operand[1:]
    if mod == 3:
        need(len(data) == 2, 'register indirect call extent')
        name = 'r' + str(rm + 8) if rex & 1 else names[rm]
        need(operand == '%' + name, 'register indirect call bytes/operand')
    else:
        need(rm == 4 and not rex & 3 and len(data) >= 3 and data[2] == 0x24,
             'only private RSP-slot indirect calls supported')
        width = {0: 0, 1: 1, 2: 4}[mod]
        need(len(data) == 3 + width, 'stack indirect call extent')
        displacement = int.from_bytes(data[3:], 'little', signed=True) if width else 0
        need(stack_slot(operand, 0) == displacement, 'stack indirect call bytes/operand')
    return operand


def checked_pointer_move(item):
    """A tainted pointer may move only via a decoded 64-bit MOV, register/RSP."""
    data = item['bytes']
    need(len(data) >= 3 and 0x48 <= data[0] <= 0x4f and data[1] in (0x89, 0x8b),
         'pointer carrier requires decoded MOV64')
    rex, opcode, modrm = data[0], data[1], data[2]
    mod, rm, reg = modrm >> 6, modrm & 7, (modrm >> 3) & 7
    names = ('rax', 'rcx', 'rdx', 'rbx', 'rsp', 'rbp', 'rsi', 'rdi')
    regname = 'r' + str(reg + 8) if rex & 4 else names[reg]
    if mod == 3:
        need(len(data) == 3, 'MOV64 register extent')
        rmname = 'r' + str(rm + 8) if rex & 1 else names[rm]
        memory = '%' + rmname
    else:
        need(rm == 4 and not rex & 3 and len(data) >= 4 and data[3] == 0x24,
             'pointer spill must use private RSP slot')
        width = {0: 0, 1: 1, 2: 4}[mod]
        need(len(data) == 4 + width, 'MOV64 stack extent')
        displacement = int.from_bytes(data[4:], 'little', signed=True) if width else 0
        memory = ('-0x%x' % -displacement if displacement < 0 else '0x%x' % displacement) + '(%rsp)'
    expected = [('%' + regname), memory] if opcode == 0x89 else [memory, ('%' + regname)]
    actual = operands(item['args'])
    need(len(actual) == 2, 'MOV64 carrier operands')
    for got, wanted in zip(actual, expected):
        if '(%rsp)' in wanted:
            need(stack_slot(got, 0) == stack_slot(wanted, 0), 'MOV64 physical stack operand')
        else:
            need(got == wanted, 'MOV64 physical register operand')


def carrier_path(model, literal, target):
    """A single bounded literal carrier, no conditional fork or unknown call."""
    first = model[literal]
    parts = operands(first['args'])
    need(len(parts) == 2 and register(parts[1]), 'function literal register')
    registers = {register(parts[1]): target}
    slots, delta, seen, path = {}, 0, set(), [literal]
    address = first['next']
    for _ in range(128):
        need(address in model and address not in seen, 'literal carrier leaves scope or cycles')
        seen.add(address)
        item = model[address]; path.append(address)
        op, args = item['op'], operands(item['args'])
        allowed = {'call', 'jmp', 'mov', 'movq', 'movl', 'lea', 'movsd', 'movaps', 'movups', 'movapd', 'movupd', 'movdqu', 'xor', 'pxor', 'xorpd', 'add', 'sub', 'and', 'or', 'shl', 'shr', 'sar', 'cmp', 'test', 'inc', 'dec', 'neg', 'not', 'push', 'pushq', 'pop', 'popq', 'nop', 'nopl', 'nopw', 'data16', 'cs', 'cvtsi2sd'}
        need(op in allowed or op.startswith('j') or op.startswith('ret'), 'unknown pointer-carrier operation')
        if op == 'call':
            value = indirect_operand(item)
            reg, slot = register(value), stack_slot(value, delta)
            resolved = registers.get(reg) if reg else slots.get(slot)
            need(resolved == target, 'indirect call does not own selected literal')
            return {'literal': literal, 'call': address, 'path': path,
                    'stack_carrier_observed': bool(slots), 'target': target}
        if op == 'jmp':
            address, _ = branch_target(item); continue
        need(not op.startswith('j') and not op.startswith('ret'), 'conditional/return before opaque call')
        if op in ('push', 'pushq'):
            delta -= 8
            value = registers.get(register(args[0]))
            slots.pop(delta, None)
            if value is not None: slots[delta] = value
        elif op in ('pop', 'popq'):
            need(register(args[0], full=False) != 'rsp', 'unsupported stack pointer pop')
            reg = register(args[0]); value = slots.pop(delta, None); delta += 8
            if reg:
                registers.pop(reg, None)
                if value is not None: registers[reg] = value
        elif op in ('inc', 'dec', 'neg', 'not'):
            need(register(args[0], full=False) != 'rsp', 'unsupported stack pointer arithmetic')
            registers.pop(register(args[0], full=False), None)
        elif op in ('xchg', 'xadd', 'mul', 'imul', 'div', 'idiv', 'cqo', 'cdq'):
            raise GateError('unknown implicit/two-sided pointer-carrier clobber')
        elif len(args) == 2:
            source, destination = args
            destreg = register(destination, full=False); destslot = stack_slot(destination, delta)
            value = registers.get(register(source))
            if value is None:
                value = slots.get(stack_slot(source, delta))
            need(destreg != 'rsp' or (op in ('sub', 'add') and destination == '%rsp'), 'unsupported stack pointer rewrite')
            if op in ('sub', 'add') and destination == '%rsp':
                need(re.fullmatch(r'\$0x[0-9a-f]+', source), 'unknown stack adjustment')
                amount = int(source[1:], 16); delta += amount if op == 'add' else -amount
            elif op in ('mov', 'movq'):
                if value is not None:
                    checked_pointer_move(item)
                if destreg:
                    registers.pop(destreg, None)
                    if value is not None and register(destination): registers[destreg] = value
                elif destslot is not None:
                    for slot in list(slots):
                        if abs(destslot - slot) < 8:
                            slots.pop(slot)
                    if value is not None: slots[destslot] = value
                elif value is not None:
                    raise GateError('function pointer escapes private carrier')
                elif '(' in destination and slots:
                    raise GateError('unresolved memory alias in opaque carrier')
            elif destreg:
                registers.pop(destreg, None)
            elif destslot is not None:
                width = 16 if op in ('movaps', 'movups', 'movapd', 'movupd', 'movdqu') else 8
                need(not any(destslot < slot + 8 and slot < destslot + width for slot in slots), 'opaque pointer stack slot overwritten')
            elif '(' in destination and slots:
                raise GateError('unresolved memory alias in opaque carrier')
        else:
            need(op in ('nop', 'nopl', 'nopw', 'data16', 'cs'), 'unknown pointer-carrier instruction')
        address = item['next']
    raise GateError('function literal carrier exceeds bound')


def _dump(binary, destination):
    result = subprocess.run(['objdump', '-d', '-r', '-C', str(binary)], capture_output=True, check=False)
    destination.write_bytes(result.stdout)
    destination.with_suffix('.stderr').write_bytes(result.stderr)
    need(result.returncode == 0 and not result.stderr, 'GNU full disassembly failed')
    need(b'file format elf64-x86-64' in result.stdout, 'GNU dialect/architecture')
    return instructions(result.stdout.decode('utf-8'))


def verify(output: Path, rust_version: str) -> dict:
    output = Path(output).resolve()
    need(rust_version in ('1.90.0', '1.97.0'), 'unreviewed compiler')
    reference = load(REFERENCE)
    need(reference['format'] == 1, 'codegen reference format')
    p = load(output / 'preflight.json')
    need(p['pins'] == PINS and p['timing_enabled'] is False and
         p['timings_collected'] is False and p['timer_body_compiled'] is True, 'capture-only enabled-body preflight')
    expected_profile = dict(CARGO_PROFILE_RELEASE_OPT_LEVEL='3', CARGO_PROFILE_RELEASE_LTO='false' if rust_version == '1.90.0' else 'thin',
        CARGO_PROFILE_RELEASE_CODEGEN_UNITS='16' if rust_version == '1.90.0' else '1', CARGO_PROFILE_RELEASE_DEBUG='false',
        RUSTFLAGS='', CARGO_ENCODED_RUSTFLAGS='', CFLAGS='', CXXFLAGS='')
    need(p['runtime']['profile'] == expected_profile and p['runtime']['rustc'].startswith('rustc ' + rust_version + ' '), 'normal profile/compiler')
    folder = output / 'enabled-codegen-gate'
    folder.mkdir(exist_ok=False)
    details, binaries = {}, {}
    for arm in ARMS:
        binary = output / arm
        need(binary.is_file() and not binary.is_symlink(), 'normal executable missing/symlink')
        binaries[arm] = file_sha(binary)
        meta = p['binaries'][arm]
        need(meta['sha256'] == binaries[arm] and meta['description']['timing_enabled'] is True and
             meta['description']['opaque_fnptr'] is True and meta['description']['pointer_bytes'] == 8, 'enabled opaque-FnPtr binary binding')
        elf = ELF(binary.read_bytes())
        rows = _dump(binary, folder / (arm + '.asm'))
        scopes = {}
        for name in ('var', 'stddev'):
            scope = meta['elf']['scopes'][name]
            start, size = scope['address'], scope['bytes']
            need(any(s['address'] == start and s['size'] == size for s in elf.symbols), 'physical public symbol extent')
            actual = normalized_scope(elf, rows, start, size)
            frozen = reference['profiles'][rust_version][arm][name]
            need(elf.functions_at(start) == frozen['physical_symbols'] and scope['symbol'] == frozen['historical_symbol'], 'public function identity changed')
            need(size == frozen['bytes'] and actual == frozen['schema'], 'unknown enabled public code/constant layout')
            scopes[name] = dict(address=start, bytes=size, normalized_schema_sha256=digest(json.dumps(actual, sort_keys=True).encode()),
                                reviewed_roles=frozen['roles'])
        # Actual carrier/timed-root proof is mandatory; descriptors are not proof.
        routes = verify_routes(elf, rows, scopes, arm, (folder / (arm + '.asm')).read_text())
        details[arm] = {'scopes': scopes, 'opaque_routes': routes}
    files = {str(path.relative_to(output)): file_sha(path) for path in folder.rglob('*') if path.is_file()}
    result = dict(timing_allowed=True, rust_version=rust_version, preflight_sha256=file_sha(output / 'preflight.json'),
        binary_sha256=binaries, source_commits=PINS, profile=expected_profile,
        reference_sha256=file_sha(REFERENCE), codegen_module_sha256=file_sha(Path(__file__)), files=files,
        scoped_details=details, limitations=reference['limitations'])
    destination = output / 'enabled-elf-gate.json'
    need(not destination.exists(), 'never overwrite prior gate')
    destination.write_text(json.dumps(result, indent=2) + '\n')
    return result


def call_target(elf, item):
    if item['op'] != 'call':
        return None
    if re.match(r'^[0-9a-f]+\b', item['args']):
        need(item['bytes'][:1] == b'\xe8' and len(item['bytes']) == 5, 'direct call bytes')
        target = item['next'] + int.from_bytes(item['bytes'][1:], 'little', signed=True)
        need(target == int(item['args'].split()[0], 16), 'direct call address')
        return target
    if '(%rip)' in item['args']:
        need(item['bytes'][:2] == b'\xff\x15', 'GOT call bytes')
        target, _ = elf.pointer(rip_target(item))
        return target
    return None


def literal_target(elf, item, targets):
    if item['op'] == 'lea' and '(%rip)' in item['args']:
        value = rip_target(item)
    elif item['op'] in ('mov', 'movq') and '(%rip)' in item['args']:
        value, external = elf.pointer(rip_target(item))
        if external:
            return None
    elif item['op'] in ('mov', 'movabs') and re.match(r'^\$0x[0-9a-f]+,', item['args']):
        parts = operands(item['args'])
        data = item['bytes']
        if len(data) != 10 or data[0] not in (0x48, 0x49) or not 0xb8 <= data[1] <= 0xbf:
            return None
        value = int.from_bytes(data[2:], 'little')
        need(value == int(parts[0][1:], 16), 'function literal immediate bytes')
    else:
        return None
    if value not in targets:
        return None
    parts = operands(item['args'])
    need(len(parts) == 2 and register(parts[1]), 'literal full pointer destination')
    data = item['bytes']
    if '(%rip)' in item['args']:
        wanted = 0x8d if item['op'] == 'lea' else 0x8b
        need(len(data) == 7 and 0x48 <= data[0] <= 0x4f and data[1] == wanted and data[2] & 0xc7 == 0x05, 'function literal RIP opcode')
        reg = (data[2] >> 3) & 7
        names = ('rax', 'rcx', 'rdx', 'rbx', 'rsp', 'rbp', 'rsi', 'rdi')
        wantedreg = 'r' + str(reg + 8) if data[0] & 4 else names[reg]
    else:
        reg = data[1] - 0xb8
        names = ('rax', 'rcx', 'rdx', 'rbx', 'rsp', 'rbp', 'rsi', 'rdi')
        wantedreg = 'r' + str(reg + 8) if data[0] & 1 else names[reg]
    need(register(parts[1]) == wantedreg, 'function literal physical register')
    return value


def function_views(elf, rows, text):
    headers = [(int(m[1], 16), m[2]) for m in re.finditer(r'^([0-9a-f]+) <(.+)>:$', text, re.M)]
    result = {}
    for address, name in headers:
        if 'bench_var_windows::' not in name and 'bench_var_windows::' not in name.replace('<', ''):
            continue
        physical = [s for s in elf.symbols if s['address'] == address]
        sizes = {s['size'] for s in physical}
        need(len(sizes) == 1, 'ambiguous physical harness function extent')
        size = next(iter(sizes))
        selected = [r for r in rows if address <= r['address'] < address + size]
        need(selected and selected[0]['address'] == address, 'harness function start')
        position = address
        for item in selected:
            need(item['address'] == position and elf.read(position, len(item['bytes'])) == item['bytes'], 'harness instruction byte gap/mismatch')
            position = item['next']
        need(position == address + size, 'harness function end')
        result[address] = {'name': name, 'rows': selected, 'model': {r['address']: r for r in selected}, 'size': size}
    need(result, 'physical harness namespace absent')
    return result


def timed_interval(elf, view):
    time_calls = []
    for item in view['rows']:
        target = call_target(elf, item)
        if target is None:
            continue
        names = elf.functions_at(target)
        if any('Instant' in n and ('now' in n or 'elapsed' in n) for n in names):
            time_calls.append(item['address'])
    need(len(time_calls) == 2, 'unknown actual sample timer-call schema')
    begin, end = time_calls
    need(begin < end, 'timer order')
    loops = []
    for item in view['rows']:
        if item['op'].startswith('j'):
            target, _ = branch_target(item)
            if begin < target < item['address'] < end:
                loops.append((target, item['address']))
    need(loops, 'actual sample inner timing loop missing')
    return begin, end, loops


def verify_routes(elf, rows, scopes, arm, text=None):
    need(text is not None, 'full physical GNU function headers required')
    views = function_views(elf, rows, text)
    samples = [a for a, v in views.items() if v['name'].endswith('::sample')]
    mains = [a for a, v in views.items() if v['name'].endswith('::main')]
    need(len(samples) == len(mains) == 1, 'normal SampleFn/main symbols must be unique')
    sample, main = samples[0], mains[0]
    targets = {scopes['var']['address']: 'var', scopes['stddev']['address']: 'stddev', sample: 'sample'}
    need(len(targets) == 3, 'public/sample target identities overlap')
    routes, edges = [], {a: [] for a in views}
    for address, view in views.items():
        for item in view['rows']:
            literal = literal_target(elf, item, targets)
            if literal is not None:
                route = carrier_path(view['model'], item['address'], literal)
                routes.append({**route, 'kind': targets[literal], 'owner': address, 'owner_name': view['name']})
            called = call_target(elf, item)
            need(called not in targets, 'direct/GOT public or sample call bypasses opaque FnPtr')
            if called in views:
                edges[address].append((item['address'], called))
    sample_routes = [r for r in routes if r['kind'] == 'sample' and r['owner'] == main]
    need(len({r['call'] for r in sample_routes}) >= 2, 'both warmup/measurement SampleFn literal carriers required')
    begin, end, loops = timed_interval(elf, views[sample])
    intervals = []
    reachable = {sample}
    for _ in range(8):
        expanded = reachable | {callee for node in reachable for _, callee in edges[node]}
        if expanded == reachable:
            break
        reachable = expanded
    else:
        raise GateError('unknown recursive/deep timer call graph')
    for role in ('var', 'stddev'):
        found = [r for r in routes if r['kind'] == role and r['owner'] in reachable]
        need(found, 'timer-root graph does not own opaque public ' + role)
        for route in found:
            if route['owner'] == sample:
                sites = [route['call']]
            else:
                # A bounded direct sample edge is required; no arbitrary deeper SSA walk.
                sites = [at for at, callee in edges[sample] if callee == route['owner']]
                need(sites, 'unknown deeper typed-call ownership graph')
            matched = [(lo, hi) for lo, hi in loops if any(lo <= site <= hi for site in sites)]
            need(matched, 'opaque typed call not inside actual sample loop/timer interval')
            intervals.append({'kind': role, 'route_owner': route['owner'], 'call': route['call'],
                              'timer_loop_bounds': matched})
    return {'sample_address': sample, 'sample_timer_call_interval': [begin, end],
            'sample_inner_loops': loops, 'routes': routes, 'verified_typed_timed_routes': intervals,
            'source_scope': 'Explicit opaque SampleFn and public VAR/STDDEV FnPtrs; controlled matched dispatch, not historical direct/FnItem/Polars execution.'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--rust-version', required=True, choices=('1.90.0', '1.97.0'))
    args = parser.parse_args()
    print(json.dumps(verify(args.output, args.rust_version), indent=2))
