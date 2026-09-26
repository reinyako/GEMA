import os
import sys
from pathlib import Path

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
os.environ["GEMA_LANG"] = "id"  # test selalu memakai Bahasa Indonesia, apa pun bahasa sistemnya
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest  # noqa: E402


@pytest.fixture(autouse=True)
def isolated_save(tmp_path, monkeypatch):
    monkeypatch.setenv("GEMA_SAVE", str(tmp_path / "save.json"))
    yield
    from gema import lang

    lang.set_lang("id")
