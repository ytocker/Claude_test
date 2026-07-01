"""RETRO ROCKET-POP — 1950s diner saucer parcel for MINI UFO redesign."""
import pygame
from game.parrot import _aaellipse

SIZE = 22
SS = 44

# Palette — a candy pulp saucer, not chrome. Warm cherry + cream + soft glass.
HULL     = (230, 58, 70)
HULL_D   = (170, 35, 45)
BAND     = (246, 231, 200)
BAND_D   = (210, 195, 158)
PORT     = (58, 166, 196)
PORT_D   = (32, 110, 135)
GLOW     = (255, 210, 90)
OUTLINE  = (42, 20, 24)
DOME     = (200, 190, 175)


def build(mode="normal"):
    s = pygame.Surface((SS, SS), pygame.SRCALPHA)

    cx = SS // 2 + 2      # slight right nudge so full disc clears Pip's tail
    cy = 28               # low on canvas — cream band stays below Pip's belly
    disc_rx, disc_ry = 16, 7

    # --- Dome first so the disc silhouette overlaps its base cleanly ---
    dome_cy = cy - disc_ry - 4
    _aaellipse(s, OUTLINE, (cx, dome_cy), 6 + 1, 4 + 1)
    _aaellipse(s, DOME,    (cx, dome_cy), 6,     4)
    # A soft cream sheen on the dome's upper-left curve.
    _aaellipse(s, BAND, (cx - 2, dome_cy - 1), 2, 1)

    # --- Dark outline halo baked around the whole disc for day-sky contrast ---
    _aaellipse(s, OUTLINE, (cx, cy), disc_rx + 3, disc_ry + 3)

    # --- Cherry hull with a vertical gradient (lighter crown, darker belly) ---
    # Build in a masked scratch surface, then blit so only disc pixels survive.
    hull = pygame.Surface((SS, SS), pygame.SRCALPHA)
    top = cy - disc_ry
    span = disc_ry * 2
    for iy in range(-disc_ry, disc_ry + 1):
        t = (iy + disc_ry) / span if span else 0.0
        col = (
            int(HULL[0] + (HULL_D[0] - HULL[0]) * t),
            int(HULL[1] + (HULL_D[1] - HULL[1]) * t),
            int(HULL[2] + (HULL_D[2] - HULL[2]) * t),
        )
        # Ellipse half-width at this scanline keeps the fill inside the disc.
        frac = 1.0 - (iy / disc_ry) ** 2
        if frac < 0:
            continue
        hw = disc_rx * (frac ** 0.5)
        yy = cy + iy
        pygame.draw.line(hull, col, (cx - hw, yy), (cx + hw, yy))
    s.blit(hull, (0, 0))

    # --- Cream equator band (the diner stripe) ---
    _aaellipse(s, BAND_D, (cx, cy + 1), disc_rx - 1, 3)
    _aaellipse(s, BAND,   (cx, cy),     disc_rx - 1, 3)

    # --- Dark hull seam along the equator, top edge of the cream band ---
    pygame.draw.line(s, OUTLINE, (cx - disc_rx + 2, cy - 2),
                     (cx + disc_rx - 2, cy - 2), 1)

    # --- Row of chunky glowing portholes along the cream band (the tell) ---
    port_y = cy + 1
    port_xs = [cx - 9, cx - 3, cx + 3, cx + 9]
    for px in port_xs:
        # Soft warm halo behind each window signals an "occupied" ship.
        glow = pygame.Surface((SS, SS), pygame.SRCALPHA)
        _aaellipse(glow, (*GLOW, 120), (px, port_y), 4, 4)
        s.blit(glow, (0, 0))
        _aaellipse(s, PORT_D, (px, port_y), 3, 3)
        _aaellipse(s, PORT,   (px, port_y), 2, 2)
        # Tiny cream catch-light in each porthole's upper-left.
        _aaellipse(s, BAND, (px - 1, port_y - 1), 1, 1)

    # --- Cream highlight arc riding the disc's top crown ---
    hi = pygame.Surface((SS, SS), pygame.SRCALPHA)
    _aaellipse(hi, (*BAND, 150), (cx - 3, cy - disc_ry + 2), 5, 2)
    s.blit(hi, (0, 0))

    # --- Tiny tripod landing nubs below the hull ---
    for nx in (cx - 7, cx, cx + 7):
        pygame.draw.line(s, OUTLINE, (nx, cy + disc_ry - 1),
                         (nx, cy + disc_ry + 2), 1)

    return pygame.transform.smoothscale(s, (SIZE, SIZE))
