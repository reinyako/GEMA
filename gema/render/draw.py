"""Menggambar satu lantai: dunia yang terkena cahaya, gema sonar, dan penanda pemain."""

import math
import random

import pygame

from .. import config as C
from .lighting import Lighting, radial_gradient
from .text import draw_left, font


def scale(color, k):
    k = max(0.0, min(1.0, k))
    return (int(color[0] * k), int(color[1] * k), int(color[2] * k))


def diamond(cx, cy, r):
    return [(cx, cy - r), (cx + r * 0.7, cy), (cx, cy + r), (cx - r * 0.7, cy)]


class FloorRenderer:
    def __init__(self, floor):
        self.floor = floor
        self.rng = random.Random(floor.run.seed + floor.rules.number)
        m = floor.maze
        self.world = pygame.Surface((m.w * C.TILE, m.h * C.TILE))
        self.world.fill(C.COL_FLOOR)
        for ty in range(m.h):
            for tx in range(m.w):
                self._draw_tile(tx, ty)
        self.view = pygame.Surface((C.SCREEN_W, C.SCREEN_H))
        self.echo = pygame.Surface((C.SCREEN_W, C.SCREEN_H))
        self.lighting = Lighting(floor.diff.aura_radius)
        self.red_glow = radial_gradient(46, (150, 26, 22), power=1.4)
        self.pale_glow = radial_gradient(46, (120, 118, 110), power=1.4)

    def _draw_tile(self, tx, ty):
        t = C.TILE
        rect = pygame.Rect(tx * t, ty * t, t, t)
        # Variasi warna tetap per petak supaya tidak berkedip saat digambar ulang.
        v = ((tx * 73856093) ^ (ty * 19349663)) % 13 - 6
        if self.floor.maze.is_wall(tx, ty):
            base = tuple(max(0, min(255, c + v)) for c in C.COL_WALL)
            self.world.fill(base, rect)
            pygame.draw.line(self.world, scale(base, 0.7), rect.bottomleft, rect.bottomright)
            pygame.draw.line(self.world, scale(base, 0.8), rect.topright, rect.bottomright)
        else:
            base = tuple(max(0, min(255, c + v // 2)) for c in C.COL_FLOOR)
            self.world.fill(base, rect)
            if v % 4 == 0:
                self.world.fill(scale(base, 0.8), (rect.x + 9 + v, rect.y + 13, 2, 2))

    def refresh(self):
        for t in self.floor.changed_tiles:
            self._draw_tile(*t)
        self.floor.changed_tiles.clear()

    # --- lapisan -----------------------------------------------------------
    def draw(self, screen, camx, camy, t):
        f = self.floor
        self.refresh()
        camx, camy = int(camx), int(camy)
        v = self.view
        v.fill(C.COL_WALL)  # di luar labirin dianggap dinding, supaya aura tidak terpotong kotak
        v.blit(self.world, (-camx, -camy))
        self._items(v, camx, camy, t)
        self._monsters(v, camx, camy)
        v.blit(self.lighting.build(camx, camy, f), (0, 0), special_flags=pygame.BLEND_MULT)
        screen.blit(v, (0, 0))

        show_memory = True
        if f.rules.tricks and f.stress.value >= C.MEMORY_FLICKER_STRESS:
            chance = 0.03 + 0.12 * (f.stress.value - C.MEMORY_FLICKER_STRESS) / (100 - C.MEMORY_FLICKER_STRESS)
            show_memory = self.rng.random() >= chance
        if show_memory:
            screen.blit(f.sonar.memory, (-camx, -camy), special_flags=pygame.BLEND_ADD)

        e = self.echo
        e.fill((0, 0, 0))
        self._echoes(e, camx, camy, t)
        screen.blit(e, (0, 0), special_flags=pygame.BLEND_ADD)
        self._exit_crack(screen, camx, camy, t)
        self._player(screen, camx, camy)

    def _on_screen(self, x, y, margin=40):
        return -margin <= x <= C.SCREEN_W + margin and -margin <= y <= C.SCREEN_H + margin

    def _items(self, v, camx, camy, t):
        f = self.floor
        for frag in f.fragments:
            if frag.taken:
                continue
            x, y = frag.x - camx, frag.y - camy
            if self._on_screen(x, y):
                r = 7 + math.sin(t * 3.0) * 1.2
                pygame.draw.polygon(v, C.COL_FRAGMENT, diamond(x, y, r))
                pygame.draw.polygon(v, scale(C.COL_FRAGMENT, 0.55), diamond(x, y, r * 0.5))
        for b in f.batteries:
            if b.taken:
                continue
            x, y = b.x - camx, b.y - camy
            if self._on_screen(x, y):
                pygame.draw.rect(v, C.COL_BATTERY, (x - 3, y - 5, 6, 11))
                pygame.draw.rect(v, scale(C.COL_BATTERY, 0.6), (x - 1, y - 7, 2, 2))
        e = f.exit
        x, y = e.x - camx, e.y - camy
        if self._on_screen(x, y):
            pygame.draw.rect(v, (78, 70, 58), (x - 10, y - 14, 20, 28), 3)
            if not e.open:
                pygame.draw.rect(v, (40, 36, 30), (x - 7, y - 11, 14, 22))

    def _monsters(self, v, camx, camy):
        f = self.floor
        for m in [*f.listeners, *f.shadows]:
            if self._on_screen(m.x - camx, m.y - camy):
                pts = m.outline(camx, camy)
                pygame.draw.polygon(v, (3, 2, 2), pts)
                pygame.draw.polygon(v, (74, 36, 34), pts, 1)
        w = f.watcher
        if w is not None and w.visible and self._on_screen(w.x - camx, w.y - camy):
            self._figure(v, w.x - camx, w.y - camy, w.aim, w.alpha)

    @staticmethod
    def _figure(surface, x, y, aim, k=1.0):
        """Bentuk pemain. Pengamat sengaja digambar dengan fungsi yang sama."""
        pygame.draw.circle(surface, scale(C.COL_PLAYER, 0.85 * k), (int(x), int(y)), C.PLAYER_RADIUS - 1)
        ex, ey = x + math.cos(aim) * 11, y + math.sin(aim) * 11
        pygame.draw.line(surface, scale(C.COL_PLAYER, 0.6 * k), (x, y), (ex, ey), 2)

    def _echoes(self, e, camx, camy, t):
        f = self.floor
        s = f.sonar
        bright, fade = C.ECHO_BRIGHT_TIME, s.echo_fade
        w, h = C.SCREEN_W, C.SCREEN_H
        for x, y, age in s.points:
            sx, sy = x - camx, y - camy
            if 0 <= sx < w and 0 <= sy < h:
                k = 1.0 if age < bright else max(0.15, 1.0 - (age - bright) / fade)
                e.fill(scale(C.COL_SONAR, k), (sx - 1, sy - 1, 2, 2))

        for p in s.pings:
            k = 0.22 * (1.0 - p.radius / C.SONAR_RANGE)
            cx, cy = p.x - camx, p.y - camy
            if p.wobble:
                pts = [
                    (cx + math.cos(a) * (p.radius + math.sin(a * 7 + t * 9) * 6),
                     cy + math.sin(a) * (p.radius + math.sin(a * 7 + t * 9) * 6))
                    for a in (i * math.tau / 64 for i in range(64))
                ]
                pygame.draw.polygon(e, scale(C.COL_SONAR, k), pts, 1)
            elif p.radius > 2:
                pygame.draw.circle(e, scale(C.COL_SONAR, k), (int(cx), int(cy)), int(p.radius), 1)
        for r in s.rings:
            k = 0.2 * (1.0 - r.radius / C.SONAR_RANGE)
            if r.radius > 2:
                pygame.draw.circle(e, scale(C.COL_MIMIC, k), (int(r.x - camx), int(r.y - camy)), int(r.radius), 1)

        for b in s.blips:
            k = 1.0 - b.age / b.life
            x, y = int(b.x - camx), int(b.y - camy)
            if not self._on_screen(x, y):
                continue
            if b.kind == "listener":
                if b.sharp:
                    pygame.draw.circle(e, scale(C.COL_LISTENER, 0.35 * k), (x, y), 8)
                    pygame.draw.circle(e, scale(C.COL_LISTENER, k), (x, y), 4)
                else:
                    pygame.draw.circle(e, scale(C.COL_LISTENER, 0.18 * k), (x, y), 12)
                    pygame.draw.circle(e, scale(C.COL_LISTENER, 0.3 * k), (x, y), 7)
            elif b.kind == "watcher":
                aim = math.atan2(f.player.y - b.y, f.player.x - b.x)
                self._figure(e, x, y, aim, k * (1.0 if b.sharp else 0.45))
            elif b.kind == "fragment":
                pygame.draw.polygon(e, scale(C.COL_FRAGMENT, k * (1.0 if b.sharp else 0.5)), diamond(x, y, 8), 1)
            elif b.kind == "battery":
                pygame.draw.circle(e, scale(C.COL_BATTERY, k * (1.0 if b.sharp else 0.5)), (x, y), 3)
            elif b.kind == "exit":
                e.fill(scale(C.COL_EXIT, k * (0.8 if b.sharp else 0.4)), (x - 1, y - 11, 3, 22))

    def _exit_crack(self, screen, camx, camy, t):
        e = self.floor.exit
        if not e.open:
            return
        x, y = e.x - camx, e.y - camy
        if self._on_screen(x, y):
            k = 0.75 + 0.25 * math.sin(t * 2.0)
            screen.fill(scale(C.COL_EXIT, k), (x - 1, y - 11, 3, 22))

    def draw_catcher(self, screen, entity, camx, camy, k):
        """Makhluk yang menangkap pemain: terlihat sesaat, walau berada di kegelapan."""
        if entity is None or k <= 0:
            return
        x, y = entity.x - camx, entity.y - camy
        if hasattr(entity, "outline"):
            glow = self.red_glow
            screen.blit(glow, (x - glow.get_width() // 2, y - glow.get_height() // 2),
                        special_flags=pygame.BLEND_ADD)
            pts = entity.outline(camx, camy)
            pygame.draw.polygon(screen, (4, 2, 2), pts)
            pygame.draw.polygon(screen, scale(C.COL_LISTENER, k), pts, 2)
        else:
            glow = self.pale_glow
            screen.blit(glow, (x - glow.get_width() // 2, y - glow.get_height() // 2),
                        special_flags=pygame.BLEND_ADD)
            self._figure(screen, x, y, entity.aim, k)
        self._player(screen, camx, camy)

    def _player(self, screen, camx, camy):
        p = self.floor.player
        self._figure(screen, p.x - camx, p.y - camy, p.aim, 0.95)

    # --- debug -------------------------------------------------------------
    def draw_debug(self, screen, fps):
        f = self.floor
        m = f.maze
        s = max(2, min(5, 300 // m.w))
        ox, oy = 8, 8
        panel = pygame.Surface((m.w * s, m.h * s))
        panel.fill((10, 10, 12))
        for ty in range(m.h):
            for tx in range(m.w):
                if m.is_wall(tx, ty):
                    panel.fill((70, 70, 76), (tx * s, ty * s, s, s))
        def dot(x, y, col, r=2):
            pygame.draw.circle(panel, col, (int(x / C.TILE * s), int(y / C.TILE * s)), r)
        for frag in f.fragments:
            if not frag.taken:
                dot(frag.x, frag.y, C.COL_FRAGMENT)
        for b in f.batteries:
            if not b.taken:
                dot(b.x, b.y, C.COL_BATTERY)
        dot(f.exit.x, f.exit.y, C.COL_EXIT if f.exit.open else (120, 110, 90), 3)
        for l in f.listeners:
            dot(l.x, l.y, (90, 170, 255) if l.frozen else C.COL_LISTENER, 3)
        if f.watcher is not None and f.watcher.visible:
            dot(f.watcher.x, f.watcher.y, (255, 255, 255), 3)
        dot(f.player.x, f.player.y, (255, 230, 90), 3)
        screen.blit(panel, (ox, oy))

        fnt = font(13)
        lines = [
            f"FPS {fps:5.1f}   seed {f.run.seed}   lantai {f.rules.number}",
            f"stres {f.stress.value:5.1f} (min {f.stress.floor_min:.0f})   baterai {f.flashlight.battery:5.1f}",
            f"sonar siap {f.sonar.ready()}   fragmen {f.taken}/{len(f.fragments)}   nyawa {f.run.lives}",
        ]
        lines += [f"pendengar {i}: {l.state}{' (beku)' if l.frozen else ''}" for i, l in enumerate(f.listeners)]
        if f.watcher is not None:
            w = f.watcher
            lines.append(f"pengamat: {w.state}  jarak nyaman {w.comfort:5.1f}  disorot {w.lit_time:.1f}")
        y = oy + m.h * s + 6
        for line in lines:
            y += draw_left(screen, line, fnt, (230, 230, 150), ox, y)
