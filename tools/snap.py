"""Merender screenshot tanpa layar untuk review visual.

Contoh:
    python tools/snap.py --floor 3 --light --ping --near --stress 90 --out shots/lantai3.png
"""

import argparse
import math
import os
import sys
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
os.environ.setdefault("GEMA_SAVE", str(Path(__file__).resolve().parent.parent / "shots" / "save.json"))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pygame  # noqa: E402

from gema import config as C  # noqa: E402
from gema.app import App, parse_args  # noqa: E402
from gema.input import InputState  # noqa: E402
from gema.run import Run  # noqa: E402
from gema.scenes.play import PlayScene  # noqa: E402
from gema.world.maze import tile_center, tile_of  # noqa: E402
from gema.world.raycast import line_of_sight  # noqa: E402


class Script:
    def __init__(self, light, ping_frame, aim):
        self.light = light
        self.ping_frame = ping_frame
        self.aim = aim
        self.frame = 0

    def handle_event(self, ev):
        pass

    def sample(self, scene):
        self.frame += 1
        aim = self.aim(scene) if callable(self.aim) else self.aim
        return InputState((0.0, 0.0), False, aim, self.light, self.frame == self.ping_frame)


def place_near(floor, entity, dist_px):
    """Memindahkan entitas ke petak yang terlihat dari pemain, sejauh kira-kira dist_px."""
    p = floor.player
    best = None
    for t in floor.maze.bfs(tile_of(p.x, p.y), limit=12):
        cx, cy = tile_center(t)
        d = math.hypot(cx - p.x, cy - p.y)
        if line_of_sight(floor.maze, p.x, p.y, cx, cy):
            score = abs(d - dist_px)
            if best is None or score < best[0]:
                best = (score, cx, cy)
    if best:
        entity.x, entity.y = best[1], best[2]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--floor", type=int, default=1)
    ap.add_argument("--difficulty", default="gelap")
    ap.add_argument("--frames", type=int, default=40)
    ap.add_argument("--light", action="store_true")
    ap.add_argument("--ping", action="store_true")
    ap.add_argument("--near", action="store_true", help="taruh Pendengar pertama dekat pemain")
    ap.add_argument("--watcher", action="store_true", help="munculkan Pengamat dekat pemain")
    ap.add_argument("--stress", type=float, default=None)
    ap.add_argument("--battery", type=float, default=100.0)
    ap.add_argument("--open", action="store_true", help="buka pintu keluar")
    ap.add_argument("--debug", action="store_true")
    ap.add_argument("--out", default="shots/snap.png")
    args = ap.parse_args()

    app = App(parse_args(["--mute", "--seed", str(args.seed)]))
    run = Run(C.difficulty_by_key(args.difficulty), seed=args.seed, attempt=1, floor=args.floor,
              battery=args.battery)
    scene = PlayScene(app, run)
    app.switch(scene)
    f = scene.floor
    target = None
    if args.near and f.listeners:
        place_near(f, f.listeners[0], 110)
        target = f.listeners[0]
    if args.watcher and f.watcher is not None:
        f.watcher.timer = 0
        f.watcher.update(0.0, f)
        place_near(f, f.watcher, 150)
        target = target or f.watcher
    if args.open:
        f._open_exit()

    def aim(scene):
        p = scene.floor.player
        if target is not None:
            return math.atan2(target.y - p.y, target.x - p.x)
        return p.aim

    scene.controller = Script(args.light, 2 if args.ping else -1, aim)
    scene.debug = args.debug
    for _ in range(args.frames):
        if args.stress is not None:
            f.stress.value = args.stress
        scene.update(1 / 60)
    scene.draw(app.screen)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    pygame.image.save(app.screen, str(out))
    print(out)


if __name__ == "__main__":
    main()
