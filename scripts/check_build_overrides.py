"""Native Linux CI checks for opt-in system TA-Lib builds and invalid overrides.

Run after `cargo test --manifest-path talib/Cargo.toml` so a pinned static
library is available. All override fixtures are copied to a temporary directory.
"""

import os
from pathlib import Path
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]


def main():
    libraries = list((ROOT / "talib/target/debug/build").glob("talib-sys-*/out/lib/libta-lib.a"))
    if not libraries:
        raise SystemExit("Run cargo test --manifest-path talib/Cargo.toml first (native Linux).")
    prefix = max(libraries, key=lambda p: p.stat().st_mtime).parent.parent
    base_env = dict(os.environ)
    for key in ("TA_LIBRARY_PATH", "TA_INCLUDE_PATH"):
        base_env.pop(key, None)
    command = [
        "cargo",
        "test",
        "--manifest-path",
        str(ROOT / "talib/Cargo.toml"),
        "--test",
        "generated",
        "--quiet",
    ]

    def check(label, overrides, error=None):
        result = subprocess.run(
            command, env={**base_env, **overrides}, capture_output=True, text=True
        )
        if error:
            assert result.returncode != 0 and error in result.stderr, result.stdout + result.stderr
        else:
            assert result.returncode == 0, result.stdout + result.stderr
        print(f"{label}: passed")

    with tempfile.TemporaryDirectory(prefix="talib-override-") as temp:
        fixture = Path(temp)
        shutil.copytree(prefix / "include", fixture / "include")
        (fixture / "lib").mkdir()
        shutil.copyfile(prefix / "lib/libta-lib.a", fixture / "lib/libta-lib.a")
        valid = {
            "TA_LIBRARY_PATH": str(fixture / "lib"),
            "TA_INCLUDE_PATH": str(fixture / "include"),
        }
        try:
            check("matching external library and headers", valid)
            check(
                "library path only",
                {"TA_LIBRARY_PATH": valid["TA_LIBRARY_PATH"]},
                "set both TA_LIBRARY_PATH",
            )
            check(
                "headers path only",
                {"TA_INCLUDE_PATH": valid["TA_INCLUDE_PATH"]},
                "set both TA_LIBRARY_PATH",
            )
            (fixture / "include/ta-lib/ta_func.h").write_text("/* wrong headers */")
            check("mismatched headers", valid, "does not match the pinned TA-Lib")
            check(
                "missing library",
                {**valid, "TA_LIBRARY_PATH": str(fixture / "missing")},
                "TA_LIBRARY_PATH: missing",
            )
        finally:
            check("vendored default restored", {})


if __name__ == "__main__":
    main()
