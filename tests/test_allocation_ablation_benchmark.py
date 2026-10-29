"""Reject incomparable ablations before they can become performance evidence."""
from collections import Counter
import copy
import importlib.util
import json
from pathlib import Path
import zipfile

import pytest

spec = importlib.util.spec_from_file_location('ablation', Path(__file__).parents[1] / 'scripts/allocation_ablation_benchmark.py')
ablation = importlib.util.module_from_spec(spec); spec.loader.exec_module(ablation)


def identities():
    return {side: {'python': '3.12.15', 'platform': 'Linux', 'polars': '1.44.2', 'numpy': '2.5.3',
                   'package': '0.2.1', 'talib': '0.8.3 (native Rust; polars-talib compatibility)'}
            for side in ablation.SIDES}


def provenance():
    return {'flags': {'rustc': 'rustc 1.90.0 (test)\nbinary: rustc\n'},
            'builds': {side: {'source': {'commit': str(i + 1) * 40, 'source_sha256': side},
                              'identity': identities()[side]}
                       for i, side in enumerate(ablation.SIDES)}}


def run(side='base'):
    build = provenance()['builds'][side]
    return {'commit': build['source']['commit'], 'source_sha256': side, **build['identity'],
            'rust': 'rustc 1.90.0 (test)', 'threads': 1, 'affinity': [2], 'repeats': 31,
            'warmups': 5, 'diagnostic': False, 'case_filters': list(ablation.CASES),
            'checked_values': ablation.CHECKED_VALUES, 'exact_reference': True,
            'results': {name: {'samples_ms': [1.] * 31, 'median_ms': 1., 'minor_faults': [0] * 31,
                               'major_faults': [0] * 31} for name in ablation.CASES}}


def test_williams_orders_balance_position_and_within_round_carryover():
    assert len(ablation.ORDERS) == 8
    for position in range(4):
        assert Counter(order[position] for order in ablation.ORDERS) == {side: 2 for side in ablation.SIDES}
    transitions = Counter((a, b) for order in ablation.ORDERS for a, b in zip(order, order[1:]))
    assert set(transitions.values()) == {2}
    assert set(transitions) == {(a, b) for a in ablation.SIDES for b in ablation.SIDES if a != b}


def test_requested_cases_keep_real_over_queries_and_unchanged_engine_controls():
    assert len(ablation.CASES) == len(set(ablation.CASES)) == 26
    for family in ('ema', 'atr', 'macd', 'bbands', 'sarext', 'add'):
        for layout in ('10000x100', '2000x100_interleaved', '100x10000'):
            assert f'grouped_{family}/{layout}' in ablation.CASES
    assert 'grouped_minmaxindex/10000x100' in ablation.CASES
    assert 'macd/1000000' in ablation.CASES
    assert sum(name.startswith('control_') for name in ablation.CASES) == 4
    assert not any('list' in name or 'by_group' in name for name in ablation.CASES)


@pytest.mark.parametrize('change', ['missing_build', 'wrong_runtime', 'original_c'])
def test_installed_runtime_gate_rejects_missing_or_mixed_builds(change):
    data = identities()
    if change == 'missing_build': del data['combined']
    elif change == 'wrong_runtime': data['map']['polars'] = '2.0.0'
    else: data['fields']['talib'] = '0.8.1 (C)'
    with pytest.raises(ValueError): ablation.validate_identities(data)


def test_source_pin_rejects_moving_refs_and_different_commit(tmp_path, monkeypatch):
    with pytest.raises(ValueError, match='immutable SHA'):
        ablation.source_record(tmp_path, 'main')
    monkeypatch.setattr(ablation.subprocess, 'check_output', lambda *args, **kwargs: 'a' * 40 + '\n')
    with pytest.raises(ValueError, match='source pin mismatch'):
        ablation.source_record(tmp_path, 'b' * 40)


