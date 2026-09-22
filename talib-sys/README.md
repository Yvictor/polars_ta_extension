# talib-sys

Raw Rust FFI bindings for the [TA-Lib](https://ta-lib.org) C library,
generated with rust-bindgen.

The build script downloads and compiles the bundled TA-Lib version
(see `TA_LIB_VER` in `build.rs`) as a static library unless an existing
installation is provided through `TA_LIBRARY_PATH` / `TA_INCLUDE_PATH`.

`src/bindings.rs` is committed and portable. Regenerate it after bumping
the bundled version with:

```bash
cargo build -p talib-sys --features bindgen
```
