# Compose Layers

## 5. Compose layered scenes (`dreamlake.layers.json`)

A scene can be **composed from other scenes**: an ordered stack of flat ops
(schema `dreamlake.env-layers/v3`, vuer-style component grammar) —
`Merge` (union; name collision is an error), `Attach` (graft a subtree at
a target under the identity root `key`, with mount pose + joint mode; one
entry per placement), `Update` (inline sparse opinions: `key` addresses an
element, every other prop is an MJCF attribute), `Remove` (delete an
element + subtree), `Patch` (Update-style opinions from a sparse-MJCF
file or scene). Later ops win. `src` is one string — `ns/name[@v]` is a
registry scene, a `./`-prefixed path is local. Materialization produces an
ordinary `mujoco` scene whose pushed version carries the flat artifact and
the pinned stack side by side.

**Read [`layers reference`](../reference/layers.md) before authoring a stack** — it maps
natural-language requests to stack constructs, gives the full field
reference, the six canonical stack shapes, and the error table. Owning
docs: https://docs.dreamlake.ai/scenes/layers.

```bash
pip install "dreamlake[compose]"   # once — the CLI delegates materialization to dreamlake-py
dreamlake scene compose              # materialize ./dreamlake.layers.json (or: compose <path>)
dreamlake scene push <out-dir>       # artifact + pinned stack as one version
```

Push discipline: a stack containing local (`./`-prefixed, unpinned) srcs
is refused on push — pass `--push-layers` to push those layers as their
own scenes first (prefer this; provenance stays resolvable), or
`--allow-local` to push anyway with the provenance permanently marked
non-resolvable (only when the user accepts that).

Three caveats to hold in mind while authoring (details in the reference):
ops after an `Attach` must target the **keyed** names (`right:palm`);
Update/Patch matching is **strict** (an unknown address is a compose
error, not a no-op — a bare name shared across kinds must be qualified,
`body:thing`); a `urdf` layer is Attach-only and imports **unactuated**
(`nu = 0` — pair it with Update ops adding actuators/damping or present
it as visualization-grade).

## Traps

- **Videos, logs, notebooks don't belong in the directory** — the push
  uploads everything under it. Stage a clean copy rather than pushing a
  repo subfolder that also holds outputs, `__pycache__/`, or previews.
- **`dreamlake env` used to mean login environments.** That command is now
  `dreamlake auth env …`; if `scene push` is missing, upgrade to CLI 0.45.0 or later.
- **Unattended runs**: set `DREAMLAKE_API_KEY` (whose identity the push is
  attributed to) and `DREAMLAKE_REMOTE` (which deployment), or the CLI uses
  whatever login is active on that machine.
