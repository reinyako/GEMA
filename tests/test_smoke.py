"""Bot memainkan game tanpa layar, lewat semua scene sungguhan."""

import random

import pygame

from gema.app import App, parse_args
from gema.input import BotController
from gema import config as C
from gema.scenes.dev import DevScene
from gema.scenes.ending import EndingScene
from gema.scenes.interlude import InterludeScene
from gema.scenes.play import DYING, PlayScene
from gema.scenes.title import TitleScene


def key(k):
    return pygame.event.Event(pygame.KEYDOWN, key=k, mod=0, unicode="", scancode=0)


def start(app):
    app.step(1 / 30, [key(pygame.K_RETURN)])  # Mulai
    app.step(1 / 30, [key(pygame.K_RETURN)])  # Gelap


def test_bot_reaches_ending_and_returns_to_title():
    app = App(parse_args(["--seed", "11"]))
    app.make_controller = lambda: BotController(random.Random(2))
    app.dev.god = True
    start(app)
    seen_floors, saw_ending = set(), False
    for _ in range(30 * 60 * 12):
        app.step(1 / 30, [])
        if isinstance(app.scene, PlayScene):
            seen_floors.add(app.scene.run.floor)
        if isinstance(app.scene, EndingScene):
            saw_ending = True
        if saw_ending and isinstance(app.scene, TitleScene):
            break
    assert seen_floors == {1, 2, 3, 4, 5, 6}
    assert saw_ending and isinstance(app.scene, TitleScene)
    assert app.save.ending == 1
    assert app.scene.menu.items[0] == "Kamu kembali. Lagi."


def test_mortal_bot_survives_without_crash():
    app = App(parse_args(["--seed", "5", "--floor", "3"]))
    app.make_controller = lambda: BotController(random.Random(9), navigate=False)
    start(app)
    for _ in range(30 * 150):
        app.step(1 / 30, [])
    assert app.save.percobaan >= 1


def test_pause_and_notes_menu():
    app = App(parse_args(["--seed", "3"]))
    start(app)
    for _ in range(30 * 5):
        app.step(1 / 30, [])
    assert isinstance(app.scene, PlayScene)
    app.step(1 / 30, [key(pygame.K_ESCAPE)])
    assert app.scene.paused
    app.step(1 / 30, [key(pygame.K_DOWN), key(pygame.K_RETURN)])
    assert app.scene.showing_notes
    app.step(1 / 30, [key(pygame.K_ESCAPE)])
    app.step(1 / 30, [key(pygame.K_ESCAPE)])
    assert not app.scene.paused


def test_caught_sequence_shakes_reveals_then_fades():
    app = App(parse_args(["--seed", "4", "--mute"]))
    start(app)
    while not isinstance(app.scene, PlayScene):
        app.step(1 / 30, [])
    scene = app.scene
    f = scene.floor
    listener = f.listeners[0]
    listener.x, listener.y = f.player.x + 3, f.player.y
    app.step(1 / 60, [])
    assert scene.state == DYING and scene.catcher is listener
    assert scene.run.lives == C.GELAP.lives - 1
    assert scene.shake.trauma > 0.9
    frozen_at = (listener.x, listener.y)
    for _ in range(int(C.HIT_STOP * 60) - 2):
        app.step(1 / 60, [])
        assert (listener.x, listener.y) == frozen_at  # dunia berhenti
    for _ in range(int((C.DEATH_FADE + C.DEATH_BLACK) * 60) + 4):
        app.step(1 / 60, [])
    assert isinstance(app.scene, InterludeScene)


def test_dev_menu_toggles_from_title_and_pause():
    app = App(parse_args(["--dev", "--mute"]))
    assert app.scene.menu.items == ["Mulai", "Mode dev", "Keluar"]
    app.step(1 / 30, [key(pygame.K_DOWN), key(pygame.K_RETURN)])
    assert isinstance(app.scene, DevScene)
    app.step(1 / 30, [key(pygame.K_RETURN)])                       # kebal
    app.step(1 / 30, [key(pygame.K_DOWN), key(pygame.K_RETURN)])   # sonar tanpa jeda
    assert app.dev.god and app.dev.no_cooldown and not app.dev.infinite_light
    app.step(1 / 30, [key(pygame.K_ESCAPE)])
    app.step(1 / 30, [key(pygame.K_RETURN)])  # Mulai
    app.step(1 / 30, [key(pygame.K_RETURN)])  # Gelap
    while not isinstance(app.scene, PlayScene):
        app.step(1 / 30, [])
    assert app.scene.floor.dev is app.dev
    app.step(1 / 30, [key(pygame.K_ESCAPE)])
    assert app.scene.pause_menu.items == ["Lanjut", "Catatan", "Mode dev", "Kembali ke judul"]
    app.step(1 / 30, [key(pygame.K_DOWN), key(pygame.K_DOWN), key(pygame.K_RETURN)])
    assert app.scene.showing_dev
    app.step(1 / 30, [key(pygame.K_DOWN), key(pygame.K_DOWN), key(pygame.K_RETURN)])  # senter tanpa batas
    assert app.dev.infinite_light


def test_dev_menu_hidden_without_flag():
    app = App(parse_args(["--mute"]))
    assert "Mode dev" not in app.scene.menu.items


def test_selftest_used_by_exe_build_passes():
    from gema import selftest

    assert selftest.run(parse_args(["--selftest"])) == 0
