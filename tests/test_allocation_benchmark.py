"""Guard experiment balance, counter validity and exact initialization checks."""
from collections import Counter
import importlib.util
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).parents[1]


@pytest.fixture(params=["allocation_ci_benchmark", "adapter_ci_benchmark"])
def allocation(monkeypatch, request):
    monkeypatch.syspath_prepend(str(ROOT/'scripts'))
    spec = importlib.util.spec_from_file_location('allocation_benchmark', ROOT/'scripts'/(request.param+'.py'))
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
    # Tiny finite rounding is tolerated; opposite signed zeros are not.
    assert probe.compare(before, after, report) == bool(np.signbit(changed[1]))
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
            'control_cumsum/100x10000', 'control_cumsum/10000x100',
            *{f'grouped_{name}/10000x100' for name in ('rsi','macd','adx','cci','stddev','ppo','add','minmaxindex','cdldoji','hma','supertrend','vwma','mavp')}} <= standard
    assert {'grouped_atr/50000x20', 'grouped_ema/1x1000000', 'control_cumsum/10x100000'} <= diagnostic
    assert standard < diagnostic
    assert not any('dispatcher' in name or 'by_group' in name for name in diagnostic)


def test_api_annotation_changes_are_reported_but_call_contract_changes_fail(tmp_path):
    import json
    spec = importlib.util.spec_from_file_location('api_probe', ROOT/'scripts/migration_probe.py')
    probe = importlib.util.module_from_spec(spec); spec.loader.exec_module(probe)
    before, after, report = (tmp_path/n for n in ('before.npz','after.npz','report.json'))
    def save(path, annotation, contract):
        meta = {'api': {'aroon': annotation}, 'api_call_contract': {'aroon': contract}, 'cases': {}}
        np.savez(path, metadata=np.array(json.dumps(meta)))
    save(before, 'Expr', '(high, low, timeperiod: int = 14)')
    save(after, 'IntoExpr', '(high, low, timeperiod: int = 14)')
    assert not probe.compare(before, after, report)
    result = json.loads(report.read_text())
    assert not result['api_signatures_match']
    assert result['api_call_contract_match']
    assert result['annotation_changed_functions'] == ['aroon']
    save(after, 'IntoExpr', '(low, high, timeperiod: int = 14)')
    assert probe.compare(before, after, report)


def test_regression_inventory_keeps_noisy_and_consistent_slower_cases():
    spec = importlib.util.spec_from_file_location('regressions', ROOT/'scripts/regression_inventory.py')
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    def row(old, new, envelope):
        return {'baseline_median_ms':old,'candidate_median_ms':new,'ratio_envelope':envelope,
                'median_paired_ratio':old/new,'baseline_process_medians_ms':[old]*6,
                'candidate_process_medians_ms':[new]*6}
    data = {'comparisons':{'original_vs_candidate':{
        'grouped_ema/10000x100':row(10,12,[.8,.9]),
        'grouped_atr/10000x100':row(10,10.2,[.9,1.1]),
        'ema/1000':row(10,9,[1.05,1.2]),
        'control_cumsum/10000x100':row(2,2,[.98,1.02])},
        'original_vs_prior':{},'prior_vs_candidate':{}}}
    for name,value in data['comparisons']['original_vs_candidate'].items():
        data['comparisons']['original_vs_prior'][name] = row(value['baseline_median_ms'],11,[.8,1.2])
        data['comparisons']['prior_vs_candidate'][name] = row(11,value['candidate_median_ms'],[.8,1.2])
    rows = module.inventory({'results':{'1':data}})
    assert len(rows) == 4
    found = {r['case']:r for r in rows}
    assert found['grouped_ema/10000x100']['category'] == 'consistent slower >5% on this runner'
    assert found['grouped_atr/10000x100']['category'] == 'slow median, process ranges overlap'
    assert found['ema/1000']['category'] == 'not slower by median'
    assert found['grouped_ema/10000x100']['matching_polars_control'] == 'control_cumsum/10000x100'


@pytest.mark.parametrize('actual,expected', [(0., -0.), (-0., 0.)])
def test_workload_tolerant_reference_rejects_opposite_signed_zero(tmp_path, monkeypatch, actual, expected):
    import sys
    import polars as pl
    spec = importlib.util.spec_from_file_location('signed_zero_workload', ROOT/'scripts/migration_benchmark.py')
    workload = importlib.util.module_from_spec(spec); spec.loader.exec_module(workload)
    data = pl.DataFrame({'close': [actual]})
    expressions = [pl.col('close').alias('out')]
    reference = tmp_path/'reference.npz'
    np.savez(reference, zero_schema=np.array(str(data.select(expressions).schema)),
             zero_0=np.array([expected]), zero_0_null=np.array([False]))
    monkeypatch.setattr(workload, 'cases', lambda *_: iter([('zero', data, expressions)]))
    monkeypatch.setattr(sys, 'argv', ['migration_benchmark.py', '--output', str(tmp_path/'result.json'),
                        '--source-root', str(ROOT), '--label', 'signed-zero',
                        '--reference', str(reference)])
    def forbidden_timer():
        raise RuntimeError('measurement started before signed-zero validation')
    monkeypatch.setattr(workload.time, 'perf_counter_ns', forbidden_timer)
    with pytest.raises(AssertionError, match='signed zero differs'):
        workload.main()
