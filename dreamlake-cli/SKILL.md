---
name: dreamlake-cli
description: "Use the DreamLake CLI to upload and download data, manage workspace resources, Notes, artifacts, workflows, hosts, Slurm inventory, external job tracking, and Infrastructure Stack metadata/backend setup. Use for 'connect AWS to DreamLake', curated AWS worker setup, command setup and troubleshooting; use an SDK only when the task requires SDK integration or the CLI lacks the needed operation."
---

# DreamLake CLI

Start with the task guide, then consult the bundled reference page for complete
options and limits:

- [Install, authenticate, and choose an environment](actions/setup.md)
- [Connect AWS to DreamLake with the curated starter](actions/connect-aws.md)
- [Upload or download data](actions/data.md)
- [Work with Notes](actions/notes.md)
- [Upload an inline image](actions/media.md)
- [Publish an artifact](actions/artifacts.md)
- [Manage workflows](actions/workflows.md)
- [Execute one registered Python UDF (CLI 0.68.0+)](actions/registered-udf.md)
- [Import and restore cloud configuration](actions/cloud-vault.md)
- [Provision machines and manage their identities](actions/machines.md)
- [Inspect hosts and Slurm jobs, or track external work](actions/hosts-jobs.md)
- [Inspect Infrastructure Stacks and backend setup](actions/infrastructure.md)

For any workload or machine launch, first read the
[launch-server requirement](actions/machines.md). Execution must use an explicitly
user-configured launch server and its appropriate IAM role, never service IAM,
ambient service credentials, an operator Vault IAM user or direct hosted-backend
provider execution. Missing routing blocks new launches, not read-only inspection.

Run `dreamlake <command> --help` for command-specific syntax. The bundled
`reference/` directory remains the complete generated CLI documentation.
Prefer plain text for people and agents; use `--json` when a program needs
structured output. Python and TypeScript APIs are appropriate for explicit SDK
integration or a documented CLI capability gap.

The source map and action guides are maintained with CLI docs. Public sync
records the source commit, generator and guide hashes.
