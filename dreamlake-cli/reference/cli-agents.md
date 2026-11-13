<!-- generated from https://cli.dreamlake.ai/agents.md at 0.125.0 b8ca5e1; do not edit -->

# Agents

## Chat with the built-in agent

Available in CLI 0.119.0 and later. `dl agent` is an alias of `dl agents`.
Use `chat` for the same server-owned agent used in the browser; definition
commands such as `create`, `list` and `edit` keep their existing behavior.
`dl sessions chat` uses the same handler and options.

```bash cli-help="agents chat"
# Interactive conversation; /exit or Ctrl+D leaves it.
dl agent chat
# One request, with streamed answer and tool receipts.
dl agent chat "Search my workspace for rope assets"
# Continue the conversation ID printed by a previous turn or the browser URL's s parameter.
dl agent chat --conversation <id> "Read the first result"
# One UTF-8 request from a file or pipe, with JSON events on stdout.
dl agent chat --file request.txt --json
printf '%s' 'Search my workspace for rope assets' | dl agent chat --json
# The request file identifies the Source namespace/ID, prefix and relative path.
# Allow changes to that explicit target, matching the browser tool-changes toggle.
dl agent chat --extensions --tools-write --file source-request.txt --json
```

Each positional message, file, or complete stdin stream is **one turn**. Without
one, a terminal opens a conversation loop. `--json` requires one-turn input and
emits newline-delimited events, including `context` (with `sessionId` and
`turnId`), `delta`, `tool`, `done`, or `error`. Stream failures exit nonzero;
a connection ending before `done` is a failure. Inspect the saved conversation
before retrying a potentially completed write. Ctrl+C interrupts the local
request; it does not roll back server work.

Prompts, skills, search and resource permissions come from the server's
existing agent configuration. This command does not load local
skills or create a separate harness. `--extensions` enables personal extensions
and MCP discovery when available on the server, matching a browser that
advertises this capability. It is opt-in here to preserve existing CLI defaults;
inspect the `context.extensions` JSON event to verify actual availability.
This is separate from the server's built-in skill bundle, which does not require
the flag. Browser-executed external actions still need a browser executor.
`--namespace <slug>` explicitly selects the
agent namespace; `--page <pathname>` supplies page context (default `/`). Neither
option grants access. Without `--namespace`, the server resolves conversation
and page context as it does for existing `sessions chat` requests.

Writes are opt-in: `--tools-write` enables the browser's tool-changes capability;
`--notes-write` and `--control` retain the narrower memo and session capabilities.
File-tool availability depends on the deployed backend. The CLI does not
implement Source file tools itself or grant a local filesystem to the agent.
Browser-only layout/cache actions require an active browser executor; passing a
page path does not supply one.

### Select the file target explicitly

Editing a Project and editing files in a Source are separate operations with
separate APIs. Attaching or linking a Source to a Project does **not** select
that Source as a default writable target, even if it is the only attached
Source. `--namespace` and `--page` are conversation context, not a file endpoint.

For a Source file request, identify the Source namespace and ID, prefix, and
relative path in the request. For example, save this as `source-request.txt`,
replacing `TEST_SOURCE_ID` with the ID of a disposable test Source you own:

```text
Use Source file operations on namespace marvin, Source ID TEST_SOURCE_ID.
Under prefix workspaces/v1/agent-chat-test, create scene/manifest.json with
exact content {} followed by a newline, using create-only semantics.
If the path already exists, read it without overwriting it. Read back the file
and report its Source ID, prefix, relative path, exact content and revision.
Do not edit Project settings, infer a target from Project attachments,
create a Source, change bindings, or substitute Memo attachments or Project files.
If these Source tools are unavailable, report that and make no substitute write.
```

Use the same resolved request text in the CLI and browser for comparison.
For direct deterministic Source file operations, see [Source text files](cli-sources.md).
A Project-targeted request must instead name the Project and its own supported
operation; it is not a fallback for a failed Source request.

