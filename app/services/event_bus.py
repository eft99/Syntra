from dataclasses import dataclass, field
from typing import Callable, Dict, List


@dataclass
class EventBus:
    _listeners: Dict[str, List[Callable]] = field(default_factory=dict)

    def subscribe(self, event: str, handler: Callable):
        self._listeners.setdefault(event, []).append(handler)

    async def publish(self, event: str, payload: dict):
        for handler in self._listeners.get(event, []):
            await handler(payload)


bus = EventBus()
