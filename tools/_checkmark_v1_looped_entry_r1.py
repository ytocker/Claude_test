"""looped-entry: left arm has a small hook/loop at entry before descending — cursive gesture."""
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
# vgrad_stops is in store_cards

sd.load()

SID = "skin_mummy"
PANEL_W, PANEL_H = sc.CARD_W * sc.SS, sc.CARD_H * sc.SS
ri   = sc.m(sc._INSET)
rect = pygame.Rect(ri, ri, PANEL_W - 2 * ri, PANEL_H - 2 * ri)
BG        = (8, 8, 20)
GOLD      = (236, 202, 116)
CREAM_LBL = (250, 246, 232)

SLUG = "looped-entry"


def _concept_check(face):
    """Left arm: l_arm → hook_tip → hook_back → vertex (cursive loop entry).
    Right arm: vertex → r_arm (clean straight line). Black ink only."""
    ink = (28, 20, 16)
    cx, cy = sc._TAG_W // 2, int(sc._TAG_H * 0.52)
    vertex    = (cx - 2,  cy + 8)
    l_arm     = (cx - 22, cy - 6)
    r_arm     = (cx + 26, cy - 20)
    # Hook: loop apex above/right of l_arm entry, then curves back to l_arm level
    hook_tip  = (cx - 10, cy - 20)   # apex of the entry loop
    hook_back = (cx - 20, cy - 10)   # back down from apex, heading toward vertex
    w = 9

    left_path = [l_arm, hook_tip, hook_back, vertex]

    # Shadow pass: full left path + right arm, offset (+1,+1)
    s_path = [(p[0] + 1, p[1] + 1) for p in left_path]
    pygame.draw.lines(face, (20, 14, 10, 80), False, s_path, w - 2)
    for pt in s_path:
        pygame.draw.circle(face, (20, 14, 10, 80), pt, (w - 2) // 2)
    pygame.draw.line(face, (20, 14, 10, 80),
                     (vertex[0] + 1, vertex[1] + 1),
                     (r_arm[0] + 1,  r_arm[1] + 1), w - 2)

    # Main ink: left arm with loop
    pygame.draw.lines(face, ink, False, left_path, w)
    for pt in left_path:
        pygame.draw.circle(face, ink, pt, w // 2)

    # Right arm: clean straight line
    pygame.draw.line(face, ink, vertex, r_arm, w)
    pygame.draw.circle(face, ink, r_arm, w // 2)


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
