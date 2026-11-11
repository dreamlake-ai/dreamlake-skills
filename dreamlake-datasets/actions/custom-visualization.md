# Publish a custom Source visualization

```bash
dl source visualization push --help
dl source browse --source SOURCE --namespace NAMESPACE
dl source visualization push ./dist --source SOURCE --namespace NAMESPACE
```

Use this action when the user wants their own application in a Source's Visualize
view. Inspect the Source and a small representative data sample before choosing
what to render. Read the [custom visualization guide](../reference/docs-sources-custom-visualization.md)
for the runtime API, supported build shape, limits and authority, and
[CLI publishing](../reference/cli-sources.md#custom-visualization) for command details.
If the installed CLI or selected server lacks the feature, report that version
gap; do not create a standalone Artifact as a substitute.

1. Resolve the intended Source and confirm current read/edit access. Inspect its
   existing configuration. Preserve it; if the publisher reports an external-only
   configuration, read it and explicitly materialize that content through a
   create-only managed write before proceeding. Stop on unreadable configuration
   or a revision conflict and reconcile with the actual current content.
2. Build a static application for the user's data and interactions. Use the
   documented current-Source bridge, including bounded reads and paging. Show
   loading, empty and failed-read states. Do not embed account credentials,
   signed object URLs, or a second private Source identity in the bundle.
3. Publish the complete build with the command above. For an explicit SDK-only
   request, use the Python or TypeScript publisher in the guide instead of
   substituting shell commands. Let the publisher manage its code generation
   and conditional configuration update; do not hand-patch a failed publication.
4. Read back the configuration and open the returned Source URL. Verify a real
   data-driven interaction and any lazy-loaded assets, not merely the iframe's
   presence. Report the Source URL, the tested CLI/SDK version, and what worked.
   If browser verification is unavailable, distinguish successful publication
   from unverified rendering.

This action does not supply an application backend or online IDE. For existing
standalone Artifact code, copy a static build as a starting point and adapt its
data access to the Source bridge. Do not alter Artifact permissions or retain a
live cross-resource dependency. Do not change Source sharing merely to make a
failing visualization load; inspect the current authority and error instead.
