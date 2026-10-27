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
| `dreamlake-cli` | Install and log in, pick an environment, upload and download, browse and upload Sources, Tasks, whole-Project transfer, Vault, hosts and Slurm, infrastructure, Lakeshore, AWS access; routes every other task to the right skill | — |
| `dreamlake-notes` | Read, edit, collaborate on, attach to, reference, version and restore Notes | `dreamlake-cli` |
| `dreamlake-artifacts` | Write content that renders in the offline artifact frame; publish, version, share, revoke, delete and restore artifacts | `dreamlake-cli` |
| `dreamlake-scenes` | Package and push MJCF/URDF scenes, publish and search asset libraries, generate and layer scenes, validate physics per body, preview and read back | `dreamlake-cli` |
| `dreamlake-datasets` | Lay out robot data, connect a Source, verify paths, write `.dreamrc`, convert simulation rollouts to MCAP | `dreamlake-cli` |
| `dreamlake-workflows` | Write a WorkflowSpec from a description or a fixed template, validate it locally, publish and review | `dreamlake-cli` |
| `dreamlake-annotations` | Upload and revise annotated training episodes with the Python SDK | — |
| `launch-claude-remote` | Start another Claude remote session | — |
| `launch-codex-chat` | Start another Codex session | — |

Earlier skills were merged into these; [`renamed.json`](renamed.json) maps
each retired name (`dreamlake-source`, `workflow-publish`, ...) to its
successor, and `dreamlake skill install <old name>` prints the new one.

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
`requires`. Download the latest, extract it, and copy the skill directory plus
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
<name>/            one skill: skill.json, SKILL.md, actions/, optional tools/ and assets/, generated reference/
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
