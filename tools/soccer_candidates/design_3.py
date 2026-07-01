"""THE CAPTAIN — Pip as a soccer team captain (DESIGN 3 of the SOCCER set).

Scratch exploration only; NOT registered in store_skins.BUILDERS, so production
is untouched.

Concept: a full soccer kit built on a deep-navy body block (jersey + shorts read
as one dark torso mass) with three bright reads that survive the 40px downscale:
(1) a white-piped navy jersey with a small white club CREST on the left chest,
(2) white socks with a navy DOUBLE-HOOP at the top over near-black cleats, and
(3) the HERO PROP — a bold white CAPTAIN'S ARMBAND looped around the near wing
arm, brighter and wider than any garment stripe so it owns the read as "captain".

At 40px, in order of value: the white armband breaking off the near arm, the
white crest + collar on the navy chest, the white socks with their double hoop,
then the near-black cleats. The navy body block is lifted off dark sky by a 1px
lighter-navy garment outline. Pip's macaw head/beak/eye stay clear so it stays
"parrot dressed as a captain."
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

    # White piping across the jersey top so the collar line reads at hero scale.
    pygame.draw.line(surf, PIPING, (HX - 12, HY + 9), (HX + 10, HY + 9), 1)
    # Thin white V-collar dipping from the piping — the open-neck cue.
    pygame.draw.line(surf, PIPING, (HX - 3, HY + 9), (HX, HY + 13), 1)
    pygame.draw.line(surf, PIPING, (HX + 3, HY + 9), (HX, HY + 13), 1)

    # Club CREST on the left chest — a small white shield with a tiny gold star.
    shield = [(HX - 8, HY + 11), (HX - 2, HY + 11), (HX - 2, HY + 17),
              (HX - 5, HY + 19), (HX - 8, HY + 17)]
    _poly(surf, WHITE, shield)
    pygame.draw.polygon(surf, NAVY_LINE, shield, 1)
    store_skins._star5(surf, HX - 5, HY + 14, 2, GOLD)

    # ── SHORTS — same navy as the jersey, crotch notch shows two leg tubes.
    shorts = [(HX - 10, HY + 23), (HX - 11, HY + 29), (HX - 3, HY + 29),
              (HX - 2, HY + 26), (HX, HY + 26), (HX + 1, HY + 29),
              (HX + 7, HY + 29), (HX + 8, HY + 23)]
    _poly(surf, NAVY, shorts)
    # Shade the off-side leg tube for roundness.
    _poly(surf, NAVY_D, [(HX + 1, HY + 29), (HX + 7, HY + 29), (HX + 8, HY + 23),
                         (HX + 3, HY + 23)])
    pygame.draw.polygon(surf, NAVY_LINE, shorts, 1)

    # ── SOCKS — white body with a navy DOUBLE-HOOP at the top.
    for sx in (HX - 7, HX + 3):
        pygame.draw.line(surf, SOCK_COL, (sx, HY + 29), (sx, HY + 37), 4)
        pygame.draw.line(surf, HOOP_COL, (sx, HY + 29), (sx, HY + 32), 4)
        pygame.draw.line(surf, HOOP2_COL, (sx, HY + 33), (sx, HY + 35), 4)

    # ── CLEATS — near-black boots with a silver sole stripe.
    for fx in (HX - 11, HX - 1):
        pygame.draw.rect(surf, CLEAT_COL, (fx, HY + 33, 10, 5), border_radius=2)
        pygame.draw.line(surf, STRIPE_COL, (fx + 1, HY + 37), (fx + 9, HY + 37), 1)

    # ── HERO PROP · CAPTAIN'S ARMBAND (drawn LAST) — a bold wide white band looped
    #    around the near (right) wing arm, brighter + wider than any garment stripe
    #    so it owns the read as "captain". Gold edge lines above/below + a small
    #    dark "C" so it reads unmistakably as the skipper's armband.
    a0 = (HX + 8, HY + 17)
    a1 = (HX + 14, HY + 21)
    pygame.draw.line(surf, ARMBAND, a0, a1, 5)
    # Thin gold edge line 1px above and below the band.
    pygame.draw.line(surf, GOLD, (a0[0], a0[1] - 3), (a1[0], a1[1] - 3), 1)
    pygame.draw.line(surf, GOLD, (a0[0], a0[1] + 3), (a1[0], a1[1] + 3), 1)
    # Small dark "C" for Captain — a short forward-facing arc reading as the letter.
    pygame.draw.arc(surf, NAVY_D, (HX + 9, HY + 16, 5, 6), 0.5, 2.6, 2)


build = store_skins._make_skin(_paint)
