"""Nonproduction probe: List-valued elementwise composition under ordinary over().

Run with a chosen environment's Python. No polars-talib plugin is imported:
this isolates host aggregation/planning behavior, not the native Arrow bridge.
"""
from __future__ import annotations

import inspect
import json
import warnings

import polars as pl
from polars.testing import assert_frame_equal


def main():
    warnings.simplefilter("ignore", DeprecationWarning)
    result_type = pl.List(pl.Struct({"out": pl.Float64, "present": pl.Boolean}))
    calls = []

    def batch(values):
        calls.append({"dtype": str(values.dtype), "list_rows": len(values)})
        # Each List row is one complete, independent partition. A real plugin
        # would invoke the existing indicator and null-mask logic on that row.
        rows = [
            [{"out": value, "present": True} for value in xs.cum_sum()]
            for xs in values
        ]
        return pl.Series("r", rows, dtype=result_type)

    def expression(argument=None):
        argument = pl.col("x") if argument is None else argument
        packed = argument.cast(pl.Float64).implode()
        output = packed.map_batches(
            batch, return_dtype=result_type, is_elementwise=True
        )
        # Older hosts explode an empty List into a null row. Remove that outer
        # Struct null, while retaining real rows whose numeric output is null.
        # The always-true marker ensures real Structs cannot be all-null.
        return output.explode().drop_nulls().struct.field("out").alias("r")

    expected = pl.col("x").cast(pl.Float64).cum_sum().alias("r")
    data = pl.DataFrame({
        "g": ["b", "a", "b", "a", None, None],
        "x": [10.0, 1.0, 20.0, None, 30.0, 3.0],
        "row": [2, 2, 1, 1, 0, 0],
    })
    outcomes = []

    def check(name, actual, reference):
        calls.clear()
        try:
            got = actual()
            assert_frame_equal(got, reference(), check_exact=True)
            outcomes.append({"case": name, "status": "pass", "calls": calls.copy()})
        except Exception as error:
            outcomes.append({
                "case": name,
                "status": "error",
                "error": type(error).__name__,
                "message": str(error).splitlines()[0],
                "calls": calls.copy(),
            })

    for layout, frame in [
        ("interleaved_nullable", data),
        ("empty", data.head(0)),
        ("one_group", data.with_columns(pl.lit(1).alias("g"))),
        ("chunked", pl.concat([data[:3], data[3:]], rechunk=False)),
    ]:
        check(layout + "/direct", lambda: frame.select(expression()),
              lambda: frame.select(expected))
        for mode in ["group_to_rows", "join", "explode"]:
            check(layout + "/over/" + mode,
                  lambda: frame.select(expression().over("g", mapping_strategy=mode)),
                  lambda: frame.select(expected.over("g", mapping_strategy=mode)))
        check(layout + "/group_by_agg",
              lambda: frame.group_by("g", maintain_order=True).agg(expression()),
              lambda: frame.group_by("g", maintain_order=True).agg(expected))

    if "order_by" in inspect.signature(pl.Expr.over).parameters:
        check("ordered_over",
              lambda: data.select(expression().over("g", order_by="row")),
              lambda: data.select(expected.over("g", order_by="row")))
    for name, predicate in [("selected", pl.col("x") > 5), ("empty", pl.lit(False))]:
        check("filter_before/" + name,
              lambda: data.lazy().filter(predicate).select(expression()).collect(),
              lambda: data.lazy().filter(predicate).select(expected).collect())
    check("filter_after",
          lambda: data.lazy().select(expression()).filter(pl.col("r") > 5).collect(),
          lambda: data.lazy().select(expected).filter(pl.col("r") > 5).collect())

    # These deliberately expose scalar semantics that a universal rewrite
    # would change; production must retain the original path or solve them.
    for name, argument in [("literal", pl.lit(2.0)),
                           ("aggregate_scalar", pl.len().cast(pl.Float64))]:
        check("scalar/" + name,
              lambda: data.select(expression(argument).over("g")),
              lambda: data.select(argument.cum_sum().alias("r").over("g")))

    return {
        "polars": pl.__version__,
        "bare_column_meta_available": pl.col("x").meta.is_column(),
        "outcomes": outcomes,
        "passed": sum(case["status"] == "pass" for case in outcomes),
        "errors": sum(case["status"] == "error" for case in outcomes),
    }


if __name__ == "__main__":
    print(json.dumps(main(), indent=2))
