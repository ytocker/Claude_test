"""DESIGN 1 — THE STRIKER (Soccer / Football).

Scratch exploration only — NOT registered in store_skins.BUILDERS. Pip the
scarlet macaw kitted as a modern outfield striker. The read is carried by the
full LEG KIT: two tall, CHUNKY knee-high SOCKS spread into distinct vertical
pillars, each with a white hoop band and a dark forward-pointing CLEAT wedge
under it. That socks+boots silhouette is the unmistakable football tell and the
deliberate break from the basketball build — a hooper has bare calves + baggy
shorts + sneakers, a striker has long socks and studded boots, so the LOWER
silhouette must win the read.

The kit is painted OVER the scarlet body (the head stays the macaw so Pip still
reads as a parrot). A solid jersey carries a single diagonal team SASH; one
small "9" sits low-left so a single white focal wins at 40px. The upper body is
kept quiet (no armband) so nothing competes with the leg kit. Three cloth values
keep the jersey reading round through the 40px downscale; dark contours hold
every shape. Footprint law: socks+cleats sit on the feet line (~HY+13..28),
nothing balloons the torso, only a thin sweatband touches the brow (crown open).

Headless render: tools/soccer_candidates/render_design_1.py.
"""
import pygame

from game import store_skins
from game.store_skins import HX, HY, CROWN_Y, _poly


# Scarlet kit (a value above Pip's natural red so the cloth reads as worn, not
# plumage), navy trim, white squad mark, near-black cleats. Three scarlet values
# give the jersey roundness; the dark contour survives downscale. The socks get a
# bright rim tone so the outer calf edge holds against the NIGHT sky.
_SOC_RED    = (226, 59, 69)         # #E23B45 jersey scarlet
_SOC_RED_D  = (150, 30, 40)         # cloth shadow / contour
_SOC_RED_H  = (255, 120, 124)       # lit shoulder / chest highlight
_SOC_WHITE  = (244, 244, 248)       # #F4F4F8 white sash / number / sole
_SOC_NAVY   = (27, 42, 107)         # #1B2A6B navy trim / collar / sock body
_SOC_NAVY_D = (16, 25, 64)          # navy shadow / sock contour
_SOC_NAVY_H = (70, 92, 178)         # sock lit face / outer rim-light
_SOC_CLEAT  = (35, 37, 46)          # #23252E cleat
_SOC_CLEAT_H= (78, 84, 102)         # cleat upper sheen


# Body centre in composite space (parrot body centre (32,32) + PARROT_DY=20).
BCX, BCY = 32, 52


def _sock_and_boot(surf, fx, lit_side):
    """One CHUNKY knee-high sock as a solid filled calf + a forward-pointing
    boot wedge under it. `lit_side` is +1 (light from the right) / -1 so the
    outer edge of each leg catches the rim-light against the night sky. Built
    as filled polys — not strokes — so each leg survives the 40px downscale as a
    distinct vertical pillar, the loudest mass below the torso."""
    # Composite Y: the base macaw body bottoms out at y~69, so the calf emerges
    # from under the belly (top ~58) and the ankle sits at the body floor (~70);
    # the boot wedge breaks just past it (to ~74), mirroring how the baseball
    # cleats poke the lower outline. This keeps the socks the loudest mass BELOW
    # the torso instead of buried inside it.
    top, bot = 58, 70                # tall calf, knee-under-hem to ankle
    # Solid navy calf: a tall, NARROW tapered pillar (3px half-width) so the two
    # legs read as two distinct vertical columns with sky between them — not a
    # single horizontal bar. Dark contour underlay first.
    calf = [(fx - 3, top), (fx + 3, top), (fx + 2, bot), (fx - 2, bot)]
    _poly(surf, _SOC_NAVY_D, [(x - lit_side, y) for x, y in calf])   # contour shift
    _poly(surf, _SOC_NAVY, calf)
    # Lit front face — a vertical slab down the inner body so the calf reads round.
    face = [(fx, top), (fx + lit_side * 3, top),
            (fx + lit_side * 2, bot), (fx, bot)]
    _poly(surf, _SOC_NAVY_H, face)
    # White hoop band — a FULL 2px cross-stripe spanning the whole calf width,
    # set near the top of the sock (the classic kit stripe).
    hb = top + 4
    pygame.draw.line(surf, _SOC_WHITE, (fx - 3, hb), (fx + 3, hb), 2)
    pygame.draw.line(surf, _SOC_NAVY_D, (fx - 3, hb + 2), (fx + 3, hb + 2), 1)
    # 1px rim-light tracing the OUTER calf edge so the sock holds on night sky.
    rx = fx + lit_side * 3
    pygame.draw.line(surf, _SOC_NAVY_H, (rx, top + 1), (rx - lit_side, bot - 1), 1)

    # Forward-pointing BOOT WEDGE: a compact solid dark cleat, toe to the FORWARD
    # (right) side, with one bright white sole edge underneath. No stud ticks —
    # sub-pixel noise at 40px; the wedge silhouette alone says "studded boot, not
    # sneaker". Kept short + only just wider than the calf so the two boots stay
    # separate and never bridge into one bar.
    ax, ay = fx, bot                 # ankle pivot at the body floor
    wedge = [(ax - 3, ay - 1), (ax + 1, ay - 1), (ax + 5, ay + 2),
             (ax + 4, ay + 4), (ax - 3, ay + 4)]
    _poly(surf, (12, 13, 18), [(x, y + 1) for x, y in wedge])         # drop shadow
    _poly(surf, _SOC_CLEAT, wedge)
    # Boot upper sheen along the laced instep so the dark mass reads as leather.
    pygame.draw.line(surf, _SOC_CLEAT_H, (ax - 2, ay), (ax + 3, ay + 1), 1)
    # Bright white sole running the length of the wedge underside — the studded
    # boot's giveaway line.
    pygame.draw.line(surf, _SOC_WHITE, (ax - 3, ay + 4), (ax + 4, ay + 4), 1)


