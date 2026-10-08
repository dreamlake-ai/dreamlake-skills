# Install and authenticate

Install the standalone CLI, then authenticate and select the deployment:

```bash
curl -fsSL https://dl.dreamlake.ai/install.sh | bash
dreamlake init  # choose Codex or Claude Code and project/global scope
dreamlake login
dreamlake auth env list
```

Built-in deployments keep separate tokens. Check `dreamlake auth env --help` for
switching and custom deployment setup. Do not assume the active environment is
production. See [installation](../reference/installation.md) and
[environments](../reference/environments.md).

For scripts, use `dreamlake init --agent codex` or
`dreamlake skill install --agent claude --global`. Skills are bundled with the
CLI; updates remind you when installed copies differ. Review local edits before
using `--force`. See [agent skills](../reference/skills.md).
