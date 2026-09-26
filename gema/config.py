"""Semua angka tuning GEMA.

Ubah angka di sini, bukan di modul lain. Semua nilai adalah nilai awal dari
docs/GDD.md dan akan disetel ulang setelah playtest.
"""

import math
from dataclasses import dataclass

from . import lang

# --- Layar ---------------------------------------------------------------
SCREEN_W = 960
SCREEN_H = 540
FPS = 60
MAX_DT = 0.05
TILE = 32

# --- Warna ---------------------------------------------------------------
COL_BG = (5, 5, 7)
COL_FLOOR = (66, 62, 56)
COL_WALL = (122, 115, 104)
COL_SONAR = (168, 224, 238)
COL_MEMORY = (25, 34, 36)
COL_LIGHT = (244, 228, 184)
COL_AURA = (150, 142, 126)
COL_LISTENER = (176, 65, 62)
COL_PLAYER = (217, 214, 204)
COL_FRAGMENT = (185, 168, 255)
COL_BATTERY = (143, 199, 154)
COL_EXIT = (255, 241, 207)
COL_TEXT = (207, 202, 192)
COL_TEXT_DIM = (110, 106, 100)
COL_MIMIC = (150, 170, 176)

# --- Pemain --------------------------------------------------------------
PLAYER_RADIUS = 7
WALK_SPEED = 80.0
RUN_SPEED = 150.0
WALK_NOISE = 70.0
RUN_NOISE = 220.0
STEP_INTERVAL_WALK = 0.45
STEP_INTERVAL_RUN = 0.30
AURA_RADIUS = 44
PICKUP_RADIUS = 18.0
EXIT_RADIUS = 18.0

# --- Sonar ---------------------------------------------------------------
SONAR_SPEED = 520.0
SONAR_RANGE = 420.0
SONAR_RAYS = 360
SONAR_NOISE = 400.0
ECHO_BRIGHT_TIME = 0.3
ECHO_FADE_TIME = 2.5
BLIP_TIME = 1.5
ITEM_BLIP_TIME = 3.0

# --- Kerikil & hancurkan dinding -----------------------------------------
STONE_RANGE = 190.0     # kerikil jatuh sejauh ini di depan pemain (melambung, bisa lewat atas dinding)
STONE_FLIGHT = 0.45     # lama kerikil di udara
STONE_NOISE = 260.0     # bunyi "tok" saat jatuh menarik Pendengar ke sana
RIPPLE_TIME = 0.8       # lingkaran samar di tempat kerikil jatuh
BREAK_TIME = 1.0        # lama menahan E sampai dinding runtuh
BREAK_NOISE = 400.0     # runtuhnya dinding sekeras sonar
DEBRIS_TIME = 0.6       # pecahan batu yang terlempar saat dinding runtuh

# --- Senter --------------------------------------------------------------
LIGHT_HALF_ANGLE = math.radians(25)
LIGHT_RANGE_MAX = 230.0
LIGHT_RANGE_MIN = 170.0
LIGHT_RAYS = 48
BATTERY_MAX = 100.0
BATTERY_PICKUP = 35.0
FLICKER_THRESHOLD = 20.0

# --- Pendengar -----------------------------------------------------------
LISTENER_RADIUS = 10
LISTENER_WANDER_SPEED = 35.0
LISTENER_INVESTIGATE_SPEED = 65.0
LISTENER_SEARCH_SPEED = 45.0
LISTENER_HUNT_SPEED = 95.0
LISTENER_HUNT_RANGE = 120.0
LISTENER_LISTEN_TIME = (1.5, 3.0)
LISTENER_SEARCH_TIME = 8.0
LISTENER_SEARCH_TILES = 8
LISTENER_SOUND_RANGE = 250.0
LISTENER_MIN_SPAWN_CELLS = 8
LISTENER_RESPAWN_MIN_TILES = 20
AGITATED_SPEED_MULT = 1.25
AGITATED_HEARING_MULT = 1.4

# --- Fragmen & pintu -----------------------------------------------------
FRAGMENTS_PER_FLOOR = 3
FRAGMENT_MIN_START_CELLS = 6
FRAGMENT_HUM_RANGE = 400.0
FRAGMENT_PICKUP_NOISE = 150.0
EXIT_SILENCE = 6.0
EXIT_HUM_RANGE = 700.0

