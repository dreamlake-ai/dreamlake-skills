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

## Declare an EC2 account and region

An EC2 declaration names an account and region scope; it does not list, adopt, start, stop or terminate instances.

```json
{
  "version": 1,
  "name": "aws-east",
  "kind": "aws-ec2",
  "config": {
    "region": "us-east-1",
    "accountId": "123456789012",
    "credentialRef": {"namespace": "team", "entryName": "aws/provider"}
  }
}
```

`region` is required; `accountId` and `credentialRef` are optional. Raw AWS keys
are rejected before anything is sent. Register it with the same
`providers register` command.

Provider responses include `capabilities`: the resource unit (`instance` for EC2,
`allocation` for Slurm) and each operation with its target, effect and `state`.
EC2 `stop` keeps volumes while `terminate` destroys the instance; Slurm `cancel`
targets one allocation. `state` is `available` only when DreamLake implements
the operation. It does not mean the provider is reachable or that you may act.
In this version only Slurm `associate` is available. Legacy records report
`capabilities: null`.

## Declare a GCE project and zone

A Compute Engine declaration names a project and zone scope; it does not list, launch, start, stop or delete VMs.

```json
{
  "version": 1,
  "name": "gce-central",
  "kind": "gcp-gce",
  "config": {
    "project": "vision-research-01",
    "zone": "us-central1-a",
    "credentialRef": {"namespace": "team", "entryName": "gcp/provider"}
  }
}
```

`project` and `zone` are required; `credentialRef` is optional. Raw service
account keys are rejected before anything is sent. GCE capabilities use the
`instance` unit; `stop` keeps persistent disks while `delete` destroys the VM
and its auto-delete disks. None of them is available yet.

## Layer launch configuration

Launch configuration is layered with [JSON Layer](https://github.com/dreamlake-ai/json-layer)
files: the provider's layer, then any number of named layers in the order
you list them (`--layer` repeated, at most 16), then this request's layer.
Preflight resolves and validates; it never launches.

`provider.jsonl`:

```jsonl
// defaults for every launch on this account
{"instanceType": "t3.large", "imageId": "ami-0123456789abcdef0", "volumeGiB": 100}
["union", "securityGroupIds", "sg-0123456789abcdef0"]
```

`gpu.jsonl`:

```jsonl
{"instanceType": "g5.xlarge"}
["merge", "tags", {"team": "vision"}]
```

```bash
dreamlake providers register team --file aws-east.json --launch provider.jsonl --request-id aws-east-01
dreamlake providers layers create team/<provider-id> --name gpu --file gpu.jsonl --request-id gpu-01
dreamlake providers preflight team/<provider-id> --layer gpu
```

```json
{
  "valid": true,
  "launched": false,
  "launch": {"instanceType": "g5.xlarge", "imageId": "ami-0123456789abcdef0", "volumeGiB": 100,
             "securityGroupIds": ["sg-0123456789abcdef0"], "tags": {"team": "vision"}},
  "sources": [{"path": "instanceType", "layer": "layer:gpu", "line": 1}, "..."],
  "errors": []
}
```

More commands:

```bash
dreamlake providers preflight team/<provider-id> --layer gpu --layer spot --file request.jsonl
dreamlake providers layers list team/<provider-id>          # state: valid | invalid | retired
dreamlake providers layers update team/<provider-id> --layer <layer-id> --revision 1 --file gpu.jsonl --request-id gpu-02
dreamlake providers layers retire team/<provider-id> --layer <layer-id> --revision 2 --request-id gpu-03
dreamlake providers launch team/<provider-id> --file provider.jsonl --revision 1 --request-id launch-02
dreamlake providers launch team/<provider-id> --clear --revision 2 --request-id launch-03
```

- Layers are not pinned to a provider revision. `layers list` shows when a
  provider change makes a layer invalid.
- Layer files are checked locally first; a syntax error names its line.
- EC2 refuses `userData`, Slurm refuses `script`, and GCE refuses boot-script
  metadata: enrollment is injected at launch, and secrets are not stored.
- Kubernetes providers do not support launch layers.

## Launch EC2 instances

An `aws-ec2` provider launches instances with credentials from your Vault.
`credentialRef` names a Vault entry holding an AWS credentials file;
`profile` picks one of its profiles.

```json
{
  "version": 1,
  "name": "aws-east",
  "kind": "aws-ec2",
  "config": {
    "region": "us-east-1",
    "credentialRef": {"namespace": "team", "entryName": "aws/credentials", "profile": "dev"}
  }
}
```

```bash
dreamlake providers instances launch team/<provider-id> --layer gpu --count 4 --request-id train-01
dreamlake providers instances list team/<provider-id>
dreamlake providers instances stop team/<provider-id> --instance i-0123456789abcdef0 --request-id stop-01
dreamlake providers instances start team/<provider-id> --instance i-0123456789abcdef0 --request-id start-01
dreamlake providers instances terminate team/<provider-id> --instance i-0123456789abcdef0 --request-id term-01
```

- Instances are billed from launch until terminated.
- A launch is refused before reaching AWS when preflight is invalid.
- Repeating a request ID returns the same instances; it never launches twice.
- `list`, `start`, `stop` and `terminate` act only on instances this provider
  launched (tag `dreamlake:provider`).
- Without enrollment options, launched instances are not enrolled. To install
  Nymph automatically, pass a host name; an unused service account is optional:

```bash cli-help="providers instances launch"
dreamlake providers instances launch team/333333333333333333333333 --service-account 0123456789abcdef01234567 --host-name team/dev/worker --unix-user ubuntu --request-id worker-01 --json
```

Automatic enrollment requires `--count 1` and a server supporting machine
bootstrap. Each Nymph gets its own account, created automatically when `--service-account`
is omitted; `--lakeshore-id` optionally selects a
namespace control plane. The backend selects the installer version and injects
one-use bootstrap material; no human token is copied to the host. A launch
receipt is not online/readiness evidence. See [Service accounts](service-accounts.md)
for grants, retry behavior and revocation.

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
