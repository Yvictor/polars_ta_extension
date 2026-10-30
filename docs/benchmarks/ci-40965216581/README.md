# Audited SAREXT component comparison

[CI40965216581](https://github.com/Yvictor/polars_ta_extension/actions/runs/40965216581) succeeded. [Raw artifact12939942104](https://github.com/Yvictor/polars_ta_extension/actions/runs/40965216581/artifacts/12939942104):587,018,936 bytes, SHA256 `2541f53a34e750d723799e80e734714d68b1a95a8e03185cebba9a70e90f583b`.

This is an isolated component comparison, **not evidence for a later combined consumer head**. Every arm was rebuilt in the same job/runner/runtime; no ratios are pooled with another run. Ordinary native Polars `.over()` is the grouped API.

| Arm | Immutable source | Behavior |
| --- | --- | --- |
| C | `b2bbc26d41ec80823c8bffb0cc436a97f29911cc` | Original C0.8.1 adapter |
| 56 | `56f6d5fb139031c20d86d7e818e7d267eb834295` | Delivered native control |
| A | `8a4fc7feacc45b28929b2e7e6d1ae9919623bd2b` | Typed Core plus zero scan/replay |
| B | `f7d800398ecd6dc79c5b346e7e151cf917272327` | Typed compatibility kernel dispatched once |

**Retain B for final composition.** Its ten short-group target medians are7.595%–10.477% lower than56, with12/12 favorable matched rounds each and nine disjoint observed ranges. B avoids A's dense legitimate-long-zero replay cost:35.460%/35.606% lower latency at1/4 configured threads. These are whole-expression observations, not allocator-only or kernel-only attribution.

**C gaps remain.** Eight of20 B target medians are slower than C; all their ranges overlap. Dense ordinary SAREXT remains+4.449%/+2.954% slower at1/4 threads, with B faster in only1/12 and0/12 matched rounds. Overlap does not establish parity or erase the repeated direction. All slower medians, including controls and A regressions, remain in the archive.

AMD EPYC9V45, Linux7/glibc2.39, Python3.12.15, Polars1.44.2, NumPy2.5.3, Rust1.90.0; portable release O3/cgu16/LTOfalse. Pool/affinity settings1/[0] and4/[0,1,2,3] do not demonstrate utilization of every core. Four arms ×14 queries ×12 balanced Williams rounds ×two settings produced **1,344 fresh children /41,664 samples**,31 samples after five warmups each.

The independent audit passed all ten physical Arrow fixtures, eight own-arm query goldens, four complete10,624-case captures and six pairwise corpus comparisons. Native finite values, signed zeros and masks match exactly in that corpus. B changes373 raw NaN signs only—183 `sarext/infinity`,190 `sarext/leading_infinity`; NaN payload/sign is outside the numerical contract, while positions remain strict. All native arms retain three inherited STOCHRSI zero-versus-tiny C cancellation positions within the established finite tolerance: global zero-position equivalence is **not** claimed. The separate untimed short-zero regression requires C/A/B +0 at fixed rows and records56's −0; it never waives timed or full-corpus checks. Legitimate long-side −0 remains required.

## Complete records

- [Approved report and full28-row four-arm table](REPORT.md), [retention rationale and every remaining C target gap](RETENTION.md).
- [All168 pairwise comparisons](all168-pairwise-comparisons.csv), [all168 full distributions](all168-distributions.csv), [28 four-arm medians](all28-four-arm-medians.csv).
- [Every slower median](all-slower-medians.csv), [all48 SAR/Polars control comparisons](all-controls.csv), [24 pure-Polars control rows](all-Polars-controls.csv), [24 legitimate-long-zero stress rows](all-replay-stress.csv).
- [B versus C target rows](B-vsC-targets-20.csv), [B versus56 target rows](B-vs56-targets-20.csv), [all11 B-versus-C slower medians including controls](all-B-slower-C.csv).
- [Complete independently replayed result](result.json), [machine-readable retention counts and NaN-sign proof](RETENTION.json), [source/transport/runtime/audit provenance](provenance.json), [archive manifest](manifest.json).

All twelve process medians, paired ratios, envelopes and sample p10/p90 arrays are retained in the distribution CSV and result JSON. The linked artifact retains every raw31-sample child vector. Process ranges are descriptive, not confidence intervals; correlated inner samples and multiple comparisons limit statistical claims. Process-wide fault counters cannot isolate allocator costs.

## Independent review and evidence boundary

Controller `37a98e2326cdcdd3d8c3b8048b1b4143199e09c6`; successful job123767857523. The original approved auditor stopped before numerical/timing reads because ELF diagnostic paths use the producer's workspace-relative form. Its source and stop log are preserved under [audit/](audit/). A separate reviewer approved only safe exact producer-relative/recorded-workspace-absolute path mapping, with area/arm/traversal/symlink binding. No numerical, statistical, ELF or compatibility gate was relaxed.

Final auditor SHA256 `761c29f8242cebc41a89627ccb7e758b610336ac5fb3c5c4cc9a187ca86b7e33`; frozen trust `726880c2b4ad089767fc56c11563548a5f0fedc0025dbd61ba25e97190ab2e04`; unchanged shared core `b8c0b004daac5d920835c7a316cf97919cc3a13633eeecd860fdd02ab669cba9`. Eighteen synthetic tests passed. Independent final review recomputed all168 rows directly from all1,344 raw children and rescanned the373 NaN sign changes.

Actual normal-wheel identity, symbol/address-bound FMA clone/portable fallback/resolver and the fresh cold-dispatch test passed. A portable `fma` transfer resolves to a local compiler_builtins shim; this is not proof of software-only execution. Final timed arrays are not separately duplicated: immutable child code rechecks its own-arm golden, with retained pre-timer digest and final-check flag. Shared Cargo fingerprints are not a unique ELF-to-linked-rlib cryptographic bridge. Existing borrowed Arrow buffers predate this change. The final composed consumer still needs its own correctness/performance CI.

The historical audit manifest keeps its original source-layout names. [The path correction patch](audit/path-fix.diff.json) is stored losslessly as a JSON string to preserve unified-diff context whitespace; its decoded SHA256 matches the original approved patch. All other copied evidence is byte-identical to the approved source, and all derived CSV selections preserve exact parsed records.
