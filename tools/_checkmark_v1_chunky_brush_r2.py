"""chunky-brush r2: shifted left, thin-entry swell, right arm tapers to flick (no tip circle)."""
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
BG        = (8, 8, 20)
GOLD      = (236, 202, 116)
CREAM_LBL = (250, 246, 232)

SLUG = "chunky-brush"


def dots(surf, col, p0, p1, w0, w1, n=14):
    """Tapered stroke via interpolated circles."""
    for i in range(n + 1):
        t = i / n
        x = int(p0[0] + t * (p1[0] - p0[0]))
        y = int(p0[1] + t * (p1[1] - p0[1]))
        r = max(1, round(w0 + t * (w1 - w0)))
        pygame.draw.circle(surf, col, (x, y), r)


def _concept_check(face):
    """Shifted ~10px left to clear tag edge. Entry thin (w=10), swells to full w=16 at vertex.
    Right arm tapers to a thin flick — no circle cap (sells the lifted-brush end)."""
    ink    = (28, 20, 16)
    shadow = (20, 14, 10, 80)

    cx, cy = sc._TAG_W // 2, int(sc._TAG_H * 0.52)
    vertex = (cx - 2, cy + 8)
    # Shift arms left vs r1: l_arm x was cx-24=-24 from cx=40 → keep; r_arm was cx+28 → cx+18
    l_arm  = (cx - 24, cy - 8)
    r_arm  = (cx + 18, cy - 22)   # pulled left by ~10px to clear right tag edge

    w_fat   = 16   # keep boldness (it holds at 1×)
    w_entry = 10   # thin left-arm entry
    w_flick = 3    # thin right-arm tip flick

    # Shadow: slightly wider, offset +1/+1
    dots(face, shadow, (l_arm[0]+1, l_arm[1]+1),  (vertex[0]+1, vertex[1]+1), w_entry+1, w_fat+1)
    dots(face, shadow, (vertex[0]+1, vertex[1]+1), (r_arm[0]+1, r_arm[1]+1),  w_fat+1, w_flick+1)

    # Left arm: thin entry swelling to full fat at vertex
    dots(face, ink, l_arm,  vertex, w_entry, w_fat)
    # Right arm: full fat at vertex, tapering to thin flick tip
    dots(face, ink, vertex, r_arm,  w_fat, w_flick)

    # Pen-down entry cap on left arm (single circle, not double)
    pygame.draw.circle(face, ink, l_arm, w_entry // 2)


# ── Baseline panel ────────────────────────────────────────────────────────────
sc._card_cache.clear()
p0 = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
sc.draw_card(p0, SID, rect, equipped=True, secret=False, owned=True)

# ── Concept panel ────────────────────���────────────────────────────────────────
_orig = sc._tag_draw_check
sc._tag_draw_check = _concept_check
sc._card_cache.clear()
p1 = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
sc.draw_card(p1, SID, rect, equipped=True, secret=False, owned=True)
sc._tag_draw_check = _orig

# ── Tag-face zoom ─────────────────────────────────────────────────────────────
ZOOM = 2
fz = pygame.Surface((sc._TAG_W, sc._TAG_H), pygame.SRCALPHA)
body_z = sc.vgrad_stops(sc._TAG_W, sc._TAG_H, sc.m(3),
                        [(0.0, (248, 238, 210)), (1.0, (224, 204, 166))],
                        255, gamma=1.04)
fz.blit(body_z, (0, 0))
_concept_check(fz)
face_big = pygame.transform.scale(fz, (sc._TAG_W * ZOOM, sc._TAG_H * ZOOM))
ZW, ZH   = face_big.get_size()

# ── Sheet layout ──────────────────────────────────────────────────────────────
PAD, GAP      = 20, 16
HDR_H, LBL_H  = 48, 34
panel_y       = PAD + HDR_H + LBL_H
sheet_w       = PAD + PANEL_W + GAP + PANEL_W + GAP + ZW + PAD
sheet_h       = PAD + HDR_H + LBL_H + max(PANEL_H, ZH) + PAD

sheet = pygame.Surface((sheet_w, sheet_h))
sheet.fill(BG)

title_f = hud_font(22, True)
tt = title_f.render(f"checkmark · {SLUG} · r2", True, GOLD)
sheet.blit(tt, tt.get_rect(midtop=(sheet_w // 2, PAD // 2 + 4)))

lbl_f = hud_font(15, True)
for i, (label, col, panel) in enumerate([
    ("BASELINE", CREAM_LBL, p0),
    (SLUG.upper(), GOLD,     p1),
]):
    px = PAD + i * (PANEL_W + GAP)
    lt = lbl_f.render(label, True, col)
    sheet.blit(lt, lt.get_rect(midbottom=(px + PANEL_W // 2, panel_y - 6)))
    sheet.blit(panel, (px, panel_y))

zx = PAD + 2 * (PANEL_W + GAP)
zt = lbl_f.render("TAG FACE ×2", True, CREAM_LBL)
sheet.blit(zt, zt.get_rect(midbottom=(zx + ZW // 2, panel_y - 6)))
sheet.blit(face_big, (zx, panel_y))

OUT = f"docs/store_equipped_v3_2_checkmarks/{SLUG}/round_2.png"
os.makedirs(os.path.dirname(OUT), exist_ok=True)
pygame.image.save(sheet, OUT)
print(f"saved {sheet_w}×{sheet_h} → {OUT}")
