"""Tes singkat tanpa layar: memastikan game bisa dibuka dan dimainkan beberapa detik.

Dipakai untuk memeriksa versi yang sudah dibungkus (misalnya GEMA.exe) di mesin build:
    GEMA --selftest
Keluar dengan kode 0 kalau berhasil.
"""

import os
import random
import tempfile


def run(args):
    os.environ["SDL_VIDEODRIVER"] = "dummy"
    os.environ["SDL_AUDIODRIVER"] = "dummy"
    os.environ["GEMA_SAVE"] = os.path.join(tempfile.mkdtemp(prefix="gema-selftest-"), "save.json")

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
    ok = played > 30 * 5 and app.audio.sounds
    print("selftest ok" if ok else "selftest GAGAL")
    pygame.quit()
    return 0 if ok else 1
