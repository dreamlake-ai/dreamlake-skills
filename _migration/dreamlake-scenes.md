# Migration: dreamlake-scenes

RFC 0010 S3 (content merge B). Sources: `dreamlake-scene-generation`
(SKILL + 4 actions + 4 generated reference pages + `tools/`),
`dreamlake-scenes` (SKILL + 5 references + hand-reconciled
`reference/layers.md`), `dreamlake-envs` (deprecated alias, deleted).

**Decision — `dreamlake-libraries` stays a separate skill.** Applying the
merge-caution rules: publishing and curating an asset library is a distinct
user goal that someone installs on its own (a team shipping a splat or mesh
library never builds a scene), and the libraries SKILL alone is 15 KB of
hand-written text, which would push the merged scenes skill past the ~50 KB
bound and past 12 actions. `dreamlake-scenes` routes to it by name
(`SKILL.md` § Boundaries, `actions/source-assets.md`). The integrator should
keep `dreamlake-libraries` in `catalog.json` and **not** add a
`dreamlake-libraries → dreamlake-scenes` entry to `renamed.json`; see
`_migration/dreamlake-libraries.md`.

`docs[]`: docs.dreamlake.ai/scene-generation,
docs.dreamlake.ai/scene-generation/quickstart, docs.dreamlake.ai/scenes,
docs.dreamlake.ai/scenes/layers, cli.dreamlake.ai/scenes,
cli.dreamlake.ai/projects (all verified `.md` → 200). No libraries page
exists on cli.dreamlake.ai (`/libraries.md` → 404); the docs-site libraries
pages belong to `dreamlake-libraries`.

`skill.json.tools`: `python >=3.10` (no 3.11-only syntax in `tools/`),
packages `mujoco>=3.2`, `numpy`, `pytest` (the test module imports it).

