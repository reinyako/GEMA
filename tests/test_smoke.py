"""Bot memainkan game tanpa layar, lewat semua scene sungguhan."""

import random

import pygame

from gema.app import App, parse_args
from gema.input import BotController
from gema import config as C
from gema.scenes.dev import DevScene
from gema.run import Run
from gema.scenes.achievements import AchievementsScene
from gema.scenes.ending import NOTE, EndingScene
from gema.scenes.interlude import InterludeScene
from gema.scenes.play import DYING, PlayScene
from gema.scenes.title import DifficultyScene, TitleScene


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
    assert app.scene.menu.items == ["Mulai", "Mode dev", "Pencapaian", "Pengaturan", "Keluar"]
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


def test_menu_choices_click_like_a_flashlight():
    app = App(parse_args([]))
    clicks = []
    real_ui = app.audio.ui
    app.audio.ui = lambda name="click": (clicks.append(name), real_ui(name))
    app.step(1 / 30, [key(pygame.K_RETURN)])  # Mulai
    app.step(1 / 30, [key(pygame.K_RETURN)])  # Gelap
    assert clicks == ["click", "click"]
    while not isinstance(app.scene, PlayScene):
        app.step(1 / 30, [])
    app.step(1 / 30, [key(pygame.K_ESCAPE)])                        # jeda: tidak berbunyi
    app.step(1 / 30, [key(pygame.K_DOWN), key(pygame.K_RETURN)])   # Catatan
    app.step(1 / 30, [key(pygame.K_RETURN)])                        # tutup catatan
    assert clicks == ["click"] * 4


def test_stop_all_keeps_the_menu_click():
    from gema.audio.manager import LOOP_SLOTS

    app = App(parse_args([]))
    audio = app.audio
    assert audio.enabled
    audio.ui("heart")      # suara panjang, supaya pasti masih berbunyi saat dicek
    audio.play("heart")
    audio.stop_all()
    ui = LOOP_SLOTS.index("ui")
    assert pygame.mixer.Channel(ui).get_busy()
    assert not any(pygame.mixer.Channel(i).get_busy()
                   for i in range(pygame.mixer.get_num_channels()) if i != ui)


def test_q_throws_a_stone_in_game():
    app = App(parse_args(["--mute", "--seed", "5"]))
    start(app)
    while not isinstance(app.scene, PlayScene):
        app.step(1 / 30, [])
    f = app.scene.floor
    left = f.stones_left
    app.step(1 / 30, [key(pygame.K_q)])
    assert f.stones_left == left - 1
    app.step(1 / 30, [key(pygame.K_ESCAPE)])   # menu jeda menggambar sisa kerikil
    app.step(1 / 30, [])
    assert app.scene.paused


def test_ending_lets_you_write_the_next_first_note():
    app = App(parse_args(["--mute"]))
    run = Run(C.GELAP, seed=8, attempt=1)
    app.switch(EndingScene(app, run))
    app.step(1 / 30, [key(pygame.K_ESCAPE)])              # lewati cahaya, langsung ke catatan
    assert app.scene.stage == NOTE
    typed = [pygame.event.Event(pygame.TEXTINPUT, text=ch) for ch in "Pakai kerikil."]
    app.step(1 / 30, typed + [key(pygame.K_BACKSPACE)])
    app.step(1 / 30, [key(pygame.K_RETURN)])
    assert app.save.catatan_pemain == "Pakai kerikil"
    assert "tamat_gelap" in app.save.pencapaian
    for _ in range(30 * 120):
        app.step(1 / 30, [])
        if isinstance(app.scene, TitleScene):
            break
    assert isinstance(app.scene, TitleScene)
    assert app.save.tamat["gelap"] == 1


def test_achievements_screen_opens_from_title():
    app = App(parse_args(["--mute"]))
    items = app.scene.menu.items
    app.step(1 / 30, [key(pygame.K_DOWN)] * items.index("Pencapaian") + [key(pygame.K_RETURN)])
    assert isinstance(app.scene, AchievementsScene)
    app.step(1 / 30, [])
    app.step(1 / 30, [key(pygame.K_ESCAPE)])
    assert isinstance(app.scene, TitleScene)


