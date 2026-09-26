"""Scene bermain: menjalankan satu lantai, menu jeda, kematian, dan pindah lantai."""

import math
import random

import pygame

from .. import config as C
from .. import lang
from .. import notes
from ..achievements import record
from ..audio.soundscape import Soundscape
from ..render.draw import FloorRenderer
from ..render.effects import Shake
from ..render.text import TypeText, draw_center, draw_left, font, wrap
from ..world.floor import Floor
from .dev import DevMenu
from .interlude import InterludeScene
from .menu import Menu

PLAYING = "main"
DYING = "mati"
LEAVING = "keluar"


class PlayScene:
    def __init__(self, app, run):
        self.app = app
        self.run = run
        self.floor = Floor(run, C.floor_rules(run.floor, run.difficulty))
        self.floor.dev = app.dev
        self.renderer = FloorRenderer(self.floor)
        self.soundscape = Soundscape(app.audio)
        self.controller = app.make_controller()
        self.rng = random.Random(run.seed ^ 0x5EED)
        self.state = PLAYING
        self.timer = 0.0
        self.t = 0.0
        self.shake = Shake()
        self.catcher = None      # makhluk yang menangkap (atau menyentuh, di mode kebal)
        self.hit_flash = 0.0     # sisa waktu efek sentuhan di mode kebal
        self.heartbeat_done = False
        self.paused = False
        self.showing_notes = False
        self.showing_dev = False
        self.pause_actions = ["resume", "notes"] + (["dev"] if app.dev.enabled else []) + ["title"]
        labels = {"resume": lang.t("resume"), "notes": lang.t("notes"), "dev": lang.t("menu_dev"),
                  "title": lang.t("to_title")}
        self.pause_menu = Menu([labels[a] for a in self.pause_actions], y=200, audio=app.audio)
        self.dev_menu = DevMenu(app.dev, app.audio)
        self.note = None
        self.hint = 9.0 if run.floor == 1 else 0.0
        self.debug = False
        p = self.floor.player
        self.cam = (p.x - C.SCREEN_W / 2, p.y - C.SCREEN_H / 2)
        app.save.record_floor(run.difficulty.key, min(run.floor, C.FLOOR_COUNT))

    def enter(self):
        pygame.mouse.set_visible(self.paused)

    def aim_at(self, mouse_pos):
        p = self.floor.player
        wx, wy = mouse_pos[0] + self.cam[0], mouse_pos[1] + self.cam[1]
        if math.hypot(wx - p.x, wy - p.y) < 2:
            return p.aim
        return math.atan2(wy - p.y, wx - p.x)

    # --- event -------------------------------------------------------------
    def set_paused(self, paused):
        self.paused = paused
        self.showing_notes = False
        self.showing_dev = False
        pygame.mouse.set_visible(paused)
        if paused:
            self.app.audio.pause()
        else:
            self.app.audio.unpause()

    def handle_event(self, ev):
        if self.paused:
            self._pause_event(ev)
            return
        if ev.type == pygame.KEYDOWN:
            if ev.key == pygame.K_ESCAPE and self.state == PLAYING:
                self.set_paused(True)
                return
            # overlay debug memperlihatkan peta, monster, dan angka: hanya untuk mode dev
            if ev.key == pygame.K_F3 and self.app.dev.enabled:
                self.debug = not self.debug
            if self.app.dev.enabled and self.state == PLAYING:
                if ev.key == pygame.K_F5:
                    self.floor.debug_collect_all()
                    self.run.assisted = True
                elif ev.key == pygame.K_F6:
                    self.floor.debug_to_exit()
                    self.run.assisted = True
        self.controller.handle_event(ev)

    def _pause_event(self, ev):
        if self.showing_dev:
            if self.dev_menu.handle_event(ev):
                self.showing_dev = False
            return
        if self.showing_notes:
            done = ev.type == pygame.KEYDOWN and ev.key in (pygame.K_ESCAPE, pygame.K_RETURN, pygame.K_SPACE)
            clicked = ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1
            if done or clicked:
                if clicked or ev.key != pygame.K_ESCAPE:
                    self.app.audio.ui("click")
                self.showing_notes = False
            return
        if ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
            self.set_paused(False)
            return
        choice = self.pause_menu.handle_event(ev)
        if choice is None:
            return
        action = self.pause_actions[choice]
        if action == "resume":
            self.set_paused(False)
        elif action == "notes":
            self.showing_notes = True
        elif action == "dev":
            self.showing_dev = True
        elif action == "title":
            record(self.app.save, self.run, finished=False)
            self.app.audio.unpause()
            self.app.go_title()

    # --- update ------------------------------------------------------------
    def update(self, dt):
        if self.paused:
            return
        self.t += dt
        self.shake.update(dt)
        self.hit_flash = max(0.0, self.hit_flash - dt)
        if self.state == DYING:
            # Waktu berhenti: dunia diam, layar bergetar, makhluk yang menangkap terlihat.
            self.timer += dt
            if self.timer >= C.LAST_HEARTBEAT and not self.heartbeat_done:
                self.heartbeat_done = True
                self.app.audio.beat(1.0)
            self._update_camera()
            if self.timer >= C.HIT_STOP + C.DEATH_FADE + C.DEATH_BLACK:
                self._after_death()
            return
        if self.state == LEAVING:
            self.timer += dt
            if self.timer >= C.EXIT_FADE:
                self._leave()
            return

        f = self.floor
        if self.app.dev.any_active():
            self.run.assisted = True
        f.update(dt, self.controller.sample(self))
        for ev in f.events:
            if ev[0] == "note":
                self.note = TypeText(ev[1])
                self.run.notes.append(ev[1])
            elif ev[0] == "death":
                self._die(ev[1])
            elif ev[0] == "hit":
                self._god_hit(ev[1])
            elif ev[0] == "exit":
                self.state = LEAVING
                self.timer = 0.0
            elif ev[0] == "wall_broken":
                self.shake.add(0.35)
        f.events.clear()
        if f.break_tile is not None:
            self.shake.add(dt * 0.35)  # dinding bergetar selama dihancurkan
        if self.state == PLAYING:
            self.soundscape.update(dt, f)
        if self.note is not None:
            self.note.update(dt)
            if self.note.done:
                self.note = None
        self.hint = max(0.0, self.hint - dt)
        self._update_camera()

    def _update_camera(self):
        f = self.floor
        p = f.player
        sx = sy = 0.0
        s = f.stress.value
        if f.rules.tricks and s >= C.SWAY_STRESS:
            amp = (s - C.SWAY_STRESS) / (100 - C.SWAY_STRESS) * 3.0
            sx = math.sin(self.t * 0.9) * amp
            sy = math.cos(self.t * 0.7) * amp
        kx, ky = self.shake.offset()
        self.cam = (p.x - C.SCREEN_W / 2 + sx + kx, p.y - C.SCREEN_H / 2 + sy + ky)

    def _die(self, catcher):
        self.state = DYING
        self.timer = 0.0
        self.catcher = catcher
        self.heartbeat_done = False
        self.note = None
        self.soundscape.silence()
        self.app.audio.play("impact")
        self.shake.add(C.SHAKE_DEATH)
        self.run.lives -= 1
        self.run.deaths += 1
        self.app.save.kematian += 1
        self.app.save.write()

    def _after_death(self):
        run, app = self.run, self.app
        if run.lives <= 0 and run.difficulty.retry_floor:
            self._retry_floor()
            return
        if run.lives <= 0:
            new = record(app.save, run, finished=False)
            lines = [lang.t("attempt_over", n=run.attempt)] + [lang.t("new_achievement", name=a.name) for a in new]
            app.switch(InterludeScene(
                app, lines, then=app.go_title, duration=3.2 + 1.5 * len(new), size=22,
            ))
            return
        self.floor.respawn()
        self.state = PLAYING
        self.t = 0.0
        self.catcher = None
        self.shake.trauma = 0.0
        app.switch(InterludeScene(
            app, [self.rng.choice(notes.death_words())], then=lambda: app.switch(self),
            duration=1.8, lives=run.lives, max_lives=run.difficulty.lives,
        ))

    def _retry_floor(self):
        """Redup: nyawa habis tidak mengakhiri percobaan. Lantai ini diulang dari awal dengan labirin baru."""
        run, app = self.run, self.app
        if self.floor.taken:
            del run.notes[-self.floor.taken:]   # fragmen lantai ini akan ditemukan lagi
        run.retries += 1
        run.floor_retries += 1
        run.lives = run.difficulty.lives
        run.battery = C.BATTERY_MAX
        text = notes.retry_text(run.floor_retries)
        app.switch(InterludeScene(app, [text], then=lambda: app.go_floor_intro(run), duration=2.4))

    def _god_hit(self, catcher):
        """Mode kebal: efek tertangkap tetap muncul supaya bisa dites, tapi tidak mati."""
        self.catcher = catcher
        self.hit_flash = 0.7
        self.shake.add(C.SHAKE_GOD_HIT)
        self.app.audio.play("impact", 0.5)

    def _leave(self):
        from .ending import EndingScene

        self.app.audio.stop_all()
        self.run.battery = self.floor.flashlight.battery
        if self.floor.rules.final:
            self.app.switch(EndingScene(self.app, self.run))
            return
        self.run.floor += 1
        self.run.floor_retries = 0
        self.app.go_floor_intro(self.run)

    # --- gambar ------------------------------------------------------------
    def draw(self, screen):
        f = self.floor
        camx, camy = self.cam
        self.renderer.draw(screen, camx, camy, self.t)
        reveal = 0.0
        if self.state == DYING:
            reveal = 1.0
        elif self.hit_flash > 0:
            reveal = self.hit_flash / 0.7
        if reveal > 0:
            self.renderer.draw_catcher(screen, self.catcher, int(camx), int(camy), reveal)
        fx = self.app.effects
        fx.grain(screen, self.t)
        fx.vignette(screen, f.stress.value)
        if self.state == DYING:
            fx.red_pulse(screen, max(0.0, 1.0 - self.timer / (C.HIT_STOP + 0.3)) * 0.9)
        elif self.hit_flash > 0:
            fx.red_pulse(screen, self.hit_flash / 0.7 * 0.6)

        if self.note is not None:
            self.note.draw(screen, C.SCREEN_W / 2, C.SCREEN_H - 96)
        if self.hint > 0 and not self.paused:
            self._draw_hint(screen, min(1.0, self.hint / 2.0) * min(1.0, (9.0 - self.hint) / 1.5))
        if not self.paused and self.state == PLAYING:
            mx, my = pygame.mouse.get_pos()
            pygame.draw.circle(screen, (90, 86, 80), (mx, my), 3, 1)

        fade = max(0.0, 1.0 - self.t / 0.8)
        if self.state == DYING:
            fade = max(0.0, min(1.0, (self.timer - C.HIT_STOP) / C.DEATH_FADE))
        elif self.state == LEAVING:
            fade = min(1.0, self.timer / C.EXIT_FADE)
        fx.fade(screen, fade)

        if self.app.dev.any_active():
            img = font(12).render(f"DEV · {self.app.dev.summary()}", True, (150, 140, 70))
            screen.blit(img, (C.SCREEN_W - img.get_width() - 10, 8))
        if self.debug:
            self.renderer.draw_debug(screen, self.app.clock.get_fps())
        if self.paused:
            self._draw_pause(screen)

    def _draw_hint(self, screen, k):
        fnt = font(14)
        a = 255 * k * 0.8
        controls = notes.controls()[:7]
        pad = max(len(key) for key, _ in controls)
        y = C.SCREEN_H - 30 - len(controls) * 18
        for key, what in controls:
            draw_left(screen, f"{key:<{pad}}  {what}", fnt, C.COL_TEXT_DIM, 24, y, a)
            y += 18

    def _draw_pause(self, screen):
        shade = pygame.Surface((C.SCREEN_W, C.SCREEN_H), pygame.SRCALPHA)
        shade.fill((0, 0, 0, 200))
        screen.blit(shade, (0, 0))
        if self.showing_notes:
            self._draw_notes(screen)
            return
        if self.showing_dev:
            self.dev_menu.draw(screen)
            return
        draw_center(screen, lang.t("pause"), font(28), C.COL_TEXT, C.SCREEN_W / 2, 90)
        lives = self.run.lives
        max_lives = self.run.difficulty.lives
        gap = 18
        x0 = C.SCREEN_W / 2 - (max_lives - 1) * gap / 2
        for i in range(max_lives):
            color = C.COL_TEXT if i < lives else (60, 57, 53)
            pygame.draw.circle(screen, color, (int(x0 + i * gap), 146), 4 if i < lives else 3, 0 if i < lives else 1)
        self._draw_tools(screen, 166)
        self.pause_menu.draw(screen)
        fnt = font(13)
        y = self.pause_menu.y + len(self.pause_menu.items) * 42 + 20
        controls = notes.controls()
        half = (len(controls) + 1) // 2
        for col, x in ((controls[:half], C.SCREEN_W / 2 - 230), (controls[half:], C.SCREEN_W / 2 + 20)):
            for i, (key, what) in enumerate(col):
                draw_left(screen, f"{key}: {what}", fnt, C.COL_TEXT_DIM, x, y + i * 18)

    def _draw_tools(self, screen, y):
        """Sisa kerikil dan dinding yang bisa dihancurkan, sebagai titik seperti nyawa (tanpa angka)."""
        f = self.floor
        groups = [(label, left, total) for label, left, total in (
            (lang.t("tool_stones"), f.stones_left, self.run.difficulty.stones),
            (lang.t("tool_walls"), f.breaks_left, self.run.difficulty.wall_breaks),
        ) if total > 0 and not f.rules.final]
        if not groups:
            return
        fnt = font(13)
        gap = 14
        widths = [fnt.size(label)[0] + 10 + total * gap for label, _, total in groups]
        x = C.SCREEN_W / 2 - (sum(widths) + 40 * (len(groups) - 1)) / 2
        for (label, left, total), w in zip(groups, widths):
            draw_left(screen, label, fnt, C.COL_TEXT_DIM, x, y - 8)
            lw = fnt.size(label)[0]
            for i in range(total):
                cx = int(x + lw + 10 + i * gap + 4)
                if i < left:
                    pygame.draw.circle(screen, C.COL_TEXT_DIM, (cx, y), 3)
                else:
                    pygame.draw.circle(screen, (60, 57, 53), (cx, y), 3, 1)
            x += w + 40

    def _draw_notes(self, screen):
        draw_center(screen, lang.t("notes"), font(24), C.COL_TEXT, C.SCREEN_W / 2, 50)
        fnt = font(16, italic=True)
        y = 100
        if not self.run.notes:
            draw_center(screen, lang.t("notes_none"), fnt, C.COL_TEXT_DIM, C.SCREEN_W / 2, y)
        for text in self.run.notes:
            for line in wrap(text, fnt, 780):
                y += draw_center(screen, line, fnt, C.COL_TEXT, C.SCREEN_W / 2, y)
            y += 8
        draw_center(screen, lang.t("back_hint"), font(13), C.COL_TEXT_DIM, C.SCREEN_W / 2, C.SCREEN_H - 36)
