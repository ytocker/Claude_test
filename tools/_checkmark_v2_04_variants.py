"""Variant 04 (angular-drop) — larger, lower, more left. 4 columns × 3 rows."""
import os, sys
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pygame
pygame.init()
pygame.display.set_mode((1, 1), pygame.NOFRAME)

import game.store_cards as sc
import game.store_data as sd
from game.hud import _font as hud_font

sd.load()

SID = "skin_mummy"
PANEL_W, PANEL_H = sc.CARD_W * sc.SS, sc.CARD_H * sc.SS
ri   = sc.m(sc._INSET)
rect = pygame.Rect(ri, ri, PANEL_W - 2 * ri, PANEL_H - 2 * ri)
BG    = (8, 8, 20)
GOLD  = (236, 202, 116)
CREAM = (250, 246, 232)
DIM   = (180, 170, 140)

INK    = (28, 20, 16)
SHADOW = (20, 14, 10, 80)


def dots(surf, col, p0, p1, w0, w1, n=14):
    for i in range(n + 1):
        t = i / n
        x = int(p0[0] + t * (p1[0] - p0[0]))
        y = int(p0[1] + t * (p1[1] - p0[1]))
        r = max(1, round(w0 + t * (w1 - w0)))
        pygame.draw.circle(surf, col, (x, y), r)


def _draw_04_variant(face, left_shift, down_shift, w, arm_scale=1.0):
    """angular-drop with parameterised position offset and scale.

    Base 04 geometry:
      vertex=(cx-2, cy+8), l_arm=(cx-8, cy-10), r_arm=(cx+26, cy-20)
    Arm deltas from vertex:  l=(-6,-18),  r=(+28,-28).
    """
    cx, cy = sc._TAG_W // 2, int(sc._TAG_H * 0.52)
    vx = cx - 2 - left_shift
    vy = cy + 8 + down_shift
    vertex = (vx, vy)
    l_arm  = (vx + int(-6  * arm_scale), vy + int(-18 * arm_scale))
    r_arm  = (vx + int( 28 * arm_scale), vy + int(-28 * arm_scale))

    pygame.draw.line(face, SHADOW, (l_arm[0]+1, l_arm[1]+1), (vertex[0]+1, vertex[1]+1), w + 2)
    pygame.draw.circle(face, SHADOW, (l_arm[0]+1, l_arm[1]+1), (w + 2) // 2)
    pygame.draw.line(face, SHADOW, (vertex[0]+1, vertex[1]+1), (r_arm[0]+1, r_arm[1]+1), w + 1)
    pygame.draw.circle(face, SHADOW, (r_arm[0]+1, r_arm[1]+1), (w + 1) // 2)

    pygame.draw.line(face, INK, l_arm, vertex, w)
    pygame.draw.circle(face, INK, l_arm, w // 2)
    pygame.draw.circle(face, INK, vertex, w // 2 + 1)
    pygame.draw.line(face, INK, vertex, r_arm, w)
    pygame.draw.circle(face, INK, r_arm, w // 2)


# ── Columns: position / scale variants ───────────────────────────────────────
# (left_shift, down_shift, own_weight, arm_scale, col_id)
COLS = [
    (4,  4,  8,  1.05, "A"),
    (6,  6,  10, 1.15, "B"),
    (8,  9,  11, 1.25, "C"),
    (10, 12, 13, 1.35, "D"),
]

# ── Rows: weight override (None = each column's own weight) ──────────────────
ROWS = [
    ("original weights", None),
    ("weight = 8",       8),
    ("weight = 9",       9),
]

# ── Render all panels ────────────────────────────────────────────────────────
_orig = sc._tag_draw_check
all_panels = []   # list of rows; each row is a list of (panel, actual_w)
for row_label, row_w in ROWS:
    row = []
    for ls, ds, own_w, sc_arm, col_id in COLS:
        w = row_w if row_w is not None else own_w
        def _fn(face, _ls=ls, _ds=ds, _w=w, _sc=sc_arm):
            _draw_04_variant(face, _ls, _ds, _w, _sc)
        sc._tag_draw_check = _fn
        sc._card_cache.clear()
        surf = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
        sc.draw_card(surf, SID, rect, equipped=True, secret=False, owned=True)
        row.append((surf.copy(), w))
    all_panels.append(row)
sc._tag_draw_check = _orig
sc._card_cache.clear()

# ── Canvas layout ─────────────────────────────────────────────────────────────
NC     = len(COLS)
NR     = len(ROWS)
PAD    = 20
GAP    = 8
HDR_H  = 48    # title
COL_H  = 30    # column ID strip (shown once at top)
ROW_H  = 26    # row label bar above each row
FTR_H  = 44    # two property lines below each row
ROW_GAP = 14   # vertical gap between rows

width  = PAD + NC * PANEL_W + (NC - 1) * GAP + PAD
height = (PAD + HDR_H + COL_H
          + NR * (ROW_H + PANEL_H + FTR_H)
          + (NR - 1) * ROW_GAP
          + PAD)

canvas = pygame.Surface((width, height))
canvas.fill(BG)

title_f  = hud_font(22, True)
rowlbl_f = hud_font(15, True)
id_f     = hud_font(16, True)
prop_f   = hud_font(13, True)

# Title
tt = title_f.render("04 · angular-drop · larger / lower / more left", True, GOLD)
canvas.blit(tt, tt.get_rect(midtop=(width // 2, PAD // 2 + 4)))

# Column IDs (A–D), drawn once
col_label_y = PAD + HDR_H
for j, (ls, ds, own_w, sc_arm, col_id) in enumerate(COLS):
    px  = PAD + j * (PANEL_W + GAP)
    mid = px + PANEL_W // 2
    lt = id_f.render(col_id, True, GOLD)
    canvas.blit(lt, lt.get_rect(midtop=(mid, col_label_y + 4)))

# Rows
cursor_y = PAD + HDR_H + COL_H
for ri_row, ((row_label, row_w), row) in enumerate(zip(ROWS, all_panels)):
    if ri_row > 0:
        cursor_y += ROW_GAP

    # Row label bar
    rl = rowlbl_f.render(row_label, True, CREAM)
    canvas.blit(rl, rl.get_rect(midleft=(PAD, cursor_y + ROW_H // 2)))
    cursor_y += ROW_H

    # Panels + footers
    for j, ((ls, ds, own_w, sc_arm, col_id), (panel, actual_w)) in enumerate(zip(COLS, row)):
        px  = PAD + j * (PANEL_W + GAP)
        mid = px + PANEL_W // 2
        canvas.blit(panel, (px, cursor_y))

        fy = cursor_y + PANEL_H + 6
        for line in (
            f"left {ls}px · down {ds}px",
            f"weight {actual_w} · arms ×{sc_arm:.2f}",
        ):
            lt = prop_f.render(line, True, DIM)
            canvas.blit(lt, lt.get_rect(midtop=(mid, fy)))
            fy += 18

    cursor_y += PANEL_H + FTR_H

OUT = "docs/store_equipped_v3_2_checkmarks/04_variants.png"
os.makedirs(os.path.dirname(OUT), exist_ok=True)
pygame.image.save(canvas, OUT)
print(f"saved {width}×{height} → {OUT}")
