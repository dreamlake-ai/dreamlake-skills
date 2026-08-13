# From dataset to visualization

**Upload a dataset laid out per its format spec, drop one `.dreamrc` at its
root, and the whole dataset renders.** This page is the end-to-end path: what
to upload, how to recognize what you have, and how to write the file — for
humans and for AI agents alike.

**Or let an AI do the writing.** Everything on this page ships as an

  const rc = validateDreamrc(parseYaml(text))
  const { episodes } = await resolveDataset(rc, {
    rootStorage: { driver: 'http', url: 'https://…/my-dataset' },
  })
  for (const ep of episodes) console.log(ep.name, await ep.episode.fields())
  ```

Common errors and what they mean:

| message | fix |
| --- | --- |
| `dataset.format '…' is not a registered format` | typo, or the format isn't supported yet — see the table in §2 |
| `views[n].component '…' is not registered` | typo — the message lists the registry |
| `episodes glob "…" — '**' is not supported` | use one `*` per path segment |
| a panel renders "no fields matched" | your `fields`/`series` pattern missed the catalog — render `fieldsCatalog` once and copy the real names |
| video plays but overlays don't draw | annotation track missing from the dataset entry file, or its `width/height/src_fps` don't match the camera |
