#!/usr/bin/env python3
"""Generate wrapper code for TA-Lib functions that are not yet exposed.

The script reads the C prototypes from ``ta_func.h`` and the metadata of the
Python ``ta-lib`` package (groups, parameter names/defaults, output names) and
emits, in the style of the hand written code base:

* ``talib/src/<module>.rs``      safe Rust wrappers + ``*Kwargs`` structs
* ``src/<module>.rs``            ``#[polars_expr]`` entry points
* ``python/polars_talib/__init__.py``  ``TAExpr`` methods, module level
  functions, ``__function_groups__`` and ``get_functions_output_struct``
* ``tests/test_ta.py`` / ``tests/test_nan.py`` parametrized lists

Usage (from the repository root, with a venv that has the target ``ta-lib``
Python version installed)::

    python scripts/gen_talib_functions.py --header dependencies/include/ta-lib/ta_func.h --apply

Without ``--apply`` the generated code is printed instead of written.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import OrderedDict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

GROUP_MODULE = {
    "Cycle Indicators": "cycle",
    "Math Operators": "math",
    "Math Transform": "math",
    "Momentum Indicators": "momentum",
    "Overlap Studies": "overlap",
    "Pattern Recognition": "pattern",
    "Price Transform": "transform",
    "Statistic Functions": "statistic",
    "Volatility Indicators": "volatility",
    "Volume Indicators": "volume",
}

IN_NAME = {
    "inReal": "real",
    "inReal0": "real0",
    "inReal1": "real1",
    "inOpen": "open",
    "inHigh": "high",
    "inLow": "low",
    "inClose": "close",
    "inVolume": "volume",
    "inPeriods": "periods",
}

C_TYPE = {"int": "i32", "double": "f64", "TA_MAType": "TA_MAType"}


def camel(name: str) -> str:
    return "".join(p.capitalize() for p in name.lower().split("_"))


def parse_prototypes(header: Path) -> dict[str, dict]:
    src = header.read_text()
    protos = {}
    for m in re.finditer(r"TA_LIB_API TA_RetCode (TA_[A-Z0-9_]+)\((.*?)\);", src, re.S):
        name, body = m.group(1), m.group(2)
        if name.startswith("TA_S_"):
            continue
        body = re.sub(r"/\*.*?\*/", "", body, flags=re.S)
        args = [re.sub(r"\s+", " ", a).strip() for a in body.split(",")]
        inputs, params, outputs = [], [], []
        for a in args:
            if a in ("int startIdx", "int endIdx", "int *outBegIdx", "int *outNBElement"):
                continue
            mm = re.match(r"const (double|float) (in\w+)\[\]", a)
            if mm:
                inputs.append(IN_NAME[mm.group(2)])
                continue
            mm = re.match(r"(int|double|TA_MAType) (optIn\w+)", a)
            if mm:
                params.append((mm.group(2), C_TYPE[mm.group(1)]))
                continue
            mm = re.match(r"(double|int) (out\w+)\[\]", a)
            if mm:
                outputs.append((mm.group(2), "f64" if mm.group(1) == "double" else "i32"))
                continue
            raise ValueError(f"{name}: cannot parse argument {a!r}")
        protos[name[3:]] = {"inputs": inputs, "params": params, "outputs": outputs}
    return protos


def load_meta(meta_path: Path | None, groups_path: Path | None) -> dict:
    if meta_path is not None:
        meta = json.loads(meta_path.read_text())
        if "__groups__" not in meta:
            if groups_path is None:
                raise SystemExit("--groups is required when --meta has no __groups__ entry")
            meta["__groups__"] = json.loads(groups_path.read_text())
        return meta
    import talib  # noqa: WPS433
    from talib import abstract

    out = OrderedDict()
    for name in talib.get_functions():
        info = abstract.Function(name).info
        out[name] = {
            "group": info["group"],
            "display_name": info["display_name"],
            "input_names": dict(info["input_names"]),
            "parameters": dict(info["parameters"]),
            "output_names": list(info["output_names"]),
        }
    out["__groups__"] = talib.get_function_groups()
    return out


def arg_order(inputs: list[str]) -> tuple[str, list[str]]:
    """Return (primary input, plugin argument order) following the code base
    conventions: close is primary for price based functions, open for OHLC
    functions and the first input otherwise."""
    if "open" in inputs:
        primary = "open"
    elif "close" in inputs:
        primary = "close"
    else:
        primary = inputs[0]
    return primary, [primary] + [i for i in inputs if i != primary]


class Spec:
    def __init__(self, name: str, proto: dict, meta: dict):
        self.c_name = name
        self.py = name.lower()
        self.group = meta["group"]
        self.module = GROUP_MODULE[self.group]
        self.display = meta["display_name"]
        self.inputs = proto["inputs"]
        self.primary, self.args = arg_order(self.inputs)
        py_params = list(meta["parameters"].items())
        if len(py_params) != len(proto["params"]):
            raise ValueError(f"{name}: parameter mismatch {py_params} vs {proto['params']}")
        self.params = [
            (py_name, rust_ty, default)
            for (py_name, default), (_c_name, rust_ty) in zip(py_params, proto["params"])
        ]
        py_outputs = meta["output_names"]
        if len(py_outputs) != len(proto["outputs"]):
            raise ValueError(f"{name}: output mismatch {py_outputs} vs {proto['outputs']}")
        self.outputs = [(py_name, ty) for py_name, (_c, ty) in zip(py_outputs, proto["outputs"])]

    # ----- naming helpers -------------------------------------------------
    @property
    def kwargs_struct(self) -> str | None:
        if not self.params:
            return None
        if [p[0] for p in self.params] == ["timeperiod"]:
            return "TimePeriodKwargs"
        return f"{camel(self.py)}Kwargs"

    @property
    def custom_kwargs(self) -> bool:
        return self.kwargs_struct not in (None, "TimePeriodKwargs")

    @property
    def multi(self) -> bool:
        return len(self.outputs) > 1

    def rust_ret(self) -> str:
        if self.multi:
            return "(" + ", ".join(f"Vec<{t}>" for _, t in self.outputs) + ")"
        return f"Vec<{self.outputs[0][1]}>"

    # ----- Rust safe wrapper ---------------------------------------------
    def rust_wrapper(self) -> str:
        lines = []
        if self.custom_kwargs:
            lines.append("#[derive(Builder, Deserialize)]")
            lines.append(f"pub struct {self.kwargs_struct} {{")
            for py_name, ty, default in self.params:
                if ty != "TA_MAType":
                    d = default if ty == "i32" else float(default)
                    lines.append(f'    #[builder(default = "{d}")]')
                lines.append(f"    pub {py_name}: {ty},")
            lines.append("}")
            lines.append("")
        sig_inputs = "".join(f"    {i}_ptr: *const f64,\n" for i in self.inputs)
        kw = f"    kwargs: &{self.kwargs_struct},\n" if self.params else ""
        lines.append(f"pub fn ta_{self.py}(")
        lines.append(sig_inputs + "    len: usize,\n" + kw + f") -> Result<{self.rust_ret()}, TA_RetCode> {{")
        lines.append("    let mut out_begin: TA_Integer = 0;")
        lines.append("    let mut out_size: TA_Integer = 0;")
        ptrs = ", ".join(f"{i}_ptr" for i in self.inputs)
        lines.append(f"    let begin_idx = check_begin_idx{len(self.inputs)}(len, {ptrs}) as i32;")
        lines.append("    let end_idx = len as i32 - begin_idx - 1;")
        lb_args = ", ".join(f"kwargs.{p[0]}" for p in self.params)
        lines.append(f"    let lookback = begin_idx + unsafe {{ TA_{self.c_name}_Lookback({lb_args}) }};")
        lines.append("    if lookback < 0 {")
        lines.append("        return Err(TA_RetCode::TA_BAD_PARAM);")
        lines.append("    }")
        lines.append("    if cannot_produce_output(len, lookback) {")
        if self.multi:
            defaults = ", ".join("make_default_vec(len)" for _ in self.outputs)
            lines.append(f"        return Ok(({defaults}));")
        else:
            lines.append("        return Ok(make_default_vec(len));")
        lines.append("    }")
        out_vars = [f"out{n}" if self.multi else "out" for n, _ in self.outputs]
        out_ptrs = [f"{v}_ptr" if self.multi else "ptr" for v in out_vars]
        for v, p in zip(out_vars, out_ptrs):
            lines.append(f"    let (mut {v}, {p}) = make_vec(len, lookback);")
        lines.append("    let ret_code = unsafe {")
        lines.append(f"        TA_{self.c_name}(")
        lines.append("            0,")
        lines.append("            end_idx,")
        for i in self.inputs:
            lines.append(f"            {i}_ptr.offset(begin_idx as isize),")
        for p in self.params:
            lines.append(f"            kwargs.{p[0]},")
        lines.append("            &mut out_begin,")
        lines.append("            &mut out_size,")
        for p in out_ptrs:
            lines.append(f"            {p},")
        lines.append("        )")
        lines.append("    };")
        lines.append("    let out_size_begin = (begin_idx + out_begin + out_size) as usize;")
        lines.append("    match ret_code {")
        lines.append("        TA_RetCode::TA_SUCCESS => {")
        lines.append("            if out_size != 0 {")
        lines.append("                unsafe {")
        for v in out_vars:
            lines.append(f"                    {v}.set_len(out_size_begin);")
        lines.append("                }")
        lines.append("            } else {")
        lines.append("                unsafe {")
        for v in out_vars:
            lines.append(f"                    {v}.set_len(len);")
        lines.append("                }")
        lines.append("            }")
        if self.multi:
            lines.append("            Ok((" + ", ".join(out_vars) + "))")
        else:
            lines.append("            Ok(out)")
        lines.append("        }")
        lines.append("        _ => Err(ret_code),")
        lines.append("    }")
        lines.append("}")
        return "\n".join(lines) + "\n"

    def rust_wrapper_uses(self) -> list[str]:
        uses = [f"use talib_sys::{{TA_{self.c_name}_Lookback, TA_{self.c_name}}};"]
        return uses

    # ----- polars expression ---------------------------------------------
    def polars_expr(self) -> str:
        lines = []
        chunked = {"f64": "Float64", "i32": "Int32"}
        if self.multi:
            lines.append(f"pub fn {self.py}_output(_: &[Field]) -> PolarsResult<Field> {{")
            for n, t in self.outputs:
                lines.append(f'    let {n} = Field::new("{n}", DataType::{chunked[t]});')
            lines.append("    let v: Vec<Field> = vec![" + ", ".join(n for n, _ in self.outputs) + "];")
            lines.append('    Ok(Field::new("", DataType::Struct(v)))')
            lines.append("}")
            lines.append("")
            lines.append(f"#[polars_expr(output_type_func={self.py}_output)]")
        else:
            lines.append(f"#[polars_expr(output_type={chunked[self.outputs[0][1]]})]")
        kw = f", kwargs: {self.kwargs_struct}" if self.params else ""
        lines.append(f"fn {self.py}(inputs: &[Series]{kw}) -> PolarsResult<Series> {{")
        for idx, arg in enumerate(self.args):
            lines.append(f"    let {arg} = &mut cast_series_to_f64(&inputs[{idx}])?;")
        for arg in self.args:
            lines.append(f"    let ({arg}_ptr, _{arg}) = get_series_f64_ptr({arg})?;")
        lines.append(f"    let len = {self.primary}.len();")
        call_args = ", ".join(f"{i}_ptr" for i in self.inputs)
        kw_call = ", &kwargs" if self.params else ""
        lines.append(f"    let res = ta_{self.py}({call_args}, len{kw_call});")
        lines.append("    match res {")
        if self.multi:
            outs = ", ".join(f"out{n}" for n, _ in self.outputs)
            lines.append(f"        Ok(({outs})) => {{")
            for n, _ in self.outputs:
                lines.append(f'            let {n} = Series::from_vec("{n}", out{n});')
            lines.append('            let out = StructChunked::new("", &[' + ", ".join(n for n, _ in self.outputs) + "])?;")
            lines.append("            Ok(out.into_series())")
            lines.append("        }")
        else:
            lines.append(f'        Ok(out) => Ok({chunked[self.outputs[0][1]]}Chunked::from_vec("", out).into_series()),')
        lines.append("        Err(ret_code) => ta_code2err(ret_code),")
        lines.append("    }")
        lines.append("}")
        return "\n".join(lines) + "\n"

    def polars_expr_uses(self) -> list[str]:
        items = [f"ta_{self.py}"]
        if self.custom_kwargs:
            items.append(self.kwargs_struct)
        uses = [f"use talib::{self.module}::{{{', '.join(items)}}};"]
        if self.kwargs_struct == "TimePeriodKwargs":
            uses.append("use talib::common::TimePeriodKwargs;")
        return uses

    # ----- python ----------------------------------------------------------
    def _py_default(self, default, ty) -> str:
        return repr(float(default)) if ty == "f64" else repr(int(default))

    def _py_input_default(self, name: str) -> str:
        col = "close" if name.startswith("real") else name
        if name == "real1":
            col = "low"
        if name == "real0":
            col = "high"
        return f'pl.col("{col}")'

    def _doc_body(self, indent: str) -> str:
        lines = [f"{indent}Inputs:"]
        if len(self.inputs) == 1 and self.inputs[0] == "real":
            lines.append(f"{indent}    real")
        else:
            lines.append(f"{indent}    prices: {self.inputs}")
        if self.params:
            lines.append(f"{indent}Parameters:")
            for n, ty, d in self.params:
                lines.append(f"{indent}    {n}: {self._py_default(d, ty)}")
        lines.append(f"{indent}Outputs:")
        lines.append(f"{indent}    " + ", ".join(n for n, _ in self.outputs))
        return "\n".join(lines)

    def python_method(self) -> str:
        others = self.args[1:]
        sig = ["self"] + [f"{a}: IntoExpr = {self._py_input_default(a)}" for a in others]
        sig += [f"{n}: {'float' if ty == 'f64' else 'int'} = {self._py_default(d, ty)}" for n, ty, d in self.params]
        example_args = [f'pl.col("{a}")' for a in others] + [f"{n}={self._py_default(d, ty)}" for n, ty, d in self.params]
        lines = [f"    def {self.py}(", *[f"        {s}," for s in sig], "    ) -> pl.Expr:"]
        lines.append(f'        """{self.display} ({self.group})')
        lines.append(f'        pl.col("{self._py_input_default(self.primary)[8:-2]}").ta.{self.py}({", ".join(example_args)})')
        lines.append("")
        lines.append(self._doc_body("        "))
        lines.append('        """')
        lines.append("        return register_plugin(")
        lines.append("            args=[" + ", ".join(["self._expr"] + others) + "],")
        lines.append("            lib=lib,")
        if self.params:
            lines.append("            kwargs={")
            for n, _, _ in self.params:
                lines.append(f'                "{n}": {n},')
            lines.append("            },")
        lines.append(f'            symbol="{self.py}",')
        lines.append("            is_elementwise=False,")
        lines.append("        )")
        return "\n".join(lines) + "\n"

    def python_function(self) -> str:
        sig = [f"{a}: IntoExpr = {self._py_input_default(a)}" for a in self.inputs]
        sig += [f"{n}: {'float' if ty == 'f64' else 'int'} = {self._py_default(d, ty)}" for n, ty, d in self.params]
        lines = [f"def {self.py}(", *[f"    {s}," for s in sig], ") -> pl.Expr:"]
        lines.append(f'    """{self.display} ({self.group})')
        others = self.args[1:]
        example_args = [f'pl.col("{a}")' for a in others] + [f"{n}={self._py_default(d, ty)}" for n, ty, d in self.params]
        lines.append(f'    pl.col("{self._py_input_default(self.primary)[8:-2]}").ta.{self.py}({", ".join(example_args)})')
        lines.append("")
        lines.append(self._doc_body("    "))
        lines.append('    """')
        call = others + [f"{n}={n}" for n, _, _ in self.params]
        lines.append(f"    return {self.primary}.ta.{self.py}(" + ", ".join(call) + ")")
        return "\n".join(lines) + "\n"


