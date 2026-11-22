# Install Ripple and read local samples

Install the published binary, verify it, and print one set of local
samples. No DreamLake account, login or token is involved.

## Before you start

- Confirm the target machine and that it is the one the user means. Run every
  command on that machine (over SSH if it is remote), not on your own.
- Check the platform against the released support table in
  [reference/docs-lakeshore-hosts-metrics.md](../reference/docs-lakeshore-hosts-metrics.md#ripple-collector):

  ```bash
  uname -s; uname -m
  ```

  If the operating system or architecture is not listed as released, stop and
  say so. Do not build from source or substitute a container to make it fit:
  a container on a Mac measures Docker Desktop's Linux VM, not the Mac
  ([reference](../reference/docs-lakeshore-hosts-metrics.md#containers-and-virtual-machines)).
- Choose the install location with the user:
  - system-wide (`/usr/local/bin`, needed for the service in
    [service.md](service.md)); the installer uses `sudo` only if that
    directory is not writable;
  - user-only (`$HOME/.local/bin`), no privileges; enough for local samples.

## Steps

1. Install from the public release base named in
   [reference/docs-lakeshore-hosts-metrics.md](../reference/docs-lakeshore-hosts-metrics.md#install-the-binary).
   Pin the version the user wants; `latest` moves forward.

   ```bash
   RIPPLE_BASE=https://pub-c0109e197b4a4d1abe5884ac4dd3a023.r2.dev/dreamlake/ripple
   curl -fsSL "$RIPPLE_BASE/install.sh" | bash -s -- --version vX.Y.Z
   # user-only:
   mkdir -p "$HOME/.local/bin"
   curl -fsSL "$RIPPLE_BASE/install.sh" | bash -s -- --version vX.Y.Z --dest "$HOME/.local/bin"
   ```

   The installer prints `Verified sha256 …` and the installed path. When the
   user needs authenticity rather than corruption detection, get the hash
   from that version's `SHA256SUMS` through a separate channel and add
   `--sha256 <hash>` ([why](../reference/docs-lakeshore-hosts-metrics.md#install-the-binary)).

2. Read back what is installed, from the path the installer printed:

   ```bash
   ripple version        # or "$HOME/.local/bin/ripple" version
   ```

3. Print local samples. This sends nothing:

   ```bash
   ripple once
   ```

   Report the three sample lines as they were printed. For another label,
   pass `--machine-id=<label>`; `ripple <command> -h` lists every flag.

4. Upgrading is the same `install.sh` run with the new version. A running
   service keeps the old binary until it restarts; restart it as in
   [service.md](service.md).

## Exceptions

| Symptom | Likely cause | Do |
|---|---|---|
| Installer refuses: version mismatch | `latest/` is mid-update, or the pinned version does not exist | Pin a version listed in the release base; retry later for `latest` |
| SHA-256 mismatch | Corrupt or altered download | Stop; do not retry with `--sha256` removed. Report it |
| `--dest` does not exist | The installer does not create it | `mkdir -p` it first |
| `ripple: command not found` after a user-only install | `$HOME/.local/bin` not on `PATH` | Use the full path |
| User asks for a platform not in the released table | No published build | Say so; do not build, cross-compile or containerize as a workaround |
