# List Artifacts

## List artifacts

```bash
dreamlake artifact list [--namespace NS]
```

Lists the artifacts in a namespace with their latest version and kind. Authenticated
members see all of a namespace's artifacts; without auth only `public` ones are listed.

## Verify the result

Confirm the requested namespace is the one listed. The command is read-only; it does not change visibility or artifact contents.
