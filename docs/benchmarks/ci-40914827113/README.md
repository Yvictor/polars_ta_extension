# Final56: independent full comparison and remaining C regressions

Run https://github.com/Yvictor/polars_ta_extension/actions/runs/40914827113. Original C `b2bbc26d41ec80823c8bffb0cc436a97f29911cc`; delivered Rust `c71cd6ecb4b48601ff409926fdb0a281505e9fec`; candidate `56f6d5fb139031c20d86d7e818e7d267eb834295`.

Audit PASS: 5,130 fresh selected children, 261,630 samples, 147 one-thread / 138 four-thread cases, six alternating orders. All 285 observations are retained. This final56 run is separate from historical6d and the integer-allocation component experiment; no ratios are multiplied across runs.

{"affinity": [0], "cpu": "AMD EPYC 9V45 96-Core Processor", "diagnostic": true, "numpy": "2.5.3", "platform": "Linux-7.0.0-1017-azure-x86_64-with-glibc2.39", "polars": "1.44.2", "profile": "release (maturin --release --locked), portable CPU target", "python": "3.12.15", "repeats": 51, "rust": "rustc 1.90.0 (1159e78c4 2025-09-14)", "threads": 1, "warmups": 5}

Official artifact [12925433359](https://github.com/Yvictor/polars_ta_extension/actions/runs/40914827113/artifacts/12925433359), ZIP SHA256 `3983afe77ec0e834a527cd6256dcfff5e414648986b668fc15cd6aa99b1945ef`, 3,587,278,276 bytes. Root verified safe extraction of15,460 files. The successful benchmark job ran in attempt1; attempt2 retried only failed cache infrastructure jobs and finished overall SUCCESS at the same56 head. Independent replay read the archived final-attempt REST record and confirmed head/attempt2/success. All15 Polars control envelopes overlap parity; their median changes range−0.865% to+3.784%.

## Correctness and provenance

{"original_vs_candidate": {"cases": 10624, "checked": 2167654, "different": 659, "error_cases": {"ComputeError": 191}, "exact_required": false, "infinite_values": 16123, "max_abs": 2.5067947717616335e-11, "nan_values": 479626, "zero_sign_differences": 0}, "prior_vs_candidate": {"cases": 10624, "checked": 2167654, "different": 0, "error_cases": {"ComputeError": 191}, "exact_required": true, "infinite_values": 16123, "max_abs": 0.0, "nan_values": 479626, "zero_sign_differences": 0}}

Original-to-candidate tolerance is 1e-10; delivered-to-candidate requires exact finite/signed-zero values with matching masks/NaN/infinity positions. NaN sign/payload is not part of the contract. Matching error cases are included in the case inventory. Query original/prior raw goldens, child checks, release wheel/source/ELF identities, all command/process manifests and all timing vectors were replayed independently. Candidate query arrays were not archived; their pre-timer checks are source-audited reports. Full candidate corpus is independently replayed.

## All observations and noise

126 TA/mix8 slower medians; 40 have disjoint slower process-median envelopes; 86 overlap. 15 Polars controls are reported separately. Six rounds with correlated inner samples do not establish formal significance or a universal result. Disjoint envelopes are actionable leads, not confidence intervals. No pooling across thread counts/runners. Fault counters are whole-process, not allocator-only.

```json
{
  "1": {
    "TA_observations": 138,
    "categories": {
      "consistent slower >5% on this runner": 5,
      "consistent small slower on this runner": 17,
      "slow median, process ranges overlap": 36,
      "not slower by median": 80
    },
    "slow_medians": 58,
    "C_envelopes": {
      "slower-disjoint": 22,
      "overlap": 74,
      "faster-disjoint": 42
    },
    "candidate_vs_c71_envelopes": {
      "faster-disjoint": 72,
      "overlap": 66
    },
    "controls": 9
  },
  "4": {
    "TA_observations": 132,
    "categories": {
      "slow median, process ranges overlap": 50,
      "consistent slower >5% on this runner": 4,
      "consistent small slower on this runner": 14,
      "not slower by median": 64
    },
    "slow_medians": 68,
    "C_envelopes": {
      "overlap": 85,
      "slower-disjoint": 18,
      "faster-disjoint": 29
    },
    "candidate_vs_c71_envelopes": {
      "overlap": 89,
      "faster-disjoint": 43
    },
    "controls": 6
  }
}
```

## Largest distinct-family disjoint slower cases

C/c71/candidate values are median milliseconds. Positive change is slower. Ranges contain all six process medians. Controls are shown without subtracting or normalizing timing.

|Threads / case|C / c71 / candidate ms|C / candidate range ms|Candidate vs C|C/candidate envelope|Candidate vs c71|Control change|
|---|---|---|---:|---|---:|---:|
|4t grouped_mavp/100x10000|12.804295 / 22.035443 / 14.653446|[12.762962,12.949032] / [14.534931,14.807168]|+14.442%|0.86194–0.89089|-33.501%|+0.050%|
|1t correl/1000000|7.319428 / 8.986845 / 8.349384|[7.221303,7.380786] / [8.124846,8.562625]|+14.072%|0.84335–0.90842|-7.093%|+0.587%|
|1t var/1000000|4.304283 / 5.090127 / 4.755735|[4.260503,4.339453] / [4.711346,4.925066]|+10.488%|0.86507–0.92106|-6.569%|+0.587%|
|4t add/1000000|3.480970 / 3.860596 / 3.811606|[3.403456,3.651684] / [3.702902,3.968000]|+9.498%|0.85773–0.98617|-1.269%|-0.842%|
|4t grouped_sarext/2000x100_interleaved|13.099021 / 16.394981 / 14.181051|[13.053705,13.512768] / [13.840998,14.293443]|+8.260%|0.91327–0.97629|-13.504%|+3.784%|
|4t grouped_stddev/1000x1000|8.752626 / 9.553619 / 9.417010|[8.470212,8.900574] / [9.264738,9.545514]|+7.591%|0.88735–0.96069|-1.430%|-0.865%|
|4t cmou/1000000|13.041666 / 14.177058 / 13.874460|[12.592676,13.247120] / [13.762015,14.035848]|+6.386%|0.89718–0.96259|-2.134%|-0.842%|
|1t hma/1000000|5.666828 / 6.081605 / 5.977703|[5.569786,5.788206] / [5.832837,6.204433]|+5.486%|0.89771–0.99235|-1.708%|+0.587%|
|1t grouped_bbands/100x10000|14.193623 / 15.038691 / 14.966048|[13.793116,14.425714] / [14.748402,15.098674]|+5.442%|0.91353–0.97812|-0.483%|+1.462%|
|1t grouped_macd/1000x1000|23.340100 / 24.679859 / 24.513098|[22.966328,23.534302] / [23.693482,25.947980]|+5.026%|0.88509–0.99328|-0.676%|-0.740%|

## Full family inventory

|Family|1t slow / disjoint / worst%|4t slow / disjoint / worst%|
|---|---|---|
|add|1 / 1 / +8.335%|3 / 1 / +9.498%|
|adx|0 / 0 / -8.019%|0 / 0 / -3.937%|
|atr|2 / 0 / +3.246%|2 / 0 / +2.066%|
|bbands|6 / 2 / +6.575%|5 / 1 / +5.420%|
|cci|0 / 0 / -10.377%|0 / 0 / -4.292%|
|cdldoji|0 / 0 / -2.839%|0 / 0 / -2.225%|
|cmou|4 / 2 / +5.743%|5 / 2 / +6.386%|
|correl|4 / 4 / +14.072%|4 / 3 / +13.486%|
|ema|0 / 0 / -1.049%|3 / 1 / +3.989%|
|hma|4 / 1 / +5.486%|5 / 2 / +5.140%|
|macd|6 / 2 / +5.026%|4 / 0 / +7.499%|
|mavp|5 / 2 / +12.927%|6 / 1 / +14.442%|
|mavp_fixed|2 / 0 / +2.462%|1 / 0 / +2.953%|
|minmaxindex|4 / 0 / +2.751%|5 / 0 / +17.128%|
|mix8|0 / 0 / -3.206%|0 / 0 / -1.599%|
|ppo|0 / 0 / -1.359%|2 / 0 / +0.696%|
|rsi|1 / 0 / +2.203%|4 / 0 / +1.889%|
|sarext|6 / 5 / +6.958%|6 / 3 / +8.260%|
|stddev|6 / 1 / +6.324%|6 / 2 / +7.591%|
|supertrend|1 / 0 / +0.607%|1 / 0 / +0.828%|
|var|6 / 2 / +10.488%|5 / 2 / +8.185%|
|vwma|0 / 0 / -2.290%|1 / 0 / +0.383%|

## Limits

- Six rounds and correlated inner samples; descriptive ranges are not confidence intervals or multiple-comparison significance.
- Original/prior query goldens and child self-check reports are retained; candidate query arrays are not. Separate full candidate corpus is replayed independently.
- Immutable local Git objects verify source fingerprints; external dependency archives and separately linked consumer Rust rlibs are not archived. Wheel native libraries and Python sources are directly hashed.
- Profile evidence comes from workflow/source, release logs and self-reports, not a complete captured process environment or assembly audit.
- No pooling across thread counts/runners. Fault counters are process-wide, not allocator-only.
- Full NPZ corpus metadata has no commit/native ELF hash. Corpus-to-wheel binding relies on immutable workflow/CI execution provenance, not a per-capture ELF identity field.
- Original C comparison uses its historical tolerance policy; any C-to-native signed-zero differences are explicitly counted, not silently claimed identical. Prior-to-candidate signed zeros remain strict.
