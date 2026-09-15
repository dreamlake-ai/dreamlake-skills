# Provider lifecycle

A **provider** is created deliberately, once, with a name a person chose.
Everything ephemeral attaches to it: a daemon never creates a provider, it
*claims* one.

There are two ways to get a working provider, and they end in the same place —
a live worker whose `providerName` is your provider's name.

| | What it does | No terraform? |
| --- | --- | --- |
| **Provision** | Scaffold terraform into `.dream/providers/<name>/`, resolve the decisions, plan, apply, then put a daemon on the result | — |
| **Adopt** | SSH to a cluster that already exists and start a daemon there under a supervisor | `--provider ssh` |

```bash file="terminal"
# provision
dreamlake provider create -n aws-demo --provider kube
dreamlake provider plan    -n aws-demo
dreamlake provider apply   -n aws-demo --yes
dreamlake provider connect -n aws-demo

# adopt
dreamlake provider create  -n lab-box --provider ssh
dreamlake provider connect -n lab-box --host you@ops.internal

dreamlake provider status  -n aws-demo
```

## The CLI embeds no model

There is no chat endpoint here, no agent framework, and nothing that calls a
language model. The CLI is a **tool an agent drives**. It does as much as it
can without guessing, then stops and reports — in prose for a human, in JSON
for an agent — *where it is* and *what the next action is*. Something else
performs that action and re-runs the tool.

```
run  →  read nextAction  →  act  →  --continue  →  run …
```

Three consequences, each a hard rule:

1. **It never blocks on a terminal.** An agent has no TTY. "Needs input" is an
   *exit state carrying a next action*, never a prompt.
2. **Every state names its next action**, in prose *and* in `--json`.
   `nextAction` is a required, nullable field, so an agent reads one key.
3. **`create` never applies.** Applying spends money and is its own verb.

## The loop, for an agent

This is the whole interface. Follow it verbatim.

```text file="the loop"
1.  Run the command with --json.
2.  Read .status and .nextAction.  Branch on THOSE, never on the exit code.
3.  nextAction == null                 → done. Stop.
    kind == "edit_then_continue"       → open .file. Resolve EVERY .blocking[].key.
                                         Then run .command.
    kind == "run" | "shell"            → run .command.
4.  Go to 1.

FUSE: if two consecutive runs return the same .blocking[] keys, STOP and ask a
human. You are not converging, and re-running will not help.

NEVER run `provider apply` unless the user asked for infrastructure to be
created. It spends money. `ready` is a legitimate place to stop and report.

.observed is a HINT from an account probe, not an answer. Its ABSENCE means
credentials were not available (check .degraded for "no-probe") — it does not
mean the account is empty.

Read ADAPT.md in the scaffolded directory before choosing values. The template
came from someone else's account and is a starting point, not a default.
```

> **Warning:** Without it an agent loops on an unresolvable decision forever, burning tokens
> and cloud API calls against a question only a person can answer. Two identical
> `blocking[]` key sets in a row means **stop and report**, not "try again".

## Exit code and status answer different questions

The single most important thing to get right when scripting this:

| | Answers | Values |
| --- | --- | --- |
| **exit code** | *did the tool work?* | `0` = coherent · `1` = error |
| **`status`** | *where are we?* | the ten-state union below |
| **`nextAction`** | *what happens next?* | an object, or `null` when done |

**`needs_input` exits 0.** It is not a failure — the tool did exactly its job,
which is to find out what it cannot decide and say so. An agent driving under
`set -e`, or a `Makefile`, must not die because the tool successfully reported
a question. Exit 1 is reserved for *the tool could not do its job*: bad flags,
no auth, no binary, a terraform error, an unreachable host.

This is not new. `dreamlake provider delete` without `--yes` on a non-TTY
already cancels and returns 0 — "I deliberately did not do the thing" has
always been a success in this CLI.

## The ten states

```ts file="status"
type ProviderStatus =
  | "scaffolded"   // files on disk, decisions look complete, nothing planned
  | "needs_input"  // blocking[] is non-empty — THE state this design exists for
  | "ready"        // init + validate + plan all clean. Nothing has been applied.
  | "applying"     // an apply is in flight or was interrupted. Resumable.
  | "applied"      // infrastructure exists. No daemon on it yet.
  | "connecting"   // ssh reached the host; the daemon is not claiming yet
  | "unclaimed"    // applied/adopted, zero live bridges. NORMAL, not an error.
  | "connected"    // ≥1 live worker with providerName == <name>. TERMINAL.
  | "exists"       // this step was already done. Idempotent no-op.
  | "error"        // the one failure shape.
```

Read the table as **verb × observed world → status**.

