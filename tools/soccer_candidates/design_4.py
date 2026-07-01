"""DESIGN 4 — THE REFEREE (Soccer / Football, v7).

Scratch exploration only — NOT registered in store_skins.BUILDERS, so
production stays untouched. Pip the scarlet macaw kitted as a soccer
REFEREE — but built the RIGHT way: the jersey IS the body colour. Instead
of anchoring a flat jersey polygon to the head centre (which missed the
belly and floated over the torso), the whole body oval is recoloured
near-black through the ghost-parrot palette system, so the kit fills the
real silhouette. Head stays macaw-red, wings stay macaw-blue, so Pip is
still unmistakably Pip in an authority strip.

Value is deliberately inverted from the player kits: the uniform is
near-black so the ONE bright YELLOW CARD — brandished high in clear sky
above the head, isolated from the yellow beak — owns the eye and survives
the 40px downscale. White piping, a bold sock hoop, and a white cleat sole
are the only relief on the black. Kit-first, hero card LAST.
"""
import pygame

from game.store_skins import HX, HY, CROWN_Y, _poly, _make_skin
from game.dollar_parrot_ghost import _pal, _build_parrot_with_palette
from game.draw import (
    BIRD_RED, BIRD_BEAK, BIRD_BEAK_D, BIRD_WING, BIRD_WING_D, BIRD_TIP,
)

# The referee strip lives in the palette: the body oval is repainted near-black
# with internal value steps (shadow < belly < main < chest) so the black torso
# still reads as a rounded form and never a flat void at 40px. Head/wings keep
# the macaw palette so Pip stays recognisable inside the authority kit.
_PAL = _pal(
    tail=[(200, 30, 40), (240, 95, 40), (255, 160, 55), (255, 220, 80)],
    tail_line=(170, 25, 25),
    body_shadow=(6, 6, 8),
    body_main=(16, 16, 20),
    body_chest=(24, 24, 28),
    body_belly=(12, 12, 16),
    sheen=(50, 50, 65, 80),
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

# Body centre in COMPOSITE space (base body centre 32,32 + PARROT_DY 20 on y).
BCX, BCY = 32, 52


def _base(angle_deg):
    return _build_parrot_with_palette(angle_deg, _PAL)


def _paint(surf, _a):
    # ── JERSEY TRIM — thin white piping is the only relief on the black torso.
    #    Two collar lines at the head/body junction read as a referee's shirt
    #    yoke; a single sleeve-edge line on the trailing back gives the black
    #    body a seam so it never collapses into a void.
    pygame.draw.line(surf, (240, 240, 240), (BCX - 11, BCY - 9), (BCX + 11, BCY - 9), 1)
    pygame.draw.line(surf, (200, 200, 200), (BCX - 10, BCY - 7), (BCX + 10, BCY - 7), 1)
    pygame.draw.line(surf, (200, 200, 200), (BCX - 14, BCY - 6), (BCX - 12, BCY + 6), 1)

    # ── SHORTS — very dark ellipse over the lower body, a hair darker than the
    #    jersey with a faint outline so the leg break separates from the torso.
    pygame.draw.ellipse(surf, (12, 12, 14), (BCX - 10, BCY + 7, 22, 11))
    pygame.draw.ellipse(surf, (28, 28, 32), (BCX - 10, BCY + 7, 22, 11), 1)

    # ── SOCKS — black legs with a bold white hoop thick enough to survive the
    #    40px downscale, at both shins.
    for sx in (27, 35):
        pygame.draw.line(surf, (20, 20, 20), (sx, BCY + 11), (sx, BCY + 17), 4)
        pygame.draw.line(surf, (224, 224, 224), (sx, BCY + 12), (sx, BCY + 15), 4)

    # ── CLEATS — black boots with a bold white sole stripe at each foot.
    for fx in (23, 31):
        pygame.draw.rect(surf, (16, 16, 16), (fx, BCY + 13, 9, 5))
        pygame.draw.line(surf, (224, 224, 224), (fx, BCY + 17), (fx + 8, BCY + 17), 2)

    # ── HERO PROP · YELLOW CARD — drawn LAST, brandished HIGH in clear sky to
    #    the upper-right of the head so it never fuses with the yellow beak.
    #    Isolation against open sky is what makes the card the unmistakable
    #    hero read at the 40px downscale.
    cx, cy = HX + 10, CROWN_Y - 14
    pygame.draw.rect(surf, (244, 215, 25), (cx, cy, 11, 15))               # card face
    pygame.draw.rect(surf, (80, 68, 0),    (cx, cy, 11, 15), 1)            # dark border
    pygame.draw.line(surf, (255, 240, 80), (cx + 1, cy + 1), (cx + 2, cy + 1), 1)  # glint
    # Dark grip/hand block at the card base — reads as the parrot holding it aloft.
    pygame.draw.rect(surf, (30, 30, 30), (cx + 1, cy + 12, 8, 4))


build = _make_skin(_paint, base_fn=_base)
