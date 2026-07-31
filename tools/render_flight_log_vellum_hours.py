"""Render the `vellum_hours` Flight Log concept sheet.

Concept: the run's day/night cycle is a single leaf from a Book of Hours.
Seven roundels down the ruled block, one per phase. A roundel is only
painted for time the player actually flew; everything ahead of death is
left as bare burnished vellum with the illuminator's sinopia underdrawing
still showing. Death is signalled ONCE — a scarlet rubricated versal in
the text column — so scarlet stays the rarest ink on the page.

Run:
    python tools/render_flight_log_vellum_hours.py
"""
import os
import math
import random

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
import pygame

pygame.display.init()
pygame.display.set_mode((1, 1))
pygame.font.init()

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT_PATH = os.path.join(ROOT, "game", "assets", "LiberationSans-Bold.ttf")
OUT_DIR = os.path.join(ROOT, "docs", "flight_log_screen", "vellum_hours")
os.makedirs(OUT_DIR, exist_ok=True)

W, H = 360, 640

# ── palette ──────────────────────────────────────────────────────────────────
TABLE = (20, 14, 10)          # dark walnut the leaf lies on
VELLUM = (238, 230, 212)      # leaf body
VELLUM_BRIGHT = (242, 236, 221)  # burnished, unflown roundels — brightest on the leaf
OCHRE = (168, 112, 58)        # sinopia: every guide line, rule and rustic capital
SCARLET = (172, 40, 32)       # rubrication — the versal ONLY
GOLD = (240, 192, 64)
INK = (38, 30, 24)

# ── biome sky keyframes (sky_* + star_alpha lifted from game/biome.py) ───────
_SKY_KEYS = [
    (0.00, (40, 110, 200), (90, 170, 230), (170, 220, 245), 0),
    (0.18, (80, 120, 200), (220, 175, 140), (255, 210, 160), 0),
    (0.32, (90, 50, 130), (230, 95, 120), (255, 160, 90), 20),
    (0.48, (25, 20, 70), (70, 45, 130), (170, 95, 140), 130),
    (0.62, (5, 8, 30), (15, 25, 70), (35, 55, 115), 235),
    (0.78, (30, 30, 80), (70, 60, 140), (200, 130, 180), 90),
    (0.90, (50, 100, 180), (255, 150, 150), (255, 220, 170), 0),
    (1.00, (40, 110, 200), (90, 170, 230), (170, 220, 245), 0),
]

PHASE_BOUNDARIES = [
    (0.000, "DAY"),
    (0.231, "GOLDEN HOUR"),
    (0.363, "SUNSET"),
    (0.513, "DUSK"),
    (0.644, "NIGHT"),
    (0.794, "PREDAWN"),
    (0.906, "SUNRISE"),
]

EVENT_MARKERS = [
    (0.15, "GEYSER"),
    (0.41, "CLOWN"),
    (0.44, "STORM"),
    (0.85, "SNOW"),
]

# Which ink figure each phase carries. One per roundel, never two.
SILHOUETTE = {
    "DAY": "macaw",
    "GOLDEN HOUR": "macaw",
    "SUNSET": "pillar",
    "DUSK": "pillar",
    "NIGHT": "moon",
    "PREDAWN": "moon",
    "SUNRISE": "macaw",
}

def phase_ref(idx):
    """Sky to paint a band's roundel with.

    The named bands sit slightly *after* the biome keyframe they describe, so
    a band's midpoint already reads as the next phase (NIGHT's midpoint comes
    out predawn-violet). Sampling just inside the band's opening keeps all
    seven roundels true to their own name and clearly distinct from each other.
    """
    b0 = PHASE_BOUNDARIES[idx][0]
    b1 = PHASE_BOUNDARIES[idx + 1][0] if idx + 1 < len(PHASE_BOUNDARIES) else 1.0
    return b0 + 0.05 * (b1 - b0)


RUN_A = dict(death_phase=0.184, pillars="XXV", clock="0:47", folio="i", day=1)
# Day 2 needs a run that outlived a full 5-minute cycle, so the first leaf is
# complete and the second one carries the death.
RUN_B = dict(death_phase=0.550, pillars="LXIII", clock="6:12", folio="ij", day=2)


# ── small helpers ────────────────────────────────────────────────────────────

def lerp(a, b, t):
    return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(3))


