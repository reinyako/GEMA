"""Layar hitam di antara momen: intro lantai, setelah mati, dan akhir percobaan."""

import pygame

from .. import config as C
from ..render.text import draw_center, font

FADE = 0.7


class InterludeScene:
    def __init__(self, app, lines, then, duration=2.6, lives=None, max_lives=None, size=26):
        self.app = app
        self.lines = lines
        self.then = then
        self.duration = duration
        self.lives = lives
        self.max_lives = max_lives
        self.font = font(size)
        self.t = 0.0
        self.finished = False

    def enter(self):
        pygame.mouse.set_visible(False)

    def handle_event(self, ev):
        skip = ev.type == pygame.KEYDOWN and ev.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_ESCAPE)
        skip = skip or (ev.type == pygame.MOUSEBUTTONDOWN)
        if skip and self.t > 0.8:
            self.t = max(self.t, FADE + self.duration)

    def update(self, dt):
        self.t += dt
        if self.t >= FADE * 2 + self.duration and not self.finished:
            self.finished = True
            self.then()

    def _alpha(self):
        if self.t < FADE:
            return 255 * self.t / FADE
        if self.t < FADE + self.duration:
            return 255
        return max(0.0, 255 * (1 - (self.t - FADE - self.duration) / FADE))

    def draw(self, screen):
        screen.fill((0, 0, 0))
        a = self._alpha()
        total = len(self.lines) * (self.font.get_linesize() + 6)
        y = C.SCREEN_H / 2 - total / 2 - (14 if self.lives is not None else 0)
        for line in self.lines:
            y += draw_center(screen, line, self.font, C.COL_TEXT, C.SCREEN_W / 2, y, a) + 6
        if self.lives is not None and self.max_lives:
            gap = 18
            x0 = C.SCREEN_W / 2 - (self.max_lives - 1) * gap / 2
            for i in range(self.max_lives):
                color = C.COL_TEXT if i < self.lives else (45, 43, 40)
                dot = pygame.Surface((12, 12), pygame.SRCALPHA)
                pygame.draw.circle(dot, color, (6, 6), 4 if i < self.lives else 3, 0 if i < self.lives else 1)
                dot.set_alpha(int(a))
                screen.blit(dot, (x0 + i * gap - 6, y + 12))
