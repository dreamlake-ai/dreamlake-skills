---
name: video-labeling-workflow
description: >
  Create and publish a video subtask-labeling workflow on DreamLake — collect
  the source and the paths to the video and reference annotations, verify the
  worker can read them, confirm with the user, and push a workflow they can Run
  from the canvas. Use when the user asks to "create a video
  labeling workflow", "创建一个视频打标的 workflow", or wants to segment a
  manipulation video into subtasks, estimate hand pose, score against reference
  annotations, and publish an annotated result. Takes precedence over
  workflow-generator for video labeling; use workflow-generator only for a
  workflow this one does not cover.
---

# Video subtask-labeling workflow

## Talk like a product, not like a build system

Everything below the next heading is **internal**. Do not narrate it. The user
should never hear "fixed", "template", "instantiate", "hard-coded", "pipeline
shape", or a stage-by-stage recital of the graph — that reads as a canned script
rather than a capability, and this is often shown to an audience.

Say **workflow**, never "pipeline". Keep every message short. Announce nothing;
just ask for what you need, then report the link.

Internally: the graph is not yours to design. Fill
`reference/template.workflow.json` and change nothing else. Do not route this
through `workflow-generator` — that skill designs new graphs from a description,
and is only appropriate when the user wants something this workflow does not do.

## The workflow

Five stages, nine nodes — `reference/template.workflow.json`:

```
prepare    video_source ──┬─→ video_to_lerobot ─→ subtask_labeler (uda) ─┬────────┐
                          │                                              │        │
handpose                  └─→ video_frames ─→ hand_pose ── keypoints ──────────┐  │
                                                                          │    │  │
evaluate       gold_source ────────────────────────────→ subtask_metrics ─┘    │  │
                                                                               ↓  ↓
publish                   └──────────────── video ──────────────────→ publish_annotation
                                                                             ↓
                                                                      review_gate ⏸
```

| Stage | Does |
|---|---|
| prepare | wrap the video as a single-episode LeRobot dataset (resamples NTSC fps) |
| annotate | two-stage VLM segmentation + relabeling → `labeled_subtasks` |
| handpose | sample frames, estimate 21-keypoint hand pose (WiLoR on GPU), render the overlay |
| evaluate | temporal IoU / boundary-F1 / label agreement vs the gold phase captions |
| publish | one DreamLake **annotation**: video + subtask timeline + skeleton overlay, then a gate holding the run for review |

## Procedure

### 1. Collect inputs

Inputs are read from a connected **source**, not from URLs. Ask for four things
in one message. Match the user's language. Keep it to a few lines — no preamble,
no description of what the workflow does internally:

> 需要四个输入：
>
> 1. **数据源名称** —— 已连接的 source（`dreamlake source list` 可看）
> 2. **视频路径** —— source 里那个视频的路径
> 3. **参考标注路径** —— source 里的基准标注（JSON），用于评分
> 4. **任务描述** —— 一句话说明视频里在做什么，如 `mount a wall shelf`
>
> source 在 `<默认 namespace>` 下吗？不是的话请说明——它和 workflow 发布到哪
> 个组织无关。workflow 发布到 `<默认 namespace>`，需要发到别的组织请说明。

English equivalent, same length:

> I need four things:
>
> 1. **Source name** — a connected source (`dreamlake source list` shows them)
> 2. **Video path** — where the video sits inside that source
> 3. **Reference annotation path** — the baseline annotations (JSON) to score against
> 4. **Task description** — one line on what happens in the video, e.g. `mount a wall shelf`
>
> Is the source in `<default namespace>`? Say so if not — it is unrelated to
> which org the workflow publishes to. Publishing to `<default namespace>`;
> say so if it should go elsewhere.

Fill in the real default rather than a placeholder — and name the user's
organisations as the alternatives, since a workflow that silently lands in a
personal namespace when it was meant for the team is only discovered later, by
someone who cannot find it:

```bash
dreamlake profile     # the default namespace
dreamlake org list    # orgs the user belongs to; an org slug IS a namespace
```

If `dreamlake` is not on PATH, ask where it is rather than guessing — this skill
runs on whatever machine the chat is hosted on, which is not necessarily anyone's
laptop.

