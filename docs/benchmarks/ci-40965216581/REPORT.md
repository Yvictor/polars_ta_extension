# Audited four-arm SAREXT comparison

CI: https://github.com/Yvictor/polars_ta_extension/actions/runs/40965216581
Controller: `37a98e2326cdcdd3d8c3b8048b1b4143199e09c6`

original: `b2bbc26d41ec80823c8bffb0cc436a97f29911cc`
prior: `56f6d5fb139031c20d86d7e818e7d267eb834295`
candidate: `8a4fc7feacc45b28929b2e7e6d1ae9919623bd2b`
alternative: `f7d800398ecd6dc79c5b346e7e151cf917272327`

The same runner built all four release arms with Rust1.90, portable CPU flags and identical runtime settings. Each of14 selected queries has12 fresh processes per arm and thread setting,31 samples after5 warmups;1,344 children/41,664 samples. The one/four thread settings remain separate.

All168 pairwise rows,28 four-arm median rows, every slower median, pure-Polars control and legitimate long-negative-zero replay stress are retained in CSV. A is typed Core plus scan/replay; B is the once-dispatched compatibility kernel. No means across workloads are used.

| Threads | Case | C ms | 56 ms | A ms | B ms |
| ---: | --- | ---: | ---: | ---: | ---: |
| 1 | sarext/1000000 | 10.088843 | 10.504838 | 10.678401 | 10.537743 |
| 1 | grouped_sarext/100x10000 | 13.203729 | 13.564793 | 13.455355 | 13.679609 |
| 1 | grouped_sarext/10000x100 | 64.198751 | 68.170100 | 62.837524 | 62.943167 |
| 1 | grouped_sarext/2000x100_interleaved | 12.025430 | 12.926403 | 11.674806 | 11.700110 |
| 1 | sarext_reversal/1000000 | 4.306261 | 4.345621 | 4.617826 | 4.429545 |
| 1 | grouped_sarext_reversal/100x10000 | 7.240254 | 7.220725 | 7.372961 | 7.216789 |
| 1 | grouped_sarext_reversal/10000x100 | 59.407280 | 62.713583 | 56.945107 | 56.665392 |
| 1 | grouped_sarext_reversal/2000x100_interleaved | 11.877218 | 12.626191 | 11.498620 | 11.376933 |
| 1 | sarext_longzero/1000000 | 5.682887 | 5.563400 | 8.739988 | 5.640766 |
| 1 | grouped_sarext_longzero/10000x100 | 60.471665 | 63.440102 | 61.285097 | 58.622067 |
| 1 | sar/1000000 | 10.868034 | 10.745105 | 10.660210 | 10.699655 |
| 1 | grouped_sar/10000x100 | 55.880115 | 56.392471 | 56.421852 | 56.481415 |
| 1 | control_cumsum_dense/1000000 | 2.895649 | 2.890656 | 2.897516 | 2.914893 |
| 1 | control_cumsum/10000x100 | 16.762836 | 16.784517 | 16.692978 | 16.642203 |
| 4 | sarext/1000000 | 10.596286 | 10.921665 | 11.105954 | 10.909308 |
| 4 | grouped_sarext/100x10000 | 13.842696 | 14.339994 | 14.141019 | 14.179173 |
| 4 | grouped_sarext/10000x100 | 66.781639 | 72.605682 | 65.850364 | 66.651233 |
| 4 | grouped_sarext/2000x100_interleaved | 12.363774 | 13.549225 | 12.260310 | 12.463531 |
| 4 | sarext_reversal/1000000 | 4.386757 | 4.421774 | 4.712862 | 4.452730 |
| 4 | grouped_sarext_reversal/100x10000 | 7.429796 | 7.512939 | 7.612583 | 7.603965 |
| 4 | grouped_sarext_reversal/10000x100 | 60.044598 | 65.872941 | 58.890075 | 58.971497 |
| 4 | grouped_sarext_reversal/2000x100_interleaved | 10.930851 | 11.951151 | 10.765356 | 10.734745 |
| 4 | sarext_longzero/1000000 | 5.744285 | 5.558682 | 8.652432 | 5.571652 |
| 4 | grouped_sarext_longzero/10000x100 | 61.107955 | 66.912631 | 63.992674 | 60.291372 |
| 4 | sar/1000000 | 10.690916 | 10.820180 | 10.641417 | 10.651893 |
| 4 | grouped_sar/10000x100 | 57.618005 | 57.994631 | 58.047704 | 57.600932 |
| 4 | control_cumsum_dense/1000000 | 2.946846 | 2.959554 | 2.958437 | 2.949138 |
| 4 | control_cumsum/10000x100 | 12.982375 | 13.123994 | 13.041154 | 12.971226 |

Process envelopes are descriptive observed ranges, not confidence intervals or a multiple-comparison significance test. Overlap limits speedup/regression conclusions; matched rounds and unchanged controls must be inspected. No ratios are pooled across runs, runners or thread settings. Positive latency change means the later arm is slower.

Strict numerical gates and the explicitly scoped untimed C-target short-zero correction are independent of timing acceptance. Legitimate long-side negative zero is preserved. Process-wide fault counters do not isolate allocator costs. Raw final timed arrays are not archived separately; immutable source checks the final output against retained own-arm goldens.

A local source/code-generation mechanism can motivate a change, but these consumer measurements do not isolate every setup/kernel/engine contribution. Remaining slower-than-C scenarios must be reported with their full distributions and noise status.


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
