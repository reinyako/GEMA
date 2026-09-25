"""Pengamat: bentuknya sama persis seperti pemain. Mendekat hanya saat tidak diamati."""

import math

from .. import config as C
from .maze import tile_center, tile_of

ABSENT = "tidak ada"
PRESENT = "ada"
FADING = "memudar"


class Watcher:
    def __init__(self, rng):
        self.rng = rng
        self.x = self.y = -10000.0
        self.state = ABSENT
        self.timer = rng.uniform(*C.WATCHER_SPAWN_DELAY)
        self.comfort = C.WATCHER_COMFORT_START
        self.lit_time = 0.0
        self.lit_now = False
        self.observed = False
        self.alpha = 0.0
        self.aim = 0.0
        self.path = []
        self.repath = 0.0
        self.sonar_seen_at = -99.0
        self.click_timer = 0.0

    @property
    def present(self):
        return self.state == PRESENT

    @property
    def visible(self):
        return self.state in (PRESENT, FADING)

    def reset(self, delay=None):
        self.state = ABSENT
        self.timer = delay if delay is not None else self.rng.uniform(*C.WATCHER_SPAWN_DELAY)
        self.path = []
        self.lit_now = False
        self.observed = False
        self.x = self.y = -10000.0

    def _spawn(self, floor):
        p = floor.player
        lo, hi = C.WATCHER_SPAWN_TILES
        dist = floor.maze.bfs(tile_of(p.x, p.y), limit=hi)
        ax, ay = math.cos(p.aim), math.sin(p.aim)
        options = []
        for t, d in dist.items():
            if d < lo:
                continue
            cx, cy = tile_center(t)
            if floor.flashlight.lit(cx, cy, floor.maze, margin=C.TILE):
                continue
            behind = (cx - p.x) * ax + (cy - p.y) * ay < 0
            options.append((0 if behind else 1, t))
        if not options:
            return False
        best = min(k for k, _ in options)
        t = self.rng.choice([t for k, t in options if k == best])
        self.x, self.y = tile_center(t)
        self.state = PRESENT
        self.comfort = C.WATCHER_COMFORT_START
        self.lit_time = 0.0
        self.alpha = 0.0
        self.path = []
        self.repath = 0.0
        self.sonar_seen_at = -99.0
        self.click_timer = self.rng.uniform(*C.WATCHER_CLICK_INTERVAL)
        return True

    def _remaining(self):
        total, x, y = 0.0, self.x, self.y
        for px, py in self.path:
            total += math.hypot(px - x, py - y)
            x, y = px, py
        return total

    def update(self, dt, floor):
        if self.state == ABSENT:
            self.timer -= dt
            if self.timer <= 0 and not self._spawn(floor):
                self.timer = 3.0
            return
        if self.state == FADING:
            self.alpha -= dt / C.WATCHER_FADE_TIME
            if self.alpha <= 0:
                self.reset(self.rng.uniform(*C.WATCHER_AWAY_TIME))
            return

        p = floor.player
        self.alpha = min(1.0, self.alpha + dt * 1.5)
        # sesekali ia mencoba menyalakan senter yang baterainya sudah habis
        self.click_timer -= dt
        if self.click_timer <= 0:
            self.click_timer = self.rng.uniform(*C.WATCHER_CLICK_INTERVAL)
            floor.sfx.append(("dead_flashlight", self.x, self.y))
        self.aim = math.atan2(p.y - self.y, p.x - self.x)
        self.lit_now = floor.flashlight.lit(self.x, self.y, floor.maze, margin=C.PLAYER_RADIUS)
        self.observed = self.lit_now or (floor.time - self.sonar_seen_at) < C.WATCHER_SONAR_OBSERVE

        if self.lit_now:
            self.lit_time += dt
            if self.lit_time >= C.WATCHER_BANISH_TIME:
                self.state = FADING
                self.lit_now = False
                floor.sfx.append(("exhale", self.x, self.y))
            return
        self.lit_time = 0.0
        if self.observed:
            return

        self.comfort = max(0.0, self.comfort - C.WATCHER_COMFORT_SHRINK * dt)
        self.repath -= dt
        if self.repath <= 0 or not self.path:
            self.repath = 0.4
            tiles = floor.maze.path(tile_of(self.x, self.y), tile_of(p.x, p.y))
            self.path = [tile_center(t) for t in tiles[1:]] + [(p.x, p.y)] if tiles else []
        budget = min(C.WATCHER_SPEED * dt, self._remaining() - self.comfort)
        while budget > 0 and self.path:
            tx, ty = self.path[0]
            dx, dy = tx - self.x, ty - self.y
            d = math.hypot(dx, dy)
            if d <= budget:
                self.x, self.y = tx, ty
                budget -= d
                self.path.pop(0)
            else:
                self.x += dx / d * budget
                self.y += dy / d * budget
                budget = 0
