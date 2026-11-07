<!-- generated from https://cli.dreamlake.ai/notes/attachments.md at 0.109.0 9f5a92b; do not edit -->

# Attachments

The [Memo presence and attachment API map](https://cli.dreamlake.ai/dev/note-collaboration-api) lists
matching TypeScript operations, JSON receipts, and recovery behavior.

Files inherit the memo's permissions. Uploading a file to a private memo keeps
it private. Set `MEMO_ID` to an accessible memo and add its owner's `--namespace`
when needed.

## Upload and retrieve

```bash
MEMO_ID=release-plan
dreamlake memos files upload ./report.html --note "$MEMO_ID"
dreamlake memos files upload ./chart.png --path assets/chart.png --note "$MEMO_ID"
dreamlake memos files cat config.json --note "$MEMO_ID"
dreamlake memos files download report.html --note "$MEMO_ID" -o ./downloaded-report.html
```

Uploads and downloads preserve bytes. `cat` refuses binary content; use
`download` for it. Downloads default to stdout if no output path is supplied.
Existing paths require explicit `--overwrite` where supported.

```bash cli-help="memos files list"
dreamlake memos files list --note release-plan
dreamlake memos files list 'assets/*.png' --note release-plan --limit 50
dreamlake memos files list --note release-plan --json
```

## Upload inline media and return its URL

Check `dreamlake memos media upload --help` for availability. Requires CLI 0.37.0 or later. If unavailable in your installed CLI, use the
[HTTP upload example](https://docs.dreamlake.ai/notes/files/#get-an-image-url-for-markdown-or-html)
with a valid API bearer token.

After `dreamlake login`, upload an image and print only its embeddable URL:

```bash cli-help="memos media upload"
dreamlake memos media upload ./diagram.png
IMAGE_URL=$(dreamlake memos media upload ./diagram.png)
```

Choose one of those commands: each invocation uploads a new media object.
No memo ID, namespace, `curl`, `jq` or `--json` is required. The command uses
saved login credentials and supports `--remote` and `--token`. For video embedding syntax, see [Videos](cli-notes-videos.md). Images and
videos are accepted; the server detects the type from the bytes. Optional
`--json` returns `url`, `contentType` and `sizeBytes`.

Use the returned URL in a Markdown or HTML file:

```bash
printf '\n![Architecture diagram](%s)\n' "${IMAGE_URL:?Upload the image first}" > image.md
printf '<img src="%s" alt="Architecture diagram">\n' "${IMAGE_URL:?Upload the image first}" > image.html
```

To append the Markdown to an existing memo, set `MEMO_ID` to its ID and run
`dreamlake memos append "$MEMO_ID" --file image.md`. Uploading media alone
does not edit a memo. Use Markdown for the Memos body; HTML markup is for an
HTML document. Keep the returned media URL, not its temporary storage redirect.

Anyone holding a media URL can load it without signing in. Making a memo
private does not revoke that URL. To keep an image under a memo's permissions,
use `memos files upload ./diagram.png --note "$MEMO_ID"` instead. That stores
an attachment with a logical path, not an embeddable URL. `memos files preview`
returns a viewer page, not an image `src`. Media uploads are not included in
`memos files list`.

## Manage files

```bash
dreamlake memos files mv old.txt new.txt --note "$MEMO_ID"
dreamlake memos files cp report.html report-copy.html --note "$MEMO_ID"
dreamlake memos files rm old.txt --note "$MEMO_ID"
dreamlake memos files list --trashed --note "$MEMO_ID"
```

`rm` moves a file to trash. Use `files restore --help` to restore the returned
file ID, optionally to a new path. `rm --purge` requests permanent deletion.
Current production has durable purge disabled: immutable attachments and files
with retained object lineage fail closed instead of deleting their stored bytes.
The CLI flag does not establish server support; do not treat a refusal or an
unconfirmed response as successful deletion.
File write/move/remove operations support `--if-match` with the **file's** ETag,
not the memo's write revision.

## Recover an attachment operation (CLI 0.48.2)

CLI 0.48.2 adds these flags and recovery commands; CLI 0.48.1 does not include
them. Check installed `--help` and server support independently. They require a
separately verified server with its known-byte publication journal enabled;
a503 unavailable response is not permission to fall back to an unguarded write.

For text writes and copies only, supply a stable printable ASCII key (1–256 bytes)
without surrounding spaces for one exact request. The CLI passes it unchanged and never automatically retries.

```bash cli-help="memos files write"
dreamlake memos files write config.json --text '{"enabled":true}' --note "$MEMO_ID" --idempotency-key config-initial-1
```

```bash cli-help="memos files cp"
dreamlake memos files cp config.json config-copy.json --note "$MEMO_ID" --idempotency-key config-copy-1
```

A response supplies an operation ID on stderr, or as an additive `operationId`
field with `--json`. Preserve that ID, the exact original request, key, Memo ID
and namespace. On an uncertain result, inspect the original operation first;
do not resend bytes, change the key, or create a replacement file. A changed
request under the same key is a409 conflict. Requests without a key remain
distinct operations. `files upload` is streamed and does **not** support the key
or this journal recovery contract; media upload is also outside this scope.

```bash cli-help="memos files status"
# OPERATION_ID is the ID from the original response.
dreamlake memos files status "$OPERATION_ID" --note "$MEMO_ID" --json
```

```bash cli-help="memos files reconcile"
dreamlake memos files reconcile "$OPERATION_ID" --note "$MEMO_ID" --json
```

Status is read-only. Reconcile verifies original staged bytes and may publish the
original database result; it never uploads bytes again. A published historical
receipt does not prove that file is still live. Current Memo edit authority and
the original actor are required; add the original `--namespace` for org memos.
An unconfirmed outcome stays unresolved:404 from storage, elapsed time and a
failed request do not establish that an upload cannot arrive later.

```bash cli-help="memos files cancel"
dreamlake memos files cancel "$OPERATION_ID" --note "$MEMO_ID" --json
```

Cancel is available only while admitted, before upload authorization. It retains
the operation and key as `aborted-before-write`; it deletes no objects and cannot
cancel `write-started` or `published` work. A cancelled operation cannot be
replayed with the same key. Inspect after an uncertain cancellation response.
These commands do not transfer a Memo, grant access or complete storage recovery.

## Preview and share

```bash
dreamlake memos files preview report.html --note "$MEMO_ID" --open
```

The default preview requires sign-in. HTML renders on a separate origin from
the dashboard. To deliberately create or withdraw a public preview link:

```bash
dreamlake memos files preview report.html --note "$MEMO_ID" --share
dreamlake memos files preview report.html --note "$MEMO_ID" --revoke
```

A shared link opens without sign-in and does not expire. Revoking it withdraws
all copies of that link. This is distinct from publishing the memo itself.

Next: [Memos](cli-notes.md).
