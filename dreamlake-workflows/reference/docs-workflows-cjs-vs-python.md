<!-- generated from https://docs.dreamlake.ai/workflows/cjs-vs-python.md at unknown; do not edit -->

# CJS Workflows vs Python Pipelines

  A CJS workflow and a Python pipeline are not two dialects of one idea. They
  share a noun and almost nothing else: one discovers its shape by running,
  the other is read off the source without running. This page puts them side by
  side across eleven axes and then names, honestly, the seven places where one
  of the two does not exist yet.

## Part 1 — the three artifacts

Three separate things in this system are called a workflow. Two of them answer
to `dreamlake workflow`.

| | Artifact | Authored as | Stored as | Executed by |
|---|---|---|---|---|
| **W1** | CJS workflow — a Claude Code JS orchestration script | a `.js` exporting a `meta` literal plus `phase()` / `agent()` / `parallel()` | `Workflow.script` + `WorkflowVersion`, plus run traces | the Claude Code CLI's Workflow tool, locally |
| **W2** | WorkflowSpec v1 — the typed stage/node graph | hand- or agent-authored JSON | a DreamDB dataset; the server holds only `specVersion` / `specMeta` | a `workflow_runtime` worker off a Redis stream |
| **P** | Python pipeline | `.py` with `@dl.pipeline` + `@ls.udf` | `Pipeline.sourceCode` + `PipelineVersion.graph` | nothing — the graph is derived, never run |

W2 is the artifact the [Workflows guide](docs-workflows.md) and the
[node types reference](docs-workflows-node-types.md) describe. This page is about the
other two: **W1 against P**, with W2 present only where the comparison needs it.

### Two facts that make this genuinely confusing

**One CLI verb, two file formats.** `dreamlake workflow create` and
`dreamlake workflow update` take `--file <script.js>` and parse a `meta` literal
out of JavaScript. `dreamlake workflow push` takes a WorkflowSpec v1 JSON file
and writes it to DreamDB. Same command group, same workflow name, entirely
different artifact on each side of the flag.

**One record, two version counters.** The `Workflow` model carries both:

- `currentVersionHash` — a twelve-hex hash pointing at a `WorkflowVersion`, and
  a `WorkflowVersion` holds a `script`. That is the **JS** history.
- `specVersion` — a monotonic integer, the latest push counter into the
  workflow's DreamDB dataset, alongside `specMeta`
  (`{ description, stageCount, nodeCount, edgeCount }`). That is the **JSON**
  history.

Nothing keeps them in sync. A workflow can be at `currentVersionHash` `a1b2…`
and `specVersion` 7 with no relationship whatsoever between the two, because
they were written by two different commands describing two different artifacts.

**And a third `push`.** `dreamlake workflow push` also exists in the Python CLI,
with the same `<file> [--name]` shape and byte-identical output — both CLIs
re-serialize the spec at two-space indent so they append to the same dataset.
The TypeScript CLI acknowledges the split in its own error text: its hidden
`workflow append-local` subcommand answers
`no_writer — append-local needs the canonical Python writer (pip install
dreamlake); the TS CLI has no DreamDB writer`. The Python CLI stays the
canonical DreamDB writer, and dreamlake-server spawns it by name for spec
applies.

---

## Part 2 — eleven axes

### 0. What the name means

**W1.** One of three artifacts, and the least documented of them. `dreamlake
workflow` covers W1 (`create`, `update`, `show`, `push-run`, `watch-run`) and W2
(`push`) from the same command group, so the verb alone never tells you which
one you are operating on.

**P.** One artifact. `dreamlake pipeline` means exactly one thing: a Python file
with a `@dl.pipeline` entry point.

### 1. Where the graph comes from

**W1 — a runtime trace.** There is no static DAG for a CJS workflow. Phases and
agents are captured as the run executes; the renderable graph is derived from a
run's `trace` (`phases` + `agents`). Before the first run, only the phase
skeleton exists, built from the current version's `meta.phases`. With no version
at all there is nothing to render. **You cannot know the shape of a CJS workflow
without running it.**

