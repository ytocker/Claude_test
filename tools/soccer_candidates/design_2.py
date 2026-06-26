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

    # ── 5. GOALKEEPER GLOVES — the hero prop, drawn LAST and OFF the body so each
    #    mitt breaks the green silhouette. The asymmetry is the read: the far hand
    #    is RAISED in a catch pose (upper-left, clearing the body to break the
    #    outline), the near hand is DROPPED LOW at hem level (lower-right). ~15px of
    #    vertical separation between the two centres sells the keeper stance.

    def _mitt(ex, ey, ew, eh):
        # A rounded catch mitt: filled ellipse body, three horizontal finger ridges
        # so it reads as fingers not a flat patch, and a white knuckle bar on top.
        pygame.draw.ellipse(surf, _GLOVE_D, (ex - 1, ey + 1, ew + 2, eh + 1))  # shadow
        pygame.draw.ellipse(surf, _GLOVE_Y, (ex, ey, ew, eh))                  # body
        cx = ex + ew // 2
        for fy in (ey + eh // 4, ey + eh // 2, ey + (3 * eh) // 4):            # ridges
            pygame.draw.line(surf, _GLOVE_D, (ex + 2, fy), (ex + ew - 2, fy), 1)
        pygame.draw.line(surf, _GLOVE_W, (ex + 1, ey + 1), (ex + ew - 1, ey + 1), 2)  # knuckle
        pygame.draw.line(surf, _GLOVE_H, (ex + 2, ey + 3), (cx + 1, ey + 3), 1)       # highlight

    # FAR (LEFT) glove — RAISED catch pose, centre ~(HX-12, HY+7); upper band
    # y≈HY+3..14, left and below the sunglasses so it never collides with the eye.
    _mitt(HX - 16, HY + 3, 10, 12)

    # NEAR (RIGHT) glove — DROP-LOW pose, centre ~(HX+7, HY+22); lower band
    # y≈HY+18..29 near the hem, giving genuine vertical separation from the far hand.
    _mitt(HX + 3, HY + 18, 10, 12)


build = store_skins._make_skin(_paint)
