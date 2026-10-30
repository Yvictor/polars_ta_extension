# Uniform-prefix MAVP: independent four-arm CI replay

**Recommend retaining candidate916 for its uniform fast paths.** Eleven of16 uniform observations have disjoint faster process ranges against combined0eb, with no disjoint slower observation across the64 cases/settings. This does not establish universal C parity or a short-group `.over()` speedup.

CI: https://github.com/Yvictor/polars_ta_extension/actions/runs/40970023623

Artifact: https://github.com/Yvictor/polars_ta_extension/actions/runs/40970023623/artifacts/12945010556

Official ZIP2,560,047,031bytes, SHA256 `d1c657249dc0142c78fba54ed82e719cc85cfe34e13fff3973daf46ac34b3255`,13,460extracted files. Root verified the official metadata/SHA and every extracted file before this audit.

## Immutable comparison and source change

- original: `b2bbc26d41ec80823c8bffb0cc436a97f29911cc`
- prior: `56f6d5fb139031c20d86d7e818e7d267eb834295`
- combined: `0eb91280cf5d13095cbfdc6f8bcc477cfbcd1498`
- candidate: `916b0de68369df410559b6dc651731cf4c36b94c`
- Controller: `5171ea5583f83766da05ef0d1f8bc69091063369`.

Candidate916 changes only `src/compat/mavp_sma.rs` plus its new public regression test compared with combined0eb. The helper normalizes the first produced period, probes to the first different normalized period, and calls the same Core::ma directly if the whole produced range is uniform. A nonuniform range fills the already-proven uniform prefix and normalizes the remaining suffix into the existing scratch vector. The existing selected-SMA seed/add/copy/subtract and output loop are preserved. Raw fractional inputs14.01/14.25/14.999 all normalize14. No new public expression or grouping composition is introduced.

Avoiding the temporary period vector is an implementation fact; it is not itself a latency measurement or proof that allocation alone explains the observed differences. The following conclusions come from the matched CI measurements.

## Environment and protocol

Intel Xeon6973P-C, Linux7.0.0-1017-azure/glibc2.39, Python3.12.15, Polars1.44.2, NumPy2.5.3, Rust1.90.0. Portable normal release wheels, opt3/codegen-units16/LTO=false, empty CPU-native flags; all four products built sequentially on the same runner. Affinity1CPU or4CPUs with matching Polars threads.

Thirty-two scenarios at each thread setting:12 balanced Williams rounds,31samples after5warmups per fresh selected-case process, **3,072children/95,232samples**. All384six-pair comparison rows and every slower median/control are preserved. One/two/29selected periods, blocked/clamped periods, fractional uniformity, early split1, late splitcount−1, dense/long/short/interleaved groups and unchanged EMA/WMA/Polars controls are included. All groups use ordinary native `.over("symbol")`.

## Independent correctness and provenance

The unchanged pre-reviewed auditor passed on its first replay:4source/wheel/installed-ELF identities and actual compile paths, normal Cargo roots/dependency edges,24physical IPC snapshots,8own-arm/thread query goldens,6full-corpus pairs, all command/order/process ledgers, raw latency/fault vectors and all top-level/negative summaries. The approved sharedb8core remains byte-identical. Nineteen synthetic audit tests passed locally and independently before raw access.

Every corpus pair includes10,624cases/2,167,654values and191matching ComputeErrors. All three native pairs are exact for finite values, signed zeros, null/NaN/±infinity positions:0different fields/max absolute0. The three C-versus-native pairs each have659fields with finite bit differences within the declared ordinary1e-10 policy (tighter tiny absolute policy), maximum2.5067947717616335e-11;0sign differences when both outputs are zero. NaN sign/payload are outside the exact contract. Zero-versus-tiny finite cancellation remains governed by finite tolerance; no claim of identical zero positions is made.

The independent physical oracle verifies exact Linux seeded input bytes, stable chronological groups, all three fractional raw levels, normalized first-difference positions, every-group warmups, direct bounded-window SMA mathematics and pure Polars cumsum. EMA/WMA arithmetic is checked using the actual original-C goldens. Timed pre/post full-output checks/hashes bind each child to its own retained golden.

## Retention evidence and all remaining effects

Against combined0eb, all16uniform medians are lower (−0.137% to−38.485%),11have disjoint faster process ranges and12/12paired faster rounds;5overlap. No uniform median is higher.

