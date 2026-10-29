"""Reject invalid stage evidence and ambiguous dependency linkage."""
import importlib.util
import json
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
spec = importlib.util.spec_from_file_location('stages', ROOT / 'scripts/kernel_stage_benchmark.py')
stages = importlib.util.module_from_spec(spec); spec.loader.exec_module(stages)


def result(family='mmi', mode='kernel', n=10000, samples=None, version='0.8.1 (test)'):
    samples = [1., 2., 3., 4., 5., 6., 7.] if samples is None else samples
    return f'C_VERSION {version}\nPROBE {family}/{mode}/{n} allocations=0 bytes=0 holder_bytes=528 ns={json.dumps(samples)}\n'


def test_stage_parser_preserves_distribution_and_actual_counter_metadata():
    row = stages.parse_probe(result(), 'mmi', 'kernel', 10000)
    assert row['samples_ns'] == [1., 2., 3., 4., 5., 6., 7.]
    assert row['median_ns'] == 4. and row['holder_bytes'] == 528
    assert row['c_version'] == '0.8.1 (test)'


@pytest.mark.parametrize('change', ['version', 'family', 'mode', 'length', 'short', 'nan', 'zero', 'boolean', 'duplicate'])
def test_stage_parser_refuses_wrong_c_or_mismatched_and_invalid_samples(change):
    text = result()
    if change == 'version': text = result(version='0.8.4 (wrong C)')
    elif change == 'family': text = result(family='doji')
    elif change == 'mode': text = result(mode='full')
    elif change == 'length': text = result(n=1000000)
    elif change == 'short': text = result(samples=[1.] * 6)
    elif change == 'nan': text = result(samples=[1.] * 6 + [float('nan')])
    elif change == 'zero': text = result(samples=[1.] * 6 + [0.])
    elif change == 'boolean': text = result(samples=[1.] * 6 + [True])
    else: text += result()
    with pytest.raises(ValueError): stages.parse_probe(text, 'mmi', 'kernel', 10000)


def test_native_dependency_fingerprints_choose_actual_wheel_features_and_reject_conflicting_builds(tmp_path):
    root = tmp_path / 'release/.fingerprint'; deps = tmp_path / 'release/deps'; deps.mkdir(parents=True)
    parent = root / 'polars_talib-native'; parent.mkdir(parents=True)
    names = ('ta_lib', 'polars', 'serde', 'jemallocator')
    mapping = []
    for i, name in enumerate(names, 1):
        folder = root / (name + '-native'); folder.mkdir()
        (folder / ('lib-' + name)).write_text(i.to_bytes(8, 'little').hex())
        (folder / ('lib-' + name + '.json')).write_text('{}')
        (deps / ('lib' + name + '-native.rlib')).touch()
        mapping.append([i, name, False, i])
    (parent / 'lib-_polars_talib.json').write_text(json.dumps({'deps': mapping, 'rustflags': []}))
    (parent / 'lib-_polars_talib').write_text((100).to_bytes(8, 'little').hex())
    # The original C wheel's smaller Polars feature graph remains in the shared target.
    other = root / 'polars-original'; other.mkdir()
    (other / 'lib-polars').write_text((99).to_bytes(8, 'little').hex())
    (other / 'lib-polars.json').write_text('{}')
    (deps / 'libpolars-original.rlib').touch()
    found, evidence = stages.native_dependency_records(tmp_path)
    assert found['polars'].name == 'libpolars-native.rlib' and evidence
    conflict = root / 'polars_talib-conflict'; conflict.mkdir()
    mapping[1][-1] = 99
    (conflict / 'lib-_polars_talib.json').write_text(json.dumps({'deps': mapping, 'rustflags': []}))
    (conflict / 'lib-_polars_talib').write_text((101).to_bytes(8, 'little').hex())
    with pytest.raises(ValueError, match='disagree'):
        stages.native_dependency_records(tmp_path)


def test_kernel_cases_include_production_legacy_and_modern_attribution():
    cases = set(stages.kernel_cases())
    for n in (1000, 10000, 1000000):
        assert {('doji', n, 'kernel'), ('doji', n, 'ffi'), ('doji', n, 'full'),
                ('mmi', n, 'kernel'), ('mmi', n, 'modern'), ('mmi', n, 'abstract'),
                ('mmi', n, 'ffi'), ('mmi', n, 'full'),
                ('doji', n, 'init_zero_int'), ('doji', n, 'init_nan_real')} <= cases
    assert len(cases) == 54


def test_stage_provenance_rejects_changed_c_archive_and_support_source(tmp_path, monkeypatch):
    from types import SimpleNamespace
    folder = tmp_path / 'stages'; folder.mkdir()
    files = {}
    for name in ('input.bin', 'original.a', 'dependency.rlib', 'wrapper.rs', 'probe', 'compat.rs'):
        path = folder / name; path.write_bytes(name.encode()); files[name] = path
    builds = {side: {'wrapper': str(files['wrapper.rs']), 'wrapper_sha256': stages.sha256(files['wrapper.rs']),
                     'binary': str(files['probe']), 'binary_sha256': stages.sha256(files['probe']),
                     'support_source_files': {str(files['compat.rs']): stages.sha256(files['compat.rs'])},
                     'source': {'commit': side}} for side in stages.SIDES}
    record = {'dependency_fingerprints': {}, 'dependencies': {str(files['dependency.rlib']): stages.sha256(files['dependency.rlib'])},
              'native_archives': {str(files['original.a']): stages.sha256(files['original.a'])},
              'input_sha256': stages.sha256(files['input.bin']),
              'probe_source_sha256': stages.sha256(stages.PROBE),
              'controller_sha256': stages.sha256(stages.__file__), 'builds': builds}
    (folder / 'build-provenance.json').write_text(json.dumps(record))
    monkeypatch.setattr(stages, 'verify_build', lambda _: {'builds': {side: {'source': {'commit': side}} for side in stages.SIDES}})
    assert stages.verify(SimpleNamespace(output=tmp_path)) == record
    files['original.a'].write_bytes(b'new C implementation')
    with pytest.raises(ValueError, match='changed'):
        stages.verify(SimpleNamespace(output=tmp_path))
    files['original.a'].write_bytes(b'original.a')
    files['compat.rs'].write_bytes(b'new legacy tie policy')
    with pytest.raises(ValueError, match='changed'):
        stages.verify(SimpleNamespace(output=tmp_path))


