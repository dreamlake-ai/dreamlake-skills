<!-- generated from https://cli.dreamlake.ai/teams.md at 0.119.0 4c56b6a; do not edit -->

# Teams

A **team** lives inside an organization and groups its members further.
Teams can be **nested** (a team can have a parent), and have a visibility of
`VISIBLE` or `SECRET`. Roles are `MAINTAINER` or `MEMBER`.

Teams are identified by `<org> <team>` — the team slug is unique only within
its organization.

## Manage teams

```bash file="terminal"
dl team list                                   # all teams you belong to
dl team list my-org                             # teams in one org
dl team show   my-org backend
dl team create my-org backend --name "Backend" --visibility secret
dl team create my-org api --parent backend     # nested under backend
dl team update my-org backend --visibility visible
dl team delete my-org backend                  # must have no child teams
dl team leave  my-org backend
```

## Members

```bash file="terminal"
dl team member list   my-org backend
dl team member add    my-org backend alice@example.com --role maintainer
dl team member role   my-org backend alice@example.com --role member
dl team member remove my-org backend alice@example.com
```

Adding a user who isn't yet in the organization adds them to the org (as a
MEMBER) automatically.

> **Warning:** The server prevents removing the last MAINTAINER of a team and deleting a
> team that still has child teams — delete or re-parent the children first.
