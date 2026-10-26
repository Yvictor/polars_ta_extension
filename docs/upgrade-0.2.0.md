# Upgrading to 0.2.0

## 0.2.1

- **Null inputs no longer become indicator values (issue #42).** Nulls reach
  TA-Lib as NaN, its results for NaN are undefined, and TA-Lib 0.8.1 turns them
  into finite numbers for several indicators: RSI returned 0.0 for every row
  after a null. A null input after the first usable row now nulls every output
  row that can depend on it. That is the rest of the partition for recursive
  indicators, and `lookback` rows for window-bounded ones. Rows that do not
  depend on a null are unchanged. See [missing inputs](#missing-inputs).
- **Polars 2 (issue #41).** The dependency is now `polars>=1.20,<3`; CI tests
  Polars 1.20, 1.44 and 2.0.

`polars-talib` is version 0.2.1; the `talib` and `talib-sys` crates remain
0.2.0. Everything below applies to both 0.2.0 and 0.2.1.

## 0.2.0

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
integer outputs. All multi-input plugins
broadcast length-one inputs to the other inputs' length, including zero rows.
Other length mismatches raise a Polars error before C sees any pointers.

New functions include AC, ACCBANDS, ADR, AO, AVGDEV, CMF, CMOU, COPPOCK,
CUMSUM, CVI, DONCHIAN, DPO, EFI, ER, ERI, FOSC, FRACTAL, HA, HMA, IMI, KC,
KDJ, MARKETFI, MASSI, NVI, PERCENTILE, PERCENTRANK, PVI, PVO, PVT, QSTICK,
RMA, RVI, RVOL, SMI, SUPERTREND, TSI, VHF, VORTEX, VWAP, VWMA, WAD and
ZLEMA. Use `get_functions_output_struct()` for multi-output field names;
SuperTrend contains Float64 `supertrend` and Int32 `trend` fields, and Fractal
returns two Int32 fields.

## Missing inputs

A Polars null is a missing observation. TA-Lib has no notion of missing values
and does not detect or support non-finite inputs: their results are undefined.
From 0.2.1:

- Leading rows where any input is null or NaN are skipped. Output starts after
  the usual warm-up from the first usable row; warm-up rows are NaN (floating)
  or 0 (integer).
- After the first usable row, a null input nulls every output row that can
  depend on it. Recursive and path-dependent indicators (RSI, EMA, MACD, ATR,
  OBV, SAR, SMA and other running-sum implementations, most candlestick patterns,
  ...) are null from the missing row to the end of the partition. Window-bounded
  indicators (MAX/MIN, WILLR, AROON, ROC/MOM, math operators and transforms, ...)
  are null for the missing row and the next `lookback` rows, then recover.
- Struct outputs are masked field by field; the struct itself is never null.
- The mask is computed per call, so under `.over(...)` or
  `group_by(...).agg(...)` a null only affects its own partition.
- NaN and +/-inf are ordinary float values in Polars and are passed to TA-Lib
  unchanged, with upstream's undefined results. Convert them with
  `pl.col("close").fill_nan(None)` when they mean "missing". Checking null counts
  is free, so data without nulls pays nothing for this policy.

`python/polars_talib/_missing.py` lists the window-bounded indicators. It is
generated by `scripts/classify_missing.py`, which measures every indicator: an
indicator is window-bounded only when perturbing one input row, or setting it to
NaN (what TA-Lib receives for a null), changes no output outside that row's
lookback window for every moving-average type. Tests check the committed list
against fresh measurements, check the exact masked rows of every indicator for a
null input, and check that NaN and +/-inf inputs reach TA-Lib unchanged.

There is no implicit imputation. To restart an indicator after each gap, add the
gap count to the partition: `.over("symbol", pl.col("close").is_null().cum_sum())`.
To compute over observed rows only, for example when one instrument is closed on
a date other instruments trade, drop the missing rows within each symbol before
computing and join the result back by timestamp.

## Platforms and build requirements

Python requires CPython 3.10+ and Polars `>=1.20,<3`. CI tests Polars 1.20.0,
1.44.2 and 2.0.0 against Python 3.10, 3.11, 3.13 and 3.14, and Python 3.12
with Polars 1.44.2 on every wheel platform.

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

The native Rust migration replaces the C build with the pinned official `ta-lib`
crate. See [native migration](native-rust-migration.md) for source-build commands,
compatibility paths, ordinary `.over()` execution boundaries, and CI evidence.
The release history and changes above describe the prior 0.2.x C releases.

## Maintaining the generated API

`scripts/api.json` is the frozen 201-function public contract from TA-Lib 0.8.1.
`scripts/plugin_abi.json` preserves each plugin's input permutation and Struct
field names. The 0.8.3 crate contains more indicators; expanding this inventory
is a separate API change. Regenerate stable wrappers and reference files with:

```sh
python scripts/generate_indicators.py
python scripts/generate_skill_reference.py
```

The wrapper generator needs `rustfmt`. All plugin symbols now share the native
adapter; Python signatures and defaults remain frozen. `scripts/extract_api.py`
is retained only as a tool for auditing the historical C API, not for native builds.

## Publishing a release

Bump the version in `pyproject.toml` and `Cargo.toml`, add
`.github/release-notes/<version>.md` in the same pull request, and merge it.
The CI run on master then runs every test job and, when that version has no tag
yet, creates the tag and GitHub release from the notes file and uploads the
tested wheels and sdist to PyPI. Pushing a tag equal to the version still works
too. Merges without a notes file for an untagged version publish nothing.

See [AI skill installation](skills.md) and [benchmark methodology/results](performance.md).
