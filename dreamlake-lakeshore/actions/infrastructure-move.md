# Move an Infrastructure registration

```bash
dl infra status "$STACK_ID"
dl infra move "$STACK_ID" --namespace "$DESTINATION_OWNER" \
  --project "$DESTINATION_PROJECT" --dry-run --out stack-move-review.json
# Review the saved intent before executing it.
dl infra move "$STACK_ID" --request-file stack-move-review.json --confirm
dl infra status "$STACK_ID"
```

1. Use the setup action of `dreamlake-cli` to select the authenticated environment.
   Inspect the installed version and `dl infra move --help`, then consult
   [the current move contract](../reference/cli-infrastructure.md#move-an-existing-stack-registration).
   Do not infer support from an installed skill or a merged source change.
2. Discover the existing registration and retain its UUID, repository/root,
   environment, current path and state version. For cleanup, distinguish an empty
   registration or recipe from a state owner. Preserve repositories, saved sessions
   and active workloads; moving metadata does not establish that a machine is idle.
3. Preview the requested destination. Inspect its access grants as well as the
   saved source/destination IDs, paths, state version/digest, key and blockers.
   Make a requested rename or path change part of this preview. Do not invent a
   collision suffix, discard a binding or delete an occupied destination.
4. Execute only the exact saved request, within the user's authorized scope.
   Re-preview stale intent for review; never silently refresh it during execution.
   A locked stack or incompatible runbook/Bindr relationship is a blocker to
   resolve through its owning workflow, not permission to detach it.
5. Read the same UUID and both Project inventories. Verify the destination path,
   retained source configuration and state version. Record the operation ID and
   result in the canonical handoff. Distinguish a completed move from a reviewed
   proposal or an uncertain response.

For an uncertain write, retain the original review and key. Inspect the same
stack and its metadata events, reconcile the outcome, and replay the identical
request only when appropriate. Do not create a replacement stack, copy Terraform
state, mint a new key or remove the source to get past a conflict. A reconciliation
receipt is not a successful move or proof of rollback.

For Python, TypeScript or agent-tool requests, use the released interface in the
[Infrastructure documentation](../reference/docs-infrastructure-stacks.md) rather
than translating the command into an undocumented API. Unsupported capability or
authorization errors remain errors. The separate access-preserving transfer
workflow must not fall back to a move automatically. Any cloud-resource change
still uses the established Terraform root and its independently authorized scope.
