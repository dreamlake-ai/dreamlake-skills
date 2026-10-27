# Reference an artifact from a Note (development preview)

Prefer the Notes rich-component form:

```markdown
:artifact[geyang/pitch-deck]
```

Use the owner namespace and the stable artifact id returned by the CLI
([list](list.md)). Editing the Note itself belongs to the `dreamlake-notes`
skill; this page covers only the reference syntax.

## Rules

- Click the copy icon after the artifact header title to copy the full
  bracket reference, including the namespace and complete id. Artifact
  headers use this icon in both wide and compact layouts; Note headers keep
  their short hash badges. Copying does not create a share link or change
  access.
- Brackets hold primary content; optional named attributes belong in braces.
  This follows the
  [remark-directive extension](https://github.com/remarkjs/remark-directive),
  not core CommonMark; the resource semantics are DreamLake-specific.
- Saved `:artifact{namespace="geyang" id="pitch-deck"}` and
  `#artifact:geyang/pitch-deck` remain accepted by the local development
  UI/API. **Do not bulk-rewrite saved references.** Bare
  `:artifact{namespace/id}` is invalid.
- The tag resolves its title through authorized metadata and opens the
  reusable artifact panel to the right of the Note, including in project
  views. It does not upload content, grant access or change sharing.
  Preserve the complete source token. Static API HTML keeps it unresolved
  and maps the whole token atomically; it never embeds a share-token URL or
  private content.
- Production deployment of artifact tags is not yet verified; do not promise
  support in older clients.

## Fragment (slide / section) references

`:artifact[namespace/id#slide-3]` preserves a target inside the artifact;
`#/3` is valid only if the artifact defines that route. The named form
`:artifact[namespace/id]{fragment="slide-3"}` is also accepted. Preserve
the exact source and percent encoding; do not supply the fragment twice or
infer slide numbering.

Clicking sends the fragment to the panel through `dreamlake.route.hash`
([routing](routing.md)); another reference to the same artifact reuses its
panel and updates its local route without reloading the iframe or changing
the Note/project URL. This requires the companion UI deployment — a skill
update does not deploy panel behaviour. Never put a share token inside
rich-reference attributes.

Owning pages:
[Reference an artifact from a Note](../reference/docs-artifacts.md#reference-an-artifact-from-a-note-development-preview),
[Artifact panels in Notes](../reference/docs-artifacts.md#artifact-panels-in-notes-development-preview)
and the
[Notes grammar](https://docs.dreamlake.ai/notes/#artifact-references-development-preview).