| Source file / section | Destination | Notes |
| --- | --- | --- |
| `dreamlake-scene-generation/SKILL.md` (frontmatter, ordered action list, tools summary, CLI ≥ 0.45.0 / dreamlake[compose] ≥ 0.23 constraints) | `SKILL.md` | "Generated from the workspace guide" provenance footer dropped: the retired sync pipeline |
| `scene-generation/actions/find-assets.md` (origins, visual-reference distinction, provenance per model, acceptance checklist, GLB/FBX, library search traps, pull verification) | `actions/source-assets.md` | Library command scopes now routed to `dreamlake-libraries` `search`; scene-side traps (ranked ≠ relevant, zero results switch source, semantic fallback, sha256 pulls) kept |
| `scene-generation/actions/design-and-inspect.md` (tool setup, `DREAMLAKE_PYTHON`, measure before placing, tight bounds, real-world anchors, wrap OBJ/STL with `mass="0"`, author base scene, render/`MUJOCO_GL=egl`) | `actions/design.md` | Verbatim |
| `scene-generation/actions/compose-and-validate.md` § two routes, prerequisites (0.23.0 vs 0.23.1, mujoco 3.2/3.8/3.14 pins, `DREAMLAKE_PYTHON`), components become layers, example stack, key/pos/quat/boolean/Patch caveats, compose `-o`, cache, errors link | `actions/compose.md` | Merged with the two items below |
| `compose-and-validate.md` § Validate the physics, pass semantics, settle ≠ pose certification, initial state / keyframes after Attach | `actions/validate.md` | Split out: one task per file |
| `scene-generation/actions/publish-and-iterate.md` § push + receipt, retry semantics, local-layer refusal | `actions/push.md` | Merged with `scenes/references/push-environment.md` § 2 (same task) |
| `publish-and-iterate.md` § Preview in the browser (`DREAMLAKE_WEB_URL` for CLIs ≤ 0.37.0, viewer types, thumbnail on first visit, keyframe honoring) | `actions/push.md` § Preview in the browser | |
| `publish-and-iterate.md` § Verify the round trip | `actions/readback.md` | Merged with `version-and-remove.md` § 3 (same task) |
| `publish-and-iterate.md` § Edit = edit the editable source; § Reuse a scene as a base | `actions/iterate.md` | |
| `scene-generation/tools/` (`scene_common.py`, `scene_report.py`, `scene_render.py`, `scene_validate.py`, `test_scene_tools.py`) | `tools/` (git mv, unchanged) | Tests: see validation output in the PR |
| `scene-generation/reference/scene-generation.md`, `libraries.md`, `scenes.md`, `scenes-layers.md` (generated) | deleted; CI fetches `reference/docs-scene-generation.md`, `docs-scenes.md`, `docs-scenes-layers.md` from `docs[]`; `docs-libraries.md` is fetched by `dreamlake-libraries` | Generated copies, no hand-written content |
| `dreamlake-scenes/SKILL.md` (prepare-only rule, CLI 0.45.0, recordings boundary) | `SKILL.md` | Boundary now names `dreamlake-datasets` (RFC §4 name) |
| `scenes/references/catalog.md` § Browsing in the app | dropped: verbatim copy of `docs.dreamlake.ai/scenes#browsing-in-the-app` (fetched into `reference/docs-scenes.md`); `actions/push.md` § Preview points to it | |
| `catalog.md` "Source … sources.json" provenance note | dropped: describes the retired sync pipeline | |
| `scenes/references/prepare-environment.md` § 1 extract (grep, sed, three rules, compile check, URDF check) | `actions/package.md` | Verbatim |
| `prepare-environment.md` § Stop conditions | `actions/package.md` § Stop conditions | |
| `scenes/references/push-environment.md` § 2 push commands, flags table, entry auto-detection, retry after error | `actions/push.md` | Flag table not restated (→ `reference/cli-scenes.md#push-a-version` / `--help`); semantics of `--entry`, `--type`, visibility, `--thumbnail` kept |
| `push-environment.md` § 2b author the thumbnail (priority order, two-line framing, dedicated camera, local verification, t=0 rule, overrides) | `actions/thumbnail.md` | Verbatim |
| `scenes/references/version-and-remove.md` § 3 version, pull, verify | `actions/iterate.md` § Versions + `actions/readback.md` | |
| `version-and-remove.md` § 4 delete safely (+ #1343 project placements) | `actions/restore.md` | |
| `version-and-remove.md` § Project-derived access | `actions/restore.md` § Project-derived access | |
| `version-and-remove.md` § Whole-Project transfer boundary (`env` type, `PROJECT_STREAM_RESOURCE_UNSUPPORTED`, legacy replay, no standalone move) | `dreamlake-cli/actions/projects.md` (other agent); here one sentence in `actions/push.md`, `actions/restore.md`, `SKILL.md` | Per task instruction |
| `scenes/references/compose-layers.md` § 5 model summary, pip install, compose/push commands, push discipline, three caveats | `actions/compose.md` (§ The model compressed, § Authoring caveats) + `actions/push.md` § Composed scenes | |
| `compose-layers.md` § Traps (clean directory, `dreamlake env` → `auth env`, unattended `DREAMLAKE_API_KEY`/`DREAMLAKE_REMOTE`) | `actions/package.md` § Keep the directory clean; `actions/push.md` § Traps | |
| `scenes/reference/layers.md` § Model, compressed | `actions/compose.md` § The model, compressed | Hand-reconciled file, not generated |
| `layers.md` § From the user's words to a stack (table + joint choice) | `actions/compose.md` § From the user's words to a stack | |
| `layers.md` § Field reference (distilled) | dropped: duplicates `docs.dreamlake.ai/scenes/layers` field reference (fetched into `reference/docs-scenes-layers.md`); `actions/compose.md` links it | |
| `layers.md` § Workflow (pip, compose, push, cache path, push discipline) | `actions/compose.md` top + § Materialize; `actions/push.md` § Composed scenes | |
| `layers.md` § The six stack shapes | dropped: duplicates `docs.dreamlake.ai/scenes/layers#examples` (same six stacks); `actions/compose.md` links it | |
| `layers.md` § Migrating a v2 stack | dropped: duplicates `docs.dreamlake.ai/scenes/layers#migrating-a-v2-stack`; `actions/compose.md` links it | |
| `layers.md` § Errors and remedies | dropped: duplicates `docs.dreamlake.ai/scenes/layers#common-errors` (which also carries the 3.2 and `xyaxes` rows); `actions/compose.md` § Materialize links it | |
| `layers.md` § Caveats (URDF Attach-only/unactuated, key targeting, strict matching, order, pin) | `actions/compose.md` § Authoring caveats | |
| `dreamlake-envs/SKILL.md` (alias to scenes; `dreamlake env` alias, `/envs` compatibility, login-env names unchanged) | deleted; `SKILL.md` § Boundaries one line → `reference/docs-scenes.md#scenes-compatibility-and-product-vocabulary` | Rename map handled by the integrator (`renamed.json`: `dreamlake-envs` → `dreamlake-scenes`, `dreamlake-scene-generation` → `dreamlake-scenes`) |
