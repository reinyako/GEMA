"""Data simpanan antar-sesi. File rusak tidak pernah membuat game crash."""

import json
import os
from dataclasses import asdict, dataclass, field
from pathlib import Path

from . import lang

NOTE_MAX = 90  # panjang maksimal catatan yang ditulis pemain di ending


def default_path():
    override = os.environ.get("GEMA_SAVE")
    if override:
        return Path(override)
    return Path.home() / ".gema" / "save.json"


@dataclass
class SaveData:
    percobaan: int = 0
    kematian: int = 0
    ending: int = 0
    lantai_terbaik: dict = field(default_factory=lambda: {"redup": 0, "gelap": 0, "pekat": 0})
    tamat: dict = field(default_factory=lambda: {"redup": 0, "gelap": 0, "pekat": 0})
    total_ping: int = 0
    total_dinding: int = 0
    pengamat_diusir: int = 0
    pencapaian: list = field(default_factory=list)
    catatan_pemain: str = ""
    bahasa: str = ""
    path: Path = field(default=None, repr=False, compare=False)

    @classmethod
    def load(cls, path=None):
        path = Path(path) if path else default_path()
        data = cls(path=path)
        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
            for key in ("percobaan", "kematian", "ending", "total_ping", "total_dinding", "pengamat_diusir"):
                value = raw.get(key, 0)
                if isinstance(value, int) and value >= 0:
                    setattr(data, key, value)
            for name in ("lantai_terbaik", "tamat"):
                stored, target = raw.get(name, {}), getattr(data, name)
                if isinstance(stored, dict):
                    for key in target:
                        value = stored.get(key, 0)
                        if isinstance(value, int) and value >= 0:
                            target[key] = value
            got = raw.get("pencapaian", [])
            if isinstance(got, list):
                data.pencapaian = [k for k in got if isinstance(k, str)]
            note = raw.get("catatan_pemain", "")
            if isinstance(note, str):
                data.catatan_pemain = note[:NOTE_MAX]
            code = raw.get("bahasa", "")
            # pemain lama (sebelum ada pilihan bahasa) tetap memakai Bahasa Indonesia
            data.bahasa = code if code in lang.CODES else "id"
        except (OSError, ValueError, AttributeError):
            pass
        if not data.bahasa:
            data.bahasa = lang.detect()  # pemain baru: ikut bahasa sistem
        return data

    def write(self):
        if self.path is None:
            return
        payload = {k: v for k, v in asdict(self).items() if k != "path"}
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            tmp = self.path.with_suffix(".tmp")
            tmp.write_text(json.dumps(payload, indent=2), encoding="utf-8")
            tmp.replace(self.path)
        except OSError:
            pass

    def record_floor(self, difficulty_key, floor):
        if floor > self.lantai_terbaik.get(difficulty_key, 0):
            self.lantai_terbaik[difficulty_key] = floor
            self.write()
