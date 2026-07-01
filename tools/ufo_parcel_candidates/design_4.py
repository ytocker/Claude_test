"""NEON NIGHT-DINER — cyberpunk saucer as a glowing neon sign. R2.

Near-black hull reads as a canvas for neon light. Every edge is drawn as
a glow pass + hot core (wide soft alpha under narrow bright). The key R2
fix: a 1-2px dark outline baked around the full disc so the silhouette
survives day-blue sky where the hull would otherwise dissolve, and all
neon strokes are thicker so they survive 2× downscale.
"""
import pygame, math

SIZE = 22
SS   = 44

HULL    = (24, 18, 40)     # near-black hull (navy-purple, not pure black)
CYAN    = (0, 229, 255)
MAGENTA = (255, 61, 203)
VIOLET  = (130, 20, 255)
OUTLINE = (8, 6, 14)       # 1px darker outline around whole disc


def _glow_line(s, color, p1, p2, core_w=3, glow_w=6):
    """Glow pass + hot core. core_w=3 survives 2× downscale."""
    g = pygame.Surface((SS, SS), pygame.SRCALPHA)
    pygame.draw.line(g, (*color, 70), p1, p2, glow_w)
    s.blit(g, (0, 0))
    pygame.draw.line(s, color, p1, p2, core_w)


def _glow_ellipse(s, color, rect, core_w=3, glow_w=6):
    """Ellipse outline as glow ring + hot core."""
    g = pygame.Surface((SS, SS), pygame.SRCALPHA)
    gr = rect.inflate(2, 2)
    pygame.draw.ellipse(g, (*color, 70), gr, glow_w)
    s.blit(g, (0, 0))
    pygame.draw.ellipse(s, color, rect, core_w)


def build(mode="normal"):
    s = pygame.Surface((SS, SS), pygame.SRCALPHA)

    cx      = SS // 2
    disc_cy = 28
    disc_rx, disc_ry = 17, 5
    dome_cx, dome_cy = cx, disc_cy - 6
    dome_rx, dome_ry = 7, 5

    disc_rect = pygame.Rect(cx - disc_rx, disc_cy - disc_ry, disc_rx*2, disc_ry*2)
    dome_rect = pygame.Rect(dome_cx - dome_rx, dome_cy - dome_ry, dome_rx*2, dome_ry*2)

    # ---- Violet beam spotlight first (drawn under everything) ----
    beam_top = disc_cy + disc_ry
    beam_bot = beam_top + 14
    beam = pygame.Surface((SS, SS), pygame.SRCALPHA)
    pygame.draw.polygon(beam, (*VIOLET, 100),
        [(cx-7, beam_top), (cx+7, beam_top), (cx+12, beam_bot), (cx-12, beam_bot)])
    s.blit(beam, (0, 0))
    # Bright neon-cyan edges on the beam
    _glow_line(s, CYAN, (cx-7, beam_top), (cx-12, beam_bot), core_w=2, glow_w=4)
    _glow_line(s, CYAN, (cx+7, beam_top), (cx+12, beam_bot), core_w=2, glow_w=4)

    # ---- Dark outline around whole disc for day-sky contrast ----
    pygame.draw.ellipse(s, OUTLINE,
        pygame.Rect(cx - disc_rx - 2, disc_cy - disc_ry - 2,
                    (disc_rx+2)*2, (disc_ry+2)*2))

    # ---- Near-black hull fill ----
    pygame.draw.ellipse(s, HULL, dome_rect)
    pygame.draw.ellipse(s, HULL, disc_rect)

    # ---- Inner violet glow bleeding through hull ----
    ig = pygame.Surface((SS, SS), pygame.SRCALPHA)
    pygame.draw.ellipse(ig, (*VIOLET, 60),
        disc_rect.inflate(-12, -2))
    s.blit(ig, (0, 0))

    # ---- Magenta dome outline ----
    _glow_ellipse(s, MAGENTA, dome_rect, core_w=2, glow_w=5)

    # ---- Cyan neon rim around disc (3px core = 1.5px at 22px, reads crisp) ----
    _glow_ellipse(s, CYAN, disc_rect, core_w=3, glow_w=6)

    # ---- Magenta equator seam across the disc waist ----
    _glow_line(s, MAGENTA,
        (cx - disc_rx + 3, disc_cy), (cx + disc_rx - 3, disc_cy),
        core_w=2, glow_w=5)

    # ---- Chase-light dots on the lower rim — the signature (8 dots) ----
    n = 8
    for i in range(n):
        angle = math.radians(200 + 140 * i / (n - 1))
        dx = cx + (disc_rx - 2) * math.cos(angle)
        dy = disc_cy + (disc_ry - 1) * math.sin(angle)
        col = CYAN if i % 2 == 0 else MAGENTA
        dot = pygame.Surface((SS, SS), pygame.SRCALPHA)
        pygame.draw.circle(dot, (*col, 100), (int(dx), int(dy)), 4)
        s.blit(dot, (0, 0))
        pygame.draw.circle(s, col, (int(dx), int(dy)), 2)

    return pygame.transform.smoothscale(s, (SIZE, SIZE))
