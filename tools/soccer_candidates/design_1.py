"""DESIGN 1 — THE STRIKER (Soccer / Football), v4.

Scratch exploration only — NOT registered in store_skins.BUILDERS, so production
is untouched. Pip the scarlet macaw kitted as a modern outfield striker.

v4 goal: make the kit read as CLOTHING, not a recolour. The four shirt-
construction cues a brain uses to spot a worn garment are drawn explicitly —
a crew-neck collar ring straddling the neckline, white sleeve hems where the
wings exit the fabric, a dark garment outline tracing the jersey edge, and a
centre seam down the chest panel. Without these the jersey just reads as
"blue parrot"; with them the scarlet neck visibly emerges from a shirt.
"""

import pygame
from game.store_skins import HX, HY, CROWN_Y, _poly, _make_skin

# Body-centre anchors in COMPOSITE space — the kit hangs off the torso, not the
# head, so it gets its own reference point below the beak/crown head anchors.
BCX, BCY = 32, 52

# ── kit palette ───────────────────────────────────────────────────────────────
# Two-zone jersey: the back (behind the body centre) sits in shadow so the
# lit chest panel reads as the front of a worn shirt rather than a flat fill.
_STR_BACK  = (25,  70, 180)   # dark blue — back zone (x < BCX)
_STR_CHEST = (40,  95, 210)   # lighter blue — chest zone (x > BCX)
_STR_OUT   = (10,  30,  92)   # dark navy garment outline
_STR_HI    = (60, 100, 220)   # highlight / front seam
_COLLAR_W  = (230, 235, 245)  # white collar ring
_COLLAR_SH = (140, 145, 155)  # collar inner keyline (shadow)
_SLEEVE    = (220, 225, 235)  # sleeve trim
_GOLD      = (240, 190,  30)  # diagonal sash
_GOLD_SH   = (200, 160,  20)  # sash shadow edge
_NUM_W     = (245, 248, 255)  # squad number "9"
_SOCK_N    = (25,  50, 160)   # navy socks
_SOCK_SH   = (18,  40, 130)   # sock shadow
_SOCK_H    = (220, 225, 235)  # sock hoop
_BOOT_D    = (26,  24,  32)   # dark boot
_BOOT_S    = (200, 205, 215)  # boot sole
_SHORTS    = (140, 145, 160)  # grey shorts strip

# Full-body jersey silhouette in COMPOSITE space (shared by fill + outline so
# the garment boundary always matches the fabric it traces).
_JERSEY = [
    (BCX - 10, HY + 7),   # left shoulder  (22, 48)
    (BCX - 12, HY + 17),  # left hip       (20, 58)
    (BCX - 8,  HY + 23),  # left hem       (24, 64)
    (HX + 8,   HY + 23),  # right hem      (55, 64)
    (HX + 11,  HY + 18),  # right hip      (58, 59)
    (HX + 9,   HY + 8),   # right shoulder (56, 49)
]


def _paint(surf, _a):
    # 1 — SOCKS (knee-high), drawn first so the kit layers over them.
    for fx in (HX - 9, HX + 1):
        pygame.draw.line(surf, _SOCK_SH, (fx + 1, HY + 13), (fx + 1, HY + 25), 6)
        pygame.draw.line(surf, _SOCK_N, (fx, HY + 13), (fx, HY + 25), 5)
        pygame.draw.line(surf, _SOCK_H, (fx - 1, HY + 15), (fx + 2, HY + 15), 2)

    # 2 — BOOTS.
    for fx in (HX - 9, HX + 1):
        pygame.draw.ellipse(surf, _BOOT_D, (fx - 4, HY + 23, 9, 5))
        pygame.draw.line(surf, _BOOT_S, (fx - 3, HY + 25), (fx + 3, HY + 25), 1)

    # 3 — SHORTS strip at the hem, between jersey and socks.
    pygame.draw.line(surf, _SHORTS, (BCX - 8, HY + 24), (HX + 8, HY + 24), 4)

    # 4 — JERSEY body, two-zone. Back fills the whole silhouette dark; the
    # chest panel overlays the front half lighter, faking a lit front face.
    _poly(surf, _STR_BACK, _JERSEY)
    chest = [
        (BCX, HY + 7), (BCX, HY + 23), (HX + 8, HY + 23),
        (HX + 11, HY + 18), (HX + 9, HY + 8),
    ]
    _poly(surf, _STR_CHEST, chest)

    # 5 — GOLD diagonal sash across the chest.
    pygame.draw.line(surf, _GOLD, (HX + 3, HY + 9), (HX - 6, HY + 19), 3)
    pygame.draw.line(surf, _GOLD_SH, (HX + 4, HY + 10), (HX - 5, HY + 20), 1)

    # 6 — SQUAD NUMBER "9" on the chest panel, built from bold rects.
    nx, ny = HX - 2, HY + 13
    pygame.draw.rect(surf, _NUM_W, (nx, ny, 5, 3))      # top bar
    pygame.draw.rect(surf, _NUM_W, (nx + 3, ny, 2, 5))  # right stroke
    pygame.draw.rect(surf, _NUM_W, (nx, ny + 2, 5, 2))  # middle bar
    pygame.draw.rect(surf, _NUM_W, (nx + 3, ny + 4, 2, 3))  # lower right

    # 7 — ELEMENT 3: garment outline tracing the full jersey perimeter.
    pygame.draw.polygon(surf, _STR_OUT, _JERSEY, 2)

    # 8 — ELEMENT 4: front-panel centre seam.
    pygame.draw.line(surf, _STR_HI, (HX - 1, HY + 11), (HX, HY + 21), 1)

    # 9 — ELEMENT 2: white sleeve hems where the wings exit the fabric.
    pygame.draw.line(surf, _SLEEVE, (BCX - 10, HY + 12), (BCX - 3, HY + 12), 2)
    pygame.draw.line(surf, _SLEEVE, (HX + 4, HY + 12), (HX + 10, HY + 12), 2)

    # 10 — ELEMENT 1: crew-neck collar ring, drawn last so it sits cleanly over
    # the jersey. Hollow on purpose — the scarlet neck shows through the centre,
    # which is the cue that sells "the parrot is wearing a shirt".
    collar_rect = pygame.Rect(HX - 7, HY + 4, 15, 9)
    pygame.draw.ellipse(surf, _COLLAR_W, collar_rect, 3)
    pygame.draw.ellipse(surf, _COLLAR_SH, collar_rect, 1)


build = _make_skin(_paint)