Continue in the browser by opening the same account/page with `?s=<conversation-id>`
(or adding `&s=...` to an existing query). Continue back in the CLI using
`--conversation`. Inspect durable results with
`dl sessions tool-calls <conversation-id> --json`; use its `nextCursor` with
`--cursor` for later pages.

## Agent definitions

An agent is a **prompt with a name**. Nothing else is required, and an agent
with nothing else is the normal case, not a degraded one.

```bash file="terminal"
dl agents create triage --prompt 'You triage failed runs. Read the
terminal event first, classify the failure, quote the line that decided it.'
```

An agent is a `Runnable` of kind `agent`, so everything on
[Declaration collections](cli-collections.md) applies to it — versions, `--if-exists`,
the 409 semantics. This group exists because authoring a prompt through
`declare` and a JSON file is miserable.

Creating an agent stores its definition; it does not create or run a session.
Use `--runtime builtin-v1` for the built-in DreamLake assistant. The default
continues to declare an external Claude agent.

## Built-in agents and project filing

Available in CLI 0.104.0 and later with the agent resource API. An agent is a
first-class runnable. Its
instructions can be inline Markdown, or one main Memo plus optional skill Memos
and folders.
Projects are filed atomically with creation; a failed filing creates no orphan.

```bash cli-help="agents create"
dl agents create reviewer --runtime builtin-v1 \
  --prompt 'Read the evidence and summarize it with citations.' \
  --tools dreamlake_notes_read --project dreamlake --namespace fortyfive

# Existing Memo/folder IDs; references remain live and are authorized per caller.
dl agents create researcher --instruction-note "$MAIN_MEMO_ID" \
  --skill-note "$SKILL_MEMO_ID" --skill-folder "$SKILLS_FOLDER_ID" \
  --project dreamlake --namespace fortyfive
```

Do not combine `--instruction-note` with inline/file/stdin instructions. Built-in
agents accept DreamLake tool names and typed `--arg` declarations. For example,
`--prompt 'Review {{topic}}' --arg 'topic:string!'` declares a required string.
Built-in definitions allow up to 20 unique arguments and 80 tools; enum arguments
allow up to 30 string values. Inline files contain plain Markdown; Claude
frontmatter is not parsed in built-in mode. External
Claude permissions, models and machine options do not apply to this runtime.
Open the returned agent link to edit its Description and Spec in the right panel.

```ts
import { createClient } from '@dreamlake/dreamlake-cli/api'

// Use the client construction documented in the TypeScript API guide.
const client = createClient({ remote: 'https://api.dreamlake.ai', token: process.env.DREAMLAKE_API_KEY! })
const agents = client.runnables('fortyfive')
const agent = await agents.create({
  name: 'Researcher', module: 'agents', qualname: 'researcher', kind: 'agent',
  content: { instructionNoteId: process.env.MAIN_MEMO_ID!, skills: [
    { kind: 'note', id: process.env.SKILL_MEMO_ID! },
  ] },
  projects: ['dreamlake'],
  metadata: { agent: { runtime: 'builtin-v1', tools: ['dreamlake_notes_read'] } },
})
await agents.update(agent.id, { description: 'Summarize evidence', expectedUpdatedAt: agent.updatedAt })
await agents.archive(agent.id)
await agents.restore(agent.id)
```

Archive hides a runnable from ordinary lists; pass `includeArchived: true` to
`list` to find it. Restore is explicit. Delete removes the definition from live
lists and unfiles its project mounts. Conditional edits return a conflict if
`expectedUpdatedAt` is stale.

## Browse, inspect, and save external Claude agents

The agent management commands below are available in CLI 0.104.0 and later.

```bash cli-help="agents list"
dl agents list --namespace my-workspace
# Stable text, even in a terminal; redirected output also defaults to text.
dl agents list --namespace my-workspace --plain
# Prefixes match the beginning of a scoped agent name or registry ID.
dl agents list --prefix my_repo. --project research
```

