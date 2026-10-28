<!-- generated from https://docs.dreamlake.ai/annotations/reference.md at 0.1.102 757a8c39; do not edit -->

# Annotations Reference

  The complete API of `dreamlake.annotation`: the generic `Annotation` for
  custom-schema data (with `Schema` and `Track`), the
  `VideoAnnotation` preset (`video.annotation/v2`) with its
  `Episode` handle, and the storage rules that explain the constraints.

New here? Start with the step-by-step [Annotations guide](docs-annotations.md).

## The annotation family

Every DreamLake annotation is a **catalog row** (name, `schemaType`,
visibility) plus a **dreamdb space** (the data). `schemaType` is the one
dispatch key, applied the same way everywhere:

| consumer | known schemaType | unknown schemaType |
| --- | --- | --- |
| `Annotation.open` | returns the preset subclass (`video.annotation/v2` → `VideoAnnotation`) | returns the generic `Annotation` |
| web app | rich view | catalog entry (generic track browser: roadmap) |
| `Annotation.list(schema_type=…)` | server-side filter | same |

Unknown never refuses — data written by newer tools stays readable
generically.

**Names.** Every name-taking classmethod accepts `"name"` (your own
namespace) or `"namespace/name"` (an organisation you belong to; the server
authorizes per request). A leading `@` on the namespace is tolerated. At
most one `/`.

## Annotation (custom schemas)

```python
from dreamlake.annotation import Annotation, Schema, Track, sequence_anchors
```

### Lifecycle (classmethods)

| method | meaning |
| --- | --- |
| `Annotation.create(name, *, schema=None, schema_type=None, visibility="private")` | create. `schema=None` starts empty — declare tracks as you go (embeddings excepted: create-time only). `schema_type` is your own dispatch label, default `"custom/v1"`; a registered preset type errors and points at the preset's own `create` |
| `Annotation.ensure(name, *, schema=None, schema_type=None, visibility="private")` | open-or-create, rerun-safe. Existing annotations are **verified, never widened**: an explicitly expected `schema_type` errors on mismatch, and every field of `schema=` must already be declared |
| `Annotation.open(name)` | open; dispatches by the catalog's schemaType (see table above) |
| `Annotation.list(namespace=None, schema_type=None)` | `list[AnnotationInfo]` — `name`, `namespace`, `schema_type`, `visibility` |
| `Annotation.delete(name, *, purge=False)` | remove the catalog row; `purge=True` also deletes storage. A classmethod on purpose: no open, no credentials — and a safe distance from row-level `ann.db.delete(anchors)` tombstones |

### Tracks — the schema, in its live form

There is no `ann.schema`: `ann.tracks()` IS the schema — each `Track` handle
carries `name` / `kind` / `mime` / `dim`.

| method | meaning |
| --- | --- |
| `ann.add_track(name, kind, *, mime=None) -> Track` | declare a track (evolution is by addition only). Idempotent for a matching re-declaration; a kind change errors. `"embedding"` refused post-create |
| `ann.track(name) -> Track` | the handle; an unknown name errors here, eagerly |
| `ann.tracks() -> list[Track]` | every declared track |

`kind` is the dreamdb vocabulary, verbatim: `"video"` / `"image"` (with
`mime=`; JSON documents are `kind="image", mime="json"`) / `"scalar_float"`
/ `"scalar_int"` / `"scalar_bool"` / `"scalar_string"` /
`"scalar_categorical"` / `"scalar_timestamp"`. Track names:
`^[a-z0-9][a-z0-9_]*$`, max 64 chars; `anchor`, `_anchor`,
`_time_anchors` are reserved.

Tracks added through the bare `ann.db` handle are invisible to `tracks()`
(the SDK keeps a fields mirror in the space meta, key
`dreamdb.dataset.fields`); another process's `add_track` becomes visible
after `ann.reload()`.

### Row-wise write / read