**P — static derivation from source.** The tracer walks the Python AST. It never
imports the module and never executes a line, which is why every UDF body in the
canonical examples is a literal `...` and traces perfectly well. The graph is a
property of the text, available before anything has ever run — and, as Part 4
records, that is just as well, since nothing runs it.

### 2. The unit of work

**W1.** An agent call:

```js
await agent(promptString, { label, phase, schema, effort })
```

The prompt is a string. The options carry the display label, the phase the agent
belongs to, an output schema, and an effort level.

**P.** A decorated function:

```python
@ls.udf(kind="review")
def review_boxes(labels) -> Mask["R", "N"]:
    ...
```

The parameters are the node's input ports; the return annotation is its output
schema.

### 3. Typing of the connection

**W1 — none.** The prompt string *is* the edge. Whatever one agent produced
reaches the next one only because the script interpolated it into the next
prompt. The `schema` option types an agent's **output**, not the connection: it
constrains what that one agent returns and says nothing about who consumes it or
whether the consumer expects that shape.

**P — typed on both ends.** The tracer reads input ports off the function's
parameter list, gives every UDF that returns something exactly **one** output
port (`out`), and reads the return annotation's names into `columns` —
`Tuple["boxes", "classes", "confidence"]` becomes three column names on the
node. A sink UDF with no return annotation gets no output port at all. Every
edge additionally carries `kind: "data" | "mask"`.

### 4. Fan-out

**W1.** An array of thunks:

```js
const findings = await parallel(
  targets.map((t) => () => agent(`Scout ${t} and report`, { label: t, phase: 0 })),
)
```

`targets` is an ordinary JavaScript array, usually parsed out of a previous
agent's output. **The width is computed at runtime.** Nothing before the run
knows whether this is three agents or thirty.

**P.** Call the UDF more than once, or write a comprehension. Each call mints a
fresh node id from the function name — `detect_objects`, then
`detect_objects_2`, then `detect_objects_3`. This is static, and it has a hard
edge: **loops never unroll.** The tracer walks a `for` body exactly once, so

```python
for i in range(3):
    x = refine(x)
```

produces **one** `refine` node, not three. Three calls written out give three
nodes; three iterations of one call give one.

### 5. Fan-in

**W1.** Ordinary array handling, then string concatenation into the next prompt:

```js
const notes = findings.filter(Boolean).map((f) => f.summary).join('\n\n')
await agent(`Synthesize these scout reports:\n\n${notes}`, { phase: 1 })
```

The join is the fan-in. There is no merge construct — the next agent simply
receives a longer prompt.

**P.** Pass several results into one UDF, and one edge per argument lands on that
node. The tracer then labels it: an untagged UDF whose **data** fan-in comes from
two or more distinct non-source nodes is re-kinded `merge`. Only `data` edges
count, and inputs drawn from a `source` node are excluded, so a side input such
as a prompt table does not accidentally promote a stage to a merge.

### 6. State between steps

**W1.** Ordinary JavaScript variables in one module scope. The script is a
normal ES module: `const` bindings hold agent results, and they reach the next
step as **interpolated prompt text**. There is no store, no artifact registry,
and no way to inspect an intermediate other than reading the run trace.

**P — provenance sets.** The tracer tracks, for every Python local, the set of
nodes its data descends from, each tagged `data` or `mask`. When both tags reach
the same node, **`data` dominates `mask`**. Consuming a value in mask position
downgrades its whole provenance. Method calls (`review.all(axis=0)`), subscripts
(`labels[consensus]`) and operators (`~consensus`) **pass provenance through
without creating a node** — they are how a value is reshaped, not a stage of
work.

### 7. Control flow

**W1.** Plain JavaScript `if`. It is untracked and invisible to the trace: the
trace records phases and agents, so a branch that skips an `agent()` call simply
leaves that agent out of the trace, and a branch that fires no `phase()` leaves
no mark at all. You cannot read a CJS workflow's branching structure off its
graph, because the graph is only what happened.

