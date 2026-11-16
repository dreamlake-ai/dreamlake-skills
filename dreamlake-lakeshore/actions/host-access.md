# Share a host's connection access with a teammate or a team

Check the installed client before touching a grant:

```shell
dl --version
dl hosts access --help
dl hosts status <namespace/group/host>
```

Product facts — who may grant, what a grant covers, revoke and pending-close
behaviour, the Compute UI flow — are in the
[product guide](../reference/docs-lakeshore-hosts-browser-terminal.md#share-a-machine-with-a-teammate).
Command syntax and output are in the
[CLI host reference](../reference/cli-host-enrollment.md#share-connection-access)
and `dl hosts access <list|grant|revoke> --help`. If `dl hosts access` is
missing, the installed CLI predates it; update the CLI or use the Compute UI.
For an SDK-only request, use the requested language's methods and minimum
version from [Manage grants without Compute](../reference/docs-lakeshore-hosts-browser-terminal.md#manage-grants-without-compute),
and check the installed package version first; do not fall back to shell
commands or raw HTTP.

Team grants are newer than person grants. Use one only when the installed
client's `dl hosts access grant --help` (or the SDK method) offers a team
recipient and the server accepts it; otherwise follow the unsupported-team
exception below.

1. Resolve with the user the exact host, the exact enrollment (one Unix
   account) and exactly one recipient: a person's DreamLake username or a
   team's slug. Do not pick an enrollment, machine, person or team yourself,
   and do not treat "share my machines" as consent for every host.
2. Before granting, tell the user that the recipient will act as that Unix
   account with its existing OS permissions, and what that exposes per the
   product guide; no OS user is created. For a team, also say that every
   current and future direct member of that team (not parent or child teams)
   connects as the same Unix user, and that the team's maintainers decide who
   that is. Grant to a team only after the user confirms this. If they want
   isolation, stop: a separate Unix account must be created and enrolled
   first (the enrollment steps in [hosts](hosts.md)), then shared.
3. Grant with an explicit enrollment and the one recipient, then read the
   grant list back and report the grant ID, person or team, Unix account and
   state.
4. To revoke, use the exact grant ID from the list. Report confirmed closes,
   unconfirmed connections (with the deadline the output gives) and
   connections kept open by another current grant separately. Never describe
   a revoke with unconfirmed connections as fully closed. To retry the close,
   revoke the same grant again; do not grant it again.
5. To cut one person off completely, list every path that reaches them on
   that enrollment (their own grant and each granting team they belong to)
   and confirm with the user which to revoke or which team membership to end.
   Removing one path leaves the others in force.

## Exceptions

- An uncertain grant result (timeout, lost response): list the grants to
  reconcile. Do not repeat the grant to "make sure"; a repeat re-activates a
  grant that was revoked in the meantime. Grant again only on the user's fresh,
  explicit instruction.
- Refusals (not a member, personal namespace, the owner themself, unknown
  enrollment or person, not the owner): report the server's reason and stop.
  Do not add the person to the organization, move the host or change
  ownership to get past it.
- Recipients are one named person or one team. Service accounts, machine
  identities and wildcards are not grant recipients; `service-accounts
  host-grants` is a different, machine-identity feature (see
  [machines](machines.md)).
- Team grant unsupported (no team option in the installed client, or the
  server refuses the team field or says it cannot list team grants): report
  that and stop. Do not grant each member individually unless the user asks
  for those person grants explicitly. A list that the client could not
  complete is unknown, not "only the owner can connect".
- An older client may be told to upgrade before it can list a host that has
  team grants. Update the client; do not read that refusal as an empty list.
- Do not add someone to a team, or to the organization, to get them onto a
  host; that is a team-membership decision for its maintainers and the user.
- Filing a host in a Project or a Bindr is placement only: Project members may
  see its name and owner but never connect through the Project. Never file a
  host as a way to share it; grant explicitly instead. Filing itself is in the
  `project-access` action of `dreamlake-cli`.
- A grant covers connecting only. Inside the shell, everything the shared Unix
  account can reach is exposed: its files, tmux sessions and credentials
  stored in it, including any DreamLake sign-in stored there; sharing gives no
  OS credential isolation. The grant itself confers no DreamLake authority:
  host management, metrics, lifecycle, launches and saved agent sessions stay
  with the owner. Do not use a grant as a workaround for those.
- A listed active grant can still be inert (the person left the organization,
  the host moved). Verify a connection only when the user asks, and only as
  that person.