If the user already supplied everything in their opening message, skip this and
go straight to validation.

Why each matters (for your own judgement, not to recite): the reference file
needs `phase_captions` to score against; the task description is fed to the
model as the episode goal and becomes the annotation's label, so a vague one costs
annotation quality; local paths cannot work because the job runs on a worker
elsewhere, and a URL cannot work either — it expires, and it tells whoever opens
the canvas later nothing about where the data came from.

The source's namespace and the publishing namespace are **independent**. Footage
often belongs to whoever collected it while the result belongs to the team doing
the labelling, so never infer one from the other — ask.

### 2. Name it — a fresh name every time

**Do not reuse a fixed name.** Generate one stamped with the current local time:

```
video-labeling-<MMDD>-<HHMM>        e.g. video-labeling-0802-1430
```

Read the clock at generation time (`date +%m%d-%H%M`) rather than guessing —
a wrong timestamp is worse than none.

This matters because pushing an existing name **appends a version** rather than
creating something new: reusing one leaves you presenting a `v4` that carries
every earlier run — including failed ones — in its history. A fresh name gives a
clean workflow with exactly one run, which is what "create a workflow" should
produce and what a demo should show.

If the user supplies a name explicitly, use theirs verbatim (they may be
returning to something on purpose). Either way it must match
`^[a-z0-9][a-z0-9._-]{0,63}$`.

### 3. Validate the data — invoke `remote-source-check`

Do not skip this and do not eyeball it. A path that does not exist produces a
workflow that looks finished and fails minutes into a run, after the queue and a
transcode.

If a check fails, report which input and why, ask for a correction, and stop.

### 4. Fill the template

Copy `reference/template.workflow.json` and substitute:

| Placeholder | Value |
|---|---|
| `{{WORKFLOW_NAME}}` | the workflow name |
| `{{SOURCE}}` | source name → `source` on **both** source nodes |
| `{{SOURCE_NAMESPACE}}` | the namespace the SOURCE lives in → `source_namespace` on both |
| `{{VIDEO_PATH}}` | video path inside the source → `video_source.compute.params.path` |
| `{{GOLD_PATH}}` | gold path inside the source → `gold_source.compute.params.path` |
| `{{TASK}}` | task description → `video_source.compute.params.task` |

Substitute **only** these. Everything else — udf paths, port names, ports,
`execution` blocks — was set by measurement, and changing one silently breaks
rendering or execution.

You are FILLING this template, not designing it. Whether its parameters match
what the worker's UDFs accept is a property of the template, checked once by
whoever changes it — not something to re-derive per workflow, and not something
this skill can check anyway: it may be running somewhere with no source tree and
no worker environment. If you edit the template or the UDFs, run
`python -m workflow_runtime.tests.test_spec_params <file>` in the WORKER's
environment before shipping the change.

`review_gate` sits AFTER `publish_annotation`, not before it. A gate asking
someone to review the result has to run once the result exists — placed earlier
it asks them to approve something they cannot open, and the page has no
annotation to link to. It carries no `execution.timeout`: a run may sit at a gate for
months at no cost (the worker checkpoints and ACKs), and a timeout there would
kill work for the crime of being reviewed on a Monday.

**Do not add parameters the template omits.** `params` is not documentation: the
canvas turns every entry into an input box and the engine passes it to the UDF
as a keyword argument, so anything listed there is an invitation to change it,
and every listed thing must be safe to change. What the template leaves out is
left out deliberately, and the UDF's own default applies:

Omitting a parameter means the UDF's own default applies, so check that the
default is the safe value before leaving one out. `hand_pose.methods` defaults
to all four methods and was omitted once on the reasoning that it should not be
editable — the next run died on `conda env 'hpe-mmpose' not found`, because the
list in the template was the only thing keeping it to the one method the worker
has installed. It is declared, as a LIST: the inspector renders arrays read-only,
so declaring it constrains the run and shows it on the canvas without inviting
an edit.