@pytest.mark.parametrize('change', ['pin', 'case', 'runtime', 'thread', 'affinity', 'rust', 'sample_count', 'nan', 'boolean', 'negative_fault', 'no_exact_check'])
def test_raw_run_gate_rejects_incomparable_or_invalid_processes(change):
    row = run(); name = ablation.CASES[0]
    if change == 'pin': row['commit'] = 'f' * 40
    elif change == 'case': row['results'].pop(name)
    elif change == 'runtime': row['numpy'] = '2.5.4'
    elif change == 'thread': row['threads'] = 4
    elif change == 'affinity': row['affinity'] = [0, 1]
    elif change == 'rust': row['rust'] = 'rustc 1.97.0'
    elif change == 'sample_count': row['results'][name]['samples_ms'].pop()
    elif change == 'nan': row['results'][name]['samples_ms'][0] = float('nan')
    elif change == 'boolean': row['results'][name]['samples_ms'][0] = True
    elif change == 'negative_fault': row['results'][name]['minor_faults'][0] = -1
    else: row['exact_reference'] = False
    with pytest.raises(ValueError): ablation.validate_run(row, 'base', 1, 31, provenance(), True)


def test_valid_process_and_overlapping_process_ranges_remain_descriptive():
    row = run(); ablation.validate_run(row, 'base', 1, 31, provenance(), True)
    before = []; after = []
    for i in range(8):
        old = 1. if i < 4 else 4.
        for dest, value in ((before, old), (after, old * .9)):
            process = copy.deepcopy(row)
            process['results'][ablation.CASES[0]]['samples_ms'] = [value] * 31
            dest.append(process)
    summary = ablation.pair_summary(before, after, ablation.CASES[0])
    assert summary['median_paired_ratio'] == pytest.approx(1 / .9)
    assert summary['ratio_envelope'][0] < 1 < summary['ratio_envelope'][1]
    assert len(summary['paired_ratios']) == summary['after_faster_rounds'] == 8


def test_installed_native_hash_must_match_preserved_wheel(tmp_path):
    wheel = tmp_path / 'native.whl'
    with zipfile.ZipFile(wheel, 'w') as archive:
        archive.writestr('polars_talib/_polars_talib.abi3.so', b'wheel-native')
    installed = {'native_files': {'/env/polars_talib/_polars_talib.abi3.so': 'incorrect'}}
    with pytest.raises(ValueError, match='installed native module'):
        ablation.wheel_record(tmp_path, installed)


def test_exact_full_api_gate_rejects_underchecked_or_changed_captures(tmp_path):
    base = tmp_path / 'base.npz'; base.write_bytes(b'full-base-capture')
    for side in ablation.SIDES[1:]:
        candidate = tmp_path / (side + '.npz'); candidate.write_bytes(base.read_bytes())
        report = {'require_exact': True, 'cases': 10624, 'checked_values': 2167654,
                  'failures': [], 'api_call_contract_match': True, 'fields_with_bit_differences': 0,
                  'max_absolute_difference': 0, 'baseline': str(base), 'candidate': str(candidate),
                  'baseline_sha256': ablation.sha256(base), 'candidate_sha256': ablation.sha256(candidate)}
        (tmp_path / ('base-vs-' + side + '-exact.json')).write_text(json.dumps(report))
    assert set(ablation.corpus_gate(tmp_path)) == set(ablation.SIDES[1:])
    report_path = tmp_path / 'base-vs-map-exact.json'; report = json.loads(report_path.read_text())
    report['checked_values'] -= 1; report_path.write_text(json.dumps(report))
    with pytest.raises(ValueError, match='complete exact API corpus'):
        ablation.corpus_gate(tmp_path)
    report['checked_values'] += 1; report_path.write_text(json.dumps(report))
    (tmp_path / 'map.npz').write_bytes(b'changed')
    with pytest.raises(ValueError, match='corpus data changed'):
        ablation.corpus_gate(tmp_path)
