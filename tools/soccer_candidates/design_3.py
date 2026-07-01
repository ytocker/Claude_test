"""JUVENTUS "LA VECCHIA SIGNORA" — Pip in the bianconeri kit (DESIGN 3 of SOCCER).

Scratch exploration only; NOT registered in store_skins.BUILDERS, so production
is untouched.

Architecture: the jersey IS the body. Rather than pasting a flat jersey polygon
over the scarlet macaw (which anchored to the head centre and skipped the belly),
this recolours the body oval WHITE through the palette system — `_pal` +
`_build_parrot_with_palette`. `_paint` then clips to the body oval and lays down
three equal-weight black bands, so the whole torso reads as Juve's black-and-
white stripes. Head stays macaw-red and wings stay macaw-blue so it still reads
as "a parrot in the bianconeri kit."
"""
import pygame

from game.store_skins import HX, HY, CROWN_Y, _poly, _make_skin
from game.dollar_parrot_ghost import _pal, _build_parrot_with_palette
from game.draw import (
    BIRD_RED, BIRD_BEAK, BIRD_BEAK_D, BIRD_WING, BIRD_WING_D, BIRD_TIP,
)

# The body oval is re-plumaged WHITE so the bianconeri stripes in _paint can sit
# on a bright field. Head stays macaw-red, wings stay macaw-blue so only the
# torso reads as the striped kit and the bird keeps its identity.
_PAL = _pal(
    tail=[(200, 30, 40), (240, 95, 40), (255, 160, 55), (255, 220, 80)],
    tail_line=(170, 25, 25),
    body_shadow=(195, 195, 205),
    body_main=(242, 242, 245),
    body_chest=(250, 250, 252),
    body_belly=(215, 215, 225),
    sheen=(255, 255, 255, 100),
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
    # BIANCONERI STRIPES — the whole "Juve" tell. Three 4px black bands spaced so
    # the white channels between them are the same width, so the torso reads as
    # true equal-weight black-and-white at 40px, not black-on-white. Clipped to
    # the body oval so the bands wrap the silhouette instead of spilling onto the
    # blue wings/sky; then a light-grey outline redefines the jersey edge the
    # wing-blue was eating into.
    clip_prev = surf.get_clip()
    surf.set_clip(pygame.Rect(BCX - 19, BCY - 14, 38, 28))
    for x in (BCX - 15, BCX - 7, BCX + 1):
        pygame.draw.rect(surf, (10, 10, 12), (x, BCY - 14, 4, 28))
    surf.set_clip(clip_prev)
    pygame.draw.ellipse(surf, (200, 200, 205), (BCX - 19, BCY - 14, 38, 28), 1)

    # COLLAR — a black crew-neck band right under the red head, so the striped
    # jersey reads as a collared shirt rather than a raw recolour edge.
    pygame.draw.line(surf, (10, 10, 12), (BCX - 8, BCY - 13), (BCX + 10, BCY - 13), 2)

    # BADGE — a single solid black dot with a white ring, sat in a white channel
    # so it survives the downscale as one crisp club mark instead of the pale
    # shield-smudge the R1 crest became at 40px.
    pygame.draw.circle(surf, (245, 245, 250), (BCX + 6, BCY - 6), 5)
    pygame.draw.circle(surf, (10, 10, 12), (BCX + 6, BCY - 6), 5, 1)
    pygame.draw.circle(surf, (10, 10, 12), (BCX + 6, BCY - 6), 4)

    # SHORTS — black to match Juve's away/short colour, with a lighter rim so
    # the leg-line stays crisp against the striped torso above.
    pygame.draw.ellipse(surf, (10, 10, 12), (BCX - 9, BCY + 7, 20, 9))
    pygame.draw.ellipse(surf, (28, 28, 36), (BCX - 9, BCY + 7, 20, 9), 1)

    # SOCKS — black shanks with a single white turn-over hoop, so the lower zone
    # keeps one bright value break above the near-black cleats.
    for sx in (27, 35):
        pygame.draw.line(surf, (10, 10, 12), (sx, BCY + 11), (sx, BCY + 16), 4)
        pygame.draw.line(surf, (242, 242, 245), (sx, BCY + 12), (sx, BCY + 13), 4)

    # CLEATS — near-black boots below the socks with a visible gap, so the kit
    # stack (shorts, socks, boots) stays legible at 40px.
    for cx in (23, 31):
        pygame.draw.rect(surf, (10, 10, 12), (cx, BCY + 14, 9, 5), border_radius=1)


build = _make_skin(_paint, base_fn=_base)
