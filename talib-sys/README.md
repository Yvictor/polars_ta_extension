# talib-sys 0.2.0

Raw Rust bindings for TA-Lib 0.8.1. The pinned, SHA-256-verified upstream source
is bundled and compiled statically with CMake for the Cargo target. No system
TA-Lib or libclang installation is needed for ordinary builds.

Building requires a C/C++ toolchain and CMake 3.18+ (3.30+ on Windows, which
upstream's CMakeLists enforces). Set `TA_LIBRARY_PATH` and `TA_INCLUDE_PATH` to
link an existing TA-Lib 0.8.1 static library instead of compiling the vendored
sources. Both paths must be set together; all five public headers must match
the pinned archive. The Python extension verifies the library version on import.
Raw Rust consumers must likewise use the matching library. The optional
`regenerate-bindings` feature requires libclang and writes regenerated bindings
to Cargo's `OUT_DIR`; it never modifies checked-in source files.

See the repository's `docs/upgrade-0.2.0.md` for supported platforms and migration
notes. The upstream license is included in `vendor/TA-Lib-LICENSE`.
