# Move a private host between namespaces

Check the installed command before selecting a host:

```shell
dreamlake --version
dreamlake hosts --help
dreamlake hosts move --help
```

**Unreleased companion workflow:** use this action only with the matching
host-move CLI and server. If the installed help has no move command, report
that capability gap; do not substitute a raw ownership update or re-enrollment.
Product facts and the released limits belong in the
[host reference](../reference/cli-host-enrollment.md).

1. Resolve the exact personal computer, its source namespace and intended
   destination. Inventory may contain test hosts, worker machines and multiple
   enrollments; do not interpret “my computers” as permission to move every row.
2. Separate placement from agent scope. If the user only wants the built-in
   agent to work in another namespace, select that session's namespace rather
   than moving resources. A move is appropriate when the computer itself should
   be filed in the destination.
3. Request the supported move preview. Review the resulting name, personal
   owner, private access and all blockers. Keep the complete preview for the
   guarded apply; use the current command help for its input format.
4. Apply that reviewed preview within the user's requested scope, retaining its
   request identity. Do not detach dependencies, delete sessions, rotate keys or
   widen permissions to make a blocked move pass.
5. Read the destination inventory and exact host/enrollment status back. Check
   terminal or metrics only when needed to verify the requested behavior. A
   completed metadata operation does not establish a working remote terminal.

For an ambiguous apply result, preserve the original request and reconcile it
through the supported replay path. Do not generate a replacement request or
silently obtain a newer preview. A historical receipt does not prove the host's
current namespace after a later move.

For a TypeScript or Python integration request, use the matching SDK's documented
host-move preview/apply API with the same guards. Do not replace a requested SDK
integration with shell commands or treat an installed SDK as proof of a server
rollout. State implementation, release and live verification separately.
