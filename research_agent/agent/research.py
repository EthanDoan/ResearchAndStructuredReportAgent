import datetime as dt
import re
import requests
from bs4 import BeautifulSoup
from typing import List
from .models import Source


def _slug_id(i: int) -> str:
    return f"S{i}"


def _clean_text(text: str) -> str:
    text = re.sub(r"\s+", " ", text).strip()
    return text


def fetch_sources(urls: List[str]) -> List[Source]:
    """
    V1 research = fetch and extract readable text from user-provided URLs.
    If urls is empty, returns [] (offline mode).
    """
    sources: List[Source] = []
    now = dt.datetime.utcnow().isoformat() + "Z"

    for idx, url in enumerate(urls, start=1):
        try:
            r = requests.get(url, timeout=20, headers={"User-Agent": "Mozilla/5.0"})
            r.raise_for_status()
            html = r.text
            soup = BeautifulSoup(html, "html.parser")

            # title
            title = soup.title.get_text(strip=True) if soup.title else url

            # remove scripts/styles
            for tag in soup(["script", "style", "noscript"]):
                tag.decompose()

            text = soup.get_text(" ", strip=True)
            text = _clean_text(text)

            # keep it bounded so prompts don’t explode
            text = text[:12000]

            sources.append(
                Source(
                    source_id=_slug_id(idx),
                    url=url,
                    title=title,
                    text=text,
                    retrieved_at=now,
                    published_date=None,
                )
            )
        except Exception as e:
            # keep going; include a stub so user sees what failed
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