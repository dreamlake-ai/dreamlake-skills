# Diagnose and improve loading

```bash
# Build/prerender first, then preserve the static build's file boundaries.
dl artifact push ./dist/client --site --id <existing-artifact-id>
```

Use [publish](publish.md#static-builds) for prerequisites and publication.
Product behavior and packaging guidance:
[Fast first render](../reference/cli-artifacts.md#fast-first-render).
Do not convert a small standalone report merely to use a different format.

## Establish the baseline

Open the requested artifact and route with the intended access. Confirm the
selected version and that the saved layout actually mounts the artifact. If a
fresh session cannot reproduce that layout, state the route used instead.
Capture a cold load before editing. Record useful first content, readiness of
the requested interaction/media, completion, transferred bytes, overlapping
requests and failures. Inspect what is inside the entry HTML and startup code.
One active request can be a dependency chain; verify the waterfall before
calling downloads serial or changing concurrency.

For a multi-artifact comparison, cover the relevant formats and sizes. Pin or
record versions, use fresh browser contexts and consistent network/CPU
conditions, alternate trial order where practical, and report repeated-trial
medians. Label single observations, controlled toggles and historical results
separately. Do not invent a historical baseline or compare different readiness
milestones as an exact speedup.

## Fix the observed bottleneck

Prefer the original source build when migrating a media-heavy artifact to site
hosting. Preserve lazy imports and file URLs. Check for app code that waits for
all assets before rendering, large inline data before the mount, and inactive
slides or simulations mounted eagerly. Move optional work behind the relevant
route or interaction. Preserve dynamically assembled asset paths and confirm
files against the source; do not replace missing content with placeholders.

If only a published standalone file is available, keep a verified original and
make a reversible, scoped conversion. Check that consumers accept file URLs
before replacing data URLs: some code reads embedded bytes synchronously.
Do not apply a blind text rewrite to arbitrary scripts or documents.

Retain the same artifact ID and existing access settings. Publishing a faster
version does not authorize making it public or issuing a share link. If the
requested hosting mode is unavailable, report that prerequisite rather than
silently repackaging the site into one large HTML file.

## Verify and report

Repeat the baseline milestones on the published version. Check the target
interaction, navigation, reload, optional resources and representative media;
inspect browser errors and failed resource requests. For decks, check all slides
for missing paths and exercise the media on the requested slide. Distinguish
navigation coverage from simulation or media fidelity acceptance.

Record the artifact links/versions, conditions, trial counts, timings and
remaining bottlenecks in the user's requested destination. Keep credentials,
capability URLs and raw private traces out of public documentation. Use general
publishing guidance in the skill/docs; keep artifact-specific measurements in
the authorized report. Report source changes, publication and live verification
separately so a build or merged PR is not mistaken for a measured deployment.
