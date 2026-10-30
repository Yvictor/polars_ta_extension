"""Performance reports must expose process noise instead of false certainty."""
import importlib.util
from pathlib import Path

import pytest


spec=importlib.util.spec_from_file_location('migration_ci_benchmark',Path(__file__).parents[1]/'scripts/migration_ci_benchmark.py')
benchmark=importlib.util.module_from_spec(spec)
spec.loader.exec_module(benchmark)


def runs(medians):
    return [{'results':{'ema/1000':{'median_ms':m,'samples_ms':[m*.9,m,m*1.1]}}} for m in medians]


def test_noisy_processes_do_not_become_a_speedup_claim():
    row=benchmark.summarize(runs([1,1,4]),runs([.8,.8,3]))['ema/1000']
    # Even thousands of correlated inner samples would not remove this spread.
    assert row['median_paired_ratio']>1.2
    assert row['ratio_envelope'][0]<1<row['ratio_envelope'][1]
    assert row['assessment']=='small or noisy difference'
    assert len(row['paired_ratios'])==3


def test_consistent_regression_is_reported_as_such():
    row=benchmark.summarize(runs([1,1.01,.99]),runs([2,2.02,1.98]))['ema/1000']
    assert row['assessment']=='consistent slower on this runner'
    assert row['median_paired_ratio']==.5


def test_comparison_rejects_missing_workloads_and_unpaired_processes():
    with pytest.raises(ValueError):benchmark.summarize(runs([1,2,3]),runs([1,2]))
    other=runs([1,2,3]);other[-1]['results']={}
    with pytest.raises(ValueError):benchmark.summarize(runs([1,2,3]),other)