| method | meaning |
| --- | --- |
| `ann.append_rows(rows) -> {"rows": n}` | one commit for the batch. Each row: `{"anchor": ns, track: value, ...}`. Sparse rows are the norm — **omit a field rather than passing None** |
| `ann.rows(start=None, end=None, tracks=None)` | rows in `[start, end)`, sorted, sparse (absent field = absent key). Video tracks are excluded by default; naming one in `tracks=` errors |

**Round-trip contract:** `rows()` returns exactly the shape `append_rows()`
accepts, and `t.read()` exactly what `t.append_range()` accepts —
`ann2.append_rows(ann1.rows(…))` needs no conversion.

### Introspection and recovery

| method | meaning |
| --- | --- |
| `ann.anchors(start=None, end=None) -> list[int]` | every item anchor, ascending — count (`len`), span (ends), upload verification |
| `ann.reload() -> ann` | refresh in place: catalog row, fields mirror, credential lease. Track handles survive. The fix for both documented stalenesses (cross-process `add_track`; the 12 h lease) |
| `ann.schema_type` / `ann.namespace` / `ann.name` | identity |
| `ann.visibility` / `ann.set_visibility("public")` | public annotations get anonymous presigned reads |
| `ann.db` | the live `dreamdb.Dataset` — the escape hatch. The meta keys `dreamdb.schema_type` / `dreamdb.dataset.*` are the SDK's; overwriting them breaks the handle |

### Anchors

Absolute int nanoseconds. Everywhere an anchor or range bound is taken,
a **tz-aware** `datetime` also works (naive datetimes are refused, not
guessed). Sequential data with no clock of its own uses row indices:
`sequence_anchors(n, start=0, step=1)`; continue an existing annotation from
`ann.anchors()[-1] + 1`.

### Write semantics (read this before scripting)

- **Append-only, write-once.** Re-writing the same (anchor, track) is
  undefined — the engine resolves same-anchor duplicates by content order,
  not write order. The SDK rejects duplicates within one batch; across
  calls it is on you. There is no update verb in v1.
- **Every `append*` / `ingest` call is one commit** (a new manifest, the
  ref advances). Batch with `append_rows` / `append_range`; a loop of
  single-point appends is slow and churns the ref history.
- **One writer per annotation at a time.** Concurrent writers lose updates.
  Readers are unrestricted.
- **Credentials are a 12 h lease** brokered at open. A stale handle raises
  `AnnotationError("credentials expired — call ann.reload()")`. One active
  platform annotation per process (the lease rides process-level AWS env
  vars).

## Schema

Mirrors `dreamdb.Schema` one-to-one — same method names, same parameters,
chainable — with two twists: every declaration is **recorded** (dreamdb's
own Schema cannot be introspected once built), and `required` is pinned
`False` (a required field could never be added later; all-optional is what
keeps `add_track` available).

```python
sch = Schema()
sch.add_video("cam", mime="h264")
sch.add_image("thumb", mime="jpeg")
sch.add_image("meta", mime="json")              # JSON documents, the dreamdb way
sch.add_embedding("clip", dim=512, lsh_bits=14) # create-time only
sch.add_scalar_float("temp")                    # ... _int/_bool/_string/_categorical/_timestamp

sch = Schema.from_fields([{"name": "cam", "type": "video", "mime": "h264"}, ...])
sch.to_fields()                                 # round-trip; the wire format
```

