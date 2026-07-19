"""barely-attached-rip — store_owned_v2 concept, round 2 (RE-ROLL of R1).

R1 was a two-piece composition (upper piece + a lower fragment dangling by a
single ~0.5px fibre) that read as damage/glitch, not "owned/triumphant". R2
resolves that into a SINGLE decisively-torn remnant: the tag was grabbed and
yanked, the price portion is gone, and a clean strong stub survives on the cord.

Construction reuses `_draw_hang_tag` VERBATIM (cord, knot, grommet, bevel, body
geometry are pixel-identical to the priced/equipped states). The only concept-
specific work happens inside `barely_torn_face`, passed as draw_face_fn: it
punches the bottom ~50% of the cream face to alpha 0 and inks a strong jagged
torn seam — downward paper-tongue teeth, deep V-bites cutting up toward the
grommet, fibre-core highlights on the peaks, valley shadow in the troughs.

Headless (SDL dummy) -> a 3-up review sheet (UNOWNED price tag / EQUIPPED base
check tag / the concept) at SS plus a scale2x zoom of the concept's real-scale
(1x) render below Panel 2. Writes docs/store_owned_v2/barely_attached_rip/round_2.png.
"""
import os
import sys

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

CARD_W, CARD_H = sc.CARD_W, sc.CARD_H
_TAG_W, _TAG_H = sc._TAG_W, sc._TAG_H

_FIBER = (255, 240, 190)             # lit fibre core catching the top-left light
_SEAM_SHADOW = (46, 38, 18)          # dark valley ink of the torn edge

# Hand-authored seam across the full face width. Mean line sits at ~0.50*_TAG_H
# (well below the grommet at y=13), so the whole grommet survives the tear.
# Teeth (T) spike DOWN past the mean as still-attached paper tongues; bites (B)
# cut UP toward the grommet baseline. 17 vertices, strong reversals — a real,
# resolved yank, not a soft sawtooth.
_MEAN = int(_TAG_H * 0.50)           # 47
_SEAM = [
    (0,  _MEAN - 1),
    (5,  _MEAN - 5),
    (10, 61),        # T1 down  (+14 below mean ≈ m(7))
    (15, _MEAN - 3),
    (20, 30),        # B1 up toward grommet
    (26, _MEAN),
    (31, 63),        # T2 down  (+16 ≈ m(8)), directly under grommet but far below it
    (37, _MEAN - 2),
    (43, _MEAN + 5),
    (49, 26),        # B2 deep bite up toward grommet baseline
    (55, _MEAN + 1),
    (60, 64),        # T3 down  (+17)
    (66, _MEAN - 1),
    (71, _MEAN + 8),
    (76, _MEAN - 5),
    (81, _MEAN),
]
_TEETH = [(10, 61), (31, 63), (60, 64)]     # down-peaks: fibre core catches light
_BITES = [(20, 30), (49, 26)]               # up-troughs: valley shadow


def barely_torn_face(face):
    """Punch away the lower half of the cream face and ink a decisive torn seam.

    Order matters: paint the edge detail first, then clip the whole face to the
    survivor polygon with BLEND_RGBA_MIN. That single clip both removes the
    price portion (bottom ~50% -> alpha 0) and trims any stray ink that fell
    below the tear, so the seam stays crisp with no dark bleed under the stub."""
    seam = _SEAM

    # continuous edge line so the torn contour reads even at 1x
    ipts = [(int(x), int(y)) for x, y in seam]
    pygame.draw.lines(face, _SEAM_SHADOW, False, ipts, max(1, sc.m(1)))

    # fibre-core highlight standing UP off each downward tooth tip (m(2) wide)
    for tx, ty in _TEETH:
        pygame.draw.line(face, _FIBER, (tx, ty), (tx, ty - sc.m(4)), sc.m(2))
        pygame.draw.line(face, _SEAM_SHADOW, (tx, ty + 1), (tx, ty + 1), 1)

    # valley shadow pooled in each deep V-bite trough (m(2) wide)
    for bx, by in _BITES:
        pygame.draw.line(face, _SEAM_SHADOW, (bx, by), (bx, by + sc.m(3)), sc.m(2))

    # clip everything to the survivor silhouette (top edge + torn seam)
    survivor = [(0, 0), (_TAG_W, 0)] + [(x, y) for x, y in reversed(seam)]
    mask = pygame.Surface(face.get_size(), pygame.SRCALPHA)
    pygame.draw.polygon(mask, (255, 255, 255, 255), survivor)
    face.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)


# ── panels ──────────────────────────────────────────────────────────────────────
def _new_panel():
    return pygame.Surface((CARD_W * sc.SS, CARD_H * sc.SS), pygame.SRCALPHA)


def _rect():
    return pygame.Rect(sc.m(sc._INSET), sc.m(sc._INSET),
                       CARD_W * sc.SS - 2 * sc.m(sc._INSET),
                       CARD_H * sc.SS - 2 * sc.m(sc._INSET))


p0 = _new_panel()
sc.draw_card(p0, SID, _rect(), equipped=False, secret=False, owned=False)

p1 = _new_panel()
sc.draw_card(p1, SID, _rect(), equipped=True, secret=False, owned=False)

# Concept: draw the base card without its state chip, then the torn hang-tag at
# the same anchor _draw_hang_tag uses for owned/equipped.
p2 = _new_panel()
_orig_state_chip = sc.state_chip
sc.state_chip = lambda *a, **kw: None
try:
    sc.draw_card(p2, SID, _rect(), equipped=False, secret=False, owned=False)
finally:
    sc.state_chip = _orig_state_chip
sc._draw_hang_tag(p2, 44, 60, draw_face_fn=barely_torn_face)


# ── review sheet ──────────────────────────────────────────────────────────────
PANEL_W, PANEL_H = CARD_W * sc.SS, CARD_H * sc.SS
BG = (8, 8, 20)
xs = [20, 360, 700]
panel_y = 102
labels = ["UNOWNED (price tag)", "EQUIPPED base (check tag)",
          "CONCEPT: barely-attached-rip"]

zoom = pygame.transform.scale2x(
    pygame.transform.smoothscale(p2, (CARD_W, CARD_H)))
zoom_label_y = panel_y + PANEL_H + 24
zoom_y = zoom_label_y + 22

sheet_w = xs[-1] + PANEL_W + 20
sheet_h = zoom_y + zoom.get_height() + 24
sheet = pygame.Surface((sheet_w, sheet_h))
sheet.fill(BG)

title = hud_font(24, True).render(
    "store_owned_v2 — barely-attached-rip — round 2 (re-roll)", True, (238, 232, 214))
sheet.blit(title, (20, 34))
sub = hud_font(15, True).render(
    "owned card-state chip: a SINGLE decisively-torn remnant on the cord — "
    "price portion yanked away, strong jagged seam", True, (168, 172, 196))
sheet.blit(sub, (20, 68))

lf = hud_font(16, True)
for x, panel, lab in zip(xs, (p0, p1, p2), labels):
    sheet.blit(panel, (x, panel_y))
    lt = lf.render(lab, True, (210, 214, 232))
    sheet.blit(lt, (x + (PANEL_W - lt.get_width()) // 2, panel_y + PANEL_H + 4))

zl = hud_font(15, True).render(
    "concept @ real scale (1x render, magnified 2x for inspection):",
    True, (200, 204, 220))
sheet.blit(zl, (xs[2], zoom_label_y))
sheet.blit(zoom, (xs[2], zoom_y))

out = "/home/user/skybit/docs/store_owned_v2/barely_attached_rip/round_2.png"
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(sheet, out)
print("saved", out, sheet.get_size())
