"""MINI UFO parcel — Golden Glyph Disc with per-player colour variant.

The player picks a colourway at purchase; build() reads the saved choice
and returns the matching 22×22 surface. No saved choice → gold original.
"""
import pygame
from game.parrot import _aaellipse


SIZE = 22
_SS  = 44


def _ring(surf, color, center, rx, ry, width):
    cx, cy = center
    rect = pygame.Rect(int(cx - rx), int(cy - ry), int(rx * 2), int(ry * 2))
    pygame.draw.ellipse(surf, color, rect, width)


def _build(PAL):
    """Render the Golden Glyph Disc on a 44×44 canvas; returns 22×22."""
    GOLD      = PAL["gold"]
    BRONZE    = PAL["bronze"]
    GLYPH     = PAL["glyph"]
    GLYPH_DIM = PAL["glyph_dim"]
    OUTLINE   = PAL["outline"]
    CROWN     = PAL["crown"]

    s  = pygame.Surface((_SS, _SS), pygame.SRCALPHA)
    cx = _SS // 2 + 2
    cy = 34
    disc_rx, disc_ry = 17, 6
    dome_cy = cy - disc_ry - 3

    # Dome
    _aaellipse(s, OUTLINE, (cx, dome_cy), 9, 6)
    _aaellipse(s, GOLD,    (cx, dome_cy), 8, 5)
    _aaellipse(s, CROWN,   (cx - 3, dome_cy - 1), 2, 1)

    # Dark halo around disc
    _aaellipse(s, OUTLINE, (cx, cy), disc_rx + 3, disc_ry + 3)

    # Gradient disc: GOLD top → BRONZE bottom
    disc = pygame.Surface((_SS, _SS), pygame.SRCALPHA)
    for iy in range(-disc_ry, disc_ry + 1):
        t   = (iy + disc_ry) / (disc_ry * 2)
        col = tuple(int(GOLD[i] + (BRONZE[i] - GOLD[i]) * t) for i in range(3))
        frac = 1.0 - (iy / disc_ry) ** 2
        if frac < 0:
            continue
        hw = disc_rx * (frac ** 0.5)
        yy = cy + iy
        pygame.draw.line(disc, col, (cx - hw, yy), (cx + hw, yy))
    s.blit(disc, (0, 0))

    # Brim overhang
    brim = pygame.Surface((_SS, _SS), pygame.SRCALPHA)
    _aaellipse(brim, (*BRONZE, 180), (cx, cy + disc_ry - 1), disc_rx + 2, 3)
    s.blit(brim, (0, 0))

    # Ridged rim
    _ring(s, BRONZE, (cx, cy), disc_rx - 1, disc_ry - 1, 1)

    # Crown catch-light on disc top
    hi = pygame.Surface((_SS, _SS), pygame.SRCALPHA)
    _aaellipse(hi, (*CROWN, 160), (cx - 4, cy - disc_ry + 2), 5, 2)
    s.blit(hi, (0, 0))

    # Glyph energy lower rim (clipped to lower half)
    energy = pygame.Surface((_SS, _SS), pygame.SRCALPHA)
    _ring(energy, (*GLYPH, 130), (cx, cy + 1), disc_rx - 2, disc_ry - 1, 1)
    energy.fill((0, 0, 0, 0), pygame.Rect(0, 0, _SS, cy + 3))
    s.blit(energy, (0, 0))

    # Central diamond glyph + echo dots
    gy   = cy + 5
    glow = pygame.Surface((_SS, _SS), pygame.SRCALPHA)
    pygame.draw.polygon(glow, (*GLYPH, 80),
        [(cx, gy - 5), (cx + 4, gy), (cx, gy + 5), (cx - 4, gy)])
    s.blit(glow, (0, 0))
    pygame.draw.polygon(s, GLYPH,
        [(cx, gy - 4), (cx + 3, gy), (cx, gy + 4), (cx - 3, gy)])
    _aaellipse(s, CROWN,     (cx,      gy), 1, 1)
    _aaellipse(s, GLYPH_DIM, (cx - 9,  gy), 2, 2)
    _aaellipse(s, GLYPH_DIM, (cx + 9,  gy), 2, 2)

    return pygame.transform.smoothscale(s, (SIZE, SIZE))


_PALETTES = {
    "original": {
        "gold":      (244, 197,  68),
        "bronze":    (176, 122,  30),
        "glyph":     ( 72, 240, 205),
        "glyph_dim": ( 36, 120, 103),
        "outline":   ( 42,  27,   8),
        "crown":     (255, 240, 176),
    },
    "sapphire": {
        "gold":      (140, 195, 255),
        "bronze":    ( 38,  78, 165),
        "glyph":     (255, 228,  90),
        "glyph_dim": (160, 140,  50),
        "outline":   (  8,  15,  45),
        "crown":     (215, 235, 255),
    },
    "rose_gold": {
        "gold":      (255, 185, 160),
        "bronze":    (195,  85,  75),
        "glyph":     (195,  85, 240),
        "glyph_dim": (110,  42, 145),
        "outline":   ( 55,  18,  18),
        "crown":     (255, 230, 220),
    },
    "obsidian": {
        "gold":      ( 90,  86, 105),
        "bronze":    ( 28,  24,  38),
        "glyph":     (255, 115,  10),
        "glyph_dim": (160,  58,   5),
        "outline":   ( 10,   8,  20),
        "crown":     (170, 165, 200),
    },
    "jade": {
        "gold":      (100, 210, 145),
        "bronze":    ( 28, 100,  58),
        "glyph":     (255, 220,  55),
        "glyph_dim": (165, 140,  28),
        "outline":   (  8,  30,  16),
        "crown":     (200, 255, 220),
    },
    "amethyst": {
        "gold":      (205, 155, 255),
        "bronze":    ( 95,  45, 185),
        "glyph":     (  0, 255, 185),
        "glyph_dim": (  0, 130,  90),
        "outline":   ( 30,   8,  62),
        "crown":     (240, 220, 255),
    },
}


def build(mode: str = "normal") -> pygame.Surface:
    from game import store_data
    key = store_data.parcel_variant("parcel_ufo") or "original"
    return _build(_PALETTES.get(key, _PALETTES["original"]))
