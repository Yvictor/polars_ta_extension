# talib-sys 0.2.0

Raw Rust bindings for TA-Lib 0.8.1. The pinned, SHA-256-verified upstream source
is bundled and compiled statically with CMake for the Cargo target. No system
TA-Lib or libclang installation is needed for ordinary builds.

Building requires a C/C++ toolchain and CMake 3.30+. The optional
`regenerate-bindings` feature requires libclang and writes regenerated bindings
to Cargo's `OUT_DIR`; it never modifies checked-in source files.

See the repository's `docs/upgrade-0.2.0.md` for supported platforms and migration
notes. The upstream license is included in `vendor/TA-Lib-LICENSE`.
