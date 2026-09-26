"""Mode dev untuk testing: kebal, sonar tanpa jeda, senter tanpa batas, dan alat tanpa batas.

Aktif dengan `python main.py --dev`. Pilihannya bisa diubah dari layar judul atau menu jeda.
"""

from dataclasses import dataclass

from . import lang

OPTIONS = ("god", "no_cooldown", "infinite_light", "infinite_tools")  # label: lang "dev_options"


def label(key):
    return lang.data("dev_options")[key][0]


@dataclass
class DevSettings:
    enabled: bool = False  # menu dev dan tombol F5/F6 tersedia
    god: bool = False
    no_cooldown: bool = False
    infinite_light: bool = False
    infinite_tools: bool = False

    def any_active(self):
        return any(getattr(self, key) for key in OPTIONS)

    def summary(self):
        return " · ".join(lang.data("dev_options")[key][1] for key in OPTIONS if getattr(self, key))
