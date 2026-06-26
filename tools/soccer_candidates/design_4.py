"""DESIGN 4 — THE REFEREE (Soccer / Football).

Scratch exploration only — NOT registered in store_skins.BUILDERS. Pip the
scarlet macaw kitted as the man in the middle: an all-BLACK officials kit —
a black collared shirt with white collar piping, black shorts + socks +
boots — with the hero props drawn LAST so they sit proud of the cloth: a
metal WHISTLE on a lanyard cord that loops the neck and rests on the chest,
and a yellow CARD with a sliver of red card peeking from the breast pocket.
A completely different role and colour-story from any player kit.

The kit is painted OVER the scarlet body (the head stays the macaw so Pip
still reads as a parrot). The risk of a black kit on a scarlet bird is that
the cloth swallows the body contour, so the read is carried by crisp WHITE
piping + the bright yellow/red cards + the steel whistle glint — all kept
high-contrast so they survive the 40px downscale on BOTH day and night.
All kit is held INSIDE the base bird footprint (socks + boots on the feet
line ~HY+15..27, only a thin cap touches the crown).

Headless render: tools/soccer_candidates/render_design_4.py.
"""
import pygame

from game import store_skins
from game.store_skins import HX, HY, CROWN_Y, _poly


# All-black officials kit. Black on the scarlet body needs THREE values so the
# cloth still reads round after downscale: a near-black core, a cool dark grey
# lit plane, and a rim light at the contour. The piping/cards/whistle then do
# the contrast work the black cloth can't.
_REF_BLACK   = (26, 28, 34)         # #1A1C22 referee black (core)
_REF_GREY    = (52, 56, 66)         # cool dark grey lit plane (mid value)
_REF_RIM     = (92, 98, 112)        # cool rim light at the cloth edge
_REF_WHITE   = (244, 244, 248)      # #F4F4F8 collar / sock piping
_REF_YELLOW  = (255, 210, 59)       # #FFD23B yellow card
_REF_YEL_H   = (255, 232, 138)      # yellow-card glint
_REF_RED     = (224, 56, 44)        # #E0382C red card sliver
_REF_RED_D   = (150, 30, 24)        # red-card edge
_REF_STEEL   = (200, 204, 212)      # #C8CCD4 whistle steel
_REF_STEEL_H = (244, 246, 250)      # whistle hot glint
_REF_STEEL_D = (96, 102, 116)       # whistle steel shadow
_REF_CORD    = (214, 216, 222)      # pale lanyard cord (so it reads on black)
_REF_CORD_D  = (120, 124, 134)      # cord shadow strand


# Body centre in composite space (parrot body centre (32,32) + PARROT_DY=20).
BCX, BCY = 32, 52


