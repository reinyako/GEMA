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
    # statistik untuk layar hasil dan pencapaian
    play_time: float = 0.0
    run_time: float = 0.0
    light_time: float = 0.0
    pings: int = 0
    stones_thrown: int = 0
    walls_broken: int = 0
    distractions: int = 0     # Pendengar yang sedang memburu lalu teralihkan kerikil
    banished: int = 0         # Pengamat yang diusir dengan senter
    retries: int = 0          # Redup: berapa kali lantai diulang karena nyawa habis
    floor_retries: int = 0    # ...dan berapa kali di lantai yang sedang dimainkan
    recorded: bool = False    # statistik sudah dicatat ke data simpanan
    assisted: bool = False    # mode dev atau mulai dari tengah: tidak dapat pencapaian
    own_note: str = ""        # catatan yang ditulis pemain di ending sebelumnya

    def __post_init__(self):
        if self.lives < 0:
            self.lives = self.difficulty.lives
        if self.floor > 1:
            self.assisted = True

    def stress_floor(self):
        return min(C.STRESS_FLOOR_MAX, C.STRESS_FLOOR_PER_DEATH * self.deaths)
