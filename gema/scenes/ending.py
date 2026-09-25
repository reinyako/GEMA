"""Ending: pemain menulis catatan pertama untuk percobaan berikutnya."""

import pygame

from .. import config as C
from .. import notes
from ..render.text import TypeText, draw_center, font

LINE_PAUSE = 1.4
PAGE_HOLD = 3.0
FADE = 1.5


def page_alpha(t, hold):
    if t < FADE:
        return 255 * t / FADE
    if t < FADE + hold:
        return 255
    return max(0.0, 255 * (1 - (t - FADE - hold) / FADE))


class EndingScene:
    def __init__(self, app, run):
        self.app = app
        self.run = run
        app.save.ending += 1
        app.save.write()
        self.lines = [TypeText(text, size=22, speed=13.0, hold=1e9) for text in notes.ENDING_LINES]
        self.current = 0
        self.wait = 0.0
        self.stage = 0       # 0 menulis, 1 percobaan berikutnya, 2 kredit
        self.stage_t = 0.0
        self.writing_fade = None

    def enter(self):
        pygame.mouse.set_visible(False)
        self.app.audio.stop_all()

    def handle_event(self, ev):
        if ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
            self.app.go_title()
        elif ev.type == pygame.KEYDOWN and ev.key in (pygame.K_RETURN, pygame.K_SPACE):
            if self.stage > 0:
                self._next_stage()

    def _next_stage(self):
        self.stage += 1
        self.stage_t = 0.0
        if self.stage > 2:
            self.app.go_title()

    def update(self, dt):
        self.stage_t += dt
        if self.stage == 0:
            if self.writing_fade is not None:
                self.writing_fade += dt
                if self.writing_fade >= FADE:
                    self._next_stage()
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
        elif self.stage == 1 and self.stage_t >= FADE * 2 + 2.5:
            self._next_stage()
        elif self.stage == 2 and self.stage_t >= FADE * 2 + 4.0:
            self._next_stage()

    def draw(self, screen):
        screen.fill((0, 0, 0))
        cx = C.SCREEN_W / 2
        if self.stage == 0:
            fade = 1.0 if self.writing_fade is None else max(0.0, 1 - self.writing_fade / FADE)
            y = C.SCREEN_H / 2 - 60
            for line in self.lines[: self.current + 1]:
                visible = line.text[: int(line.shown)]
                draw_center(screen, visible, line.font, C.COL_TEXT, cx, y, 255 * fade)
                y += 44
        elif self.stage == 1:
            text = f"Percobaan ke-{self.run.attempt + 1}."
            draw_center(screen, text, font(22), C.COL_TEXT, cx, C.SCREEN_H / 2 - 12, page_alpha(self.stage_t, 2.5))
        elif self.stage == 2:
            a = page_alpha(self.stage_t, 4.0)
            y = C.SCREEN_H / 2 - 70
            for text, size, bright in notes.CREDITS:
                color = C.COL_TEXT if bright else C.COL_TEXT_DIM
                y += draw_center(screen, text, font(size), color, cx, y, a) + 6
