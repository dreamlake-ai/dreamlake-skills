# Custom Schema Python

## Flow B — any schema you define (generic Annotation)

For sensor logs, tabular/time-series data, embeddings, image sets — data
that is not annotated video. Anchors are absolute int nanoseconds (tz-aware
`datetime` also accepted; naive refused); clockless data uses row indices
via `sequence_anchors`.

```python
from dreamlake.annotation import Annotation, Schema, sequence_anchors

# Schema mirrors dreamdb.Schema exactly. Embeddings MUST be declared here
# (create-time only); everything else can be added later with add_track.
sch = Schema()
sch.add_scalar_float("temp")
sch.add_image("meta", mime="json")        # JSON documents = image + mime="json"
sch.add_embedding("clip", dim=512)
# also: add_video(mime=), add_image(mime=), add_scalar_int/_bool/_string/
#       _categorical/_timestamp. required is always False. No audio (engine limit).

ann = Annotation.ensure("sensor-logs", schema=sch)   # open-or-create; verifies, never widens
# ann = Annotation.ensure("acme/sensor-logs", ...)   # org namespace
# schema_type="acme.sensors/v1" stamps your own dispatch label (default "custom/v1")

# Row-wise (one anchor × many tracks). SPARSE: omit a field, never pass None.
ann.append_rows([
    {"anchor": 0, "temp": 21.5, "meta": {"unit": "C"}, "clip": vec512},
    {"anchor": 1, "temp": 21.7},
])

# Column-wise (one track). append = one point; append_range = a stretch.
t = ann.add_track("humidity", "scalar_float")    # evolve anytime (kind change refused)
t.append(0, 0.41)
t.append_range(zip(sequence_anchors(3, start=1), [0.42, 0.44, 0.43]))

# Video tracks write ONLY via ingest (height=None lossless remux — clips must
# share one codec config; height=N re-encodes so mixed sources can share).
ann.add_track("cam", "video", mime="h264")
ann.track("cam").ingest("clip.mp4", anchor=0, height=480)

# Read back — same shapes you wrote (round-trip contract).
ann.rows(start=0, end=10)        # [{"anchor": 0, "temp": 21.5, ...}] video excluded
t.read(start=0)                  # [(anchor, value)]; unwritten track -> []
t.get(0)                         # value | None
ann.anchors()                    # what landed: len = count, ends = span
ann.tracks()                     # the live schema: Track handles (name/kind/mime/dim)
```

Values: pass dreamdb-native representations (bytes / int ns / scalars /
float vectors) or the conveniences: file path for image, dict/list on
mime="json", `.npy` path or ndarray for embedding (dim-checked). Scalars
are strict (bool into scalar_float errors).

## Rules that explain most errors

- **Write-once.** Re-writing the same (anchor, track) is undefined — the
  engine resolves same-anchor duplicates by content, not write order.
  Duplicates within one batch error. No update verb; plan anchors up front.
  (Preset episode tracks via `epo.set_track` DO have revision semantics.)
- **One commit per `append*`/`ingest` call.** Batch with
  `append_rows`/`append_range`; never loop single points.
- **Single writer per annotation**; readers unrestricted.
- **12 h credential lease.** "credentials expired" → `ann.reload()` (also
  the fix when another process's `add_track` is not visible yet). One
  active platform annotation per process.
- **`ensure` verifies, never widens**: missing tracks from `schema=` error —
  declare them explicitly with `add_track`.
- Track names `^[a-z0-9][a-z0-9_]*$`; `anchor`/`_anchor`/`_time_anchors`
  reserved. Preset: encoding fixed at create; one aspect ratio per camera
  track; ≤3600 s per clip; `meta=` accepts only task/scene.
- Lifecycle: `Annotation.list(namespace=, schema_type=)`,
  `Annotation.delete(name, purge=True)` (classmethod — purge also deletes
  storage), `ann.set_visibility("public")` for anonymous reads.
