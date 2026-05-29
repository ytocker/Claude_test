"""Poison vial — full green-palette brightness comparison.

Five lighter variants of the vial that shift BOTH the empty-glass
body (GREEN_GLASS) AND the liquid (GREEN_LO) up the brightness ramp
together. The meniscus colour (GREEN_TOX) is also lifted on the
brightest variants so the toxic surface line stays readable above
the liquid.

Output: docs/screenshots/icon_sizes/poison_green_variants.png
"""
from __future__ import annotations

import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(THIS_DIR))

pygame.init()
pygame.display.set_mode((1, 1))

from game import poison_vial, parrot


# Each entry: (label, GREEN_GLASS, GREEN_LO, GREEN_TOX).
# CURRENT keeps GREEN_TOX as-is; later variants step it up too so the
# meniscus stays the brightest layer.
VARIANTS = (
    ("CURRENT",
        ( 35,  90,  50), ( 40, 100,  50), (120, 200,  90)),
    ("V1",
        ( 60, 125,  75), ( 80, 150,  85), (130, 205,  95)),
    ("V2",
        ( 85, 155,  90), (105, 180, 100), (145, 215, 105)),
    ("V3",
        (110, 180, 105), (135, 205, 115), (165, 225, 120)),
    ("V4",
        (140, 205, 120), (165, 225, 130), (190, 235, 140)),
    ("V5",
        (170, 225, 140), (195, 240, 150), (215, 245, 165)),
)


CARD_BG = (24, 26, 34)
LABEL   = (235, 235, 240)
SUB     = (165, 173, 185)

CELL_W = 200
CELL_H = 160
PAD    = 14
HEADER_H = 80


def _font(size, bold=False):
    return pygame.font.SysFont("Arial", size, bold=bold)


def _draw_vial(surf, cx, cy, glass_rgb, liquid_rgb, tox_rgb):
    """Render the vial with the three greens swapped for this render
    only. Restores the originals + cache after."""
    prev_glass = poison_vial.GREEN_GLASS
    prev_lo    = poison_vial.GREEN_LO
    prev_tox   = poison_vial.GREEN_TOX
    prev_cache = getattr(poison_vial, "_VIAL_CACHE", None)
    poison_vial.GREEN_GLASS = glass_rgb
    poison_vial.GREEN_LO    = liquid_rgb
    poison_vial.GREEN_TOX   = tox_rgb
    poison_vial._VIAL_CACHE = None
    poison_vial.draw(surf, int(cx), int(cy), 0.0)
    poison_vial.GREEN_GLASS = prev_glass
    poison_vial.GREEN_LO    = prev_lo
    poison_vial.GREEN_TOX   = prev_tox
    poison_vial._VIAL_CACHE = prev_cache


def _build_cell(glass_rgb, liquid_rgb, tox_rgb):
    cell = pygame.Surface((CELL_W, CELL_H))
    cell.fill((32, 34, 42))
    pip = parrot.get_parrot(0, 0.0)
    cell.blit(pip, pip.get_rect(center=(46, CELL_H // 2)))
    _draw_vial(cell, CELL_W - 50, CELL_H // 2,
               glass_rgb, liquid_rgb, tox_rgb)
    pygame.draw.rect(cell, (45, 50, 62), cell.get_rect(), 1)
    return cell


def _fmt(rgb):
    return f"({rgb[0]:>3}, {rgb[1]:>3}, {rgb[2]:>3})"


def main():
    out_dir = os.path.join(os.path.dirname(THIS_DIR),
                           "docs", "screenshots", "icon_sizes")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "poison_green_variants.png")

    n = len(VARIANTS)
    sheet_w = PAD * 2 + n * (CELL_W + PAD) - PAD
    sheet_h = HEADER_H + CELL_H + 90
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill(CARD_BG)

    title = _font(20, bold=True).render(
        "POISON vial — lighter green variants (glass + liquid both shift)",
        True, LABEL)
    sheet.blit(title, (PAD, 14))
    sub = _font(13).render(
        "Left = current; V1..V5 step both the empty-glass body AND the "
        "liquid up the brightness ramp together.",
        True, SUB)
    sheet.blit(sub, (PAD, 38))

    for i, (code, glass, lo, tox) in enumerate(VARIANTS):
        x = PAD + i * (CELL_W + PAD)
        y = HEADER_H
        sheet.blit(_build_cell(glass, lo, tox), (x, y))
        cap_font = _font(13, bold=True)
        sub_font = _font(11)
        cap = cap_font.render(code, True, LABEL)
        sheet.blit(cap, (x + (CELL_W - cap.get_width()) // 2,
                         y + CELL_H + 6))
        # Three-line legend so the user can match colour-to-cell
        for ln, (legend_lbl, val) in enumerate((
                ("glass", glass), ("liquid", lo), ("tox", tox))):
            text = f"{legend_lbl}  {_fmt(val)}"
            s = sub_font.render(text, True, SUB)
            sheet.blit(s, (x + (CELL_W - s.get_width()) // 2,
                           y + CELL_H + 24 + ln * 14))

    pygame.image.save(sheet, out_path)
    print(f"saved {out_path}  ({sheet_w}x{sheet_h})")


if __name__ == "__main__":
    main()
