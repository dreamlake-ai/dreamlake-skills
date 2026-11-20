# Create or reopen a named tmux session

Read the [host command reference](../reference/cli-host-enrollment.md) and
[browser terminal contract](../reference/docs-lakeshore-hosts-browser-terminal.md)
first. Check their release prerequisites against the installed client and the
selected enrollment before submitting work.

```sh
dl tmux --help
dl tmux new --help
dl hosts enrollments HOST
dl tmux list --host HOST
```

1. Establish whether the user wants a new session or an existing session opened.
   Select the intended host and exact enrolled Unix account using the returned
   identity. Resolve an ambiguous target before creating anything.
2. For a new session, use the documented `tmux new` action with the user's name
   and host. Retain its request ID before waiting or retrying. Use the matching
   action grammar when the requested deliverable is a palette command or a
   Markdown directive; authoring a directive alone is not an instruction to run it.
3. Inspect the operation result. Keep its confirmed canonical directive and
   reference together. After an uncertain response, read or retry the original
   operation as documented; do not mint a new ID to bypass uncertainty or a
   conflict. A requested name that already exists requires a new user decision.
4. For an existing session, use the copied reference and the documented open
   operation. Preserve the exact enrollment, server and encoded name. If it is
   unavailable, inspect authorized inventory and report the result rather than
   substituting a different session or creating one.
5. Verify the intended interaction: newly created session, explicit attach, or
   literal saved directive, according to the user's request. Report creation and
   attachment separately. Do not save or index terminal output as a side effect.

For TypeScript or Python integrations, use the SDK signatures and return shapes
in the current reference. Validate the returned operation identity before using
its reference. If the installed SDK or enrollment lacks the operation, report
the specific capability gap; do not substitute raw shell execution.

For inserting a returned reference into a Memo, follow the edit and references
actions of `dreamlake-memos`. Saved agent conversations and session archives have
their own workflows; do not substitute one for a tmux reference.
