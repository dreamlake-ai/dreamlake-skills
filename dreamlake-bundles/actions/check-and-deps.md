# Check uses declarations and set up CI

```bash
dl bundle check ./my-bundle#<entry>                         # declared prefixes only, smoke load
dl bundle check ./my-bundle#<entry> -- python smoke.py      # plus your own smoke command
dl bundle check <ns>/<bundle>@<v>#<entry>                   # a pushed entry
dl bundle deps --suggest ./my-bundle#<entry> -- python smoke.py   # trace opened files, suggest uses
```

What the tools do: [Check declarations](../reference/docs-bundles.md#check-declarations).
Flags: `dl bundle check --help`.

## Why

The server and the client do not validate `uses`. A missing declaration
fails with "file not found" at the first load. A declaration that is too wide
makes the entry version change too often. These tools are the only guard.

## Steps

1. Run `check` on the entry. Each missing file is a missing `uses` item.
2. If the entry has `"uses": ["/"]` or `check` fails, run `deps --suggest`
   with a command that loads the entry (compile the MJCF, open the USD stage,
   make the env and step it).
3. Read the suggestion. It is only a suggestion: prefer directory prefixes
   that match the [layout guidelines](../reference/docs-bundles.md#layout-guidelines).
   Edit `uses` in the source manifest.
4. Run `check` again. Repeat until it passes.
5. Push (the publish action).
6. Add CI that runs `dl bundle check <dir>#<entry> -- <smoke command>` for
   each changed entry. CI must use the declared prefixes only, never a full
   pull: [CI rule](../reference/docs-bundles.md#ci-rule-declared-prefixes-only).

## Exceptions

| Symptom | Likely cause | Do |
|---|---|---|
| `check` passes but the program fails later | The smoke load does not read all files (for example, textures loaded at render) | Give a smoke command after `--` that renders or steps the env |
| `deps --suggest` prints nothing | `strace` is not available | Install `strace`, or use `check` and add prefixes by hand |
| The suggestion lists single files in many directories | The layout does not group the entry files | Move the files into one directory for the entry, then check again |
| No MuJoCo or USD library on the machine | `check` skips the compile step | Give your own smoke command after `--` |
