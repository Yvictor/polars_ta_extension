# Install the AI skill

The same [SKILL.md](../skills/polars-talib/SKILL.md) works with Codex, Claude Code,
Cursor and other tools implementing the Agent Skills format. It teaches usage of
the library; it does not install Python dependencies or modify agent settings.

The quickest route is the cross-tool installer, which discovers `skills/*/SKILL.md`
in this repository and installs into Claude Code, Codex, Cursor and others:

```sh
npx skills add Yvictor/polars_ta_extension
```

From a checkout of this repository, choose your tool:

```sh
python scripts/install_skill.py --agent codex
python scripts/install_skill.py --agent claude
python scripts/install_skill.py --agent cursor
```

The destinations are `~/.agents/skills/polars-talib`,
`~/.claude/skills/polars-talib`, and `~/.cursor/skills/polars-talib` respectively.
Use `--project /path/to/project` for a project-local installation. The installer
works with Windows paths and refuses to overwrite an existing skill. Install one
copy per agent search path to avoid duplicate discovery. Restart the agent session,
then invoke `polars-talib` or ask it to add indicators to a Polars pipeline.

You can also copy the `skills/polars-talib` directory manually into your tool's
skills directory. Other Agent Skills tools can use `--agent agents` or their own
configured discovery directory.

Official discovery references (checked 2026-09-22):
[Codex](https://developers.openai.com/codex/skills/),
[Claude Code](https://code.claude.com/docs/en/skills),
[Cursor](https://cursor.com/docs/skills).
