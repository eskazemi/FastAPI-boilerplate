from functools import wraps
from shared.cache.base.backend import BaseBackend
from shared.cache.base.key_maker import BaseKeyMaker
from shared.cache.cache_tag import CacheTag

class CacheManager:
    def __init__(self):
        self._backend: BaseBackend | None = None
        self._key_maker: BaseKeyMaker | None = None

    def init(self, backend: BaseBackend, key_maker: BaseKeyMaker) -> None:
        self._backend = backend
        self._key_maker = key_maker

    def cached(self, prefix: str | None = None, tag: CacheTag | None = None, ttl: int = 60):
        def _cached(function):
            @wraps(function)
            async def __cached(*args, **kwargs):
                if not self._backend or not self._key_maker:
                    # اگر در تست هستیم یا تنظیم نشده، کش را دور می‌زنیم (Fail-safe)
                    return await function(*args, **kwargs)

                key = await self._key_maker.make(
                    function=function,
                    prefix=prefix or (tag.value if tag else "default"),
                    *args, **kwargs
                )
                
                cached_response = await self._backend.get(key=key)
                if cached_response is not None:
                    return cached_response

                response = await function(*args, **kwargs)
                await self._backend.set(response=response, key=key, ttl=ttl)
                return response

            return __cached
        return _cached

    async def remove_by_tag(self, tag: CacheTag) -> None:
        if self._backend:
            await self._backend.delete_startswith(value=tag.value)

Cache = CacheManager()
