# Install Ripple and read local samples

Install the published binary on Linux or macOS, verify it, and print one set
of local samples. No DreamLake account, login or token is involved.

## Before you start

- Confirm the target machine is the one the user means, and run every
  command there (over SSH if it is remote), not on your own machine.
- Check the platform against the support table in
  [reference/docs-lakeshore-hosts-metrics.md](../reference/docs-lakeshore-hosts-metrics.md#ripple-collector):

  ```bash
  uname -s; uname -m; sw_vers -productVersion 2>/dev/null
  ```

  If it is not listed, stop and say so. Do not build from source, and do not
  use a container to make it fit: a container on a Mac measures Docker's
  Linux VM, not the Mac.
- Pick the location with the user. Defaults: Linux `/usr/local/bin` (needed
  for the systemd service; `sudo` only if not writable), macOS
  `~/.local/bin` (no `sudo`). On Linux without privileges, use
  `--dest "$HOME/.local/bin"` after `mkdir -p` it.

## Steps

1. Install a pinned version from the public release base:

   ```bash
   RIPPLE_BASE=https://pub-c0109e197b4a4d1abe5884ac4dd3a023.r2.dev/dreamlake/ripple
   RIPPLE_VERSION=vX.Y.Z    # the version the user wants; check $RIPPLE_BASE/latest/VERSION
   curl -fsSL "$RIPPLE_BASE/install.sh" | bash -s -- --version "$RIPPLE_VERSION"
   ```

   Expect `Verified sha256 …` and the installed path. For authenticity rather
   than corruption detection, add `--sha256 <hash>` with the hash from that
   version's `SHA256SUMS`, obtained through a separate channel
   ([why](../reference/docs-lakeshore-hosts-metrics.md#install-the-binary)).

2. Read back the installed version from the printed path:

   ```bash
   ~/.local/bin/ripple version      # macOS default; Linux: ripple version
   ```

3. Print local samples (sends nothing) and report the lines as printed:

   ```bash
   ripple once                      # or ripple once --machine-id=<label>
   ```

   On macOS, available memory is an estimate; explain it with
   [What the readings mean](../reference/docs-lakeshore-hosts-metrics.md#what-the-readings-mean)
   rather than in your own words.

4. Upgrade by rerunning step 1 with the new version, then restart the
   service as in [service.md](service.md).

## Exceptions

| Symptom | Likely cause | Do |
|---|---|---|
| Version mismatch refused | `latest/` mid-update, or that version is not published | Pin a published version; retry later |
| SHA-256 mismatch | Corrupt or altered download | Stop and report; never drop the check |
| macOS refuses to open the binary | Downloaded through a browser or copied with a quarantine attribute | Delete it and reinstall with `install.sh`; never remove the quarantine attribute or override Gatekeeper |
| `--dest` does not exist (Linux) | The Linux installer does not create it | `mkdir -p` it first |
| `ripple: command not found` | Install directory not on `PATH` | Use the full path |
| Platform not in the table | No published build | Say so; no build, cross-compile or container workaround |
