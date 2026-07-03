"""GOLDEN GLYPH DISC — Design 3, 5 colour-palette variants.

Same geometry as R3. Only the disc/dome/glyph palette changes.

  1  ORIGINAL   — hammered gold + turquoise glyph (the R3 build)
  2  SAPPHIRE   — steel-blue disc + warm gold glyph
  3  ROSE GOLD  — rose-gold disc + violet glyph
  4  OBSIDIAN   — dark-slate disc + hot-orange glyph
  5  JADE       — deep-green disc + bright-gold glyph
  6  AMETHYST   — purple disc + cyan-green glyph
"""
import pygame
from game.parrot import _aaellipse

SIZE = 22
SS   = 44


def _ring(surf, color, center, rx, ry, width):
    cx, cy = center
    rect = pygame.Rect(int(cx - rx), int(cy - ry), int(rx * 2), int(ry * 2))
    pygame.draw.ellipse(surf, color, rect, width)


def _build(PAL):
    """Build a 22×22 Surface with the given palette dict."""
    GOLD      = PAL["gold"]
    BRONZE    = PAL["bronze"]
    GLYPH     = PAL["glyph"]
    GLYPH_DIM = PAL["glyph_dim"]
    OUTLINE   = PAL["outline"]
    CROWN     = PAL["crown"]

    s = pygame.Surface((SS, SS), pygame.SRCALPHA)
    cx = SS // 2 + 2
    cy = 34
    disc_rx, disc_ry = 17, 6
    dome_cy = cy - disc_ry - 3

    # Dome
    _aaellipse(s, OUTLINE, (cx, dome_cy), 9, 6)
    _aaellipse(s, GOLD,    (cx, dome_cy), 8, 5)
    _aaellipse(s, CROWN,   (cx - 3, dome_cy - 1), 2, 1)

    # Dark halo
    _aaellipse(s, OUTLINE, (cx, cy), disc_rx + 3, disc_ry + 3)

    # Gradient disc (GOLD top → BRONZE bottom)
    disc = pygame.Surface((SS, SS), pygame.SRCALPHA)
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
    brim = pygame.Surface((SS, SS), pygame.SRCALPHA)
    _aaellipse(brim, (*BRONZE, 180), (cx, cy + disc_ry - 1), disc_rx + 2, 3)
    s.blit(brim, (0, 0))

    # Ridged rim
    _ring(s, BRONZE, (cx, cy), disc_rx - 1, disc_ry - 1, 1)

    # Crown catch-light on disc top
    hi = pygame.Surface((SS, SS), pygame.SRCALPHA)
    _aaellipse(hi, (*CROWN, 160), (cx - 4, cy - disc_ry + 2), 5, 2)
    s.blit(hi, (0, 0))

    # Glyph energy lower rim
    energy = pygame.Surface((SS, SS), pygame.SRCALPHA)
    _ring(energy, (*GLYPH, 130), (cx, cy + 1), disc_rx - 2, disc_ry - 1, 1)
    energy.fill((0, 0, 0, 0), pygame.Rect(0, 0, SS, cy + 3))
    s.blit(energy, (0, 0))

    # Central diamond glyph + echo dots
    gy = cy + 5
    glow = pygame.Surface((SS, SS), pygame.SRCALPHA)
    pygame.draw.polygon(glow, (*GLYPH, 80),
        [(cx, gy - 5), (cx + 4, gy), (cx, gy + 5), (cx - 4, gy)])
    s.blit(glow, (0, 0))
    pygame.draw.polygon(s, GLYPH,
        [(cx, gy - 4), (cx + 3, gy), (cx, gy + 4), (cx - 3, gy)])
    _aaellipse(s, CROWN, (cx, gy), 1, 1)
    _aaellipse(s, GLYPH_DIM, (cx - 9, gy), 2, 2)
    _aaellipse(s, GLYPH_DIM, (cx + 9, gy), 2, 2)

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
        "gold":      (140, 195, 255),   # bright steel blue
        "bronze":    ( 38,  78, 165),   # deep navy
        "glyph":     (255, 228,  90),   # warm gold glyph
        "glyph_dim": (160, 140,  50),
        "outline":   (  8,  15,  45),
        "crown":     (215, 235, 255),
    },
    "rose_gold": {
        "gold":      (255, 185, 160),   # rose gold
        "bronze":    (195,  85,  75),   # deep copper
        "glyph":     (195,  85, 240),   # violet
        "glyph_dim": (110,  42, 145),
        "outline":   ( 55,  18,  18),
        "crown":     (255, 230, 220),
    },
    "obsidian": {
        "gold":      ( 90,  86, 105),   # dark slate
        "bronze":    ( 28,  24,  38),   # near-black
        "glyph":     (255, 115,  10),   # hot orange
        "glyph_dim": (160,  58,   5),
        "outline":   ( 10,   8,  20),
        "crown":     (170, 165, 200),
    },
    "jade": {
        "gold":      (100, 210, 145),   # bright jade
        "bronze":    ( 28, 100,  58),   # forest green
        "glyph":     (255, 220,  55),   # bright gold
        "glyph_dim": (165, 140,  28),
        "outline":   (  8,  30,  16),
        "crown":     (200, 255, 220),
    },
    "amethyst": {
        "gold":      (205, 155, 255),   # bright purple
        "bronze":    ( 95,  45, 185),   # deep violet
        "glyph":     (  0, 255, 185),   # cyan-green
        "glyph_dim": (  0, 130,  90),
        "outline":   ( 30,   8,  62),
        "crown":     (240, 220, 255),
    },
}


def build_original(mode="normal"):  return _build(_PALETTES["original"])
def build_sapphire(mode="normal"):  return _build(_PALETTES["sapphire"])
def build_rose_gold(mode="normal"): return _build(_PALETTES["rose_gold"])
def build_obsidian(mode="normal"):  return _build(_PALETTES["obsidian"])
def build_jade(mode="normal"):      return _build(_PALETTES["jade"])
def build_amethyst(mode="normal"):  return _build(_PALETTES["amethyst"])


VARIANTS = [
    ("ORIGINAL\nGold + Teal",       build_original),
    ("SAPPHIRE\nBlue + Gold",        build_sapphire),
    ("ROSE GOLD\nCopper + Violet",   build_rose_gold),
    ("OBSIDIAN\nBlack + Orange",     build_obsidian),
    ("JADE\nGreen + Gold",           build_jade),
    ("AMETHYST\nPurple + Cyan",      build_amethyst),
]
