"""NEON NIGHT-DINER — Design 4, 4 beam/cord variants for art review.

Same hull / dome / chase dots as R3. Only the tractor-beam element below the
disc changes across the 4 variants:
  A  LASER    — single hot cyan line with wide glow, no fill
  B  CHAIN    — 4 linked oval rings in cyan + magenta
  C  CABLE    — twisted two-strand rope (cyan + magenta strands crossing)
  D  DASHED   — segmented pulsed beam (stacked filled boxes with gaps)
"""
import pygame, math

SIZE = 22
SS   = 44

HULL    = (24, 18, 40)
CYAN    = (0, 229, 255)
MAGENTA = (255, 61, 203)
VIOLET  = (130, 20, 255)
OUTLINE = (8, 6, 14)


def _glow_line(s, color, p1, p2, core_w=3, glow_w=6):
    g = pygame.Surface((SS, SS), pygame.SRCALPHA)
    pygame.draw.line(g, (*color, 70), p1, p2, glow_w)
    s.blit(g, (0, 0))
    pygame.draw.line(s, color, p1, p2, core_w)


def _glow_ellipse(s, color, rect, core_w=3, glow_w=6):
    g = pygame.Surface((SS, SS), pygame.SRCALPHA)
    gr = rect.inflate(2, 2)
    pygame.draw.ellipse(g, (*color, 70), gr, glow_w)
    s.blit(g, (0, 0))
    pygame.draw.ellipse(s, color, rect, core_w)


def _base(beam_top, beam_bot):
    """Draw the hull/dome/outline shared by all variants. Returns (s, cx, disc_cy, disc_rx, disc_ry)."""
    s = pygame.Surface((SS, SS), pygame.SRCALPHA)
    cx      = SS // 2
    disc_cy = 35
    disc_rx, disc_ry = 18, 5
    dome_cx, dome_cy = cx, disc_cy - 6
    dome_rx, dome_ry = 7, 5

    disc_rect = pygame.Rect(cx - disc_rx, disc_cy - disc_ry, disc_rx*2, disc_ry*2)
    dome_rect = pygame.Rect(dome_cx - dome_rx, dome_cy - dome_ry, dome_rx*2, dome_ry*2)

    # Dark outline under everything
    pygame.draw.ellipse(s, OUTLINE,
        pygame.Rect(cx - disc_rx - 2, disc_cy - disc_ry - 2,
                    (disc_rx+2)*2, (disc_ry+2)*2))

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
        (cx - disc_rx + 3, disc_cy), (cx + disc_rx - 3, disc_cy),
        core_w=2, glow_w=5)

    # Chase dots
    n = 4
    for i in range(n):
        angle = math.radians(210 + 120 * i / (n - 1))
        dx = cx + (disc_rx - 2) * math.cos(angle)
        dy = disc_cy + (disc_ry - 1) * math.sin(angle)
        col = CYAN if i % 2 == 0 else MAGENTA
        dot = pygame.Surface((SS, SS), pygame.SRCALPHA)
        pygame.draw.circle(dot, (*col, 120), (int(dx), int(dy)), 5)
        s.blit(dot, (0, 0))
        pygame.draw.circle(s, col, (int(dx), int(dy)), 3)

    return s, cx, disc_cy, disc_rx, disc_ry


def build_laser(mode="normal"):
    """A: Single hot-cyan laser line — slim, sci-fi, no fill clutter."""
    cx      = SS // 2
    disc_cy = 35
    disc_ry = 5
    beam_top = disc_cy + disc_ry
    beam_bot = beam_top + 14
    s, cx, disc_cy, disc_rx, disc_ry = _base(beam_top, beam_bot)

    # Wide glow under the line
    glow = pygame.Surface((SS, SS), pygame.SRCALPHA)
    pygame.draw.line(glow, (*CYAN, 35), (cx, beam_top), (cx, beam_bot), 12)
    pygame.draw.line(glow, (*CYAN, 70), (cx, beam_top), (cx, beam_bot), 6)
    s.blit(glow, (0, 0))
    # Hot 2px core
    pygame.draw.line(s, CYAN, (cx, beam_top), (cx, beam_bot), 2)
    # Tiny bright tip dot at bottom
    pygame.draw.circle(s, (255, 255, 255), (cx, beam_bot), 2)

    return pygame.transform.smoothscale(s, (SIZE, SIZE))


