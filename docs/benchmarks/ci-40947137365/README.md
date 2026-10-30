# Retention recommendation: reject guard fusion and initialization-only changes

The isolated four-arm CI does not support retaining98d933f or1cf188b as performance improvements. All44 observed process-median envelopes overlap for56→fused,56→initialization andinitialization→fused. No tested scenario establishes a disjoint improvement from the new factory or from fusion itself. Fused medians are slower24/44 versus56 and23/44 versus the matched initialization control. These are descriptive observations, not a universal claim that both variants always regress.

Overlapping extrema do not erase unfavorable paired trends. At1T,10,000×100 VAR is2.736% slower versus56 in12/12 paired rounds; CORREL2.481%,STDDEV2.248% and the ineligible SMA factory control2.661% are slower11/12. At4T,interleaved2,000×100 CORREL is3.797% slower11/12. Matched init→fused dense CORREL is0.990%/1.516% slower at1/4T,11/12 paired rounds each; dense STDDEV is1.694%/2.184% slower,10/12 and11/12 rounds. These repeated signs support caution, while the shared runner, multiple comparisons and correlated samples prevent formal causal/significance claims.

SMA is an ineligible native factory-overhead control, not unchanged whole-path code: the first-real-output factory attempt is newly called before rejecting SMA. Its1T short-group negative trend contrasts with4T short groups3.293% faster11/12, both envelopes overlapping. The pure Polars query controls also overlap (grouped4T median+1.402% versus56); they quantify host/engine variability and must not be subtracted from indicator timings.

The C regression inventory remains unresolved: fused is slower by median39/44 and has21 disjoint slower envelopes, all in eligible indicator workloads (15 at1T,6 at4T). Largest dense gaps: VAR+14.143%/+13.089%,STDDEV+10.741%/+10.315%,CORREL+7.830%/+11.641% at1/4T. Original56 already has20 disjoint C regressions in this matrix. The verified fused guard pass therefore does not remove the observed C bottleneck. Full-query timings and process faults cannot establish which rolling kernel, allocation, setup or execution-engine component causes the remaining gap.

## Complete per-scenario medians

Milliseconds are medians of12 fresh process medians. Percent changes use after/before−1. All264 paired ratios, raw sample percentiles and envelopes are in all264-pairwise-comparisons.csv; all original JSON31-sample vectors remain in the linked artifact. No averages across function families, thread counts or runs are used.

