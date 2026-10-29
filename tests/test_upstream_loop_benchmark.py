"""The upstream timing campaign must never bypass its exact-output gate."""
import importlib.util
import json
from pathlib import Path
from types import SimpleNamespace

import pytest

spec = importlib.util.spec_from_file_location('upstream_loop_benchmark', Path(__file__).parents[1] / 'scripts/upstream_loop_benchmark.py')
benchmark = importlib.util.module_from_spec(spec)
spec.loader.exec_module(benchmark)


def records(capture_only=False):
    entries = [{'kind': 'metadata', 'arch': 'x86_64', 'os': 'linux', 'repeats': 31, 'capture_only': capture_only},
               {'kind': 'parity', 'cases': 8512, 'written_values': 2278720}]
    if not capture_only:
        entries += [{'case': name, 'iterations': max(2_000_000 // int(name.rsplit('/', 1)[1]), 3),
                     'samples_ns': [10.] * 31} for name in sorted(benchmark.EXPECTED_CASES)]
    return entries


def encode(entries):
    return '\n'.join(json.dumps(entry) for entry in entries)


def test_parser_separates_metadata_parity_and_exact_23_case_inventory():
    result = benchmark.parse_records(encode(records()), 31, False)
    assert result['metadata']['arch'] == 'x86_64'
    assert result['parity']['written_values'] == 2278720
    assert len(result['cases']) == 23
    assert 'MACD/20' not in result['cases']
    assert 'MACDFIX/1000000' in result['cases']
    assert set(benchmark.parse_records(encode(records(True)), 31, True)['cases']) == set()


@pytest.mark.parametrize('mutation', ['missing_parity', 'duplicate_metadata', 'underchecked', 'missing_case', 'duplicate_case', 'wrong_repeats', 'nonfinite_sample', 'zero_sample'])
def test_parser_rejects_incomplete_or_invalid_campaign(mutation):
    data = records()
    if mutation == 'missing_parity': data.pop(1)
    elif mutation == 'duplicate_metadata': data.append(data[0])
    elif mutation == 'underchecked': data[1]['written_values'] -= 1
    elif mutation == 'missing_case': data.pop()
    elif mutation == 'duplicate_case': data.append(data[-1])
    elif mutation == 'wrong_repeats': data[0]['repeats'] = 5
    elif mutation == 'nonfinite_sample': data[-1]['samples_ns'][0] = float('nan')
    elif mutation == 'zero_sample': data[-1]['samples_ns'][0] = 0
    with pytest.raises(ValueError):
        benchmark.parse_records(encode(data), 31, False)


def test_capture_gate_requires_positive_byte_identical_content(tmp_path):
    paths = {side: tmp_path / side for side in benchmark.SIDES}
    for path in paths.values(): path.write_bytes(b'')
    with pytest.raises(ValueError): benchmark.validate_capture_pair(paths)
    paths['baseline'].write_bytes(b'\x00\x80\x7f')
    paths['candidate'].write_bytes(b'\x00\x00\x7f')
    with pytest.raises(ValueError): benchmark.validate_capture_pair(paths)
    paths['candidate'].write_bytes(paths['baseline'].read_bytes())
    gate = benchmark.validate_capture_pair(paths)
    assert gate['bytes'] == {'baseline': 3, 'candidate': 3}
    assert gate['sha256']['baseline'] == gate['sha256']['candidate']


def test_capture_mismatch_stops_before_timing_and_restores_affinity(tmp_path, monkeypatch):
    harness = tmp_path / 'harness.rs'; harness.write_text('harness')
    binaries = {side: tmp_path / side for side in benchmark.SIDES}
    for path in binaries.values(): path.write_bytes(b'binary')
    provenance = {'runtime': {}, 'harness': {'sha256': benchmark.sha256(harness)},
                  **{side: {'binary_sha256': benchmark.sha256(path)} for side, path in binaries.items()}}
    (tmp_path / 'build-provenance.json').write_text(json.dumps(provenance))
    args = SimpleNamespace(output=tmp_path, harness=harness, repeats=31, pairs=12, **binaries)
    monkeypatch.setattr(benchmark, 'verify_sources', lambda *args: None)
    monkeypatch.setattr(benchmark, 'runtime_record', lambda: {})
    affinity_changes = []
    monkeypatch.setattr(benchmark.os, 'sched_getaffinity', lambda pid: {3, 4}, raising=False)
    monkeypatch.setattr(benchmark.os, 'sched_setaffinity', lambda pid, cpus: affinity_changes.append(set(cpus)), raising=False)
    calls = []
    def fake_run(command, **kwargs):
        calls.append(command)
        assert command[-1] == '--capture-only', 'a timed process must not run before the capture gate'
        Path(command[2]).write_bytes(command[0].encode())
        return SimpleNamespace(stdout=encode(records(True)))
    monkeypatch.setattr(benchmark.subprocess, 'run', fake_run)
    with pytest.raises(ValueError, match='capture differs'):
        benchmark.measure(args)
    assert len(calls) == 2
    assert affinity_changes == [{3}, {3, 4}]
    assert not (tmp_path / 'summary.json').exists()


def test_summaries_keep_process_spread_and_identify_controls():
    runs = {side: [] for side in benchmark.SIDES}
    for index in range(12):
        old = 10. if index < 6 else 30.
        for side, median in [('baseline', old), ('candidate', old * .9)]:
            entries = benchmark.parse_records(encode(records()), 31, False)
            for name, entry in entries['cases'].items():
                entry['samples_ns'] = [7. if '_control/' in name else median] * 31
            runs[side].append(entries)
    rows = benchmark.summarize(runs)
    assert rows['EMA/1000000']['median_paired_ratio'] == pytest.approx(1 / .9)
    assert rows['EMA/1000000']['ratio_envelope'][0] < 1 < rows['EMA/1000000']['ratio_envelope'][1]
    assert len(rows['EMA/1000000']['paired_ratios']) == 12
    assert rows['SMA_control/1000000']['is_control']
    assert rows['SMA_control/1000000']['median_paired_ratio'] == 1
