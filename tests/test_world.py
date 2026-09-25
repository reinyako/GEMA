"""Logika lantai tanpa render: monster, senter, pintu, dan trik sonar."""

import math

import pygame
import pytest

from gema import config as C
from gema.input import InputState
from gema.run import Run
from gema.world.floor import Floor
from gema.world.listener import HUNT, INVESTIGATE
from gema.world.maze import tile_center, tile_of
from gema.world.raycast import line_of_sight

IDLE = InputState()


@pytest.fixture(autouse=True)
def _pygame():
    pygame.init()
    yield


def make_floor(number=1, seed=5, difficulty=C.GELAP):
    run = Run(difficulty, seed=seed, attempt=1, floor=number)
    return Floor(run, C.floor_rules(number, difficulty))


def visible_tile(floor, dist_px):
    p = floor.player
    best = None
    for t in floor.maze.bfs(tile_of(p.x, p.y), limit=14):
        cx, cy = tile_center(t)
        if not line_of_sight(floor.maze, p.x, p.y, cx, cy):
            continue
        score = abs(math.hypot(cx - p.x, cy - p.y) - dist_px)
        if best is None or score < best[0]:
            best = (score, cx, cy)
    return best[1], best[2]


def test_listener_hunts_close_noise():
    f = make_floor()
    listener = f.listeners[0]
    listener.relocate(*visible_tile(f, 90))
    f.noise.emit(f.player.x, f.player.y, C.RUN_NOISE, "step")
    f.update(1 / 60, IDLE)
    assert listener.state == HUNT


def test_listener_investigates_far_noise_and_ignores_silence():
    f = make_floor()
    listener = f.listeners[0]
    before = listener.state
    for _ in range(30):
        f.update(1 / 60, IDLE)
    assert listener.state == before  # pemain diam: tidak ada yang terdengar
    listener.relocate(*visible_tile(f, 300))
    f.noise.emit(f.player.x, f.player.y, C.SONAR_NOISE, "sonar")
    f.update(1 / 60, IDLE)
    assert listener.state == INVESTIGATE


def test_listener_freezes_in_light_and_still_kills():
    f = make_floor()
    listener = f.listeners[0]
    x, y = visible_tile(f, 100)
    listener.relocate(x, y)
    aim = math.atan2(y - f.player.y, x - f.player.x)
    f.noise.emit(f.player.x, f.player.y, C.RUN_NOISE, "step")
    for _ in range(30):
        f.update(1 / 60, InputState(aim=aim, light=True))
    assert listener.frozen
    assert (listener.x, listener.y) == (x, y)
    listener.x, listener.y = f.player.x + 5, f.player.y
    f.update(1 / 60, InputState(aim=aim, light=True))
    assert f.dead
    assert [e for e in f.events if e[0] == "death"] == [("death", listener)]


def test_exit_opens_after_all_fragments_and_goes_silent():
    f = make_floor()
    notes = []
    for frag in f.fragments:
        frag.x, frag.y = f.player.x, f.player.y
        f.update(1 / 60, IDLE)
        notes += [e[1] for e in f.events if e[0] == "note"]
        f.events.clear()
    assert f.exit.open and f.silence_timer > 0
    assert len(notes) == 3 and notes[0].startswith("Kalau kamu baca ini")


def test_battery_drains_and_pickup_refills():
    f = make_floor()
    start = f.flashlight.battery
    for _ in range(60):
        f.update(1 / 60, InputState(light=True))
    assert f.flashlight.battery == pytest.approx(start - C.GELAP.battery_drain, abs=0.2)
    f.batteries[0].x, f.batteries[0].y = f.player.x, f.player.y
    f.update(1 / 60, IDLE)
    expected = min(C.BATTERY_MAX, start - C.GELAP.battery_drain + C.BATTERY_PICKUP)
    assert f.flashlight.battery == pytest.approx(expected, abs=0.3)


