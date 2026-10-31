<!-- generated from https://cli.dreamlake.ai/providers/kubernetes.md at 0.97.2 1633dd9; do not edit -->

# Kubernetes launch setup

This walkthrough requires CLI 0.71.0 or later and a backend implementing the
user-owned launch-server route. Check the deployed backend and installed CLI
version before binding a provider or launching. A cluster needs worker capacity
before a Pod can run.

## Execution requirement

All cluster provisioning and Pod launches must run through the explicitly
user-configured launch server with its appropriate IAM role and scoped cluster
access. Verify this route before running the mutating steps below. Do not use
control-plane/service IAM, ambient service credentials, an operator Vault IAM
user, or direct hosted-backend Kubernetes execution. If the route is unavailable,
keep new launches/provisioning on hold and preserve existing resources. See the
[required launch boundary](cli-providers.md#required-launch-boundary).

The existing direct-backend Kubernetes smoke is implementation evidence only;
it does not validate this architecture. CLI/backend version support and a Vault
kubeconfig alone are insufficient acceptance. Read-only inventory and local
scaffolding can continue while execution routing is corrected.

## Create the InfraStack

Create a task-specific directory and scaffold the `kube` provider template:

```bash
mkdir kube-dev
cd kube-dev
dreamlake provider create --name kube-dev --provider kube --json
```

Edit the generated `.dream/providers/kube-dev/terraform/terraform.tfvars`.
Choose a unique project name, region, nonoverlapping VPC CIDR, and an EKS version
in standard support. For CPU-only capacity set `gpu_instance_types = []` and
`gpu_desired_size = 0`. Set `system_node_count = 0` when ordinary CPU pools will
also carry system Pods. Never add these counts on top of an agreed machine cap.

```hcl
cpu_node_pools = {
  small = {
    instance_types = ["t3.medium"]
    min_size = 0
    desired_size = 16
    max_size = 16
  }
  large = {
    instance_types = ["m6i.xlarge"]
    min_size = 0
    desired_size = 4
    max_size = 4
  }
}
```

These two pools expose `dreamlake.ai/tier=small` and `large`. Check account quota,
instance availability and estimated hourly cost before applying. The API is
private by default. Reach it from the selected launch server. If public access
is needed, restrict it to that server's verified egress and separately authorized
administrative access; the template rejects a world-open endpoint. Do not add
hosted-backend egress as a substitute for the launch server.

Register a hosted state backend in your infrastructure project:

```bash
dreamlake infra create kube-dev --namespace team --project infrastructure --environment dev --repository https://github.com/example/infra --directory kube-dev --json
dreamlake infra connect STACK_ID
```

Add `terraform { backend "http" {} }` to the Terraform root. Apply the environment
settings printed by `infra connect`, and provide `TF_HTTP_PASSWORD` from your
DreamLake authentication without writing it into Terraform configuration. Run
Terraform provisioning on the selected launch server with its appropriate IAM
role; verify the actual AWS account and role before planning or applying. Do not
load an operator Vault IAM user's credentials as a fallback. State-backend
authentication is separate from AWS provisioning authority.
For an AWS-hosted Docker smoke image, optionally copy the repository example
`examples/kubernetes-launch/registry.tf` into this root. It creates a disposable
ECR repository whose images are deleted on teardown.
Run `terraform init`, `terraform validate`, and `terraform plan -out=launch.tfplan`;
review the account, create/change/destroy counts, instance types, limits and
network before `terraform apply launch.tfplan`. State, locking and history are
then visible in the InfraStack. Do not commit credentials, plan files or state.

## Authorize the launch server on EKS

The launch-server mode in CLI 0.71.0 and its matching backend uses the server's IAM
role and short-lived EKS authentication. It does not copy a static Vault
kubeconfig or run a user-supplied credential plugin. The adapter verifies the
actual STS account and assumed role before reaching the cluster endpoint.

In the cluster's Terraform, create an EKS access entry for the dedicated launch
role and map it to a named Kubernetes group. With the cluster administrator,
bind that group to a namespaced Role permitting `create/get/list/delete` on
`pods` and `get` on `pods/log`, plus a ClusterRole permitting `get/list` on
`nodes`. Create `dreamlake-launch` before binding the provider. These permissions
cover provider operations; they do not grant workload Pods the launch role.
Kubernetes RBAC is separate from AWS IAM policy permissions.

The launch server needs Python 3 with boto3, access to IMDSv2, AWS STS and EKS,
and HTTPS access to the cluster endpoint. Prefer the private endpoint in the
same network. The Nymph transport is outbound, so a new hosted backend IP does
not require changing the cluster allowlist. An authenticated Nymph hostname or
heartbeat is not a verified IP address or evidence of successful SSH.

Use [launch-server binding](cli-providers.md#bind-a-launch-server) to migrate an
existing provider while preserving its ID and existing Pod ownership. Binding
removes the legacy credential reference. Legacy static credentials may still
support read-only inspection during migration; they are not a launch fallback.

## Repair permissions

Use the [launch-role permission procedure](cli-providers.md#fix-permission-limitations).
Verify the server's actual IAM role, update its Terraform policy using the
authorized management identity, and test the previously denied operation.
For Kubernetes `Forbidden`, inspect the EKS access entry and group RoleBindings;
adding AWS permissions alone will not change RBAC. IAM policy changes normally
do not require replacing the launch server. Resolve uncertain launch receipts
before retrying mutations.

## Register, launch and verify

Follow [the provider declaration and launch example](cli-providers.md#launch-a-docker-image-on-kubernetes).
Use a named layer selecting `dreamlake.ai/tier=large` to verify the larger pool,
and confirm the Pod's assigned node belongs to that pool. For a custom image,
the CLI repository includes `examples/kubernetes-launch/Dockerfile`, a bounded
CPU smoke program and small/large launch layers. Build and push using your
registry credentials:

```bash
docker build -t REGISTRY/dreamlake-kube-launch:smoke examples/kubernetes-launch
docker push REGISTRY/dreamlake-kube-launch:smoke
```

Read the pushed digest and replace the image placeholder in `launch.jsonl`.
Register that layer as the provider default; create the larger-pool overlay with
`dreamlake providers layers create team/PROVIDER_ID --name large --file
examples/kubernetes-launch/large.jsonl --request-id large-layer-01` and launch
with `--layer large`. The sample leaves `command` unset to verify the image's
Docker `ENTRYPOINT` is preserved. Supply `imagePullSecrets` for an existing namespace-local pull secret
when the registry requires authentication; never put registry passwords in layers.

Architecture acceptance first requires evidence that provisioning and Pod
creation executed on the selected user-configured launch server with its
appropriate IAM role and scoped cluster access, without service-role or hosted
backend fallback. Workload acceptance then includes a Ready node count matching
both pools, one successful
launch per pool, useful bounded logs, same-request retry returning the same Pod,
and deletion limited to provider-owned Pods. The cluster visualization reports
readiness and allocatable capacity; it does not imply a Nymph enrollment.

## Stop charges

Preserve existing resources while launch routing is corrected; this section
is not an instruction to tear them down. For separately authorized cleanup, use
the selected launch server and scoped permissions. Delete acceptance Pods first.
To temporarily remove compute, set both pools'
`desired_size = 0` and apply the reviewed Terraform plan; keep `min_size = 0`.
The EKS control plane, NAT and any retained volumes continue billing. To stop
all task-owned cluster charges, run `terraform plan -destroy`, review it against
the task's hosted state, and apply the destroy plan. Retire the provider and
remove its dedicated EKS access entry after teardown; retire any legacy Vault credential separately. Preserve InfraStack history as the
resource inventory and cleanup record.
