# Teams

A **team** lives inside an organization and groups its members further.
Teams can be **nested** (a team can have a parent), and have a visibility of
`VISIBLE` or `SECRET`. Roles are `MAINTAINER` or `MEMBER`.

Teams are identified by `<org> <team>` — the team slug is unique only within
its organization.

## Manage teams

```bash file="terminal"
dreamlake team list                                   # all teams you belong to
dreamlake team list my-org                             # teams in one org
dreamlake team show   my-org backend
dreamlake team create my-org backend --name "Backend" --visibility secret
dreamlake team create my-org api --parent backend     # nested under backend
dreamlake team update my-org backend --visibility visible
dreamlake team delete my-org backend                  # must have no child teams
dreamlake team leave  my-org backend
```

## Members

```bash file="terminal"
dreamlake team member list   my-org backend
dreamlake team member add    my-org backend alice@example.com --role maintainer
dreamlake team member role   my-org backend alice@example.com --role member
dreamlake team member remove my-org backend alice@example.com
```

Adding a user who isn't yet in the organization adds them to the org (as a
MEMBER) automatically.

> **Warning:** The server prevents removing the last MAINTAINER of a team and deleting a
> team that still has child teams — delete or re-parent the children first.
