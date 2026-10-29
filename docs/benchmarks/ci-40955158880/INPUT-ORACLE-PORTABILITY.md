# Exact retained input regeneration across architectures

The approved pre-timing audit stopped at the physical-input provenance gate. No timing statistics had been read. All retained close arrays matched the local seeded NumPy2.5.3 generator exactly, but ARM `Generator.uniform(100,1000,n)` differed from the measured Linux volume values by one ULP at78,248/1,000,000 rows (15,443/200,000).

Explicitly consuming the same RNG state with `random(n)` and applying the globally unfused vector operations `100. +900. *unit` reproduces every volume bit in all16 retained physical snapshots. Explicit correctly-rounded fused `fma(900,unit,100)` reproduces the local ARM uniform policy and differs at exactly those rows. The diagnostic JSON records every physical snapshot. Tests independently use Decimal to demonstrate three exact fused/unfused IEEE examples.

The corrected input oracle requires the exact unfused Linux policy globally. It does not use a tolerance, choose a policy per element, or change product-output correctness requirements. Self-consistent seeded-volume corruption by0.001 is rejected and differs from both policies. The original approved shared comparison core is unchanged; C both-zero signs are enforced by the reviewed local wrapper.

This narrow oracle correction was made after examining retained input/corpus/provenance data and before examining any timings. It requires a second independent review before the full audit resumes.
