"""Size-variant sheet for the secret-tier pickup icons (poison, knight,
skateboard). Renders each icon at five candidate native footprints so the
user can pick the matched size for the next polish round.

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
from game import knight_skin, poison_vial


SIZES = (32, 40, 48, 56, 72)
LABELS = ("KNIGHT (shield)", "POISON (vial)", "SKATEBOARD (skull-bunny)")

CARD_BG = (24, 26, 34)
ROW_BG  = (32, 34, 42)
LABEL   = (235, 235, 240)
SUB     = (160, 168, 180)

PAD       = 18
CELL_W    = 96
ROW_H     = 110
HEADER_H  = 78
TITLE_FONT_PX = 22
LABEL_FONT_PX = 14
SUB_FONT_PX   = 12


def _font(size, bold=False):
    return pygame.font.SysFont("Arial", size, bold=bold)


def _draw_skateboard_at(surf, cx, cy, native):
    """Re-run the live skateboard icon recipe at a configurable native
    footprint instead of the shipped 72×72."""
    import math
    p = PowerUp(cx, cy, kind="skateboard")

    # Monkey-port the live _draw_skateboard_icon body but with a parameter
    # for NATIVE_W/H. Cleaner than calling the real method (which hardcodes
    # 72 internally).
    bg = pygame.Surface((CELL_W, CELL_W), pygame.SRCALPHA)
    icon_surf = pygame.Surface((native, native), pygame.SRCALPHA)
    # The icon's own draw routine takes a PowerUp instance whose .x/.y
    # control placement on the supplied surface. The recipe runs at the
    # power-up's hardcoded 72 footprint, so we render at 72 then
    # smoothscale down. Faster than re-implementing and visually identical.
    p_big = PowerUp(36, 36, kind="skateboard")
    p_big.pulse = 0.0
    full72 = pygame.Surface((72, 72), pygame.SRCALPHA)
    p_big._draw_skateboard_icon(full72)
    scaled = pygame.transform.smoothscale(full72, (native, native))
    icon_rect = scaled.get_rect(center=(cx, cy))
    surf.blit(scaled, icon_rect.topleft)


def _draw_knight_at(surf, cx, cy, native):
    knight_skin.draw_shield_icon(surf, cx, cy, size=native)


def _draw_poison_at(surf, cx, cy, native):
    # Force a fresh build at the requested native size by toggling the
    # module constant + cache, then restore.
    prev_display = poison_vial.DISPLAY_PX
    prev_cache = getattr(poison_vial, "_VIAL_CACHE", None)
    poison_vial.DISPLAY_PX = native
    poison_vial._VIAL_CACHE = None
    poison_vial.draw(surf, cx, cy, 0.0)
    poison_vial.DISPLAY_PX = prev_display
    poison_vial._VIAL_CACHE = prev_cache


DRAWERS = {
    "knight":     _draw_knight_at,
    "poison":     _draw_poison_at,
    "skateboard": _draw_skateboard_at,
}


def main():
    out_dir = os.path.join(os.path.dirname(THIS_DIR),
                           "docs", "screenshots", "icon_sizes")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "round_1.png")

    sheet_w = PAD * 2 + 130 + len(SIZES) * CELL_W
    sheet_h = HEADER_H + len(LABELS) * ROW_H + PAD * 2 + 24
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill(CARD_BG)

    title = _font(TITLE_FONT_PX, bold=True).render(
        "Secret-tier pickup icons — size variants", True, LABEL)
    sheet.blit(title, (PAD, PAD))
    sub = _font(SUB_FONT_PX).render(
        "Each row shows the same icon at 32 / 40 / 48 / 56 / 72 native px. "
        "Pick a column number — that size applies to all three.",
        True, SUB)
    sheet.blit(sub, (PAD, PAD + 24))

    # Header row — size numbers above each column
    for col, sz in enumerate(SIZES):
        x = PAD + 130 + col * CELL_W
        h = _font(LABEL_FONT_PX, bold=True).render(f"{sz} px", True, LABEL)
        sheet.blit(h, (x + (CELL_W - h.get_width()) // 2, HEADER_H - 18))

    row_y = HEADER_H
    rows = (("knight", LABELS[0]),
            ("poison", LABELS[1]),
            ("skateboard", LABELS[2]))
    for i, (kind, label) in enumerate(rows):
        y = row_y + i * ROW_H
        # Row card
        pygame.draw.rect(sheet, ROW_BG,
                         (PAD, y, sheet_w - PAD * 2, ROW_H - 8),
                         border_radius=10)
        lbl = _font(LABEL_FONT_PX, bold=True).render(label, True, LABEL)
        sheet.blit(lbl, (PAD + 12, y + (ROW_H - 8 - lbl.get_height()) // 2))

        # Cells
        drawer = DRAWERS[kind]
        for col, sz in enumerate(SIZES):
            cx = PAD + 130 + col * CELL_W + CELL_W // 2
            cy = y + (ROW_H - 8) // 2
            drawer(sheet, cx, cy, sz)

    pygame.image.save(sheet, out_path)
    print(f"saved {out_path}  ({sheet_w}x{sheet_h})")


if __name__ == "__main__":
    main()
