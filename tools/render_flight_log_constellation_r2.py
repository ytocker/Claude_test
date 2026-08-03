#!/usr/bin/env python3
"""
constellation  ·  flight-log arc v2  ·  round 2

Round-2 art-director changes applied on top of round-1:

  1. Unflown connecting lines visible at GOLD@35 (dotted/dashed joins)
  2. Event node rings r=5, 87% of event hue, '?' centered INSIDE ring (7pt)
  3. Duplicate death-percentage labels killed — only the GOLD label near the
     death node survives; headline percentage block removed; chip sub simplified
  4. Starfield 350 stars, power-law size distribution (1/2/3 px), color
     temperature variation (blue-white → neutral white → warm gold), scattered
     across the full canvas including behind the path
  5. Overall visual weight:
       • Flown join GOLD@200 (was @140)
       • Death star 3-layer soft_glow with boosted peaks + 4-arm diffraction
       • Phase node labels in dim-gold (GOLD@120) instead of cool blue-grey
"""
import os
import math
import random

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import sys
sys.path.insert(0, "/home/user/skybit")

import pygame
pygame.init()
pygame.display.set_mode((1, 1))

from game.draw import lerp_color, lerp_color_multi

W, H = 360, 640
SS = 3
ROOT = "/home/user/skybit"
FONT_PATH = "/home/user/skybit/game/assets/LiberationSans-Bold.ttf"
INK = (6, 8, 14)
GOLD = (255, 206, 92)
CREAM = (246, 240, 230)
COOL = (150, 168, 196)
SCRIM = (26, 22, 34)
GEYSER_C = (146, 232, 255)
CLOWN_C = (255, 118, 196)
RAIN_C = (150, 190, 255)
SNOW_C = (222, 244, 255)

