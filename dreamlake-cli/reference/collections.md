# Declaration collections

DreamLake stores **declarations** — named descriptions of code and of the
environments that code runs inside. Five of them are *head* collections, all
created the same way, with `dreamlake declare`:

| Collection | What it describes |
| --- | --- |
| `lakeshore-providers` | how a machine gets launched |
| `sources` | where data lives |
| `runnables` | named code you invoke — `udf`, `session`, or `agent` |
| `run-configs` | the environment a runnable runs inside |
| `repos` | a git remote a worker imports from |

Runnables additionally have **versions**: immutable rows keyed by
`sha256(source)`. Those are not declared — they are pushed, with
`dreamlake runnable version push`.

> **Warning:** Nothing on this page schedules, claims, launches, or connects to anything.
> These commands are storage and CRUD. Execution belongs to the lakeshore
> control plane, and none of these routes reach it.

## A worked sequence

The full loop: declare a runnable, register two versions of it, read the
history back, and import a pinned copy onto another machine.

### 1 · Declare the head row

```json file="runnable.json"
{
  "name": "examples.embed.embed_frames",
  "module": "examples.embed",
  "qualname": "embed_frames",
  "kind": "udf",
  "description": "Embed video frames with a cached model."
}
```

```bash file="terminal"
dreamlake declare runnable.json
```

```text file="output"
declare  runnable.json
  remote:     http://localhost:10334
  namespace:  chengdu
  collection: runnables
✓ declared examples.embed.embed_frames → runnables (id 65f0…00aa)
```

The target is printed **before** the write, never after. If you are about to
hit the wrong server, the line that tells you has to come first.

The collection was inferred from the payload's own shape — `module` and
`qualname` mean `runnables`. Pass `--collection` when you want it explicit, or
when a payload is ambiguous:

```bash file="terminal"
dreamlake declare gpu-small.yaml --collection run-configs
dreamlake declare */*.json --dry-run          # resolve targets, send nothing
```

Inference rules, in order: `runtime` or `extras` → `run-configs`; `module` or
`qualname` → `runnables`; `remote` → `repos`; then `kind` against the shipped
vocabularies (`udf|session|agent` → `runnables`, `local|slurm-ssh|aws-ec2|gce|k8s`
→ `lakeshore-providers`, `s3|gcs|r2|b2|postgres|mysql|databricks` → `sources`).
A payload matching none of those is an error, not a guess.

Files may be JSON or YAML — the format is autodetected. The object is POSTed
**verbatim**: no wrapping envelope, no renamed fields, no injected defaults.

### 2 · Re-running the script — `--if-exists ok`

Every head row is create-only. There is no `PUT` and no upsert on these five
collections, so a second `declare` of the same name returns 409 and **nothing
is touched**.

```bash file="terminal"
dreamlake declare runnable.json                    # ✗ exit 1
dreamlake declare runnable.json --if-exists ok     # ⚠ exit 0
```

```text file="output"
⚠ already exists — nothing was overwritten
```

`fail` is the default, matching the rest of the CLI. `ok` exists because a 409
means the name is taken and nothing was overwritten — a failure for a human
typing a command, a success for a `make push` you expect to run twice.

### 3 · Register a version

```bash file="terminal"
dreamlake runnable version push examples.embed.embed_frames --source src/embed.py
```

```text file="output"
✓ registered version 9f2b…(64 hex chars) of examples.embed.embed_frames
  latestVersion is now this version
```

There is deliberately **no `--version` flag**. `RunnableVersion.version` must
stay byte-identical to the control plane's `Function.version`, so the CLI
computes it as sha256 of the file's bytes and it can never be supplied by hand.

That makes registration idempotent by content. Push the same bytes again and
you get a different answer:

```text file="output"
⚠ version 9f2b…(64 hex chars) already registered — unchanged
  registration is idempotent by content: the version IS sha256(source),
  so identical bytes cannot overwrite a stored row
```

Both exit 0. The *difference between the two messages is the information* — a
second caller holding the same source cannot silently replace what the first
one stored, and `latestVersion` does not move backwards.

Edit the source and push again, and you get a 201 and a new `latestVersion`.

> **Warning:** Not `runnable:create`. An org MEMBER with READ can *list* versions but cannot
> push one; the CLI says so rather than echoing a bare `403 Forbidden`.

An optional `--signature <file>` carries a JSON object of the shape
`{ params, returns, doc }`. Its contents are owned by the SDK and passed
through untouched.

### 4 · Read the history back

```bash file="terminal"
dreamlake runnable list --kind udf
dreamlake runnable show examples.embed.embed_frames
dreamlake runnable version list examples.embed.embed_frames
```

```text file="output"
version       hasSource  createdAt
c41e9a0f77bd  yes        2026-08-06
9f2b6d1a83c0  yes        2026-08-05

  2 version(s)
```

