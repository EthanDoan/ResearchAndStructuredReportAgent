# Research and Structured Report Agent

## API key setup (safe)

Do **not** commit real API keys to git (`.env`, `.env.example`, or source files).
GitHub push protection will block commits containing live secrets.

Use this pattern instead:

1. Keep `.env` local-only (already ignored by `.gitignore`).
2. Keep `research_agent/.env.example` with placeholders only.
3. Inject `OPENAI_API_KEY` at runtime via environment variables in CI/CD or hosting platform secrets.

Example local `.env` (not committed):

```env
OPENAI_API_KEY=your_real_key_here
```

Example committed `research_agent/.env.example`:

```env
OPENAI_API_KEY=your_openai_api_key_here
```

### Runtime injection options

- **Shell/session**
  - `export OPENAI_API_KEY=...`
  - `python research_agent/main.py`
- **GitHub Actions**
  - Store key in repo/org secret `OPENAI_API_KEY`
  - Pass as env in workflow job/step.
- **Docker/Kubernetes**
  - Use `--env OPENAI_API_KEY=...`, env files outside git, or Kubernetes Secrets.
- **PaaS (Render/Railway/Fly/Heroku, etc.)**
  - Add `OPENAI_API_KEY` in project Secret/Environment settings.

## Secret already committed?

If a real key was ever committed, do all of the following:

1. Revoke/rotate the leaked key in OpenAI dashboard.
2. Remove it from files and commit.
3. Rewrite git history to purge it (for example with `git filter-repo` or BFG).
4. Force-push cleaned history and ask collaborators to re-clone.
