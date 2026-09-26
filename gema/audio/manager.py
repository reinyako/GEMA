"""Pengelola audio: channel, panning stereo, dan loop. Kalau audio gagal, game tetap jalan tanpa suara."""

import math
import random

import numpy as np
import pygame

from .. import config as C
from . import synth

LOOP_SLOTS = (
    "drone_a", "drone_b", "heart", "frag0", "frag1", "frag2", "exit",
    "lis0", "lis1", "lis2", "lis3", "lis4", "lis5", "breath", "ui", "break",
)


def pan_gains(pan, volume):
    """Panning equal-power. pan -1 (kiri) .. 1 (kanan)."""
    a = (max(-1.0, min(1.0, pan)) + 1.0) * math.pi / 4
    return min(1.0, volume * math.cos(a) * 1.414), min(1.0, volume * math.sin(a) * 1.414)


def spatial(src_x, src_y, lx, ly, max_dist, volume):
    """Volume kiri-kanan untuk sumber di (src_x, src_y) yang didengar dari (lx, ly)."""
    dx = src_x - lx
    d = math.hypot(dx, src_y - ly)
    if d >= max_dist:
        return 0.0, 0.0
    gain = volume * (1.0 - d / max_dist) ** 1.6
    return pan_gains(dx / 260.0 * 0.9, gain)


class Audio:
    def __init__(self, enabled=True, seed=7):
        self.enabled = False
        self.sounds = {}
        self._loops = {}
        self._rng = random.Random(seed)
        if not enabled:
            return
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(44100, -16, 2, 512)
            freq, fmt, channels = pygame.mixer.get_init()
            pygame.mixer.set_num_channels(40)
            pygame.mixer.set_reserved(len(LOOP_SLOTS))
            raw = synth.build_all(freq, seed)
            self.sounds = {k: self._convert(v, fmt, channels) for k, v in raw.items()}
            self.enabled = True
        except Exception as exc:  # noqa: BLE001 - perangkat audio bisa gagal dengan banyak cara
            print(f"[GEMA] Audio dimatikan: {exc}")
            self.enabled = False

    @staticmethod
    def _to_sound(data, fmt, channels):
        data = np.clip(data, -1.0, 1.0)
        if data.ndim == 1 and channels >= 2:
            data = np.column_stack([data] * channels)
        elif data.ndim == 2 and channels == 1:
            data = data.mean(axis=1)
        elif data.ndim == 2 and channels > 2:
            data = np.column_stack([data[:, 0], data[:, 1]] + [data.mean(axis=1)] * (channels - 2))
        if abs(fmt) == 16:
            arr = (data * 32767).astype(np.int16)
        elif abs(fmt) == 8:
            arr = ((data * 127) + 128).astype(np.uint8)
        else:
            arr = data.astype(np.float32)
        return pygame.sndarray.make_sound(np.ascontiguousarray(arr))

    def _convert(self, value, fmt, channels):
        if isinstance(value, list):
            return [self._to_sound(v, fmt, channels) for v in value]
        return self._to_sound(value, fmt, channels)

    def _get(self, name):
        s = self.sounds.get(name)
        if isinstance(s, list):
            return self._rng.choice(s)
        return s

    # --- sekali putar ------------------------------------------------------
    def play(self, name, left=1.0, right=None):
        if not self.enabled:
            return
        sound = self._get(name)
        if sound is None:
            return
        base = C.VOLUME.get(name, 0.3)
        right = left if right is None else right
        channel = pygame.mixer.find_channel(True)
        if channel is None:
            return
        channel.play(sound)
        channel.set_volume(left * base, right * base)

    def ui(self, name="click"):
        """Suara menu. Punya channel sendiri, jadi tidak terpotong oleh stop_all() atau jeda."""
        if not self.enabled:
            return
        ch = pygame.mixer.Channel(LOOP_SLOTS.index("ui"))
        ch.play(self.sounds[name])
        ch.unpause()
        v = C.VOLUME.get(name, 0.3)
        ch.set_volume(v, v)

    def play_at(self, name, x, y, lx, ly, max_dist=700.0):
        left, right = spatial(x, y, lx, ly, max_dist, 1.0)
        if left + right > 0.01:
            self.play(name, left, right)

    def beat(self, volume):
        """Detak jantung selalu mono: pemain tahu bahaya dekat, tapi tidak tahu arahnya."""
        if not self.enabled:
            return
        ch = pygame.mixer.Channel(LOOP_SLOTS.index("heart"))
        ch.play(self.sounds["heart"])
        v = volume * C.VOLUME["heart"]
        ch.set_volume(v, v)

    # --- loop --------------------------------------------------------------
    def set_loop(self, slot, name, left, right=None):
        if not self.enabled:
            return
        right = left if right is None else right
        ch = pygame.mixer.Channel(LOOP_SLOTS.index(slot))
        base = C.VOLUME.get(name, 0.3)
        if left + right < 0.002:
            if self._loops.get(slot):
                ch.stop()
                self._loops[slot] = None
            return
        if self._loops.get(slot) != name or not ch.get_busy():
            ch.play(self.sounds[name], loops=-1)
            self._loops[slot] = name
        ch.set_volume(min(1.0, left * base), min(1.0, right * base))

    def stop_loop(self, slot):
        self.set_loop(slot, "", 0.0)

    def stop_all(self):
        """Menghentikan semua suara kecuali suara menu yang sedang berbunyi."""
        if not self.enabled:
            return
        ui = LOOP_SLOTS.index("ui")
        for i in range(pygame.mixer.get_num_channels()):
            if i != ui:
                pygame.mixer.Channel(i).stop()
        self._loops.clear()

    def pause(self):
        if self.enabled:
            pygame.mixer.pause()

    def unpause(self):
        if self.enabled:
            pygame.mixer.unpause()
