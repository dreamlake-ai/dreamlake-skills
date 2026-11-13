<!-- generated from https://docs.dreamlake.ai/notes/rows.md at 0.1.158 e3e61780; do not edit -->

# Images, rows and video

## Rows and video

A `:::row` block lays images side by side, one cell per image. Insert one
with **Row** in the `/` menu. Each caption is the image's title, or its alt
text when it has no title.

```markdown
:::row
![Lake at dawn](/images/notes/rows/dawn.svg '1 · Dawn')
![Lake at noon](/images/notes/rows/noon.svg '2 · Noon')
![Lake at dusk](/images/notes/rows/dusk.svg '3 · Dusk')
:::
```

Cells share one height, and each cell's width follows its image's aspect
ratio. Add `{width=… height=…}` right after an image (pixels, no space) to
size its cell before the image loads.

```markdown
:::row
![Wide](/images/notes/rows/wide.svg){width=1600 height=900}
![Tall](/images/notes/rows/tall.svg){width=800 height=1200}
![Square](/images/notes/rows/square.svg){width=1000 height=1000}
:::
```

In a memo narrower than 480px, the cells stack. This is a 320px memo at half
size:

```markdown
:::row
![Wide](/images/notes/rows/wide.svg){width=1600 height=900}
![Tall](/images/notes/rows/tall.svg){width=800 height=1200}
![Square](/images/notes/rows/square.svg){width=1000 height=1000}
:::
```

Click a row image to open it in the image viewer. The rail lists the row's
images with the rest of the memo's.

![The image viewer open on a row image: the image large in the center, a rail of the memo's images on the right.](https://docs.dreamlake.ai/images/notes/rows/lightbox.png)

- Any other block in a row (a paragraph, a list, a `:video[…]`) is one cell.
  To put several blocks in one cell, wrap them in `:::col` … `:::` and give
  the row more colons (`::::row` … `::::`).
- To edit a row's Markdown, click a caption or the space around the cells,
  Alt+click an image, or move the caret onto the row.
- Rows work only at the top level. Inside a list, quote or code, the fences
  stay text. An unclosed or malformed row shows as its source. Other Markdown
  viewers show the fences as text. The Markdown export and the Memos API keep
  the source exactly.

The retired `<Columns>` / `<ColumnBreak>` layout still renders, as a row of
two cells, but menus no longer offer it. Write `:::row` for new content.

For video, put a direct HTTPS media URL and title in a standalone directive:

```markdown
:video[https://example.com/demo.mp4]{title="Demo walkthrough"}
```

Use **Video** in the `/` insertion menu for a template.
Videos have native playback controls, do not autoplay and initialize near the
viewport. A title and source link remain available if playback fails. Entering
source mode pauses playback; returning to preview can reset it. Use captioned
media or add a transcript for speech. This increment does not provide captions,
private attachment streaming or arbitrary video-site embeds. Media URLs are
used as supplied; share public media bearer URLs only with their intended
audience. Print/PDF output contains the video title and link.
