"""GOLDEN GLYPH DISC — ancient-astronaut relic parcel for MINI UFO redesign."""
import pygame
from game.parrot import _aaellipse

SIZE = 22
SS = 44

# Palette — a hammered gold saucer humming with turquoise glyph energy.
GOLD     = (244, 197, 68)    # bright gold crown
BRONZE   = (176, 122, 30)    # deep bronze underside
GLYPH    = (72, 240, 205)    # alien turquoise
GLYPH_DIM = (36, 120, 103)   # dim turquoise for the echo dots
OUTLINE  = (42, 27, 8)       # dark relic outline
CROWN    = (255, 240, 176)   # gold crown catch highlight


def _ring(surf, color, center, rx, ry, width):
    """Hollow ellipse — the fill helper has no width, so draw the rect directly."""
    cx, cy = center
    rect = pygame.Rect(int(cx - rx), int(cy - ry), int(rx * 2), int(ry * 2))
    pygame.draw.ellipse(surf, color, rect, width)


def build(mode="normal"):
    s = pygame.Surface((SS, SS), pygame.SRCALPHA)

    cx = SS // 2 + 2      # slight right nudge so full disc clears Pip's tail
    cy = 34               # low on canvas — glyph face stays below Pip's belly
    disc_rx, disc_ry = 17, 6

    # --- Low ceremonial dome first so the disc base overlaps it cleanly ---
    dome_cy = cy - disc_ry - 3
    _aaellipse(s, OUTLINE, (cx, dome_cy), 8 + 1, 5 + 1)
    _aaellipse(s, GOLD,    (cx, dome_cy), 8,     5)
    # Bright crown catch on the dome's upper-left curve — the "polished relic" cue.
    _aaellipse(s, CROWN, (cx - 3, dome_cy - 1), 2, 1)

    # --- Dark outline halo baked around the whole disc for day-sky contrast ---
    _aaellipse(s, OUTLINE, (cx, cy), disc_rx + 3, disc_ry + 3)

    # --- Hammered-gold disc with a vertical gradient (gold crown → bronze belly) ---
    # Masked scratch surface so only disc pixels survive the per-scanline fill.
    disc = pygame.Surface((SS, SS), pygame.SRCALPHA)
    for iy in range(-disc_ry, disc_ry + 1):
        t = (iy + disc_ry) / (disc_ry * 2)
        col = (
            int(GOLD[0] + (BRONZE[0] - GOLD[0]) * t),
            int(GOLD[1] + (BRONZE[1] - GOLD[1]) * t),
            int(GOLD[2] + (BRONZE[2] - GOLD[2]) * t),
        )
        # Ellipse half-width at this scanline keeps the fill inside the disc.
        frac = 1.0 - (iy / disc_ry) ** 2
        if frac < 0:
            continue
        hw = disc_rx * (frac ** 0.5)
        yy = cy + iy
        pygame.draw.line(disc, col, (cx - hw, yy), (cx + hw, yy))
    s.blit(disc, (0, 0))

    # --- Pronounced saucer brim: a dark overhang line below the disc edge so the
    # flying-saucer silhouette reads even when Pip's tail occludes the dome. ---
    BRIM = pygame.Surface((SS, SS), pygame.SRCALPHA)
    _aaellipse(BRIM, (*BRONZE, 180), (cx, cy + disc_ry - 1), disc_rx + 2, 3)
    s.blit(BRIM, (0, 0))

    # --- Darker ridged rim ring just inside the disc edge ---
    _ring(s, BRONZE, (cx, cy), disc_rx - 1, disc_ry - 1, 1)

    # --- Gold crown catch riding the disc's top edge ---
    hi = pygame.Surface((SS, SS), pygame.SRCALPHA)
    _aaellipse(hi, (*CROWN, 160), (cx - 4, cy - disc_ry + 2), 5, 2)
    s.blit(hi, (0, 0))

    # --- Thin turquoise energy line tracing the lower rim ---
    energy = pygame.Surface((SS, SS), pygame.SRCALPHA)
    _ring(energy, (*GLYPH, 130), (cx, cy + 1), disc_rx - 2, disc_ry - 1, 1)
    # Clip the halo to the disc's lower half so only the underside rim glows.
    energy.fill((0, 0, 0, 0), pygame.Rect(0, 0, SS, cy + 3))
    s.blit(energy, (0, 0))

    # --- Glyph hierarchy: one dominant central diamond + two dim echo dots, so a
    # single hero mark reads at 22px instead of three equal marks smearing. ---
    glyph_y = cy + 5   # lower into read zone

    def _glow(draw_big):
        """Soft turquoise halo behind a glyph, drawn once at low alpha."""
        g = pygame.Surface((SS, SS), pygame.SRCALPHA)
        draw_big(g)
        s.blit(g, (0, 0))

    # Central DIAMOND — the dominant hero mark (~6px, can count as "1")
    _glow(lambda g: pygame.draw.polygon(g, (*GLYPH, 80),
        [(cx, glyph_y - 5), (cx + 4, glyph_y), (cx, glyph_y + 5), (cx - 4, glyph_y)]))
    pygame.draw.polygon(s, GLYPH,
        [(cx, glyph_y - 4), (cx + 3, glyph_y), (cx, glyph_y + 4), (cx - 3, glyph_y)])
    _aaellipse(s, (220, 255, 245), (cx, glyph_y), 1, 1)  # bright core

    # Left echo dot (smaller, ~30% value)
    _aaellipse(s, GLYPH_DIM, (cx - 9, glyph_y), 2, 2)
    # Right echo dot (smaller)
    _aaellipse(s, GLYPH_DIM, (cx + 9, glyph_y), 2, 2)

    return pygame.transform.smoothscale(s, (SIZE, SIZE))
