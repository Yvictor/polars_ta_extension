use sha2::{Digest, Sha256};
use std::{env, fs, path::PathBuf};

const VERSION: &str = "0.8.1";
const SHA256: &str = "ec59ccd88c0c77f618587d858787c8f9d06c40460a09d66751926f6fd670f985";

fn main() {
    println!("cargo:rerun-if-changed=wrapper.h");
    println!("cargo:rerun-if-changed=vendor/ta-lib-0.8.1-src.tar.gz");
    let out = PathBuf::from(env::var_os("OUT_DIR").unwrap());
    let archive = fs::read(format!("vendor/ta-lib-{VERSION}-src.tar.gz")).unwrap();
    assert_eq!(
        format!("{:x}", Sha256::digest(&archive)),
        SHA256,
        "TA-Lib source checksum mismatch"
    );
    let source = out.join(format!("ta-lib-{VERSION}"));
    if !source.exists() {
        tar::Archive::new(flate2::read::GzDecoder::new(&archive[..]))
            .unpack(&out)
            .expect("extract vendored TA-Lib");
    }
    let windows = env::var("CARGO_CFG_TARGET_OS").unwrap() == "windows";
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
    println!(
        "cargo:rustc-link-search=native={}",
        dst.join("lib").display()
    );
    println!(
        "cargo:rustc-link-lib=static={}",
        if windows { "ta-lib-static" } else { "ta-lib" }
    );
    if !windows {
        println!("cargo:rustc-link-lib=m");
    }
    println!("cargo:rerun-if-changed=src/bindings.rs");
    #[cfg(not(feature = "regenerate-bindings"))]
    fs::copy("src/bindings.rs", out.join("bindings.rs")).expect("copy portable bindings");
    #[cfg(feature = "regenerate-bindings")]
    generate_bindings(&dst, &out);
}

#[cfg(feature = "regenerate-bindings")]
fn generate_bindings(dst: &std::path::Path, out: &std::path::Path) {
    // The umbrella header includes ta_defs.h before headers using TA_LIB_API.
    // Always use the headers that belong to the archive being linked (#26).
    bindgen::Builder::default()
        .header("wrapper.h")
        .clang_arg(format!("-I{}", dst.join("include").display()))
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
