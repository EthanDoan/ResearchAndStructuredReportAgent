from typing import List

from .models import Note, Source

PLANNER_SYSTEM = """You are a research planner for engineering design documents.
Return concise, actionable research plans in plain markdown."""

NOTES_SYSTEM = """You extract grounded technical notes from one source.
Rules:
- Use ONLY provided source content.
- No outside facts.
- Prefer concrete details (limits, APIs, constraints, trade-offs).
- Output strict JSON object: {\"notes\": [ ... ]}
Each note schema:
{
  \"claim\": \"string\",
  \"support\": \"string\",
  \"tags\": [\"performance|security|api|architecture|testing|cost|other\"],
  \"confidence\": \"low|medium|high\"
}
"""

WRITER_SYSTEM = """You write senior-level engineering design docs in Markdown.
Hard rules:
- Use ONLY provided notes as factual grounding.
- Do not use raw source text or outside knowledge.
- If sources exist, technical claims must include citations [S#].
- Include exactly these sections:
  TL;DR
  Problem
  Goals / Non-Goals
  Background / Constraints
  Proposed Design
  Data / Interfaces
  Failure Modes & Edge Cases
  Performance & Cost
  Security & Privacy
  Observability
  Testing Plan
  Rollout Plan
  Alternatives Considered
  Open Questions
  References
- If no sources are provided, add section: Assumptions & Limitations.
"""

CRITIC_SYSTEM = """You are a strict report critic.
Return JSON exactly:
{
  \"pass\": true|false,
  \"issues\": [\"...\"],
  \"new_queries\": [\"...\"]
}
Fail when:
- required sections missing
- uncited technical claims when sources are present
- key engineering aspects missing
- evidence weak
"""


def make_planner_user(topic: str, audience: str, length: str) -> str:
    return f"""Topic: {topic}
Audience: {audience}
Length: {length}

Produce:
1) Report outline aligned to required sections
2) 6-10 research questions
3) 6-10 concrete web queries for Serper search
"""


def make_notes_user(source: Source) -> str:
    return f"""Source ID: {source.source_id}
URL: {source.url}
Title: {source.title}

Source text:
{source.text[:12000]}
"""


def make_writer_user(topic: str, audience: str, length: str, plan: str, notes: List[Note], has_sources: bool) -> str:
    notes_block = "\n".join(
        [
            f"[{n.source_id}] claim={n.claim}\nsupport={n.support}\ntags={','.join(n.tags)}\nconfidence={n.confidence}"
            for n in notes
        ]
    )
    return f"""Topic: {topic}
Audience: {audience}
Length: {length}
Sources available: {has_sources}

Planner output:
{plan}

Extracted notes (only allowed evidence):
{notes_block if notes_block else '(none)'}
"""


def make_critic_user(topic: str, report_markdown: str, source_count: int) -> str:
    return f"""Topic: {topic}
Source count: {source_count}

Report Markdown:
{report_markdown}
"""
