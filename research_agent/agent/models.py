from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Source:
    source_id: str
    url: str
    title: str
    text: str
    retrieved_at: str
    published_date: Optional[str] = None


@dataclass
class Note:
    claim: str
    support: str
    tags: List[str]
    confidence: str
    source_id: str
    url: str


@dataclass
class CriticResult:
    passed: bool
    issues: List[str]
    new_queries: List[str]
