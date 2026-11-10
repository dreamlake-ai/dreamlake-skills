<!-- generated from https://cli.dreamlake.ai/notes/sharing.md at 0.117.0 6ff1564; do not edit -->

# Sharing and visibility

Available in CLI 0.32.4 and later; check `dl memos share --help` for installed support.

Requires an authenticated login, an existing resource, and permission to
manage its sharing. Run these mutation steps only when the user has asked
to grant or revoke access. These commands change
metadata only; they do not upload content or create a new version.

```bash cli-help="memos share"
# Find the release plan and inspect its source and current sharing.
dl memos search "release plan"
MEMO="release-plan" # Replace with the id or slug from search.
dl memos read "$MEMO"
dl memos share get "$MEMO"

# Give signed-in recipients read access, then verify the returned link.
dl memos share create "$MEMO" --role read
dl memos share get "$MEMO"

# When link access is no longer needed, revoke it and verify.
dl memos share revoke "$MEMO"
dl memos share get "$MEMO"
```

`get` never enables sharing. It reports the resource URL, visibility, and
existing share URL. For Private memos, a resource URL alone does not grant access. `--json` provides
structured link metadata; `shareStatus: unavailable` means the server did not
expose the token to this caller, not that sharing is disabled.

```bash cli-help="memos visibility"
MEMO="release-plan" # Your existing memo id or slug.
dl memos visibility "$MEMO" unlisted
dl memos visibility "$MEMO" public
dl memos visibility "$MEMO" private
```

`unlisted` permits anonymous reading through the direct URL but hides the Memo
from public profiles, catalogs and discovery. Owners and existing collaborators
can still find it. `public` is discoverable; `private` requires existing access.
Create an Unlisted memo with `dl memos create "Review" --visibility unlisted`.
The legacy `--public` flag still creates publicly listed memos and cannot be
combined with a conflicting `--visibility`.

The TypeScript API supports
`api.memos(namespace).create({name: "Review", visibility: "unlisted"})` and
`api.memos(namespace).share(memoId).visibility("unlisted")`;
the legacy `api.notes` alias has the same support.

Visibility and sharing are independent. Making a resource private does not
revoke links or accepted access. Revoking a link does not make a public resource
private. Use `--namespace <slug>` for another namespace.

Only the namespace owner or an eligible Memo creator may manage sharing.
`create --role write` enables editing; the default is `read`. Updating the role
reuses the token and changes the role evaluated on subsequent requests for
everyone admitted through the link. Memo IDs resolve their owning namespace automatically.

```bash cli-help="memos share revoke"
MEMO="release-plan" # Your existing memo id or slug.
dl memos share revoke "$MEMO" --revoke-accepted
```

Ordinary revocation clears the link and blocks subsequent link-derived access,
including for prior recipients. Their acceptance records remain: enabling
sharing again restores access under the current link role. `--revoke-accepted`
also deletes those records, so recipients must accept a valid link again. A collaborator who already has the room address may keep
editing until the room is rotated; this command does not rotate rooms.

```bash cli-help="memos share access"
MEMO="release-plan" # Your existing memo id or slug.
# List acceptance records and stored roles as a readable table.
dl memos share access "$MEMO"
```

```bash cli-help="memos share remove"
MEMO="release-plan" # Your existing memo id or slug.
USER_ID="user-id-from-access-list"
dl memos share remove "$MEMO" "$USER_ID"
```

The access list defaults to a readable table; use `--json` for a structured
integration. It returns stored roles, which may lag behind the live link role.
Use `share get` to inspect the current link role.

Removing an acceptance record does not invalidate a circulating link; that link can admit
the user again. Membership and public access are unaffected.

## Public article URLs

Public and unlisted memos have a separate public URL slug. This is independent of
the internal memo slug and display name. Get or allocate it from the saved H1:

```bash cli-help="memos permalink"
dl memos permalink <memo-id> --namespace <namespace> --json
dl memos permalink <memo-id> --namespace <namespace> --slug my-article --json
```

The response contains `noteId`, `namespaceSlug`, `slug`, `href`, and `aliases`
(previous slugs). `href` is relative to the web app. An explicit slug edits the
URL and preserves every old slug as an alias. Renaming the title doesn't change
it. Slugs are unique within a namespace, including historical aliases. Automatic
allocation suffixes collisions; an explicitly requested reserved slug returns
409, so choose another. Duplicates and copies allocate fresh URLs and do not
inherit alias history. Making the memo private revokes anonymous access through
both current and historical URLs.

```typescript
const memo = dl.memos("<namespace>/<memo-id>");
const current = await memo.permalink();
const changed = await memo.permalink({ slug: "my-article" });
console.log(changed.href, changed.aliases);
// Namespace API: dl.memos.namespace("<namespace>").permalink(id, { slug: "my-article" })
```

Management uses `POST /namespaces/:namespace/notes/:id/permalink` with `{}` or
`{"slug":"my-article"}`. It requires metadata management permission and public
or unlisted visibility. Public lookup uses
`GET /namespaces/:namespace/notes/by-slug/:slug`; old aliases resolve directly to
the current URL without exposing the private management history.
