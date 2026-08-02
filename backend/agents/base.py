"""Base agent utilities."""

from abc import ABC, abstractmethod
from typing import Any, Dict


class BaseAgent(ABC):
    name: str = "base"

    @abstractmethod
    async def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError
