#!/usr/bin/env python3
"""Start or inspect one persistent Claude Remote Control terminal (POSIX)."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shlex
import shutil
import subprocess
import sys
import time


def run(argv, *, check=True, cwd=None):
    result = subprocess.run(argv, text=True, capture_output=True, timeout=20, cwd=cwd)
    if check and result.returncode:
        raise RuntimeError((result.stderr or result.stdout).strip() or f"Command failed: {argv[0]}")
    return result


def claude_binary():
    found = shutil.which("claude")
    native = Path.home() / ".local/bin/claude"
    if found:
        return found
    if native.is_file() and os.access(native, os.X_OK):
        return str(native)
    raise RuntimeError("Missing dependency: claude")


def probe(cwd):
    executable = claude_binary()
    if not shutil.which("tmux"):
        raise RuntimeError("Missing dependency: tmux")
    version = run([executable, "--version"], cwd=cwd).stdout.strip()
    help_text = run([executable, "remote-control", "--help"], cwd=cwd).stdout
    for flag in ("--name", "--spawn", "--permission-mode"):
        if flag not in help_text:
            raise RuntimeError(f"Installed Claude Remote Control lacks {flag}; inspect its help.")
    return version


def launch(args):
    cwd = str(Path(args.cwd).expanduser().resolve(strict=True))
    if not Path(cwd).is_dir():
        raise ValueError("--cwd must be a directory")
    if not args.name.strip() or any(ord(c) < 32 or ord(c) == 127 for c in args.name):
        raise ValueError("--name must be nonempty and contain no control characters")
    if "https://claude.ai/code/" in args.name:
        raise ValueError("Use a title without a session URL so it cannot be mistaken for registration output")
    if not 0 < args.timeout <= 120:
        raise ValueError("--timeout must be greater than zero and at most 120 seconds")
    if args.check:
        return {"status": "checked", "version": probe(cwd), "cwd": cwd}, 0
    if not shutil.which("tmux"):
        raise RuntimeError("Missing dependency: tmux")
    key = hashlib.sha256(json.dumps([cwd, args.name]).encode()).hexdigest()[:20]
    session = f"claude-remote-{key}"
    target = session
    pane_target = target + ":remote"
    command = ["claude", "remote-control", "--name", args.name, "--spawn", "session",
               "--permission-mode", args.permission_mode]
    signature = json.dumps([cwd, command])
    exists = run(["tmux", "has-session", "-t", target], check=False).returncode == 0
    if exists:
        previous = run(["tmux", "show-options", "-qv", "-t", target,
                        "@claude-remote-launch"], check=False).stdout.strip()
        if previous != signature:
            raise RuntimeError(f"Existing {session} has different or unknown launch settings; inspect it.")
    else:
        probe(cwd)
        # Start a known shell; quote every value before sending the single command.
        # Configure retention before exec so even immediate startup errors survive.
        run(["tmux", "new-session", "-d", "-s", session, "-n", "remote", "-c", cwd,
             "-e", "PATH=" + os.environ.get("PATH", ""),
             "-x", "240", "-y", "50", "/bin/sh"])
        run(["tmux", "set-option", "-w", "-t", pane_target, "remain-on-exit", "on"])
        run(["tmux", "set-option", "-t", target, "@claude-remote-launch", signature])
        executable_command = [claude_binary(), *command[1:]]
        run(["tmux", "send-keys", "-t", pane_target, "-l", "exec " + shlex.join(executable_command)])
        run(["tmux", "send-keys", "-t", pane_target, "Enter"])
    result = {"name": args.name, "cwd": cwd, "permission_mode_requested": args.permission_mode,
              "tmux_session": session, "reused": exists,
              "attach_command": shlex.join(["tmux", "attach-session", "-t", target])}
    deadline = time.monotonic() + args.timeout
    while True:
        pane = run(["tmux", "capture-pane", "-p", "-J", "-t", pane_target, "-S", "-1000"]).stdout
        dead = run(["tmux", "display-message", "-p", "-t", pane_target, "#{pane_dead}"]).stdout.strip()
        if dead == "1":
            return dict(result, status="exited", detail="Inspect the retained tmux pane before retrying."), 1
        match = re.search(r"https://claude\.ai/code/[A-Za-z0-9_-]+(?:\?[^\s\x1b<>\"']+)?", pane)
        if match:
            return dict(result, status="registered", url=match.group(0)), 0
        if time.monotonic() >= deadline:
            return dict(result, status="pending", detail="No session URL yet; inspect the pane for consent, login, or connection errors. Re-run with the same arguments."), 2
        time.sleep(0.25)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cwd", default=str(Path.cwd()))
    parser.add_argument("--name", default="Remote workspace")
    parser.add_argument("--permission-mode", default="bypassPermissions",
                        choices=("bypassPermissions", "default", "acceptEdits", "plan"))
    parser.add_argument("--timeout", type=float, default=45)
    parser.add_argument("--check", action="store_true", help="Probe CLI support without creating a session")
    args = parser.parse_args()
    try:
        result, code = launch(args)
    except (OSError, ValueError, RuntimeError, subprocess.TimeoutExpired) as exc:
        result, code = {"status": "error", "detail": str(exc)}, 1
    print(json.dumps(result, indent=2))
    return code


if __name__ == "__main__":
    sys.exit(main())
