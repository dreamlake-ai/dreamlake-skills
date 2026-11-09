# Build and repair artifact charts

Inspect the artifact's source, installed package version, parent layout, and
existing chart controls before editing. For a built application, use
[static builds](publish.md#static-builds); a package import belongs in the
application build, not in the single-file React template's global scope.
Preserve the user's requested artifact format and publication scope.

1. Read the [Viz setup guide](../reference/viz-index.md) and the applicable
   component contract: [episode line charts](../reference/viz-components-episode-line-chart.md)
   or [parallel coordinates](../reference/viz-components-parallel-coordinates.md).
   Check that the installed release supports the example before using it.
2. For a line-weight change, inspect chart-level settings, per-series overrides,
   active emphasis, and any UI control that updates them. Use the documented
   component props and shared examples; avoid an SVG-wide CSS override that
   also changes ticks, ranges, or cursor markers. Keep the control's state
   consistent across charts when the user requests a shared control.
   Start with the component's readable default; compact sizing alone is not a
   reason to reduce primary strokes to hairlines. Preserve explicit user choices.
3. Preserve recorded values, units, colors, selection, zoom, and seek behavior.
   Set the chart size from its real parent layout; inspect compact sizing,
   surface styling, and cursor ownership in the component guide rather than
   copying a full-page example into a small embed.
4. For linked chart, timeline, video, or 3D inspection, read the
   [shared pin and preview example](../reference/viz-components-episode-timeline.md#shared-click-to-pin-and-hover-preview).
   Keep the group's cursor controller shared and distinguish transient inspection
   from a committed return time. Preserve hover while pinned; verify ownership
   handoffs, leave/return behavior, external navigation, and playback together.
   Include keyboard and touch paths in the same integration checks.
5. Build and inspect the result in both themes at the intended embedded size.
   Exercise the width control, a series override, and active selection; check
   that emphasis stays legible and the axes and markers retain their intended
   weight. Exercise the readout at chart edges and during ancestor scrolling;
   compare its pointer placement and viewport bounds with the component contract.
   Keep screenshot or browser-test evidence tied to the installed version.

For an SDK-only or repository component request, use the component docs and
validate locally; artifact publication is unnecessary unless requested. A
request for an unsupported chart capability does not justify invented props:
identify the missing contract and the owning package before proposing a change.
After artifact authoring, hand off to [publish](publish.md) only within the
user's authorized publication scope.
