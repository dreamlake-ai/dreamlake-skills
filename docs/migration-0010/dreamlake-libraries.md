# Migration: dreamlake-libraries

RFC 0010 S3 (content merge B). Source: `dreamlake-libraries/SKILL.md`
(280 lines, hand-written) → `dreamlake-libraries` in the standard shape.

**Decision — kept as its own skill, not merged into `dreamlake-scenes`.**
Merge-caution rule 2 applies on both counts: (a) publishing, curating and
searching an asset library is a distinct user goal someone installs alone
(a team shipping a splat/mesh library never builds a scene); (b) its 15 KB
of hand-written text would push the merged scenes skill past the ~50 KB
bound and past 12 actions. `dreamlake-scenes` routes to it by name for
asset search. Integrator: keep `dreamlake-libraries` in `catalog.json`;
no `renamed.json` entry is needed for it. The RFC §4 table (which folded
libraries into scenes) should be amended to list `dreamlake-libraries` as a
tenth skill with `requires: ["dreamlake-cli"]`.

`docs[]`: docs.dreamlake.ai/libraries, docs.dreamlake.ai/libraries/reference
(both verified `.md` → 200). No libraries page exists on cli.dreamlake.ai.

| Source section (`dreamlake-libraries/SKILL.md`) | Destination | Notes |
| --- | --- | --- |
| frontmatter description | `skill.json` description + `SKILL.md` description | Task boundaries, keyword pile removed |
| intro (what a library is, no version history, ingredients vs Scene vs source) | `SKILL.md` intro | Boundary now names `dreamlake-datasets` (RFC §4 name) |
| § Your directory is the format — zero-config push command | `actions/publish.md` top | |
| § Your directory is the format — discovery conventions (one dir = one asset, loose files, kind/format/entry detection, multi-file splats since CLI 0.41.0, exactly-one rule, shipped thumbnail, CLI hashes) | `assets/library-conventions.md` § Your directory is the format | Verbatim |
| § `dreamlake.yml` — optional curation (schema example) | `assets/dreamlake.yml` (template) + `actions/curate.md` (when and how) | Added the splat `kind/format/entry` override example from the "In the app"/splat bullets |
| § Importers for known repos | `actions/publish.md` § Importers for known repos | |
| § Push / update (sha256 diff, server deletes, revision race) | `actions/publish.md` § What a push does | |
| § Push / update — `--thumbnails`, `--embed`, `--model` (SigLIP2 default ≥ 0.25.0, warning line, `embedModel`), `--dry-run`, `--verify`, drift guard | `actions/publish.md` § Thumbnails and semantic search, § What a push does | All constraints kept |
| § The read path — commands, `list --all` survey, one-line hit format, `files`/`digest`, `info`, `stat` exit codes, incremental verified pulls, `--json` behaviour | `actions/search.md` | |
| § Add or remove one asset remotely | `actions/edit.md` | |
| § The wire manifest — generated, never hand-edit (schema, `generated[]` declaration trap, vectors sidecar, limits, legacy `assets.json`, manifest cache) | `assets/library-conventions.md` § The wire manifest | Manifest-cache paragraph also in `actions/search.md` § Inspect and verify |
| § In the app (Scenes tab, `/libraries` global search, `?asset=` panel) | `actions/search.md` § In the app | |
| § In the app — viewers by kind, SOG/LOD coarsest level | `assets/library-conventions.md` § Viewers by kind | |
| § In the app — visibility and `?share=` | `SKILL.md` § Boundaries | |
| § Gotchas (`.dreamlake/` reserved, `assets.json` plain file, ids from dir names + GSO sanitising, delete paths, push registers metadata, `defaults:` rule, silent semantic degradation, splat orientation, `pnpm cli --` trap) | `assets/library-conventions.md` § Gotchas, § Splat orientation; `actions/curate.md` § Rules; `actions/edit.md` § Rules | Each gotcha placed at least once |
| licence / attribution (scattered: `license`, `attribution` keys, hit and `info` licence fields) | `assets/library-conventions.md` § Licence and attribution; `actions/curate.md` | |
| scene-side library search traps from `dreamlake-scene-generation/actions/find-assets.md` (ranked ≠ relevant, zero results, semantic fallback) | `actions/search.md` § Survey, then search (and kept in `dreamlake-scenes/actions/source-assets.md`) | Shared guidance, phrased for each skill's task |
