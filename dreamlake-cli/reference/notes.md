# Notes

A note is a collaborative Markdown document. People edit it in the browser in
real time; `dreamlake notes` is how a script or an agent reads and edits the
same document from a shell.

The new default read/patch contract carries exact source, hashes and opaque
write revisions together. This source change requires the Notes v2 server
contract; it is not a released client or deployed compatibility claim. Use
`--legacy` explicitly against older servers. The compatibility examples below
retain existing body-only reads and ETag behavior.

## Revision-safe Bash workflow (v2)

Both reads and uploads select `--format inline-dff` (default) or `--format diff`.
`notes diff --since` is an alias for incremental `notes read --since`. Reading
one format does not constrain the upload format. The backend owns strict parsing
and compiles validated edits to native RTC operations; the CLI does not apply
DMP or guess an alignment.

Text stdout contains `note`, `hash`, `revision`, a blank line and exact source.
An incremental response adds `format`, `base`, `unit` and the patch. `--json`
uses `content` for full reads or `base`/`patch` for incremental reads. Diagnostics
go to stderr. The CLI verifies the SHA-256 of full source before emitting it.
A malformed or legacy response is an error, never a silent downgrade.

```bash file="terminal"
set -euo pipefail
NOTE_ID=design-doc
# Login first; add --namespace <slug> for an organization's Note.
dreamlake notes read "$NOTE_ID" --json > baseline.json
BASE_HASH=$(jq -er .hash baseline.json)
BASE=$(jq -er .revision baseline.json)
jq -jr .content baseline.json > base.md

dreamlake notes read "$NOTE_ID" --since "$BASE_HASH" --format inline-dff
dreamlake notes read "$NOTE_ID" --since "$BASE_HASH" --format diff

# This example requires exact base source: Hello world. (no trailing LF).
dreamlake notes patch "$NOTE_ID" --format inline-dff --if-match "$BASE" --json > committed.json <<'PATCH'
@@ chars 0:12 @@
~ Hello [-world-]{+team+}.
PATCH
REVISION=$(jq -er .revision committed.json)
dreamlake notes read "$NOTE_ID" --if-match "$REVISION" --json > verified.json
```

The quoted here-document preserves variables, backticks, newlines and Unicode
literally. Choose a delimiter absent as a standalone patch line. Input defaults
to stdin; pipes and `--file -` work. Optional `--file path` or `--diff string`
conflicts with redirected stdin and with each other. Interactive stdin is
refused. Empty input is a no-op patch, not a whole-body deletion. `--dry-run`
prints the proposed request without uploading it.

Uploads require the original saved `--if-match` revision; `--force` is refused.
No preflight read silently replaces that token. After success, read with the
acknowledged revision before advancing a local sidecar or replacing an immutable
base snapshot. Keep local drafts and their original baselines on errors. A
separately fetched diff does not advance a draft baseline. Exit 3 means stale,
4 means RTC unavailable, and 5 means a rejected patch.

Hash references use `sha256:<hex>`. Time references are passed unchanged to the
server, including timestamps, dates and `"2 hours ago"`; server retention and
timezone rules apply. Unknown bases fail explicitly. Partial/numbered reads
remain available with `--legacy`; they are not v2 source snapshots. HTML source
mapping is a separate milestone and is not enabled by this CLI change.

## Browser sync and recovery

The browser's **Synced**, **Syncing**, and **Out of sync** indicator checks the
editor against the collaboration server. **Syncing** includes normal pending
edits and reconnects; simultaneous editing remains supported.

If a browser holds a draft after a mismatch, open **Out of sync ▾**, download
the local draft, then choose **Use server version** when you are ready to
discard that browser draft. The CLI reads the server version. It cannot read,
clear, or recover a draft held in another browser tab. Do not force-write an
old export to resolve the warning; compare it with a fresh read and make a
revision-checked edit.