def sky_for_phase(phase):
    """sky_top / sky_mid / sky_bot / star_alpha, smoothstepped like biome.py."""
    phase %= 1.0
    for i in range(len(_SKY_KEYS) - 1):
        t0, a_top, a_mid, a_bot, a_star = _SKY_KEYS[i]
        t1, b_top, b_mid, b_bot, b_star = _SKY_KEYS[i + 1]
        if t0 <= phase <= t1:
            span = t1 - t0
            t = (phase - t0) / span if span > 0 else 0.0
            t = t * t * (3 - 2 * t)
            return (lerp(a_top, b_top, t), lerp(a_mid, b_mid, t),
                    lerp(a_bot, b_bot, t), a_star + (b_star - a_star) * t)
    k = _SKY_KEYS[0]
    return k[1], k[2], k[3], k[4]


_FONT_CACHE = {}


def font(size):
    if size not in _FONT_CACHE:
        _FONT_CACHE[size] = pygame.font.Font(FONT_PATH, size)
    return _FONT_CACHE[size]


def spaced_width(text, size, spacing):
    f = font(size)
    return sum(f.size(ch)[0] + spacing for ch in text) - spacing if text else 0


def spaced_text(dest, text, size, color, x, y, spacing=1.5, align="left",
                alpha=255):
    """Rustic capitals: letter-spaced, so short words read as inscription."""
    f = font(size)
    total = spaced_width(text, size, spacing)
    if align == "center":
        x -= total / 2
    elif align == "right":
        x -= total
    cx = x
    for ch in text:
        glyph = f.render(ch, True, color)
        if alpha < 255:
            glyph.set_alpha(alpha)
        dest.blit(glyph, (int(round(cx)), int(round(y))))
        cx += f.size(ch)[0] + spacing
    return total


