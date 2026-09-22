"""Exercise the installed skill examples and benchmark reporting failure modes."""

import ast
import json
import re
import subprocess
import sys
from pathlib import Path

import polars as pl
import polars_talib as ta
import pytest

from test_complete_api import frame

ROOT = Path(__file__).resolve().parents[1]


def test_skill_reference_examples_execute(tmp_path, monkeypatch):
    df = frame(160).with_columns(
        pl.lit("A").alias("symbol"),
        pl.int_range(pl.len()).alias("date"),
        pl.col("close").alias("adj_close"),
        pl.col("close").alias("stock_ret"),
        pl.col("open").alias("index_ret"),
        pl.col("high").alias("a"),
        pl.col("low").alias("b"),
    )
    df.write_parquet(tmp_path / "prices.parquet")
    monkeypatch.chdir(tmp_path)
    namespace = {"df": df, "pl": pl, "ta": ta}
    text = (ROOT / "plugins/polars-talib/skills/polars-talib/reference/patterns.md").read_text()
    for block in re.findall(r"```python\n(.*?)```", text, re.S):
        for node in ast.parse(block).body:
            if isinstance(node, ast.Expr):
                result = eval(compile(ast.Expression(node.value), "<skill>", "eval"), namespace)
                if isinstance(result, pl.Expr):
                    assert df.select(result).height == df.height
                elif isinstance(result, pl.DataFrame):
                    assert result.height == df.height
            else:
                exec(
                    compile(ast.Module(body=[node], type_ignores=[]), "<skill>", "exec"), namespace
                )
    assert namespace["signals"].filter(pl.col("date") < 50).is_empty()


@pytest.mark.parametrize("report_only", [False, True])
def test_benchmark_timing_warning_preserves_report(tmp_path, report_only):
    metadata = dict(
        python="3.12",
        platform="test",
        cpu_model="test",
        numpy="2.5",
        polars="1.44",
        threads=4,
        affinity=[0, 1, 2, 3],
        repeats=51,
    )
    baseline = {**metadata, "results": {"rsi/100000": {"median_ms": 1.0}}}
    candidate = {**metadata, "results": {"rsi/100000": {"median_ms": 2.0}}}
    before, after = tmp_path / "before.json", tmp_path / "after.json"
    before.write_text(json.dumps(baseline))
    after.write_text(json.dumps(candidate))
    output = tmp_path / "comparison.md"
    args = [
        sys.executable,
        str(ROOT / "scripts/compare_benchmarks.py"),
        str(before),
        str(after),
        "--output",
        str(output),
    ]
    if report_only:
        args.append("--report-only")
    result = subprocess.run(args, capture_output=True, text=True)
    assert (result.returncode == 0) == report_only
    assert "0.50x" in output.read_text()
    if report_only:
        assert "::warning::" in result.stdout
    candidate["polars"] = "incompatible"
    after.write_text(json.dumps(candidate))
    result = subprocess.run(args, capture_output=True, text=True)
    assert result.returncode != 0
    assert "incomparable polars" in result.stderr


def test_skill_function_reference_matches_the_installed_api():
    defaults = {"real": "close", "real0": "high", "real1": "low"}
    api = {f["name"]: f for f in json.loads((ROOT / "scripts/api.json").read_text())}
    df = frame(128)
    seen = set()
    for row in (ROOT / "plugins/polars-talib/skills/polars-talib/reference/functions.md").read_text().splitlines():
        if not row.startswith("| `"):
            continue
        name, _, receiver, others, _, outputs = [cell.strip() for cell in row.strip("|").split("|")]
        name = name.strip("`")
        seen.add(name)
        args = [] if others == "-" else [pl.col(defaults.get(i, i)) for i in others.split(", ")]
        actual = df.select(getattr(pl.col(receiver).ta, name)(*args).alias("result"))
        expected = df.select(
            getattr(ta, name)(*[pl.col(defaults.get(i, i)) for i in api[name]["inputs"]]).alias(
                "result"
            )
        )
        assert actual.equals(expected), name
        if isinstance(actual.to_series().dtype, pl.Struct):
            assert actual.to_series().struct.fields == outputs.split(", "), name
    assert seen == set(ta.get_functions())
