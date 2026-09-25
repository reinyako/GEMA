from gema.render.icon import draw_icon


def test_icon_every_size_has_transparent_corners():
    for size in (16, 24, 32, 48, 256):
        img = draw_icon(size)
        assert img.get_size() == (size, size)
        assert img.get_at((0, 0)).a == 0
        assert img.get_at((size // 2, size // 2)).a == 255
