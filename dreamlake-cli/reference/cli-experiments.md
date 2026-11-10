<!-- generated from https://cli.dreamlake.ai/experiments.md at 0.119.0 4c56b6a6; do not edit -->

# Experiments

## Native project runs

The DreamLake-native backend stores new runs under a DreamLake project. These
commands require a server with native Experiments enabled and your existing
DreamLake login. The run key makes creation idempotent; inspect the run after an
uncertain write before retrying.

```bash cli-help="experiments runs list"
dl experiments runs list --namespace fortyfive --project research
```

```bash cli-help="experiments runs create"
dl experiments runs create trial_1 --namespace fortyfive --project research
```

```bash cli-help="experiments runs log"
dl experiments runs log "$RUN_ID" "training started" --level info --namespace fortyfive --project research
```

Archive hides a run from default lists while preserving its data. Restore makes
it visible again; neither operation deletes historical Dash data.

```bash cli-help="experiments runs archive"
dl experiments runs archive "$RUN_ID" --namespace fortyfive --project research
```

```bash cli-help="experiments runs restore"
dl experiments runs restore "$RUN_ID" --namespace fortyfive --project research
```

Runs can be moved to trash and restored without changing their archive state.
Lifecycle-enabled servers also allow running runs to be trashed; older servers require a terminal run. Historical Dash runs
remain on the old service.

```bash cli-help="experiments runs delete"
dl experiments runs delete "$RUN_ID" --namespace fortyfive --project research
```

```bash cli-help="experiments runs trash list"
dl experiments runs trash list --namespace fortyfive --project research
```

```bash cli-help="experiments runs trash restore"
dl experiments runs trash restore "$RUN_ID" --namespace fortyfive --project research
```

### Run data

These commands read and write one native run's data through the native
Experiments API of the selected project. Success prints the server's JSON.
Paged reads return one page and `nextCursor`; pass it to `--cursor` for the
next page. `--data` and `--metadata` read JSON from a file or `-` (stdin).

```bash cli-help="experiments runs show"
dl experiments runs show "$RUN_ID" --namespace fortyfive --project research
```

```bash cli-help="experiments runs status"
dl experiments runs status "$RUN_ID" COMPLETED --namespace fortyfive --project research
```

```bash cli-help="experiments runs params set"
echo '{"lr": 0.001, "batch": 64}' | dl experiments runs params set "$RUN_ID" --data - --namespace fortyfive --project research
```

`params get` reads and `params delete` removes all parameters of a run.

```bash cli-help="experiments runs metrics append"
dl experiments runs metrics append "$RUN_ID" train.loss --data points.json --namespace fortyfive --project research
```

```bash cli-help="experiments runs metrics rows"
dl experiments runs metrics rows "$RUN_ID" train.loss --limit 1000 --namespace fortyfive --project research
```

`--description`, `--tags` and `--metadata` on `metrics append` are stored
with the points only when that append creates the metric. `metrics list` lists a run's metrics, `metrics stats` shows one metric's point
count and metadata, and `metrics metadata` updates its `--description`,
`--tags` or `--metadata`.

```bash cli-help="experiments runs logs read"
dl experiments runs logs read "$RUN_ID" --level warn,error --search timeout --namespace fortyfive --project research
```

`logs append --data` appends up to 1000 `{timestamp, level, message}` entries.

```bash cli-help="experiments runs files upload"
dl experiments runs files upload "$RUN_ID" ./model.pt --prefix /checkpoints --tags best --namespace fortyfive --project research
```

```bash cli-help="experiments runs files download"
dl experiments runs files download "$RUN_ID" "$FILE_ID" --out ./model.pt --namespace fortyfive --project research
```

A download never overwrites an existing path and is removed if its bytes do not
match the file's checksum. `files list`, `files get`, `files update` and
`files delete` complete the file operations.

### Tracks

Tracks hold time-indexed entries (`{timestamp, ...data}`) on runs stored in
the native Dash store. `append` writes up to 10000 entries in one commit, and
`read` prints JSON or exports to a new file.

```bash cli-help="experiments runs tracks append"
dl experiments runs tracks append "$RUN_ID" robot/position --data entries.json --namespace fortyfive --project research
```

```bash cli-help="experiments runs tracks read"
dl experiments runs tracks read "$RUN_ID" robot/position --format mcap --out position.mcap --namespace fortyfive --project research
```

`tracks list` lists a run's tracks, and `tracks create` creates a track with an
optional `--description`, `--tags` or `--metadata`. For `--format mcap`, a topic
ending in `/` exports every track under it.

Run files use DreamLake's existing project file storage. Address the episode by
the run key you created; file upload uses your DreamLake login.

```bash
dl upload checkpoint.bin --episode research@fortyfive:trial_1 --to /models
```

## Historical Dash workspace binding

**Unreleased.** Requires the matching DreamLake and Dash server changes. These
commands have not been released or verified on a hosted deployment.

Use your existing DreamLake login and explicitly choose the DreamLake organization
namespace. An organization owner can discover eligible existing workspaces on the
managed Dash instance. No Dash URL or token is accepted or copied by this flow.
An identical organization name does not establish a binding.

```bash cli-help="experiments workspaces"
dl experiments workspaces --namespace fortyfive --json
```

Inspect the current binding, including its revision. Results contain stable
DreamLake and Dash namespace identifiers; a slug is only a discovery aid.

```bash cli-help="experiments binding"
dl experiments binding --namespace fortyfive --json
```

Select a unique slug or `namespaceId` returned by discovery. `connect` first
previews the selected target without changing anything. Review its `instanceId`,
`namespaceId`, current binding, and `expectedRevision`.

