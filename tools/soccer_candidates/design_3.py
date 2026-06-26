"""DESIGN 3 — THE NÚMERO 10 (Soccer / Football, retro legend).

Scratch exploration only — NOT registered in store_skins.BUILDERS. Pip the
scarlet macaw kitted as a vintage international glory legend: a classic
sky-blue, long-sleeve COTTON jersey with a laced V-collar at the neck (the era
tell), an old-school embroidered crest patch on the near chest, the iconic big
retro "10" low on the shirt, and classic high socks with a fold-over top band
over low retro boots. No headgear (crown stays open) so the era reads clean.

The jersey is painted OVER the scarlet body (head stays the macaw so Pip still
reads as a parrot). The laced collar + crest + long sleeves are what separate
this from the modern Striker — it must read as a DIFFERENT ERA of football.
All kit is held INSIDE the base bird footprint: socks + boots sit on the feet
line (~HY+15..27), nothing balloons the torso or drops below the feet.
"""
import pygame

from game import store_skins
from game.store_skins import HX, HY, CROWN_Y, _poly


# Sky-blue retro cotton kit. Three cloth values so the laced collar, crest and
# big "10" still separate from the jersey field after the 40px downscale, and
# the long sleeves read as set-in. Cotton, not satin — the values sit closer
# together than the modern Striker's, which is part of the nostalgic read.
_RET_SKY     = (28, 111, 224)       # #1C6FE0 jersey sky-blue (cotton mid)
_RET_SKY_D   = (16, 66, 142)        # cloth shadow / seams / line work
_RET_SKY_H   = (96, 158, 244)       # sleeve / collar highlight
_RET_WHITE   = (244, 244, 248)      # #F4F4F8 number / collar trim
_RET_RED     = (194, 57, 43)        # #C2392B retro crest field
_RET_RED_D   = (126, 34, 26)        # crest shadow / outline
_RET_GOLD    = (231, 194, 74)       # #E7C24A lace cord / crest scroll
_RET_GOLD_H  = (250, 226, 150)      # lace glint
_RET_GOLD_D  = (120, 96, 30)        # crisp dark underline so gold reads as kit
_RET_BOOT    = (35, 37, 46)         # #23252E low retro boot
_RET_BOOT_H  = (78, 84, 102)        # boot upper highlight


# Body centre in composite space (parrot body centre (32,32) + PARROT_DY=20).
BCX, BCY = 32, 52


