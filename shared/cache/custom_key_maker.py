#custom_key_maker.py
import inspect
from typing import Any, Callable

from shared.cache.base.key_maker import BaseKeyMaker


class CustomKeyMaker(BaseKeyMaker):
    async def make(
        self,
        function: Callable[..., Any],
        prefix: str,
        *args: Any,
        **kwargs: Any,
    ) -> str:
        module = inspect.getmodule(function)
        module_name = module.__name__ if module is not None else "__main__"

        func_name = getattr(
            function,
            "__name__",
            function.__class__.__name__,
        )

        args_repr = repr(args)
        kwargs_repr = repr(sorted(kwargs.items()))

        return f"{prefix}::{module_name}.{func_name}:{args_repr}:{kwargs_repr}"