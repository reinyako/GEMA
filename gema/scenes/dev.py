"""Menu mode dev: dipakai di layar judul dan di menu jeda."""

import pygame

from .. import config as C
from ..dev import OPTIONS
from ..render.text import draw_center, font
from .menu import Menu

KEYS_HELP = [
    "F5: ambil semua fragmen lantai ini",
    "F6: lompat ke pintu keluar",
    "F3: overlay debug",
]


class DevMenu:
    def __init__(self, dev, audio=None, y=150):
        self.dev = dev
        self.menu = Menu(self._labels(), y=y, spacing=40, size=22, audio=audio)

    def _labels(self):
        marks = [f"[{'x' if getattr(self.dev, key) else ' '}] {label}" for key, label, _ in OPTIONS]
        return marks + ["Kembali"]

    def handle_event(self, ev):
        """Mengembalikan True kalau menu ditutup."""
        if ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
            return True
        choice = self.menu.handle_event(ev)
        if choice is None:
            return False
        if choice >= len(OPTIONS):
            return True
        key = OPTIONS[choice][0]
        setattr(self.dev, key, not getattr(self.dev, key))
        self.menu.items = self._labels()
        return False

    def draw(self, screen):
        draw_center(screen, "Mode dev", font(26), C.COL_TEXT, C.SCREEN_W / 2, 80)
        self.menu.draw(screen)
        y = 360
        for line in KEYS_HELP:
            y += draw_center(screen, line, font(13), C.COL_TEXT_DIM, C.SCREEN_W / 2, y) + 4


class DevScene:
    def __init__(self, app):
        self.app = app
        self.t = 0.0
        self.menu = DevMenu(app.dev, app.audio)

    def enter(self):
        pygame.mouse.set_visible(True)

    def handle_event(self, ev):
        if self.menu.handle_event(ev):
            self.app.go_title()

    def update(self, dt):
        self.t += dt

    def draw(self, screen):
        screen.fill(C.COL_BG)
        self.menu.draw(screen)
        self.app.effects.grain(screen, self.t)
