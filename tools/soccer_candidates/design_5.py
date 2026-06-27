"""Soccer v4 D5 — THE ULTRA FAN.

The earlier passes read as "a parrot painted in team colours". This pass makes
the kit read as fabric you could pull off: a horizontally-striped jersey clipped
to a garment polygon, a sewn-on gold crew collar, gold sleeve trims, a stitched
seam, knee-high keeper socks + boots, a bobble hat, and the hero prop — a
purple/gold supporter scarf knotted at the neck with two fringed tails hanging
asymmetrically so the silhouette never reads as a symmetric bib.
"""
import pygame
from game.store_skins import HX, HY, CROWN_Y, _poly, _make_skin

# Body centre in composite space — the limbs/garment hang off this, not the head.
BCX, BCY = 32, 52

# Fabric reads as cloth only when every edge is a deliberate hue: stripe field,
# dark-red garment outline, gold trims, and the supporter purple of the scarf.
_STRIPE_RED = (200, 30, 30)
_STRIPE_WHT = (238, 238, 242)
_JERSEY_OUT = (120, 16, 16)
_COLLAR_G   = (240, 190, 30)
_COLLAR_SH  = (160, 120, 10)
_HAT_RED    = (160, 20, 20)
_HAT_RIM    = (90, 10, 10)
_HAT_POM    = (240, 242, 248)
_SCARF_GOLD = (240, 190, 30)
_SCARF_PUR  = (95, 38, 158)
_SCARF_FRNG = (220, 170, 20)
_SOCK_D     = (40, 44, 52)
_BOOT_D     = (26, 24, 32)
_BOOT_S     = (200, 205, 215)
_SHORTS_G   = (120, 124, 140)

# Garment silhouette — torso that flares to a hem, used both to clip the stripe
# bands and to stroke the dark seam outline.
jersey = [
    (BCX - 10, HY + 7), (BCX - 12, HY + 17), (BCX - 8, HY + 23),
    (HX + 8, HY + 23),  (HX + 11, HY + 18),  (HX + 9, HY + 8),
]


def _jersey_x_at_y(y):
    """Left/right x of the garment polygon at a scanline y, so horizontal
    stripe bands can be clipped to the body taper instead of overflowing it."""
    # Left edge: (22,48) → (20,58) → (24,64)
    if y <= HY + 17:
        t = (y - (HY + 7)) / 10.0 if (HY + 17) != (HY + 7) else 0
        t = max(0.0, min(1.0, t))
        lx = int(22 + (20 - 22) * t)
    else:
        t = (y - (HY + 17)) / 6.0 if (HY + 23) != (HY + 17) else 0
        t = max(0.0, min(1.0, t))
        lx = int(20 + (24 - 20) * t)
    # Right edge: (56,49) → (58,59) → (55,64)
    if y <= HY + 18:
        t = (y - (HY + 8)) / 10.0 if (HY + 18) != (HY + 8) else 0
        t = max(0.0, min(1.0, t))
        rx = int(56 + (58 - 56) * t)
    else:
        t = (y - (HY + 18)) / 5.0 if (HY + 23) != (HY + 18) else 0
        t = max(0.0, min(1.0, t))
        rx = int(58 + (55 - 58) * t)
    return lx, rx