`to_fields()` / `from_fields()` carry the `fields` wire format (also
stamped into the catalog's `schemaJson` and the space meta). Validation is
eager and actionable: bad/reserved/duplicate names, `video` without
`mime`, `embedding` without an int `dim`, `required=True`, and `add_audio`
(unsupported — the engine cannot ingest it yet) all error at declaration.

## Track

Column-wise reads and writes. One verb, `append`, with the shape in the
name: no suffix = one point at a specific anchor, `_range` = a stretch of
timeline (and `ann.append_rows` = the row-wise member of the same family).

| method | meaning |
| --- | --- |
| `t.append(anchor, value) -> {"items": 1}` | one data point at one anchor |
| `t.append_range(items) -> {"items": n}` | `(anchor, value)` pairs — sorted by the SDK, one commit; a duplicate anchor within the batch errors (write-once) |
| `t.get(anchor)` | the value at exactly `anchor`, else `None` |
| `t.read(start=None, end=None)` | `[(anchor, value)]` in `[start, end)`, sorted. A declared-but-never-written track reads `[]` |
| `t.ingest(src, *, anchor, frag_seconds=2.0, height=None)` | video tracks only — see below |
| `t.name` / `t.kind` / `t.mime` / `t.dim` | metadata (`dim` on embeddings) |

**Values.** dreamdb's native representations pass through untouched:
`bytes` for blobs, int ns for timestamps, native scalars, float vectors.
On top, one-way input conveniences: file paths (`image`), tz-aware
`datetime` (`scalar_timestamp` and every anchor), `dict`/`list` on
`mime="json"` tracks, `.npy` paths and ndarrays (`embedding`,
dim-checked). Scalars are strict — `bool` into `scalar_float` errors
rather than coercing. `None` is always refused: absence is an omitted
field, not a null. Reads return the stored representation as-is, with one
exception: `mime="json"` tracks decode back to the `dict`/`list` that
went in.

**Video.** `t.ingest` is the only write path for video tracks
(`append` on one errors and says so). `height=None` is a lossless remux —
fast, but a CMAF track accepts exactly one codec configuration, so every
clip on the track must be identically encoded. `height=N` re-encodes to a
uniform h264 profile so mixed sources can share a track. Each clip
occupies `[anchor, anchor + duration)`; overlapping an existing span is
refused up front. Ranged video *reads* are not in v1 — playback goes
through the platform, raw bytes via `ann.db`.

## VideoAnnotation (the `video.annotation/v2` preset)

```python
from dreamlake.annotation import VideoAnnotation
```

An annotation of **episodes**: one recording each — one or more **camera**
videos on a shared clock, plus per-frame joint annotations and action
segments. Each episode owns a one-hour timeline slot; every camera,
annotation and search vector of the episode lives inside that slot, which
is why multi-camera playback is time-aligned with zero bookkeeping.
Per-episode operations live on the `Episode` handle.

The preset subclasses the generic `Annotation` and registers its schemaType:
`Annotation.open` on one of these returns this class.

### `VideoAnnotation.create(name=None, *, backend=None, visibility=None, preview_height=720, preview_fps=30.0, frag_seconds=2.0)`

| param | meaning |
| --- | --- |
| `name` | platform mode: catalog entry + managed bucket (needs `dreamlake login` / `DREAMLAKE_API_KEY`). Accepts `namespace/name` |
| `backend` | self-hosted mode: `file:///abs/path` or `https://…` S3 URL — no platform involved |
| `visibility` | `"private"` (default) / `"public"`; public annotations omit absolute source paths from metadata |
| `preview_height` / `preview_fps` / `frag_seconds` | the **encoding profile** — playback resolution, frame rate, and fragment length. Chosen once, for the annotation's lifetime, stored in the space meta. Per-episode calls never pass encoding |

Creation is never idempotent: an existing name/path errors instead of
silently forking a second history. (`VideoAnnotation.ensure(name)`
is the open-or-create form; it takes no schema arguments — the preset owns
its schema.)

### `VideoAnnotation.open(name=None, *, backend=None, preview_height=None, preview_fps=None, frag_seconds=None)`

Open by platform name or backend URI, strictly — a space stamped with a
different schemaType is refused (use `Annotation.open` or `dreamlake.db` for
those). The optional encoding kwargs **verify, never set**: pass the
values your script assumes and `open()` errors on mismatch — so the
`try open / except create` idiom cannot silently eat a config edit.

### `ann.add_episode(videos, *, episode_id=None, joints_pose=None, subtasks=None, recon_mesh=None, recon_pose=None, recon_camera=None, recon_hands=None, recon_gravity=None, meta=None, gid=None, raw=False) -> Episode`

The upload. One call transcodes every camera for browser playback and
commits annotations + metadata atomically. Returns the `Episode` handle;
the ingest report (per-camera fragment counts, annotation counts) is on
`epo.report`.

| param | meaning |
| --- | --- |
| `videos` | one path (single camera, stored as `main`) or `{camera: path}`. Camera names: `[a-z0-9_-]`, no `__` |
| `joints_pose` | a doc (binds to the **primary** camera — `main` if present, else the first) or `{camera: doc}` to annotate several views. Docs may also be JSON file paths |
| `subtasks` | episode-level action segments (doc or path) |
| `recon_mesh` | 3D-reconstruction: object meshes `{object: obj_text}` (episode-level, no camera) |
| `recon_pose` `recon_camera` `recon_hands` `recon_gravity` | 3D-reconstruction, per camera: object 6-DoF poses / pinhole intrinsics / MANO hands / gravity up-vector. Bare doc → primary camera, or `{camera: doc}`. All optional — see [Annotation formats](#annotation-formats) |
| `meta` | labels: `{"task": ..., "scene": ...}` — whitelist-only, **nothing is inferred** |
| `gid` | pin a specific slot (rarely needed) |
| `raw` | `True` additionally archives a lossless remux (roughly doubles the upload; best-effort on mixed sources) |

Fails fast, before any transcoding: any camera ≥ 3600 s, duplicate
`episode_id`, unknown meta key, joints naming a camera not in `videos`,
annotation fps disagreeing with its camera by >10 accumulated frames, or an
aspect ratio differing from that **camera's** existing track (aspect is per
camera — head 4:3 and wrist 16:9 coexist).

### `ann.episode(episode_id)` / `ann.episodes(after_gid=None, limit=None)` / `ann.episode_count()`

Lookup, listing, and count — all scale-safe: id lookups and counts go
through a slim per-episode index track (a `scalar_string` of bare ids —
one cacheable fetch yields the whole id→slot map; the fat `episode_meta`
column is only ranged-read for the slots actually needed).
Bare `episodes()` is the full listing (fine up to a few thousand); past
that, page: `episodes(limit=100)` then
`episodes(after_gid=page[-1].gid, limit=100)` — each page is one
slot-window read. `[e.meta for e in ann.episodes()]` recovers plain dicts.

### `ann.cameras() -> list[str]` / `ann.tracks() -> list[Track]`

What is in this annotation. `cameras()` is the union over episodes, `main`
first. `tracks()` returns the same `Track` handles as the generic layer
(name/kind/mime/dim) plus the preset extras `role` (`video_preview`,
`joints_pose`, `subtasks`, `recon_mesh`, `recon_pose`, `recon_camera`,
`recon_hands`, `recon_gravity`, `episode_meta`, `search`, `user`), `camera`,
and the derived `preset` flag. Preset reads still go through the named
APIs (`read_joints_pose`, `epo.read_track`, …).

### `ann.add_track(name, kind, *, mime=None) -> Track`

Declare a custom column. Same kind vocabulary as the generic layer, with
one extra rule: names must match `^x_[a-z0-9_]+$` — the user namespace the
preset promises never to claim, so your columns can never collide with a
future SDK release. Re-declaring the same name+kind is idempotent; changing
a track's kind is refused; embeddings cannot be added after creation. The
web viewer does not render `x_*` tracks; they are first-class data for
training loaders. Write and read through the Episode handle.

### `ann.embed_episodes(*, camera=None, fps=1.0, source_dir=None, batch_size=32) -> dict`

The search sweep: for **every** episode, sample frames at `fps` from one
camera's source file (primary unless `camera=`), encode with CLIP, encode
subtask texts with BGE, upload. Episodes commit one at a time — interrupt
and re-run freely. `source_dir` locates moved files via each camera's
recorded `source_rel`. Needs `pip install "dreamlake[search]"`. One episode
= `epo.embed()`.

### `ann.search(query, top_k=10, kind="both") -> list[dict]`

Natural-language moments: CLIP text tower against frame vectors and/or BGE
against subtask texts, fused by reciprocal rank. Returns
`[{"episode_id", "time_sec", "score", "source", "subtask"?}]`.
`kind`: `"frames"` / `"subtasks"` / `"both"`.

### `ann.encoding` / `ann.db`

`encoding` — the stored profile, read-only: the create-time defaults plus
`cameras`, each camera track's **adopted playback profile**
(`{width, height, fps}`, fixed by the aspect ratio of that camera's first
clip; every later clip is validated against it before any transcoding).
`db` — the live dreamdb handle:
the escape hatch for anything outside the preset (absolute-anchor appends,
columnar bulk reads, branching). Layout invariants are yours to respect.

## Episode

Obtained from `add_episode` / `ann.episode(id)` / `ann.episodes()`. The
identity triple (`episode_id`, `gid`, `anchor`) is immutable — handles never
dangle. The meta snapshot is a read convenience; **every write re-reads the
stored metadata at call time**, so a stale handle can never clobber a newer
revision.

| member | meaning |
| --- | --- |
| `episode_id` / `gid` / `anchor` | identity: your stable id, the slot number, the slot's base time |
| `report` | ingest report (only on the handle `add_episode` returned) |
| `meta` / `cameras` / `task` / `scene` / `duration_s` | snapshot reads, zero IO |
| `refresh()` | re-read metadata, returns self |
| `info()` | fresh meta + annotation summaries per camera (does IO) |

### Reads

```python
epo.read_joints_pose(camera=None)   # default: primary camera; None if unannotated
epo.read_subtasks()                 # episode-level; None if absent

# 3D reconstruction — one method per piece (default: primary camera):
epo.read_recon_mesh()               # episode-level {object: {obj, scale}} | None
epo.read_recon_pose(camera=None)    # {"frames": {...}} | None
epo.read_recon_camera(camera=None)  # intrinsics {fx,fy,cx,cy,width,height} | None
epo.read_recon_hands(camera=None)   # {"faces","frames"} | None
epo.read_recon_gravity(camera=None) # {"vec3d": [...]} | None
```

### `epo.add_cameras(videos, *, joints_pose=None, raw=False) -> dict`

Late-arriving cameras — add-only (video fragments occupy their slot and
cannot be replaced; re-sending an existing camera errors). Dict form adds N
cameras with one metadata write.

### `epo.revise(*, joints_pose=None, subtasks=None, recon_mesh=None, recon_pose=None, recon_camera=None, recon_hands=None, recon_gravity=None, meta=None) -> dict`

The one revision verb: everything passed lands in **one committed row**.
Storage is append-only — a revision is a new version, readers see the
newest, history stays addressable. `meta` takes the same whitelist as
`add_episode`; there is no inference, and passing values identical to what
is stored is reported as an error rather than a silent no-op.

### Custom-track values (declare with `ann.add_track` first)

```python
epo.set_track("x_quality", {"blurry": False})        # one value per episode (t=0)
epo.set_track("x_reward", 0.75, t_sec=12.0)          # or at any in-slot time
epo.append_track("x_reward", [(1.0, 0.1), (2.0, 0.2)])   # batch, one commit
epo.get_track("x_quality")                            # -> value | None
epo.read_track("x_reward", start_sec=0, end_sec=None) # -> [(t_sec, value)]
```

Values follow the track's kind (dicts/lists round-trip as JSON on
`image/json` tracks). Timestamps are seconds on the episode's own clock and
are bounds-checked to the slot. Re-writing the same (track, time) is a
revision — the preset's episode clock has revision semantics the generic
layer's absolute anchors do not. For high-rate series and cross-episode
bulk reads, drop to the engine with `epo.anchor_at(t_sec)` +
`ann.db.append_many` / `ann.db.iter_all_batches(fields=[...])`.

