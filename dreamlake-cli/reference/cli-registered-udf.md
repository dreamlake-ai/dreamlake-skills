<!-- generated from https://cli.dreamlake.ai/registered-udf.md at 0.94.0 cbe0f3f; do not edit -->

# Execute a registered Python UDF

Available in CLI 0.68.0 and later. These commands reuse the managed host-run API
and an already enrolled worker with tracked-run and uv support.

This first bridge accepts a **full SHA-256 version**, one UTF-8 Python module,
a synchronous function, and JSON arguments/result. It fetches that exact registry
version, verifies its bytes, and sends those bytes through the existing explicit
source-manifest transport. Changes to your local files cannot change this run.

## Register the immutable binding

The version must have its own `metadata.repo_id`, `metadata.source_file`, and
`metadata.entrypoint`; the mutable runnable head is insufficient. The repo must
be readable in the same namespace. The source path must match the entrypoint:
`tasks/math.py` for `tasks.math:add`.

The existing authenticated API accepts this payload at
`POST /namespaces/NAMESPACE/runnables/NAME/versions`:

```json
{
  "version": "FULL_SHA256_OF_UTF8_SOURCE",
  "source": "def add(a, b):\n    return a + b\n",
  "metadata": {
    "repo_id": "EXISTING_REPO_ID",
    "source_file": "tasks/math.py",
    "entrypoint": "tasks.math:add"
  }
}
```

Register the repo and runnable first using the existing declaration API. Source
registration is immutable: compare an existing version's returned source and
metadata, rather than overwriting or assuming a retry attached new metadata.
The pending registration workflow in CLI PR #270 produces these same fields.
Older `version push` versions without immutable metadata need a correctly bound
registration; changing only head metadata does not repair an immutable version.

Registry version labels are not trusted as digest verification: this bridge hashes
the returned source before submission. The existing server validates the inline
manifest and Nymph independently verifies every delivered file before spawning.
The Python adapter rechecks the selected module before evaluating it.

## Run and recover

```json file="inputs.json"
{"args": [20, 22], "kwargs": {}}
```

```bash cli-help="runnable run"
dreamlake runnable run udf/NAMESPACE/NAME@FULL_SHA256 \
  --target NAMESPACE/GROUP/HOST --enrollment-id ENROLLMENT_ID \
  --request-id YOUR_STABLE_REQUEST_ID --inputs inputs.json --json
```

The target must be in the same namespace. The existing server checks ownership,
exact enrollment, active worker identity, signing-key validity and tracked-run/uv
readiness. It repeats dispatch admission checks. This command cannot provision
or repair a host and does not change daemon configuration.

Keep the request ID, inputs and options when submission is uncertain. Repeat the
same command to recover the existing run; changed payloads conflict. Never create
a new request ID merely because an HTTP response was lost. The command prints
the accepted receipt reference before waiting. `--no-wait` returns after submission;
a client wait timeout does not cancel or establish failure of the workload.

```bash cli-help="runnable receipt"
dreamlake runnable receipt NAMESPACE/RUN_ID --json
```

Receipt retrieval reads only the owned run and retained output, so it works
without local files or resolving a newer registry head. Existing `runs status`,
`runs logs` and `runs cancel` also apply. A worker crash or lost claim can remain
unresolved under the existing at-most-once claim policy; this bridge does not
redispatch it or promise crash-proof exactly-once side effects.

## Receipt and runtime

The durable run stores the registry binding and inputs in its exact execution
argv, together with the source manifest. Worker output stores a digest-linked
result or error. `runnable receipt` assembles these retained records into JSON:

- Namespace, repo ID, runnable/version IDs, source digest, source path and entrypoint.
- `delivery.kind: tracked-run-inline-source` and its exact file digest.
- `execution.kind: managed-host-run` and the run ID. This is not a queue invocation.
- Actual server-bound host/enrollment/machine identity and worker-reported hostname/PID.
  A CP worker ID is included only if the server exposes it; it is never guessed.
- Requested runtime/adapter digest/timeout and observed Python implementation,
  version and executable; terminal status, exit code, JSON result or error.

Both `registrySnapshotId` and `executionSnapshotId` are explicitly `null`: this
slice delivers the immutable module, not a repository archive or CP snapshot.
Versions binding a registry archive snapshot are rejected, not translated into
an unrelated execution snapshot. Repo identity describes the registered project;
it does not claim the delivered bytes came from a fetched Git tree.

Runtime is `uv run --offline --no-project --no-python-downloads --python python3
python -I -S ...`. It uses the worker's existing Python, disables project/site
setup, and records the actual resolved interpreter. No interpreter or dependency
is downloaded. There is no cross-host runtime replay guarantee. Inputs are capped
at 16 KiB, results at 128 KiB, and the existing source manifest limit is 1 MiB.
User prints go to stderr; adapter result records go to stdout. Exceptions,
unsupported async/generator returns and non-JSON results fail the execution.

The binding is verified by the CLI and worker adapter; it is not a new
server-issued registry provenance attestation. Normal run receipts/logs remain
owner-authorized. This adapter is not a security sandbox for Python code.
Agent execution, multi-module/archive delivery, dependency installation,
provisioning and generalized relaunch remain outside this slice.

## Copy-paste acceptance from the source checkout

After `pnpm install --frozen-lockfile`, use an existing owned target/enrollment:

```bash
pnpm exec tsx examples/registered-udf/demo.ts \
  --target geyang/aws/ge-cpu-20261009 \
  --enrollment-id 6ac9961b87b6b2979ecfaf3b \
  --request-id registry-bridge-20261015-01
```

This task-owned fixture registers A, edits the local file to B, deliberately loses
one real accepted submission response, recovers the same run, verifies A returns
`{"version":"A","sum":42}`, and checks a terminal retry returns that run too.
The fixed request ID intentionally recovers the recorded demonstration rather
than launching another process. Use a new deliberate ID only for a new experiment.
It retains registry/run evidence and removes only its temporary local files.

Actual acceptance on October 15, 2026: managed host-run
`geyang/6ad08163f65936f6c41ab689`, succeeded, CPython 3.12.3 at `/usr/bin/python3`,
worker machine `host-1d796efb5a9edb3acd60ac9463d4e209`, result A/42. The complete
receipt and regression scope are in `examples/registered-udf/receipt.json` and
its README in the source repository. The original evidence was captured from the source build against the deployed
service; distribution acceptance is recorded separately for each release.
