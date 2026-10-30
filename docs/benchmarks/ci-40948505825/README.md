[CI run40948505825](https://github.com/Yvictor/polars_ta_extension/actions/runs/40948505825) · [raw artifact12933856407](https://github.com/Yvictor/polars_ta_extension/actions/runs/40948505825/artifacts/12933856407).

This is the isolated `c852a96daad1a5a8b02bd5e956678c2fd46510f3` component against original `b2bbc26d41ec80823c8bffb0cc436a97f29911cc` and native `56f6d5fb139031c20d86d7e818e7d267eb834295`, not a later combined head.

# Independent ADD output-construction CI audit

Run 40948505825: raw audit PASS; 1080 fresh timed children, 33480 samples, 90 recomputed comparisons.

5 retained physical IPC fixtures independently hashed, decoded and used to derive all ADD/SUB/MULT and cumulative-sum golden outputs. C/prior goldens and full native corpus replayed; candidate timed arrays remain source-bound child pre/post checks.

| Threads | ADD case | Before ns | After ns | Latency change | Faster rounds | Process envelope |
|---:|---|---:|---:|---:|---:|---|
| 1 | add/1000000 | 6381042.500 | 6219191.500 | -2.536% | 8/12 | [0.846838, 1.216429] |
| 1 | grouped_add/100x10000 | 17539619.000 | 16802252.500 | -4.204% | 8/12 | [0.831313, 1.150229] |
| 1 | grouped_add/10000x100 | 82961614.500 | 79769049.500 | -3.848% | 11/12 | [0.934961, 1.207084] |
| 1 | grouped_add/100x10000_interleaved | 25118829.000 | 24681257.000 | -1.742% | 11/12 | [0.915853, 1.220258] |
| 1 | grouped_add/10000x100_interleaved | 91297274.000 | 87375162.500 | -4.296% | 12/12 | [0.972158, 1.174644] |
| 4 | add/1000000 | 4876057.500 | 4758544.500 | -2.410% | 8/12 | [0.939140, 1.176696] |
| 4 | grouped_add/100x10000 | 13268159.000 | 12717789.000 | -4.148% | 10/12 | [0.912224, 1.120663] |
| 4 | grouped_add/10000x100 | 81851206.500 | 78563890.500 | -4.016% | 12/12 | [0.958321, 1.166480] |
| 4 | grouped_add/100x10000_interleaved | 18621700.500 | 18478611.500 | -0.768% | 5/12 | [0.845935, 1.185744] |
| 4 | grouped_add/10000x100_interleaved | 88902876.500 | 85705375.000 | -3.597% | 11/12 | [0.947629, 1.086152] |

Controls (SUB/MULT share the native eligibility branch; cumulative sums use pure Polars):

| Threads | Case | Latency change | Faster rounds | Envelope |
|---:|---|---:|---:|---|
| 1 | sub/1000000 | +1.611% | 3/12 | [0.842778, 1.161210] |
| 1 | grouped_sub/100x10000 | -2.533% | 9/12 | [0.932797, 1.071059] |
| 1 | grouped_sub/10000x100 | -0.591% | 9/12 | [0.977717, 1.052163] |
| 1 | grouped_sub/100x10000_interleaved | -0.061% | 6/12 | [0.945287, 1.095476] |
| 1 | grouped_sub/10000x100_interleaved | -1.792% | 10/12 | [0.977741, 1.043494] |
| 1 | mult/1000000 | +0.741% | 6/12 | [0.938561, 1.061772] |
| 1 | grouped_mult/100x10000 | +1.657% | 4/12 | [0.894591, 1.136043] |
| 1 | grouped_mult/10000x100 | -1.578% | 10/12 | [0.974142, 1.070335] |
| 1 | control_cumsum_dense/1000000 | +0.028% | 3/12 | [0.986546, 1.008286] |
| 1 | control_cumsum/10000x100 | +0.550% | 6/12 | [0.937148, 1.072140] |
| 4 | sub/1000000 | -0.457% | 7/12 | [0.936068, 1.047849] |
| 4 | grouped_sub/100x10000 | -1.363% | 9/12 | [0.941534, 1.143038] |
| 4 | grouped_sub/10000x100 | -0.797% | 8/12 | [0.948896, 1.078927] |
| 4 | grouped_sub/100x10000_interleaved | -1.752% | 8/12 | [0.928594, 1.146658] |
| 4 | grouped_sub/10000x100_interleaved | -0.901% | 7/12 | [0.922225, 1.101893] |
| 4 | mult/1000000 | -1.017% | 6/12 | [0.919179, 1.099537] |
| 4 | grouped_mult/100x10000 | -0.679% | 8/12 | [0.756435, 1.164489] |
| 4 | grouped_mult/10000x100 | -0.631% | 9/12 | [0.930847, 1.121954] |
| 4 | control_cumsum_dense/1000000 | -0.051% | 6/12 | [0.980264, 1.032993] |
| 4 | control_cumsum/10000x100 | +0.397% | 6/12 | [0.881252, 1.208372] |

All 30 slower comparison medians are retained in all-negative-comparisons.csv; 8 candidate-vs-C slower medians in candidate-slower-C.csv. No averaging across controls, thread settings or runners.

Environment:
{
  "1": {
    "cpu": "AMD EPYC 7763 64-Core Processor",
    "platform": "Linux-7.0.0-1017-azure-x86_64-with-glibc2.39",
    "python": "3.12.15",
    "polars": "1.44.2",
    "numpy": "2.5.3",
    "rust": "rustc 1.90.0 (1159e78c4 2025-09-14)",
    "profile": "release (maturin --release --locked), portable CPU target",
    "affinity": [
      0
    ]
  },
  "4": {
    "cpu": "AMD EPYC 7763 64-Core Processor",
    "platform": "Linux-7.0.0-1017-azure-x86_64-with-glibc2.39",
    "python": "3.12.15",
    "polars": "1.44.2",
    "numpy": "2.5.3",
    "rust": "rustc 1.90.0 (1159e78c4 2025-09-14)",
    "profile": "release (maturin --release --locked), portable CPU target",
    "affinity": [
      0,
      1,
      2,
      3
    ]
  }
}

Evidence limits:
- Trust frozen before raw artifact access, after CI measurement completion.
- Raw physical IPC inputs and original/prior golden arrays are replayed independently. Candidate timed-query arrays are not retained: exact pre/post equality and final output are pinned source-bound child self-checks and initial output hashes. Separate full candidate corpus is independently replayed.
- C corpus uses historical tolerance1e-10, integer outputs exact; native corpus requires exact finite/signed-zero/masks/NaN positions. NaN sign/payload not a public guarantee.
- Shared-target Cargo metadata/fingerprints/dependency edges/portable flags are inspected but are not a unique cryptographic ELF-to-linked-rlib bridge; source/wheel binding includes exact actual compile logs and immutable workflow execution.
- Twelve process rounds and correlated inner samples are descriptive, not formal multiple-comparison significance; no pooling thread settings/runners.
- Fault counters cover engine/Python/allocator activity across query threads, not allocator-only events.


Independent retention recommendation: **retain this narrowly scoped ADD route for final composition review**, with modest directional CI evidence and no established latency-speedup claim. This is a judgement from the paired observations and exact correctness/source evidence, not a significance test or a guarantee that each layout improves.

The four short-group ADD observations have 11/12, 12/12, 12/12 and 11/12 favorable matched process ratios (one-thread contiguous/interleaved, four-thread contiguous/interleaved). Their median paired latency shifts are −4.13%, −4.35%, −2.76% and −3.33%; 8–9 of the twelve pairs in each are more than 2% lower. This is a more coherent pattern than a single favorable median, including both physical short-group layouts and both thread settings. The route also removes a concrete complete initialized-output construction/dispatch path, with all retained values, full native corpus and error cases unchanged. These observations support keeping a small, correctness-reviewed ADD-specific change for the final combined candidate.

The weaker cases remain material. Dense ADD is favorable in only 8/12 pairs at each thread setting (median paired latency −2.54%/−3.12%). Long contiguous groups are 8/12 and 10/12 (−2.12%/−2.29%). One-thread long interleaving is 11/12 (−3.66%), but **four-thread long interleaving is only 5/12, with median paired latency +0.68%**, despite its −0.77% ratio-of-medians change. Every primary process envelope overlaps. These data therefore do not establish a latency reduction, and retention must not be described as a universal, formal, or exclusive initialization speedup.

All controls and negative observations are retained. At one thread, five of ten controls have slower medians: dense SUB +1.611%, dense MULT +0.741%, long contiguous MULT +1.657%, dense cumsum +0.028%, grouped cumsum +0.550%. At four threads the only slower control median is grouped cumsum +0.397%; the other shared-branch control medians are lower. Every control envelope overlaps. The very tight dense pure-Polars control (paired shifts around zero) supports examining the repeated short ADD direction, but controls run in separate sequential case blocks and cannot be subtracted to produce an isolated helper cost or normalized speedup. All 30 slower rows across the 90 comparisons and all eight candidate-vs-C slower medians remain in the CSVs; none has a disjoint slower process envelope. The eight residual C-slower medians are SUB/MULT or pure-Polars controls, not ADD.

Same-run C comparison: this EPYC7763 job independently rebuilt C0.8.1, frozen native56 and c852. All ten candidate ADD medians are below C (−0.34% to −8.25%); only four-thread contiguous short ADD has a disjoint faster C envelope. A second disjoint C-faster result is unchanged MULT at one thread, reinforcing that isolated extrema are not an exclusive ADD attribution. Native56's ADD gap to C on this runner is small and changes sign by layout. The older full56 run used different runner execution and **ta.add() defaults HIGH+LOW**; this focused experiment explicitly uses distinct CLOSE+OPEN and adds different interleaved shapes. Its historical gaps must stay separate: no cross-run ratio multiplication, pooling, or decomposition of the older C gap into a measured patch component.

Correctness/provenance: full native56-to-c852 corpus is exact on 10,624 cases/2,167,654 checked non-null values, including matching 191 error cases; no finite/signed-zero mismatch. Historical C corpus uses the declared 1e−10 relative/absolute policy (659 differing floating fields; maximum absolute difference 2.5067947717616335e−11), with zero signed-zero differences. The 60 million retained query-golden values were additionally matched exactly to independent arithmetic/global-or-per-symbol cumulative sums from all five physical IPC fixtures. Candidate timed query arrays are not archived; their pre/final-output equality remains a pinned child self-check rather than a phantom replayed array. Cargo metadata proves inspectable portable dependency graphs, not a unique ELF-to-rlib cryptographic bridge. Final composed-candidate correctness and same-PR CI remain root-owned gates.
