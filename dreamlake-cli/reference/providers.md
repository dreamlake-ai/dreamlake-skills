# Provider registrations

`dreamlake providers` stores provider configuration in DreamLake and associates it with your host enrollment. These commands require a server with the provider registration API from [workspace PR #321](https://github.com/dreamlake-ai/dreamlake-workspace/pull/321). Added in CLI 0.14.0; the corresponding Python API is in 0.11.0.

## Register a provider

Save this declaration as `provider.json`. Replace the cluster, partitions and Vault entry with your values. Omit `credentialRef` if no reference is needed; never put credential contents in the declaration.

```json
{
  "version": 1,
  "name": "research-slurm",
  "kind": "slurm-ssh",
  "config": {
    "cluster": "research",
    "partitions": ["cpu"],
    "credentialRef": {"namespace": "team", "entryName": "research-ssh"}
  }
}
```

```bash
dreamlake providers register team --file provider.json \
  --request-id research-register-001 --json
dreamlake providers list team --json
dreamlake providers show team/research-slurm --json
```

Keep the returned `resource.id`, `resource.revision`, `operationId` and your request ID. Every write requires an explicit request ID. Repeating the same request returns its original receipt. Reusing the ID with a different payload returns a conflict.

## Associate your Slurm enrollment

Save an association as `association.json`, using your enrollment ID and the provider revision. Paths must be literal absolute paths. `submissionRoot` is the shared directory as seen by the submission host; `computeRoot` is that directory as seen by the compute node. Executable paths must be valid on compute nodes.

```json
{
  "providerRevision": 1,
  "enrollmentId": "0123456789abcdef01234567",
  "runner": {
    "kind": "slurm",
    "partition": "cpu",
    "staging": {
      "submissionRoot": "/export/work/alice",
      "computeRoot": "/work/alice"
    },
    "environment": {
      "uvExecutable": "/opt/tools/uv",
      "pythonExecutable": "/usr/bin/python3"
    }
  }
}
```

Replace `PROVIDER_ID` below with the registration's `resource.id`.

```bash
dreamlake providers associate team/PROVIDER_ID --file association.json \
  --request-id research-associate-001 --json
dreamlake providers status team/PROVIDER_ID --json
```

The enrollment must belong to you in the same namespace. The partition and optional account must be permitted by the declaration. Status reports `not_checked` until readiness checks exist; registration does not test SSH, paths or executables, provision machines, or submit jobs. Kubernetes declarations are accepted, but Kubernetes runner associations are not yet supported.

## Recover a missing response

After a timeout or lost connection, look up the receipt using the original request ID:

```bash
dreamlake providers operations find team --request-id research-register-001 --json
dreamlake providers operations show team/OPERATION_ID --json
```

The client does not retry writes automatically. If no receipt is found, retry the original command with exactly the same input and request ID. A receipt is a historical snapshot; use `status` for current state. Receipts are visible to their creating user.

## Retire configuration

Use the current revision of the resource being retired. To retire only an association, include its ID and revision:

```bash
dreamlake providers retire team/PROVIDER_ID --association ASSOCIATION_ID \
  --revision 1 --request-id research-association-retire-001 --json
dreamlake providers retire team/PROVIDER_ID \
  --revision 1 --request-id research-provider-retire-001 --json
```

Retirement changes metadata. It does not stop jobs, remove hosts or delete Vault entries. Retire associations separately when you want their records marked retired. Declarations and associations are immutable in this version; editing declarations and upgrading legacy provider records are not yet supported.

## Provider checks and placed runs (unreleased)

Requires the server API in [workspace PR #389](https://github.com/dreamlake-ai/dreamlake-workspace/pull/389)
and a tracked Slurm worker. These client additions are not released yet. Replace
the provider and association IDs below with your owned association.

```bash
dreamlake providers check team/aaaaaaaaaaaaaaaaaaaaaaaa \
  --association bbbbbbbbbbbbbbbbbbbbbbbb --revision 1 \
  --request-id probe-001 --json

dreamlake providers status team/aaaaaaaaaaaaaaaaaaaaaaaa --json

dreamlake run --target team/lab/host \
  --provider-id aaaaaaaaaaaaaaaaaaaaaaaa \
  --association-id bbbbbbbbbbbbbbbbbbbbbbbb --association-revision 1 \
  --cpus 4 --memory-mib 8192 --gpus 0 \
  --include train.py --request-id train-001 --no-wait --json \
  --uv-run train.py
```

The explicit check submits a small Slurm job (1 CPU, 512 MiB, no GPU, 120-second
CP timeout) and returns a run receipt. Inspect it with `dreamlake runs status`
or cancel it with `dreamlake runs cancel`, using `team/<run-id>`. Status reads do
not submit checks. Wait for association readiness before submitting the workload;
a pending or failed check does not authorize placement.

All placement and resource flags precede `--uv-run`; provider placement does not
support `--uvx`. Omitted resources default to 1 CPU, 512 MiB and no GPU. Readiness
lasts 15 minutes and verifies submission/environment access, not reserved capacity
or GPU isolation. Starting a new check supersedes previous evidence.

After a lost check response, repeat the identical check with the same request ID.
Checks use run receipts, not `providers operations`. Run retries also require the
same inputs and request ID; changing resources conflicts. No write is automatically
retried. This draft still needs paired real-server and live-worker acceptance.
