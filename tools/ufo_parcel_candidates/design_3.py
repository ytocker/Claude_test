"""GOLDEN GLYPH DISC — ancient-astronaut relic parcel for MINI UFO redesign."""
import pygame
from game.parrot import _aaellipse

SIZE = 22
SS = 44

# Palette — a hammered gold saucer humming with turquoise glyph energy.
GOLD     = (244, 197, 68)    # bright gold crown
BRONZE   = (176, 122, 30)    # deep bronze underside
GLYPH    = (46, 230, 198)    # alien turquoise
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
    cy = 28               # low on canvas — glyph face stays below Pip's belly
    disc_rx, disc_ry = 17, 6

    # --- Low ceremonial dome first so the disc base overlaps it cleanly ---
    dome_cy = cy - disc_ry - 4
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
    energy.fill((0, 0, 0, 0), pygame.Rect(0, 0, SS, cy + 1))
    s.blit(energy, (0, 0))

    # --- Glowing alien glyphs along the disc face (the legendary tell) ---
    glyph_y = cy + 2

    def _glow(draw_big):
        """Soft turquoise halo behind a glyph, drawn once at low alpha."""
        g = pygame.Surface((SS, SS), pygame.SRCALPHA)
        draw_big(g)
        s.blit(g, (0, 0))

    # DOT — solid mark with a bright core.
    _glow(lambda g: _aaellipse(g, (*GLYPH, 80), (cx - 11, glyph_y), 4, 4))
    _aaellipse(s, GLYPH, (cx - 11, glyph_y), 3, 3)
    _aaellipse(s, (200, 255, 245), (cx - 11, glyph_y - 1), 1, 1)

    # CHEVRON — a chunky ">" of two short diagonals.
    _glow(lambda g: (
        pygame.draw.line(g, (*GLYPH, 80), (cx - 6, glyph_y - 4), (cx - 2, glyph_y), 4),
        pygame.draw.line(g, (*GLYPH, 80), (cx - 2, glyph_y), (cx - 6, glyph_y + 4), 4),
    ))
    pygame.draw.line(s, GLYPH, (cx - 6, glyph_y - 3), (cx - 3, glyph_y), 3)
    pygame.draw.line(s, GLYPH, (cx - 3, glyph_y), (cx - 6, glyph_y + 3), 3)

    # RING — hollow turquoise circle.
    _glow(lambda g: _aaellipse(g, (*GLYPH, 80), (cx + 3, glyph_y), 5, 5))
    _ring(s, GLYPH, (cx + 3, glyph_y), 4, 4, 2)

    # BAR — short vertical stroke.
    _glow(lambda g: pygame.draw.line(g, (*GLYPH, 80),
                                     (cx + 10, glyph_y - 3), (cx + 10, glyph_y + 3), 4))
    pygame.draw.line(s, GLYPH, (cx + 10, glyph_y - 2), (cx + 10, glyph_y + 2), 3)

    return pygame.transform.smoothscale(s, (SIZE, SIZE))
