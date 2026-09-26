"""Pengaturan, dibuka dari layar judul. Untuk sekarang isinya bahasa."""

import pygame

from .. import config as C
from .. import lang
from ..render.text import draw_center, font
from .menu import Menu


class SettingsScene:
    def __init__(self, app):
        self.app = app
        self.t = 0.0
        self.menu = Menu(self._labels(), y=200, spacing=44, audio=app.audio)

    def _labels(self):
        return [f"{lang.t('setting_language')}: {lang.NAMES[lang.current]}", lang.t("back")]

    def enter(self):
        pygame.mouse.set_visible(True)

    def handle_event(self, ev):
        if ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
            self.app.go_title()
            return
        choice = self.menu.handle_event(ev)
        if choice == 0:
            codes = lang.CODES
            code = codes[(codes.index(lang.current) + 1) % len(codes)]
            lang.set_lang(code)
            self.app.save.bahasa = code
            self.app.save.write()
            self.menu.items = self._labels()
        elif choice == 1:
            self.app.go_title()

    def update(self, dt):
        self.t += dt

    def draw(self, screen):
        screen.fill(C.COL_BG)
        draw_center(screen, lang.t("settings_title"), font(24), C.COL_TEXT, C.SCREEN_W / 2, 110)
        self.menu.draw(screen)
        draw_center(screen, lang.t("back_hint"), font(13), (70, 67, 63), C.SCREEN_W / 2, C.SCREEN_H - 40)
        self.app.effects.grain(screen, self.t)
        self.app.effects.vignette(screen, 0)