# Round-2 derived constants
# "GOLD@120" for phase labels — GOLD at 120/255 brightness on the dark background
GOLD_DIM = tuple(int(c * 120 // 255) for c in GOLD)  # ≈ (120, 97, 43)

# Color-temperature anchors for the starfield
STAR_BLUE  = (220, 228, 255)   # blue-white cool stars
STAR_WHITE = (255, 255, 255)   # neutral
STAR_WARM  = (255, 248, 220)   # warm gold-tinted

_fonts: dict = {}


# ── helpers ──────────────────────────────────────────────────────────────────

def font(size):
    if size not in _fonts:
        _fonts[size] = pygame.font.Font(FONT_PATH, size)
    return _fonts[size]


def text(surf, s, size, center=None, midleft=None, midright=None,
         color=CREAM, shadow=(0, 0, 0, 150), track=0):
    f = font(size)
    if track:
        glyphs = [f.render(ch, True, color) for ch in s]
        tw = sum(g.get_width() for g in glyphs) + track * (len(s) - 1)
        th = f.get_height()
        img = pygame.Surface((max(1, tw), th), pygame.SRCALPHA)
        x = 0
        for ch, g in zip(s, glyphs):
            img.blit(g, (x, 0))
            x += g.get_width() + track
    else:
        img = f.render(s, True, color)
    rect = img.get_rect()
    if center:
        rect.center = center
    elif midleft:
        rect.midleft = midleft
    elif midright:
        rect.midright = midright
    if shadow:
        sh = img.copy()
        sh.fill((*shadow[:3], 255), special_flags=pygame.BLEND_RGBA_MULT)
        sh.set_alpha(shadow[3])
        surf.blit(sh, (rect.x + 1, rect.y + 1))
    surf.blit(img, rect)
    return rect


def chip(surf, rect, radius=6, fill=(18, 15, 24), alpha=234,
         border=CREAM, border_a=54):
    s = pygame.Surface(rect.size, pygame.SRCALPHA)
    pygame.draw.rect(s, (*fill, alpha), s.get_rect(), border_radius=radius)
    if border_a:
        pygame.draw.rect(s, (*border, border_a), s.get_rect(), width=1,
                         border_radius=radius)
    surf.blit(s, rect.topleft)


def soft_glow(radius, color, peak=110, falloff=2.0):
    """Additive glow with the falloff baked into RGB (premultiplied).

    BLEND_ADD ignores source alpha, so we bake the alpha ramp into RGB and
    blit all pixels at alpha=255.
    """
    size = radius * 2 + 2
    s = pygame.Surface((size, size), pygame.SRCALPHA)
    c = radius + 1
    for r in range(radius, 0, -1):
        f = (1 - (r / radius) ** falloff) * (peak / 255.0)
        s_col = (int(color[0] * f), int(color[1] * f), int(color[2] * f), 255)
        pygame.draw.circle(s, s_col, (c, c), r)
    return s


def alpha_line(surf, rgba, p0, p1, width=1):
    """Route alpha-capable line through an SRCALPHA scratch layer."""
    lay = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    pygame.draw.line(lay, rgba, p0, p1, width)
    surf.blit(lay, (0, 0))


# ── run data ──────────────────────────────────────────────────────────────────

DAY_N = 1
DEATH_PHASE = 0.184
DEATH_PILLAR = 25
TIME_ALIVE = 47
PHASE_LABEL = "DAY"

WAYPOINTS = [
    (0.000, "DAY",         "boundary", GOLD),
    (0.184, "DAY 18.4%",   "death",    GOLD),
    (0.270, "GEYSER",      "event",    GEYSER_C),
    (0.320, "SUNSET",      "boundary", GOLD),
    (0.403, "CLOWN",       "event",    CLOWN_C),
    (0.430, "RAIN",        "event",    RAIN_C),
    (0.480, "DUSK",        "boundary", GOLD),
    (0.620, "NIGHT",       "boundary", GOLD),
    (0.780, "PREDAWN",     "boundary", GOLD),
    (0.820, "SNOW",        "event",    SNOW_C),
    (0.900, "SUNRISE",     "boundary", GOLD),
]
DEATH_I = 1


# ── the walk ──────────────────────────────────────────────────────────────────

ZX0, ZX1 = 40, 320
ZY0, ZY1 = 110, 560
MIN_SEP = 28


def build_route():
    rng = random.Random(DAY_N)
    n = len(WAYPOINTS)
    pts = [(160.0, 534.0)]
    sign = 1
    run = 0
    run_len = rng.randint(1, 2)

    for i in range(1, n):
        if run >= run_len:
            sign = -sign
            run = 0
            run_len = rng.randint(1, 2)
        px, py = pts[-1]
        if ((ZY1 - py) if sign > 0 else (py - ZY0)) < 96:
            sign = -sign
            run = 0
            run_len = rng.randint(1, 2)
        want_x = ZX0 + (ZX1 - ZX0) * (i / (n - 1))
        best = None
        for attempt in range(900):
            slack = attempt / 900.0
            room = (ZY1 - py) if sign > 0 else (py - ZY0)
            dyv = sign * rng.uniform(0.50, 0.98 - 0.30 * slack) * min(room, 300.0)
            dxv = (want_x - px) * rng.uniform(0.22, 0.78) + rng.uniform(-52, 52)
            x, y = px + dxv, py + dyv
            if not (ZX0 <= x <= ZX1 and ZY0 <= y <= ZY1):
                continue
            if abs(dyv) < 34 - 16 * slack:
                continue
            if any(math.hypot(x - qx, y - qy) < MIN_SEP for qx, qy in pts):
                continue
            best = (x, y)
            break
        if best is None:
            best = (min(ZX1, max(ZX0, px + 40)),
                    min(ZY1, max(ZY0, py + sign * 60)))
        pts.append(best)
        run += 1
    return pts


ROUTE = build_route()


# ── starfield  (round 2: richer) ──────────────────────────────────────────────

def build_starfield():
    """350 field stars scattered across the full canvas (including behind the
    path). Power-law size distribution: ~75 % r=1, ~20 % r=2, ~5 % r=3 bright.
    Color temperature spans blue-white → neutral white → warm gold."""
    rng = random.Random(42)
    stars = []
    guard = 0
    # Scatter throughout the whole canvas — include behind the path (no big
    # exclusion zone).  A tiny 5px guard stops a star from sitting dead-centre
    # on a node disc and breaking the magnitude hierarchy.
    while len(stars) < 350 and guard < 80000:
        guard += 1
        x = rng.uniform(3, W - 3)
        y = rng.uniform(3, H - 3)
        if any(math.hypot(x - qx, y - qy) < 5 for qx, qy in ROUTE):
            continue

        # Power-law size: most stars 1px, some 2px, a few 3px
        u = rng.random()
        if u < 0.75:
            r = 1
        elif u < 0.95:
            r = 2
        else:
            r = 3

        # Color temperature variation
        t = rng.random()
        if t < 0.33:
            col = STAR_BLUE
        elif t < 0.66:
            col = STAR_WHITE
        else:
            col = STAR_WARM

        # Larger stars are a touch brighter
        base_a = 30 + r * 18
        a = rng.randint(base_a, min(255, base_a + 30))

        stars.append((x, y, r, col, a))
    return stars


STARS = build_starfield()


# ── supersampled layer ────────────────────────────────────────────────────────

def ss(v):
    return int(round(v * SS))


def dotted(layer, p0, p1, rgba, period=7.0, trim=(9.0, 9.0)):
    """Dotted join: r=1 output-pixel dots with gaps, trimmed at node discs."""
    dx, dy = p1[0] - p0[0], p1[1] - p0[1]
    L = math.hypot(dx, dy)
    if L < 1:
        return
    a, b = trim[0] / L, 1.0 - trim[1] / L
    if b <= a:
        return
    n = max(1, int((L * (b - a)) / period))
    for i in range(n + 1):
        t = a + (b - a) * (i / n)
        pygame.draw.circle(layer, rgba,
                           (ss(p0[0] + dx * t), ss(p0[1] + dy * t)), SS)


def draw_layer():
    layer = pygame.Surface((W * SS, H * SS), pygame.SRCALPHA)

    # ── background: field stars (power-law size + color temp) ──
    for x, y, r, col, a in STARS:
        pygame.draw.circle(layer, (*col, a), (ss(x), ss(y)), SS * r)

    # ── joins ──
    # Flown leg (origin → death star): bright, solid-ish dotted at GOLD@200
    dotted(layer, ROUTE[0], ROUTE[DEATH_I], (*GOLD, 200), period=7.0,
           trim=(7.0, 13.0))

    # Unflown legs (death star → end): visible but ghostly at GOLD@35
    # Criterion 1: draw all segments ahead of the death node so the full
    # asterism silhouette is legible even though these legs are uncharted.
    for i in range(DEATH_I, len(ROUTE) - 1):
        dotted(layer, ROUTE[i], ROUTE[i + 1], (*GOLD, 35), period=9.0,
               trim=(11.0, 11.0))

    # ── magnitude 3: unreached events ──
    # r=5 hollow ring at 87 % of event hue; ring width = 1 output px (= SS in
    # the supersampled layer).
    for (ph, lbl, kind, col), (x, y) in zip(WAYPOINTS, ROUTE):
        if kind != "event":
            continue
        dim_col = tuple(int(c * 87 // 100) for c in col)
        pygame.draw.circle(layer, (*dim_col, 153),
                           (ss(x), ss(y)), ss(5), SS)

    # ── magnitude 2: phase boundaries ──
    for (ph, lbl, kind, col), (x, y) in zip(WAYPOINTS, ROUTE):
        if kind != "boundary":
            continue
        pygame.draw.circle(layer, (*GOLD, 180), (ss(x), ss(y)), ss(2.5))

    return pygame.transform.smoothscale(layer, (W, H))


# ── labels ────────────────────────────────────────────────────────────────────

def place_labels(surf, taken):
    """Chart-style leaders: try eight compass offsets around each node."""
    blocked = [pygame.Rect(0, 0, W, 128),
               pygame.Rect(110, 572, 140, 52)]

    offsets = [(11, 0), (-11, 0), (0, -11), (0, 11),
               (10, -9), (-10, -9), (10, 9), (-10, 9)]

    for (ph, lbl, kind, col), (x, y) in zip(WAYPOINTS, ROUTE):
        if kind == "death":
            continue
        size = 8 if kind == "boundary" else 7
        # Round-2: boundary labels in dim GOLD (not washed-out COOL)
        if kind == "boundary":
            color = GOLD_DIM
        else:
            color = tuple(min(255, int(c * 0.72)) for c in col)
        f = font(size)
        gw = f.size(lbl)[0] + 1 * (len(lbl) - 1)
        gh = f.get_height()
        chosen = None
        for ox, oy in offsets:
            r = pygame.Rect(0, 0, gw + 4, gh)
            if ox > 0:
                r.midleft = (x + ox, y + oy)
            elif ox < 0:
                r.midright = (x + ox, y + oy)
            else:
                r.center = (x, y + oy * 1.5)
            if r.left < 3 or r.right > W - 3 or r.top < 3 or r.bottom > H - 3:
                continue
            if any(r.colliderect(b) for b in blocked + taken):
                continue
            if any(r.collidepoint(qx, qy) or
                   r.inflate(10, 10).collidepoint(qx, qy) for qx, qy in ROUTE):
                continue
            chosen = r
            break
        if chosen is None:
            chosen = pygame.Rect(0, 0, gw + 4, gh)
            chosen.midleft = (x + 11, y - 11)
        chosen.left = max(3, min(W - 3 - chosen.w, chosen.left))
        chosen.top = max(3, min(H - 3 - chosen.h, chosen.top))
        taken.append(chosen)
        text(surf, lbl, size, midleft=(chosen.x + 2, chosen.centery),
             color=color, shadow=None, track=1)


# ── screen ────────────────────────────────────────────────────────────────────

def render_screen():
    surf = pygame.Surface((W, H))
    surf.fill(INK)
    surf.blit(draw_layer(), (0, 0))

    dx, dy = ROUTE[DEATH_I]
    dxi, dyi = int(round(dx)), int(round(dy))

    taken = []

    # ── magnitude 3: "?" INSIDE each event ring ──
    # Round-2: glyph centered exactly on the node (inside the r=5 ring).
    # Use 7pt so the glyph comfortably fits in the 10px diameter disc.
    for (ph, lbl, kind, col), (x, y) in zip(WAYPOINTS, ROUTE):
        if kind != "event":
            continue
        xi, yi = int(round(x)), int(round(y))
        r = text(surf, "?", 7, center=(xi, yi),
                 color=tuple(c // 3 for c in col), shadow=None)
        taken.append(r.inflate(4, 2))

    # ── magnitude 0: the death star ──
    # 3-layer soft glow with boosted peaks for extra presence
    for rad, peak in ((26, 100), (16, 68), (9, 40)):
        g = soft_glow(rad, GOLD, peak=peak, falloff=2.0)
        surf.blit(g, (dxi - rad - 1, dyi - rad - 1),
                  special_flags=pygame.BLEND_ADD)
    # 4-arm diffraction cross (the one mark no other node gets)
    alpha_line(surf, (*GOLD, 130), (dxi - 14, dyi), (dxi + 14, dyi), 1)
    alpha_line(surf, (*GOLD, 130), (dxi, dyi - 14), (dxi, dyi + 14), 1)
    pygame.draw.circle(surf, GOLD, (dxi, dyi), 5)
    pygame.draw.circle(surf, (255, 240, 190), (dxi - 1, dyi - 1), 2)

    # ── death callout chip ──
    # Round-2: sub line drops the "18.4%" — that percentage appears only in
    # the single GOLD label below; this chip just shows pillar + time.
    f10, f8 = font(10), font(8)
    sub = f"PILLAR {DEATH_PILLAR}  ·  0:{TIME_ALIVE:02d}"
    cw = max(f10.size("ENDED HERE")[0], f8.size(sub)[0]) + 20
    cands = [(dxi + 22, dyi + 30), (dxi + 22, dyi - 30),
             (dxi - 22, dyi + 30), (dxi - 22, dyi - 30),
             (dxi + 26, dyi), (dxi - 26, dyi)]
    best_cr, best_cost = None, None
    for cx, cy in cands:
        r = pygame.Rect(0, 0, cw, 34)
        if cx > dxi:
            r.midleft = (cx, cy)
        else:
            r.midright = (cx, cy)
        r.left = max(6, min(W - 6 - r.w, r.left))
        r.top = max(132, min(566 - r.h, r.top))
        pad = r.inflate(12, 12)
        cost = sum(1 for j, (qx, qy) in enumerate(ROUTE)
                   if j != DEATH_I and pad.collidepoint(qx, qy))
        if best_cost is None or cost < best_cost:
            best_cr, best_cost = r, cost
        if cost == 0:
            break
    cr = best_cr
    alpha_line(surf, (*GOLD, 90), (dxi, dyi), (cr.centerx, cr.centery), 1)
    chip(surf, cr, radius=7, alpha=238, border_a=66)
    text(surf, "ENDED HERE", 10, midleft=(cr.x + 10, cr.y + 11), color=GOLD,
         shadow=None)
    text(surf, sub, 8, midleft=(cr.x + 10, cr.y + 24), color=CREAM,
         shadow=None)
    taken.append(cr.inflate(6, 6))

    # ── primary death label (the SOLE "18.4%" on screen) ──
    # Round-2: this is the one surviving instance of the death percentage.
    f8 = font(8)
    dl = pygame.Rect(0, 0, f8.size("DAY 18.4%")[0] + 8, 12)
    if dxi < W // 2:
        dl.midleft = (dxi + 13, dyi - 13)
    else:
        dl.midright = (dxi - 13, dyi - 13)
    dl.left = max(4, min(W - 4 - dl.w, dl.left))
    text(surf, "DAY 18.4%", 8, midleft=(dl.x + 2, dl.centery), color=GOLD,
         shadow=None, track=1)
    taken.append(dl)

    place_labels(surf, taken)

    # ── banner ──
    pygame.draw.rect(surf, SCRIM, (0, 0, W, 74))
    fade = pygame.Surface((W, 10), pygame.SRCALPHA)
    for i in range(10):
        fade.fill((*SCRIM, int(238 * (1 - i / 10) ** 1.4)),
                  pygame.Rect(0, i, W, 1))
    surf.blit(fade, (0, 74))
    alpha_line(surf, (255, 206, 92, 150), (0, 74), (W - 1, 74), 1)

    text(surf, f"FLIGHT LOG  ·  DAY {DAY_N}", 21, center=(W // 2, 28),
         color=GOLD, track=3, shadow=None)
    text(surf, f"PILLAR {DEATH_PILLAR}   ·   0:{TIME_ALIVE:02d}", 12,
         center=(W // 2, 55), color=CREAM, shadow=None)

    # ── headline ──
    # Round-2: percentage removed from headline — the GOLD label near the
    # death star is the single authoritative "18.4%" on screen.
    f_sml = font(9)
    text(surf, "CONSTELLATION MAP", 9, center=(W // 2, 104),
         color=COOL, shadow=None, track=2)

    # ── BACK pill ──
    pr = pygame.Rect(0, 0, 122, 36)
    pr.center = (180, 597)
    sh = pygame.Surface((pr.w + 8, pr.h + 8), pygame.SRCALPHA)
    pygame.draw.rect(sh, (0, 0, 0, 100), sh.get_rect(), border_radius=21)
    surf.blit(sh, (pr.x - 4, pr.y - 1))
    grad = pygame.Surface(pr.size, pygame.SRCALPHA)
    for y in range(pr.h):
        grad.fill(
            lerp_color((255, 228, 172), (226, 168, 96), y / (pr.h - 1)) + (255,),
            pygame.Rect(0, y, pr.w, 1))
    mask = pygame.Surface(pr.size, pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255), mask.get_rect(),
                     border_radius=18)
    grad.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(grad, pr.topleft)
    pygame.draw.rect(surf, (110, 68, 38), pr, width=1, border_radius=18)
    text(surf, "BACK", 13, center=(pr.centerx, pr.centery),
         color=(66, 40, 20), shadow=None, track=2)

    return surf


def main():
    surf = render_screen()
    out = "/home/user/skybit/docs/flight_log_arc_v2/constellation/round_2.png"
    os.makedirs(os.path.dirname(out), exist_ok=True)
    pygame.image.save(surf, out)
    loaded = pygame.image.load(out)
    print(f"saved {out}  {loaded.get_size()}")

    dys = [ROUTE[i + 1][1] - ROUTE[i][1] for i in range(len(ROUTE) - 1)]
    print("dy signs:", "".join("+" if d > 0 else "-" for d in dys))
    worst = min(math.hypot(ROUTE[i][0] - ROUTE[j][0], ROUTE[i][1] - ROUTE[j][1])
                for i in range(len(ROUTE)) for j in range(i + 1, len(ROUTE)))
    print(f"min node separation: {worst:.1f}px   stars: {len(STARS)}")
    print(f"unflown joins drawn: {len(ROUTE) - 1 - DEATH_I} segments")
    print(f"star size breakdown: "
          f"r1={sum(1 for *_, r, c, a in STARS if r == 1)}  "
          f"r2={sum(1 for *_, r, c, a in STARS if r == 2)}  "
          f"r3={sum(1 for *_, r, c, a in STARS if r == 3)}")


if __name__ == "__main__":
    main()