|T|Case|C|56|Init-only|Fused|Fused vs56|Fused vsInit|Faster vs56/init rounds|
|---:|---|---:|---:|---:|---:|---:|---:|---:|
|1|correl/1000000|13.243646|14.205686|14.140617|14.280645|+0.528%|+0.990%|4/12 ·1/12|
|1|grouped_correl/100x10000|20.973155|22.071879|21.932616|22.046236|-0.116%|+0.518%|7/12 ·6/12|
|1|grouped_correl/10000x100|89.800413|89.631409|89.842551|91.855099|+2.481%|+2.240%|1/12 ·3/12|
|1|var/1000000|6.412538|7.309893|7.183851|7.319491|+0.131%|+1.888%|4/12 ·2/12|
|1|grouped_var/100x10000|12.930741|14.028675|13.980122|13.933382|-0.679%|-0.334%|10/12 ·8/12|
|1|grouped_var/10000x100|69.897043|72.828802|74.437328|74.821238|+2.736%|+0.516%|0/12 ·2/12|
|1|stddev/1000000|7.801251|8.606714|8.495223|8.639175|+0.377%|+1.694%|7/12 ·2/12|
|1|grouped_stddev/100x10000|14.259709|15.395895|15.314265|15.161905|-1.520%|-0.995%|9/12 ·9/12|
|1|grouped_stddev/10000x100|72.476415|75.506146|76.960564|77.203716|+2.248%|+0.316%|1/12 ·6/12|
|1|bbands/1000000|17.906568|18.652257|18.644873|18.713582|+0.329%|+0.369%|3/12 ·3/12|
|1|grouped_bbands/1000x1000|38.674027|41.219185|41.829003|41.295898|+0.186%|-1.274%|5/12 ·10/12|
|1|grouped_bbands/10000x100|185.906196|197.520450|202.431802|200.817286|+1.669%|-0.798%|3/12 ·6/12|
|1|macd/1000000|14.955811|14.809579|14.833179|14.883078|+0.496%|+0.336%|1/12 ·6/12|
|1|grouped_macd/1000x1000|35.687483|37.647062|37.687002|37.125915|-1.384%|-1.489%|6/12 ·9/12|
|1|grouped_macd/10000x100|182.290146|190.019392|192.086490|192.515781|+1.314%|+0.223%|3/12 ·7/12|
|1|grouped_correl/2000x100_interleaved|18.943131|18.794185|19.113326|18.973002|+0.951%|-0.734%|3/12 ·5/12|
|1|grouped_bbands/2000x100_interleaved|35.293566|36.900830|37.664771|37.439285|+1.459%|-0.599%|3/12 ·5/12|
|1|grouped_macd/2000x100_interleaved|34.166007|35.706933|36.397796|36.088202|+1.068%|-0.851%|3/12 ·8/12|
|1|sma/1000000|5.717365|5.879882|5.899437|5.867599|-0.209%|-0.540%|5/12 ·6/12|
|1|grouped_sma/10000x100|66.569729|67.199581|67.783959|68.987617|+2.661%|+1.776%|1/12 ·3/12|
|1|control_cumsum_dense/1000000|4.527690|4.526699|4.525267|4.522534|-0.092%|-0.060%|7/12 ·8/12|
|1|control_cumsum/10000x100|24.324535|24.224162|24.196825|24.306703|+0.341%|+0.454%|3/12 ·4/12|
|4|correl/1000000|12.781907|14.216210|14.056790|14.269857|+0.377%|+1.516%|3/12 ·1/12|
|4|grouped_correl/100x10000|19.713024|21.110075|21.029220|20.945836|-0.778%|-0.397%|10/12 ·8/12|
|4|grouped_correl/10000x100|93.622647|93.432678|94.201548|94.704301|+1.361%|+0.534%|3/12 ·5/12|
|4|var/1000000|6.334084|7.130377|7.089155|7.163163|+0.460%|+1.044%|7/12 ·5/12|
|4|grouped_var/100x10000|10.121223|10.718868|10.688740|10.689338|-0.275%|+0.006%|8/12 ·5/12|
|4|grouped_var/10000x100|47.312580|49.041951|49.374555|48.993496|-0.099%|-0.772%|4/12 ·9/12|
|4|stddev/1000000|8.005903|8.873076|8.642950|8.831734|-0.466%|+2.184%|6/12 ·1/12|
|4|grouped_stddev/100x10000|10.679921|11.383567|11.289784|11.273934|-0.963%|-0.140%|7/12 ·6/12|
|4|grouped_stddev/10000x100|47.391239|49.612181|49.881863|49.225395|-0.780%|-1.316%|9/12 ·8/12|
|4|bbands/1000000|17.544180|18.248249|18.204752|18.276035|+0.152%|+0.392%|8/12 ·6/12|
|4|grouped_bbands/1000x1000|25.317496|26.366432|26.522737|25.876755|-1.857%|-2.436%|9/12 ·10/12|
|4|grouped_bbands/10000x100|110.446354|115.104647|118.349672|114.921912|-0.159%|-2.896%|7/12 ·10/12|
|4|macd/1000000|14.863189|14.618203|14.437130|14.527963|-0.617%|+0.629%|7/12 ·3/12|
|4|grouped_macd/1000x1000|24.245321|25.233188|25.322531|25.119125|-0.452%|-0.803%|6/12 ·9/12|
|4|grouped_macd/10000x100|110.819424|116.366981|115.770956|113.955695|-2.072%|-1.568%|7/12 ·10/12|
|4|grouped_correl/2000x100_interleaved|18.453805|18.301661|18.646099|18.996591|+3.797%|+1.880%|1/12 ·1/12|
|4|grouped_bbands/2000x100_interleaved|20.328961|21.229408|21.673586|21.339571|+0.519%|-1.541%|5/12 ·10/12|
|4|grouped_macd/2000x100_interleaved|20.028256|20.866060|21.328616|20.858793|-0.035%|-2.203%|6/12 ·10/12|
|4|sma/1000000|5.939789|5.975086|5.984349|6.002179|+0.453%|+0.298%|6/12 ·6/12|
|4|grouped_sma/10000x100|45.585463|46.719175|45.923238|45.180521|-3.293%|-1.617%|11/12 ·9/12|
|4|control_cumsum_dense/1000000|4.571244|4.580141|4.578603|4.579379|-0.017%|+0.017%|9/12 ·6/12|
|4|control_cumsum/10000x100|18.824916|18.658531|18.747284|18.920066|+1.402%|+0.922%|3/12 ·3/12|

## Correctness and machine evidence

All six complete10624-case/2167654-value corpus comparisons passed. Three native/native pairs are exact (finite values, signedzero, null/NaN/infinity positions;0 differing fields). Each C/native pair has659 nonexact fields within1e-10 policy, maximum absolute error2.5067947717616335e−11;191 matching ComputeErrors. This is the recorded corpus scope, not every possible input.

Normal product ELF independently verified fused backedge5550305 and init-only scan5567157/fills5566740,5566932. Codegen success establishes emitted fusion, not a speed benefit. Original full unbounded LLVM disassembly included alignment INT3s; explicit bounds from immutable ELF symbol size removed only that padding and exactly matched archived GNU instruction addresses. The failure and approved correction are retained.

[CI40947137365](https://github.com/Yvictor/polars_ta_extension/actions/runs/40947137365), [artifact12934698552](https://github.com/Yvictor/polars_ta_extension/actions/runs/40947137365/artifacts/12934698552), ZIP875282481bytes SHA256 `9645ee3448c67f07bb0326a962855b13005924d98843817cca04182292aa2e65`. AMD EPYC7763 64-Core Processor, Linux7.0.0-1017-azure/glibc2.39; Python3.12.15,Polars1.44.2,NumPy2.5.3,Rust1.90.0. Affinity[0]/[0,1,2,3]; ordinary portable O3/cgu16/CargoLTO=false release wheels with empty Rust/C flags, one shared runner. CargoLTO=false permits ordinary local ThinLTO; no explicit-Cltooff flag. No core-exclusive, allocator-exclusive or cross-run claim.

Initialization/candidate timed-query arrays and physical query input frames were not retained: input/output hashes and exact pre/final checks are source-bound and cross-checked against original/prior goldens; all four full corpus arrays are independently replayed. Shared Cargo fingerprint graphs are inspected but not cryptographically mapped to unique ELF-linked rlibs. The pure CFG matcher is the previously reviewed scoped algorithm, replayed against independent LLVM-decoded ELF, not a universal static verifier.


This negative experiment is archived to prevent treating a verified emitted loop as an unmeasured performance win. Neither98d933f nor1cf188b is retained in the consumer integration. The original56 guard implementation remains the reference. Added factory dispatch, parameter access and reduction work are possible costs to investigate, not isolated causes proven by this full-query benchmark. No new grouping expression or list batching was used.
