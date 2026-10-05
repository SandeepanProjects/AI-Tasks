from dataclasses import dataclass, field
from time import perf_counter

@dataclass
class Timer:
    name: str
    started: float = field(default_factory=perf_counter)

    def elapsed_ms(self) -> float:
        return (perf_counter() - self.started) * 1000