# --------------------------------------------------------------------------
def insert_uses(text: str, uses: list[str]) -> str:
    """Insert missing ``use`` lines after the last top level ``use`` block."""
    lines = text.split("\n")
    last_use = 0
    depth = 0
    for i, line in enumerate(lines):
        if line.startswith("use ") or depth > 0:
            depth += line.count("{") - line.count("}")
            if depth == 0 and line.rstrip().endswith(";"):
                last_use = i + 1
        if line.startswith(("pub fn", "fn ", "#[", "pub struct", "impl")):
            break
    use_block = "\n".join(lines[:last_use])
    missing = []
    for u in uses:
        ident = re.findall(r"[A-Za-z_][A-Za-z0-9_]*", u.split("::")[-1])
        needle = ident[0]
        if not re.search(rf"\b{re.escape(needle)}\b", use_block) and u not in missing:
            missing.append(u)
            use_block += "\n" + u
    return "\n".join(lines[:last_use] + missing + lines[last_use:])


def ensure_helper_uses(text: str, module_uses: list[str]) -> str:
    return insert_uses(text, module_uses)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--header", type=Path, default=ROOT / "dependencies/include/ta-lib/ta_func.h")
    ap.add_argument("--meta", type=Path, help="json produced from the python ta-lib package (optional)")
    ap.add_argument("--groups", type=Path, help="json of talib.get_function_groups() (with --meta)")
    ap.add_argument("--only", nargs="*", help="restrict to these TA function names (upper case)")
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    protos = parse_prototypes(args.header)
    meta = load_meta(args.meta, args.groups)
    groups = meta.pop("__groups__")

    init_py = (ROOT / "python/polars_talib/__init__.py").read_text()
    existing = set(re.findall(r"^    def ([a-z0-9_]+)\(", init_py, re.M))
    names = [n for n in groups_flat(groups) if n.lower() not in existing]
    if args.only:
        names = [n for n in names if n in args.only]
    specs = [Spec(n, protos[n], meta[n]) for n in names]
    if specs:
        print("generating:", " ".join(s.c_name for s in specs), file=sys.stderr)
    else:
        print("no missing functions; refreshing groups and test lists only", file=sys.stderr)

    by_module: dict[str, list[Spec]] = {}
    for s in specs:
        by_module.setdefault(s.module, []).append(s)

    out_chunks = {}
    for module, ss in by_module.items():
        wrapper_path = ROOT / "talib/src" / f"{module}.rs"
        expr_path = ROOT / "src" / f"{module}.rs"
        wrapper_text = wrapper_path.read_text()
        expr_text = expr_path.read_text()
        helper_uses = [
            "use crate::utils::cannot_produce_output;",
            "use crate::utils::make_default_vec;",
            "use crate::utils::make_vec;",
        ]
        for n in sorted({len(s.inputs) for s in ss}):
            helper_uses.append(f"use crate::utils::check_begin_idx{n};")
        if any(s.custom_kwargs for s in ss):
            helper_uses += ["use derive_builder::Builder;", "use serde::Deserialize;"]
        if any(p[1] == "TA_MAType" for s in ss for p in s.params):
            helper_uses.append("use talib_sys::TA_MAType;")
        if any(s.kwargs_struct == "TimePeriodKwargs" for s in ss):
            helper_uses.append("use crate::common::TimePeriodKwargs;")
        helper_uses.append("use talib_sys::{TA_Integer, TA_RetCode};")
        wrapper_uses = helper_uses + [u for s in ss for u in s.rust_wrapper_uses()]
        wrapper_new = insert_uses(wrapper_text, wrapper_uses).rstrip("\n") + "\n\n" + "\n".join(s.rust_wrapper() for s in ss)
        expr_uses = [u for s in ss for u in s.polars_expr_uses()]
        expr_new = insert_uses(expr_text, expr_uses).rstrip("\n") + "\n\n" + "\n".join(s.polars_expr() for s in ss)
        out_chunks[wrapper_path] = wrapper_new
        out_chunks[expr_path] = expr_new

    # python ---------------------------------------------------------------
    init_new = init_py
    if specs:
        methods = "\n".join(s.python_method() for s in specs)
        functions = "\n\n".join(s.python_function() for s in specs)
        marker = "\n\ndef ht_dcperiod("
        assert marker in init_py
        init_new = init_py.replace(marker, "\n" + methods + marker, 1).rstrip("\n") + "\n\n\n" + functions

    groups_src = "__function_groups__ = {\n"
    for g, fns in groups.items():
        groups_src += f'    "{g}": [\n' + "".join(f'        "{f.lower()}",\n' for f in fns) + "    ],\n"
    groups_src += "}\n"
    init_new = re.sub(r"__function_groups__ = \{.*?\n\}\n", groups_src, init_new, count=1, flags=re.S)

    struct_map = {n.lower(): m["output_names"] for n, m in meta.items() if len(m["output_names"]) > 1}
    struct_src = "    return {\n" + "".join(f'        "{k}": {v},\n' for k, v in struct_map.items()) + "    }\n"
    init_new = re.sub(
        r"(def get_functions_output_struct\(\):\n    \"\"\".*?\"\"\"\n)    return \{.*?\n    \}\n",
        lambda m: m.group(1) + struct_src,
        init_new,
        count=1,
        flags=re.S,
    )
    out_chunks[ROOT / "python/polars_talib/__init__.py"] = init_new

    # tests ----------------------------------------------------------------
    test_lists = {
        "momentum": "Momentum Indicators",
        "overlap": "Overlap Studies",
        "statistic": "Statistic Functions",
        "price_transform": "Price Transform",
        "volatility": "Volatility Indicators",
        "volume": "Volume Indicators",
        "math_operators": "Math Operators",
    }
    for test_file in ("tests/test_ta.py", "tests/test_nan.py"):
        text = (ROOT / test_file).read_text()
        for key, group in test_lists.items():
            fn_name = f"test_abstract_{key}_eq"
            m = re.search(
                r"@pytest\.mark\.parametrize\(\s*\"func\",\s*(\[[^\]]*\]),?\s*\)\s*\ndef " + fn_name,
                text,
                re.S,
            )
            if not m:
                continue
            current = re.findall(r'"([a-z0-9_]+)"', m.group(1))
            wanted = [f.lower() for f in groups[group]]
            if key == "math_operators":
                wanted = [f for f in wanted if f in current or f in {s.py for s in specs}]
            if set(current) == set(wanted):
                continue
            merged = current + [f for f in wanted if f not in current]
            new_list = "[\n" + "".join(f'        "{f}",\n' for f in merged) + "    ]"
            text = text[: m.start(1)] + new_list + text[m.end(1):]
        out_chunks[ROOT / test_file] = text

    if args.apply:
        for path, content in out_chunks.items():
            path.write_text(content)
            print("wrote", path.relative_to(ROOT), file=sys.stderr)
    else:
        for path, content in out_chunks.items():
            print(f"##### {path.relative_to(ROOT)}\n{content}")
    return 0


def groups_flat(groups: dict) -> list[str]:
    return [f for fns in groups.values() for f in fns]


if __name__ == "__main__":
    sys.exit(main())