### Search, single episode

```python
epo.embed(camera=None, fps=1.0, video_path=None, source_dir=None, batch_size=32)
epo.add_search_vectors(frame_vecs=[(t, vec512), ...],        # CLIP space, L2-normed
                       subtask_vecs=[(t, vec384, label), ...])  # BGE space
```

`embed` resolves the source file `video_path` → `source_dir`/`source_rel` →
recorded absolute path, and refuses a resolved file whose duration
disagrees with the ingested camera's (wrong file); an explicit `video_path`
overrides the check. Vectors are searchable the moment they land — there is
no index-build step.

## Annotation formats

Wire-compatible with the web viewer's overlays. Joint coordinates live in
the pixel space of the camera whose track holds the document.

```jsonc
// joints_pose — per camera, one doc per episode
{
  "width": 1920, "height": 1080,   // REQUIRED: annotation-time pixel space
  "src_fps": 29.987,               // REQUIRED: frame k renders at k / src_fps
  "joint_order": ["wrist", ...],   // optional: names, index-aligned
  "bones": [[0, 1], ...],          // optional: skeleton edges
  "frames": {                      // REQUIRED, sparse: only annotated frames
    "0": [{"keypoints_2d": [[x, y], ...],           // REQUIRED per detection
           "is_right": 1, "det_conf": 0.9}]          // optional
  }
}

// subtasks — episode-level, one doc per episode
{
  "task": "wash the dishes",       // optional, NOT copied to episode meta
  "labeled_subtasks": [            // REQUIRED; gaps are fine
    {"start_sec": 0.0, "end_sec": 2.5, "subtask": "pick up plate"}
  ]
}
```