| From | Verb | Trigger | → status | rc |
| --- | --- | --- | --- | --- |
| — | `create` | dir absent, vendor known, no decision blocks | `scaffolded` | 0 |
| — | `create` | dir absent, vendor known, decisions unresolved | `needs_input` | 0 |
| — | `create` | dir absent, `--provider` names no vendor | `error` | 1 |
| `scaffolded`/`needs_input` | `create --continue` (or a bare re-run) | decisions now all resolved | `scaffolded` | 0 |
| `needs_input` | `create --continue` | still unresolved | `needs_input` | 0 |
| any | `create` | dir exists, **same** vendor, no file would change | `exists` | 0 |
| any | `create` | dir exists, **different** vendor | `error` | 1 |
| `scaffolded` | `plan` | init + validate + plan all clean | `ready` | 0 |
| `scaffolded` | `plan` | plan surfaces a missing/invalid variable | `needs_input` | 0 |
| `scaffolded` | `plan` | terraform errors for any other reason | `error` | 1 |
| `ready` | `apply --yes` | apply exits 0 | `applied` | 0 |
| `ready` | `apply` **without** `--yes` | — | `needs_input` | 0 |
| `ready`/`applying` | `apply --yes` | state lock held, or apply interrupted | `applying` | 0 |
| `ready` | `apply --yes` | terraform errors for any other reason | `error` | 1 |
| `applied` | `connect` | ssh ok, supervisor started, claim observed | `connected` | 0 |
| `applied` | `connect` | ssh ok, daemon started, claim not yet observed | `connecting` | 0 |
| `applied` | `connect` | no `--host` and none derivable from outputs | `needs_input` | 0 |
| `connected` | `connect` | a live worker already claims it | `exists` | 0 |
| any | `status` | recomputed from the world | any of the above | 0 |
| `applied` | `status` | zero live claimants | `unclaimed` | 0 |
| any | any | no auth / no binary / unwritable dir / ssh refused | `error` | 1 |

`scaffolded → needs_input` and back is a **cycle, and that is the point** — it
is the loop the agent walks. Everything else is a DAG.

**`error` is not a dead end.** Every terraform failure — `init`, `validate`,
`plan` or `apply` — carries a real `nextAction`: `edit_then_continue` pointing
at the terraform directory, with `dreamlake provider plan -n <name>` as the
command. That is the one state where an agent most needs a next step, and
`nextAction: null` there would tell it the run is over.

The recovery command is **always `plan`, never `apply`**. `plan` reads and
costs nothing; if it comes back clean, *its* `nextAction` is the apply. A
failed apply that handed back `apply --yes` would turn a broken config into a
retry loop that spends money on every turn.

`applying` is the only state whose next action is "run the same command
again". Terraform owns that recovery and this CLI does not reimplement it: it
detects `.terraform.tfstate.lock.info`, or an apply that left a partial state,
and says so.

## `needs_input` — the state this exists for

The prose form:

```text file="output"
provider create  aws-demo
  root:       /Users/you/proj              (.dreamrc)
  dir:        .dream/providers/aws-demo
  vendor:     kube
✓ scaffolded .dream/providers/aws-demo/terraform/
  wrote /Users/you/proj/.dream/providers/aws-demo/provider.json
  … 9 more
⚠ needs decisions before it can apply:
    · region        — not set. account has resources in us-east-1, us-west-2
    · vpc           — create new, or adopt vpc-0abc123 (10.0.0.0/16)
    · node type     — not set

  next: edit .dream/providers/aws-demo/terraform/terraform.tfvars, then
        dreamlake provider create -n aws-demo --continue
```

The same run, with `--json`. This is the payload an agent branches on:

```json file="dreamlake provider create -n aws-demo --provider kube --json"
{
  "status": "needs_input",
  "provider": "aws-demo",
  "vendor": "kube",
  "dir": "/Users/you/proj/.dream/providers/aws-demo",
  "files": [
    "/Users/you/proj/.dream/providers/aws-demo/provider.json",
    "/Users/you/proj/.dream/providers/aws-demo/terraform/main.tf"
  ],
  "blocking": [
    {
      "key": "region",
      "reason": "unset",
      "file": "/Users/you/proj/.dream/providers/aws-demo/terraform/terraform.tfvars",
      "line": 3,
      "observed": ["us-east-1", "us-west-2"],
      "why": "Every resource in this template is regional. Pick the region your data already sits in."
    }
  ],
  "degraded": [],
  "nextAction": {
    "kind": "edit_then_continue",
    "file": "/Users/you/proj/.dream/providers/aws-demo/terraform/terraform.tfvars",
    "command": "dreamlake provider create -n aws-demo --continue"
  }
}
```

