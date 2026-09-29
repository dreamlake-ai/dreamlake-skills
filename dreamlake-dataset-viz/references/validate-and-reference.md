# Validate And Reference

## 5. Validate and iterate

```bash
npx tsx scripts/check-dreamrc.mts ./draft.dreamrc   # decodes every binding
```

Errors are written to be fixed mechanically — each names the offending key,
the allowed values, and the nearest registered name
(`views[2].view 'lineChart2' is not registered (did you mean 'lineChart'?)`).
Loop write → validate → fix until clean; then confirm every binding decodes
the payload you expected. One catch: a root-arranged draft (no `storage:`)
cannot resolve standalone — temporarily add a `storage:` line while
validating, drop it before upload.

The gallery at https://viz.dreamlake.ai/dataset-viz/gallery.md is a
**playground**: 13 complete `.dreamrc` files over public data. Pick the
entry closest to the dataset, edit the YAML in the left pane, and the
render follows every valid edit — point its `storage:` at your data to
tune against the real thing.

## Reference

Fetch these when you need option-level detail — never invent keys:

- Spec — every `.dreamrc` key, defaults, errors, TypeScript API:
  https://viz.dreamlake.ai/dataset-viz/spec.md
- Views — every view, its options, live demos:
  https://viz.dreamlake.ai/dataset-viz/views.md
- Reference — inventory kinds, payload contracts, storage drivers,
  `index.json` manifests: https://viz.dreamlake.ai/dataset-viz/reference.md
- Requirements — folder recipe, shape rules, annotations, camera encoding:
  https://viz.dreamlake.ai/dataset-viz/requirements.md
- Templates — two annotated Hub datasets to copy:
  https://viz.dreamlake.ai/dataset-viz/templates.md
- Architecture — why the system has this shape:
  https://viz.dreamlake.ai/dataset-viz/overview.md
- Package overview: https://viz.dreamlake.ai/index.md · full corpus:
  https://viz.dreamlake.ai/llms-full.txt
