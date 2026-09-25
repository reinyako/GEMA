"""Benda di labirin: fragmen, baterai cadangan, dan pintu keluar."""

from dataclasses import dataclass


@dataclass
class Fragment:
    x: float
    y: float
    taken: bool = False
    sonar_seen_at: float = -99.0


@dataclass
class Battery:
    x: float
    y: float
    taken: bool = False
    sonar_seen_at: float = -99.0


@dataclass
class Exit:
    x: float
    y: float
    open: bool = False
    sonar_seen_at: float = -99.0
