"""Senter: kerucut cahaya yang terhalang dinding, baterai, dan kedipan saat baterai lemah."""

import math

from .. import config as C
from .raycast import angle_diff, cast, line_of_sight


class Flashlight:
    def __init__(self, battery):
        self.battery = battery
        self.held = False        # tombol ditahan dan baterai masih ada
        self.on = False          # benar-benar memancarkan cahaya frame ini
        self.flicker_off = False
        self.flicker_timer = 0.0
        self.origin = (0.0, 0.0)
        self.aim = 0.0
        self.range = C.LIGHT_RANGE_MAX
        self.poly = []
        self._input_prev = False

    @property
    def fraction(self):
        return self.battery / C.BATTERY_MAX

    def intensity(self):
        return 0.55 + 0.45 * self.fraction

    def update(self, dt, pressed, x, y, aim, maze, drain, rng, sfx):
        if pressed and not self._input_prev:
            sfx.append(("click" if self.battery > 0 else "click_dead", None, None))
        elif not pressed and self._input_prev and self.battery > 0:
            sfx.append(("click", None, None))
        self._input_prev = pressed

        self.held = pressed and self.battery > 0
        if self.held:
            self.battery = max(0.0, self.battery - drain * dt)
            if self.battery <= 0:
                self.held = False
                sfx.append(("click_dead", None, None))

        if self.held and self.battery < C.FLICKER_THRESHOLD:
            self.flicker_timer -= dt
            if self.flicker_timer <= 0:
                self.flicker_off = not self.flicker_off
                weak = 1.0 - self.battery / C.FLICKER_THRESHOLD
                if self.flicker_off:
                    self.flicker_timer = rng.uniform(0.04, 0.10 + 0.12 * weak)
                else:
                    self.flicker_timer = rng.uniform(0.15, 0.9 - 0.5 * weak)
        else:
            self.flicker_off = False
            self.flicker_timer = 0.0

        self.on = self.held and not self.flicker_off
        self.origin = (x, y)
        self.aim = aim
        self.range = C.LIGHT_RANGE_MIN + (C.LIGHT_RANGE_MAX - C.LIGHT_RANGE_MIN) * self.fraction
        if self.on:
            n = C.LIGHT_RAYS
            half = C.LIGHT_HALF_ANGLE
            poly = [(x, y)]
            for i in range(n + 1):
                a = aim - half + 2 * half * i / n
                dx, dy = math.cos(a), math.sin(a)
                d = cast(maze, x, y, dx, dy, self.range)
                poly.append((x + dx * d, y + dy * d))
            self.poly = poly
        else:
            self.poly = []

    def lit(self, px, py, maze, margin=0.0):
        """True kalau titik (px, py) sedang terkena cahaya senter."""
        if not self.on:
            return False
        ox, oy = self.origin
        dx, dy = px - ox, py - oy
        d = math.hypot(dx, dy)
        if d > self.range + margin:
            return False
        if d < 1.0:
            return True
        slack = math.asin(min(1.0, margin / d)) if margin > 0 else 0.0
        if angle_diff(math.atan2(dy, dx), self.aim) > C.LIGHT_HALF_ANGLE + slack:
            return False
        return line_of_sight(maze, ox, oy, px, py)

    def central(self, px, py):
        """True kalau titik berada di bagian tengah kerucut (tempat senter tidak pernah berbohong)."""
        if not self.on:
            return False
        ox, oy = self.origin
        a = math.atan2(py - oy, px - ox)
        return angle_diff(a, self.aim) < C.LIGHT_HALF_ANGLE * 0.4
