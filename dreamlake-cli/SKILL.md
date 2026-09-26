---
name: dreamlake-cli
description: "dreamlake — a CLI for the DreamLake data warehouse: upload and download assets, manage projects, bindrs, and datasets, and administer organizations and teams from your terminal. Use when answering questions about DreamLake (Introduction, Installation, Quick start, Environments, Uploading, Downloading, Verify SSH passwords, Projects & data, Artifacts, Envs, Workflows, Pipelines, Declaration collections, External sources, and 23 more)."
---
# DreamLake

dreamlake — a CLI for the DreamLake data warehouse: upload and download assets, manage projects, bindrs, and datasets, and administer organizations and teams from your terminal.

This skill bundles the DreamLake documentation. Read the reference
file that matches the question; each is a self-contained markdown page.

## Reference

**Getting started**

- `reference/overview.md` — Introduction: dreamlake — a CLI for the DreamLake data warehouse. Upload and download assets, manage projects/bindrs/datasets, and administer organizations and teams from your terminal.
- `reference/installation.md` — Installation: Install the dreamlake CLI with one command — a native binary that needs no Node or Python and keeps itself up to date.
- `reference/quick-start.md` — Quick start: Log in, create a project, upload a file, list it, and download it back — the full round-trip in a handful of commands.
- `reference/environments.md` — Environments: Switch the CLI between staging, prod, and custom deployments. Built-in environments need no URLs; each keeps its own token.

**Data**

- `reference/uploading.md` — Uploading: Upload single files or whole folders with resumable multipart uploads, automatic type detection, and bindr membership.
- `reference/downloading.md` — Downloading: Download a single asset, or a whole folder / episode recursively, preserving the directory tree.

**Vault**

- `reference/vault-passwords.md` — Verify SSH passwords: Fresh password-only authentication for one saved host binding.

**Resources**

- `reference/projects.md` — Projects & data: Organize data with projects, bindrs, and datasets. Create, list, update, and delete — including hard-deleting episodes and files.
- `reference/artifacts.md` — Artifacts: Push renderable HTML, React, Markdown, SVG, code, and Mermaid content as versioned artifacts, and control who can read them.
- `reference/envs.md` — Envs: Push simulation environments (a MuJoCo MJCF scene or a URDF robot plus assets) as versioned envs, pull them back byte-identical, compose layered env stacks, and view them interactively on the web.
- `reference/workflows.md` — Workflows: Push and manage WorkflowSpec v1 definitions, and send run traces from an executing agent.
- `reference/pipelines.md` — Pipelines: Manage Python pipelines and their versions, inspect node graphs, and write back node execution state.
- `reference/collections.md` — Declaration collections: Declare runnables, run configs, providers, sources, and repos; register immutable versions keyed by sha256 of the source; and import a pinned version back onto disk.
- `reference/sources.md` — External sources: Browse and read data out of connected external sources — S3, Dropbox, HuggingFace — without copying it into DreamLake first.
- `reference/agents.md` — Agents: Declare an agent — a named prompt, optionally with tools, permissions, typed arguments and a machine to run on — from a Claude agent file, a heredoc, or $EDITOR.
- `reference/notes.md` — Notes: Read, search, and edit collaborative notes from the terminal — by section, with a diff, and without overwriting whoever is typing at the other end.
- `reference/tasks.md` — Tasks: Track project task folders, progress, actual timing and linked Notes.
- `reference/layout.md` — Layout control: Inspect, resolve and apply declarative layout requests in an explicitly selected browser page.

**Org & teams**

- `reference/organizations.md` — Organizations: Create and administer organizations, manage members and roles. Members are resolved by email or name.
- `reference/teams.md` — Teams: Manage teams within an organization, including nested teams and visibility. Team roles are maintainer or member.

**Lakeshore**

- `reference/queues.md` — Mount a queue server: Connect an existing Lakeshore server to DreamLake and inspect its queues, jobs, and workers.
- `reference/lakeshore.md` — Lakeshore resources: Providers, storages, and queue definitions — three collections, one set of five verbs. How a machine gets launched, where it reads bulk data, and what a queue's policy is.
- `reference/provider-lifecycle.md` — Provider lifecycle: Drive `provider create → plan → apply → connect` from an agent. The CLI embeds no model — it reports where it is and what to do next, and something else does it.
- `reference/snapshot-launch.md` — Snapshot & launch: Archive this working tree into an immutable snapshot, then run one of its scripts on the fabric. A launch names a queue, never a machine.

**Hosts**

- `reference/host-enrollment.md` — Host enrollment: Enroll Linux hosts through SSH and inspect their connection status.
- `reference/runs.md` — Tracked host runs: Submit explicit source files and uv arguments to an enrolled host.
- `reference/providers.md` — Provider registrations: Register providers, associate Slurm enrollments, and recover operation receipts.

**Guides**

- `reference/vault-kms.md` — Prefix KMS policies: Inspect operator-approved prefix encryption and activate an empty prefix.

**Reference**

- `reference/command-reference.md` — Command reference: Every dreamlake command at a glance. Run `dreamlake <command> --help` for full options.
- `reference/skills.md` — Agent skills: Install these docs as an agent skill with `dreamlake skill install`. It never overwrites a skill you edited, never deletes a peer, and never touches settings.json.
- `reference/ssh-sync.md` — Selected SSH import: Review and upload explicitly selected SSH profiles and private keys to the vault.
- `reference/vault-write-recovery.md` — Vault write recovery: Recover uncertain vault entry writes using authenticated operation receipts.
- `reference/vault-operations.md` — Vault operations: HOTP ownership and recovery, paginated metadata, and releasing host references.
- `reference/release-notes.md` — Release notes: CLI releases and validation status.

**Dev Notes**

- `reference/dev-notes-npm-publication.md` — npm publication gate: Verify platform tarballs before publishing their dependent CLI wrapper.
- `reference/dev-notes-queue-mount-release.md` — Queue mount release: Queue mount CLI releases, public artifact verification and hosted acceptance.
- `reference/dev-notes-task-session-scope.md` — Task session scope defaults: Session environment defaults for task namespace and project.

## Canonical source

These docs live at https://cli.dreamlake.ai. Each page is also fetchable as markdown
at `<page-url>.md`, and the full corpus at https://cli.dreamlake.ai/llms-full.txt.
