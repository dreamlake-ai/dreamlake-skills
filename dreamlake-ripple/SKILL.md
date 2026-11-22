---
name: dreamlake-ripple
description: Install the Ripple CPU and memory collector (formerly lakeshore-host-metrics) on Linux or macOS by hand, read local samples without an account, report an enrolled host through the manual operator-token service, and check or remove it. Not for enrolling hosts or Ripple set up by dl hosts enroll.
---

# Ripple collector

Ripple is a small standalone collector that samples CPU and memory on Linux
and macOS. It works on its own (print local samples, no account) or reports
an enrolled host to DreamLake. There are two supported reporting paths:

- **At enrollment.** When the installed `dl hosts enroll --help` lists
  `--ripple` and `--no-ripple`, enrollment sets Ripple up itself, signed with
  the enrollment's identity, as the enrolled user, with no operator token and
  no root. That path, its receipt and its retries belong to the `machines`
  action of `dreamlake-lakeshore`, not to this skill.
- **By hand (this skill).** For an older CLI, or when the user asks for it:
  the DreamLake operator enables the host and issues a machine token, and
  Ripple runs as a systemd service on Linux (root) or a per-user launchd agent
  on macOS (never root).

Use the release that is actually published; supported systems and versions
are listed in
[reference/docs-lakeshore-hosts-metrics.md](reference/docs-lakeshore-hosts-metrics.md#ripple-collector).

## When to use

- "Install ripple", "set up the host metrics collector", "is ripple running",
  "show this machine's CPU and memory with ripple", "make this host report CPU
  and memory to DreamLake", "upgrade / rotate the token / remove ripple".
- Not for enrolling or connecting a host, or for Ripple that `dl hosts enroll`
  installs, adds with `--ripple` or skips with `--no-ripple` (the
  `dreamlake-lakeshore` skill), not for reading metrics back from DreamLake
  (`dl hosts metrics`, also `dreamlake-lakeshore`), and not for releasing or
  building Ripple itself.

## Route the request

| Request looks like | Open |
|---|---|
| Install or upgrade the binary; print local samples; verify a download | [actions/install.md](actions/install.md) |
| Report an enrolled host to DreamLake (systemd or launchd); check, inspect backlog, upgrade, rotate token; opt in to or out of automatic updates; set its upgrade target | [actions/service.md](actions/service.md) |
| Stop reporting or uninstall | [actions/remove.md](actions/remove.md) |

## Rules

- Never install onto a machine the user did not name, and say which machine
  and which user you are acting as before anything needs root.
- The manual path has no self-service token: it needs a machine ID and a
  matching machine token from the DreamLake operator. Never invent, mint or
  reuse another machine's token, and never accept a user sign-in token in its
  place. Do not ask for one when enrollment can set Ripple up itself.
- If Ripple already reports an enrollment (set up at enrollment or by hand),
  leave it: do not run manual setup over it, re-enroll, or call an
  `awaiting_data` or `pending` enrollment receipt a failure.
- Never print, echo, paste or commit a token; keep it in a `0600` file.
- A container measures the kernel it runs on: on a Mac, a Docker container
  reports Docker Desktop's Linux virtual machine, not the Mac.
- On macOS, install by hand only with `install.sh` (enrollment uses its own
  verified setup); never remove a quarantine
  attribute or override Gatekeeper. The launchd agent runs only while its
  user is logged in; do not suggest auto-login to work around that.
- Claim only what a command showed: an installed binary is not a running
  service, and a running service is not proof DreamLake received samples.

## Canonical source

Product facts come from the docs site, fetched into `reference/` by CI:

- https://docs.dreamlake.ai — [Machine metrics](reference/docs-lakeshore-hosts-metrics.md)
  (Ripple collector) and [Enroll a host](reference/docs-lakeshore-hosts-enroll.md)

Every page is fetchable as Markdown at `<page-url>.md`. Do not edit
`reference/`; CI overwrites it.
