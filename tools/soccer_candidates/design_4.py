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
_REF_BLACK   = (26, 28, 34)         # #1A1C22 referee black (core)
_REF_GREY    = (52, 56, 66)         # cool dark grey lit plane (mid value)
_REF_RIM     = (108, 116, 132)      # cool rim light at the cloth edge
_REF_WHITE   = (244, 244, 248)      # #F4F4F8 collar / sock piping
_REF_YELLOW  = (255, 210, 59)       # #FFD23B yellow card
_REF_YEL_H   = (255, 232, 138)      # yellow-card glint
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
    # Cool grey lit plane down the near (left) chest so a light source reads on
    # the black cloth instead of a flat silhouette.
    _poly(surf, _REF_GREY, [(HX - 12, HY + 9), (HX - 4, HY + 9),
                            (HX - 6, HY + 22), (HX - 11, HY + 21)])
    # Rim light along the far (right) side edge — the cool highlight that pulls
    # the black contour off the scarlet body at small sizes. 2px so it survives
    # the NIGHT swatch.
    pygame.draw.line(surf, _REF_RIM, (HX + 9, HY + 8), (HX + 11, HY + 18), 2)
    pygame.draw.line(surf, _REF_RIM, (HX + 11, HY + 18), (HX + 8, HY + 23), 2)
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
    pygame.draw.ellipse(surf, _REF_BLACK, (HX - 11, cy - 4, 22, 12))
    pygame.draw.ellipse(surf, _REF_BLACK, (HX - 11, cy - 4, 22, 12), 1)
    pygame.draw.ellipse(surf, _REF_GREY, (HX - 6, cy - 3, 9, 5))   # top sheen
    pygame.draw.line(surf, _REF_RIM, (HX - 5, cy - 3), (HX + 4, cy - 3), 1)
    # Short forward brim projecting over the beak — the cap tell, kept SHORT so
    # it doesn't crowd the beak.
    brim = [(HX + 3, cy + 5), (HX + 15, cy + 4), (HX + 16, cy + 7),
            (HX + 4, cy + 8)]
    _poly(surf, _REF_BLACK, brim)
    _poly(surf, _REF_GREY, [(HX + 4, cy + 7), (HX + 16, cy + 7),
                            (HX + 15, cy + 8), (HX + 4, cy + 8)])

    # --- HERO PROPS, drawn LAST so they sit IN FRONT of the cloth ----------------
    # Whistle on a lanyard: two pale-cord lines from the neck V-ing down to a
    # silver disc resting on the chest. The neck base sits at the jersey top.
    nlx, nly = HX, HY + 8                            # neck base of the lanyard
    wx, wy = HX - 2, HY + 14                         # whistle resting point on chest
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

    # Yellow + red CARDS from the breast pocket — a fat near-upright bright
    # yellow rectangle with the red card a sliver behind, both bright so they
    # punch through the black at 40px and instantly say "referee".
    cx, cyy = HX + 3, HY + 11
    # Red card sliver behind.
    _poly(surf, _REF_RED_D, [(cx + 3, cyy - 2), (cx + 8, cyy - 1),
                             (cx + 7, cyy + 5), (cx + 2, cyy + 4)])
    _poly(surf, _REF_RED, [(cx + 3, cyy - 2), (cx + 7, cyy - 1),
                           (cx + 6, cyy + 4), (cx + 2, cyy + 3)])
    # Yellow card in front — fat near-upright rounded rect (HY+9..14). Dark edge
    # first so the yellow contour separates from both red and black.
    yl, yr, yt, yb = cx - 4, cx + 2, cyy - 2, cyy + 5
    _poly(surf, _REF_BLACK, [(yl, yt), (yr, yt - 1), (yr + 1, yb - 1),
                             (yl, yb)])                      # dark edge halo
    _poly(surf, _REF_YELLOW, [(yl + 1, yt), (yr, yt), (yr, yb - 1),
                              (yl + 1, yb - 1)])             # fat yellow face
    # Glint down the lit (near) edge + knocked corners so the card reads round.
    pygame.draw.line(surf, _REF_YEL_H, (yl + 1, yt + 1), (yl + 1, yb - 2), 1)
    surf.set_at((yl + 1, yt), _REF_BLACK)
    surf.set_at((yr, yb - 1), _REF_BLACK)


build = store_skins._make_skin(_paint)