# --- Pengamat ------------------------------------------------------------
WATCHER_SPEED = 45.0
WATCHER_COMFORT_START = 260.0
WATCHER_COMFORT_SHRINK = 4.0
WATCHER_BANISH_TIME = 2.0
WATCHER_FADE_TIME = 0.8
WATCHER_AWAY_TIME = (25.0, 40.0)
WATCHER_SPAWN_DELAY = (20.0, 30.0)
WATCHER_SPAWN_TILES = (8, 14)
WATCHER_BREATH_RANGE = 110.0
WATCHER_HEART_RANGE = 400.0   # detak kedua terdengar dari sejauh ini, dari arah Pengamat
WATCHER_HEART_BPM = 46.0      # lebih lambat dari jantung pemain
WATCHER_CLICK_INTERVAL = (6.0, 12.0)  # sesekali terdengar klik senter mati dari arah Pengamat
WATCHER_SONAR_OBSERVE = 0.5

# --- Stres ---------------------------------------------------------------
STRESS_NEAR_RANGE = 150.0
STRESS_NEAR_RATE = 8.0
STRESS_DARK_DELAY = 8.0
STRESS_DARK_RATE = 0.8
STRESS_STARE_RATE = 8.0
STRESS_MIMIC = 10.0
STRESS_SHIFT = 3.0
STRESS_DEATH = 20.0
STRESS_SAFE_RANGE = 250.0
STRESS_SAFE_RATE = 3.0
STRESS_FRAGMENT = -15.0
STRESS_FLOOR_PER_DEATH = 10.0
STRESS_FLOOR_MAX = 40.0

# --- Detak jantung -------------------------------------------------------
HEART_RANGE = 240.0
HEART_MIN_BPM = 60.0
HEART_MAX_BPM = 150.0
HEART_THRESHOLD = 0.2
HEART_STRESS_WEIGHT = 0.4

# --- Trik persepsi & director --------------------------------------------
FALSE_ECHO_PER_PING = 2.0
FALSE_ECHO_MIN_DIST = 150.0
FALSE_ECHO_MAX_DIST = 400.0
MISS_ECHO_STRESS = 60.0
MISS_ECHO_MIN_DIST = 200.0
MISS_ECHO_CHANCE = 0.25
WHISPER_STRESS = 60.0
WHISPER_INTERVAL = (6.0, 14.0)
SHADOW_STRESS = 85.0
SHADOW_INTERVAL = (10.0, 20.0)
SHADOW_LIFE = 3.0
MEMORY_FLICKER_STRESS = 60.0
SWAY_STRESS = 85.0
WOBBLE_STRESS = 85.0
BIG_EVENT_GAP = 8.0
POST_CHASE_CALM = 12.0
SHIFT_MIN_DIST = 160.0
SHIFT_SONAR_WINDOW = 3.0
MIMIC_RANDOM_DIST = (250.0, 350.0)

# --- Transisi & tertangkap -----------------------------------------------
HIT_STOP = 0.9          # waktu berhenti + getar + makhluk terlihat, sebelum fade
DEATH_FADE = 0.8
DEATH_BLACK = 0.6
LAST_HEARTBEAT = 0.35   # satu detak terakhir, lalu jantung diam
EXIT_FADE = 1.0
SHAKE_MAX = 10.0        # piksel
SHAKE_DECAY = 1.6       # trauma berkurang per detik
SHAKE_DEATH = 1.0
SHAKE_GOD_HIT = 0.55    # mode kebal: efek tetap muncul, tapi tidak mati
GOD_HIT_COOLDOWN = 1.2

# --- Volume (0..1). Aturan: efek suara tidak lebih dari ±2x dengung latar.
VOLUME = {
    "drone": 0.35,
    "drone_bad": 0.35,
    "hum": 0.45,
    "exit_hum": 0.5,
    "drag": 0.5,
    "breath": 0.5,
    "heart": 0.6,
    "step": 0.16,
    "step_run": 0.28,
    "ping": 0.42,
    "mimic": 0.42,
    "chime": 0.32,
    "battery": 0.32,
    "click": 0.22,
    "click_dead": 0.22,
    "door": 0.5,
    "grind": 0.3,
    "whisper": 0.2,
    "impact": 0.5,
    "exhale": 0.35,
    "title_ping": 0.2,
    "heart_other": 0.48,
    "dead_flashlight": 0.6,
    "stone": 0.5,
    "crumble": 0.55,
    "melody": 0.4,
}


