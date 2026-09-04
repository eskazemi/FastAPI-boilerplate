#key_maker.py
from abc import (
    ABC, 
    abstractmethod,
)
from typing import (
    Callable, 
    Any,
)

class BaseKeyMaker(ABC):
    @abstractmethod
    async def make(
        self,
        function: Callable[..., Any],
        prefix: str,
        *args: Any,
        **kwargs: Any,
    ) -> str:
        ...
