# Share a host's connection access with a teammate

Check the installed client before touching a grant:

```shell
dl --version
dl hosts access --help
dl hosts status <namespace/group/host>
```

Product facts — who may grant, what a grant covers, revoke and pending-close
behaviour, the Compute UI flow — are in the
[product guide](../reference/docs-lakeshore-hosts-browser-terminal.md#share-a-machine-with-a-teammate).
Command syntax and output are in the [CLI host reference](../reference/cli-host-enrollment.md)
and `dl hosts access <list|grant|revoke> --help`. If `dl hosts access` is
missing, the installed CLI predates it; update the CLI or use the Compute UI.
For an SDK-only request, use the requested language's documented methods
(Python `client.hosts`, TypeScript `hosts(ns)` from the CLI's `./api`) and their
documented minimum version; do not fall back to shell commands or raw HTTP.

1. Resolve the exact host, the exact enrollment (one Unix account) and the
   person's DreamLake username with the user. Do not pick an enrollment,
   machine or person yourself, and do not treat "share my machines" as consent
   for every host.
2. Before granting, tell the user that the person will act as that Unix
   account with its existing OS permissions, and what that exposes per the
   product guide; no OS user is created. If they want isolation, stop: a
   separate Unix account must be created and enrolled first (the enrollment
   steps in [hosts](hosts.md)), then shared.
3. Grant with an explicit enrollment and username, then read the grant list
   back and report the grant ID, person, Unix account and state.
4. To revoke, use the exact grant ID from the list. Report confirmed closes and
   unconfirmed connections separately, with the deadline the output gives.
   Never describe a revoke with unconfirmed connections as fully closed. To
   retry the close, revoke the same grant again; do not grant it again.

## Exceptions

- An uncertain grant result (timeout, lost response): list the grants to
  reconcile. Do not repeat the grant to "make sure"; a repeat re-activates a
  grant that was revoked in the meantime. Grant again only on the user's fresh,
  explicit instruction.
- Refusals (not a member, personal namespace, the owner themself, unknown
  enrollment or person, not the owner): report the server's reason and stop.
  Do not add the person to the organization, move the host or change
  ownership to get past it.
- Grants are for named people only. Service accounts, machine identities,
  teams and wildcards are not grant recipients; `service-accounts host-grants`
  is a different, machine-identity feature (see [machines](machines.md)).
- A grant covers connecting only. Inside the shell, everything the shared Unix
  account can reach is exposed: its files, tmux sessions and credentials
  stored in it. What stays with the owner is DreamLake authority: host
  management, metrics, lifecycle, launches, the owner's DreamLake sign-in and
  saved agent sessions. Do not use a grant as a workaround for those.
- A listed active grant can still be inert (the person left the organization,
  the host moved). Verify a connection only when the user asks, and only as
  that person.
