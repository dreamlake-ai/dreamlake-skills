# Inspect Infrastructure Stacks and register empty backends

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

## Register an empty backend

When the task calls for a new environment, first inspect the intended owner's
project inventory. `dreamlake infra create NAME --namespace OWNER --project PROJECT
--environment ENV --repository HTTPS_URL --directory RELATIVE_ROOT` registers
metadata and an empty backend; it provisions no resources. Stack creation requires
ADMIN authority. Use `--directory ''` for the repository root and retain the
returned immutable stack UUID. Existing state is not copied or migrated.

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

## Provision Kubernetes capacity and launch containers

When explicitly authorized to provision a cluster, use the
[Kubernetes setup walkthrough](../reference/providers-kubernetes.md) for the
InfraStack, CPU pool limits, restricted endpoint, Vault kubeconfig and provider
registration sequence. The Kubernetes launch commands require the matching
backend and CLI source release; do not infer deployment from these docs. Verify
both the worker-node inventory and a completed Pod in each intended pool, then
record the task-owned teardown plan. Docker-built images run as Pods on existing
nodes; an accepted Pod launch is not a machine-provisioning or readiness receipt.
