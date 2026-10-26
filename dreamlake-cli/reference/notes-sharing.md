# Sharing and visibility

Available in CLI 0.32.4 and later; check `dreamlake notes share --help` for installed support.

Requires an authenticated login, an existing resource, and permission to
manage its sharing. Run these mutation steps only when the user has asked
to grant or revoke access. These commands change
metadata only; they do not upload content or create a new version.

```bash cli-help="notes share"
# Find the release plan and inspect its source and current sharing.
dreamlake notes search "release plan"
NOTE="release-plan" # Replace with the id or slug from search.
dreamlake notes read "$NOTE"
dreamlake notes share get "$NOTE"

# Give signed-in recipients read access, then verify the returned link.
dreamlake notes share create "$NOTE" --role read
dreamlake notes share get "$NOTE"

# When link access is no longer needed, revoke it and verify.
dreamlake notes share revoke "$NOTE"
dreamlake notes share get "$NOTE"
```

`get` never enables sharing. It reports the resource URL, visibility, and
existing share URL. A resource URL alone does not grant access. `--json` provides
structured link metadata; `shareStatus: unavailable` means the server did not
expose the token to this caller, not that sharing is disabled.

```bash cli-help="notes visibility"
NOTE="release-plan" # Your existing note id or slug.
dreamlake notes visibility "$NOTE" public
dreamlake notes visibility "$NOTE" private
```

Visibility and sharing are independent. Making a resource private does not
revoke links or accepted access. Revoking a link does not make a public resource
private. Use `--namespace <slug>` for another namespace.

Only the namespace owner or an eligible Note creator may manage sharing.
`create --role write` enables editing; the default is `read`. Updating the role
reuses the token and changes the role evaluated on subsequent requests for
everyone admitted through the link. Note IDs resolve their owning namespace automatically.

```bash cli-help="notes share revoke"
NOTE="release-plan" # Your existing note id or slug.
dreamlake notes share revoke "$NOTE" --revoke-accepted
```

Ordinary revocation clears the link and blocks subsequent link-derived access,
including for prior recipients. Their acceptance records remain: enabling
sharing again restores access under the current link role. `--revoke-accepted`
also deletes those records, so recipients must accept a valid link again. A collaborator who already has the room address may keep
editing until the room is rotated; this command does not rotate rooms.

```bash cli-help="notes share access"
NOTE="release-plan" # Your existing note id or slug.
# List acceptance records and stored roles as a readable table.
dreamlake notes share access "$NOTE"
```

```bash cli-help="notes share remove"
NOTE="release-plan" # Your existing note id or slug.
USER_ID="user-id-from-access-list"
dreamlake notes share remove "$NOTE" "$USER_ID"
```

The access list defaults to a readable table; use `--json` for a structured
integration. It returns stored roles, which may lag behind the live link role.
Use `share get` to inspect the current link role.

Removing an acceptance record does not invalidate a circulating link; that link can admit
the user again. Membership and public access are unaffected.
