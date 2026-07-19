"""grommet-rip-down — store_owned_v2 concept, round 1 headless render.

An OWNED card-state chip: the cord ripped THROUGH the grommet hole, and the
tear kept going — a jagged one-sided rip runs DOWN from the ruptured hole into
the body, carving away the right half of the swing-tag. The tag is clearly
half-gone; the surviving cream remnant hangs askew at a steeper -15° (vs the
priced tag's -7°) because its attachment point is damaged. The grommet ring is
drawn as a partial ~270° arc, broken open on the tear side. This is a
one-sided, top-originating vertical tear — NOT a symmetric V-notch.

Construction (custom-draw, not _draw_hang_tag): cord + knot are pixel-identical
to the priced state (same _draw_hang_tag coordinates). A full cream face is
built, its grommet punched + wrapped in a ruptured partial ring, then the right
half is polygon-punched away along a jagged asymmetric seam. The torn edge is
the hero: fiber-core highlights on the peaks that jut toward the lost half,
deep valley shadow in the notches. The remnant is rotated -15° and pinned so
its grommet lands exactly where the cord meets the tag.

Headless (SDL dummy) -> a 3-up review sheet (UNOWNED price tag / EQUIPPED base
✓ tag / the concept) at SS (324x200 panels, no downscale) plus a scale2x zoom
of the concept's real-scale (1x) render below Panel 2. Not wired into the live
store; writes docs/store_owned_v2/grommet_rip_down/round_1.png.
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

# Fixed swing-tag anchor on the 324x200 SS panel — the same anchor the owned/
# equipped tags use, so the concept lands exactly where the ✓ tag would.
_TAG_CENTER = (44, 60)
_KNOT = (22, 13)
_GROMMET = (30, 13)

# The steeper hang of a damaged attachment: the remnant tilts -15° where the
# intact priced tag hangs at -7°.
_RIP_TILT = -15

_CORD = (190, 165, 115)
_RING = (110, 80, 30)                 # grommet ring, matches _draw_hang_tag
_FIBER = (255, 240, 190)              # lit torn-fiber crest (bevel highlight tone)
_SEAM_SHADOW = (46, 38, 18)           # torn-edge shadow (regalia KEY tone)
_SEAM_VALLEY = (9, 9, 22)             # deepest notch shadow (regalia VALLEY tone)

# The jagged tear in FACE space (81x94): a vertical-ish, asymmetric channel that
# originates at the top edge beside the grommet, pinches through the hole's right
# rim, then rips down to the bottom. Everything RIGHT of it is torn away, so the
# remnant is the left ~half that still owns the grommet.
_SEAM = [
    (37, 0),      # torn top corner where the cord ripped out through the hole
    (34, 8),      # pinches in across the grommet's right rim
    (42, 16),
    (36, 26),
    (45, 36),
    (38, 47),
    (46, 58),
    (39, 69),
    (47, 80),
    (41, _TAG_H),
]
# Local x-maxima are torn fibers jutting toward the lost half (catch light);
# local x-minima are notches that fall into shadow.
_SEAM_PEAKS = [(42, 16), (45, 36), (46, 58), (47, 80)]
_SEAM_VALLEYS = [(34, 8), (36, 26), (38, 47), (39, 69)]


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


def _ruptured_ring(face):
    """Punch the grommet hole, then wrap it in a PARTIAL ~270° ring broken open
    on the tear side (down-right) — where the cord ripped out through the hole."""
    pygame.draw.circle(face, (0, 0, 0, 0), _GROMMET, sc.m(5))
    rr = sc.m(5) + 1
    # Screen-angle sweep (0°=east, +90°=down): keep 80°..340°, leaving the gap
    # facing east / down-right toward the lost half and the descending rip.
    pts = []
    for deg in range(80, 341, 6):
        a = math.radians(deg)
        pts.append((_GROMMET[0] + rr * math.cos(a), _GROMMET[1] + rr * math.sin(a)))
    pygame.draw.lines(face, _RING, False, pts, max(1, sc.m(1)))


def _keep_mask():
    """Polygon covering the surviving LEFT remnant: top-left corner, along the
    top edge to the seam origin, DOWN the jagged seam, then across the bottom."""
    poly = [(0, 0)] + _SEAM + [(0, _TAG_H)]
    mask = pygame.Surface((_TAG_W, _TAG_H), pygame.SRCALPHA)
    pygame.draw.polygon(mask, (255, 255, 255, 255), poly)
    return mask


def _dress_seam(face, mask):
    """The torn edge is the hero seam: a dark shadow line hugging the tear, deep
    notch shadow in the valleys, lit fiber crests on the peaks that jut toward
    the lost half. Re-clip to the mask so nothing bleeds past the remnant."""
    pygame.draw.lines(face, _SEAM_SHADOW, False, _SEAM, max(1, sc.m(1.2)))
    for vx, vy in _SEAM_VALLEYS:
        pygame.draw.circle(face, _SEAM_VALLEY, (vx, vy), max(1, sc.m(0.9)))
    for px, py in _SEAM_PEAKS:
        # crest highlight nudged a hair INTO the remnant so it reads as a lit
        # fiber tip, not an outline.
        pygame.draw.circle(face, _FIBER, (px - sc.m(1), py), max(1, sc.m(0.8)))
    face.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)


def _build_remnant():
    face = _build_face()
    _ruptured_ring(face)
    mask = _keep_mask()
    face.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    _dress_seam(face, mask)
    return face


def draw_grommet_rip_down(surf):
    """The grommet-rip-down owned chip: pixel-identical cord + knot, then the
    -15° cream remnant pinned so its grommet lands where the cord meets the tag."""
    remnant = _build_remnant()
    rot = pygame.transform.rotate(remnant, _RIP_TILT)

    # Cord attaches at the priced tag's grommet surface point (pixel-identical).
    gx, gy = sc._tag_rot_point(*_GROMMET, _TAG_CENTER)
    # Pin the remnant so its own grommet lands on that same cord point: solve the
    # blit centre from the grommet's offset under the -15° rotation.
    th = math.radians(_RIP_TILT)
    dx, dy = _GROMMET[0] - _TAG_W / 2, _GROMMET[1] - _TAG_H / 2
    rx = dx * math.cos(th) + dy * math.sin(th)
    ry = -dx * math.sin(th) + dy * math.cos(th)
    remnant_center = (gx - rx, gy - ry)

    lw = sc.m(1.5)
    pygame.draw.line(surf, _CORD, (gx, gy), (_KNOT[0] - 1, _KNOT[1] - 1), lw)
    pygame.draw.line(surf, _CORD, (gx, gy), (_KNOT[0] + 2, _KNOT[1] + 2), lw)
    surf.blit(rot, rot.get_rect(center=remnant_center))
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


# ── review sheet ──────────────────────────────────────────────────────────────
PANEL_W, PANEL_H = CARD_W * sc.SS, CARD_H * sc.SS
BG = (8, 8, 20)
xs = [20, 360, 700]
panel_y = 102
labels = ["UNOWNED (price tag)", "EQUIPPED base (✓ tag)",
          "CONCEPT: grommet-rip-down"]

zoom = pygame.transform.scale2x(
    pygame.transform.smoothscale(p2, (CARD_W, CARD_H)))
zoom_label_y = panel_y + PANEL_H + 24
zoom_y = zoom_label_y + 22

sheet_w = xs[-1] + PANEL_W + 20
sheet_h = zoom_y + zoom.get_height() + 24
sheet = pygame.Surface((sheet_w, sheet_h))
sheet.fill(BG)

title = hud_font(24, True).render(
    "store_owned_v2 — grommet-rip-down — round 1", True, (238, 232, 214))
sheet.blit(title, (20, 34))
sub = hud_font(15, True).render(
    "owned card-state chip: cord rips through the grommet, tear runs down and "
    "carves away half the tag; remnant hangs askew at -15°",
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

out = "/home/user/skybit/docs/store_owned_v2/grommet_rip_down/round_1.png"
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(sheet, out)
print("saved", out, sheet.get_size())
