#!/usr/bin/env python3
"""
constellation  ·  flight-log arc v2  ·  round 1

CONSTELLATION MAP. The day is not an arc — it is an asterism.

The route wanders freely in 2D through the live zone as a deterministic walk
(random.Random(1)) with an enforced sign-change in dy every 1-2 steps, so the
node chain can never settle into an arc, dome or rainbow silhouette. What the
player flew is a dotted gold join; what lies ahead is uncharted, so those nodes
are drawn but never connected.

Strict magnitude hierarchy is what makes it readable at a glance:
  magnitude 0  death star        r=5 gold + 3-layer glow + diffraction cross
  magnitude 2  phase boundaries  r=2.5 GOLD@180 + tiny cool label
  magnitude 3  events (unreached) r=2 hollow ring + "?" at 1/3 brightness
  background   ~150 field stars  r=1 GOLD@25-50, seeded separately

Geometry, dotted joins and node discs are drawn on a 3x supersampled layer and
downscaled once; glow, diffraction and type land at 1x so they stay crisp.
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

_fonts: dict = {}


# ── helpers (copied from render_flight_log_arc_count_r7.py) ───────────────────

def font(size):
    if size not in _fonts:
        _fonts[size] = pygame.font.Font(FONT_PATH, size)
    return _fonts[size]


def text(surf, s, size, center=None, midleft=None, midright=None,
         color=CREAM, shadow=(0, 0, 0, 150), track=0):
    f = font(size)
    if track:
        # Manual letter-spacing keeps headers reading as signage; pygame has no
        # tracking control.
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
    """Additive glow with the falloff baked into RGB.

    BLEND_ADD ignores the source alpha channel, so an alpha-ramped glow blits
    as a flat hard-edged disc. Premultiplying keeps the ramp.
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
    """`surf` is an opaque Surface, so pygame.draw would ignore the alpha and
    stamp the colour at full strength. Route through a scratch layer."""
    lay = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    pygame.draw.line(lay, rgba, p0, p1, width)
    surf.blit(lay, (0, 0))


# ── run data ──────────────────────────────────────────────────────────────────

DAY_N = 1
DEATH_PHASE = 0.184
DEATH_PILLAR = 25
TIME_ALIVE = 47
PHASE_LABEL = "DAY"

# 7 phase boundaries + 4 events = 11 waypoints, in flight order.
# The death star sits on the 2nd waypoint (the GOLDEN HOUR boundary, nudged to
# the exact death phase 0.184). Every event is ahead of it, so every event is
# unreached — the geyser rides its zone midpoint rather than its 0.167 entry so
# it cannot read as something the player already saw.
#   (phase, label, kind, colour)
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
# Live zone: clear of the 74px banner + headline above, and of the BACK pill
# below. Nodes keep 28px of air between them so no two ever read as one star.

ZX0, ZX1 = 40, 320
ZY0, ZY1 = 110, 560
MIN_SEP = 28


def build_route():
    """Deterministic 2D wander. dy is forced to flip sign every 1-2 steps, which
    is the single rule that stops eleven left-to-right nodes from collapsing
    into the arc this design is trying to get away from.

    Vertical amplitude is drawn as a fraction of the room remaining in the sign
    direction, so the zigzag always spans the live zone instead of settling into
    a shallow band; horizontal drift is only loosely pulled toward an even
    left-to-right spread, which leaves room for genuine backtracking."""
    rng = random.Random(DAY_N)
    n = len(WAYPOINTS)
    pts = [(160.0, 534.0)]
    sign = 1                        # immediately flipped by the room guard
    run = 0
    run_len = rng.randint(1, 2)

    for i in range(1, n):
        if run >= run_len:
            sign = -sign
            run = 0
            run_len = rng.randint(1, 2)
        px, py = pts[-1]
        # Flipping early is always legal (the rule caps a same-sign run at 2, it
        # does not mandate one). Without this the walk can pin itself against an
        # edge with no legal step left and fall back onto a neighbour.
        if ((ZY1 - py) if sign > 0 else (py - ZY0)) < 96:
            sign = -sign
            run = 0
            run_len = rng.randint(1, 2)
        want_x = ZX0 + (ZX1 - ZX0) * (i / (n - 1))
        best = None
        # Relax the step envelope on repeated failure so the walk can always
        # escape a corner without ever abandoning the sign rule.
        for attempt in range(900):
            slack = attempt / 900.0
            room = (ZY1 - py) if sign > 0 else (py - ZY0)
            dyv = sign * rng.uniform(0.50, 0.98 - 0.30 * slack) * min(room, 300.0)
            dxv = (want_x - px) * rng.uniform(0.22, 0.78) + rng.uniform(-52, 52)
            x, y = px + dxv, py + dyv
            if not (ZX0 <= x <= ZX1 and ZY0 <= y <= ZY1):
                continue
            if abs(dyv) < 34 - 16 * slack:          # keep the zigzag legible
                continue
            if any(math.hypot(x - qx, y - qy) < MIN_SEP for qx, qy in pts):
                continue
            best = (x, y)
            break
        if best is None:                            # never hit in practice
            best = (min(ZX1, max(ZX0, px + 40)),
                    min(ZY1, max(ZY0, py + sign * 60)))
        pts.append(best)
        run += 1
    return pts


