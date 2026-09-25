"""Bus kejadian suara. Suara yang dikirim di satu frame didengar monster di frame berikutnya."""

from dataclasses import dataclass


@dataclass
class Noise:
    x: float
    y: float
    radius: float
    source: str


class NoiseBus:
    def __init__(self):
        self.events = []
        self._pending = []

    def emit(self, x, y, radius, source):
        self._pending.append(Noise(x, y, radius, source))

    def advance(self):
        self.events = self._pending
        self._pending = []

    def clear(self):
        self.events = []
        self._pending = []
