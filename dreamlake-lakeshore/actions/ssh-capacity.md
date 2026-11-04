# Inspect SSH capacity and Nymph permissions

```bash
dreamlake --version
dreamlake ssh --help
dreamlake hosts --help
# On the intended machine, using its existing config path:
nymph access --config /absolute/path/to/udf-daemon.toml
```

Read the [host-enrollment product guide](../reference/cli-host-enrollment.md) and [enrollment documentation](../reference/docs-lakeshore-hosts-enroll.md), plus the [complete SSH capacity reference](../reference/docs-lakeshore-hosts-browser-terminal.md#ssh-capacity-and-usage) and [Nymph permission/command inventory](../reference/docs-lakeshore-hosts-nymph-permissions.md) for configuration details. Check the canonical guide’s release requirements against the deployed components before using expanded usage/configuration support. An installed skill is not evidence that a server or binary supports it. Never invent a limit flag or a remote config command.

## Inspect and explain

Resolve the user's exact host, enrollment, Unix user, worker and control-plane namespace through the existing [hosts procedure](hosts.md). Keep these identities distinct. Use host details or the documented authenticated usage read when the deployed API supports it. Explain each returned scope and use actual `used` and `limit` values; do not substitute remembered defaults or present unavailable reads as zero. Namespace aggregate usage is shared, not a personal allowance.

For a refusal, distinguish a full worker quota from the shared namespace cap, local daemon capacity, write-queue overload, readiness and authorization failures. Report which boundary the evidence identifies; a generic error cannot prove which counter is full. Use the product guide's counting/lifecycle rules. Refresh after a connection closes; do not delete session records, restart arbitrary processes or stop another user's work to clear a counter. Detaching an SSH viewer and stopping its underlying workload are different actions.

## Change capacity within the requested scope

Establish requested values, operator authority, deployed versions, current usage, existing service config and the intended restart window. Inspect local effective policy without printing credential files. Use the canonical configuration reference for exact supported names, ranges, defaults and restart semantics; preserve private state directories, host keys, enrollment and unrelated settings.

Prepare a concrete patch and validate it before rollout. Keep control-plane replicas consistent and local capacity compatible with the intended quotas. Follow the documented mixed-version order and existing supervisor; do not silently re-enroll a host to apply a scalar setting. Report startup validation and live effective readback separately. Reducing capacity must follow documented drain behavior, not implicitly terminate sessions. If the requested change would broaden permissions or interrupt work beyond authorization, explain the concrete additional action before proceeding.

## Review permission boundaries

Classify the operation as inspection, capacity configuration, workload/session execution, lifecycle/key maintenance or a permission change. Check both local policy and server authority. Record the actual parser, local gate and server route for each command; do not infer authority from a token, queue mount, successful heartbeat or generic configuration comment. Preserve documented lifecycle exceptions rather than claiming that command denial blocks every remote state change.

Dynamic configuration requires an explicit design and local opt-in. Document allowed fields, actor/scope, local ceilings, expected revisions, idempotency, expiry, audit/provenance, desired versus effective values, apply timing, rollback, restarts and active-session behavior. Do not implement a generic config setter as a workaround for a quota. Treat this design as proposed until supported by product code and release evidence.

## Verify and record

Verify counts before/after a connection, refusal at capacity, recovery after release, unavailable/stale displays, unauthorized reads and configuration validation. Keep source tests, merge, deployed versions, production checks, docs publication, skill release and installed client readback separate. Product facts belong in the owning docs; update generated references only through the normal docs-fetch workflow after publication.
