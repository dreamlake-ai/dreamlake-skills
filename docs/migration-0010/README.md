# RFC 0010 migration tables

Per-skill tables recording where every section of the pre-RFC-0010 skills
went. They were attached to the migration PR and ticked line by line; nothing
here is read by the tooling. The authoritative layout and rules are in
[CONTRIBUTING.md](../../CONTRIBUTING.md).

## The 14 skills

| Skill | Table | Requires |
|---|---|---|
| `dreamlake-cli` | [dreamlake-cli.md](dreamlake-cli.md) | — |
| `dreamlake-lakeshore` | [dreamlake-lakeshore.md](dreamlake-lakeshore.md) | `dreamlake-cli` |
| `dreamlake-notes` | [dreamlake-notes.md](dreamlake-notes.md) | `dreamlake-cli` |
| `dreamlake-tasks` | [dreamlake-tasks.md](dreamlake-tasks.md) | `dreamlake-cli` |
| `dreamlake-artifacts` | [dreamlake-artifacts.md](dreamlake-artifacts.md) | `dreamlake-cli` |
| `dreamlake-scenes` | [dreamlake-scenes.md](dreamlake-scenes.md) | `dreamlake-cli` |
| `dreamlake-libraries` | [dreamlake-libraries.md](dreamlake-libraries.md) | `dreamlake-cli` |
| `dreamlake-datasets` | [dreamlake-datasets.md](dreamlake-datasets.md) | `dreamlake-cli` |
| `sim-to-mcap` | [sim-to-mcap.md](sim-to-mcap.md) | `dreamlake-datasets` |
| `dreamlake-workflows` | [dreamlake-workflows.md](dreamlake-workflows.md) | `dreamlake-cli` |
| `video-labeling-workflow` | [video-labeling-workflow.md](video-labeling-workflow.md) | `dreamlake-workflows`, `dreamlake-datasets` |
| `dreamlake-annotations` | [dreamlake-annotations.md](dreamlake-annotations.md) | — |
| `launch-claude-remote` | [launch-claude-remote.md](launch-claude-remote.md) | — |
| `launch-codex-chat` | [launch-codex-chat.md](launch-codex-chat.md) | — |

## Kept as their own skills

RFC 0010 §4 planned nine skills. Four sources stayed separate under the
owner's rule "do not lose information, do not merge what should not be merged,
avoid oversized skills" (soft caps: about 50 KB of hand-written text and about
12 actions per skill; a distinct user goal someone installs alone stays
separate). The reasons, from the tables:

| Skill | RFC §4 planned | Why it stayed separate |
|---|---|---|
| `dreamlake-tasks` | fold into `dreamlake-cli` | `dreamlake-cli` is ~57 KB hand-written and 15 actions already; absorbing the Tasks sources (21 KB, seven one-task actions plus a 60-line contract) would push it to ~90 KB and 22 actions. Task tracking is also a goal someone installs on its own. `dreamlake-cli/SKILL.md` routes task work here by name. |
| `dreamlake-libraries` | fold into `dreamlake-scenes` | Publishing, curating and searching an asset library is a distinct user goal someone installs alone (a team shipping a splat/mesh library never builds a scene), and its 15 KB of hand-written text would push the merged scenes skill past the ~50 KB bound and past 12 actions. `dreamlake-scenes` routes to it by name for asset search. |
| `sim-to-mcap` | fold into `dreamlake-datasets` | Rolling a trained policy out in a local simulator and writing MCAP is a distinct user goal that an RL/sim user installs on its own. It requires `dreamlake-datasets` and hands off by name to that skill's `upload`, `connect`, `dreamrc` and `validate` actions. |
| `video-labeling-workflow` | fold into `dreamlake-workflows` | The procedure is four distinct user-facing steps (~14 KB of prose) with confirmation gates, plus an 11 KB measured template; it is a product demo a user installs on its own. It requires `dreamlake-workflows` (publish) and `dreamlake-datasets` (the `check` action). |

## Split during integration

| Skill | Split from | Why |
|---|---|---|
| `dreamlake-lakeshore` | `dreamlake-cli` | After the merge `dreamlake-cli` was 74.6 KB hand-written in 15 actions, past both soft caps; the compute loop (Lakeshore connection, hosts and terminal sessions, Slurm and external jobs, machines, Infrastructure Stacks, AWS) is a distinct goal, so its five actions moved out (with `hosts-jobs` split into `hosts` and `jobs`), leaving `dreamlake-cli` at 10 actions / ~35 KB. |

## Retired names

[`renamed.json`](../../renamed.json) carries these nine mappings; the CLI
prints the new name when an old one is installed.

| Old skill | Now |
|---|---|
| `dreamlake-artifact-authoring` | `dreamlake-artifacts` |
| `dreamlake-scene-generation` | `dreamlake-scenes` |
| `dreamlake-envs` | `dreamlake-scenes` |
| `dreamlake-source` | `dreamlake-datasets` |
| `dreamlake-dataset-viz` | `dreamlake-datasets` |
| `remote-source-check` | `dreamlake-datasets` |
| `workflow-generator` | `dreamlake-workflows` |
| `workflow-publish` | `dreamlake-workflows` |
| `dreamlake-note-references` | `dreamlake-notes` |

`dreamlake-tasks`, `dreamlake-libraries`, `sim-to-mcap`,
`video-labeling-workflow`, `dreamlake-annotations`, `launch-claude-remote` and
`launch-codex-chat` keep their names, `dreamlake-lakeshore` is new, and none
of them is in `renamed.json`.
