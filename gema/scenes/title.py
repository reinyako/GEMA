"""Layar judul dan layar pilih tingkat kesulitan."""

import math
import random

import pygame

from .. import config as C
from .. import notes
from ..render.draw import scale
from ..render.text import draw_center, font
from .menu import Menu

RING_PERIOD = 4.0
RING_SPEED = 380.0


class TitleScene:
    def __init__(self, app):
        self.app = app
        self.t = 0.0
        self.ring_t = RING_PERIOD - 0.8
        self.origin = (C.SCREEN_W / 2, 175)
        self.points = self._letter_points("GEMA")
        items = [notes.start_label(app.save)] + (["Mode dev"] if app.dev.enabled else []) + ["Keluar"]
        self.menu = Menu(items, y=330 if len(items) == 2 else 316)

    def _letter_points(self, text):
        img = font(118, bold=True).render(text, True, (255, 255, 255))
        w, h = img.get_size()
        alpha = pygame.surfarray.array_alpha(img)
        rng = random.Random(4)
        ox, oy = C.SCREEN_W / 2 - w / 2, self.origin[1] - h / 2
        pts = []
        for x in range(0, w, 3):
            for y in range(0, h, 3):
                if alpha[x, y] > 140:
                    px, py = ox + x + rng.uniform(-0.8, 0.8), oy + y + rng.uniform(-0.8, 0.8)
                    pts.append((px, py, math.hypot(px - self.origin[0], py - self.origin[1])))
        return pts

    def enter(self):
        pygame.mouse.set_visible(True)
        self.app.audio.stop_all()

    def handle_event(self, ev):
        if ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
            self.app.running = False
            return
        choice = self.menu.handle_event(ev)
        if choice is None:
            return
        label = self.menu.items[choice]
        if label == "Keluar":
            self.app.running = False
        elif label == "Mode dev":
            from .dev import DevScene

            self.app.switch(DevScene(self.app))
        else:
            self.app.switch(DifficultyScene(self.app))

    def update(self, dt):
        self.t += dt
        self.ring_t += dt
        if self.ring_t >= RING_PERIOD:
            self.ring_t -= RING_PERIOD
            self.app.audio.play("title_ping")

    def draw(self, screen):
        screen.fill(C.COL_BG)
        radius = self.ring_t * RING_SPEED
        for x, y, d in self.points:
            since = (radius - d) / RING_SPEED
            if since < 0:
                since += RING_PERIOD
            k = max(0.07, math.exp(-since * 1.1))
            screen.fill(scale(C.COL_SONAR, k), (int(x), int(y), 2, 2))
        if radius < 700:
            pygame.draw.circle(
                screen, scale(C.COL_SONAR, 0.12 * (1 - radius / 700)),
                (int(self.origin[0]), int(self.origin[1])), int(radius), 1,
            )
        self.menu.draw(screen)
        draw_center(screen, "Gunakan earphone.", font(14), C.COL_TEXT_DIM, C.SCREEN_W / 2, C.SCREEN_H - 40)
        self.app.effects.grain(screen, self.t)
        self.app.effects.vignette(screen, 0)
        self._draw_signature(screen, radius)

    def _draw_signature(self, screen, radius):
        """Nama pembuat di pojok kanan bawah. Samar, dan ikut menyala sesaat saat gelombang lewat."""
        fnt = font(13)
        w, h = fnt.size("v.obscura")
        x = C.SCREEN_W - w - 18
        y = C.SCREEN_H - h - 16
        d = math.hypot(x + w / 2 - self.origin[0], y - self.origin[1])
        since = (radius - d) / RING_SPEED
        if since < 0:
            since += RING_PERIOD
        k = 0.3 + 0.35 * math.exp(-since * 1.5)
        screen.blit(fnt.render("v.obscura", True, scale(C.COL_TEXT, k)), (x, y))


class DifficultyScene:
    def __init__(self, app):
        self.app = app
        self.t = 0.0
        keys = [d.key for d in C.DIFFICULTIES]
        selected = keys.index(app.args.difficulty) if app.args.difficulty in keys else 1
        subs = []
        for d in C.DIFFICULTIES:
            best = app.save.lantai_terbaik.get(d.key, 0)
            extra = f"   (terdalam: Lantai {best})" if 0 < best <= C.FLOOR_COUNT else ""
            subs.append(d.desc + extra)
        self.menu = Menu([d.name for d in C.DIFFICULTIES], y=170, spacing=70, size=26,
                         selected=selected, subtitles=subs)

    def enter(self):
        pygame.mouse.set_visible(True)

    def handle_event(self, ev):
        if ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
            self.app.go_title()
            return
        choice = self.menu.handle_event(ev)
        if choice is not None:
            self.app.start_run(C.DIFFICULTIES[choice])

    def update(self, dt):
        self.t += dt

    def draw(self, screen):
        screen.fill(C.COL_BG)
        draw_center(screen, "Seberapa gelap?", font(18), C.COL_TEXT_DIM, C.SCREEN_W / 2, 90)
        self.menu.draw(screen)
        draw_center(screen, "Esc: kembali", font(13), (70, 67, 63), C.SCREEN_W / 2, C.SCREEN_H - 40)
        self.app.effects.grain(screen, self.t)
        self.app.effects.vignette(screen, 0)
