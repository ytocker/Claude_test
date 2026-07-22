"""Skin x power-up appearance reference grid.

Shows 6 representative skins across 8 power-up states so you can verify
that equipped cosmetics persist through KFC, ghost, and triple pickups.
Below the grid: custom parcel KFC amber-tint demo comparing the kraft
box (legacy mode palettes) against custom parcels (new tint system).

Run from the repo root or from tools/:
    python tools/render_interaction_figure.py

Output: docs/skin_powerup_interactions.png
"""
import math
import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pygame  # noqa: E402

pygame.init()
pygame.display.set_mode((1, 1))

from game.entities import Bird  # noqa: E402
from game import parrot  # noqa: E402

# ── Layout ─────────────────────────────────────────────────────────────────
LABEL_W = 118
CELL_W  = 96
CELL_H  = 136
HDR_H   = 48   # column-label header row height
MARGIN  = 10
BG      = (22, 26, 36)

SKIN_ROWS = [
    ("skin_base",   "Base Macaw"),
    ("skin_pirate", "Pirate"),
    ("skin_zombie", "Zombie"),
    ("skin_chrome", "Chrome Macaw"),
    ("skin_disco",  "Disco"),
    ("skin_cowboy", "Cowboy"),
]

# (column label, kfc, ghost, triple)
PU_COLS = [
    ("Normal",          False, False, False),
    ("KFC",             True,  False, False),
    ("Ghost",           False, True,  False),
    ("Triple $",        False, False, True),
    ("KFC\n+Ghost",     True,  True,  False),
    ("KFC\n+Triple",    True,  False, True),
    ("Ghost\n+Triple",  False, True,  True),
    ("All\nThree",      True,  True,  True),
]

N_ROWS = len(SKIN_ROWS)
N_COLS = len(PU_COLS)

GRID_W = LABEL_W + N_COLS * CELL_W
GRID_H = HDR_H + N_ROWS * CELL_H

# Parcel section
PARCEL_HDR_H  = 34
PARCEL_CELL_H = 80
PARCEL_SCALE  = 3   # scale parcels 3x for visibility

# (column label, parcel_id, use_kfc_tint)
PARCEL_COLS = [
    ("kraft/normal",   "parcel_base",    False),
    ("kraft/KFC",      "parcel_base",    True),
    ("airmail/normal", "parcel_airmail", False),
    ("airmail/KFC",    "parcel_airmail", True),
    ("soccer/normal",  "parcel_soccer",  False),
    ("soccer/KFC",     "parcel_soccer",  True),
]

N_PCOLS = len(PARCEL_COLS)
PARCEL_CELL_W = GRID_W // N_PCOLS

TITLE_H = 28
TOTAL_H = MARGIN + TITLE_H + GRID_H + PARCEL_HDR_H + PARCEL_CELL_H + MARGIN
TOTAL_W = GRID_W


# ── Helpers ────────────────────────────────────────────────────────────────

def fill_sky(surf):
    """Vertical sky gradient — deep azure at top, softer blue at bottom."""
    w, h = surf.get_size()
    for y in range(h):
        t = y / h
        surf.fill((
            int(80  + 20 * t),
            int(130 + 20 * t),
            int(210 - 10 * t),
        ), (0, y, w, 1))


def render_bird_cell(skin_id, kfc, ghost, triple):
    """Return a CELL_W x CELL_H sky tile with the bird centred."""
    cell = pygame.Surface((CELL_W, CELL_H))
    fill_sky(cell)
    b = Bird()
    b.frame_t      = 1.0   # frame 1: mid-flap
    b.x            = CELL_W / 2
    b.y            = 58.0  # leaves headroom for stovepipe hat at top
    b.equipped_skin = skin_id
    b.rebuild_skin_combos()
    b.kfc_active    = kfc
    b.ghost_active  = ghost
    b.triple_active = triple
    b.draw(cell, 0, 0)
    return cell


