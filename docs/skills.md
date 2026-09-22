# Install the AI skill

The repository is a native plugin marketplace for Claude Code and Codex, using
[Shioaji's packaging layout](https://github.com/Sinotrade/Shioaji#ai-coding-agent-skills).
Both plugins contain the same [polars-talib skill](../plugins/polars-talib/skills/polars-talib/SKILL.md)
and its 201-function reference and usage patterns. Installing the plugin adds
coding guidance; it does not install Python packages or run trading software.

## Native installation

The commands below use the repository's default branch. **Until PR #38 is merged,
use the [review-branch commands](#try-the-review-branch) instead.**

Claude Code, from a terminal:

```sh
claude plugin marketplace add Yvictor/polars_ta_extension
claude plugin install polars-talib@polars-ta-extension
```

Inside Claude Code, the equivalent commands are:

```text
/plugin marketplace add Yvictor/polars_ta_extension
/plugin install polars-talib@polars-ta-extension
```

Start a new session or reload plugins, then invoke `/polars-talib:polars-talib`.
Check installation with `claude plugin details polars-talib@polars-ta-extension`.

Codex, from a terminal:

```sh
codex plugin marketplace add Yvictor/polars_ta_extension
codex plugin add polars-talib@polars-ta-extension
```

Start a new session, select the skill through `/skills`, or mention
`$polars-talib:polars-talib`. Check installation with
`codex plugin list --marketplace polars-ta-extension`.

Native installation and discovery are tested with Codex CLI 0.155.1 and Claude
Code 2.1.278. These are tested versions, not inferred minimum versions. If your
CLI lacks these subcommands, update it or use the standalone installer below.

## Try the review branch

These commands install the PR's files before they are available on the default branch:

```sh
claude plugin marketplace add Yvictor/polars_ta_extension@codex/talib-020-independent
claude plugin install polars-talib@polars-ta-extension

codex plugin marketplace add Yvictor/polars_ta_extension --ref codex/talib-020-independent
codex plugin add polars-talib@polars-ta-extension
```

Alternatively, from a checkout of that branch:

```sh
claude plugin marketplace add .
claude plugin install polars-talib@polars-ta-extension
codex plugin marketplace add .
codex plugin add polars-talib@polars-ta-extension
```

After merging, remove the review marketplace with
`claude plugin marketplace remove polars-ta-extension` or
`codex plugin marketplace remove polars-ta-extension`, then run the default-branch
installation commands above. Review-branch registrations track that branch until changed.

## Updates and removal

For Claude Code:

```sh
claude plugin marketplace update polars-ta-extension
claude plugin update polars-talib@polars-ta-extension
# To uninstall:
claude plugin uninstall polars-talib@polars-ta-extension
```

For Codex:

```sh
codex plugin marketplace upgrade polars-ta-extension
codex plugin add polars-talib@polars-ta-extension
# To uninstall:
codex plugin remove polars-talib@polars-ta-extension
```

Start a new session after updating. Plugin versions are independent of whether
the Python distribution is installed; plugin releases must bump the manifest
versions so clients invalidate their caches.

## Cursor and standalone skills

Cursor marketplace/plugin manifests are included in the same layout as Shioaji.
They prepare this repository for Cursor's publisher flow; this PR does **not**
mean the plugin has been published or approved in the public Cursor Marketplace.
Use the standalone installer now, or install through Cursor's Marketplace once
it is published there. No unsupported Cursor CLI installation command is claimed.

From a checkout of the desired branch:

```sh
python scripts/install_skill.py --agent codex
python scripts/install_skill.py --agent claude
python scripts/install_skill.py --agent cursor
```

These copy the skill to `~/.agents/skills/polars-talib`,
`~/.claude/skills/polars-talib`, or `~/.cursor/skills/polars-talib`.
Use `--project /path/to/project` for project-local installation. The installer
refuses to overwrite an existing skill and copies all reference files.
Standalone skills are named `polars-talib`, without the plugin namespace.
Choose either the native plugin or standalone skill in each tool to avoid duplicate discovery.

Codex's built-in `$skill-installer` can also install only the skill. Ask it to use
repo `Yvictor/polars_ta_extension`, path
`plugins/polars-talib/skills/polars-talib`, and the desired ref
(`codex/talib-020-independent` during PR review; `master` after merge).

The third-party cross-tool installer also discovers the nested skill directory:

```sh
npx skills add Yvictor/polars_ta_extension
```

That command uses the default branch and is not a native Claude Code or Codex command.

## Maintaining and validating the package

The single canonical skill lives in `plugins/polars-talib/skills/polars-talib`.
Do not add a second copy under the repository's top-level `skills/` directory.
The plugin is self-contained because native installers may copy only its directory.

```sh
python scripts/generate_skill_reference.py
claude plugin validate plugins/polars-talib
claude plugin validate .claude-plugin/marketplace.json
python scripts/check_native_plugins.py
```

The native smoke test installs both plugins in temporary configuration roots,
checks Codex's actual `skills/list` response and cached reference files, and checks
Claude Code's skill component inventory. It needs no credentials or model calls
and leaves the user's normal configuration unchanged. Pass
`--source Yvictor/polars_ta_extension@codex/talib-020-independent` to test fetching
and installing from GitHub instead of a local checkout. CI runs the local native
smoke test as a release gate alongside the existing wheel/source tests.

Official references:
[Codex plugin packaging](https://developers.openai.com/plugins/build/plugins),
[Claude Code marketplaces](https://code.claude.com/docs/en/plugin-marketplaces),
[Cursor plugins](https://cursor.com/docs/reference/plugins).
