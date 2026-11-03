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
[built-in harness reference](https://docs.dreamlake.ai/agents/resource-tools)
for supported transports, scopes and recovery guarantees. If this deployed
version has no resource-discovery tools, use documented existing adapters and
report the remaining capability gap.
