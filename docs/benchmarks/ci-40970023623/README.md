# MAVP uniform prefix: retained component CI evidence

This archive records the isolated comparison of original C, delivered56, combined0eb and uniform candidate916. Latency acceptance comes from [CI40970023623](https://github.com/Yvictor/polars_ta_extension/actions/runs/40970023623), with four portable release wheels built and measured on one Intel Xeon6973P-C runner. It is not a benchmark of a later combined PR head.

[REPORT.md](REPORT.md) contains the complete32-scenario table, remaining C gaps and limitations. [all-384-comparisons.csv](all-384-comparisons.csv) retains every pair/thread/scenario, including process vectors, sample p10/p90, paired ratios and roles. [all-slower-medians.json](all-slower-medians.json) preserves every slower median, including fallback and unchanged controls. [comparison-inventory.json](comparison-inventory.json) contains all six pair inventories.

The scoped RETAIN decision: against0eb, all16uniform medians are lower,11have disjoint faster process ranges; no disjoint regression appears among all64 observations. All32fallback and16unchanged control observations overlap. Short/interleaved uniform cases overlap, so no established short-group speedup is claimed. Candidate still has24C-slower medians,11disjoint; all11disjoint losses are unchanged EMA/WMA controls. Process ranges are descriptive, not confidence intervals. Allocation counts do not establish latency or allocator-only causation.

## Focused views without numeric reformatting

- [uniform-vs-combined-16.csv](uniform-vs-combined-16.csv): all16uniform observations.
- [fallback-vs-combined-32.csv](fallback-vs-combined-32.csv): all32fallback guards, including early/last mismatch cases.
- [controls-vs-combined-16.csv](controls-vs-combined-16.csv): unchanged EMA/WMA and Polars controls.
- [all-candidate-slower-C.csv](all-candidate-slower-C.csv): all24candidate medians slower than C, including noisy controls.
- [short-interleaved-vs-combined.csv](short-interleaved-vs-combined.csv): all short/interleaved scenarios, including overlapping and negative findings.

These filter exact string records from the approved complete CSV. No numerical values, vectors or precision were rewritten.

## Correctness and review

[audit-result.json](audit-result.json) records the unchanged approved replay:3,072fresh children/95,232samples,24physical inputs,8own-arm goldens,6full-corpus pairs and all384comparisons. Native finite values, signed zeros and null/NaN/Inf positions are exact; C finite/tiny tolerances and strict both-zero signs remain explicit.

[INDEPENDENT-384-ROW-REVIEW.json](INDEPENDENT-384-ROW-REVIEW.json) records separate recomputation from every raw child/stdout/command ledger. [audit/](audit/) preserves the pre-data frozen auditor, trust and positive/negative fixtures. [raw-replay-first.log](raw-replay-first.log) and its [exit record](raw-replay-first-exit.json) preserve the first successful replay. [provenance.json](provenance.json) maps copied source files/digests. [manifest.json](manifest.json) indexes every archived payload, including logs, excluding itself to avoid recursive hashing.

The official artifact ZIP is2,560,047,031bytes, SHA256 `d1c657249dc0142c78fba54ed82e719cc85cfe34e13fff3973daf46ac34b3255`. [official/](official/) retains GitHub metadata, root READY and all13,460extracted-file hashes. Bulk raw arrays, wheels and build fingerprints remain in the linked CI artifact and are not duplicated into Git. Exact pins/runtime are in provenance.json.

### Lossless preservation of the original Rust log

The archive contains53 byte-identical source copies and one losslessly encoded log. [local-gates/rust.log.json](local-gates/rust.log.json) is a JSON string containing every original UTF-8 byte, including the final blank line. This preserves the evidence without trimming the original log or waiving whitespace checks. Decode it with `json.loads(path.read_text()).encode("utf-8")`; the decoded5,718bytes have SHA256 `3d852d50059b7aab66765a6cb71862a97788c9869f330b788d035da021d1d813`, identical to the untouched source. Nine ordinary `.log` files plus this encoded log preserve all10logs. Provenance records both stored and decoded hashes.

## Original Mac gate label correction

**The original local `no_timing_invocations:true` label is false.** Complete Mac correctness suites included all five legacy pytest-benchmark tests, which execute timers. [LOCAL-GATE-ERRATA.json](LOCAL-GATE-ERRATA.json) and the original additive [local-gates/GATES_COMPLETE-ERRATA.json](local-gates/GATES_COMPLETE-ERRATA.json) correct this explicitly. [The original gate record](local-gates/GATES_COMPLETE.json) is preserved byte-for-byte. Full local logs retain their timer tables; no local timing number is used for performance acceptance.

Local records prove correctness/node accounting and source/wheel identities. They predate CI acceptance, so historical pending/local-only labels remain untouched. Full local coverage was12,476nodes on each of Polars1.20.0/1.44.2/2.1.0, including the five legacy benchmark nodes. Windows fixes and final composition require separate gates. This archive does not claim there were no local timers.

## Replay

Verify the linked official ZIP digest and safely extract it before replay. With NumPy2.5.3 and Polars1.44.2:

```
python audit/audit.py VERIFIED_RAW_ROOT --output replay-result.json
```

The auditor reads retained artifacts only; it never executes a product wheel or imports a repository controller. VERIFIED_RAW_ROOT must contain `mavp-uniform-results` and `wheels`. Synthetic fixtures can run independently of repository configuration:

```
PYTHONDONTWRITEBYTECODE=1 python -m pytest -c /dev/null --noconftest -p no:cacheprovider audit/test_ledger.py audit/test_inputs.py audit/test_boundaries.py audit/test_provenance.py -q
```

This archive does not claim a unique ELF-to-rlib link, allocator-only attribution, cold-path latency, formal significance, universal C parity, or performance of any later combined head. See complete limits in REPORT.md/provenance.json.
