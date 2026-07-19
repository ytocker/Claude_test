"""clean-rip-halves — store_owned_v1 concept, round 1 headless render.

An OWNED card-state chip: the cream swing-tag is torn into two halves that
still hang from the one cord. A clean straight/gentle-diagonal rip (NOT a
lightning zigzag) runs from the bottom edge up to just below the grommet; the
two halves splay ~5° apart, revealing a slim wedge of card indigo between them.
A gold coin token bridges the seam at mid-height — the positive "you kept your
half" claim that replaces the dark ✓. Each inner seam edge carries a 1px
dark-key shadow line so the tear reads crisp. Boldest silhouette of the set.

Construction (custom-draw, not _draw_hang_tag): build ONE cream face, split it
into a full-top LEFT mask (owns the grommet) and a right-of-seam RIGHT mask,
draw the dark seam-shadow on each inner edge, then rotate LEFT at the base -7°
and RIGHT at -2° (adds +5° splay) — both PINNED to the same grommet point so
the tag hangs from a single cord. The bottoms fan out; the gap widens downward.

Headless (SDL dummy) → a 3-up review sheet (UNOWNED price tag / EQUIPPED base
✓ tag / the concept) at SS (324x200 panels, no downscale) plus a scale2x zoom
of the concept's real-scale (1x) render below Panel 2. Not wired into the live
store; writes docs/store_owned_v1/clean_rip_halves/round_1.png.
"""
import math
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


# ── the concept chip ───────────────────────────────────────────────────────────
# Fixed swing-tag anchor on the 324x200 SS panel — same anchor the owned/equipped
# tags use, so the concept lands exactly where the ✓ tag would.
_TAG_CENTER = (44, 60)
_KNOT = (22, 13)
_GROMMET = (30, 13)

# The rip line in FACE space (81x94): near-vertical, gentle rightward lean,
# starting just BELOW the grommet ring (y≈28) down to the bottom edge.
_SEAM_Y0, _SEAM_Y1 = 28, _TAG_H
_SEAM_X0, _SEAM_X1 = 39, 45          # ~6px over 66px ≈ 5°: a clean diagonal
# The halves' inner edges sit 1px either side of the seam centre so a slim wedge
# of card indigo shows through between the pieces.
_SEAM_INSET = 1

_CORD = (190, 165, 115)
_SEAM_SHADOW = (54, 38, 20)          # dark-key line hugging each inner tear edge


def _seam_x(y):
    t = (y - _SEAM_Y0) / max(1, (_SEAM_Y1 - _SEAM_Y0))
    return _SEAM_X0 + (_SEAM_X1 - _SEAM_X0) * t


def _rot_point(px, py, center, tilt):
    """Face-space point → surface coords for an arbitrary tilt (the module helper
    is locked to -7°, but the right half needs its own -2° mapping)."""
    th = math.radians(tilt)
    dx, dy = px - _TAG_W / 2, py - _TAG_H / 2
    rx = dx * math.cos(th) + dy * math.sin(th)
    ry = -dx * math.sin(th) + dy * math.cos(th)
    return (center[0] + rx, center[1] + ry)


def _build_face():
    """The full cream swing-tag face + gold bevel — the exact affordable-tag body
    from _draw_hang_tag, so the halves read as the same product."""
    rad = sc.m(3)
    face = pygame.Surface((_TAG_W, _TAG_H), pygame.SRCALPHA)
    brect = pygame.Rect(0, 0, _TAG_W, _TAG_H)
    body = sc.vgrad_stops(_TAG_W, _TAG_H, rad,
                          [(0.0, (248, 238, 210)), (1.0, (224, 204, 166))],
                          255, gamma=1.04)
    face.blit(body, (0, 0))
    sc.bevel_rim(face, brect, rad, (80, 52, 12, 200),
                 (255, 240, 190, 200), w=max(1, sc.m(1.2)))
    return face


def _half(face, side):
    """Mask ONE half out of the cream face. Both halves keep the FULL top strip
    (above the tear origin) so, once pinned to the same grommet, they overlap
    into one joined head; only BELOW the origin do they part along the seam."""
    h = face.copy()
    xL0, xL1 = _seam_x(_SEAM_Y0) - _SEAM_INSET, _seam_x(_SEAM_Y1) - _SEAM_INSET
    xR0, xR1 = _seam_x(_SEAM_Y0) + _SEAM_INSET, _seam_x(_SEAM_Y1) + _SEAM_INSET
    if side == "left":
        poly = [(0, 0), (_TAG_W, 0), (_TAG_W, _SEAM_Y0),
                (xL0, _SEAM_Y0), (xL1, _SEAM_Y1), (0, _SEAM_Y1)]
        seam = ((xL0, _SEAM_Y0), (xL1, _SEAM_Y1))
    else:
        poly = [(0, 0), (_TAG_W, 0), (_TAG_W, _SEAM_Y1),
                (xR1, _SEAM_Y1), (xR0, _SEAM_Y0), (0, _SEAM_Y0)]
        seam = ((xR0, _SEAM_Y0), (xR1, _SEAM_Y1))
    mask = pygame.Surface((_TAG_W, _TAG_H), pygame.SRCALPHA)
    pygame.draw.polygon(mask, (255, 255, 255, 255), poly)
    h.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    # dark-key shadow hugging the inner tear edge, then re-clip so it can't bleed
    # past the masked silhouette.
    pygame.draw.line(h, _SEAM_SHADOW, seam[0], seam[1], max(1, sc.m(1)))
    h.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    return h