- Period14dense:6.890324→5.450024ms (1T,−20.903%) and7.375925→5.653661ms (4T,−23.350%); both disjoint,12/12paired faster.
- Period14,100×10,000:−11.986%/−17.329%; both disjoint,12/12paired faster.
- Fractional uniform dense:−21.851%/−30.005%; long groups−12.369%/−14.227%; all four disjoint,12/12paired faster.
- Period1dense:1T−26.253%disjoint. The larger4T median reduction−38.485%remains **overlapping** despite12/12paired improvements: combined process medians7.108949–10.337150ms versus candidate5.237470–7.415862ms. Do not report the4T number as a uniformly separated result.
- Uniform10,000×100:−1.734%/−0.881%, both overlapping. Uniform2000×100interleaved:−2.156%/−0.137%, both overlapping. These do not establish a short-group speedup.

All32nonuniform fallback observations overlap against0eb:23lower medians and9higher, ranging−11.719% to+1.761%. The worst higher median is4T early-split100×10,000 (+1.761%,5/12paired faster); process ranges overlap. The4T last-split dense−11.719% also overlaps despite12/12paired improvements. Preserve both findings rather than selectively promoting one. All16unchanged EMA/WMA/Polars controls overlap (13lower/3higher medians). No measured introduced regression has disjoint process ranges, but overlapping ranges do not prove equivalence.

Against delivered56,15/64observations have disjoint faster ranges and0disjoint slower;11of those faster observations are uniform fast paths,4are nonuniform. This is a same-run direct comparison; it is not obtained by multiplying earlier component ratios.

## Remaining original-C gaps

Candidate916 is slower than C in24/64medians:8uniform,1nonuniform and15unchanged-control observations. Eleven have disjoint slower ranges, all unchanged EMA/WMA controls. Uniform observations have0disjoint C-slower ranges,3disjoint C-faster and13overlapping. This is not proof of C speed parity: for example dense period14 still has+18.075%/+9.693%slower medians than C, both overlapping; dense period1 has+23.351%1T slower median, overlapping.

Credible remaining C gaps include:

- EMA dense+35.708%/+38.401%, long groups+17.476%/+22.522%, all disjoint. EMA short groups+5.013%1T disjoint/+5.303%4T overlapping.
- WMA dense+71.310%/+60.220%, long groups+29.702%/+31.842%, short groups+5.438%/+6.488%, all disjoint.

The source-bound routes establish these EMA/WMA cases bypass the changed selected-SMA helper. Their setup/allocation/kernel partition is not determined by this audit; no allocation-only causal claim or solved-regression claim is justified. The sole nonuniform C-slower candidate median is4T four-period10,000×100 at+0.026%, overlapping. Four pure Polars controls all overlap against C.

## Complete scenario table

Percentages are candidate latency changes; positive means slower. D=disjoint process ranges, O=overlap. The complete384-row CSV also includes all six pairings, raw process medians, paired ratios and samplep10/p90.

