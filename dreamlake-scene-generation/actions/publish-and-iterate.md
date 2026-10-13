# Publish and iterate

Push the scene directory — a composed output or a raw authored MJCF
directory — as a normal scene (private by default) and **save the version
from the receipt**:

```bash
dreamlake scene push ./composed --name <scene-name> --title "..."
# ✓ pushed <ns>/<scene-name> vN …   ← record N
```

Re-pushes upload only changed file blobs (content-addressed). On a
network/backend error or timeout, **check before retrying**: compare
`dreamlake scene list` with your last receipt to see what actually landed.
Retrying an _unchanged_ directory is normally safe — the CLI's no-change
guards compare entry + file hashes with the latest version and reuse,
re-register, or adopt an identical version instead of minting a new one.
Those are content checks, not a transaction guarantee: a directory edit
between attempts or an intervening different push means the retry mints a
legitimate new version. Retry at most 2–3 times, confirm the version on
the final receipt, and report ambiguity with what `scene list` shows —
don't assume. Pushing a stack that still
references local `./` layers is refused: push those as scenes first
(`--push-layers`), pin, and recompose — or `--allow-local` if you accept
non-resolvable provenance.

**Preview in the browser.** Open the scene page and look with human eyes:
hero framing from your `thumbnail` camera, materials under viewer
lighting, props resting where placed, play/pause/reset sane. The push
prints an `open:` link; on the staging deployment, CLIs ≤ 0.37.0
print the API host there — set
`DREAMLAKE_WEB_URL=https://staging.dreamlake.ai` (an override those
CLIs honor), upgrade to CLI ≥ 0.45.0 (its receipts target the web app),
or use your namespace's Scenes page. Only `mujoco`-type scenes get
the interactive simulating viewer (`urdf` gets the kinematic poser). The
first member visit captures the gallery thumbnail. What t=0 shows — and
which viewer versions actually honor keyframe 0 — is in the
[scenes reference](../reference/scenes.md#drive-it); confirm visually rather
than assuming.

**Verify the round trip** when the scene will be consumed elsewhere — pull
the exact receipt version into a fresh empty directory (a bare
`scene pull <name>` fetches latest, which can race a concurrent push):

```bash
dreamlake scene pull <scene-name>@<N> -o ./readback
python tools/scene_validate.py ./readback --settle <body>
```

Pulls are hash-verified; compare the entry XML (including any keyframe
block you appended post-compose), the validation result, and — for a
composed scene — the embedded pinned `dreamlake.layers.json`, the stack
that keeps it editable.

**Edit = edit the editable source**, then push the same scene name for a new
version. Raw MJCF scene: edit the authored XML, re-validate, re-render,
push. Composed scene: edit the **stack**, not the materialized XML — change
the op (a mug's `Attach.pos`, a light `Update`) keeping instance keys
stable, then recompose, re-validate, re-render, push again. One-line diff
in the stack. Re-apply any post-compose `<keyframe>` block before the push
([compose and validate](compose-and-validate.md)). Keep the per-model
provenance record ([source assets](find-assets.md)) beside the source — it
answers "where did this model come from and under what license" at every
future edit.

**Reuse a scene as a base.** A pushed composed scene is an ordinary scene:
start a new stack with `{ "tag": "Merge", "src": "<ns>/<scene>@<v>" }` and
attach more on top. It enters as one materialized layer; its own stack is
not re-walked. Version/lifecycle commands (delete, restore, permanent):
[scenes reference](../reference/scenes.md).
