import hashlib
import logging
from functools import wraps
from typing import Type, TypeVar, Callable, Union, get_origin, get_args

import diskcache as dc
from pydantic import BaseModel, TypeAdapter

logger = logging.getLogger(__name__)

T = TypeVar("T")

cache = dc.Cache(".llm_cache", size_limit=2_000_000_000)


def get_schema_name(schema: Type[T]) -> str:
    if hasattr(schema, '__name__'):
        return schema.__name__
    return str(schema)


def create_cache_key(model: str, text: str, schema: Type[T]) -> str:
    schema_name = get_schema_name(schema)
    content_to_hash = f"{model}|{text}|{schema_name}"
    return hashlib.sha256(content_to_hash.encode()).hexdigest()


def disk_cache(func: Callable[..., T]) -> Callable[..., T]:
    @wraps(func)
    def wrapper(self, text: str, schema: Type[T]) -> T:
        schema_name = get_schema_name(schema)
        cache_key = create_cache_key(self.model, text, schema)
        cached_result = cache.get(cache_key)

        if cached_result is not None:
            logger.debug(f"🎯 Cache hit for {schema_name} - using cached response")
            try:
                origin = get_origin(schema)
                is_pydantic_type = False

                if (isinstance(schema, type) and issubclass(schema, BaseModel)):
                    is_pydantic_type = True
                elif origin is Union:
                    args = get_args(schema)
                    if args and all(isinstance(arg, type) and issubclass(arg, BaseModel) for arg in args if isinstance(arg, type)):
                        is_pydantic_type = True

                if is_pydantic_type:
                    adapter = TypeAdapter(schema)
                    return adapter.validate_python(cached_result)
                else:
                    return cached_result
                
            except Exception as e:
                logger.warning(
                    f"Failed to deserialize cached response: {e}. Making fresh API call."
                )
        else:
            logger.debug(f"🔄 Cache miss for {schema_name} - making API call")

        result: T = func(self, text, schema)

        try:
            if hasattr(result, "model_dump"):
                cache.set(cache_key, result.model_dump())
            else:
                cache.set(cache_key, result)

            logger.debug(f"💾 Cached {schema_name} response")
        except Exception as e:
            logger.warning(f"Failed to cache response: {e}")

        return result

    return wrapper
