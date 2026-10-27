<!-- generated from https://docs.dreamlake.ai/workflows.md at unknown; do not edit -->

{/* FigWf* come from the site-wide mdxComponents map in site.config.ts —
    no import needed. */}

# Workflows

  A workflow is a typed graph of data production: ordered **stages** whose
  member nodes do the work — deterministic **compute** (UDFs), judgment-making
  **agents**, statistical **samplers**, and **control flow** — joined by typed
  data edges. You push it from the terminal and it renders as a live canvas.

> **Note:** This page is about the **WorkflowSpec** — the typed stage/node graph you push
>   as JSON and run on a canvas. Claude Code's JS orchestration scripts and Python
>   pipelines are also called workflows, share the `Workflow` server model, and
>   answer to the same CLI. If that is what you came for, start at
>   [CJS Workflows vs Python Pipelines](https://docs.dreamlake.ai/workflows/cjs-vs-python).

## How you use it

One round, from a sentence to a published dataset. Skills live in
[dreamlake-skills](https://github.com/dreamlake-ai/dreamlake-skills).

1. **Install the CLI and the three skills.**

   [Claude Code](https://docs.claude.com/en/docs/claude-code/overview) is where
   you talk to it — install that first.

   | Skill | Does |
   |---|---|
   | `video-labeling-workflow` | fills the template, drives the whole round |
   | `remote-source-check` | proves your source really holds those paths |
   | `workflow-publish` | validates and pushes, and asks which namespace |

   Install all three — the first invokes the other two by name.

   `--env prod` is worth typing. Without it `login` targets whichever
   environment is **active on that machine**, so anyone who has ever logged into
   staging lands there silently — and the failures that follow (an empty
   `source list`, a push to the wrong place) never point back at the cause.
   `dreamlake auth env list` shows which login environment is active.

   Install the standalone CLI from [the CLI guide](https://docs.dreamlake.ai/cli) and check
   `dreamlake workflow --help`. The Python `dreamlake` package provides the
   SDK; it is not the supported CLI installation path.

2. **Say what you want — it asks for the data, verifies it, shows you what it found.**

3. **It pushes — validated against the schema and the graph rules first.**

4. **Review on DreamLake — iterate, hot-reload.**

5. **Run it — nodes light up, output streams.**

6. **Review at the gate, then approve.**

   The run publishes its dataset and stops. Select the gate node: **↗ Review
   dataset** opens what was produced, **✓ Approve & continue** completes the
   run. The link stays after approval — it is the way back to what was signed
   off.

## What a spec is made of

| Part | What it is |
|---|---|
| **Stages** | phases that group and order — not barriers; execution follows the edges |
| **Nodes** | the members of a stage, from four families |
| **Edges** | typed connections between ports (`samples`, `dataset`, `metrics`, …); types must match end to end, and a `collect` port fans several streams into one input |

| Family | Does | Runs today |
|---|---|---|
| `compute` | deterministic work — filter, transcode, train, publish (any UDF) | ✅ |
| `uda` | agent judgment — labeling, review, curation | ✅ |
| `control` | human **approval** gates | ✅ approval only |
| `sampler` | statistical subset selection | ⏳ spec-only |

The schema also accepts `condition`, `switch`, `loop` and `foreach` control
types. They pass validation, then stop a run with `not supported yet` —
vocabulary to design against, not behaviour to rely on.

A `uda` node declares the tools and **`permissions`** its agent may use, so
judgment never runs on raw credentials. Intermediate results stay in the
worker's run directory; what reaches DreamLake is what a `publish` node
writes.

## Version it

Pushes never overwrite. Each one appends an immutable version, and the
**spec picker** on the workflow page pins the canvas to any of them —
pick the latest to resume following pushes.

Editing a node's settings on the canvas and pressing **Apply** does the same
thing: the edited spec is validated and appended as the next version. Nothing
is edited in place, so a run always names the version it executed.

## Next steps

    The spec graph, Claude Code's JS orchestration scripts, and Python
    pipelines side by side — and the seven places where one of them does not
    exist yet.

    The full vocabulary — every family's inputs, outputs, and configuration,
    rendered with the real components.

    The grant registry uda nodes draw from — domains, verbs, and scopes.

    `dreamlake workflow push` and `list` — flags, namespaces, versioning.

## Project attachment access

Explicit user/team Project READ grants spec-content access to live Workflow
attachments; WRITE/ADMIN permit supported spec updates. Public Project
visibility does not itself authorize spec-content reads. The existing public
Workflow catalog metadata remains public under its independent policy.

Current grants apply to current and later attachments; detaching or revoking
removes only the inherited contribution. Project content grants do not authorize
workflow execution, host/secret access, catalog management or ownership transfer.
Delegated uploads require resource-scoped temporary credentials; custom-S3
static identities and unscoped STS fallback return
`DELEGATED_UPLOAD_UNSUPPORTED` (403). A Workflow owned by another namespace
attaches only through its owner's [cross-namespace mount grant](https://docs.dreamlake.ai/api/external-mounts),
at READ at most; it never authorizes editing or running the Workflow.

The Project-sharing backend and Web update are released. CLI Project commands
require 0.62.0 or later; Python Project support requires SDK 0.29.0 or later. See the
[Project resource access contract](https://docs.dreamlake.ai/dev/notes/project-resource-sharing).

The [whole-Project and owned-Notes transfer](https://docs.dreamlake.ai/dev/notes/project-note-transfer)
supports Project, ordinary Project files/images/videos and owned Notes.
A mount/reference of this resource blocks
the entire transfer rather than silently excluding it. Its existing independent
sharing and released Project-derived content access remain available.
