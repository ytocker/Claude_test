"""PHARAOH store-skin exploration — DESIGN 2: ANUBIS, the jackal god of the dead.

Scratch candidate only. Mirrors the production skin contract via
``store_skins._make_skin`` but is NOT registered in ``store_skins.BUILDERS``.

The hero is the pointed-ear silhouette over a jackal-black body: on a bright
day sky the black reads as a hard cut-out, and on night the gold ear-lining +
collar + ankh carry it. Every body-worn element (collar, was-scepter, ankh,
anklets, recolor) stays INSIDE the base bird footprint so the figure never
reads bigger than its fixed ~10px hitbox — only the tall ears rise above the
crown.
"""
import math
import pygame

from game import store_skins
from game.store_skins import HX, HY, CROWN_Y, _poly
from game.dollar_parrot_ghost import _pal, _build_parrot_with_palette


# Jackal-black re-plumage with a faint blue-black sheen. Three near-black values
# (shadow / main / a lifted blue-black) keep the dark mass from collapsing into
# a flat void on a night sky; the beak goes dark so no warm gold survives, and
# lenses are dropped so the painted almond eye + kohl flick own the face.
_AN_BLACK   = (14, 14, 20)         # #0E0E14 jackal black
_AN_SHEEN   = (26, 34, 56)         # #1A2238 blue-black sheen (value lift)
_AN_GOLD    = (232, 181, 58)       # #E8B53A gold
_AN_GOLD_D  = (168, 124, 30)
_AN_GOLD_H  = (255, 226, 140)
_AN_IVORY   = (245, 240, 230)      # #F5F0E6 ankh ivory
_AN_KOHL    = (8, 8, 12)           # deepest snout/kohl shadow

_AN_BODY = _pal(
    tail=[(11, 11, 16), (16, 18, 26), (22, 26, 40), (30, 36, 56)],
    tail_line=(6, 6, 10),
    body_shadow=(9, 9, 14),
    body_main=_AN_BLACK,
    body_chest=(24, 28, 44),
    body_belly=(18, 20, 32),
    sheen=(70, 90, 140, 60),       # cool blue-black gloss across the breast
    wing_main=(13, 14, 22),
    wing_dark=(7, 7, 11),
    wing_tip=(34, 40, 60),
    wing_secondary=None,
    wing_highlight=_AN_SHEEN,
    head_shadow=(9, 9, 14),
    head_main=_AN_BLACK,
    head_cheek=(22, 26, 40),
    head_crown=(26, 30, 46),
    lens_frame=(20, 22, 32),
    lens_body=(7, 7, 11),
    lens_tint=None,
    lens_glint=None,
    beak_main=(28, 30, 42),
    beak_dark=(8, 8, 12),
    beak_gloss=(54, 60, 82),
    foot=(18, 20, 30),
)


def _an_base(angle_deg):
    # Jackal-black bird, no aviators — the painted gold-rimmed eye + kohl flick
    # own the face below the ears.
    return _build_parrot_with_palette(angle_deg, _AN_BODY, draw_lenses=False)


def _ear(surf, base_x, tip_x, base_y, tip_y, half_w):
    """One tall erect jackal ear: a near-black blade rising straight up with a
    thin gold inner lining so it reads against a night sky. The black mass is
    the hero silhouette; the gold is only an inner sliver so the day cut-out
    stays a hard point, not a gold lollipop."""
    outer = [(base_x - half_w, base_y), (base_x + half_w, base_y), (tip_x, tip_y)]
    _poly(surf, _AN_KOHL, [(x, y) for x, y in outer])           # crisp dark edge
    _poly(surf, _AN_BLACK, [(base_x - half_w + 1, base_y),
                            (base_x + half_w - 1, base_y), (tip_x, tip_y + 1)])
    # Blue-black sheen down the front face so the ear isn't a flat void.
    _poly(surf, _AN_SHEEN, [(base_x - 1, base_y - 1),
                            (base_x + half_w - 2, base_y - 1),
                            (tip_x, tip_y + 3)])
    # Thin gold inner-ear lining — the night read.
    inner = [(base_x, base_y - 1), (base_x + half_w - 3, base_y - 1),
             (tip_x, tip_y + 5)]
    _poly(surf, _AN_GOLD_D, inner)
    _poly(surf, _AN_GOLD, [(base_x + 1, base_y - 2),
                           (base_x + half_w - 4, base_y - 2),
                           (tip_x, tip_y + 7)])
    pygame.draw.line(surf, _AN_GOLD_H, (tip_x, tip_y + 4),
                     (base_x + 1, base_y - 2), 1)


def _was_scepter(surf):
    """Gold was-scepter slung diagonally INSIDE the wing silhouette: a straight
    gold shaft with the canonical forked base low and a stylised animal-head
    crook at the top. Kept inside the body footprint — neither end overshoots
    far past the back, and nothing crosses the feet line."""
    top = (HX - 17, CROWN_Y + 3)       # crook head, high in the wing
    bot = (HX - 7, HY + 21)            # forked base, above the feet line
    pygame.draw.line(surf, _AN_GOLD_D, top, bot, 4)
    pygame.draw.line(surf, _AN_GOLD, top, bot, 2)
    pygame.draw.line(surf, _AN_GOLD_H, (top[0] + 1, top[1] + 1),
                     (bot[0] + 1, bot[1] - 3), 1)
    # Angular Set-animal head crook at the top (the was tell).
    _poly(surf, _AN_GOLD, [(top[0], top[1] + 1), (top[0] - 5, top[1] - 3),
                           (top[0] - 4, top[1] + 2)])
    pygame.draw.line(surf, _AN_GOLD_H, (top[0] - 4, top[1] - 2),
                     (top[0] - 1, top[1] + 1), 1)
    # Forked base — the two-prong fork that names the scepter.
    pygame.draw.line(surf, _AN_GOLD_D, bot, (bot[0] - 3, bot[1] + 4), 2)
    pygame.draw.line(surf, _AN_GOLD_D, bot, (bot[0] + 3, bot[1] + 4), 2)
    pygame.draw.line(surf, _AN_GOLD, bot, (bot[0] - 2, bot[1] + 4), 1)
    pygame.draw.line(surf, _AN_GOLD, bot, (bot[0] + 2, bot[1] + 4), 1)


