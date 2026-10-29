<!-- generated from https://cli.dreamlake.ai/skills.md at 0.94.0 8badc55; do not edit -->

# Agent skills

DreamLake skills are written once, in the public
[dreamlake-skills](https://github.com/dreamlake-ai/dreamlake-skills) repository,
and published as a release: a `catalog.json` listing every skill and a
`skills.tar.gz` holding their directories. The `dreamlake` CLI is the installer.
It carries one skill, `dreamlake-cli`, embedded for offline use; everything else
is downloaded from the latest release. Manual install is unpacking the same
tarball.

## Setup

Run `dreamlake init` once. It asks which agent you use (Claude Code, Codex,
or both) and where skills should go (this project or your home directory), remembers
both, installs the embedded `dreamlake-cli` skill without touching the
network, and lists the other skills in the catalog.

```bash file="terminal" cli-help="dreamlake"
# Guided agent setup: choose agent and scope, install dreamlake-cli offline
dreamlake init
# Install more skills from the public release
dreamlake skill install dreamlake-notes
# Keep installed skills current
dreamlake skill update
```

```bash file="terminal" cli-help="init"
dreamlake init
dreamlake init --agent codex
dreamlake init --agent claude --global
# Claude Code and Codex: one copy in each agent's directory
dreamlake init --agent all --global
```

With `--agent`, `init` runs without prompts and still saves the choice; add
`--global` to save global scope. Non-interactive or `--json` usage requires
`--agent` with `claude`, `codex`, `all`, or a comma-separated list such as
`claude,codex`. Canceling the guided setup writes nothing,
not even the preference.

The choice is saved as `{ "agent", "scope" }` in
`~/.local/state/dreamlake/skill-preferences.json` (`$XDG_STATE_HOME` is
honoured). Several agents are saved as `{ "agent", "agents", "scope" }`:
`agents` is the list and `agent` its first entry, so a CLI older than
multi-agent support still reads the file and uses that one agent. Every `skill` subcommand defaults to it; `--agent`, `--global`,
`--project` and `--dir <path>` override it for one invocation without changing
it. With nothing saved and no `--agent`, commands use Claude Code and the
current project and print a one-line hint to run `dreamlake init`.

## Commands

```bash file="terminal" cli-help="skill"
dreamlake skill list
dreamlake skill install dreamlake-notes
dreamlake skill update
dreamlake skill remove dreamlake-notes
```

```bash file="terminal" cli-help="skill list"
dreamlake skill list
# Fetch the latest catalog and show it next to the installed versions
dreamlake skill list --refresh
dreamlake skill list --agent codex --json
```

```bash file="terminal" cli-help="skill install"
# The embedded dreamlake-cli skill; offline when it matches the release
dreamlake skill install dreamlake-cli
# A catalog skill plus whatever it requires, from the latest release
dreamlake skill install dreamlake-notes --agent codex
# One copy for Claude Code and one for Codex
dreamlake skill install dreamlake-notes --agent all --global
# Replace files you edited with the release copies
dreamlake skill install dreamlake-notes --force
```

```bash file="terminal" cli-help="skill update"
# Every skill with a manifest in the selected scope
dreamlake skill update
dreamlake skill update dreamlake-cli --global
# Overwrite edited files; retired files you edited are still kept
dreamlake skill update dreamlake-notes --force
# Go back to an older release, or replace a copy whose version cannot be ordered
dreamlake skill update dreamlake-notes --allow-downgrade
```

```bash file="terminal" cli-help="skill remove"
dreamlake skill remove dreamlake-notes
dreamlake skill remove dreamlake-notes --agent codex --global --json
```

| Command | Reads | Writes | Network |
| --- | --- | --- | --- |
| `init` | embedded bundle and catalog snapshot | preference file, `dreamlake-cli` | never |
| `skill list` | catalog snapshot, install manifests | nothing | only with `--refresh` |
| `skill install <name...>` | latest `catalog.json`, `skills.tar.gz` | the named skills and their `requires` | yes; `dreamlake-cli` alone works offline |
| `skill update [name...]` | latest `catalog.json`, `skills.tar.gz`, manifests | changed, new and retired files | yes; `dreamlake-cli` alone works offline |
| `skill remove <name>` | the manifest | deletes listed, unedited files | never |

## Where it goes

| Agent | `project` (default) | `--global` |
| --- | --- | --- |
| `claude` | `<cwd>/.claude/skills/<name>/` | `~/.claude/skills/<name>/` |
| `codex` | `<cwd>/.agents/skills/<name>/` | `~/.agents/skills/<name>/` |

Skill names are lower-case letters, digits and dashes, starting with a letter
(`^[a-z][a-z0-9-]*$`); anything else is refused with `kind: "invalid-name"`
before any path is resolved, and a skill is always a direct child of the
skills directory. `--project` forces the current project when `dreamlake init`
saved global scope. `--dir <path>` replaces the project root and overrides `--global` and
`--project`, retaining the agent-specific subdirectory. It does not name the
skill directory itself. Codex's supported
[skill locations](https://developers.openai.com/codex/skills) include
`.agents/skills`.

Requires CLI 0.93.0 or later: `--agent all` (or `claude,codex`, or what
`init` saved) selects both rows of the table: every `install`, `update` and `remove` handles each agent's copy on
its own, with its own manifest, from one catalog and one download. `update`
with names skips an agent that does not have the skill, and `remove` skips an
agent where it is absent; a skill absent under every selected agent is still
`not-installed`. When only one agent's copy conflicts, the suggested `--force`
command names that agent alone.

## Sources and versions

Every result names where each skill came from and which release it is:

```text file="output"
skill install  dreamlake-notes
  agent:      claude (saved)
  scope:      project
  catalog:    v2026.11.02 (release)
✓ dreamlake-notes  catalog v2026.11.02   installed 14 file(s)
    target: /work/.claude/skills/dreamlake-notes
⚠ dreamlake-cli    embedded v2026.11.02  already installed — unchanged  (required by dreamlake-notes)
    target: /work/.claude/skills/dreamlake-cli
```

- **embedded** — the `dreamlake-cli` directory built into this CLI, with the
  release tag it was cut from. `install` and `update` use it when the latest
  catalog carries the same version, and whenever the release cannot be reached.
  While the CLI pins a commit rather than a tag, the version is that commit and
  is shown as its first 12 hex digits.
- **catalog** — downloaded from `skills.tar.gz` of the latest release. Only the
  directories you asked for (plus `requires`) are unpacked. The release's
  `catalog.json` must name the tarball under `assets["skills.tar.gz"].sha256`
  (every release does); the download is hashed before anything is unpacked. A
  catalog without that record is refused before any download, and a download
  that does not hash to it is refused before unpacking — both are `status:
  "error"` with `kind: "integrity"` and write nothing.

`install` resolves names through the catalog's `renamed` map first: an old name
prints the new one and exits with `kind: "renamed"`. Each skill's `requires`
are installed with it, in one download.

When the release is unreachable, `dreamlake-cli` still installs from the
embedded copy and the output says the release was not consulted. Any other
skill is an error with `kind: "catalog-unreachable"` and a `nextAction` of
`kind: "download"` naming the tarball address, so you can install by hand:

```bash file="terminal"
curl -L -o skills.tar.gz \
  https://github.com/dreamlake-ai/dreamlake-skills/releases/latest/download/skills.tar.gz
curl -L -o catalog.json \
  https://github.com/dreamlake-ai/dreamlake-skills/releases/latest/download/catalog.json
# Unpack the skill and everything its catalog entry `requires`:
tar -xzf skills.tar.gz -C .claude/skills dreamlake-notes dreamlake-cli
```

A hand-unpacked directory has no manifest. `skill list` reports it as
`unmanaged`, `install` never adopts it on its own (identical: `exists` with
`unmanaged: true` and the command to adopt; otherwise a conflict), and
`install --force` or `update --force` adopts it: the skill's files are
written, a manifest listing only them is written, and your other files are
reported under `extra` — the manifest never lists a file you did not
explicitly accept, so `remove` can never delete one.

### Versions: never an implicit downgrade

Release tags are `vYYYY.MM.DD` with an optional `.N`, and only those are
ordered. Before `install` or `update` compares a single file of a skill that
already has a manifest, it orders the candidate's version against the
installed one:

| Installed vs candidate | Result |
| --- | --- |
| same version string (whatever its form) | compared file by file, as usual |
| candidate newer | compared file by file, as usual |
| candidate older | `exists` with `message: "installed vX is newer than available vY; nothing changed"`; the manifest keeps its version |
| not comparable (a commit pin against a tag, an unknown format, a missing version) | `error`, `kind: "version-unknown"`; nothing changed; `nextAction` is the `--allow-downgrade` command |

`--allow-downgrade` is the explicit way through both: with it an older
release, or one whose version cannot be ordered against the installed one,
replaces the installed copy and the manifest records the new version.
`--force` keeps its single meaning — overwrite files you edited — and does not
bypass this guard; the two combine when an edited skill is to be downgraded.
`update` is the command for changing versions: it compares three ways and
replaces files you did not edit on its own. `install` onto a managed copy
compares bytes only, so with `--allow-downgrade` it still reports every
differing file as a conflict until `--force` is added.

When the release is unreachable, `update` of a skill whose manifest says
`source: "catalog"` is `error`, `kind: "catalog-unreachable"` — it is never
replaced by the embedded copy. `dreamlake-cli` installed from the embedded
copy is updated from a newer embedded copy, and left alone (`exists`, with
the message above) when the embedded copy is older.

### Environment overrides

| Variable | Effect |
| --- | --- |
| `DREAMLAKE_SKILLS_RELEASE_URL` | Release base URL (same layout as GitHub: `<base>/latest/download/catalog.json`, `<base>/download/<tag>/skills.tar.gz`), or a `file://` URL / filesystem path to a directory holding `catalog.json` and `skills.tar.gz`. |
| `DREAMLAKE_SKILLS_DIR` | A local `skills/` directory to treat as the embedded bundle (a checkout, for development): `dreamlake-cli/` plus the optional side files `.manifest.json` and `catalog.json`. An invalid path fails instead of falling back. |
| `DREAMLAKE_SKILLS_MANIFEST_FILE` | JSON `{ tag, commit, files }` describing the bundle in `DREAMLAKE_SKILLS_DIR`; defaults to `<dir>/.manifest.json`, else the bundle is unversioned. |
| `DREAMLAKE_SKILLS_CATALOG_FILE` | A `catalog.json` to use as the embedded snapshot; defaults to `<dir>/catalog.json`. |

## The install manifest

Every install or update writes `<skill>/.dreamlake-skill.json`:

```json file=".dreamlake-skill.json"
{
  "name": "dreamlake-notes",
  "version": "v2026.11.02",
  "source": "catalog",
  "agent": "claude",
  "scope": "project",
  "files": {
    "SKILL.md": "3b1f…",
    "actions/read.md": "9c0a…",
    "reference/cli-notes.md": "77e2…"
  }
}
```

`files` maps every path the installer wrote to the sha256 of those bytes.
`update` and `remove` trust nothing else: a file whose hash still matches is
the installer's to replace or delete; anything else is yours. Paths are
relative, forward-slash, without `..`; a manifest that breaks that rule, or is
a symlink, is rejected when read and the directory is treated as `unmanaged`.

## What is and is not touched

Both `.claude/skills/` and `.agents/skills/` are **shared** directories. Yours
probably already holds hand-written skills next to anything you install. The
installer never `rm -rf`s a directory, never touches `.claude/settings.json` or
`settings.local.json`, and never assumes every entry under a skills directory
is a directory.

A skills directory that is itself a symlink (a dotfiles setup that links
`~/.claude/skills` elsewhere) is followed: the directory is resolved once per
command, every `target` and `path` in the output is the resolved one, and
before any write or delete the target is checked to still be a direct child
of that resolved directory. Symlinks *inside* a skill directory are never
followed: a symlink where a file belongs is a conflict `--force` does not
override, and a symlinked manifest is rejected.

### `install`

| Target | Behaviour | `status` | rc |
| --- | --- | --- | --- |
| absent | write it and a manifest | `installed` | 0 |
| present with a manifest, every file byte-identical | refresh the manifest only | `exists` | 0 |
| present with a manifest, differs | **refuse**, list the paths, print the `--force` command | `conflict` | 1 |
| present with a manifest, differs, `--force` | overwrite **only the files that differ** | `installed` | 0 |
| present **without** a manifest, every file byte-identical, nothing else there | nothing written, no manifest; `unmanaged: true`, `nextAction` is `skill update <name> --force` | `exists` | 0 |
| present **without** a manifest, anything missing or different, or other files present | **refuse**; `conflicts` lists the missing/differing files, `extra` the others | `conflict` (`kind: "unmanaged"`) | 1 |
| present **without** a manifest, `--force` | write the missing and differing files, write a manifest listing **only the skill's files**; other files kept under `extra` | `installed` (`exists` when nothing had to be written) | 0 |
| a file or symlink where a file belongs | refuse; `--force` does not override | `conflict` | 1 |
| a file where the directory belongs | refuse | `error` | 1 |

```text file="output"
✗ dreamlake-cli is already installed at /work/.claude/skills/dreamlake-cli and differs from the embedded v2026.11.02 copy
    · SKILL.md
    · reference/cli-notes.md

  overwrite it with:
        dreamlake skill install dreamlake-cli --force
```

Nothing was written. A skill you edited survives a mistyped install.

### `update`

`update` compares three things per path — the old manifest's hash, the local
file, and the new release — and never deletes anything the manifest does not
vouch for:

| Old manifest | Local file | New release | Result |
| --- | --- | --- | --- |
| hash A | matches A | A | unchanged |
| hash A | matches A | B | overwritten |
| hash A | edited | B | **conflict**; `--force` overwrites |
| hash A | edited | A | unchanged (already current) |
| hash A | missing | any | written |
| hash A | matches A | retired | **deleted**, empty directories pruned |
| hash A | edited | retired | kept, listed under `extra` |
| none | present | B | **conflict** (new path collides with your file) — even when the bytes are identical, since the manifest never vouched for it; `--force` adopts it (overwriting only if it differs) |
| none | absent | B | written |
| no manifest | anything | any | every present file is a **conflict** until `--force` adopts the directory and writes a manifest |

Status is `installed` when anything was written or deleted, `exists` when the
skill was already current, `conflict` when at least one path needs `--force`,
`error` when the skill is not installed, its manifest is invalid, or its
version cannot be ordered against the candidate's (`version-unknown`). Without
names, `update` takes every manifest-bearing skill in the selected agent and
scope.

Neither command adopts a file on its own: `install` into a directory without
a manifest and `update` of a managed directory both treat a file the
manifest does not list as yours, identical or not, until `--force` accepts it.

### `remove`

Deletes the files the manifest lists whose hash still matches, then the
manifest, then directories left empty — the skill directory included. A file
you edited and a file the manifest does not list are **kept** and reported
under `kept`; the status is still `removed`. There is no `--force`: nothing
makes the installer delete an edit. When `SKILL.md` is among the kept files
the agent still discovers the skill, and the prose output says so — delete
the directory yourself if that is what you want. A directory without a
manifest is an `error` (`kind: "unmanaged"`): it was not installed by the
CLI, so the CLI will not delete it.

## Reminders after updating

At the start of a terminal command, the CLI compares each installed manifest's
version with the newest version it knows — the embedded `dreamlake-cli` tag,
and the catalog snapshot for other skills — for both agents, in the current
project and your home directory. When something newer exists it prints one
stderr line per installed path per CLI version:

```text file="stderr"
Installed skill /work/.claude/skills/dreamlake-cli is v2026.10.27; v2026.11.02 is available. Update with: dreamlake skill update dreamlake-cli --agent claude --dir '/work'
```

Reminders never change files, never use the network, and stay out of JSON,
piped and background invocations. `skill list --refresh` is the networked
check and shows `latest` next to each installed version.

## `--json`

Every subcommand emits one object with a discriminated `status` and a
required, nullable `nextAction` (`{ "kind": "run", "command" }`,
`{ "kind": "download", "url" }`, or `null`). On failure, stdout still carries
exactly one object and stderr stays empty.

```json file="dreamlake skill list --refresh --json"
{
  "status": "ok",
  "source": "embedded-skills",
  "agent": "claude",
  "catalog": { "version": "v2026.10.27", "origin": "embedded" },
  "latest": { "version": "v2026.11.02", "origin": "release" },
  "skills": [
    {
      "name": "dreamlake-cli",
      "description": "Install, log in, upload and download with the dreamlake CLI.",
      "requires": [],
      "files": 41,
      "embedded": true,
      "latest": "v2026.11.02",
      "project": { "path": "/work/.claude/skills/dreamlake-cli", "state": "installed", "version": "v2026.10.27" },
      "global":  { "path": "/home/you/.claude/skills/dreamlake-cli", "state": "absent", "version": null }
    }
  ],
  "nextAction": null
}
```

`state` is one of `absent`, `installed`, `modified` (a manifest file was
edited or removed), `unmanaged` (a directory with no valid manifest; `error`
says why when one was rejected), or `blocked` (something that is not a
directory is in the way). When `--refresh` fails, `latest` is
`{ "error", "url" }` and the rest of the object is unchanged.

```json file="dreamlake init --agent codex --json"
{
  "status": "installed",
  "agent": "codex",
  "scope": "project",
  "catalog": { "version": "v2026.10.27", "origin": "embedded" },
  "skills": [
    {
      "status": "installed",
      "skill": "dreamlake-cli",
      "version": "v2026.10.27",
      "source": "embedded",
      "scope": "project",
      "target": "/work/.agents/skills/dreamlake-cli",
      "files": ["/work/.agents/skills/dreamlake-cli/SKILL.md", "…"],
      "manifest": "/work/.agents/skills/dreamlake-cli/.dreamlake-skill.json",
      "nextAction": null
    }
  ],
  "preferences": { "agent": "codex", "scope": "project", "path": "/home/you/.local/state/dreamlake/skill-preferences.json" },
  "available": [{ "name": "dreamlake-notes", "description": "Read, edit and share DreamLake Notes." }],
  "nextAction": null
}
```

`init` adds `preferences` (what was saved, and where) and `available` (the
other skills in the embedded catalog snapshot). Its `catalog.origin` is never
`release`: `init` does not use the network.

```json file="dreamlake skill install dreamlake-notes --json"
{
  "status": "installed",
  "agent": "claude",
  "scope": "project",
  "catalog": { "version": "v2026.11.02", "origin": "release" },
  "skills": [
    {
      "status": "installed",
      "skill": "dreamlake-notes",
      "version": "v2026.11.02",
      "source": "catalog",
      "scope": "project",
      "target": "/work/.claude/skills/dreamlake-notes",
      "files": ["/work/.claude/skills/dreamlake-notes/SKILL.md", "…"],
      "manifest": "/work/.claude/skills/dreamlake-notes/.dreamlake-skill.json",
      "nextAction": null
    },
    {
      "status": "exists",
      "skill": "dreamlake-cli",
      "version": "v2026.11.02",
      "source": "embedded",
      "scope": "project",
      "target": "/work/.claude/skills/dreamlake-cli",
      "files": [],
      "requiredBy": "dreamlake-notes",
      "nextAction": null
    }
  ],
  "nextAction": null
}
```

The top-level `status` is the worst across `skills` (`error` > `conflict` >
`installed` > `exists`). Per skill, `files` lists what **this run** wrote, so
`files: []` is the proof nothing happened; a conflict carries `conflicts`;
unowned files appear under `extra`; an `exists` that was a guarded no-op
(the installed copy is newer, or the target has no manifest and was not
adopted — then also `unmanaged: true`) carries `message`. `update` adds
`previous` (the manifest's version before the run) and `deleted`. `catalog.origin` is `release`,
`embedded` (the release was not consulted or unreachable — then
`catalog.unreachable` says why) or `none`.

```json file="offline: dreamlake skill install dreamlake-notes --json"
{
  "status": "error",
  "agent": "claude",
  "scope": "project",
  "catalog": { "version": "v2026.10.27", "origin": "embedded", "unreachable": "cannot reach https://github.com/dreamlake-ai/dreamlake-skills/releases/latest/download/catalog.json: fetch failed" },
  "error": "cannot reach the skills release (…) — dreamlake-notes must come from the release. Download skills.tar.gz by hand and unpack the needed directories into your skills directory.",
  "kind": "catalog-unreachable",
  "nextAction": { "kind": "download", "url": "https://github.com/dreamlake-ai/dreamlake-skills/releases/latest/download/skills.tar.gz" }
}
```

```json file="dreamlake skill remove dreamlake-notes --json"
{
  "status": "removed",
  "agent": "claude",
  "scope": "project",
  "skill": "dreamlake-notes",
  "target": "/work/.claude/skills/dreamlake-notes",
  "version": "v2026.11.02",
  "deleted": ["/work/.claude/skills/dreamlake-notes/actions/read.md", "…"],
  "kept": ["NOTES.md", "SKILL.md"],
  "nextAction": null
}
```

`kept` lists, relative to `target`, every file left behind: manifest files
you edited and files the manifest never listed. `remove` has only `removed`
and `error` statuses.

### Several agents

With one agent every object above is unchanged. With several, the top-level
`agent` is replaced by `agents`, and:

- `install`, `update` and `init` list one entry per agent and skill in
  `skills`, each with an `agent`; `init`'s `preferences` carries `agents`.
- `remove` puts one single-agent result per agent in `removals`; the top level
  has `agents`, `scope`, `skill`, `status` (`error` when any removal failed)
  and that failure's `error` and `kind`.
- `list` replaces each row's `project` and `global` with `installs`, keyed by
  agent.

```json file="dreamlake skill list --agent all --json"
{
  "status": "ok",
  "source": "embedded-skills",
  "agents": ["claude", "codex"],
  "catalog": { "version": "v2026.10.27", "origin": "embedded" },
  "skills": [
    {
      "name": "dreamlake-cli",
      "description": "Install, log in, upload and download with the dreamlake CLI.",
      "requires": [],
      "files": 41,
      "embedded": true,
      "latest": "v2026.10.27",
      "installs": {
        "claude": {
          "project": { "path": "/work/.claude/skills/dreamlake-cli", "state": "absent", "version": null },
          "global":  { "path": "/home/you/.claude/skills/dreamlake-cli", "state": "installed", "version": "v2026.10.27" }
        },
        "codex": {
          "project": { "path": "/work/.agents/skills/dreamlake-cli", "state": "absent", "version": null },
          "global":  { "path": "/home/you/.agents/skills/dreamlake-cli", "state": "installed", "version": "v2026.10.27" }
        }
      }
    }
  ],
  "nextAction": null
}
```

Error `kind` values: `invalid-agent`, `agent-required`, `canceled`,
`invalid-name`, `unknown-skill`, `renamed`, `ambiguous`, `bad-catalog`,
`catalog-unreachable`, `integrity`
(the release catalog names no sha256 for `skills.tar.gz`, or the download does
not match it),
`bad-release`, `missing-in-release`, `version-unknown`, `not-installed`,
`not-a-directory`, `unmanaged`, `invalid-manifest`, `write-failed`,
`remove-failed`, `no-bundle`.

## Where the skills come from

Skill content is not authored in this repository. Facts about commands live in
these docs; task steps live in `dreamlake-skills/<name>/actions/`; each skill's
`reference/` is fetched from the documentation sites by that repository's CI.
This CLI pins one dreamlake-skills revision in `skills.lock` (a release tag,
or a commit until the first tag exists); the build downloads that revision's
archive, verifies its sha256, and embeds `dreamlake-cli/` together with a
manifest of its tag, commit and file hashes. The npm package ships the same
directory as `skills/dreamlake-cli/` with `skills/.manifest.json` and
`skills/catalog.json` beside it, so an `npm install` reports the same version
and source as the native binary. Bumping the pin is an ordinary pull request.

## Release acceptance checklist

- [ ] Edit docs first; regenerate the command-help examples
      (`node docs/scripts/gen-help-examples.mjs`) and commit them with the source.
- [ ] Run source tests and the isolated native packaging test in CI.
- [ ] Compile all platforms from the reviewed commit. The build embeds the
      pinned release's `dreamlake-cli` — `SKILL.md`, `skill.json` and every
      `reference/` page its `docs[]` names — and rejects a bundle missing any
      of them.
- [ ] Test a copied binary outside the checkout with a temporary home and no
      `DREAMLAKE_SKILLS_*` variables: `init`, byte readback, identical reinstall,
      conflict refusal, forced update preserving peer files, `remove` keeping an
      edited file, the offline error shape, and — against local release
      directories — a `requires` closure install, an `update` that overwrites,
      retires and adds files and rewrites the manifest, a release without a
      checksum refused, an older release left alone.
- [ ] Pack the npm package, install it into an empty prefix, and read the
      same skill back through `bin/dreamlake.js` (`skill list`, `skill install`).
- [ ] Publish immutable versioned binaries and npm packages; verify downloaded
      bytes before moving release pointers.
- [ ] Repeat `dreamlake init` and `skill install <name>` from the public native
      download and npm package.

`bun run scripts/verify-native-skills.ts` runs the isolated packaging gate and
the npm acceptance locally.