def _paint(surf, _a):
    # 1 — knee-high keeper socks (shadow, sock body, contrast hoop) drawn first
    #     so the garment hem sits over their tops.
    for fx in (HX - 9, HX + 1):
        pygame.draw.line(surf, (30, 34, 42), (fx + 1, HY + 13), (fx + 1, HY + 25), 6)
        pygame.draw.line(surf, _SOCK_D, (fx, HY + 13), (fx, HY + 25), 5)
        pygame.draw.line(surf, (200, 205, 215), (fx - 1, HY + 15), (fx + 2, HY + 15), 2)

    # 2 — boots at the foot of each sock
    for fx in (HX - 9, HX + 1):
        pygame.draw.ellipse(surf, _BOOT_D, (fx - 4, HY + 23, 9, 5))
        pygame.draw.line(surf, _BOOT_S, (fx - 3, HY + 25), (fx + 3, HY + 25), 1)

    # 3 — grey match shorts band across the hip
    pygame.draw.line(surf, _SHORTS_G, (BCX - 8, HY + 24), (HX + 8, HY + 24), 4)

    # 4 — horizontally-striped jersey, each band clipped to the garment taper
    stripe_defs = [
        (_STRIPE_RED, HY + 7,  HY + 13),
        (_STRIPE_WHT, HY + 13, HY + 18),
        (_STRIPE_RED, HY + 18, HY + 23),
    ]
    for color, y0, y1 in stripe_defs:
        lx0, rx0 = _jersey_x_at_y(y0)
        lx1, rx1 = _jersey_x_at_y(y1)
        band = [(lx0, y0), (rx0, y0), (rx1, y1), (lx1, y1)]
        _poly(surf, color, band)

    # 5 — ELEMENT 3: dark-red garment outline that makes the cloth a sewn object
    pygame.draw.polygon(surf, _JERSEY_OUT, jersey, 2)

    # 6 — ELEMENT 4: white stitched seam, legible where it crosses the red stripes
    pygame.draw.line(surf, (240, 242, 248), (HX - 1, HY + 11), (HX, HY + 21), 1)

    # 7 — ELEMENT 2: gold sleeve trims at the shoulder line
    pygame.draw.line(surf, _COLLAR_G, (BCX - 10, HY + 12), (BCX - 3, HY + 12), 2)
    pygame.draw.line(surf, _COLLAR_G, (HX + 4, HY + 12), (HX + 10, HY + 12), 2)

    # 8 — bobble hat on the crown (a dome, not a headband)
    pygame.draw.ellipse(surf, _HAT_RIM, (HX - 10, CROWN_Y - 2, 20, 8), 2)
    pygame.draw.ellipse(surf, _HAT_RED, (HX - 9, CROWN_Y - 5, 18, 9))
    pygame.draw.line(surf, (200, 60, 60), (HX - 5, CROWN_Y - 4), (HX + 2, CROWN_Y - 4), 2)
    pygame.draw.circle(surf, _HAT_POM, (HX - 2, CROWN_Y - 9), 4)
    pygame.draw.circle(surf, (255, 255, 255), (HX - 3, CROWN_Y - 10), 2)

    # 9 — ELEMENT 1: gold crew-neck collar ring with shadow keyline
    collar_rect = pygame.Rect(HX - 7, HY + 4, 15, 9)
    pygame.draw.ellipse(surf, _COLLAR_G, collar_rect, 3)
    pygame.draw.ellipse(surf, _COLLAR_SH, collar_rect, 1)

    # 10 — supporter scarf, drawn LAST so it reads as the hero prop in front of
    #      the kit: neck loop, then a V-split into two fringed hanging tails.
    pygame.draw.line(surf, _SCARF_GOLD, (HX - 6, HY + 8), (HX + 6, HY + 8), 4)
    pygame.draw.line(surf, _SCARF_PUR, (HX - 5, HY + 10), (HX + 5, HY + 10), 3)

    # left tail
    pygame.draw.line(surf, _SCARF_GOLD, (HX - 4, HY + 10), (HX - 12, HY + 22), 4)
    for i in range(3):
        ty = HY + 12 + i * 4
        tx = HX - 5 - i * 3
        pygame.draw.line(surf, _SCARF_PUR, (tx - 1, ty), (tx + 1, ty), 2)
    for j in (0, 2, 4):
        pygame.draw.line(surf, _SCARF_FRNG, (HX - 11 - j, HY + 22), (HX - 11 - j, HY + 24), 1)

    # right tail
    pygame.draw.line(surf, _SCARF_GOLD, (HX + 1, HY + 10), (HX + 9, HY + 22), 4)
    for i in range(3):
        ty = HY + 12 + i * 4
        tx = HX + 3 + i * 3
        pygame.draw.line(surf, _SCARF_PUR, (tx - 1, ty), (tx + 1, ty), 2)
    for j in (0, 2, 4):
        pygame.draw.line(surf, _SCARF_FRNG, (HX + 8 + j, HY + 22), (HX + 8 + j, HY + 24), 1)


build = _make_skin(_paint)
