"""Satu lantai: merakit labirin dan isinya, lalu menjalankan semua sistem setiap frame."""

import math
import random

from .. import config as C
from .. import notes
from ..dev import DevSettings
from .director import Director
from .flashlight import Flashlight
from .items import Battery, Exit, Fragment
from .listener import Listener, Silhouette
from .maze import Layout, final_corridor, generate, plan_layout, tile_center, tile_of
from .noise import NoiseBus
from .player import Player
from .raycast import line_of_sight
from .sonar import Sonar
from .stress import Stress
from .watcher import Watcher


class Shadow(Silhouette):
    """Bayangan palsu di tepi kerucut senter. Hilang begitu disorot langsung."""

    def __init__(self, x, y, rng):
        self.x, self.y = x, y
        self.life = C.SHADOW_LIFE
        self.init_shape(rng)


class Floor:
    def __init__(self, run, rules):
        self.run = run
        self.rules = rules
        self.diff = run.difficulty
        # lantai yang diulang (Redup) mendapat labirin baru
        self.rng = random.Random(run.seed * 7919 + rules.number * 104729 + run.retries * 15485863)

        if rules.final:
            self.maze, start, exit_tile = final_corridor(self.rng)
            layout = Layout(start, exit_tile)
        else:
            self.maze = generate(*rules.cells, self.rng, rules.braid, rules.rooms)
            layout = plan_layout(
                self.maze, self.rng, C.FRAGMENTS_PER_FLOOR,
                self.diff.batteries_per_floor, rules.listeners,
            )

        self.start_tile = layout.start
        sx, sy = tile_center(layout.start)
        self.player = Player(sx, sy, self._open_direction(layout.start))
        self.fragments = [Fragment(*tile_center(t)) for t in layout.fragments]
        self.batteries = [Battery(*tile_center(t)) for t in layout.batteries]
        self.exit = Exit(*tile_center(layout.exit), open=rules.final)
        self.listeners = [Listener(*tile_center(t), self.rng) for t in layout.listeners]
        self.watcher = Watcher(self.rng) if rules.watcher else None
        self.shadows = []
        tools = not rules.final
        self.stones_left = self.diff.stones if tools else 0
        self.breaks_left = self.diff.wall_breaks if tools else 0
        self.stones = []          # kerikil yang sedang melayang: [x0, y0, x1, y1, umur]
        self.ripples = []         # lingkaran samar di tempat kerikil jatuh: [x, y, umur]
        self.break_tile = None    # dinding yang sedang dihancurkan
        self.break_dir = (0, 0)   # arah dari pemain ke dinding itu
        self.break_progress = 0.0
        self.debris = []          # pecahan dinding yang baru runtuh: [petak, arah, umur]
        self._break_held = False

        self.noise = NoiseBus()
        memory = tuple(min(255, int(c * self.diff.memory_glow)) for c in C.COL_MEMORY)
        self.sonar = Sonar(self.maze, self.rng, memory, self.diff.echo_fade)
        self.flashlight = Flashlight(run.battery)
        self.stress = Stress(run.stress_floor())
        self.director = Director(rules, self.diff, self.rng)
        self.connectors = self.maze.connectors()

        self.time = 0.0
        self.last_light_time = 0.0
        self.silence_timer = 0.0
        self.taken = 0
        self.dead = False
        self.dev = DevSettings()
        self.hit_cooldown = 0.0
        self.events = []         # untuk scene: ("note", teks), ("death", makhluk), ("hit", makhluk), ("exit",)
        self.sfx = []            # untuk audio: (nama, x, y); x None = suara dari pemain sendiri
        self.changed_tiles = []  # untuk renderer: petak yang berubah karena labirin bergeser

    def _open_direction(self, tile):
        for t in self.maze.floor_neighbors(tile):
            return math.atan2(t[1] - tile[1], t[0] - tile[0])
        return 0.0

    # --- loop utama --------------------------------------------------------
    def update(self, dt, inp):
        if self.dead:
            return
        self.time += dt
        self.noise.advance()
        p = self.player
        p.update(dt, inp.move, inp.run, inp.aim, self.maze, self.noise, self.sfx)

        fl = self.flashlight
        if self.dev.infinite_light:
            fl.battery = C.BATTERY_MAX
        if self.dev.no_cooldown:
            self.sonar.cooldown = 0.0
        if self.dev.infinite_tools and not self.rules.final:
            self.stones_left = self.diff.stones
            self.breaks_left = self.diff.wall_breaks
        drain = 0.0 if self.dev.infinite_light else self.diff.battery_drain
        fl.update(dt, inp.light, p.x, p.y, p.aim, self.maze, drain, self.rng, self.sfx)
        if fl.on:
            self.last_light_time = self.time
        run = self.run
        run.play_time += dt
        if p.running:
            run.run_time += dt
        if fl.on:
            run.light_time += dt

        if inp.sonar and self.sonar.ready():
            self._ping()
        self.sonar.update(dt, self.time)
        if inp.throw:
            self._throw()
        self._update_stones(dt)
        self._update_break(dt, inp.break_wall)

        for listener in self.listeners:
            listener.update(dt, self)
        if self.watcher is not None:
            self.watcher.update(dt, self)
        self._update_shadows(dt)

        self._pickups()
        if self.dead:  # baru saja masuk pintu keluar
            return
        self.hit_cooldown = max(0.0, self.hit_cooldown - dt)
        catcher = self.touching_monster()
        if catcher is not None:
            if not self.dev.god:
                self.dead = True
                self.events.append(("death", catcher))
                return
            if self.hit_cooldown <= 0:
                self.hit_cooldown = C.GOD_HIT_COOLDOWN
                self.events.append(("hit", catcher))

        self._update_stress(dt)
        self.director.update(dt, self)
        if self.silence_timer > 0:
            self.silence_timer = max(0.0, self.silence_timer - dt)

    # --- sonar -------------------------------------------------------------
    def sonar_targets(self):
        targets = [(l, "listener") for l in self.listeners]
        if self.watcher is not None and self.watcher.present:
            targets.append((self.watcher, "watcher"))
        targets += [(f, "fragment") for f in self.fragments if not f.taken]
        targets += [(b, "battery") for b in self.batteries if not b.taken]
        targets.append((self.exit, "exit"))
        return targets

    def _ping(self):
        p = self.player
        path_map = self.maze.bfs(tile_of(p.x, p.y), limit=int(C.SONAR_RANGE / C.TILE) + 2)
        fakes = self.director.false_echoes(self, path_map)
        self.sonar.ping(
            p.x, p.y, self.diff.sonar_cooldown, self.sonar_targets(), path_map,
            fakes=fakes,
            drop=lambda ent, kind, d: self.director.drop_echo(self, kind, d),
            wobble=self.rules.tricks and self.stress.value >= C.WOBBLE_STRESS,
        )
        self.noise.emit(p.x, p.y, C.SONAR_NOISE, "sonar")
        self.sfx.append(("ping", None, None))
        self.run.pings += 1

    # --- kerikil & dinding -------------------------------------------------
    def _throw(self):
        endless = self.dev.infinite_tools
        if self.stones_left <= 0 and not endless:
            self.sfx.append(("click_dead", None, None))
            return
        if not endless:
            self.stones_left -= 1
        self.run.stones_thrown += 1
        p = self.player
        tx = p.x + math.cos(p.aim) * C.STONE_RANGE
        ty = p.y + math.sin(p.aim) * C.STONE_RANGE
        self.stones.append([p.x, p.y, *self._landing(tx, ty), 0.0])

    def _landing(self, x, y):
        """Titik jatuh kerikil: titik yang dituju, atau lantai terdekat darinya kalau itu dinding."""
        tx, ty = tile_of(x, y)
        if not self.maze.is_wall(tx, ty):
            return x, y
        for r in range(1, 4):
            best = None
            for ny in range(ty - r, ty + r + 1):
                for nx in range(tx - r, tx + r + 1):
                    if not self.maze.is_wall(nx, ny):
                        cx, cy = tile_center((nx, ny))
                        d = math.hypot(cx - x, cy - y)
                        if best is None or d < best[0]:
                            best = (d, cx, cy)
            if best is not None:
                return best[1], best[2]
        return self.player.x, self.player.y

    def _update_stones(self, dt):
        flying = []
        for s in self.stones:
            s[4] += dt
            if s[4] < C.STONE_FLIGHT:
                flying.append(s)
                continue
            x, y = s[2], s[3]
            self.noise.emit(x, y, C.STONE_NOISE, "stone")
            self.sfx.append(("stone", x, y))
            self.ripples.append([x, y, 0.0])
        self.stones = flying
        for r in self.ripples:
            r[2] += dt
        self.ripples = [r for r in self.ripples if r[2] < C.RIPPLE_TIME]
        for d in self.debris:
            d[2] += dt
        self.debris = [d for d in self.debris if d[2] < C.DEBRIS_TIME]

    def break_target(self):
        """Petak dinding di depan pemain yang bisa dihancurkan, atau None.

        Hanya dinding dalam yang di baliknya ada lorong, supaya jatahnya tidak terbuang percuma.
        """
        p = self.player
        tx, ty = tile_of(p.x, p.y)
        ax, ay = math.cos(p.aim), math.sin(p.aim)
        if abs(ax) >= abs(ay):
            dx, dy = (1 if ax > 0 else -1), 0
        else:
            dx, dy = 0, (1 if ay > 0 else -1)
        wall, beyond = (tx + dx, ty + dy), (tx + 2 * dx, ty + 2 * dy)
        m = self.maze
        inside = 1 <= wall[0] <= m.w - 2 and 1 <= wall[1] <= m.h - 2
        if inside and m.is_wall(*wall) and not m.is_wall(*beyond):
            return wall
        return None

    def _update_break(self, dt, held):
        pressed = held and not self._break_held
        self._break_held = held
        if held and self.breaks_left <= 0 and not self.dev.infinite_tools:
            if pressed:
                self.sfx.append(("click_dead", None, None))
            return
        target = self.break_target() if held else None
        if target != self.break_tile:
            self.break_tile = target
            self.break_progress = 0.0
        if target is None:
            return
        tx, ty = tile_of(self.player.x, self.player.y)
        self.break_dir = (target[0] - tx, target[1] - ty)
        self.break_progress += dt
        if self.break_progress >= C.BREAK_TIME:
            self._break_wall(target)

    def _break_wall(self, tile):
        self.maze.open_tile(tile)
        self.changed_tiles.append(tile)
        self.sonar.forget(tile)
        for listener in self.listeners:
            listener.invalidate(self.maze)
        if self.watcher is not None:
            self.watcher.path = []
        cx, cy = tile_center(tile)
        self.noise.emit(cx, cy, C.BREAK_NOISE, "wall")
        self.sfx.append(("crumble", cx, cy))
        self.events.append(("wall_broken",))
        self.debris.append([tile, self.break_dir, 0.0])
        if not self.dev.infinite_tools:
            self.breaks_left -= 1
        self.run.walls_broken += 1
        self.break_tile = None
        self.break_progress = 0.0

    # --- benda -------------------------------------------------------------
    def _pickups(self):
        p = self.player
        for f in self.fragments:
            if not f.taken and math.hypot(f.x - p.x, f.y - p.y) < C.PICKUP_RADIUS:
                f.taken = True
                self.taken += 1
                index = (self.rules.number - 1) * C.FRAGMENTS_PER_FLOOR + self.taken - 1
                self.events.append(("note", notes.note_text(index, self.run.attempt, self.run.own_note)))
                self.noise.emit(f.x, f.y, C.FRAGMENT_PICKUP_NOISE, "fragment")
                self.sfx.append(("chime", None, None))
                self.stress.add(C.STRESS_FRAGMENT)
                if self.taken >= len(self.fragments):
                    self._open_exit()
        for b in self.batteries:
            if not b.taken and math.hypot(b.x - p.x, b.y - p.y) < C.PICKUP_RADIUS:
                b.taken = True
                self.flashlight.battery = min(C.BATTERY_MAX, self.flashlight.battery + C.BATTERY_PICKUP)
                self.sfx.append(("battery", None, None))
        if self.exit.open and math.hypot(self.exit.x - p.x, self.exit.y - p.y) < C.EXIT_RADIUS:
            self.dead = True  # hentikan update; scene mengurus transisi
            self.events.append(("exit",))

    def _open_exit(self):
        if self.exit.open:
            return
        self.exit.open = True
        self.silence_timer = C.EXIT_SILENCE
        self.sfx.append(("door", self.exit.x, self.exit.y))
        self.events.append(("exit_open",))

    # --- bahaya ------------------------------------------------------------
    def touching_monster(self):
        """Makhluk yang sedang menyentuh pemain, atau None."""
        p = self.player
        reach = C.PLAYER_RADIUS + C.LISTENER_RADIUS - 2
        for listener in self.listeners:
            if math.hypot(listener.x - p.x, listener.y - p.y) < reach:
                return listener
        w = self.watcher
        if w is not None and w.present and math.hypot(w.x - p.x, w.y - p.y) < 2 * C.PLAYER_RADIUS:
            return w
        return None

    def nearest_listener(self):
        p = self.player
        return min((math.hypot(l.x - p.x, l.y - p.y) for l in self.listeners), default=math.inf)

    def danger(self):
        """Nilai 0..1 untuk detak jantung: kedekatan monster atau stres, mana yang lebih besar."""
        p = self.player
        d = self.nearest_listener()
        w = self.watcher
        if w is not None and w.present:
            d = min(d, math.hypot(w.x - p.x, w.y - p.y))
        proximity = max(0.0, 1.0 - d / C.HEART_RANGE)
        return max(proximity, self.stress.value / 100.0 * C.HEART_STRESS_WEIGHT)

    def _update_stress(self, dt):
        dark_time = self.time - max(self.last_light_time, self.sonar.last_ping_time)
        staring = self.watcher is not None and self.watcher.present and self.watcher.lit_now
        self.stress.update(dt, self.nearest_listener(), dark_time, staring)

    # --- kejadian dari director --------------------------------------------
    def _tile_occupied(self, tile):
        cx, cy = tile_center(tile)
        entities = [self.player, *self.listeners, *self.shadows]
        entities += [f for f in self.fragments if not f.taken]
        entities += [b for b in self.batteries if not b.taken]
        if self.watcher is not None and self.watcher.visible:
            entities.append(self.watcher)
        return any(abs(e.x - cx) < C.TILE and abs(e.y - cy) < C.TILE for e in entities)

    def try_shift_wall(self):
        p = self.player
        want_close = self.rng.random() < 0.5
        lpx, lpy = self.sonar.last_ping_pos
        recent_ping = self.time - self.sonar.last_ping_time < C.SHIFT_SONAR_WINDOW
        for t in self.rng.sample(self.connectors, min(40, len(self.connectors))):
            cx, cy = tile_center(t)
            if math.hypot(cx - p.x, cy - p.y) < C.SHIFT_MIN_DIST:
                continue
            if self.flashlight.lit(cx, cy, self.maze, margin=C.TILE):
                continue
            if recent_ping and math.hypot(cx - lpx, cy - lpy) < C.SONAR_RANGE:
                continue
            is_wall = self.maze.is_wall(*t)
            if want_close and not is_wall:
                if self._tile_occupied(t) or not self.maze.try_close(t):
                    continue
            elif not want_close and is_wall:
                self.maze.open_tile(t)
            else:
                continue
            self.changed_tiles.append(t)
            for listener in self.listeners:
                listener.invalidate(self.maze)
            if self.watcher is not None:
                self.watcher.path = []
            self.sfx.append(("grind", cx, cy))
            self.stress.add(C.STRESS_SHIFT)
            return True
        return False

    def mimic_ping(self):
        w = self.watcher
        p = self.player
        if w is not None and w.present:
            x, y = w.x, w.y
        else:
            lo, hi = C.MIMIC_RANDOM_DIST
            options = [
                tile_center(t) for t in self.maze.floor_tiles()
                if lo <= math.hypot(tile_center(t)[0] - p.x, tile_center(t)[1] - p.y) <= hi
            ]
            if not options:
                return
            x, y = self.rng.choice(options)
        self.sonar.add_ring(x, y)
        self.noise.emit(x, y, C.SONAR_NOISE, "mimic")
        self.sfx.append(("mimic", x, y))
        self.stress.add(C.STRESS_MIMIC)

    def whisper(self):
        p = self.player
        side = self.rng.choice((-1, 1))
        self.sfx.append(("whisper", p.x + side * 160, p.y))

    def spawn_shadow(self):
        fl = self.flashlight
        if not fl.on:
            return False
        ox, oy = fl.origin
        a = fl.aim + self.rng.choice((-1, 1)) * C.LIGHT_HALF_ANGLE * 0.85
        d = fl.range * self.rng.uniform(0.55, 0.8)
        x, y = ox + math.cos(a) * d, oy + math.sin(a) * d
        if self.maze.is_wall(*tile_of(x, y)) or not line_of_sight(self.maze, ox, oy, x, y):
            return False
        self.shadows.append(Shadow(x, y, self.rng))
        return True

    def _update_shadows(self, dt):
        keep = []
        for s in self.shadows:
            s.life -= dt
            s.animate(dt, self.rng)
            if s.life > 0 and self.flashlight.on and not self.flashlight.central(s.x, s.y):
                keep.append(s)
        self.shadows = keep

    # --- mati & debug ------------------------------------------------------
    def respawn(self):
        """Muncul lagi di pintu masuk setelah kehilangan nyawa."""
        self.dead = False
        sx, sy = tile_center(self.start_tile)
        self.player = Player(sx, sy, self._open_direction(self.start_tile))
        self.noise.clear()
        self.sonar.clear_active()
        self.shadows.clear()
        self.stones.clear()
        self.break_tile = None
        self.break_progress = 0.0
        dist = self.maze.bfs(self.start_tile)
        far = [t for t, d in dist.items() if d >= C.LISTENER_RESPAWN_MIN_TILES]
        if not far:
            far = sorted(dist, key=dist.get)[-10:]
        for listener in self.listeners:
            listener.relocate(*tile_center(self.rng.choice(far)))
        if self.watcher is not None:
            self.watcher.reset()
        self.stress.set_floor(self.run.stress_floor())
        self.stress.add(C.STRESS_DEATH)
        self.last_light_time = self.time
        self.director.on_respawn()

    def debug_collect_all(self):
        p = self.player
        for f in self.fragments:
            if not f.taken:
                f.x, f.y = p.x, p.y

    def debug_to_exit(self):
        self.player.x, self.player.y = self.exit.x, self.exit.y
