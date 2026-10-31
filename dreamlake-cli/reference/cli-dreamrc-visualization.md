<!-- generated from https://cli.dreamlake.ai/dreamrc/visualization.md at 0.97.2 1633dd9; do not edit -->

# Visualization .dreamrc

Visualization configuration remains owned by `@dreamlake/viz/dataset-viz`.
The execution and registration loaders do not reinterpret these fields.

| Field | Meaning |
| --- | --- |
| `version` | Schema version, currently `1`. |
| `name` | Optional dataset display name. |
| `storage` | Optional registered driver config; inherited from host storage when omitted. Explicit storage wins. |
| `storage.driver` | Registered storage driver; additional fields follow that driver's schema. No credentials. |
| `dataset.format` | Registered dataset format. |
| `dataset.episodes` | `auto`, supported glob, or discovery options. |
| `dataset.episodes.glob` | Episode path glob; `*` supported, `**` unsupported. |
| `dataset.episodes.sort` | `name`, `name-desc`, or `none`. |
| `dataset.episodes.limit` | Enumeration limit. |
| `dataset.annotations` | Named annotation paths or declaration objects. |
| `dataset.labels` | Field/dimension glob to display label mapping. |
| `dataset.*` | Additional format-specific fields validated by that adapter. |
| `views[]` | Explicit view/layout tree; no guessed automatic layout. |
| `views[].view` | Registered view component; its bindings/options follow its schema. |
| `views[].split` | Layout direction: row, column, grid. |
| `views[].children` | Nested view nodes. |

Complete existing documentation lives in the visualization project:

- [Every configuration key and example](https://github.com/dreamlake-ai/viz-workspace/blob/main/packages/docs/pages/dataset-viz/spec/%2BPage.mdx).
- [Storage drivers, adapters, and binding registries](https://github.com/dreamlake-ai/viz-workspace/blob/main/packages/docs/pages/dataset-viz/reference/%2BPage.mdx).
- [Every view component and its options](https://github.com/dreamlake-ai/viz-workspace/blob/main/packages/docs/pages/dataset-viz/views/%2BPage.mdx).

These are owning reference pages, not a second schema maintained by the CLI.

The schema is extensible: storage drivers, dataset formats, annotation codecs,
field payload kinds and component options have their own contracts. The full
[typed field definitions](https://github.com/dreamlake-ai/viz-workspace/blob/main/packages/viz/src/dataset-viz/types.ts)
and [field validation](https://github.com/dreamlake-ai/viz-workspace/blob/main/packages/viz/src/dataset-viz/dreamrc.ts)
are the authoritative reference for nested fields, bounds and component-specific
options. This index does not impose a new wrapper or migrate existing files.
