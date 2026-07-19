"""grommet-rip-down — store_owned_v2 concept, round 2 headless render.

An OWNED card-state chip whose STORY is now the simplest one that fits the art:
the cord is fine — properly knotted and still threaded through the grommet — but
the swing-tag BODY tore around the top. The left ~half of the tag survived; the
right half ripped away along a near-vertical torn seam. A clean notch is bitten
out of the grommet's top-right (a visible gap in an otherwise near-complete ring)
where the tear originated. The surviving cream remnant hangs askew at a steeper
-15° (vs the priced tag's -7°) because its attachment is damaged.

Round 2 addresses the R1 critique:
  * The R1 260° "ruptured arc" smudged at display scale, so the grommet is now a
    standard near-complete ring PLUS a punched notch (a ~15 SS-px bite) in the
    top-right quadrant — a readable gap, not a sub-pixel break.
  * The R1 -15° swing clipped the bottom-left corner past x=0 (a flat vertical
    shear). The remnant is nudged right (_TAG_CENTER x 44->56) so the corner
    clears the card inset by ~4.7 SS-px while the tilt stays a damaged -15°.
  * The story drops the contradictory "cord ripped through the grommet" claim:
    cord + knot are intact; only the tag tore.
  * The R1 10-point high-frequency jitter is replaced by 4 deliberate triangular
    teeth of consistent amplitude, backed by a solid key-tone shadow line hugging
    the INNER side of the seam so the remnant reads as paper with thickness.

Construction (custom-draw, not _draw_hang_tag): cord + knot are pixel-identical
to the priced state (same knot, cord colour/width). A full cream face is built,
its grommet punched + wrapped in a near-complete ring with a top-right notch bite,
then the right ~half is polygon-punched away along a 4-tooth seam. The remnant is
rotated -15° and pinned so its grommet lands exactly where the cord ends.

Headless (SDL dummy) -> a 3-up review sheet (UNOWNED price tag / EQUIPPED base
✓ tag / the concept) at SS (324x200 panels, no downscale) plus a scale2x zoom
of the concept's real-scale (1x) render below Panel 2. Not wired into the live
store; writes docs/store_owned_v2/grommet_rip_down/round_2.png.
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

# The knot is pixel-identical to _draw_hang_tag so the cord's card-end matches the
# priced/equipped siblings exactly. The tag CENTRE, however, is nudged right of the
# priced tag's (44,60): the -15° swing would otherwise carry the remnant's
# bottom-left corner past x=0 and shear it flat against the panel edge. At x=56 the
# corner clears the card inset by ~4.7 SS-px; the cord's tag-end simply follows the
# grommet out, reading as a tag swung aside by its damaged attachment.
_TAG_CENTER = (56, 60)
_KNOT = (22, 13)
_GROMMET = (30, 13)

# The steeper hang of a damaged attachment: the remnant tilts -15° where the
# intact priced tag hangs at -7°.
_RIP_TILT = -15

_CORD = (190, 165, 115)
_RING = (110, 80, 30)                 # grommet ring, matches _draw_hang_tag
_SEAM_SHADOW = (46, 38, 18)           # torn-edge inner shadow (regalia KEY tone)

# The torn seam in FACE space (81x94): a near-vertical, one-sided edge with FOUR
# deliberate triangular teeth of consistent amplitude (apex ~x48 jutting toward the
# lost half, valleys pulled back to ~x38 — a ~10 SS-px / ~5 real-px sawtooth). It
# starts beside the grommet notch (the tear origin) and rips straight down. The
# LEFT half is kept; everything right of the seam tore away.
_SEAM = [
    (45, 0),      # tear origin, hard against the grommet notch
    (48, 8),      # tooth 1 apex
    (38, 20),     # valley
    (48, 31),     # tooth 2 apex
    (38, 43),     # valley
    (47, 54),     # tooth 3 apex
    (39, 66),     # valley
    (47, 77),     # tooth 4 apex
    (39, 88),     # valley
    (42, _TAG_H), # torn edge meets the bottom
]

# The grommet notch: a wedge bitten out of the ring's top-right quadrant where the
# tag began to tear. Reaches up to the top edge so the bite reads as "tore around
# the top". Chord across the outer mouth is ~15 SS-px (~7.5 real-px) — a clear gap.
_NOTCH_R = 16
_NOTCH_A1, _NOTCH_A2 = -68, -12       # degrees, screen space (y-down)
_NOTCH_APEX = (31, 14)


def _rot_point(px, py, center, tilt):
    """Face-space point -> surface coords for an arbitrary tilt. The module helper
    is locked to -7°; the remnant needs its own -15° mapping."""
    th = math.radians(tilt)
    dx, dy = px - _TAG_W / 2, py - _TAG_H / 2
    rx = dx * math.cos(th) + dy * math.sin(th)
    ry = -dx * math.sin(th) + dy * math.cos(th)
    return (center[0] + rx, center[1] + ry)


def _build_face():
    """The full cream swing-tag face + gold bevel — the exact affordable-tag body
    from _draw_hang_tag, so the remnant reads as the same product."""
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


def _notched_grommet(face):
    """Punch the grommet hole, draw a STANDARD near-complete ring, then bite a
    clean notch out of the top-right quadrant. The cord still threads the intact
    ~304° of ring; the notch is a visible gap (not a sub-pixel arc break) marking
    where the tag tore."""
    pygame.draw.circle(face, (0, 0, 0, 0), _GROMMET, sc.m(5))
    pygame.draw.circle(face, _RING, _GROMMET, sc.m(5) + 1, width=max(1, sc.m(1.4)))
    # A transparent wedge removes the ring arc AND the paper in that sector, so the
    # notch reads as a bite rather than a break in the ring alone.
    gx, gy = _GROMMET
    p1 = (gx + _NOTCH_R * math.cos(math.radians(_NOTCH_A1)),
          gy + _NOTCH_R * math.sin(math.radians(_NOTCH_A1)))
    p2 = (gx + _NOTCH_R * math.cos(math.radians(_NOTCH_A2)),
          gy + _NOTCH_R * math.sin(math.radians(_NOTCH_A2)))
    pygame.draw.polygon(face, (0, 0, 0, 0), [_NOTCH_APEX, p1, p2])


def _keep_mask():
    """Polygon covering the surviving LEFT remnant: top-left corner, along the top
    edge to the tear origin, DOWN the 4-tooth seam, then across the bottom."""
    poly = [(0, 0)] + _SEAM + [(0, _TAG_H)]
    mask = pygame.Surface((_TAG_W, _TAG_H), pygame.SRCALPHA)
    pygame.draw.polygon(mask, (255, 255, 255, 255), poly)
    return mask


def _seam_thickness(face):
    """A solid key-tone shadow line hugging the INNER side of the torn seam. Offset
    a hair LEFT of the edge so it stays inside the remnant, it gives the tear a
    paper-thickness read without the R1 sub-pixel crest/valley dots."""
    inner = [(x - sc.m(1.5), y) for x, y in _SEAM]
    pygame.draw.lines(face, _SEAM_SHADOW, False, inner, max(1, sc.m(2)))


def _build_remnant():
    face = _build_face()
    _notched_grommet(face)
    mask = _keep_mask()
    face.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    _seam_thickness(face)
    return face


def draw_grommet_rip_down(surf):
    """The grommet-rip-down owned chip: pixel-identical cord + knot, then the -15°
    cream remnant pinned by its centre so its grommet lands where the cord ends."""
    remnant = pygame.transform.rotate(_build_remnant(), _RIP_TILT)

    # Rotating about the centre keeps the face centre at _TAG_CENTER, so the grommet
    # lands at its own rotated surface point — draw the cord's tag-end to that point.
    gx, gy = _rot_point(*_GROMMET, _TAG_CENTER, _RIP_TILT)

    lw = sc.m(1.5)
    pygame.draw.line(surf, _CORD, (gx, gy), (_KNOT[0] - 1, _KNOT[1] - 1), lw)
    pygame.draw.line(surf, _CORD, (gx, gy), (_KNOT[0] + 2, _KNOT[1] + 2), lw)
    surf.blit(remnant, remnant.get_rect(center=_TAG_CENTER))
    pygame.draw.circle(surf, _CORD, _KNOT, sc.m(1.5))
    pygame.draw.circle(surf, (min(_CORD[0] + 30, 255), min(_CORD[1] + 30, 255),
                              min(_CORD[2] + 30, 255)), _KNOT, max(1, sc.m(0.6)))


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
draw_grommet_rip_down(p2)


# ── 1× re-verification (R2 note 5) ──────────────────────────────────────────────
# Confirm at REAL scale that the tag never shears against x=0. The card body's own
# drop shadow bleeds to x=0, so measuring on the full card is misleading; instead
# isolate the tag on a transparent panel, smoothscale to 1x, and scan the bottom
# rows (tag-only region) for the leftmost opaque column.
_one_x = pygame.transform.smoothscale(p2, (CARD_W, CARD_H))
_iso = _new_panel()
draw_grommet_rip_down(_iso)
_iso1 = pygame.transform.smoothscale(_iso, (CARD_W, CARD_H))
_min_x = CARD_W
for _x in range(0, CARD_W // 2):
    if any(_iso1.get_at((_x, _y)).a > 40 for _y in range(0, CARD_H)):
        _min_x = _x
        break
_corner = _rot_point(0, _TAG_H, _TAG_CENTER, _RIP_TILT)
print(f"1x leftmost opaque tag column x={_min_x} (>=2 real-px clears inset); "
      f"analytic bottom-left corner SS={_corner}")
assert _min_x >= 2, f"tag shears at left edge (min_x={_min_x})"


# ── review sheet ──────────────────────────────────────────────────────────────
PANEL_W, PANEL_H = CARD_W * sc.SS, CARD_H * sc.SS
BG = (8, 8, 20)
xs = [20, 360, 700]
panel_y = 102
labels = ["UNOWNED (price tag)", "EQUIPPED base (✓ tag)",
          "CONCEPT: grommet-rip-down"]

zoom = pygame.transform.scale2x(_one_x)
zoom_label_y = panel_y + PANEL_H + 24
zoom_y = zoom_label_y + 22

sheet_w = xs[-1] + PANEL_W + 20
sheet_h = zoom_y + zoom.get_height() + 24
sheet = pygame.Surface((sheet_w, sheet_h))
sheet.fill(BG)

title = hud_font(24, True).render(
    "store_owned_v2 — grommet-rip-down — round 2", True, (238, 232, 214))
sheet.blit(title, (20, 34))
sub = hud_font(15, True).render(
    "owned card-state chip: cord intact + threaded, but the tag BODY tore — left "
    "half survives, notch bitten from the grommet's top-right; remnant hangs -15°",
    True, (168, 172, 196))
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

out = "/home/user/skybit/docs/store_owned_v2/grommet_rip_down/round_2.png"
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(sheet, out)
print("saved", out, sheet.get_size())