On a TTY, use the arrow keys to select an agent and Enter to inspect or edit it.
Choose **Edit prompt** or **Edit parameters and projects (YAML)** to open your
configured terminal editor, then choose **Save** to write both together.
Leaving with **Back / discard changes** does not save. Ctrl+C exits.
The TUI requires both stdin and stdout to be terminals; pipes print a text table.
`--json` explicitly selects JSON and bypasses the TUI.

```bash cli-help="agents show"
dl agents show my_repo.tri --namespace my-workspace
```

A unique name or ID prefix identifies an agent. Exact matches take precedence;
ambiguous prefixes fail with the matching names. Show prints the complete prompt
and parameters. Use `--json` for the registry record.

```bash cli-help="agents edit"
dl agents edit my_repo.tri --namespace my-workspace
# Browser form: follow the localhost URL printed by the command.
dl agents edit my_repo.tri --namespace my-workspace --web
```

The browser form has separate prompt and YAML parameter fields and a **Save**
button. Keep the command running while editing; Ctrl+C closes its local server.
It binds only to `127.0.0.1`, uses a random session URL, and keeps registry
credentials in the CLI process. On a remote machine, localhost refers to that
machine; forward its printed port explicitly if you need to use a local browser.

Save validates prompt placeholders, typed arguments, permissions, project
references, and credential-shaped fields before writing. Other registry metadata
is preserved. Errors leave the form draft available. An observed concurrent edit
is refused: reopen the agent before saving. The existing registry PATCH has no
atomic compare-and-swap contract, so the pre-save check cannot prevent a change
made in the interval between that check and the write.

These commands update the mutable agent declaration; Save does not execute an
agent, register an immutable version, or publish it.

## Project affiliation

Affiliate an agent with one or more existing projects in its namespace:

```bash
dl agents create triage --scope my_repo \
  --project research --project operations --prompt 'Triage failed runs.'
dl agents list --project research --plain
```

Agent frontmatter and the parameter editor accept the same list:

```yaml
projects: [research, operations]
arguments:
  - { name: target, type: string, required: true }
```

Creation and Save resolve each project with your existing namespace identity.
Project affiliation is stored as project slug references in `metadata.agent.projects`.
It is used for organization and list filtering; it does not change registry
ownership, project access, or create a node in the project's file tree. This
paragraph describes external Claude affiliation; built-in agents created with
`--runtime builtin-v1 --project` use actual project filings instead. If an
affiliated project is renamed, update the stored reference in the agent editor. Remove an affiliation
by removing its slug, or set `projects: []` to remove all.

## Three ways to write the prompt

### A heredoc

Quote the delimiter — `<<'AGENT'`, not `<<AGENT` — or the shell expands
`$VARIABLES` and backticks inside your prose before the CLI ever sees it.

```bash file="terminal"
dl agents create triage --file - <<'AGENT'
# Run triage

You triage failed invocations. Read the terminal event before the logs — it
says whether the worker died, the container exited, or the body raised, and
those three send you to different places.

Quote the single log line that decided your classification. One line.
AGENT
```

That file has no frontmatter and does not need any.

### A Claude agent file

Add frontmatter when you want to constrain the agent or give it a machine.
`--file <path>` reads one; `--file -` reads stdin.

```yaml file="agent.md"
---
name: run-triage
description: Triages a failed invocation and proposes the smallest fix.
tools: [Read, Grep, Bash]
model: claude-opus-5
permissions:
  allow: [Read(./runs/**), Bash(lakeshore logs:*)]
  deny:  [Read(./.env), Bash(rm:*)]
run_config: gpu-a10g
arguments:
  - { name: invocation_id, type: string, required: true }
---

Triage invocation {{ invocation_id }}. Read its terminal event first.
```

### `$EDITOR`, on a scaffold

```bash file="terminal"
dl agents create run-triage --edit
```

Opens a filled-in scaffold and declares whatever you save.

## The frontmatter fields

The file format is **Claude's agent file** — the same bytes work in
`.claude/agents/` — plus fields this platform needs. Every field is optional.

