"""THE CAPTAIN — Pip as a soccer team captain (DESIGN 3 of the SOCCER set).

Scratch exploration only; NOT registered in store_skins.BUILDERS, so production
is untouched.

Architecture: the jersey IS the body. Rather than pasting a flat jersey polygon
over the scarlet macaw (which anchored to the head centre and skipped the belly),
this recolours the body oval through the palette system — `_pal` + the
`_build_parrot_with_palette` builder used for the ghost variants. The whole torso
mass reads as a deep-navy kit, while the head stays macaw-red and the wings stay
macaw-blue so it still reads as "a parrot dressed as a captain."

`_paint` then overlays only the garment detail that can't be a body recolour —
white club crest, shorts, hooped socks, near-black cleats, and the HERO PROP: a
wide white captain's armband with a gold spine on the near wing, the brightest,
widest mark on the sprite so it owns the "captain" read at 40px.
"""
import pygame

from game.store_skins import HX, HY, CROWN_Y, _poly, _make_skin
from game.dollar_parrot_ghost import _pal, _build_parrot_with_palette
from game.draw import (
    BIRD_RED, BIRD_BEAK, BIRD_BEAK_D, BIRD_WING, BIRD_WING_D, BIRD_TIP,
)

# Kit navy is the body palette — jersey, chest and belly are all one dark mass,
# shaded so the recoloured torso still reads as a rounded body under the wing.
_PAL = _pal(
    tail=[(200, 30, 40), (240, 95, 40), (255, 160, 55), (255, 220, 80)],
    tail_line=(170, 25, 25),
    body_shadow=(4, 10, 30),
    body_main=(10, 26, 62),
    body_chest=(14, 36, 78),
    body_belly=(8, 20, 52),
    sheen=(40, 65, 120, 70),
    wing_main=BIRD_WING,
    wing_dark=BIRD_WING_D,
    wing_tip=BIRD_TIP,
    wing_secondary=(255, 200, 60),
    wing_highlight=(170, 210, 255),
    head_shadow=(150, 15, 20),
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

# Body centre in COMPOSITE space — the palette builder draws the body oval at
# native (32, 32); +PARROT_DY (20) on y lands it at the composite anchor.
BCX, BCY = 32, 52


def _base(angle_deg):
    return _build_parrot_with_palette(angle_deg, _PAL)


def _paint(surf, _a):
    # WING-BODY SEAM PIPING — the critical VALUE BREAK. With the jersey and the
    # macaw-blue wing both dark, a bright white line down the wing root is what
    # keeps the two masses from fusing into one silhouette at 40px.
    pygame.draw.line(surf, (200, 200, 200), (BCX + 9, BCY - 12), (BCX + 16, BCY - 4), 2)
    pygame.draw.line(surf, (200, 200, 200), (BCX - 9, BCY - 12), (BCX - 16, BCY - 4), 1)

    # Club CREST — a hard-edged white shield with a navy keyline and a vertical
    # bar device. Geometric so it survives the downscale as a crisp emblem, not
    # a soft smudge, on the deep-navy torso.
    crest_x, crest_y = BCX - 8, BCY - 8
    shield = [(crest_x - 4, crest_y - 4), (crest_x + 4, crest_y - 4),
              (crest_x + 4, crest_y + 2), (crest_x, crest_y + 5),
              (crest_x - 4, crest_y + 2)]
    _poly(surf, (240, 240, 240), shield)
    pygame.draw.polygon(surf, (10, 26, 62), shield, 1)
    pygame.draw.line(surf, (10, 26, 62),
                     (crest_x, crest_y - 4), (crest_x, crest_y + 5), 1)

    # SHORTS — a fraction lighter than the body so there is a 1px value tick
    # between torso and kit; the socks below carry the real light break.
    _SHT = (18, 42, 90)
    pygame.draw.ellipse(surf, _SHT, (BCX - 9, BCY + 7, 20, 9))
    pygame.draw.ellipse(surf, (28, 58, 120), (BCX - 9, BCY + 7, 20, 9), 1)

    # SOCKS — the only light value in the lower zone, so they must be BOLD: a
    # thick white hoop split by a navy double-hoop keeps clear white gaps above
    # the near-black cleats instead of a single dark clump.
    for sx in (27, 35):
        pygame.draw.line(surf, (240, 240, 245), (sx, BCY + 11), (sx, BCY + 16), 4)
        pygame.draw.line(surf, (10, 26, 62), (sx, BCY + 12), (sx, BCY + 13), 4)
        pygame.draw.line(surf, (10, 26, 62), (sx, BCY + 14), (sx, BCY + 15), 4)

    # CLEATS — near-black boots with a silver sole stripe along the bottom edge.
    for fx in (23, 31):
        pygame.draw.rect(surf, (28, 28, 36), (fx, BCY + 14, 9, 5), border_radius=1)
        pygame.draw.line(surf, (160, 162, 170),
                         (fx + 1, BCY + 18), (fx + 8, BCY + 18), 1)

    # HERO PROP · CAPTAIN'S ARMBAND (drawn LAST) — the whole "captain" tell. Sat
    # further out on the near wing against open sky, wide with a hard dark border
    # so the bright white band + gold spine own the read even at 40px.
    _ARM_W = (248, 248, 248)
    _ARM_G = (200, 165, 40)
    _ARM_D = (30, 25, 10)
    ax, ay = BCX + 17, BCY - 12
    _poly(surf, _ARM_D, [(ax - 5, ay - 8), (ax + 7, ay - 8),
                         (ax + 7, ay + 8), (ax - 5, ay + 8)])
    _poly(surf, _ARM_W, [(ax - 4, ay - 7), (ax + 6, ay - 7),
                         (ax + 6, ay + 6), (ax - 4, ay + 6)])
    pygame.draw.line(surf, _ARM_G, (ax - 4, ay - 1), (ax + 6, ay - 1), 2)
    pygame.draw.rect(surf, _ARM_D, (ax - 5, ay - 8, 13, 17), 1)


build = _make_skin(_paint, base_fn=_base)
