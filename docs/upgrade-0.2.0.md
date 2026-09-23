# Upgrading to 0.2.0

`polars-talib`, `talib` and `talib-sys` are version 0.2.0. The bundled C library
is [TA-Lib 0.8.1](https://github.com/TA-Lib/ta-lib/releases/tag/v0.8.1).
There are 201 batch indicators: the previous 158 plus 43 additions.
Both the top-level Python functions and `.ta` namespace support the additions.
The generated Rust slice APIs are in `talib::generated`; the raw C bindings also
include upstream's streaming API. The Python Polars API remains batch-oriented.

## Behavior changes

| Parameter | Previous wrapper default | 0.2.0 / upstream default |
| --- | --- | --- |
| BBANDS `timeperiod` | 5 | 20 |
| APO / PPO `matype` | 0 (SMA) | 1 (EMA) |
| CDLDARKCLOUDCOVER / CDLMATHOLD `penetration` | 0.3 | 0.5 |

Pass the old values explicitly to retain those parameter choices. Upstream also
fixes numerical bugs and uses fused operations; rounding and some edge cases will
change even with explicit parameters. Compare results with tolerances appropriate
to the indicator, not byte equality against a 0.4.0 library. Tests in this project
use the official Python `TA-Lib==0.8.1` wheel as the independent reference.

`MA_Type` exposes SMA, EMA, WMA, DEMA, TEMA, TRIMA, KAMA, MAMA, T3, HMA,
DISABLED, DEFAULT, ZLEMA and RMA. Integer values remain accepted. Integer
parameters such as `timeperiod` accept integers, NumPy integers and whole-number
floats such as `14.0` (issue #6), matching the upstream Python wrapper. Strings,
`None` and `bool` raise an explicit Python `TypeError` before plugin
serialization; fractional or non-finite values such as `14.5` raise `ValueError`
instead of being truncated silently, as do integer range violations.

The package ships a `py.typed` marker and every `.ta` namespace method is a
class attribute, so static type checkers and editors resolve all 201 methods.
`polars_talib.col("close").ema(5)` is a typed alternative to
`pl.col("close").ta.ema(5)` (issue #28); it accepts a column name or any
expression and returns the same `TAExpr` namespace.

Empty inputs return empty outputs. Inputs shorter than lookback and all-missing
inputs retain their original length, with NaN for floating outputs and zero for
integer outputs. Nulls convert to NaN. Internal NaNs follow upstream behavior;
there is no implicit imputation or session reset. All multi-input plugins
broadcast length-one inputs to the other inputs' length, including zero rows.
Other length mismatches raise a Polars error before C sees any pointers.

New functions include AC, ACCBANDS, ADR, AO, AVGDEV, CMF, CMOU, COPPOCK,
CUMSUM, CVI, DONCHIAN, DPO, EFI, ER, ERI, FOSC, FRACTAL, HA, HMA, IMI, KC,
KDJ, MARKETFI, MASSI, NVI, PERCENTILE, PERCENTRANK, PVI, PVO, PVT, QSTICK,
RMA, RVI, RVOL, SMI, SUPERTREND, TSI, VHF, VORTEX, VWAP, VWMA, WAD and
ZLEMA. Use `get_functions_output_struct()` for multi-output field names;
SuperTrend contains Float64 `supertrend` and Int32 `trend` fields, and Fractal
returns two Int32 fields.

## Platforms and build requirements

Python requires CPython 3.10+ and Polars `>=1.20,<2`. CI tests the minimum and
current Polars release against Python 3.10, 3.11, 3.12, 3.13 and 3.14.

| Wheel platform | Architectures | Runtime validation |
| --- | --- | --- |
| Linux glibc 2.28+ | x86_64, aarch64 | Native Ubuntu runners |
| Linux musl 1.2+ | x86_64, aarch64 | Native Alpine containers |
| macOS | Intel, Apple Silicon | Native macOS runners |
| Windows | x64, ARM64 | Native Windows runners |

These are the tested wheel targets, not a claim about every operating system.
Windows wheels use MSVC; MinGW builds are not covered by the support matrix.
32-bit Windows, PyPy and Python <3.10 are no longer claimed as supported: the
current Polars runtime and the test dependency matrix do not support that set.
CI status on the PR is the authority for whether a target has actually passed.

Wheels statically include TA-Lib and require no system TA-Lib, libclang or
separate Python TA-Lib installation. This replaces the dynamic linking behind the
`_TA_ACOS` (macOS Intel, issue #24) and `TA_CDL3BLACKCROWS_Lookback` (Linux
AArch64, issue #36) import failures of the 0.1.x wheels; a test checks that the
extension module names no TA-Lib shared library. By default the build compiles
the pinned, checksum-verified source so headers and library can never mismatch
(issue #26).
Packagers who must link a system TA-Lib 0.8.1 can set both `TA_LIBRARY_PATH`
(directory with `libta-lib.a` / `ta-lib-static.lib`) and `TA_INCLUDE_PATH`
(directory containing the five public headers under `ta-lib/`). Both variables
are required together. The build checks those headers against the pinned archive;
the extension also checks the linked library's version when imported. Use the
matching static library, compiled with PIC on Unix. Official wheels always use
the vendored build. `DEPS_PATH` is no longer used.

For a source build install Rust (CI uses 1.90.0), a C/C++ build toolchain, CMake
and Python. Upstream's CMake project needs CMake 3.18+ on Linux/macOS and 3.30+
on Windows (Visual Studio 2026 requires CMake 4.2+). Then:

```sh
python -m pip install maturin
maturin build --release --locked --out dist
python -m pip install dist/*.whl
```

The upstream source archive is included in the sdist and Rust crate, together
with its license. The build verifies SHA-256
`ec59ccd88c0c77f618587d858787c8f9d06c40460a09d66751926f6fd670f985` and builds in
Cargo's `OUT_DIR`. It never downloads TA-Lib or writes generated files into the
source tree. Cargo/Python dependencies still need an available package cache or
network access. Published wheels use portable CPU targets, not `-march=native`
or `-ffast-math`.

## Maintaining the generated API

`scripts/api.json` records all upstream batch signatures, groups, defaults and
outputs. To regenerate it, compile upstream 0.8.1 as a shared library and run:

```sh
python scripts/extract_api.py /path/to/ta-lib-0.8.1 /path/to/libta-lib.so
python scripts/generate_indicators.py
python scripts/generate_skill_reference.py
```

The wrapper generator needs `rustfmt`. CI checks wrappers and the skill reference
for drift. It generates the 43 added APIs; the 158 legacy APIs retain their
existing Python signatures and Rust builder types. Migrating those public APIs
to generation needs a separate compatibility review. Both paths share input
broadcasting; the 201-function parity suite covers their behavior.
For FFI bindings, install libclang and build
`cargo build --manifest-path talib-sys/Cargo.toml --features regenerate-bindings`.
Review and copy the resulting `OUT_DIR/bindings.rs` into
`talib-sys/src/bindings.rs`; default builds use these portable checked-in bindings.

## Publishing a release

Either push a tag equal to the `pyproject.toml` version, or run the CI workflow
manually on `master` with the `release_tag` input set to that version. A manual
run builds and tests every wheel, then creates the tag and GitHub release from
`.github/release-notes/<tag>.md` (falling back to GitHub's generated notes) and
uploads the tested wheels and sdist to PyPI. Both paths refuse a tag that does
not match the package version, and re-running a partially completed publish
skips the release and files that already exist.

See [AI skill installation](skills.md) and [benchmark methodology/results](performance.md).
