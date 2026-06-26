"""design_4 · NEST-BABY — baby-parrot store exploration (scratch only).

"Still in the nest." Pip re-plumaged into a warm fawn chick sitting in a little
woven twig-nest ruff that rings the lower body, with a wide-open peeping beak
(the bright coral inner-mouth wedge that says "feed me!"), big-baby catch-light
eyes under the aviators, and a soft down cowlick with a stray twig caught in it.
The woven-twig collar is the silhouette-breaker no other skin owns — a whole
baby-bird scene rather than bare fuzz (Downball) or an egg cap (Hatchling).

North star is "lives or dies at 40px on BOTH skies". The riskiest element is the
woven nest collar, which mushes into noise if it's drawn as fine basketwork — so
it's built from FEW, CHUNKY twig strokes (each ≥2px) in a dark twig-brown that
sits hard against the warm fawn body, so the ring reads as one woven band, not
clutter. The peep-beak is kept crisp (a dark mouth socket + a bright coral inner
wedge + a hard lower mandible) because the open mouth is the cheapest, strongest
cuteness tell. Geometry is the FIXED macaw build — "baby" is sold by palette +
overlay only, never by shrinking. Aviators STAY (warm-tan tint) as Pip's tell.

The earthy fawn / twig-brown lane is owned by no adult or rarity skin, so the
costume can't be confused with the green amazon, gold-blue, or pearl rarities.
Exploration only — NEVER registered in store_skins.BUILDERS.
"""
import math
import pygame

from game import store_skins
from game.store_skins import HX, HY, CROWN_Y
from game.dollar_parrot_ghost import _pal, _build_parrot_with_palette


# Nest-baby palette — warm fawn down body with a deep-tan shadow owning the line
# work, a cream belly bright so the natal-down wisps read, the twig-brown +
# dry-grass straw for the nest props, and the coral peep-mouth as the one warm
# pop. Aviators retinted warm tan so the shades sit IN the earthy scheme instead
# of fighting it. Warmth is bought with saturated local FAWN, never emission, so
# nothing here reads like a glow rarity.
_NB_FAWN    = (233, 201, 140)        # #E9C98C body fawn
_NB_SHADOW  = (185, 138, 78)         # #B98A4E deep-tan shadow / keyline
_NB_CREAM   = (246, 230, 190)        # #F6E6BE cream belly + down wisp
_NB_TWIG    = (138, 90, 50)          # #8A5A32 nest-twig brown
_NB_TWIG_D  = (96, 62, 34)           # deep twig shadow (the woven under-strokes)
_NB_TWIG_H  = (176, 124, 76)         # lit twig edge so the ring reads round
_NB_STRAW   = (203, 167, 96)         # #CBA760 dry-grass straw wisp
_NB_STRAW_H = (228, 200, 140)        # lit straw tip
_NB_CORAL   = (232, 122, 102)        # #E87A66 peep inner-mouth coral
_NB_CORAL_D = (176, 78, 64)          # mouth socket shadow / throat
_NB_TAN     = (216, 168, 96)         # #D8A860 aviator warm-tan tint
_NB_WHITE   = (252, 248, 238)        # eye catch-light dome / down-tip spec
_NB_INK     = (58, 44, 32)           # warm-dark pupil + beak keyline


# Full fawn-down re-plumage. The shadow slots run deep tan so the chick already
# carries a dark→light range (the nest ring sits on a warm, not pale, body); the
# belly + chest stay cream so the natal-down highlights echo down the body. The
# twig-browns are deliberately kept OUT of the base plumage — they belong only to
# the overlaid nest so the woven ring reads as a separate thing Pip sits in, not
# a feather pattern. Aviators retinted warm tan; lenses KEPT (Pip's tell).
P_NESTBABY = _pal(
    tail=[(150, 108, 60), (178, 134, 80), (206, 164, 104), (228, 196, 140)],
    tail_line=_NB_SHADOW,
    body_shadow=(178, 132, 74),
    body_main=_NB_FAWN,
    body_chest=(244, 224, 178),
    body_belly=_NB_CREAM,
    sheen=(255, 246, 222, 120),
    wing_main=(214, 178, 116),
    wing_dark=(160, 116, 64),
    wing_tip=(240, 218, 168),
    wing_secondary=None,               # single warm hue — no contrast feather
    wing_highlight=(248, 232, 190),
    head_shadow=(178, 132, 74),
    head_main=_NB_FAWN,
    head_cheek=(244, 220, 172),
    head_crown=(228, 196, 140),
    lens_frame=(196, 150, 86),         # warm-tan rims
    lens_body=(58, 44, 34),
    lens_tint=(216, 168, 96, 130),     # warm-tan lens tint
    lens_glint=(255, 248, 232),
    beak_main=(226, 178, 110),
    beak_dark=(150, 104, 56),
    beak_gloss=(248, 224, 176),
    foot=(150, 104, 56),
)