**P.** The tracer walks **both** branches of an `if/else` — an intentional
over-approximation, so every path's nodes appear. A variable assigned in both
branches gets the **union** of the two provenance sets, so a downstream node
connects to both and nothing dangles. The `else` branch walks from the pre-`if`
bindings rather than the `if` branch's, because the branches are independent.
And **the condition is discarded**: `stmt.test` is evaluated in mask role for its
provenance only. The graph shows what a branch might touch, never which way it
went.

### 8. Failure

**W1.** A failed agent yields a falsy entry rather than throwing, which is why
`.filter(Boolean)` is idiomatic on every `parallel` result. That idiom silently
swallows the failure. Partial failure is entirely the calling script's problem
to notice and report; nothing in the runtime stops the workflow because two of
five scouts came back empty.

**P.** The opposite discipline. Any undecorated call inside a `@dl.pipeline`
**raises at trace time**:

```
pipeline calls undecorated function 'to_dataset' — every function called in a
@dl.pipeline must be a @ls.udf / @dl.node (wrap framework helpers like
to_dataset/requeue in a udf)
```

No hidden helpers, no silent passthrough. The one exemption is a `for` loop's
*iterator* expression (`batch(src, n=64)`, `stream(…)`), evaluated leniently so
a structural helper there does not raise; the loop **body** is strict again.

### 9. Execution

**W1.** The Claude Code CLI's Workflow tool runs the script locally and rewrites
a `wf_<runId>.json` run file under the session's `workflows/` directory as it
goes. `dreamlake workflow push-run` and `watch-run` reduce that file and PUT it
to the server, which is how a local run becomes a visible run.

**P.** Nothing executes it. `dreamlake pipeline create --file` stores the source
and the derived graph; that is the entire lifecycle. There is no runner, no
scheduler and no queue on the pipeline side.

### 10. Storage, versioning, renderer

**W1.** `Workflow` (identity, metadata) → `WorkflowVersion` (an immutable
snapshot of `script` plus the parsed `meta`) → `WorkflowRun` (a mutable trace
snapshot, upserted while the run progresses). Rendered as a metro map: phase
bands with agent cards strung along a spine.

**P.** `Pipeline` → `PipelineVersion` (`sourceCode` plus the derived `graph`) →
`NodeState` for runtime status. Rendered by uikit's `` as node
cards joined by typed edges, solid for `data` and dashed for `mask`.

Both version immutably, and both mint the same kind of identifier: a
**twelve-character hash**, `SHA256(id:timestamp:nonce).slice(0, 12)`.

---

## Two real samples

### W1 — a CJS workflow

The `meta` literal and its storage contract are defined by dreamlake-server and
are exact. The `phase` / `agent` / `parallel` bindings come from the Claude Code
CLI's Workflow tool, which is not part of this repository — treat the body below
as the shape of the fan-out, not as a normative signature.

```js file="scout.js"
export const meta = {
  name: 'workflow-feature-scout',
  description: 'Map the five subsystems a feature touches, then synthesize.',
  phases: [
    { title: 'Scout', detail: '5 parallel readers' },
    { title: 'Synthesize', detail: 'one writer' },
  ],
}

export default async function run({ phase, agent, parallel }) {
  await phase(0)
  const targets = ['server', 'cli', 'uikit', 'docs', 'schema']
  const findings = await parallel(
    targets.map((t) => () => agent(`Read the ${t} and report what it owns.`, {
      label: t,
      phase: 0,
      effort: 'medium',
    })),
  )

  await phase(1)
  const notes = findings.filter(Boolean).map((f) => f.summary).join('\n\n')
  return agent(`Synthesize these scout reports:\n\n${notes}`, { phase: 1 })
}
```

