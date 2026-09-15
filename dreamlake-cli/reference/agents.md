# Agents

An agent is a **prompt with a name**. Nothing else is required, and an agent
with nothing else is the normal case, not a degraded one.

```bash file="terminal"
dreamlake agents create triage --prompt 'You triage failed runs. Read the
terminal event first, classify the failure, quote the line that decided it.'
```

An agent is a `Runnable` of kind `agent`, so everything on
[Declaration collections](collections.md) applies to it — versions, `--if-exists`,
the 409 semantics. This group exists because authoring a prompt through
`declare` and a JSON file is miserable.

> **Warning:** There is no agent API in the SDK and no agent route on the control plane.
> DreamLake stores declarations. `dreamlake agents create` writes a row; some
> other system reads it and does the running.

## Three ways to write the prompt

### A heredoc

Quote the delimiter — `<<'AGENT'`, not `<<AGENT` — or the shell expands
`$VARIABLES` and backticks inside your prose before the CLI ever sees it.

```bash file="terminal"
dreamlake agents create triage --file - <<'AGENT'
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
dreamlake agents create run-triage --edit
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
dreamlake agents create run-triage \
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
dreamlake agents create triage        # in dreamlake-starter-kit
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
dreamlake agents create colmap-driver --file agent.md \
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
