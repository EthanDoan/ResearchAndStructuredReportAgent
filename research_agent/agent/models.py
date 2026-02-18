from dataclasses import dataclass
from typing import Optional


@dataclass
class Source:
    source_id: str
    url: str
    title: str
    text: str
    retrieved_at: str
    published_date: Optional[str] = None