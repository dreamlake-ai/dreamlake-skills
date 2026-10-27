<!-- generated from https://cli.dreamlake.ai/connect-aws.md at unknown; do not edit -->

# Connect AWS to DreamLake

Ask your agent **“connect AWS to DreamLake”** to start with the curated AWS
recipe. The default arrangement keeps your existing Personal AI computer as
the controller and connects a distinct EC2 worker. It reuses owned enrollments
and retains existing resources and results. A second EC2 controller is an
explicit option, not a prerequisite.

The [public starter archive](https://cli.dreamlake.ai/recipes/aws-starter-1.0.0.tar.gz)
and its [provenance manifest](https://cli.dreamlake.ai/recipes/aws-starter-1.0.0.json)
provide the reviewed recipe without requiring GitHub access. The
[Recipes Bindr](https://dreamlake.ai/geyang/dreamlake?bindr=6acc03033b0d79eacb518ed5)
provides its human-readable entry point. Contributors with repository access can
also inspect [the source](https://github.com/dreamlake-ai/provider-setups/tree/main/04_dreamlake_starter).
The manifest records the source revision; verify the archive before extraction.
The CLI itself packages the underlying Terraform module as `aws-jump-worker`.
These recipes are code and instructions, not a replacement for DreamLake's
provider configuration, enrollment or runtime records.

In a new directory, download and verify the selected recipe using Python 3:

```bash file="terminal"
mkdir aws-starter-recipe
cd aws-starter-recipe
curl -fSLo aws-starter-1.0.0.tar.gz https://cli.dreamlake.ai/recipes/aws-starter-1.0.0.tar.gz
curl -fSLo aws-starter-1.0.0.json https://cli.dreamlake.ai/recipes/aws-starter-1.0.0.json
python3 - <<'PYVERIFY'
import hashlib, json, pathlib
manifest = json.loads(pathlib.Path("aws-starter-1.0.0.json").read_text())
actual = hashlib.sha256(pathlib.Path("aws-starter-1.0.0.tar.gz").read_bytes()).hexdigest()
if actual != manifest["sha256"]:
    raise SystemExit("Recipe checksum mismatch; do not extract or execute")
print("Recipe checksum verified")
PYVERIFY
tar -xzf aws-starter-1.0.0.tar.gz
```

Read `04_dreamlake_starter/README.md` before running the recipe. Keep your
instance/account-specific configuration in your project, outside the published
archive. A checksum proves matching download bytes, not runtime readiness.

Use CLI 0.54.0 or newer for this bundled task guide. The underlying Terraform
template and Vault state tools require 0.49.0+. These enrollment examples need
0.53.0+; browser terminal support
also needs Nymph 0.1.11+ and the matching deployed APIs. Check your installed
version and help. Updating the executable does not overwrite your installed
agent skill: review local edits before updating that skill.

```bash file="terminal"
curl -fsSL https://dl.dreamlake.ai/install.sh | bash
dreamlake --version
dreamlake login
dreamlake skill install --agent codex
# Or use --agent claude for Claude Code.
dreamlake auth env list
dreamlake providers --help
dreamlake hosts enroll --help
```

See [installation](cli-installation.md) and [authentication environments](cli-environments.md)
if the CLI or intended personal login is missing. Machine credentials and your
personal login are separate; do not copy a personal token onto the worker.

## Required execution server

New provisioning and workload launches must run through the user's explicitly
configured launch server and its appropriate IAM role. Verify that selection
before proceeding; an existing controller enrollment or Vault credential reference
does not by itself establish it. Do not use control-plane/service IAM, ambient
service credentials, an operator Vault IAM user or direct hosted-backend provider
execution. If routing is missing, stop new launches and preserve existing resources;
read-only inspection can continue. See the
[launch boundary](cli-providers.md#required-launch-boundary) for implementation limits.

## Supply only the missing decisions

An agent should inspect the selected project and authenticated records first,
then ask for the facts it cannot establish. Preserve an existing choice instead
of creating another provider, enrollment, state key, or instance during a retry.

| Decision | What to supply or verify |
| --- | --- |
| DreamLake destination | Your environment, namespace, existing provider ID/revision if present, and existing Personal AI host/enrollment. |
| AWS scope and access | Exact account and region, explicitly user-configured launch server and its appropriate IAM role. Verify the runtime identity; do not substitute an operator Vault IAM user. Never paste secret values into the recipe. |
| Worker | An exact existing EC2 instance ID for reuse, or an explicitly chosen new worker size, pinned AMI, availability zone, key-pair name, network/IAM and storage inputs. |
| State and results | Existing S3 state bucket/key/region/expected owner with locking, encryption and versioning; a retained results bucket/prefix. |
| Workload and cost scope | Required tools, CPU/GPU needs, and whether paid AMI building, backend creation, worker provisioning and a small verification run are authorized. |

A request to inspect or prepare a setup permits scaffolding and validation; it
is not a request to spend on a managed AMI build or new machines. A local
container build uses your existing Docker runtime; it is not an AWS allocation. If the user has
already authorized a specific paid scope, carry it through that scope rather
than asking for the same permission again. Keep changes outside it separate.
Do not infer ownership from a hostname, Name tag, instance label or provider name.

## Select the existing provider, or register its declaration

List your namespace's provider records and inspect the exact selected one.
These plural `providers` commands use the authenticated product API; the singular
`provider create --provider ...` command below creates local scaffold files.

```bash file="terminal"
dreamlake providers list YOUR_NAMESPACE --json
dreamlake providers status YOUR_NAMESPACE/EXISTING_PROVIDER_ID --json
```

If your intended account/region has no suitable owned record, prepare an
`aws-ec2` declaration using the [providers reference](cli-providers.md#declare-an-ec2-account-and-region).
Include the selected account and region and, if needed, a Vault entry reference;
never include AWS key contents. Within the requested registration scope:

```bash file="terminal"
dreamlake providers register YOUR_NAMESPACE --file provider.json \
  --request-id aws-starter-provider-001 --json
```

Keep the returned ID and revision. Reuse the same request ID and identical
input after a lost response; inspect `providers operations find` before creating
another record. Registration does not adopt Terraform resources or make a
worker ready. Do not use the scaffold's internal provider.json as this API
declaration; it is template provenance with a different schema.

## Scaffold, fill inputs, and plan

Choose one deliberate scaffold name and keep using it. `create` is local and
does not invoke Terraform or register a provider in the product.

```bash file="terminal"
dreamlake provider create -n aws-starter --provider aws-jump-worker --json
```

Open `AGENT.md`, `ADAPT.md`, `inputs.schema.json` and `backend.schema.json` in
the returned directory. Fill `terraform/terraform.tfvars.json` and
`terraform/backend.json`; do not replace the directory on reentry.

The shipped inputs use `mode: "reference-existing"` and
`controller_mode: "external"`. Supply the exact worker ID and retained results
bucket; the external controller has no invented EC2 jump ID. If the user
chooses a new worker, select `mode: "create"`, fill the `create` object, and
remove or null the inactive `existing` object. Keep `controller_mode: "external"`.
Choose `controller_mode: "ec2"` only for an explicitly requested second EC2
controller, with its own distinct jump inputs.

```bash file="terminal"
dreamlake provider create -n aws-starter --continue --json
dreamlake provider plan -n aws-starter --json
```

Read `status`, `blocking` and `nextAction`. `needs_input` exits zero: edit the
reported file and rerun the returned command. JSON next actions preserve the
scaffold directory. If the same unresolved inputs recur, obtain the missing
facts instead of looping. Reentry preserves edits and only repairs missing
packaged files; conflicting paths and symlinks are refused.

`plan` runs the typed offline scan first, then initializes the selected backend,
validates and plans. It can contact AWS and acquire a state lock. It does not
apply. Review the detailed plan locally in the protected Terraform directory;
the lifecycle JSON reports change counts, and raw provider diagnostics are
suppressed because they can contain secrets. Never paste raw state or plan
output into Notes, a Bindr, or a chat.

For a from-zero account, the scaffold includes `terraform/modules/state-backend`
for separately authorized backend creation. The main plan needs that backend
to exist. The CLI does not silently migrate an existing backend or create a
replacement when initialization fails.

## Choose the worker image and execution profile

Select an existing reviewed worker AMI with the prerequisites in the scaffold's
ENROLLMENT.md. The curated recipe builds a **container image**, not an EC2 AMI;
its tools do not automatically appear in the host's process-runner environment.
An optional separate AMI build is its own billable action and is not part of
this starter's offline validation. Never bake an enrolled host identity,
bootstrap grant, private SSH key or cloud/vendor credentials into either image.

The normal Terraform enrollment path uses the existing Nymph process runner
with `uv` and tracked-run support. Docker and Kubernetes are separately selected
SDK execution profiles. The container includes Python, the pinned
`dreamlake-lakeshore` SDK, Git, curl and CA certificates. Use the recipe's
base-image digest, dependency hashes and tool manifest when choosing those
profiles; configuration generation installs or
starts no daemon and does not change the existing controller or Launch worker.

## Apply only the chosen scope

After reviewing the plan and confirming it is within the user's authorization:

```bash file="terminal"
dreamlake provider apply -n aws-starter --yes --json
```

`--yes` performs the action; a returned command containing `--yes` does not
supply authorization. Reconcile a failed or interrupted apply through its
returned action and Terraform's backend before retrying. Do not force-unlock,
destroy retained resources, or create another instance to recover a lost response.

An `applied` result means infrastructure work finished. It does not mean that
hosts are enrolled, inventory is adopted, provider setup is ready, or a job ran.
Generic `provider connect` and `provider disconnect` do not manage this template.

## Reuse enrollments, then verify the exact worker

Read the existing controller and worker host status first:

```bash file="terminal"
dreamlake hosts status YOUR_NAMESPACE/EXISTING_CONTROLLER --json
dreamlake hosts status YOUR_NAMESPACE/EXISTING_WORKER --json
```

Reuse a suitable owned enrollment on each role. Do not install another daemon
or rerun enrollment on an already connected Personal AI computer. For a worker
that lacks the required enrollment, follow `terraform/ENROLLMENT.md`: verify
SSH transport and host keys, the Unix account, systemd user manager and linger,
then use the authenticated enrollment flow with a stable request ID. The short
bootstrap grant travels over SSH stdin and does not enter Terraform.

```bash file="terminal"
# Only for a worker that needs enrollment, within the authorized setup scope.
dreamlake hosts enroll --name YOUR_NAMESPACE/aws-starter/worker \
  --ssh '-F /private/operator-ssh-config dreamlake-worker-enroll' \
  --lakeshore-id YOUR_LAKESHORE_ID --nymph-version v0.1.17 \
  --request-id aws-starter-worker-001 --no-save-credentials --json
```

The SSH alias and placeholders above must come from the reviewed transport and
selected deployment. Retry an interrupted enrollment with the same request ID
and identical inputs. `pending` is not online. An existing Nymph binary is
reused; `--nymph-version` is not an upgrade switch. Report browser terminal
readiness separately from enrollment and workload execution.

Use the packaged `terraform/tools/map_setup.py` and schemas as described in
`terraform/ENROLLMENT.md`. They join the named `setup_infrastructure` output
with the actual provider scope and fresh enrollment evidence. Infrastructure
IDs, Host IDs, Enrollment IDs, machine IDs and Worker IDs are different fields.
The hosts status API does not supply every worker-binding field; obtain missing
fields through the existing authorized control-plane read or deployed setup
flow. Do not manufacture them from a hostname or another identifier.

The mapper produces a local candidate; it does not authenticate evidence or
write product setup. Use the existing deployed provider setup flow for its
revision-checked application and readiness checks. This CLI does not add a
`providers setup` command, new registry, automatic scheduler or runtime adapter.
If that deployed flow or exact binding is unavailable, report the candidate and
the specific missing step rather than calling the connection complete.

For the default process-runner path, verify a small workload only when execution
on that exact worker is authorized. In a new local test directory:

```bash file="terminal"
printf 'print(20 + 22)\n' > hello.py
dreamlake run --target YOUR_NAMESPACE/aws-starter/worker --include hello.py \
  --request-id aws-starter-hello-001 --timeout-seconds 60 --uv-run python hello.py
```

Keep the run receipt and confirm the completed result is 42. Recover a lost run
through [run status and recovery](cli-runs.md) instead of submitting a new job under a
new ID. This proves the selected host's process-runner workload, not the separate
SDK container profile or automatic provider routing. Preserve its result location
and receipt.
Report infrastructure, enrollment, provider readiness, terminal access and
workload results separately. Do not upload or index terminal output automatically.

## Optional SDK container profile

Once you have the infrastructure and real enrollment IDs, select this path only
if your workload needs the container profile and a separately reviewed worker
and queue support it. This is a separate acceptance step from the default
process-runner connection.

Use Python 3.13 to match the tested container and trusted pickle transport.
For this optional profile, from the extracted `04_dreamlake_starter` directory:

```bash file="terminal"
python3.13 -m venv .venv
.venv/bin/pip install --require-hashes -r image/requirements.txt
cp -n inputs.example.json inputs.json
# Fill only missing fields using the reviewed infrastructure and enrollment IDs.
.venv/bin/python configure.py --input inputs.json --out generated
docker build -t dreamlake-starter:0.5.0 image
```

No hosted starter image is assumed. Build on the selected worker, explicitly
transfer the image, or push it to an approved registry and select its digest;
a local image on the controller alone is not available to a remote runner.

The generator writes `runtime-profile.toml`, `run-config.json` and `handoff.json`
under `generated/`. Missing-input feedback names the infrastructure, enrollment
or runtime stage and exits 2; fix those fields and rerun. An identical rerun is
a no-op, while a changed existing output is refused. The handoff explicitly
marks the operator-supplied identities unverified. Choose an operator-reviewed compatible container worker and
an existing permitted queue before applying that runtime fragment. It is not
Terraform enrollment, an automatic process-to-container bridge, or product
setup. Leave an existing daemon unchanged unless the user requested its
reconfiguration. Do not launch an EKS cluster to make the Kubernetes example fit.

The Kubernetes profile requires an explicit context and namespace, plus the
shared-filesystem acknowledgment in the recipe. `hostPath` requires the same
intended data at the configured path on every eligible execution node; it is
not a shared multi-node volume. Verify actual placement and paths before use.
The Docker profile defaults to no container network; changing that choice must
match the requested workload's access needs.

An authorized container-profile smoke test uses its separate control-plane
connection, namespace and scoped client token. DreamLake personal login and a
registered AWS provider do not supply those SDK credentials. Select them through
the approved private environment/secret-reference mechanism; do not put values
in inputs.json, images, Notes or command arguments. With the recipe's required
`LAKESHORE_URL`, `LAKESHORE_CLIENT_TOKEN` and `LAKESHORE_NAMESPACE` environment
selected, run:

```bash file="terminal"
.venv/bin/python smoke.py --config generated/run-config.json --queue APPROVED_EXISTING_QUEUE --timeout 90
```

A verified result includes sum 42, its actual invocation ID and the Python,
SDK, Git and curl versions. A timeout does not cancel the invocation. Retain the
submitted ID, verify the control plane's assigned Worker ID against the selected
worker evidence, and use `--invocation-id EXISTING_INVOCATION_ID` with the same config
and queue to retrieve it without submitting another job. This submits work;
it is not a read-only setup check. No compatible worker, queue, scoped credentials
or execution authorization means report that particular gap and preserve the
generated configuration. Do not claim the process-runner setup or AWS launch is
validated by an offline container configuration.

## Keep state authoritative and private

Keep active state in the selected S3 backend with `use_lockfile: true`, encryption
and bucket versioning. Supply credentials through the approved AWS credential
chain, not backend arguments or Terraform variables. See HashiCorp's
[S3 backend and locking documentation](https://developer.hashicorp.com/terraform/language/backend/s3).
Terraform's `sensitive` flag hides presentation; state and saved plans can still
contain those values. See [sensitive state handling](https://developer.hashicorp.com/terraform/language/manage-sensitive-data).

[Vault state tools](cli-vault-terraform-state.md) support nonsecret backend references
and an optional, explicitly selected encrypted-at-rest snapshot. A snapshot is
backup evidence, not an active backend, a Terraform lock, or proof of current
state freshness. Never discover or upload active state automatically. Keep
state, plans, grants and credentials out of the recipe, GitHub and Bindr.
Preserve retained resources and results; review the cleanup boundaries before
any later lifecycle operation.
