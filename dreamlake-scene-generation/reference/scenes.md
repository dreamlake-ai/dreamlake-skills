{/* FigEnv* come from the site-wide mdxComponents map in site.config.ts —
    no import needed. */}

# Scenes

  A scene is a **simulation environment** — a directory holding one MJCF scene
  or one URDF robot, plus its assets — that you push from the terminal and
  open as a live, interactive 3D page in the dashboard.

## Browsing in the app

`/<namespace>/profile?tab=scenes` and `/<namespace>/scenes` reuse the same
Scenes catalog. Your own namespace and organizations you belong to show
resources and actions allowed by your permissions. Signed-out visitors and
signed-in visitors to other namespaces see public resources only, without
creation or modification controls. Profile uses an avatar rail; the application
uses resource navigation for the namespace in the URL.

Your own Scenes catalog also includes recent scenes from your organizations. Public scenes and valid Scene share-token links open without sign-in.

The application sidebar shows the resource owner's avatar and links, including
for anonymous public readers. Your signed-in identity and personal/organization
switcher are separate from that owner. See [Profiles and workspaces](https://docs.dreamlake.ai/workspaces).

The detail header returns anonymous readers to `/<namespace>/profile?tab=scenes`
and signed-in readers to `/<namespace>/scenes`. Details opened inside a project
retain their return-to-project action. There is no extra sign-in navigation bar.

## Generate with chat

Members can also create and edit scenes from the browser, by prompting an
embedded agent that runs the
[scene-generation skill](https://docs.dreamlake.ai/scene-generation/quickstart). The chat panel
ships with the web app — it appears once an app deployment that includes
scene chat reaches your server:

1. In your namespace's Scenes catalog, click **+ new scene** — in the page
   header next to the Scenes/Libraries switch, and offered again by
   the empty catalog's placeholder. One click opens a fresh *draft* with an
   auto-minted name (`env_xxxxxx`) — no dialog, nothing to type first, and
   nothing exists on the server until the agent's first successful push.
2. The draft opens straight into the **intro composer** — describe the
   scene there; the agent sources assets, measures, composes, validates,
   and publishes with `dreamlake scene push`.
3. On the first successful push the draft becomes the **saved preview** —
   the interactive viewer on the pushed version, chat still beside it.
4. **Follow-up prompts create new versions** of the same scene. The viewer
   tracks the latest; picking an older version in the header pins it, and
   a "vN available" button jumps back to latest.
5. Editing an **existing** scene works the same: open its page as a member
   and prompt the chat panel next to the viewer. Read-only viewers, share
   links, and anonymous visitors never see the chat.
6. To grow a **new** scene out of an existing one, start from the catalog,
   not from the source scene's page — the chat edits the scene whose page it
   sits on. Click **+ new scene** for a fresh draft, then ask it to start
   from the source scene at a pinned version; the source scene keeps its own
   versions, untouched (details in the
   [Quickstart](https://docs.dreamlake.ai/scene-generation/quickstart)).

The scene chat opens in **Auto** permission mode, so one prompt can carry
through the whole workflow — the agent runs the scene tools and
`dreamlake scene push` without per-command approval. The composer's
permission control still works as usual: switch to **Ask permissions** or
**Plan mode** for a read-only conversation (the agent inspects and answers
but does not generate or push), and switch back to Auto when you want it
to build. A read-only choice is respected for as long as you keep it — the
page sets the mode only once, on open, and never overrides your selection.
Scene membership still governs what a push may touch: the mode routes what
the agent may *run*, not what your account may *write*.

The install-and-use guide for the same workflow from a local agent —
ordinary create / edit / reuse prompts included — is the
[Scene Generation Quickstart](https://docs.dreamlake.ai/scene-generation/quickstart).

**Troubleshooting the preview when running the app from source.** If the
viewer panel shows an error fallback instead of the scene and the console
logs `R3F: Hooks can only be used within the Canvas component!`, that is a
dev-server fault, fixed in the app source on 2026-09-29: the dev server
could load two copies of the 3D renderer and which copy a session got
depended on load order — so the crash appears and disappears between
checkouts, and its absence on one run proves nothing. If you see it, your
source checkout predates the fix: update to a checkout that carries it and
restart the dev server. In that source's dependency graph the production build
resolves a single renderer copy, which bounds the fault to the dev server
— an inference about the current source only, not an audit of anything
previously deployed. Count the scene as loaded only when its actual
geometry is visible and the simulation controls respond; that console
error is failure evidence, and a page shell or a bare `<canvas>` is not
success — the canvas can mount and then unmount again while the model
loads.

## Push one

```bash
dreamlake scene push ./cassie
```

The entry file is auto-detected — the one root-level `*.xml`/`*.mjcf`
containing `<mujoco>`, or (with no MJCF around) the one root-level `*.urdf`
containing `<robot>`, which also sets the scene's type to `urdf`. Relative
`<include>`, `<mesh file="…">` and `package://` references keep working
exactly as they do on disk. The CLI prints an **open link**.

| Flag | What it does |
|------|--------------|
| `--entry scene.mjcf` | Pick the entry when there are several candidates |
| `--type isaaclab` | Simulator family — stored and pullable; `mujoco` and `urdf` have viewers |
| `--visibility public` | Anyone can open the viewer, no login |
| `--name`, `--title` | Identity (defaults to the directory name) |
| `--thumbnail cover.png` | Set the gallery cover yourself (PNG ≤ 512 KiB) — see [Thumbnails](#thumbnails) |

## Version it — only changes upload

Push the same scene again and you get **v2**. Files are content-addressed, so
unchanged meshes and textures are never uploaded or stored twice — the CLI
tells you exactly what moved:

```txt
✓ pushed you/cassie v2 — 20 files (1 uploaded 12.4 KB, 19 reused)
```

## Drive it

For a **mujoco** scene the viewer is a real simulation, not a screenshot: the
engine runs on load, and the toolbar gives you **play / pause / reset /
speed**.

- **Sliders** — every actuator (`ctrl`, with its real range) and every
  hinge/slide joint, straight from the model.
- **t = 0 is your authored initial state** — when the model defines a
  `<keyframe>`, the viewer opens at (and **reset** returns to) keyframe 0,
  including its `ctrl`; without one it uses the compiled defaults (qpos0).
  *Keyframe honoring is a source change awaiting the next viewer
  deployment: the prior source baseline (and its wasm runtime) opens at
  qpos0 regardless of keyframes, so until the deploy — verify in the app —
  expect qpos0.*
- **⌥ / Alt + drag** — pull any body with a mass-scaled spring force, like the
  MuJoCo app's perturbation.
- **files** — the version's full file listing, entry highlighted.
- The first member visit renders the gallery **thumbnail** — see
  [Thumbnails](#thumbnails) for how the angle is chosen and how to control it.

A **urdf** scene opens as a poseable robot instead — no physics, pure
kinematics: every non-mimic revolute / continuous / prismatic joint gets a
slider with its real limits, **dragging a link in the scene rotates its
joint directly** (orbit pauses while you hold it), and **reset** returns the
pose to zero. Meshes referenced as relative paths or `package://` URIs
resolve against the pushed directory.

## Thumbnails

The scene grid's cover image is rendered in the browser the first time a member
opens a new version: a fixed 16:10 PNG with a **transparent background**, at
the scene's initial (t=0) pose — physics is held until the capture, so the
cover shows the authored t=0 state (see [Drive it](#drive-it)), not half a
second of free fall.

The camera angle is chosen from the scene itself, in priority order:

1. **A camera named `thumbnail`** — add one to your MJCF and the cover (and
   the viewer's opening shot) is exactly that camera:

   ```xml
   <worldbody>
     <camera name="thumbnail" pos="1.6 -1.8 1.4" xyaxes="0.75 0.66 0 -0.28 0.32 0.9"/>
     …
   </worldbody>
   ```

2. **The first `<camera>` in the model** (including `<include>`d files) —
   scenes authored with a hero camera need no rename.
3. **The free-camera stance MuJoCo's own viewer would use** —
   `<visual><global azimuth="…" elevation="…"/></visual>` plus
   `<statistic center="x y z" extent="…"/>` when authored. This is the
   cheapest lever: two lines, and the cover matches what you see in
   `simulate`:

   ```xml
   <statistic center="0 0 0.7" extent="1.2"/>
   <visual>
     <global azimuth="120" elevation="-20"/>
   </visual>
   ```

4. **A geometry fit** — bounding sphere of all geoms (ground planes
   excluded), from a three-quarter angle. URDF robots always use this fit.

Two overrides beat all of the above:

- **The camera button in the viewer toolbar** (members only, latest version):
  orbit to any angle and click it — that exact view becomes the cover, and
  the angle is remembered, so **future versions auto-capture from it** too.
- **`dreamlake scene push --thumbnail cover.png`** stores your own image
  (≤ 512 KiB PNG) and marks it manual, so the viewer won't overwrite it for
  that version. Works on a no-change push (thumbnail-only update).

## Pull it back

```bash
dreamlake scene pull cassie          # latest → ./cassie/
dreamlake scene pull cassie@1 -o v1  # any version
```

Every file is verified against its content hash on the way down — the
directory you get is byte-identical to the one that was pushed.

<span id="env-layers" />

## Scene layers

A scene can also be **composed from other scenes**. A layer stack
(`dreamlake.layers.json`) is an ordered list of **ops** — one flat object
per line, in the vocabulary of vuer's imperative updates — and
materializes into an ordinary `mujoco` scene. No layer has a special role,
and later ops win; swapping the gripper is editing one line and
re-pushing. The pushed version carries both the flat artifact (what every
viewer and SDK reads) and the pinned stack, so any composed scene can be
reopened, edited, and recomposed later.

```json file="dreamlake.layers.json"
{
  "schema": "dreamlake.env-layers/v3",
  "layers": [
    { "tag": "Merge",  "src": "you/kitchen" },
    { "tag": "Attach", "src": "you/sharpa-right", "key": "right",
      "at": "world", "pos": [0.45, -0.12, 0.30], "joint": "free-anchored" },
    { "tag": "Update", "key": "obj/mug", "pos": [0.30, 0.10, 0.02] },
    { "tag": "Remove", "key": "body:fixture/plant" }
  ]
}
```

```bash
dreamlake scene compose          # materialize ./dreamlake.layers.json locally
dreamlake scene push <out-dir>   # push artifact + pinned stack as one version
```

| op | what it does |
|----|--------------|
| `Merge` | union the scene's MJCF into the stack — a same-name collision is an error |
| `Attach` | graft the scene's subtree at a target under the identity root `key` (`right` makes `right:palm`), with a mount pose and joint mode |
| `Update` | inline sparse opinions: `key` addresses one element, every other prop is an MJCF attribute — nothing else is touched |
| `Remove` | delete the addressed element and its subtree — drop the line and it's back |
| `Patch` | `Update`-style opinions from a sparse-MJCF file or scene, for big opinion sets |

`src` is one string: `ns/name[@v]` is a registry scene (unversioned floats),
a `./`-prefixed path is a local directory or file.

> **Note:** Materialization is a real MuJoCo build, so `dreamlake scene compose`
>   delegates it to the engine in **dreamlake-py** — install it with
>   `pip install "dreamlake[compose]"` (Python + MuJoCo) on the composing
>   machine. Push / pull / list need no Python.

Every field, the exact semantics, and six annotated stacks:
[Scene Layers Reference](scenes-layers.md).

## Under the hood

Uploads go straight to storage with short-lived scoped credentials, and reads
are presigned URLs — **scene bytes never pass through the API server**. The
read side is two plain REST calls (`…/versions` and `…/versions/:v`), so any
HTTP client can list and download a scene without special tooling.

## Delete it (safely)

```bash
dreamlake scene delete cassie              # soft delete (restorable)
dreamlake scene restore cassie             # bring it back
dreamlake scene delete cassie --permanent  # erase storage — no undo
```

## Let Claude do it

Add the [scenes skill](https://github.com/dreamlake-ai/dreamlake-skills),
point at a repo, and say *"push the MuJoCo scenes in here to DreamLake"*:

```bash
git clone https://github.com/dreamlake-ai/dreamlake-skills.git ~/dreamlake-skills
mkdir -p ~/.claude/skills
ln -s ~/dreamlake-skills/dreamlake-scenes ~/.claude/skills/
```

Update with `git -C ~/dreamlake-skills pull --ff-only`. If a skill already
exists, preserve local edits before replacing it with a symlink.

The `dreamlake-scenes` skill does the part that isn't a single command:
extracting a **self-contained directory** from a scene that references
meshes outside itself (collecting the robot folders, rewriting the relative
paths), verifying the result still compiles before pushing, and running the
pull-back round-trip check after.

## Next steps

Recorded teleop episodes don't live here — they play back inside
**sources**, each dataset carrying its own model snapshot, with the scene
itself unchanged: [visualize a source](https://docs.dreamlake.ai/sources).

    One skill install, then build / edit / reuse scenes with ordinary
    prompts — locally or from the scene page's chat.

    The `dreamlake.layers.json` contract — merge / attach / override, field
    by field, with annotated stacks.

    Every flag — names, types, entries, visibility, limits.

    The REST endpoints behind push, versions, and presigned reads.

## Scenes compatibility and product vocabulary

Scenes are versioned worlds containing geometry, robots, objects, materials and
physics properties. A Simulation will pair a scene version with a simulator and
task logic (observations, actions, rewards and termination). A Sandbox is an
isolated execution workspace; a Run is one execution, and an Episode spans reset
to termination. Compute owns machines. Simulation and isolated Sandbox registries
are proposals, not existing interfaces; the bounded Compute experiment launcher
is not a sandbox lifecycle.

The canonical collection and detail URLs are `/<namespace>/scenes` and
`/<namespace>/scenes/<name>`. Old `/envs` browser URLs redirect, retaining resource,
query and fragment. Libraries remain a Scenes tab; library detail URLs remain
`/<namespace>/libraries/<name>`.

CLI 0.45.0 introduces `dreamlake scene` (`env` remains an alias). REST uses
`/namespaces/:slug/scenes` and all existing resource/version/upload/restore/delete
suffixes. The `/envs` API aliases run the same handlers, with identical auth and
storage; writes are not redirected. Catalog responses expose `scenes`, retaining
`envs` for older clients. Share tokens and resource identities are unchanged.
Existing `envType`, `EnvEntry`, `env_*` identifiers, `ENVS_*` configuration,
`envs/` object prefixes, the immutable `~/.dreamlake/cache/envs/` cache,
`dreamlake.env-layers/v3` and `dreamlake.envlayer` remain compatible technical
contracts. Login environments (`dreamlake auth env`), environment variables and
RL environment interfaces retain their technical names.
