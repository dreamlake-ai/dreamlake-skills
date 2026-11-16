# Publish or roll back an agent definition

For CLI requests, inspect the installed release commands before using them:

```bash
dl runnable definition --help
dl runnable definition publish --help
dl runnable definition activate --help
```

1. Resolve the existing agent and intended namespace. Read its saved draft and
   active release; do not create a duplicate to obtain a new version.
2. Review the prompt, README template, configuration and referenced sources.
   Finish pending memo edits and save the draft before publication. Use the
   release contract in [agent authoring](../reference/docs-agents-authoring.md)
   and [the runnable API](../reference/cli-runnable-api.md).
3. For publication, submit the reviewed draft's concurrency precondition and
   requested label through the available CLI, SDK or discovered resource API.
   For rollback, inspect the intended historical release before activating it.
   Do not turn a failed precondition into an automatic reload-and-retry.
4. Read back the active version and inspect that version's README and prompt
   together. Report the full version and whether the change was published or
   activated; saving a draft alone is not publication.
5. If a write response is uncertain, inspect the head and history before taking
   another action. Keep the draft and existing history. If source access was
   revoked, report the failure rather than substituting live draft content.

For SDK-only requests use the documented methods in the runnable API reference.
If the installed client or deployed server lacks the operation, report that
boundary and retain the reviewed draft; do not invent commands or claim a release.
