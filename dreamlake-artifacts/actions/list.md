# List artifacts

```bash
dreamlake artifact list [--namespace <slug>]
```

Lists the artifacts in a namespace with their latest version and kind.
Authenticated members see all of a namespace's artifacts; without auth only
`public` ones are listed. Options:
[Listing, deleting, restoring](reference/cli-artifacts.md#listing-deleting-restoring)
or `dreamlake artifact list --help`.

## Verify the result

Confirm the requested namespace is the one listed. The command is read-only;
it does not change visibility or artifact contents. Use the ids it prints for
[share](share.md), [restore](restore.md) and
[notes-references](notes-references.md).

## In the app

`/<namespace>/artifacts` and `/<namespace>/profile?tab=artifacts` show the
same catalog, filtered by the viewer's access; see
[Browsing in the app](reference/docs-artifacts.md#browsing-in-the-app) and
[Profiles and workspaces](reference/docs-workspaces.md) for what signed-out
visitors, other-namespace visitors and members each see, and where the detail
header returns them.
