"""DESIGN 4 — THE REFEREE (Soccer / Football) — v2.

Scratch exploration only — NOT registered in store_skins.BUILDERS. Pip the
scarlet macaw kitted as the man in the middle: an all-BLACK officials kit —
a black collared shirt with white collar piping, black shorts + socks +
boots — with the hero props drawn LAST so they sit proud of the cloth: a
metal WHISTLE on a lanyard cord that loops the neck and rests on the chest,
and a yellow CARD with a sliver of red card peeking from the breast pocket.
A completely different role and colour-story from any player kit.

v2 fix: the jersey now uses the SAME HX,HY-anchored polygon as the baseball
kit (sports design_4) — top at HY+8 (y=49), hem at HY+23 (y=64) — so the
shirt sits ON the torso instead of riding high-left over the head. NOTHING
in the kit rises above y=49 except the slim officials cap on the crown; there
is NO horizontal band across the brow/crown.

The risk of a black kit on a scarlet bird is that the cloth swallows the body
contour, so the read is carried by crisp WHITE piping + the bright yellow/red
cards + the steel whistle glint — all high-contrast so they survive the 40px
downscale on BOTH day and night.

Headless render: tools/soccer_candidates/render_design_4.py.
"""
import pygame

from game import store_skins
from game.store_skins import HX, HY, CROWN_Y, _poly


# All-black officials kit. Black on the scarlet body needs THREE values so the
# cloth still reads round after downscale: a near-black core, a cool dark grey
# lit plane, and a rim light at the contour. The piping/cards/whistle then do
# the contrast work the black cloth can't.
_REF_BLACK   = (26, 28, 34)         # #1A1C22 referee black (the main jersey fill, sub-40)
_REF_GREY    = (38, 40, 46)         # near-black lit plane (kept a THIN sliver, never blue)
_REF_RIM     = (90, 92, 96)         # neutral (not cool) rim light, 1px on the contour only
_REF_WHITE   = (244, 244, 248)      # #F4F4F8 collar / sock piping
_REF_YELLOW  = (255, 221, 70)       # #FFDD46 yellow card — punched up so it finds the eye on night
_REF_YEL_H   = (255, 240, 150)      # yellow-card glint
_REF_RED     = (224, 56, 44)        # #E0382C red card sliver
_REF_RED_D   = (150, 30, 24)        # red-card edge
_REF_STEEL   = (200, 204, 212)      # #C8CCD4 whistle steel
_REF_STEEL_H = (244, 246, 250)      # whistle hot glint
_REF_STEEL_D = (96, 102, 116)       # whistle steel shadow
_REF_CORD    = (220, 222, 228)      # pale lanyard cord (so it reads on black)


