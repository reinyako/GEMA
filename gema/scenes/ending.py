"""Ending: cahaya, semua dirimu yang dulu, catatan pertama, lalu hasil percobaan ini.

Urutan tahap: cahaya dan melodi → ping raksasa → menulis catatan pertama → pemain menulis
catatannya sendiri (jadi catatan pertama di percobaan berikutnya) → hasil dan pencapaian, di dalam
cahaya → kredit, sambil cahayanya padam → "Percobaan ke-N." di kegelapan.
"""

import math
import random

import numpy as np
import pygame

from .. import achievements
from .. import config as C
from .. import lang
from .. import notes
from ..render.draw import scale
from ..render.lighting import radial_gradient
from ..render.text import TypeText, draw_center, font
from ..save import NOTE_MAX
from ..world.maze import DIRS, generate

LIGHT, REVEAL, WRITE, NOTE, RESULT, CREDITS, NEXT = range(7)

LINE_PAUSE = 1.4
PAGE_HOLD = 3.0
FADE = 1.5
LIGHT_TIME = 8.0
REVEAL_TIME = 11.0
REVEAL_TILE = 16           # ukuran petak labirin di ping raksasa (setengah petak di dalam game)
REVEAL_SPEED = 260.0
NOTE_IDLE = 60.0           # catatan dilewati kalau tidak ada ketikan selama ini
RESULT_IDLE = 45.0         # layar hasil lanjut sendiri setelah ini
ACH_START = 2.0            # pencapaian baru mulai muncul setelah cahayanya terang
ACH_GAP = 0.7              # jeda antar pencapaian baru di layar hasil
CREDITS_DARK = 3.0         # lama cahaya padam di awal kredit
CREDITS_TIME = 9.4

# warna teks di atas cahaya (layar hasil)
INK = (40, 34, 26)
INK_DIM = (98, 86, 66)
INK_FAINT = (124, 110, 86)
INK_MARK = (44, 96, 104)
MAX_SELVES = 60


def page_alpha(t, hold):
    if t < FADE:
        return 255 * t / FADE
    if t < FADE + hold:
        return 255
    return max(0.0, 255 * (1 - (t - FADE - hold) / FADE))


def smooth(x):
    x = max(0.0, min(1.0, x))
    return x * x * (3 - 2 * x)


