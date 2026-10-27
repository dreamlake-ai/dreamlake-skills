# Validate the `.dreamrc` and iterate

```bash
# from a checkout of dreamlake-ai/viz-workspace, in packages/viz/
npx tsx scripts/check-dreamrc.mts ./draft.dreamrc   # decodes every binding
```

Errors are written to be fixed mechanically — each names the offending key,
the allowed values, and the nearest registered name
(`views[2].view 'lineChart2' is not registered (did you mean 'lineChart'?)`).
Loop write → validate → fix until clean; then confirm every binding decodes
the payload you expected. One catch: a root-arranged draft (no `storage:`)
cannot resolve standalone — temporarily add a `storage:` line while
validating, drop it before upload.

The gallery ([reference/viz-dataset-viz-gallery.md](../reference/viz-dataset-viz-gallery.md))
is a **playground**: 13 complete `.dreamrc` files over public data. Pick the
entry closest to the dataset, edit the YAML in the left pane, and the
render follows every valid edit — point its `storage:` at your data to
tune against the real thing.

## Reference

Fetch these when you need option-level detail — never invent keys:

- Spec — every `.dreamrc` key, defaults, errors, TypeScript API:
  [reference/viz-dataset-viz-spec.md](../reference/viz-dataset-viz-spec.md)
- Views — every view, its options, live demos:
  [reference/viz-dataset-viz-views.md](../reference/viz-dataset-viz-views.md)
- Reference — inventory kinds, payload contracts, storage drivers,
  `index.json` manifests:
  [reference/viz-dataset-viz-reference.md](../reference/viz-dataset-viz-reference.md)
- Requirements — folder recipe, shape rules, annotations, camera encoding:
  [reference/viz-dataset-viz-requirements.md](../reference/viz-dataset-viz-requirements.md)
- Templates — two annotated Hub datasets to copy:
  [reference/viz-dataset-viz-templates.md](../reference/viz-dataset-viz-templates.md)
- Architecture — why the system has this shape:
  [reference/viz-dataset-viz-overview.md](../reference/viz-dataset-viz-overview.md)
- First dataset walkthrough:
  [reference/viz-dataset-viz-start.md](../reference/viz-dataset-viz-start.md);
  package overview: [reference/viz-index.md](../reference/viz-index.md);
  full corpus: https://viz.dreamlake.ai/llms-full.txt

When the file is clean, place it at the dataset root with no `storage:` block
([connect](connect.md)).
