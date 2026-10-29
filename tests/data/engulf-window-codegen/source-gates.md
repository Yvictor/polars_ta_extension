# Safe Engulfing window candidate

Base433; current officialmainccd has identical canonical Engulf, generated Rust Engulf and relevant Rust renderer/window files. No upstream duplicate fix in those paths.

The renderer recognizes a total decision tree that writes the same integer out[index++] in every leaf. It requires two same-length inputs read only at current/previous bar, boolean conditions, integer-only leaves, one unconditional counter step and no other effects or index-dependent values. Existing checked windows and the original fallback perform all bounds/error behavior. Canonical C, guards, stream code, APIs, arithmetic and comparison order remain unchanged. Bare generation changes only the Rust Engulfing batch body.

Matched Rust1.97 x86 postThinLTO demonstrates a bounds-free window loop; whole implementation750→1097B with preserved fallback, public wrapper324B unchanged. Per-call entry checks remain. No speed claim: extra entry work and code size need same-runner CI. See expanded-cfg-proof.md and raw objects for branch targets and retained panic blocks.

Gates: generator517unit+624integration(1docignored), library105tests plus final3focused contracts, both strict all-target Clippy, C237/Rust237 codegen parity, Engulf294Rust hashcases/285rideverdicts with0mismatches. Final full regeneration changes none of2641tracked files. The three public contracts exercise28561IEEE two-bar combinations with all five signed hit classes, partialranges/offset slices/canaries and four-component OHLC/error/empty-output validation.

Sources and logs are bound in source-gates.json. Earlier /Volumes artifacts are inaccessible; these baseline/candidate/static/correctness results were rebuilt in /tmp. The C reference here is current433 0.8.4, distinguished from original0.8.1 in the CI diagnostic. No local benchmark, consumer modification or publication occurred.