def _paint(surf, _a):
    # --- Long-sleeve cotton JERSEY over the torso (THE retro read) --------------
    # A clean jersey block clipped to the chest, filled sky-blue. Held inside the
    # footprint (shoulders ~BCY-12, hem ~BCY+12). The hem dips slightly lower than
    # the Striker's so the big "10" has room to sit LOW on the shirt — the retro
    # placement, not high-centre like a modern squad number.
    jersey = [(BCX - 15, BCY - 9), (BCX - 16, BCY - 1), (BCX - 14, BCY + 12),
              (BCX + 13, BCY + 12), (BCX + 15, BCY - 1), (BCX + 13, BCY - 9),
              (BCX + 4, BCY - 12), (BCX - 6, BCY - 12)]
    _poly(surf, _RET_SKY, jersey)

    # Long SLEEVES — the era tell vs the modern short-sleeve Striker. A set-in
    # sleeve cap with a darker seam at each shoulder, carried down the near wing
    # so the cloth reads as a full long sleeve, not a tank cut.
    for sx, seam in ((BCX - 15, BCX - 13), (BCX + 13, BCX + 11)):
        pygame.draw.line(surf, _RET_SKY_D, (seam, BCY - 9), (seam, BCY + 6), 1)
    # Cuffs at the wing roots — a hooped band closing each long sleeve.
    for cx, sgn in ((BCX - 14, -1), (BCX + 13, 1)):
        pygame.draw.line(surf, _RET_WHITE, (cx, BCY + 3), (cx + sgn * 3, BCY + 6), 2)

    # Shoulder-seam shadow + re-edge the jersey contour.
    pygame.draw.line(surf, _RET_SKY_D, (BCX - 12, BCY - 8), (BCX + 10, BCY - 8), 1)
    pygame.draw.polygon(surf, _RET_SKY_D, jersey, 1)
    # A soft vertical highlight down the chest so the cotton reads rounded.
    pygame.draw.line(surf, _RET_SKY_H, (BCX - 7, BCY - 7), (BCX - 7, BCY + 6), 1)

    # --- Laced V-COLLAR at the neck (THE era tell) ------------------------------
    # A short laced placket: a white V-collar notch, then a gold lace cord
    # cross-hatched across it with eyelets either side. This must survive the
    # downscale, so the V is a cleared white wedge (high contrast) and the laces
    # are 2 bold gold cross-ticks — readable as "laced collar" even at 40px.
    cy = BCY - 11
    # White V-collar wedge sitting in the neck gap.
    collar = [(BCX - 5, cy), (BCX + 4, cy), (BCX + 1, cy + 6), (BCX - 2, cy + 6)]
    _poly(surf, _RET_WHITE, collar)
    pygame.draw.polygon(surf, _RET_SKY_D, collar, 1)
    # The dark placket slit down the centre of the V (where the lacing closes).
    pygame.draw.line(surf, _RET_SKY_D, (BCX, cy + 1), (BCX - 1, cy + 6), 1)
    # Eyelets — two dark dots either side of the slit.
    for ex in (BCX - 2, BCX + 2):
        pygame.draw.line(surf, _RET_GOLD_D, (ex, cy + 2), (ex, cy + 5), 1)
    # Gold lace cord — bold cross-ticks (an X over the slit) so it reads laced.
    pygame.draw.line(surf, _RET_GOLD, (BCX - 2, cy + 2), (BCX + 2, cy + 4), 1)
    pygame.draw.line(surf, _RET_GOLD, (BCX + 2, cy + 2), (BCX - 2, cy + 4), 1)
    pygame.draw.line(surf, _RET_GOLD_H, (BCX - 2, cy + 2), (BCX, cy + 3), 1)

    # --- Embroidered CREST patch on the near chest ------------------------------
    # A small but crisp shield (woven, not printed): red field, gold scroll edge,
    # a white chevron inside. Sits high on the near (right) chest, above the "10".
    crx, cry = BCX + 6, BCY - 3
    shield = [(crx - 3, cry - 4), (crx + 3, cry - 4), (crx + 4, cry),
              (crx, cry + 5), (crx - 4, cry)]
    _poly(surf, _RET_GOLD_D, [(p[0], p[1] + 1) for p in shield])   # drop shadow
    _poly(surf, _RET_RED, shield)
    pygame.draw.polygon(surf, _RET_GOLD, shield, 1)                # woven gold edge
    # White chevron device inside the shield (the "embroidery").
    pygame.draw.line(surf, _RET_WHITE, (crx - 2, cry - 1), (crx, cry + 1), 1)
    pygame.draw.line(surf, _RET_WHITE, (crx + 2, cry - 1), (crx, cry + 1), 1)
    pygame.draw.line(surf, _RET_RED_D, (crx - 3, cry - 3), (crx + 3, cry - 3), 1)

    # --- Big retro "10" low on the shirt ----------------------------------------
    # The iconic number, set LOW and large in white with a crisp dark edge so the
    # two digits stay separate after the downscale. Sits below the crest, centred
    # a touch left so it doesn't collide with the chest crest.
    nx, ny = BCX - 1, BCY + 6
    # "1" — a bold vertical stroke with a serif foot, the retro style.
    pygame.draw.line(surf, _RET_SKY_D, (nx - 4, ny - 5), (nx - 4, ny + 5), 4)
    pygame.draw.line(surf, _RET_WHITE, (nx - 4, ny - 5), (nx - 4, ny + 5), 2)
    pygame.draw.line(surf, _RET_WHITE, (nx - 6, ny + 5), (nx - 2, ny + 5), 1)
    pygame.draw.line(surf, _RET_WHITE, (nx - 5, ny - 5), (nx - 3, ny - 6), 1)
    # "0" — a bold white oval with a knocked-out sky-blue centre + dark edge.
    pygame.draw.ellipse(surf, _RET_SKY_D, (nx, ny - 6, 9, 12))
    pygame.draw.ellipse(surf, _RET_WHITE, (nx + 1, ny - 5, 7, 10))
    pygame.draw.ellipse(surf, _RET_SKY, (nx + 3, ny - 3, 3, 6))

    # --- High SOCKS with fold-over top band + low retro boots -------------------
    # Classic pulled-up socks: a tall sky-blue sock, a contrasting fold-over band
    # near the top (white turn-down) — the unmistakable retro footballer mark —
    # then a low dark boot hugging the feet line. Everything sits ON the feet line
    # (~HY+15..27), nothing drops below it, so the bird keeps its true size.
    for fx in (28, 35):
        # Tall sock — taller than a band so it reads as a pulled-up retro sock.
        pygame.draw.line(surf, _RET_SKY_D, (fx + 1, HY + 15), (fx + 1, HY + 23), 5)
        pygame.draw.line(surf, _RET_SKY, (fx, HY + 15), (fx, HY + 23), 4)
        # Fold-over top band — a chunky white turn-down at the top of the sock.
        pygame.draw.line(surf, _RET_WHITE, (fx - 1, HY + 15), (fx + 1, HY + 15), 5)
        pygame.draw.line(surf, _RET_SKY_D, (fx - 1, HY + 17), (fx + 1, HY + 17), 1)
        # Low retro boot — a flat dark toe-cap at the feet line, no high cleats.
        pygame.draw.ellipse(surf, _RET_BOOT_H, (fx - 4, HY + 22, 9, 5))
        pygame.draw.ellipse(surf, _RET_BOOT, (fx - 4, HY + 23, 9, 4))
        # White boot stripe + a heel toe-cap line — the old leather-boot detail.
        pygame.draw.line(surf, _RET_WHITE, (fx - 3, HY + 24), (fx + 2, HY + 24), 1)
        pygame.draw.line(surf, _RET_BOOT, (fx - 4, HY + 25), (fx + 4, HY + 25), 1)


build = store_skins._make_skin(_paint)
