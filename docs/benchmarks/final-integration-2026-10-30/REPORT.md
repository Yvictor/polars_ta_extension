# Final composed source: local correctness verification

Source head: `97aeffb91a648f792f3c6689c5967e2dd0a14051`. Head at completion: `97aeffb91a648f792f3c6689c5967e2dd0a14051`. No product source, Git or remote mutation was performed by this verification. Parent-owned documentation work remains untouched. All selected runtime and verification file sets and bytes are unchanged before build, after build and after all gates.

## Actual results

- Release Rust suite: **46 passed,1ignored**. The ignored test is a diagnostic probe, not silently counted as executed.
- One release wheel built using `maturin build --release --offline --locked`; that same wheel was force-installed into all3private runtimes.
- Complete command `python -m pytest -q tests` passed **12,479tests on each runtime**, including all5legacy pytest-benchmark tests. Their timers executed as part of correctness verification; no local timing is used for a performance conclusion.

| Polars | Passed | Private runtime |
| --- | ---: | --- |
| 1.20.0 | 12479 | `/tmp/polars-recovery/mavp-uniform-polars120` |
| 1.44.2 | 12479 | `/tmp/polars-recovery/mavp-uniform-env` |
| 2.1.0 | 12479 | `/tmp/polars-recovery/mavp-uniform-polars21` |

Exact collected node IDs account for11,975baseline0eb nodes,501new uniform nodes,2old signed-zero IDs replaced by4load-average variants, and1new capture test:12,479total. No other baseline nodes were removed. A CI command excluding tests/test_bench.py has12,474expected nodes; it must not be described as the complete12,479suite.

- Full capture: **10,624cases /2,167,654values**. OriginalC comparison:0failures,657finite fields differ within the existing declared tolerance, maximum absolute difference2.1543655748246238e-11.
- Exact comparisons against both0eb and916:0failures,0finite differences. **All26,351capture arrays, including metadata, are byte-identical** to both references.
- Strict IEEE supplement: no both-zero sign differences and no NaN-word differences. OriginalC retains3zero-versus-tiny-finite positions within the declared finite tolerance; this is not a zero-position equivalence claim. Native0eb/916have no such differences.
- Frozen real-option fixture hashes match their retained C-reference manifest. The reference JSON hasLFbytes and noCRLF.

## Source, build and installed binary binding

Runtime fingerprint(55files): `182e8e8a684676c3c1d0f69df383051e3c746cda87028bb266e278b29aa3ba3a`.
Verification fingerprint(63files): `20f6ac992916d4ea30da4876a8c192ad29785c15b1107581ff144d56cb41e53d`.
Algorithm and per-file mappings are retained in SOURCE_FINGERPRINTS.json and source-before.json. The complete before/after source manifest SHA256is `3d7a4422179956709f0fb6968dcaaa97f31714b12740b13453210b8856b4e00b`.

Wheel SHA256: `d7982d6ea7b13e11f923b5d6b2dc82fc5c0ac38bfc7a63f299e0f29cb37e233a`.
Native module SHA256, identical in all3installed runtimes: `9a919626915cda3a2e1fe2e42a8a6fbe254fb233abe41cec1ef6cd3084d0bb11`. It also equals the previously validated916native binary; wheel ZIP bytes have their own new hash.

Local runtime: Python3.12.14, NumPy2.5.3, original reference C0.8.1. The exact versions, prefixes and installed paths are in installed-provenance.json. Rust1.90.0verbose provenance and all process-local compiler/Cargo settings are retained. Existing private uniform targets/builddirs/envs were reused; global Cargo configuration was not changed.

The recorded build commands were `cargo test --release --offline --locked --lib -- --test-threads=1` and the single release maturin command. Build-commands.json retains their complete paths and environment, including private CARGO_HOME/target/build paths, releaseO3/cgu16/ltofalse/debugfalse, empty RUSTFLAGS and the private PYO3interpreter.

## Verification-side issues and independent review

Two verification-side issues were preserved and corrected without product changes or repeating completed stages:

1. After successful C/native comparison reports, an extra raw-array diagnostic wrongly required the originalC metadata Unicode storage width to equal native metadata. Independent review verified equal normalized cases, schema, field order, errors and APIcontracts/APIsets. The approved resume exempts only that literal originalC metadata representation; every numerical dtype/shape/mask/IEEE check remains strict, and native metadata remains byte-exact.
2. After all remaining gates and after-source checks passed, the resumed script's summary writer lacked its `refhash` variable. An independently reviewed record-only writer consumed retained successful reports and hashes to finish GATES_COMPLETE.json. No build, install, capture, numerical comparison or test suite was repeated.

Both failed scripts/logs and their hashes remain available; verification-resume-provenance.json records the first correction. GATES_COMPLETE.json records both stops and the record-only completion. Independent final source/API/concurrency/CPU/unsafe composition review approved97with no product finding; the reviewer also independently ran14allocation/portability tests. independent-review.json retains the review scope and frozen script hashes.

These are **local correctness results**, not CI performance acceptance or proof of cross-platform bit equivalence. Parent owns final-head CI, same-runner benchmark evidence, remaining C regressions, Windows execution and publication. No merge or release occurred.
