"""Labirin berbasis grid petak: pembuatan, pencarian jalur, penempatan, dan pergeseran dinding.

Modul ini tidak memakai pygame supaya mudah dites.
"""

from collections import deque
from dataclasses import dataclass, field

from .. import config as C

FLOOR = 0
WALL = 1
DIRS = ((1, 0), (-1, 0), (0, 1), (0, -1))


def tile_center(tile):
    return (tile[0] + 0.5) * C.TILE, (tile[1] + 0.5) * C.TILE


def tile_of(x, y):
    return int(x // C.TILE), int(y // C.TILE)


class Maze:
    """Grid petak. Sel labirin ada di koordinat ganjil, petak di antaranya adalah sambungan."""

    def __init__(self, grid, rooms=()):
        self.grid = grid
        self.h = len(grid)
        self.w = len(grid[0])
        self.rooms = list(rooms)  # (tx0, ty0, tx1, ty1), inklusif
        self.version = 0

    # --- dasar -----------------------------------------------------------
    def is_wall(self, tx, ty):
        return tx < 0 or ty < 0 or tx >= self.w or ty >= self.h or self.grid[ty][tx] == WALL

    def floor_neighbors(self, tile):
        tx, ty = tile
        grid, w, h = self.grid, self.w, self.h
        for dx, dy in DIRS:
            nx, ny = tx + dx, ty + dy
            if 0 <= nx < w and 0 <= ny < h and grid[ny][nx] == FLOOR:
                yield (nx, ny)

    def degree(self, tile):
        return sum(1 for _ in self.floor_neighbors(tile))

    def floor_tiles(self):
        return [(x, y) for y in range(self.h) for x in range(self.w) if self.grid[y][x] == FLOOR]

    def cell_tiles(self):
        return [
            (x, y)
            for y in range(1, self.h, 2)
            for x in range(1, self.w, 2)
            if self.grid[y][x] == FLOOR
        ]

    def dead_ends(self):
        return [t for t in self.cell_tiles() if self.degree(t) == 1]

    def room_tiles(self):
        out = []
        for x0, y0, x1, y1 in self.rooms:
            out.extend(
                (x, y) for y in range(y0, y1 + 1, 2) for x in range(x0, x1 + 1, 2)
                if self.grid[y][x] == FLOOR
            )
        return out

    # --- pencarian -------------------------------------------------------
    def bfs(self, start, limit=None):
        """Jarak (dalam petak) dari start ke setiap petak lantai yang terjangkau."""
        if self.is_wall(*start):
            return {}
        dist = {start: 0}
        queue = deque([start])
        while queue:
            cur = queue.popleft()
            d = dist[cur]
            if limit is not None and d >= limit:
                continue
            for nxt in self.floor_neighbors(cur):
                if nxt not in dist:
                    dist[nxt] = d + 1
                    queue.append(nxt)
        return dist

    def path(self, start, goal):
        """Jalur terpendek berupa daftar petak (termasuk start dan goal), atau None."""
        if self.is_wall(*start) or self.is_wall(*goal):
            return None
        if start == goal:
            return [start]
        prev = {start: None}
        queue = deque([start])
        while queue:
            cur = queue.popleft()
            if cur == goal:
                break
            for nxt in self.floor_neighbors(cur):
                if nxt not in prev:
                    prev[nxt] = cur
                    queue.append(nxt)
        if goal not in prev:
            return None
        out = []
        node = goal
        while node is not None:
            out.append(node)
            node = prev[node]
        out.reverse()
        return out

    def is_connected(self):
        tiles = self.floor_tiles()
        if not tiles:
            return True
        return len(self.bfs(tiles[0])) == len(tiles)

    # --- pergeseran ------------------------------------------------------
    def connectors(self):
        """Petak sambungan di antara dua sel (tepat satu koordinat ganjil), tidak di tepi."""
        return [
            (x, y)
            for y in range(1, self.h - 1)
            for x in range(1, self.w - 1)
            if (x % 2) != (y % 2)
        ]

    def open_tile(self, tile):
        x, y = tile
        if self.grid[y][x] == WALL:
            self.grid[y][x] = FLOOR
            self.version += 1
            return True
        return False

    def try_close(self, tile):
        """Menutup petak kalau labirin tetap terhubung penuh. Mengembalikan True kalau berhasil."""
        x, y = tile
        if self.grid[y][x] == WALL:
            return False
        self.grid[y][x] = WALL
        if self.is_connected():
            self.version += 1
            return True
        self.grid[y][x] = FLOOR
        return False


# --- pembuatan -----------------------------------------------------------
def generate(cells_w, cells_h, rng, braid=0.0, rooms=0):
    w, h = cells_w * 2 + 1, cells_h * 2 + 1
    grid = [[WALL] * w for _ in range(h)]
    sx, sy = rng.randrange(cells_w), rng.randrange(cells_h)
    grid[2 * sy + 1][2 * sx + 1] = FLOOR
    visited = {(sx, sy)}
    stack = [(sx, sy)]
    while stack:
        cx, cy = stack[-1]
        options = [
            (cx + dx, cy + dy)
            for dx, dy in DIRS
            if 0 <= cx + dx < cells_w and 0 <= cy + dy < cells_h and (cx + dx, cy + dy) not in visited
        ]
        if not options:
            stack.pop()
            continue
        nx, ny = rng.choice(options)
        grid[cy + ny + 1][cx + nx + 1] = FLOOR
        grid[2 * ny + 1][2 * nx + 1] = FLOOR
        visited.add((nx, ny))
        stack.append((nx, ny))
    maze = Maze(grid)
    _braid(maze, cells_w, cells_h, rng, braid)
    _carve_rooms(maze, cells_w, cells_h, rng, rooms)
    return maze


def _braid(maze, cells_w, cells_h, rng, ratio):
    """Membuka sebagian jalan buntu supaya ada jalur memutar untuk kabur."""
    if ratio <= 0:
        return
    grid = maze.grid
    cells = [(cx, cy) for cy in range(cells_h) for cx in range(cells_w)]
    rng.shuffle(cells)
    for cx, cy in cells:
        tx, ty = 2 * cx + 1, 2 * cy + 1
        if maze.degree((tx, ty)) != 1 or rng.random() >= ratio:
            continue
        options = []
        for dx, dy in DIRS:
            nx, ny = cx + dx, cy + dy
            if 0 <= nx < cells_w and 0 <= ny < cells_h and grid[ty + dy][tx + dx] == WALL:
                options.append((dx, dy, maze.degree((2 * nx + 1, 2 * ny + 1)) == 1))
        if not options:
            continue
        preferred = [o for o in options if o[2]] or options
        dx, dy, _ = rng.choice(preferred)
        grid[ty + dy][tx + dx] = FLOOR


def _carve_rooms(maze, cells_w, cells_h, rng, count):
    """Memahat ruangan kecil 2x2 sel (3x3 petak)."""
    if count <= 0 or cells_w < 2 or cells_h < 2:
        return
    placed = []
    for _ in range(count * 12):
        if len(placed) >= count:
            break
        cx, cy = rng.randrange(cells_w - 1), rng.randrange(cells_h - 1)
        if any(abs(cx - px) < 3 and abs(cy - py) < 3 for px, py in placed):
            continue
        rect = (2 * cx + 1, 2 * cy + 1, 2 * cx + 3, 2 * cy + 3)
        for y in range(rect[1], rect[3] + 1):
            for x in range(rect[0], rect[2] + 1):
                maze.grid[y][x] = FLOOR
        placed.append((cx, cy))
        maze.rooms.append(rect)


def final_corridor(rng):
    """Lorong panjang berkelok untuk lantai terakhir: satu-satunya jalur di sebuah labirin."""
    best = None
    for _ in range(30):
        m = generate(15, 5, rng)
        start, goal = (1, 1), (m.w - 2, m.h - 2)
        route = m.path(start, goal)
        if route and 55 <= len(route) <= 95:
            best = (m, route)
            break
        if route and (best is None or abs(len(route) - 75) < abs(len(best[1]) - 75)):
            best = (m, route)
    m, route = best
    grid = [[WALL] * m.w for _ in range(m.h)]
    for x, y in route:
        grid[y][x] = FLOOR
    return Maze(grid), route[0], route[-1]


# --- penempatan ----------------------------------------------------------
@dataclass
class Layout:
    start: tuple
    exit: tuple
    fragments: list = field(default_factory=list)
    batteries: list = field(default_factory=list)
    listeners: list = field(default_factory=list)


def _spread_pick(candidates, n, rng, anchors):
    """Memilih n petak yang saling berjauhan (dan jauh dari anchors), dengan sedikit acak."""
    pool = list(candidates)
    rng.shuffle(pool)
    picked = []
    for _ in range(min(n, len(pool))):
        refs = list(anchors) + picked

        def score(t):
            return min((t[0] - r[0]) ** 2 + (t[1] - r[1]) ** 2 for r in refs)

        pool.sort(key=score, reverse=True)
        choice = rng.choice(pool[:3])
        picked.append(choice)
        pool.remove(choice)
    return picked


def plan_layout(maze, rng, n_fragments, n_batteries, n_listeners):
    corners = [(1, 1), (maze.w - 2, 1), (1, maze.h - 2), (maze.w - 2, maze.h - 2)]
    corners = [c for c in corners if not maze.is_wall(*c)] or [maze.cell_tiles()[0]]
    start = rng.choice(corners)
    dist = maze.bfs(start)
    cells = [t for t in maze.cell_tiles() if t in dist]
    exit_tile = max(cells, key=lambda t: (dist[t], t))
    taken = {start, exit_tile}

    dead = [t for t in maze.dead_ends() if t not in taken]
    rooms = [t for t in maze.room_tiles() if t not in taken and t in dist]
    min_frag = 2 * C.FRAGMENT_MIN_START_CELLS
    candidates = [t for t in dict.fromkeys(dead + rooms) if dist.get(t, 0) >= min_frag]
    if len(candidates) < n_fragments:
        candidates = [t for t in cells if t not in taken and dist[t] >= 8]
    if len(candidates) < n_fragments:
        candidates = [t for t in cells if t not in taken]
    fragments = _spread_pick(candidates, n_fragments, rng, anchors=[start, exit_tile])
    taken.update(fragments)

    batteries = [t for t in dead if t not in taken and dist.get(t, 0) >= 6]
    rng.shuffle(batteries)
    batteries = batteries[:n_batteries]
    if len(batteries) < n_batteries:
        extra = [t for t in cells if t not in taken and t not in batteries and dist[t] >= 6]
        rng.shuffle(extra)
        batteries += extra[: n_batteries - len(batteries)]
    taken.update(batteries)

    spawn = [t for t in cells if t not in taken and dist[t] >= 2 * C.LISTENER_MIN_SPAWN_CELLS]
    if len(spawn) < n_listeners:
        spawn = sorted((t for t in cells if t not in taken), key=dist.get, reverse=True)
        spawn = spawn[: max(n_listeners * 3, 6)]
    if len(spawn) >= n_listeners:
        listeners = rng.sample(spawn, n_listeners)
    else:
        listeners = [rng.choice(spawn) for _ in range(n_listeners)]

    return Layout(start, exit_tile, fragments, batteries, listeners)
