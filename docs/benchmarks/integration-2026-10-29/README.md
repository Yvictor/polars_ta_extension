# Combined migration candidate: correctness and pending full CI

The compiled product source is `3ed5d1ad60214cfe5d2dc074340b1feffa2c4904`. This composition retains the reviewed ADD initialized-output path, ENGULF checked window and selected-MAVP SMA iterator change. It includes the typed SAREXT decoder and licensed signed-zero-compatible scalar body with public CPU multiversion dispatch. Ordinary Polars expressions and native `.over()` remain the public API. The rejected guard-fusion experiment is not integrated. Borrowed Arrow Float64 inputs were already present before this work.

On the authorized Apple arm64 Mac, Rust1.90 release and Python3.12.14, the final composition passed45Rust tests (one ignored cost diagnostic) and all11,975Python tests separately on Polars1.20.0,1.44.2 and2.1.0. The10,624-case corpus checks2,167,654values and matching schemas, field order, dtypes, masks, padding and errors. It matches delivered56 exactly for finite values, signed zeros and null/NaN/Inf positions; NaN representation is outside that contract. Against the original C wheel on the same Mac,657finite fields differ within the declared1e-10 policy, maximum absolute2.1543655748246238e-11. Newly added SAREXT short-zero/cancellation and legitimate long-negative-zero fixtures are strict C checks; they extend the historical corpus. This finite matrix is not every possible argument combination.

Independent review found no blocking API, lifetime, arithmetic-order or concurrency defect in the composition. It corrected a misleading architecture sentence and a test-harness false acceptance of opposite signed zeros. The tolerant finite lane now independently rejects opposite signs when both values are zero; zero versus a tiny nonzero finite value remains governed by the disclosed numerical tolerance. Two real-query tests prove both signed-zero mismatch directions fail before any timer starts.

The final full285scenario CI comparison is required on this composition. It rebuilds original C `b2bbc26d41ec80823c8bffb0cc436a97f29911cc`, delivered Rust `56f6d5fb139031c20d86d7e818e7d267eb834295`, and the candidate in the same job. The original baseline and six balanced arm orders remain unchanged; the previous full report againstc71 remains historical and is not pooled with this run. Component reports linked below are evidence for isolated changes, not combined-head performance.

- [Full delivered56 inventory](../ci-40914827113/README.md) retains all285observations and unresolved C regressions.
- [ENGULF component](../ci-40942396197/README.md) establishes dense improvements; grouped comparisons overlap.
- [ADD component](../ci-40948505825/README.md) is qualified directional evidence with overlapping ranges.
- [MAVP component](../ci-40955158880/REPORT.md) has four narrow disjoint improvements, no broad `.over()` claim, and explicitly lists remaining C gaps.
- [Rejected guard fusion](../ci-40947137365/README.md) preserves all negative findings; no fused guard code is shipped.

SAREXT four-arm CI and upstream SAR/SAREXT kernel CI run independently; their actual Linux product proof and runtime conclusions remain pending at source freeze. No speedup, universal C parity or final CI success is claimed from these local correctness checks. See the hash manifest for source/wheel/installed-library binding.
