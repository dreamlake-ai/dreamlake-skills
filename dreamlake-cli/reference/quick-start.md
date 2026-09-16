# Quick start

From login to a verified round-trip in a few commands.

## Step 1 — Log in

The CLI ships with built-in environments and logs into **prod** by default:

```bash file="terminal"
dreamlake login
```

A browser opens for device authorization. Approve it, and your token is
saved. Confirm:

```bash file="terminal"
dreamlake profile
```

It prints your user and **namespace** — note the namespace, you'll use it
in targets below.

## Step 2 — Create a project

```bash file="terminal"
dreamlake create project my-robots --description "robot captures"
```

Projects are **private by default**. Pass `--public` to share. The output
shows the project **slug** — use it in targets.

## Step 3 — Upload a file

```bash file="terminal"
dreamlake upload ./clip.mp4 --episode my-robots:run-001 --to /camera/front
```

- `my-robots:run-001` is a **target**: `project[:episode]`.
- The episode `run-001` is created automatically if it doesn't exist.
- `--to` is the path inside the episode.

## Step 4 — List and download

```bash file="terminal"
dreamlake list --episode my-robots:run-001
dreamlake download --episode my-robots:run-001 --from /camera/front/clip.mp4 -o ./out.mp4
```

> **Note:** Create → upload → list → download. From here, explore
> [uploading](uploading.md) (folders, resume), [projects & data](projects.md)
> (bindrs, datasets), or [organizations](organizations.md).

## Targets at a glance

Most data commands take a target string:

| Form | Used by | Example |
| --- | --- | --- |
| `project[@namespace]` | `--project` | `my-robots@alice` |
| `project[@namespace][:episode]` | `--episode` | `my-robots@alice:run-001` |

`@namespace` is optional — it defaults to your own (from `dreamlake profile`).
