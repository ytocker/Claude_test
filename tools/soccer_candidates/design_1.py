"""DESIGN 1 — THE STRIKER (Soccer / Football).

Scratch exploration only — NOT registered in store_skins.BUILDERS. Pip the
scarlet macaw kitted as a modern outfield striker. The read is carried by the
full LEG KIT: tall knee-high SOCKS with a white hoop band over dark CLEATS at
the feet line. That socks+boots silhouette is the unmistakable football tell
and the deliberate break from the basketball build — a hooper has bare calves
and sneakers, a striker has long socks and studs.

The kit is painted OVER the scarlet body (the head stays the macaw so Pip still
reads as a parrot). A solid jersey carries a single diagonal team SASH + a crisp
white "9" on a cleared plate, with short shorts above the legs. Three cloth
values keep the jersey reading round through the 40px downscale; dark contours
hold every shape. Footprint law: socks+cleats sit on the feet line (~HY+15..27),
nothing balloons the torso or drops below the feet, only a thin sweatband
touches the brow (crown stays open).

Headless render: tools/soccer_candidates/render_design_1.py.
"""
import pygame

from game import store_skins
from game.store_skins import HX, HY, CROWN_Y, _poly


# Scarlet kit (a value above Pip's natural red so the cloth reads as worn, not
# plumage), navy trim, white squad mark, captain gold, near-black cleats. Three
# scarlet values give the jersey roundness; the dark contour survives downscale.
_SOC_RED    = (226, 59, 69)         # #E23B45 jersey scarlet
_SOC_RED_D  = (150, 30, 40)         # cloth shadow / contour
_SOC_RED_H  = (255, 120, 124)       # lit shoulder / chest highlight
_SOC_WHITE  = (244, 244, 248)       # #F4F4F8 white sash / number / sole
_SOC_NAVY   = (27, 42, 107)         # #1B2A6B navy trim / collar / sock body
_SOC_NAVY_D = (16, 25, 64)          # navy shadow / sock contour
_SOC_GOLD   = (255, 206, 84)        # #FFCE54 captain band
_SOC_CLEAT  = (35, 37, 46)          # #23252E cleat
_SOC_CLEAT_H= (78, 84, 102)         # cleat upper sheen


# Body centre in composite space (parrot body centre (32,32) + PARROT_DY=20).
BCX, BCY = 32, 52


