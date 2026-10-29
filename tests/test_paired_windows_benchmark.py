"""Standalone fail-closed tests; run without the Polars package conftest."""
import copy
import importlib.util
import json
from pathlib import Path
import struct
import subprocess
from types import SimpleNamespace

import pytest

spec = importlib.util.spec_from_file_location('paired_windows_benchmark', Path(__file__).parents[1] / 'scripts/paired_windows_benchmark.py')
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
FNV = 'ba4ce2a7bf8baf01'


def metadata(mode, selected=None, record_bytes=0):
    return {'kind': 'metadata', 'format': 1, 'mode': mode, 'selected_case': selected,
            'cases': len(m.TIMED_CASES), 'validation_cases': len(m.VALIDATION_CASES),
            'capture_records': len(m.SPECS) if mode == 'capture-full' else 1,
            'warmups': 5, 'repeats': 31, 'arch': 'x86_64', 'os': 'linux', 'version': '0.8.4',
            'input_bytes': 8000000, 'close_fnv1a64': FNV,
            'selected_validated': mode == 'bench', 'actual_capture_written': True,
            'selected_record_bytes': 0 if mode == 'capture-full' else record_bytes + 8}


def raw_record(name, value=1.25):
    expected = m.SPECS[name].expected(); n = expected['n']; count = expected['count']
    def string(s):
        b = s.encode(); return struct.pack('<I', len(b)) + b
    payload = string(name) + string(expected['status'])
    payload += struct.pack('<7Q', *(expected[k] for k in ('n', 'start', 'end', 'beg', 'count', 'real_outputs', 'integer_outputs')))
    for _ in range(expected['real_outputs']):
        values = struct.pack('<Q', m.CANARY) + struct.pack('<d', value) * count + struct.pack('<Q', m.CANARY) * (n + 7 - count)
        payload += struct.pack('<Q', n + 8) + values
    for _ in range(expected['integer_outputs']):
        values = struct.pack('<i', m.ICANARY) + struct.pack('<i', 1) * count + struct.pack('<i', m.ICANARY) * (n + 7 - count)
        payload += struct.pack('<Q', n + 8) + values
    return struct.pack('<Q', len(payload)) + payload


