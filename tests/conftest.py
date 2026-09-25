import os
import sys
from pathlib import Path

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest  # noqa: E402


@pytest.fixture(autouse=True)
def isolated_save(tmp_path, monkeypatch):
    monkeypatch.setenv("GEMA_SAVE", str(tmp_path / "save.json"))
