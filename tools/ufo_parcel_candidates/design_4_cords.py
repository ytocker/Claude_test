"""NEON NIGHT-DINER — Design 4, 4 beam/cord variants for art review.

Disc sits at cy=26 (centre of the 44px canvas) giving 12px of cord space
below (SS y=31..43 → 6px at 22px display). All variants share the same
hull/dome/rim/seam/chase-dots.

  A  LASER   — single cyan laser line + wide glow bloom
  B  CHAIN   — 3 linked oval rings alternating cyan / magenta
  C  CABLE   — two-strand helical braid (cyan + magenta zigzag)
  D  DASHED  — 2 violet pulse segments with a cyan-edged gap
"""
import pygame, math

SIZE = 22
SS   = 44

HULL    = (24, 18, 40)
CYAN    = (0, 229, 255)
MAGENTA = (255, 61, 203)
VIOLET  = (130, 20, 255)
OUTLINE = (8, 6, 14)

DISC_CY  = 26
DISC_RX  = 18
DISC_RY  = 5
DOME_CY  = DISC_CY - 7
DOME_RX  = 7
DOME_RY  = 5
BEAM_TOP = DISC_CY + DISC_RY    # = 31
BEAM_BOT = SS - 2               # = 42  →  11px of cord


def _glow_line(s, color, p1, p2, core_w=3, glow_w=6):
    g = pygame.Surface((SS, SS), pygame.SRCALPHA)
    pygame.draw.line(g, (*color, 70), p1, p2, glow_w)
    s.blit(g, (0, 0))
    pygame.draw.line(s, color, p1, p2, core_w)


def _glow_ellipse(s, color, rect, core_w=3, glow_w=6):
    g = pygame.Surface((SS, SS), pygame.SRCALPHA)
    pygame.draw.ellipse(g, (*color, 70), rect.inflate(2, 2), glow_w)
    s.blit(g, (0, 0))
    pygame.draw.ellipse(s, color, rect, core_w)


def _hull(cord_fn):
    """Build the shared hull then call cord_fn(s, cx) to add the cord."""
    s  = pygame.Surface((SS, SS), pygame.SRCALPHA)
    cx = SS // 2

    disc_rect = pygame.Rect(cx - DISC_RX, DISC_CY - DISC_RY, DISC_RX*2, DISC_RY*2)
    dome_rect = pygame.Rect(cx - DOME_RX, DOME_CY - DOME_RY, DOME_RX*2, DOME_RY*2)

    # Draw cord FIRST so hull blit covers the join cleanly
    cord_fn(s, cx)

    # Dark outline around disc
    pygame.draw.ellipse(s, OUTLINE,
        pygame.Rect(cx - DISC_RX - 2, DISC_CY - DISC_RY - 2,
                    (DISC_RX+2)*2, (DISC_RY+2)*2))

    # Hull fill
    pygame.draw.ellipse(s, HULL, dome_rect)
    pygame.draw.ellipse(s, HULL, disc_rect)

    # Inner violet glow
    ig = pygame.Surface((SS, SS), pygame.SRCALPHA)
    pygame.draw.ellipse(ig, (*VIOLET, 60), disc_rect.inflate(-12, -2))
    s.blit(ig, (0, 0))

    # Dome + rim + seam
    _glow_ellipse(s, MAGENTA, dome_rect, core_w=2, glow_w=5)
    _glow_ellipse(s, CYAN, disc_rect, core_w=3, glow_w=6)
    _glow_line(s, MAGENTA,
        (cx - DISC_RX + 3, DISC_CY), (cx + DISC_RX - 3, DISC_CY),
        core_w=2, glow_w=5)

    # Chase-light dots
    n = 4
    for i in range(n):
        angle = math.radians(210 + 120 * i / (n - 1))
        dx = cx + (DISC_RX - 2) * math.cos(angle)
        dy = DISC_CY + (DISC_RY - 1) * math.sin(angle)
        col = CYAN if i % 2 == 0 else MAGENTA
        dot = pygame.Surface((SS, SS), pygame.SRCALPHA)
        pygame.draw.circle(dot, (*col, 120), (int(dx), int(dy)), 5)
        s.blit(dot, (0, 0))
        pygame.draw.circle(s, col, (int(dx), int(dy)), 3)

    return pygame.transform.smoothscale(s, (SIZE, SIZE))