def render_parcel_cell(parcel_id, use_kfc_tint, cell_w, cell_h):
    """Return a sky tile with the parcel sprite scaled up for visibility."""
    cell = pygame.Surface((cell_w, cell_h))
    fill_sky(cell)
    if use_kfc_tint and parcel_id == "parcel_base":
        # base parcel: legacy per-mode KFC palette
        p = parrot.get_parcel("kfc", parcel_id)
    else:
        p = parrot.get_parcel("normal", parcel_id)
        if use_kfc_tint:
            # custom parcel: palette-derived crispy treatment (same as entities.py)
            p = parrot.get_crispy_parcel(parcel_id, p)
    pw, ph = p.get_size()
    big = pygame.transform.scale(p, (pw * PARCEL_SCALE, ph * PARCEL_SCALE))
    cell.blit(big, big.get_rect(center=(cell_w // 2, cell_h // 2 - 4)))
    return cell


# ── Canvas ─────────────────────────────────────────────────────────────────

canvas = pygame.Surface((TOTAL_W, TOTAL_H))
canvas.fill(BG)

font_title = pygame.font.SysFont("monospace", 13, bold=True)
font_hdr   = pygame.font.SysFont("monospace", 11, bold=True)
font_row   = pygame.font.SysFont("monospace", 11, bold=True)
font_sm    = pygame.font.SysFont("monospace", 10)

# ── Title ──────────────────────────────────────────────────────────────────

title_y = MARGIN
title_txt = font_title.render(
    "Skin x Power-Up Interactions — equipped skin persists through KFC / Ghost / Triple",
    True, (240, 235, 180),
)
canvas.blit(title_txt, (MARGIN, title_y + 6))

# ── Column headers ─────────────────────────────────────────────────────────

hdr_top = MARGIN + TITLE_H
for ci, (label, *_) in enumerate(PU_COLS):
    cx = LABEL_W + ci * CELL_W + CELL_W // 2
    lines = label.split("\n")
    y0 = hdr_top + (HDR_H - len(lines) * 14) // 2
    for line in lines:
        t = font_hdr.render(line, True, (220, 220, 160))
        canvas.blit(t, t.get_rect(centerx=cx, y=y0))
        y0 += 14

# ── Main grid ──────────────────────────────────────────────────────────────

grid_top = hdr_top + HDR_H
for ri, (skin_id, row_label) in enumerate(SKIN_ROWS):
    row_y = grid_top + ri * CELL_H
    # row label (right-aligned inside label column)
    lbl = font_row.render(row_label, True, (200, 200, 200))
    canvas.blit(lbl, lbl.get_rect(midright=(LABEL_W - 6, row_y + CELL_H // 2)))
    for ci, (_, kfc, ghost, triple) in enumerate(PU_COLS):
        cell_x = LABEL_W + ci * CELL_W
        cell = render_bird_cell(skin_id, kfc, ghost, triple)
        canvas.blit(cell, (cell_x, row_y))
        pygame.draw.rect(canvas, (50, 55, 72), (cell_x, row_y, CELL_W, CELL_H), 1)

# grid outline
pygame.draw.rect(
    canvas, (90, 100, 130),
    (LABEL_W, grid_top, N_COLS * CELL_W, N_ROWS * CELL_H), 2,
)
# header underline
pygame.draw.line(
    canvas, (90, 100, 130),
    (LABEL_W, hdr_top + HDR_H - 1),
    (LABEL_W + N_COLS * CELL_W, hdr_top + HDR_H - 1), 1,
)

# ── Parcel section ─────────────────────────────────────────────────────────

parcel_section_top = grid_top + N_ROWS * CELL_H
parcel_hdr_y = parcel_section_top + PARCEL_HDR_H // 2
hdr_surf = font_hdr.render(
    "Parcels — KFC amber tint on custom parcels (kraft box uses built-in KFC palette)",
    True, (200, 200, 200),
)
canvas.blit(hdr_surf, hdr_surf.get_rect(midleft=(MARGIN, parcel_hdr_y)))

parcel_row_top = parcel_section_top + PARCEL_HDR_H
for ci, (label, parcel_id, kfc_tint) in enumerate(PARCEL_COLS):
    px = ci * PARCEL_CELL_W
    cell = render_parcel_cell(parcel_id, kfc_tint, PARCEL_CELL_W, PARCEL_CELL_H)
    canvas.blit(cell, (px, parcel_row_top))
    # label below parcel
    lbl = font_sm.render(label, True, (190, 190, 190))
    canvas.blit(lbl, lbl.get_rect(centerx=px + PARCEL_CELL_W // 2,
                                  y=parcel_row_top + PARCEL_CELL_H - 14))
    pygame.draw.rect(canvas, (50, 55, 72),
                     (px, parcel_row_top, PARCEL_CELL_W, PARCEL_CELL_H), 1)

# parcel section outline
pygame.draw.rect(
    canvas, (90, 100, 130),
    (0, parcel_row_top, N_PCOLS * PARCEL_CELL_W, PARCEL_CELL_H), 2,
)

# ── Save ───────────────────────────────────────────────────────────────────

repo = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
out  = os.path.join(repo, "docs", "skin_powerup_interactions_v5.png")
pygame.image.save(canvas, out)
print(f"saved {TOTAL_W}x{TOTAL_H} -> {out}")
