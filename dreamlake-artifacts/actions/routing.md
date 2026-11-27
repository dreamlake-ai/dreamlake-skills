# Route-aware artifacts

For slides, tabs, filters or selected items, read the
[routing contract](../reference/docs-artifacts.md#artifact-paths-and-local-routing)
and start from the [route template](../assets/templates/route-aware.html) for a
single-file HTML artifact. Built sites should keep their existing client router
and follow the [site contract](../reference/cli-artifacts.md#static-sites-with-on-demand-files).

1. Read the incoming state before choosing defaults. Use the supported route
   API/history integration for in-page state; do not navigate or reload the
   document to change a slide. Do not rewrite the URL on every render or echo
   incoming route notifications back as new navigation.
2. Parse and validate state, encode it with URL utilities, and clean up
   subscriptions. Treat route values as public user input, never credentials or
   authority. Keep viewer credentials and share tokens out of artifact code.
3. Test in the actual DreamLake viewer: open a deep link, switch slides/tabs,
   go back/forward where supported, and reload. For a project panel, check its
   local navigation separately from standalone browser-history behavior.
   Confirm same-page navigation preserves form/component state and does not
   repeatedly request or replace the document. Include a slow-start check when
   changing initialization; do not add artifact-specific bridge handshakes.
4. Share the viewer URL, not the isolated frame address. For Memo links use
   [notes-references](notes-references.md); never put share tokens in rich-reference
   attributes. If navigation fails, verify deployed viewer support before
   claiming the route works.

URL shapes, reserved keys, limits, API semantics and deployment compatibility
belong to the linked contract; do not maintain a second copy here.
