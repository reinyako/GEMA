"""Jendela, loop utama, dan pergantian scene."""

import argparse
import random

import pygame

from . import config as C
from .audio.manager import Audio
from .dev import DevSettings
from .input import HumanController
from .render.effects import Effects
from .run import Run
from .save import SaveData


def parse_args(argv=None):
    p = argparse.ArgumentParser(description="GEMA: horor psikologis top-down.")
    p.add_argument("--seed", type=int, help="kunci labirin supaya selalu sama (untuk laporan bug)")
    p.add_argument("--floor", type=int, default=1, choices=range(1, C.FINAL_FLOOR + 1),
                   help="mulai langsung dari lantai ini")
    p.add_argument("--difficulty", choices=[d.key for d in C.DIFFICULTIES], help="pilihan awal kesulitan")
    p.add_argument("--dev", "--debug", dest="dev", action="store_true",
                   help="mode dev: menu kebal/sonar tanpa jeda/senter tanpa batas, plus F5 dan F6")
    p.add_argument("--mute", action="store_true", help="main tanpa suara")
    return p.parse_args(argv)


class App:
    def __init__(self, args):
        self.args = args
        pygame.mixer.pre_init(44100, -16, 2, 512)
        pygame.init()
        pygame.display.set_caption("GEMA")
        try:
            self.screen = pygame.display.set_mode((C.SCREEN_W, C.SCREEN_H), pygame.SCALED | pygame.RESIZABLE)
        except pygame.error:
            self.screen = pygame.display.set_mode((C.SCREEN_W, C.SCREEN_H))
        self.clock = pygame.time.Clock()
        self.save = SaveData.load()
        self.audio = Audio(enabled=not args.mute)
        self.effects = Effects()
        self.make_controller = HumanController
        self.dev = DevSettings(enabled=args.dev)
        self.running = True
        self.scene = None
        self.go_title()

    # --- pergantian scene --------------------------------------------------
    def switch(self, scene):
        self.scene = scene
        scene.enter()

    def go_title(self):
        from .scenes.title import TitleScene

        self.audio.stop_all()
        self.switch(TitleScene(self))

    def start_run(self, difficulty):
        self.save.percobaan += 1
        self.save.write()
        seed = self.args.seed if self.args.seed is not None else random.randrange(1, 1 << 30)
        run = Run(difficulty=difficulty, seed=seed, attempt=self.save.percobaan, floor=self.args.floor)
        self.go_floor_intro(run)

    def go_floor_intro(self, run):
        from .scenes.interlude import InterludeScene
        from .scenes.play import PlayScene

        title = "Lantai" if run.floor >= C.FINAL_FLOOR else f"Lantai {run.floor}"
        self.audio.stop_all()
        self.switch(InterludeScene(
            self, [title], then=lambda: self.switch(PlayScene(self, run)),
            lives=run.lives, max_lives=run.difficulty.lives,
        ))

    # --- loop --------------------------------------------------------------
    def step(self, dt, events):
        for ev in events:
            if ev.type == pygame.QUIT:
                self.running = False
            elif ev.type == pygame.KEYDOWN and ev.key == pygame.K_F11:
                pygame.display.toggle_fullscreen()
            else:
                self.scene.handle_event(ev)
        self.scene.update(dt)
        self.scene.draw(self.screen)

    def run(self):
        while self.running:
            dt = min(self.clock.tick(C.FPS) / 1000.0, C.MAX_DT)
            self.step(dt, pygame.event.get())
            pygame.display.flip()
        pygame.quit()


def main(argv=None):
    App(parse_args(argv)).run()
