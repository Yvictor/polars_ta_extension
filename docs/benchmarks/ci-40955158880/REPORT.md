# MAVP selected-SMA checked-iterator consumer comparison

**Retain the narrow helper change for final composition, with modest and scenario-specific evidence.** This component run does not establish a broad native `.over()` speedup or C parity.

CI: https://github.com/Yvictor/polars_ta_extension/actions/runs/40955158880

Artifact: https://github.com/Yvictor/polars_ta_extension/actions/runs/40955158880/artifacts/12935908467

Official ZIP1,576,462,230bytes, SHA256 `9506e14139c7314ca597d2fb5f92ef8b2f3f721cc488ee1db3cff9a24d78ad3e`,8,416files.

Immutable products, rebuilt in the same CI job:

- Original C: `b2bbc26d41ec80823c8bffb0cc436a97f29911cc` (C0.8.1).
- Delivered native reference: `56f6d5fb139031c20d86d7e818e7d267eb834295`.
- Candidate: `5bb6c66498794221804a76a1fd84af9501157a3f`.
- Controller: `d59283ed056fdaa0c3501ca0698f3fe133f8c154`.

The candidate changes only `src/compat/mavp_sma.rs`, replacing validated indexed selected-SMA loops with checked iterator windows while preserving the seed/add/copy/subtract order, division placement, period1 copies, buffer/error behavior and routes. No public API or grouping composition changes.

## Protocol and independent replay

AMD EPYC9V74 80-Core, Linux7.0.0-1017-azure/glibc2.39, Python3.12.15, Polars1.44.2, NumPy2.5.3, Rust1.90.0. Normal portable release builds: opt3, codegen-units16, LTO=false, no CPU-native flags. Affinity1CPU or4CPUs with matching Polars threads.

Twenty-four queries per thread setting,12process rounds covering all six arm orders twice,31samples after5warmups per fresh selected-case process:1,728children/53,568samples. The24queries include12 helper-target workloads and12 unchanged-route/host controls. All measured use ordinary direct expressions or native `.over("symbol")`.

The independently reviewed auditor passed all source/wheel/installed-ELF checks,16retained physical IPC snapshots (15.2million stored rows), six own-arm/thread raw query goldens, all144comparison records and every negative result. Full10624-case corpus independently replays2,167,654values per pair and191matching ComputeErrors:56→candidate exact finite/±0/null/NaN/±Inf positions,0differing fields; C→candidate659finite fields within declared1e-10 policy, max absolute2.5067947717616335e-11,0both-zero sign differences. NaN payload/sign are outside this exact contract. This does not assert zero-versus-near-zero finite positions are identical.

Independent review fixed a pre-raw falseaccept: tolerant C comparisons now reject sign differences when both outputs are zero. Shared approved core bytes remain unchanged. A second pre-timing review established an input regeneration portability issue: ARM `Generator.uniform` uses fused arithmetic whereas this Linux wheel uses separate multiply/add. The exact globally unfused `100+900*random(n)` oracle matches every retained volume bit; no tolerance or per-element choice was introduced. See `INPUT-ORACLE-PORTABILITY.md`.14synthetic tests pass; the reviewer independently replayed all16IPC seeds/groups and14tests.

## Retention and remaining regressions

Against56,21/24target medians decrease. Four target observations have disjoint12-process ranges and12/12paired improvements:1Tdensefour−1.075%,1Tdenseclamped−3.534%,1Tclamped100×10,000−2.050%,4Tdenseclamped−3.939%. Twenty target observations overlap; three higher medians are at most+0.166%. All24unchanged controls overlap, with12higher and12lower medians. These are descriptive process ranges, not confidence intervals or corrected statistical significance.

The familiar four-period100×10,000 case changes−0.849%/−0.491% at1/4threads, both overlapping;10,000×100 changes−2.132%/−3.064%, both overlapping;2000×100interleaved changes−2.361%/−3.231%, both overlapping. Those grouped observations support a directional finding, not an established general `.over()` speedup.

Against original C, candidate remains slower in35/48total medians,29with disjoint process ranges. Among the24changed-helper observations,14are slower and10disjoint. The existing unchanged routes also retain credible gaps: one-period14dense+49.353%/+47.538%; period1dense+60.448%/+60.948%; EMA dense+23.512%/+23.162%; WMA dense+52.508%/+51.440%. All are disjoint against C, and all overlap against56. They must not be described as regressions introduced by this helper change or as solved by it. Source-bound route proofs establish one/period1 normalize through the existing selected-period setup then call Core::ma; EMA/WMA bypass the selected-SMA helper. The setup/allocation/kernel cost partition remains unprofiled in this component run.

