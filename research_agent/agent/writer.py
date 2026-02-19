from typing import List

from .cache import CacheStore
from .llm import llm_json, llm_text
from .models import CriticResult, Note
from .prompts import (
    CRITIC_SYSTEM,
    PLANNER_SYSTEM,
    WRITER_SYSTEM,
    make_critic_user,
    make_planner_user,
    make_writer_user,
)


def build_plan(topic: str, audience: str, length: str, model: str, cache: CacheStore) -> str:
    key = f"plan::{topic}::{audience}::{length}"
    cached = cache.get("plan", key)
    if cached is not None:
        return cached.get("text", "")
    plan = llm_text(
        model=model,
        system=PLANNER_SYSTEM,
        user=make_planner_user(topic=topic, audience=audience, length=length),
    )
    cache.set("plan", key, {"text": plan})
    return plan


def write_report(topic: str, audience: str, length: str, plan: str, notes: List[Note], model: str) -> str:
    return llm_text(
        model=model,
        system=WRITER_SYSTEM,
        user=make_writer_user(topic=topic, audience=audience, length=length, plan=plan, notes=notes, has_sources=bool(notes)),
    )


def critic_report(topic: str, report_markdown: str, source_count: int, model: str, cache: CacheStore) -> CriticResult:
    key = f"review::{topic}::sources={source_count}::len={len(report_markdown)}"
    cached = cache.get("review", key)
    if cached is None:
        payload = llm_json(
            model=model,
            system=CRITIC_SYSTEM,
            user=make_critic_user(topic=topic, report_markdown=report_markdown, source_count=source_count),
        )
        cache.set("review", key, payload)
    else:
        payload = cached

    return CriticResult(
        passed=bool(payload.get("pass", False)),
        issues=[str(x) for x in payload.get("issues", [])],
        new_queries=[str(x) for x in payload.get("new_queries", [])],
    )
