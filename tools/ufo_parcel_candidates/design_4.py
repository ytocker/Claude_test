"""NEON NIGHT-DINER — a cyberpunk saucer built like a glowing neon sign.

The hull is near-black, so it vanishes against the sky: the SILHOUETTE tell is
the neon tube-light itself. Every stroke is drawn twice — a wide low-alpha glow
under a narrow hot core — so the electric edges survive the downscale to 22px
and pop hardest against the night phase. A dotted chase-light ring on the lower
rim is the signature, and a short violet spotlight cone plants the ship low in
the read zone where Pip's belly won't eat it.
"""
import pygame

SIZE = 22
SS = 44

HULL    = (20, 16, 32)     # near-black neon-sign backing
CYAN    = (0, 229, 255)    # neon cyan tube
MAGENTA = (255, 61, 203)   # neon magenta tube
VIOLET  = (122, 0, 255)    # inner-glow / beam fill
OUTLINE = (10, 6, 16)


def _neon_line(s, color, p1, p2):
    """Glow pass (wide, soft) under a hot core (narrow, opaque)."""
    pygame.draw.line(s, (*color, 90), p1, p2, 5)
    pygame.draw.line(s, (*color, 255), p1, p2, 2)


def _neon_ellipse(s, color, rect, glow_w=4, core_w=2):
    """Ellipse outline as a soft glow ring beneath a hot core ring."""
    glow = rect.inflate(2, 2)
    pygame.draw.ellipse(s, (*color, 90), glow, glow_w)
    pygame.draw.ellipse(s, (*color, 255), rect, core_w)


def build(mode="normal"):
    s = pygame.Surface((SS, SS), pygame.SRCALPHA)

    cx = SS // 2
    disc_cy = 28              # low so the neon disc lands in the read zone
    disc_rx, disc_ry = 17, 5
    dome_cx, dome_cy = cx, disc_cy - 5
    dome_rx, dome_ry = 7, 6

    disc_rect = pygame.Rect(0, 0, disc_rx * 2, disc_ry * 2)
    disc_rect.center = (cx, disc_cy)
    dome_rect = pygame.Rect(0, 0, dome_rx * 2, dome_ry * 2)
    dome_rect.center = (dome_cx, dome_cy)

    # --- Short violet spotlight cone FIRST so neon edges sit on top of it ---
    beam_top = disc_cy + disc_ry
    beam_bot = beam_top + 12
    beam = pygame.Surface((SS, SS), pygame.SRCALPHA)
    trapezoid = [
        (cx - 6, beam_top), (cx + 6, beam_top),
        (cx + 10, beam_bot), (cx - 10, beam_bot),
    ]
    pygame.draw.polygon(beam, (*VIOLET, 80), trapezoid)
    s.blit(beam, (0, 0))
    _neon_line(s, CYAN, (cx - 6, beam_top), (cx - 10, beam_bot))
    _neon_line(s, CYAN, (cx + 6, beam_top), (cx + 10, beam_bot))

    # --- Near-black hull fill (dome first, then disc over its base) ---
    pygame.draw.ellipse(s, HULL, dome_rect)
    pygame.draw.ellipse(s, HULL, disc_rect)
    # Faint violet inner glow bleeding up through the dark hull.
    inner = pygame.Surface((SS, SS), pygame.SRCALPHA)
    ig = disc_rect.inflate(-14, -3)
    pygame.draw.ellipse(inner, (*VIOLET, 55), ig)
    s.blit(inner, (0, 0))

    # --- Magenta dome outline over its near-black fill ---
    _neon_ellipse(s, MAGENTA, dome_rect, glow_w=4, core_w=2)

    # --- Cyan neon rim around the disc ---
    _neon_ellipse(s, CYAN, disc_rect, glow_w=5, core_w=2)

    # --- Magenta equator seam across the disc's waist ---
    seam_y = disc_cy
    _neon_line(s, MAGENTA, (cx - disc_rx + 2, seam_y), (cx + disc_rx - 2, seam_y))

    # --- Chase-light dots along the lower rim (the signature) ---
    import math
    n = 6
    for i in range(n):
        # Sweep the lower arc of the ellipse (angles 200..340 deg).
        t = 200 + (140 * i / (n - 1))
        rad = math.radians(t)
        dx = cx + (disc_rx - 1) * math.cos(rad)
        dy = disc_cy + (disc_ry - 1) * math.sin(rad)
        col = CYAN if i % 2 == 0 else MAGENTA
        dot = pygame.Surface((SS, SS), pygame.SRCALPHA)
        pygame.draw.circle(dot, (*col, 110), (dx, dy), 3)   # halo
        pygame.draw.circle(dot, (*col, 255), (dx, dy), 2)   # hot dot
        s.blit(dot, (0, 0))

    return pygame.transform.smoothscale(s, (SIZE, SIZE))