> **Warning:** Both the Studio parser and dreamlake-server lift `meta` out of the script text
>   **without executing it** — a balanced-brace scan from the first `{` after
>   `export const meta`, then a constrained recursive-descent read of objects,
>   arrays, strings, numbers, `true` / `false` / `null`, comments and trailing
>   commas. Identifiers, calls and arrow functions are treated as unparseable and
>   skipped, never evaluated. So `name: WORKFLOW_NAME` does not resolve to a
>   string — it resolves to nothing, and the server returns **`400
>   invalid_script`** because `meta.name` must be a non-empty string. The same
>   applies to `meta.description`. `phases` is tolerant by comparison: it defaults
>   to `[]`, non-object entries and entries without a string `title` are dropped
>   silently, and `detail` is kept only when it is a string.

### P — a Python pipeline

```python file="image_object_annotation.py"
import dreamlake as dl
import lakeshore as ls
from dreamlake import batch, requeue, to_dataset
from lakeshore.types import Mask, Tensor, Tuple


@ls.udf(kind="source")
def load_images() -> Tuple["images"]:
    """Pull the batch of images to annotate."""
    ...


@ls.udf
def detect_objects(images: Tensor["N", "H", "W", 3]) -> Tuple["boxes", "classes", "confidence"]:
    ...


@ls.udf(kind="review")
def review_boxes(labels) -> Mask["R", "N"]:
    """R reviewers pass/fail each box."""
    ...


@ls.udf(kind="sink")
def save_dataset(rows):
    to_dataset(rows)


@ls.udf(kind="sink")
def rework(rows):
    requeue(rows)


@dl.pipeline
def image_object_annotation():
    src = load_images()
    for items in batch(src, n=64):
        labels    = detect_objects(items.images)
        review    = review_boxes(labels)

        consensus = review.all(axis=0)       # method call: provenance passes through
        save_dataset(labels[consensus])      # subscript: the mask gate
        rework(labels[~consensus])           # unary op: still the same provenance
```

Read the last three lines against axis 6. `review.all(axis=0)` and `~consensus`
create no nodes — they carry `review_boxes`'s provenance forward with a `mask`
tag. `labels[consensus]` mixes a `data` provenance (the subscripted value) with a
`mask` provenance (the slice), so `save_dataset` ends up with a solid edge from
`detect_objects` and a dashed one from `review_boxes`. That is the whole of
"tapping data off the main stream" in the pipeline model — no sampler function
is involved, because there isn't one.

---

## Part 3 — the CLI, both sides

