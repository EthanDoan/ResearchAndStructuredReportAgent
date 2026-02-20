from typing import List

from .cache import CacheStore
from .log import get_logger
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


logger = get_logger(__name__)


def build_plan(topic: str, audience: str, length: str, model: str, cache: CacheStore) -> str:
    key = f"plan::{topic}::{audience}::{length}"
    cached = cache.get("plan", key)
    logger.info("Build plan (%s)", "cache" if cached is not None else "llm")
    if cached is not None:
        return cached.get("text", "")
    planner_user = make_planner_user(topic=topic, audience=audience, length=length)
    logger.info("make_planner_user() output=%s", planner_user)
    plan = llm_text(
        model=model,
        system=PLANNER_SYSTEM,
        user=planner_user,
    )
    cache.set("plan", key, {"text": plan})
    return plan


def write_report(topic: str, audience: str, length: str, plan: str, notes: List[Note], model: str) -> str:
    logger.info("Writing report with %d note(s)", len(notes))
    writer_user = make_writer_user(topic=topic, audience=audience, length=length, plan=plan, notes=notes, has_sources=bool(notes))
    logger.info("make_writer_user() output=%s", writer_user)
    return llm_text(
        model=model,
        system=WRITER_SYSTEM,
        user=writer_user,
    )


def critic_report(topic: str, report_markdown: str, source_count: int, model: str, cache: CacheStore) -> CriticResult:
    key = f"review::{topic}::sources={source_count}::len={len(report_markdown)}"
    cached = cache.get("review", key)
    logger.info("Critic review (%s)", "cache" if cached is not None else "llm")
    if cached is None:
        critic_user = make_critic_user(topic=topic, report_markdown=report_markdown, source_count=source_count)
        logger.info("make_critic_user() output=%s", critic_user)
        payload = llm_json(
            model=model,
            system=CRITIC_SYSTEM,
            user=critic_user,
        )
        cache.set("review", key, payload)
    else:
        payload = cached

    return CriticResult(
        passed=bool(payload.get("pass", False)),
        issues=[str(x) for x in payload.get("issues", [])],
        new_queries=[str(x) for x in payload.get("new_queries", [])],
    )
