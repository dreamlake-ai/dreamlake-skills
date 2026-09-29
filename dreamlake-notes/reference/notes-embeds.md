# Embeds and query arguments

This feature is **unreleased**. Existing references continue to open side panels.

Use `inline="4:3"` or `inline="16:9"` to render an artifact or web page inside
the Note. The value both enables the embed and sets its aspect ratio.
`inline="true"` is shorthand for `inline="16:9"`. Omit `inline` (or set it to
`"false"`) to keep the existing click-to-open panel tag.

## Sizing models

**Responsive ratio:** fill the available document width and derive height from
the ratio. This is the default model; it responds when the Note panel resizes.

```markdown
:artifact[geyang/dashboard]{inline="4:3"}
:artifact[geyang/pitch-deck#slide-3]{inline="16:9"}
```

**Fixed width with ratio:** request a pixel width and derive height from the
ratio. Width still shrinks to fit a narrower document.

```markdown
:artifact[geyang/dashboard]{inline="4:3" width="640"}
```

**Fixed height:** use an explicit height for a scrollable report or web page.
Height overrides the ratio; width remains responsive unless specified.

```markdown
:preview[https://example.com/report]{title="Report" inline="true" height="480"}
:artifact[geyang/dashboard]{inline="4:3" width="640" height="400"}
```

**Content zoom:** the default `zoom="fit"` gives responsive content the embed's
viewport dimensions. It does not inspect or automatically shrink a fixed-size
third-party page. Use a percentage to scale its content independently of the
outer dimensions; 75% provides a larger internal layout viewport.

```markdown
:preview[https://example.com/report]{inline="16:9" zoom="75%" border="false"}
```

| Argument | Values | Default |
| --- | --- | --- |
| `inline` | `"true"`, `"false"`, or a positive integer ratio such as `"4:3"` | `"false"` |
| `width` | Positive pixels (bare number or `px`, up to 4096), or 1–100% | `"100%"` |
| `height` | Positive pixels (bare number or `px`, up to 4096) | From ratio |
| `zoom` | `"fit"` or integer percentages from `"25%"` through `"200%"` | `"fit"` |
| `border` | `"true"` or `"false"` | `"false"` |

Ratio terms are integers from 1 through 999. Sizing, zoom and border arguments
require an enabled inline embed; invalid sizing values remain literal source. CSS and sandbox permissions cannot
be changed through these arguments. Use a standalone line for larger
embeds. Hover or focus a reference, then choose the pin + **Embed** bubble below it to make it inline. The bubble contains only the pin icon and **Embed**. In an inline web preview, hovering or focusing its header shows the destination URL beside the preview tag. Drag the
bottom capsule to change height, or the left/right capsules to change width.
Capsules appear when the pointer reaches their edge or they receive keyboard focus.
Capsules also accept arrow keys (16px steps; Shift for 64px). A drag saves pixel
dimensions and preserves content query arguments. Use the unpin icon in the preview header to collapse it back to a reference;
content query arguments are preserved and inline sizing is removed. Edit the
directive in source to return to percentage width or ratio sizing. Read-only views do
not expose editing controls.

Inline artifacts use the isolated, content-only artifact renderer with the
current reader's existing access; embedding does not grant access or create a
share link. Web pages must allow iframe embedding. Static HTML snapshots retain
inert references and never load embedded content.

## Query pass-through API

Keep the artifact reference or page URL in brackets. Put embed options and
content-specific query arguments together in braces:

```markdown
:artifact[geyang/video-viewer]{inline="4:3" view="contact-sheet" columns="4" frames="12"}
:preview[https://example.com/video]{inline="16:9" view="storyboard" start="30"}
```

These resource names are examples, not preinstalled artifacts. The referenced
artifact or website must implement the requested views.

Notes consumes `inline`, `width`, `height`, `zoom`, and `border`. Resource identity
fields (`namespace`, `id`, `fragment` for artifacts; `url` and `title` for previews)
also belong to Notes. All other valid arguments become public query parameters;
they are never interpreted as HTML attributes, CSS, or sandbox flags.

