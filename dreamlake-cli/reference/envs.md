# Envs

An **env** is a MuJoCo environment: one MJCF entry file plus the assets it
references (meshes, textures, `<include>`d XMLs). `dreamlake env` pushes a
directory as a new version of an env under your namespace, and every version
opens as an interactive 3D viewer at `dreamlake.ai/<namespace>/envs/<name>`.

Unchanged files are **never re-uploaded**: file content is content-addressed,
so a new version only transfers what actually changed.

## Push a version

```bash file="terminal"
dreamlake env push ./cartpole                 # name defaults to the dir name
dreamlake env push ./scenes/cassie \
  --name cassie --entry scene.mjcf \
  --title "Agility Cassie" --visibility public
```

- `--type` records the simulator family (`mujoco` by default; `isaaclab`,
  `superdex`, … are accepted). Every type is stored, versioned and pullable —
  the interactive web viewer currently exists for `mujoco` only; other types
  show the version's file listing.
- `--entry` is auto-detected when the directory has exactly one root-level
  `*.xml`/`*.mjcf` containing `<mujoco>`; otherwise pass it explicitly.
- Paths are stored relative to the pushed directory, so relative
  `<mesh file="…"/>` and `<include file="…"/>` references keep working.
- Dot-files, `node_modules` and symlinks are skipped. Limits: ≤ 1000 files,
  ≤ 100 MiB per file, ≤ 1 GiB per version.
- `env create` is `push` that refuses a name that already exists.

Each push prints what was uploaded vs reused, and the web URL:

```txt file="output"
✓ pushed geyang/cassie v2 — 20 files (1 uploaded 12.4 KB, 19 reused)
  open:      https://dreamlake.ai/geyang/envs/cassie
```

## List, pull, delete

```bash file="terminal"
dreamlake env list                     # envs in your namespace
dreamlake env pull cassie              # latest → ./cassie/
dreamlake env pull cassie@1 -o /tmp/c1 # a specific version
dreamlake env delete cassie            # soft delete (restorable)
dreamlake env restore cassie
dreamlake env delete cassie --permanent  # purge storage — irreversible
```

`pull` downloads every file over presigned URLs and verifies each against its
content hash, so the reconstructed directory is byte-identical to what was
pushed. It needs no special tooling server-side — any HTTP client can follow
the same two REST calls (`GET …/envs/:name/versions` and
`GET …/envs/:name/versions/:version`).

## Visibility

Envs are **private** by default (only namespace members can see them). Make
one public at push time (`--visibility public`) or later from the env's web
page; a public env's viewer link opens without login.

> **Note:** Before v0.6, `dreamlake env` switched login environments. That moved to
> `dreamlake auth env list|use|remove` — see the Environments page.
