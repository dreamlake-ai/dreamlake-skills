---
name: remote-source-check
description: >
  Verify that a connected DreamLake source really holds the files a workflow
  will read — before they are written into a spec. Use when a user names a
  source plus paths as workflow input, or asks to "check/validate this data"
  for a pipeline. Rejects raw URLs and local paths: the worker reads through
  the source, and the machine that runs the job is not this machine.
---

# Source check

A workflow spec written here executes **somewhere else** — a queue worker on a
GPU box. Inputs are named as a **source** (a connected S3 / Dropbox /
HuggingFace store) plus a **path** inside it, and the worker resolves that pair
at run time with the token the run carries. So the thing to verify is not "is
this link alive" but "does that source hold that path, and can this account see
it".

Getting it wrong fails *late*: after the queue, inside a node, minutes in.

This skill is deliberately narrow: it answers "can the worker read this?" and
nothing else.

## What you need

`source`, `source_namespace`, and one path per input (video, gold annotations).
A source name alone is ambiguous — the same name can exist in more than one
namespace, and the source's namespace has nothing to do with where the workflow
publishes.

## Procedure

**1. Reject anything that is not a source reference.**

| Input | Verdict |
|---|---|
| source + path | check it (below) |
| `https://…`, `s3://…` | **reject** — ask which source it lives in. A URL in a spec expires, cannot be reviewed, and tells the next reader nothing about where the data came from |
| `/abs/path`, `./rel`, `file://`, `C:\…` | **reject** — the worker cannot see the user's filesystem |

**2. Confirm the source exists in that namespace.**

```bash
dreamlake source list --namespace <ns> --json
```

If the name is absent, list what IS there rather than just failing — the answer
is usually one line away, and a user who mistypes a source name cannot guess the
right one from "not found".

**3. Confirm each path resolves, and look at what came back.**

```bash
dreamlake source browse "<dir>" --source <name> --namespace <ns> --files --json
dreamlake source fetch  "<path>" --source <name> --namespace <ns> --json
```

`browse` shows the path really exists and how it is spelled; `fetch` proves this
account can actually mint a download for it, which is the thing the worker does.
A path that browses but will not fetch is a permissions problem, and it is worth
separating the two — they have different fixes.

Quote every path: names with spaces are normal in these stores.

**4. Sanity-check each file against its intended role.** A video input should
look like `.mp4/.mov/.mkv/.webm`; a gold-annotation input like `.json`. A
mismatch is usually a swapped pair — cheap to catch here, confusing to debug
after a failed run. Report the size too: a 300 MB transfer is worth knowing
about *before* the run, not during it.

## Reporting

One line per input: source, path, size, verdict. If anything fails, **do not
proceed to generate a spec** — ask for a correction. A spec naming a path that
does not exist is worse than no spec: it looks finished and costs a full queue
round-trip to disprove.

Do not report the URL `fetch` mints. It is short-lived and account-scoped; it
proves the check passed and has no other use, and pasting it into a spec is
exactly what this design replaced.