def figure(surface, x, y, aim, color, r):
    """Bentuk pemain (dan Pengamat): lingkaran dengan garis arah."""
    reach = r * 1.8
    pygame.draw.line(surface, scale(color, 0.7), (x, y), (x + math.cos(aim) * reach, y + math.sin(aim) * reach),
                     max(1, r // 3))
    pygame.draw.circle(surface, color, (int(x), int(y)), r)


class Reveal:
    """Ping sonar raksasa di atas labirin selebar layar. Di dalamnya berdiri semua dirimu yang dulu."""

    def __init__(self, seed, past):
        rng = random.Random(seed)
        t = REVEAL_TILE
        maze = generate(29, 16, rng, 0.3, 2)
        ox = (C.SCREEN_W - maze.w * t) // 2
        oy = (C.SCREEN_H - maze.h * t) // 2
        cx, cy = maze.w // 2 | 1, maze.h // 2 | 1   # sel selalu di koordinat ganjil
        self.center = (ox + (cx + 0.5) * t, oy + (cy + 0.5) * t)

        # dua titik gema di setiap sisi dinding yang bersebelahan dengan lantai
        xs, ys = [], []
        for y in range(maze.h):
            for x in range(maze.w):
                if not maze.is_wall(x, y):
                    continue
                for dx, dy in DIRS:
                    if maze.is_wall(x + dx, y + dy):
                        continue
                    mx, my = ox + (x + 0.5 + dx * 0.5) * t, oy + (y + 0.5 + dy * 0.5) * t
                    for s in (-0.25, 0.25):
                        xs.append(mx - dy * s * t + rng.uniform(-0.8, 0.8))
                        ys.append(my + dx * s * t + rng.uniform(-0.8, 0.8))
        self.px = np.clip(np.array(xs, dtype=int), 0, C.SCREEN_W - 2)
        self.py = np.clip(np.array(ys, dtype=int), 0, C.SCREEN_H - 2)
        self.d = np.hypot(self.px - self.center[0], self.py - self.center[1])
        self.layer = pygame.Surface((C.SCREEN_W, C.SCREEN_H))
        self.glows = [radial_gradient(18, scale((120, 118, 110), i / 8), power=1.6) for i in range(9)]

        cells = [c for c in maze.cell_tiles() if abs(c[0] - cx) + abs(c[1] - cy) >= 8]
        rng.shuffle(cells)
        self.selves = []
        for c in cells[:past]:
            x, y = ox + (c[0] + 0.5) * t, oy + (c[1] + 0.5) * t
            aim = math.atan2(self.center[1] - y, self.center[0] - x)
            dist = math.hypot(self.center[0] - x, self.center[1] - y)
            self.selves.append((x, y, aim, dist, rng.random()))

    def draw(self, screen, t):
        radius = t * REVEAL_SPEED
        fade = 1.0 - smooth((t - 9.5) / 1.5)
        since = (radius - self.d) / REVEAL_SPEED
        k = np.where(since >= 0, np.maximum(0.24, np.exp(-np.maximum(since, 0.0) * 1.1)), 0.0) * fade
        colors = (np.asarray(C.COL_SONAR, dtype=float)[None, :] * k[:, None]).astype(np.uint8)
        layer = self.layer
        layer.fill((0, 0, 0))
        px = pygame.surfarray.pixels3d(layer)
        for ddx in (0, 1):
            for ddy in (0, 1):
                px[self.px + ddx, self.py + ddy] = colors
        del px
        screen.blit(layer, (0, 0))
        cx, cy = self.center
        if 2 < radius < 700:
            pygame.draw.circle(screen, scale(C.COL_SONAR, 0.2 * fade * (1 - radius / 700)),
                               (int(cx), int(cy)), int(radius), 1)
        for x, y, aim, dist, order in self.selves:
            seen = (radius - dist) / REVEAL_SPEED
            if seen < 0:
                continue
            gone = smooth((t - 7.5 - order * 1.6) / 0.25)   # padam satu per satu
            a = min(1.0, seen / 0.4) * (1.0 - gone) * fade * 0.9
            if a > 0.01:
                glow = self.glows[round(a * 8)]
                screen.blit(glow, (x - 18, y - 18), special_flags=pygame.BLEND_ADD)
                figure(screen, x, y, aim, scale(C.COL_PLAYER, a), 5)
        figure(screen, cx, cy, -math.pi / 2, scale(C.COL_PLAYER, max(fade, 0.0)), 5)


class EndingScene:
    def __init__(self, app, run):
        self.app = app
        self.run = run
        app.save.ending += 1
        app.save.write()
        self.new = achievements.record(app.save, run, finished=True)
        self.lines = [TypeText(text, size=22, speed=13.0, hold=1e9) for text in notes.ending_lines()]
        self.current = 0
        self.wait = 0.0
        self.writing_fade = None
        self.stage = LIGHT
        self.stage_t = 0.0
        self.reveal = Reveal(run.seed, min(MAX_SELVES, max(3, app.save.percobaan - 1)))
        self.note = ""
        self.note_saved = False
        self.idle = 0.0
        self.chimes = 0

    def enter(self):
        pygame.mouse.set_visible(False)
        self.app.audio.stop_all()
        self.app.audio.play("melody")

    # --- tahap -------------------------------------------------------------
    def _goto(self, stage):
        self.stage = stage
        self.stage_t = 0.0
        if stage == REVEAL:
            self.app.audio.play("ping")
        elif stage == NOTE:
            self.idle = 0.0
            pygame.key.start_text_input()
        elif stage == RESULT:
            self.app.audio.play("melody")
        elif stage > NEXT:
            self.app.go_title()

    def _next(self):
        self._goto(self.stage + 1)

    def handle_event(self, ev):
        if self.stage == NOTE:
            self._note_event(ev)
            return
        if ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
            self._goto(NOTE if self.stage < NOTE else self.stage + 1)
            return
        confirm = ev.type == pygame.KEYDOWN and ev.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE)
        confirm = confirm or (ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1)
        if confirm and self.stage >= RESULT:
            self._next()

    def _note_event(self, ev):
        if ev.type == pygame.TEXTINPUT:
            room = NOTE_MAX - len(self.note)
            if room > 0:
                self.note += ev.text[:room]
            self.idle = 0.0
        elif ev.type == pygame.KEYDOWN:
            self.idle = 0.0
            if ev.key == pygame.K_BACKSPACE:
                self.note = self.note[:-1]
            elif ev.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                text = " ".join(self.note.split())
                if text:
                    self.app.save.catatan_pemain = text
                    self.app.save.write()
                    self.note_saved = True
                    self.app.audio.ui("click")
                self._next()
            elif ev.key == pygame.K_ESCAPE:
                self._next()

    def update(self, dt):
        self.stage_t += dt
        s = self.stage
        if s == LIGHT and self.stage_t >= LIGHT_TIME:
            self._next()
        elif s == REVEAL and self.stage_t >= REVEAL_TIME:
            self._next()
        elif s == WRITE:
            self._update_writing(dt)
        elif s == NOTE:
            self.idle += dt
            if self.idle >= NOTE_IDLE:
                self._next()
        elif s == RESULT:
            while self.chimes < len(self.new) and self.stage_t >= ACH_START + self.chimes * ACH_GAP:
                self.chimes += 1
                self.app.audio.play("chime")
            if self.stage_t >= RESULT_IDLE:
                self._next()
        elif s == CREDITS and self.stage_t >= CREDITS_TIME:
            self._next()
        elif s == NEXT and self.stage_t >= FADE * 2 + 2.5:
            self._next()

    def _update_writing(self, dt):
        if self.writing_fade is not None:
            self.writing_fade += dt
            if self.writing_fade >= FADE:
                self._next()
            return
        line = self.lines[self.current]
        line.update(dt)
        if line.typed:
            self.wait += dt
            last = self.current == len(self.lines) - 1
            if last and self.wait >= PAGE_HOLD:
                self.writing_fade = 0.0
            elif not last and self.wait >= LINE_PAUSE:
                self.current += 1
                self.wait = 0.0

    # --- gambar ------------------------------------------------------------
    def draw(self, screen):
        screen.fill((0, 0, 0))
        cx = C.SCREEN_W / 2
        s, t = self.stage, self.stage_t
        if s == LIGHT:
            self._draw_light(screen, t)
        elif s == REVEAL:
            self.reveal.draw(screen, t)
            a = page_alpha(t - 4.0, 2.5)
            if a > 0:
                draw_center(screen, notes.notes_list()[13], font(17, italic=True), C.COL_TEXT_DIM, cx, C.SCREEN_H - 58, a)
        elif s == WRITE:
            fade = 1.0 if self.writing_fade is None else max(0.0, 1 - self.writing_fade / FADE)
            y = C.SCREEN_H / 2 - 60
            for line in self.lines[: self.current + 1]:
                visible = line.text[: int(line.shown)]
                draw_center(screen, visible, line.font, C.COL_TEXT, cx, y, 255 * fade)
                y += 44
        elif s == NOTE:
            self._draw_note(screen, t)
        elif s == NEXT:
            text = lang.t("next_attempt", n=self.run.attempt + 1)
            draw_center(screen, text, font(22), C.COL_TEXT, cx, C.SCREEN_H / 2 - 12, page_alpha(t, 2.5))
        elif s == RESULT:
            self._draw_result(screen, t)
        elif s == CREDITS:
            # cahayanya padam pelan-pelan, lalu kredit muncul di kegelapan
            self._light_bg(screen, 1.0 - smooth(t / CREDITS_DARK))
            a = page_alpha(t - (CREDITS_DARK - 0.8), 4.0)
            y = C.SCREEN_H / 2 - 70
            for text, size, bright in notes.credits():
                color = C.COL_TEXT if bright else C.COL_TEXT_DIM
                y += draw_center(screen, text, font(size), color, cx, y, a) + 6
        self.app.effects.grain(screen, t)

    def _light_bg(self, screen, level):
        """Latar cahaya hangat, level 0 (gelap) sampai 1 (paling terang)."""
        if level <= 0:
            return
        screen.fill(scale(C.COL_LIGHT, 0.82 * level))
        self.app.effects.vignette(screen, 0)

    def _draw_light(self, screen, t):
        """Untuk pertama kalinya di seluruh game, layarnya terang. Kamu berjalan masuk ke cahaya."""
        k = smooth((t - 0.4) / 3.2) * (1.0 - smooth((t - 5.2) / 2.6))
        self._light_bg(screen, k)
        body = tuple(int(p + (s - p) * k) for p, s in zip(C.COL_PLAYER, (46, 41, 33)))
        y = C.SCREEN_H * 0.64 - 60 * smooth(t / 6.5)
        figure(screen, C.SCREEN_W / 2, y, -math.pi / 2, body, C.PLAYER_RADIUS)

    def _draw_note(self, screen, t):
        a = min(255.0, 255 * t / 0.8)
        cx = C.SCREEN_W / 2
        # sengaja tidak memberi tahu di mana catatan ini akan muncul: biar ditemukan sendiri
        draw_center(screen, lang.t("note_prompt"), font(17), C.COL_TEXT_DIM, cx, 190, a)
        fnt = font(22, italic=True)
        cursor = "|" if int(t * 2) % 2 == 0 else " "
        text = self.note + cursor
        draw_center(screen, text, fnt, C.COL_TEXT, cx, 262, a)
        draw_center(screen, lang.t("note_keys"), font(13), (80, 77, 72), cx, C.SCREEN_H - 40, a)

    def _draw_result(self, screen, t):
        """Hasil percobaan, di dalam cahaya: kamu benar-benar keluar, setidaknya untuk sekarang."""
        run = self.run
        self._light_bg(screen, smooth(t / 2.0))
        a = 255 * smooth((t - 0.6) / 1.2)
        cx = C.SCREEN_W / 2
        y = 64
        y += draw_center(screen, lang.t("result_title", name=run.difficulty.name), font(26), INK, cx, y, a) + 22
        mins, secs = divmod(int(run.play_time), 60)
        total_notes = C.FRAGMENTS_PER_FLOOR * C.FLOOR_COUNT
        retried = lang.t("result_retried", n=run.retries) if run.retries else ""
        line1 = lang.t("result_line1", time=f"{mins}:{secs:02d}", deaths=run.deaths, retried=retried,
                       notes=len(run.notes), total=total_notes)
        line2 = lang.t("result_line2", pings=run.pings, stones=run.stones_thrown, walls=run.walls_broken,
                       banished=run.banished)
        y += draw_center(screen, line1, font(15), INK, cx, y, a) + 8
        y += draw_center(screen, line2, font(13), INK_DIM, cx, y, a) + 44

        if run.assisted:
            draw_center(screen, lang.t("assisted"), font(14), INK_DIM, cx, y, a)
        elif self.new:
            y += draw_center(screen, lang.t("new_achievements"), font(17), INK, cx, y, a) + 14
            name_font, desc_font = font(15), font(13)
            for i, ach in enumerate(self.new):
                show = t - (ACH_START + i * ACH_GAP)
                if show < 0:
                    break
                k = min(1.0, show / 0.4) * a / 255
                label = f"{ach.name}  —  {ach.desc}"
                w = name_font.size(ach.name)[0] + desc_font.size(f"  —  {ach.desc}")[0]
                x = cx - w / 2
                dot = pygame.Surface((8, 8), pygame.SRCALPHA)
                pygame.draw.circle(dot, INK_MARK, (4, 4), 3)
                dot.set_alpha(int(255 * k))
                screen.blit(dot, (int(x - 18), int(y + 5)))
                img = name_font.render(ach.name, True, INK)
                img.set_alpha(int(255 * k))
                screen.blit(img, (x, y))
                rest = desc_font.render(label[len(ach.name):], True, INK_DIM)
                rest.set_alpha(int(255 * k))
                screen.blit(rest, (x + img.get_width(), y + 2))
                y += 26
        else:
            got = len(set(self.app.save.pencapaian) & set(achievements.BY_KEY))
            draw_center(screen, lang.t("no_new"), font(14), INK_DIM, cx, y, a)
            draw_center(screen, lang.t("achievements_total", got=got, total=len(achievements.ALL)), font(13),
                        INK_FAINT, cx, y + 24, a)
        if self.note_saved:
            draw_center(screen, lang.t("note_saved"), font(13), INK_FAINT, cx, C.SCREEN_H - 70, a)
        draw_center(screen, lang.t("continue_hint"), font(13), INK_FAINT, cx, C.SCREEN_H - 40, a)
