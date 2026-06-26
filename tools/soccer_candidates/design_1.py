"""DESIGN 1 — THE STRIKER (Soccer / Football), v2.

Scratch exploration only — NOT registered in store_skins.BUILDERS, so production
is untouched. Pip the scarlet macaw kitted as a modern outfield striker.

v2 fix: the kit now hangs off the HEAD anchor (HX,HY) instead of the old body
centre, using the EXACT jersey polygon proven on the baseball SLUGGER build —
top at y=HY+8 (=49), hem at HY+23 (=64). That seats the shirt cleanly BELOW the
macaw head; nothing rises above y=49 into the face. NO headband — soccer players
wear no forehead band, so the crown stays open like the ball-cap baseball look.

R2 fix (kills the macaw-on-macaw camouflage the R1 orange jersey caused):
- Jersey is now a COOL ROYAL BLUE (#1B4FC8). Blue is maximally far from the
  scarlet plumage in hue AND value, so the shirt mass reads as worn cloth on
  both day and night sky instead of melting into the bird. A 1px bright-white
  contour rings the whole jersey so the silhouette crisps at the 40px downscale.
- The squad number is a BOLD FLAT-FILL BLOCK "9" on a white plate (white panel,
  navy numeral), ~6px tall, centred at HX-2 / HY+13..18, so it stays a legible
  glyph after downscale instead of a thin loop that vanishes.
- The LEG KIT is rebuilt for night: two navy socks with a BRIGHT WHITE sock-top
  hoop, a guaranteed bare-body gap between the two sock pillars, and a lifted
  navy value (#2C46B0) on the outer calf so the legs hold against night sky.
- The sash is kept but loud — a 3px GOLD diagonal (#E8B23A) over a dark underlay,
  now crossing the dark-blue jersey with real contrast.
"""
import pygame

from game import store_skins
from game.store_skins import HX, HY, CROWN_Y, _poly


# Royal-blue kit (cool blue is maximally separated from Pip's red plumage in both
# hue and value, so the shirt reads as cloth, not bird). Gold sash, white squad
# plate, navy trim + socks, near-black boots. Three jersey values give roundness;
# a bright-white contour + lifted sock navy survive the downscale on day + night.
_SOC_BLUE   = (27, 79, 200)         # #1B4FC8 royal-blue jersey body
_SOC_BLUE_D = (16, 46, 124)         # #102E7C cloth shadow / off-side shade
_SOC_BLUE_H = (86, 138, 246)        # #568AF6 lit shoulder / chest highlight
_SOC_WHITE  = (244, 244, 248)       # #F4F4F8 contour + number plate + hoops
_SOC_GOLD   = (232, 178, 58)        # #E8B23A diagonal shoulder sash
_SOC_GOLD_H = (255, 222, 130)       # sash glint
_SOC_NAVY   = (22, 32, 78)          # #16204E sock body / collar / number glyph
_SOC_NAVY_D = (12, 17, 44)          # near-black sock core / shadow plate
_SOC_NAVY_H = (44, 70, 176)         # #2C46B0 lifted sock outer rim (holds on night)
_SOC_BOOT   = (32, 34, 44)          # near-black boot
_SOC_BOOT_H = (90, 96, 114)         # boot instep sheen


