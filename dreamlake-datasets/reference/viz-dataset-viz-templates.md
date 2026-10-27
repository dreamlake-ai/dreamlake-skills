<!-- generated from https://viz.dreamlake.ai/dataset-viz/templates.md at unknown; do not edit -->

<span id="templates" />

# Dataset examples

Choose the example closest to how your data is stored. Each demo reads the
`.dreamrc` published with its dataset; inspect the config, then change the field
bindings in the [playground](viz-dataset-viz-gallery.md).

## 1. LeRobot with annotation features

This recording includes an egocentric camera, hand keypoints, and subtask
labels. Scrub to check whether the hand overlay and task interval agree with
the image.

Keypoints are numeric features inside the dataset. Subtasks use an integer
column with a label table. Use this arrangement when your annotation pipeline
can write features alongside the original measurements.

## 2. A folder of video and sidecar files

The ceramics recording keeps a video, a COCO keypoint file, and WebVTT labels
in each episode directory. It produces similar views without putting the data
in a LeRobot container.

The folder reader discovers `annotations/`. The config binds `hand_keypoints`
as keypoints and `subtasks` as segments; changing a filename requires changing
an explicit binding to that field.

## 3. A folder of MCAP recordings

Each file is one nuScenes scene. Camera, lidar, and transform schemas provide
the data for synchronized media and 3D views. Use the timeline to change time
and drag within a 3D panel to inspect another angle.

This example uses nuScenes data under CC BY-NC-SA; consult the
[dataset README](https://huggingface.co/datasets/live9080/dreamlake-mcap) before
reusing the recordings.

<span id="more-examples" />
<span id="validate-your-example" />
<span id="upstream-datasets-untouched" />
<span id="not-ours-and-just-as-valid" />
<span id="where-the-dreamrc-goes" />
<span id="check-before-you-ship" />

## Try another modality

The [view examples](viz-dataset-viz-views.md) isolate depth, point clouds,
trajectories, and motion reconstruction. Start there when the question is how
to display one field rather than how to arrange a complete dataset.
