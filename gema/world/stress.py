"""Meter stres tersembunyi (0-100). Tidak pernah ditampilkan, hanya terasa efeknya."""

from .. import config as C


class Stress:
    def __init__(self, floor_min=0.0):
        self.floor_min = floor_min
        self.value = floor_min

    def add(self, amount):
        self.value = min(100.0, max(self.floor_min, self.value + amount))

    def set_floor(self, floor_min):
        self.floor_min = floor_min
        self.value = max(self.value, floor_min)

    def update(self, dt, near_dist, dark_time, staring):
        rate = 0.0
        if near_dist < C.STRESS_NEAR_RANGE:
            rate += C.STRESS_NEAR_RATE * (1.0 - near_dist / C.STRESS_NEAR_RANGE)
        if dark_time > C.STRESS_DARK_DELAY:
            rate += C.STRESS_DARK_RATE
        if staring:
            rate += C.STRESS_STARE_RATE
        if rate == 0.0 and near_dist >= C.STRESS_SAFE_RANGE:
            rate = -C.STRESS_SAFE_RATE
        self.add(rate * dt)
