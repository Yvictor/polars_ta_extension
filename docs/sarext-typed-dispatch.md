# Typed SAREXT and legacy signed zero

The [same-runner component diagnostic](https://github.com/Yvictor/polars_ta_extension/actions/runs/40940594703) found two actionable costs: actual original typed SAREXT kwargs decoded in 4.111 µs versus 4.697 µs for the current map (+14.24%, all12 pairs slower with disjoint process ranges), and current holder creation/eight binds/lookback took 945.525 ns with zero counted Rust allocations. Those isolated stages exclude Polars `.over()` and cannot be subtracted as exclusive costs. The map adds one counted request/456 requested bytes; it does not add eight new string allocations.

Only SAREXT's generated plugin entry changes to `Masked<SarExtParams>`. The fixed eight-field decoder reuses the numeric `Param` rules, consumes unknown values before ignoring their keys, preserves duplicate-key/error behavior, and never builds a `BTreeMap`. Defaults are exactly `0,0,.02,.02,.2,.02,.02,.2`, including integer conversion and `REAL_DEFAULT` handling. Python names/signatures, all201 plugin symbols, missing-data flags and native Polars `.over()` remain unchanged.

Small shared helpers retain the original input-count/metadata checks, broadcast/cast/null-fill/rechunk ownership, borrowed slices and length limit. They return owners before borrowing slices; there is no self-referential structure or unsafe code. Both routes validate parameters after preparation and before first-usable-row/output work. Generic kernels retain their existing calls. SAREXT uses the official public typed lookback and kernel API, with the existing full initialized-NaN output, range checks, output padding and null-mask wrapper. Borrowed Arrow inputs predate this optimization.

## The newly tested signed-zero boundary

New coverage found an inherited version difference: original C0.8.1 writes `0 - sar` at two short-side stores, whereas official C/Rust0.8.3 writes `-sar`. For positive-zero `sar`, these return +0 and -0 respectively. This is a C0.8.1→0.8.3 boundary, not a Rust-specific upstream bug. Short zeros can arise through cancellation even when every input price is nonzero. Long-side -0 is legitimate and must be preserved.

Candidate A first runs the official typed kernel, then reduces only the written output bits for negative zero. On a hit, it replays a licensed scalar compatibility copy into the same initialized buffer and requires the same `OutRange`. The copy changes exactly those two stores to `0.0 - sar`; it does not normalize arbitrary output zeros or test only zero inputs. For non-NaN values, subtraction and negation differ only when `sar` is +0, whose official output is -0, so the scan covers this operator difference. NaN positions remain part of the contract; NaN sign/payload does not.

[The provenance manifest](../scripts/sarext_legacy_provenance.json) pins the0.8.3 crate checksum, official commit and complete source hashes. A regression test checks all1,409 scalar tokens after reversing only declared plumbing/formatting and the two stores. The original BSD notice is retained. The common path keeps official runtime FMA dispatch; the safe replay copy may call libm FMA on portable x86 targets. Scanning costs a pass, and legitimate long -0 can cause a redundant full replay. These are performance questions for CI, not assumed wins.

## Completed correctness gates

On the authorized arm64 Mac, Rust1.90 release, Python3.12.14 and NumPy2.5.3:

- 32 Rust tests passed; one existing cost diagnostic remained ignored. New gates cover765 real pickle fixtures (protocols0–5), exact map-compatible errors/defaults,65,546 IEEE operator cases, typed/generic error ordering, ranges and physical no-write/tail canaries.
- All11,748 public tests passed separately on Polars1.20.0,1.44.2 and2.1.0. The171 new scenarios include4,096 three-bar signed-zero/integer OHLC states, scalar literals, all integer widths, defaults/nondefaults/sentinels, chunking, ordered/interleaved native windows and missing/IEEE inputs. The original C package independently passes all4,096 states too.
- The external real-option suite passed32 tests/3,780 cases on each version, covering27 real options across17 functions, including all SAREXT fields.
- The existing10,624-case/2,167,654-value capture remains byte-identical to same-Mac56 (NPZ SHA256 `67a4bfcee152899b8a7058c2e3958264796453641c0118f85450b9dbeb88b41e`) and passes the existing original-C tolerance policy. This existing corpus did not contain the newly found zero boundary. Separate three-arm raw captures show the intended56 -0→C/candidate +0 corrections and unchanged legitimate long -0.

No local performance timings were collected. Retention requires controlled final-code CI comparisons against original C and56, including short/long native groups, interleaving, one/four threads, unchanged controls and replay stress. The shared preparation extraction also requires broad final integration checks; unchanged performance of other functions is not assumed.
