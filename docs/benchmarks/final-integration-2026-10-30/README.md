# Final97 local correctness verification

This is a concise **local correctness** archive for runtime source `97aeffb91a648f792f3c6689c5967e2dd0a14051`. Final-head CI and controlled CI performance evidence are separate and pending; this archive is not a speedup claim or proof of Windows execution. A subsequent pytest discovery configuration change is separately bound in TEST-DISCOVERY-SUPPLEMENT.json. The final tree is configuration plus documentation; the original55/63snapshots exclude pyproject.toml and do not prove whole-project byte identity.

- Release Rust: **46passed,1ignored**.
- Complete `python -m pytest -q tests`: **12,479passed on each Polars1.20.0/1.44.2/2.1.0**. All5legacy pytest-benchmark tests executed timers; their local timings support no performance conclusion.
- Full10,624case/2,167,654value capture: originalC0.8.1comparison passes the declared tolerance;657finite fields differ, maximum absolute difference2.1543655748246238e-11. Three existing zero-versus-tiny-finite positions remain; no both-zero sign or NaN-word difference was found. This is not full C bit or zero-position equivalence.
- All26,351capture arrays, including metadata, are byte-identical to both0eb and916native references.
- All55runtime and63verification file hashes and file sets remained unchanged through the build and all gates.

WheelSHA256: `d7982d6ea7b13e11f923b5d6b2dc82fc5c0ac38bfc7a63f299e0f29cb37e233a`. NativeSO SHA256 in all3private runtimes: `9a919626915cda3a2e1fe2e42a8a6fbe254fb233abe41cec1ef6cd3084d0bb11`. Runtime fingerprint: `182e8e8a684676c3c1d0f69df383051e3c746cda87028bb266e278b29aa3ba3a`. See SOURCE_FINGERPRINTS.json for the canonical hashing algorithm and source-before.json for every file hash.

REPORT.md and the original JSON records listed as byte-identical copies in manifest.json are preserved exactly. commands-and-exits.json combines the exact15existing successful stage command records; node-inventory-summary.json preserves counts and exact portability replacements without copying full node lists. The accounting is11,975baseline+501uniform+3net portability=12,479; CI commands excluding tests/test_bench.py have12,474expected tests and must be labelled accordingly.

Two verification-side script stops were preserved honestly: an overstrict originalC metadata Unicode-width assertion after successful API/schema/numerical comparisons, and a missing `refhash` name while writing the final record **after all remaining gates passed**. Independent review approved the narrow metadata-only correction and a record-only completion writer. These were not product failures, changed tolerances, or repeated builds/tests/captures. GATES_COMPLETE.json and independent-review.json retain the disposition; private-evidence-index.json identifies the excluded original scripts and logs by path and hash.

Large captures, wheels, native binaries, complete node lists and logs are **not copied here**. Their original private files remain intact; hashes and private executor paths are in private-evidence-index.json. Do not interpret those pointers as downloadable or in-repository artifacts. The final public CI evidence must be checked separately.

## Default pytest discovery and archived auditor fixtures

The only new configuration is `[tool.pytest.ini_options] testpaths = ["tests"]`. It makes default collection match the existing explicit CI product-suite selection. All3private runtimes collect exactly the same ordered12,479node IDs as the already executed full suites, including all5legacy benchmark tests; no product test is removed. This is collection-equivalence evidence, not another full-suite execution.

Before this configuration, default root collection also included37historical auditor fixtures from documentation. Combining those independent snapshots in one process produced5failures from their generic `inputs` module-name collision. Their original bytes are preserved. Select each historical auditor explicitly in a separate fresh Python process, for example:

```sh
python -m pytest --noconftest -q docs/benchmarks/ci-40965216581/audit
python -m pytest --noconftest -q docs/benchmarks/ci-40970023623/audit
```

The separate-process guidance does not modify frozen imports or claim these commands were rerun for this fix. TEST-DISCOVERY-SUPPLEMENT.json retains the before/after pyproject hashes, parsed-setting equality proof, default-collection log hashes and exact source-snapshot scope. Project/build/dependency/maturin/ruff settings are unchanged; no new wheel-byte equality or post-configuration numerical execution is claimed. Final CI must rebuild the actual configuration.
