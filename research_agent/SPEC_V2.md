

# Research + Structured Report Agent V2

## Overview

This project implements a Research + Structured Report Agent (V2) in Python.

The agent autonomously:
- Plans technical research
- Discovers sources using Serper.dev
- Fetches and extracts content
- Extracts grounded technical notes
- Writes an engineering design document in Markdown
- Verifies quality using a critic loop
- Exports Markdown + PDF
- Caches intermediate artifacts

Target audience: Senior / Staff-level software engineers.
Writing style: Deep technical engineer.

---

## Architecture (V2)

Pipeline:

1. Planner
2. Search (Serper.dev)
3. Fetch HTML
4. Extract Notes (LLM JSON)
5. Writer (Design Doc)
6. Critic (Quality Gate)
7. Optional iteration
8. Export (Markdown + PDF)

The writer must ONLY use extracted notes as factual grounding.

---

## CLI Interface

Main entry: main.py

Example:

```
python main.py \
  --topic "Agentic AI architecture for mobile apps" \
  --audience "Senior iOS developers" \
  --search \
  --max-sources 8 \
  --iterations 2 \
  --outdir outputs
```

### CLI Flags

Required:
- --topic

Optional:
- --audience (default: Senior software engineers)
- --length (short|medium|long)
- --search (enable Serper search)
- --max-sources (default: 8)
- --iterations (default: 2)
- --urls (comma separated extra URLs)
- --outdir (default: outputs)
- --model (default: gpt-5)
- --no-cache (disable caching)

---

## Environment Variables

Required:

```
OPENAI_API_KEY=...
SERPER_API_KEY=...
```

---

## Required Sections in Final Report

The generated Markdown must contain ALL sections:

- TL;DR
- Problem
- Goals / Non-Goals
- Background / Constraints
- Proposed Design
- Data / Interfaces
- Failure Modes & Edge Cases
- Performance & Cost
- Security & Privacy
- Observability
- Testing Plan
- Rollout Plan
- Alternatives Considered
- Open Questions
- References

If sources are provided:
- All technical claims must include citations [S#]

If no sources:
- Must include "Assumptions & Limitations"

---

## Notes Extraction Rules

Each source is converted into atomic notes.

Note schema:

```
{
  "claim": "string",
  "support": "string",
  "tags": ["performance|security|api|architecture|testing|cost|other"],
  "confidence": "low|medium|high"
}
```

Notes must:
- Be grounded in the provided source text
- Avoid outside knowledge
- Prefer technical specifics (limits, APIs, constraints, trade-offs)

---

## Critic Rules

The critic must:

- Fail if required sections are missing
- Fail if uncited technical claims appear
- Fail if key engineering aspects are missing
- Suggest new search queries if evidence is weak

Output format:

```
{
  "pass": true|false,
  "issues": ["..."],
  "new_queries": ["..."]
}
```

---

## Caching

Cache location:

```
outputs/cache/
```

Namespaces:
- plan
- serper
- fetch
- notes
- review

Cache key format example:

```
plan::<topic>::<audience>::<length>
serper::<query>::num=10
fetch::<url>
notes::<url>::<model>
```

---

## Acceptance Criteria (Definition of Done)

The implementation is complete when:

1. Running the CLI produces:
   - outputs/report.md
   - outputs/report.pdf
2. Search works when --search is enabled
3. Notes extraction produces JSON-grounded notes
4. Writer only uses notes (not raw HTML)
5. Critic loop runs and can trigger second iteration
6. No runtime exceptions occur in normal flow

---

## Non-Goals (V2)

- No vector database
- No embeddings
- No multi-model orchestration
- No UI
- No advanced PDF rendering (basic ReportLab only)

---

## Future Improvements (V3+)

- Vector store + semantic retrieval
- Domain scoring (prefer official docs / GitHub)
- HTML → readability/trafilatura extraction
- Structured JSON design-doc output
- Evaluation metrics (coverage, citation density)
- Web UI

---

## Developer Notes

Python version: 3.10+

Install:

```
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Smoke test:

```
python main.py --topic "Test report" --search --max-sources 3 --iterations 1
```

Expected result:
- Markdown design document
- PDF export
- Cache populated

---

END OF SPEC