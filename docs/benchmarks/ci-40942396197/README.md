# Audited consumer ENGULFING component comparison

[CI40942396197](https://github.com/Yvictor/polars_ta_extension/actions/runs/40942396197) succeeded. Controller `bcbb2a6c74699ddf59eacd531d3e904be198d127`; three immutable product pins:

- original: `b2bbc26d41ec80823c8bffb0cc436a97f29911cc`
- prior: `56f6d5fb139031c20d86d7e818e7d267eb834295`
- candidate: `46db222092c4f8f391377420e441f12a403f8fce`

This measures the isolated 46db candidate, not a later combined integration head. No ratio is pooled or multiplied with another run.

{"affinity": [0], "cpu": "AMD EPYC 9V45 96-Core Processor", "numpy": "2.5.3", "platform": "Linux-7.0.0-1017-azure-x86_64-with-glibc2.39", "polars": "1.44.2", "profile": "release (maturin --release --locked), portable CPU target", "python": "3.12.15", "rust": "rustc 1.90.0 (1159e78c4 2025-09-14)"}

The job rebuilt all three portable release wheels on one runner. One/four controlled threads, 20 direct/native `.over()` queries, 12 fresh selected-case processes per arm/query/thread setting, all six orders twice, 31 samples after five warmups: **1,440 children / 44,640 samples**. The full 10,624-case / 2,167,654-value corpus passed original-C tolerances and exact native56 checks before timing.

| Dense1m case / threads | Original C ms | Native56 ms | Candidate ms | vs56 | vsC | Faster rounds |
|---|---:|---:|---:|---:|---:|---:|
|cdlengulfing/1000000 / 1T|0.703477|0.731616|0.623633|-14.760%|-11.350%|12/12|
|cdlengulfing_mixed/1000000 / 1T|0.972951|1.196655|0.979202|-18.172%|+0.643%|12/12|
|cdlengulfing/1000000 / 4T|0.804936|0.813829|0.703037|-13.614%|-12.659%|12/12|
|cdlengulfing_mixed/1000000 / 4T|1.073710|1.267189|1.070486|-15.523%|-0.300%|12/12|

All four dense target comparisons against56 have disjoint observed process-median ranges and12/12 faster rounds. Mixed-candle dense comparisons against C overlap parity. Legacy all-bullish dense results are faster than C with disjoint ranges.

**No native `.over()` gain is established:** all16 grouped target comparisons against56 have overlapping process ranges. Short all-bullish medians are +0.803%/+1.187% (1T/4T), mixed short medians −1.360%/−0.963%, interleaved mixed short +0.569%/+0.583%; all overlap. All20 Doji/ADD control comparisons against56 overlap. No tested Engulf comparison has a disjoint slower C range. All40 observations, including every slower median, are in [all-observations.csv](all-observations.csv).

Mixed fixtures independently assert−100,−80,0,80,100 in every chronological group, including interleaved groups; the retained historical fixture is explicitly all-bullish/all-zero. No custom grouping expression or list batching is used.

## Artifact and independent audit

[Artifact12930801241](https://github.com/Yvictor/polars_ta_extension/actions/runs/40942396197/artifacts/12930801241):222,722,664bytes; ZIP SHA256 `ce17f4e50c191deef592095723dd5a879213123d597f3aaee54f34a27a594776`. Independent read-only audit reconciled all ledger entries, raw samples, source/wheel/ELF identities, references, mixed per-group oracle and complete corpus. Its new auditor was independently reviewed with seven owner fixtures and five additional gates; three reproduced false accepts were fixed before raw replay.

## Limits

- Frozen audit expectations before raw result access, after CI measurements began.
- Original C real control tolerance1e-10, allinteger outputs exact; native-arm goldens exact finite/signedzero/masks/NaN positions. NaN sign/payload not a public guarantee.
- Final candidate query arrays not archived; retained C/prior goldens and source-bound pre/post child checks. Separate complete candidate corpus independently replayed.
- Descriptive twelve-round extrema are not confidence intervals; no cross-run ratio multiplication or pooling thread counts.
- Fault counters are process-wide, not allocator-only.
- Raw query input frames are not archived: deterministic generation is source-bound and fixture hashes are checked across arms and timed children. Mixed Engulf golden outputs and per-group counts additionally have an independent literal oracle.
- Retained shared-target Cargo metadata is reconstructed but not independently mapped to unique ELF/archived Rust rlibs; exact source compile logs and installed/wheel hashes bind the normal products through immutable CI provenance.
