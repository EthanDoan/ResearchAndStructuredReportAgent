import hashlib
import json
from pathlib import Path
from typing import Any, Optional

from .log import get_logger


logger = get_logger(__name__)


class CacheStore:
    def __init__(self, outdir: Path, enabled: bool = True):
        self.enabled = enabled
        self.base_dir = Path(outdir) / "cache"
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def _path_for_key(self, namespace: str, key: str) -> Path:
        digest = hashlib.sha256(key.encode("utf-8")).hexdigest()
        ns_dir = self.base_dir / namespace
        ns_dir.mkdir(parents=True, exist_ok=True)
        return ns_dir / f"{digest}.json"

    def get(self, namespace: str, key: str) -> Optional[Any]:
        if not self.enabled:
            return None
        path = self._path_for_key(namespace, key)
        if not path.exists():
            logger.debug("Cache miss namespace=%s key=%s", namespace, key)
            return None
        payload = json.loads(path.read_text(encoding="utf-8"))
        logger.debug("Cache hit namespace=%s key=%s", namespace, key)
        return payload.get("value")

    def set(self, namespace: str, key: str, value: Any) -> None:
        if not self.enabled:
            return
        path = self._path_for_key(namespace, key)
        payload = {"cache_key": key, "value": value}
        path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
        logger.debug("Cache store namespace=%s key=%s", namespace, key)
