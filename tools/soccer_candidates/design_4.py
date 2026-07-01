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
near-black so the ONE bright RED CARD — brandished high in clear sky to
the upper-right, isolated from the yellow beak — owns the eye and survives
the 40px downscale. A red rectangle against blue sky reads instantly with
no hue collision against the beak, and is the more iconic referee gesture.
White piping and one bold sock hoop are the only relief on the black; a
faint charcoal body rim holds the near-black silhouette on night sky.
Kit-first, hero card LAST.
"""
import math

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


_CARD_RED = (220, 40, 40)     # vivid referee red
_CARD_DARK = (80, 10, 10)     # dark border
_CARD_H = (255, 90, 90)       # left-edge highlight


def _paint(surf, _a):
    # ── BODY EDGE RIM — a faint charcoal ellipse traces the body oval so the
    #    near-black jersey silhouette still holds against a dark night-biome sky
    #    instead of dissolving into it. Drawn under the trim so seams sit on top.
    pygame.draw.ellipse(surf, (40, 40, 50), (BCX - 19, BCY - 14, 38, 28), 1)

    # ── JERSEY TRIM — thin white piping is the only relief on the black torso.
    #    Two collar lines at the head/body junction read as a referee's shirt
    #    yoke; a single sleeve-edge line on the trailing back gives the black
    #    body a seam so it never collapses into a void.
    pygame.draw.line(surf, (220, 220, 220), (BCX - 11, BCY - 9), (BCX + 11, BCY - 9), 1)
    pygame.draw.line(surf, (180, 180, 180), (BCX - 10, BCY - 7), (BCX + 10, BCY - 7), 1)
    pygame.draw.line(surf, (180, 180, 180), (BCX - 14, BCY - 6), (BCX - 12, BCY + 6), 1)

    # ── SHORTS — black ellipse over the lower body with a slightly lighter
    #    outline so the leg break separates from the torso.
    pygame.draw.ellipse(surf, (22, 22, 28), (BCX - 9, BCY + 7, 20, 9))
    pygame.draw.ellipse(surf, (36, 36, 44), (BCX - 9, BCY + 7, 20, 9), 1)

    # ── SOCKS — black legs, ONE bold white hoop at the top of each. A single
    #    hoop stays legible at the 40px downscale; a second stripe was noise.
    for sx in (27, 35):
        pygame.draw.line(surf, (14, 14, 18), (sx, BCY + 11), (sx, BCY + 17), 4)
        pygame.draw.line(surf, (220, 220, 220), (sx, BCY + 11), (sx, BCY + 14), 4)

    # ── CLEATS — clean dark boots; the sole stripe was too fine to hold at 40px.
    for fx in (23, 31):
        pygame.draw.rect(surf, (10, 10, 14), (fx, BCY + 14, 9, 5), border_radius=1)

    # ── HERO PROP · RED CARD — drawn LAST, brandished HIGH and RIGHT into fully
    #    open sky, far clear of the head and yellow beak. A tilted hard-edged red
    #    rectangle against blue sky reads instantly as a referee's send-off, with
    #    no hue collision, and survives the 40px downscale as the single hero.
    cx, cy = HX + 14, CROWN_Y - 20
    angle = math.radians(15)
    w2, h2 = 6, 8
    cos_a, sin_a = math.cos(angle), math.sin(angle)
    corners = [
        (cx + w2 * cos_a - h2 * sin_a, cy + w2 * sin_a + h2 * cos_a),
        (cx - w2 * cos_a - h2 * sin_a, cy - w2 * sin_a + h2 * cos_a),
        (cx - w2 * cos_a + h2 * sin_a, cy - w2 * sin_a - h2 * cos_a),
        (cx + w2 * cos_a + h2 * sin_a, cy + w2 * sin_a - h2 * cos_a),
    ]
    corners_int = [(int(x), int(y)) for x, y in corners]
    _poly(surf, _CARD_DARK, [(int(x + 1), int(y + 1)) for x, y in corners])  # drop shadow
    _poly(surf, _CARD_RED, corners_int)                                       # card face
    pygame.draw.polygon(surf, _CARD_DARK, corners_int, 1)                     # crisp border
    pygame.draw.line(surf, _CARD_H, corners_int[1], corners_int[2], 1)        # left-edge highlight
    # Dark grip block — reads as the hand holding the card aloft at its base.
    grip_x = int((corners_int[0][0] + corners_int[3][0]) / 2)
    grip_y = int((corners_int[0][1] + corners_int[3][1]) / 2)
    pygame.draw.rect(surf, (30, 30, 30), (grip_x - 4, grip_y, 8, 4))


build = _make_skin(_paint, base_fn=_base)
