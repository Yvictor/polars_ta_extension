# Ordinary `.over()` dispatch and Arrow memory

The shipped expression remains `ta.rsi(...).over(...)` (and the existing `.ta`
namespace). No new grouping expression, automatic list wrapper, method override,
or private ABI shortcut is included. This report separates source-derived memory
costs from timings; the CI release comparison measures the complete query.

## Existing execution and ownership

The original C-backed adapter already borrowed contiguous, non-null Float64
values after cast/rechunk. This migration retains that path using safe slices
instead of C input pointers. It does **not** introduce a new zero-copy input
optimization. See the [fixed original adapter](https://github.com/Yvictor/polars_ta_extension/blob/b2bbc26d41ec80823c8bffb0cc436a97f29911cc/src/utils.rs)
and current [native adapter](../src/native.rs).

An Arrow ListArray consists of an offsets buffer, child array and optional
validity bitmap. It is not a Python list. Whether it shares or copies child
values depends on its construction; the word Arrow does not establish zero-copy.

For the inspected Polars **1.44.2** numeric, non-overlapping, groupwise path:

| Stage | Contiguous group positions | Interleaved group positions |
| --- | --- | --- |
| Engine grouping | Computes/caches groups, possibly slice positions | Computes/caches row-index positions |
| Numeric `agg_list` | Rechunks input, allocates offsets and a values vector, copies each slice with `extend_from_slice` | Rechunks input, allocates offsets and a values vector, gathers by row indices |
| Iterating grouped child values | Group Series can view a child-buffer range; callback is still per group | Group Series can view the already gathered child-buffer range |
| Plugin import and kernel | Borrow the received contiguous Float64 values; casts/rechunk/null-to-NaN can allocate | Same; original row indices are no longer available at this boundary |
| Kernel output | New initialized output buffer per output/group; padding and optional null bitmap | Same |
| Window result mapping | Engine can use ordered/explode fast paths where applicable | Engine may allocate inverse mapping and `take` values back to row order |

Source: [groupwise apply](https://github.com/pola-rs/polars/blob/py-1.44.2/crates/polars-expr/src/expressions/apply.rs#L117),
[aggregation context](https://github.com/pola-rs/polars/blob/py-1.44.2/crates/polars-expr/src/expressions/mod.rs#L451),
[numeric Arrow-list construction](https://github.com/pola-rs/polars/blob/py-1.44.2/crates/polars-core/src/frame/group_by/aggregations/agg_list.rs#L14),
[window mapping](https://github.com/pola-rs/polars/blob/py-1.44.2/crates/polars-expr/src/expressions/window.rs#L125).
These are specific source paths, not a claim that every window uses the same
materialization. Multiple-input, sorted, overlapping and aggregated inputs have
additional execution choices. In particular, [overlapping groups](https://github.com/pola-rs/polars/blob/py-1.44.2/crates/polars-expr/src/expressions/group_iter.rs#L80)
can be sliced lazily instead of greedily materializing every overlapping list.

For one Float64 aggregation of N rows into G disjoint groups, the new values
vector accounts for about `8*N` bytes and LargeList offsets about `8*(G+1)`;
nullable input also needs validity. At 1M rows / 10k groups this is roughly
8 MB plus 80 KB, before output, indices, other inputs or rechunking. This is
source-derived buffer accounting, **not measured peak RSS**. Group caches and
expression reuse affect total allocations, so multiplying this by every
expression is not a measured query-memory estimate.

Inside this repository, `Series` clones share existing buffers. Single-chunk
Float64 inputs with no nulls are borrowed; Float32/integer casts, multi-chunk
rechunking, scalar broadcast and null-to-NaN conversion can own new storage.
Null-output masking clones the value array and applies a validity bitmap. The
kernel still allocates its outputs. None of this removes copies already made
by host grouping before the callback.

The [FFI export](https://github.com/pola-rs/polars/blob/py-1.44.2/crates/polars-ffi/src/version_0.rs#L4)
allocates wrapper/schema metadata and clones Arrow array handles; numeric value
buffers can stay shared and release callbacks retain their owners. Repeated
group callbacks therefore have metadata/kwargs costs even when values are
borrowed. `SeriesExport.len` counts **chunks**, not groups; chunk boundaries must
never be interpreted as partition boundaries.

## Supported ABI boundary

The [version-0 callback](https://github.com/pola-rs/polars/blob/py-1.44.2/crates/polars-plan/src/plans/aexpr/function_expr/plugin.rs)
receives exported input Series, kwargs, a return slot and CallerContext. It does
not receive all source columns, group positions, keys or query identity. The
[plugin's frozen CallerContext](https://docs.rs/polars-ffi/0.36.2/src/polars_ffi/version_0.rs.html)
contains a parallelism flag. Marking an ordinary recursive indicator
`is_elementwise=True` would violate the registration contract and lose partition
state. A TA-Lib dispatcher beneath an already-per-group callback cannot recover
the other groups or undo host materialization.

Newer Polars has an internal groups-aware UDF interface, but the inspected
[`function_expr_to_groups_udf` dispatch](https://github.com/pola-rs/polars/blob/py-1.44.2/crates/polars-expr/src/dispatch/mod.rs#L544)
has no FFI-plugin branch (the [ordinary FFI branch](https://github.com/pola-rs/polars/blob/py-1.44.2/crates/polars-expr/src/dispatch/mod.rs#L440)
uses the Series callback). This is an engine
capability boundary, not a reason to reinterpret private Rust layouts or foreign
pointers. Changing the TA-Lib kernel alone cannot expose group positions.

## Bounded composition experiment and its limits

A diagnostic tried `implode -> elementwise List-to-List callback -> explode`
under ordinary `.over()`, with an outer Struct marker to preserve genuine null
outputs while dropping empty-list phantom rows. It can batch group lists on
Polars 1.44/2.0 and mainly removes repeated callback/kwargs overhead. It does
**not** inherently remove the gathered child buffer, offsets, output buffers,
rechunking or result mapping. No allocation or speed improvement was established
for this experiment.

It is not shipped because:

- Polars 1.20 rejects this `implode` + aggregation + window composition before
  the callback. The supported original expressions execute successfully.
  [Planner restriction](https://github.com/pola-rs/polars/blob/py-1.20.0/crates/polars-expr/src/planner.rs#L479).
- Literal and aggregate-scalar expressions expose different shape/broadcast
  behavior. A bare-column guard alone cannot determine the enclosing execution
  context; the same expression can later appear in windows, rolling aggregation,
  nested aggregation or a direct query.
- Eagerly packaging overlapping groups can duplicate observations many times,
  bypassing the existing lazy-slice execution choice. A blanket rewrite would
  need additional semantic and memory validation.

The [nonproduction host probe](../scripts/probe_over_batching.py) imports only
Polars and isolates planner/callback behavior; it is not a native-kernel memory
or performance benchmark. Recorded [1.20](over-dispatch-probe/polars-1.20.0.json),
[1.44](over-dispatch-probe/polars-1.44.2.json) and
[2.0](over-dispatch-probe/polars-2.0.0.json) results show the failures as well as
successes. The temporary native prototype passed the then-current 5,717-test
suite on 1.44/2.0 but failed 1,084 tests on 1.20; it was removed, not silently
enabled only on selected versions. These findings do not prove transparent
batching is mathematically impossible. They show that this rewrite is not a
validated universal replacement within the migration's compatibility contract.

## Concrete future native design

A supported, versioned **groups-aware FFI capability**, selected by the engine
under the existing `.over()` expression, is the preferred design to investigate:

1. Host Polars evaluates arguments and retains its existing group positions,
   `order_by`, scalar-broadcast and mapping semantics. The plugin advertises an
   optional grouped callback; old hosts/plugins retain the current callback.
2. The callback receives owned-lifetime Arrow column exports plus checked group
   slices or index buffers, rather than reconstructed keys or copied list values.
   These must be versioned ABI structures with explicit index width, lengths,
   ownership/release and overlap/order semantics, not Rust `GroupPositions` casts.
   Per-input layout tags must distinguish whole-column, scalar and per-group
   scalar values so broadcasting remains an engine decision.
3. Contiguous single-chunk Float64 partitions can borrow `values[start..end]`.
   TA-Lib's current batch kernels require contiguous slices, so interleaved groups
   still need a gather (prefer reusable worker scratch). Eliminating that gather
   would require indexed kernels or an earlier physical layout change.
4. Bind immutable parameters once per grouped call, run independent groups under
   an explicit host thread budget, and return output plus group layout. Host
   Polars retains validation and mapping; contiguous ordered outputs can avoid
   an unnecessary inverse scatter. Output arrays and validity still have costs.
5. Test scalar/derived inputs, every window mapping mode, nulls, ordering,
   overlapping/dynamic groups, cancellation/concurrency and all supported hosts.
   Compare complete queries, allocation counts and peak memory in same-runner CI.

This would require Polars engine/ABI work for the group-position route. A newer-
host list composition is an alternative research path, not inherently required
or inherently efficient. The migration keeps the safe local improvements
(initialized output padding and reviewed compatibility scans) that already apply
within normal `.over()` callbacks. No Polars upstream communication is included in this dispatch investigation.

## Upstream draft since the original investigation

TA-Lib's [Arrow API RFC](https://github.com/TA-Lib/ta-lib/blob/3394ffa4750b0bd56842f66393aeca9763d5ef0b/docs/RFC-Arrow-API.md)
proposes borrowed partition offsets, validity buffers and a segmented Rust facade.
It is a draft, not a released capability. It could supply the kernel-side piece
of a future grouped interface; ordinary Polars plugin callbacks still lack the
whole-query group positions. Its default gap restart and nonfinite-to-null rules
also differ from this package's preserved behavior. Adoption would require
explicit compatibility modes and host ABI support, not a transparent substitution
of those defaults in the existing expressions.
