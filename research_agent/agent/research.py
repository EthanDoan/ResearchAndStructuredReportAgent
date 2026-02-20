import datetime as dt
import os
import re
from typing import List

import requests
from bs4 import BeautifulSoup

from .cache import CacheStore
from .log import get_logger
from .llm import llm_json
from .models import Note, Source
from .prompts import NOTES_SYSTEM, make_notes_user


logger = get_logger(__name__)


def _slug_id(i: int) -> str:
    return f"S{i}"


def _clean_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def plan_cache_key(topic: str, audience: str, length: str) -> str:
    return f"plan::{topic}::{audience}::{length}"


def search_serper(queries: List[str], max_sources: int, cache: CacheStore) -> List[str]:
    if not queries:
        return []
    api_key = os.getenv("SERPER_API_KEY")
    if not api_key:
        raise RuntimeError("Missing SERPER_API_KEY while --search is enabled.")

    urls: List[str] = []
    seen = set()

    logger.info("Searching with Serper across %d query(s)", len(queries))

    for q in queries:
        key = f"serper::{q}::num=10"
        cached = cache.get("serper", key)
        logger.info("Serper query: %s (%s)", q, "cache" if cached is not None else "live")
        if cached is None:
            resp = requests.post(
                "https://google.serper.dev/search",
                headers={"X-API-KEY": api_key, "Content-Type": "application/json"},
                json={"q": q, "num": 10},
                timeout=25,
            )
            resp.raise_for_status()
            data = resp.json()
            cache.set("serper", key, data)
        else:
            data = cached

        for item in data.get("organic", []):
            link = item.get("link")
            if not link or link in seen:
                continue
            seen.add(link)
            urls.append(link)
            if len(urls) >= max_sources:
                return urls

    return urls


def fetch_sources(urls: List[str], cache: CacheStore) -> List[Source]:
    sources: List[Source] = []
    now = dt.datetime.utcnow().isoformat() + "Z"

    logger.info("Fetching %d URL(s)", len(urls))

    for idx, url in enumerate(urls, start=1):
        try:
            key = f"fetch::{url}"
            cached = cache.get("fetch", key)
            logger.info("Fetch source %s (%s)", url, "cache" if cached is not None else "live")
            if cached is None:
                r = requests.get(url, timeout=20, headers={"User-Agent": "Mozilla/5.0"})
                r.raise_for_status()
                html = r.text
                cache.set("fetch", key, {"html": html})
            else:
                html = cached.get("html", "")

            soup = BeautifulSoup(html, "html.parser")
            title = soup.title.get_text(strip=True) if soup.title else url
            for tag in soup(["script", "style", "noscript"]):
                tag.decompose()
            text = _clean_text(soup.get_text(" ", strip=True))[:12000]

            sources.append(Source(source_id=_slug_id(idx), url=url, title=title, text=text, retrieved_at=now))
        except Exception as e:
            logger.warning("Failed to fetch source %s: %s", url, e)
            sources.append(
                Source(
                    source_id=_slug_id(idx),
                    url=url,
                    title=f"(Failed to fetch) {url}",
                    text=f"ERROR: {type(e).__name__}: {e}",
                    retrieved_at=now,
                )
            )
    return sources


def extract_notes(sources: List[Source], model: str, cache: CacheStore) -> List[Note]:
    notes: List[Note] = []
    logger.info("Extracting notes from %d source(s)", len(sources))
    for source in sources:
        key = f"notes::{source.url}::{model}"
        cached = cache.get("notes", key)
        logger.info("Notes for %s (%s)", source.url, "cache" if cached is not None else "llm")
        if cached is None:
            payload = llm_json(model=model, system=NOTES_SYSTEM, user=make_notes_user(source))
            cache.set("notes", key, payload)
        else:
            payload = cached

        for item in payload.get("notes", []):
            claim = item.get("claim", "").strip()
            support = item.get("support", "").strip()
            tags = item.get("tags") or ["other"]
            confidence = item.get("confidence", "low")
            if not claim:
                continue
            notes.append(
                Note(
                    claim=claim,
                    support=support,
                    tags=tags,
                    confidence=confidence,
                    source_id=source.source_id,
                    url=source.url,
                )
            )
    return notes