def _ankh(surf, cx, cy):
    """Small ivory ankh glyph at the hip — loop + crossbar + stem, the lone pale
    splash that pops on both day and night."""
    pygame.draw.ellipse(surf, _AN_KOHL, (cx - 3, cy - 6, 6, 6))
    pygame.draw.ellipse(surf, _AN_IVORY, (cx - 2, cy - 5, 4, 5), 1)
    pygame.draw.line(surf, _AN_IVORY, (cx, cy - 1), (cx, cy + 5), 2)
    pygame.draw.line(surf, _AN_IVORY, (cx - 3, cy + 1), (cx + 3, cy + 1), 2)
    pygame.draw.circle(surf, _AN_GOLD_H, (cx, cy - 4), 1)


def _paint(surf, _a):
    cy = CROWN_Y

    # Was-scepter first so the body covers the shaft mid-section and only the
    # gold crook/fork read as a carried staff inside the wing.
    _was_scepter(surf)

    # Two TALL erect pointed jackal ears spiking straight up above the head —
    # the unmistakable ~40px hero silhouette. Slightly splayed, both rising well
    # past CROWN_Y; ONLY headgear allowed above the crown.
    _ear(surf, HX - 4, HX - 7, cy + 1, cy - 22, 4)
    _ear(surf, HX + 6, HX + 10, cy + 1, cy - 21, 4)
    # A small black skull-cap bridging the ear bases so they read as growing
    # from one head, not floating.
    pygame.draw.ellipse(surf, _AN_BLACK, (HX - 9, cy - 3, 22, 9))
    pygame.draw.ellipse(surf, _AN_SHEEN, (HX - 6, cy - 3, 11, 4))
    pygame.draw.line(surf, _AN_GOLD, (HX - 8, cy + 2), (HX + 11, cy + 1), 1)

    # Dark snout shadow along the beak — implies the long jackal muzzle without
    # changing the bird's footprint.
    _poly(surf, _AN_KOHL, [(HX + 6, HY + 1), (HX + 17, HY + 3),
                           (HX + 16, HY + 8), (HX + 6, HY + 7)])
    pygame.draw.line(surf, _AN_SHEEN, (HX + 7, HY + 2), (HX + 15, HY + 4), 1)

    # Gold-rimmed almond eye + a long curved gold kohl flick sweeping back —
    # the Egyptian face tell that survives downscale.
    ex, ey = HX + 6, HY - 1
    _poly(surf, _AN_GOLD, [(ex - 4, ey), (ex, ey - 3), (ex + 5, ey),
                           (ex, ey + 3)])
    _poly(surf, _AN_KOHL, [(ex - 2, ey), (ex, ey - 1), (ex + 3, ey),
                           (ex, ey + 1)])
    pygame.draw.circle(surf, _AN_IVORY, (ex, ey), 1)
    # Long upturned kohl flick.
    pygame.draw.lines(surf, _AN_GOLD, False,
                      [(ex + 5, ey), (ex + 10, ey - 1), (ex + 13, ey - 4)], 2)
    pygame.draw.line(surf, _AN_GOLD_H, (ex + 6, ey - 1), (ex + 11, ey - 2), 1)

    # Narrow gold-and-black striped collar band across the upper breast, held
    # inside the body footprint — alternating gold/dark bars so it reads as a
    # banded usekh, not a solid plate.
    collar = [(HX - 11, HY + 8), (HX + 11, HY + 6),
              (HX + 9, HY + 13), (HX - 9, HY + 15)]
    _poly(surf, _AN_KOHL, collar)
    _poly(surf, _AN_GOLD, [(HX - 10, HY + 8), (HX + 10, HY + 6),
                           (HX + 9, HY + 11), (HX - 9, HY + 13)])
    for i in range(6):
        x0 = HX - 9 + i * 3
        col = _AN_KOHL if i % 2 == 0 else _AN_GOLD_D
        pygame.draw.line(surf, col, (x0, HY + 8), (x0 - 1, HY + 13), 2)
    pygame.draw.line(surf, _AN_GOLD_H, (HX - 9, HY + 8), (HX + 9, HY + 6), 1)
    # A single gold drop bead centring the collar.
    pygame.draw.circle(surf, _AN_GOLD, (HX, HY + 14), 2)
    pygame.draw.circle(surf, _AN_GOLD_H, (HX - 1, HY + 13), 1)

    # Small ivory ankh glyph at the hip (near side), inside the footprint.
    _ankh(surf, HX - 13, HY + 14)

    # Gold anklets at the feet line — a bright ring on each foot, not below it.
    for fx, fy in ((28, HY + 24), (34, HY + 24)):
        pygame.draw.line(surf, _AN_GOLD_D, (fx - 3, fy), (fx + 3, fy), 3)
        pygame.draw.line(surf, _AN_GOLD, (fx - 3, fy - 1), (fx + 3, fy - 1), 1)
        pygame.draw.circle(surf, _AN_GOLD_H, (fx, fy - 1), 1)


build = store_skins._make_skin(_paint, base_fn=_an_base)