### Reconstruction (3D)

An optional third modality: 3D hand–object reconstruction, as five flat
`recon_*` arguments (one per stored track). Geometry is in the camera's
**OpenCV frame** (x-right / y-down / z-forward), metres, quaternion **wxyz**,
frame `f` ↔ time `f/fps`; colour is not stored. `recon_mesh` is episode-level;
the other four are per-camera (bare doc → primary, or `{camera: doc}`).

```python
epo = ann.add_episode(
    video, subtasks=..., joints_pose=...,
    recon_mesh={name: obj_text},                          # or {name: {"obj","scale"}}
    recon_pose={frame: {name: {"t":[x,y,z], "q":[w,x,y,z]}}},
    recon_camera={"fx":.., "fy":.., "cx":.., "cy":..},    # pinhole intrinsics (→ recon_camera__<cam>)
    recon_hands={"faces": {"left":[[a,b,c]...], "right":[...]},   # optional
                 "frames": {frame: {"left": {"verts":[[x,y,z]...], "joints":[[x,y,z]...]}, "right": {...}}}},
    recon_gravity=[x, y, z],                              # optional; up direction
)
epo.revise(recon_pose={"left": ...}, recon_camera={"left": ...})   # fill a camera in later
```

Each is optional; at least one present. Re-passing a piece revises it. `recon_pose`
tells a bare per-frame doc from a `{camera: doc}` map by whether the keys are
frame indices vs camera names — so don't name a camera a bare number.

## Storage semantics worth knowing (preset)

- **Slots.** Episode `gid` occupies `[gid × 1 h, (gid+1) × 1 h)` on one
  timeline; slots are never reused; any single camera clip ≤ 3600 s.
- **Encoding is annotation-lifetime.** Every clip on one camera track shares
  one init segment, so height/fps/fragment length cannot vary per episode —
  that is why they live on `create`, not `add_episode`.
- **Aspect ratio is per camera track**, not per annotation.
- **Revisions are versioned, bounded, and never in-place.** Each
  episode-level value carries up to 1024 revisions; readers always resolve
  to the newest; history stays in the timeline.
- **Video is add-only.** Cameras can join an episode; fragments are never
  replaced.
- **`x_` is yours, everything else is the contract.** Preset track names
  and metadata keys evolve only by addition, in SDK releases; tools render
  what they recognize and skip the rest.