# ── A: LASER ────────────────────────────────────────────────────────────────
def _cord_laser(s, cx):
    glow = pygame.Surface((SS, SS), pygame.SRCALPHA)
    pygame.draw.line(glow, (*CYAN, 30), (cx, BEAM_TOP), (cx, BEAM_BOT), 14)
    pygame.draw.line(glow, (*CYAN, 70), (cx, BEAM_TOP), (cx, BEAM_BOT),  6)
    s.blit(glow, (0, 0))
    pygame.draw.line(s, CYAN, (cx, BEAM_TOP), (cx, BEAM_BOT), 2)
    pygame.draw.circle(s, (255, 255, 255), (cx, BEAM_BOT), 2)   # bright tip


def build_laser(mode="normal"):
    return _hull(_cord_laser)


# ── B: CHAIN ────────────────────────────────────────────────────────────────
def _cord_chain(s, cx):
    link_w, link_h, gap = 8, 4, 2
    n_links = 3
    total   = n_links * link_h + (n_links - 1) * gap
    sy      = BEAM_TOP + (BEAM_BOT - BEAM_TOP - total) // 2
    for i in range(n_links):
        y   = sy + i * (link_h + gap)
        col = CYAN if i % 2 == 0 else MAGENTA
        r   = pygame.Rect(cx - link_w // 2, y, link_w, link_h)
        glo = pygame.Surface((SS, SS), pygame.SRCALPHA)
        pygame.draw.ellipse(glo, (*col, 55), r.inflate(4, 4), 5)
        s.blit(glo, (0, 0))
        pygame.draw.ellipse(s, col, r, 2)


def build_chain(mode="normal"):
    return _hull(_cord_chain)


# ── C: CABLE ────────────────────────────────────────────────────────────────
def _cord_cable(s, cx):
    amp    = 4          # ± pixels each strand deviates
    period = 10         # pixels per full twist cycle
    pts_c, pts_m = [], []
    for step in range(BEAM_BOT - BEAM_TOP + 1):
        y = BEAM_TOP + step
        t = step / period * math.pi * 2
        pts_c.append((cx + int(amp * math.sin(t)),            y))
        pts_m.append((cx + int(amp * math.sin(t + math.pi)), y))
    if len(pts_c) > 1:
        glo = pygame.Surface((SS, SS), pygame.SRCALPHA)
        pygame.draw.lines(glo, (*CYAN,    55), False, pts_c, 5)
        pygame.draw.lines(glo, (*MAGENTA, 55), False, pts_m, 5)
        s.blit(glo, (0, 0))
        pygame.draw.lines(s, CYAN,    False, pts_c, 2)
        pygame.draw.lines(s, MAGENTA, False, pts_m, 2)


def build_cable(mode="normal"):
    return _hull(_cord_cable)


# ── D: DASHED ───────────────────────────────────────────────────────────────
def _cord_dashed(s, cx):
    seg_w  = 12
    seg_h  = 4
    gap_h  = 3
    n      = 2
    total  = n * seg_h + (n - 1) * gap_h
    sy     = BEAM_TOP + (BEAM_BOT - BEAM_TOP - total) // 2
    colors = [VIOLET, CYAN]
    for i in range(n):
        y   = sy + i * (seg_h + gap_h)
        col = colors[i]
        r   = pygame.Rect(cx - seg_w // 2, y, seg_w, seg_h)
        glo = pygame.Surface((SS, SS), pygame.SRCALPHA)
        pygame.draw.rect(glo, (*VIOLET, 90), r.inflate(4, 2))
        s.blit(glo, (0, 0))
        pygame.draw.rect(s, col, r)
        pygame.draw.line(s, (255, 255, 255), (r.left, r.top), (r.right, r.top), 1)


def build_dashed(mode="normal"):
    return _hull(_cord_dashed)


# Export for render script
VARIANTS = [
    ("A — LASER",   build_laser),
    ("B — CHAIN",   build_chain),
    ("C — CABLE",   build_cable),
    ("D — DASHED",  build_dashed),
]