def _die_with_no_lives_left(app, difficulty):
    run = Run(difficulty, seed=4, attempt=1)
    run.lives = 1
    app.go_floor_intro(run)
    while not isinstance(app.scene, PlayScene):
        app.step(1 / 30, [])
    scene = app.scene
    scene.run.notes.append("catatan lantai ini")
    scene.floor.taken = 1
    scene._die(scene.floor.listeners[0])
    return run, scene


def test_redup_repeats_the_floor_with_a_new_maze_when_lives_run_out():
    app = App(parse_args(["--mute"]))
    run, scene = _die_with_no_lives_left(app, C.REDUP)
    old_grid = [row[:] for row in scene.floor.maze.grid]
    for _ in range(30 * 20):
        app.step(1 / 30, [])
        if isinstance(app.scene, PlayScene) and app.scene is not scene:
            break
    assert isinstance(app.scene, PlayScene) and app.scene is not scene
    assert run.floor == 1 and run.retries == run.floor_retries == 1 and run.lives == C.REDUP.lives
    assert run.notes == []
    assert app.scene.floor.maze.grid != old_grid


def test_gelap_still_ends_the_attempt_when_lives_run_out():
    app = App(parse_args(["--mute"]))
    _die_with_no_lives_left(app, C.GELAP)
    for _ in range(30 * 20):
        app.step(1 / 30, [])
        if isinstance(app.scene, TitleScene):
            break
    assert isinstance(app.scene, TitleScene)


def test_settings_switch_the_language():
    from gema import lang
    from gema.scenes.settings import SettingsScene

    app = App(parse_args(["--mute"]))
    items = app.scene.menu.items
    app.step(1 / 30, [key(pygame.K_DOWN)] * items.index("Pengaturan") + [key(pygame.K_RETURN)])
    assert isinstance(app.scene, SettingsScene)
    app.step(1 / 30, [key(pygame.K_RETURN)])    # Bahasa: Indonesia -> English
    assert lang.current == "en" and app.save.bahasa == "en"
    assert app.scene.menu.items[0] == "Language: English"
    app.step(1 / 30, [key(pygame.K_ESCAPE)])
    assert isinstance(app.scene, TitleScene)
    assert app.scene.menu.items == ["Begin", "Achievements", "Settings", "Quit"]
    start(app)
    while not isinstance(app.scene, PlayScene):
        app.step(1 / 30, [])
    app.step(1 / 30, [key(pygame.K_ESCAPE)])
    assert app.scene.pause_menu.items == ["Resume", "Notes", "Back to title"]


def test_lang_flag_is_for_this_session_only():
    from gema import lang

    from gema.save import SaveData

    saved = SaveData.load()
    saved.bahasa = "id"
    saved.write()
    app = App(parse_args(["--mute", "--lang", "en"]))
    assert lang.current == "en" and app.scene.menu.items[0] == "Begin"
    assert C.GELAP.name == "Dark" and C.PEKAT.name == "Pitch Black"
    assert SaveData.load().bahasa == "id"   # --lang tidak mengubah pengaturan yang tersimpan


def test_debug_overlay_only_in_dev_mode():
    for flags, allowed in ((["--mute"], False), (["--mute", "--dev"], True)):
        app = App(parse_args(flags))
        start(app)
        while not isinstance(app.scene, PlayScene):
            app.step(1 / 30, [])
        app.step(1 / 30, [key(pygame.K_F3)])
        assert app.scene.debug is allowed


def test_selftest_used_by_exe_build_passes():
    from gema import selftest

    assert selftest.run(parse_args(["--selftest"])) == 0


def test_difficulty_screen_darkens_with_selection():
    app = App(parse_args([]))
    app.step(1 / 30, [key(pygame.K_RETURN)])  # Mulai
    scene = app.scene
    assert isinstance(scene, DifficultyScene)
    app.step(1 / 30, [key(pygame.K_DOWN)])  # Gelap -> Pekat
    for _ in range(90):
        app.step(1 / 30, [])
    assert scene.dark > 0.9
    app.step(1 / 30, [key(pygame.K_UP)])
    app.step(1 / 30, [key(pygame.K_UP)])  # Redup
    for _ in range(90):
        app.step(1 / 30, [])
    assert scene.dark < 0.1 and not scene.flicker_off
    # vignette yang dipakai di dalam game tidak boleh ikut jadi transparan
    assert all(v.get_alpha() == 255 for v in app.effects.vignettes)
