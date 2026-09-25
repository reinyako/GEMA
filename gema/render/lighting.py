"""Peta cahaya: kerucut senter, aura redup di sekitar pemain, dan celah cahaya pintu."""

import numpy as np
import pygame

from .. import config as C


def radial_gradient(radius, color, power=1.0):
    size = radius * 2
    y, x = np.ogrid[:size, :size]
    d = np.sqrt((x - radius + 0.5) ** 2 + (y - radius + 0.5) ** 2) / radius
    k = np.clip(1.0 - d, 0.0, 1.0) ** power
    arr = np.zeros((size, size, 3), dtype=np.uint8)
    for i in range(3):
        arr[..., i] = (color[i] * k).astype(np.uint8)
    return pygame.surfarray.make_surface(arr.transpose(1, 0, 2))


class Lighting:
    def __init__(self):
        self.light = pygame.Surface((C.SCREEN_W, C.SCREEN_H))
        self.rmax = int(C.LIGHT_RANGE_MAX) + 4
        self.cone = pygame.Surface((self.rmax * 2, self.rmax * 2))
        self._grad_full = radial_gradient(self.rmax, (255, 255, 255), power=0.75)
        self._grad_cache = {}
        self.aura = radial_gradient(C.AURA_RADIUS, C.COL_AURA, power=1.3)
        self.exit_glow = radial_gradient(56, (130, 112, 80), power=1.6)

    def _gradient(self, r):
        key = max(8, int(r) // 4 * 4)
        g = self._grad_cache.get(key)
        if g is None:
            g = pygame.transform.smoothscale(self._grad_full, (key * 2, key * 2))
            self._grad_cache[key] = g
        return g, key

    def build(self, camx, camy, floor):
        light = self.light
        light.fill((0, 0, 0))
        fl = floor.flashlight
        rm = self.rmax
        if fl.on and len(fl.poly) >= 3:
            ox, oy = fl.origin
            k = fl.intensity()
            color = tuple(int(c * k) for c in C.COL_LIGHT)
            cone = self.cone
            cone.fill((0, 0, 0))
            pygame.draw.polygon(cone, color, [(px - ox + rm, py - oy + rm) for px, py in fl.poly])
            grad, r = self._gradient(fl.range + 4)
            cone.blit(grad, (rm - r, rm - r), special_flags=pygame.BLEND_MULT)
            light.blit(cone, (ox - camx - rm, oy - camy - rm), special_flags=pygame.BLEND_ADD)
        p = floor.player
        a = C.AURA_RADIUS
        light.blit(self.aura, (p.x - camx - a, p.y - camy - a), special_flags=pygame.BLEND_ADD)
        if floor.exit.open:
            e = floor.exit
            g = self.exit_glow.get_width() // 2
            light.blit(self.exit_glow, (e.x - camx - g, e.y - camy - g), special_flags=pygame.BLEND_ADD)
        return light