def _twig(surf, x0, y0, x1, y1):
    """One CHUNKY nest twig — a dark under-stroke + a twig-brown body + a short
    lit edge, so each stick reads as a round woody stroke with a hard value jump
    against the fawn body and survives the 40px downsample. Kept ≥2px and FEW so
    the woven ring is a band, not noise."""
    pygame.draw.line(surf, _NB_TWIG_D, (x0, y0 + 1), (x1, y1 + 1), 3)
    pygame.draw.line(surf, _NB_TWIG, (x0, y0), (x1, y1), 2)
    pygame.draw.line(surf, _NB_TWIG_H, (x0, y0 - 1),
                     ((x0 + x1) // 2, (y0 + y1) // 2 - 1), 1)


def _grass(surf, x0, y0, dx, dy):
    """A dry-grass straw wisp poking just past the nest rim — a 2px straw stroke
    with a brighter tip, breaking the lower silhouette into a fuzzy nest edge."""
    pygame.draw.line(surf, _NB_STRAW, (x0, y0), (x0 + dx, y0 + dy), 2)
    pygame.draw.line(surf, _NB_STRAW_H, (x0 + dx, y0 + dy),
                     (x0 + int(dx * 0.6), y0 + int(dy * 0.6)), 1)


def _down(surf, x0, y0, dx, dy):
    """A short natal-down wisp — a 2px cream tapered flick poking past the
    silhouette, the No.1 baby tell: it breaks the sleek macaw outline into fuzz."""
    pygame.draw.line(surf, _NB_SHADOW, (x0, y0), (x0 + dx, y0 + dy), 2)
    pygame.draw.line(surf, _NB_CREAM, (x0, y0), (x0 + int(dx * 0.7),
                                                  y0 + int(dy * 0.7)), 2)
    pygame.draw.circle(surf, _NB_WHITE, (x0 + dx, y0 + dy), 1)


def _paint_nestbaby(surf, _a):
    # Composite-space anchors: head centre (HX,HY)=(47,41); the aviator lenses
    # sit at ~(46,40) and (56,39); the beak tip is ~(61,44); body centre ~(32,52).
    BCX, BCY = 32, 52

    # 1 · WOVEN TWIG-NEST COLLAR — the hero silhouette-breaker. A ring of FEW
    #     chunky crossing twigs around the LOWER body (the nest Pip sits in),
    #     drawn FIRST so the body's lower edge tucks INTO the nest and it reads as
    #     a bowl Pip nestles in, not a belt strapped on. Dry-grass wisps poke past
    #     the rim so the lower outline goes fuzzy. Kept to a handful of strokes
    #     with hard brown-on-fawn contrast so the band survives 40px.
    nest_y = BCY + 9
    # Back rim of the bowl (behind the belly) — a continuous woven arc of crossing
    # twigs sweeping under the body from tail side to wing side.
    _twig(surf, BCX - 19, nest_y - 4, BCX - 9, nest_y + 3)
    _twig(surf, BCX - 12, nest_y + 4, BCX - 1, nest_y - 1)
    _twig(surf, BCX - 4, nest_y - 2, BCX + 8, nest_y + 4)
    _twig(surf, BCX + 3, nest_y + 4, BCX + 14, nest_y - 2)
    _twig(surf, BCX + 9, nest_y - 3, BCX + 19, nest_y + 3)
    # A second lower course so the wall of the nest has woven depth (the basket
    # reads thick, not a single hoop).
    _twig(surf, BCX - 16, nest_y + 3, BCX - 5, nest_y + 7)
    _twig(surf, BCX - 7, nest_y + 7, BCX + 5, nest_y + 6)
    _twig(surf, BCX + 3, nest_y + 6, BCX + 16, nest_y + 4)
    # Dry-grass straw wisps tufting past the rim — the fuzzy nest edge.
    _grass(surf, BCX - 17, nest_y - 2, -5, -3)
    _grass(surf, BCX - 8, nest_y + 6, -3, 5)
    _grass(surf, BCX + 6, nest_y + 7, 2, 5)
    _grass(surf, BCX + 17, nest_y - 1, 5, -3)
    _grass(surf, BCX + 11, nest_y - 4, 3, -5)

    # 2 · CHEST NATAL-DOWN — a couple of pale cream wisps over the warm body so
    #     the chick still reads downy above the nest line, breaking the chest edge.
    _down(surf, BCX - 2, BCY - 5, -4, -4)
    _down(surf, BCX + 4, BCY - 7, 2, -5)

    # 3 · STUBBY DOWN-WING — a rounded bright highlight blob faking a pudgy half-
    #     grown wing, plus a short down fringe along the trailing edge so the wing
    #     reads not-yet-feathered. One bright note, kept off the busy nest zone.
    pygame.draw.circle(surf, (248, 232, 190), (BCX + 8, BCY - 4), 4)
    pygame.draw.circle(surf, _NB_WHITE, (BCX + 6, BCY - 6), 2)
    for fx, fy in ((BCX + 13, BCY - 2), (BCX + 14, BCY + 2), (BCX + 12, BCY + 5)):
        _down(surf, fx, fy, 3, 1)

    # 4 · BIG-BABY EYES — oversized white catch-light domes peeking under the near
    #     aviator lens so the round baby eye reads huge below the frame (neoteny),
    #     with a tiny warm-dark pupil + a starry spec. Drawn UNDER the lens rim so
    #     the aviators still own the face. A 2px rosy-tan cheek dabs warmth below.
    for ex, ey, r in ((46, 44, 3), (55, 43, 3)):
        pygame.draw.circle(surf, _NB_WHITE, (ex, ey), r)
        pygame.draw.circle(surf, _NB_INK, (ex, ey + 1), 1)
        pygame.draw.circle(surf, (255, 255, 255), (ex - 1, ey - 1), 1)
    pygame.draw.circle(surf, (224, 158, 120), (43, 47), 2)   # cheek-blush

    # 5 · WIDE-OPEN PEEP BEAK — the hero cuteness tell, replacing the closed adult
    #     beak with a gaping "feed me!" mouth: an upper mandible wedge hinged open
    #     over a dark throat socket with a BRIGHT coral inner-mouth wedge, and a
    #     hard lower mandible. The dark socket + bright coral give the crisp value
    #     jump that keeps the open mouth legible at 40px.
    bx, by = 56, 44                     # beak base, just past the head
    # Throat socket — the dark gape behind the coral, so the mouth reads as a hole.
    pygame.draw.polygon(surf, _NB_CORAL_D,
                        [(bx, by - 4), (bx + 8, by - 2), (bx + 7, by + 6),
                         (bx, by + 4)])
    # Bright coral inner-mouth wedge (the tongue/gape) — the peep pop.
    pygame.draw.polygon(surf, _NB_CORAL,
                        [(bx + 1, by - 1), (bx + 7, by - 1), (bx + 6, by + 4),
                         (bx + 1, by + 3)])
    pygame.draw.line(surf, (248, 176, 160), (bx + 2, by + 1), (bx + 6, by + 1), 1)
    # Upper mandible — hinged open, pointing up-forward off the head.
    upper = [(bx - 1, by - 3), (bx + 9, by - 6), (bx + 8, by - 2), (bx, by - 1)]
    pygame.draw.polygon(surf, _NB_TAN, upper)
    pygame.draw.polygon(surf, _NB_INK, upper, 1)
    pygame.draw.line(surf, (248, 224, 176), (bx, by - 3), (bx + 7, by - 5), 1)
    # Lower mandible — the open jaw dropped below the gape.
    lower = [(bx, by + 3), (bx + 8, by + 5), (bx + 6, by + 9), (bx, by + 7)]
    pygame.draw.polygon(surf, (208, 158, 92), lower)
    pygame.draw.polygon(surf, _NB_INK, lower, 1)

    # 6 · DOWN-TUFT COWLICK + STRAY TWIG — one soft sprout of cream down off the
    #     crown breaking the head outline (the baby cowlick idiom, soft not a
    #     feather), with a tiny stray nest-twig caught in it (fell from the rim).
    cwx, cwy = HX - 2, CROWN_Y
    for dx, dy in ((-3, -7), (0, -8), (3, -6)):
        pygame.draw.line(surf, _NB_SHADOW, (cwx, cwy), (cwx + dx, cwy + dy), 2)
        pygame.draw.line(surf, _NB_CREAM, (cwx, cwy),
                         (cwx + int(dx * 0.7), cwy + int(dy * 0.7)), 2)
    pygame.draw.circle(surf, _NB_WHITE, (cwx, cwy - 8), 1)
    # Stray twig caught in the cowlick — a tiny chunky brown stick poking out.
    _twig(surf, cwx - 5, cwy - 4, cwx + 4, cwy - 9)


# Body recolour through the palette system + the nest overlay, wrapped by the
# house _make_skin contract (lazy flat build + per-(frame, 3°) rotation cache).
build = store_skins._make_skin(
    _paint_nestbaby,
    base_fn=lambda a: _build_parrot_with_palette(a, P_NESTBABY),
)
