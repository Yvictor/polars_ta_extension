"""Guard experiment balance, counter validity and exact initialization checks."""
from collections import Counter
import importlib.util
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).parents[1]


@pytest.fixture
def allocation(monkeypatch):
    monkeypatch.syspath_prepend(str(ROOT/'scripts'))
    spec = importlib.util.spec_from_file_location('allocation_benchmark', ROOT/'scripts/allocation_ci_benchmark.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_three_build_orders_balance_position_and_all_permutations(allocation):
    assert len(set(allocation.ORDERS)) == 6
    for index in range(3):
        assert Counter(order[index] for order in allocation.ORDERS) == {side: 2 for side in allocation.SIDES}


def test_fault_report_exposes_process_spread_and_rejects_missing_samples(allocation):
    data = [{'repeats': 3, 'results': {'atr': {'minor_faults': samples}}}
            for samples in ([0, 2, 4], [10, 12, 14], [20, 22, 24])]
    report = allocation.fault_summary(data, 'atr', 'minor_faults')
    assert report['process_medians'] == [2, 12, 22]
    assert report['median'] == 12
    assert report['p10_p90'][0] < 2 < 22 < report['p10_p90'][1]
    data[-1]['results']['atr']['minor_faults'] = []
    with pytest.raises(ValueError):
        allocation.fault_summary(data, 'atr', 'minor_faults')


def capture(path, values):
    import json
    metadata = {'api': {}, 'cases': {'one': {'schema': 'Float64', 'height': len(values), 'fields': ['c0']}}}
    np.savez(path, metadata=np.array(json.dumps(metadata)), c0=np.array(values, dtype=np.float64), c0_null=np.zeros(len(values), dtype=bool))


@pytest.mark.parametrize('changed', [[1.+1e-12, 0., float('nan')], [1., -0., float('nan')]], ids=['tiny-change','signed-zero'])
def test_exact_corpus_mode_catches_tiny_changes_and_signed_zero(tmp_path, changed):
    spec = importlib.util.spec_from_file_location('allocation_probe', ROOT/'scripts/migration_probe.py')
    probe = importlib.util.module_from_spec(spec); spec.loader.exec_module(probe)
    before = tmp_path/'before.npz'; after = tmp_path/'after.npz'; report = tmp_path/'report.json'
    capture(before, [1., 0., float('nan')]); capture(after, changed)
    assert not probe.compare(before, after, report)
    assert probe.compare(before, after, report, require_exact=True)
    import json
    assert json.loads(report.read_text())['fields_with_bit_differences'] == 1
    capture(after, [1., 0., float('nan')])
    assert not probe.compare(before, after, report, require_exact=True)


def test_requested_workload_inventory_has_no_custom_dispatch():
    spec = importlib.util.spec_from_file_location('allocation_workloads', ROOT/'scripts/migration_benchmark.py')
    workloads = importlib.util.module_from_spec(spec); spec.loader.exec_module(workloads)
    standard = {name for name, _, _ in workloads.cases()}
    diagnostic = {name for name, _, _ in workloads.cases(diagnostic=True)}
    assert {'grouped_atr/100x10000', 'grouped_ema/100x10000', 'grouped_atr/10000x100',
            'grouped_ema/10000x100', 'grouped_atr/2000x100_interleaved', 'ema/1000000',
            'control_cumsum/100x10000', 'control_cumsum/10000x100'} <= standard
    assert {'grouped_atr/50000x20', 'grouped_ema/1x1000000', 'control_cumsum/10x100000'} <= diagnostic
    assert standard < diagnostic
    assert not any('dispatcher' in name or 'by_group' in name for name in diagnostic)
