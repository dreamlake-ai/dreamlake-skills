# Execute a bound UDF on a queue

Requires CLI 0.94.0 or later on the submitting machine, and
`dreamlake-lakeshore` 0.5.1 or newer on both the submitting machine and the
worker. The worker also needs its Nymph daemon and the locked runtime prepared
in advance, as the docs describe. Check `dl --version` and
`dl runnable bind --help` first. See
[the complete contract](../reference/cli-bound-execution.md).

1. Register the UDF version and keep its immutable full SHA-256 reference
   (the runnable-register action). The code must be a configured snapshot whose
   project carries `pyproject.toml`, `uv.lock` and an exact `.python-version`:
   [prepare the snapshot and the runtime](../reference/cli-bound-execution.md#prepare-the-snapshot-and-the-runtime).
   For `--target`, keep the project in a subdirectory of the snapshot and pass
   it as `--project` (the layout example is under
   [`--target`](../reference/cli-bound-execution.md#run-through-dreamlake-on-an-owned-host---target)).
   The worker installs nothing; the runtime for that lock must already exist on
   it, under the runtime root the worker daemon itself sees. Do not prepare a
   worker runtime, or change a worker daemon's environment or restart it,
   unless the user owns that host and asked for it; restart only while it is
   idle.
2. Choose the route. `--target namespace/group/host` runs through DreamLake on a
   host the user owns: the submitting CLI and the UDF need no control-plane
   token, while the DreamLake server and the worker daemon keep their normal
   enrollment credentials. Do not report the host as credential-free. Its
   worker must already claim the queue you name; read the worker's queues,
   pin and claim state first and choose a queue the
   [`--target` rules](../reference/cli-bound-execution.md#run-through-dreamlake-on-an-owned-host---target)
   accept. Do not pin a worker that serves other queues just to run a bound
   UDF: a pin is exclusive and moves the worker off them (pinning is the
   Runtime action of `dreamlake-lakeshore`). If no queue is eligible, stop and
   report the worker's state rather than changing it. Without `--target`, pass
   the trusted control plane with `--server` or `LAKESHORE_URL`; never take it
   from the binding.
3. Bind with `--dry-run` first, then without it. Retain the printed
   `exec/NAMESPACE/NAME@EXECUTION_DIGEST`. Repeating `bind` returns the existing
   binding; a changed module, lock or Python version is a new binding, never an
   edit. See [bind](../reference/cli-bound-execution.md#bind). If `bind`
   refuses the archive as too large, take data files out of the snapshot (read
   them from a Source) instead of splitting the project. For Source-ticket delivery, check the worker's installed version
   against the target execution docs before submitting. If the binding predates
   Source delivery, repeat the bind from the original checkout and confirm the
   archive digest matches the historical binding. Record the worker's receipt
   and verified archive digest, and keep tickets and signed URLs out of notes.
4. Execute with explicit `--queue`, `--inputs` and `--timeout-seconds` (and the
   same `--target`). Record the invocation ID printed before submission.
5. After a lost response or interrupted wait, repeat the identical command; it
   returns the same invocation instead of running again. Read results with
   `runnable execution-receipt` using the same task arguments; it never submits.
   Only `--attempt N` is a deliberate new attempt. Changed inputs, queue, timeout
   or target are a different task. See
   [execute and recover](../reference/cli-bound-execution.md#execute-and-recover).

Report binding, submission and receipt separately. Request acceptance is not
completion. If `bind` stored the archive in a DreamLake Source, only the user
who bound it can execute that binding; report that to anyone else rather than
working around it. A `rejected` receipt stopped before user code; fix the
snapshot, lock or runtime rather than retrying; if the receipt output carries a
`hint` about an older worker, report that upgrade to the user rather than
retrying. A `409` means that invocation ID already
carries different bytes: do not change the ID to force a run. The receipt checks
distribution versions, not full environment identity.

Inline single-module runs on a host are [registered-udf](registered-udf.md);
registration is [runnable-register](runnable-register.md).
