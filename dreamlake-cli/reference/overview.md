# DreamLake CLI

**`dreamlake`** is the command-line tool for the DreamLake data warehouse.
Upload and download assets, organize them into projects, bindrs, and
datasets, and administer organizations and teams — all from your terminal.

> **Note:** The CLI talks to a DreamLake server (REST + GraphQL) and BSS
> (big-streaming-server). It ships with two built-in environments —
> **staging** and **prod** — so you can switch targets with one command.

## Get started

| I want to… | Start here |
| --- | --- |
| Install the CLI | [Installation](installation.md) |
| Log in and move a file end-to-end | [Quick start](quick-start.md) |
| Switch between staging and prod | [Environments](environments.md) |
| Upload files or folders | [Uploading](uploading.md) |
| Organize data (projects, bindrs, datasets) | [Projects & data](projects.md) |
| Manage an organization | [Organizations](organizations.md) |
| See every command | [Command reference](command-reference.md) |

## What it does

```
your terminal                DreamLake server              BSS (storage)
─────────────                ────────────────              ─────────────

 dreamlake upload  ──┬──▶  POST /nodes (register)
                     └────────────────────────────▶  multipart /files → S3
 dreamlake list    ─────▶  GET /nodes/:id/contents
 dreamlake org ... ─────▶  POST /graphql
```

| Surface | What it covers |
| --- | --- |
| **Data** | `upload`, `download`, `list` — assets in projects/episodes |
| **Resources** | `create` / `update` / `delete` for projects, bindrs, datasets, episodes, files |
| **Org & teams** | `org` and `team` — members, roles, nested teams |
| **Auth & envs** | `login`, `logout`, `profile`, `env` — multi-environment |

## Quick example

```bash file="terminal"
dreamlake login
dreamlake create project my-robots --public
dreamlake upload ./clip.mp4 --episode my-robots:run-001 --to /camera/front
dreamlake list --episode my-robots:run-001
dreamlake download --episode my-robots:run-001 --from /camera/front/clip.mp4 -o ./out.mp4
```
