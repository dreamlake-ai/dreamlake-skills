# Share and control access

```bash
dreamlake artifact share get <id>        # inspect: URL, visibility, existing share link
dreamlake artifact share create <id>     # mint a share link (signed-in recipients can read)
dreamlake artifact share revoke <id>     # clear the token
dreamlake artifact visibility <id> public|private
```

Available in CLI 0.32.4 and later; check `dreamlake artifact share --help`
for installed support. These change metadata only — no upload, no new
version. Run the mutating steps only when the user asked to grant or revoke
access, and run `get` before and after a change to verify it. Flags,
`--json` fields and the exact recipe:
[Manage existing share links](reference/cli-artifacts.md#manage-existing-share-links).

## Visibility and sharing are independent

Artifacts are **private by default** — only members of the owning namespace
can see them.

- **Public** (`--visibility public` at push, `artifact visibility … public`,
  or the dashboard toggle): anyone can view, no login, plain URL.
- **Share link** (`--share` at push, `share create`, or the dashboard Share
  button on a private artifact): a URL of the form
  `https://dreamlake.ai/<namespace>/artifacts/<id>?share=<token>`. Opening
  it requires the recipient to sign in; invalid or revoked tokens grant
  nothing.
- Setting an artifact back to `private` does **not** clear an existing share
  token; revoking a link does not make a public artifact private. Omitting
  `--share` on a later push preserves the existing token — it does not revoke
  it. Use `share revoke` or the dashboard stop-sharing action to kill live
  links.
- Revocation blocks link-derived access while sharing is disabled; recorded
  recipients may regain access if sharing is enabled again. There are no
  per-user revocation endpoints or link roles.
- `shareStatus: unavailable` in `--json` means the server did not expose the
  token to this caller, not that sharing is off.

## Link cards leak before content does

Every artifact page unfurls as an Open Graph card (title, description, cover
— set in [publish](publish.md)). What the card shows follows visibility:

- **Public** — the real title, description and cover (the user's own, or the
  screenshot DreamLake generates).
- **Share link** — the same real card. **Anyone holding the `?share=` URL sees
  it, a chat tool's preview bot included**; only the content still needs a
  signed-in viewer. Warn the user before pasting a share link where the card
  itself would be the leak.
- **Private, no token** — a generic DreamLake card, indistinguishable from a
  dead link; nothing about the artifact leaks.

Platforms cache cards for days: a changed cover or a revoked link can keep
showing in messages already posted. A user's own permissions never reach a
platform's preview bot — rich previews of plain private links are not
available. Source:
[Make the link card yours](reference/docs-artifacts.md#make-the-link-card-yours).

## Project-derived access

The Project-sharing backend and Web update are released. CLI Project
attachment commands require 0.62.0 or later; Python Project support requires
SDK 0.29.0 or later. Check installed client versions separately from server
support.

- Explicit Project READ grants read current and later attached artifacts;
  WRITE/ADMIN permit supported content updates. A public Project alone does
  not open a private artifact. Independent membership and sharing remain
  valid; detachment or revocation removes only inherited access.
- Project grants never authorize artifact sharing management, deletion or
  ownership transfer. Use the reader's own credentials at the canonical
  address, not a copied share link.
- Project-only uploads require resource-scoped temporary credentials;
  `DELEGATED_UPLOAD_UNSUPPORTED` (403) means the broker cannot safely supply
  them — never request the server's static credentials instead.
- A new Project attachment requires independent sharing-management authority
  on the artifact **and** actual Project WRITE/ADMIN; ordinary
  organization-member READ or public Project visibility is insufficient.
  Grouping an already-live attachment into a Bindr of that same Project needs
  Project write authority and resource readability, without sharing it again.
  Use the server's current `canBind` result, not a role guessed from
  membership
  ([Project choice and grouping](https://docs.dreamlake.ai/api/project-queries/)).
- Contract: [Project attachment access](reference/docs-artifacts.md#project-attachment-access),
  [CLI project attachment commands](reference/cli-projects.md#project-attachment-access-cli-0620)
  and the
  [owning access notes](https://docs.dreamlake.ai/dev/notes/project-resource-sharing/).

An owned artifact moves with its whole Project; see the `projects` action of
`dreamlake-cli`.
