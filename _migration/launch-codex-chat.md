# Migration: launch-codex-chat (restructured in place)

| Source file / section | Destination |
|---|---|
| `SKILL.md` | `SKILL.md` — links repointed (`references/…` → `actions/…`, `scripts/` → `tools/`), `## Canonical source` added; substance unchanged |
| `references/launching-chats.md` intro + §What the successful flow did + §Commands | `actions/launching-chats.md` (git mv; `scripts/` → `tools/` in commands) |
| `launching-chats.md` §Fresh-host prerequisites and manual gaps + §Service readiness after credential restore | `actions/fresh-host.md` (split out; text unchanged, subsection promoted to `##`) |
| `launching-chats.md` §Pairing codes and desktop registration | `actions/pairing.md` (split out; text unchanged) |
| `launching-chats.md` §Sources (four learn.chatgpt.com pages) | `actions/launching-chats.md` §Sources |
| `scripts/launch_chat.py` | `tools/launch_chat.py` (git mv; unchanged) |
| repo `scripts/test_launch_chat.py` | copied to `tools/test_launch_chat.py` loading `Path(__file__).resolve().parent / 'launch_chat.py'`; the root copy is owned by the tooling agent and must be deleted or repointed to `launch-codex-chat/tools/launch_chat.py` |
| `agents/openai.yaml` | `assets/agents/openai.yaml` (git mv; see report — Codex reads `agents/openai.yaml` at the skill root) |
| (new) | `skill.json`: `requires: []`, `docs: []`, `tools: {python >=3.8, packages: []}` |
