# Tracked host runs

`dreamlake run` submits a persistent run to an enrolled host through the authenticated DreamLake API. The server and nymph must support tracked runs, the enrollment must be online, and the target must have `uv`. This client change does not deploy those services. Host enrollment and resource provisioning are separate steps.

```shell
dreamlake run --target fortyfive/bos14/bos14-ctrl \
  --include train.py --include pyproject.toml \
  --request-id train-trial-001 \
  --uv-run train.py --epochs 10

dreamlake run --target fortyfive/bos14/bos14-ctrl --no-wait \
  --uvx --from ruff ruff --version
```

Put every DreamLake option before `--uv-run` or `--uvx`. The selector consumes all remaining arguments verbatim, including `--json`, `--help`, and `--`. Include each source file explicitly with `--include`; the CLI does not infer the script, scan Git, recurse directories, or include hidden files automatically. Paths must be relative regular files without symlinks or traversal. The limit is 100 files and 1 MiB of decoded content.

The default waits for a terminal receipt and streams stdout and stderr. `--no-wait` returns after submission. `--json` produces a JSON receipt; read logs separately. A generated request ID is printed before submission in human output. For retryable automation, supply your own `--request-id` and reuse the same payload; a changed payload with that ID is rejected. If a wait is interrupted, the remote run continues. A transport failure does not prove that submission failed.

```shell
dreamlake runs status fortyfive/RUN_ID --json
dreamlake runs logs fortyfive/RUN_ID --json
dreamlake runs logs fortyfive/RUN_ID --cursor CURSOR --json
dreamlake runs cancel fortyfive/RUN_ID --json
```

Log requests return one page. JSON pages contain `entries` with base64 bytes, `nextCursor`, and `done`; repeat using the cursor until done. Human output writes bytes directly to their original streams. Cancellation records an intent; `cancel_requested` does not mean the process has stopped. Inspect the terminal receipt. `--timeout-seconds` sets a remote deadline from 1 to 86400 seconds (default 3600). Use `--enrollment-id` before the selector when a host has multiple eligible enrollments.

## Integration verification

Maintainers can run `node scripts/test-runs-integration.mjs protected-env.json /path/to/nymph` after `pnpm build`. The protected config contains `remote`, `namespace`, `token`, `outsiderToken`, and `lakeshoreId` for an isolated loopback server. The driver uses real server persistence, control-plane HTTP, nymph, and `uv`; only SSH and user-systemd transport use local adapters. It also downloads a `ruff` tool for the `uvx` check. It stops its nymph and removes its temporary files afterward. This is not a live network-SSH test or a deployment check.

See the repository's `scripts/RUNS_INTEGRATION.md` for a copy-paste configuration generator, prerequisites, an explicit remote-test-server option, and cleanup instructions.

## Provider placement (unreleased)

See [provider checks and placed runs](/providers/) for the explicit check, association
and resource flags. This requires the draft server API in workspace PR #389.

## Private repository setup (requires an enabled compatible server)

Private setup delegates only reviewed vault entry IDs, exact revisions and selections to the enrolled host. It uses a pinned public HTTPS repository and `uv-lock` dependencies. The server controls allowed repository origins. Setup contains metadata only: never include credential values, access keys or credential-bearing URLs. This client interface does not enable the server feature or prove hosted availability.

```json
{
  "repository": "https://github.com/example/task.git",
  "commit": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
  "destination": "repo",
  "dependencies": "uv-lock",
  "mappings": [{
    "id": "api", "entryId": "REVIEWED_ENTRY_ID", "revision": 1,
    "valueShape": "map", "selection": {"kind": "fields", "names": ["token"]},
    "output": {"kind": "env", "name": "SERVICE_TOKEN"}
  }]
}
```

Replace the illustrative repository, commit, entry and enrollment with reviewed values. CLI options precede the execution selector:

```shell
dreamlake run --target alice/research/host --enrollment-id REVIEWED_ENROLLMENT_ID \
  --setup setup.json --allow-vault-delivery --request-id research-check-001 \
  --no-wait --uv-run python verify_service.py
dreamlake runs status alice/RUN_ID --json
dreamlake runs cancel alice/RUN_ID --json
```

```python
run = client.runs.submit(
    "alice/research/host", enrollment_id="REVIEWED_ENROLLMENT_ID",
    kind="uv-run", argv=["python", "verify_service.py"],
    setup=reviewed_metadata, allow_vault_delivery=True,
    request_id="research-check-001", timeout_seconds=3600,
)
status = client.runs.status("alice", run["id"])
client.runs.cancel("alice", run["id"])
```

Private setup rejects inline includes, provider placement and `uvx`. Python never reads a setup file implicitly or prompts. CLI reads only the explicitly named bounded metadata file. Status reports mapping progress; private workload logs are discarded at the source. Reuse the exact request ID and payload after an uncertain submission; changing revisions requires a new reviewed request. Cancellation intent is not proof that a remote process stopped. Mapping retry is not implemented.

## Discover server support

Discovery requires account authorization. It reports server support and limits;
it does not assert that an enrolled host is online or authorized for a run.
Private setup remains subject to fresh checks when submitted.

```shell
dreamlake runs capabilities alice --json
```

```python
capabilities = client.runs.capabilities("alice")
```

Production activation remains blocked pending the reviewed/live-tested private-runner termination-refusal fix. Server capability discovery is not a deployment-readiness guarantee.
