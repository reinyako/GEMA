"""Mode dev untuk testing: kebal, sonar tanpa jeda, dan senter tanpa batas.

Aktif dengan `python main.py --dev`. Pilihannya bisa diubah dari layar judul atau menu jeda.
"""

from dataclasses import dataclass

OPTIONS = (
    ("god", "Kebal (tidak bisa mati)", "kebal"),
    ("no_cooldown", "Sonar tanpa jeda", "sonar tanpa jeda"),
    ("infinite_light", "Senter tanpa batas", "senter tanpa batas"),
)


@dataclass
class DevSettings:
    enabled: bool = False  # menu dev dan tombol F5/F6 tersedia
    god: bool = False
    no_cooldown: bool = False
    infinite_light: bool = False

    def any_active(self):
        return any(getattr(self, key) for key, _, _ in OPTIONS)

    def summary(self):
        return " · ".join(short for key, _, short in OPTIONS if getattr(self, key))
