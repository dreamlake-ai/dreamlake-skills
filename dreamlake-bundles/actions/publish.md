# Publish a bundle version

```bash
dl bundle fmt ./my-bundle                            # normalize source manifest whitespace
dl bundle push ./my-bundle --dry-run                 # show effective hashes; upload nothing
dl bundle push ./my-bundle --message "Add mug-0002"  # make the new version
dl bundle entries <ns>/my-bundle                     # read back the entries at the latest version
```

Flags: `dl bundle push --help` and
[CLI](../reference/docs-bundles-reference.md#cli).

## Before you start

- `dl bundle --help` works and `dl login` points at the right environment
  (`dreamlake-cli` skill).
- The directory has `bundle.json` and one `entries/<name>.json` for each
  entry. Fields: [Entry manifest](../reference/docs-bundles-reference.md#entry-manifest).

## Steps

1. Choose the bundle. A bundle is a unit of release: put entries in one
   bundle only when they must change together. Give each product with its own
   releases its own bundle, and connect bundles with pinned `refs`
   ([A bundle is a unit of release](../reference/docs-bundles.md#a-bundle-is-a-unit-of-release)).
2. Lay out the directory with the
   [layout guidelines](../reference/docs-bundles.md#layout-guidelines): one
   directory for each entry, shared files in `shared/`, objects in
   `objects/<category>-<id>/`.
3. Write each entry manifest. Set `kind`. If you do not know the exact files
   that the entry reads, start with `"uses": ["/"]`. Check each `uses` item
   against the [uses grammar](../reference/docs-bundles-reference.md#uses-grammar).
4. Write cross-bundle references in `refs` as `ns/bundle@N#entry`. You can
   write `@latest`; push pins it.
5. Run `dl bundle check ./my-bundle#<entry>` for each entry (the
   check-and-deps action). Do not push an entry that fails `check`.
6. Run `dl bundle fmt`, then `push --dry-run`. Read the effective hashes. An
   entry that you did not change must keep its hash.
7. Run `push` with a `--message`. Report the new version and the changed
   entries to the user.
8. Narrow `"uses": ["/"]` later with the check-and-deps action, then push
   again.

## Exceptions

| Symptom | Likely cause | Do |
|---|---|---|
| 409 on push | Another person pushed a new version first | Pull the latest version, merge your change, push again |
| 400 `manifest not in stored form` | A client other than `dl bundle push` uploaded the manifest | Push with `dl bundle push`; it writes the stored form ([Manifest format](../reference/docs-bundles-reference.md#manifest-format)) |
| Push warns about the format | Whitespace is not in the standard format | `dl bundle fmt ./my-bundle`; the warning does not stop the push |
| An entry got a new version but you changed nothing in it | A file under one of its `uses` prefixes changed, or `uses` is `/` | Narrow `uses` (check-and-deps action) |
| A manifest is YAML | YAML is not accepted | Convert it to JSON (`bundle.json`, `entries/<name>.json`) |
| The user wants to put code in the bundle | Bundles do not hold code | Register the code with `dl runnable`; set the env `code` field |
| An incompatible change of a task contract | Same entry name would break consumers | Make a new entry name, for example `pick-mug-v2` ([Incompatible changes](../reference/docs-bundles.md#incompatible-changes)) |