def dotted_line(dest, color, p0, p1, dot=1, gap=5, alpha=150):
    x0, y0 = p0
    x1, y1 = p1
    dist = math.hypot(x1 - x0, y1 - y0)
    if dist <= 0:
        return
    steps = int(dist // (dot + gap))
    layer = pygame.Surface(dest.get_size(), pygame.SRCALPHA)
    for i in range(steps + 1):
        t = i * (dot + gap) / dist
        if t > 1:
            break
        px = x0 + (x1 - x0) * t
        py = y0 + (y1 - y0) * t
        pygame.draw.circle(layer, color + (alpha,), (int(px), int(py)), dot)
    dest.blit(layer, (0, 0))


def hairline(dest, color, p0, p1, alpha=110, width=1):
    layer = pygame.Surface(dest.get_size(), pygame.SRCALPHA)
    pygame.draw.line(layer, color + (alpha,), p0, p1, width)
    dest.blit(layer, (0, 0))


# ── the leaf itself ──────────────────────────────────────────────────────────

def leaf_polygon(seed=42):
    """A cut sheet of calfskin: corners never square, edges gently deckled."""
    rng = random.Random(seed)
    corners = [(15, 12), (345, 15), (342, 626), (12, 622)]
    pts = []
    for i in range(4):
        ax, ay = corners[i]
        bx, by = corners[(i + 1) % 4]
        seg = 14
        nx, ny = (by - ay), -(bx - ax)
        nlen = math.hypot(nx, ny) or 1
        nx, ny = nx / nlen, ny / nlen
        for s in range(seg):
            t = s / seg
            wob = math.sin(t * math.pi * 2.4 + i * 1.7) * 1.3 + rng.uniform(-0.7, 0.7)
            pts.append((ax + (bx - ax) * t + nx * wob,
                        ay + (by - ay) * t + ny * wob))
    return pts


def leaf_mask(poly, ss=3):
    """Alpha mask for the leaf, supersampled so the deckled edge stays soft."""
    big = pygame.Surface((W * ss, H * ss), pygame.SRCALPHA)
    pygame.draw.polygon(big, (255, 255, 255, 255), [(x * ss, y * ss) for x, y in poly])
    return pygame.transform.smoothscale(big, (W, H))


def vellum_body(mask, seed=42):
    """Base tone + cockle luminance + hair-follicle speckle, cut to the leaf."""
    body = pygame.Surface((W, H), pygame.SRCALPHA)
    body.fill(VELLUM)

    # Cockle: parchment never dries flat, so light pools along soft ridges.
    lw, lh = 30, 52
    add = pygame.Surface((lw, lh))
    sub = pygame.Surface((lw, lh))
    for y in range(lh):
        for x in range(lw):
            u = x / (lw - 1) - 0.5
            v = y / (lh - 1) - 0.5
            ridge = (math.sin(v * 11.0 + math.cos(u * 3.1) * 1.4) * 3.0
                     + math.sin(u * 6.2 + 1.1) * 2.2)
            centre = (1.0 - min(1.0, math.hypot(u * 1.35, v) * 2.05)) * 7.0
            val = ridge + centre - 2.0
            a = max(0, min(26, int(val)))
            s = max(0, min(22, int(-val)))
            add.set_at((x, y), (a, a, a))
            sub.set_at((x, y), (s, s, int(s * 0.7)))
    add = pygame.transform.smoothscale(add, (W, H))
    sub = pygame.transform.smoothscale(sub, (W, H))
    body.blit(add, (0, 0), special_flags=pygame.BLEND_RGB_ADD)
    body.blit(sub, (0, 0), special_flags=pygame.BLEND_RGB_SUB)

    # Hair side: follicles come in tight clusters, not an even scatter.
    rng = random.Random(seed)
    spec = pygame.Surface((W, H), pygame.SRCALPHA)
    for _ in range(140):
        x, y = rng.uniform(8, W - 8), rng.uniform(8, H - 8)
        a = rng.randint(22, 55)
        pygame.draw.circle(spec, (120, 96, 66, a), (int(x), int(y)), 1)
    for _ in range(22):
        cx, cy = rng.uniform(14, W - 14), rng.uniform(14, H - 14)
        for _ in range(3):
            x = cx + rng.uniform(-3.5, 3.5)
            y = cy + rng.uniform(-3.5, 3.5)
            pygame.draw.circle(spec, (112, 88, 60, rng.randint(30, 62)),
                               (int(x), int(y)), 1)
    for _ in range(5):  # faint dermal veining
        x, y = rng.uniform(30, W - 30), rng.uniform(30, H - 30)
        pts = [(x + i * 7, y + math.sin(i * 1.3) * 4 + i * 2) for i in range(5)]
        pygame.draw.lines(spec, (150, 128, 100, 26), False, pts, 1)
    body.blit(spec, (0, 0))

    body.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    return body


def leaf_shadow(poly, dx=5, dy=7, alpha=150):
    sh = pygame.Surface((W, H), pygame.SRCALPHA)
    pygame.draw.polygon(sh, (0, 0, 0, alpha), [(x + dx, y + dy) for x, y in poly])
    small = pygame.transform.smoothscale(sh, (W // 5, H // 5))
    return pygame.transform.smoothscale(small, (W, H))


# ── silhouettes ──────────────────────────────────────────────────────────────

MACAW = [
    [(-0.55, -0.05), (-0.30, -0.30), (0.05, -0.38), (0.32, -0.34), (0.50, -0.20),
     (0.66, -0.26), (0.92, -0.14), (0.68, 0.03), (0.52, 0.07), (0.40, 0.22),
     (0.10, 0.34), (-0.25, 0.30), (-0.50, 0.16)],
    [(-0.45, 0.05), (-1.10, 0.26), (-1.02, 0.44), (-0.38, 0.24)],      # tail
    [(-0.05, -0.20), (-0.24, -0.88), (0.16, -0.60), (0.22, -0.18)],    # wing up
    [(-0.10, 0.10), (-0.34, 0.70), (0.10, 0.44), (0.14, 0.06)],        # wing down
]

PILLAR = [
    [(-0.34, -0.60), (0.34, -0.60), (0.30, -0.44), (-0.30, -0.44)],    # capital
    [(-0.24, -0.44), (0.24, -0.44), (0.20, -0.34), (-0.20, -0.34)],    # necking
    [(-0.19, -0.34), (0.19, -0.34), (0.23, 0.62), (-0.23, 0.62)],      # shaft
    [(-0.33, 0.62), (0.33, 0.62), (0.38, 0.80), (-0.38, 0.80)],        # base
    [(-0.30, -0.60), (-0.44, -0.78), (-0.16, -0.70), (-0.06, -0.60)],  # crown
    [(0.02, -0.60), (0.06, -0.86), (0.26, -0.66), (0.30, -0.60)],
]


def _scaled(shapes, scale, ox, oy):
    return [[(ox + px * scale, oy + py * scale) for px, py in poly]
            for poly in shapes]


def draw_silhouette(surf, kind, cx, cy, r, mode, ss):
    """mode 'ink' = finished illumination, 'sinopia' = ochre underdrawing."""
    stroke = max(1, int(1.6 * ss))
    if kind == "moon":
        rad = int(r * 0.60)
        if mode == "ink":
            pygame.draw.circle(surf, VELLUM_BRIGHT, (cx, cy), rad)
            pygame.draw.circle(surf, INK, (cx, cy), rad, stroke)
            crat = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
            for fx, fy, fr in ((-0.26, -0.20, 0.17), (0.18, 0.10, 0.22),
                               (-0.06, 0.36, 0.11)):
                pygame.draw.circle(crat, INK + (60,),
                                   (int(cx + fx * rad * 2), int(cy + fy * rad * 2)),
                                   max(1, int(fr * rad)))
            surf.blit(crat, (0, 0))
        else:
            pygame.draw.circle(surf, OCHRE, (cx, cy), rad, max(1, ss))
        return

    if kind == "macaw":
        shapes = _scaled(MACAW, r * 0.76, cx + r * 0.07, cy + r * 0.05)
    else:
        shapes = _scaled(PILLAR, r * 1.02, cx, cy - r * 0.02)
    for poly in shapes:
        pts = [(int(round(x)), int(round(y))) for x, y in poly]
        if mode == "ink":
            pygame.draw.polygon(surf, INK, pts)
        else:
            pygame.draw.polygon(surf, OCHRE, pts, max(1, ss))


# ── roundels ─────────────────────────────────────────────────────────────────

def roundel(r, phase_mid, kind, state, seed=0, paint_frac=0.5):
    """state: 'painted' | 'bare' | 'half'. Returns an SRCALPHA square."""
    ss = 4
    pad = 3
    R = r + pad
    size = int(2 * R * ss)
    c = int(R * ss)
    rr = int(r * ss)
    surf = pygame.Surface((size, size), pygame.SRCALPHA)

    sky_top, sky_mid, sky_bot, star_alpha = sky_for_phase(phase_mid)

    # 1 ── bare burnished vellum. The unflown roundels are the brightest thing
    #      on the leaf, so they read as "not yet lived" rather than as holes.
    vell = pygame.Surface((size, size), pygame.SRCALPHA)
    pygame.draw.circle(vell, VELLUM_BRIGHT, (c, c), rr)
    sheen = pygame.Surface((size, size), pygame.SRCALPHA)
    pygame.draw.circle(sheen, (255, 252, 244, 70),
                       (int(c - rr * 0.26), int(c - rr * 0.28)), int(rr * 0.72))
    pygame.draw.circle(sheen, (188, 168, 138, 46),
                       (int(c + rr * 0.30), int(c + rr * 0.32)), int(rr * 0.62))
    sheen = pygame.transform.smoothscale(
        pygame.transform.smoothscale(sheen, (size // 6, size // 6)), (size, size))
    msk = pygame.Surface((size, size), pygame.SRCALPHA)
    pygame.draw.circle(msk, (255, 255, 255, 255), (c, c), rr)
    sheen.blit(msk, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    vell.blit(sheen, (0, 0))

    if state in ("bare", "half"):
        if state == "half":
            draw_silhouette(vell, kind, c, c, rr, "sinopia", ss)
        # Compass work the illuminator leaves behind: prick + guide circle.
        pygame.draw.circle(vell, OCHRE, (c, c), int(rr - 1.8 * ss), max(1, ss))
        arm = int(2.2 * ss)
        pygame.draw.line(vell, OCHRE, (c - arm, c), (c + arm, c), max(1, ss))
        pygame.draw.line(vell, OCHRE, (c, c - arm), (c, c + arm), max(1, ss))
        pygame.draw.circle(vell, OCHRE, (c, c), max(1, int(0.9 * ss)))

    surf.blit(vell, (0, 0))

    # 2 ── painted sky + its one ink figure + gilding.
    if state in ("painted", "half"):
        sky = pygame.Surface((size, size), pygame.SRCALPHA)
        for y in range(c - rr, c + rr + 1):
            t = (y - (c - rr)) / (2 * rr)
            col = (lerp(sky_top, sky_mid, t * 2) if t < 0.5
                   else lerp(sky_mid, sky_bot, (t - 0.5) * 2))
            pygame.draw.line(sky, col, (c - rr, y), (c + rr, y))
        if star_alpha > 4:
            rng = random.Random(seed + 7)
            for _ in range(9):
                a = rng.uniform(0, math.tau)
                d = rng.uniform(0, rr * 0.82)
                sx, sy = c + math.cos(a) * d, c + math.sin(a) * d * 0.85
                pygame.draw.circle(sky, GOLD + (int(star_alpha * 0.9),),
                                   (int(sx), int(sy)), max(1, int(0.8 * ss)))
        sky.blit(msk, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        draw_silhouette(sky, kind, c, c, rr, "ink", ss)
        # Gilded frame, laid last like real gold leaf over the finished paint.
        pygame.draw.circle(sky, GOLD, (c, c), int(rr - 1.0 * ss), max(1, int(1.8 * ss)))
        pygame.draw.circle(sky, INK, (c, c), rr, max(1, ss))

        if state == "half":
            # The brush stopped mid-roundel; the edge wobbles like a real hand.
            cut = pygame.Surface((size, size), pygame.SRCALPHA)
            for y in range(size):
                wob = math.sin(y * 0.055 / ss * 4) * 1.6 * ss
                bx = c - rr + 2 * rr * paint_frac + wob
                pygame.draw.line(cut, (255, 255, 255, 255), (0, y), (int(bx), y))
            sky.blit(cut, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        surf.blit(sky, (0, 0))

    return pygame.transform.smoothscale(surf, (2 * R, 2 * R))


# ── marginal drolleries ──────────────────────────────────────────────────────

def drollery(dest, kind, x, y, inked):
    """Small marginal beasts/objects. Ink once flown, sinopia while still ahead."""
    col = INK if inked else OCHRE
    lw = 1
    layer = pygame.Surface(dest.get_size(), pygame.SRCALPHA)
    a = 255 if inked else 150
    c = col + (a,)

    if kind == "GEYSER":
        pygame.draw.arc(layer, c, pygame.Rect(x - 8, y + 2, 16, 9), math.pi, math.tau, lw)
        for off, hgt in ((-4, 7), (0, 11), (4, 8)):
            pts = [(x + off, y + 4)]
            for i in range(1, 5):
                t = i / 4
                pts.append((x + off + math.sin(t * 3.0 + off) * 1.8, y + 4 - hgt * t))
            pygame.draw.lines(layer, c, False, pts, lw)
        for dx, dy in ((-7, -4), (7, -6), (0, -10)):
            pygame.draw.circle(layer, c, (x + dx, y + dy), 1)

    elif kind == "CLOWN":
        pygame.draw.circle(layer, c, (x, y + 3), 5, lw)
        pygame.draw.lines(layer, c, False,
                          [(x - 5, y), (x - 7, y - 6), (x - 2, y - 2)], lw)
        pygame.draw.lines(layer, c, False,
                          [(x + 5, y), (x + 7, y - 6), (x + 2, y - 2)], lw)
        pygame.draw.circle(layer, c, (x - 7, y - 6), 1)
        pygame.draw.circle(layer, c, (x + 7, y - 6), 1)
        pygame.draw.circle(layer, c, (x - 2, y + 2), 1)
        pygame.draw.circle(layer, c, (x + 2, y + 2), 1)
        pygame.draw.arc(layer, c, pygame.Rect(x - 3, y + 2, 6, 5), math.pi, math.tau, lw)

    elif kind == "STORM":
        pygame.draw.circle(layer, c, (x - 4, y - 1), 4, lw)
        pygame.draw.circle(layer, c, (x + 1, y - 3), 5, lw)
        pygame.draw.circle(layer, c, (x + 5, y), 4, lw)
        pygame.draw.lines(layer, c, False,
                          [(x + 1, y + 3), (x - 2, y + 8), (x + 1, y + 8),
                           (x - 2, y + 13)], lw)

    elif kind == "SNOW":
        for i in range(6):
            ang = i * math.pi / 3
            ex, ey = x + math.cos(ang) * 7, y + math.sin(ang) * 7
            pygame.draw.line(layer, c, (x, y), (ex, ey), lw)
            bx, by = x + math.cos(ang) * 4.5, y + math.sin(ang) * 4.5
            for s in (-0.5, 0.5):
                pygame.draw.line(layer, c, (bx, by),
                                 (bx + math.cos(ang + s) * 3,
                                  by + math.sin(ang + s) * 3), lw)
        pygame.draw.circle(layer, c, (x - 10, y + 7), 1)
        pygame.draw.circle(layer, c, (x + 10, y - 6), 1)

    dest.blit(layer, (0, 0))


def draw_ivy(dest, top, bot, events, death_phase, rows, r):
    """Gilt ivy on a sinuous stem — the canonical Book of Hours margin — with
    each run event hung off it as a drollery at its true vertical position."""
    base_x = 44
    stem = []
    y = top
    while y <= bot:
        stem.append((base_x + math.sin((y - top) * 0.028) * 11.0
                     + math.sin((y - top) * 0.071) * 3.0, y))
        y += 4
    layer = pygame.Surface(dest.get_size(), pygame.SRCALPHA)
    pygame.draw.lines(layer, (96, 66, 38, 190), False, stem, 1)
    dest.blit(layer, (0, 0))

    rng = random.Random(9)
    for i in range(6, len(stem) - 4, 9):
        sx, sy = stem[i]
        side = 1 if (i // 9) % 2 == 0 else -1
        lx, ly = sx + side * 7, sy - 3
        leaf = [(lx, ly - 4), (lx + side * 4.5, ly - 1), (lx + side * 2.5, ly + 4),
                (lx - side * 1.0, ly + 3)]
        pygame.draw.polygon(dest, GOLD, [(int(a), int(b)) for a, b in leaf])
        pygame.draw.polygon(dest, (120, 84, 40),
                            [(int(a), int(b)) for a, b in leaf], 1)
        hairline(dest, (120, 84, 40), (sx, sy), (lx, ly), alpha=170)
        if rng.random() < 0.4:  # curling tendril
            pygame.draw.arc(dest, (120, 84, 40),
                            pygame.Rect(int(sx - side * 8), int(sy + 1), 7, 7),
                            0, math.pi * 1.4, 1)

    # Place each event at the height it happened inside its phase's roundel,
    # then push overlaps apart and tie them back with a hairline.
    placed = []
    for phase, name in events:
        idx = 0
        for i, (b, _) in enumerate(PHASE_BOUNDARIES):
            if phase >= b:
                idx = i
        b0 = PHASE_BOUNDARIES[idx][0]
        b1 = PHASE_BOUNDARIES[idx + 1][0] if idx + 1 < len(PHASE_BOUNDARIES) else 1.0
        frac = (phase - b0) / (b1 - b0)
        true_y = rows[idx] - r + 2 * r * frac
        y = true_y
        if placed and y < placed[-1][1] + 30:
            y = placed[-1][1] + 30
        placed.append((name, y, true_y, phase))

    for i, (name, y, true_y, phase) in enumerate(placed):
        dx = 30 if i % 2 == 0 else 56
        inked = phase <= death_phase
        if abs(y - true_y) > 1.5:
            hairline(dest, OCHRE, (dx + 10, y), (base_x, true_y), alpha=110)
        drollery(dest, name, int(dx), int(y), inked)
        spaced_text(dest, name, 7, OCHRE, dx, y + 12, spacing=0.6,
                    align="center", alpha=235 if inked else 150)


# ── the leaf page ────────────────────────────────────────────────────────────

BLOCK_L, BLOCK_R = 76, 308
BLOCK_T, BLOCK_B = 42, 452
COL_X = 172
ROUND_R = 34
ROW0, ROW_PITCH = 78, 50
ROWS = [ROW0 + ROW_PITCH * i for i in range(7)]
RULE_STEP = 14


def render_leaf(run, seed=42, with_inset=True, shadow=(5, 7, 150)):
    panel = pygame.Surface((W, H), pygame.SRCALPHA)
    poly = leaf_polygon(seed)
    mask = leaf_mask(poly)
    panel.blit(leaf_shadow(poly, *shadow), (0, 0))
    panel.blit(vellum_body(mask, seed), (0, 0))
    edge = pygame.Surface((W, H), pygame.SRCALPHA)
    pygame.draw.polygon(edge, (176, 158, 128, 150), poly, 1)
    panel.blit(edge, (0, 0))

    # ── ruling: text lines first, so the block reads as prepared for writing
    for y in range(BLOCK_T + RULE_STEP, BLOCK_B, RULE_STEP):
        hairline(panel, OCHRE, (BLOCK_L, y), (BLOCK_R, y), alpha=24)
        for px in (17, 339):
            pygame.draw.circle(panel, OCHRE, (px, y), 1)
    for x in (BLOCK_L, BLOCK_L - 4, BLOCK_R):
        hairline(panel, OCHRE, (x, BLOCK_T), (x, BLOCK_B), alpha=60 if x != BLOCK_L else 85)
    hairline(panel, OCHRE, (BLOCK_L - 4, BLOCK_T), (BLOCK_R, BLOCK_T), alpha=85)
    hairline(panel, OCHRE, (BLOCK_L - 4, BLOCK_B), (BLOCK_R, BLOCK_B), alpha=85)

    spaced_text(panel, "FLIGHT LOG", 11, OCHRE, 192, 26, spacing=3.4, align="center")

    # ── which roundels the run actually reached
    death = run["death_phase"]
    death_idx = 0
    for i, (b, _) in enumerate(PHASE_BOUNDARIES):
        if death >= b:
            death_idx = i
    complete = run.get("complete", False)

    for i, (b0, name) in enumerate(PHASE_BOUNDARIES):
        mid = phase_ref(i)
        if complete:
            state = "painted"
        elif i < death_idx:
            state = "painted"
        elif i == death_idx:
            state = "half"
        else:
            state = "bare"
        rs = roundel(ROUND_R, mid, SILHOUETTE[name], state, seed=i * 13)
        panel.blit(rs, (COL_X - rs.get_width() // 2, ROWS[i] - rs.get_height() // 2))
        spaced_text(panel, name, 9, OCHRE, COL_X, ROWS[i] + ROUND_R + 4,
                    spacing=1.6, align="center")

    # ── death: ONE signal. A scarlet rubricated versal opening the run's line.
    if not complete:
        vy = ROWS[death_idx]
        draw_versal(panel, 212, vy, run)

    draw_ivy(panel, BLOCK_T + 6, BLOCK_B - 6, EVENT_MARKERS,
             1.0 if complete else death, ROWS, ROUND_R)

    # ── catchword bubble: the death roundel magnified ×3 in the lower margin
    if with_inset and not complete:
        draw_catchword_inset(panel, phase_ref(death_idx),
                             SILHOUETTE[PHASE_BOUNDARIES[death_idx][1]],
                             ROWS[death_idx])

    # ── folio + back rubric
    spaced_text(panel, "Fol. " + run["folio"], 8, OCHRE, 322, 600,
                spacing=1.0, align="right")
    tri = [(26, 596), (34, 601), (26, 606)]
    pygame.draw.polygon(panel, OCHRE, tri)
    spaced_text(panel, "BACK", 8, OCHRE, 40, 596, spacing=1.8)

    return panel


def draw_versal(dest, x, y, run):
    """A two-line scarlet capital opening the run's rubric — the only red ink
    anywhere on the leaf, which is what makes death land."""
    f = font(30)
    glyph = f.render("P", True, SCARLET)
    dest.blit(glyph, (x, y - glyph.get_height() // 2 - 2))
    gw, gh = glyph.get_size()
    gx, gy = x, y - gh // 2 - 2
    # Fine white-line tracery inside the bowl, plus a descending flourish.
    pygame.draw.line(dest, VELLUM, (gx + 5, gy + 9), (gx + 5, gy + 19), 1)
    pygame.draw.arc(dest, SCARLET,
                    pygame.Rect(gx - 3, gy + gh - 12, 12, 16),
                    math.pi * 0.9, math.pi * 1.75, 1)
    pygame.draw.arc(dest, SCARLET,
                    pygame.Rect(gx - 6, gy + gh - 18, 14, 22),
                    math.pi * 1.0, math.pi * 1.6, 1)

    tx = x + gw + 4
    spaced_text(dest, "PILLARS " + run["pillars"], 7, OCHRE, tx, y - 11, spacing=0.9)
    spaced_text(dest, "TIME " + run["clock"], 7, OCHRE, tx, y - 1, spacing=0.9)
    spaced_text(dest, "DAY " + ("ij" if run["day"] == 2 else "i"), 7, OCHRE,
                tx, y + 9, spacing=0.9, alpha=190)


def draw_catchword_inset(dest, phase_mid, kind, from_y):
    """Manuscripts hang a catchword in the lower margin; here it carries the
    death roundel at ×3 so the moment is readable without a second red mark."""
    cx, cy, r = COL_X, 522, ROUND_R * 3
    dotted_line(dest, OCHRE, (COL_X - 24, from_y + 12), (112, from_y + 22),
                dot=1, gap=4, alpha=130)
    dotted_line(dest, OCHRE, (112, from_y + 22), (112, cy), dot=1, gap=4, alpha=130)

    big = roundel(r, phase_mid, kind, "half", seed=3)
    dest.blit(big, (cx - big.get_width() // 2, cy - big.get_height() // 2))
    ring = pygame.Surface(dest.get_size(), pygame.SRCALPHA)
    pygame.draw.circle(ring, OCHRE + (120,), (cx, cy), r + 5, 1)
    pygame.draw.circle(ring, OCHRE + (70,), (cx, cy), r + 8, 1)
    for i in range(24):  # beaded cartouche
        a = i * math.tau / 24
        pygame.draw.circle(ring, OCHRE + (110,),
                           (int(cx + math.cos(a) * (r + 6.5)),
                            int(cy + math.sin(a) * (r + 6.5))), 1)
    dest.blit(ring, (0, 0))
    spaced_text(dest, "×iij", 8, OCHRE, cx + r + 14, cy - 5, spacing=1.0)


def render_day_two():
    """The next day is a fresh leaf laid over the last, which survives only as
    a sliver of edge — the run's history stacking up as a physical quire."""
    panel = pygame.Surface((W, H), pygame.SRCALPHA)
    under = render_leaf(dict(RUN_B, complete=True, folio="i", day=1),
                        seed=77, with_inset=False)
    panel.blit(under, (6, 6))
    # A leaf resting on its neighbour throws a much shorter shadow than one
    # resting on the table, and a heavy one would swallow the 6 px strip.
    top = render_leaf(RUN_B, seed=42, shadow=(2, 2, 80))
    panel.blit(top, (0, 0))
    return panel


# ── review sheet ─────────────────────────────────────────────────────────────

SHEET_BG = (26, 24, 26)
LABEL = (226, 220, 210)
DIM = (150, 144, 138)


def vocab_strip(width, height):
    """Reference view: the three ink figures a roundel can carry, one each."""
    s = pygame.Surface((width, height), pygame.SRCALPHA)
    s.fill((44, 40, 38))
    trio = [("DAY", phase_ref(0), "macaw"), ("DUSK", phase_ref(3), "pillar"),
            ("NIGHT", phase_ref(4), "moon")]
    for i, (name, mid, kind) in enumerate(trio):
        r = 26
        rs = roundel(r, mid, kind, "painted", seed=i * 5)
        rs = pygame.transform.smoothscale(rs, (rs.get_width() * 2, rs.get_height() * 2))
        x = int(width * (i + 0.5) / 3)
        s.blit(rs, (x - rs.get_width() // 2, 16))
        spaced_text(s, name, 11, (214, 172, 120), x, 16 + rs.get_height() + 6,
                    spacing=1.8, align="center")
    return s


def build_sheet():
    panel_a = render_leaf(RUN_A)
    panel_b = render_day_two()

    det_w, det_h = 380, 148
    gap, marg = 22, 22
    head = 62
    cap = 40
    sheet_w = marg * 3 + W * 2 + gap + det_w
    sheet_h = head + H + cap
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill(SHEET_BG)

    f_title = font(19)
    f_sub = font(12)
    sheet.blit(f_title.render("SKYBIT  ·  FLIGHT LOG  ·  CONCEPT: VELLUM HOURS  ·  ROUND 1",
                              True, LABEL), (marg, 16))
    sheet.blit(f_sub.render(
        "One leaf of a Book of Hours. 7 phase roundels; only flown time is painted. "
        "Death = one scarlet rubricated versal. All underdrawing is sinopia ochre.",
        True, DIM), (marg, 40))

    for i, (pan, title, sub) in enumerate((
        (panel_a, "DAY i — RUN_A",
         "died 0:47 · 25 pillars · phase 0.184 (DAY) · 6 roundels still unflown"),
        (panel_b, "DAY ij — second leaf laid over the first",
         "day i survives as a 6 px edge strip · folio ij · death in DUSK"),
    )):
        x = marg + i * (W + gap)
        pygame.draw.rect(sheet, (56, 52, 50), (x - 1, head - 1, W + 2, H + 2), 1)
        base = pygame.Surface((W, H))
        base.fill(TABLE)
        # Faint table grain so the leaf reads as lying on walnut, not on void.
        for gy in range(0, H, 3):
            a = 8 + int(6 * math.sin(gy * 0.21))
            pygame.draw.line(base, (20 + a, 14 + a // 2, 10 + a // 3), (0, gy), (W, gy))
        base.blit(pan, (0, 0))
        sheet.blit(base, (x, head))
        sheet.blit(font(13).render(title, True, LABEL), (x, head + H + 8))
        sheet.blit(font(10).render(sub, True, DIM), (x, head + H + 24))

    dx = marg * 2 + W * 2 + gap
    details = [
        ((140, 46, 190, 74), panel_a,
         "DEATH ROUNDEL + RUBRICATED VERSAL (2x)",
         "half painted / half sinopia; scarlet appears once"),
        ((60, 268, 190, 74), panel_a,
         "UNFLOWN ROUNDEL (2x)",
         "burnished vellum 242, compass prick + guide only"),
        ((8, 42, 190, 74), panel_a,
         "MARGINAL DROLLERY ON IVY (2x)",
         "flown events inked; events still ahead stay sinopia"),
        (None, None,
         "ROUNDEL VOCABULARY (reference)",
         "macaw / pillar / moon — exactly one ink figure each"),
    ]
    for i, (rect, src, title, sub) in enumerate(details):
        y = head + i * (det_h + 16)
        if rect is None:
            crop = vocab_strip(det_w, det_h - 26)
        else:
            sub_s = src.subsurface(pygame.Rect(*rect)).copy()
            flat = pygame.Surface((rect[2], rect[3]))
            flat.fill(TABLE)
            flat.blit(sub_s, (0, 0))
            crop = pygame.transform.smoothscale(flat, (rect[2] * 2, rect[3] * 2))
        pygame.draw.rect(sheet, (56, 52, 50),
                         (dx - 1, y - 1, crop.get_width() + 2, crop.get_height() + 2), 1)
        sheet.blit(crop, (dx, y))
        sheet.blit(font(12).render(title, True, LABEL), (dx, y + crop.get_height() + 4))
        sheet.blit(font(10).render(sub, True, DIM), (dx, y + crop.get_height() + 19))

    sheet.blit(font(10).render(
        "scarlet audit: 1 mark (the versal). gold: gilded roundel frames + ivy leaves. "
        "no red lead, no scorch notch.", True, (196, 150, 120)),
        (marg, sheet_h - 22))
    return sheet


if __name__ == "__main__":
    out = os.path.join(OUT_DIR, "round_2.png")
    sheet = build_sheet()
    pygame.image.save(sheet, out)
    print("saved", out, sheet.get_size())
    for p in ((30, 300), (200, 400), (700, 200), (1000, 120)):
        print("  px", p, sheet.get_at(p)[:3])
