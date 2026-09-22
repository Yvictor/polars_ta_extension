"""A copied plugin must carry all skill resources without repository dependencies."""

import json
from pathlib import Path
import re
import shutil

ROOT = Path(__file__).resolve().parents[1]


def test_native_marketplaces_resolve_the_same_self_contained_plugin(tmp_path):
    sources = []
    for catalog in (
        ".agents/plugins/marketplace.json",
        ".claude-plugin/marketplace.json",
        ".cursor-plugin/marketplace.json",
    ):
        data = json.loads((ROOT / catalog).read_text())
        assert data["name"] == "polars-ta-extension"
        (entry,) = data["plugins"]
        source = entry["source"]
        sources.append((ROOT / (source["path"] if isinstance(source, dict) else source)).resolve())
    assert len(set(sources)) == 1
    plugin = tmp_path / "plugin"
    shutil.copytree(sources[0], plugin)
    for tool in ("codex", "claude", "cursor"):
        manifest = json.loads((plugin / f".{tool}-plugin/plugin.json").read_text())
        assert manifest["name"] == "polars-talib" and manifest["version"] == "0.2.0"
        skill = plugin / manifest["skills"] / "polars-talib/SKILL.md"
        assert skill.is_file()
        for link in re.findall(r"\]\(([^)]+)\)", skill.read_text()):
            if "://" not in link:
                resource = (skill.parent / link).resolve()
                assert resource.is_relative_to(plugin.resolve()) and resource.is_file()
    assert (plugin / "LICENSE").read_bytes() == (ROOT / "LICENSE").read_bytes()
