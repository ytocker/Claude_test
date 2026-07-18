"""calligraphic: broad-nib contrast — fat left downstroke, razor-thin right upstroke."""
import os, sys, math
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pygame
pygame.init()
pygame.display.set_mode((1, 1), pygame.NOFRAME)

import game.store_cards as sc
import game.store_data as sd
from game.hud import _font as hud_font
# vgrad_stops is in store_cards

sd.load()

SID = "skin_mummy"
PANEL_W, PANEL_H = sc.CARD_W * sc.SS, sc.CARD_H * sc.SS
ri   = sc.m(sc._INSET)
rect = pygame.Rect(ri, ri, PANEL_W - 2 * ri, PANEL_H - 2 * ri)
BG        = (8, 8, 20)
GOLD      = (236, 202, 116)
CREAM_LBL = (250, 246, 232)

SLUG = "calligraphic"


def _concept_check(face):
    """Left arm: fat tapered polygon (broad pen descending). Right arm: 2px hairline (thin upstroke)."""
    ink = (28, 20, 16)
    cx, cy = sc._TAG_W // 2, int(sc._TAG_H * 0.52)
    vertex = (cx - 2, cy + 8)
    l_arm  = (cx - 22, cy - 6)
    r_arm  = (cx + 26, cy - 20)

    # ── Left arm: broad-nib fat taper ─────────────────────────────────────────
    dx, dy = vertex[0] - l_arm[0], vertex[1] - l_arm[1]
    length = math.sqrt(dx * dx + dy * dy)
    px, py = -dy / length, dx / length   # perpendicular unit

    w_start, w_end = 13, 4   # fat at entry, tapers into vertex
    la_pts = [
        (l_arm[0]  + px * w_start, l_arm[1]  + py * w_start),
        (vertex[0] + px * w_end,   vertex[1] + py * w_end),
        (vertex[0] - px * w_end,   vertex[1] - py * w_end),
        (l_arm[0]  - px * w_start, l_arm[1]  - py * w_start),
    ]
    # shadow
    pygame.draw.polygon(face, (20, 14, 10, 70),
                        [(int(p[0] + 1), int(p[1] + 1)) for p in la_pts])
    pygame.draw.circle(face, (20, 14, 10, 70), (l_arm[0] + 1, l_arm[1] + 1), w_start)
    # main fat arm
    pygame.draw.polygon(face, ink,
                        [(int(p[0]), int(p[1])) for p in la_pts])
    pygame.draw.circle(face, ink, l_arm, w_start)   # round entry cap

    # ── Right arm: hairline ────────────────────────────────────────────────────
    pygame.draw.line(face, (20, 14, 10, 70),
                     (vertex[0] + 1, vertex[1] + 1), (r_arm[0] + 1, r_arm[1] + 1), 2)
    pygame.draw.line(face, ink, vertex, r_arm, 2)


# ── Baseline panel ────────────────────────────────────────────────────────────
sc._card_cache.clear()
p0 = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
sc.draw_card(p0, SID, rect, equipped=True, secret=False, owned=True)

# ── Concept panel ─────────────────────────────────────────────────────────────
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
tt = title_f.render(f"checkmark · {SLUG} · r1", True, GOLD)
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

OUT = f"docs/store_equipped_v3_2_checkmarks/{SLUG}/round_1.png"
os.makedirs(os.path.dirname(OUT), exist_ok=True)
pygame.image.save(sheet, OUT)
print(f"saved {sheet_w}×{sheet_h} → {OUT}")
