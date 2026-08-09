import inspect
from typing import Callable, Any
from shared.cache.base.key_maker import BaseKeyMaker

class CustomKeyMaker(BaseKeyMaker):
    async def make(self, function: Callable, prefix: str, *args: Any, **kwargs: Any) -> str:
        # ایجاد نام منحصر‌به‌فرد تابع
        module = inspect.getmodule(function).__name__
        func_name = function.__name__
        
        # تبدیل آرگومان‌ها به رشته جهت تشخیص در کلید کش
        args_repr = repr(args)
        kwargs_repr = repr(sorted(kwargs.items()))
        
        return f"{prefix}::{module}.{func_name}:{args_repr}:{kwargs_repr}"
