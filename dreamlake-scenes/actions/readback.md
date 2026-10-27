# Pull an exact version back and verify it

```bash
dreamlake scene list --namespace <org>                 # name · version · type · files · entry
dreamlake scene pull <scene-name>@<N> --namespace <org> -o /tmp/check
diff -rq /tmp/scenes/my-scene /tmp/check               # byte-identical
```

Flags (`-o`, `--force` to write into a non-empty directory, `@N`):
`dreamlake scene pull --help` and
[List, pull, delete](reference/cli-scenes.md#list-pull-delete).

## Rules

- Pull the **exact receipt version** ([push](push.md)) into a **fresh empty
  directory**. A bare `scene pull <name>` fetches latest, which can race a
  concurrent push.
- Pulls are hash-verified: every file is checked after download.
- Then recompile and re-validate from the pulled copy:

```bash
python tools/scene_validate.py /tmp/check --settle <body>
```

- Compare the entry XML (including any `<keyframe>` block you appended
  after compose — [validate](validate.md)), the validation result, and — for
  a composed scene — the embedded pinned `dreamlake.layers.json`, the stack
  that keeps it editable ([iterate](iterate.md)).
- Do the round trip whenever the scene will be consumed elsewhere.

Owning page: [Pull it back](reference/docs-scenes.md#pull-it-back).
