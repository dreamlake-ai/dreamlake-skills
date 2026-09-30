# Source assets

Assets can come from **any origin** — pick per model, in any mix. There is
no required survey or library-search step:

- **Internet models.** For robots, the curated first stop is the
  [MuJoCo Menagerie](https://github.com/google-deepmind/mujoco_menagerie)
  (ready-made MJCF). Any MJCF/OBJ/STL you may legitimately download works.
- **User-provided files** — repo checkouts, scan-pipeline exports, CAD
  meshes.
- **Procedural MJCF** — authoring primitives yourself is a first-class
  source, often the best one for tables, shelves, walls. Element/attribute
  authority: the
  [MuJoCo XML reference](https://mujoco.readthedocs.io/en/latest/XMLreference.html).
- **A DreamLake library** (optional convenience; needs the `dreamlake` CLI
  logged in — `dreamlake login`, check `dreamlake profile`): per-asset
  search and manifest-sha256-verified pulls.

Keep two distinctions straight: a **visual reference** (photo, render) sets
dimensions/materials but is not a model — only downloaded, compiling files
enter the scene; and a model you *saw* is not one you *have* until its files
are on disk and complete.

**Record provenance per model, at sourcing time**: exact source URL,
version/commit, and the license — **per model**, not per repository
(Menagerie model dirs each carry their own `LICENSE`; copy it alongside).

**Acceptance checklist — any source.** An asset is usable when:

- dependency closure is complete: every mesh/texture/`<include>` present
  and resolving (`<compiler meshdir= texturedir=>`) outside its original
  repo;
- it compiles — `python tools/scene_report.py <entry-or-dir>` measures it
  (and fails usefully when broken);
- units/up-axis are right (MuJoCo: meters, Z-up; mm exports need
  `<mesh scale="0.001 …">` — re-measure after fixing);
- collision geometry exists (not all `contype=0 conaffinity=0`);
- reported mass is plausible for the object;
- the right entry file is used — for robots the bare robot XML, not
  `scene*.xml` (a scene entry drags its own floor and lights into yours);
- for layer `Attach` use: exactly one root body under `<worldbody>`.

A bare OBJ/STL becomes a scene object by wrapping it in your own MJCF body
with simple collision — pattern in
[design and inspect](design-and-inspect.md). **GLB/FBX are not loadable by
MuJoCo**; do not invent a conversion pipeline — if you convert with an
external tool, verify the output like any downloaded mesh.

**Library search, when you use it:**

```bash
dreamlake library list --all
dreamlake library search "coffee mug" --library <ns>/<lib> --kind mjcf
```

- Without `--library`, search fans out over up to 50 visible libraries.
- `--kind mjcf` keeps results compilable as-is (a `mesh` hit is still
  usable via wrapping).
- **Ranked ≠ relevant**: semantic search ranks by closeness, so a hopeless
  query can still return confident-looking rows. Read titles; inspect the
  top candidate before use.
- Zero results: drop `--category`/`--tag`/`--kind` filters and retry; then
  another library — **or leave the library route** and download or author
  the asset instead. Empty results switch the source, never end the task.
  Libraries without usable embeddings fall back to keyword matching
  silently; use short literal terms there. `dreamlake library info <ns>/<lib>`
  reports `semantic` — `false` means keyword-only for that library.

Pull one asset and check it against the checklist above:

```bash
dreamlake library pull <ns>/<lib> --asset <id> -o ./assets   # incremental; safe into a non-empty dir
python tools/scene_report.py ./assets/<id>
```

Every pulled file is verified against its manifest sha256 — rerun a failed
pull; nothing lands silently corrupted.

Full search scopes, `dreamlake.yml` curation, manifest and HTTP endpoints:
[libraries reference](../reference/libraries.md).
