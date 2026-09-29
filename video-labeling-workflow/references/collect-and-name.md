# Collect And Name

## Talk like a product, not like a build system

Everything below the next heading is **internal**. Do not narrate it. The user
should never hear "fixed", "template", "instantiate", "hard-coded", "pipeline
shape", or a stage-by-stage recital of the graph — that reads as a canned script
rather than a capability, and this is often shown to an audience.

Say **workflow**, never "pipeline". Keep every message short. Announce nothing;
just ask for what you need, then report the link.

Internally: the graph is not yours to design. Fill
`../reference/template.workflow.json` and change nothing else. Do not route this
through `workflow-generator` — that skill designs new graphs from a description,
and is only appropriate when the user wants something this workflow does not do.

## The workflow

Five stages, nine nodes — `../reference/template.workflow.json`:

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
