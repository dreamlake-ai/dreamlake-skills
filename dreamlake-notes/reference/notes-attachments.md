# Attachments

Files inherit the note's permissions. Uploading a file to a private note keeps
it private. Set `NOTE_ID` to an accessible note and add its owner's `--namespace`
when needed.

## Upload and retrieve

```bash
NOTE_ID=release-plan
dreamlake notes files upload ./report.html --note "$NOTE_ID"
dreamlake notes files upload ./chart.png --path assets/chart.png --note "$NOTE_ID"
dreamlake notes files cat config.json --note "$NOTE_ID"
dreamlake notes files download report.html --note "$NOTE_ID" -o ./downloaded-report.html
```

Uploads and downloads preserve bytes. `cat` refuses binary content; use
`download` for it. Downloads default to stdout if no output path is supplied.
Existing paths require explicit `--overwrite` where supported.

```bash cli-help="notes files list"
dreamlake notes files list --note release-plan
dreamlake notes files list 'assets/*.png' --note release-plan --limit 50
dreamlake notes files list --note release-plan --json
```

## Upload an inline image and return its URL

Check `dreamlake notes media upload --help` for availability. Requires CLI 0.37.0 or later. If unavailable in your installed CLI, use the
[HTTP upload example](https://docs.dreamlake.ai/notes/#get-an-image-url-for-markdown-or-html)
with a valid API bearer token.

After `dreamlake login`, upload an image and print only its embeddable URL:

```bash cli-help="notes media upload"
dreamlake notes media upload ./diagram.png
IMAGE_URL=$(dreamlake notes media upload ./diagram.png)
```

Choose one of those commands: each invocation uploads a new media object.
No note ID, namespace, `curl`, `jq` or `--json` is required. The command uses
saved login credentials and supports `--remote` and `--token`. Images and
videos are accepted; the server detects the type from the bytes. Optional
`--json` returns `url`, `contentType` and `sizeBytes`.

Use the returned URL in a Markdown or HTML file:

```bash
printf '\n![Architecture diagram](%s)\n' "${IMAGE_URL:?Upload the image first}" > image.md
printf '<img src="%s" alt="Architecture diagram">\n' "${IMAGE_URL:?Upload the image first}" > image.html
```

To append the Markdown to an existing note, set `NOTE_ID` to its ID and run
`dreamlake notes append "$NOTE_ID" --file image.md`. Uploading media alone
does not edit a note. Use Markdown for the Notes body; HTML markup is for an
HTML document. Keep the returned media URL, not its temporary storage redirect.

Anyone holding a media URL can load it without signing in. Making a note
private does not revoke that URL. To keep an image under a note's permissions,
use `notes files upload ./diagram.png --note "$NOTE_ID"` instead. That stores
an attachment with a logical path, not an embeddable URL. `notes files preview`
returns a viewer page, not an image `src`. Media uploads are not included in
`notes files list`.

## Manage files

```bash
dreamlake notes files mv old.txt new.txt --note "$NOTE_ID"
dreamlake notes files cp report.html report-copy.html --note "$NOTE_ID"
dreamlake notes files rm old.txt --note "$NOTE_ID"
dreamlake notes files list --trashed --note "$NOTE_ID"
```

`rm` moves a file to trash. Use `files restore --help` to restore the returned
file ID, optionally to a new path. `rm --purge` permanently deletes stored bytes.
File write/move/remove operations support `--if-match` with the **file's** ETag,
not the note's write revision.

## Recover an attachment operation (CLI 0.48.2)

CLI 0.48.2 adds these flags and recovery commands; CLI 0.48.1 does not include
them. Check installed `--help` and server support independently. They require a
separately verified server with its known-byte publication journal enabled;
a503 unavailable response is not permission to fall back to an unguarded write.

For text writes and copies only, supply a stable printable ASCII key (1–256 bytes)
without surrounding spaces for one exact request. The CLI passes it unchanged and never automatically retries.

```bash cli-help="notes files write"
dreamlake notes files write config.json --text '{"enabled":true}' --note "$NOTE_ID" --idempotency-key config-initial-1
```

```bash cli-help="notes files cp"
dreamlake notes files cp config.json config-copy.json --note "$NOTE_ID" --idempotency-key config-copy-1
```

A response supplies an operation ID on stderr, or as an additive `operationId`
field with `--json`. Preserve that ID, the exact original request, key, Note ID
and namespace. On an uncertain result, inspect the original operation first;
do not resend bytes, change the key, or create a replacement file. A changed
request under the same key is a409 conflict. Requests without a key remain
distinct operations. `files upload` is streamed and does **not** support the key
or this journal recovery contract; media upload is also outside this scope.

```bash cli-help="notes files status"
# OPERATION_ID is the ID from the original response.
dreamlake notes files status "$OPERATION_ID" --note "$NOTE_ID" --json
```

```bash cli-help="notes files reconcile"
dreamlake notes files reconcile "$OPERATION_ID" --note "$NOTE_ID" --json
```

Status is read-only. Reconcile verifies original staged bytes and may publish the
original database result; it never uploads bytes again. A published historical
receipt does not prove that file is still live. Current Note edit authority and
the original actor are required; add the original `--namespace` for org notes.
An unconfirmed outcome stays unresolved:404 from storage, elapsed time and a
failed request do not establish that an upload cannot arrive later.

```bash cli-help="notes files cancel"
dreamlake notes files cancel "$OPERATION_ID" --note "$NOTE_ID" --json
```

Cancel is available only while admitted, before upload authorization. It retains
the operation and key as `aborted-before-write`; it deletes no objects and cannot
cancel `write-started` or `published` work. A cancelled operation cannot be
replayed with the same key. Inspect after an uncertain cancellation response.
These commands do not transfer a Note, grant access or complete storage recovery.

## Preview and share

```bash
dreamlake notes files preview report.html --note "$NOTE_ID" --open
```

The default preview requires sign-in. HTML renders on a separate origin from
the dashboard. To deliberately create or withdraw a public preview link:

```bash
dreamlake notes files preview report.html --note "$NOTE_ID" --share
dreamlake notes files preview report.html --note "$NOTE_ID" --revoke
```

A shared link opens without sign-in and does not expire. Revoking it withdraws
all copies of that link. This is distinct from publishing the note itself.

Next: [Notes](notes.md).
