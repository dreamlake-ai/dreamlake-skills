# Collaborate on Infrastructure Stacks

Infrastructure commands require CLI 0.58.0 or later and a compatible API. CLI
0.57.0 does not include `infra`. Check the installed version and command help
before using these examples.

Authenticate and choose the intended environment using [setup](setup.md). These
commands use the authenticated user flow and require explicit Infrastructure project authority;
organization membership or a publicly readable project does not grant stack access.
Infrastructure READ authority includes access to secret-bearing Terraform state,
although this inspection workflow reads metadata only.

1. Inspect `dreamlake infra --help` and discover the existing environment with
   `dreamlake infra list --namespace OWNER --project PROJECT`. The CLI follows
   bounded cursor pagination. It rejects malformed responses, repeated IDs or
   cursors, access-role changes and reads exceeding its pagination bound. The
   result is not a snapshot across concurrent changes.
2. Retain the immutable stack UUID. Run `dreamlake infra status STACK_ID` to
   inspect its repository, Terraform directory, environment, state version and
   lock metadata. Distinguish the authenticated lock holder from client-reported
   operation/Who text. A state version does not prove deployment success or
   current resource health.
3. For backend setup instructions, run `dreamlake infra connect STACK_ID`.
   This validates metadata access and prints configuration plus credential
   variable names; it does not print a token, execute Terraform, edit files or
   migrate state. Obtain credentials privately through the authorized environment.
   Do not place credentials, state or plans in a Note, artifact or source control.
4. Review the existing Terraform root/backend before using any printed setup.
   Preserve the existing stack, state, locking and history. Creating a second
   stack is not migration. Any Terraform apply, resource provisioning or live
   backend migration needs its own authorized scope; inspection grants none.

For retained metadata, use `dreamlake infra history STACK_ID` for state-version
metadata and `dreamlake infra events STACK_ID --after SEQUENCE` for stack events.
History follows descending version cursors; events follow increasing decimal
sequence cursors. Preserve the returned event `nextCursor` for a later read.
Both reads are bounded and exclude raw state and Terraform output. Metadata
events do not establish execution success or current resource health.

## Manual operators and automation