For the first example, the artifact receives
`?view=contact-sheet&columns=4&frames=12`. Its ordinary viewer link uses
`?art.view=contact-sheet&art.columns=4&art.frames=12`. Only the viewer URL uses
`art.`; do not prefix directive arguments. A fragment stays in the reference:

```markdown
:artifact[geyang/video-viewer#scene-3]{inline="16:9" view="player" start="30"}
```

Preview arguments are merged into the URL query. Brace arguments replace an
existing value with the same key; unrelated URL parameters and the fragment stay
intact. Values use quoted strings and are URL-encoded automatically, including
nested URLs. Do not pre-encode them:

```markdown
:preview[https://example.com/viewer?theme=dark]{inline="16:9" src="https://example.com/clip.mp4?a=1&b=2" view="contact-sheet"}
```

The same arguments work on clickable tags without `inline`: opening the side
panel or the ordinary viewer link carries the query to the renderer.

### Read and update configuration inside an artifact

Use the existing artifact route API rather than `window.location`: HTML artifacts
run in a nested `about:srcdoc` frame.

```html
<div id="summary"></div>
<script>
  const route = window.dreamlake.route;
  function render() {
    const query = new URLSearchParams(route.search);
    const view = query.get('view') || 'player';
    const columns = Math.max(1, Math.min(8, Number(query.get('columns')) || 4));
    document.getElementById('summary').textContent = `${view}, ${columns} columns`;
  }
  const unsubscribe = route.subscribe(render);
  render();
  // For example, a view-selector control can call:
  async function showStoryboard() {
    const query = new URLSearchParams(route.search);
    query.set('view', 'storyboard');
    await route.navigate({ search: query.toString() }, { replace: true });
  }
</script>
```

Route changes stay inside the embed; they do not rewrite the Note or inherit its
page query. Dispose subscriptions when a renderer unmounts. See the full
[artifact routing contract](https://docs.dreamlake.ai/artifacts/#artifact-paths-and-local-routing) for navigation,
fragments, lifecycle, and access boundaries.

### Argument validation

Names must match `[A-Za-z][A-Za-z0-9_.-]{0,63}`. Values are double-quoted strings;
the renderer validates their meaning and parses numbers or JSON. Duplicate
arguments are invalid. Reserved route names such as `share`, `token`, `auth`,
`authorization`, `cookie`, `project`, `namespace`, `instanceId`, `__proto__`,
`prototype`, `constructor`, and `dreamlake` (including their `.`, `_`, or `-`
suffix forms) cannot be forwarded. Encoded route state is limited to 8192
characters. Invalid directives remain literal text.

Query data is public configuration, not authorization. Notes never forwards its
own URL parameters or credentials. References and queries do not grant access.

## Video, storyboard, and contact-sheet contracts

A video artifact can define these query arguments without changing Notes:

| Argument | Suggested renderer meaning |
| --- | --- |
| `view` | `player`, `storyboard` (ordered scene cards), or `contact-sheet` (frame grid) |
| `src` | A video source supported by that renderer |
| `columns` | Number of grid columns |
| `frames` | Number of evenly sampled frames |
| `interval` | Sample spacing in seconds, instead of a fixed frame count |
| `start`, `end` | Sampling or playback range in seconds |

This is a renderer API convention, not a built-in Notes video feature. A renderer
should bound sampling work, show timestamps, and make a frame open playback at
that timestamp. It should reject conflicting `frames` and `interval` options.
A future `:contact-sheet[...]` directive could be shorthand for this renderer;
it is not currently implemented.

The artifact sandbox currently blocks arbitrary remote video-file loading.
A self-contained artifact can bundle video or precomputed frames. Passing a
`src` URL does not bypass that policy; general remote-video sampling needs an
authorized host media bridge. A separately hosted viewer used through `:preview`
can implement its own video access, subject to that site's embedding policy and
its media origin's CORS rules.

Parent-scoped user-data access is tracked in
[issue #837](https://github.com/dreamlake-ai/dreamlake-workspace/issues/837).
The embedding parent and current viewer must determine the authorized context;
the artifact owner's identity alone is insufficient.
