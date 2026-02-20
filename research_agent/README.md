# Research + Structured Report Agent (V2)

## Setup

```bash
cd research_agent
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Set:
- `OPENAI_API_KEY`
- `SERPER_API_KEY` (required when `--search` is used)

## CLI

```bash
python main.py \
  --topic "Agentic AI architecture for mobile apps" \
  --audience "Senior iOS developers" \
  --search \
  --max-sources 8 \
  --iterations 2 \
  --outdir outputs
```

Outputs:
- `outputs/report.md`
- `outputs/report.pdf`
- `outputs/cache/*` (unless `--no-cache`)
