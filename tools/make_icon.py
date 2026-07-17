"""Generuje dedykowaną ikonę aplikacji: resources/app_icon.png i app_icon.ico.

Motyw: ciemny kafel z akcentową kartą klienta i sylwetką — spójny z UI.
"""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw

OUT = Path(__file__).resolve().parent.parent / "resources"

BG_TOP = (29, 35, 48)      # #1D2330
BG_BOTTOM = (18, 23, 34)   # #121722
ACCENT = (76, 141, 255)    # #4C8DFF
CARD = (32, 39, 55)        # #202737
LIGHT = (242, 244, 247)    # #F2F4F7
MUTED = (143, 163, 200)


def _rounded(draw: ImageDraw.ImageDraw, box, radius, fill) -> None:
    draw.rounded_rectangle(box, radius=radius, fill=fill)


def render(size: int) -> Image.Image:
    scale = size / 256
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # pionowy gradient tła w zaokrąglonym kwadracie
    radius = int(56 * scale)
    for y in range(size):
        t = y / size
        r = int(BG_TOP[0] * (1 - t) + BG_BOTTOM[0] * t)
        g = int(BG_TOP[1] * (1 - t) + BG_BOTTOM[1] * t)
        b = int(BG_TOP[2] * (1 - t) + BG_BOTTOM[2] * t)
        draw.line([(0, y), (size, y)], fill=(r, g, b, 255))
    mask = Image.new("L", (size, size), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, size - 1, size - 1], radius=radius, fill=255)
    img.putalpha(mask)
    draw = ImageDraw.Draw(img)

    # karta klienta (panel)
    _rounded(draw, [int(52 * scale), int(60 * scale), int(204 * scale), int(196 * scale)],
             int(20 * scale), CARD)
    # akcentowy pasek nagłówka karty
    _rounded(draw, [int(52 * scale), int(60 * scale), int(204 * scale), int(96 * scale)],
             int(20 * scale), ACCENT)
    draw.rectangle([int(52 * scale), int(82 * scale), int(204 * scale), int(96 * scale)], fill=ACCENT)

    # sylwetka (głowa + tors) na karcie
    cx = int(128 * scale)
    draw.ellipse([cx - int(24 * scale), int(104 * scale), cx + int(24 * scale), int(152 * scale)], fill=LIGHT)
    draw.pieslice([cx - int(40 * scale), int(150 * scale), cx + int(40 * scale), int(214 * scale)],
                  180, 360, fill=LIGHT)

    # linie „danych” pod sylwetką
    for i, w in enumerate((70, 52)):
        y = int((166 + i * 16) * scale)
        _rounded(draw, [int(150 * scale), y, int((150 + w) * scale), y + int(8 * scale)],
                 int(4 * scale), MUTED)

    return img


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    master = render(256)
    master.save(OUT / "app_icon.png")
    sizes = [16, 24, 32, 48, 64, 128, 256]
    master.save(OUT / "app_icon.ico", sizes=[(s, s) for s in sizes])
    print(f"Zapisano: {OUT / 'app_icon.png'} i {OUT / 'app_icon.ico'}")


if __name__ == "__main__":
    main()
