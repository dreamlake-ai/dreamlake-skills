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
| `dreamlake-agents` | Create and maintain DreamLake agent definitions, and use the built-in agent's discovered resource APIs while preserving resource permissions and recovery. | `dreamlake-cli` |
| `dreamlake-lakeshore` | Operate DreamLake compute through the CLI: connect Lakeshore (Add Host, Runtime workers, queue mounts), enroll and inspect hosts and terminal sessions, read Slurm and externally launched jobs, provision machines through a user-configured launch server, manage Infrastructure Stacks, and connect AWS. | `dreamlake-cli` |
| `dreamlake-memos` | Work with DreamLake collaborative Memos through the CLI: find, read, edit with revision guards, save or recover versions, follow live collaboration, attach files and media, create memos, set summaries, file into Projects, link list items to Memos or artifacts, transfer a standalone Memo. | `dreamlake-cli` |
| `dreamlake-tasks` | Design and operate DreamLake task folders, subtasks, waterfall and status views, progress events and linked Memos for prompts, comments, details and acceptance; for task tracking inside a Project, not execution scheduling, and only after checking the installed CLI and target server. | `dreamlake-cli` |
| `dreamlake-artifacts` | Author content that renders inside DreamLake's isolated offline artifact frame, then publish, version, list, share, revoke, remove and restore artifacts with the CLI, and reference them from Memos. | `dreamlake-cli` |
| `dreamlake-scenes` | Build, validate and publish MuJoCo (MJCF) and URDF scenes on DreamLake: source and measure assets, derive placements, author the base scene, compose layered stacks, validate physics per body, package, push, preview, pull back byte-identical, version, delete and restore. | `dreamlake-cli` |
| `dreamlake-libraries` | Publish, curate, search and pull DreamLake asset libraries: push a directory of 3D assets zero-config, curate it with dreamlake.yml, add thumbnails and semantic search, search per asset across libraries, inspect without downloading, pull one asset or the whole tree, add or remove single assets. | `dreamlake-cli` |
| `dreamlake-datasets` | Get a robot dataset reachable and rendered in DreamLake: lay out the files, upload or link them as a Source, prove the paths a workflow will read, and write the .dreamrc that binds fields to views, including MuJoCo/URDF sim playback. | `dreamlake-cli` |
| `sim-to-mcap` | Roll a trained policy out in a local Python physics simulator and write an indexed MCAP with Foxglove /tf, /robot and /metrics channels that DreamLake plays natively, then hand the file to dreamlake-datasets. | `dreamlake-datasets` |
| `dreamlake-workflows` | Design a DreamLake WorkflowSpec v1 from a natural-language data-production, labeling or training goal, validate it against the bundled schema, publish it to the right namespace with the CLI, and recover from validation errors. | `dreamlake-cli` |
| `video-labeling-workflow` | Create and publish the fixed DreamLake video subtask-labeling workflow: collect the source, video and reference-annotation paths, verify the worker can read them, fill the bundled template, confirm with the user, and push a workflow they can Run from the canvas. | `dreamlake-workflows`, `dreamlake-datasets` |
| `dreamlake-experiments` | Log ML experiments with the DreamLake Python SDK and configure per-run Dash dashboards; use for RL logging, inspecting recorded data and missing charts, not implementing training algorithms or provisioning compute. | `dreamlake-cli` |
| `dreamlake-annotations` | Create, extend, revise and read DreamLake annotations with the Python SDK; change annotation display titles and URL slugs through the metadata API or CLI while preserving identity and links. | — |
| `launch-claude-remote` | Create a new named Claude Remote Control session with maximum permissions in a detached tmux terminal on this host, so the user can continue in their Claude app; keeps existing sessions running. | — |
| `launch-codex-chat` | Create a new named, resumable Codex chat with maximum permissions on this host's running app-server daemon, so the user can continue it in their Codex app; keeps existing sessions and daemons running. | — |

Earlier skills were merged into these; [`renamed.json`](renamed.json) maps
each retired name (`dreamlake-source`, `workflow-publish`, ...) to its
successor, and `dl skill install <old name>` prints the new one. Where
each section of the old skills went is recorded in
[`docs/migration-0010/`](docs/migration-0010/README.md).

## Install

With the [`dl` CLI](https://cli.dreamlake.ai):

```bash
dl init                                 # choose agent and scope; installs dreamlake-cli
dl skill list                           # the catalog, with installed versions
dl skill install dreamlake-artifacts    # brings dreamlake-cli along (requires)
dl skill update                         # refresh what is installed
```

By hand: every release carries `skills.tar.gz`, whose top-level entries are
the skill directories plus `catalog.json`, and a separate `catalog.json` that
also records the tarball's sha256 and size under `assets` so you can verify the
download. Unpack, read `catalog.json`, and copy the skill directory and every
directory in its `requires` closure (follow `requires` transitively) into your
agent's skills folder: `.claude/skills/` for Claude Code or `.agents/skills/`
for Codex, either in the project or in your home directory.

```bash
curl -fsSL -o skills.tar.gz \
  https://github.com/dreamlake-ai/dreamlake-skills/releases/latest/download/skills.tar.gz
mkdir -p dreamlake-skills && tar -xzf skills.tar.gz -C dreamlake-skills
python3 -c 'import json;print(json.load(open("dreamlake-skills/catalog.json"))["skills"]["dreamlake-artifacts"]["requires"])'
mkdir -p .claude/skills
cp -R dreamlake-skills/dreamlake-artifacts dreamlake-skills/dreamlake-cli .claude/skills/
```

Install the same set with either method; the CLI does nothing the archive does
not contain.

## Unattended agents

Skills drive DreamLake through the `dl` CLI alone. Where an agent runs
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

## Contributing

Edit a skill, run `python3 scripts/check.py`, open a PR; after the merge the
nightly workflow refreshes every `reference/`, tags `vYYYY.MM.DD` when `main`
has moved, and publishes the release that `dl skill update` installs.
Everything else, from fixing a step to creating or splitting a skill and the
acceptance a PR needs, is in [CONTRIBUTING.md](CONTRIBUTING.md).