| Field | Type | Whose | Meaning |
| --- | --- | --- | --- |
| `name` | string | Claude | the agent's name. The positional argument or `--name` wins over it |
| `description` | string | Claude | one line on **when** to use this agent |
| `tools` | list | Claude | e.g. `[Read, Grep, Bash]`. Omit to inherit all |
| `model` | string | Claude | a model id (`claude-opus-5`) or an alias: `opus`, `sonnet`, `haiku`, `inherit` |
| `permissions.allow` / `ask` / `deny` | list of rules | Claude | `Tool` or `Tool(specifier)`, e.g. `Read(./runs/**)`, `Bash(npm run test:*)` |
| `permissions.additionalDirectories` | list of paths | Claude | extra roots the agent may read and write |
| `permissions.defaultMode` | string | Claude | what happens to a call no rule matches: `default`, `acceptEdits`, `plan`, `bypassPermissions` |
| `run_config` | string | Lakeshore | names an existing `RunConfig` — the machine it lands on |
| `queue` | string | Lakeshore | the queue to submit on |
| `grants` | list | Lakeshore | `domain.resource.verb` resource grants |
| `arguments` | list | Lakeshore | typed prompt arguments — see below |
| `projects` | list of project slugs | Lakeshore | project affiliation in the agent namespace; does not grant access |
| `channel` | mapping | Lakeshore | `{ kind, target? }`, e.g. `{ kind: http-sse, target: /v1/agents/triage/stream }` |

An `arguments` entry is
`{ name, type, required?, default?, values?, description? }`, where `type` is
one of `string | integer | number | boolean | enum` and `values` lists an
enum's fixed set. `required: true` and a `default` on the same argument are
rejected — they contradict each other.

That is the whole vocabulary. There is no thinking-level or effort field —
`model` is the only model-shaped knob, matching Claude's format — and no
placement field beyond `run_config`, because placement is derived from the
`RunConfig`'s host key.

Three rules about keys the table does not list:

- An unknown key **under `permissions`** is refused. The merge is an
  allowlist, and an allowlist that silently drops a `permissions.allowed`
  typo declares nothing and says nothing.
- An unknown key **at the top level** is ignored, so a Claude agent file
  carrying fields this platform does not read still declares cleanly.
- A **credential-shaped key anywhere** — `token`, `secret`, `api_key`,
  `authorization`, … — is refused before any merge, ignored or not. See the
  callout at the bottom for why.

When a field appears in both the file and a flag, the flag wins for `model`,
`run_config`, `queue`, `defaultMode` — and for `tools`, where `--tools`
replaces the file's list wholesale. Rule lists (`allow`, `ask`, `deny`,
`grants`, `additionalDirectories`) concatenate, file first then flags; a
`--arg` replaces a file argument of the same name.

## Or stay on one line

Every property has a flag.

```bash file="terminal"
dl agents create run-triage \
  --description 'Triages a failed invocation.' \
  --tools Read,Grep,Bash --model claude-opus-5 \
  --allow 'Read(./runs/**)' --deny 'Bash(rm:*)' \
  --run-config gpu-a10g --queue gpu-a10g \
  --arg 'invocation_id:string!' \
  --arg 'max_log_lines:integer=200' \
  --prompt 'Triage {{ invocation_id }}. Read at most {{ max_log_lines }} lines.'
```

Quote every rule and every `--arg`. `Bash(npm run test:*)` contains a glob and
parentheses; unquoted, the shell gets there first.