Neither command group is documented at [/cli](https://docs.dreamlake.ai/cli) today, so both are recorded
here.

```bash
# W1 — the JavaScript orchestration script
dreamlake workflow create <name> --file <script.js> [--message <text>]
dreamlake workflow update <name> --file <script.js> [--message <text>]
dreamlake workflow show   <name>
dreamlake workflow list

# W1 — run traces, pushed from the local wf_*.json the Workflow tool writes
dreamlake workflow push-run  <name> <wf_*.json>
dreamlake workflow watch-run <name> <wf_*.json> [--interval 5]

# W2 — a WorkflowSpec v1 JSON, NOT the JS
dreamlake workflow push <spec.json> [--name <name>]

# P — the Python pipeline
dreamlake pipeline create <name> --file <pipeline.py>
dreamlake pipeline update <name> --file <pipeline.py>
dreamlake pipeline version list <name>
dreamlake pipeline version show <name> <hash>
dreamlake pipeline node    list <name> <hash>
dreamlake pipeline node    show <name> <hash> <nodeId>
```

Two details worth knowing before you use them.

**`workflow push` takes the file positionally, not the name.** The workflow name
comes from the spec's own `name` field unless you override it with `--name`.
This differs from every other verb in the group, which takes `<name>` first —
another consequence of `push` operating on a different artifact from its
siblings.

**`watch-run` is designed to be backgrounded** alongside the Workflow tool. It
polls the local run file and pushes a trace snapshot on each tick until the file
leaves `running`, then pushes once more so the terminal state lands. Every push
is size-budgeted below the server's body limit and degrades deterministically —
free-text previews are capped first, then log lines, then `result` is replaced
with a size marker. The status, the phase/agent skeleton and the run totals
always survive, because those are what the run page renders. If the terminal
push were dropped, the server-side run would never leave `running` and the
detail page would poll it forever.

---

## Part 4 — the honest gaps

This is the part that makes the page worth writing. Everything above describes
what the two systems *mean*. This describes what is not there.

> **Warning:** The `.py` files above trace correctly and will not import. The shipped
>   `dreamlake` package exports no `pipeline`, no `node`, no `batch`, no `stream`,
>   no `to_dataset` and no `requeue`. The real `udf` signature is
>   `udf(fn=None, *, queue=None, transport="auto", config=None)` —
>   **no `kind=`**. `kind` is notation the tracer reads out of the decorator's
>   keyword arguments; the runtime never sees it. `lakeshore.types` does not exist,
>   so `Mask`, `Tensor` and the string-literal `Tuple` are annotations with no
>   implementation behind them. And the canonical import for the real package is
>   `import dreamlake.lakeshore as dls`, not `import lakeshore as ls`.
>
>   The conclusion follows directly: **those `.py` files are a specification format
>   that happens to be Python syntax.** They work precisely because the tracer
>   parses text and never imports a module. Do not read them as runnable code.

> **Warning:** dreamlake-server calls an external tracer at `PIPELINE_PARSER_URL/trace`. When
>   that variable is unset it falls back to `parsePython()`, an in-process mock
>   that matches only a **bare `@ls.udf` line** — not `@ls.udf(kind="source")` —
>   infers `kind` from whether the function name starts with `tr_`, and returns
>   `inputs: []` and `edges: []`. That is an empty graph with a few disconnected
>   nodes in it. Real graphs require the external `dl_trace` service; without it,
>   a pushed pipeline renders as unconnected cards.

> **Warning:** There is no way to see a CJS workflow's shape without running it, and
>   `meta.phases` does not substitute for one. It is a hand-written label list
>   with **no relationship to the `agent()` calls the script actually makes** —
>   nothing validates that a phase exists for every `phase: n` an agent declares,
>   or that a declared phase is ever entered. It is display metadata that happens
>   to be ordered.

> **Warning:** The edge type system documented at [/workflows/node-types](docs-workflows-node-types.md)
>   — typed ports, `samples` / `table` / `dataset` / `model` / `metrics`, branch
>   ports, collect ports — applies to **W2 only**. None of it exists for a JS
>   script, where the only connection between two steps is a string that one of
>   them wrote into the other's prompt.

> **Warning:** No `uda`, no permission grants, no `tools` declaration. A "review" step in a
>   pipeline is a UDF with `kind="review"` — an ordinary function node with a
>   cosmetic label, which the renderer draws differently and the tracer treats
>   identically to a transform. The whole `uda` concept, and the grant taxonomy at
>   [/workflows/agent-permissions](docs-workflows-agent-permissions.md), lives only in W2.

> **Warning:** Neither a CJS script nor a Python pipeline has one. W2 has a real
>   `approval` control node and a matching server endpoint
>   (`POST …/runs/:runId/approve`, which resumes from a checkpoint against the
>   same spec version the run started on). A CJS workflow that needs a human in
>   the loop has to arrange it in JavaScript; a Python pipeline has nowhere to put
>   it, because nothing executes the pipeline in the first place.

> **Warning:** dreamlake-server enqueues a run onto a Redis stream: `XADD` to `WF_QUEUE`,
>   defaulting to `labeling_task`, carrying the full spec inline so the worker
>   never has to read DreamDB. The comment in the route names a `workflow_runtime`
>   worker as the consumer. **No such consumer was found anywhere in this
>   checkout** — not the string `workflow_runtime`, not a reader of
>   `labeling_task`. It may be a separately deployed service. Until that is
>   confirmed, W2's "push it and it runs" story is unproven, and this page will not
>   assert it either way.

---

## Related

    The W2 vocabulary — every node family's inputs, outputs and configuration,
    and the artifact type system on every edge.

    The grant registry uda nodes draw from — domains, verbs, and scopes. W2 only.

    The Python authoring vocabulary, one construct per page, each with a live
    node view.

    The rest of the `dreamlake` command surface.
