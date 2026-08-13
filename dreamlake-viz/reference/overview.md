# Quick start

`@dreamlake/viz` is the visualization library for robotics data — point clouds, TF
trees, occupancy grids, and image streams, rendered in the browser from a live ROS bridge
or a recorded bag. This page gets your first scene on screen in under two minutes.

## Install

Add `@dreamlake/viz` to any modern bundler. The package ships ESM and a CDN build —
both are tree-shakeable down to just the renderers you actually use.

```bash file="terminal"
# npm
npm install @dreamlake/viz

# or pnpm
pnpm add @dreamlake/viz
```

## Your first scene

A `Scene` binds a transport (rosbridge, foxglove ws, or a local `.bag`/`.mcap` file)
to a set of `Layer` objects. Layers subscribe to topics and own their own GPU
buffers — you can mount them in any order and toggle visibility independently.

```ts file="scene.ts"

const scene = new Scene({
  canvas: document.querySelector("#viewport"),
  transport: { kind: "rosbridge", url: "ws://robot.local:9090" },
  fixedFrame: "map",
});

scene.add(new TFTree());
scene.add(new Grid({ size: 20, divisions: 20 }));
scene.add(new PointCloud({ topic: "/velodyne_points", colorBy: "z" }));

await scene.start();
```

### HTML scaffold

The renderer needs a sized canvas and nothing else. `Scene` will observe the canvas
and adopt its CSS pixel size, including DPR.

```html file="index.html"
<canvas id="viewport" style="width: 100%; height: 100vh"></canvas>
<script type="module" src="./scene.ts"></script>
```

> **Note:** On Chromium-based browsers `@dreamlake/viz` uses WebGPU automatically; on Safari and
>   Firefox it falls back to WebGL2 with the same scene graph. Performance differences are
>   documented per-layer.

## Replay a recorded bag

Swap the transport for `kind: "file"` to play back a `.bag` or `.mcap` from disk —
same scene, same layers, no live robot required. The clock becomes scrubbable
via `scene.clock`.

```ts file="replay.ts"
const file = await fetch("/runs/2026-04-30.mcap").then(r => r.blob());

const scene = new Scene({
  canvas, fixedFrame: "odom",
  transport: { kind: "file", source: file },
});

scene.clock.on("tick", t => console.log(t.toFixed(3)));
await scene.start();
scene.clock.play(1.0); // 1× speed
```

## Built-in layers

Every layer is a small class with a topic, a message type, and render options. You can
subclass `Layer` for anything custom; below is the catalog that ships in the box.

| Layer | Message type | Notes |
| --- | --- | --- |
| `PointCloud` | `sensor_msgs/PointCloud2` | Color by axis, intensity, or RGB field. |
| `TFTree` | `tf2_msgs/TFMessage` | Renders frame axes; doubles as the transform graph. |
| `Grid` | — | Static reference grid, anchored to `fixedFrame`. |
| `OccupancyGrid` | `nav_msgs/OccupancyGrid` | 2D costmaps and SLAM output. |
| `Image` | `sensor_msgs/Image` | Decodes on a worker; supports compressed variants. |
| `MarkerArray` | `visualization_msgs/MarkerArray` | Cubes, spheres, lines, text — rviz-compatible. |

## React binding

Prefer JSX? `@dreamlake/viz/react` exposes the same primitives as components.
Layer order in JSX is render order; toggle visibility by mounting/unmounting.

```tsx file="App.tsx"

export function App() {
  return (
    <Scene
      transport={{ kind: "rosbridge", url: "ws://robot.local:9090" }}
      fixedFrame="map"
    >
      <TFTree />
      <Grid size={20} divisions={20} />
      <PointCloud topic="/velodyne_points" colorBy="z" />
    </Scene>
  );
}
```

> **Warning:** In React 18 dev with Strict Mode the `Scene` component will create & tear down a
>   transport on first mount. This is expected; production builds run a single mount.

## Where to go next

1. Skim the [layer catalog](#built-in-layers) — one section per layer, with full
   options and message-field mapping.
2. Wire up authoring & deeplinking via `scene.serialize()` for sharable snapshots.
3. Drop a `` next to your viewport for scrubbing across recorded segments.
