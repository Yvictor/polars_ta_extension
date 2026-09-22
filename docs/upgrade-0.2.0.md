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
DISABLED, DEFAULT, ZLEMA and RMA. Integer values remain accepted.

Empty inputs return empty outputs. Inputs shorter than lookback and all-missing
inputs retain their original length, with NaN for floating outputs and zero for
integer outputs. Nulls convert to NaN. Internal NaNs follow upstream behavior;
there is no implicit imputation or session reset. Inputs to legacy multi-input
plugins must have equal lengths; mismatches raise a Polars error before C sees
any pointers. New indicators additionally support broadcasting scalar inputs.

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
32-bit Windows, PyPy and Python <3.10 are no longer claimed as supported: the
current Polars runtime and the test dependency matrix do not support that set.
CI status on the PR is the authority for whether a target has actually passed.

Wheels statically include TA-Lib and require no system TA-Lib, libclang or
separate Python TA-Lib installation. Old `DEPS_PATH`, `TA_LIBRARY_PATH` and
`TA_INCLUDE_PATH` overrides are no longer used: one pinned source and matching
headers avoid accidental version/ABI mixing (issue #26).

For a source build install Rust (CI uses 1.90.0), a C/C++ build toolchain, CMake
3.30+ and Python (Visual Studio 2026 requires CMake 4.2+). Then:

```sh
python -m pip install maturin
maturin build --release --locked
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
```

The second command needs `rustfmt`. CI checks generated wrappers are unchanged.
For FFI bindings, install libclang and build
`cargo build --manifest-path talib-sys/Cargo.toml --features regenerate-bindings`.
Review and copy the resulting `OUT_DIR/bindings.rs` into
`talib-sys/src/bindings.rs`; default builds use these portable checked-in bindings.

See [AI skill installation](skills.md) and [benchmark methodology/results](performance.md).