### Every field, once

```ts file="contract"
interface Blocking {
  /** Stable, machine-branchable. Not the prose label. */
  key: string
  reason: "unset" | "placeholder" | "invalid" | "conflict"
  /** Absolute path. Where to go and fix it. */
  file?: string
  line?: number
  /** Best-effort account probe. ABSENT is normal — see `degraded`. */
  observed?: string[]
  /** One sentence from the template's TEMPLATE.json. How to choose. */
  why?: string
}

type NextAction =
  | { kind: "edit_then_continue"; file: string; command: string }
  | { kind: "run";   command: string }
  | { kind: "shell"; command: string; host?: string }
  | null

interface ProviderLifecycleResult {
  status: ProviderStatus
  provider: string
  vendor?: string
  server: string
  namespace: string
  /** Absolute. The one directory this provider owns. */
  dir?: string
  /** Files written BY THIS RUN. `[]` proves a no-op. */
  files?: string[]
  blocking?: Blocking[]
  plan?: { add: number; change: number; destroy: number }
  claim?: { live: number; gone: number; instances: string[] }
  /** Unavailable but not fatal: "no-credentials", "no-probe",
   *  "no-supervisor", "no-lakeshore". */
  degraded?: string[]
  /** REQUIRED, nullable. An agent reads exactly one key. */
  nextAction: NextAction
  error?: string
  kind?: string
}
```

> **Warning:** Filling `observed` needs a live account probe. When credentials are not
> available the field is simply **omitted** and `degraded` carries `"no-probe"`.
> An agent that reads a missing `observed` as "there are no regions in use" will
> confidently pick the wrong one. Check `degraded` first.

## The other states, in prose

```text file="scaffolded"
✓ scaffolded .dream/providers/aws-demo/terraform/
  every decision in this template has a value.

  next: dreamlake provider plan -n aws-demo
```

```text file="ready"
✓ plan is clean — 14 to add, 0 to change, 0 to destroy
  nothing has been applied. The next command spends money.

  next: dreamlake provider apply -n aws-demo --yes
```

`--yes` is baked into the printed command **on purpose**. There is no
confirmation prompt anywhere on this path; the guard is that you have to type
a different command than the one you just ran.

```text file="applying"
⚠ an apply is in progress or was interrupted
  terraform holds a state lock (…/terraform.tfstate.lock.info, held 00:04:12)

  next: dreamlake provider apply -n aws-demo --yes    # re-run; terraform resumes
```

```text file="connected / unclaimed"
✓ connected — 2 live workers claiming 'aws-demo'
    i-0abc…  active    12s ago   queues: gpu, cpu
    i-0def…  joining    3s ago   queues: gpu
  next: (none)

⚠ unclaimed — no bridge is claiming 'aws-demo'
  this is a normal state, not a fault: it means nothing can launch into this
  account right now.
  next: dreamlake provider connect -n aws-demo
```

`connected` is the **only** status whose `nextAction` is `null`. All of these
exit 0. Zero bridges for a provider is a normal state, not an error — it must
never render as a failure.

```text file="exists"
⚠ .dream/providers/aws-demo/ already exists from vendor 'kube' — nothing was overwritten
```

`exists` carries `files: []`. The *empty write list is the proof* it was a
no-op, and it is exactly what a test asserts.

## Idempotence

**Re-running is the resume.** `--continue` is sugar over that, not a second
code path: without it, a directory that already exists is *reported*
(`exists`); with it, the existing directory is expected and the command goes
straight to the decision scan.

Two refusals you can rely on:

* A second `create` with identical inputs → `exists`, rc 0, `files: []`, and
  no file's mtime moves.
* A second `create` with a **different** `--provider` → `error`, rc 1. It
  never merges and never overwrites:

  ```text file="output"
  ✗ 'aws-demo' was scaffolded from vendor 'kube'. Refusing to overwrite it
    with 'ec2' — delete the directory or pick another name.
  ```

## Where the state lives: nowhere

The phase is **derived on every invocation**, never stored. Four observations,
in this order:

1. Does `.dream/providers/<name>/` exist, and what does its `provider.json`
   say it is — identity and template provenance, written once, never a phase.
2. The decision scan over `terraform/terraform.tfvars` against
   `TEMPLATE.json`'s `decisions` (or `adopt.json` for the ssh vendor) →
   `blocking[]`.
3. `terraform show -json`, plus the presence of `terraform.tfstate` and any
   lock file → `applied` vs not, `applying` or not.
4. The control plane's live workers, filtered to `providerName == <name>` →
   `connected` / `unclaimed`.

A stored phase can disagree with the world; a derived one cannot, and it
cannot lie about a `terraform apply` someone ran by hand in that directory.

