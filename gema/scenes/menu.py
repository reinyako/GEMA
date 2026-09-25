"""Menu vertikal sederhana yang bisa dipakai dengan keyboard dan mouse."""

import pygame

from .. import config as C
from ..render.draw import scale
from ..render.text import font


class Menu:
    def __init__(self, items, y, spacing=40, size=24, selected=0, subtitles=None, audio=None):
        self.items = list(items)
        self.audio = audio  # kalau diisi, memilih item berbunyi "cetik" seperti senter
        self.subtitles = subtitles
        self.y = y
        self.spacing = spacing
        self.font = font(size)
        self.sub_font = font(14)
        self.selected = selected
        self.rects = []

    def handle_event(self, ev):
        """Mengembalikan indeks yang dipilih, atau None."""
        if ev.type == pygame.KEYDOWN:
            if ev.key in (pygame.K_UP, pygame.K_w):
                self.selected = (self.selected - 1) % len(self.items)
            elif ev.key in (pygame.K_DOWN, pygame.K_s):
                self.selected = (self.selected + 1) % len(self.items)
            elif ev.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
                return self._choose(self.selected)
        elif ev.type == pygame.MOUSEMOTION:
            for i, r in enumerate(self.rects):
                if r.collidepoint(ev.pos):
                    self.selected = i
        elif ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
            for i, r in enumerate(self.rects):
                if r.collidepoint(ev.pos):
                    self.selected = i
                    return self._choose(i)
        return None

    def _choose(self, i):
        if self.audio is not None:
            self.audio.ui("click")
        return i

    def draw(self, screen, alpha=255, item_alpha=None):
        """item_alpha: pengali terang (0..1) per item, misalnya untuk efek kedip."""
        self.rects = []
        cx = C.SCREEN_W // 2
        y = self.y
        for i, item in enumerate(self.items):
            active = i == self.selected
            a = int(alpha * (item_alpha[i] if item_alpha else 1.0))
            color = C.COL_TEXT if active else C.COL_TEXT_DIM
            img = self.font.render(item, True, color)
            img.set_alpha(a)
            rect = img.get_rect(midtop=(cx, y))
            screen.blit(img, rect)
            if active:
                pygame.draw.circle(screen, scale(C.COL_SONAR, a / 255), (rect.left - 16, rect.centery), 3)
            height = rect.height
            if self.subtitles and self.subtitles[i]:
                sub = self.sub_font.render(self.subtitles[i], True, C.COL_TEXT_DIM if active else (70, 67, 63))
                sub.set_alpha(a)
                srect = sub.get_rect(midtop=(cx, rect.bottom + 2))
                screen.blit(sub, srect)
                height += srect.height + 2
            self.rects.append(rect.inflate(160, 8))
            y += max(self.spacing, height + 14)
