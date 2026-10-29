"""Replay the frozen C0.8.1 public real-option contract using expression inputs.

Regenerate only in the original wheel environment, with an explicit binary pin:
python scripts/real_option_contract.py --capture tests/data/real-option-reference.json.gz \
    --expected-native-sha256 HASH
The metadata printer in real_option_metadata.c supplies the original range data.
"""
from __future__ import annotations
import argparse
import ast
import gzip
import hashlib
import inspect
import json
import re
from pathlib import Path
import struct
import textwrap

import numpy as np
import polars as pl
import polars_talib as ta
from polars_talib._polars_talib import lookback

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'tests/data'
API = {f['name']: f for f in json.loads((ROOT / 'scripts/api.json').read_text())}
USAGE = json.loads((ROOT / 'scripts/public_api_coverage.json').read_text())['functions']
ABI = json.loads((ROOT / 'scripts/plugin_abi.json').read_text())
MANIFEST = json.loads((DATA / 'real-option-manifest.json').read_text())
VARIANTS = ('omitted_default', 'explicit_default', 'nan', 'positive_infinity',
            'negative_infinity', 'default_sentinel', 'finite_below_minimum',
            'finite_above_maximum', 'finite_far_low', 'finite_far_high',
            'positive_zero', 'negative_zero', 'minimum', 'maximum')
FIXTURES = ('empty', 'one', 'finite', 'null_chunked_offset', 'interleaved_over')
FORMS = ('namespace', 'expression_method')


def inventory(api=API, manifest=MANIFEST):
    real = {(f['name'], p['name']) for f in api.values()
            for p in f['params'] if p['type'] == 'double'}
    frozen = {(p['function'], p['option']) for p in manifest['options']}
    assert real == frozen, f'real-option coverage changed: {real ^ frozen}'
    assert len(real) == 27 and len({name for name, _ in real}) == 17
    assert set(api) == set(USAGE) == {f['name'] for f in manifest['all_functions']}
    assert len(api) == 201
    for option in manifest['options']:
        assert tuple(v['name'] for v in option['variants']) == VARIANTS
        param = next(p for p in api[option['function']]['params'] if p['name'] == option['option'])
        assert param['c_name'] == option['c_name']
        assert param['default'] == option['metadata']['default']
    return real


def binding_contract():
    """Check receiver aliases against installed source, signatures and the ABI."""
    for name, spec in API.items():
        rule = USAGE[name]
        assert rule['roles'] == spec['inputs']
        count = len(spec['inputs'])
        order = rule['namespace_role_order']
        assert sorted(order) == list(range(count)), name
        method = getattr(pl.col('__receiver__').ta, name)
        parameters = list(inspect.signature(method).parameters)
        assert parameters[:count - 1] == rule['namespace_inputs'], name
        assert parameters[count - 1:] == rule['namespace_parameter_order'], name

        def source_roles(function, mapping, depth=0):
            assert depth <= 1, name
            tree = ast.parse(textwrap.dedent(inspect.getsource(function)))
            calls = [node for node in ast.walk(tree) if isinstance(node, ast.Call)
                     and isinstance(node.func, ast.Name)
                     and (node.func.id == 'register_plugin' or node.func.id.startswith('_call_'))]
            assert len(calls) == 1, name
            call = calls[0]

            def role(node):
                if (isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name)
                        and node.value.id == 'self' and node.attr == '_expr'):
                    return order[0]
                assert isinstance(node, ast.Name) and node.id in mapping, (name, ast.dump(node))
                return mapping[node.id]

            if call.func.id == 'register_plugin':
                args = next(k.value for k in call.keywords if k.arg == 'args')
                assert isinstance(args, ast.List), name
                return [role(node) for node in args.elts]
            owner = function.__func__ if inspect.ismethod(function) else function
            callee = owner.__globals__[call.func.id]
            inputs = list(inspect.signature(callee).parameters)[:count]
            bound = {param: role(node) for param, node in zip(inputs, call.args)}
            bound.update({k.arg: role(k.value) for k in call.keywords if k.arg in inputs})
            assert set(bound) == set(inputs), name
            return source_roles(callee, bound, depth + 1)

        actual = source_roles(method, dict(zip(rule['namespace_inputs'], order[1:])))
        assert actual == list(np.argsort(ABI[name]['order'])), name


def frames():
    with np.load(DATA / 'real-option-inputs.npz', allow_pickle=False) as source:
        base = pl.DataFrame({name: source[name] for name in source.files}).slice(3, 257)
    null = base.with_columns(
        pl.when(pl.int_range(pl.len()).is_in([0, 1, 29, 104])).then(None)
        .otherwise(pl.col(c)).alias(c) for c in base.columns if c != 'periods')
    chunked = pl.concat([null.slice(i, 41) for i in range(0, 257, 41)], rechunk=False)
    assert all(chunked[c].n_chunks() > 1 for c in chunked.columns)
    return {'empty': base.head(0), 'one': base.head(1), 'finite': base,
            'null_chunked_offset': chunked,
            'interleaved_over': null.with_columns((pl.int_range(pl.len()) % 3).alias('g'))}


