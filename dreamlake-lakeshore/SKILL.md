---
name: dreamlake-lakeshore
description: Operate DreamLake compute through the CLI — connect Lakeshore (Add Host, Runtime workers, queue mounts), enroll and inspect hosts and terminal sessions, read Slurm and externally launched jobs, provision machines through a user-configured launch server, discover and collaborate on Infrastructure Stacks (manual or automated Terraform setup), connect AWS. Use for any host, machine, queue, Stack or AWS-connection task. Not for uploads, Notes, artifacts, scenes or datasets.
---

# DreamLake Lakeshore and compute

The compute loop of the `dreamlake` CLI: connecting machines to DreamLake,
inspecting what is enrolled and running, provisioning more, and the
infrastructure and cloud connections behind it. The CLI itself, login and
environment selection are the `setup` action of `dreamlake-cli` (installed
with this skill); read it first.

## Launch-server requirement (safety rule, read before any launch)

Before any workload or machine launch, verify the explicitly user-configured
launch server and its appropriate IAM role. Never use or broaden control-plane
or service IAM, substitute ambient service credentials or an operator Vault IAM
user, or execute provider launches directly from the hosted backend. If that
route is missing or unverified, stop new launch and provisioning actions and
report the gap; read-only inspection may continue. The full rule and its
evidence standard are in [machines](actions/machines.md).

## Actions

| Request | Action |
| --- | --- |
| Connect Lakeshore: Add Host, Runtime workers, queue mounts, shared connection upkeep | [lakeshore](actions/lakeshore.md) |
| Hosts, enrollments, metrics, SSH/exec, power, catalog visibility, agent terminal sessions | [hosts](actions/hosts.md) |
| Read Slurm scheduler jobs; register and report externally launched work | [jobs](actions/jobs.md) |
| Machine identities, service accounts, launch-server binding, provisioning and EC2 launches | [machines](actions/machines.md) |
| Infrastructure Stacks: discover and collaborate (manual and automated Terraform setup), register an empty backend, move, Kubernetes capacity | [infrastructure](actions/infrastructure.md) |
| "Connect AWS to DreamLake" with the curated starter | [connect-aws](actions/connect-aws.md) |

Each action is one task: commands first, exceptions after. Flag detail is in
`reference/` or `dreamlake <command> --help`.

## Boundaries

- Uploads, Sources, Vault, Project moves, ownership transfer and session links
  are actions of `dreamlake-cli`; this skill names them and does not repeat them.
- Running a registered UDF on a host is the `registered-udf` action of
  `dreamlake-cli`; authoring workflows is `dreamlake-workflows`.
- Infrastructure Stacks move with a whole Project through the `projects`
  action of `dreamlake-cli`; `infra move` / `infra transfer` here cover a
  single Stack.

## Conventions

- Check the installed `dreamlake --version` and `--help` against each action's
  version floor. A merged change, updated docs or an installed skill does not
  prove the executable or the server supports a command.
- Host IDs, enrollment IDs, cloud instance IDs and Nymph supervisor IDs are
  different identifiers; keep request IDs and revisions for retries, and never
  mint a new request ID to get past a conflict.
- An online enrollment, a saved session descriptor or a fresh tracking report
  is not proof that a process is running; preserve unknown as unknown.

## Canonical source

Product facts live on the documentation sites, not in this skill: cli.dreamlake.ai
(commands, starting at [Lakeshore](reference/cli-lakeshore.md)) and
docs.dreamlake.ai (product). Every page is fetchable as Markdown at
`<page-url>.md`, and each site's full corpus at `<site>/llms-full.txt`.
`reference/` holds the pages listed in `skill.json` `docs[]`, fetched by CI as
`reference/cli-<slug>.md`; do not edit them.
