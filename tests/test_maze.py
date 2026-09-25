import random

import pytest

from gema import config as C
from gema.world.maze import final_corridor, generate, plan_layout


def maze_for(number, seed):
    rules = C.floor_rules(number, C.GELAP)
    rng = random.Random(seed)
    return generate(*rules.cells, rng, rules.braid, rules.rooms), rng


@pytest.mark.parametrize("number", [1, 2, 3, 4, 5])
@pytest.mark.parametrize("seed", range(8))
def test_generated_maze_is_connected_and_sized(number, seed):
    maze, _ = maze_for(number, seed)
    cw, ch = C.floor_rules(number, C.GELAP).cells
    assert (maze.w, maze.h) == (cw * 2 + 1, ch * 2 + 1)
    assert maze.is_connected()
    # Tepi luar selalu dinding.
    assert all(maze.is_wall(x, 0) and maze.is_wall(x, maze.h - 1) for x in range(maze.w))
    assert all(maze.is_wall(0, y) and maze.is_wall(maze.w - 1, y) for y in range(maze.h))


def test_braiding_reduces_dead_ends():
    perfect = [len(generate(16, 11, random.Random(s)).dead_ends()) for s in range(10)]
    braided = [len(generate(16, 11, random.Random(s), braid=0.5).dead_ends()) for s in range(10)]
    assert sum(braided) < sum(perfect) * 0.75


@pytest.mark.parametrize("seed", range(15))
def test_layout_rules(seed):
    maze, rng = maze_for(3, seed)
    layout = plan_layout(maze, rng, 3, 3, 2)
    dist = maze.bfs(layout.start)
    cells = [t for t in maze.cell_tiles() if t in dist]
    assert dist[layout.exit] == max(dist[t] for t in cells)
    assert len(layout.fragments) == 3 and len(set(layout.fragments)) == 3
    assert layout.start not in layout.fragments and layout.exit not in layout.fragments
    assert all(dist[t] >= 2 * C.FRAGMENT_MIN_START_CELLS for t in layout.fragments)
    assert len(layout.batteries) == 3
    assert not set(layout.batteries) & set(layout.fragments)
    assert all(dist[t] >= 2 * C.LISTENER_MIN_SPAWN_CELLS for t in layout.listeners)


@pytest.mark.parametrize("seed", range(3))
def test_shifting_never_disconnects(seed):
    maze, rng = maze_for(5, seed)
    connectors = maze.connectors()
    closed = 0
    for _ in range(1000):
        t = rng.choice(connectors)
        if maze.is_wall(*t):
            maze.open_tile(t)
        elif maze.try_close(t):
            closed += 1
        assert maze.is_connected()
    assert closed > 50


@pytest.mark.parametrize("seed", range(5))
def test_final_corridor_is_single_path(seed):
    maze, start, goal = final_corridor(random.Random(seed))
    assert maze.is_connected()
    assert maze.degree(start) == 1 and maze.degree(goal) == 1
    assert all(maze.degree(t) <= 2 for t in maze.floor_tiles())
    assert len(maze.path(start, goal)) >= 40
