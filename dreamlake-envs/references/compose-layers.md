# Compose Layers

## 5. Compose layered envs (`dreamlake.layers.json`)

An env can be **composed from other envs**: an ordered layer stack, each
layer carrying its own compose rule — `merge` (union; name collision is an
error), `attach` (graft a subtree at a target under a name prefix, with
mount pose + joint mode, optionally N instances), `override` (sparse MJCF
attribute opinions; the rule may also delete elements). Later layers win.
Materialization produces an ordinary `mujoco` env whose pushed version
carries the flat artifact and the pinned stack side by side.

**Read [`layers reference`](../reference/layers.md) before authoring a stack** — it maps
natural-language requests to stack constructs, gives the full field
reference, the six canonical stack shapes, and the error table. Owning
docs: https://docs.dreamlake.ai/envs/layers.

```bash
pip install "dreamlake[compose]"   # once — the CLI delegates materialization to dreamlake-py
dreamlake env compose              # materialize ./dreamlake.layers.json (or: compose <path>)
dreamlake env push <out-dir>       # artifact + pinned stack as one version
```

Push discipline: a stack containing local `{"path": …}` sources is refused
on push — pass `--push-layers` to push those layers as their own envs first
(prefer this; provenance stays resolvable), or `--allow-local` to push
anyway with the provenance permanently marked non-resolvable (only when the
user accepts that).

Three caveats to hold in mind while authoring (details in the reference):
overrides after an `attach` must target the **prefixed** names
(`right:palm`); override matching is **strict** (an unknown name is a
compose error, not a no-op); a `urdf` layer is attach-only and imports
**unactuated** (`nu = 0` — pair it with an actuator/damping override layer
or present it as visualization-grade).

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
