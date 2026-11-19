# Rename a Project or correct its address

```bash
dl project rename --help
dl project inspect "$PROJECT" --namespace "$NAMESPACE" --json
```

1. Establish the owning namespace and stable project ID from the user's context
   and a current read. Distinguish the display name from the current slug. If the
   intended target remains ambiguous, ask for that missing detail before writing.
2. Read [Rename and project addresses](../reference/cli-projects.md#rename-and-project-addresses)
   and the installed client's help. Choose name-following or custom behavior
   according to the request. A mismatch between name and slug is not evidence
   that an existing custom address should be replaced.
3. Show the current and proposed addresses, then perform the authorized change
   with the observed identity and revision. For SDK or MCP work, use that
   interface's documented project update method; do not substitute an unrelated
   resource rename or a namespace transfer.
4. Read back the stable project ID, canonical address and saved mode. Check the
   previous browser link when URL continuity is part of the request. Report any
   collision directly; do not invent another slug or edit the competing project.

After an uncertain result, inspect by stable ID before considering another write.
Do not remove a stale-edit guard to force a request through. An unsupported
installed client or backend is a capability gap, not permission to patch storage
or silently fall back to a different namespace.
