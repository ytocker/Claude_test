"""MOSQUITO redesign — design_2 AMBER RELIC (legendary showpiece).

A mosquito caught mid-strike and frozen inside a lit teardrop of amber. The
selling idea is a warm gemstone glowing from within — but the two things that
make it read MOSQUITO (a forward proboscis and dangling legs) deliberately
break OUT of the amber so the silhouette survives the 40px gameplay shrink
against pale day sky. The resin hugs the body like a teardrop rather than
swallowing it in an opaque pill, and a hot honey core blooms behind the thorax
so the jewel looks lit, not like dark set resin.

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


def _rot_blit(surf, s, anchor):
    surf.blit(s, s.get_rect(center=anchor).topleft)


# Teardrop axis: rounded rear at lower-left (abdomen), tapering to a point at
# upper-right toward the proboscis. Radii bulge just behind the thorax so the
# resin reads as a body-hugging drop, not a level pill.
_TEAR_A = (22.0, 52.0)
_TEAR_B = (53.0, 30.0)
_TEAR_CHAIN = (
    (0.00, 9.0), (0.15, 11.0), (0.30, 11.0), (0.45, 9.4),
    (0.58, 7.4), (0.72, 5.0), (0.85, 3.0), (1.00, 1.0),
)


def _tear_nodes():
    ax, ay = _TEAR_A
    bx, by = _TEAR_B
    return [((ax + (bx - ax) * t, ay + (by - ay) * t), r) for t, r in _TEAR_CHAIN]


def _amber_teardrop():
    """The resin drop itself: an opaque-ish honey-cored teardrop that hugs the
    body. A metaball chain gives the drop shape; a hot core blooms behind the
    thorax so it looks lit from within instead of like flat brown resin."""
    a = _new()
    nodes = _tear_nodes()
    # Fill pass — overlapping circles fuse into a smooth teardrop silhouette.
    for (cx, cy), r in nodes:
        _aaellipse(a, (*AMBER, 236), (cx, cy), r, r)
    # Hot core behind the thorax — additive so the overlaps bloom to white.
    core = pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)
    for r, col, al in ((11, AMBER, 70), (8, HONEY, 90), (5, GLINT, 120),
                       (3, GLINT, 150)):
        _aaellipse(core, (*col, al), (35, 42), r, int(r * 0.82))
    a.blit(core, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
    return a


def _ghost_wing():
    """A single swept-back translucent forewing angled up-and-back — replaces
    the old raking streak that read as a scratch. Gold-veined, low alpha, so it
    frames the glow without competing with the silhouette."""
    poly = [(36, 38), (29, 31), (21, 24), (15, 19),
            (19, 26), (27, 34), (34, 41)]
    w = pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)
    pygame.draw.polygon(w, (*AMBER, 66), poly)
    pygame.draw.polygon(w, (*HONEY, 90), poly, 1)
    for a, b in (((33, 39), (17, 21)), ((30, 41), (20, 26))):
        pygame.draw.line(w, (*HONEY, 70), a, b, 1)
    return w


def build_mosquito_amber(wing_angle_deg):
    surf = _new()
    f = (wing_angle_deg + 40) / 90.0        # 0 down-stroke … 1 up-stroke
    sway = int(round((f - 0.5) * 3))         # frozen, so only a faint drift

    # ── 1 · additive halo bleeding OUT of the drop into the sky ───────────────
    # Warm haze past the resin edge, so the jewel glows against the cool sky.
    halo = pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)
    for r, col, al in ((26, AMBER, 16), (21, AMBER, 24), (16, HONEY, 30),
                       (11, HONEY, 40), (7, GLINT, 46)):
        _aaellipse(halo, (*col, al), (34, 42), r, int(r * 1.18))
    surf.blit(halo, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

    # ── 2 · the amber teardrop (lit core) ─────────────────────────────────────
    surf.blit(_amber_teardrop(), (0, 0))

    # ── 3 · two bubble glints suspended in the FIELD (off the body) ───────────
    # Curved to follow the drop; low opacity so they never rival the eye.
    for bx, by, br in ((47, 46, 2), (26, 55, 2)):
        pygame.draw.circle(surf, (*GLINT, 150), (bx, by), br)
        pygame.draw.circle(surf, (*AMBER, 130), (bx + 1, by + 1), max(1, br - 1))
        pygame.draw.circle(surf, (*GLINT, 190), (bx - 1, by - 1), 1)

    # ── 4 · swept-back ghost wing (behind the body) ───────────────────────────
    surf.blit(_ghost_wing(), (0, 0))

    # ── 5 · legs — 3 dark filaments hanging BELOW the resin ───────────────────
    # Caramel core with a honey lit edge; feet punch 6–10px past the drop's
    # bottom so the dangle tell lives OUTSIDE the amber.
    for (x0, y0), (kx, ky), (x1, y1) in (
        ((37, 47), (41, 58), (44 + sway, 68)),     # front
        ((32, 49), (30, 60), (27 + sway, 70)),     # mid
        ((30, 48), (24, 58), (19 + sway, 67)),     # rear
    ):
        pygame.draw.lines(surf, SEPIA, False, [(x0, y0), (kx, ky), (x1, y1)], 2)
        pygame.draw.lines(surf, (*HONEY, 210), False,
                          [(x0 - 1, y0 - 1), (kx - 1, ky - 1), (x1 - 1, y1 - 1)], 1)
        pygame.draw.circle(surf, FOSSIL, (x1, y1), 1)

    # ── 6 · thorax (dark fossil hump, honey top rim, dark underside) ──────────
    _aaellipse(surf, FOSSIL, (35, 40), 8, 6)
    pygame.draw.arc(surf, HONEY, (27, 32, 17, 14),
                    math.radians(30), math.radians(150), 2)
    _aaellipse(surf, FOSSIL, (35, 43), 6, 3)          # deepen the shaded belly

    # ── 7 · abdomen (tapering dark tail toward the rounded rear) ──────────────
    abdomen = [
        (35, 39), (38, 43), (30, 54), (24, 60),
        (21, 57), (27, 48), (31, 41),
    ]
    pygame.draw.polygon(surf, FOSSIL, abdomen)
    # Single honey rim along the top edge separates fossil from the resin.
    pygame.draw.lines(surf, (*HONEY, 205), False,
                      [(35, 39), (31, 45), (26, 52), (22, 57)], 1)
    for bx, by in ((30, 49), (26, 54)):               # faint warm segment bands
        pygame.draw.line(surf, SEPIA, (bx + 2, by - 1), (bx - 2, by + 1), 1)

    # ── 8 · head + darkened eye with a single catchlight ──────────────────────
    _aaellipse(surf, FOSSIL, (HCX, HCY), 6, 6)
    pygame.draw.arc(surf, HONEY, (HCX - 6, HCY - 7, 12, 11),
                    math.radians(35), math.radians(155), 2)
    _aaellipse(surf, SEPIA, (HCX + 1, HCY), 4, 4)      # low-contrast compound eye
    _aaellipse(surf, FOSSIL, (HCX + 2, HCY + 1), 3, 3)
    pygame.draw.circle(surf, GLINT, (HCX - 1, HCY - 2), 1)   # eye catchlight

    # ── 9 · proboscis — the needle that MUST exit the amber ───────────────────
    # Dark shaft + honey highlight strike forward ~10px past the drop's point,
    # so an unmistakable spike breaks the outline even at 40px.
    for py in (HCY + 2, HCY + 4):                      # two short palp stubs
        pygame.draw.line(surf, FOSSIL, (HCX + 3, py), (HCX + 8, py + 1), 1)
    pygame.draw.line(surf, FOSSIL, (HCX + 1, HCY + 1), (63, HCY - 2), 3)
    pygame.draw.line(surf, (*HONEY, 235), (HCX + 2, HCY), (62, HCY - 3), 1)

    return surf


build = _make_prebuilt_skin(build_mosquito_amber)
