"""Raycasting DDA di atas grid petak."""

import math

from .. import config as C


def cast(maze, ox, oy, dx, dy, max_dist):
    """Jarak dari (ox, oy) searah vektor satuan (dx, dy) sampai dinding pertama, maksimal max_dist."""
    tile = C.TILE
    tx, ty = int(ox // tile), int(oy // tile)
    grid, w, h = maze.grid, maze.w, maze.h
    if tx < 0 or ty < 0 or tx >= w or ty >= h or grid[ty][tx]:
        return 0.0
    if dx > 0:
        step_x, side_x, delta_x = 1, ((tx + 1) * tile - ox) / dx, tile / dx
    elif dx < 0:
        step_x, side_x, delta_x = -1, (ox - tx * tile) / -dx, tile / -dx
    else:
        step_x, side_x, delta_x = 0, math.inf, math.inf
    if dy > 0:
        step_y, side_y, delta_y = 1, ((ty + 1) * tile - oy) / dy, tile / dy
    elif dy < 0:
        step_y, side_y, delta_y = -1, (oy - ty * tile) / -dy, tile / -dy
    else:
        step_y, side_y, delta_y = 0, math.inf, math.inf
    while True:
        if side_x < side_y:
            dist = side_x
            side_x += delta_x
            tx += step_x
        else:
            dist = side_y
            side_y += delta_y
            ty += step_y
        if dist >= max_dist:
            return max_dist
        if tx < 0 or ty < 0 or tx >= w or ty >= h or grid[ty][tx]:
            return dist


def cast_angle(maze, ox, oy, angle, max_dist):
    return cast(maze, ox, oy, math.cos(angle), math.sin(angle), max_dist)


def line_of_sight(maze, ax, ay, bx, by):
    dx, dy = bx - ax, by - ay
    d = math.hypot(dx, dy)
    if d < 1e-6:
        return True
    return cast(maze, ax, ay, dx / d, dy / d, d) >= d - 0.5


def angle_diff(a, b):
    """Selisih sudut terkecil (absolut) antara a dan b, dalam radian."""
    return abs((a - b + math.pi) % math.tau - math.pi)
