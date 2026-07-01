"""Soccer v4 D5 — THE ULTRA FAN.

The kit must read as fabric worn ON the bird, with a supporter scarf as the
hero prop. The jersey is a horizontally-striped garment polygon clipped to the
body taper (RED/WHITE/RED) with dark keylines separating the panels so it reads
as sewn cloth, a bold gold crew collar sitting on a dark shadow ring, gold
sleeve trims, keeper socks + dark boots below the hem, and a bobble hat on the
crown. The purple/gold supporter scarf is knotted at the neck and drops two
long fringed tails past the jersey hem — drawn LAST so it sits in front of the
kit and owns the silhouette even at 40px.
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
_KEYLINE    = (100, 10, 10)          # dark panel seam between stripe bands
_COLLAR_G   = (240, 190, 30)
_COLLAR_SH  = (80, 10, 10)           # dark ring separating gold collar from red
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

# Garment silhouette — torso that starts at the body edge (BCX-10) and flares to
# a hem, used both to clip the stripe bands and to stroke the dark seam outline.
jersey = [
    (BCX - 10, HY + 7), (BCX - 12, HY + 17), (BCX - 8, HY + 23),
    (HX + 8, HY + 23),  (HX + 11, HY + 18),  (HX + 9, HY + 8),
]


def _jersey_x_at_y(y):
    """Left/right x of the garment polygon at a scanline y, so horizontal stripe
    bands clip to the body taper instead of overflowing it. Left edge runs
    (22,48)->(20,58)->(24,64); right edge (56,49)->(58,59)->(55,64)."""
    # Left edge.
    if y <= HY + 17:
        t = max(0.0, min(1.0, (y - (HY + 7)) / 10.0))
        lx = int(round(22 + (20 - 22) * t))
    else:
        t = max(0.0, min(1.0, (y - (HY + 17)) / 6.0))
        lx = int(round(20 + (24 - 20) * t))
    # Right edge.
    if y <= HY + 18:
        t = max(0.0, min(1.0, (y - (HY + 8)) / 10.0))
        rx = int(round(56 + (58 - 56) * t))
    else:
        t = max(0.0, min(1.0, (y - (HY + 18)) / 5.0))
        rx = int(round(58 + (55 - 58) * t))
    return lx, rx


def _paint(surf, _a):
    # 1 — knee-high keeper socks (shadow, sock body, contrast hoop) drawn first
    #     so the garment hem sits over their tops. Socks extend below the hem
    #     (HY+23) so they read as legs, not part of the jersey.
    for fx in (HX - 9, HX + 1):
        pygame.draw.line(surf, (30, 34, 42), (fx + 1, HY + 22), (fx + 1, HY + 27), 6)
        pygame.draw.line(surf, _SOCK_D, (fx, HY + 22), (fx, HY + 27), 5)
        pygame.draw.line(surf, (200, 205, 215), (fx - 1, HY + 24), (fx + 2, HY + 24), 2)

    # 2 — boots at the foot of each sock: dark ellipse with a light sole stripe.
    for fx in (HX - 9, HX + 1):
        pygame.draw.ellipse(surf, _BOOT_D, (fx - 4, HY + 25, 9, 5))
        pygame.draw.line(surf, _BOOT_S, (fx - 3, HY + 28), (fx + 3, HY + 28), 1)

    # 3 — grey match shorts band across the hip, tucked under the jersey hem.
    pygame.draw.line(surf, _SHORTS_G, (BCX - 8, HY + 23), (HX + 8, HY + 23), 4)

    # 4 — horizontally-striped jersey, each band clipped to the garment taper so
    #     the stripes fill the FULL polygon width at every scanline.
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

    # 5 — dark keylines between the bands so the kit reads as sewn fabric panels,
    #     not a flat printed flag.
    for ky in (HY + 13, HY + 18):
        lx, rx = _jersey_x_at_y(ky)
        pygame.draw.line(surf, _KEYLINE, (lx, ky), (rx, ky), 1)

    # 6 — dark-red garment outline that makes the cloth a sewn object.
    pygame.draw.polygon(surf, _JERSEY_OUT, jersey, 2)

    # 7 — white stitched seam, legible where it crosses the red stripes.
    pygame.draw.line(surf, (240, 242, 248), (HX - 1, HY + 11), (HX, HY + 21), 1)

    # 8 — gold sleeve trims at the shoulder line.
    pygame.draw.line(surf, _COLLAR_G, (BCX - 10, HY + 12), (BCX - 3, HY + 12), 2)
    pygame.draw.line(surf, _COLLAR_G, (HX + 4, HY + 12), (HX + 10, HY + 12), 2)

    # 9 — bobble hat on the crown (a dome, not a headband) — stays above HY+8.
    pygame.draw.ellipse(surf, _HAT_RIM, (HX - 10, CROWN_Y - 2, 20, 8), 2)
    pygame.draw.ellipse(surf, _HAT_RED, (HX - 9, CROWN_Y - 5, 18, 9))
    pygame.draw.line(surf, (200, 60, 60), (HX - 5, CROWN_Y - 4), (HX + 2, CROWN_Y - 4), 2)
    pygame.draw.circle(surf, _HAT_POM, (HX - 2, CROWN_Y - 9), 4)
    pygame.draw.circle(surf, (255, 255, 255), (HX - 3, CROWN_Y - 10), 2)

    # 10 — bold gold crew-neck collar ring sitting on a dark shadow ring so the
    #      gold separates crisply from the red jersey below it.
    collar_rect = pygame.Rect(HX - 7, HY + 4, 15, 9)
    pygame.draw.ellipse(surf, _COLLAR_SH, collar_rect.inflate(2, 2), 1)
    pygame.draw.ellipse(surf, _COLLAR_G, collar_rect, 3)

    # 11 — supporter scarf, drawn LAST so it reads as the hero prop in FRONT of
    #      the kit: a WIDE knotted neck band, then two long fringed tails that
    #      hang past the jersey hem so the scarf dominates the silhouette.
    # Wide neck loop.
    pygame.draw.line(surf, _SCARF_GOLD, (HX - 8, HY + 6), (HX + 6, HY + 6), 6)
    pygame.draw.line(surf, _SCARF_PUR, (HX - 7, HY + 8), (HX + 5, HY + 8), 5)

    # Left tail — thick gold with a purple stripe, extending past the hem.
    pygame.draw.line(surf, _SCARF_GOLD, (HX - 5, HY + 9), (HX - 15, HY + 24), 5)
    pygame.draw.line(surf, _SCARF_PUR, (HX - 6, HY + 11), (HX - 14, HY + 24), 3)
    for j in (0, 2, 4):
        pygame.draw.line(surf, _SCARF_FRNG, (HX - 15 + j, HY + 24), (HX - 15 + j, HY + 27), 1)

    # Right tail — thick gold with a purple stripe, extending past the hem.
    pygame.draw.line(surf, _SCARF_GOLD, (HX + 2, HY + 9), (HX + 12, HY + 24), 5)
    pygame.draw.line(surf, _SCARF_PUR, (HX + 3, HY + 11), (HX + 11, HY + 24), 3)
    for j in (0, 2, 4):
        pygame.draw.line(surf, _SCARF_FRNG, (HX + 8 + j, HY + 24), (HX + 8 + j, HY + 27), 1)


build = _make_skin(_paint)
