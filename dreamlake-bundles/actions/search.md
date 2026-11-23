# Search and inspect entries

```bash
dl bundle search "red mug" --kind object       # one result for each entry
dl bundle info <ns>/<bundle>@<v>#<entry>       # manifest, effective hash, displayed version, refs
dl bundle entries <ns>/<bundle>@<v>            # all entries of a version
dl bundle versions <ns>/<bundle>               # version history
dl bundle entry <ns>/<bundle>#<entry> --versions   # displayed versions of one entry
```

Flags: `dl bundle search --help`. API:
[REST API](../reference/docs-bundles-reference.md#rest-api).

## Steps

1. Search with the user's words. Add `--kind` when the user names a kind
   (robot, part, object, scene, env, env-set).
2. Run `info` on the best result before you pull it. Read `kind`, `uses` and
   `refs`. An entry with `"uses": ["/"]` pulls the full bundle.
3. Give the user the full reference `ns/bundle@N#entry`, with the version.
   In a Memo or a Chat, write it as the directive `:bundle[ns/bundle@N#entry]`
   (the [directive](../reference/docs-bundles-reference.md#directive)); the
   Memo edit procedure is `dreamlake-memos` references.
4. To get it, use the pull action.
5. To show it to the user in the browser, give the app route
   ([Browse in the app](../reference/docs-bundles.md#browse-in-the-app)).

## Exceptions

| Symptom | Likely cause | Do |
|---|---|---|
| The user asks the built-in agent to change a bundle | Its bundle tools are read-only | Use `dl bundle push` (the publish action) |
| No results | Search uses keywords over title, description and tags | Try other words; drop `--kind` |
| The user searches a library, not a bundle | Library search is separate | Use `dreamlake-libraries` for library assets |
| Many versions in `versions`, few in `entry --versions` | An entry version changes only when its effective hash changes | Expected |
