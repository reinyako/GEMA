"""Tes singkat tanpa layar: memastikan game bisa dibuka dan dimainkan beberapa detik.

Dipakai untuk memeriksa versi yang sudah dibungkus (misalnya GEMA.exe) di mesin build:
    GEMA --selftest
Keluar dengan kode 0 kalau berhasil. GEMA.exe tidak punya console, jadi hasilnya juga
ditulis ke file di GEMA_SELFTEST_LOG kalau variabel itu diisi.
"""

import os
import random
import tempfile
import traceback


def run(args):
    os.environ["SDL_VIDEODRIVER"] = "dummy"
    os.environ["SDL_AUDIODRIVER"] = "dummy"
    os.environ["GEMA_SAVE"] = os.path.join(tempfile.mkdtemp(prefix="gema-selftest-"), "save.json")
    try:
        ok = _play(args)
        report = "selftest ok" if ok else "selftest GAGAL"
    except Exception:  # noqa: BLE001 - semua error harus sampai ke laporan
        ok, report = False, "selftest GAGAL\n" + traceback.format_exc()
    print(report)  # tidak menulis apa-apa kalau tidak ada console
    log = os.environ.get("GEMA_SELFTEST_LOG")
    if log:
        with open(log, "w", encoding="utf-8") as f:
            f.write(report + "\n")
    return 0 if ok else 1


def _play(args):
    import pygame

    from .app import App
    from .input import BotController
    from .scenes.play import PlayScene

    app = App(args)
    app.make_controller = lambda: BotController(random.Random(1))

    def key(k):
        return pygame.event.Event(pygame.KEYDOWN, key=k, mod=0, unicode="", scancode=0)

    for _ in range(30):
        app.step(1 / 30, [])
    app.step(1 / 30, [key(pygame.K_RETURN)])  # Mulai
    app.step(1 / 30, [key(pygame.K_RETURN)])  # Gelap
    played = 0
    for _ in range(30 * 20):
        app.step(1 / 30, [])
        if isinstance(app.scene, PlayScene):
            played += 1
    # pygame.quit() sengaja tidak dipanggil: font yang sudah di-cache jadi rusak kalau pygame
    # dibuka lagi di proses yang sama (misalnya di test). Pygame ditutup otomatis saat keluar.
    return played > 30 * 5 and bool(app.audio.sounds)
