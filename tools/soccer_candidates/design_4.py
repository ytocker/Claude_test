"""Soccer v9 Design 4 — NETHERLANDS "ORANJE" (body-recolor approach).

Same STRIKER anatomy as design_1, but the jersey IS the body: the macaw's
torso oval is re-plumaged brilliant Dutch orange through the palette system,
while the head stays macaw-red and the wings/beak stay macaw. On top of that
orange field the _paint pass lays the Oranje kit — a black neck collar band
that separates the orange body from the red head, a crew collar, a large white
KNVB badge disc, black shorts, orange hooped socks, and near-black cleats. No
chest stripe: the orange field is strong enough alone, and a wide black band
plus the collar was tipping the lower body too dark at 40px.

The single most important detail is the 4px black neck band at BCY-13: it
divides the scarlet macaw head from the orange jersey so the two warm tones
never fuse into one muddy mass at 40px.
"""
import pygame

from game.store_skins import HX, HY, CROWN_Y, _poly, _make_skin
from game.dollar_parrot_ghost import _pal, _build_parrot_with_palette
from game.draw import (
    BIRD_RED, BIRD_BEAK, BIRD_BEAK_D, BIRD_WING, BIRD_WING_D, BIRD_TIP,
)

# ── kit trim colours (drawn in _paint, over the orange body) ──────────────────
_BLACK    = ( 10,  10,  12)   # #0A0A0C KNVB black trim — collar, band, shorts
_SHORT_R  = ( 28,  28,  36)   # #1C1C24 shorts rim / cleat body
_ORANGE   = (243, 108,  33)   # #F36C21 brilliant Dutch orange — sock field
_WHITE    = (245, 245, 250)   # crest white
_AMBER    = (180,  60,   8)   # #B43C08 deep amber — oval border (no black noise)

# The body oval is re-plumaged ORANGE so the jersey IS the body colour. Head
# stays macaw-red, wings/beak stay macaw — so only the torso reads as the
# Oranje kit and the bird keeps its scarlet-macaw identity.
_PAL = _pal(
    tail=[(200, 30, 40), (240, 95, 40), (255, 160, 55), (255, 220, 80)],
    tail_line=(170, 25, 25),
    body_shadow=(185, 72, 12),        # jersey back-half shade (rounds torso)
    body_main=(243, 108, 33),         # brilliant Dutch orange field
    body_chest=(255, 125, 45),        # lit chest
    body_belly=(215, 88, 18),         # cooler belly
    sheen=(255, 160, 80, 70),
    wing_main=BIRD_WING,              # keep macaw-blue wings
    wing_dark=BIRD_WING_D,
    wing_tip=BIRD_TIP,
    wing_secondary=(255, 200, 60),
    wing_highlight=(170, 210, 255),
    head_shadow=(150, 15, 20),        # keep macaw-red head
    head_main=BIRD_RED,
    head_cheek=(255, 130, 130),
    head_crown=(255, 170, 170),
    lens_frame=(255, 200, 50),
    lens_body=(20, 20, 30),
    lens_tint=(35, 55, 90, 130),
    lens_glint=(255, 255, 255),
    beak_main=BIRD_BEAK,
    beak_dark=BIRD_BEAK_D,
    beak_gloss=(255, 230, 150),
    foot=BIRD_BEAK_D,
)

# Body centre in COMPOSITE space (sprite body centre (32,32) + PARROT_DY=20).
BCX, BCY = 32, 52


def _base(angle_deg):
    return _build_parrot_with_palette(angle_deg, _PAL)


def _paint(surf, _a):
    # All geometry here is in COMPOSITE space (the 64×100 canvas). The body is
    # already brilliant orange from _base, so the trim below is what turns the
    # recolor into the Oranje kit.

    # Deep-amber oval border — anchors the orange field so the bright jersey
    # holds its silhouette against the sky. A darker orange (not black) keeps
    # the edge crisp without dropping black noise onto the warm identity.
    pygame.draw.ellipse(surf, _AMBER, (BCX - 19, BCY - 14, 38, 28), 1)

    # NECK COLLAR SEPARATION — the load-bearing detail. A fat 4px black band at
    # the neck splits the scarlet macaw head from the orange jersey so the two
    # warm tones never fuse into one muddy mass at 40px.
    pygame.draw.line(surf, _BLACK, (BCX - 9, BCY - 13), (BCX + 11, BCY - 13), 4)

    # Crew collar — a thinner black line just below the separation band, so the
    # jersey reads as a collared shirt rather than a bare orange belly.
    pygame.draw.line(surf, _BLACK, (BCX - 7, BCY - 12), (BCX + 9, BCY - 12), 3)

    # KNVB badge — a single large white disc with one dark core, sized to survive
    # the 40px downscale. The fine white+black+white layering read as a random
    # pixel before; a fat 6px disc reads unambiguously as a chest badge dot.
    pygame.draw.circle(surf, _WHITE, (BCX + 6, BCY - 6), 6)
    pygame.draw.circle(surf, _BLACK, (BCX + 6, BCY - 6), 2)

    # Black shorts with a lighter rim so the leg-line stays crisp under the
    # orange torso.
    pygame.draw.ellipse(surf, _BLACK, (BCX - 9, BCY + 7, 20, 9))
    pygame.draw.ellipse(surf, _SHORT_R, (BCX - 9, BCY + 7, 20, 9), 1)

    # Socks — a clean 4px orange shank per leg with one 2px black turn-over
    # hoop. Kept deliberately flat: extra layers only read as noise at 40px.
    for sx in (27, 35):
        pygame.draw.line(surf, _ORANGE, (sx, BCY + 11), (sx, BCY + 16), 4)
        pygame.draw.line(surf, _BLACK, (sx, BCY + 12), (sx, BCY + 13), 2)

    # Cleats — near-black boots below the socks with a visible gap.
    for cx in (23, 31):
        pygame.draw.rect(surf, _SHORT_R, (cx, BCY + 14, 9, 5), border_radius=1)


build = _make_skin(_paint, base_fn=_base)
