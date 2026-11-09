<!-- generated from https://cli.dreamlake.ai/installation.md at 0.110.1 25b3739; do not edit -->

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
dl --version
```

## The `dl` command

Starting with CLI 0.110.0, both native installers and the npm package provide
`dl` alongside `dreamlake`. They run the same CLI with the same arguments,
exit status, credentials, settings, and help. For example, `dl login` and
`dl memos list` are equivalent to their `dreamlake` forms. Help continues to
use the canonical `dreamlake` name.

This is an executable on PATH, so Bash, Zsh, Fish, sh/dash, PowerShell, CMD,
and scripts can use it without loading a shell alias. Both names need the
same bin directory on PATH. On POSIX, `~/.local/bin/dl` links to `dreamlake`,
so it follows upgrades, pins, and downgrades automatically. On Windows,
`~/.local/bin/dl.exe` is a managed copy refreshed with the main executable.

For an existing native installation, re-run the bootstrap installer above to
add `dl`. An update driven by a pre-0.110.0 binary does not create the new
command; after updating, run `dreamlake install --no-modify-path` to add it
without changing shell configuration. This follows your saved channel; if you
want to retain an exact pin, pass that version to `install` explicitly.
Subsequent installs and updates maintain both commands.

The native installer leaves an unrelated `dl` file, directory, symlink, or
executable on PATH unchanged and reports the conflict. Remove or rename that
command yourself, then re-run the installer to add DreamLake's `dl`. A shell
alias or function can also take precedence; the child installer cannot inspect
these. Use your shell's command lookup (`type -a dl` in Bash/Zsh,
`type dl` in Fish, `Get-Command dl -All` in PowerShell, or `where dl` in CMD)
and check `dl --version`. A conflict with `dl` does not prevent installation
of `dreamlake`.

Shells can complete the command name from PATH. DreamLake currently ships no
argument-completion scripts for either name. Any user-maintained `dreamlake`
completion needs an additional binding for `dl`.

## npm

```bash file="terminal"
npm install -g @dreamlake/dreamlake-cli
dl --version
```

npm creates both commands using its usual bin links (command shims on Windows),
including local installs through `node_modules/.bin` and `npm exec --package
@dreamlake/dreamlake-cli -- dl --help`. The global npm bin directory must be on
PATH. Updates use `npm install -g @dreamlake/dreamlake-cli@latest`; removal uses
`npm uninstall -g @dreamlake/dreamlake-cli`, which removes both owned entries.
Automatic native updates remain disabled for the npm installation; use npm
to update it.

npm owns conflict handling: an unrelated file at the same bin path normally
causes `EEXIST`; resolve that conflict instead of using `--force`. Commands
elsewhere on PATH and shell aliases/functions still follow shell precedence.
No npm install scripts or shell startup edits are needed for `dl`.

## Product analytics

CLI 0.56.0 and later support quiet, optional usage measurement through the
DreamLake API. No command arguments or contents are collected. Set
`DREAMLAKE_TELEMETRY=0` before running the CLI or save the preference with
`dreamlake telemetry disable --quiet`. See [product analytics](cli-analytics.md) for
collected fields and delivery limits.

## What it installs

Everything lands under `$HOME` — no `sudo`, nothing system-wide:

| Path | Contents |
|---|---|
| `~/.local/share/dreamlake/versions/<version>` | the binary for each installed version |
| `~/.local/bin/dreamlake` | symlink to the active version (`dreamlake.exe`, a copy, on Windows) |
| `~/.local/bin/dl` | symlink to `dreamlake` (`dl.exe`, a managed copy, on Windows); omitted if a foreign command conflicts |
| `~/.dreamlake/settings.yml` | release channel, and a version pin if set |
| `~/.local/state/dreamlake/update.json` | when the last update check ran |

(`~/.dreamlake` also holds your logins — `tokens.json`, `config.json`, and
the per-environment cache `auth.yml`, all chmod 600 and shared with the
Python SDK — but those are written by `dreamlake login`, not the installer.)

Every download is checked against the SHA-256 in the release manifest before
writing anything executable. `XDG_DATA_HOME` and `XDG_STATE_HOME`, when absolute,
move the version store and update state respectively; the launcher stays at
`~/.local/bin/dreamlake` and `~/.local/bin/dl`.

## Shell PATH setup

> **Note:** The expanded shell setup and opt-out controls below require CLI 0.107.2
> or later. CLI 0.107.1 and earlier configure only one startup file and do not support
> `--no-modify-path` or `DREAMLAKE_INSTALL_NO_MODIFY_PATH`.

The installer configures the shell named by `$SHELL`, even when the bootstrap
runs through `curl ... | bash`. It prints each file it updates or finds already
configured, and a command to apply PATH in your current shell. No prompt or
terminal is required. Only explicit `dreamlake install` configures PATH;
`self-update`, including background updates, leaves shell files alone.

| Shell | Startup files configured | Applies to |
| --- | --- | --- |
| Bash | `~/.bashrc` plus the first existing `~/.bash_profile`, `~/.bash_login`, or `~/.profile`; creates `~/.profile` if none exists | Interactive shells and login shells |
| Zsh | `$ZDOTDIR/.zprofile` and `$ZDOTDIR/.zshrc`, using `$HOME` when `ZDOTDIR` is unset | Login shells and interactive shells |
| Fish | `$XDG_CONFIG_HOME/fish/conf.d/dreamlake-path.fish`, using `~/.config` when XDG is unset or relative | Shells that load Fish configuration |
| sh / dash | `~/.profile` | Login shells only |
| Other or unset `$SHELL` | No automatic edits | Manual setup required |

Export an absolute `ZDOTDIR` before installing if you use a custom location;
the installer does not execute `.zshenv` to discover it. Relative `ZDOTDIR` is
reported for manual setup. Fish's `config.fish` and universal variables are
left unchanged. On Windows the native installer updates the current user's
registry PATH; open a new terminal afterward.

Each shell block checks PATH before adding `~/.local/bin`, so repeated installs
and sourcing do not add duplicate entries. Setup still runs when the installer
already inherited that directory in PATH: that does not prove future shells are
configured. Existing user content and file permissions are preserved. The
installer upgrades its exact old unguarded export; customized DreamLake blocks,
symlinked startup files, special files, and files it cannot safely read or write
are left unchanged with manual guidance. An unavailable shell configuration does
not undo a successful binary installation.

To leave shell files and user PATH unchanged, use either control below. These
work without prompting in both terminals and unattended provisioning; they do
not remove configuration from an earlier install.

```bash file="terminal"
curl -fsSL https://dl.dreamlake.ai/install.sh | bash -s -- --no-modify-path
curl -fsSL https://dl.dreamlake.ai/install.sh | DREAMLAKE_INSTALL_NO_MODIFY_PATH=1 bash
```

An installed or downloaded binary accepts the same flag:

```bash cli-help="install" file="terminal"
# Reinstall and configure the shell selected by SHELL.
dreamlake install
# Install a channel without editing shell startup files or user PATH.
dreamlake install stable --no-modify-path
```

The installer cannot change its parent shell's environment. Open a new terminal
that reads the configured files, or apply PATH in the current shell:

```bash file="Bash / Zsh / sh / dash"
case ":$PATH:" in
    *":$HOME/.local/bin:"*) ;;
    *) export PATH="$HOME/.local/bin${PATH:+:$PATH}" ;;
