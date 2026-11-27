# Design an artifact interface

For a new interface, implement a **Vike page in TypeScript and React with DreamLake UIKit**.
A request for an “artifact” leaves this default in effect, even for a small review tool.
Aim for a meticulously polished interface, excellent UX and a high-quality visual experience.
Honor explicit choices of style, stack and format. Preserve the design when editing.

- **Compose the page.** Make the task title the first visible text. Omit branding bars, category
  labels above the title, slogans and repeated explanations. Use spacing and alignment before
  frames and borders. Start the page and title area on `background: var(--bg)` with
  `color: var(--ink)`. Let the heading inherit both. Use UIKit tokens for panels,
  controls, focus and selection. Keep illustration colors inside the illustration.
- **Choose what to show.** For alternative visual items, use selectable image
  thumbnails and one active detail. Keep synchronized signals together. Use a list
  or disclosure for text records.
- **Reuse controls.** Read the [setup](https://uikit.dreamlake.ai/index.md), search the
  [component index](https://uikit.dreamlake.ai/llms.txt), and check the installed public
  package's exports and README before implementing a control. Bundle its components
  and CSS as documented. Preserve tab state and width when switching views.
- **Polish the result.** Inspect the rendered interface at desktop and narrow widths
  in both themes. Complete its main task by pointer and keyboard. Refine hierarchy,
  contrast, focus and clipping until the selection and next action are clear.
  Compare the first visible text with the main heading and remove anything above it.
  Verify the heading and its nearest painted background against the UIKit theme
  in both modes, including any header or banner wrapped around it.

Before delivery, locate the actual Vike page, its UIKit component imports and the
prerendered client entry. Complete missing parts unless the user chose another format.
For publication, use the [static build workflow](publish.md#static-builds).
For an explicitly requested standalone file, bundle its dependencies and check it in the sandbox.
