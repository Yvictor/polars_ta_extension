//! Build script for `talib-sys`.
//!
//! Resolution order for the TA-Lib C library:
//!
//! 1. If `TA_LIBRARY_PATH` (default: `<DEPS_PATH>/lib`) already contains a
//!    TA-Lib >= 0.6 static library, it is used as-is.
//! 2. Otherwise the upstream source tarball for [`TA_LIB_VER`] is downloaded
//!    (or read from `TA_LIB_SRC_ARCHIVE`), built as a static, position
//!    independent library and installed into `DEPS_PATH`.
//!
//! Environment variables:
//!
//! * `DEPS_PATH`            – install prefix (default: `<crate dir>/dependencies`)
//! * `TA_LIBRARY_PATH`      – directory containing `libta-lib.a` / `ta-lib-static.lib`
//! * `TA_INCLUDE_PATH`      – directory containing `ta-lib/ta_func.h`
//! * `TA_LIB_SRC_ARCHIVE`   – local path of `ta-lib-<ver>-src.tar.gz` (offline builds)
//! * `TA_LIB_SRC_URL`       – alternative download URL for the source tarball
//! * `TA_LIB_BUILD_SYSTEM`  – `autotools` (unix default) or `cmake` (windows default)
//! * `TA_LIB_CFLAGS`        – extra C flags for the TA-Lib build (default: `-O3`)
//!
//! Bindings are committed in `src/bindings.rs`; enable the `bindgen` cargo
//! feature to regenerate them from the headers.

use std::env;
use std::fs;
use std::io::Write;
use std::path::{Path, PathBuf};
use std::process::Command;

/// Bundled TA-Lib version. Keep in sync with `src/bindings.rs`.
pub const TA_LIB_VER: &str = "0.8.1";

fn env_var(name: &str) -> Option<String> {
    println!("cargo:rerun-if-env-changed={name}");
    env::var(name).ok().filter(|v| !v.is_empty())
}

fn target_os() -> String {
    env::var("CARGO_CFG_TARGET_OS").unwrap_or_else(|_| env::consts::OS.to_string())
}

fn target_arch() -> String {
    env::var("CARGO_CFG_TARGET_ARCH").unwrap_or_else(|_| env::consts::ARCH.to_string())
}

fn is_windows() -> bool {
    target_os() == "windows"
}

fn num_jobs() -> String {
    env::var("NUM_JOBS").unwrap_or_else(|_| "4".to_string())
}

/// Name of the static library (without prefix/suffix) found in `lib_dir`.
fn find_static_lib(lib_dir: &Path) -> Option<&'static str> {
    if is_windows() {
        if lib_dir.join("ta-lib-static.lib").exists() {
            return Some("ta-lib-static");
        }
        if lib_dir.join("ta-lib.lib").exists() {
            return Some("ta-lib");
        }
    } else if lib_dir.join("libta-lib.a").exists() {
        return Some("ta-lib");
    }
    None
}

fn download(url: &str, dest: &Path) {
    println!("cargo:warning=downloading TA-Lib {TA_LIB_VER} source from {url}");
    let client = reqwest::blocking::Client::builder()
        .timeout(std::time::Duration::from_secs(600))
        .build()
        .expect("failed to build HTTP client");
    let resp = client
        .get(url)
        .send()
        .unwrap_or_else(|e| panic!("failed to download {url}: {e}"));
    if !resp.status().is_success() {
        panic!("failed to download {url}: HTTP {}", resp.status());
    }
    let content = resp.bytes().expect("failed to read download body");
    fs::create_dir_all(dest.parent().unwrap()).unwrap();
    let tmp = dest.with_extension("part");
    let mut f = fs::File::create(&tmp).unwrap();
    f.write_all(&content).unwrap();
    f.sync_all().unwrap();
    fs::rename(&tmp, dest).unwrap();
}

/// Extract `archive` into `dest`, stripping the leading path component.
fn extract(archive: &Path, dest: &Path) {
    if dest.exists() {
        fs::remove_dir_all(dest).unwrap();
    }
    fs::create_dir_all(dest).unwrap();
    let file = fs::File::open(archive)
        .unwrap_or_else(|e| panic!("cannot open {}: {e}", archive.display()));
    let mut ar = tar::Archive::new(flate2::read::GzDecoder::new(file));
    for entry in ar.entries().unwrap() {
        let mut entry = entry.unwrap();
        let path = entry.path().unwrap().into_owned();
        let stripped: PathBuf = path.iter().skip(1).collect();
        if stripped.as_os_str().is_empty() {
            continue;
        }
        let out = dest.join(stripped);
        if let Some(parent) = out.parent() {
            fs::create_dir_all(parent).unwrap();
        }
        entry.unpack(&out).unwrap();
    }
}

