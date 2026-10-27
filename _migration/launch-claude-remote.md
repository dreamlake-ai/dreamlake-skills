# Migration: launch-claude-remote (restructured in place)

| Source file / section | Destination |
|---|---|
| `SKILL.md` | `SKILL.md` — links repointed (`references/…` → `actions/…`, `scripts/` → `tools/`), `## Canonical source` added, two paragraphs tightened to stay ≤ 80 lines; substance unchanged |
| `references/remote-sessions.md` intro (upstream docs, review date, flag notes, bypass semantics, host/tmux lifetime) | `actions/remote-sessions.md` (git mv) |
| `remote-sessions.md` §Inspect and stop | `actions/remote-sessions.md` §Inspect and stop |
| `remote-sessions.md` §Another session in the same folder (Claude Code 2.1.293 refusal, interactive tmux launch) | `actions/remote-sessions.md` §Another session in the same folder |
| `remote-sessions.md` §Startup gaps (consent, ineligible help, tests description) | `actions/remote-sessions.md` §Startup gaps (test path now `tools/test_launch_remote.py`) |
| `remote-sessions.md` §Fresh-host prerequisites and manual gaps + §Service readiness after credential restore | `actions/fresh-host.md` (split out; text unchanged, subsection promoted to `##`) |
| `scripts/launch_remote.py` | `tools/launch_remote.py` (git mv; unchanged) |
| repo `scripts/test_launch_remote.py` | copied to `tools/test_launch_remote.py` with `SCRIPT = Path(__file__).resolve().parent / 'launch_remote.py'`; the root copy is owned by the tooling agent and must be deleted or repointed to `launch-claude-remote/tools/launch_remote.py` |
| `agents/openai.yaml` | `assets/agents/openai.yaml` (git mv; see report — Codex reads `agents/openai.yaml` at the skill root) |
| (new) | `skill.json`: `requires: []`, `docs: []`, `tools: {python >=3.8, packages: []}` |
