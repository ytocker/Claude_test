"""THE CAPTAIN — Pip as a soccer team captain (DESIGN 3 of the SOCCER set).

Scratch exploration only; NOT registered in store_skins.BUILDERS, so production
is untouched.

Concept: a full soccer kit built on a deep-navy body block (jersey + shorts read
as one dark torso mass) with three bright reads that survive the 40px downscale:
(1) a chunky white club CREST with a single navy bar under one piping line,
(2) white socks with a compressed navy DOUBLE-HOOP that keeps clear white gaps
above the near-black cleats, and (3) the HERO PROP — a wide white CAPTAIN'S
ARMBAND anchored on the navy shoulder with a single gold spine, brighter and
wider than any garment stripe so it owns the read as "captain".

At 40px, in order of value: the wide white armband + gold spine on the navy
shoulder, the solid white crest on the navy chest, the white socks with their
hoop gaps, then the near-black cleats. The navy body block is lifted off dark
sky by a 1px lighter-navy garment outline. Pip's macaw head/beak/eye stay clear
so it stays "parrot dressed as a captain."
"""
import pygame

from game import store_skins
from game.store_skins import HX, HY, _poly

# Team navy — jersey + shorts share this so the torso reads as one dark block.
NAVY      = (13, 32, 72)        # #0D2048 kit navy
NAVY_D    = (8, 20, 40)         # #081428 shaded right half (roundness)
NAVY_LINE = (26, 58, 112)       # #1A3A70 lighter-navy garment outline (lifts off dark sky)
PIPING    = (230, 230, 255)     # cool white piping at the jersey top
WHITE     = (240, 245, 255)     # #F0F5FF sock body / crest field
GOLD      = (207, 181, 59)      # #CFB53B crest star / armband gold edge
SOCK_COL  = WHITE
HOOP_COL  = NAVY                # navy double-hoop at the sock top
HOOP2_COL = NAVY_D
CLEAT_COL = (28, 28, 36)        # #1C1C24 near-black cleats
STRIPE_COL= (160, 168, 176)     # #A0A8B0 silver sole stripe
ARMBAND   = (250, 251, 255)     # bright white captain's armband (brighter than piping)


def _paint(surf, _a):
    # ── JERSEY — deep navy torso, held inside the base bird footprint (hem ~HY+23).
    jersey = [(HX - 13, HY + 8), (HX - 14, HY + 18), (HX - 10, HY + 23),
              (HX + 8, HY + 23), (HX + 11, HY + 18), (HX + 9, HY + 8)]
    _poly(surf, NAVY, jersey)
    # Darker navy down the off-side so the jersey reads as a rounded torso.
    _poly(surf, NAVY_D, [(HX, HY + 8), (HX + 9, HY + 8), (HX + 11, HY + 18),
                         (HX + 8, HY + 23), (HX, HY + 23)])
    # 1px lighter-navy garment outline so the navy block separates from dark sky.
    pygame.draw.polygon(surf, NAVY_LINE, jersey, 1)

    # ONE horizontal piping line across the jersey top — the sole collar cue, so
    # it never fights the crest for the same white pixels at 40px.
    pygame.draw.line(surf, (200, 210, 240), (HX - 12, HY + 9), (HX + 10, HY + 9), 1)

    # Club CREST — a chunky white shield block that survives downscale, with ONE
    # navy vertical bar as its only interior mark (a gold star at r=2 is gone at
    # 40px, so drop it and let the crest read as a solid white shape).
    shield = [(HX - 9, HY + 11), (HX - 1, HY + 11), (HX - 1, HY + 18),
              (HX - 4, HY + 20), (HX - 9, HY + 18)]
    _poly(surf, (240, 240, 255), shield)
    pygame.draw.line(surf, NAVY, (HX - 5, HY + 12), (HX - 5, HY + 18), 1)
    pygame.draw.polygon(surf, NAVY, shield, 1)

    # ── SHORTS — same navy as the jersey, crotch notch shows two leg tubes.
    shorts = [(HX - 10, HY + 23), (HX - 11, HY + 29), (HX - 3, HY + 29),
              (HX - 2, HY + 26), (HX, HY + 26), (HX + 1, HY + 29),
              (HX + 7, HY + 29), (HX + 8, HY + 23)]
    _poly(surf, NAVY, shorts)
    # Shade the off-side leg tube for roundness.
    _poly(surf, NAVY_D, [(HX + 1, HY + 29), (HX + 7, HY + 29), (HX + 8, HY + 23),
                         (HX + 3, HY + 23)])
    pygame.draw.polygon(surf, NAVY_LINE, shorts, 1)

    # ── SOCKS — white body with a navy DOUBLE-HOOP compressed UP so a clear white
    #    gap survives between the hoops and again below the second hoop before the
    #    cleat, otherwise the whole foot merges into one dark block at 40px. The
    #    white sock body is laid first so the two 2px navy hoops leave white in the
    #    gaps (HY+31..33) and below (HY+35..37).
    for sx in (HX - 7, HX + 3):
        pygame.draw.line(surf, SOCK_COL, (sx, HY + 29), (sx, HY + 37), 4)
        pygame.draw.line(surf, HOOP_COL, (sx, HY + 29), (sx, HY + 31), 4)   # hoop 1
        pygame.draw.line(surf, HOOP2_COL, (sx, HY + 33), (sx, HY + 35), 4)  # hoop 2

    # ── CLEATS — near-black boots with a silver sole stripe.
    for fx in (HX - 11, HX - 1):
        pygame.draw.rect(surf, CLEAT_COL, (fx, HY + 33, 10, 5), border_radius=2)
        pygame.draw.line(surf, STRIPE_COL, (fx + 1, HY + 37), (fx + 9, HY + 37), 1)

    # ── HERO PROP · CAPTAIN'S ARMBAND (drawn LAST) — a bold, WIDE white band
    #    anchored inboard onto the navy shoulder (not the scarlet wing, where it
    #    vanished), with a single gold spine down its length for the classic
    #    captain's-armband read. No arc "C" and no hairline edge lines — both are
    #    sub-pixel noise at 40px; the fat white band + one gold line own the read.
    pygame.draw.line(surf, ARMBAND, (HX + 6, HY + 14), (HX + 15, HY + 20), 6)
    pygame.draw.line(surf, GOLD, (HX + 7, HY + 15), (HX + 14, HY + 19), 1)


build = store_skins._make_skin(_paint)
