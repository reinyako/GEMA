"""Pendengar: buta, berburu dengan telinga, membeku saat terkena cahaya."""

import math

from .. import config as C
from .maze import tile_center, tile_of

WANDER = "berkeliaran"
INVESTIGATE = "menyelidik"
LISTEN = "mendengarkan"
SEARCH = "mencari"
HUNT = "memburu"

SPEEDS = {
    WANDER: C.LISTENER_WANDER_SPEED,
    INVESTIGATE: C.LISTENER_INVESTIGATE_SPEED,
    SEARCH: C.LISTENER_SEARCH_SPEED,
    HUNT: C.LISTENER_HUNT_SPEED,
    LISTEN: 0.0,
}


class Silhouette:
    """Bentuk bergerigi yang tepinya bergetar. Saat tidak dianimasikan, bentuknya diam total."""

    VERTS = 11

    def init_shape(self, rng, base=C.LISTENER_RADIUS + 1):
        self.base = [base * rng.uniform(0.75, 1.25) for _ in range(self.VERTS)]
        self.phase = [rng.uniform(0, math.tau) for _ in range(self.VERTS)]
        self.freq = [rng.uniform(5, 11) for _ in range(self.VERTS)]
        self.shape = list(self.base)
        self.spin = rng.uniform(0, math.tau)
        self.anim_t = 0.0

    def animate(self, dt, rng):
        self.anim_t += dt
        t = self.anim_t
        self.shape = [
            b + math.sin(t * f + ph) * 2.5 + rng.uniform(-1.2, 1.2)
            for b, f, ph in zip(self.base, self.freq, self.phase)
        ]
        self.spin += dt * 0.4

    def outline(self, ox=0.0, oy=0.0):
        n = len(self.shape)
        return [
            (self.x - ox + math.cos(self.spin + i * math.tau / n) * r,
             self.y - oy + math.sin(self.spin + i * math.tau / n) * r)
            for i, r in enumerate(self.shape)
        ]


class Listener(Silhouette):
    def __init__(self, x, y, rng):
        self.x, self.y = x, y
        self.rng = rng
        self.state = WANDER
        self.path = []
        self.target = None
        self.timer = 0.0
        self.search_center = (x, y)
        self.frozen = False
        self.moving = False
        self.sonar_seen_at = -99.0
        self.init_shape(rng)

    # --- navigasi --------------------------------------------------------
    def _route(self, maze, goal_tile, final_point=None):
        tiles = maze.path(tile_of(self.x, self.y), goal_tile)
        if not tiles:
            self.path = []
            return
        pts = [tile_center(t) for t in tiles[1:]]
        if final_point is not None:
            pts.append(final_point)
        self.path = pts

    def go_to(self, x, y, maze):
        self.target = (x, y)
        self._route(maze, tile_of(x, y), (x, y))

    def invalidate(self, maze):
        """Dipanggil saat labirin berubah: hitung ulang jalur."""
        if self.target is not None and self.state in (INVESTIGATE, HUNT):
            self.go_to(self.target[0], self.target[1], maze)
        else:
            self.path = []

    def _pick_random(self, maze, center_tile, min_d, max_d):
        dist = maze.bfs(center_tile, limit=max_d)
        options = [t for t, d in dist.items() if d >= min_d]
        if not options:
            options = list(dist)
        if options:
            self._route(maze, self.rng.choice(options))

    def _follow(self, dt, speed):
        budget = speed * dt
        self.moving = bool(self.path) and speed > 0
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
        return not self.path

    def relocate(self, x, y):
        self.x, self.y = x, y
        self.state = WANDER
        self.path = []
        self.target = None
        self.frozen = False
        self.moving = False

    # --- update ----------------------------------------------------------
    def update(self, dt, floor):
        maze = floor.maze
        self.frozen = floor.flashlight.lit(self.x, self.y, maze, margin=C.LISTENER_RADIUS * 0.6)
        if self.frozen:
            self.moving = False
            return
        self.animate(dt, self.rng)

        agitated = floor.exit.open and not floor.rules.final
        speed_mult = floor.diff.listener_speed * (C.AGITATED_SPEED_MULT if agitated else 1.0)
        hearing = floor.diff.listener_hearing * (C.AGITATED_HEARING_MULT if agitated else 1.0)

        heard, best = None, math.inf
        for n in floor.noise.events:
            d = math.hypot(n.x - self.x, n.y - self.y)
            if d <= n.radius * hearing and d < best:
                heard, best = n, d
        if heard is not None:
            if heard.source == "stone" and self.state == HUNT:
                floor.run.distractions += 1
            if best <= C.LISTENER_HUNT_RANGE * hearing:
                self.state = HUNT
            elif self.state != HUNT:
                self.state = INVESTIGATE
            self.go_to(heard.x, heard.y, maze)

        if self.state == LISTEN:
            self.moving = False
            self.timer -= dt
            if self.timer <= 0:
                self.state = SEARCH
                self.timer = C.LISTENER_SEARCH_TIME
                self.path = []
            return

        if self.state == SEARCH:
            self.timer -= dt
            if self.timer <= 0:
                self.state = WANDER
                self.path = []
                self.target = None
            elif not self.path:
                self._pick_random(maze, tile_of(*self.search_center), 2, C.LISTENER_SEARCH_TILES)

        if self.state == WANDER and not self.path:
            self._pick_random(maze, tile_of(self.x, self.y), 4, 10)

        arrived = self._follow(dt, SPEEDS[self.state] * speed_mult)
        if arrived and self.state in (INVESTIGATE, HUNT):
            self.state = LISTEN
            self.timer = self.rng.uniform(*C.LISTENER_LISTEN_TIME)
            self.search_center = (self.x, self.y)
            self.target = None
