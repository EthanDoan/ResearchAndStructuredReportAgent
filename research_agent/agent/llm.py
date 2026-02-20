import json
from openai import OpenAI

from .log import get_logger

_client = None
logger = get_logger(__name__)


def get_client() -> OpenAI:
    global _client
    if _client is None:
        _client = OpenAI()
    return _client


def llm_text(model: str, system: str, user: str) -> str:
    client = get_client()
    request_payload = {
        "model": model,
        "input": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
    }
    logger.info("LLM text request model=%s", model)
    logger.info("LLM request payload=%s", request_payload)
    resp = client.responses.create(**request_payload)
    return resp.output_text


def llm_json(model: str, system: str, user: str) -> dict:
    logger.info("LLM JSON request model=%s", model)
    text = llm_text(model=model, system=system, user=user)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # Best-effort fallback for markdown fenced JSON
        cleaned = text.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        return json.loads(cleaned)
