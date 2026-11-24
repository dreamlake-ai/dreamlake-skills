<!-- generated from https://cli.dreamlake.ai/teams.md at 0.146.3 08ef5bd; do not edit -->

# Teams

A **team** lives inside an organization and groups its members further.
Teams can be **nested** (a team can have a parent), and have a visibility of
`VISIBLE` or `SECRET`.

Teams are identified by `<org> <team>` — the team slug is unique only within
its organization.

## Manage teams

```bash cli-help="team"
dl team list                                   # all teams you belong to, including as a guest
dl team list my-org                             # active teams in one org
dl team show   my-org backend                   # your role, what you can do, members
dl team create my-org backend --name "Backend" --visibility secret
dl team create my-org api --parent backend     # nested under backend
dl team update my-org backend --visibility visible
dl team leave  my-org backend
```

`dl team show` prints your role and what the server lets you do on that team
(`--json` includes the server's `myPermissions`). Rely on that rather than
working it out from the role table below.

## Rename a team's slug

```bash cli-help="team update"
dl team update my-org backend --slug platform    # rename the slug
dl team update my-org backend --name "Platform"  # an old slug still finds the team
dl team show   my-org platform                   # slug, previous slugs, members
```

The slug is the name in `dl team` commands and team links. Renaming it needs
edit authority on an active team: the team `OWNER`, `ADMIN` or `MAINTAINER`, or
an organization owner. The server applies the same rules as `dl team create`:
3–40 lowercase letters, digits and hyphens, with no hyphen at the start or end.
It may lowercase what you type, and `dl team update` prints the slug it saved.
A slug change is refused while the team holds Vault state.

The old slug stays **reserved for that team**. No other team in the
organization can take it, including a deleted team's slug or any team's
earlier slug. So an old command, script or link can never reach a different
team. The team itself may take one of its own earlier slugs back. Team grants,
members and invitations refer to the team itself, not its slug, so they are
unaffected.

`dl team` commands still accept an earlier slug and print a note with the
current one. They check current slugs first, then earlier slugs, and only
among the teams you can see. An earlier slug of a team you cannot see is
reported as not found, the same as an unknown slug. `dl team show` lists the
team's earlier slugs. Renaming needs a server with slug changes; an older
server rejects `--slug` and nothing is changed.

## Roles

| Role | Can do |
| --- | --- |
| `OWNER` | Everything: edit the team, manage members, admins, owners and guests, archive, restore and delete. |
| `ADMIN` | Edit the team, add, remove and re-role `MEMBER`s, invite and remove guests. Cannot grant or change `OWNER`, `ADMIN` or `MAINTAINER`, archive, restore or delete. |
| `MAINTAINER` | Legacy role. In a team with no `OWNER` it keeps full owner authority, as before; once the team has an `OWNER` it acts like `ADMIN`. |
| `MEMBER` | Organization member in the team: sees the team and receives the access shared with it. |
| `GUEST` | Outside collaborator who is **not** an organization member (see [Guests](#guests)). |

Organization owners always have owner authority on every team in their
organization, including archived teams. A new team's creator becomes its
`OWNER`. An existing team with only maintainers keeps working unchanged; make
someone `OWNER` to give it the tiered roles. The last `OWNER` cannot leave or be
removed or demoted; in a team with no `OWNER`, the last `MAINTAINER` cannot.
Changing a role never changes the Project grant roles shared with the team.

## Archive, restore and delete

```bash cli-help="team archive"
dl team archive my-org backend                 # keeps members, grants and invitations
dl team list my-org --archived                 # archived teams only
dl team restore my-org backend
dl team delete my-org backend                  # permanent; must have no child teams
```

Archiving is reversible. While archived, a team grants nothing: no Project
access through its grants, no host connections through its team grants (open
team-path connections are closed), and organization invitations do not add
anyone to it. It cannot be edited and its members cannot be changed, though
members may still leave. It is hidden from `dl team list` unless you pass
`--archived`, and its slug stays reserved. Restoring brings back everything it
had. Archive, restore and delete need owner authority: the team `OWNER`, a
`MAINTAINER` of a team with no `OWNER`, or an organization owner. Delete works
on archived teams too, but it cannot be undone.

## Members

```bash cli-help="team member"
dl team member list   my-org backend
dl team member add    my-org backend alice@example.com --role admin
dl team member role   my-org backend alice@example.com --role owner
dl team member remove my-org backend alice@example.com
```

`--role` is `owner`, `admin`, `maintainer` or `member` (default `member`).
`ADMIN`s and maintainers of a team with an `OWNER` may only add or set
`member`, and may only remove members and guests. A team maintainer or admin
can add only existing organization members. An organization owner may also
add someone who is not yet in the organization with `dl team member add`, but
that **also adds them to the organization** as a `MEMBER`, with organization
membership's access. This is different from a guest invitation. To bring in
someone without organization membership, use `dl team guest invite` instead.
`guest` is not a `--role` value.

## Guests

A guest belongs to one team without joining the organization.

```bash cli-help="team guest"
# Team owners, admins and maintainers:
dl team guest invite my-org backend partner@example.com
dl team guest list   my-org backend                  # pending; --status accepted|declined|revoked|expired
dl team guest revoke my-org backend partner@example.com
# The invited person:
dl team guest inbox
dl team guest accept 0123456789abcdef01234567
dl team guest decline 0123456789abcdef01234567
```

An invitation is addressed to an email address and expires after 14 days.
Inviting the same address again while it is pending returns the same
invitation. **DreamLake does not send an email.** `dl team guest invite` prints
the invitation's join link, `/teams/invitations/<invitation id>` on the
DreamLake web app (for example
`https://dreamlake.ai/teams/invitations/0123456789abcdef01234567`), for you to
share. The link is not a pass: only someone signed in with the invited email,
verified by their identity provider, can accept it. The recipient can also
find it in `dl team guest inbox` after signing in
(`dl login`) with that email, verified by their identity provider. An
invitation sent after their current sign-in appears on their next sign-in.
Accepting adds them to the team as `GUEST`, or as `MEMBER` if they already
belong to the organization. It never adds them to the organization.
`dl team guest revoke` takes the invitation id or the invited email and only
revokes pending invitations on that team. Remove an accepted guest with
`dl team member remove`.

A guest can see their team and its members, the organization's name, and the
Projects shared with that team, at the role of each grant, and they can leave.
Guests never get host or compute access through the team: no SSH, web
terminal or host session through any team connection grant. This holds even if
they later join the organization while their team role is still `GUEST`; an
owner or admin changes the role to `MEMBER` to change that. Access granted to
them independently, such as a direct host grant or a grant through another
team where they are not a guest, is not affected. They cannot see the organization, its members or its other teams,
any of its Projects that weren't shared with their team, or the team's
parent and child teams. They cannot manage anything. Archiving the team
suspends a guest's access along with everyone else's.

## Nesting and host access

**CLI 0.132.0+; requires a server that supports team grants.** A Host owner can grant a
team connection access to one host enrollment (see
[Team grants](https://cli.dreamlake.ai/host-enrollment#team-grants)). Every current direct member of
the team can then connect as that enrollment's Unix account, so adding a
member also lets them connect, and removing them closes their connections
through the team. Members of parent or child teams are not included, and
neither are the team's guests (see [Guests](#guests)). Connecting through a
team grant also requires organization membership.

> **Warning:** The server prevents removing the last owner of a team (the last MAINTAINER in a
> team with no OWNER) and deleting a team that still has child teams. Delete the
> children first.

## Server support and TypeScript

Roles beyond `maintainer`/`member`, archive and restore, `--archived`,
`--slug` and `dl team guest` need a server with team roles and guests. An older server
rejects those requests and nothing is changed. The CLI reports this and does
not retry. `dl team show` and `dl team member list` fall back to the fields an
older server has. Commands without the new options send the same requests as
earlier versions.

The TypeScript SDK has the same operations on `client.teams`:

```typescript
const { teamUpdate } = await client.teams.update(teamId, { slug: "platform" }) // teamUpdate.slug is the saved slug
await client.teams.archive(teamId)
await client.teams.restore(teamId)
await client.teams.list(orgId, { archived: true })
await client.teams.memberRole(teamId, userId, "ADMIN")
await client.teams.guestInvite(teamId, "partner@example.com")
await client.teams.guestInvitations(teamId, "PENDING")
await client.teams.guestRevoke(invitationId)
await client.teams.myGuestInvitations()
await client.teams.guestAccept(invitationId)
await client.teams.guestDecline(invitationId)
```

On an older server, these throw `TeamFeatureUnsupportedError`.
