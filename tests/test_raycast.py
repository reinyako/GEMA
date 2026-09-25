import math
import random

from gema import config as C
from gema.world.maze import Maze, generate, tile_center
from gema.world.raycast import angle_diff, cast, line_of_sight


def brute_cast(maze, ox, oy, dx, dy, max_dist, step=0.25):
    d = 0.0
    while d < max_dist:
        if maze.is_wall(int((ox + dx * d) // C.TILE), int((oy + dy * d) // C.TILE)):
            return d
        d += step
    return max_dist


def test_cast_matches_brute_force():
    rng = random.Random(1)
    maze = generate(10, 8, rng, braid=0.3)
    tiles = maze.floor_tiles()
    for _ in range(300):
        tx, ty = rng.choice(tiles)
        ox = tx * C.TILE + rng.uniform(2, C.TILE - 2)
        oy = ty * C.TILE + rng.uniform(2, C.TILE - 2)
        a = rng.uniform(0, math.tau)
        dx, dy = math.cos(a), math.sin(a)
        assert abs(cast(maze, ox, oy, dx, dy, 400) - brute_cast(maze, ox, oy, dx, dy, 400)) < 0.6


def test_line_of_sight_blocked_by_wall():
    rows = ["#####", "#...#", "#.#.#", "#...#", "#####"]
    maze = Maze([[1 if c == "#" else 0 for c in row] for row in rows])
    ax, ay = tile_center((1, 1))
    assert line_of_sight(maze, ax, ay, ax, ay)
    assert line_of_sight(maze, ax, ay, *tile_center((3, 1)))
    assert line_of_sight(maze, ax, ay, *tile_center((1, 3)))
    assert not line_of_sight(maze, ax, ay, *tile_center((3, 3)))


def test_angle_diff_wraps():
    assert math.isclose(angle_diff(0.1, math.tau - 0.1), 0.2, abs_tol=1e-9)
    assert math.isclose(angle_diff(math.pi, -math.pi), 0.0, abs_tol=1e-9)