def _sock_and_boot(surf, fx, lit_side):
    """One navy knee-high sock as a tall solid pillar + a forward-pointing boot
    wedge under it. `lit_side` (+1 light from the right / -1) steers the lifted
    rim-light onto the OUTER calf edge so neither leg vanishes on night sky. Built
    as filled polys so each leg holds as a distinct vertical column after the 40px
    downscale; the two callers leave a bare-body gap between the pillars so the
    legs never bridge into a single bar. Spans HY+13..HY+24."""
    top, bot = HY + 13, HY + 24      # knee-under-hem to ankle (y=54..65)
    # Near-black core pillar (narrow tapered column) under everything, contour-
    # shifted to the outer side so the column reads round, not flat.
    core = [(fx - 3, top), (fx + 3, top), (fx + 2, bot), (fx - 2, bot)]
    _poly(surf, _SOC_NAVY_D, [(x - lit_side, y) for x, y in core])   # contour
    _poly(surf, _SOC_NAVY, core)
    # Lifted-navy lit face down the outer column so the calf reads cylindrical AND
    # the bright edge survives the night downscale instead of crushing to black.
    face = [(fx, top), (fx + lit_side * 3, top),
            (fx + lit_side * 2, bot), (fx, bot)]
    _poly(surf, _SOC_NAVY_H, face)
    # BRIGHT WHITE sock-top hoop — the classic kit stripe, full calf width, made a
    # fat 2px band so it reads as the brightest cue on the dark leg at 40px night.
    hb = top + 2
    pygame.draw.line(surf, _SOC_WHITE, (fx - 3, hb), (fx + 3, hb), 2)
    pygame.draw.line(surf, _SOC_NAVY_D, (fx - 3, hb + 2), (fx + 3, hb + 2), 1)
    # Lifted rim-light tracing the OUTER calf edge so the sock holds on night sky.
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
    #    tops and the legs read as worn UNDER the shorts. Two distinct pillars with
    #    a guaranteed >=3px bare-body gap between them (HX-11 and HX+3 cores sit ~8px
    #    apart at the calf), each outer edge rim-lit so neither sock vanishes.
    _sock_and_boot(surf, HX - 11, lit_side=-1)   # far leg, rim-light on its left
    _sock_and_boot(surf, HX + 3,  lit_side=+1)   # near leg, rim-light on its right

    # ── JERSEY — the EXACT baseball-SLUGGER polygon at the HX,HY anchor (top
    #    y=HY+8=49, hem y=HY+23=64), so the shirt seats cleanly BELOW the head and
    #    nothing rises into the face. Royal-blue fill → off-side shade → near
    #    shoulder highlight gives the cloth three values so it stays round at 40px.
    jersey = [(HX - 13, HY + 8), (HX - 14, HY + 18), (HX - 10, HY + 23),
              (HX + 8, HY + 23), (HX + 11, HY + 18), (HX + 9, HY + 8)]
    _poly(surf, _SOC_BLUE, jersey)
    _poly(surf, _SOC_BLUE_D, [(HX + 4, HY + 9), (HX + 11, HY + 18),
                              (HX + 8, HY + 23), (HX + 5, HY + 22)])   # off-side shade
    _poly(surf, _SOC_BLUE_H, [(HX - 12, HY + 9), (HX - 6, HY + 9),
                              (HX - 7, HY + 14), (HX - 13, HY + 13)])  # lit shoulder

    # ── DIAGONAL GOLD shoulder sash, shoulder-to-hip — the modern outfield mark.
    #    Clipped to the jersey box so it never leaks past the contour; a dark
    #    underlay + bright glint keep the 3px gold reading on the night sky.
    clip_prev = surf.get_clip()
    surf.set_clip(pygame.Rect(HX - 14, HY + 7, 26, 17))
    sash = [(HX - 13, HY + 16), (HX - 10, HY + 22),
            (HX + 9, HY + 9), (HX + 6, HY + 8)]
    _poly(surf, _SOC_NAVY_D, [(x, y + 1) for x, y in sash])          # dark underlay
    _poly(surf, _SOC_GOLD, sash)
    pygame.draw.line(surf, _SOC_GOLD_H, (HX - 12, HY + 16), (HX + 8, HY + 8), 1)
    surf.set_clip(clip_prev)

    # ── Navy crew COLLAR + bright-WHITE contour RING so the jersey reads as a team
    #    shirt and the whole shape crisps at the downscale against any sky.
    _poly(surf, _SOC_NAVY, [(HX - 4, HY + 7), (HX + 4, HY + 7),
                            (HX + 2, HY + 10), (HX - 2, HY + 10)])
    pygame.draw.line(surf, _SOC_WHITE, (HX - 3, HY + 8), (HX + 3, HY + 8), 1)
    pygame.draw.polygon(surf, _SOC_WHITE, jersey, 1)

    # ── Bold BLOCK squad "9" at mid-chest — a navy numeral on a white plate so the
    #    glyph stays legible (high value contrast both ways) after the 40px
    #    downscale, replacing the thin loop that vanished. Plate ~8x9, numeral ~6px.
    nx, ny = HX - 2, HY + 13
    pygame.draw.rect(surf, _SOC_NAVY_D, (nx - 4, ny - 1, 9, 9))       # plate shadow
    pygame.draw.rect(surf, _SOC_WHITE, (nx - 4, ny - 1, 8, 8))        # white plate
    # Flat-fill block "9": a solid bowl (top) + a down-stroke tail on the right.
    pygame.draw.rect(surf, _SOC_NAVY, (nx - 2, ny, 5, 4))             # bowl block
    pygame.draw.rect(surf, _SOC_WHITE, (nx, ny + 1, 2, 2))            # bowl hole
    pygame.draw.rect(surf, _SOC_NAVY, (nx + 1, ny, 2, 6))             # right tail

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
