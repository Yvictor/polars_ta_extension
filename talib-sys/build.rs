use sha2::{Digest, Sha256};
use std::{env, fs, path::PathBuf};

const VERSION: &str = "0.8.1";
const SHA256: &str = "ec59ccd88c0c77f618587d858787c8f9d06c40460a09d66751926f6fd670f985";

/// Static library file name produced by upstream's CMake build for this target.
fn static_lib_name(windows: bool) -> &'static str {
    if windows {
        "ta-lib-static"
    } else {
        "ta-lib"
    }
}

fn static_lib_file(dir: &std::path::Path, windows: bool) -> PathBuf {
    if windows {
        dir.join("ta-lib-static.lib")
    } else {
        dir.join("libta-lib.a")
    }
}

fn main() {
    println!("cargo:rerun-if-changed=wrapper.h");
    println!("cargo:rerun-if-changed=vendor/ta-lib-0.8.1-src.tar.gz");
    println!("cargo:rerun-if-env-changed=TA_LIBRARY_PATH");
    println!("cargo:rerun-if-env-changed=TA_INCLUDE_PATH");
    let out = PathBuf::from(env::var_os("OUT_DIR").unwrap());
    let windows = env::var("CARGO_CFG_TARGET_OS").unwrap() == "windows";

    // Optional override for packagers: link an existing TA-Lib 0.8.1 static
    // library instead of compiling the vendored sources. Both variables must
    // point at a `lib` directory holding the static library and an `include`
    // directory holding `ta-lib/ta_func.h`.
    if let (Some(lib_dir), Some(include_dir)) = (
        env::var_os("TA_LIBRARY_PATH").map(PathBuf::from),
        env::var_os("TA_INCLUDE_PATH").map(PathBuf::from),
    ) {
        let lib_file = static_lib_file(&lib_dir, windows);
        assert!(
            lib_file.exists(),
            "TA_LIBRARY_PATH is set but {} does not exist",
            lib_file.display()
        );
        assert!(
            include_dir.join("ta-lib").join("ta_func.h").exists(),
            "TA_INCLUDE_PATH is set but {}/ta-lib/ta_func.h does not exist",
            include_dir.display()
        );
        println!(
            "cargo:warning=linking system TA-Lib from {}",
            lib_dir.display()
        );
        emit_link(&lib_dir, windows);
        finish_bindings(&include_dir, &out);
        return;
    }

    let archive = fs::read(format!("vendor/ta-lib-{VERSION}-src.tar.gz")).unwrap();
    assert_eq!(
        format!("{:x}", Sha256::digest(&archive)),
        SHA256,
        "TA-Lib source checksum mismatch"
    );
    let source = out.join(format!("ta-lib-{VERSION}"));
    // A stamp file marks a complete extraction so an interrupted build never
    // reuses a partially unpacked tree.
    let stamp = source.join(".extracted");
    if !stamp.exists() {
        if source.exists() {
            fs::remove_dir_all(&source).expect("remove partial TA-Lib extraction");
        }
        tar::Archive::new(flate2::read::GzDecoder::new(&archive[..]))
            .unpack(&out)
            .expect("extract vendored TA-Lib");
        fs::write(&stamp, SHA256).expect("write extraction stamp");
    }
    let mut config = cmake::Config::new(&source);
    if windows {
        // Cargo/CMake discover MSVC without vcvarsall, but upstream requires this
        // variable even with an explicit Visual Studio generator architecture.
        let platform = match env::var("CARGO_CFG_TARGET_ARCH").unwrap().as_str() {
            "x86_64" => "x64",
            "aarch64" => "ARM64",
            "x86" => "Win32",
            arch => panic!("unsupported Windows architecture: {arch}"),
        };
        config.env("Platform", platform);
        if env::var("CARGO_CFG_TARGET_ENV").unwrap() == "msvc" {
            // cmake-rs synthesizes CMAKE_C_FLAGS_RELEASE for MSVC and strips
            // cc's optimization flags. Restore optimization explicitly.
            config.cflag("/O2");
        }
    }
    let dst = config
        .profile("Release")
        .define("BUILD_SHARED_LIBS", "OFF")
        .define("BUILD_STATIC_LIBS", "ON")
        .define("BUILD_DEV_TOOLS", "OFF")
        .define("CMAKE_POSITION_INDEPENDENT_CODE", "ON")
        .build();
    emit_link(&dst.join("lib"), windows);
    finish_bindings(&dst.join("include"), &out);
}

fn emit_link(lib_dir: &std::path::Path, windows: bool) {
    println!("cargo:rustc-link-search=native={}", lib_dir.display());
    println!("cargo:rustc-link-lib=static={}", static_lib_name(windows));
    if !windows {
        println!("cargo:rustc-link-lib=m");
    }
}

#[allow(unused_variables)]
fn finish_bindings(include_dir: &std::path::Path, out: &std::path::Path) {
    println!("cargo:rerun-if-changed=src/bindings.rs");
    #[cfg(not(feature = "regenerate-bindings"))]
    fs::copy("src/bindings.rs", out.join("bindings.rs")).expect("copy portable bindings");
    #[cfg(feature = "regenerate-bindings")]
    generate_bindings(include_dir, out);
}

#[cfg(feature = "regenerate-bindings")]
fn generate_bindings(include_dir: &std::path::Path, out: &std::path::Path) {
    // The umbrella header includes ta_defs.h before headers using TA_LIB_API.
    // Always use the headers that belong to the archive being linked (#26).
    bindgen::Builder::default()
        .header("wrapper.h")
        .clang_arg(format!("-I{}", include_dir.display()))
        .allowlist_function("TA_.*")
        .allowlist_type("TA_.*")
        .allowlist_var("TA_.*")
        .constified_enum(".*")
        .rustified_enum("TA_RetCode")
        .layout_tests(false)
        .parse_callbacks(Box::new(bindgen::CargoCallbacks::new()))
        .generate()
        .expect("generate TA-Lib bindings")
        .write_to_file(out.join("bindings.rs"))
        .expect("write TA-Lib bindings");
}