### The directory

`.dream/` goes beside the nearest `.dreamrc` walking up from cwd; with no
`.dreamrc` anywhere, beside cwd. The chosen root is **printed before anything
is written**. `--dream-dir <path>` overrides it.

```text file=".dream/"
.dream/
  .gitignore                       written on first scaffold
  providers/aws-demo/
    provider.json                  identity + template provenance
    terraform/                     scaffolded, yours to edit
      terraform.tfvars             the decisions — THE file an agent edits
      ADAPT.md                     how to choose each one, per vendor
    adopt.json                     ssh vendor only, instead of terraform/
```

The generated `.gitignore` covers `providers/*/terraform/.terraform/`,
`providers/*/terraform/terraform.tfstate*` and `providers/*/terraform/*.tfplan`
— so the provider is reviewable in a PR while state and the plugin cache stay
out of git.

## Adopting a cluster over SSH

`--provider ssh` selects a vendor with no terraform at all. `create` writes
`adopt.json`; `connect` does the work, in this order:

1. **Check the claim first.** If a live worker already claims the provider →
   `exists`, rc 0, **no ssh at all**. Idempotence before action.
2. `ssh -o BatchMode=yes -o StrictHostKeyChecking=accept-new` to probe.
   `BatchMode=yes` is the never-block-on-a-TTY rule applied to ssh: it can
   never sit at a password prompt. A refused key is a sentence plus
   `nextAction: {"kind":"shell","command":"ssh-copy-id you@ops.internal"}`.
3. Install the daemon.
4. Start it under **the best supervisor the host actually has**, and say which.

| Available on the host | What `connect` does | `status` |
| --- | --- | --- |
| `systemctl --user` + `loginctl enable-linger` | user unit, `Restart=always` | `connected` |
| `systemd` + passwordless sudo | system unit, `Restart=always` | `connected` |
| neither | `tmux new-session -d -s nymph-<name>` | `connected`, `degraded: ["no-supervisor"]` |

### tmux is for attaching, not for supervising

tmux is chosen over `nohup` and `screen` for one reason: **the session is
reattachable, which is how you debug a daemon that is misbehaving.** `nohup`
gives you a log file and no way in. But reattachable is not supervised, and
the prose says so plainly:

```text file="output"
⚠ no supervisor on this host — the daemon is running under tmux (session nymph-lab-box)
  tmux keeps it alive after your ssh session ends. It does NOT restart it.
  If this daemon dies, nothing brings it back:
    dreamlake provider connect -n lab-box     # re-run to restart
```

**The SSH connection is never the supervisor.** `connect` returns as soon as
`tmux new-session -d` (or `systemctl start`) does; it holds no socket. Killing
the CLI does not touch the daemon, and there is no long-lived `--wait` on this
path.

## Templates are a starting point, not a default

Vendor templates ship inside the CLI, one directory per vendor, each with a
`TEMPLATE.json` manifest whose `decisions[]` *is* `blocking[]`, pre-written:

```json file="TEMPLATE.json"
{ "vendor": "kube", "version": 1, "kind": "k8s",
  "files": ["terraform/*.tf", "terraform/terraform.tfvars", "ADAPT.md"],
  "decisions": [
    { "key": "region", "var": "region", "file": "terraform/terraform.tfvars",
      "probe": "aws-regions-in-use",
      "why": "Every resource here is regional. Pick the region your data already sits in." },
    { "key": "node_type", "var": "gpu_instance_types", "file": "terraform/terraform.tfvars",
      "why": "List every interchangeable type — more types means fewer spot interruptions." }
  ] }
```

The decision scan is: for each decision, read `var` out of `file`; unset, still
the placeholder, or failing `variables.tf`'s own `validation` block → a
`Blocking`. That is the whole algorithm, and it is **offline**. A missing
account probe never fails a command; it only leaves `observed` empty.

> **Warning:** They are derived from a real, working setup — which means a real VPC CIDR, real
> IAM names, a real project prefix. Account-specific values are **deleted, not
> defaulted**: they ship as a `decisions[]` entry with no default and a commented-out
> key in `terraform.tfvars`. Read `ADAPT.md` in the scaffolded directory, which
> says per decision what to look at in your account and how to choose, **before**
> picking values.

`provider.json` records `templateVersion`, so `provider status` can report
`template: kube v1 (v2 available)` and offer a command. It never edits files
under you.

## What this page does not cover

The five CRUD verbs on the provider *row* in DreamLake — `create` from a file,
`list`, `show`, `update`, `delete` — are a different surface, documented in
[Lakeshore resources](lakeshore.md). The lifecycle verbs on this page are leaves
on that same `provider` group; both keep working.
