"""Data simpanan antar-sesi. File rusak tidak pernah membuat game crash."""

import json
import os
from dataclasses import asdict, dataclass, field
from pathlib import Path


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
    path: Path = field(default=None, repr=False, compare=False)

    @classmethod
    def load(cls, path=None):
        path = Path(path) if path else default_path()
        data = cls(path=path)
        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
            for key in ("percobaan", "kematian", "ending"):
                value = raw.get(key, 0)
                if isinstance(value, int) and value >= 0:
                    setattr(data, key, value)
            best = raw.get("lantai_terbaik", {})
            if isinstance(best, dict):
                for key in data.lantai_terbaik:
                    value = best.get(key, 0)
                    if isinstance(value, int) and value >= 0:
                        data.lantai_terbaik[key] = value
        except (OSError, ValueError, AttributeError):
            pass
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
