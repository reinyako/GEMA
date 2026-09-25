"""Director: menjadwalkan kejadian horor dan menjaga ritme tegang-lega."""

import math

from .. import config as C
from .listener import HUNT
from .maze import tile_center
from .raycast import line_of_sight


class Director:
    def __init__(self, rules, diff, rng):
        self.rules = rules
        self.diff = diff
        self.rng = rng
        self.gap = 10.0  # beri waktu pemain beradaptasi di awal lantai
        self.was_chasing = False
        self.shift_timer = rng.uniform(*rules.shift_interval) if rules.shifting else math.inf
        self.mimic_timer = rng.uniform(*rules.mimic_interval) if rules.mimic else math.inf
        self.whisper_timer = rng.uniform(*C.WHISPER_INTERVAL)
        self.shadow_timer = rng.uniform(*C.SHADOW_INTERVAL)

    def on_respawn(self):
        self.gap = max(self.gap, 10.0)

    def update(self, dt, floor):
        if self.rules.final:
            return
        self.gap -= dt
        chasing = any(l.state == HUNT for l in floor.listeners)
        if chasing:
            self.gap = max(self.gap, 2.0)
        elif self.was_chasing:
            self.gap = max(self.gap, C.POST_CHASE_CALM)
        self.was_chasing = chasing

        stress = floor.stress.value
        pace = 1.0 + 0.45 * stress / 100.0  # stres tinggi = kejadian lebih sering

        if self.rules.shifting:
            self.shift_timer -= dt * pace
            if self.shift_timer <= 0 and self.gap <= 0:
                if floor.try_shift_wall():
                    self.gap = C.BIG_EVENT_GAP
                    self.shift_timer = self.rng.uniform(*self.rules.shift_interval)
                else:
                    self.shift_timer = 2.0

        if self.rules.mimic and floor.watcher is not None:
            self.mimic_timer -= dt * pace
            if self.mimic_timer <= 0 and self.gap <= 0:
                floor.mimic_ping()
                self.gap = C.BIG_EVENT_GAP
                self.mimic_timer = self.rng.uniform(*self.rules.mimic_interval)

        if self.rules.tricks and stress >= C.WHISPER_STRESS:
            self.whisper_timer -= dt
            if self.whisper_timer <= 0:
                floor.whisper()
                self.whisper_timer = self.rng.uniform(*C.WHISPER_INTERVAL)

        if self.rules.shadows and stress >= C.SHADOW_STRESS and floor.flashlight.on:
            self.shadow_timer -= dt
            if self.shadow_timer <= 0 and self.gap <= 0:
                if floor.spawn_shadow():
                    self.gap = C.BIG_EVENT_GAP
                    self.shadow_timer = self.rng.uniform(*C.SHADOW_INTERVAL)
                else:
                    self.shadow_timer = 1.0

    # --- trik sonar ------------------------------------------------------
    def false_echoes(self, floor, path_map):
        if not self.rules.tricks:
            return []
        expected = floor.stress.value / 100.0 * C.FALSE_ECHO_PER_PING * self.diff.false_echo_mult
        n = int(expected) + (1 if self.rng.random() < expected - int(expected) else 0)
        if n <= 0:
            return []
        p = floor.player
        options = []
        for t, d in path_map.items():
            if d * C.TILE > C.SONAR_RANGE:
                continue
            cx, cy = tile_center(t)
            e = math.hypot(cx - p.x, cy - p.y)
            if C.FALSE_ECHO_MIN_DIST <= e <= C.FALSE_ECHO_MAX_DIST:
                options.append((cx, cy))
        out = []
        for cx, cy in self.rng.sample(options, min(n, len(options))):
            fx = cx + self.rng.uniform(-8, 8)
            fy = cy + self.rng.uniform(-8, 8)
            out.append((fx, fy, line_of_sight(floor.maze, p.x, p.y, fx, fy)))
        return out

    def drop_echo(self, floor, kind, dist):
        if kind != "listener" or not self.rules.tricks:
            return False
        if floor.stress.value <= C.MISS_ECHO_STRESS or dist <= C.MISS_ECHO_MIN_DIST:
            return False
        return self.rng.random() < C.MISS_ECHO_CHANCE * self.diff.false_echo_mult
