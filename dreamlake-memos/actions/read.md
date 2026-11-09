# Read a memo

First complete [task identity setup](identity.md); reuse it in every shell call.

Set `MEMO_ID` to an ID or slug from `dl memos list`. Add
`--namespace <slug>` when the memo belongs to an organization. Check the
installed CLI before choosing a read contract:

```bash
MEMO_ID=release-plan
dl memos read --help
```

When help lists `--view markdown`, `--toc`, `--section`, `--tag` and `--at`,
use addressable Markdown reads. Start with the outline, then pin any section or
element reads to the revision printed in the first result:

```bash
dl memos read "$MEMO_ID" --view markdown --toc
REVISION='revision from the outline result'
dl memos read "$MEMO_ID" --view markdown --at "$REVISION" --section s1.1
# Or target one passage or list item instead of reading the whole section:
dl memos read "$MEMO_ID" --view markdown --at "$REVISION" --tag s1.1.p1
dl memos read "$MEMO_ID" --view markdown --at "$REVISION" --tag s1.ul2.li3
```

Use the smallest read that answers the question. The Markdown view adds
address, character and line hints as comments before headings, paragraphs,
lists and list items. Read the actual IDs from the snapshot: paragraphs `p`,
unordered lists `ul`, ordered lists `ol` and all items `li` share one counter
per section: `s1.p1 → s1.ul2 → s1.ul2.li3 → s1.ul2.li4 → s1.p5`.
Nested lists extend the parent path, e.g. `s1.ul2.li4.ol5.li6`. A list/item
target includes its subtree. Checkbox state is an item attribute
(`data-checked="true|false"`), not a different ID type. Hints are not saved memo text.
Keep the revision with the passage. Do not combine `--at` with `--since` or
`--if-match`, or combine multiple scope selectors. If the installed CLI lacks
these options, use the compatible legacy reads below and do not infer HTML
addresses:

```bash
dl memos toc --note "$MEMO_ID"
dl memos read --legacy "$MEMO_ID" --section setup
dl memos read --legacy "$MEMO_ID" --start-line 40 --end-line 80
```

For a whole-source delta, retain the complete snapshot’s `hash` and pass it to
`--since`; `hash` and opaque write `revision` are different tokens. Use
`--json` only when a program needs parsed fields. See [reading and changes](../reference/cli-notes-reading.md)
and [the full Memos guide](../reference/docs-notes.md).

For saved checkpoints or a missing earlier draft, use [versions and recovery](versions.md).
Recovery requires a complete source read; scoped or annotated reads cannot supply its hash.

Summary metadata is read and updated with [`memos summary`](summary.md),
independently of body patches. `memos read --json` includes a nullable summary
alongside the body snapshot; plain reads print the summary separately when one
is set.

For comment targeting in HTML reads, use the emitted `sN.cK` ID with `--tag` and
the same revision. Saved comments also expose persistent `data-comment-id`;
HTML target IDs are revision-local. See [comment targets](../reference/docs-notes-html-reads.md#comment-targets-in-html-reads).

## Literal agent markup

For Markdown memos on the literal-markdown contract, HTML-like wrappers provide
IDs and ranges; their contents are **verbatim Markdown**, including list markers,
checkboxes and comment directives. Use one `data-char` range for that source;
do not invent inner/outer ranges. Keep `<`, `&`, backslashes and Unicode literal.
Do not add escapes and do not remove escapes already in the saved Markdown.
This is for agents, not browsers: do not render it or DOM-parse its body.
Use `--view markdown` for ordinary reads; machine integrations decode canonical
source metadata once and use its address index. Preserve the original revision.

## Project-derived access

With the released Project-sharing backend, explicit Project user/team grants
cover all live attached Memos, including later additions. Public Project
visibility alone never reveals private Memos. Independent Memo links and
namespace membership remain valid. Detachment or Project grant revocation removes
only that source of access. Do not mint a Memo share link to simulate Project
access; use the reader's own credentials and inspect current Memo permissions.
Grant semantics for every resource type are the `project-access` action of
`dreamlake-cli`.

## Explicit Python SDK request

For a request specifically asking for Python SDK code, use the released Memo
examples in [the product guide](../reference/docs-notes-cli-editing.md#python-sdk-read).
Resolve the existing Memo and set the same task identity first. Use the
`dreamlake-cli` skill for login and environment setup. Keep source and its
original revision together if the read will be used for an edit. Do not invent
SDK counterparts for commands that the references do not document.
