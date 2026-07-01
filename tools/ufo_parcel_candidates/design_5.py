"""DISCO MIRROR-BALL SAUCER — a faceted party disc for the MINI UFO redesign.

The read is festive over mechanical: a mirror-ball hull scattering coloured
glints, so the tell lives in chunky pink/gold/cyan sparkles low on the disc
(the region a buyer's eye lands on) rather than in fine facet geometry that
would dissolve at 22px.
"""
import pygame
from game.parrot import _aaellipse

SIZE = 22
SS = 44

# Palette — cool silver-violet mirror facets with hot party glints.
FACET_LIGHT = (201, 195, 232)   # mirror silver-violet
FACET_DARK  = (175, 168, 210)   # dimmer facet row for the grid value break
SHADOW      = (138, 127, 208)   # facet shadow at the belly
PINK        = (255, 111, 216)
CYAN        = (102, 224, 255)
GOLD        = (255, 215, 90)
OUTLINE     = (32, 24, 46)
DOME        = (222, 218, 244)


def build(mode="normal"):
    s = pygame.Surface((SS, SS), pygame.SRCALPHA)

    cx = SS // 2 + 2      # nudge right so the disc clears Pip's tail
    cy = 28               # low on canvas so the sparkle zone stays readable
    disc_rx, disc_ry = 17, 6

    # --- Mirrored dome first so the disc base overlaps it cleanly ---
    dome_cy = cy - disc_ry - 3
    _aaellipse(s, OUTLINE, (cx, dome_cy), 5 + 1, 4 + 1)
    _aaellipse(s, DOME,    (cx, dome_cy), 5,     4)
    # Bright catch-light on the dome — a mirror ball always has a hot spot.
    _aaellipse(s, (255, 255, 255), (cx - 1, dome_cy - 1), 2, 1)

    # --- Dark outline halo for day-sky contrast ---
    _aaellipse(s, OUTLINE, (cx, cy), disc_rx + 3, disc_ry + 3)

    # --- Faceted disc: alternating scanline shades give the mirror-grid read.
    # Built in a masked scratch surface so only disc pixels survive; the value
    # break every few rows plus a per-zone column flip reads as a facet grid.
    hull = pygame.Surface((SS, SS), pygame.SRCALPHA)
    zone_w = (disc_rx * 2) / 4.0    # 4 horizontal facet columns
    for iy in range(-disc_ry, disc_ry + 1):
        frac = 1.0 - (iy / disc_ry) ** 2
        if frac < 0:
            continue
        hw = disc_rx * (frac ** 0.5)
        yy = cy + iy
        row_shade = ((iy + disc_ry) // 2) % 2   # facet row every 2 scanlines
        # Belly rows drift toward shadow for a rounded ball read.
        belly = iy > disc_ry - 3
        for zx in range(4):
            x0 = cx - hw + zx * (2 * hw / 4)
            x1 = cx - hw + (zx + 1) * (2 * hw / 4)
            col_flip = (zx + row_shade) % 2      # checker the zones per row
            if belly:
                col = SHADOW
            else:
                col = FACET_LIGHT if col_flip == 0 else FACET_DARK
            pygame.draw.line(hull, col, (x0, yy), (x1, yy))
    s.blit(hull, (0, 0))

    # --- Faint dark facet seams (a couple of vertical grid lines) ---
    for gx in (cx - 8, cx, cx + 8):
        frac_top = cy - disc_ry + 1
        frac_bot = cy + disc_ry - 1
        pygame.draw.line(s, (*OUTLINE, 60), (gx, frac_top), (gx, frac_bot), 1)

    # --- Sparkle glints: chunky coloured circles on the bright lower face.
    # This is the TELL — kept at radius 2 so they survive the down-scale.
    glints = [
        (cx - 10, cy + 1, PINK),
        (cx - 4,  cy + 3, GOLD),
        (cx + 2,  cy + 2, CYAN),
        (cx + 9,  cy + 1, PINK),
        (cx - 7,  cy + 3, CYAN),
        (cx + 6,  cy + 3, GOLD),
        (cx,      cy - 1, PINK),
        (cx + 11, cy - 1, CYAN),
    ]
    for gx, gy, gc in glints:
        _aaellipse(s, gc, (gx, gy), 2, 2)
        # White core so each glint pops as a lit mirror facet.
        _aaellipse(s, (255, 255, 255), (gx, gy), 1, 1)

    # --- Star-glints: 4-point crosses floating just off the rim ---
    def star(px, py, col):
        pygame.draw.line(s, col, (px - 3, py), (px + 3, py), 1)
        pygame.draw.line(s, col, (px, py - 3), (px, py + 3), 1)
        _aaellipse(s, (255, 255, 255), (px, py), 1, 1)

    star(cx - disc_rx - 1, cy - 2, GOLD)
    star(cx + disc_rx + 2, cy + 1, PINK)
    star(cx - 2, cy - disc_ry - 1, CYAN)

    # --- Fan of short coloured light-rays from the underside (the scatter) ---
    ray_y = cy + disc_ry - 1
    rays = [
        (cx - 9, ray_y, -3, 8, PINK),
        (cx - 3, ray_y, -1, 8, CYAN),
        (cx + 3, ray_y,  1, 8, GOLD),
        (cx + 9, ray_y,  3, 8, PINK),
    ]
    for rx, ry, dx, dlen, col in rays:
        pygame.draw.line(s, col, (rx, ry), (rx + dx, ry + dlen), 1)

    return pygame.transform.smoothscale(s, (SIZE, SIZE))
