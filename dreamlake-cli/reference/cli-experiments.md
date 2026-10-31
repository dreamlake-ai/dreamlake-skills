<!-- generated from https://cli.dreamlake.ai/experiments.md at 0.97.1 086d6d7; do not edit -->

# Experiments workspace binding

**Unreleased.** Requires the matching DreamLake and Dash server changes. These
commands have not been released or verified on a hosted deployment.

Use your existing DreamLake login and explicitly choose the DreamLake organization
namespace. An organization owner can discover eligible existing workspaces on the
managed Dash instance. No Dash URL or token is accepted or copied by this flow.
An identical organization name does not establish a binding.

```bash cli-help="experiments workspaces"
dreamlake experiments workspaces --namespace fortyfive --json
```

Inspect the current binding, including its revision. Results contain stable
DreamLake and Dash namespace identifiers; a slug is only a discovery aid.

```bash cli-help="experiments binding"
dreamlake experiments binding --namespace fortyfive --json
```

Select a unique slug or `namespaceId` returned by discovery. `connect` first
previews the selected target without changing anything. Review its `instanceId`,
`namespaceId`, current binding, and `expectedRevision`.

```bash cli-help="experiments connect"
dreamlake experiments connect research --namespace fortyfive --json
# Apply only after reviewing the preview. Use its actual revision, not this example's 0.
dreamlake experiments connect "$DASH_NAMESPACE_ID" --namespace fortyfive --instance-id "$DASH_INSTANCE_ID" --apply --expected-revision 0 --json
```

Apply requires the discovered stable `namespaceId` (`DASH_NAMESPACE_ID` above),
copied from the reviewed preview's `target.namespaceId`; slugs are preview-only.
Set `DASH_INSTANCE_ID` to its `target.instanceId`. Apply requires this explicit
instance ID so configuration changes cannot silently redirect the selection.
The server verifies the current user's Dash organization ownership
and the instance again at apply time. A stale revision fails rather than
overwriting another owner's change. Refresh and review after a conflict; do not
automatically retry with a newer revision.

To detach, review a separate preview and apply its revision. Detaching disables
the DreamLake binding without deleting remote experiments, changing Dash members,
or revoking SDK credentials. It remains available when remote discovery is down.
Detached rows keep their revision; only a namespace with no previous binding uses 0.

```bash cli-help="experiments disconnect"
dreamlake experiments disconnect --namespace fortyfive --json
# Replace 1 with the revision returned by this preview.
dreamlake experiments disconnect --namespace fortyfive --apply --expected-revision 1 --json
```

Success always emits a JSON receipt. With `--json`, errors emit
`{ok:false,error:{code,message,remediation}}` and exit nonzero. A rejected write
is not confirmation of its outcome: inspect `binding` before retrying after a
network interruption.

This phase connects existing workspaces and preserves both systems' permissions.
Researchers continue logging through the existing Python ml-dash SDK; this CLI
does not create experiments, unify SDK authentication, or migrate storage.
Authorized members read metrics on the DreamLake organization Experiments page;
binding administration alone does not grant Dash data access. Managed onboarding
and Source-backed storage remain later phases.