|Scenario|Role|vs0eb1T|vs0eb4T|vsC1T|vsC4T|
|---|---|---:|---:|---:|---:|
|mavp_four/1000000|nonuniform fallback regression guard|-1.960% O|+0.149% O|-25.572% D|-24.538% D|
|grouped_mavp_four/100x10000|nonuniform fallback regression guard|-0.576% O|+0.044% O|-4.084% D|-1.266% O|
|grouped_mavp_four/10000x100|nonuniform fallback regression guard|+0.077% O|+0.233% O|-2.297% O|+0.026% O|
|grouped_mavp_four/2000x100_interleaved|nonuniform fallback regression guard|-0.911% O|-0.596% O|-3.462% O|-1.700% O|
|mavp_one/1000000|uniform fast path|-20.903% D|-23.350% D|+18.075% O|+9.693% O|
|grouped_mavp_one/100x10000|uniform fast path|-11.986% D|-17.329% D|-4.971% O|-11.498% D|
|mavp_few/1000000|nonuniform fallback regression guard|-0.540% O|-1.692% O|-25.532% D|-30.194% D|
|grouped_mavp_few/100x10000|nonuniform fallback regression guard|-0.776% O|-1.506% O|-6.853% O|-5.944% O|
|mavp_many/1000000|nonuniform fallback regression guard|-0.751% O|-0.610% O|-18.694% D|-18.808% D|
|grouped_mavp_many/100x10000|nonuniform fallback regression guard|-0.487% O|+1.416% O|-3.120% O|-2.745% O|
|mavp_blocked/1000000|nonuniform fallback regression guard|-0.492% O|-2.077% O|-37.255% D|-26.540% D|
|grouped_mavp_blocked/100x10000|nonuniform fallback regression guard|-1.854% O|-0.276% O|-13.493% D|-10.335% D|
|mavp_clamped/1000000|nonuniform fallback regression guard|-4.412% O|-0.621% O|-28.076% D|-19.955% D|
|grouped_mavp_clamped/100x10000|nonuniform fallback regression guard|+0.247% O|+0.583% O|-8.214% D|-2.955% O|
|mavp_period1/1000000|uniform fast path|-26.253% D|-38.485% O|+23.351% O|-15.703% O|
|grouped_mavp_period1/100x10000|uniform fast path|-12.468% D|-17.016% D|-5.795% O|-7.514% D|
|mavp_ema/1000000|unchanged EMA/WMA or Polars control|-0.416% O|-0.001% O|+35.708% D|+38.401% D|
|grouped_mavp_ema/100x10000|unchanged EMA/WMA or Polars control|+0.076% O|-0.467% O|+17.476% D|+22.522% D|
|grouped_mavp_ema/10000x100|unchanged EMA/WMA or Polars control|-0.002% O|-1.258% O|+5.013% D|+5.303% O|
|mavp_wma/1000000|unchanged EMA/WMA or Polars control|-1.736% O|-2.726% O|+71.310% D|+60.220% D|
|grouped_mavp_wma/100x10000|unchanged EMA/WMA or Polars control|+1.285% O|-0.968% O|+29.702% D|+31.842% D|
|grouped_mavp_wma/10000x100|unchanged EMA/WMA or Polars control|-0.452% O|-1.238% O|+5.438% D|+6.488% D|
|control_cumsum_dense/1000000|unchanged EMA/WMA or Polars control|-0.311% O|-0.667% O|+1.207% O|+2.844% O|
|control_cumsum/10000x100|unchanged EMA/WMA or Polars control|-1.257% O|+0.534% O|-0.550% O|+0.069% O|
|mavp_early/1000000|nonuniform fallback regression guard|-0.173% O|-0.262% O|-40.709% D|-27.712% D|
|grouped_mavp_early/100x10000|nonuniform fallback regression guard|+0.021% O|+1.761% O|-16.010% D|-13.267% D|
|mavp_last/1000000|nonuniform fallback regression guard|-3.431% O|-11.719% O|-37.280% D|-36.368% D|
|grouped_mavp_last/100x10000|nonuniform fallback regression guard|-0.577% O|-0.674% O|-15.353% D|-11.961% D|
|mavp_fractional/1000000|uniform fast path|-21.851% D|-30.005% D|+14.388% O|-28.887% O|
|grouped_mavp_fractional/100x10000|uniform fast path|-12.369% D|-14.227% D|-6.998% O|-9.453% D|
|grouped_mavp_one/10000x100|uniform fast path|-1.734% O|-0.881% O|+1.945% O|+1.547% O|
|grouped_mavp_one/2000x100_interleaved|uniform fast path|-2.156% O|-0.137% O|+0.203% O|+3.744% O|

## Limits

- Trust frozen from immutable Git before any uniform-MAVP raw artifact/results access.
- All24physical IPC inputs, all8own-arm/thread query goldens and4full corpora are retained. Timedfinal arrays are checked/hashed against each arm golden but not duplicated for every child.
- Shared-target Cargo snapshots bind selected dependency edges/flags but may include old roots; no unique measuredELF-to-linkedrlib bridge is claimed. Source/wheel/actualELF compile and byte identities are checked.
- Twelve process rounds and correlated31inner samples are descriptive; process ranges are not confidence intervals or multiple-comparison significance. No pooling runners or thread settings.
- Fault counters are whole-process engine/Python/allocator/thread activity, not allocator-only causation. Zero-allocation evidence is separate from latency.
- C finite differences use declared1e-10 policy with tighter tiny absolute tolerance; both-zero signs are strict. Native finite/signedzero/null/NaN/Inf positions are exact. NaNpayload/sign are outside the exact contract.
- Actual normal-wheel bounds removal or cold-dispatch speedups are not established by source labels. Source route/early-split proofs are eligibility, not branch instrumentation.
- The direct-window finite SMA oracle is independent of the rolling helper and uses declared C finite tolerance. EMA/WMA control arithmetic relies on retained original-C goldens; every native golden pair is exact including finite/signedzero/masks/NaN/Inf positions.
- Explicit globally unfused100+900*random transform regenerates Linux volume bits; ARM Generator.uniform may fuse. This is exact input provenance, not numerical tolerance.
- This is the isolated916component run. Integration changes require their own final-head gates/comparison; no result is pooled with other runners.
- Process-median envelopes and matched rounds are descriptive, not confidence intervals or formal multiple-comparison significance. CPU frequency/shared-host contention remain uncontrolled.
- Allocation counts and page faults cannot alone establish the cause or size of a latency improvement.
