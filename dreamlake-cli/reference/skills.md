# Agent skills

Everything on this site is also shipped **as a skill** — a
`SKILL.md` plus one markdown file per page — inside the CLI package. Installing
it puts the corpus where an agent looks for it.

```bash file="terminal"
dreamlake skill list
dreamlake skill install                       # → ./.claude/skills/dreamlake-cli/
dreamlake skill install dreamlake-cli --global
```

| Command | What it does |
| --- | --- |
| `skill list [--json]` | every bundled skill, and whether it is installed at project or global scope |
| `skill install [name] [--global] [--dir <path>] [--force] [--json]` | copy one onto disk |

Omit `name` when the build bundles exactly one skill, which today it does.

## Where it goes

| Scope | Path |
| --- | --- |
| project (default) | `<cwd>/.claude/skills/<name>/` |
| `--global` | `~/.claude/skills/<name>/` |
| `--dir <path>` | `<path>/.claude/skills/<name>/` |

`--dir` overrides `--global`. The layout is fixed — `SKILL.md` at the top,
`reference/*.md` beneath it — because that is what Claude Code reads.

## It will not overwrite your edits

`.claude/skills/` is a **shared** directory. Yours probably already holds
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
  "source": "/usr/local/lib/dreamlake/skills",
  "skills": [
    {
      "name": "dreamlake-cli",
      "files": 16,
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
pnpm -C docs check:llms        # exit 1 if the committed skill is stale
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
