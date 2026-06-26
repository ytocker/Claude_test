"""DESIGN 2 — THE GOALKEEPER (Soccer / Football), v3.

Scratch exploration only — NOT registered in store_skins.BUILDERS, so production
is untouched. Pip the scarlet macaw kitted as a modern goalkeeper.

The defining beat that sets this apart from the outfield STRIKER (design 1) is a
FULL-BODY high-vis green keeper jersey — it wraps the whole visible body from the
left shoulder (BCX-10) across to the right shoulder (HX+9), ~36px wide, instead of
hanging off only the right chest. The keeper's hero props are the bright
yellow-orange GLOVES, drawn last so the catch pose reads clearly. No headgear: a
keeper wears no forehead band, so the crown stays open.
"""
import pygame

from game import store_skins
from game.store_skins import HX, HY, CROWN_Y, _poly

# Body centre in composite space — the full-body jersey hangs from here, not from
# the head anchor alone, so the shirt cloth covers the macaw's torso left-to-right.
BCX, BCY = 32, 52

# High-vis green keeper kit. Two jersey values (dark back / light chest) round the
# cloth; bright yellow-orange gloves are the hero prop against the green + sky.
_GK_BACK    = (19, 160, 101)        # #13A065 dark HV green — back zone
_GK_CHEST   = (34, 212, 136)        # #22D488 light HV green — chest zone
_GK_FOLD    = (25, 195, 125)        # seam fold line between zones
_GK_OUTLINE = (10, 90, 55)          # dark green silhouette contour
_GLOVE_Y    = (255, 184, 0)         # #FFB800 bright yellow-orange glove body
_GLOVE_H    = (255, 220, 80)        # glove highlight
_GLOVE_D    = (180, 120, 0)         # glove shadow / finger lines
_GLOVE_W    = (240, 240, 245)       # white knuckle bar
_SOCK_W     = (240, 240, 248)       # white knee-high sock
_SOCK_D     = (160, 165, 180)       # sock shadow
_BOOT_D     = (26, 24, 32)          # near-black boot
_BOOT_SOLE  = (200, 200, 210)       # sole stripe
_SHORTS_D   = (20, 24, 30)          # dark shorts band


def _paint(surf, _a):
    # Full-body jersey polygon — left shoulder/hip at BCX-10/-12 so the cloth wraps
    # the whole torso, not just the right chest. ~36px wide.
    jersey = [
        (BCX - 10, HY + 7),          # left shoulder  (22, 48)
        (BCX - 12, HY + 17),         # left hip       (20, 58)
        (BCX - 8,  HY + 23),         # left hem       (24, 64)
        (HX + 8,   HY + 23),         # right hem      (55, 64)
        (HX + 11,  HY + 18),         # right hip      (58, 59)
        (HX + 9,   HY + 8),          # right shoulder (56, 49)
    ]
    # Right-chest zone painted in the lighter HV value so the shirt reads as lit
    # from the near side; the seam between zones is the fold line.
    chest_zone = [
        (BCX,      HY + 7),
        (BCX,      HY + 23),
        (HX + 8,   HY + 23),
        (HX + 11,  HY + 18),
        (HX + 9,   HY + 8),
    ]

    # ── 1. WHITE KNEE-HIGH SOCK PILLARS (two feet) — drawn first so the boots and
    #    shorts band lap over them. Spans HY+13..HY+25.
    for fx in (HX - 9, HX + 1):
        pygame.draw.line(surf, _SOCK_D, (fx + 1, HY + 13), (fx + 1, HY + 25), 6)
        pygame.draw.line(surf, _SOCK_W, (fx, HY + 13), (fx, HY + 25), 5)
        # Dark hoop band near the sock top — the classic kit stripe.
        pygame.draw.line(surf, _SHORTS_D, (fx - 1, HY + 15), (fx + 2, HY + 15), 2)

    # ── 2. BOOTS — a compact dark cleat under each sock with one bright sole tick.
    for fx in (HX - 9, HX + 1):
        pygame.draw.ellipse(surf, _BOOT_D, (fx - 4, HY + 23, 9, 5))
        pygame.draw.line(surf, _BOOT_SOLE, (fx - 3, HY + 25), (fx + 3, HY + 25), 1)

    # ── 3. DARK SHORTS strip — a thin band at the hem so shorts show between shirt
    #    and socks.
    pygame.draw.line(surf, _SHORTS_D, (BCX - 8, HY + 24), (HX + 8, HY + 24), 4)

    # ── 4. HV GREEN JERSEY (two zones) — back fill, lighter chest zone, fold seam,
    #    then a dark-green contour so the full silhouette crisps at the downscale.
    _poly(surf, _GK_BACK, jersey)
    _poly(surf, _GK_CHEST, chest_zone)
    pygame.draw.line(surf, _GK_FOLD, (BCX, HY + 7), (BCX, HY + 23), 1)
    pygame.draw.polygon(surf, _GK_OUTLINE, jersey, 1)

    # ── 5. GOALKEEPER GLOVES — the hero prop, drawn LAST so the catch pose sits in
    #    front of the jersey. Two small (8x10) bright gloves, one per wing.

    # FAR (LEFT) glove — raised catch pose.
    gx, gy = HX - 10, HY + 14
    pygame.draw.rect(surf, _GLOVE_D, (gx - 5, gy - 6, 9, 11))          # shadow
    pygame.draw.rect(surf, _GLOVE_Y, (gx - 4, gy - 6, 8, 10))          # main
    for fy in (gy - 4, gy - 2, gy):                                    # finger lines
        pygame.draw.line(surf, _GLOVE_D, (gx - 3, fy), (gx + 3, fy), 1)
    pygame.draw.line(surf, _GLOVE_W, (gx - 3, gy - 6), (gx + 3, gy - 6), 2)  # knuckle
    pygame.draw.line(surf, _GLOVE_H, (gx - 3, gy - 5), (gx + 2, gy - 5), 1)  # highlight

    # NEAR (RIGHT) glove — relaxed lower pose.
    gx, gy = HX + 5, HY + 17
    pygame.draw.rect(surf, _GLOVE_D, (gx - 5, gy - 6, 9, 11))          # shadow
    pygame.draw.rect(surf, _GLOVE_Y, (gx - 4, gy - 6, 8, 10))          # main
    for fy in (gy - 4, gy - 2, gy):                                    # finger lines
        pygame.draw.line(surf, _GLOVE_D, (gx - 3, fy), (gx + 3, fy), 1)
    pygame.draw.line(surf, _GLOVE_W, (gx - 3, gy - 6), (gx + 3, gy - 6), 2)  # knuckle
    pygame.draw.line(surf, _GLOVE_H, (gx - 3, gy - 5), (gx + 2, gy - 5), 1)  # highlight


build = store_skins._make_skin(_paint)