def _paint(surf, _a):
    # --- Black collared ref JERSEY over the torso (THE officials read) -----------
    # SAME polygon shape as the baseball jersey (sports design_4), recolored
    # near-black: top at HY+8 (y=49), hem at HY+23 (y=64). Three cloth values so
    # the black reads ROUND on the scarlet body; nothing rises above y=49.
    jersey = [(HX - 13, HY + 8), (HX - 14, HY + 18), (HX - 10, HY + 23),
              (HX + 8, HY + 23), (HX + 11, HY + 18), (HX + 9, HY + 8)]
    _poly(surf, _REF_BLACK, jersey)
    # Near-black lit plane kept as a THIN 2px sliver on the near (left) edge only —
    # enough to suggest a light source without flooding the torso with a value
    # that reads blue against the scarlet body.
    pygame.draw.line(surf, _REF_GREY, (HX - 12, HY + 9), (HX - 13, HY + 18), 2)
    # Neutral rim light, 1px on the far (right) contour only — pulls the black
    # edge off the body without going cool/blue.
    pygame.draw.line(surf, _REF_RIM, (HX + 9, HY + 8), (HX + 11, HY + 18), 1)
    pygame.draw.line(surf, _REF_RIM, (HX + 11, HY + 18), (HX + 8, HY + 23), 1)
    # Cloth edge so the jersey contour stays crisp.
    pygame.draw.polygon(surf, _REF_BLACK, jersey, 1)

    # White V-collar piping at the jersey top (HY+8..12) — the first contrast hit
    # so the shirt reads as a collared officials top, not a plain black bib.
    pygame.draw.line(surf, _REF_WHITE, (HX - 6, HY + 8), (HX - 1, HY + 13), 2)
    pygame.draw.line(surf, _REF_WHITE, (HX + 5, HY + 8), (HX, HY + 13), 2)
    # White placket flash down the centre seam.
    pygame.draw.line(surf, _REF_WHITE, (HX - 1, HY + 12), (HX - 1, HY + 22), 1)

    # --- Black SHORTS band at the hem (HY+23..26) -------------------------------
    pygame.draw.line(surf, _REF_GREY, (HX - 10, HY + 24), (HX + 8, HY + 24), 4)
    pygame.draw.line(surf, _REF_BLACK, (HX - 10, HY + 26), (HX + 8, HY + 26), 2)

    # --- Black SOCKS + boots at the feet line -----------------------------------
    # Two black sock pillars (HY+13..HY+24) with a single white hoop band near the
    # top (the kit tell), then black boots with a bright white sole stripe so the
    # feet read as boots, not a dark blob, at small sizes.
    for fx in (HX - 9, HX + 1):
        pygame.draw.line(surf, _REF_GREY, (fx + 1, HY + 13), (fx + 1, HY + 24), 5)
        pygame.draw.line(surf, _REF_BLACK, (fx, HY + 13), (fx, HY + 24), 4)
        # White hoop band near the top of the sock.
        pygame.draw.line(surf, _REF_WHITE, (fx - 1, HY + 15), (fx + 1, HY + 15), 2)
        # Boot — black upper + a bright white sole stripe + two stud ticks.
        pygame.draw.ellipse(surf, _REF_GREY, (fx - 4, HY + 23, 9, 5))
        pygame.draw.ellipse(surf, _REF_BLACK, (fx - 4, HY + 24, 9, 4))
        pygame.draw.line(surf, _REF_WHITE, (fx - 3, HY + 25), (fx + 2, HY + 25), 1)
        for tx in (fx - 2, fx + 1):
            pygame.draw.line(surf, _REF_BLACK, (tx, HY + 27), (tx, HY + 28), 2)

    # --- Slim peaked officials CAP on the crown ---------------------------------
    # Adapted from the baseball cap (sports design_4) for black: a small navy
    # shell becomes a near-black officials cap with one rim-light edge + a short
    # forward brim. NO horizontal band crosses the brow — the shell sits ON TOP.
    cy = CROWN_Y - 3
    # FLATTENED crown ellipse (height 9 vs the old 12) so the shell reads as a
    # low peaked-cap dome, not a tall round bowler.
    pygame.draw.ellipse(surf, _REF_BLACK, (HX - 11, cy - 1, 22, 9))
    pygame.draw.ellipse(surf, _REF_BLACK, (HX - 11, cy - 1, 22, 9), 1)
    pygame.draw.ellipse(surf, _REF_GREY, (HX - 6, cy, 9, 4))   # top sheen
    pygame.draw.line(surf, _REF_RIM, (HX - 5, cy, ), (HX + 4, cy), 1)
    # Longer forward brim (2px more reach) projecting over the beak, with a hard
    # bright rim-light line on the leading edge so the silhouette reads as an
    # official's peaked cap rather than a round hat.
    brim = [(HX + 3, cy + 5), (HX + 17, cy + 4), (HX + 18, cy + 7),
            (HX + 4, cy + 8)]
    _poly(surf, _REF_BLACK, brim)
    _poly(surf, _REF_GREY, [(HX + 4, cy + 7), (HX + 18, cy + 7),
                            (HX + 17, cy + 8), (HX + 4, cy + 8)])
    # Hard bright rim-light along the brim's leading edge — the peaked-cap tell.
    pygame.draw.line(surf, _REF_WHITE, (HX + 5, cy + 4), (HX + 17, cy + 4), 1)

    # --- HERO PROPS, drawn LAST so they sit IN FRONT of the cloth ----------------
    # Cards and whistle are split to OPPOSITE chest quadrants so two separated
    # bright marks each read as their own thing instead of piling into noise.
    # Whistle dead-CENTRE on the lanyard V; cards on the LEFT breast below.

    # Whistle on a lanyard: two pale-cord lines from the neck V-ing down to a
    # silver disc resting at chest centre. The neck base sits at the jersey top.
    nlx, nly = HX, HY + 8                            # neck base of the lanyard
    wx, wy = HX, HY + 14                             # whistle at chest centre
    pygame.draw.line(surf, _REF_CORD, (nlx - 5, nly), (wx, wy - 3), 2)
    pygame.draw.line(surf, _REF_CORD, (nlx + 5, nly), (wx, wy - 3), 2)

    # Steel WHISTLE disc on the chest — THE referee prop. A full dark contour
    # rings the steel so it separates from BOTH the black cloth and the scarlet
    # body, surviving the NIGHT swatch as a clear bright dot.
    pygame.draw.ellipse(surf, _REF_STEEL_D, (wx - 6, wy - 3, 12, 10))   # dark contour ring
    pygame.draw.ellipse(surf, _REF_STEEL, (wx - 5, wy - 2, 11, 9))      # steel body
    # Mouthpiece nub on the near side.
    _poly(surf, _REF_STEEL, [(wx + 5, wy + 1), (wx + 8, wy + 2), (wx + 5, wy + 4)])
    pygame.draw.line(surf, _REF_STEEL_D, (wx + 5, wy + 4), (wx + 8, wy + 2), 1)
    # Hot glint — the single brightest pixels, sells metal.
    pygame.draw.rect(surf, _REF_STEEL_H, (wx - 3, wy - 1, 2, 2))
    pygame.draw.ellipse(surf, _REF_STEEL_D, (wx - 6, wy - 3, 12, 10), 1)

    # Yellow + red CARDS on the LEFT breast (x=HX-7), well clear of the centred
    # whistle — a fat near-upright bright yellow rectangle with the red card a
    # sliver behind, both bright so they punch through the black at 40px and
    # instantly say "referee".
    cx, cyy = HX - 7, HY + 11
    # Red card sliver behind, peeking to the near side.
    _poly(surf, _REF_RED_D, [(cx - 4, cyy - 1), (cx + 1, cyy - 2),
                             (cx + 2, cyy + 4), (cx - 3, cyy + 5)])
    _poly(surf, _REF_RED, [(cx - 3, cyy - 1), (cx + 1, cyy - 2),
                           (cx + 2, cyy + 3), (cx - 2, cyy + 4)])
    # Yellow card in front — the TALLEST non-cap element (yt=HY+8 .. yb=HY+18) so
    # the eye lands on it first. A 1px BLACK halo rings ALL FOUR sides so the
    # bright yellow separates from red, black cloth and scarlet body on night.
    yl, yr, yt, yb = cx - 2, cx + 4, cyy - 3, cyy + 7
    pygame.draw.rect(surf, _REF_BLACK, (yl - 1, yt - 1, (yr - yl) + 2, (yb - yt) + 2))
    _poly(surf, _REF_YELLOW, [(yl, yt), (yr, yt), (yr, yb), (yl, yb)])  # fat yellow face
    # Glint down the lit (near) edge + knocked corners so the card reads round.
    pygame.draw.line(surf, _REF_YEL_H, (yl + 1, yt + 1), (yl + 1, yb - 1), 1)
    surf.set_at((yl, yt), _REF_BLACK)
    surf.set_at((yr, yb), _REF_BLACK)


build = store_skins._make_skin(_paint)
