# DreamLake Skills

Public [Claude](https://claude.ai/code) **skills** for working with
[DreamLake](https://dreamlake.ai) — each is a self-contained `SKILL.md` that teaches
an AI agent (Claude Code, or any Skills-compatible client) how to perform a DreamLake
task correctly.

## Available skills

| Skill | What it does |
|---|---|
| [`dreamlake-source`](./dreamlake-source/SKILL.md) | Upload a robot dataset (LeRobot/zarr/MCAP/raw folders) to object storage or DreamLake so a `.dreamrc` can visualize it; layout rules, listing manifests, verification |
| [`dreamlake-viz`](./dreamlake-viz/SKILL.md) | Author the `.dreamrc` dataset-visualization file — formats, storage, view components, annotations. GENERATED from the viz docs (`scripts/sync-dreamlake-viz.sh` re-syncs; never hand-edit) |
| [`dreamlake-artifacts`](./dreamlake-artifacts/SKILL.md) | Publish, version, share, and view renderable artifacts (HTML/React/Markdown/SVG/Mermaid/code) via the `dreamlake artifact` CLI |
| [`dreamlake-artifact-authoring`](./dreamlake-artifact-authoring/SKILL.md) | Write the artifact *content* so it renders in DreamLake's sandboxed frame — self-containedness, per-kind templates, design quality. Pairs with `dreamlake-artifacts` |
| [`dreamlake-annotations`](./dreamlake-annotations/SKILL.md) | Upload annotated robot-training episodes (video + joints + subtasks, multi-camera) to a DreamLake annotation with the Python SDK, revise them, and search |
| [`workflow-generator`](./workflow-generator/SKILL.md) | Generate DreamLake WorkflowSpec v1 JSON (stages, compute/agent/sampler/control nodes, typed edges) from a natural-language goal, then validate + push via `dreamlake workflow push` (CLI ≥ 0.5.0) |
| [`video-labeling-workflow`](./video-labeling-workflow/SKILL.md) | Create and publish a video subtask-labeling workflow — segment a manipulation video into subtasks, estimate hand pose, score against reference annotations, publish a dataset |
| [`remote-source-check`](./remote-source-check/SKILL.md) | Verify a connected source really holds the files a workflow will read, before they are written into a spec |
| [`workflow-publish`](./workflow-publish/SKILL.md) | Validate a WorkflowSpec file and push it to a namespace, then report the canvas URL |

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

Keep the trailing slash on the destination: `ln -s <src> ~/.claude/skills/` refuses to
clobber an existing skill of the same name, whereas naming the destination explicitly
(`…/skills/dreamlake-artifacts`) silently creates a nested link *inside* it when one
already exists. If `ln` reports `File exists`, remove the old copy and re-run.

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

Add a new top-level directory `my-skill/` containing a `SKILL.md` with YAML
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