ROUTE = build_route()


# ── starfield ─────────────────────────────────────────────────────────────────

def build_starfield():
    """~150 field stars, strictly outside a 28px exclusion disc around every
    route node — a background star touching a waypoint would break the whole
    magnitude hierarchy."""
    rng = random.Random(42)
    stars = []
    guard = 0
    while len(stars) < 150 and guard < 40000:
        guard += 1
        x = rng.uniform(3, W - 3)
        y = rng.uniform(3, H - 3)
        if any(math.hypot(x - qx, y - qy) < 28 for qx, qy in ROUTE):
            continue
        stars.append((x, y, rng.randint(20, 60)))
    return stars


STARS = build_starfield()


# ── supersampled layer ────────────────────────────────────────────────────────

def s(v):
    return int(round(v * SS))


def dotted(layer, p0, p1, rgba, period=7.0, trim=(9.0, 9.0)):
    """Dotted join: r=1 output-pixel dots with gaps. Trimmed at both ends so the
    dots never crowd the node discs they connect."""
    dx, dy = p1[0] - p0[0], p1[1] - p0[1]
    L = math.hypot(dx, dy)
    a, b = trim[0] / L, 1.0 - trim[1] / L
    if b <= a:
        return
    n = max(1, int((L * (b - a)) / period))
    for i in range(n + 1):
        t = a + (b - a) * (i / n)
        pygame.draw.circle(layer, rgba,
                           (s(p0[0] + dx * t), s(p0[1] + dy * t)), SS)


def draw_layer():
    layer = pygame.Surface((W * SS, H * SS), pygame.SRCALPHA)

    # magnitude "background" — field stars
    for x, y, a in STARS:
        pygame.draw.circle(layer, (*GOLD, a), (s(x), s(y)), SS)

    # joins — only the flown leg is charted. Everything ahead of the death star
    # is deliberately unconnected: the route past the end is not known.
    dotted(layer, ROUTE[0], ROUTE[DEATH_I], (*GOLD, 140), period=7.0,
           trim=(7.0, 13.0))

    # magnitude 3 — unreached events: hollow, thin, dimmed to 60%
    for (ph, lbl, kind, col), (x, y) in zip(WAYPOINTS, ROUTE):
        if kind != "event":
            continue
        pygame.draw.circle(layer, (*col, 153), (s(x), s(y)), s(2), SS)

    # magnitude 2 — phase boundaries
    for (ph, lbl, kind, col), (x, y) in zip(WAYPOINTS, ROUTE):
        if kind != "boundary":
            continue
        pygame.draw.circle(layer, (*GOLD, 180), (s(x), s(y)), s(2.5))

    return pygame.transform.smoothscale(layer, (W, H))


# ── labels ────────────────────────────────────────────────────────────────────

