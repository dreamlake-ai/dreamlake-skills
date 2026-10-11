# Owned TCP tunnels

Unreleased: consult [TCP tunnels](../reference/tunnel.md) for the coordinated
client/API/control-plane/Nymph prerequisites. CLI through 0.54.0 has no tunnel command.
Authenticate with [setup](setup.md), select `--identity user`, and choose the
exact namespace/group/host and enrollment. Do not launch a new machine as a
connectivity retry. This feature initially supports Linux and macOS OpenSSH.

Use `tunnel start --target ... --remote-port ... --name ... --detach --json` for
agent workflows. Read the ready receipt before connecting to its local port;
pending, failure or an unknown outcome does not establish connectivity. The
listener is local loopback, and the remote destination is one literal loopback
address. No shell or general network access is granted by the tunnel key.

Keep the local tunnel ID, exact remote worker/session IDs and expiry. Default
conflicts are errors. Use a different local port or logical name unless the user
intends replacement. `--replace` replaces both owned managed local conflicts and
the owner's named remote lease; side-specific flags limit the operation. It
never kills unrelated listeners, browser sessions or another user's tunnels.

Use `list`, `status` and `stop` with JSON receipts. If a client disappears, inspect
`list --remote --target ...` and stop the exact worker/session through the owner
API. A failed create is never blindly retried: inspect the exact target/name,
then stop or explicitly replace. Ephemeral credentials and SSH bytes must never
enter logs, Notes, model context or process arguments. Ordinary shutdown removes
temporary key files; an abrupt process kill may leave private files for owned
orphan cleanup. Remote authorization remains bounded by the lease expiry.

This does not add SDK tunnel support, Windows forwarding, arbitrary remote
listeners or a generic process-kill command. Data, Notes, artifact and workflow
operations retain their own authorization and revision rules.