def test_watcher_banished_after_two_seconds_of_light():
    f = make_floor(number=2)
    w = f.watcher
    w.timer = 0
    f.update(1 / 60, IDLE)
    assert w.present
    x, y = visible_tile(f, 150)
    w.x, w.y = x, y
    aim = math.atan2(y - f.player.y, x - f.player.x)
    for _ in range(int(60 * (C.WATCHER_BANISH_TIME + 0.1))):
        f.update(1 / 60, InputState(aim=aim, light=True))
    assert not w.present


def test_watcher_approaches_only_when_unobserved():
    f = make_floor(number=2)
    w = f.watcher
    w.timer = 0
    f.update(1 / 60, IDLE)
    w.comfort = 0
    x, y = visible_tile(f, 200)
    w.x, w.y = x, y
    aim = math.atan2(y - f.player.y, x - f.player.x)
    f.update(1 / 60, InputState(aim=aim, light=True))
    assert (w.x, w.y) == (x, y)
    for _ in range(30):
        f.update(1 / 60, InputState(aim=aim + math.pi, light=False))
    assert math.hypot(w.x - f.player.x, w.y - f.player.y) < math.hypot(x - f.player.x, y - f.player.y)


def test_false_echoes_respect_fairness():
    f = make_floor(number=4)
    f.stress.value = 100
    p = f.player
    path_map = f.maze.bfs(tile_of(p.x, p.y), limit=16)
    seen = 0
    for _ in range(50):
        for x, y, _sharp in f.director.false_echoes(f, path_map):
            seen += 1
            assert math.hypot(x - p.x, y - p.y) >= C.FALSE_ECHO_MIN_DIST - 12
    assert seen > 0
    assert not f.director.drop_echo(f, "listener", C.MISS_ECHO_MIN_DIST - 1)
    assert not f.director.drop_echo(f, "fragment", 400)


def test_floor_one_has_no_perception_tricks():
    f = make_floor(number=1)
    f.stress.value = 100
    p = f.player
    path_map = f.maze.bfs(tile_of(p.x, p.y), limit=16)
    assert f.director.false_echoes(f, path_map) == []
    assert not f.director.drop_echo(f, "listener", 400)


def test_wall_shift_keeps_maze_connected():
    f = make_floor(number=3)
    shifted = 0
    for _ in range(200):
        if f.try_shift_wall():
            shifted += 1
        assert f.maze.is_connected()
    assert shifted > 20
    assert f.changed_tiles


def test_respawn_moves_listeners_away():
    f = make_floor(number=2)
    f.run.deaths = 1
    f.respawn()
    start = f.start_tile
    dist = f.maze.bfs(start)
    for listener in f.listeners:
        assert dist[tile_of(listener.x, listener.y)] >= C.LISTENER_RESPAWN_MIN_TILES
    assert f.stress.floor_min == C.STRESS_FLOOR_PER_DEATH


def test_god_mode_reports_hits_without_dying():
    f = make_floor()
    f.dev.god = True
    listener = f.listeners[0]
    hits = 0
    for _ in range(120):
        listener.x, listener.y = f.player.x + 4, f.player.y
        f.update(1 / 60, IDLE)
        hits += sum(1 for e in f.events if e[0] == "hit")
        assert not any(e[0] == "death" for e in f.events)
        f.events.clear()
    assert not f.dead
    assert hits == 2  # sekali saat menyentuh, sekali lagi setelah jeda GOD_HIT_COOLDOWN


def test_infinite_light_and_no_cooldown():
    f = make_floor()
    f.dev.infinite_light = True
    f.dev.no_cooldown = True
    pings = 0
    for _ in range(120):
        f.update(1 / 60, InputState(light=True, sonar=True))
        pings += sum(1 for s in f.sfx if s[0] == "ping")
        f.sfx.clear()
    assert f.flashlight.battery == C.BATTERY_MAX
    assert pings == 120


def test_normal_mode_has_sonar_cooldown():
    f = make_floor()
    pings = 0
    for _ in range(120):
        f.update(1 / 60, InputState(sonar=True))
        pings += sum(1 for s in f.sfx if s[0] == "ping")
        f.sfx.clear()
    assert pings == 1  # dua detik < jeda sonar Gelap (3 detik)
