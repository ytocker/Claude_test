"""Scratch option-strip for how far right to seat all 11 shades.

For each style, render the on-Pip head crop at a row of candidate in-game
anchors (cx values) so the rightward seat can be picked at a glance. The
product ICON is anchor-independent, so it isn't shown. Headless.

Run:  SDL_VIDEODRIVER=dummy python tools/_shades_nudge_options.py "53,55,57,59"
"""
import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
import pygame  # noqa: E402

pygame.init()
pygame.display.set_mode((1, 1))

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from game import parrot, store_skins, glasses_skins  # noqa: E402
from game import (  # noqa: E402
    shades_nerd, shades_round, shades_heart, shades_star, shades_black,
    shades_white, shades_3d, shades_pixel, shades_ski, shades_monocle,
    shades_cyber,
)

STYLES = [
    ("nerd", shades_nerd), ("round", shades_round), ("heart", shades_heart),
    ("star", shades_star), ("black", shades_black), ("white", shades_white),
    ("3d", shades_3d), ("pixel", shades_pixel), ("ski", shades_ski),
    ("monocle", shades_monocle), ("cyber", shades_cyber),
]


def head_crop(fn, cx, zoom=5):
    comp = pygame.Surface((store_skins.COMPOSITE_W, store_skins.COMPOSITE_H),
                          pygame.SRCALPHA)
    comp.blit(parrot._build_frame_bare(-8), (0, store_skins.PARROT_DY))
    fn(comp, cx, 40, 22, 1)
    pip = parrot._add_outline(comp)
    crop = pip.subsurface(pygame.Rect(28, 20, 36, 42)).copy()
    return pygame.transform.scale(crop, (36 * zoom, 42 * zoom))


def _checker(surf, rect, a=(54, 60, 78), b=(44, 50, 66), s=10):
    for y in range(rect.top, rect.bottom, s):
        for x in range(rect.left, rect.right, s):
            c = a if ((x // s + y // s) % 2 == 0) else b
            surf.fill(c, (x, y, min(s, rect.right - x), min(s, rect.bottom - y)))


def main():
    arg = sys.argv[1] if len(sys.argv) > 1 else "53,55,57,59"
    cxs = [int(v) for v in arg.split(",")]
    cur = glasses_skins._EYE_CX

    pygame.font.init()
    title_f = pygame.font.SysFont("Arial", 20, bold=True)
    lab_f = pygame.font.SysFont("Arial", 15, bold=True)
    sub_f = pygame.font.SysFont("Arial", 12, bold=True)

    ZOOM = 5
    cw, ch = 36 * ZOOM, 42 * ZOOM
    GAP = 8
    LABEL_W = 70
    CELL_W = LABEL_W + len(cxs) * (cw + GAP) + 12
    CELL_H = ch + 40
    MARGIN = 22
    TITLE_H = 54
    W = MARGIN * 2 + CELL_W
    H = TITLE_H + MARGIN + len(STYLES) * (CELL_H + 14)

    sheet = pygame.Surface((W, H))
    sheet.fill((28, 32, 46))
    sheet.blit(title_f.render(
        "SKYBIT — SHADES  ·  how far right?  ·  candidate in-game anchors (cx)",
        True, (235, 240, 250)), (MARGIN, 16))

    for i, (name, mod) in enumerate(STYLES):
        y = TITLE_H + MARGIN + i * (CELL_H + 14)
        cell = pygame.Rect(MARGIN, y, CELL_W, CELL_H)
        pygame.draw.rect(sheet, (40, 45, 62), cell, border_radius=10)
        pygame.draw.rect(sheet, (70, 78, 100), cell, 1, border_radius=10)
        sheet.blit(lab_f.render(name, True, (235, 240, 250)),
                   (cell.left + 12, cell.centery - 8))

        for j, cx in enumerate(cxs):
            x = cell.left + LABEL_W + j * (cw + GAP)
            r = pygame.Rect(x, cell.top + 22, cw, ch)
            _checker(sheet, r)
            sheet.blit(head_crop(mod.draw_shades, cx, ZOOM), r.topleft)
            tag = f"cx={cx}" + ("  (now)" if cx == cur else "")
            col = (150, 235, 160) if cx == cur else (210, 218, 236)
            sheet.blit(sub_f.render(tag, True, col), (x, r.bottom + 2))

    out = os.path.join(_ROOT, "docs", "shades", "nudge_options.png")
    pygame.image.save(sheet, out)
    print("wrote", out, sheet.get_size())


if __name__ == "__main__":
    main()
