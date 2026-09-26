"""Layar judul dan layar pilih tingkat kesulitan."""

import math
import random

import pygame

from .. import config as C
from .. import lang
from .. import notes
from ..render.draw import scale
from ..render.lighting import radial_gradient
from ..render.text import draw_center, font
from .menu import Menu

RING_PERIOD = 4.0
RING_SPEED = 380.0

# Layar pilih kesulitan ikut gelap sesuai pilihan yang disorot: Redup, Gelap, Pekat.
DARKNESS = (0.0, 0.45, 1.0)
DARKNESS_EASE = 2.5     # seberapa cepat suasana berpindah saat pilihan berganti
LIGHT_STEPS = 12        # banyaknya tingkat terang kolam cahaya yang disimpan


class TitleScene:
    def __init__(self, app):
        self.app = app
        self.t = 0.0
        self.ring_t = RING_PERIOD - 0.8
        self.origin = (C.SCREEN_W / 2, 175)
        self.points = self._letter_points("GEMA")
        self.actions = ["start"] + (["dev"] if app.dev.enabled else []) + ["achievements", "settings", "quit"]
        labels = {
            "start": notes.start_label(app.save),
            "dev": lang.t("menu_dev"),
            "achievements": lang.t("menu_achievements"),
            "settings": lang.t("menu_settings"),
            "quit": lang.t("menu_quit"),
        }
        items = [labels[a] for a in self.actions]
        self.menu = Menu(items, y=330 - 14 * (len(items) - 2), audio=app.audio)

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
        action = self.actions[choice]
        if action == "quit":
            self.app.running = False
        elif action == "dev":
            from .dev import DevScene

            self.app.switch(DevScene(self.app))
        elif action == "achievements":
            from .achievements import AchievementsScene

            self.app.switch(AchievementsScene(self.app))
        elif action == "settings":
            from .settings import SettingsScene

            self.app.switch(SettingsScene(self.app))
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
        draw_center(screen, lang.t("earphones"), font(14), C.COL_TEXT_DIM, C.SCREEN_W / 2, C.SCREEN_H - 40)
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
    """Pilih tingkat kesulitan. Makin berat pilihan yang disorot, makin gelap layarnya.

    Redup: pilihan disorot cahaya hangat seperti senter, dan ada ping sonar yang tenang.
    Gelap: cahayanya mengecil, detak jantung mulai terdengar.
    Pekat: tanpa cahaya. Pilihan lain tenggelam, pinggiran berdenyut merah, dan tulisannya
    kedip seperti senter yang baterainya hampir habis.
    """

    def __init__(self, app):
        self.app = app
        self.t = 0.0
        keys = [d.key for d in C.DIFFICULTIES]
        selected = keys.index(app.args.difficulty) if app.args.difficulty in keys else 1
        subs = []
        for d in C.DIFFICULTIES:
            best = app.save.lantai_terbaik.get(d.key, 0)
            if app.save.tamat.get(d.key, 0) > 0:
                extra = lang.t("finished_mark")
            elif 0 < best <= C.FLOOR_COUNT:
                extra = lang.t("deepest", n=best)
            else:
                extra = ""
            subs.append(d.desc + extra)
        self.menu = Menu([d.name for d in C.DIFFICULTIES], y=170, spacing=70, size=26,
                         selected=selected, subtitles=subs, audio=app.audio)
        self.dark = DARKNESS[selected]
        self.ring_t = RING_PERIOD - 0.8
        self.heart_timer = 0.0
        self.pulse = 0.0
        self.flicker_off = False
        self.flicker_timer = 0.0
        self.rng = random.Random()
        self.light_y = self.menu.y + self.menu.spacing * selected + 30
        self._pools = {}

    def enter(self):
        pygame.mouse.set_visible(True)

    def handle_event(self, ev):
        if ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
            self.app.go_title()
            return
        choice = self.menu.handle_event(ev)
        if choice is not None:
            self.app.start_run(C.DIFFICULTIES[choice])

    def _calm(self):
        return max(0.0, 1.0 - self.dark / DARKNESS[1])

    def _pool(self, light):
        """Kolam cahaya di bawah pilihan yang disorot. Makin gelap, makin kecil dan redup."""
        step = round(light * LIGHT_STEPS)
        if step <= 0:
            return None
        pool = self._pools.get(step)
        if pool is None:
            k = step / LIGHT_STEPS
            r = int(140 + 180 * k)
            glow = radial_gradient(r, scale(C.COL_AURA, 0.32 * k), power=1.6)
            pool = pygame.transform.smoothscale(glow, (int(r * 3.2), int(r * 1.3)))
            self._pools[step] = pool
        return pool

    def update(self, dt):
        self.t += dt
        self.dark += (DARKNESS[self.menu.selected] - self.dark) * min(1.0, dt * DARKNESS_EASE)

        # Redup: ping sonar pelan, seperti di layar judul
        self.ring_t += dt
        if self.ring_t >= RING_PERIOD:
            self.ring_t -= RING_PERIOD
            if self._calm() > 0.5:
                self.app.audio.play("title_ping")

        # Gelap dan Pekat: detak jantung, makin cepat dan makin jelas
        beat = max(0.0, (self.dark - 0.2) / 0.8)
        if beat > 0:
            self.heart_timer -= dt
            if self.heart_timer <= 0:
                self.heart_timer = 60.0 / (52 + 68 * beat)
                self.app.audio.beat(0.25 + 0.45 * beat)
                self.pulse = 1.0
        else:
            self.heart_timer = min(self.heart_timer, 0.3)
        self.pulse = max(0.0, self.pulse - dt * 2.5)

        # cahaya pindah pelan ke pilihan yang disorot, seperti senter yang diarahkan
        if self.menu.rects:
            target = self.menu.rects[self.menu.selected].centery + 12
            self.light_y += (target - self.light_y) * min(1.0, dt * 8.0)

        # Pekat: tulisannya kedip seperti senter yang baterainya hampir habis
        if DARKNESS[self.menu.selected] >= 1.0:
            self.flicker_timer -= dt
            if self.flicker_timer <= 0:
                self.flicker_off = not self.flicker_off
                self.flicker_timer = self.rng.uniform(0.04, 0.12) if self.flicker_off else self.rng.uniform(0.2, 1.3)
        else:
            self.flicker_off = False

    def draw(self, screen):
        screen.fill(C.COL_BG)
        pool = self._pool((1.0 - self.dark) ** 1.5)
        if pool is not None:
            screen.blit(pool, pool.get_rect(center=(C.SCREEN_W // 2, int(self.light_y))),
                        special_flags=pygame.BLEND_ADD)
        radius = self.ring_t * RING_SPEED
        calm = self._calm()
        if calm > 0 and 2 < radius < 700:
            pygame.draw.circle(screen, scale(C.COL_SONAR, 0.22 * calm * (1 - radius / 700)),
                               (C.SCREEN_W // 2, 98), int(radius), 1)
        draw_center(screen, lang.t("how_dark"), font(18), scale(C.COL_TEXT_DIM, 1 - 0.4 * self.dark),
                    C.SCREEN_W / 2, 90)
        # pilihan lain ikut tenggelam saat yang disorot makin gelap
        others = 1.0 - 0.8 * self.dark ** 1.5
        dims = []
        for i in range(len(self.menu.items)):
            if i == self.menu.selected:
                dims.append(0.2 if self.flicker_off else 1.0)
            else:
                dims.append(others)
        self.menu.draw(screen, item_alpha=dims)
        draw_center(screen, lang.t("back_hint"), font(13), (70, 67, 63), C.SCREEN_W / 2, C.SCREEN_H - 40)
        fx = self.app.effects
        heavy = max(0.0, (self.dark - 0.6) / 0.4)   # hanya terasa di Pekat
        fx.grain(screen, self.t, 1.0 + 0.8 * heavy)
        fx.vignette_smooth(screen, 200 * self.dark ** 2)
        fx.red_pulse(screen, self.pulse * 0.6 * heavy)