def _paint(surf, _a):
    # --- Black collared ref SHIRT over the torso (THE officials read) -----------
    # A clean shirt block clipped to the chest, painted near-black, then a cool
    # grey lit plane down the left chest and a rim light at the right contour so
    # the cloth reads ROUND despite being black on a scarlet body. Kept inside
    # the footprint (top at the shoulders ~BCY-12, hem at ~BCY+11).
    shirt = [(BCX - 15, BCY - 9), (BCX - 16, BCY - 1), (BCX - 14, BCY + 11),
             (BCX + 13, BCY + 11), (BCX + 15, BCY - 1), (BCX + 13, BCY - 9),
             (BCX + 4, BCY - 12), (BCX - 6, BCY - 12)]
    _poly(surf, _REF_BLACK, shirt)

    # Lit plane — a soft grey wedge down the near (left) chest so a light source
    # reads on the black cloth instead of a flat silhouette.
    _poly(surf, _REF_GREY, [(BCX - 14, BCY - 7), (BCX - 6, BCY - 8),
                            (BCX - 8, BCY + 9), (BCX - 14, BCY + 8)])
    # Rim light along the far (right) shoulder/side edge — the cool highlight
    # that pulls the contour off the scarlet body at small sizes.
    pygame.draw.line(surf, _REF_RIM, (BCX + 13, BCY - 9), (BCX + 14, BCY + 9), 1)
    pygame.draw.line(surf, _REF_RIM, (BCX + 4, BCY - 12), (BCX + 13, BCY - 9), 1)

    # Shoulder-seam shadow so the sleeves read as set-in, plus the cloth edge.
    pygame.draw.line(surf, _REF_BLACK, (BCX - 13, BCY - 8), (BCX + 11, BCY - 8), 1)
    pygame.draw.polygon(surf, _REF_BLACK, shirt, 1)

    # Collar — a sharp white-piped V so the shirt reads as a collared officials
    # top, not a plain black bib. The white piping is the first contrast hit.
    _poly(surf, _REF_BLACK, [(BCX - 6, BCY - 12), (BCX + 4, BCY - 12),
                             (BCX, BCY - 6), (BCX - 3, BCY - 8)])
    pygame.draw.line(surf, _REF_WHITE, (BCX - 6, BCY - 12), (BCX - 1, BCY - 6), 2)
    pygame.draw.line(surf, _REF_WHITE, (BCX + 4, BCY - 12), (BCX, BCY - 6), 2)
    # White placket flash down the centre seam (a thin officials trim).
    pygame.draw.line(surf, _REF_WHITE, (BCX - 1, BCY - 6), (BCX - 2, BCY + 4), 1)
    # White piping along each sleeve cap so the shoulders read crisp on day+night.
    pygame.draw.line(surf, _REF_WHITE, (BCX - 15, BCY - 7), (BCX - 13, BCY - 1), 1)
    pygame.draw.line(surf, _REF_WHITE, (BCX + 14, BCY - 7), (BCX + 13, BCY - 1), 1)

    # --- Black SOCKS + boots at the feet line -----------------------------------
    # Black socks with a single white hoop band (the kit tell), then black boots
    # with a white sole stripe so the feet read as boots, not a dark blob, at
    # small sizes. Everything sits ON the feet line (~HY+15..27).
    for fx in (28, 35):
        pygame.draw.line(surf, _REF_GREY, (fx + 1, HY + 15), (fx + 1, HY + 23), 5)
        pygame.draw.line(surf, _REF_BLACK, (fx, HY + 15), (fx, HY + 23), 4)
        # White hoop band near the top of the sock — crisp contrast on the black.
        pygame.draw.line(surf, _REF_WHITE, (fx - 1, HY + 16), (fx + 1, HY + 16), 2)
        # Boot — black upper + a bright white sole stripe + two stud ticks.
        pygame.draw.ellipse(surf, _REF_GREY, (fx - 4, HY + 22, 9, 5))
        pygame.draw.ellipse(surf, _REF_BLACK, (fx - 4, HY + 23, 9, 4))
        pygame.draw.line(surf, _REF_WHITE, (fx - 3, HY + 24), (fx + 2, HY + 24), 1)
        for tx in (fx - 2, fx + 1):
            pygame.draw.line(surf, _REF_BLACK, (tx, HY + 26), (tx, HY + 27), 2)

    # --- Optional thin black CAP on the crown (officials touch) ------------------
    # A slim peaked black cap with one rim-light edge — adds the official's
    # headgear tell without the bulk that would hide the macaw head.
    cap = [(HX - 10, CROWN_Y + 4), (HX + 11, CROWN_Y + 4),
           (HX + 9, CROWN_Y - 1), (HX - 7, CROWN_Y - 1)]
    _poly(surf, _REF_BLACK, cap)
    _poly(surf, _REF_GREY, [(HX - 7, CROWN_Y - 1), (HX + 3, CROWN_Y - 1),
                            (HX + 2, CROWN_Y + 2), (HX - 6, CROWN_Y + 2)])
    pygame.draw.line(surf, _REF_RIM, (HX - 7, CROWN_Y - 1), (HX + 9, CROWN_Y - 1), 1)
    # Short brim peeking forward (toward the beak) so it reads as a peaked cap.
    _poly(surf, _REF_BLACK, [(HX + 9, CROWN_Y + 3), (HX + 14, CROWN_Y + 4),
                             (HX + 9, CROWN_Y + 5)])

    # --- HERO PROPS, drawn LAST so they sit IN FRONT of the cloth ----------------
    # Lanyard CORD looping the neck — a pale cord so it reads against the black
    # shirt, with a darker companion strand for round. Two strands V down to the
    # whistle resting at the chest centre.
    nlx, nly = BCX, BCY - 7                          # neck base of the lanyard
    wx, wy = BCX, BCY + 2                            # whistle resting point
    pygame.draw.line(surf, _REF_CORD_D, (nlx - 6, nly - 1), (wx - 1, wy - 2), 2)
    pygame.draw.line(surf, _REF_CORD_D, (nlx + 6, nly - 1), (wx + 1, wy - 2), 2)
    pygame.draw.line(surf, _REF_CORD, (nlx - 6, nly - 2), (wx - 1, wy - 3), 1)
    pygame.draw.line(surf, _REF_CORD, (nlx + 6, nly - 2), (wx + 1, wy - 3), 1)

    # Steel WHISTLE on the chest — a rounded body + a small mouthpiece, with a
    # hot glint so the metal reads bright on both day and night swatches.
    pygame.draw.ellipse(surf, _REF_STEEL_D, (wx - 4, wy - 2, 9, 7))
    pygame.draw.ellipse(surf, _REF_STEEL, (wx - 4, wy - 2, 8, 6))
    # Mouthpiece nub on the near side.
    _poly(surf, _REF_STEEL, [(wx + 3, wy), (wx + 6, wy + 1), (wx + 3, wy + 3)])
    pygame.draw.line(surf, _REF_STEEL_D, (wx + 3, wy + 3), (wx + 6, wy + 1), 1)
    # Hot glint — the single brightest pixel cluster, sells the metal.
    pygame.draw.line(surf, _REF_STEEL_H, (wx - 2, wy - 1), (wx, wy - 1), 2)
    pygame.draw.ellipse(surf, _REF_STEEL_D, (wx - 4, wy - 2, 9, 7), 1)

    # Yellow + red CARDS peeking from the near breast pocket — stacked, the red
    # a sliver behind the yellow, both bright so they punch through the black at
    # 40px and instantly say "referee" alongside the whistle.
    cx, cy = BCX + 7, BCY - 4
    # Red card sliver behind (offset up-right).
    _poly(surf, _REF_RED_D, [(cx + 2, cy - 6), (cx + 6, cy - 5),
                             (cx + 5, cy + 1), (cx + 1, cy)])
    _poly(surf, _REF_RED, [(cx + 2, cy - 6), (cx + 5, cy - 5),
                           (cx + 4, cy), (cx + 1, cy - 1)])
    # Yellow card in front.
    _poly(surf, _REF_BLACK, [(cx - 3, cy - 5), (cx + 2, cy - 4),
                             (cx + 1, cy + 3), (cx - 4, cy + 2)])   # dark edge
    _poly(surf, _REF_YELLOW, [(cx - 3, cy - 5), (cx + 1, cy - 4),
                              (cx, cy + 2), (cx - 4, cy + 1)])
    pygame.draw.line(surf, _REF_YEL_H, (cx - 3, cy - 5), (cx - 4, cy + 1), 1)


build = store_skins._make_skin(_paint)
