"""Install/discover the plugin with native CLIs in isolated configuration roots.

Requires codex and claude on PATH. No model calls, credentials, or changes to the
user's normal configuration. Pass --source owner/repo@ref to test Git installs.
"""

import argparse
import json
import os
from pathlib import Path
import queue
import subprocess
import tempfile
import threading

ROOT = Path(__file__).resolve().parents[1]
PLUGIN_ID = "polars-talib@polars-ta-extension"
SKILL_NAME = "polars-talib:polars-talib"


def run(command, env):
    result = subprocess.run(command, env=env, text=True, capture_output=True, timeout=180)
    if result.returncode:
        raise RuntimeError(f"{command}: {result.stdout}\n{result.stderr}")
    return result.stdout


def codex_skills(env, cwd):
    responses = queue.Queue()
    with tempfile.TemporaryFile(mode="w+") as errors:
        proc = subprocess.Popen(
            ["codex", "app-server", "--stdio"],
            env=env,
            text=True,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=errors,
        )

        def receive():
            for line in proc.stdout:
                responses.put(json.loads(line))

        reader = threading.Thread(target=receive, daemon=True)
        reader.start()

        def request(message):
            proc.stdin.write(json.dumps(message) + "\n")
            proc.stdin.flush()
            while True:
                response = responses.get(timeout=30)
                if response.get("id") == message["id"]:
                    if "error" in response:
                        raise RuntimeError(response["error"])
                    return response["result"]

        try:
            request(
                {
                    "id": 1,
                    "method": "initialize",
                    "params": {"clientInfo": {"name": "polars-plugin-ci", "version": "1.0.0"}},
                }
            )
            proc.stdin.write(json.dumps({"method": "initialized"}) + "\n")
            proc.stdin.flush()
            response = request(
                {
                    "id": 2,
                    "method": "skills/list",
                    "params": {"cwds": [str(cwd)], "forceReload": True},
                }
            )
            return [
                skill
                for data in response["data"]
                for skill in data["skills"]
                if skill.get("pluginId") == PLUGIN_ID
            ]
        finally:
            proc.stdin.close()
            try:
                proc.wait(timeout=10)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait()
            reader.join(timeout=2)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--source", default=str(ROOT), help="Local marketplace root or owner/repo@ref"
    )
    args = parser.parse_args()
    expected = ROOT / "plugins/polars-talib/skills/polars-talib"
    with tempfile.TemporaryDirectory(prefix="polars-native-plugins-") as temp:
        config_dir = Path(temp)
        for folder in ("codex", "claude", "workspace"):
            (config_dir / folder).mkdir()
        # These are the CLIs' documented configuration-root overrides.
        codex_env = {**os.environ, "CODEX_HOME": str(config_dir / "codex")}
        claude_env = {**os.environ, "CLAUDE_CONFIG_DIR": str(config_dir / "claude")}
        run(["claude", "plugin", "validate", str(ROOT / "plugins/polars-talib")], claude_env)
        run(
            ["claude", "plugin", "validate", str(ROOT / ".claude-plugin/marketplace.json")],
            claude_env,
        )
        run(["codex", "plugin", "marketplace", "add", args.source, "--json"], codex_env)
        install = json.loads(run(["codex", "plugin", "add", PLUGIN_ID, "--json"], codex_env))
        cached_skill = Path(install["installedPath"]) / "skills/polars-talib"
        for source in expected.rglob("*"):
            if source.is_file():
                assert (
                    cached_skill / source.relative_to(expected)
                ).read_bytes() == source.read_bytes()
        skills = codex_skills(codex_env, config_dir / "workspace")
        assert len(skills) == 1 and skills[0]["name"] == SKILL_NAME and skills[0]["enabled"], skills
        assert Path(skills[0]["path"]).resolve() == (cached_skill / "SKILL.md").resolve()
        print("Codex: native install, complete cached references, and skills/list discovery passed")
        run(["claude", "plugin", "marketplace", "add", args.source], claude_env)
        install = json.loads(run(["claude", "plugin", "install", PLUGIN_ID, "--json"], claude_env))
        assert install["outcome"] == "ok", install
        details = run(["claude", "plugin", "details", PLUGIN_ID], claude_env)
        assert "Skills (1)" in details and "polars-talib" in details, details
        print("Claude Code: native install and skill component discovery passed")


if __name__ == "__main__":
    main()
