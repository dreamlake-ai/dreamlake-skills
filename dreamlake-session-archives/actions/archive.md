# Approve and verify archival

Start with the selected Source's current metadata, policy, device configuration
and upload capabilities. Read [session archive Sources](../reference/docs-sources.md#session-archive-sources)
before issuing a write; inspect the current documented interface rather than
inventing an upload CLI command.

1. Match the namespace, owner, enrollment and native session. Resolve whether the
   user's authorization covers one observed snapshot, historical import, or a
   separately supported future-upload capability. Discovery and opening a row
   alone are not content consent. Existing explicit authorization need not be
   requested again, but it must match the concrete destination and scope.
2. For one session, inspect its current observation and offered representation,
   then approve that exact snapshot through the supported upload fence. For
   history, follow [explicit historical import](../reference/docs-sources.md#explicit-historical-import):
   inspect the ready preview, counts, encoded bytes, exclusions and revisions
   before approving its exact manifest. Inspect [Claude components](../reference/docs-sources.md#claude-subagent-components)
   when child logs are requested; never infer their consent from a parent.
   Build each request from that operation's documented contract; do not copy a
   preview's fields into its approval request or invent missing body fields.
3. Use the supported bounded uploader and durable progress/status path. Keep
   source policy, account-wide concurrency and resource controls in force. Do
   not create a per-file worker swarm or repeatedly probe AWS credentials.
   Diagnose explicit denial or configuration mismatch rather than deleting its
   recovery state or repeatedly retrying the same upload.
4. Verify committed archive progress and exact Source ownership. Report the
   frozen eligible denominator, complete and blocked entries, excluded files,
   root sessions and child components separately. Distinguish retained native
   bytes from readable message coverage and an incomplete inventory from a
   complete census. Check [provider and representation boundaries](../reference/docs-sources.md#native-archive-completeness-and-provider-boundaries)
   before promising a readable conversation: test its paginated projection
   separately from retained bytes. Follow [conversation provenance](../reference/docs-lakeshore-hosts-native-session-lineage.md#saved-conversation-provenance)
   when interpreting inherited history or inter-agent input; do not describe
   opaque content as recovered plaintext. A successful PUT alone is not upload completion.
5. Recover an uncertain result by reading status and using the documented
   recovery operation. If a snapshot changed, inspect the new observation and
   applicable consent instead of silently expanding the old approval. After
   stop or revocation, read back the resulting state; do not restore old consent
   when re-enabling configuration.

Offer automatic upload only when the deployed capability actually supports the
requested scope. Keep that choice separate from remote control. Administrative
read access does not supply another owner's local upload consent; unsupported
enterprise overrides must not be emulated through a legacy upload route.
