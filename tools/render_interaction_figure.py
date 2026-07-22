"""Skin x power-up appearance reference grid.

Shows representative skins across power-up states — KFC/Ghost/Triple combos
in the top grid, additional effect power-ups (Poison, Grow, Shrink, Flip,
Skateboard, Knight) in the bottom grid.

Run from the repo root or from tools/:
    python tools/render_interaction_figure.py

Output: docs/skin_powerup_interactions_vN.png (auto-incremented)
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

# ── Layout constants ────────────────────────────────────────────────────────
LABEL_W = 118
CELL_W  = 96
CELL_H  = 136
HDR_H   = 48
MARGIN  = 10
BG      = (22, 26, 36)

# ── Grid 1: KFC / Ghost / Triple combos ────────────────────────────────────

SKIN_ROWS = [
    ("skin_binky",  "Binky"),
    ("skin_chrome", "Chrome Macaw"),
]

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

# ── Parcel section ──────────────────────────────────────────────────────────
PARCEL_HDR_H  = 34
PARCEL_CELL_H = 80
PARCEL_SCALE  = 3

PARCEL_COLS = [
    ("love/normal",       "parcel_love",      False, False),
    ("love/KFC",          "parcel_love",      True,  False),
    ("love/ghost",        "parcel_love",      False, True),
    ("love/KFC+ghost",    "parcel_love",      True,  True),
    ("chest/normal",      "parcel_chest",     False, False),
    ("chest/KFC",         "parcel_chest",     True,  False),
    ("chest/ghost",       "parcel_chest",     False, True),
    ("chest/KFC+ghost",   "parcel_chest",     True,  True),
    ("globe/normal",      "parcel_snowglobe", False, False),
    ("globe/KFC",         "parcel_snowglobe", True,  False),
    ("globe/ghost",       "parcel_snowglobe", False, True),
    ("globe/KFC+ghost",   "parcel_snowglobe", True,  True),
]

N_PCOLS = len(PARCEL_COLS)
PARCEL_CELL_W = GRID_W // N_PCOLS

# ── Grid 2: Additional effects (Poison / Grow / Shrink / Flip / Skateboard / Knight)
EFF_SKIN_ROWS = [
    ("skin_base",     "Base Macaw"),
    ("skin_bluegold", "Blue Macaw"),
    ("skin_mummy",    "Mummy"),
    ("skin_chrome",   "Chrome Macaw"),
]

# (column label, effect key)
EFF_COLS = [
    ("Normal",          "normal"),
    ("Poison",          "poison"),
    ("Grow",            "grow"),
    ("Shrink",          "shrink"),
    ("Flip /\nReverse", "flip"),
    ("Skate-\nboard",   "skateboard"),
    ("Skate+\nTriple",  "skate_triple"),
    ("Knight",          "knight"),
]

EFF_N_ROWS = len(EFF_SKIN_ROWS)
EFF_N_COLS = len(EFF_COLS)
EFF_TITLE_H = 28
EFF_GRID_H  = HDR_H + EFF_N_ROWS * CELL_H

# ── Total canvas size ────────────────────────────────────────────────────────
TITLE_H = 28
TOTAL_W = GRID_W
TOTAL_H = (
    MARGIN
    + TITLE_H + GRID_H
    + PARCEL_HDR_H + PARCEL_CELL_H
    + EFF_TITLE_H + EFF_GRID_H
    + MARGIN
)


# ── Helpers ─────────────────────────────────────────────────────────────────

def fill_sky(surf):
    w, h = surf.get_size()
    for y in range(h):
        t = y / h
        surf.fill((
            int(80  + 20 * t),
            int(130 + 20 * t),
            int(210 - 10 * t),
        ), (0, y, w, 1))


def render_bird_cell(skin_id, kfc, ghost, triple):
    """KFC/Ghost/Triple combo cell."""
    cell = pygame.Surface((CELL_W, CELL_H))
    fill_sky(cell)
    b = Bird()
    b.frame_t       = 1.0
    b.x             = CELL_W / 2
    b.y             = 58.0
    b.equipped_skin = skin_id
    b.rebuild_skin_combos()
    if ghost:
        b.ghost_pulse = math.pi / 2
    b.kfc_active    = kfc
    b.ghost_active  = ghost
    b.triple_active = triple
    b.draw(cell, 0, 0)
    return cell


def render_eff_cell(skin_id, effect):
    """Additional-effects cell: poison, grow, shrink, flip, skateboard, etc."""
    cell = pygame.Surface((CELL_W, CELL_H))
    fill_sky(cell)
    b = Bird()
    b.frame_t       = 1.0
    b.x             = CELL_W / 2
    b.y             = 58.0
    b.equipped_skin = skin_id
    b.rebuild_skin_combos()

    draw_flipped = False

    if effect == "poison":
        b.poison_active = True
        b.poison_t = 1.0          # full-strength chartreuse tint
    elif effect == "grow":
        b.grow_active = True
        b.y = 68.0                # push down slightly for the larger sprite
    elif effect == "shrink":
        b.shrink_scale = 0.6
    elif effect == "flip":
        draw_flipped = True
    elif effect == "skateboard":
        b.skateboard_active = True
        b.y = 52.0                # raise slightly — board hangs below
    elif effect == "skate_triple":
        b.skateboard_active = True
        b.triple_active = True
        b.y = 52.0
    elif effect == "knight":
        b.knight_active = True

    b.draw(cell, 0, 0, flipped=draw_flipped)
    return cell


def render_parcel_cell(parcel_id, use_kfc, use_ghost, cell_w, cell_h):
    cell = pygame.Surface((cell_w, cell_h))
    fill_sky(cell)
    p = parrot.get_parcel("normal", parcel_id)
    if use_kfc:
        p = parrot.get_crispy_parcel(parcel_id, p)
    if use_ghost:
        p = parrot.get_ghost_parcel(parcel_id)
        p = p.copy()
        p.set_alpha(170)
    pw, ph = p.get_size()
    big = pygame.transform.scale(p, (pw * PARCEL_SCALE, ph * PARCEL_SCALE))
    cell.blit(big, big.get_rect(center=(cell_w // 2, cell_h // 2 - 4)))
    return cell


# ── Canvas ──────────────────────────────────────────────────────────────────

canvas = pygame.Surface((TOTAL_W, TOTAL_H))
canvas.fill(BG)

font_title = pygame.font.SysFont("monospace", 13, bold=True)
font_hdr   = pygame.font.SysFont("monospace", 11, bold=True)
font_row   = pygame.font.SysFont("monospace", 11, bold=True)
font_sm    = pygame.font.SysFont("monospace", 10)

# ── Title ────────────────────────────────────────────────────────────────────

title_y = MARGIN
title_txt = font_title.render(
    "Skin x Power-Up Interactions — equipped skin persists through KFC / Ghost / Triple",
    True, (240, 235, 180),
)
canvas.blit(title_txt, (MARGIN, title_y + 6))

# ── Grid 1: column headers ───────────────────────────────────────────────────

hdr_top = MARGIN + TITLE_H
for ci, (label, *_) in enumerate(PU_COLS):
    cx = LABEL_W + ci * CELL_W + CELL_W // 2
    lines = label.split("\n")
    y0 = hdr_top + (HDR_H - len(lines) * 14) // 2
    for line in lines:
        t = font_hdr.render(line, True, (220, 220, 160))
        canvas.blit(t, t.get_rect(centerx=cx, y=y0))
        y0 += 14

# ── Grid 1: skin rows ────────────────────────────────────────────────────────

grid_top = hdr_top + HDR_H
for ri, (skin_id, row_label) in enumerate(SKIN_ROWS):
    row_y = grid_top + ri * CELL_H
    lbl = font_row.render(row_label, True, (200, 200, 200))
    canvas.blit(lbl, lbl.get_rect(midright=(LABEL_W - 6, row_y + CELL_H // 2)))
    for ci, (_, kfc, ghost, triple) in enumerate(PU_COLS):
        cell_x = LABEL_W + ci * CELL_W
        cell = render_bird_cell(skin_id, kfc, ghost, triple)
        canvas.blit(cell, (cell_x, row_y))
        pygame.draw.rect(canvas, (50, 55, 72), (cell_x, row_y, CELL_W, CELL_H), 1)

pygame.draw.rect(
    canvas, (90, 100, 130),
    (LABEL_W, grid_top, N_COLS * CELL_W, N_ROWS * CELL_H), 2,
)
pygame.draw.line(
    canvas, (90, 100, 130),
    (LABEL_W, hdr_top + HDR_H - 1),
    (LABEL_W + N_COLS * CELL_W, hdr_top + HDR_H - 1), 1,
)

# ── Parcel section ───────────────────────────────────────────────────────────

parcel_section_top = grid_top + N_ROWS * CELL_H
parcel_hdr_y = parcel_section_top + PARCEL_HDR_H // 2
hdr_surf = font_hdr.render(
    "Parcels — normal / KFC amber / ghost blue / KFC+ghost",
    True, (200, 200, 200),
)
canvas.blit(hdr_surf, hdr_surf.get_rect(midleft=(MARGIN, parcel_hdr_y)))

parcel_row_top = parcel_section_top + PARCEL_HDR_H
for ci, (label, parcel_id, kfc_tint, ghost_tint) in enumerate(PARCEL_COLS):
    px = ci * PARCEL_CELL_W
    cell = render_parcel_cell(parcel_id, kfc_tint, ghost_tint, PARCEL_CELL_W, PARCEL_CELL_H)
    canvas.blit(cell, (px, parcel_row_top))
    lbl = font_sm.render(label, True, (190, 190, 190))
    canvas.blit(lbl, lbl.get_rect(centerx=px + PARCEL_CELL_W // 2,
                                  y=parcel_row_top + PARCEL_CELL_H - 14))
    pygame.draw.rect(canvas, (50, 55, 72),
                     (px, parcel_row_top, PARCEL_CELL_W, PARCEL_CELL_H), 1)

pygame.draw.rect(
    canvas, (90, 100, 130),
    (0, parcel_row_top, N_PCOLS * PARCEL_CELL_W, PARCEL_CELL_H), 2,
)

# ── Grid 2: Additional effects ───────────────────────────────────────────────

eff_section_top = parcel_row_top + PARCEL_CELL_H
eff_title_y = eff_section_top + EFF_TITLE_H // 2
eff_title_txt = font_title.render(
    "Additional power-up effects on parrot appearance",
    True, (240, 235, 180),
)
canvas.blit(eff_title_txt, eff_title_txt.get_rect(midleft=(MARGIN, eff_title_y)))

eff_hdr_top = eff_section_top + EFF_TITLE_H
for ci, (label, _) in enumerate(EFF_COLS):
    cx = LABEL_W + ci * CELL_W + CELL_W // 2
    lines = label.split("\n")
    y0 = eff_hdr_top + (HDR_H - len(lines) * 14) // 2
    for line in lines:
        t = font_hdr.render(line, True, (220, 220, 160))
        canvas.blit(t, t.get_rect(centerx=cx, y=y0))
        y0 += 14

eff_grid_top = eff_hdr_top + HDR_H
for ri, (skin_id, row_label) in enumerate(EFF_SKIN_ROWS):
    row_y = eff_grid_top + ri * CELL_H
    lbl = font_row.render(row_label, True, (200, 200, 200))
    canvas.blit(lbl, lbl.get_rect(midright=(LABEL_W - 6, row_y + CELL_H // 2)))
    for ci, (_, effect) in enumerate(EFF_COLS):
        cell_x = LABEL_W + ci * CELL_W
        cell = render_eff_cell(skin_id, effect)
        canvas.blit(cell, (cell_x, row_y))
        pygame.draw.rect(canvas, (50, 55, 72), (cell_x, row_y, CELL_W, CELL_H), 1)

pygame.draw.rect(
    canvas, (90, 100, 130),
    (LABEL_W, eff_grid_top, EFF_N_COLS * CELL_W, EFF_N_ROWS * CELL_H), 2,
)
pygame.draw.line(
    canvas, (90, 100, 130),
    (LABEL_W, eff_hdr_top + HDR_H - 1),
    (LABEL_W + EFF_N_COLS * CELL_W, eff_hdr_top + HDR_H - 1), 1,
)

# ── Save ─────────────────────────────────────────────────────────────────────

BRANCH = "claude/v5-item-interactions-f8eeqx"

repo  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
docs  = os.path.join(repo, "docs")

import re as _re
_existing = [
    int(m.group(1))
    for f in os.listdir(docs)
    for m in [_re.search(r"skin_powerup_interactions_v(\d+)\.png", f)]
    if m
]
_next = (max(_existing) + 1) if _existing else 1
FILENAME   = f"skin_powerup_interactions_v{_next}.png"
GITHUB_URL = f"https://github.com/ytocker/skybit/blob/{BRANCH}/docs/{FILENAME}"

out = os.path.join(docs, FILENAME)
pygame.image.save(canvas, out)
print(f"saved {TOTAL_W}x{TOTAL_H} -> {out}")
print(f"\033]8;;{GITHUB_URL}\033\\{GITHUB_URL}\033]8;;\033\\")
