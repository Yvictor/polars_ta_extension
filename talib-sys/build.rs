extern crate bindgen;

use std::env;
use std::path::PathBuf;

fn main() {
    println!("cargo:rustc-link-lib=static=ta_lib");
    let ta_library_path = env::var("TA_LIBRARY_PATH").unwrap_or("dependencies/lib".to_string());
    let ta_include_path = env::var("TA_INCLUDE_PATH").unwrap_or("dependencies/include".to_string());
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
