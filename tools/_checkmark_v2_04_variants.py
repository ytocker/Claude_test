"""Variant 04 (angular-drop) — larger, lower, more left. 4 stepped options."""
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

    Base 04 geometry in original coords:
      vertex=(cx-2, cy+8), l_arm=(cx-8, cy-10), r_arm=(cx+26, cy-20)
    Arm deltas FROM vertex:   l=(-6,-18),  r=(+28,-28).
    """
    cx, cy = sc._TAG_W // 2, int(sc._TAG_H * 0.52)
    vx = cx - 2 - left_shift
    vy = cy + 8 + down_shift
    vertex = (vx, vy)
    # Scale arm vectors from vertex
    l_arm = (vx + int(-6  * arm_scale), vy + int(-18 * arm_scale))
    r_arm = (vx + int( 28 * arm_scale), vy + int(-28 * arm_scale))

    pygame.draw.line(face, SHADOW, (l_arm[0]+1, l_arm[1]+1), (vertex[0]+1, vertex[1]+1), w + 2)
    pygame.draw.circle(face, SHADOW, (l_arm[0]+1, l_arm[1]+1), (w + 2) // 2)
    pygame.draw.line(face, SHADOW, (vertex[0]+1, vertex[1]+1), (r_arm[0]+1, r_arm[1]+1), w + 1)
    pygame.draw.circle(face, SHADOW, (r_arm[0]+1, r_arm[1]+1), (w + 1) // 2)

    pygame.draw.line(face, INK, l_arm, vertex, w)
    pygame.draw.circle(face, INK, l_arm, w // 2)
    pygame.draw.circle(face, INK, vertex, w // 2 + 1)
    pygame.draw.line(face, INK, vertex, r_arm, w)
    pygame.draw.circle(face, INK, r_arm, w // 2)


# ── Four options ─────────────────────────────────────────────────────────────
# (left_shift, down_shift, weight, arm_scale, label, note)
OPTIONS = [
    (4,  4,  8,  1.05, "A", "w=8 · slight"),
    (6,  6,  10, 1.15, "B", "w=10 · medium"),
    (8,  9,  11, 1.25, "C", "w=11 · bold"),
    (10, 12, 13, 1.35, "D", "w=13 · chunky"),
]

_orig = sc._tag_draw_check
panels = []
for ls, ds, w, sc_arm, lbl, note in OPTIONS:
    def _fn(face, _ls=ls, _ds=ds, _w=w, _sc=sc_arm):
        _draw_04_variant(face, _ls, _ds, _w, _sc)
    sc._tag_draw_check = _fn
    sc._card_cache.clear()
    surf = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
    sc.draw_card(surf, SID, rect, equipped=True, secret=False, owned=True)
    panels.append(surf.copy())
sc._tag_draw_check = _orig
sc._card_cache.clear()

# ── Canvas ────────────────────────────────────────────────────────────────────
N      = len(panels)
PAD    = 20
GAP    = 8
HDR_H  = 48
LBL_H  = 32
FTR_H  = 28
width  = PAD + N * PANEL_W + (N - 1) * GAP + PAD
height = PAD + HDR_H + LBL_H + PANEL_H + FTR_H + PAD

canvas = pygame.Surface((width, height))
canvas.fill(BG)

title_f = hud_font(22, True)
tt = title_f.render("04 · angular-drop · larger / lower / more left", True, GOLD)
canvas.blit(tt, tt.get_rect(midtop=(width // 2, PAD // 2 + 4)))

id_f  = hud_font(18, True)
lbl_f = hud_font(13, True)
panel_y = PAD + HDR_H + LBL_H

for i, ((ls, ds, w, sc_arm, lbl, note), panel) in enumerate(zip(OPTIONS, panels)):
    px = PAD + i * (PANEL_W + GAP)
    id_t = id_f.render(lbl, True, GOLD)
    canvas.blit(id_t, id_t.get_rect(midbottom=(px + PANEL_W // 2, panel_y - 4)))
    canvas.blit(panel, (px, panel_y))
    nm_t = lbl_f.render(note, True, CREAM)
    canvas.blit(nm_t, nm_t.get_rect(midtop=(px + PANEL_W // 2, panel_y + PANEL_H + 4)))

OUT = "docs/store_equipped_v3_2_checkmarks/04_variants.png"
os.makedirs(os.path.dirname(OUT), exist_ok=True)
pygame.image.save(canvas, OUT)
print(f"saved {width}×{height} → {OUT}")
