from typing import List
from .models import Source
from .llm import llm_text
from .prompts import (
    PLANNER_SYSTEM,
    WRITER_SYSTEM,
    make_planner_user,
    make_writer_user,
)


def _format_sources_block(sources: List[Source]) -> str:
    if not sources:
        return "(no sources provided)"

    lines = []
    for s in sources:
        lines.append(f"[{s.source_id}] {s.title}\nURL: {s.url}\nText excerpt:\n{s.text}\n")
    return "\n---\n".join(lines)


def write_report(topic: str, audience: str, length: str, sources: List[Source], model: str) -> str:
    # 1) plan
    plan = llm_text(
        model=model,
        system=PLANNER_SYSTEM,
        user=make_planner_user(topic, audience, length),
    )

    # 2) write using plan + sources
    sources_block = _format_sources_block(sources)
    report = llm_text(
        model=model,
        system=WRITER_SYSTEM,
        user=make_writer_user(topic, audience, length, sources_block, plan),
    )

    return report