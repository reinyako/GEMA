"""Masukan pemain: dari keyboard dan mouse, atau dari bot untuk pengujian."""

import math
from dataclasses import dataclass

import pygame

from .world.maze import tile_center, tile_of


@dataclass
class InputState:
    move: tuple = (0.0, 0.0)
    run: bool = False
    aim: float = 0.0
    light: bool = False
    sonar: bool = False
    throw: bool = False       # lempar kerikil (sekali tekan)
    break_wall: bool = False  # hancurkan dinding (ditahan)


class HumanController:
    def __init__(self):
        self._sonar = False
        self._throw = False

    def handle_event(self, ev):
        if ev.type == pygame.KEYDOWN and ev.key == pygame.K_SPACE:
            self._sonar = True
        elif ev.type == pygame.KEYDOWN and ev.key == pygame.K_q:
            self._throw = True
        elif ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 3:
            self._sonar = True

    def sample(self, scene):
        keys = pygame.key.get_pressed()
        mx = (keys[pygame.K_d] or keys[pygame.K_RIGHT]) - (keys[pygame.K_a] or keys[pygame.K_LEFT])
        my = (keys[pygame.K_s] or keys[pygame.K_DOWN]) - (keys[pygame.K_w] or keys[pygame.K_UP])
        run = bool(keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT])
        light = bool(pygame.mouse.get_pressed()[0])
        inp = InputState((float(mx), float(my)), run, scene.aim_at(pygame.mouse.get_pos()), light, self._sonar,
                         throw=self._throw, break_wall=bool(keys[pygame.K_e]))
        self._sonar = False
        self._throw = False
        return inp


class BotController:
    """Bot sederhana untuk pengujian: berjalan ke fragmen/pintu terdekat sambil memakai alat secara acak."""

    def __init__(self, rng, navigate=True):
        self.rng = rng
        self.navigate = navigate
        self.sonar_timer = 1.0
        self.light_timer = 0.0
        self.light = False
        self.wander = (1.0, 0.0)
        self.wander_timer = 0.0
        self.aim = 0.0

    def handle_event(self, ev):
        pass

    def _goal(self, floor):
        """Tujuan tetap (fragmen terdekat lewat lorong, lalu pintu) sampai tercapai."""
        current = getattr(self, "_target", None)
        if current is not None and current in floor.fragments and not current.taken:
            return current.x, current.y
        options = [f for f in floor.fragments if not f.taken]
        if not options and floor.exit.open:
            options = [floor.exit]
        if not options:
            self._target = None
            return None
        p = floor.player
        dist = floor.maze.bfs(tile_of(p.x, p.y))
        self._target = min(options, key=lambda o: dist.get(tile_of(o.x, o.y), 1 << 30))
        return self._target.x, self._target.y

    def sample(self, scene, dt=1 / 60):
        floor = scene.floor
        p = floor.player
        move = (0.0, 0.0)
        goal = self._goal(floor) if self.navigate else None
        if goal is not None:
            route = floor.maze.path(tile_of(p.x, p.y), tile_of(*goal))
            if route and len(route) > 1:
                tx, ty = tile_center(route[1])
            else:
                tx, ty = goal
            move = (tx - p.x, ty - p.y)
        else:
            self.wander_timer -= dt
            if self.wander_timer <= 0:
                a = self.rng.uniform(0, math.tau)
                self.wander = (math.cos(a), math.sin(a))
                self.wander_timer = self.rng.uniform(0.5, 2.0)
            move = self.wander
        if math.hypot(*move) > 0.1:
            target = math.atan2(move[1], move[0])
            self.aim += ((target - self.aim + math.pi) % math.tau - math.pi) * 0.15

        self.sonar_timer -= dt
        sonar = self.sonar_timer <= 0
        if sonar:
            self.sonar_timer = self.rng.uniform(2.5, 6.0)
        self.light_timer -= dt
        if self.light_timer <= 0:
            self.light = self.rng.random() < 0.25
            self.light_timer = self.rng.uniform(0.3, 2.0)
        return InputState(move, self.rng.random() < 0.05, self.aim, self.light, sonar)