def _paint(surf, _a):
    # --- Solid team JERSEY over the torso ---------------------------------------
    # One clean scarlet block clipped to the chest. Top at the shoulders, hem at
    # ~BCY+11 so it stays inside the bird footprint; sleeve caps reach the wing
    # roots so it reads as worn, not a bib. Fill → side shade → lit edge gives
    # the cloth three values so it stays round after the downscale.
    jersey = [(BCX - 15, BCY - 9), (BCX - 16, BCY - 1), (BCX - 14, BCY + 11),
              (BCX + 13, BCY + 11), (BCX + 15, BCY - 1), (BCX + 13, BCY - 9),
              (BCX + 4, BCY - 12), (BCX - 6, BCY - 12)]
    _poly(surf, _SOC_RED, jersey)
    # Far side falls into shadow; near shoulder catches the light.
    _poly(surf, _SOC_RED_D, [(BCX - 15, BCY - 9), (BCX - 16, BCY - 1),
                             (BCX - 14, BCY + 11), (BCX - 8, BCY + 11),
                             (BCX - 9, BCY - 10)])
    _poly(surf, _SOC_RED_H, [(BCX + 4, BCY - 12), (BCX + 13, BCY - 9),
                             (BCX + 15, BCY - 1), (BCX + 9, BCY - 2),
                             (BCX + 6, BCY - 11)])

    # --- Diagonal team SASH across the chest ------------------------------------
    # A single white band running shoulder-to-hip — the modern outfield mark, and
    # what distinguishes it from a stripe-noise jersey. Clipped to the cloth so it
    # never leaks past the contour; a navy edge crisps it for the downscale.
    clip_prev = surf.get_clip()
    surf.set_clip(pygame.Rect(BCX - 16, BCY - 12, 32, 24))
    sash = [(BCX - 16, BCY + 4), (BCX - 13, BCY + 9),
            (BCX + 11, BCY - 11), (BCX + 8, BCY - 13)]
    _poly(surf, _SOC_WHITE, sash)
    pygame.draw.line(surf, _SOC_NAVY, (BCX - 16, BCY + 4), (BCX + 8, BCY - 13), 1)
    pygame.draw.line(surf, _SOC_NAVY, (BCX - 13, BCY + 9), (BCX + 11, BCY - 11), 1)
    surf.set_clip(clip_prev)

    # Re-edge the cloth so the sash stops at the seam, and drop a shoulder-seam
    # line so the sleeves read set-in.
    pygame.draw.polygon(surf, _SOC_RED_D, jersey, 1)
    pygame.draw.line(surf, _SOC_RED_D, (BCX - 13, BCY - 8), (BCX + 11, BCY - 8), 1)

    # Crew collar — a small navy/white notch so the jersey reads as a team shirt.
    _poly(surf, _SOC_NAVY, [(BCX - 5, BCY - 12), (BCX + 4, BCY - 12),
                            (BCX + 2, BCY - 9), (BCX - 3, BCY - 9)])
    pygame.draw.line(surf, _SOC_WHITE, (BCX - 4, BCY - 11), (BCX + 3, BCY - 11), 1)

    # --- Squad NUMBER "9" on a cleared plate ------------------------------------
    # The digit sits low-left so the sash sweeps clear of it. A scarlet plate
    # knocks back the sash/shade behind it so the white reads as a clean number,
    # not a smudge; a dark rim holds the glyph through the downscale.
    nx, ny = BCX - 5, BCY + 3
    pygame.draw.ellipse(surf, _SOC_RED, (nx - 6, ny - 8, 13, 15))
    # Bowl of the 9 (outer dark rim → white ring → red centre).
    pygame.draw.ellipse(surf, _SOC_RED_D, (nx - 4, ny - 7, 9, 8))
    pygame.draw.ellipse(surf, _SOC_WHITE, (nx - 3, ny - 6, 7, 6))
    pygame.draw.ellipse(surf, _SOC_RED, (nx - 1, ny - 4, 3, 3))
    # Tail of the 9 dropping from the bowl's lower-right.
    pygame.draw.line(surf, _SOC_RED_D, (nx + 4, ny - 3), (nx + 1, ny + 6), 4)
    pygame.draw.line(surf, _SOC_WHITE, (nx + 4, ny - 3), (nx + 1, ny + 6), 2)

    # --- Captain's gold ARMBAND on the near (right) wing ------------------------
    # One step brighter than Pip's natural wing patch so it reads as kit; a dark
    # underline crisps it.
    ax, ay = BCX + 13, BCY - 4
    pygame.draw.line(surf, _SOC_NAVY_D, (ax - 4, ay - 5), (ax + 4, ay + 5), 6)
    pygame.draw.line(surf, _SOC_GOLD, (ax - 3, ay - 4), (ax + 3, ay + 4), 4)

    # --- Short SHORTS hem above the legs ----------------------------------------
    # A navy hem band closes the kit between jersey and socks (BCY+11..+14) so the
    # leg kit reads as worn shorts, not bare body, before the socks begin.
    pygame.draw.line(surf, _SOC_NAVY, (BCX - 13, BCY + 12), (BCX + 12, BCY + 12), 3)
    pygame.draw.line(surf, _SOC_NAVY_D, (BCX - 13, BCY + 14), (BCX + 12, BCY + 14), 1)

    # --- Tall team SOCKS + cleats at the feet line (THE soccer read) ------------
    # Knee-high socks + studs are the unmistakable footballer mark — the lower
    # silhouette that separates this from a hooper. Each leg: a tall navy sock
    # (shade + lit faces so the calf reads round) with a white hoop band, then a
    # dark cleat with a white sole + stud ticks. All on the feet line, nothing
    # drops below it, so the bird keeps its true size.
    for fx in (28, 35):
        # Knee-high sock — shaded back face, lit front, dark contour.
        pygame.draw.line(surf, _SOC_NAVY_D, (fx + 1, HY + 15), (fx + 1, HY + 23), 5)
        pygame.draw.line(surf, _SOC_NAVY, (fx, HY + 15), (fx, HY + 23), 3)
        pygame.draw.line(surf, _SOC_NAVY_D, (fx - 2, HY + 15), (fx - 2, HY + 23), 1)
        # White hoop band near the top — the classic kit stripe.
        pygame.draw.line(surf, _SOC_WHITE, (fx - 2, HY + 16), (fx + 1, HY + 16), 4)
        pygame.draw.line(surf, _SOC_NAVY_D, (fx - 2, HY + 18), (fx + 1, HY + 18), 1)
        # Cleat boot hugging the feet line — dark upper + sheen, white sole, studs.
        pygame.draw.ellipse(surf, _SOC_CLEAT_H, (fx - 4, HY + 22, 9, 5))
        pygame.draw.ellipse(surf, _SOC_CLEAT, (fx - 4, HY + 23, 9, 4))
        pygame.draw.line(surf, _SOC_WHITE, (fx - 3, HY + 25), (fx + 3, HY + 25), 1)
        for tx in (fx - 2, fx + 1):
            pygame.draw.line(surf, _SOC_CLEAT, (tx, HY + 26), (tx, HY + 27), 2)

    # --- Thin brow sweatband (keeps the macaw reading, crown open) --------------
    # A slim scarlet band across the brow with a white edge — a sport tell that
    # adds no headgear bulk, so Pip's macaw head stays recognizable.
    pygame.draw.line(surf, _SOC_RED_D, (HX - 11, CROWN_Y + 6), (HX + 12, CROWN_Y + 5), 4)
    pygame.draw.line(surf, _SOC_RED, (HX - 11, CROWN_Y + 5), (HX + 12, CROWN_Y + 4), 2)
    pygame.draw.line(surf, _SOC_WHITE, (HX - 9, CROWN_Y + 4), (HX + 6, CROWN_Y + 3), 1)


build = store_skins._make_skin(_paint)
