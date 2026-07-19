"""clean-rip-halves — store_owned_v1 concept, round 2 headless render.

An OWNED card-state chip: the cream swing-tag is torn into two halves that
still hang from the one cord. A clean straight/gentle-diagonal rip (NOT a
lightning zigzag) runs from just below the grommet down to the bottom edge; the
right half is dropped + nudged so the two bottom corners are visibly offset — a
notched, double-bottomed outline that reads as "two halves" even at 40px. The
rip TAPERS: a pin-narrow origin at the grommet punch widening to a bold wedge at
the bottom, filled with a lit indigo reveal — the card's inside showing through,
not a shadow crack. A gold coin sits slightly off-centre, overlapping the left
half's torn lip, so it bridges two KEPT halves rather than plugging a fracture.

Round-2 changes vs r1 (all art-director notes):
 1. Right half staggered DOWN + right so the silhouette actually splits (offset
    bottom corners), instead of relying on the near-invisible 5° splay alone.
 2. Gap widened (taper + stagger) and the inner bevel/dark-brown rims dropped so
    a continuous slice of card body shows top-to-bottom.
 3. The reveal is an explicit saturated indigo wedge with a lit interior
    highlight, so it reads as intentional "inside the card", not a shadow.
 4. The dark-key torn-lip shadow is drawn as one unbroken continuous line down
    each half's outward edge (surface space), so it survives the full rip length.
 5. The rip tapers narrow-at-grommet → wide-at-bottom, and the coin is biased
    onto one half's edge so it bridges rather than patches.

Construction (custom-draw, not _draw_hang_tag): build ONE cream face, split it
into a full-top LEFT mask (owns the grommet) and a right-of-seam RIGHT mask
along a tapering seam, rotate LEFT at -7° and RIGHT at -3° (+4° splay), pin both
to the same grommet point, then translate RIGHT down + right for the stagger.
The visible gap between the two rotated torn edges is painted with the indigo
reveal; the torn-lip shadow lines and coin go on top.

Headless (SDL dummy) → a 3-up review sheet (UNOWNED price tag / EQUIPPED base
✓ tag / the concept) at SS (324x200 panels, no downscale) plus a scale2x zoom
of the concept's real-scale (1x) render below Panel 2. Not wired into the live
store; writes docs/store_owned_v1/clean_rip_halves/round_2.png.
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
_SEAM_YS = list(range(_SEAM_Y0, _SEAM_Y1 + 1))

# Tilts: LEFT keeps the base -7°; RIGHT gets +4° splay AND a physical stagger so
# the two bottom corners clearly separate (a splay alone is invisible at 40px).
_TILT_L = sc._TAG_TILT
_TILT_R = sc._TAG_TILT + 4
# Surface-space nudge of the right half (panel is 2× real → ~2.5px right, 5px
# down at the final ~47px tag): the double-bottomed silhouette.
_STAG = (5, 10)

_CORD = (190, 165, 115)
# Warm dark torn-lip shadow — the cream cardstock's own shadow, drawn continuous
# down each half's outward edge so every torn edge carries one unbroken 1px line.
_SEAM_SHADOW = (48, 36, 28)
# The reveal: a saturated indigo (well above the card slate ~69,71,103 so it
# reads as "inside the card", not a shadow) with a lit interior highlight.
_REVEAL = (60, 62, 112)
_REVEAL_LIT = (112, 120, 198, 95)


def _seam_x(y):
    t = (y - _SEAM_Y0) / max(1, (_SEAM_Y1 - _SEAM_Y0))
    return _SEAM_X0 + (_SEAM_X1 - _SEAM_X0) * t


def _inset(y):
    """Half-width of the rip at height y (face space). Pin-narrow at the grommet
    punch, widening downward — a tear pulling apart from the hole down."""
    t = (y - _SEAM_Y0) / max(1, (_SEAM_Y1 - _SEAM_Y0))
    return 0.9 + 3.4 * t


def _rot_point(px, py, center, tilt):
    """Face-space point → surface coords for an arbitrary tilt (the module helper
    is locked to -7°, but the right half needs its own tilt + stagger mapping)."""
    th = math.radians(tilt)
    dx, dy = px - _TAG_W / 2, py - _TAG_H / 2
    rx = dx * math.cos(th) + dy * math.sin(th)
    ry = -dx * math.sin(th) + dy * math.cos(th)
    return (center[0] + rx, center[1] + ry)


def _build_face():
    """The full cream swing-tag face + gold bevel — the exact affordable-tag body
    from _draw_hang_tag, so the halves read as the same product. The bevel rim
    lives only on the OUTER rounded rect; the torn (interior) edge is raw body,
    so no bevel rims kiss shut in the gap."""
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
    """Mask ONE half out of the cream face along the tapering seam. Both halves
    keep the FULL top strip (above the tear origin) so, once pinned to the same
    grommet, they overlap into one joined head; only BELOW the origin do they
    part along the widening seam."""
    h = face.copy()
    if side == "left":
        edge = [(_seam_x(y) - _inset(y), y) for y in _SEAM_YS]
        poly = [(0, 0), (_TAG_W, 0), (_TAG_W, _SEAM_Y0)] + edge + [(0, _SEAM_Y1)]
    else:
        edge = [(_seam_x(y) + _inset(y), y) for y in reversed(_SEAM_YS)]
        poly = [(0, 0), (_TAG_W, 0), (_TAG_W, _SEAM_Y1)] + edge + [(0, _SEAM_Y0)]
    mask = pygame.Surface((_TAG_W, _TAG_H), pygame.SRCALPHA)
    pygame.draw.polygon(mask, (255, 255, 255, 255), poly)
    h.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    return h


def _edge_pts(side, center, tilt):
    """Surface-space polyline of ONE half's torn edge, so the reveal wedge and the
    torn-lip shadow trace exactly where the rotated/staggered half was cut."""
    sign = -1 if side == "left" else 1
    return [_rot_point(_seam_x(y) + sign * _inset(y), y, center, tilt)
            for y in _SEAM_YS]


def draw_split_halves(surf):
    """The clean-rip-halves owned chip: cord + knot, two staggered cream halves
    hanging from one grommet, a lit indigo reveal down the widening rip, and the
    gold coin bridging the seam onto the left half's torn lip."""
    face = _build_face()
    left = _half(face, "left")
    right = _half(face, "right")

    # The LEFT half owns the grommet hole + ring (its full top strip carries it);
    # the RIGHT half's top is hidden beneath the LEFT half once composited.
    pygame.draw.circle(left, (0, 0, 0, 0), _GROMMET, sc.m(5))
    pygame.draw.circle(left, (110, 80, 30), _GROMMET, sc.m(5) + 1,
                       width=max(1, sc.m(1)))

    rotL = pygame.transform.rotate(left, _TILT_L)
    rotR = pygame.transform.rotate(right, _TILT_R)

    # Pin BOTH grommets to the same surface point (one shared cord), then slide
    # the RIGHT half down + right for the stagger that splits the silhouette.
    gx, gy = _rot_point(*_GROMMET, _TAG_CENTER, _TILT_L)
    gRx, gRy = _rot_point(*_GROMMET, _TAG_CENTER, _TILT_R)
    right_center = (_TAG_CENTER[0] + (gx - gRx) + _STAG[0],
                    _TAG_CENTER[1] + (gy - gRy) + _STAG[1])

    # Torn-edge polylines in surface space (must match the blits below exactly).
    left_edge = _edge_pts("left", _TAG_CENTER, _TILT_L)
    right_edge = _edge_pts("right", right_center, _TILT_R)

    # cord first (its top end tucks under the cream head), then the reveal, then
    # the halves.
    lw = sc.m(1.5)
    pygame.draw.line(surf, _CORD, (gx, gy), (_KNOT[0] - 1, _KNOT[1] - 1), lw)
    pygame.draw.line(surf, _CORD, (gx, gy), (_KNOT[0] + 2, _KNOT[1] + 2), lw)

    # ── the indigo reveal wedge ──────────────────────────────────────────────
    # Fill the gap between the two torn edges with saturated indigo (slightly
    # inflated outward so the halves crop it clean), then a lit highlight down
    # the interior so the opening reads as the card's inside, not a crack.
    infl = 1.6
    wedge = ([(x - infl, y) for (x, y) in left_edge] +
             [(x + infl, y) for (x, y) in reversed(right_edge)])
    reveal = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    pygame.draw.polygon(reveal, _REVEAL,
                        [(int(round(x)), int(round(y))) for (x, y) in wedge])
    mid = [((lx + rx) / 2, (ly + ry) / 2)
           for (lx, ly), (rx, ry) in zip(left_edge, right_edge)]
    hi = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    pygame.draw.lines(hi, _REVEAL_LIT, False,
                      [(int(round(x)), int(round(y))) for (x, y) in mid],
                      max(1, sc.m(1)))
    reveal.blit(hi, (0, 0))
    surf.blit(reveal, (0, 0))

    # RIGHT under LEFT: the LEFT head + grommet stay crisp; the halves crop the
    # inflated reveal back to the true gap.
    surf.blit(rotR, rotR.get_rect(center=right_center))
    surf.blit(rotL, rotL.get_rect(center=_TAG_CENTER))

    pygame.draw.circle(surf, _CORD, _KNOT, sc.m(1.5))
    pygame.draw.circle(surf, (min(_CORD[0] + 30, 255), min(_CORD[1] + 30, 255),
                              min(_CORD[2] + 30, 255)), _KNOT, max(1, sc.m(0.6)))

    # ── continuous torn-lip shadow ───────────────────────────────────────────
    # One unbroken 1px dark line down each half's outward edge (drawn on top of
    # the composited halves so it can't erode after a few rows).
    sw = max(1, sc.m(1))
    for edge in (left_edge, right_edge):
        pygame.draw.lines(surf, _SEAM_SHADOW, False,
                          [(int(round(x)), int(round(y))) for (x, y) in edge], sw)

    # gold coin token biased onto the LEFT half's torn lip — "you kept your half",
    # bridging two kept pieces rather than plugging a fracture.
    ax, ay = _rot_point(_seam_x(60) - _inset(60), 60, _TAG_CENTER, _TILT_L)
    cx, cy = int(round(ax + sc.m(2.5))), int(round(ay))
    r = sc.m(7)
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
    "store_owned_v1 — clean-rip-halves — round 2", True, (238, 232, 214))
sheet.blit(title, (20, 34))
sub = hud_font(15, True).render(
    "owned card-state chip: staggered torn halves on one cord, lit indigo reveal "
    "down the taper, gold coin bridging the lip", True, (168, 172, 196))
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

out = "/home/user/skybit/docs/store_owned_v1/clean_rip_halves/round_2.png"
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(sheet, out)
print("saved", out, sheet.get_size())
