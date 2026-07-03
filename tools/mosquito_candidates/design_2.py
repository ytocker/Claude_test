"""MOSQUITO redesign — design_2 AMBER RELIC (legendary showpiece).

A mosquito caught mid-strike and frozen inside a lit teardrop of amber. The
selling idea is a warm gemstone glowing from within. The silhouette is laid
over on a DIAGONAL: the thorax humps high at the upper-left, the abdomen trails
down-and-right to a point at the lower-right (~35° slant), and the head with
its proboscis reaches out to the upper-right. Thorax is the corner of a shallow
boomerang — one arm (head + needle) up-right, the other (abdomen tail) down-
right — so at the 40px gameplay shrink it reads bug-on-a-slant, never an
upright figure. A swept-back wing pair fanned up-and-back over the body and
three thin legs dangling straight down are the two cues that survive the
shrink, so both are pushed to break the amber outline. A hot honey core blooms
directly behind the thorax so the jewel looks backlit from within, not like
dark set resin.

Scratch exploration only — NOT registered in animal_skins.BUILDERS / catalog.
Production art stays untouched until a winner is picked.
"""
import math
import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pygame  # noqa: E402

pygame.init()

from game.parrot import _WING_ANGLES, _add_outline, _aaellipse  # noqa: E402,F401
from game.animal_skins import (  # noqa: E402
    _make_prebuilt_skin, COMPOSITE_W, COMPOSITE_H, BCX, BCY, HCX, HCY, _new,
)

# ── palette ──────────────────────────────────────────────────────────────────
# Every note colour resolves to one of these five so the fossil, the resin and
# the glow share a single warm ramp: darkest underside → caramel → mid amber →
# honey rim → white glint.
FOSSIL = (58, 30, 8)      # #3A1E08 darkened fossil / shadowed underside
SEPIA  = (138, 75, 18)    # #8A4B12 caramel leg core / warm mid shade
AMBER  = (232, 162, 44)   # #E8A22C mid-amber resin field
HONEY  = (255, 216, 115)  # #FFD873 honey rim-light / lit leg edge
GLINT  = (255, 243, 201)  # #FFF3C9 hot-core highlight / catchlight

# Backlight sits directly behind the thorax hump so the fossil is lit from
# within and the halo bleeds out evenly in all directions.
CORE = (30, 32)

# Teardrop metaball chain — a true body-hugging drop. It rounds at the rear
# (upper-left, over the thorax back), swells widest behind the thorax, wraps the
# whole abdomen down to its lower-right tip, and pinches to a point aimed at the
# proboscis exit (upper-right). Radii are sized so head, thorax and abdomen all
# sit INSIDE; only the proboscis tip and the leg feet are meant to escape.
_TEAR_NODES = (
    (24, 31, 10.0),   # rounded rear over the thorax back (upper-left)
    (29, 30, 11.0),
    (31, 37, 12.0),   # widest bulge, right behind the thorax
    (36, 44, 11.0),
    (41, 50, 10.0),
    (46, 55,  8.0),
    (49, 58,  5.5),   # lobe enclosing the abdomen tail tip (lower-right)
    (42, 31,  9.5),   # over the head
    (49, 31,  7.0),
    (54, 31,  4.0),   # taper point toward the proboscis exit (upper-right)
)


def _amber_teardrop():
    """The resin drop: a body-hugging teardrop with a hot honey core. A
    metaball chain fuses into the smooth silhouette; the additive core blooms
    the overlap to white directly behind the thorax so it looks lit."""
    a = _new()
    for cx, cy, r in _TEAR_NODES:
        _aaellipse(a, (*AMBER, 236), (cx, cy), r, r)
    core = pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)
    for r, col, al in ((12, AMBER, 66), (9, HONEY, 88), (6, GLINT, 118),
                       (3, GLINT, 150)):
        _aaellipse(core, (*col, al), CORE, r, r)
    a.blit(core, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
    return a


def _wing(root, angle_deg, length, width):
    """One narrow, pointed wing as a leaf lens from a thorax root out to a tip
    along `angle_deg` (measured CCW from +x, up = negative y). Swept-back and
    honey-veined; the pair is the strongest 'mosquito, not man' cue."""
    a = math.radians(angle_deg)
    dx, dy = math.cos(a), -math.sin(a)
    px, py = -dy, dx                       # perpendicular for the lens bulge
    rx, ry = root
    tx, ty = rx + dx * length, ry + dy * length
    mx, my = rx + dx * length * 0.42, ry + dy * length * 0.42   # widest point
    poly = [(rx, ry), (mx + px * width, my + py * width),
            (tx, ty), (mx - px * width, my - py * width)]
    w = pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)
    pygame.draw.polygon(w, (*AMBER, 70), poly)
    pygame.draw.polygon(w, (*HONEY, 96), poly, 1)
    # A couple of honey veins running root→tip so it reads as a wing membrane.
    pygame.draw.line(w, (*HONEY, 78), (rx, ry), (tx, ty), 1)
    pygame.draw.line(w, (*HONEY, 60),
                     (mx + px * width * 0.4, my + py * width * 0.4),
                     (tx, ty), 1)
    return w


