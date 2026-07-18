"""V2 showcase: 5 short-left/long-right checkmark variants with IDs 01–05."""
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
BG   = (8, 8, 20)
GOLD = (236, 202, 116)
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


# ── 01 · nib-sharp ────────────────────────────────────────────────────────────
# Pronounced asymmetry: vertex shifted right, l_arm shortened, r_arm extended.
# Fat left (w=12) / hair-thin right (w=4). 3:1 contrast.
def _draw_01(face):
    cx, cy = sc._TAG_W // 2, int(sc._TAG_H * 0.52)
    vertex = (cx + 4,  cy + 8)
    l_arm  = (cx - 16, cy - 4)
    r_arm  = (cx + 30, cy - 22)
    w_fat, w_thin = 12, 4

    pygame.draw.line(face, SHADOW, (l_arm[0]+1, l_arm[1]+1), (vertex[0]+1, vertex[1]+1), w_fat + 2)
    pygame.draw.circle(face, SHADOW, (l_arm[0]+1, l_arm[1]+1), (w_fat + 2) // 2)
    pygame.draw.line(face, SHADOW, (vertex[0]+1, vertex[1]+1), (r_arm[0]+1, r_arm[1]+1), w_thin + 1)

    pygame.draw.line(face, INK, l_arm, vertex, w_fat)
    pygame.draw.circle(face, INK, l_arm, w_fat // 2)
    pygame.draw.circle(face, INK, vertex, (w_fat + w_thin) // 3)
    pygame.draw.line(face, INK, vertex, r_arm, w_thin)


# ── 02 · pressure-swell ───────────────────────────────────────────────────────
# dots() both arms. Left thin→fat (short), right fat→thin (long). Pooled vertex.
def _draw_02(face):
    cx, cy = sc._TAG_W // 2, int(sc._TAG_H * 0.52)
    vertex = (cx - 2, cy + 8)
    l_arm  = (cx - 22, cy - 6)
    r_arm  = (cx + 26, cy - 20)

    dots(face, SHADOW, (l_arm[0]+1, l_arm[1]+1), (vertex[0]+1, vertex[1]+1), 3, 13)
    dots(face, SHADOW, (vertex[0]+1, vertex[1]+1), (r_arm[0]+1, r_arm[1]+1), 13, 4)

    dots(face, INK, l_arm, vertex, 2, 12)
    pygame.draw.circle(face, INK, vertex, 7)
    dots(face, INK, vertex, r_arm, 12, 3)


# ── 03 · stamp-serif ──────────────────────────────────────────────────────────
# Left arm with a horizontal serif foot at entry. Left medium (w=8), right thin (w=5).
def _draw_03(face):
    cx, cy = sc._TAG_W // 2, int(sc._TAG_H * 0.52)
    vertex = (cx - 2, cy + 8)
    l_arm  = (cx - 22, cy - 6)
    r_arm  = (cx + 26, cy - 20)
    w_left, w_right = 8, 5
    serif_w = 10  # horizontal span of the serif foot

    pygame.draw.line(face, SHADOW, (l_arm[0]+1, l_arm[1]+1), (vertex[0]+1, vertex[1]+1), w_left + 2)
    pygame.draw.line(face, SHADOW, (vertex[0]+1, vertex[1]+1), (r_arm[0]+1, r_arm[1]+1), w_right + 1)

    pygame.draw.line(face, INK, l_arm, vertex, w_left)
    # Serif foot: small horizontal bar centred on l_arm top
    pygame.draw.line(face, INK,
                     (l_arm[0] - serif_w // 2, l_arm[1]),
                     (l_arm[0] + serif_w // 2, l_arm[1]), 3)
    pygame.draw.circle(face, INK, vertex, (w_left + w_right) // 3)
    pygame.draw.line(face, INK, vertex, r_arm, w_right)


# ── 04 · angular-drop ────────────────────────────────────────────────────────
# Left arm nearly vertical (steep, short). Right arm long gentle diagonal.
# Same weight (w=7) — angle contrast tells the story. Pen-down caps at both tips.
def _draw_04(face):
    cx, cy = sc._TAG_W // 2, int(sc._TAG_H * 0.52)
    vertex = (cx - 2, cy + 8)
    l_arm  = (cx - 8,  cy - 10)   # near-vertical, short drop
    r_arm  = (cx + 26, cy - 20)
    w = 7

    pygame.draw.line(face, SHADOW, (l_arm[0]+1, l_arm[1]+1), (vertex[0]+1, vertex[1]+1), w + 2)
    pygame.draw.circle(face, SHADOW, (l_arm[0]+1, l_arm[1]+1), (w + 2) // 2)
    pygame.draw.line(face, SHADOW, (vertex[0]+1, vertex[1]+1), (r_arm[0]+1, r_arm[1]+1), w + 1)
    pygame.draw.circle(face, SHADOW, (r_arm[0]+1, r_arm[1]+1), (w + 1) // 2)

    pygame.draw.line(face, INK, l_arm, vertex, w)
    pygame.draw.circle(face, INK, l_arm, w // 2)
    pygame.draw.circle(face, INK, vertex, w // 2 + 1)
    pygame.draw.line(face, INK, vertex, r_arm, w)
    pygame.draw.circle(face, INK, r_arm, w // 2)


# ── 05 · brush-taper ─────────────────────────────────────────────────────────
# Left arm: uniform thick (w=10), short, no end cap (lifted brush).
# Right arm: starts thick at vertex, tapers all the way to w=1 at tip — very long thin tail.
def _draw_05(face):
    cx, cy = sc._TAG_W // 2, int(sc._TAG_H * 0.52)
    vertex = (cx - 2, cy + 8)
    l_arm  = (cx - 22, cy - 6)
    r_arm  = (cx + 26, cy - 20)

    dots(face, SHADOW, (l_arm[0]+1, l_arm[1]+1), (vertex[0]+1, vertex[1]+1), 11, 11)
    dots(face, SHADOW, (vertex[0]+1, vertex[1]+1), (r_arm[0]+1, r_arm[1]+1), 11, 2)

    dots(face, INK, l_arm, vertex, 10, 10)
    pygame.draw.circle(face, INK, vertex, 6)
    dots(face, INK, vertex, r_arm, 10, 1)


# ── Render panels ─────────────────────────────────────────────────────────────
VARIANTS = [
    ("01", "nib-sharp",      _draw_01),
    ("02", "pressure-swell", _draw_02),
    ("03", "stamp-serif",    _draw_03),
    ("04", "angular-drop",   _draw_04),
    ("05", "brush-taper",    _draw_05),
]

_orig = sc._tag_draw_check
panels = []
for vid, vname, fn in VARIANTS:
    sc._tag_draw_check = fn
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
tt = title_f.render("checkmark v2 · short-left / long-right · 5 variants", True, GOLD)
canvas.blit(tt, tt.get_rect(midtop=(width // 2, PAD // 2 + 4)))

id_f   = hud_font(18, True)
lbl_f  = hud_font(13, True)
panel_y = PAD + HDR_H + LBL_H

for i, ((vid, vname, _), panel) in enumerate(zip(VARIANTS, panels)):
    px = PAD + i * (PANEL_W + GAP)
    id_t = id_f.render(vid, True, GOLD)
    canvas.blit(id_t, id_t.get_rect(midbottom=(px + PANEL_W // 2, panel_y - 4)))
    canvas.blit(panel, (px, panel_y))
    nm_t = lbl_f.render(vname, True, CREAM)
    canvas.blit(nm_t, nm_t.get_rect(midtop=(px + PANEL_W // 2, panel_y + PANEL_H + 4)))

OUT = "docs/store_equipped_v3_2_checkmarks/v2_showcase.png"
os.makedirs(os.path.dirname(OUT), exist_ok=True)
pygame.image.save(canvas, OUT)
print(f"saved {width}×{height} → {OUT}")