esac
```

```fish file="Fish"
contains -- "$HOME/.local/bin" $PATH; or set -gx PATH "$HOME/.local/bin" $PATH
```

### SSH commands and other noninteractive shells

Startup-file edits do not guarantee PATH in a noninteractive SSH command,
service, cron job, or shell started with startup files disabled. Bash and Zsh
load different files for login and interactive modes; `sh -lc` uses sh's login
configuration, not Zsh's `.zprofile` or `.zshrc`. Later user configuration can
also replace PATH. Use the full binary path or set PATH explicitly in that
command's environment:

```bash file="remote POSIX shell"
"$HOME/.local/bin/dreamlake" --version
PATH="$HOME/.local/bin:$PATH" dreamlake --version
```

For example, a macOS account using Zsh may run `dreamlake` successfully in a new
terminal while `sh -lc 'dreamlake --version'` still cannot find it. Use
`sh -lc '"$HOME/.local/bin/dreamlake" --version'` for that environment. No global
shell configuration or SSH daemon settings are changed.

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

> **Warning:** The install lives under that machine's `~/.local/share/dreamlake`, so every
> computer you use updates on its own schedule. A feature that works on one
> machine and prints an older error on another usually means the second one
> hasn't picked up the release yet: run `dreamlake --version` there, then
> `dreamlake self-update`.

On macOS, every update check (background or `dreamlake self-update`) also
removes the leftover nymph restart job from the October 2026 fleet upgrade, if
present: a submitted `ai.dreamlake.refresh.*` launchd job running
`~/.local/share/dreamlake/fleet-upgrades/<id>/restart.py`, which restarted
nymph every ~15 seconds. No other job is touched.

On Windows there is no background updater at all: Windows locks a running
`.exe`, so updates are always an explicit `dreamlake self-update`.

After an update, installed agent skills are checked against the new bundled
reference. If a local copy differs, the CLI reminds you with its path and an
update command. Skills are never overwritten automatically. See
[skill update reminders](cli-skills.md#reminders-after-updating) for scope and behavior.

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

If `dreamlake` is not found, run `"$HOME/.local/bin/dreamlake" doctor` to
inspect the installed launcher and the current process's PATH. Follow the
[shell PATH setup](#shell-path-setup) instructions above; a startup file may
have been skipped or may not apply to the shell you are running.

## From source

For working on the CLI itself:

```bash file="terminal"
git clone https://github.com/dreamlake-ai/dreamlake-cli.git
cd dreamlake-cli
pnpm install
pnpm cli --help          # runs src/ through tsx, no build step
pnpm link --global      # optional: expose both dreamlake and dl for development
```

## Uninstall

Remove `dl` only if it belongs to DreamLake; preserve any conflicting command
that the installer left untouched. On macOS/Linux/WSL:

```bash file="terminal"
if [ -L "$HOME/.local/bin/dl" ] && [ "$(readlink "$HOME/.local/bin/dl")" = dreamlake ]; then
    rm "$HOME/.local/bin/dl"
fi
rm -f  ~/.local/bin/dreamlake
rm -rf ~/.local/share/dreamlake ~/.local/state/dreamlake ~/.dreamlake
```

On Windows, close running CLI processes, then remove `dreamlake.exe` and the
DreamLake-owned `dl.exe` from `$HOME\.local\bin`, plus the DreamLake data/state
directories listed above. Do not remove a foreign `dl.exe` that the installer
reported as a conflict. For npm installs use the npm uninstall command above;
for a source link use `pnpm remove --global @dreamlake/dreamlake-cli`.

(`~/.dreamlake` holds saved logins, settings, and resumable-upload state —
note the Python SDK reads its credentials from there too.) On a machine
that ran a ≤ 0.4.x CLI, add `rm -rf ~/.config/dreamlake` for its old
location. For every version, remove the `# added by the dreamlake installer`
blocks from the startup files listed above, or remove Fish's
`conf.d/dreamlake-path.fish` if it contains only the installer block. Keep any
user additions and other tools' PATH setup. On Windows remove the installer
entry from your user PATH if no other program uses it.

## Next

- [Quick start](cli-quick-start.md) — log in and move a file end-to-end.
- [Environments](cli-environments.md) — point the CLI at staging or prod.