The browser also offers view-only time travel: play or step through retained
versions without changing the live note. There is no new CLI history or restore
command. See the [Notes guide](https://docs.dreamlake.ai/notes/) for browser
controls and recovery details.

## Finding a note

```bash file="terminal"
dreamlake notes list
dreamlake notes list --shared        # shared with you, from other namespaces
dreamlake notes search deploy
```

### Which namespace

Notes belong to a namespace, and **the default is your personal one** — not an
organization you belong to. An organization's notes live in its own namespace
and are only reachable by naming it:

```bash file="terminal"
dreamlake notes list                        # your own
dreamlake org list                          # the organizations you belong to
dreamlake notes list --namespace acme       # one of theirs
```

`--namespace` works on every command below. `notes list --shared` is the one
exception that crosses namespaces: it lists what other people shared with you,
wherever it lives.

A note is named by its slug, its title, or its id. All three work wherever
`<note>` appears below.

`search` is current: before querying, it flushes the notes anyone has open in
this namespace, so a sentence a colleague typed seconds ago is findable. You
do not have to wait for anything.

`search` also says **where** in each note it matched:

```
NOTE      SLUG        UPDATED     ID
Runbook   runbook     2026-03-01  507f…

runbook
  deploy  …Run `pnpm run deploy` to ship…
```

Go straight to that section — `notes read runbook --section deploy` — instead
of reading the whole note to find it. The most specific section is listed
first.

`search` matches **titles and bodies**, case-insensitively, by substring — so a
phrase inside a note finds it, and so does a fragment of an identifier like
`LAKE_REMOTE`. Chinese and other non-spaced scripts match the same way.

A note last written before bodies were indexed matches on its title only,
until someone edits it or an administrator runs the one-off backfill.

## Creating

```bash file="terminal"
dreamlake notes create "Design Doc"
dreamlake notes create "Design Doc" --file draft.md
dreamlake notes create "Public Notes" --text '# Hello\n' --public
```

Titles may repeat; the slug gets a suffix to stay unique, so the command
prints the slug and id it actually made rather than the title you asked for.

## Reading

```bash file="terminal"
dreamlake notes read --legacy design-doc                 # the whole body, to stdout
dreamlake notes read --legacy design-doc > local.md      # …which means this works
dreamlake notes sections design-doc             # the outline
dreamlake notes read --legacy design-doc --section install
```

`sections` lists what you can address:

```
ANCHOR    LEVEL  TITLE        CHARS
title     1      Design Doc     820
install   2        Install      412
macos     3          macOS      180
usage     2        Usage        228
```

A **section** is a heading plus everything under it, up to the next heading of
the same or a higher level — so `install` contains `macos`. The anchor is a
slug of the title, with a numeric suffix when titles repeat (`setup`,
`setup-2`). Text before the first heading is addressed as `preamble`.

For a long note, read a range of lines:

```bash file="terminal"
dreamlake notes read --legacy design-doc --start-line 40 --end-line 80
dreamlake notes read --legacy design-doc --start-line 40 --end-line 80 --numbered
```

A partial read says so on stderr, so a redirected body stays a body. The
revision it reports is the **whole** note's — writing a range back as the body
would delete everything outside it.

## Writing

```bash file="terminal"
# one section
dreamlake notes write design-doc --section install --file install.md

# the whole body
dreamlake notes write design-doc --file whole.md

# inline, or from a pipe
dreamlake notes write design-doc --section install --text '## Install
pip install dreamlake
'
cat install.md | dreamlake notes write design-doc --section install

# add to the end
dreamlake notes append design-doc --text $'\n## Changelog\n- shipped\n'
```

A section is replaced **verbatim, heading included** — which is how you rename
one. Leave the heading out and the section stops being a section.

### Adding and removing sections

```bash file="terminal"
dreamlake notes insert design-doc --after install --text '## Troubleshooting

Check the logs.
'
dreamlake notes insert design-doc --before install --file prereqs.md
dreamlake notes insert design-doc --text '## Licence\n\nMIT\n'   # at the end

dreamlake notes rm-section design-doc troubleshooting
```

`--after` places the new section past that one **and its subsections** —
anything else would drop it inside the section you named. The heading is part
of the text, so you pick the level: a `###` can go under a `##`.

`insert` prints the new outline, because the anchor is only knowable afterwards
— a duplicate title takes the next free suffix.

`rm-section` removes the subtree too. That is what the section is; leaving the
subsections behind would promote them into the previous one.

## Editing by what it says

Naming the text beats counting lines, and is safer: a query that matches twice
is **refused** rather than applied to the first one.

```bash file="terminal"
dreamlake notes find "Draft" --note design-doc
dreamlake notes replace "Draft" --text "Published" --all --note design-doc
dreamlake notes replace --regex '(\w+)=(\d+)' --text '$1: $2' --all --note design-doc --dry-run
dreamlake notes insert --text "New line" --line 10 --note design-doc
dreamlake notes delete "obsolete paragraph" --note design-doc
dreamlake notes toc --note design-doc
```

Patterns are JavaScript: `(?<name>…)`, `$1`, `$<name>`, `$&`. Expansion is
automatic. `--dry-run` prints the result without writing, and every mutation
takes `--if-match`.

For HTML, address an element:

```bash file="terminal"
dreamlake notes select "#contact" --note page
dreamlake notes replace "Contact us" --text "Talk to sales" --selector "#contact" --note page
dreamlake notes insert --text "<li>New</li>" --selector "#list" --position append --note page
dreamlake notes replace --html "<b>done</b>" --selector "#status" --note page
```

Only the characters addressed change — entity spelling and attribute quoting
survive, so the diff is the edit and nothing else.

## Searching across notes

`notes search` finds *which* note; `notes grep` finds *where*, in a form you
can act on.

```bash file="terminal"
dreamlake notes grep "TODO" -C 2
dreamlake notes grep --regex '\bFIXME\b' --case-sensitive
dreamlake notes grep "deploy" --glob 'spec-*' --limit 20
dreamlake notes grep "Draft" --json          # etag + character range per hit
```

Output is `slug:line:column`, like `rg`. Literal and case-insensitive by
default, so `v1.2` does not also match `v1x2`. The JSON form carries each
hit's revision and `ind` range — enough to edit exactly what was found.

## Files on a note

Files inherit the note's permissions, so an attachment on a private note stays
private.

```bash file="terminal"
dreamlake notes files upload ./report.html --note design-doc
dreamlake notes files list --note design-doc
dreamlake notes files list 'assets/*.png' --note design-doc --limit 50
dreamlake notes files cat config.json --note design-doc
dreamlake notes files download report.html --note design-doc -o ./report.html
dreamlake notes files mv old.txt new.txt --note design-doc
dreamlake notes files rm old.txt --note design-doc        # trash; restore brings it back
```

Bytes are streamed both ways and never decoded, so any file survives the round
trip. `cat` refuses a binary rather than printing mojibake you might pipe back.

To look at one:

```bash file="terminal"
dreamlake notes files preview report.html --note design-doc --open
dreamlake notes files preview report.html --note design-doc --share
dreamlake notes files preview report.html --note design-doc --revoke
```

The default link needs the reader signed in. `--share` opens without signing
in and does not expire; `--revoke` withdraws it everywhere at once. Uploaded
HTML renders in a separate origin, never the dashboard's.

## Writing while other people are in the note

Every write is a **real-time collaborative edit**. The server joins the note's
collaboration room and applies your change there, so anyone with the note open
watches it appear — and it merges with what they are typing, the same way two
people's edits merge.

That is true of all of them: `write`, `append`, `patch`, `add-section`,
`rm-section`. You do not have to wait for people to leave, and nothing is
locked.

### The precondition is a different thing

Collaboration handles two edits arriving at once. It does not help with an
edit built from a document that has since changed — read a note, spend a
minute deciding, write the whole body back, and you would erase what happened
while you were deciding.

So a write also sends the version it was based on. If the note moved in
between, it is **refused** rather than applied:

| Exit | Means | Do |
|---|---|---|
| `3` | The note changed since you read it | Re-read, redo the edit. Retrying as-is fails again. |
| `4` | The realtime service could not take the write, and people are editing | Transient — wait a few seconds and retry. |
| `5` | Your diff no longer applies | Re-read and regenerate it. |

Exit `4` is an infrastructure signal, not a queue. It means the collaboration
room was unreachable AND somebody is connected — the fallback (writing the
archive) would reset the room and cost them whatever they have not saved, so
the command refuses instead. With the service healthy you will not see it.

```bash file="terminal"
dreamlake notes write design-doc --section install --file new.md
case $? in
  0) echo "done" ;;
  3) echo "someone edited it — re-read and redo" ;;
  4) sleep 30; echo "retrying" ;;
  5) echo "regenerate the diff" ;;
esac
```

### Pinning a version yourself

`read --json` gives you the validator, which you can hold across a longer edit:

```bash file="terminal"
ETAG=$(dreamlake notes read --legacy design-doc --json | jq -r .etag)
# …edit…
dreamlake notes write design-doc --file new.md --if-match "$ETAG"
```

### Overwriting on purpose

```bash file="terminal"
dreamlake notes write design-doc --file whole.md --force
```

`--force` is the only way past the check. Overwriting a colleague should be
something you typed, not something that happened.

## Changes since your last read or edit

**Unreleased:** requires the server revision-diff endpoint and a CLI build with
`notes diff`. Check `dreamlake notes diff --legacy --help` for command availability.

A read's `etag` is the quoted SHA-256 hash of the complete note. Keep that ref
and pass it as `--since` to compare with the current body, including edits made
by others. References are retained by the server and can be reused across
shell sessions. Partial reads still identify the complete note.

```bash
NOTE=release-plan
dreamlake notes read --legacy "$NOTE" --json > note-snapshot.json
REV=$(jq -er .etag note-snapshot.json)
dreamlake notes diff --legacy "$NOTE" --since "$REV"
dreamlake notes diff --legacy "$NOTE" --since "$REV" --json > changes.json
```

These shell recipes use `jq`. Plain output writes only the unified diff to
stdout and the current ETag to stderr. `--json` returns `diff`, `from`, `to`,
and `etag` (same as `to`). `--context 0` removes context lines; the default is
3 and the maximum is 100. No changes produce empty stdout and exit 0.

`--since` is required: the CLI does not guess which earlier read you mean or
maintain a hidden per-machine baseline. Keep the quoted ETag intact. Identical
text has the same hash, regardless of RTC operations. Unknown or unretained
refs return an error; refs issued before retention was deployed may be missing.
Fetching a diff does not edit the note. Apply a patch you prepared from the
saved body using `notes patch --if-match "$REV"`; stale refs are refused.
A successful patch's JSON `etag` is the next ref you can save.

## Patching

A unified diff carries its own precondition — the context has to match — so a
document that moved refuses the patch instead of taking half of it.

```bash file="terminal"
dreamlake notes read --legacy design-doc > before.md
cp before.md after.md
# …edit after.md…
diff -u before.md after.md | dreamlake notes patch --legacy design-doc --file -
```

## Permissions

Reading needs read access; writing needs write access. A read-only share link
gives the first and not the second — reads work, writes fail with "read-only
access to this note". A note you cannot read at all reports as not found.

## Command summary

| Command | Does |
|---|---|
| `notes create <name>` | Make a note, optionally with a body |
| `notes list [--shared]` | Notes in the namespace, or shared with you |
| `notes search <query>` | Match note titles and bodies |
| `notes sections <note>` | The outline, with anchors |
| `notes read <note> [--since <ref>] [--format <format>]` | Exact source or selected patch with hash/revision metadata |
| `notes read <note> --legacy [--section <anchor>]` | Previous body-only or section output |
| `notes write <note> [--section <anchor>]` | Replace body or section |
| `notes insert <note> [--before\|--after]` | Add a section |
| `notes rm-section <note> <anchor>` | Remove a section and its subtree |
| `notes patch <note> --if-match <revision> [--format <format>]` | Upload inline or line patch from stdin |
| `notes append <note>` | Add to the end |
| `notes find <query> --note` | Where the text is, in one note |
| `notes grep <query>` | Where it is, across every note you can see |
| `notes toc --note` | Outline with line and character ranges |
| `notes replace <query> --text` | Replace by text, regex, line or selector |
| `notes insert --text` | Insert at a line, offset or element |
| `notes delete <query> --note` | Remove what a query matches |
| `notes select <css> --note` | One HTML element and its text |
| `notes files upload/download` | Attach a file, or fetch it back |
| `notes files list/mv/cp/rm/restore` | Manage what is attached |
| `notes files preview [--share]` | A link that renders the file |

Every one of them takes `--namespace`, `--json`, and the usual connection flags.
V2 `patch` requires `--if-match` and rejects `--force`; legacy mutation commands retain their previous flags.

## Command-help recipes

These examples are also shipped in each command's `--help`. Log in first.
Replace `release-plan` with a note you can access. Shell recipes using `jq`
require it locally. Each edit example captures the revision before the edit;
a stale revision requires a fresh read and a reviewed edit, never a blind force.

```bash cli-help="notes list"
dreamlake notes list --limit 10
dreamlake notes list --shared --json
dreamlake notes list --namespace acme
```

```bash cli-help="notes search"
dreamlake notes search "release plan"
dreamlake notes search deploy --namespace acme --json
```

```bash cli-help="notes create"
dreamlake notes create "Release plan" --text "Draft checklist"
printf '# Release plan\n' | dreamlake notes create "Release plan" --file - --json
```

```bash cli-help="notes read"
dreamlake notes read release-plan
dreamlake notes read release-plan --json > baseline.json
BASE_HASH=$(jq -er .hash baseline.json)
BASE=$(jq -er .revision baseline.json)
dreamlake notes read release-plan --since "$BASE_HASH" --format inline-dff
# Partial reads use the explicit compatibility interface.
dreamlake notes read release-plan --legacy --start-line 1 --end-line 20 --numbered
```

```bash cli-help="notes write"
NOTE=release-plan
dreamlake notes read --legacy "$NOTE" --json > note-snapshot.json
REV=$(jq -er .etag note-snapshot.json)
jq -r .text note-snapshot.json > note.md
# Edit note.md after reading the snapshot, then preview and apply.
dreamlake notes write "$NOTE" --file note.md --if-match "$REV" --dry-run
dreamlake notes write "$NOTE" --file note.md --if-match "$REV" --json
```

```bash cli-help="notes diff"
dreamlake notes read release-plan --json > baseline.json
BASE_HASH=$(jq -er .hash baseline.json)
dreamlake notes diff release-plan --since "$BASE_HASH" --format diff
# Keep the original baseline.json while preparing an edit.
```

```bash cli-help="notes patch"
# Requires the exact saved base: Hello world. (no trailing newline).
NOTE_ID=release-plan
dreamlake notes read "$NOTE_ID" --json > baseline.json
BASE=$(jq -er .revision baseline.json)
dreamlake notes patch "$NOTE_ID" --format inline-dff --if-match "$BASE" --json > committed.json <<'PATCH'
@@ chars 0:12 @@
~ Hello [-world-]{+team+}.
PATCH
REVISION=$(jq -er .revision committed.json)
dreamlake notes read "$NOTE_ID" --if-match "$REVISION" --json
```

```bash cli-help="notes sections"
dreamlake notes sections release-plan
dreamlake notes sections release-plan --json
```

```bash cli-help="notes files list"
dreamlake notes files list --note release-plan
dreamlake notes files list --note release-plan --json
```
