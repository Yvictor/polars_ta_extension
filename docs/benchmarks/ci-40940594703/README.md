> Scope update from later coverage: these component fixtures are not universal signed-zero equivalence evidence. A separate scalar-high-zero case exposes the official C0.8.1→C0.8.3 change from `0 - sar` to `-sar`; the existing native56 shares C0.8.3 behavior. The adapter compatibility correction is a separate candidate. These numbers measure the pinned56 implementation only.

# SAREXT: independent CI component diagnostic audit

Run https://github.com/Yvictor/polars_ta_extension/actions/runs/40940594703 SUCCESS; controller `6684b3e6baa3d1c27067e97eb028bb49c4fef748`. Original C `b2bbc26d41ec80823c8bffb0cc436a97f29911cc`; native control `56f6d5fb139031c20d86d7e818e7d267eb834295`.

Artifact [12927142990](https://github.com/Yvictor/polars_ta_extension/actions/runs/40940594703/artifacts/12927142990), 129,038,001 bytes, official digest `sha256:bde03c9bc8e695ec57a73da62636423d0bbf33899bc3ba56550e0b0b7e41fa97`. Root sole download verified2,900 extracted files. Independent replay PASS:50 cells,50 retained correctness captures,50 separate counter children,600 fresh timing children,18,600 samples,57 comparisons,all12 balanced rounds.

{"CFLAGS": "", "CXXFLAGS": "", "cpu": "AMD EPYC 7763 64-Core Processor", "machine": "x86_64", "platform": "Linux-7.0.0-1017-azure-x86_64-with-glibc2.39", "python": "3.12.15 (main, Oct  1 2026, 02:35:59) [GCC 13.3.0]"}

Product Rust1.90 portable O3/16codegen units/Cargo lto=false/empty flags; standalone probe explicitly -Clto=off. Product/local ThinLTO behavior differs from probe; source/rlib/ELF identity is not proof of machine-code equivalence. No stage subtraction or Polars throughput inference. The benchmark does not execute .over(): native_full means native::compute with predecoded Params, excluding pickle, missing.apply, plugin/Python/Polars execution.

## Independent review and correction

17 independent auditor fixtures passed; source reviewed separately. Actual Cargo raw16hex little-endian fingerprints and parent dependency edges were reconstructed, bridged to linked rlib suffix/hash and full primary/counter commands.42 immutable source overlays/exact wrapper and15 input/pickle hashes passed. Original frozen trust used string ordering for the source fingerprint, whereas the pinned producer uses Path ordering. First raw replay stopped before timings. A separate reviewed correction independently rederived the same44 C/51 native Git files, preserving every file hash; only two fingerprint fields changed, with explicit disclosure. Original trust, failed log, ordered inventories and corrected trust remain in this bundle. No numerical tolerance/content waiver.

## Kernel and adapter modes

Median ns per selected call;12 fresh-process medians per cell. All process ranges and raw vectors are retained in all50-cells.csv.

|Fixture / rows|C preallocated|Rust typed|Rust abstract|Native compute|Typed vs C|C/typed envelope|
|---|---:|---:|---:|---:|---:|---|
|default/100|194.080|244.986|1211.941|1633.474|+26.229%|C/typed 0.78185–1.67750|
|default/1000|1916.160|2388.595|3370.245|3995.220|+24.655%|C/typed 0.79456–0.80449|
|default/10000|19594.950|24964.500|25943.300|28919.950|+27.403%|C/typed 0.76125–0.81484|
|default/1000000|8734261.500|9605677.500|9607525.000|13465829.500|+9.977%|C/typed 0.90214–0.91052|
|reversal/100|211.433|238.955|1203.586|1612.906|+13.017%|C/typed 0.87299–0.89398|
|reversal/1000|1864.560|1999.120|2953.460|3547.825|+7.217%|C/typed 0.92191–0.94091|
|reversal/10000|18763.300|19723.100|20576.750|23004.800|+5.115%|C/typed 0.94642–0.97240|
|reversal/1000000|1912746.000|1976706.000|1980953.500|5748008.500|+3.344%|C/typed 0.89907–0.97582|

All8 typed medians exceed C;7 have disjoint slower envelopes. Default100 has a C first-process outlier409.931ns (remaining processes roughly193–195ns), so its+26.229% median gap has an overlapping full envelope and is not treated as a disjoint result. All negative component comparisons are retained; comparing more inclusive stages is diagnostic, not an implementation regression claim.

## Decode, setup and allocation requests

|Fixture / mode pair|Before ns|After ns|After change|Envelope before/after|Separate counter requests / cumulative bytes|
|---|---:|---:|---:|---|---|
|default decode_old→decode_current|4111.374|4696.962|+14.243%|0.82677–0.90837|32/24110 → 33/24566|
|reversal decode_old→decode_current|4099.358|4681.263|+14.195%|0.85233–0.88904|32/24110 → 33/24566|
|add decode_old→decode_current|1406.614|1407.081|+0.033%|0.94077–1.03245|11/17626 → 11/17626|
|default setup_c→setup_current|14.818|945.525|+6280.770%|0.01479–0.01573|0/0 → 0/0|
|reversal setup_c→setup_current|14.819|945.670|+6281.516%|0.01523–0.01593|0/0 → 0/0|

Actual original typed SAREXT kwargs vs current map decode is+14.243%/+14.195% for default/reversal,12/12 slower,disjoint;ADD empty kwargs control is+0.033%,overlap. Current decode adds one counted request/456 cumulative requested bytes, not eight new string allocations. Both SAREXT decode paths record11 realloc requests;ADD both2. Per-call new holder/bind/lookback has zero counted Rust requests but roughly945ns, so allocation count alone does not establish its cause. Typed/abstract/kernel/setup modes measure different complete selected drivers and are not exclusive additive costs.

## Safe initialization opportunity control

|Rows|Full NaN ns|Reserve+prefix ns|Requested bytes each|
|---:|---:|---:|---:|
|100|33.338|21.431|800|
|1000|191.160|38.570|8000|
|10000|1957.700|385.200|80000|
|1000000|3649737.500|5726.000|8000000|

Prefix control initializes only one element, reads only initialized memory and never calls a kernel. It is not a valid replacement for a full output Vec and does not justify unsafe output. Both modes request the same allocation capacity; measured differences do not isolate the allocator. Full native_compute records6 Rust requests/1128B at100 rows and6/8000328B at1m;preallocated C/typed/abstract drivers record0 Rust requests. Cmalloc is not instrumented.

## Correctness and nonfinite contract

100 C/Core range comparisons,20 Core→full raw-exact comparisons,68 invalid/undersized no-write assertions,48 C/Core nonfinite-option BadParam/no-write cases pass. All50 pre-timing stage captures match their comparable stage goldens exactly; timed finite kernel outputs pass their retained golden checks, including integer range metadata,canonical prefix and raw physical canary tails where present. The appended full-Series tail is virtual and is not proof of spare output bytes.

327 NaN sign-only bit differences across9 of100 input/range rows are explicitly retained in all327-NaN-bit-differences.csv. All differ only by the sign bit; NaN positions match and every non-NaN bit, including signed zero/infinity, is exact under the declared written-prefix policy. Both physical unwritten tails remain raw-canary exact. NaN sign/payload is not claimed compatible. All48 nonfinite option observations return C BadParam2,beg=count0 and72 untouched raw canaries, matching Core.

## Limits

- Product Cargo lto=false may use default local ThinLTO; standalone probe explicitly -Clto=off. Source/library identities are not proof of machine-code equivalence.
- Full diagnostic excludes pickle, missing.apply, plugin ABI, Python and Polars query/over. Never subtract stages as exclusive/additive costs.
- Separate counter binary counts Rust requests/cumulative bytes/zeroed/realloc, not C malloc/live/RSS; faults whole-child.
- Synthetic prefix initialization changes initialized length and never runs a kernel; no equivalent output or unsafe optimization inference.
- Extrema process envelopes are descriptive, not confidence intervals.
- Counter and timing duplicate captures deleted after driver hash checks; independent raw replay checks all50 retained pretime captures, not deleted bytes. IEEE/error no-write checks are source-audited assertions plus retained logs, not all raw input/output matrices.
- 12 round extrema and pooled inner-sample quantiles are descriptive, not confidence intervals. Shared runner contention, frequency and placement remain possible.
- Validation/golden reads may warm allocator/cache; counters use a separate cfg-only binary and fresh children. Counter histories never precede timed calls in the same process.
- This identifies candidate adapter decode/setup/kernel areas. Any retained optimization still requires exact correctness and same-runner ordinary native .over comparisons, using final code.