| Flag | Meaning |
| --- | --- |
| `--name <kebab>` | the agent's name, if not in the file or the positional argument |
| `--description <text>` | one line on **when** to use this agent |
| `--tools <csv>` | e.g. `Read,Grep,Glob,Bash`. Omit to inherit all |
| `--model <id>` | e.g. `claude-opus-5`, or an alias: `opus`, `sonnet`, `haiku`, `inherit` |
| `--allow` / `--ask` / `--deny <rule>` | permission rules, repeatable |
| `--permission-mode <mode>` | what happens to a call no rule matches: `default`, `acceptEdits`, `plan`, `bypassPermissions` |
| `--add-dir <path>` | extra root the agent may read and write, repeatable |
| `--run-config <name>` | attach a `RunConfig` — the machine it lands on |
| `--queue <name>` | the queue to submit on |
| `--grant <string>` | a `domain.resource.verb` resource grant, repeatable |
| `--arg <spec>` | a typed prompt argument, repeatable |
| `--channel <kind[:target]>` | e.g. `http-sse:/v1/agents/triage/stream` |
| `--scope` / `--qualname` | override the stored scope / leaf name |
| `--dry-run` | resolve, validate and print — send no request at all |
| `--if-exists <mode>` | what a 409 means: `fail` (default) or `ok` |
| `--json` | emit JSON instead of prose |

## Typed arguments

A `{{ placeholder }}` in the prompt **must** have a matching `--arg` or the
create is refused. A typo'd `{{ invocaton_id }}` must never reach a model as
literal braces.

```text file="the mini-syntax"
invocation_id:string!                               required
max_log_lines:integer=200                           defaulted
verdict_detail:enum(terse|normal|forensic)=normal    fixed set
dry_run:boolean=false
```

`!` and `=` are mutually exclusive: required plus a default are two statements
that contradict each other.

## Naming

An agent has a name, not a module path — it is not a UDF and nothing here asks
you to think in packages. The name is **scoped to the repository you are
standing in**, so two repos can each hold a `triage` without colliding.

```text file="output"
dl agents create triage        # in dreamlake-starter-kit
→ agent `triage`, scope `dreamlake_starter_kit`
```

With no name at all one is generated — from the description if there is one,
otherwise `agent-<8 hex>`. The generated form is meant to *look* generated, so
it invites being renamed rather than being left forever. Scope and name are
both printed before anything is sent.

## Attaching a machine

Most agents need none. Attach one when the agent has to run somewhere in
particular — a GPU, a specific image, a prepared host:

```bash file="terminal"
dl agents create colmap-driver --file agent.md \
  --run-config colmap-docker-gpu --queue colmap-gpu
```

`--run-config` names an existing `RunConfig` **by name**; it is a reference,
not a copy, so the machine can be re-tuned without touching the agent.
Placement is then derived from that `RunConfig`'s host key — there is no second
field where you say "and this needs a GPU".

## What actually gets stored

`markdown` and `channel` are real columns. `tools`, `model`, `permissions`,
`run_config`, `queue`, `grants` and `arguments` have none and ride in
`metadata`, which round-trips unchanged.

> **Warning:** The server walks `channel` for credentials at full depth and walks **nothing
> else** — so a token under `metadata` would be stored in plaintext and returned
> by `GET`. This command refuses one locally, because the server will not.

## Workspace context

An agent can declare resource references alongside its prompt and arguments:

```yaml
context:
  - {kind: repo, repo: udf-recipes, snapshot: SNAPSHOT_ID, path: docs/, mode: ro}
  - {kind: source, source: training-data, revision: DATA_REVISION, path: samples/, mode: ro}
  - {kind: bindr, bindr: BINDR_ID, mode: ro}
```

| Field | Contract |
| --- | --- |
| `context[].kind` | `repo`, `source`, or `bindr`. |
| `context[].repo/source/bindr` | Nonempty reference matching the kind. |
| `context[].path` | Optional relative path, no traversal or absolute paths. |
| `context[].mode` | `ro` or `rw`; runtime default is planned as `ro`. |
| `context[].snapshot` | Optional immutable repo snapshot reference. |
| `context[].revision` | Optional Source version reference. |

The editor and registration path store validated declarations. They do not
materialize context or grant resource access. The execution identity must
resolve and authorize all required resources before starting. Mutable context
cannot promise exact replay. A reusable named execution workspace is proposed;
it is distinct from namespace/account ownership and is not resolved by this CLI.
