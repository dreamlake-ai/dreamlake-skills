---
name: video-labeling-workflow
description: Create and publish the fixed video subtask-labeling workflow on DreamLake — collect a connected source plus the video and reference-annotation paths inside it, verify the worker can read them, fill the bundled five-stage template (LeRobot wrap → VLM subtask segmentation → WiLoR hand pose → scoring against the reference → publish as an annotation behind a review gate), confirm the resolved inputs, and push a workflow the user can Run from the canvas. Use for "create a video labeling workflow", "创建一个视频打标的 workflow", or segmenting a manipulation video into subtasks with hand pose and accuracy scores. Takes precedence over designing a new graph; use dreamlake-workflows only for a workflow this one does not cover.
---

# Create a video labeling workflow

Fill the supplied fixed template; do not design a new graph. Follow the four
actions in order and stop at every "wait" — publishing proceeds only after the
user confirms the resolved source paths, task description, and publishing
namespace.

| Step | Action |
|---|---|
| 1–2. Ask for the four inputs in one message; pick a fresh time-stamped name | [collect-and-name](actions/collect-and-name.md) |
| 3. Prove the source holds both paths (browse **and** fetch) | [check-inputs](actions/check-inputs.md) → the `check` action of `dreamlake-datasets` |
| 4. Substitute only the six placeholders; show the resolved data back and wait | [fill-and-confirm](actions/fill-and-confirm.md) |
| 5–6. Push to the confirmed namespace; hand over the link in two lines | [publish-and-handoff](actions/publish-and-handoff.md) → the `publish` action of `dreamlake-workflows` |

## Rules that hold across actions

- Talk like a product: say **workflow**, never "pipeline"; never narrate
  "template", "fixed", "instantiate", or the stage list to the user.
- Inputs are read from a connected **source**; URLs and local paths are
  rejected — the job runs on a worker elsewhere.
- The source's namespace and the publishing namespace are independent; ask,
  never infer one from the other, and never silently publish to the personal
  namespace.
- A fresh name every time (`video-labeling-<MMDD>-<HHMM>` from the real clock)
  unless the user supplies one; pushing an existing name appends a version.
- Substitute only `{{WORKFLOW_NAME}}`, `{{SOURCE}}`, `{{SOURCE_NAMESPACE}}`,
  `{{VIDEO_PATH}}`, `{{GOLD_PATH}}`, `{{TASK}}`; add no parameters.

## Assets

`assets/templates/video-labeling.workflow.json` — the five-stage, nine-node
template. Its parameters were set by measurement; changing the template or the
UDFs requires `python -m workflow_runtime.tests.test_spec_params <file>` in
the WORKER's environment before shipping the change.

## Boundaries

- Anything other than this fixed shape: the `design` action of
  `dreamlake-workflows`.
- Worker prerequisites (refiner, dreamlake/dreamdb, dreamlake-lakeshore,
  Gemini key, WiLoR conda env, `HAND_POSE_REPO`) are listed in
  [publish-and-handoff](actions/publish-and-handoff.md); mention them only if
  asked or if a run fails.

## Canonical source

Product facts (node vocabulary, CLI flags, validation output) live on the docs
sites, not here: https://docs.dreamlake.ai, https://cli.dreamlake.ai,
https://viz.dreamlake.ai. Any page is readable as Markdown at
`<page-url>.md`; the whole corpus of a site is at `<site>/llms-full.txt`.
`reference/` holds CI-fetched copies of the pages listed in `skill.json`
`docs[]` — read them, never edit them.
