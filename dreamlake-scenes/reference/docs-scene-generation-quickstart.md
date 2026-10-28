<!-- generated from https://docs.dreamlake.ai/scene-generation/quickstart.md at 0.1.102 757a8c39; do not edit -->

# Scene Generation Quickstart

  Install one agent skill, then ask for scenes in plain language — *"build a
  kitchen counter with a mug and a cocoa tin"* — and get back a rendered,
  physically validated, versioned [scene](docs-scenes.md) you can keep editing with more
  prompts. This page is the install-and-use guide; the full method lives in
  the [Scene Generation](docs-scene-generation.md) technical guide.

## What the skill gives you

`dreamlake-scenes` teaches a coding agent (Claude Code, or any
Skills-compatible client) the complete scene workflow:

- **Source assets from anywhere** — download models from the internet (the
  [MuJoCo Menagerie](https://github.com/google-deepmind/mujoco_menagerie) is
  the curated first stop for robots), use files you already have, author
  props procedurally as plain MJCF, or pull from a
  [DreamLake asset library](https://docs.dreamlake.ai/libraries) when one is available. The library is
  a convenience — hash-verified pulls and versioned reuse — not a required
  first step.
- **Measure instead of guessing** — bundled inspection tools read each
  model's real dimensions and bounding boxes, so objects rest *on* tables
  instead of floating above them or launching out of them.
- **Validate the physics** — a short simulation checks penetration, support
  forces, and that props stay where they were placed, with explicit per-body
  assertions rather than a vague "looks stable".
- **Render and publish** — camera renders for your eyes, then
  `dreamlake scene push` publishes a versioned scene with an interactive
  [browser viewer page](docs-scenes.md), private by default.
- **Edit and reuse with more prompts** — a published scene stays editable:
  the agent pulls it back, changes what you asked for, and pushes a new
  version; existing scenes can seed new ones.

These scenes were produced by exactly this loop, from ordinary prompts,
during the skill's evaluation runs:

![A warm kitchen prep counter with a butcher-block top, a cutting board, a red patterned mug, and a cocoa tin under a key light.](https://docs.dreamlake.ai/images/scene-generation/kitchen-hero.png)

![A UR5e robot arm work cell: the arm mounted on a workbench with small parts placed on the table surface.](https://docs.dreamlake.ai/images/scene-generation/workcell-hero.png)

![A pottery display: bowls, a jug, cups, and a plate resting on a two-tier work table, with a shelf of glazed cups behind.](https://docs.dreamlake.ai/images/scene-generation/pottery-hero.png)

## Prerequisites

- **`dreamlake` CLI ≥ 0.45.0**, logged in (`dreamlake login`).
- **Python** — how much depends on the route the agent takes:
  - **Raw MJCF scenes** need only the skill's inspection/validation tools'
    dependencies: `mujoco` (≥ 3.2) and `numpy`. The layer composer is
    **optional** — a scene authored as one self-contained MJCF directory is
    pushed directly, no `dreamlake[compose]` install involved.
  - **Layer-composed scenes** (`dreamlake scene compose`) additionally need
    the composer: dreamlake-py ≥ 0.23 with **MuJoCo 3.14**. Details
    in [Scene Generation § Requirements](docs-scene-generation.md#requirements).
- **An agent that reads Skills** — Claude Code is the reference client.

A plain `pip install "dreamlake[compose]"` does **not** guarantee MuJoCo
3.14 — dreamlake 0.23.0 declares `mujoco>=3.2` (0.23.1 raises the floor
to `>=3.8`), and composition fails below 3.8 either way. Use a fresh venv
with pinned versions (the validated combination: Python 3.11, dreamlake-py
0.23.x, MuJoCo 3.14.0, NumPy 2.x), and verify what you got:

```bash
python3 -m venv ~/.venvs/dreamlake-scenes
source ~/.venvs/dreamlake-scenes/bin/activate
pip install "dreamlake[compose]==0.23.1" "mujoco==3.14.0"

python -c "import dreamlake, mujoco; print(dreamlake.__version__, mujoco.__version__)"
# expect: 0.23.1 3.14.0
dreamlake --version    # ≥ 0.45.0

# the CLI's compose step finds this venv through DREAMLAKE_PYTHON
# (there is no --python flag):
export DREAMLAKE_PYTHON="$(command -v python)"
```

Raw-MJCF-only setups can install just `pip install "mujoco==3.14.0" numpy`
into the venv instead.

## Install the skill

Scene generation ships in the `dreamlake-scenes` skill, written in the public
[dreamlake-skills](https://github.com/dreamlake-ai/dreamlake-skills)
repository: `SKILL.md`, one action page per task, the runnable `tools/`
(physics validation and reporting) and the reference pages fetched from
these docs. The `dreamlake` CLI installs it:

```bash
# once: pick Claude or Codex, and project or user scope
dreamlake init

# installs dreamlake-scenes and dreamlake-cli, which it requires
dreamlake skill install dreamlake-scenes
```

`dreamlake init` remembers the agent and scope; `--global` or `--dir` on a
later command overrides them for one install.

**Updating safely.** `dreamlake skill update dreamlake-scenes` brings in a
new release: unchanged files are replaced, files you have edited are
reported as conflicts and kept unless you pass `--force`, and nothing the
installer did not write is touched. `dreamlake skill list` shows the
installed and latest versions.

Without the CLI, download `skills.tar.gz` from the latest
[dreamlake-skills release](https://github.com/dreamlake-ai/dreamlake-skills/releases/latest)
and copy `dreamlake-scenes/` and `dreamlake-cli/` into `~/.claude/skills/`
(user scope) or `.claude/skills/` (one project). A copied directory has no
install manifest, so its first `dreamlake skill update` needs `--force`.

The agent discovers the skill from its frontmatter and picks it up when a
scene request matches — no registration step.

## Use it — ordinary prompts

No special syntax. Describe the scene, name the outcome you want:

**Create:**

> Build a breakfast table scene — a wooden table with two mugs and a bowl
> resting on it, warm lighting, a nice camera angle — and publish it to my
> namespace as `breakfast-table`.

**Edit** (a published scene stays editable — same name, new version):

> In `breakfast-table`, move the blue mug 10 cm to the left, dim the key
> light a little, and push the result.

**Reuse** (an existing scene can seed a new one):

> Start from `breakfast-table` and add a robot arm from the MuJoCo Menagerie
> on a stand next to the table. Publish it as `breakfast-robot`.

Behind each prompt the agent runs the loop from the
[technical guide](docs-scene-generation.md): source and verify assets, measure,
derive placements, compose, validate physics, render, push, and report the
version it published.

## What a finished run leaves you

Ask the agent to keep the **reusable deliverables** with your project, and
treat everything else as disposable scratch:

**Keep — this is what makes the scene editable and auditable later:**

- **The editable source** — the layer stack (`dreamlake.layers.json`) for
  composed scenes, or the authored MJCF directory for raw scenes. This is
  what edits are made to; the pushed scene embeds a pinned copy.
- **Per-model provenance** — for every third-party model: the exact source
  URL, version or commit, and its license (Menagerie models each carry their
  own `LICENSE` file — record each one, not one blanket note).
- **Component scenes** — base room and props published as their own pinned
  versions, when the composed route was used.
- **Initial state** — prop poses live in the stack (`Attach` `pos`/`quat`);
  an articulated opening pose is a keyframe block kept in a file beside the
  stack and re-applied after every recompose.
- **The published scene itself** — the compiled entry XML plus all assets, at
  an exact version from the push receipt.
- **Renders and the validation report** — the images you approved and the
  physics evidence behind the version.

**Disposable** — scratch pull directories, intermediate compose attempts,
validation JSON from rejected layouts, probe scenes: safe to delete once the
version is published and verified.

## Preview in the browser

Every pushed scene gets an interactive viewer page — open the link the push
prints, look at the framing and materials, and play the simulation
([Scenes guide](docs-scenes.md)).

<span id="generate-from-the-env-page" />

### Generate from the scene page

Scenes can also be created and edited *in the browser*, from a chat panel
next to the 3D viewer. This flow ships with the web app: it needs an app
deployment that includes scene chat, so if your scene page does not offer the
chat panel yet, that deployment hasn't reached your server — prompt your
local agent and use the browser to inspect the result instead. How it
works:

1. Open your namespace's **Scenes** catalog (`/<namespace>/scenes`) and click
   **+ new scene** (members only) — it sits in the page header next to the
   Scenes/Libraries switch, and an empty catalog offers the same
   button in its placeholder.
2. One click opens the scene page as a *draft* under an auto-minted name
   (`env_xxxxxx`) — there is no name dialog, and nothing is created on
   the server yet.
3. **Describe the scene** in the intro composer the draft opens into ("a
   breakfast table with two mugs and a bowl…"). The prompt goes to the
   embedded agent, which runs the same skill workflow — source, measure,
   compose, validate — and publishes with `dreamlake scene push`. The chat
   opens in **Auto** permission mode so this runs end-to-end without
   per-command approval; switching the composer to Ask/Plan makes it a
   read-only conversation (no generation, no push) until you switch back.
4. When the first push succeeds, the page swaps the draft placeholder for
   the **saved preview**: the interactive viewer on the version that was
   just pushed, with the chat still open beside it.
5. **Keep prompting to edit** — each successful push adds a version. The
   viewer follows the latest version; picking an older version from the
   header dropdown pins it (a "vN available" button jumps back to
   latest).
6. **Edit an existing scene** the same way: open its scene page (as a member)
   and use the chat panel beside the viewer.
7. **Reuse starts from the catalog, not from the source scene's page.** The
   chat edits the scene whose page it sits on — a "start from
   `breakfast-table` and add…" prompt *on `breakfast-table`'s own page*
   pushes new versions of `breakfast-table` itself. To grow a new scene
   out of it, go back to the Scenes catalog, click **+ new scene**, and
   prompt in the fresh draft: "Start from `breakfast-table` v3 and add a
   robot arm…". The new scene references the source at that pinned version;
   `breakfast-table` keeps its own versions, untouched.

## Next steps

    Sourcing, measuring, placement math, validation, publish/iterate.

    Push, version, drive, thumbnails, and pull round-trips.

    The full v3 stack grammar and compose semantics.