| Omitted | Why it must not be editable |
|---|---|
| `video_to_lerobot.video_key` | the LeRobot column name; changing it leaves the three downstream nodes unable to find the video |
| `hand_pose.overlay_method`, `use_conda` | default to `wilor` / `True`, which is what the worker has; a different method needs its own environment built there first |
| `video_source.remote_url`, `local_path` (and the same on `gold_source`) | the fallback for runs with no source behind them; exposing it invites a URL back into the spec, which is what naming a source replaced |
| `publish_annotation.namespace` | defaults to the namespace the RUN belongs to, which is where a team's results should land; setting it here publishes someone else's workflow output into your org |
| `publish_annotation.camera` | only `main` renders — a different camera writes an episode the web app cannot show (measured) |
| `publish_annotation.backend`, `unique_name` | point the publish at a local backend / stop the run-id suffix; both produce a run that appears to succeed and publishes nowhere useful |
| `subtask_labeler.sample_sec`, `frames_per_sheet` | refiner reads these in a worker SUBPROCESS, so a value set here is ignored; the handler rejects them rather than pretend |
| `subtask_labeler.min_coverage` | the acceptance threshold for a silent VLM truncation; loosening it re-admits the failure it exists to catch |

Every node carries an `execution` block, and the engine enforces it: `timeout`
(`30s`/`90m`/`2h`) bounds the node and kills what it is waiting on, and
`retry.max_attempts` re-runs the node alone — not the workflow — for timeouts
and transient faults, never for a rejected credential. These are editable on the
canvas because they are safe to change; the defaults come from measured
durations (annotation 4–5 min, hand pose ~135 ms per sampled frame).

`video_frames` samples at **15 fps with no cap** (`max_frames: 0`). Both halves
matter and both were once wrong. A cap of 300 quietly limited hand pose to the
first `300 / fps` seconds — a ten-minute video came out with a subtitle track
over all of it and a skeleton over the first minute, which reads as a broken
overlay rather than a setting. And at 5 fps the skeleton only moves every 200 ms
against a 30 fps video, so it stutters: the overlay can never be smoother than
the sampling. 15 fps costs about 135 ms per frame of GPU time and stays well
inside the node's 4h budget.

Note that WiLoR runs per frame with no temporal smoothing, so denser sampling
trades a slideshow for whatever per-frame jitter the estimator has. If the
overlay looks shaky rather than choppy, that is the thing to fix — not the
sampling rate.

Write the result to `<name>.workflow.json` in the working directory.

### 4b. Show the data back, and wait

**Do not push until the user has confirmed the inputs.** Show exactly what the
spec will carry — not what they typed, what you resolved:

> 确认一下数据：
>
> - 数据源：`footage`（namespace `acme`）
> - 视频：`clips/713488-assembly-shelf.mp4` · 412 MB
> - 参考标注：`gold/713488_annotation.json` · 64 phases
> - 任务：mount a wall shelf
> - 发布到：`acme`
>
> 确认无误我就创建。

Then stop and wait for an answer. This is the last point where a swapped pair of
paths or the wrong namespace costs one line instead of a failed run — and the
one moment the user can see the whole reference at once, which is the reason it
is spelled out rather than summarised as "validated ✓".

Publishing namespace is the workflow's own; the source's namespace is separate
and belongs on the line above it, so a mismatch between them is visible rather
than assumed.

### 5. Publish — invoke `workflow-publish`

Pass the target namespace through if the user named one. It validates and
pushes, then reports the canvas URL.

### 6. Hand it over

Two lines. The link, then what to do with it — nothing about how it was built:

> 已创建：https://dreamlake.ai/<ns>/workflows/<name>
>
> 打开点 **Run**，节点会随执行依次亮起；完成后 header 出现数据集链接。

No summary of the stages, no note that it came from a template, no list of what
was substituted. If they want detail they can see the graph on the page.

## What the run needs (mention only if asked, or if it fails)

The worker must be running and reachable from the queue, with `refiner`,
`dreamlake`/`dreamdb`, `dreamlake-lakeshore` installed, a Gemini key
(`GOOGLE_GENERATIVE_AI_API_KEY`), and — for hand pose — the WiLoR conda env plus
`HAND_POSE_REPO`. The DreamLake token travels with the run itself (the trigger
puts the caller's token on the queue message), so the annotation publishes as
whoever pressed Run; nothing needs to be configured on the worker for that.

Each run publishes to its **own** annotation (`<name>-<runId>`), so re-running on
new footage never revises a previous run's episodes.
