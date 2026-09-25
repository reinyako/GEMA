"""Ikon GEMA, digambar dengan kode seperti semua visual lain.

Huruf G dari titik-titik gema, sama seperti judul di layar pertama: gelombang sonar baru saja
lewat, jadi bagian yang baru tersentuh lebih terang. Dipakai untuk ikon jendela saat bermain,
dan oleh tools/make_icon.py untuk GEMA.exe.
"""

import math
import random

import numpy as np
import pygame

from .. import config as C
from .text import font

_SMALL = 48   # di bawah ukuran ini titiknya lebih besar dan tanpa grain
_TINY = 24    # di bawah ukuran ini huruf digambar utuh, bukan titik


def _to_array(surf):
    return pygame.surfarray.array3d(surf).transpose(1, 0, 2).astype(float)


def _to_surface(arr):
    return pygame.surfarray.make_surface(np.clip(arr, 0, 255).astype(np.uint8).transpose(1, 0, 2))


def _glyph(height):
    """Masker huruf G (0..1, indeks [y, x]), dipotong rapat dan setinggi height piksel."""
    img = font(int(height * 1.6), bold=True).render("G", True, (255, 255, 255))
    img = img.subsurface(img.get_bounding_rect())
    w, h = img.get_size()
    img = pygame.transform.smoothscale(img, (max(1, round(w * height / h)), height))
    return pygame.surfarray.array_alpha(img).T / 255.0


def _art(res, size):
    """Isi ikon persegi res x res (tanpa sudut membulat)."""
    small, tiny = size < _SMALL, size < _TINY
    canvas = np.zeros((res, res, 3))
    canvas[:] = C.COL_BG

    glyph = _glyph(int(res * (0.66 if small else 0.6)))
    gh, gw = glyph.shape
    x0, y0 = (res - gw) // 2, (res - gh) // 2

    # gelombang datang dari kiri bawah dan baru saja melewati seluruh huruf
    ox, oy = -res * 0.15, res * 1.15
    front = math.hypot(x0 + gw - ox, oy - y0) + res * 0.02

    def brightness(d):
        return np.maximum(0.4, np.exp(-(front - d) / (res * 0.75)))

    sonar = np.asarray(C.COL_SONAR, dtype=float)
    if tiny:
        y, x = np.mgrid[y0:y0 + gh, x0:x0 + gw]
        k = brightness(np.hypot(x - ox, y - oy))
        canvas[y0:y0 + gh, x0:x0 + gw] += (glyph * k)[..., None] * (sonar - C.COL_BG)
    else:
        # titik-titik kecil dengan sedikit acak, seperti huruf di layar judul
        layer = pygame.Surface((res, res))
        step = gh / (11 if small else 22)
        dot = step * (0.74 if small else 0.66)
        jitter = step * 0.22
        rng = random.Random(4)
        for gy in np.arange(step / 2, gh, step):
            for gx in np.arange(step / 2, gw, step):
                if glyph[int(gy), int(gx)] <= 0.5:
                    continue
                px = x0 + gx + rng.uniform(-jitter, jitter)
                py = y0 + gy + rng.uniform(-jitter, jitter)
                k = float(brightness(math.hypot(px - ox, py - oy)))
                layer.fill(tuple(int(c * k) for c in C.COL_SONAR), (px - dot / 2, py - dot / 2, dot, dot))
        canvas += _to_array(layer)

    # sudut lebih gelap, seperti vignette di layar game
    y, x = np.ogrid[:res, :res]
    d = np.sqrt((x - res / 2 + 0.5) ** 2 + (y - res / 2 + 0.5) ** 2) / (res * 0.71)
    canvas *= 1.0 - 0.55 * np.clip((d - 0.45) / 0.55, 0, 1)[..., None] ** 1.4
    return canvas


def _rounded(res, radius, inset):
    """Masker persegi bersudut membulat (0..1), dengan tepi halus."""
    y, x = np.ogrid[:res, :res]
    half = res / 2 - inset - radius
    qx = np.clip(np.abs(x + 0.5 - res / 2) - half, 0, None)
    qy = np.clip(np.abs(y + 0.5 - res / 2) - half, 0, None)
    return np.clip(0.5 - (np.sqrt(qx * qx + qy * qy) - radius), 0.0, 1.0)


def _shrink(arr, k):
    """Memperkecil k kali dengan rata-rata tiap blok k x k (tepat, tidak seperti smoothscale)."""
    n = arr.shape[0] // k
    return arr.reshape(n, k, n, k, *arr.shape[2:]).mean(axis=(1, 3))


def draw_icon(size):
    """Ikon ukuran size x size dengan sudut membulat dan latar transparan."""
    pygame.font.init()
    k = max(4, -(-256 // size))  # digambar k kali lebih besar, lalu diperkecil
    res = size * k
    rgb = _art(res, size)
    inset = res * (0.02 if size < _SMALL else 0.04)
    radius = res * 0.2
    edge = res * (0.03 if size < _SMALL else 0.01)
    mask = _rounded(res, radius, inset)
    # garis tepi tipis supaya ikon tetap terlihat di taskbar yang gelap
    rim = np.clip(mask - _rounded(res, radius - edge, inset + edge), 0, 1)
    rgb += rim[..., None] * np.array([24, 28, 30])
    alpha = _shrink(mask, k)
    rgb = _shrink(rgb * mask[..., None], k) / np.maximum(alpha, 1e-6)[..., None]
    if size >= _SMALL:
        # film grain, dengan butiran seukuran piksel ikon
        cell = 2 if size >= 128 else 1
        n = -(-size // cell)
        grain = np.random.default_rng(3).random((n, n)) ** 6 * 20
        grain = np.kron(grain, np.ones((cell, cell)))[:size, :size]
        rgb += grain[..., None] * np.array([0.82, 0.8, 0.76])
    out = pygame.Surface((size, size), pygame.SRCALPHA)
    out.blit(_to_surface(rgb), (0, 0))
    px = pygame.surfarray.pixels_alpha(out)
    px[:] = np.round(alpha.T * 255).astype(np.uint8)
    del px
    return out
