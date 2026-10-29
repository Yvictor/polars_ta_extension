"""Fresh-case measurement must not silently run or allocate sibling workloads."""
import copy
import importlib
from pathlib import Path

import pytest


@pytest.fixture
def modules(monkeypatch):
    monkeypatch.syspath_prepend(str(Path(__file__).parents[1] / 'scripts'))
    return importlib.import_module('adapter_ci_benchmark'), importlib.import_module('migration_benchmark')


def report():
    return {'case_inventory': ['ema/1000'], 'case_filters': ['ema/1000'],
            'checked_values': 1000, 'results': {'ema/1000': {}}}


def test_selected_child_requires_exactly_one_requested_validated_case(modules):
    controller, _ = modules
    controller.selected_inventory(report(), ['ema/1000'])
    for key, value in [('case_inventory', ['ema/1000', 'atr/1000']),
                       ('case_filters', []), ('checked_values', 0),
                       ('results', {'atr/1000': {}})]:
        child = copy.deepcopy(report())
        child[key] = value
        with pytest.raises(ValueError):
            controller.selected_inventory(child, ['ema/1000'])
    with pytest.raises(ValueError):
        controller.selected_inventory(report(), [])


def test_workload_inventory_keeps_all_families_and_thread_diagnostics(modules):
    _, benchmark = modules
    standard = [row[0] for row in benchmark.case_specs(False)]
    diagnostic = [row[0] for row in benchmark.case_specs(True)]
    assert len(standard) == len(set(standard)) == 132
    assert len(diagnostic) == len(set(diagnostic)) == 141
    assert set(standard) < set(diagnostic)
    controller, _ = modules
    assert controller.requested_inventory(False, []) == standard
    assert controller.requested_inventory(True, []) == diagnostic
    for family in ('var', 'correl', 'cmou'):
        assert f'{family}/1000000' in standard
        assert f'grouped_{family}/2000x100_interleaved' in standard


def test_selected_case_does_not_construct_other_frames(modules, monkeypatch):
    _, benchmark = modules
    original = benchmark.frame
    constructed = []
    def frame(rows, bars):
        constructed.append((rows, bars))
        assert rows == 1000
        return original(rows, bars)
    monkeypatch.setattr(benchmark, 'frame', frame)
    selected = list(benchmark.cases(True, ['correl/1000']))
    assert [row[0] for row in selected] == ['correl/1000']
    assert constructed == [(1000, 1000)]
    assert selected[0][1].select(selected[0][2]).height == 1000


@pytest.mark.parametrize('omit', [False, True])
def test_controller_uses_fresh_single_case_children_and_keeps_goldens(modules, monkeypatch, tmp_path, omit):
    import argparse
    import json
    controller, _ = modules
    args = argparse.Namespace(output=tmp_path, case_filter=['ema/*'], rounds=6, repeats=5)
    for side in controller.SIDES:
        setattr(args, side+'_python', tmp_path/side/'bin/python')
        setattr(args, side+'_source', tmp_path/side/'source')
    inv = ['ema/1000'] if omit else ['ema/1000', 'ema/1000000']
    timed_commands = []
    def fake_child(command, **kwargs):
        side = next(side for side in controller.SIDES if str(getattr(args, side+'_python')) == command[0])
        selected = command[command.index('--case-filter')+1]
        timed = '--check-only' not in command
        inventory = [selected] if timed else inv
        if timed:
            assert command.count('--case-filter') == 1
            assert selected in inv
            timed_commands.append((side, selected, command))
        if '--write-reference' in command:
            Path(command[command.index('--write-reference')+1]).write_bytes(b'preserved golden')
        entry = {'samples_ms': [1.0]*5, 'median_ms': 1.0,
                 'minor_faults': [0]*5, 'major_faults': [0]*5}
        data = dict(commit={'original':controller.ORIGINAL_COMMIT, 'prior':controller.PRIOR_COMMIT, 'candidate':'candidate'}[side], source_sha256=side, native_binary_sha256=side,
                    python='fixture', platform='fixture', cpu='fixture',
                    polars='fixture', numpy='fixture', rust='fixture', profile='fixture',
                    threads=1, affinity=None, repeats=5, warmups=5, diagnostic=True,
                    checked_values=1000 if timed else (0 if side=='original' else 1001000),
                    case_filters=[selected], case_inventory=inventory,
                    exact_reference='--exact-reference' in command,
                    talib='0.8.1 test fixture' if side=='original' else '0.8.3 (native Rust; polars-talib compatibility)',
                    results={selected: entry} if timed else {})
        Path(command[command.index('--output')+1]).write_text(json.dumps(data))
    monkeypatch.setattr(controller.subprocess, 'run', fake_child)
    if omit:
        with pytest.raises(ValueError, match='omitted or changed'):
            controller.run_setting(args, 1, None, prepare_only=True)
        assert timed_commands == []
        return
    prepared = controller.run_setting(args, 1, None, prepare_only=True)
    assert timed_commands == []
    report, _ = controller.run_setting(args, 1, None)
    assert len(timed_commands) == 2*3*6
    assert report['process_isolation'] == 'one case per fresh process'
    assert report['case_inventory'] == inv
    assert len(report['processes']) == 36
    assert set(report['comparisons']['original_vs_candidate']) == set(inv)
    assert (tmp_path/'threads-1/reference.npz').read_bytes() == b'preserved golden'
    assert (tmp_path/'threads-1/prior-reference.npz').is_file()


def test_all_thread_references_precede_any_timing(modules, monkeypatch):
    import argparse
    controller, _ = modules
    calls = []
    def run(args, threads, affinity, *, prepare_only=False):
        calls.append((threads, prepare_only))
        return {} if prepare_only else ({'threads': threads}, [])
    monkeypatch.setattr(controller, 'run_setting', run)
    reports, _ = controller.run_all_settings(argparse.Namespace(thread_counts=[1,4]), None)
    assert calls == [(1, True), (4, True), (1, False), (4, False)]
    assert set(reports) == {'1', '4'}
