---
name: dreamlake-cli
description: Install and log in to the DreamLake CLI, pick an environment, upload and download data, browse or upload Sources, grant Project access, move whole Projects, transfer ownership, link writes to agent sessions, manage Vault, register UDFs, push workflows. Routes compute (hosts, machines, Lakeshore, Stacks, AWS) to dreamlake-lakeshore and artifact, note, task, scene, dataset, workflow-authoring and annotation work to their own skills.
---

# DreamLake CLI

This is the base skill: the CLI itself and the operations no domain skill owns.
Compute (hosts, machines, Lakeshore, Stacks, AWS) is `dreamlake-lakeshore`.
Pick one action; each is one task, command first and exceptions after. Domain
work has its own skill (second table) and this skill does not repeat its steps.

## Actions

| Request | Action |
| --- | --- |
| Install, log in, choose the environment; machine identity, telemetry, Nymph | [setup](actions/setup.md) |
| Upload or download episode data; browse or upload files in a Source | [data](actions/data.md) |
| Grant or revoke Project access; attach or detach a resource | [project-access](actions/project-access.md) |
| Move a whole Project and its owned resources to another namespace | [projects](actions/projects.md) |
| Transfer one Artifact, Env/Scene, Annotation, Pipeline or Source | [ownership](actions/ownership.md) |
| Link a Note or Artifact write to the agent's session; upload a conversation | [session-links](actions/session-links.md) |
| Import or restore cloud configuration; Terraform state snapshots in Vault | [cloud-vault](actions/cloud-vault.md) |
| Register UDF or agent definitions from `.dreamrc` | [runnable-register](actions/runnable-register.md) |
| Execute one registered Python UDF on an owned host | [registered-udf](actions/registered-udf.md) |
| Push or list a workflow spec | [workflows](actions/workflows.md) |

## Domain skills (install by name)

| Task | Skill |
| --- | --- |
| Lakeshore, hosts, terminal sessions, Slurm and external jobs, machines, Infrastructure Stacks, AWS | `dreamlake-lakeshore` |
| Publish, version, share, restore artifacts | `dreamlake-artifacts` |
| Read, edit, version, attach, inline images, references, transfer a Note | `dreamlake-notes` |
| Task folders, subtasks, progress, events, linked Notes | `dreamlake-tasks` |
| Scenes, MJCF/URDF packaging, asset libraries | `dreamlake-scenes` |
| Robot datasets, Source connection and path checks, `.dreamrc` | `dreamlake-datasets` |
| Author, validate and publish WorkflowSpecs | `dreamlake-workflows` |
| Annotations through the Python SDK | `dreamlake-annotations` |

## Launch-server requirement

Any workload or machine launch must go through an explicitly user-configured
launch server, never service IAM or direct provider execution from the hosted
backend; the rule and its evidence standard are the `machines` action of
`dreamlake-lakeshore`.

## Conventions

- Run `dreamlake <command> --help` for syntax; actions do not restate flags.
- Plain text is for people and agents; add `--json` only when a program parses the output.
- Check the installed `dreamlake --version` against each action's version floor. A
  merged change, updated docs or an installed skill does not prove that the
  executable or the server supports a command.
- Use the Python or TypeScript SDK only for explicit SDK integration or a documented
  CLI capability gap.

## Canonical source

Product facts live on the documentation sites, not in this skill: cli.dreamlake.ai
(commands), docs.dreamlake.ai (product) and viz.dreamlake.ai (visualization). Every
page is fetchable as Markdown at `<page-url>.md`, and each site's full corpus is at
`<site>/llms-full.txt`. `reference/` holds the pages listed in `skill.json` `docs[]`,
fetched by CI as `reference/cli-<slug>.md`; do not edit them.
