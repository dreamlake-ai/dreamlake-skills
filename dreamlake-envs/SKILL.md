---
name: dreamlake-envs
description: Push a MuJoCo scene (MJCF) or URDF robot to DreamLake as an env — extract a self-contained directory from a repo, verify it compiles, push it versioned with `dreamlake env push`, and get an interactive 3D viewer page. Use when a user wants to upload, publish, share, or version a simulation environment, scene, or robot model on DreamLake, or pull one back byte-identical.
---

# DreamLake Envs — push a sim scene, get a live 3D page

An **env** is a simulation environment: a directory holding one MJCF scene
or one URDF robot plus its assets, pushed from the terminal and opened as an
interactive 3D page in the dashboard. A `mujoco` env runs the real engine in
the browser (play / pause / reset, actuator and joint sliders, Alt+drag
perturbation); a `urdf` env opens as a poseable kinematic robot. Versions
are immutable integers, files are content-addressed (re-pushes upload only
what changed), and `pull` returns the directory byte-identical.

Envs hold the *scene*, not recordings — teleop episodes and rollout logs
belong in a **source** (`dreamlake-source` skill). Guide:
https://docs.dreamlake.ai/envs/ · CLI: https://docs.dreamlake.ai/cli#envs

## Browse and manage

`/<namespace>/profile?tab=envs` is the public showcase; it excludes private
resources even when the owner is signed in. `/<namespace>/envs` requires sign-in
and retains the existing namespace permissions. A personal Envs catalog adds
recent environments from member organizations as separate groups.

Public environments and valid Env share-token links can open anonymously.
Anonymous detail readers have no application sidebar. Signed-in readers keep
their selected personal or organization workspace sidebar; the resource owner
continues to come from the URL.

Your own profile and organization profiles you belong to show **Enter workspace**,
a single text link to `/<namespace>/projects`. Choose other resources from the
application sidebar. Switching accounts from Settings or an unavailable management
page also falls back to Projects; resource pages keep the matching list. Profile
switching preserves its tab. Overview previews at most six public projects without
querying every resource catalog. Member avatars and profile-edit dialogs remain.
Cmd+Shift+D preserves the global developer-discovery preference without granting
access to private resources. No extra owner breadcrumb is added above app pages.

Source: [Envs guide](https://docs.dreamlake.ai/envs) and
[Profiles and workspaces](https://docs.dreamlake.ai/workspaces). The companion
workspace revision is recorded in `sources.json`. This section is paired with
the owning docs explicitly; the Env skill is not managed by the Notes/CLI generator.

## 1. Extract a self-contained directory

One env = one scene. The pushed directory must contain the entry file at
its **root** and every file the scene references **inside** the directory —
scenes living in a larger repo usually reach outside themselves
(`../../assets/...`), so extract first:

```bash
# every path the scene pulls in — meshes, textures, includes, hfields all use file="…"
grep -oE 'file="[^"]+"' scene.xml | sort -u
# plus the compiler dirs, which are also relative paths
grep -E 'meshdir|texturedir|assetdir' scene.xml
```

Then stage: copy the entry to the root of a fresh directory, copy each
referenced out-of-tree folder in, and rewrite the escaping prefixes — one
`sed` over the entry usually covers both `file=` and `meshdir=` values:

```bash
mkdir -p /tmp/envs/my-scene/assets
sed 's|\.\./\.\./assets/|assets/|g' repo/experiments/my-scene/scene.xml \
  > /tmp/envs/my-scene/scene.xml
cp -R repo/assets/kinova_gen3 /tmp/envs/my-scene/assets/
find /tmp/envs -name '.DS_Store' -delete
```

Three rules that keep the extraction correct:

- **Copy referenced robot folders wholesale**, not file-by-file. Nested
  `<include>`s resolve relative to the file that contains them, so a robot
  XML that includes sibling files (`actuators.xml`, `keyframe.xml`) and a
  local `assets/` dir keeps working if its folder moves as a unit. Bring
  the robot's LICENSE along — you are redistributing its meshes.
- **Rewrite every escaping path** — `<include file>`, `<mesh file>`,
  `<texture file>`, and the `meshdir`/`texturedir` compiler attributes all
  carry relative paths.
- **Verify from the staged copy, outside the repo** — any reference you
  missed still resolves if you test in place, and fails loudly from `/tmp`:

```bash
cd /tmp/envs/my-scene && python -c \
  "import mujoco; m = mujoco.MjModel.from_xml_path('scene.xml'); \
   print(m.nbody, 'bodies,', m.nmesh, 'meshes,', m.nu, 'actuators')"
```

For a URDF, check the mesh paths instead: every `filename="…"` (relative or
`package://…`) must resolve against the pushed directory.

## 2. Push

```bash
dreamlake env push /tmp/envs/my-scene                 # entry auto-detected; prints an open link
dreamlake env push <dir> --namespace <org>            # into an org instead of your personal namespace
dreamlake env push <dir> --title "…" --description "…"
dreamlake env create <dir>                            # push that FAILS if the name already exists
```

| Flag | What it does |
|---|---|
| `--name` | env name (default: slug of the directory name) |
| `--entry scene.mjcf` | pick the entry when several root-level candidates qualify |
| `--type isaaclab` | simulator family — stored and pullable; `mujoco` and `urdf` have viewers |
| `--namespace <slug>` | target namespace/org (default: active login) |
| `--visibility public` | anyone can open the viewer, no login (default: private) |
| `--share` | mint a `?share=` link readable by anyone who has it |

Entry auto-detection: the single root-level `*.xml`/`*.mjcf` containing
`<mujoco>`, or — with no MJCF around — the single root-level `*.urdf`
containing `<robot>`, which also sets `type: urdf`. Two candidates at the
root → the push asks for `--entry`.

A transient upload error (`backend transient error`, closed socket) is safe
to retry: **re-run the exact same push**. Files are content-addressed, so
completed uploads are reused and only the remainder transfers.

## 3. Version, pull, verify

Pushing the same name again creates v2 — the CLI reports exactly what moved
(`1 uploaded 12.4 KB, 19 reused`). Shared meshes dedupe **across envs** in
the namespace too, so pushing five scenes that use the same robot uploads
its meshes once.

```bash
dreamlake env list --namespace <org>        # name · version · type · files · entry
dreamlake env pull my-scene                 # latest → ./my-scene/, hash-verified
dreamlake env pull my-scene@1 -o v1         # any version; --force writes into a non-empty dir
```

The round-trip check after a first push — pull to a fresh dir, diff, and
recompile:

```bash
dreamlake env pull my-scene --namespace <org> -o /tmp/check
diff -rq /tmp/envs/my-scene /tmp/check      # byte-identical
```

## 4. Delete (safely)

```bash
dreamlake env delete my-scene               # soft delete (restorable; -y skips the confirm)
dreamlake env restore my-scene              # bring it back
dreamlake env delete my-scene --permanent   # purge storage + catalog — IRREVERSIBLE
```

Never pass `--permanent` unless the user explicitly asked to erase storage.

## Traps

- **Videos, logs, notebooks don't belong in the directory** — the push
  uploads everything under it. Stage a clean copy rather than pushing a
  repo subfolder that also holds outputs, `__pycache__/`, or previews.
- **`dreamlake env` used to mean login environments.** That command is now
  `dreamlake auth env …`; if `env push` is missing, the CLI predates envs —
  update it.
- **Unattended runs**: set `DREAMLAKE_API_KEY` (whose identity the push is
  attributed to) and `DREAMLAKE_REMOTE` (which deployment), or the CLI uses
  whatever login is active on that machine.
