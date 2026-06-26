"""DESIGN 1 — THE STRIKER (Soccer / Football), v2.

Scratch exploration only — NOT registered in store_skins.BUILDERS, so production
is untouched. Pip the scarlet macaw kitted as a modern outfield striker.

v2 fix: the kit now hangs off the HEAD anchor (HX,HY) instead of the old body
centre, using the EXACT jersey polygon proven on the baseball SLUGGER build —
top at y=HY+8 (=49), hem at HY+23 (=64). That seats the shirt cleanly BELOW the
macaw head; nothing rises above y=49 into the face. NO headband — soccer players
wear no forehead band, so the crown stays open like the ball-cap baseball look.

The read is carried by (1) a vivid scarlet-orange jersey with a bold white "9"
and a diagonal gold sash — louder/more orange than macaw plumage so it reads as
worn cloth, and (2) the full LEG KIT below the hem: two tall navy knee-high
socks (each with a white hoop) dropping into dark forward-pointing boots. That
socks+boots silhouette is the unmistakable football tell. Three cloth values
keep the jersey round at 40px; a dark-navy contour ring holds the shape through
the downscale.
"""
import pygame

from game import store_skins
from game.store_skins import HX, HY, CROWN_Y, _poly


# Scarlet-ORANGE kit (pushed orange so it separates from Pip's red plumage and
# reads as a worn shirt), gold sash, white squad mark, dark-navy trim + socks,
# near-black boots. Three jersey values give roundness; the navy contour and the
# sock rim-light survive the downscale on both day and night sky.
_SOC_ORN    = (232, 82, 30)         # #E8521E scarlet-orange jersey body
_SOC_ORN_D  = (158, 46, 14)         # cloth shadow / contour ring
_SOC_ORN_H  = (255, 138, 78)        # lit shoulder / chest highlight
_SOC_WHITE  = (244, 244, 248)       # #F4F4F8 squad number / hoops / sole tick
_SOC_GOLD   = (244, 198, 86)        # #F4C656 diagonal shoulder sash
_SOC_GOLD_H = (255, 228, 150)       # sash glint
_SOC_NAVY   = (27, 42, 107)         # #1B2A6B shorts band + sock body + contour
_SOC_NAVY_D = (15, 23, 60)          # near-black sock core / navy shadow
_SOC_NAVY_H = (74, 98, 184)         # sock lit face / outer rim-light
_SOC_BOOT   = (32, 34, 44)          # near-black boot
_SOC_BOOT_H = (90, 96, 114)         # boot instep sheen


def _sock_and_boot(surf, fx, lit_side):
    """One navy knee-high sock as a tall solid pillar + a forward-pointing boot
    wedge under it. `lit_side` (+1 light from the right / -1) steers the rim-light
    onto the OUTER calf edge so neither leg vanishes on night sky. Built as filled
    polys so each leg holds as a distinct vertical column after the 40px downscale.
    Spans HY+13..HY+24 so the calves emerge from under the shorts hem and the boot
    pokes the lower outline like the baseball cleats."""
    top, bot = HY + 13, HY + 24      # knee-under-hem to ankle (y=54..65)
    # Near-black core pillar (narrow tapered column) under everything, contour-
    # shifted to the outer side so the column reads round, not flat.
    core = [(fx - 3, top), (fx + 3, top), (fx + 2, bot), (fx - 2, bot)]
    _poly(surf, _SOC_NAVY_D, [(x - lit_side, y) for x, y in core])   # contour
    _poly(surf, _SOC_NAVY, core)
    # Lit mid-navy front face down the inner column so the calf reads cylindrical.
    face = [(fx, top), (fx + lit_side * 3, top),
            (fx + lit_side * 2, bot), (fx, bot)]
    _poly(surf, _SOC_NAVY_H, face)
    # White hoop band near the sock top — the classic kit stripe, full calf width.
    hb = top + 3
    pygame.draw.line(surf, _SOC_WHITE, (fx - 3, hb), (fx + 3, hb), 2)
    pygame.draw.line(surf, _SOC_NAVY_D, (fx - 3, hb + 2), (fx + 3, hb + 2), 1)
    # Rim-light tracing the OUTER calf edge so the sock holds on the night sky.
    rx = fx + lit_side * 3
    pygame.draw.line(surf, _SOC_NAVY_H, (rx, top + 1), (rx - lit_side, bot - 1), 1)

    # Forward-pointing BOOT WEDGE — a compact dark cleat, toe to the FORWARD
    # (right) side, with one bright sole tick beneath. Mirrors the SLUGGER cleat
    # placement: short + only just wider than the calf so the two boots stay
    # separate and never bridge into a single bar.
    ax, ay = fx, bot
    wedge = [(ax - 3, ay - 1), (ax + 1, ay - 1), (ax + 5, ay + 2),
             (ax + 4, ay + 4), (ax - 3, ay + 4)]
    _poly(surf, (12, 13, 18), [(x, y + 1) for x, y in wedge])        # drop shadow
    _poly(surf, _SOC_BOOT, wedge)
    pygame.draw.line(surf, _SOC_BOOT_H, (ax - 2, ay), (ax + 3, ay + 1), 1)  # instep
    pygame.draw.line(surf, _SOC_WHITE, (ax - 3, ay + 4), (ax + 4, ay + 4), 1)  # sole tick