def build_mosquito_amber(wing_angle_deg):
    surf = _new()
    f = (wing_angle_deg + 40) / 90.0        # 0 down-stroke … 1 up-stroke
    sway = int(round((f - 0.5) * 3))         # frozen, so only a faint drift
    beat = (f - 0.5) * 16.0                   # wing rotation across the stroke

    # ── 1 · additive halo bleeding OUT of the drop into the sky, centred on the
    #        core so it glows evenly in every direction, not left-weighted ──────
    halo = pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)
    for r, col, al in ((28, AMBER, 15), (22, AMBER, 24), (16, HONEY, 30),
                       (11, HONEY, 40), (7, GLINT, 46)):
        _aaellipse(halo, (*col, al), CORE, r, r)
    surf.blit(halo, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

    # ── 2 · the amber teardrop (lit core) enclosing the whole fossil ──────────
    surf.blit(_amber_teardrop(), (0, 0))

    # ── 3 · two bubble glints suspended in the FIELD (off the body) ───────────
    for bx, by, br in ((26, 45, 2), (39, 53, 2)):
        pygame.draw.circle(surf, (*GLINT, 150), (bx, by), br)
        pygame.draw.circle(surf, (*AMBER, 130), (bx + 1, by + 1), max(1, br - 1))
        pygame.draw.circle(surf, (*GLINT, 190), (bx - 1, by - 1), 1)

    # ── 4 · swept-back wing PAIR fanned up-and-back over the body ──────────────
    # Forewing + hindwing rooted at the thorax, sweeping up-and-back at ~60–70°
    # above horizontal (angle ~118–130° CCW), tips punching past the top-left of
    # the drop. They rotate ±8° across the four frames for a real wingbeat.
    surf.blit(_wing((28, 28), 118 + beat, 26, 3.6), (0, 0))
    surf.blit(_wing((29, 29), 131 + beat, 22, 2.8), (0, 0))

    # ── 5 · legs — 3 thin filaments dangling straight DOWN ────────────────────
    # Near-parallel caramel filaments with a honey lit edge, minimal splay, feet
    # punching 6–10px past the drop's bottom so the dangle tell lives OUTSIDE
    # the amber. No X-cross stance.
    for (x0, y0), (kx, ky), (x1, y1) in (
        ((28, 40), (27, 54), (26 + sway, 68)),     # rear
        ((32, 42), (33, 55), (33 + sway, 70)),     # mid
        ((37, 43), (39, 54), (41 + sway, 67)),     # front
    ):
        pygame.draw.lines(surf, SEPIA, False, [(x0, y0), (kx, ky), (x1, y1)], 2)
        pygame.draw.lines(surf, (*HONEY, 200), False,
                          [(x0 - 1, y0), (kx - 1, ky), (x1 - 1, y1)], 1)
        pygame.draw.circle(surf, FOSSIL, (x1, y1), 1)

    # ── 6 · abdomen — dark segmented tail sweeping DOWN-RIGHT to the point ─────
    # Axis (31,35)→(51,59); the honey rim rides the upper contour that faces the
    # backlight, so fossil separates cleanly from the resin field.
    abdomen = [
        (36.4, 30.5), (41.6, 39.2), (46.5, 47.1), (49.9, 54.4), (51, 59),
        (46.1, 57.6), (39.5, 52.9), (32.4, 46.8), (25.6, 39.5),
    ]
    pygame.draw.polygon(surf, FOSSIL, abdomen)
    pygame.draw.lines(surf, (*HONEY, 200), False,
                      [(36.4, 30.5), (41.6, 39.2), (46.5, 47.1),
                       (49.9, 54.4), (51, 59)], 1)
    for (bx, by) in ((38, 41), (43, 48), (47, 54)):     # warm segment bands
        pygame.draw.line(surf, SEPIA, (bx + 3, by - 3), (bx - 3, by + 3), 1)

    # ── 7 · neck bridging thorax → head so the boomerang reads as one body ────
    _aaellipse(surf, FOSSIL, (37, 32), 6, 3)

    # ── 8 · thorax (dark fossil hump high on the upper-left, honey top rim) ────
    _aaellipse(surf, FOSSIL, (29, 30), 8, 6)
    pygame.draw.arc(surf, HONEY, (21, 23, 17, 14),
                    math.radians(45), math.radians(175), 2)
    _aaellipse(surf, FOSSIL, (30, 34), 6, 3)          # shaded underside

    # ── 9 · head + darkened compound eye with a catchlight ────────────────────
    _aaellipse(surf, FOSSIL, (HCX, HCY), 6, 6)
    pygame.draw.arc(surf, HONEY, (HCX - 6, HCY - 7, 12, 11),
                    math.radians(30), math.radians(150), 2)
    _aaellipse(surf, SEPIA, (HCX + 1, HCY), 4, 4)      # low-contrast eye
    _aaellipse(surf, FOSSIL, (HCX + 2, HCY + 1), 3, 3)
    pygame.draw.circle(surf, GLINT, (HCX - 1, HCY - 2), 1)   # eye catchlight

    # ── 10 · proboscis — the needle that MUST exit the amber ──────────────────
    # Dark shaft + honey highlight strike forward past the drop's point so an
    # unmistakable spike breaks the outline even at 40px.
    for py in (HCY + 2, HCY + 4):                      # two short palp stubs
        pygame.draw.line(surf, FOSSIL, (HCX + 3, py), (HCX + 8, py + 1), 1)
    pygame.draw.line(surf, FOSSIL, (HCX + 1, HCY + 1), (63, HCY - 2), 3)
    pygame.draw.line(surf, (*HONEY, 235), (HCX + 2, HCY), (62, HCY - 3), 1)

    return surf


build = _make_prebuilt_skin(build_mosquito_amber)
