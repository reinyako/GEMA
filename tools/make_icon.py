"""Membuat file ikon GEMA (.ico untuk Windows, dan .png besar) dari gema/render/icon.py.

Contoh:
    python tools/make_icon.py --out build/gema.ico --png build/gema.png
"""

import argparse
import io
import os
import struct
import sys
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pygame  # noqa: E402

from gema.render.icon import draw_icon  # noqa: E402

# semua ukuran yang dipakai Explorer, taskbar, dan Alt+Tab di berbagai skala DPI
ICO_SIZES = (16, 20, 24, 32, 40, 48, 64, 128, 256)


def png_bytes(surface):
    buf = io.BytesIO()
    pygame.image.save(surface, buf, "icon.png")
    return buf.getvalue()


def write_ico(path, sizes=ICO_SIZES):
    """File .ico berisi satu gambar PNG per ukuran (didukung sejak Windows Vista)."""
    images = [(s, png_bytes(draw_icon(s))) for s in sizes]
    header = struct.pack("<HHH", 0, 1, len(images))
    offset = 6 + 16 * len(images)
    entries, data = [], []
    for size, png in images:
        # lebar/tinggi 0 berarti 256
        entries.append(struct.pack("<BBBBHHII", size % 256, size % 256, 0, 0, 1, 32, len(png), offset))
        data.append(png)
        offset += len(png)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(header + b"".join(entries) + b"".join(data))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="build/gema.ico")
    ap.add_argument("--png", help="simpan juga versi PNG 512 piksel")
    args = ap.parse_args()
    pygame.init()
    write_ico(Path(args.out))
    print(args.out)
    if args.png:
        Path(args.png).parent.mkdir(parents=True, exist_ok=True)
        pygame.image.save(draw_icon(512), args.png)
        print(args.png)


if __name__ == "__main__":
    main()
