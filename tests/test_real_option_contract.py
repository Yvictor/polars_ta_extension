"""Original C public real-option expectations, including namespace receiver roles."""
import copy
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('real_option_contract', ROOT / 'scripts/real_option_contract.py')
contract = importlib.util.module_from_spec(spec)
spec.loader.exec_module(contract)
REFERENCE = json.loads(gzip.decompress((contract.DATA / 'real-option-reference.json.gz').read_bytes()))


def verify_reference(reference):
    expected = set().union(*(contract.case_ids(option) for option in contract.MANIFEST['options']))
    assert set(reference['cases']) == expected
    assert len(expected) == 3780
    assert reference['manifest_sha256'] == hashlib.sha256((contract.DATA / 'real-option-manifest.json').read_bytes()).hexdigest()
    assert reference['input_sha256'] == hashlib.sha256((contract.DATA / 'real-option-inputs.npz').read_bytes()).hexdigest()
    assert reference['reference'] == contract.MANIFEST['reference']
    assert reference['native_sha256'] == reference['reference']['native_sha256']


def test_real_option_inventory_and_original_reference_are_closed():
    contract.inventory()
    verify_reference(REFERENCE)
    for name, frame in contract.frames().items():
        assert contract.frame_hash(frame) == REFERENCE['fixture_hashes'][name]


def test_missing_real_option_or_case_cannot_silently_reduce_coverage():
    api = copy.deepcopy(contract.API)
    api['sarext']['params'].append({'name': 'uncovered_real', 'type': 'double'})
    with pytest.raises(AssertionError, match='real-option coverage changed'):
        contract.inventory(api=api)
    manifest = copy.deepcopy(contract.MANIFEST)
    manifest['options'].pop()
    with pytest.raises(AssertionError, match='real-option coverage changed'):
        contract.inventory(manifest=manifest)
    missing = dict(REFERENCE, cases=dict(REFERENCE['cases']))
    missing['cases'].pop(next(iter(missing['cases'])))
    with pytest.raises(AssertionError):
        verify_reference(missing)


def test_all_public_namespace_receivers_match_source_signatures_and_abi():
    contract.binding_contract()
    assert contract.USAGE['kc']['namespace_role_order'][0] == 2
    assert contract.USAGE['supertrend']['namespace_role_order'][0] == 2
    assert contract.USAGE['aroon']['namespace_role_order'][0] == 0


def test_receiver_verifier_rejects_a_first_input_assumption(monkeypatch):
    usage = copy.deepcopy(contract.USAGE)
    usage['kc']['namespace_role_order'] = [0, 1, 2]
    monkeypatch.setattr(contract, 'USAGE', usage)
    with pytest.raises(AssertionError):
        contract.binding_contract()


def error_contract(got, want):
    assert got['class'] == want['class']
    assert got['ta_codes'] == want['ta_codes']



def test_error_codes_survive_polars_display_prefix_changes():
    reference = contract.error_record(ValueError('plugin failed: TA_BAD_PARAM'))
    wrapped = contract.error_record(ValueError('new wrapper prefix\nplugin failed: TA_BAD_PARAM\nTA_BAD_PARAM'))
    error_contract(wrapped, reference)
    with pytest.raises(AssertionError):
        error_contract(contract.error_record(ValueError('TA_INTERNAL_ERROR')), reference)
    with pytest.raises(AssertionError):
        error_contract(contract.error_record(TypeError('TA_BAD_PARAM')), reference)


def compare(got, want):
    assert set(got) == set(want)
    for phase in ('lookback', 'construction', 'execution'):
        if phase not in want:
            continue
        a, b = got[phase], want[phase]
        assert ('error' in a) == ('error' in b)
        if 'error' in b:
            error_contract(a['error'], b['error'])
            continue
        if phase == 'lookback':
            assert a == b
            continue
        assert (a['schema'], a['height']) == (b['schema'], b['height'])
        assert len(a['fields']) == len(b['fields'])
        for actual, expected in zip(a['fields'], b['fields']):
            assert (actual['name'], actual['dtype']) == (expected['name'], expected['dtype'])
            np.testing.assert_array_equal(actual['null'], expected['null'])
            if 'bits' not in expected:
                assert actual['values'] == expected['values']
                continue
            av = np.array([int(x, 16) for x in actual['bits']], dtype=np.uint64).view(np.float64)
            bv = np.array([int(x, 16) for x in expected['bits']], dtype=np.uint64).view(np.float64)
            valid = ~np.array(expected['null'], dtype=bool)
            av, bv = av[valid], bv[valid]
            np.testing.assert_array_equal(np.isnan(av), np.isnan(bv))
            np.testing.assert_array_equal(np.isposinf(av), np.isposinf(bv))
            np.testing.assert_array_equal(np.isneginf(av), np.isneginf(bv))
            zeros = bv == 0
            np.testing.assert_array_equal(av[zeros].view(np.uint64), bv[zeros].view(np.uint64))
            finite = np.isfinite(bv)
            # Same policy as migration_probe.compare's ordinary finite lane.
            np.testing.assert_allclose(av[finite], bv[finite], rtol=1e-10, atol=1e-10)


@pytest.mark.parametrize('option', contract.MANIFEST['options'],
                         ids=lambda option: option['function'] + '/' + option['option'])
def test_public_real_options_match_original_c_contract(option):
    data = contract.frames()
    checked = set()
    failures = []
    for variant in contract.VARIANTS:
        for fixture in contract.FIXTURES:
            for form in contract.FORMS:
                key = '/'.join((option['function'], option['option'], variant, fixture, form))
                actual = contract.capture_case(option, variant, fixture, form, data[fixture])
                checked.add(key)
                try:
                    compare(actual, REFERENCE['cases'][key])
                except AssertionError as exc:
                    failures.append(f'{key}: {exc}')
    assert checked == contract.case_ids(option)
    assert not failures, '\n'.join(failures)
