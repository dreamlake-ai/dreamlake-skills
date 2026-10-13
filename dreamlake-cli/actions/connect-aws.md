# Connect AWS to DreamLake

Use this guide for “connect AWS to DreamLake,” a first-time AWS worker setup,
or the curated DreamLake starter recipe. For ordinary CLI login use
[setup](setup.md); for a specifically requested managed provider launch use
[machines](machines.md). Do not convert an existing project's requested flow
into a different provisioning method.

This guide is bundled starting in CLI 0.54.0. Read [Connect AWS](../reference/connect-aws.md) and the
[public starter archive](https://cli.dreamlake.ai/recipes/aws-starter-1.0.0.tar.gz)
with its [provenance manifest](https://cli.dreamlake.ai/recipes/aws-starter-1.0.0.json).
Verify the archive SHA-256 before extraction. GitHub source access is optional.
The recipe and its Recipes Bindr are reviewed code/instructions, not a provider
configuration database. Prefer the installed `aws-jump-worker` template and
actual CLI commands; do not build another registry or guess a missing setup API.

Inspect the selected environment, namespace, owned provider and existing Personal
AI host first. Reuse that controller's valid enrollment. The default is an
external controller plus a distinct EC2 worker, with `reuse-retain` execution
and retained results. An optional second EC2 jump requires an explicit choice.
Do not re-enroll, migrate or reconfigure the existing controller to satisfy the
example. Reuse a suitable existing worker enrollment too.

Ask only for unresolved inputs: AWS account/region and approved credential
reference/profile; exact existing worker or authorized new-worker/image choices;
state backend and retained results locations; namespace/provider/controller;
required tools and spending/execution scope. Read known choices from reviewed
project files and authenticated records. A hostname or label is not ownership.
Never request secret values in chat, Terraform inputs or user data.

Run `dreamlake provider create -n NAME --provider aws-jump-worker --json`.
Read its AGENT.md, ADAPT.md and schemas. Fill terraform.tfvars.json and backend.json
in the returned terraform directory. Defaults are `reference-existing` and
`controller_mode=external`. A new worker uses `mode=create`; preserve external
controller mode unless the user explicitly wants dual EC2. `create` never applies.

Drive `create --continue`, `plan`, and authorized `apply --yes` through `status`,
`blocking` and `nextAction`. Preserve the scaffold name/directory and edits.
`needs_input` is exit zero; resolve missing facts, and stop repeated identical
blocks instead of retrying blindly. Plan contacts AWS and the locked backend.
Review its detailed diff privately; summary counts are not the full plan.
A nextAction containing --yes is not spending permission. Continue within an
already authorized cost scope; otherwise finish the reviewable plan before
requesting the particular missing paid action. Paid AMI builds and backend creation
are separate cost decisions; a local container build uses the existing Docker
runtime and does not allocate AWS resources. This guide itself grants no
paid apply, destroy, instance lifecycle or workload authorization.

Use the recipe's reviewed image digest, dependency pins and tool manifest; its
Docker image is not
an AMI and does not install host tools. Keep enrollment keys, tokens and
cloud/vendor credentials out of all images. The normal setup uses the authenticated
Nymph process runner with uv/tracked_runs. Docker/Kubernetes are optional,
explicit execution profiles; a container-capable image does not automatically
bridge them into the Launch setup or change an existing daemon. Kubernetes
hostPath requires the selected path/data on the execution node; it is not
shared multi-node storage. The optional SDK smoke needs a separate CP URL,
namespace, scoped client token and approved existing queue; personal DreamLake
login/provider metadata do not provide those credentials. Keep their values
private. Configure/install from the recipe and submit smoke work only within
authorized execution scope. Report an unsupported adapter as a gap, not a success.

After infrastructure, follow the packaged terraform/ENROLLMENT.md. Generic
provider connect/disconnect is unsupported for this template. Use hosts status
first; enroll only missing/explicitly replaced identities through authenticated
SSH stdin bootstrap, verified host keys and a stable request ID. Recover the
same request, and distinguish pending, online, terminal-ready and workload-ready.
Do not copy a personal login to a daemon or treat an AMI identity document as
first-enrollment authority.

Use the packaged mapper with real fresh provider/enrollment/worker evidence.
Never substitute EC2, Host, Enrollment, machine or Worker IDs for one another.
A candidate file is not applied provider setup. Use the existing deployed setup
flow and revision checks; if absent, report exactly that gap. Verify the exact
owned worker and a small authorized workload before claiming the connection
complete. Preserve results and report separate readiness receipts.

Use locked/versioned encrypted S3 as authoritative state. Vault may hold
nonsecret references and explicitly selected encrypted-at-rest snapshots;
revision/idempotency is not Terraform backend locking. No automatic scan, state
upload, raw log indexing, migration or cleanup. For user-requested Notes updates,
use [Notes](notes.md) with fresh normal read output/revision; write authored
progress only, never state, secrets or raw terminal output. Uploads, artifacts,
workflows and explicit SDK integration retain their own task boundaries.