# --- Tingkat kesulitan ---------------------------------------------------
@dataclass(frozen=True)
class Difficulty:
    key: str
    lives: int
    listener_speed: float
    listener_hearing: float
    battery_drain: float
    batteries_per_floor: int
    sonar_cooldown: float
    false_echo_mult: float
    watcher_from_floor: int
    extra_listener_floors: tuple = ()
    aura_radius: int = AURA_RADIUS   # cahaya redup di sekitar pemain
    memory_glow: float = 1.0         # terangnya ingatan sonar (dinding yang pernah terlihat)
    echo_fade: float = ECHO_FADE_TIME  # berapa lama gema sonar memudar
    stones: int = 2                  # kerikil per lantai
    wall_breaks: int = 1             # dinding yang bisa dihancurkan per lantai
    retry_floor: bool = False        # nyawa habis: ulangi lantai ini dengan labirin baru, bukan kembali ke judul

    @property
    def name(self):
        return lang.data("difficulty")[self.key][0]

    @property
    def desc(self):
        return lang.data("difficulty")[self.key][1]


REDUP = Difficulty(
    "redup", lives=3, listener_speed=0.8, listener_hearing=0.85, battery_drain=5.0,
    batteries_per_floor=4, sonar_cooldown=2.0, false_echo_mult=0.5, watcher_from_floor=2,
    aura_radius=88, memory_glow=3.4, echo_fade=4.5, stones=3, wall_breaks=2, retry_floor=True,
)
GELAP = Difficulty(
    "gelap", lives=2, listener_speed=1.0, listener_hearing=1.0, battery_drain=7.0,
    batteries_per_floor=3, sonar_cooldown=3.0, false_echo_mult=1.0, watcher_from_floor=2,
)
PEKAT = Difficulty(
    "pekat", lives=1, listener_speed=1.2, listener_hearing=1.15, battery_drain=10.0,
    batteries_per_floor=2, sonar_cooldown=4.5, false_echo_mult=1.5, watcher_from_floor=1,
    extra_listener_floors=(3, 4, 5), stones=1,
)
DIFFICULTIES = (REDUP, GELAP, PEKAT)


def difficulty_by_key(key):
    for d in DIFFICULTIES:
        if d.key == key:
            return d
    raise KeyError(key)


# --- Aturan per lantai ---------------------------------------------------
FLOOR_COUNT = 5
FINAL_FLOOR = FLOOR_COUNT + 1

# lantai: (lebar sel, tinggi sel, jumlah Pendengar, porsi jalan buntu dibuka)
_FLOOR_BASE = {
    1: (12, 9, 1, 0.40),
    2: (14, 10, 2, 0.35),
    3: (16, 11, 2, 0.30),
    4: (18, 12, 3, 0.25),
    5: (20, 13, 3, 0.20),
}


@dataclass(frozen=True)
class FloorRules:
    number: int
    cells: tuple
    listeners: int
    watcher: bool
    shifting: bool
    shift_interval: tuple
    mimic: bool
    mimic_interval: tuple
    braid: float
    rooms: int
    tricks: bool      # gema palsu, bisikan, dan efek persepsi lain (Lantai 2+)
    shadows: bool     # bayangan palsu di tepi senter (Lantai 3+)
    final: bool = False


def floor_rules(number, diff):
    if number >= FINAL_FLOOR:
        return FloorRules(
            number=number, cells=(0, 0), listeners=0, watcher=False,
            shifting=False, shift_interval=(0, 0), mimic=False, mimic_interval=(0, 0),
            braid=0.0, rooms=0, tricks=False, shadows=False, final=True,
        )
    cw, ch, listeners, braid = _FLOOR_BASE[number]
    if number in diff.extra_listener_floors:
        listeners += 1
    return FloorRules(
        number=number,
        cells=(cw, ch),
        listeners=listeners,
        watcher=number >= diff.watcher_from_floor,
        shifting=number >= 3,
        shift_interval=(15.0, 30.0) if number >= 5 else (25.0, 45.0),
        mimic=number >= 4,
        mimic_interval=(25.0, 45.0) if number >= 5 else (40.0, 70.0),
        braid=braid,
        rooms=2 if number < 3 else 3,
        tricks=number >= 2,
        shadows=number >= 3,
    )
