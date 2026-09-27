# Publish And Handoff

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
