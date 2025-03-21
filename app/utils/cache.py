from cachetools import TTLCache
from typing import Any

_cache = TTLCache(
    maxsize=1024,
    ttl=15
)


def set_cache(key: str, value: Any) -> None:
    _cache[key] = value


def read_cache(key: str) -> Any:
    if key not in _cache:
        return None

    return _cache[key]


__all__ = ['set_cache', 'read_cache']
