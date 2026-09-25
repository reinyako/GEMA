"""Status satu run (satu percobaan dari Lantai 1 sampai ending atau nyawa habis)."""

from dataclasses import dataclass, field

from . import config as C


@dataclass
class Run:
    difficulty: C.Difficulty
    seed: int
    attempt: int
    floor: int = 1
    lives: int = -1
    battery: float = C.BATTERY_MAX
    deaths: int = 0
    notes: list = field(default_factory=list)

    def __post_init__(self):
        if self.lives < 0:
            self.lives = self.difficulty.lives

    def stress_floor(self):
        return min(C.STRESS_FLOOR_MAX, C.STRESS_FLOOR_PER_DEATH * self.deaths)
