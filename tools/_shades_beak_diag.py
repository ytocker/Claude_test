"""Scratch diagnostic: large-zoom head crop of every shade on Pip, to judge
beak occlusion / natural seating. Headless. Writes docs/shades/_beak_diag.png."""
import os, sys
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
import pygame
pygame.init()
pygame.display.set_mode((1, 1))
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from game import parrot, store_skins  # noqa: E402
from game import (  # noqa: E402
    shades_nerd, shades_round, shades_heart, shades_star, shades_black,
    shades_white, shades_3d, shades_pixel, shades_ski, shades_monocle,
    shades_cyber,
)

STYLES = [
    ("nerd", shades_nerd.draw_shades), ("round", shades_round.draw_shades),
    ("heart", shades_heart.draw_shades), ("star", shades_star.draw_shades),
    ("black", shades_black.draw_shades), ("white", shades_white.draw_shades),
    ("3d", shades_3d.draw_shades), ("pixel", shades_pixel.draw_shades),
    ("ski", shades_ski.draw_shades), ("monocle", shades_monocle.draw_shades),
    ("cyber", shades_cyber.draw_shades), ("(bare)", None),
]


def on_pip(fn, angle=-8):
    comp = pygame.Surface((store_skins.COMPOSITE_W, store_skins.COMPOSITE_H),
                          pygame.SRCALPHA)
    comp.blit(parrot._build_frame_bare(angle), (0, store_skins.PARROT_DY))
    if fn:
        fn(comp, 50, 40, 22, 1)
    return parrot._add_outline(comp)


def main():
    pygame.font.init()
    font = pygame.font.SysFont("Arial", 18, bold=True)
    ZOOM = 7
    # Crop the head region of the composite: x[30,64], y[20,60].
    CROP = pygame.Rect(28, 20, 36, 42)
    cw, ch = CROP.w * ZOOM, CROP.h * ZOOM
    COLS = 4
    PAD, LAB = 14, 26
    rows = (len(STYLES) + COLS - 1) // COLS
    W = PAD + COLS * (cw + PAD)
    H = 50 + rows * (ch + LAB + PAD)
    sheet = pygame.Surface((W, H))
    sheet.fill((28, 32, 46))
    sheet.blit(font.render("SHADES beak-occlusion diagnostic  ·  head crop @7x  ·  beak=orange front",
                           True, (235, 240, 250)), (PAD, 14))
    for i, (name, fn) in enumerate(STYLES):
        c, r = i % COLS, i // COLS
        x = PAD + c * (cw + PAD)
        y = 50 + r * (ch + LAB + PAD)
        # checker bg
        for yy in range(0, ch, 14):
            for xx in range(0, cw, 14):
                col = (52, 58, 76) if ((xx // 14 + yy // 14) % 2 == 0) else (42, 48, 64)
                sheet.fill(col, (x + xx, y + yy, 14, 14))
        pip = on_pip(fn)
        crop = pip.subsurface(CROP).copy()
        big = pygame.transform.scale(crop, (cw, ch))
        sheet.blit(big, (x, y))
        pygame.draw.rect(sheet, (70, 78, 100), (x, y, cw, ch), 1)
        sheet.blit(font.render(name, True, (220, 226, 240)), (x, y + ch + 4))
    out = os.path.join(_ROOT, "docs", "shades", "_beak_diag.png")
    pygame.image.save(sheet, out)
    print("wrote", out, sheet.get_size())


if __name__ == "__main__":
    main()
