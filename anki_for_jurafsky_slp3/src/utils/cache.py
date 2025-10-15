import hashlib
import logging
from functools import wraps
from typing import Any, Callable, Tuple, Type, TypeVar, Union

import diskcache as dc
from pydantic import BaseModel

logger = logging.getLogger(__name__)

T = TypeVar("T")

cache = dc.Cache(".llm_cache", size_limit=1_000_000_000)


def get_cache_stats() -> dict:
    try:
        cache_size_mb = (
            sum(cache.volume().values()) / (1024 * 1024) if cache.volume() else 0
        )
        return {
            "cache_items": getattr(cache, "size", 0),
            "cache_size_mb": round(cache_size_mb, 1),
            "cache_directory": cache.directory,
        }
    except Exception as e:
        logger.warning(f"Failed to get cache stats: {e}")
        return {"error": str(e)}


def create_cache_key(model: str, text: str, schema: Type[T]) -> str:
    content_to_hash = f"{model}|{text}|{schema.__name__}"
    return hashlib.sha256(content_to_hash.encode()).hexdigest()


def disk_cache(func: Callable[..., Tuple[T, float]]) -> Callable[..., Tuple[T, float]]:
    @wraps(func)
    def wrapper(self, text: str, schema: Type[T]) -> Tuple[T, float]:
        cache_key = create_cache_key(self.model, text, schema)
        cached_result = cache.get(cache_key)

        if cached_result is not None:
            logger.debug(f"🎯 Cache hit for {schema.__name__} - using cached response")
            try:
                response_data = cached_result["response"]
                cached_api_latency = cached_result["api_latency"]
                
                if issubclass(schema, BaseModel):
                    return schema(**response_data), cached_api_latency
                else:
                    return response_data, cached_api_latency
            except Exception as e:
                logger.warning(
                    f"Failed to deserialize cached response: {e}. Making fresh API call."
                )
        else:
            logger.debug(f"🔄 Cache miss for {schema.__name__} - making API call")

        result, api_latency = func(self, text, schema)

        try:
            if hasattr(result, 'model_dump'):
                cache_data = {"response": result.model_dump(), "api_latency": api_latency}
            else:
                cache_data = {"response": result, "api_latency": api_latency}
            
            cache.set(cache_key, cache_data)
            logger.debug(
                f"💾 Cached {schema.__name__} response with API latency {api_latency:.3f}s"
            )
        except Exception as e:
            logger.warning(f"Failed to cache response: {e}")

        return result, api_latency

    return wrapper