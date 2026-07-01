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
    body_shadow=(6, 14, 40),
    body_main=(13, 32, 72),
    body_chest=(18, 44, 92),
    body_belly=(10, 26, 62),
    sheen=(50, 80, 150, 80),
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
    # Lighter-navy piping across the top of the recoloured jersey — the sole
    # collar cue, a single line so it never fights the crest for white pixels.
    pygame.draw.line(surf, (26, 56, 128), (BCX - 13, BCY - 8), (BCX + 13, BCY - 8), 1)

    # Club CREST on the left chest — a chunky white shield with one navy bar so
    # it survives the 40px downscale as a solid white read on the navy torso.
    shield = [(BCX - 10, BCY - 8), (BCX - 4, BCY - 8), (BCX - 4, BCY - 2),
              (BCX - 7, BCY + 1), (BCX - 10, BCY - 2)]
    _poly(surf, (255, 255, 255), shield)
    pygame.draw.line(surf, (13, 32, 72), (BCX - 7, BCY - 7), (BCX - 7, BCY - 2), 1)
    pygame.draw.polygon(surf, (13, 32, 72), shield, 1)

    # SHORTS — same deep navy as the body, a lighter-navy outline so they
    # separate from the recoloured torso above them.
    shorts = pygame.Rect(BCX - 10, BCY + 7, 22, 11)
    pygame.draw.ellipse(surf, (13, 32, 72), shorts)
    pygame.draw.ellipse(surf, (26, 56, 128), shorts, 1)

    # SOCKS — white body with a compressed navy DOUBLE-HOOP so clear white gaps
    # survive above and between the hoops before the near-black cleat, otherwise
    # the whole foot merges into one dark block at 40px.
    for sx in (27, 35):
        pygame.draw.line(surf, (255, 255, 255), (sx, BCY + 11), (sx, BCY + 17), 4)
        pygame.draw.line(surf, (13, 32, 72), (sx, BCY + 12), (sx, BCY + 13), 4)
        pygame.draw.line(surf, (13, 32, 72), (sx, BCY + 14), (sx, BCY + 15), 4)

    # CLEATS — near-black boots with a silver sole stripe along the bottom edge.
    for fx in (23, 31):
        pygame.draw.rect(surf, (28, 28, 36), (fx, BCY + 13, 9, 5), border_radius=1)
        pygame.draw.line(surf, (168, 168, 176),
                         (fx, BCY + 17), (fx + 8, BCY + 17), 1)

    # HERO PROP · CAPTAIN'S ARMBAND (drawn LAST) — a bold, wide white band
    # wrapping the near wing arm with a single gold spine. Brighter and wider
    # than any garment stripe, so it owns the "captain" read at 40px.
    ax, ay = BCX + 15, BCY - 3
    pygame.draw.line(surf, (207, 181, 59), (ax - 2, ay - 6), (ax + 4, ay + 6), 8)
    pygame.draw.line(surf, (255, 255, 255), (ax - 2, ay - 6), (ax + 4, ay + 6), 6)
    pygame.draw.line(surf, (180, 150, 40), (ax - 1, ay - 5), (ax + 3, ay + 5), 1)


build = _make_skin(_paint, base_fn=_base)
