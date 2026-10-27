<!-- generated from https://viz.dreamlake.ai/dataset-viz/requirements.md at unknown; do not edit -->

<span id="prepare-your-data" />

# Read your files

First check whether a reader supports your recording's layout. Then check the
fields you want to display. A supported container can still contain an encoding
or tensor shape that a particular view cannot read.

<span id="existing-dataset-formats" />
<span id="other-containers" />
<span id="route-1-an-existing-dataset--nothing-to-do" />
<span id="route-3-a-container-we-cannot-read-yet" />

## Choose a reader

| Your data | `dataset.format` | Episode selection |
| --- | --- | --- |
| LeRobot v2.0, v2.1, or v3.0 | `lerobot` | `auto`; metadata at `meta/info.json` |
| UMI Zarr ReplayBuffer zip or supported v3 directory store | `umi` | `auto`; use `path` to select a store |
| Indexed MCAP v1 recordings | `mcap` | `auto` for root files, a glob, or one `path` |
| Directories of videos, images, and tables | `folder` | A directory glob |

Zarr support covers the layouts used by the [examples](viz-dataset-viz-templates.md),
not every codec or array layout. MCAP supports uncompressed, lz4, and zstd
chunks with supported Foxglove, ROS 1, or ROS 2 schemas. HDF5 and RLDS/TFRecord
need an export or a custom reader.

<span id="route-2-raw-recordings--the-folder-layout" />

## A folder of recordings

```text
recordings/
├── .dreamrc
└── episodes/
    └── run_001/
        ├── cam_front.mp4
        ├── joints.parquet
        └── annotations/
            ├── subtasks.vtt
            └── hands.json
```

Select it with `dataset: { format: folder, episodes: 'episodes/*/', fps: 30 }`.
Each matched directory is an episode. Media keep their filenames; other files
use basenames as field names, so `subtasks.vtt` is bound as `subtasks`.
The reader also lists `annotations/`; its fields override matching names at
the episode root.

Numbered stills form a frame sequence. Set `fps` to the actual recording rate.
CSV and Parquet traces use a timestamp-like column when available, otherwise
row indices. For synchronization, give numeric data and annotations the same
episode clock as the media.

## The shape each payload needs

| View input | Supported representation |
| --- | --- |
| Traces | Numeric scalars or vectors with timestamps |
| Image keypoints | `[J,2]` xy or `[J,3]` xy plus score, in image pixels |
| Depth | `[H,W]`, `[H,W,1]`, or a supported 16-bit PNG sequence |
| Point cloud | `[N,3]` xyz or `[N,6]` xyz plus rgb |
| Rigid pose | Translation plus quaternion, with the declared quaternion order |
| 3D points | `[J,3]` or flattened xyz coordinates |
| Labelled intervals | Start, end, and label; or a per-frame label column |

The reader must support how these values are stored. Use NaN for missing
numeric keypoints rather than a zero coordinate. Depth uses zero for a missing
reading. Check image dimensions, coordinate frames, and units in the rendered
result.

<span id="annotations-inside-the-container" />
<span id="labelled-intervals" />
<span id="image-keypoints" />
<span id="geometry-and-motion" />

## Annotations: files beside the data

WebVTT/SRT supplies intervals, COCO supplies image keypoints, and glTF supplies
geometry. Declare external paths with
[`dataset.annotations`](viz-dataset-viz-spec.md#datasetannotations--tracks-that-live-beside-the-data).
COCO files need an `fps` value to map image indices to episode time.

Annotations may also live inside a container: for example, LeRobot keypoint
features or an index column joined to a label table. The
[annotated dataset](viz-dataset-viz-templates.md#1-lerobot-with-annotation-features)
shows that arrangement.

<span id="cameras-the-encoding-that-actually-matters" />

<span id="camera-playback-and-seeking" />
<span id="verify" />
<span id="checklist" />

## Check playback

Use a browser-supported codec. Video seeking decodes from a preceding keyframe,
so long gaps between keyframes can make scrubbing slow. Check seeking against
your actual browser and storage service before diagnosing it as a chart delay.

HTTP storage must permit browser access and the range requests required by the
reader. Directory discovery also needs a listing service: Hugging Face provides
one; a static HTTP directory needs an
[`index.json` manifest](viz-dataset-viz-reference.md#the-http-indexjson-manifest).