Versions come back newest first, and the list projection **never includes
`source`** — 200 rows of source is megabytes. Hashes are truncated to 12
characters in tables so the columns fit; `runnable show` always prints the full
64, because a truncated hash addresses nothing.

To get the source of one version:

```bash file="terminal"
dreamlake runnable version show examples.embed.embed_frames c41e9a0f77bd… --source-only > embed.py
```

`--source-only` writes the stored bytes to stdout with no decoration at all, so
the redirect above reproduces the same sha256 you started from. Without it, the
command emits the whole row as JSON.

### 5 · Import a pinned copy

`import` is a composition of the reads above, not a new capability:

```bash file="terminal"
dreamlake runnable import examples.embed.embed_frames --out ./vendor/embed
```

```text file="output"
  wrote /work/vendor/embed/embed_frames.py
  wrote /work/vendor/embed/signature.json
  wrote /work/vendor/embed/PINNED.json
✓ imported examples.embed.embed_frames @ c41e9a0f77bd…
```

Without `--at` it makes exactly two requests: read `latestVersion` off the
head, then fetch that version. With `--at <sha256>` it makes one fewer decision
and pins whatever you named; `--at latest` and `--at <hex prefix>` are also
accepted and resolved client-side.

> **Warning:** `dreamlake` declares `-v, --version` on the root program, and Commander
> resolves a root option from **any** descendant command. So
> `dreamlake runnable import <name> --version <sha256>` prints the CLI's own
> version number and **exits 0 having imported nothing** — a silent no-op that
> looks like a success. Use `--at`.

`PINNED.json` records
`{ remote, namespace, name, kind, version, path, importedAt }`, where `path` is
the one-token address — `udf/chengdu/examples.cpu.add@<sha256>`. Commit it next
to the source: a pin that lives only in shell history is not a pin.

### 6 · Find the environment

```bash file="terminal"
dreamlake runconfig list
dreamlake runconfig show gpu-small
dreamlake runconfig list --host-key hk1_2f6c9d
```

`--host-key` answers exactly one question: which configs resolve to the same
placement key, i.e. which ones could share a worker.

## The nine commands

```bash file="terminal"
dreamlake declare <file...> [--collection <name>] [--if-exists ok|fail] [--dry-run] [--json]

dreamlake runnable list [--kind <k>] [--module <m>] [--json]
dreamlake runnable show <name> [--json]
dreamlake runnable version push <name> --source <file> [--signature <file>] [--json]
dreamlake runnable version list <name> [--json]
dreamlake runnable version show <name> [version] [--at <ref>] [--source-only] [--json]
dreamlake runnable import <name> [--at <latest|prefix|sha256>] --out <dir> [--json]

dreamlake runconfig list [--provider <name>] [--host-key <hk>] [--json]
dreamlake runconfig show <name> [--json]
```

`version show`'s positional argument is **optional** and defaults to `latest`;
`--at` says the same thing as a flag. Both accept `latest`, a hex prefix of at
least 8 characters, or the full 64-character sha256. `latest` and prefixes are
resolved here, client-side — the server still addresses versions by the full
hash and nothing else — and an ambiguous prefix is an error rather than a guess.

Every one of them takes `--namespace <slug>` (default: the active login) and
every read takes `--json`. There is no `PATCH` or `DELETE` surface here, and no
`repo` or `snapshot` group — the server has those routes, the CLI deliberately
does not.

## Four honest limits

**1 · On the server, a version has exactly one name, and it is 64 hex characters.**
There is no tag, no semver and no alias — and no `?version=latest` or prefix
match on the route. The `latest` and short-prefix forms the CLI accepts are
resolved **client-side**, at the cost of extra round trips: `latest` reads
`latestVersion` off the head (one more request), a prefix lists the versions and
matches on it (two more). The 12-character forms in tables are display only.

**2 · Nothing joins a runnable to a run config.**
No route returns both, and there is no `?include=`. A `RunConfig` is referenced
by *name*, resolved late by the control plane. If you want "the UDF and the
environment it runs in", make two calls and correlate them yourself.

**3 · `hostKey` is derived, display-only and non-authoritative.**
The server recomputes it on every write and never accepts it from a request
body — `dreamlake declare` refuses a payload containing `hostKey` locally,
rather than letting you believe a value you sent was stored. The Python SDK's
copy, stamped at submit time, is the one a scheduler uses. A **null** `hostKey`
does not mean "no placement"; it means the key could not be computed, most
often because `runtime.resources` contains a float. `runconfig show` says that
in place of a bare dash.

**4 · DreamLake does not execute anything.**
Storage and CRUD only. Declaring a runnable does not deploy it, pushing a
version does not run it, and a `RunConfig` describes an environment that
something else has to build.

> **Note:** There is no route that removes a `RunnableVersion`, soft or hard. Deleting a
> runnable is a soft delete on the head row; the version rows are immutable
> history and survive it.
