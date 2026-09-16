# Installation

The CLI is a single native binary. There is no runtime to install first,
and it keeps itself up to date.

**macOS, Linux, WSL:**

```bash file="terminal"
curl -fsSL https://dl.dreamlake.ai/install.sh | bash
```

**Windows (PowerShell):**

```powershell file="terminal"
irm https://dl.dreamlake.ai/install.ps1 | iex
```

From CMD, wrap it: `powershell -NoProfile -Command "irm https://dl.dreamlake.ai/install.ps1 | iex"`

Open a new terminal and confirm:

```bash file="terminal"
dreamlake --version
```

## What it installs

Everything lands under `$HOME` — no `sudo`, nothing system-wide:

| Path | Contents |
|---|---|
| `~/.local/share/dreamlake/versions/<version>` | the binary for each installed version |
| `~/.local/bin/dreamlake` | symlink to the active version (a copy on Windows, which has no unprivileged symlinks) |
| `~/.dreamlake/settings.yml` | release channel, and a version pin if set |
| `~/.local/state/dreamlake/update.json` | when the last update check ran |

(`~/.dreamlake` also holds your logins — `tokens.json`, `config.json`, and
the per-environment cache `auth.yml`, all chmod 600 and shared with the
Python SDK — but those are written by `dreamlake login`, not the installer.)

The installer appends one line to your login shell's rc file if
`~/.local/bin` isn't on `PATH` already, and checks every download against
the SHA-256 in the release manifest before writing anything executable.

> **Note:** macOS 13+ (Apple Silicon and Intel), Linux x86-64 / arm64 on both glibc and
> musl, and Windows 10+ x86-64 / arm64. 32-bit Windows is not supported.

## Updates

At most once every four hours, a command may start a short detached
background process that installs any newer release; it takes effect on your
next command.

```bash file="terminal"
dreamlake self-update                  # update now
dreamlake self-update 0.3.0            # pin to an exact version
dreamlake self-update channel stable   # switch channel (also unpins)
dreamlake self-update --status         # version, channel, pin, last check
```

Installing an exact version **pins** it — auto-update stays paused until you
pick a channel again. Without that, the updater would quietly move you off
the version you asked for.

On Windows there is no background updater at all: Windows locks a running
`.exe`, so updates are always an explicit `dreamlake self-update`.

> **Note:** `dreamlake update` edits bindrs, datasets, and projects. Updating the CLI
> itself is `dreamlake self-update`.

Channels: `latest` (default) ships every release; `stable` moves only when a
release is promoted with `publish-release.sh --stable`. Set
`DREAMLAKE_DISABLE_AUTOUPDATER=1` to stop background checks while leaving
`self-update` and `install` working, or `DREAMLAKE_DISABLE_UPDATES=1` to
block every path that would change your version.

## Diagnosing

```bash file="terminal"
dreamlake doctor
```

Prints the running executable, the version the launcher points at, your
channel, and the last auto-update result. No network calls.

If `dreamlake` is not found right after installing, your current shell
started before the `PATH` line was added — open a new terminal, or run
`export PATH="$HOME/.local/bin:$PATH"`.

## From source

For working on the CLI itself:

```bash file="terminal"
git clone https://github.com/dreamlake-ai/dreamlake-cli.git
cd dreamlake-cli
pnpm install
pnpm cli --help          # runs src/ through tsx, no build step
```

## Uninstall

```bash file="terminal"
rm -f  ~/.local/bin/dreamlake
rm -rf ~/.local/share/dreamlake ~/.local/state/dreamlake ~/.dreamlake
```

(`~/.dreamlake` holds saved logins, settings, and resumable-upload state —
note the Python SDK reads its credentials from there too.) On a machine
that ran a ≤ 0.4.x CLI, add `rm -rf ~/.config/dreamlake` for its old
location, and delete the `# added by the dreamlake installer` block from
your shell rc.

## Next

- [Quick start](quick-start.md) — log in and move a file end-to-end.
- [Environments](environments.md) — point the CLI at staging or prod.
