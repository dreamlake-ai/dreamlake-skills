# Change a published scene, add a version, reuse one as a base

```bash
# edit the editable source, then push the SAME scene name → new version
dreamlake scene push ./composed --name <scene-name>
# ✓ pushed <ns>/<scene-name> vN+1 …
```

## Versions

A changed push under the same name creates a new version. An unchanged
entry and file set reuses the existing version; save the version from the
receipt instead of assuming it incremented. The CLI reports uploaded and
reused files. Shared meshes dedupe **across scenes** in the same namespace.
Receipt and retry rules: [push](push.md); verification:
[readback](readback.md). Owning page:
[Version it](reference/docs-scenes.md#version-it--only-changes-upload).

## Edit = edit the editable source

- **Raw MJCF scene**: edit the authored XML, re-validate, re-render, push.
- **Composed scene**: edit the **stack**, not the materialized XML — change
  the op (a mug's `Attach.pos`, a light `Update`) keeping instance keys
  stable, then recompose, re-validate, re-render, push again. One-line diff
  in the stack. Re-apply any post-compose `<keyframe>` block before the push
  ([validate](validate.md)).
- Keep the per-model provenance record ([source-assets](source-assets.md))
  beside the source — it answers "where did this model come from and under
  what license" at every future edit.

## Reuse a scene as a base

A pushed composed scene is an ordinary scene: start a new stack with
`{ "tag": "Merge", "src": "<ns>/<scene>@<v>" }` and attach more on top
([compose](compose.md)). It enters as one materialized layer; its own stack
is not re-walked. Pin the version for reproducibility.

Lifecycle commands (delete, restore, permanent): [restore](restore.md).
