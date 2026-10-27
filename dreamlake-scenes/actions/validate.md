# Validate the physics — per body, explicitly

```bash
python tools/scene_validate.py ./composed \
  --settle mug1:model --settle bowl:model=0.02 --support mug1:model
```

Explicit per-body assertions, no scene-wide "stable" verdict (an
uncontrolled robot is supposed to move). Applies identically to a raw MJCF
directory and a composed one. Tolerances and every flag:
`python tools/scene_validate.py --help`. Tool setup and the
`DREAMLAKE_PYTHON` rule: [design](design.md).

## What a run checks

Loads keyframe 0 (else qpos0) and holds authored `ctrl` (`--passive`
zeroes it); simulates `--seconds 2.0`. Hard failures: initial / mid-run /
final penetration beyond `--penetration-tol`, non-finite state, MuJoCo
warnings, bodies below `--floor-z`, and for each **named** body: drift
beyond its tolerance, residual speed/spin over `--max-speed`/`--max-spin`,
net attitude change over `--max-rotation`, or (`--support`) no contact
carrying real upward force. Note the `=` in `--settle body=0.02` — body
names contain `:` after attach. `--json` gives a machine-readable report.

## What a pass means — and does not

A pass covers exactly those checks for that initial state; it is not proof
of task feasibility or visual quality — render and look
([design](design.md)).

A settle/support pass also does **not** certify the authored pose: a prop
placed floating falls onto the table and still ends supported, but the
scene opens (and renders its cover) at the floating t=0 pose — simulation
never writes back into the artifact. Render the initial state and look;
if a settle row shows a straight drop (`start_pos` vs `end_pos` in the
JSON), fold that correction into the persistent `Attach.pos` (or your
keyframe) and recompose. A good-looking screenshot is not physical
validity either — both checks, separately.

## Initial state and keyframes

Any `Attach` strips all keyframes (dof layout changes); Merge-only stacks
keep them. Need an articulated opening pose (servo-held arm)? Append your
`<keyframe>` block to the **materialized** entry XML after compose,
re-validate, then push — and re-apply it after every recompose (keep the
block in a file beside the stack). The viewer opens at keyframe 0 when one
exists, but keyframe honoring is a source change awaiting a viewer
deployment — which versions actually honor it and what t=0 shows:
[Drive it](../reference/docs-scenes.md#drive-it); confirm visually rather than
assuming.

Owning method pages:
[Validate physics — and know what a pass means](../reference/docs-scene-generation.md#validate-physics--and-know-what-a-pass-means)
and
[Initial state and keyframes](../reference/docs-scene-generation.md#initial-state-and-keyframes).