def frame_hash(df):
    digest = hashlib.sha256()
    for name in df.columns:
        series = df[name]
        digest.update(name.encode())
        digest.update(series.is_null().to_numpy().tobytes())
        digest.update(series.fill_null(0).to_numpy().tobytes())
    return digest.hexdigest()


def case_ids(option):
    return {'/'.join((option['function'], option['option'], variant, fixture, form))
            for variant in VARIANTS for fixture in FIXTURES for form in FORMS}


def error_record(exc):
    message = str(exc)
    return {'class': type(exc).__module__ + '.' + type(exc).__qualname__,
            'message_head': message.split('\n', 1)[0],
            'ta_codes': sorted(set(re.findall(r'\bTA_[A-Z_]+\b', message)))}


def capture_case(option, variant, fixture, form, data):
    name = option['function']
    bits = next(v['bits'] for v in option['variants'] if v['name'] == variant)
    params = {} if bits is None else {option['option']: struct.unpack('>d', bytes.fromhex(bits))[0]}
    row = {}


    try:
        row['lookback'] = {'value': lookback(name, params or None)}
    except Exception as exc:
        row['lookback'] = {'error': error_record(exc)}
    try:
        columns = [{'real': 'close', 'real0': 'high', 'real1': 'low'}.get(i, i)
                   for i in API[name]['inputs']]
        expressions = [pl.col(c) for c in columns]
        if form == 'namespace':
            expression = getattr(ta, name)(*expressions, **params)
        else:
            rule = USAGE[name]
            order = rule['namespace_role_order']
            method = getattr(expressions[order[0]].ta, name)
            expression = method(**dict(zip(rule['namespace_inputs'],
                                           [expressions[i] for i in order[1:]])), **params)
        if fixture == 'interleaved_over':
            expression = expression.over('g')
        expression = expression.alias('result')
    except Exception as exc:
        row['construction'] = {'error': error_record(exc)}
        return row
    try:
        result = data.select(expression).to_series()
    except Exception as exc:
        row['execution'] = {'error': error_record(exc)}
        return row
    fields = ([result.struct.field(f) for f in result.struct.fields]
              if isinstance(result.dtype, pl.Struct) else [result])
    row['execution'] = {'schema': str(result.dtype), 'height': len(result), 'fields': []}
    for field in fields:
        values = field.fill_null(0).to_numpy()
        item = {'name': field.name, 'dtype': str(field.dtype),
                'null': field.is_null().to_numpy().tolist()}
        if values.dtype.kind == 'f':
            assert values.dtype.itemsize == 8
            item['bits'] = [f'{int(value):016x}' for value in values.view(np.uint64)]
        else:
            item['values'] = [int(value) for value in values]
        row['execution']['fields'].append(item)
    return row


def capture_reference(path, expected_native_sha256):
    module = Path(ta._polars_talib.__file__)
    assert hashlib.sha256(module.read_bytes()).hexdigest() == expected_native_sha256
    assert ta.__talib_version__.startswith('0.8.1 '), 'capture requires the original C wheel'
    inventory()
    binding_contract()
    data = frames()
    rows = {}
    for option in MANIFEST['options']:
        for variant in VARIANTS:
            for fixture in FIXTURES:
                for form in FORMS:
                    key = '/'.join((option['function'], option['option'], variant, fixture, form))
                    rows[key] = capture_case(option, variant, fixture, form, data[fixture])
    assert len(rows) == 3780
    result = {'schema_version': 1, 'reference': MANIFEST['reference'],
              'native_sha256': expected_native_sha256, 'talib_version': ta.__talib_version__,
              'manifest_sha256': hashlib.sha256((DATA / 'real-option-manifest.json').read_bytes()).hexdigest(),
              'input_sha256': hashlib.sha256((DATA / 'real-option-inputs.npz').read_bytes()).hexdigest(),
              'fixture_hashes': {name: frame_hash(df) for name, df in data.items()}, 'cases': rows}
    with Path(path).open('wb') as raw, gzip.GzipFile(fileobj=raw, mode='wb', mtime=0) as output:
        output.write(json.dumps(result, separators=(',', ':'), allow_nan=False).encode())


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--capture', type=Path, required=True)
    parser.add_argument('--expected-native-sha256', required=True)
    args = parser.parse_args()
    capture_reference(args.capture, args.expected_native_sha256)
