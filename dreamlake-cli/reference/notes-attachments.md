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

Next: [Notes](/notes/).
