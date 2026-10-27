---
name: dreamlake-datasets
description: Get a robot dataset reachable and rendered in DreamLake — inspect and lay out the files, upload them or link S3/Hugging Face/Dropbox storage as a Source, prove that a Source holds the paths a workflow will read, and write or repair the .dreamrc that binds fields to views (video walls, charts, timelines, 3D, MuJoCo/URDF sim playback). Use for "visualize my data", "connect this bucket / HF repo", "check this source has these paths", or a dataset that renders wrong or not at all. Not for rolling a trained policy out to MCAP (sim-to-mcap), designing workflows (dreamlake-workflows), or annotation uploads (dreamlake-annotations).
---

# DreamLake datasets

Route on what the user has. Each action is self-contained; follow the handoff at
its end.

| User has | Action |
|---|---|
| Recordings on disk, "visualize my data", unsure what format | [prepare](actions/prepare.md) — inspect first, pick the layout, fix the video encoding |
| Files to get into storage, or bytes for an existing managed Source | [upload](actions/upload.md) — provider tools or `dreamlake source upload`; `index.json` for static HTTPS |
| Storage to link (S3 / Hugging Face / Dropbox), or a Source to verify | [connect](actions/connect.md) — dashboard linking, CLI browse/download, episode-tree alternative |
| A Source plus paths that a workflow spec will name | [check](actions/check.md) — prove browse **and** fetch; reject URLs and local paths |
| A reachable dataset root with no `.dreamrc`, or a broken one | [dreamrc](actions/dreamrc.md) — match `format`, read the field inventory, bind views |
| A draft `.dreamrc` to validate | [validate](actions/validate.md) — write → validate → fix loop, playground, option-level references |
| MuJoCo qpos logs or URDF joint trajectories | [sim-playback](actions/sim-playback.md) — convert to the sim-playback layout, bind `mujoco` / `urdf` |

Order for new data: prepare → upload → connect → check (only when a workflow
will read it) → dreamrc → validate. Sim playback plugs into prepare (layout) and
dreamrc (views).

## Rules that hold across actions

- Inspect before you ask. Deciding what the data is and how it should be laid
  out is your job; never ask "what format is this?" before looking.
- Sources keep data in place and never convert an unsupported container. Offer
  a conversion (LeRobot export, folder extraction, sim-playback layout) instead.
- A `.dreamrc` at a dataset root carries no `storage:` block; only a standalone
  draft adds one for local validation.
- Fetch the reference page for option-level detail; never invent `.dreamrc` keys.
- Report what you verified (source, path, size, verdict), never the short-lived
  URL that `fetch` mints.

## Boundaries

- A trained policy that still has to be rolled out in a simulator: the
  `sim-to-mcap` skill writes the MCAP, then returns here as `format: mcap`.
- Designing or publishing a WorkflowSpec: `dreamlake-workflows`; it calls this
  skill's `check` action for its inputs.
- Annotated episodes through the Python SDK: `dreamlake-annotations`.
- Moving a whole Project (a Source mount blocks it): the `projects` action of
  `dreamlake-cli`.

## Assets

`assets/dreamrc/` holds complete `.dreamrc` files to copy: a `fields` starter, a
LeRobot binding, and the `mujoco` / `urdf` sim-playback bindings.

## Canonical source

Product facts (commands, flags, keys, limits) live on the docs sites, not here:
https://docs.dreamlake.ai, https://cli.dreamlake.ai, https://viz.dreamlake.ai.
Any page is readable as Markdown at `<page-url>.md`; the whole corpus of a site
is at `<site>/llms-full.txt`. `reference/` holds CI-fetched copies of the pages
listed in `skill.json` `docs[]` — read them, never edit them.
