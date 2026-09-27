# Fill And Confirm

### 4. Fill the template

Copy `../reference/template.workflow.json` and substitute:

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
