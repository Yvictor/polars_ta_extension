# Retain B, with remaining C gaps explicit

Recommendation: retain B (`f7d800398ecd6dc79c5b346e7e151cf917272327`) for final composition. It preserves the newly covered original-C short-zero contract, improves the ten native short-group target medians versus delivered56, and avoids A’s full scalar replay on legitimate long negative zeros. Acceptance remains subject to the final composed consumer head’s full CI; this component result does not establish universal C parity.

Verified CI: https://github.com/Yvictor/polars_ta_extension/actions/runs/40965216581
Raw artifact: https://github.com/Yvictor/polars_ta_extension/actions/runs/40965216581/artifacts/12939942104
Artifact:587,018,936 bytes, SHA256 `2541f53a34e750d723799e80e734714d68b1a95a8e03185cebba9a70e90f583b`;8,297 extracted files.

AMD EPYC9V45/Linux7.0.0-1017-azure/glibc2.39; Python3.12.15, Polars1.44.2, NumPy2.5.3, Rust1.90.0. All four portable release builds share O3/cgu16/LTOfalse and empty native CPU flags, one job/runner. Configured Polars pool/CPU affinity is1/[0] or4/[0,1,2,3]; this does not demonstrate utilization of all four cores. Twelve balanced Williams fresh processes per case/arm/setting,31 samples after5 warmups;1,344 children/41,664 raw samples.

There are20 SAREXT target observations (10 cases ×2 settings), four generic-SAR shared-preparation controls and four pure-Polars drift controls. All168 pairwise rows and28 four-arm median rows are retained. Counts below use disjoint observed process-median envelopes around1, not formal confidence intervals; the original5% assessment labels also remain in the audited result.

| Later B versus | Target rows | Slower medians | Disjoint faster | Disjoint slower | Overlap |
| --- | ---: | ---: | ---: | ---: | ---: |
| original C | 20 | 8 | 1 | 0 | 19 |
| delivered56 | 20 | 7 | 9 | 0 | 11 |
| A typed Core + scan/replay | 20 | 7 | 4 | 0 | 16 |

The ten short-group SAREXT target observations improve versus56 by7.595%–10.477% in median latency; all12 matched rounds are faster in each, with9/10 disjoint observed ranges. The remaining short reversal/interleaved1-thread observation is−9.894% but its range overlaps. All eight SAR/Polars controls overlap for B versus56, C and A. No B-versus56 observed range is disjoint slower among all28 target/control observations.

B’s dense legitimate-long-zero stress is35.460%/35.606% lower latency than A at1/4 threads, with disjoint ranges and12/12 faster rounds. Its short-group stress is4.345%/5.784% lower than A with disjoint ranges. This compares the complete routes, not an exclusive measurement of scanner, allocator or kernel cost.

Eight of20 B target medians remain slower than original C. Their ranges overlap, but repeated paired direction can still be informative: dense ordinary SAREXT is slower in11/12 and12/12 matched rounds. These observations must not be dismissed as proven equivalence or hidden in an overall average. All remaining slower medians are listed below and in the complete CSV.

| Threads | B slower than C case | Latency increase | B faster rounds | C/B envelope |
| ---: | --- | ---: | ---: | --- |
| 1 | sarext/1000000 | +4.449% | 1/12 | 0.90485–1.00740 |
| 1 | grouped_sarext/100x10000 | +3.604% | 4/12 | 0.88600–1.11964 |
| 1 | sarext_reversal/1000000 | +2.863% | 2/12 | 0.90417–1.05582 |
| 4 | sarext/1000000 | +2.954% | 0/12 | 0.92874–1.02707 |
| 4 | grouped_sarext/100x10000 | +2.431% | 3/12 | 0.86235–1.03848 |
| 4 | grouped_sarext/2000x100_interleaved | +0.807% | 6/12 | 0.93999–1.08140 |
| 4 | sarext_reversal/1000000 | +1.504% | 3/12 | 0.89693–1.05272 |
| 4 | grouped_sarext_reversal/100x10000 | +2.344% | 2/12 | 0.88206–1.04555 |

The one disjoint B-versus-C faster target has only a0.055% margin at its lower envelope bound; treat it as a narrow observed result, not broad speedup evidence. Against56, seven B target medians are slower; all seven ranges overlap. All82 slower medians across every pair/target/control, including A regressions, are retained; across all168 rows there are21 disjoint faster and14 disjoint slower ranges.

Correctness replay passed all four10,624-case captures and all six pairwise comparisons,2,167,654 checked values per comparison; existing error classes, shape, dtype, output field order, null/NaN/Inf positions and integer padding were retained. C-versus-each-native has659 differing finite fields within the declared1e−10/tiny-case policy (max absolute2.5067947717616335e−11),0 both-zero sign differences, and3 inherited STOCHRSI zero-versus-tiny cancellation positions. Zero positions therefore are not globally equivalent to C. Native56/A/B finite values, signed zeros and masks are exact in this corpus.

B versus56/A has373 raw NaN sign-only changes:183 in `sarext/infinity` and190 in `sarext/leading_infinity`; every XOR is `8000000000000000`. NaN payload/sign is excluded from the numerical contract, while NaN positions remain strict. There are no additional finite or signed-zero differences. The four separate untimed short-zero fixtures explicitly require C/A/B +0 and document56’s −0 at fixed rows; this is never a timed/full-corpus waiver. Legitimate long-side −0 is checked in every chronological stress group.

Actual normal-wheel ELF replay passed, including exact wheel/installed/retained binary hashes, unique FMA clone/portable-wrapper/resolver roles, exact disassembly symbol/address binding, four inline FMA updates in B’s clone and the portable out-of-line `fma` transfer. The latter resolves through a local compiler_builtins shim; this does not establish that all its execution is software-only. The public resolver’s full feature closure and the fresh exact eight-thread cold-dispatch test passed. No manual unsafe code, global native-CPU flag or private Polars/TA-Lib ABI is used.

The first approved auditor stopped before numerical/timing reads because the producer stores ELF diagnostic paths relative to the workspace. Its original source/log are preserved. A second independent review approved only exact producer-relative or recorded-workspace absolute mapping with arm/area/traversal/symlink checks. Approved replay hash `761c29f8242cebc41a89627ccb7e758b610336ac5fb3c5c4cc9a187ca86b7e33`; frozen trust `726880c2b4ad089767fc56c11563548a5f0fedc0025dbd61ba25e97190ab2e04`;18 synthetic tests passed, shared b8 core unchanged. Numerical/statistical/ELF gates were not relaxed.

Remaining limits: process envelopes and31 correlated inner samples are descriptive, not confidence intervals; no pooling across runner/thread settings/runs. Raw final timed arrays are not duplicated: immutable child code rechecks its own-arm golden, with retained pre-timer digest and final-check flag. Cargo snapshots do not uniquely cryptographically bridge each ELF to its linked Rust rlib. Process-wide page faults include Polars/Python/allocator activity and cannot isolate allocator causes. Existing borrowed Arrow buffers are not a new optimization. Ordinary native `.over()` remains the sole grouped API.
