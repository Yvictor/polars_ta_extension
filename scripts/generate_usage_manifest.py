"""Freeze public Python signatures and their mapping to the TA-Lib/Polars ABI.

No installed package or reference binding is used to generate this manifest.
Runtime tests independently check it against inspect and official abstract metadata.
"""
import ast
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUST_UNEXPOSED = ['ALMA', 'ASI', 'BBW', 'CG', 'CHOP', 'CHOPTR', 'CKSP', 'CRSI', 'CTI', 'DOSC', 'EMV', 'FISHER', 'FRAMA', 'IBS', 'ICHIMOKU', 'KST', 'KSTEXT', 'KURTOSIS', 'KVO', 'MCGD', 'MEDIAN', 'PERCENTB', 'PSO', 'ROGERSSATCHELL', 'RVIR', 'SI', 'SQZMOM', 'STC', 'SWAK_2PHP', 'SWAK_BP', 'SWAK_BUTTER', 'SWAK_GAUSS', 'SWAK_HP', 'VIDYA', 'WAVETREND', 'ZIGZAG']

FORMS = ['positional_names', 'positional_exprs', 'keyword_names', 'keyword_exprs',
         'mixed', 'positional_parameters', 'namespace_positional_parameters', 'defaults', 'namespace_names', 'namespace_keywords', 'typed_col']
SCENARIOS = ['finite', 'leading_null', 'internal_null', 'internal_nan', 'empty',
             'short', 'chunked', 'interleaved_over']


def generate():
    api = json.loads((ROOT/'scripts/api.json').read_text())
    abi = json.loads((ROOT/'scripts/plugin_abi.json').read_text())
    functions, methods = {}, {}
    legacy = set()
    for file in ('__init__.py', '_generated.py'):
        tree = ast.parse((ROOT/'python/polars_talib'/file).read_text())
        functions.update({n.name: n for n in tree.body if isinstance(n, ast.FunctionDef)})
        if file == "__init__.py": legacy = set(functions)
        for cls in (n for n in tree.body if isinstance(n, ast.ClassDef)):
            methods.update({n.name: n for n in cls.body if isinstance(n, ast.FunctionDef)})
    entries = {}
    for spec in api:
        name = spec['name']; count = len(spec['inputs'])
        function, method = functions[name], methods[name]
        args = function.args.args
        defaults = dict(zip([a.arg for a in args[-len(function.args.defaults):]], function.args.defaults))
        input_names = [a.arg for a in args[:count]]
        namespace_names = [a.arg for a in method.args.args[1:count]]
        method_defaults = dict(zip([a.arg for a in method.args.args[-len(method.args.defaults):]], method.args.defaults))
        namespace_defaults_applicable = all(key in method_defaults for key in namespace_names)
        order = abi[name]['order']
        if name not in legacy:
            primary = spec['inputs'].index('close') if 'close' in spec['inputs'] else 0
            namespace_role_order = [primary] + [i for i in range(count) if i != primary]
        else:
            namespace_role_order = [order.index(i) for i in range(count)]
        default_columns = []
        for key in input_names:
            node = defaults[key]
            assert isinstance(node, ast.Call) and ast.unparse(node.func) == 'pl.col', name
            default_columns.append(ast.literal_eval(node.args[0]))
        alternate = {}
        for p in spec['params']:
            key, value = p['name'], p['default']
            alternate[key] = (0 if value != 0 else 1) if p['type'] == 'TA_MAType' else (
                value * .8 if value else .2) if p['type'] == 'double' else (
                value + 1 if value >= 1 else 2)
        entries[name] = {'inputs': input_names, 'roles': spec['inputs'],
                         'default_columns': default_columns,
                         'namespace_inputs': namespace_names,
                         'namespace_defaults_applicable': namespace_defaults_applicable,
                         'namespace_default_exclusion': None if namespace_defaults_applicable else 'Namespace requires explicit non-receiver input(s)',
                         'namespace_parameter_order': [a.arg for a in method.args.args[count:]],
                         'namespace_role_order': namespace_role_order,
                         'parameters': spec['params'], 'nondefault': alternate,
                         'outputs': spec['outputs'], 'struct_fields': abi[name]['fields'],
                         'forms': FORMS, 'scenarios': SCENARIOS,
                         'additional_forms': ['series', 'numpy_array', 'scalar', 'namespace_default_columns'],
                         'invalid': ['unknown_keyword', 'too_many_positional', 'missing_column'] +
                                    (['length_mismatch'] if count > 1 else []) +
                                    (['parameter_types'] if spec['params'] else [])}
    result = {'schema_version': 1, 'reference': 'TA-Lib Python 0.8.1 / C 0.8.1; Rust 0.8.3 metadata',
              'rust_metadata_count': 237, 'rust_additional_not_exposed': RUST_UNEXPOSED,
              'helpers_excluded': ['col', 'get_function_groups', 'get_functions', 'get_functions_output_struct',
                                   'initialize', 'shutdown', 'version', 'register_plugin', 'parse_version', 'parse_into_expr'],
              'functions': entries}
    return result


if __name__ == '__main__':
    path = ROOT/'scripts/public_api_coverage.json'
    path.write_text(json.dumps(generate(), indent=2)+'\n')
    print(f'wrote {path.name} ({len(generate()["functions"])} functions)')
