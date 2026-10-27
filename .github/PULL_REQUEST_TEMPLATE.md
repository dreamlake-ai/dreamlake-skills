## What changed

<!-- one of: task step / exception · product fact (link the docs-site PR instead) · new skill · rename, merge or split -->

- Skill(s):
- Kind of change:
- Why:

## Checks

```
python3 scripts/check.py --offline
python3 -m unittest discover -s scripts -p 'test_*.py'
```

<!-- paste both outputs -->

## Acceptance (CONTRIBUTING.md > Acceptance before merge)

| Request | Claude Code | Codex |
|---|---|---|
| representative task | | |
| SDK-only request | | |
| unsupported capability | | |

## Reviewer checklist

- [ ] Step or exception here, fact on the docs site; nothing patched into an action
- [ ] No hand edits under any `reference/`; `references.lock` and `catalog.json` regenerated if `docs[]` or `skill.json` changed
- [ ] Flag semantics link into `../reference/<page>.md#<heading>`; links are file-relative and stay inside the skill; other skills are named
- [ ] `requires` closure and `renamed.json` correct
- [ ] Files moved or retired: note under `docs/migration-<topic>/`
- [ ] Size caps respected or the skill was split (CONTRIBUTING.md > Maintain an existing skill > Size caps)
- [ ] Acceptance results pasted for both agents
- [ ] Nothing private or operational: this repository and its releases are public
