# Kubernetes launch setup

This walkthrough requires CLI 0.66.0 or later and the Kubernetes launch backend.
Check the deployed backend and installed CLI version before using the `nodes`
and `instances logs` commands. A cluster needs worker capacity before a Pod can run.

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
private by default. If public access is needed, explicitly allow only operator
and DreamLake backend egress CIDRs; the template rejects a world-open endpoint.

Register a hosted state backend in your infrastructure project:

```bash
dreamlake infra create kube-dev --namespace team --project infrastructure --environment dev --repository https://github.com/example/infra --directory kube-dev --json
dreamlake infra connect STACK_ID
```

Add `terraform { backend "http" {} }` to the Terraform root. Apply the environment
settings printed by `infra connect`, and provide `TF_HTTP_PASSWORD` from your
DreamLake authentication without writing it into Terraform configuration. Load
AWS credentials from your authorized Vault profile into the process environment.
For an AWS-hosted Docker smoke image, optionally copy the repository example
`examples/kubernetes-launch/registry.tf` into this root. It creates a disposable
ECR repository whose images are deleted on teardown.
Run `terraform init`, `terraform validate`, and `terraform plan -out=launch.tfplan`;
review the account, create/change/destroy counts, instance types, limits and
network before `terraform apply launch.tfplan`. State, locking and history are
then visible in the InfraStack. Do not commit credentials, plan files or state.

## Bootstrap restricted cluster access

Use administrator access only to create `dreamlake-launch`, its `dreamlake-provider`
service account, a namespaced Role/RoleBinding for Pods and Pod logs, and a
ClusterRole/ClusterRoleBinding for read-only node inventory. The Pod role needs
`create/get/list/delete` on `pods` and `get` on `pods/log`. No secrets, exec,
cluster-admin or node mutation permission is needed by the provider.

Mint a short-lived service account token with `kubectl create token dreamlake-provider
--namespace dreamlake-launch --duration=24h`; verify the granted expiration.
The repository includes `examples/kubernetes-launch/rbac.yaml`; inspect its
namespace and role names, then apply it with administrator credentials.
Build a kubeconfig containing only the cluster HTTPS endpoint, inline CA, this
token, and a `dreamlake` context. Store it through stdin:

```bash
dreamlake vault add --name team/kubernetes/kube-dev --stdin --request-id kube-credential-01 < provider.kubeconfig
```

Protect the local file and remove it after the Vault write. Record credential
expiry and rotate before it expires; the provider does not execute AWS CLI
plugins or renew tokens. This token is the API client identity; workload Pods use the configured workload
service account and do not need these API permissions. Kubernetes nodes use containerd to run Docker-built
OCI images; a Docker daemon on every worker is not required.

## Renew the credential

Token expiration is an operational limit, not a launch failure. Check Vault
metadata with `dreamlake vault show --name team/kubernetes/kube-dev`. Before its
recorded expiry, use administrator access to mint a new token for the same
service account and replace only the token in the inline kubeconfig. Save it
with the observed Vault revision and a new stable request ID:

```bash
dreamlake vault add --name team/kubernetes/kube-dev --if-match REVISION --stdin --expires-at TOKEN_EXPIRY_UTC --request-id kube-credential-renew-01 < provider.kubeconfig
```

Remove the private local kubeconfig afterward and repeat `providers nodes` plus
a small launch to verify the replacement. A lost Vault response must be
reconciled through `vault write-status --request-id kube-credential-renew-01`
before retrying identical input. The provider reference stays the same.
If a Fargate backend uses a public task IP, deployments can change its egress;
refresh the cluster's restricted allowlist from the actual new task ENI before
claiming connectivity. Do not widen it to the internet as a workaround.

## Register, launch and verify

Follow [the provider declaration and launch example](providers.md#launch-a-docker-image-on-kubernetes).
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

Acceptance includes a Ready node count matching both pools, one successful
launch per pool, useful bounded logs, same-request retry returning the same Pod,
and deletion limited to provider-owned Pods. The cluster visualization reports
readiness and allocatable capacity; it does not imply a Nymph enrollment.

## Stop charges

Delete acceptance Pods first. To temporarily remove compute, set both pools'
`desired_size = 0` and apply the reviewed Terraform plan; keep `min_size = 0`.
The EKS control plane, NAT and any retained volumes continue billing. To stop
all task-owned cluster charges, run `terraform plan -destroy`, review it against
the task's hosted state, and apply the destroy plan. Retire the provider and
revoke its Vault credential after teardown. Preserve InfraStack history as the
resource inventory and cleanup record.
