# Push a scene

```bash
dreamlake scene push /tmp/scenes/my-scene                 # entry auto-detected; prints an open link
dreamlake scene push <dir> --namespace <org>              # into an org instead of your personal namespace
dreamlake scene push <dir> --name <scene-name> --title "…" --description "…"
dreamlake scene create <dir>                              # push that FAILS if the name already exists
# ✓ pushed <ns>/<scene-name> vN …   ← record N
```

Only push after the staged directory passed [package](package.md) and
[validate](validate.md) checks **and the user asked to publish**. Flags
(`--entry`, `--type`, `--visibility`, `--share`, `--thumbnail`, …):
`dreamlake scene push --help` and [Push a version](reference/cli-scenes.md#push-a-version).
Private by default; `--visibility public` opens the viewer without login,
`--share` mints a `?share=` link; `--type isaaclab` is stored and pullable
but only `mujoco` and `urdf` have viewers; `--thumbnail` is covered in
[thumbnail](thumbnail.md).

## Entry auto-detection

The single root-level `*.xml`/`*.mjcf` containing `<mujoco>`, or — with no
MJCF around — the single root-level `*.urdf` containing `<robot>`, which
also sets `type: urdf`. Two candidates at the root → the push asks for
`--entry`.

## Save the version from the receipt

Re-pushes upload only changed file blobs (content-addressed). On a
network/backend error or timeout, **check before retrying**: compare
`dreamlake scene list` with your last receipt to see what actually landed.
Retrying an _unchanged_ directory is normally safe — the CLI's no-change
guards compare entry + file hashes with the latest version and reuse,
re-register, or adopt an identical version instead of minting a new one.
Those are content checks, not a transaction guarantee: a directory edit
between attempts or an intervening different push means the retry mints a
legitimate new version. Keep the same inputs, retry at most 2–3 times,
confirm the version on the final receipt, and report ambiguity with what
`scene list` shows — don't assume. Save the version for
[readback](readback.md).

## Composed scenes

A stack containing local (`./`-prefixed, unpinned) srcs is refused on push:
pass `--push-layers` to push those layers as their own scenes first, pin,
and recompose (prefer this; provenance stays resolvable), or
`--allow-local` to push anyway with the provenance permanently marked
non-resolvable — only when the user accepts that. Details:
[Pushing a composed scene](reference/cli-scenes.md#pushing-a-composed-scene).

## Preview in the browser

Open the scene page and look with human eyes: hero framing from your
`thumbnail` camera, materials under viewer lighting, props resting where
placed, play/pause/reset sane. The push prints an `open:` link; on the
staging deployment, CLIs ≤ 0.37.0 print the API host there — set
`DREAMLAKE_WEB_URL=https://staging.dreamlake.ai` (an override those CLIs
honor), upgrade to CLI ≥ 0.45.0 (its receipts target the web app), or use
your namespace's Scenes page. Only `mujoco`-type scenes get the interactive
simulating viewer (`urdf` gets the kinematic poser). The first member visit
captures the gallery thumbnail. What t=0 shows — and which viewer versions
honor keyframe 0 — is in [Drive it](reference/docs-scenes.md#drive-it);
confirm visually rather than assuming. Where the catalog, profile tab and
detail header take anonymous and signed-in readers:
[Browsing in the app](reference/docs-scenes.md#browsing-in-the-app).

## Traps

- **`dreamlake env` used to mean login environments.** That command is now
  `dreamlake auth env …`; if `scene push` is missing, upgrade to CLI 0.45.0
  or later.
- **Unattended runs**: set `DREAMLAKE_API_KEY` (whose identity the push is
  attributed to) and `DREAMLAKE_REMOTE` (which deployment), or the CLI uses
  whatever login is active on that machine.
- The push uploads everything under the directory — stage a clean copy
  ([package](package.md)).

An owned scene moves with its whole Project; see the `projects` action of
`dreamlake-cli`.
