"""design_4 · NEST-BABY — baby-parrot store exploration (scratch only).

"Still in the nest." Pip re-plumaged into a warm fawn chick sitting DOWN INTO a
little twig-bowl nest under the lower body, with a wide-open peeping beak (the
bright coral inner-mouth wedge that says "feed me!"), big-baby catch-light eyes
peeking under the aviators, and a soft down cowlick. The twig-bowl is the
silhouette-breaker no other skin owns — a whole baby-bird scene rather than bare
fuzz (Downball) or an egg cap (Hatchling).

North star is "lives or dies at 40px on BOTH skies". A woven basket mushes into
noise at 40px, so the nest is drawn as a SHAPE, not a weave: a U-shaped cradle of
FEW chunky HORIZONTAL twig-bars (each ≥3px tall, each with a deep ink-brown
underline) stacked into a curved wall the body sits into, plus a handful of dry-
grass stalks poking UP past the rim to break the outline. The weave is a lie told
by ~5 bars + ~4 stalks — never twelve crossing twigs. The hard dark-twig-on-fawn
value jump (a 2-step drop below the body shadow) is what makes the bowl read at
icon size. The peep-beak is kept crisp (a dark throat socket + a bright coral
inner wedge + a full ink-keyed lower mandible) because the open mouth is the
cheapest, strongest cuteness tell, and it anchors hard to the head every frame.
Geometry is the FIXED macaw build — "baby" is sold by palette + overlay only,
never by shrinking. Aviators STAY (warm-tan tint) as Pip's tell.

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
# Twig browns run a hard 3-step ramp so each bar reads as a lit top edge over a
# deep shadow body over an INK underline — the value jump that makes the bowl
# survive 40px. #8A5A32 is RESERVED for the lit top edge only; the bar body and
# its underline sit ~2 steps below the fawn body shadow so the nest never reads
# as a feather tone.
_NB_TWIG    = (96, 62, 34)            # #603E22 bar body — 2 steps under body shadow
_NB_TWIG_D  = (74, 47, 28)           # #4A2F1C deep ink underline beneath each bar
_NB_TWIG_H  = (138, 90, 50)          # #8A5A32 lit top edge of each bar (round read)
# Straw stalks need to read AGAINST the fawn body, so the stalk base runs a
# darker grass-brown (a clear step under the fawn) with a bright #E4C88C lit tip —
# a hard dark→light flick that survives the body it crosses, instead of vanishing
# into the same tone.
_NB_STRAW   = (150, 112, 58)         # dry-grass stalk base (reads on fawn)
_NB_STRAW_H = (228, 200, 140)        # #E4C88C lit straw tip
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


def _bar(surf, x0, x1, y, *, w=3):
    """One chunky HORIZONTAL twig-bar of the bowl wall — a deep INK underline, a
    thick #603E22 body, then a thin #8A5A32 lit top edge. Few-and-fat (≥3px) and
    all-horizontal so the curved wall reads as a SHAPE that survives the 40px
    downsample, never a weave that smears. Endpoints round-cap so the bowl rim
    curves instead of stair-stepping."""
    pygame.draw.line(surf, _NB_TWIG_D, (x0, y + w), (x1, y + w), 2)
    pygame.draw.line(surf, _NB_TWIG, (x0, y), (x1, y), w)
    pygame.draw.line(surf, _NB_TWIG_H, (x0 + 1, y - (w - 1) // 2),
                     (x1 - 1, y - (w - 1) // 2), 1)


def _grass(surf, x0, y0, dx, dy):
    """A dry-grass stalk poking UP past the nest rim — a 2px straw stroke with a
    bright tip. These silhouette-breakers above the bowl edge sell "nest" cheaply
    by breaking the outline, better than any internal weave."""
    pygame.draw.line(surf, _NB_STRAW, (x0, y0), (x0 + dx, y0 + dy), 2)
    pygame.draw.line(surf, _NB_STRAW_H, (x0 + dx, y0 + dy),
                     (x0 + int(dx * 0.55), y0 + int(dy * 0.55)), 1)


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

    # 1 · TWIG-BOWL NEST — the hero silhouette-breaker, drawn as a SHAPE not a
    #     weave. A U-shaped cradle of FEW chunky HORIZONTAL twig-bars stacked under
    #     the lower body, each bar shorter as it climbs the side walls, so the
    #     stack forms a curved bowl the body sits DOWN INTO ("Pip in a bowl", not
    #     "Pip wearing a brown belt"). Drawn FIRST so the belly's lower edge tucks
    #     behind the rim. The hard #4A2F1C underline beneath each #603E22 bar is
    #     the 2-step value drop that keeps the band legible at 40px. Dry-grass
    #     stalks poke UP past the rim to break the outline and sell "nest".
    #
    #     Bowl geometry sits under the curved lower belly (which spans ~x12..66 at
    #     y68, narrowing to ~x33..55 by y80): wide top rim, narrowing as it drops.
    bowl_l, bowl_r = 11, 60            # outer rim x-extents (widest, top course)
    bowl_top = 67                      # top rim y; bars step DOWN from here
    # Stacked horizontal bars, each narrower than the one above so the walls curve
    # inward — five fat bars total, the wall the chick nestles into.
    _bar(surf, bowl_l,      bowl_r,      bowl_top,      w=4)   # top rim, widest
    _bar(surf, bowl_l + 4,  bowl_r - 4,  bowl_top + 4,  w=4)
    _bar(surf, bowl_l + 9,  bowl_r - 9,  bowl_top + 8,  w=3)
    _bar(surf, bowl_l + 15, bowl_r - 15, bowl_top + 11, w=3)
    _bar(surf, bowl_l + 20, bowl_r - 20, bowl_top + 13, w=3)  # bottom, narrowest
    # The two side walls of the cradle rise above the top rim so the bowl cups UP
    # around the body — a short fat bar climbing each upper corner.
    _bar(surf, bowl_l - 1, bowl_l + 8, bowl_top - 4, w=3)
    _bar(surf, bowl_r - 8, bowl_r + 1, bowl_top - 4, w=3)
    # Dry-grass stalks rising tall from the rim corners and leaning OUTWARD so
    # their bright tips clear the belly silhouette and break the outline at the
    # sides — the cheap, high-value "nest" tell. A hard dark stalk + bright tip so
    # each reads against the fawn it crosses, never vanishing into body tone.
    _grass(surf, bowl_l + 1,  bowl_top - 2, -5, -13)
    _grass(surf, bowl_l + 5,  bowl_top - 3, -7, -10)
    _grass(surf, bowl_r - 1,  bowl_top - 2,  5, -13)
    _grass(surf, bowl_r - 5,  bowl_top - 3,  7, -10)

    # 2 · CHEST NATAL-DOWN — a couple of pale cream wisps over the warm body so
    #     the chick still reads downy above the nest line, breaking the chest edge.
    _down(surf, BCX - 2, BCY - 5, -4, -4)
    _down(surf, BCX + 4, BCY - 7, 2, -5)

    # 3 · STUBBY DOWN-WING — a hard bright cream pop faking a pudgy half-grown
    #     wing, with a 1px INK tuck at the tip so it reads as a distinct stubby
    #     wing and not a sheen. Kept above the nest zone so it stays the body's one
    #     bright note. R1's soft blob was invisible at 40px; this is a fat 3px arc.
    wing = [(BCX + 2, BCY - 7), (BCX + 11, BCY - 5), (BCX + 12, BCY + 1),
            (BCX + 4, BCY)]
    pygame.draw.polygon(surf, (246, 230, 190), wing)               # #F6E6BE pop
    pygame.draw.line(surf, _NB_WHITE, (BCX + 3, BCY - 6), (BCX + 9, BCY - 5), 2)
    pygame.draw.line(surf, _NB_INK, (BCX + 11, BCY - 5), (BCX + 12, BCY + 1), 1)

    # 4 · BIG-BABY EYES — demoted under the aviators so they peek UNDER the lens
    #     rim instead of displacing the frame: a small 2px catch-light dome dropped
    #     ~1px lower than R1, with a warm-dark pupil and a 1px spec. The aviator
    #     frame line must stay the TOPMOST element on the face (aviators are Pip),
    #     so these sit low and small and never crowd the rim. A rosy-tan cheek dab
    #     adds warmth below.
    for ex, ey in ((46, 45), (55, 44)):
        pygame.draw.circle(surf, _NB_WHITE, (ex, ey), 2)
        pygame.draw.circle(surf, _NB_INK, (ex, ey + 1), 1)
        pygame.draw.circle(surf, (255, 255, 255), (ex - 1, ey), 1)
    pygame.draw.circle(surf, (224, 158, 120), (43, 48), 2)   # cheek-blush

    # 5 · WIDE-OPEN PEEP BEAK — the hero cuteness tell, replacing the closed adult
    #     beak with a gaping "feed me!" mouth: an upper mandible wedge hinged open
    #     over a dark throat socket with a BRIGHT coral inner-mouth wedge, and a
    #     hard lower mandible. The dark socket + bright coral give the crisp value
    #     jump that keeps the open mouth legible at 40px. The base is pulled 1px
    #     INTO the head (rooted under the head's right edge ~x61) so the upper
    #     mandible stays welded to the face across all four wing frames instead of
    #     drifting off as a free wedge.
    bx, by = 55, 44                     # beak base, rooted under the head edge
    # Throat socket — the dark gape behind the coral, so the mouth reads as a hole.
    pygame.draw.polygon(surf, _NB_CORAL_D,
                        [(bx, by - 4), (bx + 8, by - 2), (bx + 7, by + 6),
                         (bx, by + 4)])
    # Bright coral inner-mouth wedge (the tongue/gape) — the peep pop.
    pygame.draw.polygon(surf, _NB_CORAL,
                        [(bx + 1, by - 1), (bx + 7, by - 1), (bx + 6, by + 4),
                         (bx + 1, by + 3)])
    pygame.draw.line(surf, (248, 176, 160), (bx + 2, by + 1), (bx + 6, by + 1), 1)
    # Upper mandible — hinged open, pointing up-forward, its hinge corner buried
    # 2px back inside the head so it never floats free of the face.
    upper = [(bx - 2, by - 3), (bx + 9, by - 6), (bx + 8, by - 2), (bx, by - 1)]
    pygame.draw.polygon(surf, _NB_TAN, upper)
    pygame.draw.polygon(surf, _NB_INK, upper, 1)
    pygame.draw.line(surf, (248, 224, 176), (bx, by - 3), (bx + 7, by - 5), 1)
    # Lower mandible — the open jaw dropped below the gape, fully INK-keyed so the
    # two mandibles read as a distinct open jaw, not one blob.
    lower = [(bx, by + 3), (bx + 8, by + 5), (bx + 6, by + 9), (bx, by + 7)]
    pygame.draw.polygon(surf, (208, 158, 92), lower)
    pygame.draw.polygon(surf, _NB_INK, lower, 2)

    # 6 · DOWN-TUFT COWLICK — one soft sprout of cream down off the crown breaking
    #     the head outline (the baby cowlick idiom, soft not a feather). The R1
    #     stray nest-twig is CUT: it smeared at 40px and crowded the aviators, and
    #     the bowl already carries all the twig storytelling. Kept to three fat
    #     2px flicks so the tuft survives the strip as a clean hard shape.
    cwx, cwy = HX - 2, CROWN_Y
    for dx, dy in ((-3, -7), (0, -8), (3, -6)):
        pygame.draw.line(surf, _NB_SHADOW, (cwx, cwy), (cwx + dx, cwy + dy), 2)
        pygame.draw.line(surf, _NB_CREAM, (cwx, cwy),
                         (cwx + int(dx * 0.7), cwy + int(dy * 0.7)), 2)
    pygame.draw.circle(surf, _NB_WHITE, (cwx, cwy - 8), 1)


# Body recolour through the palette system + the nest overlay, wrapped by the
# house _make_skin contract (lazy flat build + per-(frame, 3°) rotation cache).
build = store_skins._make_skin(
    _paint_nestbaby,
    base_fn=lambda a: _build_parrot_with_palette(a, P_NESTBABY),
)
