extern crate bindgen;

use bindgen::callbacks::{DeriveInfo, ParseCallbacks, TypeKind};
use std::env;
use std::io::{Cursor, Read};
use std::process::Command;
use std::{io::Write, path::PathBuf};

const TA_LIB_VER: &str = "0.4.0";
// const TA_LIB_TGZ: &str = "ta-lib-0.4.0-src.tar.gz";

#[derive(Debug)]
struct DerivesCallback;

impl ParseCallbacks for DerivesCallback {
    // Test the "custom derives" capability by adding `PartialEq` to the `Test` struct.
    fn add_derives(&self, info: &DeriveInfo<'_>) -> Vec<String> {
        if info.name.starts_with("_") {
            vec![]
        } else if info.kind == TypeKind::Struct {
            vec![]
        } else if info.name == "TA_RangeType"
            || info.name == "TA_CandleSettingType"
            || info.name == "TA_InputParameterType"
            || info.name == "TA_OptInputParameterType"
            || info.name == "TA_OutputParameterType"
            || info.name == "TA_Compatibility"
            || info.name == "TA_MAType"
            || info.name == "TA_FuncUnstId"
            || info.name == "TA_RetCode"
            || info.name == "TA_FuncUnstId"
        {
            vec!["Deserialize".into()]
        } else {
            vec!["Deserialize".into(), "Deserialize_repr".into()]
        }
    }
}

fn main() {
    #[cfg(target_os = "windows")]
    let ta_lib_gz = format!("ta-lib-{TA_LIB_VER}-msvc.zip");
    #[cfg(target_family = "unix")]
    let ta_lib_gz = format!("ta-lib-{TA_LIB_VER}-src.tar.gz");
    let ta_lib_url = format!(
        "https://sourceforge.net/projects/ta-lib/files/ta-lib/{TA_LIB_VER}/{ta_lib_gz}/download"
    );
    let cwd = env::current_dir().unwrap();
    let deps_dir = PathBuf::from(
        &env::var("DEPS_PATH").unwrap_or(cwd.join("dependencies").display().to_string()),
    );
    let tmp_dir = deps_dir.join("tmp");
    let file_gz_path = tmp_dir.join(ta_lib_gz);
    let ta_library_path =
        env::var("TA_LIBRARY_PATH").unwrap_or(cwd.join("dependencies/lib").display().to_string());
    let ta_include_path = env::var("TA_INCLUDE_PATH")
        .unwrap_or(cwd.join("dependencies/include").display().to_string());
    if !file_gz_path.exists() {
        let resp = reqwest::blocking::get(ta_lib_url).unwrap();
        let content = resp.bytes().unwrap();
        std::fs::create_dir_all(tmp_dir.clone()).unwrap();
        let mut file_gz = std::fs::File::create(file_gz_path.clone()).unwrap();
        file_gz.write_all(&content).unwrap();
        file_gz.sync_data().unwrap();
    }
    let lib_path = PathBuf::from(ta_library_path.clone());
    let os = std::env::consts::OS;
    if !lib_path.exists() {
        let mut file_gz = std::fs::File::open(file_gz_path).unwrap();
        if os == "windows" {
            let metadata = std::fs::File::metadata(&file_gz).expect("unable to read metadata");
            let mut buf = vec![0; metadata.len() as usize];
            file_gz.read(&mut buf).expect("buffer overflow");
            zip_extract::extract(Cursor::new(buf), &tmp_dir, false).unwrap();
            Command::new("nmake")
                .current_dir(
                    &tmp_dir
                        .join("ta-lib")
                        .join("c")
                        .join("make")
                        .join("cdr")
                        .join("win32")
                        .join("msvc"),
                )
                .status()
                .expect("Failed to run make command");
            // nmake and clang
            // set LIBCLANG_PATH=bin
            fs_extra::dir::copy(
                &tmp_dir.join("ta-lib").join("c").join("lib"),
                deps_dir.clone(),
                &fs_extra::dir::CopyOptions::new().skip_exist(true),
            )
            .unwrap();
            fs_extra::dir::copy(
                &tmp_dir.join("ta-lib").join("c").join("include"),
                deps_dir.clone(),
                &fs_extra::dir::CopyOptions::new().skip_exist(true),
            )
            .unwrap();
            let _ = std::fs::create_dir_all(PathBuf::from(&ta_include_path).join("ta-lib"));
            fs_extra::dir::copy(
                &PathBuf::from(&ta_include_path),
                PathBuf::from(&ta_include_path).join("ta-lib"),
                &fs_extra::dir::CopyOptions::new()
                    .skip_exist(true)
                    .content_only(true),
            )
            .unwrap();
            let ta_lib_path = PathBuf::from(&ta_library_path);
            let _ = std::fs::copy(
                ta_lib_path.join("ta_libc_crd.lib"),
                ta_lib_path.join("ta_lib.lib"),
            );
        } else {
            let mut archive = tar::Archive::new(flate2::read::GzDecoder::new(file_gz));
            archive
                .entries()
                .unwrap()
                .filter_map(|r| r.ok())
                .map(|mut entry| -> std::io::Result<PathBuf> {
                    let strip_path = entry.path()?.iter().skip(1).collect::<std::path::PathBuf>();
                    let path = tmp_dir.join("ta-lib").join(strip_path);
                    // println!("unpack: {:?}", path);
                    entry.unpack(&path)?;
                    Ok(path)
                })
                .filter_map(|e| e.ok())
                .for_each(|x| println!("> {}", x.display()));
    
            Command::new("./configure")
                .arg(format!("--prefix={}", deps_dir.display()))
                .current_dir(&tmp_dir.join("ta-lib"))
                .status()
                .expect("Failed to run configure command");
    
            Command::new("make")
                .current_dir(&tmp_dir.join("ta-lib"))
                .status()
                .expect("Failed to run make command");
    
            Command::new("make")
                .arg("install")
                .current_dir(&tmp_dir.join("ta-lib"))
                .status()
                .expect("Failed to run make install command");
        }
    }

    println!("cargo:rustc-link-lib=static=ta_lib");
    println!("cargo:rustc-link-search=native={ta_library_path}");
    println!("cargo:rustc-link-search=native=../dependencies/lib");
    // let cb = ParseCallbacks::add_derives();
    let bindings = bindgen::Builder::default()
        // The input header we would like to generate
        // bindings for.
        .header("wrapper.h")
        .clang_arg(format!("-I{}", ta_include_path))
        .clang_arg("-I../dependencies/include")
        .clang_arg("-v")
        // Generate rustified enums
        // .newtype_enum("*")
        // .bitfield_enum("*")
        // .constified_enum_module(".*")
        // .rustified_enum(".*")
        .constified_enum(".*")
        .rustified_enum("TA_RetCode")
        // .rustified_non_exhaustive_enum(".*")
        // .raw_line("use serde::Deserialize;")
        // .raw_line("use serde_repr::Deserialize_repr;")
        // .parse_callbacks(bindgen::callbacks::ParseCallbacks::add_derives(vec!["Deserialize"]))
        // .parse_callbacks(Box::new(DerivesCallback {}))
        // Finish the builder and generate the bindings.
        .generate()
        // Unwrap the Result and panic on failure.
        .expect("Unable to generate bindings");

    // Write the bindings to the $OUT_DIR/bindings.rs file.
    // let out_path = PathBuf::from(env::var("OUT_DIR").unwrap());
    let out_path = PathBuf::from("src");
    bindings
        .write_to_file(out_path.join("bindings.rs"))
        .expect("Couldn't write bindings!");
}