def json_row(name, mode):
    row = {'kind': 'case' if mode == 'bench' else 'capture', 'case': name,
           **m.SPECS[name].expected(), 'record_bytes': len(raw_record(name))}
    if mode == 'bench':
        row.update(iterations=max(100000 // m.SPECS[name].n, 1), warmups=5, samples_ns=[100.] * 31)
    return row


def json_records(mode, selected=None):
    names = sorted(m.SPECS) if mode == 'capture-full' else [selected]
    size = 0 if selected is None else len(raw_record(selected))
    return [metadata(mode, selected, size), *(json_row(n, mode) for n in names)]


def encode(rows):
    return '\n'.join(json.dumps(r) for r in rows)


@pytest.fixture
def small(monkeypatch):
    name = 'supertrend/default/100'
    validation = 'validation/supertrend/error/empty_output_before_warmup'
    monkeypatch.setattr(m, 'TIMED_CASES', {name})
    monkeypatch.setattr(m, 'VALIDATION_CASES', {validation})
    monkeypatch.setattr(m, 'SPECS', {name: m.Spec('supertrend', 100), validation: m.Spec('supertrend', 1, error='empty_output', capacity_variant='empty')})
    return name


def test_inventory_and_independent_range_rules():
    assert len(m.TIMED_CASES) == 28 and len(m.VALIDATION_CASES) == 494 and len(m.SPECS) == 522
    for name, lb in [('supertrend', 10), ('accbands', 19), ('kvo', 55), ('wavetrend', 41),
                     ('macd_control', 33), ('macdfix_control', 33), ('ema_control', 29), ('sma_control', 29)]:
        assert m.Spec(name, 1000).expected()['beg'] == lb
    assert m.Spec('wavetrend', 1000, unstable=3).expected()['beg'] == 50
    assert m.Spec('kvo', 1000, unstable=3).expected()['beg'] == 58
    assert m.Spec('macd_control', 1000, unstable=3).expected()['beg'] == 39
    assert m.Spec('ema_control', 1000, param_variant='minimum').expected()['beg'] == 0
    assert m.Spec('macd_control', 250000, param_variant='maxfirst').expected()['beg'] == 100007
    overflow = m.SPECS['validation/kvo/error/start_overflow'].expected()
    assert overflow['start'] == 100000001 and overflow['status'] == 'OutOfRangeStartIndex'


def test_all_six_orders_twice_for_every_case():
    orders = [m.order_for_round(i) for i in range(12)]
    assert len(set(orders)) == 6 and orders[:6] == orders[6:]
    for side in m.SIDES:
        for position in range(3):
            assert sum(order[position] == side for order in orders) == 4
    for invalid in (-1, 12, True):
        with pytest.raises(ValueError): m.order_for_round(invalid)


def test_valid_modes_and_normalized_metadata(small):
    full = m.parse_records(encode(json_records('capture-full')), 'capture-full', close_fnv=FNV)
    selected = m.parse_records(encode(json_records('capture-case', small)), 'capture-case', small, FNV)
    bench = m.parse_records(encode(json_records('bench', small)), 'bench', small, FNV)
    assert m.stable_metadata(full['metadata']) == m.stable_metadata(selected['metadata']) == m.stable_metadata(bench['metadata'])
    assert set(bench['cases']) == {small}


@pytest.mark.parametrize('field,value', [('format', True), ('version', '0.8.3'), ('os', 'macos'), ('arch', 'aarch64'),
    ('cases', 0), ('validation_cases', True), ('capture_records', 1), ('warmups', 4), ('repeats', 30),
    ('input_bytes', 0), ('close_fnv1a64', '0' * 16), ('actual_capture_written', False), ('selected_validated', True),
    ('selected_record_bytes', 8), ('mode', 'bench'), ('selected_case', 'bad')])
def test_metadata_fail_closed(small, field, value):
    rows = json_records('capture-full'); rows[0][field] = value
    with pytest.raises(ValueError): m.parse_records(encode(rows), 'capture-full', close_fnv=FNV)


@pytest.mark.parametrize('field,value', [('n', 99), ('beg', 9), ('count', True), ('status', 'BadParam'),
    ('start', 1), ('end', 98), ('real_outputs', 2), ('integer_outputs', 0), ('output_capacity', 100),
    ('pattern', 'zero'), ('param_variant', 'minimum'), ('unstable', 1), ('short_input', True), ('record_bytes', False)])
def test_semantic_headers_fail_closed(small, field, value):
    rows = json_records('bench', small); rows[1][field] = value
    with pytest.raises(ValueError): m.parse_records(encode(rows), 'bench', small, FNV)


@pytest.mark.parametrize('mutation', ['duplicate_metadata', 'missing_metadata', 'row_before_metadata', 'missing_case',
    'duplicate_case', 'unknown_case', 'timing_in_capture', 'unknown_field', 'duplicate_json_key'])
def test_inventory_and_protocol_order_fail_closed(small, mutation):
    rows = json_records('capture-full')
    if mutation == 'duplicate_metadata': rows.insert(1, rows[0])
    elif mutation == 'missing_metadata': rows.pop(0)
    elif mutation == 'row_before_metadata': rows[0], rows[1] = rows[1], rows[0]
    elif mutation == 'missing_case': rows.pop()
    elif mutation == 'duplicate_case': rows.append(rows[-1])
    elif mutation == 'unknown_case': rows[-1]['case'] = 'bogus'
    elif mutation == 'timing_in_capture': rows[-1]['kind'] = 'case'
    elif mutation == 'unknown_field': rows[-1]['samples_ns'] = [1.] * 31
    if mutation == 'duplicate_json_key':
        text = encode(rows).replace('"format": 1', '"format": 1, "format": 1')
    else: text = encode(rows)
    with pytest.raises(ValueError): m.parse_records(text, 'capture-full', close_fnv=FNV)


@pytest.mark.parametrize('sample', [0., -1., float('inf'), float('nan'), True, -0.])
def test_samples_and_prevalidation_are_mandatory(small, sample):
    rows = json_records('bench', small); rows[1]['samples_ns'][0] = sample
    with pytest.raises(ValueError): m.parse_records(encode(rows), 'bench', small, FNV)
    rows = json_records('bench', small); rows[0]['selected_validated'] = False
    with pytest.raises(ValueError): m.parse_records(encode(rows), 'bench', small, FNV)


@pytest.mark.parametrize('field,value', [('iterations', 1), ('warmups', 4), ('samples_ns', [1.] * 30)])
def test_no_repetition_or_iteration_cuts(small, field, value):
    rows = json_records('bench', small); rows[1][field] = value
    with pytest.raises(ValueError): m.parse_records(encode(rows), 'bench', small, FNV)


def test_raw_guards_order_shapes_and_exact_hash(small, tmp_path):
    path = tmp_path / 'capture.bin'
    content = m.MAGIC + b''.join(raw_record(n) for n in sorted(m.SPECS))
    path.write_bytes(content)
    valid = m.read_capture(path)
    assert len(valid['records']) == 2 and valid['all_guards_checked']
    changed = bytearray(content); changed[-1] ^= 1; path.write_bytes(changed)
    with pytest.raises(ValueError, match='guard'): m.read_capture(path)
    path.write_bytes(content + raw_record(small))
    with pytest.raises(ValueError, match='duplicate'): m.read_capture(path)
    path.write_bytes(content[:-1])
    with pytest.raises(ValueError, match='truncated'): m.read_capture(path)
    path.write_bytes(content + b'bad')
    with pytest.raises(ValueError, match='truncated'): m.read_capture(path)
    path.write_bytes(b'BADMAGIC' + content[8:])
    with pytest.raises(ValueError, match='magic'): m.read_capture(path)


def test_raw_references_compare_actual_bits_not_just_json(small, tmp_path):
    paths = {s: tmp_path / (s + '.bin') for s in m.SIDES}
    for side, path in paths.items():
        path.write_bytes(m.MAGIC + b''.join(raw_record(n, 1. if side != 'paired' else 2.) for n in sorted(m.SPECS)))
    with pytest.raises(ValueError, match='raw bits'): m.validate_capture_pair(paths)
    paths['paired'].write_bytes(paths['before'].read_bytes())
    assert m.validate_capture_pair(paths)['paired']['sha256'] == m.sha256(paths['before'])


def test_golden_split_is_exact_and_refuses_rewrite(small, tmp_path):
    full = tmp_path / 'all.bin'; full.write_bytes(m.MAGIC + b''.join(raw_record(n) for n in sorted(m.SPECS)))
    index = m.read_capture(full); goldens = m.write_goldens(full, index, tmp_path / 'goldens')
    assert Path(goldens[small]['path']).read_bytes() == m.MAGIC + raw_record(small)
    m.read_capture(goldens[small]['path'], {small})
    with pytest.raises(FileExistsError): m.write_goldens(full, index, tmp_path / 'goldens')


def allocation_row(name):
    expected = m.SPECS[name].expected()
    return {'kind': 'allocation', 'format': 1, 'case': name,
            **{k: expected[k] for k in ('n', 'start', 'end', 'status', 'beg', 'count')},
            'version': '0.8.4', 'arch': 'x86_64', 'os': 'linux', 'input_bytes': 8000000,
            'close_fnv1a64': FNV, **dict.fromkeys(m.ALLOCATION_COUNTERS, 0)}


def orchestration(monkeypatch, tmp_path, small, mismatch_full=False, mismatch_selected=False, invalid_selected=False):
    data = m.MAGIC + b''.join(raw_record(n) for n in sorted(m.SPECS))
    output = tmp_path / 'out'; output.mkdir()
    provenance = {'input': {'path': '/input', 'sha256': m.CLOSE_SHA, 'close_fnv1a64': FNV},
                  'runtime': {}, **{s: {'binary': s, 'binary_sha256': s, 'diagnostic_binary': s + '-allocation'} for s in m.SIDES}}
    (output / 'build-provenance.json').write_text('{}')
    monkeypatch.setattr(m, 'verify_provenance', lambda args: provenance)
    monkeypatch.setattr(m, 'verify_input', lambda record: record['sha256'])
    affinities = []
    monkeypatch.setattr(m.os, 'sched_getaffinity', lambda pid: {3, 4}, raising=False)
    monkeypatch.setattr(m.os, 'sched_setaffinity', lambda pid, values: affinities.append(set(values)), raising=False)
    calls = []
    def fake_run(command, **kwargs):
        calls.append(command)
        if command[1] == '--capture-full':
            bytes_ = data
            if mismatch_full and command[0] == 'paired': bytes_ = m.MAGIC + b''.join(raw_record(n, 2.) for n in sorted(m.SPECS))
            Path(command[2]).write_bytes(bytes_)
            return SimpleNamespace(returncode=0, stdout=encode(json_records('capture-full')), stderr='')
        if command[1] == '--allocation-case':
            return SimpleNamespace(returncode=0, stdout=json.dumps(allocation_row(command[2])), stderr='')
        assert command[1] == '--bench'
        assert len([c for c in calls if c[1] == '--capture-full']) == 3
        golden, actual = Path(command[3]), Path(command[4]); assert not actual.exists()
        actual.write_bytes(golden.read_bytes() + (b'BAD' if mismatch_selected else b''))
        rows = json_records('bench', command[2])
        if invalid_selected: rows[0]['selected_validated'] = False
        return SimpleNamespace(returncode=0, stdout=encode(rows), stderr='')
    monkeypatch.setattr(m.subprocess, 'run', fake_run)
    args = SimpleNamespace(output=output)
    return args, calls, affinities


def test_capture_mismatch_stops_before_any_timer_and_restores_affinity(monkeypatch, tmp_path, small):
    args, calls, affinities = orchestration(monkeypatch, tmp_path, small, mismatch_full=True)
    with pytest.raises(ValueError, match='raw bits'): m.measure(args)
    assert len(calls) == 3 and all(c[1] == '--capture-full' for c in calls)
    assert affinities == [{3}, {3, 4}] and not (args.output / 'summary.json').exists()
    assert len(json.loads((args.output / 'execution-order.json').read_text())) == 3


@pytest.mark.parametrize('mismatch_selected,invalid_selected', [(True, False), (False, True)])
def test_invalid_selected_child_is_retained_and_aborts(monkeypatch, tmp_path, small, mismatch_selected, invalid_selected):
    args, calls, affinities = orchestration(monkeypatch, tmp_path, small, mismatch_selected=mismatch_selected, invalid_selected=invalid_selected)
    with pytest.raises(ValueError): m.measure(args)
    assert len(calls) == 7 and Path(calls[-1][4]).exists()
    assert affinities[-1] == {3, 4} and not (args.output / 'summary.json').exists()
    ledger = json.loads((args.output / 'execution-order.json').read_text())
    assert ledger[-1]['phase'] == 'bench' and ledger[-1]['case'] == small


def test_every_selected_case_is_a_fresh_balanced_child_and_only_duplicates_deleted(monkeypatch, tmp_path, small):
    args, calls, affinities = orchestration(monkeypatch, tmp_path, small)
    m.measure(args)
    benches = [c for c in calls if c[1] == '--bench']
    assert len(benches) == 36
    assert all(len(c) == 5 and c[2] == small for c in benches)
    assert len({c[4] for c in benches}) == 36 and all(not Path(c[4]).exists() for c in benches)
    ledger = json.loads((args.output / 'execution-order.json').read_text())
    assert all(r['selected_validated_before_clock'] and r['identical_capture_deleted'] for r in ledger if r['phase'] == 'bench')
    assert all(Path(r['stdout']).exists() for r in ledger)
    summary = json.loads((args.output / 'summary.json').read_text())
    assert summary['protocol']['timed_children'] == 36 and summary['protocol']['fresh_process_per_case']
    assert affinities == [{3}, {3, 4}]


def test_negative_child_stdout_stderr_and_command_are_preserved(monkeypatch, tmp_path):
    monkeypatch.setattr(m.subprocess, 'run', lambda *args, **kwargs: SimpleNamespace(returncode=101, stdout='before panic', stderr='bad golden'))
    ledger = []; out = tmp_path / 'out'; err = tmp_path / 'err'
    with pytest.raises(subprocess.CalledProcessError): m.child_run(['bin', '--bench'], out, err, {}, ledger)
    assert out.read_text() == 'before panic' and err.read_text() == 'bad golden'
    assert ledger[0]['returncode'] == 101


def test_noise_ranges_negative_results_and_controls_are_not_filtered(monkeypatch):
    control = 'sma_control/default/512'; changed = 'supertrend/default/100'
    monkeypatch.setattr(m, 'TIMED_CASES', {control, changed})
    runs = {s: {} for s in m.SIDES}
    for side in m.SIDES:
        runs[side][control] = [{'samples_ns': [100.] * 31} for _ in range(12)]
        base = [80.] * 6 + [120.] * 6
        scale = {'before': 1., 'common': 1., 'paired': 1.02}[side]
        runs[side][changed] = [{'samples_ns': [v * scale] * 31} for v in base]
    summary = m.summarize(runs)
    assert summary['cases'][control]['is_control']
    pair = summary['cases'][changed]['comparisons']['common_vs_paired']
    assert pair['median_ratio'] < 1 and pair['new_slower_pairs'] == 12
    assert pair['ratio_envelope'][0] < 1 < pair['ratio_envelope'][1] and not pair['ranges_disjoint']
    assert len(summary['cases'][changed]['raw_samples_ns']['paired']) == 12
    runs['paired'][control].pop()
    with pytest.raises(ValueError): m.summarize(runs)


def test_fixed_source_inventory_and_control_hashes_fail_closed():
    names = m.BASE_COMMON_FILES | m.POLICY_FILES | {f'ta_codegen/output/rust/library/src/ta_func/{f}.rs' for f in ('macd', 'macdfix', 'ema', 'sma')}
    before = {p: 'same' for p in names if p != 'ta_codegen/output/rust/library/tests/supertrend_output_windows.rs'}
    common = {p: ('common' if p in m.BASE_COMMON_FILES else value) for p, value in before.items()}
    paired = dict(common)
    for p in m.POLICY_FILES: paired[p] = 'paired'
    records = {s: {'source_files': files} for s, files in zip(m.SIDES, (before, common, paired))}
    assert m.verify_inventory(records)['controls_byte_identical'] == ['macd', 'macdfix', 'ema', 'sma']
    changed = copy.deepcopy(records); changed['paired']['source_files']['ta_codegen/output/rust/library/src/ta_func/macd.rs'] = 'bad'
    with pytest.raises(ValueError): m.verify_inventory(changed)
    changed = copy.deepcopy(records); changed['common']['source_files']['unrelated'] = 'bad'
    with pytest.raises(ValueError): m.verify_inventory(changed)


def test_workflow_pins_gates_order_affinity_and_failure_artifacts():
    text = (Path(__file__).parents[1] / '.github/workflows/paired-windows.yml').read_text()
    for pin in m.PINS.values(): assert text.count(pin) == 1
    assert text.count('repository: Yvictor/ta-lib-native') == 3
    assert 'timeout-minutes: 90' in text and '--noconftest' in text
    assert text.index('All three source arms') < text.index('Build all three portable') < text.index('Exact full captures first')
    for check in ('cargo test --locked --manifest-path ta_codegen/generator/Cargo.toml',
                  'cargo test --locked -p ta-lib', 'cargo clippy --locked --all-targets',
                  'servers --language=c,rust', '(cd bin &&', './ta_regtest --codegen --language=c,rust', 'regen-check'):
        assert check in text
    assert 'if: always()' in text and '!paired-windows-results/target-before/**' in text
    assert '--rounds' not in text and '--repeats' not in text
    assert 'Publish' not in text and 'contents: read' in text


def test_git_record_covers_generated_nonrust_common_store_sources(monkeypatch, tmp_path):
    required = {'ta_codegen/output/rust/Cargo.toml', 'ta_codegen/output/rust/library/Cargo.toml',
                'ta_codegen/generator/src/backends/rust_window.rs', 'ta_codegen/input/supertrend/supertrend.c'}
    names = required | m.BASE_COMMON_FILES | {'ta_codegen/output/csharp/library/src/Other.cs', 'ta_codegen/output/java/tools/Other.java'}
    for name in names:
        p = tmp_path / name; p.parent.mkdir(parents=True, exist_ok=True); p.write_text(name)
    def output(command, **kwargs):
        if command[-2:] == ['rev-parse', 'HEAD']: return m.PINS['before'] + '\n'
        if command[-2:] == ['status', '--porcelain']: return b''
        assert command[-2:] == ['ls-files', '-z']; return '\0'.join(sorted(names)) + '\0'
    monkeypatch.setattr(m.subprocess, 'check_output', output)
    record = m.git_record(tmp_path, m.PINS['before'])
    assert m.BASE_COMMON_FILES <= record['source_files'].keys()
    assert record['source_files']['ta_codegen/output/java/tools/Other.java'] == m.sha256(tmp_path / 'ta_codegen/output/java/tools/Other.java')
    with pytest.raises(ValueError, match='immutable'): m.git_record(tmp_path, 'wrong')


def test_raw_signed_zero_is_not_normalized_away(small, tmp_path):
    paths = {s: tmp_path / (s + '.bin') for s in m.SIDES}
    for side, path in paths.items():
        path.write_bytes(m.MAGIC + b''.join(raw_record(n, -0. if side == 'paired' else 0.) for n in sorted(m.SPECS)))
    for path in paths.values(): m.read_capture(path)
    with pytest.raises(ValueError, match='raw bits'): m.validate_capture_pair(paths)


def test_raw_rejects_forged_status_range_and_missing_fields(small, tmp_path):
    record = bytearray(raw_record(small)); path = tmp_path / 'raw.bin'
    name_end = 8 + 4 + len(small.encode())
    status_length = struct.unpack_from('<I', record, name_end)[0]
    n_offset = name_end + 4 + status_length
    struct.pack_into('<Q', record, n_offset + 3 * 8, 9)  # forged beg=9 instead of10
    path.write_bytes(m.MAGIC + record)
    with pytest.raises(ValueError, match='shape/status/range'): m.read_capture(path, {small})
    valid = raw_record(small); path.write_bytes(m.MAGIC + valid[:-8])
    with pytest.raises(ValueError, match='truncated'): m.read_capture(path, {small})


def test_separate_allocation_audit_preserves_differences_and_caveats(monkeypatch, tmp_path, small):
    args, calls, _ = orchestration(monkeypatch, tmp_path, small)
    m.measure(args)
    allocations = [c for c in calls if c[1] == '--allocation-case']
    assert len(allocations) == 3 and all(c[0].endswith('-allocation') for c in allocations)
    assert all(len(c) == 3 for c in allocations)
    audit = json.loads((args.output / 'allocation-audit.json').read_text())
    assert not audit['primary_instrumented'] and audit['children'] == 3
    assert 'do not prove' in audit['caveat'] and 'not live bytes' in audit['caveat']
    assert set(audit['cases'][small]) == set(m.SIDES)


@pytest.mark.parametrize('field,value', [('alloc_requests', True), ('alloc_requested_bytes', -1),
    ('realloc_requests', 0.5), ('dealloc_requests', -1), ('alloc_requested_bytes', 1),
    ('status', 'BadParam'), ('count', 1), ('close_fnv1a64', '0' * 16), ('os', 'macos')])
def test_allocation_schema_and_scope_fail_closed(small, field, value):
    row = allocation_row(small); row[field] = value
    with pytest.raises(ValueError): m.parse_allocation(json.dumps(row), small, FNV)


def test_allocation_primary_footprint_is_not_claimed_from_equal_diagnostics(small):
    row = allocation_row(small); row['alloc_requests'] = 2; row['alloc_requested_bytes'] = 64
    parsed = m.parse_allocation(json.dumps(row), small, FNV)
    assert parsed['alloc_requested_bytes'] == 64
    assert 'optimizer allocation elision' in m.ALLOCATION_CAVEAT
    assert 'support' in m.ALLOCATION_CAVEAT and 'do not prove' in m.ALLOCATION_CAVEAT


def test_input_hash_cannot_mutate_between_selected_children(tmp_path, monkeypatch):
    path = tmp_path / 'input.bin'; path.write_bytes(b'x' * 8000000)
    record = {'path': str(path), 'sha256': m.sha256(path)}
    assert m.verify_input(record) == record['sha256']
    with path.open('r+b') as f: f.seek(123); f.write(b'y')
    with pytest.raises(ValueError, match='input changed'): m.verify_input(record)


def test_build_archives_exact_linked_libraries_and_serializes_counter_tests(monkeypatch, tmp_path):
    out = tmp_path / 'results'; out.mkdir()
    harness = tmp_path / 'harness.rs'; harness.write_text('fn main() {}')
    roots = {s: tmp_path / s for s in m.SIDES}
    for root in roots.values(): root.mkdir()
    args = SimpleNamespace(output=out, harness=harness, **{s + '_source': r for s, r in roots.items()})
    monkeypatch.setattr(m, 'runtime_record', lambda: {})
    monkeypatch.setattr(m, 'git_record', lambda root, expected: {'commit': expected, 'source_files': {}, 'clean': True})
    monkeypatch.setattr(m, 'verify_inventory', lambda sources: {'controls_byte_identical': list(m.CONTROLS)})
    monkeypatch.setattr(m, 'input_file', lambda output: {'path': str(output / 'input.bin'), 'sha256': 'fake'})
    commands = []
    def output(command, **kwargs):
        root = next(r for r in roots.values() if str(r / 'ta_codegen/output/rust/Cargo.toml') == command[-1])
        return json.dumps({'packages': [{'name': 'ta-lib', 'version': '0.8.4', 'source': None,
                                        'manifest_path': str(root / 'ta_codegen/output/rust/library/Cargo.toml')}]})
    monkeypatch.setattr(m.subprocess, 'check_output', output)
    def fake_logged(command, log, cwd=None, env=None):
        command = list(map(str, command)); commands.append(command)
        if command[0] == 'cargo':
            target = Path(command[command.index('--target-dir') + 1]); (target / 'release/deps').mkdir(parents=True)
            (target / 'release/libta_lib.rlib').write_bytes(('library-' + str(cwd)).encode())
        elif command[0] == 'rustc':
            Path(command[command.index('-o') + 1]).write_bytes(('binary-' + ' '.join(command)).encode())
    monkeypatch.setattr(m, 'run_logged', fake_logged)
    m.build(args)
    provenance = json.loads((out / 'build-provenance.json').read_text())
    assert (out / 'input-manifest.json').exists()
    for side in m.SIDES:
        row = provenance[side]
        assert Path(row['library']).parent == out / 'libraries'
        assert Path(row['library']).read_bytes() == Path(row['linked_library']).read_bytes()
        assert row['library_sha256'] == row['linked_library_sha256']
        assert not row['primary_allocation_instrumentation']
        assert '--cfg' not in row['commands'][1]
        assert row['diagnostic_command'][-4:-2] == ['--cfg', 'paired_alloc_probe']
        assert '-Dwarnings' in row['commands'][1]
    test_command = provenance['allocation_cli_tests']['commands'][-1]
    assert test_command[-1] == '--test-threads=1'
    assert any(c[-1] == '--test-threads=1' for c in commands)
    assert len([c for c in commands if c[0] == 'rustc' and '--test' not in c]) == 6
