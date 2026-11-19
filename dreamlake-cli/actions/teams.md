# Administer a team: roles, archive and guests

```bash
dl team --help
dl team show "$ORG" "$TEAM" --json
```

Syntax, roles and what each state grants are on the [Teams](../reference/cli-teams.md)
page and in `dl team <command> --help`.

1. Confirm the installed client offers what is asked: `dl team --help` lists
   `archive`, `restore` and `guest`, and `dl team member add --help` accepts
   the role asked for. If not, update the CLI (the [setup](setup.md) action); no other
   command substitutes. If the server refuses a new operation, report that
   nothing was changed and do not retry.
2. Identify the team as `<org> <team>` and read `dl team show`. Act from the
   server's permissions in that output, not from a role you worked out. When
   the caller lacks the permission, name who holds it; do not look for
   another path.
3. Roles: change one named person to the role the user stated. Granting or
   removing an owner, admin or maintainer needs the user's explicit
   instruction for that person.
4. Archive, restore, delete: archiving suspends everything the team grants
   to every member until restore. State that, ask, then archive; read the
   team back as archived. Prefer archive when the user wants access to stop;
   delete is permanent, so do it only on an explicit request to delete.
5. Guests are outside collaborators, not organization members. Before
   inviting, confirm the exact email address, the one team, and that the user
   accepts the guest receiving the Projects shared with that team. Invite,
   then read back the pending invitation from `dl team guest list`. Tell the
   user the recipient accepts from their own account by signing in with that
   email; do not accept, or sign in, on their behalf.
6. Recipient side: list with `dl team guest inbox`, then accept or decline
   the one invitation the user names.

## Exceptions

- Someone who should belong to the organization is an organization member
  added with `dl team member add`, not a guest. `guest` is never a `--role`.
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
