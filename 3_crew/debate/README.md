# Debate Crew

Two debaters. One judge. Clear outputs. This project runs a structured debate with separate agents for the proposition and opposition, then a judge decides the winner — all powered by [crewAI](https://crewai.com).

## Installation

- Python: `>=3.10,<3.13`
- Package manager: [UV](https://docs.astral.sh/uv/)

Install UV (if needed):

```bash
pip install uv
```

Install project deps (optional via CLI helper):

```bash
crewai install
```

## Configuration

- API keys: add your `OPENAI_API_KEY` (and/or others) to `.env`.
- Agents: `src/debate/config/agents.yaml`
  - `proposer`: proposition debater (affirmative)
  - `opposer`: opposition debater (negative)
  - `judge`: neutral arbiter
- Tasks: `src/debate/config/tasks.yaml`

Each agent can use a different LLM via the `llm` field in `agents.yaml`, e.g.:

```yaml
llm: openai/gpt-4o-mini
```

You can also override models without editing YAML using env vars:

- `PROPOSER_LLM` — overrides proposer’s model
- `OPPOSER_LLM` — overrides opposer’s model
- `JUDGE_LLM` — overrides judge’s model

PowerShell example:

```powershell
$env:PROPOSER_LLM = "openai/gpt-4o"
$env:OPPOSER_LLM = "anthropic/claude-3-7-sonnet-latest"
$env:JUDGE_LLM   = "openai/o4-mini"
```

## Running

From the project root:

```bash
crewai run
```

Default motion is configured in `src/debate/main.py`. Outputs are written to:

- `output/propose.md` — affirmative case
- `output/oppose.md` — negative case
- `output/decide.md` — judge’s decision and rationale

## What’s improved

- Separate debaters with individual LLMs (`proposer`, `opposer`).
- Stronger role instructions and task prompts.
- Structured, concise markdown outputs for easy comparison.
- Optional env var overrides for per-agent models.

## Customize the motion

Edit the `inputs` in `src/debate/main.py` to change the debate motion. You can also wire this to CLI args if desired.

## Support

- Docs: https://docs.crewai.com
- GitHub: https://github.com/joaomdmoura/crewai
- Discord: https://discord.com/invite/X4JWnZnxPb

Have fun debating!
