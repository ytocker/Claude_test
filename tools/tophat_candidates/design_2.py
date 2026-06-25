"""THE RINGMASTER — crimson-showman top-hat candidate (DESIGN 2 of 5).

Scratch exploration only; NOT registered in store_skins.BUILDERS, so the live
``skin_tophat`` is untouched.

Concept: keep the TOP HAT as the identity anchor, then dress Pip as a circus
ringmaster — a crimson tailcoat blazing with a vertical ladder of gold frog-
braid down the chest. The hero read is COLOUR: a black topper over a loud red
torso striped with three distinct gold bars, the one silhouette no sober
gentleman concept has. A slim black cane slung behind the body breaks the
outline; tall black riding boots and an upward-curled handlebar finish the
showman.

At 40px the read, in order of value: (1) a top-hatted bird, (2) the CRIMSON
coat holding its red value against day AND night sky, (3) the THREE gold frog-
braid bars staying separate (each fill→shadow→highlight so they never merge
into one gold blob), then (4) the black cane tip + gold ferrule breaking the
silhouette. Crimson is kept mid-high value and the lapels/hat/boots stay near-
black so the red never muddies; gold gets a bright highlight pass on every
object so the braid survives the downscale.
"""
import pygame

from game import store_skins
from game.store_skins import HX, HY, CROWN_Y, _poly

# Crimson coat — kept mid-high value so the red survives on BOTH skies; a dark
# wine shadow and a lifted highlight give the torso form without dropping value.
_RM_RED    = (176, 18, 26)         # #B0121A crimson coat
_RM_RED_D  = (58, 5, 8)            # #3A0508 coat shadow
_RM_RED_H  = (216, 54, 60)         # lifted crimson highlight (sheen on the chest)
# Near-black for hat / lapels / boots / moustache — one mass, two values so the
# black shapes still separate from each other and from the dark night sky.
_RM_BLACK  = (21, 21, 26)          # #15151A
_RM_BLACK_H = (54, 54, 64)         # black highlight / felt sheen edge
# Gold frogging — soft glow body + a bright highlight so each braid bar reads as
# its own bright line, never collapsing into a single gold smear.
_RM_GOLD   = (233, 194, 76)        # #E9C24C frogging
_RM_GOLD_D = (150, 116, 34)        # gold shadow (under-edge so a bar reads round)
_RM_GOLD_H = (242, 217, 138)       # #F2D98A gold highlight


