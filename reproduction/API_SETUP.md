# LLM API setup for PVBench

Do not paste API keys into chat or commit them to Git. Create `.env` in the
repository root; the repository's `.gitignore` already ignores this file.

```dotenv
OPENAI_API_KEY=replace-with-your-openai-project-key
ANTHROPIC_API_KEY=replace-with-your-anthropic-key
LITELLM_MASTER_KEY=replace-with-a-long-random-local-secret
```

`LITELLM_MASTER_KEY` is a local password chosen for this benchmark's LiteLLM proxy, not another provider key. Generate one locally if desired:

```bash
openssl rand -hex 32
```

After saving the file, restrict its permissions:

```bash
chmod 600 .env
```

PVBench currently requests `gpt-4.1` and `claude-4-sonnet`, so the provider accounts behind those keys must have access to those model names. PatchAgent talks to the local LiteLLM proxy using `LITELLM_MASTER_KEY`; San2Patch and generated-test jobs receive the provider keys directly from Compose.

Start LiteLLM explicitly because the repository's `full` profile does not select the `litellm` service:

```bash
docker compose --profile litellm up -d litellm-postgres litellm
```

Before any paid benchmark run, verify only that the variables are present (never print their values), start the proxy, and run one case. Do not launch the full 4,180-run matrix on this host without an explicit time and spend budget.
