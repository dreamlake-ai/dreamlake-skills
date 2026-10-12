# TCP tunnels

Requires CLI 0.55.0 or later, Nymph 0.1.18 or later, and server forwarding support. CLI through 0.54.0 supports web terminal enrollment but does not include this tunnel command.

Forward a local loopback port to a service on the exact enrolled machine. The
connection travels through Nymph's outbound SSH relay; no inbound cloud port is
needed. Each tunnel permits one literal remote loopback destination, with no
shell, SFTP, reverse forwarding or arbitrary network destination.

```bash cli-help="tunnel start"
dreamlake --identity user tunnel start --target alice/dev/laptop \
  --local-port 8080 --remote-port 3000 --name dev-web
```

The default remote host is `127.0.0.1`; `--remote-host ::1` selects IPv6 loopback.
The listener binds `127.0.0.1` on the computer running the CLI. `--local-port 0`
chooses a free port and reports it. Use `--enrollment-id` if a host has several
enrollments. The default lifetime is 1800 seconds; `--duration-seconds` accepts
60–1800. Expiry closes active connections. Setup does not copy the personal login
to the enrolled host or grant persistent worker access.

A logical tunnel name reserves one owned lease on that enrollment. Two names
may reach the same remote service. The default name is `tcp-<remote-port>`.
The command runs in the foreground until interrupted. For an agent or script,
use `--detach --json`; it returns only after SSH and local forwarding are ready.
A successful receipt contains the tunnel ID, target, bound local port, remote
endpoint and expiry. It never contains SSH keys, relay tickets or credentials.

```bash
dreamlake --identity user tunnel start --target alice/dev/laptop \
  --local-port 8080 --remote-port 3000 --name dev-web --detach --json
```

## Conflicts and replacement

An occupied local port returns `local_port_in_use`. An existing owned remote
lease with the same name returns `remote_tunnel_conflict`. Nothing is killed by
default. `--replace` replaces both matching managed local tunnels and the matching
owned remote lease. `--replace-local` and `--replace-remote` select one side.
Replacement verifies ownership, waits for cleanup and fails if the requested port
remains occupied. It never kills an unrelated process, another user's remote
tunnel, a browser SSH session or the service listening on the remote destination.

```bash
dreamlake --identity user tunnel start --target alice/dev/laptop \
  --local-port 8080 --remote-port 3000 --name dev-web --replace --detach --json
```

## Inspect and stop

```bash cli-help="tunnel list"
dreamlake tunnel list --json
```

```bash cli-help="tunnel status"
dreamlake tunnel status TUNNEL_ID --json
```

```bash cli-help="tunnel stop"
dreamlake tunnel stop TUNNEL_ID --json
```

List remote leases or clean up a lease whose local client has disappeared:

```bash
dreamlake --identity user tunnel list --remote --target alice/dev/laptop --json
```

```bash
dreamlake --identity user tunnel stop SESSION_ID --remote \
  --target alice/dev/laptop --worker-id WORKER_ID --json
```

A failed request after submission can have an unknown outcome. The CLI never
blindly retries a lease creation. Inspect the exact target/name with `list --remote`,
then stop or explicitly replace it. A stopped, expired or replaced tunnel cannot
resume using its former session credential. Local manager records contain only
metadata; secrets stay in memory or temporary private SSH key files that are
removed during ordinary shutdown. An abrupt process kill can leave private files;
`stop` uses the owner API to close an orphaned lease before cleaning its local
files. A manager still starting is given its bounded setup window. No PID from
a saved record authorizes terminating a process. Remote authorization expires
even if the local client disappears. If the owner API cannot confirm cleanup,
the stopped receipt reports `remoteCleanup: "pending"`; inspect or stop that
remote lease before claiming that authorization was revoked.
