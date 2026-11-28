# Publish

```bash
dl artifact push <file> --id <artifact-id> --namespace <namespace>
# Built client output; check installed help and target hosting first.
dl artifact push ./dist/client --site --id <artifact-id> --namespace <namespace>
```

Read [command help and options](../reference/cli-artifacts.md#pushing).
Use the required `dreamlake-cli` skill for installation/authentication; check
`dl --version` and `dl artifact push --help` before writing. Preserve the
intended namespace, existing ID, metadata and access policy. Use a new ID only
for a separate artifact. Apply [author](author.md) before publishing new content.

## Static builds

Build/prerender the application and publish its client output, not the source
or server tree. Follow the [CLI site guide](../reference/cli-artifacts.md#static-sites-with-on-demand-files)
and [hosting prerequisites](../reference/docs-artifacts.md#static-build-directories).
If hosting is unavailable, report it; do not silently flatten the requested site.

Keep chunks and lazy imports intact. Keep startup small; defer large media,
fonts, datasets and inactive content. Check all asset paths against the output,
including paths built dynamically. Use [UIKit](uikit.md) for internal team UI.
For a slow build, follow [performance](performance.md) rather than adding a
new loader or retry mechanism without evidence.

For self-contained HTML directories, use the separate
[pages workflow](../reference/cli-artifacts.md#multiple-html-pages) and apply the
single-file authoring rules to each page. An available directory option is not
itself a reason to repackage an existing file.

## Verify the published content

Open the returned viewer link with the intended access and selected version.
Check the entry page, nested/deep link, reload, and an interaction that loads
optional code or media. For decks, visit every slide for missing assets and
exercise Present, Next and Back. Check browser errors, failed asset requests,
and document reloads during same-page navigation; use [routing](routing.md)
when state or initialization changes. Verify the affected media interaction,
not just slide navigation. Inspect both the actual embedded panel and standalone
viewer when the change affects them.

A build or upload receipt is not live verification. Fix discovered failures
within scope; report any unverified interaction explicitly. Keep these checks
in the publishing workflow, not as per-artifact runtime validation machinery.

## Thumbnail check on every update

```bash
dl artifact meta show <artifact-id> --namespace <namespace>
# Replace only when the existing cover is absent or no longer representative.
dl artifact meta set <artifact-id> --namespace <namespace> --cover ./cover.png
dl artifact meta show <artifact-id> --namespace <namespace>
```

Before updating, inspect the current cover and content. Retain an accurate custom
cover; otherwise generate and inspect a representative local image and supply
`--cover` on the push or metadata update. Prefer an explicit inspected cover for
new artifacts unless the user asks to omit it. Give new content a useful title
and description; preserve unrelated metadata on updates. Options and persistence:
[link previews](../reference/cli-artifacts.md#link-previews).

After publication, read metadata back and visually compare the gallery/list
thumbnail with the latest rendered content. Reject loading-state images. For
asynchronous scenes or automatic-generation fallback, follow
[shared preview generation](../reference/docs-artifacts.md#shared-preview-generation),
including readiness, access-triggered recovery and cooldown. Do not clear a valid
custom cover or repeatedly repush unchanged content to force generation. Separate
content failures, generation delays and third-party card caching. Report whether
the cover was retained, replaced or remains unverified.

## Conditional follow-ups

- Sharing or customer access to only the latest version: use [share](share.md)
  and read the saved policy back. Publication alone does not authorize public access.
- Older-viewer compatibility or upload retries: consult
  [incremental uploads](../reference/cli-artifacts.md#incremental-uploads).
- A client upload/registration conflict after a server upgrade or Project transfer:
  follow [ownership transfer](../reference/cli-artifacts.md#whole-project-ownership-transfer);
  obtain fresh credentials and re-upload before registration rather than retrying
  registration against a guessed storage key.
- Session affiliation: use the `session-links` action of `dreamlake-cli`.
  Retry a failed link without republishing successful content.

Return the viewer link and verified version, relevant interaction/thumbnail
results and remaining limitations. Do not include private traces or credentials.
