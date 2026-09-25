"""Menerjemahkan keadaan lantai menjadi suara: loop posisional, detak jantung, dan efek sekali putar."""

from .. import config as C
from .manager import spatial

POSITIONAL_RANGE = {
    "mimic": 900.0,
    "door": 1400.0,
    "grind": 900.0,
    "whisper": 400.0,
    "exhale": 500.0,
}


class Soundscape:
    def __init__(self, audio):
        self.audio = audio
        self.heart_timer = 0.0
        self.drone_level = 0.0

    def silence(self):
        self.drone_level = 0.0
        self.heart_timer = 0.0
        self.audio.stop_all()

    def update(self, dt, floor):
        a = self.audio
        if not a.enabled:
            floor.sfx.clear()
            return
        p = floor.player
        px, py = p.x, p.y

        for name, x, y in floor.sfx:
            if x is None:
                a.play(name)
            else:
                a.play_at(name, x, y, px, py, POSITIONAL_RANGE.get(name, 700.0))
        floor.sfx.clear()

        # Dengung latar: berhenti saat hening dan di lantai terakhir.
        target = 0.0 if (floor.rules.final or floor.silence_timer > 0) else 1.0
        speed = 5.0 if target < self.drone_level else 0.35
        self.drone_level += (target - self.drone_level) * min(1.0, dt * speed)
        mix = 0.0
        if floor.rules.tricks:
            mix = max(0.0, min(1.0, (floor.stress.value - 60.0) / 40.0))
        a.set_loop("drone_a", "drone", self.drone_level * (1.0 - 0.6 * mix))
        a.set_loop("drone_b", "drone_bad", self.drone_level * mix)

        for i in range(3):
            slot = f"frag{i}"
            if i < len(floor.fragments) and not floor.fragments[i].taken:
                f = floor.fragments[i]
                a.set_loop(slot, "hum", *spatial(f.x, f.y, px, py, C.FRAGMENT_HUM_RANGE, 1.0))
            else:
                a.stop_loop(slot)

        e = floor.exit
        if e.open and not floor.rules.final:
            a.set_loop("exit", "exit_hum", *spatial(e.x, e.y, px, py, C.EXIT_HUM_RANGE, 1.0))
        else:
            a.stop_loop("exit")

        for i in range(6):
            slot = f"lis{i}"
            if i < len(floor.listeners):
                l = floor.listeners[i]
                if l.moving and not l.frozen:
                    a.set_loop(slot, "drag", *spatial(l.x, l.y, px, py, C.LISTENER_SOUND_RANGE, 1.0))
                    continue
            a.stop_loop(slot)

        w = floor.watcher
        if w is not None and w.present:
            a.set_loop("breath", "breath", *spatial(w.x, w.y, px, py, C.WATCHER_BREATH_RANGE, 1.0))
        else:
            a.stop_loop("breath")

        danger = floor.danger()
        if danger > C.HEART_THRESHOLD and not floor.rules.final:
            self.heart_timer -= dt
            if self.heart_timer <= 0:
                bpm = C.HEART_MIN_BPM + (C.HEART_MAX_BPM - C.HEART_MIN_BPM) * danger
                self.heart_timer = 60.0 / bpm
                a.beat(0.25 + 0.75 * danger)
        else:
            self.heart_timer = min(self.heart_timer, 0.3)
