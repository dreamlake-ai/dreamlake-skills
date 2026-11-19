# Administer a team: roles, archive and guests

```bash
dl team --help
dl team show "$ORG" "$TEAM" --json
```

Syntax, roles and what each state grants are on the [Teams](../reference/cli-teams.md)
page and in `dl team <command> --help`.

A request that names the team and the action, with the person and role or
the recipient email when one applies, already authorizes it: act without
asking again, and mention an impact the user may not expect in one sentence.
Ask only when the team, person, role, email or authority is missing or
ambiguous. An explicit request also covers the CLI's own confirmation prompt
(`--help` names the flag that skips it).

1. Confirm the installed client offers what is asked: `dl team --help` lists
   `archive`, `restore` and `guest`, and `dl team member add --help` accepts
   the role asked for. If not, update the CLI (the [setup](setup.md) action); no other
   command substitutes. If the server refuses a new operation, report that
   nothing was changed and do not retry.
2. Identify the team as `<org> <team>` and read `dl team show`. Act from the
   server's permissions in that output, not from a role you worked out. When
   the caller lacks the permission, name who holds it; do not look for
   another path.
3. Roles: set the named person to the stated role, then read the member list
   back.
4. Archive, restore (`dl team archive`, `dl team restore`): archiving
   suspends everything the team grants to every member until restore; read
   the team back as archived or active. When the user wants access to stop
   without naming an operation, archive.
5. Delete (`dl team delete`) is permanent. Delete only when the user
   explicitly asked to delete that named team; a request to stop access,
   clean up or archive is not one. If that is unclear, ask whether to archive
   instead.
6. Guests are outside collaborators, not organization members. Invite the
   stated email to the stated team with `dl team guest invite`, then read
   back the pending invitation from `dl team guest list`. Once accepted, the
   guest receives the Projects shared with that team, at each grant's role.
   Tell the user the recipient accepts from their own account by signing in with that email;
   do not accept, or sign in, on their behalf.
7. Recipient side: list with `dl team guest inbox`, then accept or decline
   the one invitation the user names.

## Exceptions

- `dl team member add` takes existing organization members. Only an
  organization owner can use it to bring in someone outside the organization,
  who then joins it as a member. A team owner, admin or maintainer cannot
  enroll anyone into the organization; for an outsider they invite a guest.
  When the user asked to add an outsider as a member and the caller is not
  an organization owner, say so and ask whether a guest invitation fits; do
  not send one in its place. `guest` is never a `--role`.
- Revoke a pending invitation with `dl team guest revoke`; remove an accepted
  guest with `dl team member remove`. Revoking does not remove a member.
- An invitation missing from the recipient's inbox usually needs a fresh sign-in
  with the invited, verified email; do not send a second invitation to a
  different address.
- Removing someone from a team, archiving it or changing a role never edits a
  Project grant; change Project access with the [project-access](project-access.md)
  action.
- Do not invite a guest, or add a member, only to reach a host. Host connection
  access is the host access action of `dreamlake-lakeshore`.
