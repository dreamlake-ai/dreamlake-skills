<!-- generated from https://cli.dreamlake.ai/bound-execution.md at 0.135.1 9021997; do not edit -->

# Execute a bound UDF on a queue

> Requires CLI 0.94.0 or later. These commands need
> `dreamlake-lakeshore` 0.5.1 or newer on both the
> submitting machine and the worker, and a DreamLake server with the
> execution-binding routes; `--target` also needs the bound-execution routes
> and a control plane with the worker queue pin. With an older SDK, these
> commands stop with the required version instead of running anything.

A registered UDF version identifies one module's bytes. An **execution
binding** identifies what actually runs: that version and entrypoint, the
registry Repo and RepoSnapshot, the exact control-plane CodeRepo, the full
archive SHA-256, the locked runtime and the runner protocol. Its identity is
`sha256(canonical binding)`, written `exec/NAMESPACE/NAME@EXECUTION_DIGEST`.
A changed helper module, dependency lock or Python version produces a new
binding. An existing binding cannot be edited or retargeted.

## Prepare the snapshot and the runtime

The code must be a configured snapshot (a `.dreamrc` `code:` block, see
[snapshot and launch](../snapshot-launch/)). The legacy `git archive`
snapshot is refused. The project directory inside the snapshot must contain
`pyproject.toml`, `uv.lock` and an exact `.python-version` such as `3.12.13`.

```bash
dl runnable register .dreamrc --namespace acme   # registers the UDF source version
dl snapshot --server "$LAKESHORE_URL" --namespace acme   # prints the CodeRepo id
```

On each worker, prepare the environment from the same lock before any
execution. The worker does not install dependencies:

```bash
export DREAMLAKE_RUNTIME_ROOT=/srv/dreamlake/runtimes
LOCK=$(shasum -a 256 uv.lock | cut -d' ' -f1)
UV_PROJECT_ENVIRONMENT="$DREAMLAKE_RUNTIME_ROOT/$LOCK" uv sync --locked --no-dev --python 3.12.13
```

The worker's runner reads `DREAMLAKE_RUNTIME_ROOT` from its own process
environment, not from your shell. For a host worker started by a service
manager, set it in the daemon service's environment and restart the daemon
while it is idle. The runtime's interpreter is separate from the one that runs
the worker daemon and its `dreamlake-lakeshore`: the runner starts the
environment's `bin/python -I -B`, so neither the daemon's `PYTHONPATH` nor its
site-packages reach the UDF. To keep the runtime off interpreters a system
package manager upgrades, build it on a uv-managed CPython:

```bash
uv python install 3.12.13
LOCK=$(shasum -a 256 uv.lock | cut -d' ' -f1)
UV_PYTHON_PREFERENCE=only-managed UV_PROJECT_ENVIRONMENT="$DREAMLAKE_RUNTIME_ROOT/$LOCK" \
  uv sync --locked --no-dev --python 3.12.13
"$DREAMLAKE_RUNTIME_ROOT/$LOCK/bin/python" -I -c 'import platform; print(platform.python_version())'
```

Run `uv sync` in a checkout of the bound revision. A missing environment
directory, a different interpreter version or a locked distribution version
mismatch rejects the attempt before user code runs. Matching distribution
versions are a necessary check, not proof of complete environment identity:
installed file contents, system libraries and tools outside the venv are not
verified.

## Bind

```bash cli-help="runnable bind"
dl runnable bind udf/acme/recipes.process@FULL_SHA256 \
  --snapshot CODE_REPO_ID --project recipes \
  --server "$LAKESHORE_URL" --cp-namespace acme --dry-run
dl runnable bind udf/acme/recipes.process@FULL_SHA256 \
  --snapshot CODE_REPO_ID --project recipes --server "$LAKESHORE_URL" --cp-namespace acme
```

`bind` downloads the stored archive through the SDK bridge, verifies its full
SHA-256 and reads the digests of the registered source, `pyproject.toml` and
`uv.lock` from that archive. The source file in the archive must equal the
registered version. It then registers a RepoSnapshot (`commit` = full archive
SHA-256) and the binding. The server checks that every registry reference
belongs to the namespace and agrees with the version-owned metadata; it
recomputes the digest and stores the canonical bytes. Repeating the command
returns the existing binding. `--dry-run` performs the checks without registry
writes.

The server does not read the archive and the binding is not a Git provenance
proof. The worker verifies the delivered bytes.

The DreamLake server also never contacts the control plane. The binding's
`controlPlane` origin, namespace and CodeRepo are what `bind` read through
your control-plane credentials; the server stores them and checks only the
registry side. They are not a server-issued attestation. `execute` therefore
never defaults to the binding's origin: pass `--server` or set
`LAKESHORE_URL` to the control plane you trust, and the command refuses a
binding that names a different origin or namespace. The bridge then resolves
the pinned CodeRepo id with your credentials and refuses a row whose commit,
archive key or storage differs from the binding.

## Execute and recover

```bash cli-help="runnable execute"
dl runnable execute exec/acme/recipes.process@EXECUTION_DIGEST \
  --queue cpu --inputs record.json --timeout-seconds 600 --json
dl runnable execute exec/acme/recipes.process@EXECUTION_DIGEST \
  --queue cpu --inputs record.json --timeout-seconds 600 --attempt 2 --json
```

There are three identities:

| Identity | Derived from | Meaning |
| --- | --- | --- |
| Execution digest | the binding | what runs |
| Task key | execution digest, queue, timeout, canonical inputs | the business task |
| Invocation ID | `bx1-<task key prefix>-a<attempt>` or `--invocation-id` | one attempt |

