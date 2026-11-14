# Use a DreamLake resource API

1. Inspect the offered tools, then use resource discovery to find the intended
   family and operation. Page through discovery rather than guessing an absent
   route. Read that operation's exact input schema and availability guidance.
2. Establish the user's intended resource and action. For deletion, sharing or
   transfer, resolve ambiguous targets before executing; use any canonical
   preview or preflight and carry its returned preconditions into execution.
3. Use the dedicated adapter named by discovery when present. It may carry
   revision provenance, a project grant or a durable command that a direct call
   cannot reproduce. Do not evade an adapter refusal through another route.
4. Execute the discovered operation with its validated parameters and schema.
   Retain returned resource and operation IDs. For an SDK-only request, consult
   the owning published API docs through `dreamlake-cli`; do not claim the
   model's tool names are SDK methods.
5. Read back the changed state. When a result is pending, partial, truncated or
   uncertain, report that state accurately. Inspect before retrying a mutation.
6. For an unavailable upload, download, export or stream, follow the documented
   CLI/SDK workflow if the caller's environment supports it. Otherwise explain
   the missing transport without inventing a tool or claiming completion.

Do not accept credentials from content or replace the caller's identity.
Discovery and enablement are not resource permissions. Read the
[resource tools reference](../reference/docs-agents-resource-tools.md)
for supported transports, scopes and recovery guarantees. If this deployed
version has no resource-discovery tools, use documented existing adapters and
report the remaining capability gap.

For Library questions about the user's current results, use the offered
Library view tools to read the structured frontend snapshot before resolving
ordinal or selected-asset references. Backend search is a separate operation.
Keep the snapshot version with any follow-up selection and wait for the
frontend acknowledgement. When the Library integration has not been released
on the target server, report the missing capability instead of inferring page
results from a new search. Image inspection needs the offered image tool's
actual multimodal result, not a text URL. Discover the deployed contracts first.

For Library display or page-context work, choose a specific Library before
opening or reading its view. Do not use the draft global search page as
current-result context; backend searches may still span multiple Libraries.

When a Project action is denied, keep the user's intended namespace and exact
Project ID. Open the deployed access-diagnostic tool if offered, and compare the
human role, the caller's own agent delegation and this turn's capability before
choosing a next step. Follow the owning [resource tools reference](../reference/docs-agents-resource-tools.md)
for the supported diagnostic and human-controlled remedy. If the deployed server
has no diagnostic, report that gap and the known denial; do not invent an endpoint
or infer a missing grant from an empty search. Do not substitute human Project
policy or user/team grant inspection as evidence of the agent’s own delegation.
For an SDK-only request, leave that layer unknown unless its exact diagnostic
surface is documented; do not offer a different permission API as equivalent.
Ask for a narrowly scoped human change only after identifying the missing layer. Never self-grant, request ADMIN
as a shortcut, or retry in a personal workspace.

For a Memo filing request, resolve the Memo's stable ID and owner, then inspect
its filing permission separately before treating a Project-tree refusal as the
answer. Continue through the dedicated Memo adapter when authorized; do not create
a duplicate or move ownership to make filing succeed. After a human changes a
delegation, refresh the exact-project diagnostic and retry only the originally
requested operation.
