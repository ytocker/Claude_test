"""Poison power-up diagnostic figure.

3 rows (skin_base, skin_wizard, skin_bluegold) × 2 columns (Normal, Poison-final).
Shows the actual in-game final-state rendering for each skin so the poison
appearance can be evaluated and fixed.

Run from repo root or tools/:
    python tools/render_poison_figure.py

Output: docs/poison_diagnostic_vN.png (auto-incremented)
"""
import os
import re
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pygame  # noqa: E402

pygame.init()
pygame.display.set_mode((1, 1))

from game.entities import Bird  # noqa: E402

# ── Layout constants (match render_interaction_figure.py) ────────────────────
LABEL_W = 130
CELL_W  = 96
CELL_H  = 120
HDR_H   = 44
MARGIN  = 10
BG      = (22, 26, 36)
TITLE_H = 28

SKIN_ROWS = [
    ("skin_base",    "Base Macaw"),
    ("skin_wizard",  "Wizard"),
    ("skin_bluegold", "Blue Macaw"),
]

EFF_COLS = [
    ("Normal",        "normal"),
    ("Poison (final)", "poison"),
]

N_ROWS  = len(SKIN_ROWS)
N_COLS  = len(EFF_COLS)
GRID_W  = LABEL_W + N_COLS * CELL_W
GRID_H  = HDR_H + N_ROWS * CELL_H
TOTAL_W = GRID_W
TOTAL_H = MARGIN + TITLE_H + GRID_H + MARGIN


def fill_sky(surf):
    w, h = surf.get_size()
    for y in range(h):
        t = y / h
        surf.fill((
            int(80  + 20 * t),
            int(130 + 20 * t),
            int(210 - 10 * t),
        ), (0, y, w, 1))


def render_cell(skin_id, effect):
    cell = pygame.Surface((CELL_W, CELL_H))
    fill_sky(cell)

    b = Bird()
    b.frame_t       = 1.0
    b.x             = CELL_W / 2
    b.y             = 48.0
    b.equipped_skin = skin_id
    b.rebuild_skin_combos()

    if effect == "poison":
        b.poison_active = True
        b.poison_t      = 1.0

    b.draw(cell, 0, 0)
    return cell


# ── Canvas ───────────────────────────────────────────────────────────────────

canvas = pygame.Surface((TOTAL_W, TOTAL_H))
canvas.fill(BG)

font_title = pygame.font.SysFont("monospace", 13, bold=True)
font_hdr   = pygame.font.SysFont("monospace", 11, bold=True)
font_row   = pygame.font.SysFont("monospace", 11, bold=True)

# ── Title ────────────────────────────────────────────────────────────────────

canvas.blit(
    font_title.render("Poison power-up — current in-game final state", True, (240, 235, 180)),
    (MARGIN, MARGIN + 6),
)

# ── Column headers ────────────────────────────────────────────────────────────

hdr_top = MARGIN + TITLE_H
for ci, (label, _) in enumerate(EFF_COLS):
    cx = LABEL_W + ci * CELL_W + CELL_W // 2
    t  = font_hdr.render(label, True, (220, 220, 160))
    canvas.blit(t, t.get_rect(centerx=cx, centery=hdr_top + HDR_H // 2))

pygame.draw.line(
    canvas, (90, 100, 130),
    (LABEL_W, hdr_top + HDR_H - 1),
    (LABEL_W + N_COLS * CELL_W, hdr_top + HDR_H - 1), 1,
)

# ── Grid rows ─────────────────────────────────────────────────────────────────

grid_top = hdr_top + HDR_H
for ri, (skin_id, row_label) in enumerate(SKIN_ROWS):
    row_y = grid_top + ri * CELL_H
    lbl   = font_row.render(row_label, True, (200, 200, 200))
    canvas.blit(lbl, lbl.get_rect(midright=(LABEL_W - 6, row_y + CELL_H // 2)))
    for ci, (_, effect) in enumerate(EFF_COLS):
        cell_x = LABEL_W + ci * CELL_W
        cell   = render_cell(skin_id, effect)
        canvas.blit(cell, (cell_x, row_y))
        pygame.draw.rect(canvas, (50, 55, 72), (cell_x, row_y, CELL_W, CELL_H), 1)

pygame.draw.rect(
    canvas, (90, 100, 130),
    (LABEL_W, grid_top, N_COLS * CELL_W, N_ROWS * CELL_H), 2,
)

# ── Save ──────────────────────────────────────────────────────────────────────

BRANCH = "claude/v5-item-interactions-f8eeqx"
repo   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
docs   = os.path.join(repo, "docs")

_existing = [
    int(m.group(1))
    for f in os.listdir(docs)
    for m in [re.search(r"poison_diagnostic_v(\d+)\.png", f)]
    if m
]
_next    = (max(_existing) + 1) if _existing else 1
FILENAME = f"poison_diagnostic_v{_next}.png"

out        = os.path.join(docs, FILENAME)
GITHUB_URL = f"https://github.com/ytocker/skybit/blob/{BRANCH}/docs/{FILENAME}"

pygame.image.save(canvas, out)
print(f"saved {TOTAL_W}x{TOTAL_H} -> {out}")
print(f"\033]8;;{GITHUB_URL}\033\\{GITHUB_URL}\033]8;;\033\\")