fn run(cmd: &mut Command, what: &str) {
    println!("cargo:warning=running {what}: {cmd:?}");
    let status = cmd
        .status()
        .unwrap_or_else(|e| panic!("failed to spawn {what} ({cmd:?}): {e}"));
    if !status.success() {
        panic!("{what} failed with {status} ({cmd:?})");
    }
}

fn has_cmake() -> bool {
    Command::new("cmake")
        .arg("--version")
        .output()
        .map(|o| o.status.success())
        .unwrap_or(false)
}

fn build_with_cmake(src_dir: &Path, prefix: &Path) {
    let build_dir = src_dir.join("_build");
    let _ = fs::remove_dir_all(&build_dir);
    let mut configure = Command::new("cmake");
    configure
        .arg("-S")
        .arg(src_dir)
        .arg("-B")
        .arg(&build_dir)
        .arg(format!("-DCMAKE_INSTALL_PREFIX={}", prefix.display()))
        .arg("-DCMAKE_BUILD_TYPE=Release")
        .arg("-DBUILD_SHARED_LIBS=OFF")
        .arg("-DBUILD_STATIC_LIBS=ON")
        .arg("-DBUILD_DEV_TOOLS=OFF")
        .arg("-DCMAKE_POSITION_INDEPENDENT_CODE=ON");
    if let Some(flags) = env_var("TA_LIB_CFLAGS") {
        configure.arg(format!("-DCMAKE_C_FLAGS={flags}"));
    }
    match target_os().as_str() {
        "windows" => {
            let (vs_platform, vcvars_platform) = match target_arch().as_str() {
                "x86" => ("Win32", "x86"),
                "x86_64" => ("x64", "x64"),
                "aarch64" => ("ARM64", "arm64"),
                other => panic!("unsupported windows target arch: {other}"),
            };
            // Only Visual Studio generators accept `-A`.
            let generator = env::var("CMAKE_GENERATOR").unwrap_or_default();
            if generator.is_empty() || generator.contains("Visual Studio") {
                configure.arg("-A").arg(vs_platform);
            }
            // TA-Lib's CMakeLists requires the `Platform` variable that
            // vcvarsall.bat exports; provide it when not building from a
            // developer command prompt.
            if env::var_os("Platform").is_none() {
                configure.env("Platform", vcvars_platform);
            }
        }
        "macos" => {
            let target_arch = target_arch();
            let arch = match target_arch.as_str() {
                "aarch64" => "arm64",
                other => other,
            };
            configure.arg(format!("-DCMAKE_OSX_ARCHITECTURES={arch}"));
        }
        _ => {}
    }
    run(&mut configure, "cmake configure");
    run(
        Command::new("cmake")
            .arg("--build")
            .arg(&build_dir)
            .arg("--config")
            .arg("Release")
            .arg("--parallel")
            .arg(num_jobs()),
        "cmake build",
    );
    run(
        Command::new("cmake")
            .arg("--install")
            .arg(&build_dir)
            .arg("--config")
            .arg("Release"),
        "cmake install",
    );
}

fn build_with_autotools(src_dir: &Path, prefix: &Path) {
    let mut cflags = env_var("TA_LIB_CFLAGS").unwrap_or_else(|| "-O3".to_string());
    let mut configure = Command::new("sh");
    configure
        .arg("./configure")
        .arg(format!("--prefix={}", prefix.display()))
        .arg("--disable-shared")
        .arg("--enable-static")
        .arg("--with-pic")
        .current_dir(src_dir);
    if target_os() == "macos" && target_arch() != env::consts::ARCH {
        // Cross compiling between Apple silicon and Intel.
        let (arch, host) = match target_arch().as_str() {
            "aarch64" => ("arm64", "aarch64-apple-darwin"),
            "x86_64" => ("x86_64", "x86_64-apple-darwin"),
            other => panic!("unsupported macOS target arch: {other}"),
        };
        cflags.push_str(&format!(" -arch {arch}"));
        configure.arg(format!("--host={host}"));
    }
    configure.env("CFLAGS", cflags);
    run(&mut configure, "configure");
    run(
        Command::new("make")
            .arg(format!("-j{}", num_jobs()))
            .current_dir(src_dir),
        "make",
    );
    run(
        Command::new("make").arg("install").current_dir(src_dir),
        "make install",
    );
}

