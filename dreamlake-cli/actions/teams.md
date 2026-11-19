# Administer a team: slug, roles, archive and guests

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
   `archive`, `restore` and `guest`, `dl team update --help` lists `--slug`,
   and `dl team member add --help` accepts the role asked for. If not, update
   the CLI (the [setup](setup.md) action); no other command substitutes. If the server refuses a new operation, report that
   nothing was changed and do not retry.
2. Identify the team as `<org> <team>` and read `dl team show`. Act from the
   server's permissions in that output, not from a role you worked out. When
   the caller lacks the permission, name who holds it; do not look for
   another path.
3. Slug: to show it, read `dl team show` (current and earlier slugs). To
   change it, run `dl team update "$ORG" "$TEAM" --slug <new>`, report the
   slug the command prints as saved (the server may normalize it), and read
   it back with `dl team show` under the new slug. The team ID does not
   change, and the old slug stays reserved for that team, so old commands
   and links still reach it with a note. Grants, members and invitations
   are unaffected. Report a refusal (taken, invalid, or the team holds Vault
   state) as is; do not pick another slug.
4. Roles: set the named person to the stated role, then read the member list
   back.
5. Archive, restore (`dl team archive`, `dl team restore`): archiving
   suspends everything the team grants to every member until restore; read
   the team back as archived or active. Archive when the user asked to
   archive, or clearly wants everyone's access through the team suspended
   while keeping the team. A vague request such as "clean up" names no
   outcome: ask which one they want (archive, delete, remove members) and
   change nothing meanwhile.
6. Delete (`dl team delete`) is permanent. Delete only when the user
   explicitly asked to delete that named team; a request to stop access,
   clean up or archive is not one.
7. Guests are outside collaborators, not organization members. Invite the
   stated email to the stated team with `dl team guest invite`, then read
   back the pending invitation from `dl team guest list`. Once accepted, the
   guest receives the Projects shared with that team, at each grant's role.
   A guest never gets host access through the team: no SSH, web terminal or
   host session through a team connection grant, even after joining the
   organization, until their team role is changed from `GUEST`. Their own
   direct host grants and other teams' grants are unaffected. Tell the user
   the recipient accepts from their own account by signing in with that
   email; do not accept, or sign in, on their behalf.
8. Recipient side: list with `dl team guest inbox`, then accept or decline
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
- Do not add a member only to reach a host, and do not invite a guest for
  it; a guest gets none through the team. Host connection access is the host
  access action of `dreamlake-lakeshore`.
