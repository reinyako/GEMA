"""Pemain: gerak, tabrakan dengan dinding, dan suara langkah."""

import math

from .. import config as C


def push_out(maze, x, y, r):
    """Mendorong lingkaran (x, y, r) keluar dari petak dinding di sekitarnya."""
    tile = C.TILE
    for ty in range(int((y - r) // tile), int((y + r) // tile) + 1):
        for tx in range(int((x - r) // tile), int((x + r) // tile) + 1):
            if not maze.is_wall(tx, ty):
                continue
            rx, ry = tx * tile, ty * tile
            cx = min(max(x, rx), rx + tile)
            cy = min(max(y, ry), ry + tile)
            dx, dy = x - cx, y - cy
            d2 = dx * dx + dy * dy
            if d2 >= r * r:
                continue
            if d2 > 1e-9:
                d = math.sqrt(d2)
                x += dx / d * (r - d)
                y += dy / d * (r - d)
            else:
                # Pusat berada di dalam dinding: dorong lewat sisi terdekat.
                left, right = x - rx, rx + tile - x
                top, bottom = y - ry, ry + tile - y
                m = min(left, right, top, bottom)
                if m == left:
                    x = rx - r
                elif m == right:
                    x = rx + tile + r
                elif m == top:
                    y = ry - r
                else:
                    y = ry + tile + r
    return x, y


class Player:
    def __init__(self, x, y, aim=0.0):
        self.x = x
        self.y = y
        self.aim = aim
        self.radius = C.PLAYER_RADIUS
        self.moving = False
        self.running = False
        self.step_timer = 0.12

    def update(self, dt, move, running, aim, maze, noise, sfx):
        self.aim = aim
        mx, my = move
        length = math.hypot(mx, my)
        if length < 1e-6:
            self.moving = False
            self.running = False
            self.step_timer = min(self.step_timer, 0.12)
            return
        mx, my = mx / length, my / length
        speed = C.RUN_SPEED if running else C.WALK_SPEED
        dist = speed * dt
        steps = max(1, math.ceil(dist / 3.0))
        for _ in range(steps):
            self.x += mx * dist / steps
            self.x, self.y = push_out(maze, self.x, self.y, self.radius)
            self.y += my * dist / steps
            self.x, self.y = push_out(maze, self.x, self.y, self.radius)
        self.moving = True
        self.running = running
        self.step_timer -= dt
        if self.step_timer <= 0:
            self.step_timer = C.STEP_INTERVAL_RUN if running else C.STEP_INTERVAL_WALK
            noise.emit(self.x, self.y, C.RUN_NOISE if running else C.WALK_NOISE, "step")
            sfx.append(("step_run" if running else "step", None, None))
