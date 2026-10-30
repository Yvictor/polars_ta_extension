"""Keep one executable default-use example on every public function and method."""
import ast
from pathlib import Path
from generate_usage_manifest import generate as usage_manifest

ROOT = Path(__file__).resolve().parents[1]


def generate():
    specs = usage_manifest()['functions']
    for filename in ('__init__.py', '_generated.py'):
        path = ROOT/'python/polars_talib'/filename
        lines = path.read_text().splitlines()
        tree = ast.parse('\n'.join(lines))
        edits = []
        for parent in [tree] + [n for n in tree.body if isinstance(n, ast.ClassDef)]:
            namespace = isinstance(parent, ast.ClassDef)
            for node in parent.body:
                if not isinstance(node, ast.FunctionDef) or node.name not in specs:
                    continue
                spec = specs[node.name]
                params = [f"{p['name']}={p['default']!r}" for p in spec['parameters']]
                columns = spec['default_columns']
                if namespace:
                    ordered = [columns[i] for i in spec['namespace_role_order']]
                    call = f'pl.col({ordered[0]!r}).ta.{node.name}('
                    args = [repr(c) for c in ordered[1:]]
                else:
                    call = f'ta.{node.name}('
                    args = [repr(c) for c in columns]
                example = call + ', '.join(args + params) + ')'
                doc = ast.get_docstring(node).splitlines()
                doc = [line for line in doc if '.ta.' not in line and not line.strip().startswith(f'ta.{node.name}(')]
                doc.insert(1, example)
                prefix = ' ' * node.body[0].col_offset
                replacement = [prefix + '"""' + doc[0]] + [prefix + line if line else '' for line in doc[1:]] + [prefix + '"""']
                edits.append((node.body[0].lineno-1, node.body[0].end_lineno, replacement))
        for begin, end, replacement in sorted(edits, reverse=True):
            lines[begin:end] = replacement
        path.write_text('\n'.join(lines)+'\n')


if __name__ == '__main__':
    generate()
