from dataclasses import dataclass

@dataclass(frozen=True)
class WorkflowStep:
    name: str
    retries: int = 1

class WorkflowDefinition:
    def __init__(self, steps: list[WorkflowStep]):
        self.steps = steps

    def names(self) -> list[str]:
        return [step.name for step in self.steps]