def test_raw_fingerprint_endianness_matches_actual_rust190_cargo_artifact():
    # Observed native-single-chunk Cargo parent deps entry for Polars:
    # [12302415943370065676, "polars", false, 12829913266768297537].
    # Its .fingerprint/polars-e3f1f97ac13c28e9/lib-polars file contains this raw hex.
    assert stages.fingerprint_value('41becbec23020db2') == 12829913266768297537


def test_zero_product_parent_retains_unfiltered_c_and_test_filter_reasons(tmp_path):
    root = tmp_path / 'release/.fingerprint/polars_talib-current'; root.mkdir(parents=True)
    (root / 'lib-_polars_talib.json').write_text(json.dumps({'deps': [[1, 'talib', False, 8]], 'rustflags': []}))
    (root / 'test-lib-_polars_talib.json').write_text(json.dumps({'deps': [[1, name, False, i] for i, name in enumerate(('polars', 'serde', 'ta_lib', 'jemallocator'))], 'rustflags': []}))
    inventory = tmp_path / 'ordinary-inventory.json'
    with pytest.raises(ValueError, match='zero native product parents; unfiltered candidates=2'):
        stages.native_dependency_records(tmp_path, inventory_path=inventory)
    data = json.loads(inventory.read_text())
    assert all(not p['selected'] for p in data['parents'])
    assert any('missing native' in reason for p in data['parents'] for reason in p['filter_reasons'])
    assert any('test artifact' in reason for p in data['parents'] for reason in p['filter_reasons'])


def linkage_fixture(tmp_path):
    from types import SimpleNamespace
    dependencies = {}
    for name in ('ta_lib', 'polars', 'serde', 'jemallocator'):
        path = tmp_path / (name + '.rlib'); path.write_bytes(name.encode())
        dependencies[name] = {'path': str(path), 'sha256': stages.sha256(path)}
    provenance = {'flags': {'rustc': 'Rust1.90'}, 'builds': {}}
    for side in stages.SIDES:
        folder = tmp_path / 'linkage' / side; folder.mkdir(parents=True)
        fingerprint = folder / 'raw-parent'; fingerprint.write_bytes(b'wheel-time-raw-fingerprint')
        inventory = folder / 'inventory.json'; inventory.write_text('{}')
        build = {'source': {'commit': side}, 'identity': {'native': side}, 'wheel': {'sha256': side}}
        provenance['builds'][side] = build
        record = {'side': side, **build, 'flags': provenance['flags'], 'dependencies': dependencies,
                  'fingerprint_files': {str(fingerprint): stages.sha256(fingerprint)},
                  'inventory_path': str(inventory), 'inventory_sha256': stages.sha256(inventory)}
        (folder / 'product-linkage.json').write_text(json.dumps(record))
    return SimpleNamespace(output=tmp_path), provenance


def test_wheel_time_dependency_graph_survives_later_c_and_test_parent_overwrite(tmp_path):
    args, provenance = linkage_fixture(tmp_path)
    current = tmp_path / 'release/.fingerprint/polars_talib-current'; current.mkdir(parents=True)
    (current / 'lib-_polars_talib.json').write_text(json.dumps({'deps': [[1, 'talib', False, 9]], 'rustflags': []}))
    found, evidence = stages.product_dependency_records(args, provenance)
    assert set(found) == {'ta_lib', 'polars', 'serde', 'jemallocator'}
    assert all(p.is_file() for p in found.values())
    assert len(evidence) == 12


@pytest.mark.parametrize('change', ['source', 'snapshot', 'rlib', 'disagreeing_graph'])
def test_product_graph_snapshot_rejects_changed_wheel_source_or_dependencies(tmp_path, change):
    args, provenance = linkage_fixture(tmp_path)
    folder = tmp_path / 'linkage/mmi'; path = folder / 'product-linkage.json'
    record = json.loads(path.read_text())
    if change == 'source':
        record['source']['commit'] = 'different'; path.write_text(json.dumps(record))
    elif change == 'snapshot': (folder / 'raw-parent').write_bytes(b'unit-test-fingerprint-overwrite')
    elif change == 'rlib': (tmp_path / 'polars.rlib').write_bytes(b'wrong-features')
    else:
        different = tmp_path / 'different-polars.rlib'; different.write_bytes(b'different-polars')
        record['dependencies']['polars'] = {'path': str(different), 'sha256': stages.sha256(different)}
        path.write_text(json.dumps(record))
    with pytest.raises(ValueError): stages.product_dependency_records(args, provenance)
