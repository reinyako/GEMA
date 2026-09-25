"""Efek layar: vignette yang menyempit mengikuti stres, film grain, getaran, dan fade hitam."""

import math

import numpy as np
import pygame

from .. import config as C

VIGNETTE_LEVELS = 6


def _vignette(level, color=(0, 0, 0)):
    w, h = C.SCREEN_W // 4, C.SCREEN_H // 4
    y, x = np.ogrid[:h, :w]
    nx = (x - w / 2 + 0.5) / (w / 2)
    ny = (y - h / 2 + 0.5) / (h / 2)
    d = np.sqrt(nx * nx + ny * ny) / np.sqrt(2)
    inner = 0.52 - 0.075 * level
    strength = 150 + 20 * level
    alpha = (np.clip((d - inner) / (1.0 - inner), 0, 1) ** 1.4) * strength
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    surf.fill((*color, 0))
    px = pygame.surfarray.pixels_alpha(surf)
    px[:] = alpha.T.astype(np.uint8)
    del px
    return pygame.transform.smoothscale(surf, (C.SCREEN_W, C.SCREEN_H))


def _grain(rng):
    w, h = C.SCREEN_W // 2, C.SCREEN_H // 2
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    surf.fill((210, 205, 195, 0))
    px = pygame.surfarray.pixels_alpha(surf)
    px[:] = (rng.random((w, h)) ** 6 * 18).astype(np.uint8)
    del px
    return pygame.transform.scale(surf, (C.SCREEN_W, C.SCREEN_H))


class Effects:
    def __init__(self, seed=3):
        rng = np.random.default_rng(seed)
        self.vignettes = [_vignette(k) for k in range(VIGNETTE_LEVELS)]
        self.grains = [_grain(rng) for _ in range(4)]
        self.red = _vignette(2, color=(130, 12, 10))
        self.black = pygame.Surface((C.SCREEN_W, C.SCREEN_H))
        self.black.fill((0, 0, 0))

    def vignette(self, screen, stress):
        level = min(VIGNETTE_LEVELS - 1, int(stress / 100.0 * VIGNETTE_LEVELS))
        screen.blit(self.vignettes[level], (0, 0))

    def grain(self, screen, t):
        screen.blit(self.grains[int(t * 12) % len(self.grains)], (0, 0))

    def red_pulse(self, screen, amount):
        """Pinggiran layar berdenyut merah saat tertangkap."""
        if amount <= 0:
            return
        self.red.set_alpha(int(255 * min(1.0, amount)))
        screen.blit(self.red, (0, 0))

    def fade(self, screen, amount):
        if amount <= 0:
            return
        self.black.set_alpha(int(255 * min(1.0, amount)))
        screen.blit(self.black, (0, 0))


class Shake:
    """Getaran layar berbasis "trauma": kuat di awal lalu mereda dengan halus."""

    def __init__(self):
        self.trauma = 0.0
        self.t = 0.0

    def add(self, amount):
        self.trauma = min(1.0, self.trauma + amount)

    def update(self, dt):
        self.t += dt
        self.trauma = max(0.0, self.trauma - C.SHAKE_DECAY * dt)

    def offset(self):
        if self.trauma <= 0:
            return 0.0, 0.0
        k = self.trauma * self.trauma * C.SHAKE_MAX
        t = self.t
        return (
            k * (math.sin(t * 47.0) + math.sin(t * 29.0 + 1.3)) / 2,
            k * (math.sin(t * 41.0 + 2.1) + math.sin(t * 23.0 + 0.4)) / 2,
        )
