"""Daftar pencapaian, dibuka dari layar judul."""

import pygame

from .. import achievements
from .. import config as C
from .. import lang
from ..render.draw import scale
from ..render.text import draw_center, draw_left, font


class AchievementsScene:
    def __init__(self, app):
        self.app = app
        self.t = 0.0

    def enter(self):
        pygame.mouse.set_visible(True)

    def handle_event(self, ev):
        back = ev.type == pygame.KEYDOWN and ev.key in (pygame.K_ESCAPE, pygame.K_RETURN, pygame.K_SPACE)
        if back or (ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1):
            self.app.audio.ui("click")
            self.app.go_title()

    def update(self, dt):
        self.t += dt

    def draw(self, screen):
        save = self.app.save
        screen.fill(C.COL_BG)
        got = set(save.pencapaian)
        total = len(achievements.ALL)
        draw_center(screen, lang.t("achievements_title"), font(24), C.COL_TEXT, C.SCREEN_W / 2, 40)
        count = lang.t("achievements_count", got=len(got & set(achievements.BY_KEY)), total=total)
        draw_center(screen, count, font(13), C.COL_TEXT_DIM, C.SCREEN_W / 2, 74)
        name_font, desc_font = font(15), font(13)
        x_name, x_desc = 150, 390
        y = 108
        for a in achievements.ALL:
            unlocked = a.key in got
            color = C.COL_TEXT if unlocked else (78, 75, 70)
            if unlocked:
                pygame.draw.circle(screen, C.COL_SONAR, (x_name - 16, y + 9), 3)
            else:
                pygame.draw.circle(screen, (60, 57, 53), (x_name - 16, y + 9), 3, 1)
            draw_left(screen, a.name, name_font, color, x_name, y)
            desc = a.desc
            prog = achievements.progress(save, a)
            if prog is not None and not unlocked:
                desc += f"  ({prog[0]}/{prog[1]})"
            draw_left(screen, desc, desc_font, scale(C.COL_TEXT_DIM, 1.0 if unlocked else 0.75), x_desc, y + 2)
            y += 27
        draw_center(screen, lang.t("back_hint"), font(13), (70, 67, 63), C.SCREEN_W / 2, C.SCREEN_H - 34)
        self.app.effects.grain(screen, self.t)
        self.app.effects.vignette(screen, 0)
