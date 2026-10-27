# Curate a library with `dreamlake.yml`

Start from [`assets/dreamlake.yml`](../assets/dreamlake.yml) — every key is
optional, so write only the keys you need and delete the rest. Place it at
the library root; it is a normal source file, pushed and pulled with the
tree. Full key reference:
[`dreamlake.yml` — optional curation](../reference/docs-libraries.md#dreamlakeyml--optional-curation).

## When you need it at all

Discovery is zero-config ([`assets/library-conventions.md`](../assets/library-conventions.md)):
one top-level directory = one asset (`id` = directory name), loose files
are single-file assets, kind/format/entry are auto-detected, and a shipped
`thumbnail.*`/`preview.*` at the asset root is picked up. Add
`dreamlake.yml` only to:

- give the library a catalog identity (`library:` title, description,
  provider, homepage, tags, `upstream` repo/commit);
- set a **licence** (library default, per-asset override) and the
  `attribution` credit line CC-BY-style licences require;
- set per-asset `title`, `description`, `category`, `tags`;
- pick a different `entry` or declare `entryPoints` (for MJCF the CLI
  prefers `scene*.xml` and offers the bare robot as an alternative; override
  here when that is wrong) — entryPoints render as a switcher in the app;
- reshape which files belong to an asset (`files:` globs) or override
  discovery altogether (`discover.assets` / `discover.exclude` globs,
  `*` and `**`);
- point `thumbnail:` at your own image instead of a render;
- force `kind:`/`format:`/`entry:` for a layout detection misses (an
  unusual SOG/LOD splat tree, two `.ply` files in one asset).

## Rules

- Paths are relative to the library root.
- `defaults:` accepts exactly `category`, `license`, `tags` — and only
  `tags` merges; the other two are fallbacks a per-asset value overrides.
- Asset ids come from directory names — rename the dir to rename the id;
  ids must match `^[a-zA-Z0-9][a-zA-Z0-9._-]{0,127}$`.
- `kind` only picks the web viewer; any `^[a-z0-9][a-z0-9._-]{0,31}$` token
  is legal.
- Never create `.dreamlake/` paths yourself (reserved platform area; a user
  file under it is rejected at push) and never write an `assets.json`
  manifest — the CLI generates the real one.
- Importers ([publish](publish.md)) emit a `dreamlake.yml` for you; edit it
  rather than starting from scratch.

Then [publish](publish.md); run with `--dry-run` first to see the effect on
the asset list.
