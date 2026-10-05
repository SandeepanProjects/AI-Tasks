from dataclasses import dataclass, field
from typing import Any

@dataclass
class Checkpoint:
    workflow_id: str
    state: dict[str, Any] = field(default_factory=dict)
    paused: bool = False
    resume_token: str | None = None

class InMemoryCheckpointStore:
    def __init__(self):
        self._items = {}

    async def save(self, checkpoint: Checkpoint) -> None:
        self._items[checkpoint.workflow_id] = checkpoint

    async def load(self, workflow_id: str):
        return self._items.get(workflow_id)
