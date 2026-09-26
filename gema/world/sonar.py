"""Sonar: gelombang yang memantul di dinding, titik gema, jejak ingatan, dan tanda objek."""

import math

import pygame

from .. import config as C
from .maze import tile_of
from .raycast import cast, line_of_sight


class Ping:
    __slots__ = ("x", "y", "radius", "hits", "hit_i", "dets", "det_i", "wobble")


class Blip:
    __slots__ = ("x", "y", "kind", "sharp", "age", "life", "fake")

    def __init__(self, x, y, kind, sharp, life, fake):
        self.x, self.y = x, y
        self.kind = kind
        self.sharp = sharp
        self.age = 0.0
        self.life = life
        self.fake = fake


class Ring:
    """Lingkaran visual tanpa pantulan (dipakai ping peniru)."""

    __slots__ = ("x", "y", "radius")

    def __init__(self, x, y):
        self.x, self.y = x, y
        self.radius = 0.0


class Sonar:
    def __init__(self, maze, rng, memory_color=C.COL_MEMORY, echo_fade=C.ECHO_FADE_TIME):
        self.maze = maze
        self.rng = rng
        self.memory_color = memory_color
        self.echo_fade = echo_fade
        self.memory = pygame.Surface((maze.w * C.TILE, maze.h * C.TILE))
        self.memory.fill((0, 0, 0))
        self.points = []   # [x, y, umur]
        self.blips = []
        self.pings = []
        self.rings = []
        self.cooldown = 0.0
        self.time = 0.0
        self.last_ping_time = -99.0
        self.last_ping_pos = (-9999.0, -9999.0)

    def ready(self):
        return self.cooldown <= 0

    def ping(self, x, y, cooldown, targets, path_map, fakes=(), drop=None, wobble=False):
        """Mengirim satu gelombang.

        targets: daftar (objek, jenis). Objek harus punya x, y, dan sonar_seen_at.
        path_map: hasil BFS dari petak pemain, untuk menentukan tanda buram di balik tikungan.
        fakes: daftar (x, y, tajam) untuk gema palsu.
        drop(objek, jenis, jarak) -> True kalau tanda objek itu sengaja dihilangkan.
        """
        self.cooldown = cooldown
        self.last_ping_time = self.time
        self.last_ping_pos = (x, y)
        p = Ping()
        p.x, p.y = x, y
        p.radius = 0.0
        p.wobble = wobble
        hits = []
        n = C.SONAR_RAYS
        for i in range(n):
            a = (i + self.rng.uniform(-0.3, 0.3)) * math.tau / n
            dx, dy = math.cos(a), math.sin(a)
            d = cast(self.maze, x, y, dx, dy, C.SONAR_RANGE)
            hit = d < C.SONAR_RANGE
            hits.append((d, dx, dy, hit))
        hits.sort(key=lambda h: h[0])
        p.hits = hits
        p.hit_i = 0

        dets = []
        for ent, kind in targets:
            d = math.hypot(ent.x - x, ent.y - y)
            if d > C.SONAR_RANGE:
                continue
            if drop is not None and drop(ent, kind, d):
                continue
            sharp = line_of_sight(self.maze, x, y, ent.x, ent.y)
            if not sharp:
                pd = path_map.get(tile_of(ent.x, ent.y))
                if pd is None or pd * C.TILE > C.SONAR_RANGE:
                    continue
            dets.append((d, ent, kind, sharp, None))
        for fx, fy, sharp in fakes:
            dets.append((math.hypot(fx - x, fy - y), None, "listener", sharp, (fx, fy)))
        dets.sort(key=lambda t: t[0])
        p.dets = dets
        p.det_i = 0
        self.pings.append(p)

    def forget(self, tile):
        """Menghapus jejak ingatan di satu petak, misalnya dinding yang baru runtuh."""
        t = C.TILE
        self.memory.fill((0, 0, 0), (tile[0] * t - 2, tile[1] * t - 2, t + 4, t + 4))

    def add_ring(self, x, y):
        self.rings.append(Ring(x, y))

    def update(self, dt, now):
        self.time = now
        self.cooldown = max(0.0, self.cooldown - dt)
        grow = C.SONAR_SPEED * dt

        for p in self.pings:
            p.radius += grow
            hits = p.hits
            while p.hit_i < len(hits) and hits[p.hit_i][0] <= p.radius:
                d, dx, dy, hit = hits[p.hit_i]
                p.hit_i += 1
                # Ruang sepanjang sinar terbukti kosong: hapus jejak ingatan yang basi.
                end = max(0.0, d - 5.0)
                pygame.draw.line(
                    self.memory, (0, 0, 0), (p.x, p.y), (p.x + dx * end, p.y + dy * end), 3
                )
                if hit:
                    self.points.append([p.x + dx * d, p.y + dy * d, 0.0])
            while p.det_i < len(p.dets) and p.dets[p.det_i][0] <= p.radius:
                _, ent, kind, sharp, pos = p.dets[p.det_i]
                p.det_i += 1
                life = C.BLIP_TIME if kind in ("listener", "watcher") else C.ITEM_BLIP_TIME
                if ent is not None:
                    ent.sonar_seen_at = now
                    self.blips.append(Blip(ent.x, ent.y, kind, sharp, life, False))
                else:
                    self.blips.append(Blip(pos[0], pos[1], kind, sharp, life, True))
        self.pings = [p for p in self.pings if p.radius < C.SONAR_RANGE]

        for r in self.rings:
            r.radius += grow
        self.rings = [r for r in self.rings if r.radius < C.SONAR_RANGE]

        life = C.ECHO_BRIGHT_TIME + self.echo_fade
        keep = []
        for pt in self.points:
            pt[2] += dt
            if pt[2] >= life:
                self.memory.fill(self.memory_color, (int(pt[0]) - 1, int(pt[1]) - 1, 2, 2))
            else:
                keep.append(pt)
        self.points = keep

        for b in self.blips:
            b.age += dt
        self.blips = [b for b in self.blips if b.age < b.life]

    def clear_active(self):
        self.pings.clear()
        self.rings.clear()
        self.blips.clear()
