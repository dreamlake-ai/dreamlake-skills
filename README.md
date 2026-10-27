# DreamLake skills

Agent skills for [DreamLake](https://dreamlake.ai): the task procedures an
agent (Claude Code, Codex or any other client that reads `SKILL.md`) follows to
get work done with the DreamLake CLI, SDK and web app.

Product facts (commands, flags, API, behaviour) live on the docs sites:
[docs.dreamlake.ai](https://docs.dreamlake.ai), [cli.dreamlake.ai](https://cli.dreamlake.ai)
and [viz.dreamlake.ai](https://viz.dreamlake.ai). This repository holds the
steps. Each skill names the docs pages it needs, and CI copies those pages into
its `reference/` directory, so an installed skill works offline and never
drifts from what is actually released.

## Skills

| Skill | Use it for | Requires |
|---|---|---|
| `dreamlake-cli` | Install and log in to the DreamLake CLI, pick an environment, upload and download data, browse or upload Sources, grant Project access, move whole Projects, transfer ownership, link writes to agent sessions, manage Vault, register UDFs, push workflows; routes compute and domain work elsewhere. | — |
| `dreamlake-lakeshore` | Operate DreamLake compute through the CLI: connect Lakeshore (Add Host, Runtime workers, queue mounts), enroll and inspect hosts and terminal sessions, read Slurm and externally launched jobs, provision machines through a user-configured launch server, manage Infrastructure Stacks, and connect AWS. | `dreamlake-cli` |
| `dreamlake-notes` | Work with DreamLake collaborative Notes through the CLI: find, read, edit with revision guards, save or recover versions, follow live collaboration, attach files and media, create notes, set summaries, file into Projects, link list items to Notes or artifacts, transfer a standalone Note. | `dreamlake-cli` |
| `dreamlake-tasks` | Design and operate DreamLake task folders, subtasks, waterfall and status views, progress events and linked Notes for prompts, comments, details and acceptance; for task tracking inside a Project, not execution scheduling, and only after checking the installed CLI and target server. | `dreamlake-cli` |
| `dreamlake-artifacts` | Author content that renders inside DreamLake's isolated offline artifact frame, then publish, version, list, share, revoke, remove and restore artifacts with the CLI, and reference them from Notes. | `dreamlake-cli` |
| `dreamlake-scenes` | Build, validate and publish MuJoCo (MJCF) and URDF scenes on DreamLake: source and measure assets, derive placements, author the base scene, compose layered stacks, validate physics per body, package, push, preview, pull back byte-identical, version, delete and restore. | `dreamlake-cli` |
| `dreamlake-libraries` | Publish, curate, search and pull DreamLake asset libraries: push a directory of 3D assets zero-config, curate it with dreamlake.yml, add thumbnails and semantic search, search per asset across libraries, inspect without downloading, pull one asset or the whole tree, add or remove single assets. | `dreamlake-cli` |
| `dreamlake-datasets` | Get a robot dataset reachable and rendered in DreamLake: lay out the files, upload or link them as a Source, prove the paths a workflow will read, and write the .dreamrc that binds fields to views, including MuJoCo/URDF sim playback. | `dreamlake-cli` |
| `sim-to-mcap` | Roll a trained policy out in a local Python physics simulator and write an indexed MCAP with Foxglove /tf, /robot and /metrics channels that DreamLake plays natively, then hand the file to dreamlake-datasets. | `dreamlake-datasets` |
| `dreamlake-workflows` | Design a DreamLake WorkflowSpec v1 from a natural-language data-production, labeling or training goal, validate it against the bundled schema, publish it to the right namespace with the CLI, and recover from validation errors. | `dreamlake-cli` |
| `video-labeling-workflow` | Create and publish the fixed DreamLake video subtask-labeling workflow: collect the source, video and reference-annotation paths, verify the worker can read them, fill the bundled template, confirm with the user, and push a workflow they can Run from the canvas. | `dreamlake-workflows`, `dreamlake-datasets` |
| `dreamlake-annotations` | Upload, extend, revise and read back DreamLake annotations with the Python SDK: annotated robot-video episodes through the VideoAnnotation preset, or any user-defined schema through the generic Annotation. | — |
| `launch-claude-remote` | Create a new named Claude Remote Control session with maximum permissions in a detached tmux terminal on this host, so the user can continue in their Claude app; keeps existing sessions running. | — |
| `launch-codex-chat` | Create a new named, resumable Codex chat with maximum permissions on this host's running app-server daemon, so the user can continue it in their Codex app; keeps existing sessions and daemons running. | — |

Earlier skills were merged into these; [`renamed.json`](renamed.json) maps
each retired name (`dreamlake-source`, `workflow-publish`, ...) to its
successor, and `dreamlake skill install <old name>` prints the new one. Where
each section of the old skills went is recorded in
[`docs/migration-0010/`](docs/migration-0010/README.md).

## Install

With the [`dreamlake` CLI](https://cli.dreamlake.ai):

```bash
dreamlake init                                 # choose agent and scope; installs dreamlake-cli
dreamlake skill list                           # the catalog, with installed versions
dreamlake skill install dreamlake-artifacts    # brings dreamlake-cli along (requires)
dreamlake skill update                         # refresh what is installed
```

By hand: every release carries `skills.tar.gz`, whose top-level entries are
the skill directories, and `catalog.json`, which lists each skill with its
`requires` and, under `assets`, the tarball's sha256 and size so you can verify
the download. Download the latest, extract it, and copy the skill directory plus
every directory it requires into your agent's skills folder: `.claude/skills/`
for Claude Code or `.agents/skills/` for Codex, either in the project or in
your home directory.

```bash
curl -fsSL -o skills.tar.gz \
  https://github.com/dreamlake-ai/dreamlake-skills/releases/latest/download/skills.tar.gz
mkdir -p dreamlake-skills && tar -xzf skills.tar.gz -C dreamlake-skills
mkdir -p .claude/skills
cp -R dreamlake-skills/dreamlake-artifacts dreamlake-skills/dreamlake-cli .claude/skills/
```

Install the same set with either method; the CLI does nothing the archive does
not contain.

## Unattended agents

Skills drive DreamLake through the `dreamlake` CLI alone. Where an agent runs
without a person at the keyboard, set two variables explicitly:

| Variable | Why |
|---|---|
| `DREAMLAKE_API_KEY` | The identity the work is attributed to: inject the end user's token so the agent acts as them |
| `DREAMLAKE_REMOTE` | Which deployment to talk to; otherwise the CLI uses whatever environment is active on that machine |

## Repository layout

```
<name>/            one skill: skill.json, SKILL.md, actions/, optional tools/, assets/ and agents/ (Codex UI metadata, openai.yaml), generated reference/
_template/         copy this to start a new skill
skill.schema.json  what skill.json must look like
renamed.json       retired skill names -> current names
catalog.json       generated index of all skills (scripts/catalog.py)
references.lock    generated record of every fetched reference page (scripts/sync_references.py)
scripts/           sync_references.py, check.py, catalog.py, package.py and their tests
```

How to write or change a skill, and the commands behind CI, are in
[CONTRIBUTING.md](CONTRIBUTING.md). Releases are tagged `vYYYY.MM.DD` by the
nightly workflow whenever `main` has moved since the previous tag.
