# DreamLake Skills

Public agent **skills** for working with [DreamLake](https://dreamlake.ai) and
related development tools. Each skill has a `SKILL.md` entrypoint for Claude Code,
Codex, or another compatible client; individual skills can require a specific host.

**Where do I edit a skill, and is it duplicated elsewhere?** See the
[maintenance inventory](MAINTENANCE.md) for every skill's source, generated or
manual status, and known overlaps. This catalog and the CLI bundle are separate
distribution channels. `dreamlake skill install` installs the CLI's bundled
snapshot, not every skill in this repository.

## Available skills

| Skill | What it does |
|---|---|
| [`sim-to-mcap`](./sim-to-mcap/SKILL.md) | Turn a trained policy + physics sim (MuJoCo/mjlab/Isaac) into a DreamLake-ready MCAP — roll out and emit Foxglove `/tf` (poses), `/robot` (meshes), `/metrics` (scalars). The upstream half of "training result → visualized" |
| [`dreamlake-source`](./dreamlake-source/SKILL.md) | Get a robot dataset into a DreamLake source — link third-party storage (S3/HF/Dropbox), or upload the bytes so it can be linked; layout rules, listing manifests, verification |
| [`dreamlake-dataset-viz`](./dreamlake-dataset-viz/SKILL.md) | Visualize a DreamLake source by authoring its `.dreamrc` (LeRobot/zarr/MCAP/folders) — format matching, view bindings, the validate-and-iterate loop |
| [`dreamlake-envs`](./dreamlake-envs/SKILL.md) | Push a MuJoCo scene or URDF robot as a versioned env — extract a self-contained directory from a repo, verify it compiles, push it, get an interactive 3D viewer page — or compose a layered env from a `dreamlake.layers.json` stack (Merge / Attach / Update / Remove / Patch) |
| [`dreamlake-libraries`](./dreamlake-libraries/SKILL.md) | Publish, search, inspect, and download reusable asset libraries |
| [`launch-codex-chat`](./launch-codex-chat/SKILL.md) | Create a named, persistent chat on an existing Codex server and verify it is available to continue in a connected app. [Protocol and troubleshooting](./launch-codex-chat/references/launching-chats.md) |
| [`dreamlake-artifacts`](./dreamlake-artifacts/SKILL.md) | Publish, version, share, and view renderable artifacts (HTML/React/Markdown/SVG/Mermaid/code) via the `dreamlake artifact` CLI |
| [`dreamlake-artifact-authoring`](./dreamlake-artifact-authoring/SKILL.md) | Write the artifact *content* so it renders in DreamLake's sandboxed frame — self-containedness, per-kind templates, design quality. Pairs with `dreamlake-artifacts` |
| [`dreamlake-notes`](./dreamlake-notes/SKILL.md) | The whole notes surface — create and list, read a section or a line range, replace text by name rather than line number, grep across every note for where a phrase is, attach files and get a link that renders them |
| [`dreamlake-cli`](./dreamlake-cli/SKILL.md) | The whole `dreamlake` CLI reference, generated from its docs. Native and npm releases also bundle this skill; install their matching copy with `dreamlake skill install dreamlake-cli` |
| [`dreamlake-scene-generation`](./dreamlake-scene-generation/SKILL.md) | Build and edit MuJoCo scenes with internet models, user files, procedural MJCF or optional DreamLake libraries: measure and place models, validate physics, render previews, publish and reuse versioned envs. [Install and use guide](https://docs.dreamlake.ai/scene-generation/quickstart) |
| [`dreamlake-annotations`](./dreamlake-annotations/SKILL.md) | Upload annotated robot-training episodes (video + joints + subtasks, multi-camera) to a DreamLake annotation with the Python SDK, revise them, and search |
| [`workflow-generator`](./workflow-generator/SKILL.md) | Generate DreamLake WorkflowSpec v1 JSON (stages, compute/agent/sampler/control nodes, typed edges) from a natural-language goal, then validate + push via `dreamlake workflow push` (CLI ≥ 0.5.0) |
| [`video-labeling-workflow`](./video-labeling-workflow/SKILL.md) | Create and publish a video subtask-labeling workflow — segment a manipulation video into subtasks, estimate hand pose, score against reference annotations, publish a dataset |
| [`remote-source-check`](./remote-source-check/SKILL.md) | Verify a connected source really holds the files a workflow will read, before they are written into a spec |
| [`workflow-publish`](./workflow-publish/SKILL.md) | Validate a WorkflowSpec file and push it to a namespace, then report the canvas URL |

### The source pair

`dreamlake-source` gets the bytes connected; `dreamlake-dataset-viz` makes
them render. **Install both for the full "my data → visualized in DreamLake"
flow** — source preps layout and linking, dataset-viz writes the `.dreamrc`,
and each links to https://viz.dreamlake.ai for option-level detail (every
docs page serves clean markdown at `<page-url>.md`), so the skills stay thin. Changes to task procedures still require an explicit
docs/skill comparison until those skills are generated from docs.

### The sim-training trio

For a *training result* there's no dataset yet — the bytes have to be made
first. `sim-to-mcap` rolls the trained policy out and writes the MCAP; the
source pair then uploads and renders it:

```
sim-to-mcap        →  dreamlake-source  →  dreamlake-dataset-viz
emit tf+mesh+metrics   upload the .mcap      write the .dreamrc
```

**Install all three** to go from a checkpoint to an agent playing in DreamLake.
`sim-to-mcap` hands off by name to the other two.

These are end-user skills. Developers integrating the `@dreamlake/viz`
*library* (components, schema-viz, file-preview) don't need a skill — point
your agent at the LLM-readable docs instead:
https://viz.dreamlake.ai/llms.txt.

### The artifacts pair

`dreamlake-artifacts` publishes; `dreamlake-artifact-authoring` writes content that
actually renders.

**Install both or neither.** The frame runs offline (`connect-src 'self'`), so an
artifact written the way most web pages are written — a CDN `<script>`, a web font, a
remote image, a `fetch` — publishes successfully and renders **blank**. With only
`dreamlake-artifacts` installed, that is the default outcome, and it looks like a
product bug rather than a missing skill.

### The video-labeling trio

The last three are one workflow split three ways, and they call each other:

```
video-labeling-workflow
├── remote-source-check     (step 3 — does that source hold those paths?)
└── workflow-publish        (step 5 — validate and push)
```

**Install all three or none.** `video-labeling-workflow` invokes the other two by
name; on its own it will improvise the checking and the pushing, which is exactly
what splitting them out was meant to stop. The other two are also useful alone —
`workflow-publish` publishes any spec, `remote-source-check` validates any source
reference.

## Installation

The simplest route is to ask Claude Code, giving it this repo's URL:

> install the DreamLake artifacts skills from https://github.com/dreamlake-ai/dreamlake-skills

Each top-level directory is one skill. To do it by hand — **symlink, don't copy**, so
`git pull` here updates every installed skill:

```bash
git clone https://github.com/dreamlake-ai/dreamlake-skills.git ~/dreamlake-skills
mkdir -p ~/.claude/skills

# user-scoped (all your projects)
ln -s ~/dreamlake-skills/dreamlake-artifacts          ~/.claude/skills/
ln -s ~/dreamlake-skills/dreamlake-artifact-authoring ~/.claude/skills/
```

Use `.claude/skills/` instead of `~/.claude/skills/` to scope a skill to one project.

For the Codex chat launcher, install its complete directory into Codex's user
skills directory (or `$CODEX_HOME/skills` when configured):

```bash
mkdir -p ~/.codex/skills
ln -s ~/dreamlake-skills/launch-codex-chat ~/.codex/skills/
```

Then ask Codex to use `$launch-codex-chat`. The helper runs on the machine
hosting the already connected Codex server. This catalog installation does not
require the DreamLake CLI, Nymph, or a DreamLake login.

Keep the trailing slash on the destination: `ln -s <src> ~/.claude/skills/` refuses to
clobber an existing skill of the same name, whereas naming the destination explicitly
(`…/skills/dreamlake-artifacts`) silently creates a nested link *inside* it when one
already exists. If `ln` reports `File exists`, inspect the existing skill and preserve local
edits before replacing it; do not blindly remove the old copy.

Claude discovers each skill by its `name`/`description` frontmatter and invokes it when
a task matches. **Skills that name each other must be installed together** — see the
artifacts pair and the video-labeling trio above.

## Running the video-labeling trio

These three drive DreamLake through the **`dreamlake` CLI** and nothing else — no
source checkout, no worker environment, no repository-local paths. That is what lets
them run on a hosted agent rather than only on the machine they were written on.

```bash
curl -fsSL https://dl.dreamlake.ai/install.sh | sh   # installs under $HOME, no sudo
dreamlake login                                       # or inject a token, below
```

Two things are worth setting explicitly wherever an agent runs unattended:

| | Why |
|---|---|
| `DREAMLAKE_API_KEY` | The identity the work is attributed to. Injecting the end user's token per session makes the agent act as them — their namespaces, their permissions, their datasets |
| `DREAMLAKE_REMOTE` | Which deployment to talk to. Without it the CLI uses whatever environment is *active on that machine*, so an agent holding a production token can end up calling a staging server (and getting a 401 that looks like a bad token) |

## Contributing a skill

Choose the canonical source first using the [maintenance rules](MAINTENANCE.md).
Product procedures belong with the owning docs and should be generated here;
standalone utilities can be authored here with their helpers and documentation.
Register the skill in `catalog.json`, add its README row, and run
`python3 scripts/catalog.py` followed by `python3 scripts/catalog.py --check`.

Each top-level directory `my-skill/` contains a `SKILL.md` with YAML
frontmatter:

```markdown
---
name: my-skill
description: One or two sentences on what this skill does and when to use it.
---

# My Skill

...instructions...
```

Keep skills accurate to the shipped CLI/UI, concrete, and command-first.

## Docs-first maintenance

Maintain procedures and executable examples in their owning docs. Notes, CLI
and scene-generation are now reproducible outputs, not independent writing
surfaces:

| Output | Source |
|---|---|
| `dreamlake-notes/SKILL.md`, `actions/*`, selected references | `dreamlake-workspace/docs/skill-guides/notes/` plus generated Notes docs |
| `dreamlake-cli/**` | `dreamlake-cli/docs/pages/**/+Page.mdx` and its docs generator |
| `dreamlake-scene-generation/**` | `dreamlake-workspace/docs/skill-guides/scene-generation/` (router, actions, tools) plus the generated scene-generation/libraries/envs/envs-layers references |

Task routing is maintained separately from product facts: Notes uses
`dreamlake-workspace/docs/skill-guides/notes/`, CLI uses
`dreamlake-cli/docs/skill-guides/cli/`, and scene-generation uses
`dreamlake-workspace/docs/skill-guides/scene-generation/` (whose `tools/`
ship inside the skill and are hashed as guide source). Entrypoints route to
independent action files; selected generated references remain available for
deeper lookup. Source provenance records guide hashes with source commits and
generator hashes. Only Notes, CLI and scene-generation are migrated. Remaining
product skills need explicit paired review; standalone utilities are maintained
here. The [inventory](MAINTENANCE.md) distinguishes them.

With Git, Node and Python 3.12+, and authorized checkouts of the source repos:

```bash
python3 scripts/sync-docs.py --workspace /path/to/dreamlake-workspace --cli /path/to/dreamlake-cli
python3 scripts/sync-docs.py --workspace /path/to/dreamlake-workspace --cli /path/to/dreamlake-cli --check
python3 scripts/catalog.py
python3 scripts/catalog.py --check
python3 -m unittest discover -s scripts -p 'test_*.py'
python3 scripts/sync-docs.py --verify-files
```

Commit source docs first. Synchronization exports committed HEAD snapshots into
scratch directories and runs the original generators; it never regenerates into
those checkouts. Review and commit the generated skills with `sources.json` and
`generated-files.json`. The latter defines owned files; unrelated resources survive.
A changed generated file being removed requires manual reconciliation.
Before publication, run both source generators and checks, public offline sync
tests and integrity checks, then evaluate representative actions and capability
boundaries offline. Current-source `--check` is the drift check; locked
reproduction and integrity checks do not prove freshness.

`--check` checks current source HEADs. Add `--locked` to reproduce recorded source
commits instead. Public CI runs offline tests and file-integrity verification;
it does **not** read private source repos or prove upstream freshness. Run the
full source check locally before merging. Publish companion source branches so
reviewers can access the recorded commits. Other skills still need explicit
paired docs/skill review until migrated; no automatic sync is claimed for them.

A source synchronization is not a release. After publication, check live docs
and a fresh installed skill, then report their URLs, source revisions, update
command and evidence. See [AGENTS.md](AGENTS.md) for the maintenance policy.
