extern crate bindgen;

use std::env;
use std::process::Command;
use std::{io::Write, path::PathBuf};

const TA_LIB_VER: &str = "0.4.0";
// const TA_LIB_TGZ: &str = "ta-lib-0.4.0-src.tar.gz";

fn main() {
    let ta_lib_gz = format!("ta-lib-{TA_LIB_VER}-src.tar.gz");
    let ta_lib_url = format!(
        "https://sourceforge.net/projects/ta-lib/files/ta-lib/{TA_LIB_VER}/{ta_lib_gz}/download"
    );
    let cwd = env::current_dir().unwrap();
    let deps_dir = PathBuf::from(
        &env::var("DEPS_DIR").unwrap_or(cwd.join("dependencies").display().to_string()),
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
    let file_gz = std::fs::File::open(file_gz_path).unwrap();
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
        .arg("install")
        .current_dir(&tmp_dir.join("ta-lib"))
        .status()
        .expect("Failed to run make install command");

    println!("cargo:rustc-link-lib=static=ta_lib");
    println!("cargo:rustc-link-search=native={ta_library_path}");
    println!("cargo:rustc-link-search=native=../dependencies/lib");
    let bindings = bindgen::Builder::default()
        // The input header we would like to generate
        // bindings for.
        .header("wrapper.h")
        .clang_arg(format!("-I{}", ta_include_path))
        .clang_arg("-I../dependencies/include")
        .clang_arg("-v")
        // Generate rustified enums
        .rustified_enum(".*")
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
