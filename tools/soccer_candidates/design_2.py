"""SOCCER — THE GOALKEEPER (DESIGN 2 of the SOCCER set).

Scratch exploration only; NOT registered in store_skins.BUILDERS, so production
is untouched.

Concept: the jersey IS the body. Instead of stapling a flat polygon shirt over
the scarlet macaw (which only ever covered the head-side of the torso and left
the belly bare), this recolours the whole body oval through the palette system
the ninja/cockatoo skins use — HV neon keeper green from chest to belly, with a
darker green shade for roundness and a bright sheen. The head stays macaw-red and
the wings stay macaw-blue so Pip is still recognisably himself, just kitted out.

Over that recoloured torso the _paint pass lays a deliberately minimal keeper
kit — a faint green collar, a clean charcoal shorts ellipse, two yellow cleat
dots — and, drawn LAST so nothing dulls them, the hero prop: a PAIR of hard,
outlined SAFETY-ORANGE keeper mitts with white wrist straps, staggered so both
read in side profile. Safety orange (#FF6A00) is chosen to stay distinct from
the macaw's natural tail orange, so the gloves read as gear, not feathers. At
40px the order of value is (1) the two bright outlined mitts (the unmistakable
keeper tell), (2) the neon green torso mass, (3) the yellow boots. The orange
gloves and yellow boots are warm notes that pop off the cool green on both day
and night skies.
"""
import pygame

from game.store_skins import HX, HY, CROWN_Y, _poly, _make_skin
from game.dollar_parrot_ghost import _pal, _build_parrot_with_palette
from game.draw import BIRD_RED, BIRD_BEAK, BIRD_BEAK_D, BIRD_WING, BIRD_WING_D, BIRD_TIP


# Keeper kit — the body oval is recoloured to the neon-green jersey; the head is
# kept macaw-red so Pip stays recognisable under the kit.
_PAL = _pal(
    tail=[(200, 30, 40), (240, 95, 40), (255, 160, 55), (255, 220, 80)],
    tail_line=(170, 25, 25),
    body_shadow=(20, 130, 42),      # jersey drop-shade for roundness
    body_main=(57, 211, 83),        # #39D353 neon keeper green
    body_chest=(80, 230, 105),      # lit upper chest
    body_belly=(38, 178, 66),       # shaded lower belly
    sheen=(120, 255, 160, 110),     # bright jersey sheen band
    wing_main=BIRD_WING,            # keep macaw-blue wings
    wing_dark=BIRD_WING_D,
    wing_tip=BIRD_TIP,
    wing_secondary=(255, 200, 60),
    wing_highlight=(170, 210, 255),
    head_shadow=(150, 15, 20),      # keep macaw-red head
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

# Body centre in COMPOSITE space (base body centre (32,32) + PARROT_DY 20 on y).
BCX, BCY = 32, 52

_COLLAR   = (25, 140, 50)      # subtle dark-green shirt neckline
_SHT      = (42, 42, 42)       # #2A2A2A charcoal shorts
_SHT_D    = (28, 28, 28)       # shorts outline
_CLT      = (232, 192, 32)     # #E8C020 yellow cleats
_CLT_D    = (140, 115, 15)     # cleat outline

# Hero-prop glove palette. Safety orange keeps the mitts distinct from the
# macaw's natural tail orange so the pair reads as gear, not feathers.
_GLV_ORANGE = (255, 106, 0)    # safety orange — HOT, off the macaw tail orange
_GLV_DARK   = (140, 48, 0)     # dark glove outline / shadow
_GLV_STRAP  = (240, 240, 240)  # white wrist strap


def _base(angle_deg):
    return _build_parrot_with_palette(angle_deg, _PAL)


def _paint(surf, _a):
    # ── GREEN COLLAR — a single subtle line so the recoloured torso reads as a
    #    shirt neckline rather than bare feathers. Kept faint on purpose.
    pygame.draw.line(surf, _COLLAR, (BCX - 5, BCY - 11), (BCX + 11, BCY - 11), 1)

    # ── SHORTS — one clean charcoal ellipse. The lower kit is deliberately
    #    minimal (no sock hoop) so it doesn't collapse to mud at 40px.
    pygame.draw.ellipse(surf, _SHT, (BCX - 9, BCY + 7, 20, 9))
    pygame.draw.ellipse(surf, _SHT_D, (BCX - 9, BCY + 7, 20, 9), 1)

    # ── CLEATS — two small bright dots are the only lower-body value pop.
    for fx in (23, 31):
        pygame.draw.rect(surf, _CLT, (fx, BCY + 14, 9, 4), border_radius=1)
        pygame.draw.rect(surf, _CLT_D, (fx, BCY + 14, 9, 4), border_radius=1, width=1)

    # ── GOALKEEPER GLOVES (HERO PROP, drawn LAST so nothing dulls them) — hard
    #    rectangular safety-orange mitts with a dark outline and a white wrist
    #    strap, staggered so BOTH read as a pair in side profile. The near mitt
    #    is larger and forward; the far mitt sits smaller and behind for depth.
    gx1, gy1 = BCX + 11, BCY - 8
    pygame.draw.rect(surf, _GLV_DARK,   (gx1 - 1, gy1 - 1, 16, 14), border_radius=3)
    pygame.draw.rect(surf, _GLV_ORANGE, (gx1,     gy1,     14, 12), border_radius=3)
    pygame.draw.rect(surf, _GLV_DARK,   (gx1,     gy1,     14, 12), border_radius=3, width=1)
    pygame.draw.line(surf, _GLV_STRAP,  (gx1 + 1, gy1 + 9), (gx1 + 13, gy1 + 9), 2)
    pygame.draw.line(surf, _GLV_ORANGE, (gx1 + 2, gy1 + 1), (gx1 + 12, gy1 + 1), 2)

    gx2, gy2 = BCX - 24, BCY - 6
    pygame.draw.rect(surf, _GLV_DARK,   (gx2 - 1, gy2 - 1, 14, 12), border_radius=3)
    pygame.draw.rect(surf, _GLV_ORANGE, (gx2,     gy2,     12, 10), border_radius=3)
    pygame.draw.rect(surf, _GLV_DARK,   (gx2,     gy2,     12, 10), border_radius=3, width=1)
    pygame.draw.line(surf, _GLV_STRAP,  (gx2 + 1, gy2 + 7), (gx2 + 11, gy2 + 7), 2)


build = _make_skin(_paint, base_fn=_base)
