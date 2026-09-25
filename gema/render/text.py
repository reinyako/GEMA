"""Font dan teks: font monospace sistem dengan cadangan font bawaan, plus efek mesin ketik."""

import pygame

from .. import config as C

_FONT_NAMES = "dejavusansmono,couriernew,consolas,menlo,liberationmono,monospace"
_cache = {}


def font(size, italic=False, bold=False):
    key = (size, italic, bold)
    f = _cache.get(key)
    if f is None:
        try:
            f = pygame.font.SysFont(_FONT_NAMES, size, bold=bold, italic=italic)
        except Exception:  # noqa: BLE001 - sebagian sistem tidak punya fontconfig
            f = pygame.font.Font(None, int(size * 1.3))
        _cache[key] = f
    return f


def wrap(text, fnt, width):
    lines, line = [], ""
    for word in text.split():
        trial = f"{line} {word}".strip()
        if fnt.size(trial)[0] <= width or not line:
            line = trial
        else:
            lines.append(line)
            line = word
    if line:
        lines.append(line)
    return lines


def draw_center(surface, text, fnt, color, cx, y, alpha=255):
    img = fnt.render(text, True, color)
    if alpha < 255:
        img.set_alpha(max(0, int(alpha)))
    surface.blit(img, (int(cx - img.get_width() / 2), int(y)))
    return img.get_height()


def draw_left(surface, text, fnt, color, x, y, alpha=255):
    img = fnt.render(text, True, color)
    if alpha < 255:
        img.set_alpha(max(0, int(alpha)))
    surface.blit(img, (int(x), int(y)))
    return img.get_height()


class TypeText:
    """Teks yang muncul huruf demi huruf, bertahan sebentar, lalu memudar."""

    def __init__(self, text, size=20, speed=30.0, hold=4.5, fade=1.2, color=C.COL_TEXT):
        self.text = text
        self.font = font(size, italic=True)
        self.speed = speed
        self.hold = hold
        self.fade = fade
        self.color = color
        self.shown = 0.0
        self.after = 0.0

    @property
    def typed(self):
        return self.shown >= len(self.text)

    @property
    def done(self):
        return self.typed and self.after >= self.hold + self.fade

    def update(self, dt):
        if not self.typed:
            self.shown = min(len(self.text), self.shown + self.speed * dt)
        else:
            self.after += dt

    def alpha(self):
        if self.after <= self.hold:
            return 255
        return max(0.0, 255 * (1.0 - (self.after - self.hold) / self.fade))

    def draw(self, surface, cx, y, width=720):
        visible = self.text[: int(self.shown)]
        a = self.alpha()
        for i, line in enumerate(wrap(visible, self.font, width)):
            draw_center(surface, line, self.font, self.color, cx, y + i * (self.font.get_linesize() + 2), a)
