"""Poison vial — GREEN_GLASS brightness comparison sheet.

Five lighter candidates for the dominant glass-body green, plus a
left-most CURRENT cell so the user can see how much brighter each
candidate reads vs today's (35, 90, 50). Each cell shows Pip + the
vial at the live 56-px display footprint against a charcoal card.

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


VARIANTS = (
    ("CURRENT", poison_vial.GREEN_GLASS),
    ("V1", ( 55, 120,  65)),
    ("V2", ( 75, 145,  80)),
    ("V3", ( 95, 165,  85)),
    ("V4", (115, 185,  90)),
    ("V5", (140, 205,  95)),
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


def _draw_vial(surf, cx, cy, glass_rgb):
    """Render the live poison_vial sprite with GREEN_GLASS swapped
    to `glass_rgb` for this render only. Restores the original
    constant + cache after."""
    prev_glass = poison_vial.GREEN_GLASS
    prev_cache = getattr(poison_vial, "_VIAL_CACHE", None)
    poison_vial.GREEN_GLASS = glass_rgb
    poison_vial._VIAL_CACHE = None
    poison_vial.draw(surf, int(cx), int(cy), 0.0)
    poison_vial.GREEN_GLASS = prev_glass
    poison_vial._VIAL_CACHE = prev_cache


def _build_cell(glass_rgb):
    cell = pygame.Surface((CELL_W, CELL_H))
    cell.fill((32, 34, 42))
    pip = parrot.get_parrot(0, 0.0)
    cell.blit(pip, pip.get_rect(center=(46, CELL_H // 2)))
    _draw_vial(cell, CELL_W - 50, CELL_H // 2, glass_rgb)
    pygame.draw.rect(cell, (45, 50, 62), cell.get_rect(), 1)
    return cell


def main():
    out_dir = os.path.join(os.path.dirname(THIS_DIR),
                           "docs", "screenshots", "icon_sizes")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "poison_green_variants.png")

    n = len(VARIANTS)
    sheet_w = PAD * 2 + n * (CELL_W + PAD) - PAD
    sheet_h = HEADER_H + CELL_H + 40
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill(CARD_BG)

    title = _font(20, bold=True).render(
        "POISON vial — lighter GREEN_GLASS variants",
        True, LABEL)
    sheet.blit(title, (PAD, 14))
    sub = _font(13).render(
        "Left = current; V1..V5 step up the brightness ramp toward the "
        "liquid + toxic tones already in the palette.",
        True, SUB)
    sheet.blit(sub, (PAD, 38))

    for i, (code, rgb) in enumerate(VARIANTS):
        x = PAD + i * (CELL_W + PAD)
        y = HEADER_H
        sheet.blit(_build_cell(rgb), (x, y))
        cap = _font(13, bold=True).render(
            f"{code} — ({rgb[0]}, {rgb[1]}, {rgb[2]})",
            True, LABEL)
        sheet.blit(cap, (x + (CELL_W - cap.get_width()) // 2,
                         y + CELL_H + 6))

    pygame.image.save(sheet, out_path)
    print(f"saved {out_path}  ({sheet_w}x{sheet_h})")


if __name__ == "__main__":
    main()
