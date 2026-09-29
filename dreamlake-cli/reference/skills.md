# Agent skills

Everything on this site is also shipped **as a skill** — a
`SKILL.md` plus one markdown file per page — inside the CLI package. Installing
it puts the corpus where an agent looks for it.

## Setup

Run `dreamlake init` in a terminal to choose Codex or Claude Code and project
or global scope. It installs the bundled CLI skill using the same installer
as `dreamlake skill install`; no login or download is required.

```bash file="terminal" cli-help="dreamlake"
# Guided agent setup
dreamlake init
# Install directly for Codex in this project
dreamlake skill install --agent codex
# Install for Claude Code across projects
dreamlake skill install --agent claude --global
```

```bash file="terminal" cli-help="init"
dreamlake init
dreamlake init --agent codex
dreamlake init --agent claude --global
```

With any setup options, `init` runs without prompts; scope defaults to the
current project. Non-interactive or `--json` usage requires `--agent codex`
or `--agent claude`. Canceling the guided setup writes nothing.

```bash file="terminal" cli-help="skill"
dreamlake skill list --agent codex
dreamlake skill install --agent codex
dreamlake skill install --agent claude --global
```

```bash file="terminal" cli-help="skill install"
dreamlake skill install --agent codex
dreamlake skill install dreamlake-cli --agent claude --global
# Explicitly replace modified bundled files
dreamlake skill install --agent codex --force
```

```bash file="terminal" cli-help="skill list"
dreamlake skill list --agent codex
dreamlake skill list --agent claude --json
```

`skill install` and `skill list` default to `--agent claude` for compatibility.
Omit the skill name when the build bundles exactly one skill, which today it does.
Both installation commands accept `--global`, `--dir <path>`, `--force`, and
`--json`. `skill list` accepts `--agent` and `--json` and reports project and
global installation status for the selected agent.

## Where it goes

| Agent | Project (default) | `--global` |
| --- | --- | --- |
| `claude` | `<cwd>/.claude/skills/<name>/` | `~/.claude/skills/<name>/` |
| `codex` | `<cwd>/.agents/skills/<name>/` | `~/.agents/skills/<name>/` |

