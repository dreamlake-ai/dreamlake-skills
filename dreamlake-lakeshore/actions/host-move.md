# Move a private host between namespaces

For a CLI request, check the installed command before selecting a host:

```shell
dl --version
dl hosts --help
dl hosts move --help
```

Use the supported surface for the task. An absent CLI command is a client
capability gap; it does not establish that the server or a published SDK lacks
the operation. For an SDK request, use the requested language's matching,
documented API rather than shell commands or another SDK language. If the CLI
lacks the operation and the user has not specified an SDK language, the
published Python API described in the
[product host guide](../reference/docs-lakeshore-hosts-enroll.md) can complete
the authorized task with the same guards. Verify that client's installed
capability and the deployed server before mutation. State native CLI availability
separately; if neither supported route is available, report the gap and stop.
Never substitute a raw ownership update or re-enrollment.

Product facts and limits live in the [product host guide](../reference/docs-lakeshore-hosts-enroll.md)
and [CLI host reference](../reference/cli-host-enrollment.md). Use the documented
authentication path for the selected client, confirm the intended deployment and
signed-in namespace, and keep credentials out of output.
1. Resolve the exact personal computer, its source namespace and intended
   destination. Inventory may contain test hosts, worker machines and multiple
   enrollments; do not interpret “my computers” as permission to move every row.
2. Separate placement from agent scope. If the user only wants the built-in
   agent to work in another namespace, select that session's namespace rather
   than moving resources. A move is appropriate when the computer itself should
   be filed in the destination.
3. Request the supported move preview. Review the resulting name, personal
   owner, private access, retained-session/run policies, exposure changes and
   all blockers. Keep the complete preview for the guarded apply; use the
   selected client's documentation or command help for its input format.
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

An installed SDK alone is not proof of a server rollout. Follow the selected
client's documented preview/apply contract; do not invent method names or relax
guards to bridge a version mismatch. State implementation, release and live
verification separately.