def build_chain(mode="normal"):
    """B: 4 linked oval rings (alternating cyan/magenta) — retro sci-fi chain."""
    cx      = SS // 2
    disc_cy = 35
    disc_ry = 5
    beam_top = disc_cy + disc_ry
    beam_bot = beam_top + 14
    s, cx, disc_cy, disc_rx, disc_ry = _base(beam_top, beam_bot)

    # 4 link ovals stacked vertically; each 6px tall × 4px wide
    link_h = 4
    link_w = 6
    gap    = 1
    n_links = 4
    total_h = n_links * link_h + (n_links - 1) * gap
    start_y = beam_top + (beam_bot - beam_top - total_h) // 2

    for i in range(n_links):
        ly  = start_y + i * (link_h + gap)
        col = CYAN if i % 2 == 0 else MAGENTA
        rect = pygame.Rect(cx - link_w // 2, ly, link_w, link_h)
        # Soft glow
        go = pygame.Surface((SS, SS), pygame.SRCALPHA)
        pygame.draw.ellipse(go, (*col, 60), rect.inflate(4, 4), 5)
        s.blit(go, (0, 0))
        # Hot ring
        pygame.draw.ellipse(s, col, rect, 2)

    return pygame.transform.smoothscale(s, (SIZE, SIZE))


def build_cable(mode="normal"):
    """C: Twisted two-strand cord — cyan + magenta helical braid."""
    cx      = SS // 2
    disc_cy = 35
    disc_ry = 5
    beam_top = disc_cy + disc_ry + 1
    beam_bot = beam_top + 13
    s, cx, disc_cy, disc_rx, disc_ry = _base(beam_top - 1, beam_bot)

    # Two strands weave left+right of center, crossing every 4px
    period = 8    # pixels per half-twist (full cross every 4px)
    amp    = 3    # ± pixels from center

    steps  = beam_bot - beam_top
    pts_c = []   # cyan strand
    pts_m = []   # magenta strand
    for step in range(steps + 1):
        y  = beam_top + step
        t  = step / period * math.pi   # phase ramps continuously
        pts_c.append((cx + int(amp * math.sin(t)),         y))
        pts_m.append((cx + int(amp * math.sin(t + math.pi)), y))

    # Glow pass for both strands
    glow = pygame.Surface((SS, SS), pygame.SRCALPHA)
    if len(pts_c) > 1:
        pygame.draw.lines(glow, (*CYAN,    60), False, pts_c, 5)
        pygame.draw.lines(glow, (*MAGENTA, 60), False, pts_m, 5)
    s.blit(glow, (0, 0))
    # Hot 2px core
    if len(pts_c) > 1:
        pygame.draw.lines(s, CYAN,    False, pts_c, 2)
        pygame.draw.lines(s, MAGENTA, False, pts_m, 2)

    return pygame.transform.smoothscale(s, (SIZE, SIZE))


def build_dashed(mode="normal"):
    """D: Segmented pulse beam — stacked filled rectangles with bright-edge gaps."""
    cx      = SS // 2
    disc_cy = 35
    disc_ry = 5
    beam_top = disc_cy + disc_ry
    beam_bot = beam_top + 14
    s, cx, disc_cy, disc_rx, disc_ry = _base(beam_top, beam_bot)

    # 3 segments separated by 1px gaps; violet fill + cyan border each
    seg_h   = 3
    gap_h   = 2
    seg_w   = 10    # narrower than the old wide polygon
    n_segs  = 3
    total   = n_segs * seg_h + (n_segs - 1) * gap_h
    start_y = beam_top + 2

    for i in range(n_segs):
        sy  = start_y + i * (seg_h + gap_h)
        # Glow backing
        glow = pygame.Surface((SS, SS), pygame.SRCALPHA)
        pygame.draw.rect(glow, (*VIOLET, 100),
            pygame.Rect(cx - seg_w // 2 - 2, sy - 1, seg_w + 4, seg_h + 2))
        s.blit(glow, (0, 0))
        # Fill
        pygame.draw.rect(s, VIOLET,
            pygame.Rect(cx - seg_w // 2, sy, seg_w, seg_h))
        # Cyan bright edge line at top of each segment
        pygame.draw.line(s, CYAN,
            (cx - seg_w // 2, sy), (cx + seg_w // 2, sy), 1)
        # Hot cyan center dot
        pygame.draw.circle(s, CYAN, (cx, sy + seg_h // 2), 1)

    return pygame.transform.smoothscale(s, (SIZE, SIZE))


# Build map for the render script
VARIANTS = [
    ("A — LASER",   build_laser),
    ("B — CHAIN",   build_chain),
    ("C — CABLE",   build_cable),
    ("D — DASHED",  build_dashed),
]
