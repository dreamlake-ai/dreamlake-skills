# Notes References

## Reference in Notes (development preview)

Prefer the Notes rich-component form:

```markdown
:artifact[geyang/pitch-deck]
```

Click the development artifact header’s `#…` badge to copy the full bracket
reference. The badge shows the last six ID characters, but copying retains the
namespace and complete ID. This does not create a share link or change access.

Use the owner namespace and stable artifact ID returned by the CLI. Brackets hold
primary content; optional named attributes belong in braces. This follows the
[remark-directive extension](https://github.com/remarkjs/remark-directive), not core
CommonMark; resource semantics remain DreamLake-specific. Saved
`:artifact{namespace="geyang" id="pitch-deck"}` and `#artifact:geyang/pitch-deck`
remain accepted by the local development UI/API. Do not bulk-rewrite saved references.
Bare `:artifact{namespace/id}` is invalid.
The tag resolves its title through authorized metadata and opens the reusable
artifact panel to the right of the Note, including in project views;
it does not upload content, grant access, or change sharing. Preserve the complete
source token. Static API HTML keeps it unresolved and maps the whole token atomically;
it does not embed a share-token URL or private content. Production deployment of
artifact tags is not yet verified; do not promise support in older clients.
See the owning [artifact guide](https://docs.dreamlake.ai/artifacts/#reference-an-artifact-from-a-note-development-preview)
and [Notes grammar](https://docs.dreamlake.ai/notes/#artifact-references-development-preview).

## Fragment reference syntax

`:artifact[namespace/id#slide-3]` preserves a target inside the artifact;
`#/3` is valid only if the artifact defines that route. The named form
`:artifact[namespace/id]{fragment="slide-3"}` is also accepted. Preserve exact
source and percent encoding; do not supply the fragment twice or infer slide
numbering. Clicking sends the fragment to the panel through `dreamlake.route.hash`.
Another reference to the same artifact reuses its panel and updates its local
route without reloading the iframe or changing the Note/project URL. This requires
the companion UI deployment; a skill update does not deploy panel behavior.