```bash cli-help="experiments connect"
dl experiments connect research --namespace fortyfive --json
# Apply only after reviewing the preview. Use its actual revision, not this example's 0.
dl experiments connect "$DASH_NAMESPACE_ID" --namespace fortyfive --instance-id "$DASH_INSTANCE_ID" --apply --expected-revision 0 --json
```

Apply requires the discovered stable `namespaceId` (`DASH_NAMESPACE_ID` above),
copied from the reviewed preview's `target.namespaceId`; slugs are preview-only.
Set `DASH_INSTANCE_ID` to its `target.instanceId`. Apply requires this explicit
instance ID so configuration changes cannot silently redirect the selection.
The server verifies the current user's Dash organization ownership
and the instance again at apply time. A stale revision fails rather than
overwriting another owner's change. Refresh and review after a conflict; do not
automatically retry with a newer revision.

To detach, review a separate preview and apply its revision. Detaching disables
the DreamLake binding without deleting remote experiments, changing Dash members,
or revoking SDK credentials. It remains available when remote discovery is down.
Detached rows keep their revision; only a namespace with no previous binding uses 0.

```bash cli-help="experiments disconnect"
dl experiments disconnect --namespace fortyfive --json
# Replace 1 with the revision returned by this preview.
dl experiments disconnect --namespace fortyfive --apply --expected-revision 1 --json
```

Success always emits a JSON receipt. With `--json`, errors emit
`{ok:false,error:{code,message,remediation}}` and exit nonzero. A rejected write
is not confirmation of its outcome: inspect `binding` before retrying after a
network interruption.

Binding administration preserves existing Dash workspaces for historical reads.
It does not move their data or grant Dash data access. New native runs use
DreamLake project permissions and storage.

## Transfer complete experiments

`dl experiments upload` and `download` use the interoperable `.dash` directory
format. They use your selected DreamLake environment and existing `dl login`;
they never send new data to the historical Dash service.

```bash cli-help="experiments upload"
dl experiments upload ./.dash --project 'fortyfive/research/*' --strict
```

```bash cli-help="experiments download"
dl experiments download ./experiment-copy --project fortyfive/research --experiment trial_1
```

Transfers include run folders/names, description, tags, metadata, Bindr names,
write protection, parameters, logs, metrics and run files. Both flat and directory
metric layouts are accepted. Protection is applied after the run's data and labels
are written. Files are checksum-verified and filenames preserve Unicode, quotes
and literal percent sequences. Downloads are installed only after every selected
section succeeds; `--overwrite` replaces a prior local run without appending its
data again. A failed replacement leaves the previous local copy intact.

Use `--dry-run` to inspect selection, `--target namespace/project/folder` to upload
under another directory, and `--skip-logs`, `--skip-metrics`, `--skip-files` or
`--skip-params` to omit sections. `--batch-size` controls log/metric batching;
downloads also accept `--max-concurrent-metrics` and `--max-concurrent-files`.
A failure exits nonzero and retains the state file. `--resume --state-file PATH`
skips fully completed runs for the same server, local root and target. A partially
written remote run can contain accepted appends: inspect it before repeating an
upload; resume is not transactional rollback or append deduplication.

Tracks are transferred separately as JSONL entries, or exported in a server format:

```bash
dl experiments upload --tracks pose.jsonl --remote-path fortyfive/research/trial_1/robot/pose
dl experiments download --tracks fortyfive/research/trial_1/robot/pose --format mcap --output pose.mcap
```

The `parquet` server format returns Arrow IPC bytes, preserving the existing
ML-Dash wire contract. A project/run selector can include folder paths or globs;
ordinary `--project namespace/project` selects all of that project's runs.

## Native writers and jobs

Writers are metadata identities used to mint short-lived recording sessions.
Create with a stable intent UUID; inspect before rotating or retiring an observed
generation. Retiring is permanent and does not stop a compute process.

```bash cli-help="experiments writers list"
dl experiments writers list --namespace fortyfive --project research
```

```bash cli-help="experiments writers create"
dl experiments writers create --namespace fortyfive --project research --idempotency-key "$INTENT_UUID" --run-id "$RUN_ID"
```

```bash cli-help="experiments writers inspect"
dl experiments writers inspect "$WRITER_ID" --namespace fortyfive --project research
```

```bash cli-help="experiments writers rotate"
dl experiments writers rotate "$WRITER_ID" --expected-generation 1 --namespace fortyfive --project research
```

```bash cli-help="experiments writers retire"
dl experiments writers retire "$WRITER_ID" --expected-generation 2 --namespace fortyfive --project research
```

Native jobs create their experiment run in this DreamLake project and dispatch to
your explicitly configured host. The manifest contains `requestId`, `target`,
optional `enrollmentId`, `execution: {kind: "uv-run", argv: ["script.py"]}`,
`source: {files: [{path, contentBase64, sha256, mode: 420}]}` and optional
`timeoutSeconds`. Files are explicit; no script or dependency is inferred from argv.
Keep the original manifest and request ID after an uncertain submission.

```bash cli-help="experiments jobs submit"
dl experiments jobs submit --spec job.json --namespace fortyfive --project research
```

```bash cli-help="experiments jobs list"
dl experiments jobs list --namespace fortyfive --project research
```

```bash cli-help="experiments jobs show"
dl experiments jobs show "$JOB_ID" --namespace fortyfive --project research
```

```bash cli-help="experiments jobs logs"
dl experiments jobs logs "$JOB_ID" --namespace fortyfive --project research
```

```bash cli-help="experiments jobs cancel"
dl experiments jobs cancel "$JOB_ID" --namespace fortyfive --project research
```

`show` returns the compute receipt and native experiment binding. Cancellation and
logs first verify the job belongs to the selected project. A job's SDK logging
context uses the worker broker; the compute receipt owns terminal status.
