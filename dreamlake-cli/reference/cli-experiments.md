<!-- generated from https://cli.dreamlake.ai/experiments.md at 0.112.1 2a2fef0; do not edit -->

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

Terminal runs can be moved to trash and restored without changing their
archive state. Running runs must finish before deletion. Historical Dash runs
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
