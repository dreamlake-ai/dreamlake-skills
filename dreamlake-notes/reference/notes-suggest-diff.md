# Suggested-edit redlines

A unified diff answers *which lines changed*. A reviewer usually wants to read
the new text with the changes marked in place, and to keep or drop each one.
Notes already does this with
[suggested edits](https://docs.dreamlake.ai/notes/markdown/): `:insert[…]`
shows new text underlined, `:delete[…]` shows removed text struck through, and
`:replace[…]{with="…"}` shows both. A note writer can accept or reject each one.

`notes suggest-diff` writes those tags for you. Given an earlier and a later
version of a Markdown document, it prints a note body in which every change is a
suggested edit:

```bash
dreamlake notes suggest-diff before.md after.md
```

```markdown
We ship on :replace[Friday after]{with="Thursday once"} the smoke tests :insert[and the canary ]pass.
```

The command only reads the two files and prints Markdown. It sends nothing, so
you choose where the output goes: a new review note, back into the note you are
editing, or a file. **Availability:** CLI 0.47.0 and later; check that
`dreamlake notes suggest-diff --help` exists.

```bash cli-help="notes suggest-diff"
# Review a change as a new private note.
dreamlake notes suggest-diff before.md after.md --user "Docs review" \
  | dreamlake notes create "Redline: release plan" --file -
# Propose edits inside the note itself; refuses changes it cannot express.
dreamlake notes suggest-diff current.md edited.md --in-place --user "$DREAMLAKE_AGENT_NAME" > proposal.md
# Count insertions, deletions, replacements and changed code blocks.
dreamlake notes suggest-diff before.md after.md --json | jq .stats
```

There are two kinds of output, and the scenarios below use one or the other.
A **review redline** goes into a separate note. It is optimized for reading:
unchanged code blocks collapse to one line, a changed code block becomes a
`diff` fence, and in `.mdx` input, component tags such as `<Callout>` are shown
as inline code. `<Lead>` and `</Lead>` marker lines are the exception: Notes
renders a Lead block itself, so those lines stay as written. **In-place output** (`--in-place`) replaces the earlier text
inside the same note. It leaves every unchanged block exactly as written. When
all its suggestions are accepted, the note holds the later version; when all are
rejected, it holds the earlier one.

## Review a document change from Git

Use this for a docs page, a README, release notes, an `AGENTS.md`, or any
Markdown in a pull request. Write both revisions to files and create a review
note:

```bash
git show main:docs/pages/quickstart/+Page.mdx > before.mdx
git show HEAD:docs/pages/quickstart/+Page.mdx > after.mdx
dreamlake notes suggest-diff before.mdx after.mdx --user "Docs review" \
  | dreamlake notes create "Redline: quickstart" --file -
```

A pull request that touches several pages fits in one note, with one section
per file. A file that was added or deleted has an empty side and comes out as
all insertions or all deletions:

```bash
BASE=main
{
  printf '# Docs redline\n\n'
  git diff --name-only "$BASE" HEAD -- '*.md' '*.mdx' | while read -r f; do
    printf '## %s\n\n' "$f"
    git show "$BASE:$f" > before 2>/dev/null || : > before
    git show "HEAD:$f" > after 2>/dev/null || : > after
    dreamlake notes suggest-diff before after --mdx | sed 's/^#/###/'
    printf '\n'
  done
} | dreamlake notes create "Redline: $(git rev-parse --abbrev-ref HEAD)" --file -
```

The `sed` demotes each page's own headings below the per-file heading. Pass
`--mdx` when the temporary files lose the `.mdx` extension. Generated output
such as committed skill bundles is usually better left out of the file list.

Accepting or rejecting a suggestion in this note changes only the note. It does
not change the pull request, so treat decisions as review feedback.

## Propose edits inside an existing note

Use this when you, or an agent working for you, have a revision of someone's
note and the owner should decide on each change. Writing the revision directly
would replace their text; writing it as suggestions leaves their text in place
with each proposed change marked on it.

Read the exact source and its write baseline, edit a copy, render the proposal,
and write it back on the condition that nobody changed the note in the meantime:

```bash
NOTE_ID=release-plan
dreamlake notes read "$NOTE_ID" --legacy --json > base.json
jq -jr .text base.json > current.md
cp current.md edited.md            # make the intended edits in edited.md
dreamlake notes suggest-diff current.md edited.md --in-place \
  --user "$DREAMLAKE_AGENT_NAME" > proposal.md
dreamlake notes write "$NOTE_ID" --file proposal.md --if-match "$(jq -r .etag base.json)"
```

The owner then sees, for example:

```markdown
We ship on :replace[Friday after]{with="Thursday once" user="Claude"} the smoke tests :insert[and the canary ]{user="Claude"}pass.

:insert[- Rollback: revert the release tag.]{user="Claude"}
```

`--in-place` refuses, with exit status 2 and nothing printed, in the two cases
where the result could not be resolved back to either version:

- **A code block or frontmatter changed.** Suggested edits do not work inside
  code. Write the code change directly, or leave a comment for the owner.
- **The current text already has pending suggestions.** Comparing against
  them would nest one proposal in another. Ask the owner to accept or reject
  them first.

Existing `:comment[…]` tags are kept intact and never split by a nearby edit.
Set the [agent identity](notes-collaboration.md) before the read and the write
so the owner can see who proposed the changes. If `--if-match` fails, read the
note again and redo the edit against the new text.

## Compare two saved versions of a note

[Saved versions](https://cli.dreamlake.ai/notes/versions/) are immutable checkpoints. To see what
changed between two of them as a readable redline, read each version's text
and create a review note. A saved-version read returns its body as `.text`:

```bash
dreamlake notes hist "$NOTE_ID" --json | jq -r '.versions[] | "\(.id)  \(.tag)"'
dreamlake notes read "$NOTE_ID" --version "$OLDER" --json | jq -jr .text > older.md
dreamlake notes read "$NOTE_ID" --version "$NEWER" --json | jq -jr .text > newer.md
dreamlake notes suggest-diff older.md newer.md \
  | dreamlake notes create "Changes: release plan v1 → v2" --file -
```

Comparing a saved version with the live note works the same way, with
`dreamlake notes read "$NOTE_ID" --json | jq -jr .content` as the newer side.

## Review what changed since you last read

An agent or a teammate edited a note, and you want to read what they changed
rather than the whole note. Keep the `revision` from your earlier read, read
the note as it was then with `--at`, and compare it with the live note:

```bash
dreamlake notes read "$NOTE_ID" --json > earlier.json      # earlier, at your last read
dreamlake notes read "$NOTE_ID" --at "$(jq -r .revision earlier.json)" --json | jq -jr .content > then.md
dreamlake notes read "$NOTE_ID" --json | jq -jr .content > now.md
dreamlake notes suggest-diff then.md now.md \
  | dreamlake notes create "Changes since my last read: release plan" --file -
```

`--at` reads only retained snapshots, so keep the revision rather than relying
on a time long ago. `notes diff` (`read --since`) answers the same question as
a unified diff, which suits scripts and patches. `suggest-diff` is for a person
reading the change.

## Compare a note with a file

When a note and a repository file are meant to say the same thing, such as a
design note and the docs page written from it, compare them in either
direction. Either side can be `-` for standard input:

```bash
dreamlake notes read design-notes --json | jq -jr .content \
  | dreamlake notes suggest-diff - docs/pages/design/+Page.mdx --mdx \
  | dreamlake notes create "Redline: design note → docs page" --file -
```

To bring the note in line with the file instead, use the note as the earlier
side and write the output into the note with `--in-place`, as in
[proposing edits](#propose-edits-inside-an-existing-note).

## How changes are shown

Prose is compared word by word. Short unchanged words between two edits are
folded into one replacement, so a rewritten clause reads as one change. A
paragraph that was mostly rewritten becomes a deletion of the old paragraph
followed by an insertion of the new one. A tag never spans a line break: each
line of a multi-line change gets its own tag, and list, quote and heading
markers go inside it. Accepting a deleted list item therefore leaves no empty
bullet behind. A change that begins right after `/` or `\` starts one
character earlier, because Notes does not recognize a tag directly after
those characters.

Notes shows a suggestion's text as plain text. Markdown inside a changed span,
such as `` `code` `` or `*emphasis*`, appears with its punctuation until the
suggestion is accepted. Accepting every suggestion gives the later version, and
rejecting every suggestion gives the earlier one. The only difference may be
blank lines, which do not change the rendered note. In a review redline this
holds for prose only, because code is shown as `diff` fences.

| Option | Effect |
|---|---|
| `--user <name>` | Attribution on every tag, up to 128 characters |
| `--in-place` | Output to replace the earlier text in the same note; exit 2 on a code change or pending suggestions |
| `--full-code` | Keep unchanged code blocks in a review redline |
| `--mdx` / `--no-mdx` | Show component tags as inline code, except `<Lead>` / `</Lead>` marker lines, which Notes renders; on by default when an input path ends in `.mdx`, never applied with `--in-place` |
| `--json` | Print `{ markdown, stats }`, where `stats` counts `inserts`, `deletes`, `replaces` and `codeBlocks` |

Exit status is 0 on success, 1 when an input cannot be read, and 2 when
`--in-place` refuses.
