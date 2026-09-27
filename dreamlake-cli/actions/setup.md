# Install and authenticate

Install the standalone CLI, then authenticate and select the deployment:

```bash
curl -fsSL https://dl.dreamlake.ai/install.sh | bash
dreamlake login
dreamlake env list
```

Built-in deployments keep separate tokens. Check `dreamlake env --help` for
switching and custom deployment setup. Do not assume the active environment is
production. See [installation](../reference/installation.md) and
[environments](../reference/environments.md).