def place_labels(surf, taken):
    """Chart-style leaders: try the eight compass offsets around each node and
    take the first that clears every node, every label already set, the banner
    and the BACK pill."""
    blocked = [pygame.Rect(0, 0, W, 128),            # banner + headline
               pygame.Rect(110, 572, 140, 52)]       # BACK pill

    offsets = [(11, 0), (-11, 0), (0, -11), (0, 11),
               (10, -9), (-10, -9), (10, 9), (-10, 9)]

    for (ph, lbl, kind, col), (x, y) in zip(WAYPOINTS, ROUTE):
        if kind == "death":
            continue
        size = 8 if kind == "boundary" else 7
        color = COOL if kind == "boundary" else tuple(
            min(255, int(c * 0.72)) for c in col)
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
        # Never let a label run off the plate, fallback included.
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

    # "?" on each unreached event, at 1/3 of the event's brightness. It rides
    # just off the centroid rather than dead on it: a 9pt glyph is wider than
    # the r=2 ring it marks, and stacked they smear into one dim blob instead of
    # reading as ring-plus-question.
    for (ph, lbl, kind, col), (x, y) in zip(WAYPOINTS, ROUTE):
        if kind != "event":
            continue
        qy = int(round(y)) - 10
        if qy < 136:
            qy = int(round(y)) + 10
        r = text(surf, "?", 9, center=(int(round(x)), qy),
                 color=tuple(c // 3 for c in col), shadow=None)
        taken.append(r.inflate(4, 2))

    # ── magnitude 0: the death star, brightest object on screen ──
    for rad, peak in ((22, 90), (14, 60), (8, 35)):
        g = soft_glow(rad, GOLD, peak=peak, falloff=2.0)
        surf.blit(g, (dxi - rad - 1, dyi - rad - 1), special_flags=pygame.BLEND_ADD)
    # 4-point diffraction cross — the one thing no other node gets
    alpha_line(surf, (*GOLD, 120), (dxi - 12, dyi), (dxi + 12, dyi), 1)
    alpha_line(surf, (*GOLD, 120), (dxi, dyi - 12), (dxi, dyi + 12), 1)
    pygame.draw.circle(surf, GOLD, (dxi, dyi), 5)
    pygame.draw.circle(surf, (255, 240, 190), (dxi - 1, dyi - 1), 2)

    # ── death callout ──
    f10, f8 = font(10), font(8)
    sub = f"PILLAR {DEATH_PILLAR}  ·  {PHASE_LABEL} 18.4%"
    cw = max(f10.size("ENDED HERE")[0], f8.size(sub)[0]) + 20
    # Hang the callout off the star on whichever side keeps it clear of the
    # other waypoints — a chip sitting on a node would hide a magnitude.
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
    text(surf, sub, 8, midleft=(cr.x + 10, cr.y + 24), color=CREAM, shadow=None)
    taken.append(cr.inflate(6, 6))

    # GOLD magnitude-0 label, hung off the star away from the chip
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
        fade.fill((*SCRIM, int(238 * (1 - i / 10) ** 1.4)), pygame.Rect(0, i, W, 1))
    surf.blit(fade, (0, 74))
    alpha_line(surf, (255, 206, 92, 150), (0, 74), (W - 1, 74), 1)

    text(surf, f"FLIGHT LOG  ·  DAY {DAY_N}", 21, center=(W // 2, 28),
         color=GOLD, track=3, shadow=None)
    text(surf, f"PILLAR {DEATH_PILLAR}   ·   0:{TIME_ALIVE:02d}", 12,
         center=(W // 2, 55), color=CREAM, shadow=None)

    # ── headline ──
    pct = f"{DEATH_PHASE * 100:.0f}%"
    f_big, f_sml = font(21), font(8)
    w_pct = f_big.size(pct)[0]
    w_tail = f_sml.size("  OF THE DAY FLOWN")[0] + 1 * len("  OF THE DAY FLOWN")
    x0 = (W - (w_pct + w_tail)) / 2
    text(surf, pct, 21, midleft=(x0, 104), color=GOLD, shadow=None)
    text(surf, "  OF THE DAY FLOWN", 8, midleft=(x0 + w_pct, 107), color=COOL,
         shadow=None, track=1)

    # ── BACK pill ──
    pr = pygame.Rect(0, 0, 122, 36)
    pr.center = (180, 597)
    sh = pygame.Surface((pr.w + 8, pr.h + 8), pygame.SRCALPHA)
    pygame.draw.rect(sh, (0, 0, 0, 100), sh.get_rect(), border_radius=21)
    surf.blit(sh, (pr.x - 4, pr.y - 1))
    grad = pygame.Surface(pr.size, pygame.SRCALPHA)
    for y in range(pr.h):
        grad.fill(lerp_color((255, 228, 172), (226, 168, 96), y / (pr.h - 1)) + (255,),
                  pygame.Rect(0, y, pr.w, 1))
    mask = pygame.Surface(pr.size, pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255), mask.get_rect(), border_radius=18)
    grad.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(grad, pr.topleft)
    pygame.draw.rect(surf, (110, 68, 38), pr, width=1, border_radius=18)
    text(surf, "BACK", 13, center=(pr.centerx, pr.centery), color=(66, 40, 20),
         shadow=None, track=2)

    return surf


def main():
    surf = render_screen()
    out = "/home/user/skybit/docs/flight_log_arc_v2/constellation/round_1.png"
    os.makedirs(os.path.dirname(out), exist_ok=True)
    pygame.image.save(surf, out)
    loaded = pygame.image.load(out)
    print(f"saved {out}  {loaded.get_size()}")

    # sanity: the rules this design lives or dies by
    dys = [ROUTE[i + 1][1] - ROUTE[i][1] for i in range(len(ROUTE) - 1)]
    print("dy signs:", "".join("+" if d > 0 else "-" for d in dys))
    worst = min(math.hypot(ROUTE[i][0] - ROUTE[j][0], ROUTE[i][1] - ROUTE[j][1])
                for i in range(len(ROUTE)) for j in range(i + 1, len(ROUTE)))
    print(f"min node separation: {worst:.1f}px   stars: {len(STARS)}")


if __name__ == "__main__":
    main()
