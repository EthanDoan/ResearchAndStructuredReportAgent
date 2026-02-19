import json
from openai import OpenAI

_client = None


def get_client() -> OpenAI:
    global _client
    if _client is None:
        _client = OpenAI()
    return _client


def llm_text(model: str, system: str, user: str) -> str:
    client = get_client()
    resp = client.responses.create(
        model=model,
        input=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
    )
    return resp.output_text


def llm_json(model: str, system: str, user: str) -> dict:
    text = llm_text(model=model, system=system, user=user)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # Best-effort fallback for markdown fenced JSON
        cleaned = text.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        return json.loads(cleaned)
