"""Size-variant sheet for the secret-tier pickup icons (poison, knight,
skateboard). Each cell shows a gameplay-scale strip with Pip on the left
and the candidate pickup on the right, so the user can see how the size
actually reads in-flight.

Output: docs/screenshots/icon_sizes/round_1.png
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

from game.entities import PowerUp
from game import knight_skin, poison_vial, parrot, biome


SIZES = (32, 40, 48, 56, 72)
LABELS = ("KNIGHT (shield)", "POISON (vial)", "SKATEBOARD (skull-bunny)")

CARD_BG = (24, 26, 34)
LABEL   = (235, 235, 240)
SUB     = (160, 168, 180)

PAD       = 14
STRIP_W   = 130            # gameplay-mock strip width
STRIP_H   = 110            # gameplay-mock strip height
ROW_GAP   = 14
HEADER_H  = 80
LABEL_COL = 132            # left column for the row label


def _font(size, bold=False):
    return pygame.font.SysFont("Arial", size, bold=bold)


def _sky_strip(w, h):
    """Approximate the score-450 biome (~phase 0.46 — golden-hour to dusk
    transition) so the icons sit on a representative gameplay background."""
    pal = biome.palette_for_phase(0.46)
    top = pal.get("sky_top", (110, 165, 220))
    bot = pal.get("sky_bot", (220, 200, 200))
    surf = pygame.Surface((w, h))
    for y in range(h):
        t = y / max(1, h - 1)
        c = (int(top[0] + (bot[0] - top[0]) * t),
             int(top[1] + (bot[1] - top[1]) * t),
             int(top[2] + (bot[2] - top[2]) * t))
        pygame.draw.line(surf, c, (0, y), (w - 1, y))
    return surf


def _draw_pip(surf, cx, cy):
    pip = parrot.get_parrot(0, 0.0)
    surf.blit(pip, pip.get_rect(center=(cx, cy)))


def _draw_knight_at(surf, cx, cy, native):
    knight_skin.draw_shield_icon(surf, cx, cy, size=native)


def _draw_poison_at(surf, cx, cy, native):
    prev_display = poison_vial.DISPLAY_PX
    prev_cache = getattr(poison_vial, "_VIAL_CACHE", None)
    poison_vial.DISPLAY_PX = native
    poison_vial._VIAL_CACHE = None
    poison_vial.draw(surf, cx, cy, 0.0)
    poison_vial.DISPLAY_PX = prev_display
    poison_vial._VIAL_CACHE = prev_cache


def _draw_skateboard_at(surf, cx, cy, native):
    p = PowerUp(36, 36, kind="skateboard")
    p.pulse = 0.0
    full72 = pygame.Surface((72, 72), pygame.SRCALPHA)
    p._draw_skateboard_icon(full72)
    scaled = pygame.transform.smoothscale(full72, (native, native))
    surf.blit(scaled, scaled.get_rect(center=(cx, cy)).topleft)


DRAWERS = {
    "knight":     _draw_knight_at,
    "poison":     _draw_poison_at,
    "skateboard": _draw_skateboard_at,
}


def _build_cell(kind, native):
    """Pip on the left, pickup on the right, on a biome-coloured strip."""
    cell = _sky_strip(STRIP_W, STRIP_H)
    _draw_pip(cell, 32, STRIP_H // 2)
    DRAWERS[kind](cell, STRIP_W - 36, STRIP_H // 2, native)
    # Thin border so cards separate visually.
    pygame.draw.rect(cell, (40, 44, 56), cell.get_rect(), 1)
    return cell


def main():
    out_dir = os.path.join(os.path.dirname(THIS_DIR),
                           "docs", "screenshots", "icon_sizes")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "round_1.png")

    sheet_w = PAD * 2 + LABEL_COL + len(SIZES) * (STRIP_W + ROW_GAP) - ROW_GAP
    sheet_h = HEADER_H + 3 * (STRIP_H + ROW_GAP) - ROW_GAP + PAD * 2
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill(CARD_BG)

    title = _font(22, bold=True).render(
        "Secret-tier pickup icons — size variants (gameplay scale)",
        True, LABEL)
    sheet.blit(title, (PAD, PAD))
    sub = _font(13).render(
        "Pip + the pickup on a score-450 biome strip. Sizes 32 / 40 / 48 "
        "/ 56 / 72 native px. Pick one — applies to all three.",
        True, SUB)
    sheet.blit(sub, (PAD, PAD + 28))

    # Column headers
    for col, sz in enumerate(SIZES):
        x = PAD + LABEL_COL + col * (STRIP_W + ROW_GAP) + STRIP_W // 2
        h = _font(14, bold=True).render(f"{sz} px", True, LABEL)
        sheet.blit(h, (x - h.get_width() // 2, HEADER_H - 22))

    rows = (("knight", LABELS[0]),
            ("poison", LABELS[1]),
            ("skateboard", LABELS[2]))
    for i, (kind, label) in enumerate(rows):
        y = HEADER_H + i * (STRIP_H + ROW_GAP)
        lbl = _font(14, bold=True).render(label, True, LABEL)
        sheet.blit(lbl, (PAD, y + (STRIP_H - lbl.get_height()) // 2))
        for col, sz in enumerate(SIZES):
            x = PAD + LABEL_COL + col * (STRIP_W + ROW_GAP)
            cell = _build_cell(kind, sz)
            sheet.blit(cell, (x, y))

    pygame.image.save(sheet, out_path)
    print(f"saved {out_path}  ({sheet_w}x{sheet_h})")


if __name__ == "__main__":
    main()