`--dir <path>` replaces the project root and overrides `--global`, retaining
the agent-specific subdirectory. It does not name the skill directory itself.
Each bundle contains `SKILL.md` and `reference/*.md`. Codex's supported
[skill locations](https://developers.openai.com/codex/skills) include `.agents/skills`.
Updating the CLI does not update installed skills automatically; rerun the
installation command and review conflicts before choosing `--force`.

## It will not overwrite your edits

Both `.claude/skills/` and `.agents/skills/` are **shared** directories. Yours probably already holds
hand-written skills next to anything you install. So:

| Target | Behaviour | `status` | rc |
| --- | --- | --- | --- |
| absent | write it | `installed` | 0 |
| present, every file byte-identical | do nothing | `exists` | 0 |
| present, differs | **refuse**, list the differing paths, print the `--force` command | `conflict` | 1 |
| present, differs, `--force` | overwrite **only the files that differed** | `installed` | 0 |

```text file="output"
✗ dreamlake-cli is already installed at /work/.claude/skills/dreamlake-cli and differs from the bundled copy
    · SKILL.md
    · reference/collections.md

  overwrite it with:
        dreamlake skill install dreamlake-cli --force
```

Nothing was written. The refusal is the feature: a skill you edited survives a
mistyped install.

> **Warning:** It never `rm -rf`s the target directory — it deletes nothing, ever, and
> overwrites only files the bundle itself owns. It never touches
> `.claude/settings.json` or `settings.local.json`, which sit beside `skills/`
> and carry permissions. And it never assumes every entry under
> `.claude/skills/` is a directory — loose `.md` files there are left alone.

A file that is not part of the bundle but sits inside the skill directory —
your own `NOTES.md`, say — is reported and left untouched, by `--force` too.

## `--json`

Both subcommands emit one object with a discriminated `status` and a required,
nullable `nextAction`. On failure, stdout still carries exactly one object and
stderr stays empty.

```json file="dreamlake skill list --json"
{
  "status": "ok",
  "source": "embedded-skills",
  "skills": [
    {
      "name": "dreamlake-cli",
      "files": 37,
      "project": { "path": "/work/.claude/skills/dreamlake-cli", "state": "absent" },
      "global":  { "path": "/home/you/.claude/skills/dreamlake-cli", "state": "identical" }
    }
  ],
  "nextAction": null
}
```

`state` is one of `absent`, `identical`, `differs`, or `blocked` (something
that is not a directory is in the way).

```json file="a conflict"
{
  "status": "conflict",
  "skill": "dreamlake-cli",
  "scope": "project",
  "target": "/work/.claude/skills/dreamlake-cli",
  "files": [],
  "conflicts": ["SKILL.md"],
  "error": "dreamlake-cli is already installed at /work/.claude/skills/dreamlake-cli and differs from the bundled copy",
  "nextAction": { "kind": "run", "command": "dreamlake skill install dreamlake-cli --force" }
}
```

`files` is the list written **by this run**, so `files: []` is the proof that
nothing happened.

## The skill is generated, not written

`skills/<name>/` is built from `docs/pages/**/+Page.mdx` by
`docs/scripts/gen-llms.mjs`. Editing it by hand is pointless — the next docs
build overwrites it. Change the page, then regenerate:

```bash file="terminal"
pnpm -C docs gen:llms          # rebuild skills/<name>/ from the pages
pnpm -C docs check:llms        # fail on stale skill or committed command-help output
```

The same generator writes the other machine-readable surfaces of this site:
every page is fetchable as markdown at `<page-url>.md`, the index at
`/llms.txt`, and the whole corpus at `/llms-full.txt`.

## If your install has no skill to install

A build that ships no `skills/` directory says so and names the escape hatch:

```text file="output"
✗ no bundled skills found — this build ships none. Point DREAMLAKE_SKILLS_DIR
  at a skills/ directory to install from a checkout.
```

`DREAMLAKE_SKILLS_DIR` also lets you install from a working copy of this
repository without publishing anything.

## Copyable command help

These reviewed blocks also populate each command's `--help`. The native binary
and npm platform package embed the CLI reference at build time starting with
0.24.3. No checkout, runtime, network, or environment variable is needed to list
or install it. This bundles `dreamlake-cli`, not every skill in the public catalog.
Updating the executable does not overwrite an installed skill: rerun install,
review any conflict, preserve local edits, and use `--force` only deliberately.

```bash
# Inspect the bundle and installed state without changing files.
dreamlake skill list
dreamlake skill list --json
```

```bash
# Install into this project; an identical second install is a no-op.
dreamlake skill install dreamlake-cli
dreamlake skill install dreamlake-cli --dir ./my-project --json
# Install for the current user instead.
dreamlake skill install dreamlake-cli --global
# After reviewing/backing up local edits, update owned files only.
dreamlake skill install dreamlake-cli --force
```

## Release acceptance checklist

- [ ] Edit docs first; regenerate the skill and command-help examples.
- [ ] Run source tests and the isolated native packaging test in CI.
- [ ] Compile all eight platforms from the reviewed commit. The build embeds
      the freshly generated CLI skill and rejects an empty or incomplete bundle.
- [ ] Test a copied binary outside the checkout with a temporary home and no
      `DREAMLAKE_SKILLS_DIR`: list, install, byte readback, identical reinstall,
      conflict refusal, and forced update preserving peer files.
- [ ] Publish immutable versioned binaries and npm packages; verify downloaded
      bytes before moving release pointers. Never re-upload an uncertain version.
- [ ] Repeat skill installation from the public native download and npm package.
- [ ] Synchronize the public skill repository from the merged source commit;
      check current source freshness, not only integrity or locked reproduction.
- [ ] Publish the versioned docs and record source, PR, release, checksums, public
      URLs, and fresh-install results separately.

`bun run scripts/verify-native-skills.ts` runs the isolated packaging gate locally.
`DREAMLAKE_SKILLS_DIR` remains an explicit development override; an invalid path
fails instead of silently falling back to a different bundle.