Use the [manual and automated Terraform walkthrough](../reference/infrastructure.md#manual-and-automated-terraform)
when the task includes setup or an authorized Terraform operation. Both paths
reuse the canonical UUID/backend; discover before creating. Confirm the repo/root,
environment, provider identity and configured execution route. New workload or
machine provisioning follows the launch-server boundary below. Stack access alone
does not authorize an apply or supply cloud permissions.

- For a person, initialize the reviewed checkout with private backend credentials,
  retain locking, review a fresh saved plan and apply within the authorized scope.
  A normal plan needs WRITE because it acquires a lock. CLI login does not export
  `TF_HTTP_PASSWORD`; use the supported private credential mechanism.
- For automation, pin commit/tool/provider versions and input sources. Inject
  DreamLake and provider credentials separately on the authorized runner. Serialize
  jobs by stack UUID without canceling active applies; keep backend locking for
  coordination with manual users and other schedulers. Protect the exact plan
  artifact through review/apply; replan if stale. A cloud OIDC token does not
  authenticate the DreamLake HTTP backend. The backend is not an execution queue.
- For drift monitoring, use a bounded, locking plan and distinguish no change,
  differences and errors. A scheduled check does not authorize remediation.
- After uncertain apply/publication, inspect the same runner, UUID, history and
  provider resources before retrying. Never replace a stack or use `-lock=false`.
  Locks do not expire on disconnect. Verify the original runner stopped before
  authorized recovery; require the original actor/lock ID and check the client's
  unlock-body compatibility. Do not promise an ADMIN override or automatic unlock.
- Leave a discoverable runbook with stack ID, repo/root, environment/account,
  runner/roles, variable and credential references, verification/recovery commands,
  commit/run link, observed outcome and remaining work. Separate Terraform-owned
  resources from CI-owned deployment settings. Keep raw state/plans and secrets
  private. A persisted version is not a health check.

For adoption, use disposable resources to verify two independent operators share
state, only one can hold the lock, the next operator replans after release, and
uncertain outcomes preserve the original stack for reconciliation. Distinguish
configured, executed and verified; docs examples alone do not establish CI setup.

## Register an empty backend

When the task calls for a new environment, first inspect the intended owner's
project inventory. `dreamlake infra create NAME --namespace OWNER --project PROJECT
--environment ENV --repository HTTPS_URL --directory RELATIVE_ROOT` registers
metadata and an empty backend; it provisions no resources. Stack creation requires
ADMIN authority. Use `--directory ''` for the repository root and retain the
returned immutable stack UUID. Existing state is not copied or migrated.
Each stack also gets one path in the Project resource tree; pass `--path
infra/k3s/prod` or accept the default `infra/NAME/ENV`. A path occupied by a
Note, folder or stack returns 409; choose another path rather than overwriting.

Creation sends one request without automatic retries or a request-ID idempotency
contract. If the result is unknown, the receipt is invalid, or a conflict is
reported, retain the intended namespace/project/name/environment/repository/root
and reconcile it with `infra list` before repeating creation. Do not change its
name to get past an uncertain result. An accepted registration does not prove
deployment or resource health.

Use `--json` when another program needs metadata. Invalid credentials or an
inaccessible stack require access review, not an alternate endpoint or copied
credential. Use the [Infrastructure reference](../reference/infrastructure.md)
for complete options, pagination limits and release status.

Stack-to-Note attachment remains proposed. Creating or filing a Note does not
attach it or grant independent Note access. Reuse the existing [Notes guide](notes.md)
for canonical source reads, original-revision patches and acknowledged readback;
preserve Note identity, collaborative revisions and existing sharing.

## Move an existing registration

For a requested Project/workspace consolidation, preserve the existing UUID,
state endpoint, state bytes and history. Use CLI 0.67.0 or later
and the matching backend with its receipt migration and admission flag enabled.
Source and destination require namespace OWNER and Project ADMIN authority.

Preview the explicit destination with `dreamlake infra move STACK_ID --namespace
OWNER --project PROJECT --dry-run --out review.json`. Inspect blockers and saved
source/destination IDs, original name, state version/digest and idempotency key.
For an explicitly approved collision rename, add `--destination-name NAME` to
preview; never invent an automatic rename. To change only the tree path, preview
the stack's own namespace/project with `--destination-path NEW/PATH`; the UUID and
state stay unchanged. The review pins the current path, so re-preview if it is
reported stale. A stack with a path cannot yet move to another Project; report
the `STACK_MOVE_PATH_CROSS_PROJECT_UNSUPPORTED` blocker instead of working around it. A runbook (for cross-Project moves) or active lock may block
admission. The saved review file must be new and is private.

Execute only the saved intent with `dreamlake infra move STACK_ID --request-file
review.json --confirm`. The server rechecks authority and state/location; the
contract is admission-linearized across stores. Do not refresh the preview or
change destinations during confirmation. The CLI never retries a move write.
After an ambiguous outcome inspect the same UUID and reconcile, then replay the
same saved request/key if appropriate. Do not create a replacement stack.

## Provision Kubernetes capacity and launch containers

Before any workload or machine launch, verify the explicitly user-configured
launch server and its appropriate IAM role. Do not use or broaden control-plane
or service IAM, substitute ambient service credentials or an operator Vault IAM
user, or execute provider launches directly from the hosted backend. If the
server route is missing or unverified, stop new launch/provisioning actions and
report the gap. Preserve existing resources and unrelated service operation;
read-only inspection may continue. Current command/schema support and a direct
backend smoke do not prove this architecture is implemented. See the
[required launch boundary](../reference/providers.md#required-launch-boundary).

When explicitly authorized to provision a cluster through that server, use the
[Kubernetes setup walkthrough](../reference/providers-kubernetes.md) for the
InfraStack, CPU pool limits, restricted endpoint, EKS IAM/RBAC and enrolled-server
provider registration sequence. The server binding requires CLI 0.71.0 and the
matching backend route; legacy kubeconfig inventory does not authorize launches.
For denied actions, follow the [IAM repair reference](../reference/providers.md#fix-permission-limitations).
Do not infer deployment from these docs. Verify
both the worker-node inventory and a completed Pod in each intended pool, then
record the task-owned teardown plan. Docker-built images run as Pods on existing
nodes; an accepted Pod launch is not a machine-provisioning or readiness receipt.

## Access-preserving Stack transfer — source candidate

Use `infra transfer plan`, `create`, `status`, and `accept` for the new saved-review
and recipient-acceptance protocol only when its server migration/reader floor is
activated. Follow the owning Infrastructure page. Keep `infra move` as its distinct
explicit access-scope relocation; never fall back automatically.

The plan saves an exclusive private SHA256-bound singleton review. Creation takes
that exact file and `--confirm`; `--accept-if-authorized` preflights destination
authority before creating anything. Otherwise share the operation ID with an
authorized recipient, who saves `infra transfer status OP --out review.json` and
accepts with `infra transfer accept OP --request-file review.json --confirm`.
Acknowledge completion only when the metadata receipt confirms `ownerCommitted`.
An unknown write result includes the operation ID for read-only reconciliation;
never blindly replay with a new key. Source/destination organization MEMBER
transfer authority does not grant stack Read/Write/Admin, launch or IAM authority.
Mounted/runbook-bound profiles remain blocked. This guidance is unreleased source,
not evidence that a production endpoint or installed CLI already supports it.