def draw_split_halves(surf):
    """The clean-rip-halves owned chip drawn onto an SS panel at the fixed tag
    anchor: cord + knot, two splayed cream halves hanging from one grommet, and
    the gold coin token bridging the seam."""
    face = _build_face()
    left = _half(face, "left")
    right = _half(face, "right")

    # The LEFT half owns the grommet hole + ring (its full top strip carries it);
    # the RIGHT half's top is hidden beneath the LEFT half once composited.
    pygame.draw.circle(left, (0, 0, 0, 0), _GROMMET, sc.m(5))
    pygame.draw.circle(left, (110, 80, 30), _GROMMET, sc.m(5) + 1,
                       width=max(1, sc.m(1)))

    rotL = pygame.transform.rotate(left, sc._TAG_TILT)          # -7°: base tilt
    rotR = pygame.transform.rotate(right, sc._TAG_TILT + 5)     # -2°: +5° splay

    # Pin BOTH grommets to the same surface point so the two halves hang from the
    # one cord; the +5° on the right then fans its bottom out into the wedge gap.
    gx, gy = _rot_point(*_GROMMET, _TAG_CENTER, sc._TAG_TILT)
    gRx, gRy = _rot_point(*_GROMMET, _TAG_CENTER, sc._TAG_TILT + 5)
    right_center = (_TAG_CENTER[0] + (gx - gRx), _TAG_CENTER[1] + (gy - gRy))

    # cord first (its top end tucks under the cream head), then the halves.
    lw = sc.m(1.5)
    pygame.draw.line(surf, _CORD, (gx, gy), (_KNOT[0] - 1, _KNOT[1] - 1), lw)
    pygame.draw.line(surf, _CORD, (gx, gy), (_KNOT[0] + 2, _KNOT[1] + 2), lw)

    # RIGHT under LEFT: the LEFT head + grommet stay crisp; below the origin the
    # halves are separated by the wedge, so nothing of the RIGHT bottom is lost.
    surf.blit(rotR, rotR.get_rect(center=right_center))
    surf.blit(rotL, rotL.get_rect(center=_TAG_CENTER))

    pygame.draw.circle(surf, _CORD, _KNOT, sc.m(1.5))
    pygame.draw.circle(surf, (min(_CORD[0] + 30, 255), min(_CORD[1] + 30, 255),
                              min(_CORD[2] + 30, 255)), _KNOT, max(1, sc.m(0.6)))

    # gold coin token straddling the seam at mid-height — "you kept your half".
    cx, cy = _rot_point(_seam_x((_SEAM_Y0 + _SEAM_Y1) / 2),
                        (_SEAM_Y0 + _SEAM_Y1) / 2, _TAG_CENTER, sc._TAG_TILT)
    cx, cy = int(round(cx)), int(round(cy))
    r = sc.m(8)
    pygame.draw.circle(surf, (236, 202, 116), (cx, cy), r)
    pygame.draw.circle(surf, (255, 248, 224),
                       (cx - int(r * 0.32), cy - int(r * 0.32)), max(1, int(r * 0.42)))
    pygame.draw.circle(surf, (110, 80, 30), (cx, cy), r, width=max(1, sc.m(1)))


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

p2 = _new_panel()
_orig_state_chip = sc.state_chip
sc.state_chip = lambda *a, **kw: None
try:
    sc.draw_card(p2, SID, _rect(), equipped=False, secret=False, owned=False)
finally:
    sc.state_chip = _orig_state_chip
draw_split_halves(p2)


# ── review sheet ──────────────────────────────────────────────────────────────
PANEL_W, PANEL_H = CARD_W * sc.SS, CARD_H * sc.SS
BG = (8, 8, 20)
xs = [20, 360, 700]
panel_y = 102
labels = ["UNOWNED (price tag)", "EQUIPPED base (✓ tag)",
          "CONCEPT: clean-rip-halves"]

zoom = pygame.transform.scale2x(
    pygame.transform.smoothscale(p2, (CARD_W, CARD_H)))
zoom_label_y = panel_y + PANEL_H + 24
zoom_y = zoom_label_y + 22

sheet_w = xs[-1] + PANEL_W + 20
sheet_h = zoom_y + zoom.get_height() + 24
sheet = pygame.Surface((sheet_w, sheet_h))
sheet.fill(BG)

title = hud_font(24, True).render(
    "store_owned_v1 — clean-rip-halves — round 1", True, (238, 232, 214))
sheet.blit(title, (20, 34))
sub = hud_font(15, True).render(
    "owned card-state chip: tag torn into two halves on one cord, gold coin "
    "bridging the seam", True, (168, 172, 196))
sheet.blit(sub, (20, 68))

lf = hud_font(16, True)
for x, panel, lab in zip(xs, (p0, p1, p2), labels):
    sheet.blit(panel, (x, panel_y))
    lt = lf.render(lab, True, (210, 214, 232))
    sheet.blit(lt, (x + (PANEL_W - lt.get_width()) // 2, panel_y + PANEL_H + 4))

zl = hud_font(15, True).render(
    "concept @ real scale (1× render, magnified 2× for inspection):",
    True, (200, 204, 220))
sheet.blit(zl, (xs[2], zoom_label_y))
sheet.blit(zoom, (xs[2], zoom_y))

out = "/home/user/skybit/docs/store_owned_v1/clean_rip_halves/round_1.png"
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(sheet, out)
print("saved", out, sheet.get_size())