def _paint(surf, _a):
    # --- Tall team SOCKS + cleats at the feet line (THE soccer read) ------------
    # Drawn FIRST so the short-shorts hem laps over the sock tops and the legs
    # read as worn under the kit. Two distinct pillars: outer leg lit on its
    # outer edge so neither sock vanishes on night sky.
    _sock_and_boot(surf, 27, lit_side=-1)   # far leg, rim-light on its left edge
    _sock_and_boot(surf, 39, lit_side=+1)   # near leg, rim-light on its right edge

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
    # the ONE white focal up top. Clipped to the cloth so it never leaks past the
    # contour; a navy edge crisps it for the downscale.
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

    # --- Squad NUMBER "9" — small, low-left, thick dark rim ----------------------
    # Shrunk ~25% and pushed low-left so it never competes with the sash for the
    # white focal; a thick scarlet plate with a heavy dark rim separates the digit
    # from the sash so at 40px the sash wins one clean white and the "9" reads as
    # a small kit mark, not a second smear.
    nx, ny = BCX - 7, BCY + 5
    pygame.draw.ellipse(surf, _SOC_RED_D, (nx - 5, ny - 6, 11, 12))   # thick rim
    pygame.draw.ellipse(surf, _SOC_RED, (nx - 4, ny - 5, 9, 10))
    # Bowl of the 9 (dark ring → small white loop → red centre).
    pygame.draw.ellipse(surf, _SOC_RED_D, (nx - 3, ny - 4, 6, 6))
    pygame.draw.ellipse(surf, _SOC_WHITE, (nx - 2, ny - 3, 5, 4))
    pygame.draw.ellipse(surf, _SOC_RED, (nx, ny - 2, 2, 2))
    # Short tail of the 9 dropping from the bowl's lower-right.
    pygame.draw.line(surf, _SOC_RED_D, (nx + 3, ny - 1), (nx + 1, ny + 5), 3)
    pygame.draw.line(surf, _SOC_WHITE, (nx + 3, ny - 1), (nx + 1, ny + 5), 1)

    # --- Short SHORTS hem lapping over the sock tops -----------------------------
    # A navy hem band closes the kit at the sock tops (~y55..58) so the leg kit
    # reads as worn shorts over socks, not bare body; the socks emerge from under
    # it. A scalloped pair of hem dips between the legs sells the two-leg read.
    _poly(surf, _SOC_NAVY, [(BCX - 13, BCY + 3), (BCX + 12, BCY + 3),
                            (BCX + 11, BCY + 7), (BCX + 5, BCY + 6),
                            (BCX + 1, BCY + 8), (BCX - 5, BCY + 6),
                            (BCX - 11, BCY + 8)])
    pygame.draw.line(surf, _SOC_NAVY_D, (BCX - 13, BCY + 4), (BCX + 12, BCY + 4), 1)
    pygame.draw.line(surf, _SOC_WHITE, (BCX - 12, BCY + 4), (BCX + 10, BCY + 4), 1)

    # --- Thin brow sweatband (keeps the macaw reading, crown open) --------------
    # A slim scarlet band across the brow with a white edge — a sport tell that
    # adds no headgear bulk, so Pip's macaw head stays recognizable.
    pygame.draw.line(surf, _SOC_RED_D, (HX - 11, CROWN_Y + 6), (HX + 12, CROWN_Y + 5), 4)
    pygame.draw.line(surf, _SOC_RED, (HX - 11, CROWN_Y + 5), (HX + 12, CROWN_Y + 4), 2)
    pygame.draw.line(surf, _SOC_WHITE, (HX - 9, CROWN_Y + 4), (HX + 6, CROWN_Y + 3), 1)


build = store_skins._make_skin(_paint)