The invocation ID is printed before submission. After a lost response or an
interrupted wait, repeat the same command with the same inputs: the control
plane returns the original invocation for the same ID and identical bytes, and
answers 409 when the same ID carries different bytes. `--attempt 2` is a
deliberate new attempt of the same task. Inputs are one JSON object of at most
256 KiB; non-integer numbers must be encoded as strings.

```bash cli-help="runnable execution-receipt"
dl runnable execution-receipt exec/acme/recipes.process@EXECUTION_DIGEST \
  --queue cpu --inputs record.json --timeout-seconds 600 --wait-seconds 30
```

`execution-receipt` takes the same task arguments and never submits.

## Run through DreamLake on an owned host (`--target`)

With `--target namespace/group/host[/user]`, the submitting CLI and the UDF need no
control-plane token. The DreamLake server uses the host enrollment's
connection on your behalf, and the worker daemon keeps its normal enrollment
credentials; you must own the host, and its worker must claim the queue you
name: either it is pinned to exactly that queue (see
[Pin a worker to dedicated queues](../queues/)), or it is unpinned, its claims
are enabled and the queue is one of its declared queues.
`default` is never accepted. Otherwise the server answers
`409 target_not_eligible` (`target_not_pinned` on earlier servers).

```bash
dl runnable bind udf/acme/recipes.process@FULL_SHA256 \
  --target acme/compute/worker --project recipes
```

`bind --target` builds this checkout's configured archive locally, then uploads
it through DreamLake. The archive must be at most 128 KiB. The server checks its
layout and digest, stores it at a key derived from the sha256 in the host's
control plane, and registers the RepoSnapshot. `bind` then registers the binding
with the server-derived control-plane block.

Keep the project in a subdirectory of the snapshot and name it with
`--project`: put `.dreamrc` beside the project files, mount them under a
target directory, and declare the UDF `source` as the entrypoint's module
path. For example, with `udf_full/main.py` and its helper modules next to
`pyproject.toml`, `uv.lock` and `.python-version`:

```yaml
udfs:
  - {name: acme.full_project, entrypoint: "udf_full.main:run", source: udf_full/main.py}
code:
  mounts:
    - local_path: .
      target: app
      exclude: [".dreamrc", ".venv/", "__pycache__/"]
```

and bind with `--project app`. Sibling modules of the entrypoint's package
import from the snapshot; third-party packages come from the locked runtime.

**Source-staged snapshots.** No CLI or SDK upgrade is needed. In a namespace where
the DreamLake deployment stages launch code in DreamLake Sources, `bind
--target` stores the archive in your private `launch-code-<user id>` Source
instead of control-plane storage, and the binding's control-plane block points
at it (`storageName` `dreamlake-source`, archive key
`source/<source id>/dreamrc-mounts/<sha256>.tar.gz`). The commands and output
are the same. At `execute --target`, DreamLake reads the archive as you, checks
its full SHA-256 and submits it inline. Only the user who bound a Source-staged
binding can execute it; another member gets `409 launch_code_source_conflict`.
The same archive already registered for the repository at another location
(control-plane storage, or another user's Source) is `409 snapshot_mismatch`.

```bash
dl runnable execute exec/acme/recipes.process@EXECUTION_DIGEST \
  --target acme/compute/worker --queue fixture --inputs record.json --timeout-seconds 600 --json
```

The task request becomes `dreamlake-bound-task-v2`: the target host,
enrollment and worker are part of the task key and invocation ID, so the same
inputs on another worker are a different task. The server checks that the worker claims the queue,
re-reads the control-plane CodeRepo and the stored archive bytes against the
binding, and submits with the archive inline. Only the target worker can
claim the attempt, and the UDF run needs no control-plane token. Inputs are at
most 16 KiB. Repeating the identical command returns the same invocation. Changed
inputs (or queue, timeout or target) are a different task, with a new task key and
invocation ID. A request that keeps an old task key or invocation ID with changed
inputs is rejected before submission (`400 invalid_task_request`). If the control
plane already holds that invocation ID with a different payload, the command fails
with `409 attempt_conflict`. `execution-receipt --target` reads the
receipt through DreamLake; it does not need the worker to be online.

## What the worker checks and returns

The queued function is `dreamlake.lakeshore.bound.run_bound_udf`, resolved
from the worker's installed SDK; the user's code comes from the snapshot. In
order, before any user module is imported, the worker:

1. takes the archive (inline with `--target`, otherwise downloaded) and
   requires its full SHA-256;
2. unpacks it with the configured-snapshot runner into a fresh directory;
3. re-hashes the registered source, `pyproject.toml` and `uv.lock`;
4. selects `$DREAMLAKE_RUNTIME_ROOT/<uv.lock sha256>` and starts
   `bin/python -I -B` there;
5. checks the exact CPython version, the environment prefix and the version of
   every distribution in the lock's runtime closure. Locks this check cannot
   decide without a marker evaluator are rejected: forked resolutions, several
   entries for one name, and any dependency carrying a marker or extra;
6. imports the entrypoint from the snapshot only, refusing a module resolved
   from any other path, and calls it with the inputs object.

The receipt is the invocation's stored result: execution digest, task key,
attempt, invocation ID, `status` (`succeeded`, `failed`, or `rejected` when
verification stopped it before user code), the stage, verified digests,
observed runtime, the JSON result or error, and the child's stderr (up to
1 MiB). The control plane's at-most-once claim policy applies; this is not
crash-proof exactly-once execution.
