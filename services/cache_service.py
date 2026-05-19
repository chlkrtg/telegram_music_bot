import asyncio
from functools import wraps
from datetime import datetime, timedelta


class SimpleCache:
    """Простой кэш в памяти"""

    def __init__(self, ttl_seconds=3600):
        self._cache = {}
        self._ttl = ttl_seconds

    def _make_key(self, func_name: str, args: tuple, kwargs: dict) -> str:
        """Создаёт ключ, игнорируя self (первый аргумент)"""
        # Убираем self если есть (args[0] - это self в методах класса)
        if args and hasattr(args[0], '__dict__'):
            clean_args = args[1:]
        else:
            clean_args = args

        # Сортируем kwargs
        sorted_kwargs = tuple(sorted(kwargs.items()))

        return f"{func_name}:{str(clean_args)}:{str(sorted_kwargs)}"

    def get(self, key: str):
        if key in self._cache:
            value, timestamp = self._cache[key]
            if datetime.now() - timestamp < timedelta(seconds=self._ttl):
                return value
            del self._cache[key]
        return None

    def set(self, key: str, value):
        self._cache[key] = (value, datetime.now())

    def clear(self):
        self._cache.clear()


def cached(ttl_seconds=3600):
    """Декоратор для кэширования (работает с async и sync функциями)"""

    def decorator(func):
        cache = SimpleCache(ttl_seconds)

        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            key = cache._make_key(func.__name__, args, kwargs)

            result = cache.get(key)
            if result is not None:
                print(f"[CACHE HIT] {func.__name__}")
                return result

            print(f"[CACHE MISS] {func.__name__}")
            result = await func(*args, **kwargs)
            cache.set(key, result)
            return result

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            key = cache._make_key(func.__name__, args, kwargs)

            result = cache.get(key)
            if result is not None:
                print(f"[CACHE HIT] {func.__name__}")
                return result

            print(f"[CACHE MISS] {func.__name__}")
            result = func(*args, **kwargs)
            cache.set(key, result)
            return result

        # Автоматически определяем тип функции
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper

    return decorator