The largest changed-helper remaining C gap is few-period100×10,000 at+7.495%/+8.798%, both disjoint. Four-period100×10,000 remains+2.722%/+4.191%, both disjoint; blocked long groups+3.628%/+5.455%, clamped long groups+5.068%/+5.739%, also disjoint. Final combined-head results may differ and require their own full same-job comparison. No ratios are pooled or multiplied with earlier runners.

## Complete case table

Percentages are after latency versus reference; positive means slower. `D`=disjoint process ranges, `O`=overlap. Full medians, process vectors, paired ratios, sample p10/p90 and all three pairings are in `all-comparisons.csv`; every slower median is retained in `all-negative-comparisons.json`.

|Case|vs56 1T|vs56 4T|vsC 1T|vsC 4T|
|---|---:|---:|---:|---:|
|mavp_four/1000000|-1.075% D|-2.065% O|-5.095% D|-5.406% D|
|grouped_mavp_four/100x10000|-0.849% O|-0.491% O|+2.722% D|+4.191% D|
|grouped_mavp_four/10000x100|-2.132% O|-3.064% O|+1.090% O|-1.261% O|
|grouped_mavp_four/2000x100_interleaved|-2.361% O|-3.231% O|+1.410% O|-0.557% O|
|mavp_one/1000000|-0.157% O|-0.252% O|+49.353% D|+47.538% D|
|grouped_mavp_one/100x10000|+0.127% O|+0.589% O|+28.064% D|+32.578% D|
|mavp_few/1000000|+0.166% O|-0.393% O|+1.668% D|+1.527% O|
|grouped_mavp_few/100x10000|-0.150% O|-0.416% O|+7.495% D|+8.798% D|
|mavp_many/1000000|-0.109% O|-0.073% O|-2.152% D|-2.185% D|
|grouped_mavp_many/100x10000|-0.406% O|+0.057% O|+1.934% D|+2.520% O|
|mavp_blocked/1000000|+0.012% O|-0.156% O|-0.876% O|-0.392% O|
|grouped_mavp_blocked/100x10000|-0.235% O|-0.906% O|+3.628% D|+5.455% D|
|mavp_clamped/1000000|-3.534% D|-3.939% D|-2.655% D|-3.737% D|
|grouped_mavp_clamped/100x10000|-2.050% D|-2.415% O|+5.068% D|+5.739% D|
|mavp_period1/1000000|-0.009% O|+0.009% O|+60.448% D|+60.948% D|
|grouped_mavp_period1/100x10000|+0.035% O|-0.019% O|+28.075% D|+32.509% D|
|mavp_ema/1000000|-0.280% O|+0.435% O|+23.512% D|+23.162% D|
|grouped_mavp_ema/100x10000|+0.188% O|-0.172% O|+21.519% D|+26.215% D|
|grouped_mavp_ema/10000x100|-0.068% O|-1.134% O|+5.138% D|+4.104% D|
|mavp_wma/1000000|+0.159% O|+0.086% O|+52.508% D|+51.440% D|
|grouped_mavp_wma/100x10000|-0.119% O|+2.132% O|+41.781% D|+50.891% D|
|grouped_mavp_wma/10000x100|+0.453% O|-0.387% O|+8.502% D|+6.964% O|
|control_cumsum_dense/1000000|+0.113% O|-0.007% O|+0.243% O|-0.058% O|
|control_cumsum/10000x100|+0.267% O|-0.152% O|-0.633% O|-0.351% O|

## Limits

- Actual ELF/source identities are bound, and retained Cargo dependency snapshots are checked, but there is no independent unique ELF→linked-rlib cryptographic bridge.
- Source/static motivation is distinct from measured runtime. This audit makes no claim that bounds checks were removed from the actual normal-wheel helper machine code.
- All six query golden arrays and physical inputs are retained. Timed pre/post checks and hashes are exact against each arm’s own golden; every timed output array is not duplicated in the artifact.
- Inner samples within a process and rounds on one host are correlated. Process range disjointness is descriptive; small overlapping differences remain noisy. No separate-runner speedup conclusion is drawn.
- Process page faults include Polars/Python/allocator/thread activity and cannot establish allocator-only causation.
- The full correctness corpus is broad but does not enumerate every possible parameter/input combination.