fn build_ta_lib(deps_dir: &Path) {
    let tmp_dir = deps_dir.join("tmp");
    let archive_name = format!("ta-lib-{TA_LIB_VER}-src.tar.gz");
    let archive = match env_var("TA_LIB_SRC_ARCHIVE") {
        Some(p) => PathBuf::from(p),
        None => {
            let archive = tmp_dir.join(&archive_name);
            if !archive.exists() {
                let url = env_var("TA_LIB_SRC_URL").unwrap_or_else(|| {
                    format!(
                        "https://github.com/ta-lib/ta-lib/releases/download/v{TA_LIB_VER}/{archive_name}"
                    )
                });
                download(&url, &archive);
            }
            archive
        }
    };
    let src_dir = tmp_dir.join(format!("ta-lib-{TA_LIB_VER}"));
    extract(&archive, &src_dir);

    let build_system = env_var("TA_LIB_BUILD_SYSTEM").unwrap_or_else(|| {
        if is_windows() {
            "cmake".to_string()
        } else {
            "autotools".to_string()
        }
    });
    match build_system.as_str() {
        "cmake" => {
            if !has_cmake() {
                panic!(
                    "cmake was not found on PATH but is required to build TA-Lib {TA_LIB_VER} \
                     (Windows needs CMake >= 3.30). Install cmake or point TA_LIBRARY_PATH / \
                     TA_INCLUDE_PATH at an existing TA-Lib >= 0.6 installation."
                );
            }
            build_with_cmake(&src_dir, deps_dir)
        }
        "autotools" => build_with_autotools(&src_dir, deps_dir),
        other => panic!("unknown TA_LIB_BUILD_SYSTEM={other} (expected `cmake` or `autotools`)"),
    }
    let _ = fs::remove_dir_all(&src_dir);
}

#[cfg(feature = "bindgen")]
fn generate_bindings(include_dir: &Path) {
    let bindings = bindgen::Builder::default()
        .header("wrapper.h")
        .clang_arg(format!("-I{}", include_dir.display()))
        // Only expose TA-Lib items so the generated file is platform independent.
        .allowlist_function("TA_.*")
        .allowlist_type("TA_.*")
        .allowlist_var("TA_.*")
        .constified_enum(".*")
        .rustified_enum("TA_RetCode")
        .layout_tests(false)
        .generate_comments(false)
        .raw_line(format!("// TA-Lib {TA_LIB_VER}"))
        .generate()
        .expect("Unable to generate bindings");
    bindings
        .write_to_file(PathBuf::from("src").join("bindings.rs"))
        .expect("Couldn't write bindings!");
}

fn main() {
    println!("cargo:rerun-if-changed=build.rs");
    println!("cargo:rerun-if-changed=wrapper.h");

    let crate_dir = PathBuf::from(env::var("CARGO_MANIFEST_DIR").unwrap());
    let deps_dir = env_var("DEPS_PATH")
        .map(PathBuf::from)
        .unwrap_or_else(|| crate_dir.join("dependencies"));
    let lib_dir = env_var("TA_LIBRARY_PATH")
        .map(PathBuf::from)
        .unwrap_or_else(|| deps_dir.join("lib"));
    let include_dir = env_var("TA_INCLUDE_PATH")
        .map(PathBuf::from)
        .unwrap_or_else(|| deps_dir.join("include"));

    if find_static_lib(&lib_dir).is_none() {
        if lib_dir != deps_dir.join("lib") {
            println!(
                "cargo:warning=no TA-Lib static library in TA_LIBRARY_PATH={}, building TA-Lib {TA_LIB_VER} into {}",
                lib_dir.display(),
                deps_dir.display()
            );
        }
        build_ta_lib(&deps_dir);
    }

    let (lib_dir, include_dir) = match find_static_lib(&lib_dir) {
        Some(_) => (lib_dir, include_dir),
        None => (deps_dir.join("lib"), deps_dir.join("include")),
    };
    let lib_name = find_static_lib(&lib_dir).unwrap_or_else(|| {
        panic!(
            "TA-Lib static library not found in {} after build. \
             Expected libta-lib.a (unix) or ta-lib-static.lib (windows) from TA-Lib >= 0.6.",
            lib_dir.display()
        )
    });
    if !include_dir.join("ta-lib").join("ta_func.h").exists() {
        panic!(
            "TA-Lib headers not found: expected {}/ta-lib/ta_func.h",
            include_dir.display()
        );
    }

    println!("cargo:rustc-link-search=native={}", lib_dir.display());
    println!("cargo:rustc-link-lib=static={lib_name}");
    if !is_windows() {
        println!("cargo:rustc-link-lib=m");
    }
    println!("cargo:include={}", include_dir.display());
    println!("cargo:lib={}", lib_dir.display());

    #[cfg(feature = "bindgen")]
    generate_bindings(&include_dir);
}