def _paint(surf, _a):
    # ── LEG KIT first (socks + boots) so the navy shorts band laps over the sock
    #    tops and the legs read as worn UNDER the shorts. Two distinct pillars at
    #    the feet line; outer edge of each is rim-lit so neither sock vanishes.
    _sock_and_boot(surf, HX - 10, lit_side=-1)   # far leg, rim-light on its left
    _sock_and_boot(surf, HX + 1,  lit_side=+1)   # near leg, rim-light on its right

    # ── JERSEY — the EXACT baseball-SLUGGER polygon at the HX,HY anchor (top
    #    y=HY+8=49, hem y=HY+23=64), so the shirt seats cleanly BELOW the head and
    #    nothing rises into the face. Scarlet-orange fill → off-side shade → near
    #    shoulder highlight gives the cloth three values so it stays round at 40px.
    jersey = [(HX - 13, HY + 8), (HX - 14, HY + 18), (HX - 10, HY + 23),
              (HX + 8, HY + 23), (HX + 11, HY + 18), (HX + 9, HY + 8)]
    _poly(surf, _SOC_ORN, jersey)
    _poly(surf, _SOC_ORN_D, [(HX + 4, HY + 9), (HX + 11, HY + 18),
                             (HX + 8, HY + 23), (HX + 5, HY + 22)])   # off-side shade
    _poly(surf, _SOC_ORN_H, [(HX - 12, HY + 9), (HX - 6, HY + 9),
                             (HX - 7, HY + 14), (HX - 13, HY + 13)])  # lit shoulder

    # ── DIAGONAL GOLD shoulder sash, shoulder-to-hip — the modern outfield mark.
    #    Clipped to the jersey box so it never leaks past the contour; a glint line
    #    keeps it bright against the night sky.
    clip_prev = surf.get_clip()
    surf.set_clip(pygame.Rect(HX - 14, HY + 7, 26, 17))
    sash = [(HX - 13, HY + 16), (HX - 11, HY + 21),
            (HX + 9, HY + 9), (HX + 7, HY + 8)]
    _poly(surf, _SOC_GOLD, sash)
    pygame.draw.line(surf, _SOC_GOLD_H, (HX - 12, HY + 16), (HX + 8, HY + 8), 1)
    surf.set_clip(clip_prev)

    # ── Navy crew COLLAR + dark contour RING so the jersey reads as a team shirt
    #    and the whole shape crisps at the downscale.
    _poly(surf, _SOC_NAVY, [(HX - 4, HY + 7), (HX + 4, HY + 7),
                            (HX + 2, HY + 10), (HX - 2, HY + 10)])
    pygame.draw.line(surf, _SOC_WHITE, (HX - 3, HY + 8), (HX + 3, HY + 8), 1)
    pygame.draw.polygon(surf, _SOC_ORN_D, jersey, 1)

    # ── Bold white squad "9" at mid-chest (HX-2 column, HY+13..18) — the ONE
    #    white focal up top. A loop bowl over a short tail, fattened so it survives
    #    downscale; an orange shadow plate behind it lifts it off the cloth.
    nx, ny = HX - 2, HY + 13
    pygame.draw.ellipse(surf, _SOC_ORN_D, (nx - 4, ny - 1, 9, 8))     # shadow plate
    pygame.draw.ellipse(surf, _SOC_WHITE, (nx - 3, ny - 1, 7, 6))     # bowl ring
    pygame.draw.ellipse(surf, _SOC_ORN,  (nx - 1, ny + 1, 3, 3))      # bowl hole
    pygame.draw.line(surf, _SOC_WHITE, (nx + 3, ny + 1), (nx + 1, ny + 7), 2)  # tail

    # ── SHORTS — a dark-navy band just below the jersey hem (HY+23..26) so a
    #    shorts-hem shows between shirt and socks. A scalloped pair of hem dips
    #    between the legs sells the two-leg read.
    _poly(surf, _SOC_NAVY, [(HX - 10, HY + 22), (HX + 8, HY + 22),
                            (HX + 7, HY + 26), (HX + 2, HY + 25),
                            (HX - 1, HY + 27), (HX - 4, HY + 25),
                            (HX - 9, HY + 26)])
    pygame.draw.line(surf, _SOC_NAVY_D, (HX - 10, HY + 23), (HX + 8, HY + 23), 1)
    pygame.draw.line(surf, _SOC_NAVY_H, (HX - 9, HY + 23), (HX + 6, HY + 23), 1)


build = store_skins._make_skin(_paint)