def _paint(surf, _a):
    # Body centre in composite space (parrot body centre (32,32) + PARROT_DY).
    BCX, BCY = 32, 52

    # ── RINGMASTER CANE slung diagonally BEHIND the body (painted first so only
    #    the tip + ferrule that overshoot the silhouette survive). Slim black
    #    shaft with a gold knob at the grip and a bright gold ferrule at the tip
    #    poking past the lower-back outline into open sky.
    grip = (BCX - 11, BCY - 2)
    tip = (BCX - 24, BCY + 21)
    pygame.draw.line(surf, _RM_BLACK, grip, tip, 4)
    pygame.draw.line(surf, _RM_BLACK_H, (grip[0] + 1, grip[1]), (tip[0] + 1, tip[1]), 1)
    pygame.draw.circle(surf, _RM_GOLD_D, grip, 3)          # gold pommel knob
    pygame.draw.circle(surf, _RM_GOLD, grip, 2)
    pygame.draw.circle(surf, _RM_GOLD_H, (grip[0] - 1, grip[1] - 1), 1)
    pygame.draw.line(surf, _RM_GOLD_D, (tip[0] - 1, tip[1] - 2),
                     (tip[0] + 1, tip[1] + 2), 4)            # gold ferrule
    pygame.draw.line(surf, _RM_GOLD, tip, (tip[0] + 1, tip[1] + 1), 2)
    pygame.draw.circle(surf, _RM_GOLD_H, tip, 1)

    # ── TALL BLACK RIDING BOOTS over the feet, each with a gold cuff line. Drawn
    #    before the coat so the coat skirt overlaps their tops → reads "boots
    #    under a tailcoat". Chunky (the base foot is ~2px) so they survive
    #    downscale and poke below the body to anchor the lower silhouette.
    for fx in (BCX - 4, BCX + 2):
        pygame.draw.line(surf, _RM_BLACK, (fx, BCY + 11), (fx, BCY + 19), 4)
        pygame.draw.line(surf, _RM_BLACK_H, (fx - 2, BCY + 12), (fx - 2, BCY + 18), 1)
        _poly(surf, _RM_BLACK, [(fx - 2, BCY + 19), (fx + 4, BCY + 19),
                                (fx + 4, BCY + 22), (fx - 2, BCY + 22)])  # foot
        pygame.draw.line(surf, _RM_GOLD, (fx - 2, BCY + 12), (fx + 2, BCY + 12), 2)  # cuff
        pygame.draw.line(surf, _RM_GOLD_H, (fx - 2, BCY + 11), (fx + 1, BCY + 11), 1)

    # ── CRIMSON TAILCOAT painted OVER the body. A broad crimson field across the
    #    chest/belly with a dark-wine under-shadow so the torso reads round, a
    #    lifted sheen high on the chest, then BLACK cutaway lapels framing a
    #    central red placket (the lapels keep the red as a bold central wedge so
    #    the gold ladder sits on clean crimson).
    coat = [(BCX - 15, BCY - 9), (BCX + 14, BCY - 9), (BCX + 16, BCY + 6),
            (BCX + 10, BCY + 13), (BCX - 11, BCY + 13), (BCX - 16, BCY + 5)]
    _poly(surf, _RM_RED_D, [(x, y + 1) for x, y in coat])      # under-shadow
    _poly(surf, _RM_RED, coat)
    pygame.draw.line(surf, _RM_RED_H, (BCX - 9, BCY - 6), (BCX + 9, BCY - 7), 2)  # chest sheen
    # Tail skirts sweeping below the body — the tailcoat silhouette.
    _poly(surf, _RM_RED_D, [(BCX - 11, BCY + 9), (BCX - 4, BCY + 11),
                            (BCX - 7, BCY + 19), (BCX - 13, BCY + 16)])
    _poly(surf, _RM_RED_D, [(BCX + 4, BCY + 11), (BCX + 11, BCY + 9),
                            (BCX + 13, BCY + 16), (BCX + 7, BCY + 19)])
    # Black cutaway lapels framing a central red placket.
    _poly(surf, _RM_BLACK, [(BCX - 15, BCY - 9), (BCX - 6, BCY - 9),
                            (BCX - 9, BCY + 6), (BCX - 16, BCY + 4)])
    _poly(surf, _RM_BLACK, [(BCX + 14, BCY - 9), (BCX + 5, BCY - 9),
                            (BCX + 8, BCY + 6), (BCX + 15, BCY + 4)])
    pygame.draw.line(surf, _RM_BLACK_H, (BCX - 14, BCY - 7), (BCX - 8, BCY + 4), 1)
    pygame.draw.line(surf, _RM_BLACK_H, (BCX + 13, BCY - 7), (BCX + 7, BCY + 4), 1)

    # ── GOLD EPAULETTE dots at the shoulders (top of the ladder).
    for ex in (BCX - 10, BCX + 9):
        pygame.draw.circle(surf, _RM_GOLD_D, (ex, BCY - 8), 2)
        pygame.draw.circle(surf, _RM_GOLD, (ex, BCY - 8), 1)

    # ── THREE PAIRS of horizontal GOLD FROG-BRAID bars stacked vertically down
    #    the chest — the red-torso-ladder SIGNATURE. Each bar is drawn
    #    fill→shadow→highlight with a full empty crimson row between bars so the
    #    THREE stay distinct (never merging into one gold blob) at 40px; a dot
    #    button sits centred on each bar.
    bar_w = 7
    for i, by in enumerate((BCY - 4, BCY + 1, BCY + 6)):
        x0, x1 = BCX - bar_w, BCX + bar_w
        pygame.draw.line(surf, _RM_GOLD_D, (x0, by + 1), (x1, by + 1), 3)  # under-shadow
        pygame.draw.line(surf, _RM_GOLD, (x0, by), (x1, by), 2)            # braid body
        pygame.draw.line(surf, _RM_GOLD_H, (x0 + 1, by - 1), (x1 - 1, by - 1), 1)  # top glint
        # Curled frog-knot ends so the bar reads as braid, not a plain stripe.
        for sx in (x0, x1):
            pygame.draw.circle(surf, _RM_GOLD_D, (sx, by), 2)
            pygame.draw.circle(surf, _RM_GOLD, (sx, by), 1)
        # Central dot button.
        pygame.draw.circle(surf, _RM_GOLD_H, (BCX, by - 1), 1)

    # ── TALL BLACK STAND COLLAR with a small gold-knot cravat at the throat,
    #    bridging the coat to the head.
    _poly(surf, _RM_BLACK, [(HX - 7, HY + 6), (HX + 9, HY + 5),
                            (HX + 8, HY + 12), (HX - 6, HY + 13)])
    pygame.draw.line(surf, _RM_BLACK_H, (HX - 6, HY + 7), (HX + 8, HY + 6), 1)
    pygame.draw.circle(surf, _RM_GOLD_D, (HX + 1, HY + 10), 3)   # gold cravat knot
    pygame.draw.circle(surf, _RM_GOLD, (HX + 1, HY + 10), 2)
    pygame.draw.circle(surf, _RM_GOLD_H, (HX, HY + 9), 1)
    _poly(surf, _RM_GOLD_D, [(HX - 1, HY + 12), (HX + 3, HY + 12),
                            (HX + 1, HY + 16)])                  # cravat tail

    # ── TOP HAT — the IDENTITY ANCHOR. A tall near-black topper rising above the
    #    crown with a CRIMSON satin band and a thin gold pinstripe on the brim
    #    edge. Built brim → crown → band → pinstripe so the layers read cleanly.
    cy = CROWN_Y
    # Wide brim breaking the crown outline.
    pygame.draw.ellipse(surf, _RM_BLACK, (HX - 16, cy - 1, 33, 8))
    pygame.draw.ellipse(surf, _RM_BLACK_H, (HX - 14, cy - 1, 12, 3))  # brim sheen
    # Tall crown rising well above CROWN_Y (slight taper out at the top = top hat).
    crown = [(HX - 9, cy + 2), (HX - 11, cy - 17), (HX + 11, cy - 17),
             (HX + 9, cy + 2)]
    _poly(surf, _RM_BLACK, crown)
    pygame.draw.line(surf, _RM_BLACK_H, (HX - 8, cy - 15), (HX - 8, cy), 2)  # vertical sheen
    pygame.draw.ellipse(surf, _RM_BLACK_H, (HX - 9, cy - 19, 18, 5))         # flat top
    pygame.draw.ellipse(surf, _RM_BLACK, (HX - 8, cy - 18, 16, 4))
    # Crimson satin band around the base of the crown.
    pygame.draw.line(surf, _RM_RED_D, (HX - 10, cy), (HX + 10, cy), 5)
    pygame.draw.line(surf, _RM_RED, (HX - 10, cy - 1), (HX + 10, cy - 1), 3)
    pygame.draw.line(surf, _RM_RED_H, (HX - 9, cy - 2), (HX + 4, cy - 2), 1)
    # Thin gold pinstripe along the brim edge.
    pygame.draw.lines(surf, _RM_GOLD, False,
                      [(HX - 14, cy + 4), (HX, cy + 6), (HX + 14, cy + 4)], 1)
    pygame.draw.lines(surf, _RM_GOLD_H, False,
                      [(HX - 11, cy + 4), (HX, cy + 5), (HX + 11, cy + 4)], 1)

    # ── SHARP UPWARD-CURLED HANDLEBAR MOUSTACHE — the showman tell. Black, the
    #    curls sweeping up off the cheeks so they pop against the red collar; no
    #    monocle, so the face stays clean for the curls to be the read.
    mx, my = HX + 1, HY + 3
    pygame.draw.line(surf, _RM_BLACK, (mx - 1, my), (mx + 9, my + 1), 3)  # bar
    # Left curl sweeping up.
    pygame.draw.lines(surf, _RM_BLACK, False,
                      [(mx - 1, my), (mx - 7, my - 1), (mx - 9, my - 5),
                       (mx - 6, my - 7)], 3)
    # Right curl sweeping up.
    pygame.draw.lines(surf, _RM_BLACK, False,
                      [(mx + 9, my + 1), (mx + 14, my), (mx + 16, my - 4),
                       (mx + 13, my - 6)], 3)
    pygame.draw.line(surf, _RM_BLACK_H, (mx - 1, my - 1), (mx + 8, my), 1)  # sheen


build = store_skins._make_skin(_paint)
