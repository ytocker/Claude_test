"""Scratch BEFORE/AFTER review sheet for the SHADES on-Pip seating fix (R2).

Same layout as round_1: for each of the 11 eyewear styles it shows the OLD
(R0-baseline) head crop, the NEW (current R2) head crop, and the product ICON;
plus a (bare) reference cell showing the eye position the glasses seat onto.

The OLD drawers come from the pre-fix baseline package given via SK_OLD_SHADES
so this harness stays a pure renderer with no vendored copies. The R2 goal is a
NATURAL forward seat: the near lens grazes / slightly laps the beak BASE while
the beak tip + hook stay visible — not a beak fully cleared, not a beak buried.
Headless. Writes docs/shades/round_2.png.
"""
import importlib
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

NEW = [
    ("nerd", shades_nerd), ("round", shades_round), ("heart", shades_heart),
    ("star", shades_star), ("black", shades_black), ("white", shades_white),
    ("3d", shades_3d), ("pixel", shades_pixel), ("ski", shades_ski),
    ("monocle", shades_monocle), ("cyber", shades_cyber),
]

_OLD_DIR = os.environ["SK_OLD_SHADES"]
_old_parent = os.path.dirname(_OLD_DIR)
if _old_parent not in sys.path:
    sys.path.insert(0, _old_parent)
_old_pkg = os.path.basename(_OLD_DIR)


def _old_fn(name):
    mod = importlib.import_module(f"{_old_pkg}.shades_{name}")
    return mod.draw_shades


def head_crop(fn, zoom=7, cx=glasses_skins._EYE_CX):
    comp = pygame.Surface((store_skins.COMPOSITE_W, store_skins.COMPOSITE_H),
                          pygame.SRCALPHA)
    comp.blit(parrot._build_frame_bare(-8), (0, store_skins.PARROT_DY))
    if fn:
        fn(comp, cx, 40, 22, 1)
    pip = parrot._add_outline(comp)
    crop = pip.subsurface(pygame.Rect(28, 20, 36, 42)).copy()
    return pygame.transform.scale(crop, (36 * zoom, 42 * zoom))


def product_shot(fn, canvas=150):
    surf = pygame.Surface((canvas, canvas), pygame.SRCALPHA)
    fn(surf, canvas // 2, canvas // 2, 92, 1)
    return parrot._add_outline(surf)


def _checker(surf, rect, a=(54, 60, 78), b=(44, 50, 66), s=12):
    for y in range(rect.top, rect.bottom, s):
        for x in range(rect.left, rect.right, s):
            c = a if ((x // s + y // s) % 2 == 0) else b
            surf.fill(c, (x, y, min(s, rect.right - x), min(s, rect.bottom - y)))


def main():
    pygame.font.init()
    title_f = pygame.font.SysFont("Arial", 20, bold=True)
    lab_f = pygame.font.SysFont("Arial", 15, bold=True)
    sub_f = pygame.font.SysFont("Arial", 12)

    ZOOM = 6
    cw, ch = 36 * ZOOM, 42 * ZOOM
    prod_w = 150
    CELL_W = cw * 2 + prod_w + 48
    CELL_H = max(ch, prod_w) + 36
    COLS = 2
    items = NEW + [("(bare)", None)]
    rows = (len(items) + COLS - 1) // COLS
    MARGIN = 24
    TITLE_H = 60
    W = MARGIN * 2 + COLS * CELL_W + (COLS - 1) * MARGIN
    H = TITLE_H + MARGIN + rows * (CELL_H + MARGIN)

    sheet = pygame.Surface((W, H))
    sheet.fill((28, 32, 46))
    sheet.blit(title_f.render(
        "SKYBIT — SHADES on-Pip seating fix  ·  round 2  ·  natural forward seat (near lens laps beak base)",
        True, (235, 240, 250)), (MARGIN, 18))

    for i, (name, mod) in enumerate(items):
        col, row = i % COLS, i // COLS
        x = MARGIN + col * (CELL_W + MARGIN)
        y = TITLE_H + MARGIN + row * (CELL_H + MARGIN)
        cell = pygame.Rect(x, y, CELL_W, CELL_H)
        pygame.draw.rect(sheet, (40, 45, 62), cell, border_radius=10)
        pygame.draw.rect(sheet, (70, 78, 100), cell, 1, border_radius=10)

        if mod is None:
            bare = head_crop(None, ZOOM)
            r = pygame.Rect(cell.left + 16, cell.top + 24, cw, ch)
            _checker(sheet, r)
            sheet.blit(bare, r.topleft)
            sheet.blit(lab_f.render("(bare) — eye anchor", True, (230, 236, 248)),
                       (cell.left + 16, cell.top + 4))
            sheet.blit(sub_f.render("glasses seat ON this eye, lapping the beak base toward the front",
                                    True, (180, 188, 206)),
                       (cell.left + 16, cell.top + ch + 28))
            continue

        old = head_crop(_old_fn(name), ZOOM, cx=51)
        new = head_crop(mod.draw_shades, ZOOM)
        icon = product_shot(mod.draw_shades)

        sheet.blit(lab_f.render(name, True, (235, 240, 250)),
                   (cell.left + 16, cell.top + 4))

        ox = cell.left + 16
        ny = cell.top + 24
        r_old = pygame.Rect(ox, ny, cw, ch)
        _checker(sheet, r_old)
        sheet.blit(old, r_old.topleft)
        sheet.blit(sub_f.render("OLD (R0 baseline)", True, (255, 150, 150)),
                   (ox, ny + ch + 2))

        nx = ox + cw + 12
        r_new = pygame.Rect(nx, ny, cw, ch)
        _checker(sheet, r_new)
        sheet.blit(new, r_new.topleft)
        sheet.blit(sub_f.render("NEW (R2)", True, (150, 235, 160)),
                   (nx, ny + ch + 2))

        ix = nx + cw + 12
        r_icon = pygame.Rect(ix, ny, prod_w, prod_w)
        _checker(sheet, r_icon, a=(48, 54, 72), b=(40, 46, 62))
        ir = icon.get_rect(center=r_icon.center)
        sheet.blit(icon, ir.topleft)
        sheet.blit(sub_f.render("ICON (product shot)", True, (200, 208, 226)),
                   (ix, ny + prod_w + 2))

    out = os.path.join(_ROOT, "docs", "shades", "round_2.png")
    pygame.image.save(sheet, out)
    print("wrote", out, sheet.get_size())


if __name__ == "__main__":
    main()
