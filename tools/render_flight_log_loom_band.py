"""Render docs/flight_log_screen/loom_band/round_1.png — the LOOM BAND flight log.

LOOM BAND reads a run as a strap loom seen head-on. The day is a warp: ~20 pale
flax threads tensioned from a gold heddle bar and running off the bottom edge.
The part of the day the player actually flew is *finished weave* — 5 px weft
picks dyed from the biome sky palette, with the over/under grain rendered as a
warp-aligned two-tone checker. The part they never reached is bare warp on a
neutral ground: no hue at all, and the brightest mass on the screen, so the
screen's headline reads as "look how much thread is still waiting" rather than
"here is where you died".

Why the weft is lifted off the raw sky colour: a dyed thread reflects light off
a fibre surface, so it always reads lighter and chalkier than the sky it samples
— and the night keyframes (sky_mid ~ (15,25,70)) would otherwise sink into the
very dark plum background and break the band's silhouette.

Why the sky palette is inlined instead of imported: this render must stay
runnable from a bare checkout of the branch, and only the sky_mid/sky_bot stops
are needed — not the stone/foliage half of the biome keyframes.

Scarlet appears exactly once per strap: the overhand knot that ties off the
broken weft on the last woven row. Every other accent is gold, flax or grey.
"""
import math
import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

pygame.display.init()
pygame.display.set_mode((1, 1))
pygame.font.init()

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT_PATH = os.path.join(ROOT, "game", "assets", "LiberationSans-Bold.ttf")
OUT_DIR = os.path.join(ROOT, "docs", "flight_log_screen", "loom_band")
os.makedirs(OUT_DIR, exist_ok=True)
OUT = os.path.join(OUT_DIR, "round_1.png")


# ── canvas + palette ─────────────────────────────────────────────────────────
W, H = 360, 640

BG = (12, 10, 18)
BG_LIFT = (26, 21, 38)

GOLD = (240, 192, 64)
GOLD_BRIGHT = (255, 231, 160)
GOLD_DEEP = (146, 100, 26)
GOLD_MUTED = (198, 162, 92)
SCARLET = (172, 40, 32)
SCARLET_LIT = (214, 78, 62)

FLAX = (200, 190, 170)
FLAX_DARK = (128, 120, 106)
GROUND_TOP = (240, 238, 235)
GROUND_BOT = (230, 226, 220)
THREAD_ON_GROUND = (212, 205, 190)
THREAD_HILITE = (252, 250, 246)
BAND_EDGE = (206, 200, 190)

GREY_LABEL = (150, 140, 130)
INK = (74, 62, 50)

# ── loom geometry ────────────────────────────────────────────────────────────
BAR_Y0, BAR_Y1 = 80, 96
WEAVE_TOP, WEAVE_BOT = 110, 530
WEAVE_H = WEAVE_BOT - WEAVE_TOP
ROW_H = 5
# Thread gauge is a constant 9 px on every strap — a narrower band holds fewer
# warps, it does not hold thinner ones.
STRAP_SOLO = dict(x0=90, x1=270, n=20)
STRAP_D1 = dict(x0=48, x1=156, n=12)
STRAP_D2 = dict(x0=180, x1=288, n=12)

PHASE_BOUNDARIES = [
    (0.000, "DAY"),
    (0.231, "GOLDEN HOUR"),
    (0.363, "SUNSET"),
    (0.513, "DUSK"),
    (0.644, "NIGHT"),
    (0.794, "PREDAWN"),
    (0.906, "SUNRISE"),
]
PHASE_SHORT = {
    "GOLDEN HOUR": "GOLDEN HR",
    "PREDAWN": "PREDAWN",
}
EVENT_MARKERS = [
    (0.15, "GEYSER"),
    (0.41, "CLOWN"),
    (0.44, "STORM"),
    (0.85, "SNOW"),
]
# Which warp each bead is strung on, chosen so neighbouring events never stack
# on the same thread.
EVENT_WARP_SOLO = {"GEYSER": 5, "CLOWN": 6, "STORM": 13, "SNOW": 9}
EVENT_WARP_NARROW = {"GEYSER": 3, "CLOWN": 4, "STORM": 8, "SNOW": 6}

# A day runs ~175 pillars for a steady flyer, which is what makes the day-2
# mock runs land on pillar 249 (42% into day 2) and pillar 180 (3% into it).
DAY_PILLARS = 175

RUN_A = dict(phase=0.184, pillar=25, day=1, time="0:47")
RUN_B = dict(phase=0.420, pillar=DAY_PILLARS + 74, day=2, time="7:06")
RUN_C = dict(phase=0.030, pillar=DAY_PILLARS + 5, day=2, time="5:09")


# ── colour helpers ───────────────────────────────────────────────────────────
def lerp(a, b, t):
    t = max(0.0, min(1.0, t))
    return (int(a[0] + (b[0] - a[0]) * t),
            int(a[1] + (b[1] - a[1]) * t),
            int(a[2] + (b[2] - a[2]) * t))


def scale_v(c, k):
    return tuple(max(0, min(255, int(round(ch * k)))) for ch in c[:3])


def lum(c):
    return 0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2]


def desat(c, keep):
    l = lum(c)
    return tuple(max(0, min(255, int(round(l + (ch - l) * keep)))) for ch in c[:3])


def smoothstep(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


# sky_mid / sky_bot lifted from the biome keyframes — the two stops that carry
# the phase's identity at eye level.
_SKY_STOPS = [
    (0.00, (90, 170, 230), (170, 220, 245)),
    (0.18, (220, 175, 140), (255, 210, 160)),
    (0.32, (230, 95, 120), (255, 160, 90)),
    (0.48, (70, 45, 130), (170, 95, 140)),
    (0.62, (15, 25, 70), (35, 55, 115)),
    (0.78, (70, 60, 140), (200, 130, 180)),
    (0.90, (255, 150, 150), (255, 220, 170)),
    (1.00, (90, 170, 230), (170, 220, 245)),
]


def sky_for_phase(p):
    p = p % 1.0
    for i in range(len(_SKY_STOPS) - 1):
        t0, m0, b0 = _SKY_STOPS[i]
        t1, m1, b1 = _SKY_STOPS[i + 1]
        if t0 <= p <= t1:
            span = t1 - t0
            t = smoothstep((p - t0) / span) if span > 0 else 0.0
            return lerp(m0, m1, t), lerp(b0, b1, t)
    return _SKY_STOPS[0][1], _SKY_STOPS[0][2]


def weft_color(p):
    """Dye colour for a weft pick sampled straight off the sky at phase p."""
    mid, bot = sky_for_phase(p)
    c = lerp(mid, bot, 0.35)
    c = lerp(c, (255, 255, 255), 0.14)
    l = lum(c)
    if l < 58:
        c = lerp(c, (255, 255, 255), (58 - l) / 220.0)
    return c


# One dye per named phase, taken from the keyframe that names it. Sampling the
# continuously-lerped sky instead would hand mid-morning a near-grey weft — the
# blue-to-amber crossfade passes through neutral — and grey is the one thing the
# weave must never be, because "no hue" is what marks the unflown warp.
PHASE_DYES = [weft_color(stop[0]) for stop in _SKY_STOPS[:len(PHASE_BOUNDARIES)]]


def dye_for_phase(p):
    """The weaver swaps the shuttle at a phase boundary, so a phase is woven in
    one dye that drifts only slightly toward the next before the gold pass."""
    p = p % 1.0
    idx = 0
    for i, (b, _n) in enumerate(PHASE_BOUNDARIES):
        if p >= b:
            idx = i
    b0 = PHASE_BOUNDARIES[idx][0]
    b1 = PHASE_BOUNDARIES[idx + 1][0] if idx + 1 < len(PHASE_BOUNDARIES) else 1.0
    t = (p - b0) / max(1e-6, b1 - b0)
    nxt = PHASE_DYES[(idx + 1) % len(PHASE_DYES)]
    return lerp(PHASE_DYES[idx], nxt, 0.22 * t)


# ── text ─────────────────────────────────────────────────────────────────────
_FONTS = {}


def font(size):
    f = _FONTS.get(size)
    if f is None:
        f = pygame.font.Font(FONT_PATH, size)
        _FONTS[size] = f
    return f


def text(surf, s, size, color, pos, anchor="topleft", track=0):
    if track:
        glyphs = [font(size).render(ch, True, color) for ch in s]
        w = sum(g.get_width() for g in glyphs) + track * (len(s) - 1)
        h = glyphs[0].get_height() if glyphs else 0
        strip = pygame.Surface((max(1, w), max(1, h)), pygame.SRCALPHA)
        x = 0
        for g in glyphs:
            strip.blit(g, (x, 0))
            x += g.get_width() + track
        img = strip
    else:
        img = font(size).render(s, True, color)
    r = img.get_rect(**{anchor: pos})
    surf.blit(img, r)
    return r


# ── warp geometry ────────────────────────────────────────────────────────────
def warp_x(strap, i, y, slack=0.0):
    """x of warp i at height y. Threads gather slightly as they leave the bar,
    and carry a slow sine sag so the band never reads as a printed ruler."""
    x0, x1, n = strap["x0"], strap["x1"], strap["n"]
    pitch = (x1 - x0) / float(n)
    base = x0 + pitch * (i + 0.5)
    cx = (x0 + x1) * 0.5
    gather = 0.045 * (1.0 - smoothstep((y - BAR_Y1) / 54.0))
    x = cx + (base - cx) * (1.0 - gather)
    amp = 1.5 + 2.6 * slack
    x += math.sin(y / 80.0 + i * 0.3) * amp
    if slack:
        x += math.sin(y / 190.0 + i * 0.11) * 2.4 * slack
    return x


def warp_poly(strap, i, y_from, y_to, slack=0.0, step=5):
    pts = []
    y = y_from
    while y < y_to:
        pts.append((warp_x(strap, i, y, slack), y))
        y += step
    pts.append((warp_x(strap, i, y_to, slack), y_to))
    return pts


def draw_warps(surf, strap, y_from, y_to, color, slack=0.0, hilite=None):
    for i in range(strap["n"]):
        pts = warp_poly(strap, i, y_from, y_to, slack)
        if hilite is not None:
            pygame.draw.aalines(surf, hilite, False,
                                [(x - 1.0, y) for x, y in pts])
        pygame.draw.aalines(surf, color, False, pts)


# ── background ───────────────────────────────────────────────────────────────
def draw_background(surf):
    for y in range(H):
        t = y / float(H)
        surf.fill(lerp(BG_LIFT, BG, smoothstep(min(1.0, t * 1.35))), (0, y, W, 1))
    # A cold rim at the very bottom keeps the live warp from dissolving into
    # the panel edge on a dark display.
    glow = pygame.Surface((W, 90), pygame.SRCALPHA)
    for y in range(90):
        a = int(16 * (y / 89.0))
        glow.fill((40, 44, 70, a), (0, y, W, 1))
    surf.blit(glow, (0, H - 90))


# ── heddle bar ───────────────────────────────────────────────────────────────
def draw_bar(surf, straps):
    x0 = min(s["x0"] for s in straps) - 10
    x1 = max(s["x1"] for s in straps) + 10
    h = BAR_Y1 - BAR_Y0
    for y in range(h):
        t = y / float(h - 1)
        if t < 0.42:
            c = lerp(GOLD_BRIGHT, GOLD, t / 0.42)
        else:
            c = lerp(GOLD, GOLD_DEEP, (t - 0.42) / 0.58)
        surf.fill(c, (x0, BAR_Y0 + y, x1 - x0, 1))
    surf.fill(scale_v(GOLD_DEEP, 0.55), (x0, BAR_Y1 - 1, x1 - x0, 1))
    surf.fill(lerp(GOLD_BRIGHT, (255, 255, 255), 0.5), (x0, BAR_Y0, x1 - x0, 1))

    for s in straps:
        for i in range(s["n"]):
            nx = int(round(warp_x(s, i, BAR_Y1)))
            pygame.draw.line(surf, (72, 50, 18), (nx, BAR_Y0 + 3), (nx, BAR_Y1 - 3))
            pygame.draw.line(surf, lerp(GOLD_BRIGHT, (255, 255, 255), 0.3),
                             (nx + 1, BAR_Y0 + 3), (nx + 1, BAR_Y1 - 4))

    cy = (BAR_Y0 + BAR_Y1) // 2
    for kx in (x0, x1):
        pygame.draw.circle(surf, GOLD_DEEP, (kx, cy), 8)
        pygame.draw.circle(surf, GOLD, (kx, cy), 7)
        pygame.draw.circle(surf, GOLD_BRIGHT, (kx - 2, cy - 2), 3)
        pygame.draw.circle(surf, scale_v(GOLD_DEEP, 0.7), (kx, cy), 8, 1)


# ── finished weave ───────────────────────────────────────────────────────────
def row_shift(y, slack):
    if not slack:
        return 0.0, 1.0
    dx = math.sin(y * 0.055 + 0.8) * 3.0 * slack
    sq = 1.0 - 0.035 * slack * (1.0 + math.sin(y * 0.031))
    return dx, sq


def draw_weave(surf, strap, p_from, p_to, keep_chroma=1.0, slack=0.0):
    """Lay 5 px weft picks from phase p_from to p_to, warp-aligned checker grain."""
    x0, x1, n = strap["x0"], strap["x1"], strap["n"]
    cw = (x1 - x0) / float(n)
    y_end = WEAVE_TOP + p_to * WEAVE_H
    r = 0
    y = WEAVE_TOP + p_from * WEAVE_H
    while y < y_end - 0.5:
        rh = min(ROW_H, y_end - y)
        p = (y + rh * 0.5 - WEAVE_TOP) / WEAVE_H
        # Hand-dyed yarn is never twice the same, so each pick carries a hair
        # of value drift — without it the band reads as a printed swatch.
        base = scale_v(dye_for_phase(p), 1.0 + 0.028 * math.sin(r * 1.7))
        if keep_chroma < 1.0:
            base = scale_v(desat(base, keep_chroma), 0.9)
        dx, sq = row_shift(y, slack)
        rx0 = x0 + dx + (x1 - x0) * (1 - sq) * 0.5
        rx1 = x1 + dx - (x1 - x0) * (1 - sq) * 0.5
        rcw = (rx1 - rx0) / float(n)
        for c in range(n):
            col = scale_v(base, 1.12 if (r + c) % 2 == 0 else 0.88)
            a = rx0 + c * rcw
            b = rx0 + (c + 1) * rcw
            surf.fill(col, (int(round(a)), int(round(y)),
                            max(1, int(round(b)) - int(round(a))), int(math.ceil(rh))))
        # Each pick is beaten down onto the last, so the seam between them is a
        # shadow line, not a gap.
        shade = pygame.Surface((max(1, int(rx1 - rx0)), 1), pygame.SRCALPHA)
        shade.fill((0, 0, 0, 46))
        surf.blit(shade, (int(round(rx0)), int(round(y + rh)) - 1))
        # Weft turns around at alternating selvedges — that is what scallops it.
        bulge = scale_v(base, 0.94)
        bx = rx0 if r % 2 == 0 else rx1
        pygame.draw.ellipse(surf, bulge,
                            pygame.Rect(int(bx - 2.5), int(y), 5, max(2, int(rh))))
        pygame.draw.ellipse(surf, scale_v(base, 0.72),
                            pygame.Rect(int(bx - 2.5), int(y), 5, max(2, int(rh))), 1)
        y += ROW_H
        r += 1

    # Warp ribbing: the same threads still run under the picks, so the band
    # keeps a vertical grain that lines up with the bare warp below it.
    rib = pygame.Surface((W, H), pygame.SRCALPHA)
    top = WEAVE_TOP + p_from * WEAVE_H
    for c in range(n + 1):
        pts = []
        yy = top
        while yy < y_end:
            dx, sq = row_shift(yy, slack)
            ax0 = x0 + dx + (x1 - x0) * (1 - sq) * 0.5
            pts.append((ax0 + c * cw * sq, yy))
            yy += 6
        if len(pts) > 1:
            pygame.draw.aalines(rib, (0, 0, 0, 40), False, pts)
    surf.blit(rib, (0, 0))
    return y_end


def draw_gold_pass(surf, strap, phase, slack=0.0):
    """A single pass of metallic thread marks a phase boundary in the weave."""
    y = WEAVE_TOP + phase * WEAVE_H
    dx, sq = row_shift(y, slack)
    x0 = strap["x0"] + dx + (strap["x1"] - strap["x0"]) * (1 - sq) * 0.5
    x1 = strap["x1"] + dx - (strap["x1"] - strap["x0"]) * (1 - sq) * 0.5
    pygame.draw.line(surf, GOLD_BRIGHT, (x0, y), (x1, y))
    pygame.draw.line(surf, GOLD_DEEP, (x0, y + 1), (x1, y + 1))
    for k in range(int(x0) + 2, int(x1) - 1, 7):
        surf.fill(GOLD, (k, int(y), 3, 1))


def draw_heading_cord(surf, strap, y_top):
    """The 3% floor: a doubled gold heading cord, never thinner than 10 px."""
    x0, x1 = strap["x0"], strap["x1"]
    for k, yy in enumerate((y_top, y_top + 6)):
        for dy in range(4):
            t = dy / 3.0
            surf.fill(lerp(GOLD_BRIGHT, GOLD_DEEP, t), (x0, yy + dy, x1 - x0, 1))
        for tx in range(int(x0), int(x1) - 2, 5):
            pygame.draw.line(surf, scale_v(GOLD_DEEP, 0.75),
                             (tx, yy + 3), (tx + 3, yy))
        pygame.draw.circle(surf, GOLD, (int(x0), yy + 2), 2)
        pygame.draw.circle(surf, GOLD, (int(x1), yy + 2), 2)
    return y_top + 10


# ── bare warp ────────────────────────────────────────────────────────────────
def draw_bare_warp(surf, strap, y_from, slack=0.0, fade_to=546):
    x0, x1 = strap["x0"], strap["x1"]
    w = int(x1 - x0)
    top = int(math.ceil(y_from))
    bot = fade_to
    ground = pygame.Surface((w, bot - top), pygame.SRCALPHA)
    for y in range(bot - top):
        yy = top + y
        t = (yy - top) / max(1.0, float(WEAVE_BOT - top))
        c = lerp(GROUND_TOP, GROUND_BOT, min(1.0, t))
        a = 255 if yy <= WEAVE_BOT else int(255 * max(0.0, 1.0 - (yy - WEAVE_BOT) / 16.0))
        ground.fill((c[0], c[1], c[2], a), (0, y, w, 1))
    surf.blit(ground, (int(x0), top))

    draw_warps(surf, strap, top + 1, min(bot - 2, WEAVE_BOT + 12),
               THREAD_ON_GROUND, slack, hilite=THREAD_HILITE)

    # Raking light across taut thread — the sheen is what makes the unflown
    # stretch the brightest mass on the screen instead of a flat swatch.
    sheen = pygame.Surface((w, bot - top), pygame.SRCALPHA)
    for x in range(w):
        u = x / float(w)
        v = math.exp(-((u - 0.36) ** 2) / 0.030) * 26 + math.exp(-((u - 0.80) ** 2) / 0.012) * 12
        if v <= 0.5:
            continue
        for y in range(bot - top):
            yy = top + y
            fall = 1.0 if yy <= WEAVE_BOT else max(0.0, 1.0 - (yy - WEAVE_BOT) / 16.0)
            sheen.fill((255, 255, 250, int(v * fall)), (x, y, 1, 1))
    surf.blit(sheen, (int(x0), top))

    for ex in (x0, x1):
        pygame.draw.line(surf, BAND_EDGE, (ex, top), (ex, WEAVE_BOT))
    pygame.draw.line(surf, lerp(BAND_EDGE, GROUND_TOP, 0.5), (x0 + 1, top), (x0 + 1, WEAVE_BOT))


def draw_fringe(surf, strap, slack=0.0):
    """A survived day is cut off the loom: its warp ends hang as fringe."""
    for i in range(strap["n"]):
        x = warp_x(strap, i, WEAVE_BOT, slack)
        splay = (i - (strap["n"] - 1) / 2.0) * 0.22
        pts = [(x + splay * (k / 4.0) ** 2 + math.sin(k * 0.5 + i) * 0.8, WEAVE_BOT + k)
               for k in range(0, 16)]
        pygame.draw.aalines(surf, desat(FLAX_DARK, 0.6), False, pts)
        pygame.draw.circle(surf, desat(FLAX, 0.6), (int(pts[-1][0]), int(pts[-1][1])), 1)


# ── labels along the bare warp ───────────────────────────────────────────────
def draw_phase_labels(surf, strap, death_phase, label_x, size=8, short=False,
                      flown_gold=False):
    for p, name in PHASE_BOUNDARIES:
        if p <= death_phase:
            # A phase that was actually woven is named in its own gold thread.
            if flown_gold:
                y = max(WEAVE_TOP + 5, WEAVE_TOP + p * WEAVE_H)
                text(surf, name, size, GOLD_MUTED, (label_x, y), anchor="midleft")
            continue
        y = WEAVE_TOP + p * WEAVE_H
        pygame.draw.line(surf, (198, 190, 178), (strap["x1"] + 2, y), (strap["x1"] + 6, y))
        dash = pygame.Surface((int(strap["x1"] - strap["x0"]), 1), pygame.SRCALPHA)
        for dx in range(0, dash.get_width(), 6):
            dash.fill((150, 142, 130, 90), (dx, 0, 3, 1))
        surf.blit(dash, (int(strap["x0"]), int(y)))
        label = PHASE_SHORT.get(name, name) if short else name
        text(surf, label, size, GREY_LABEL, (label_x, y), anchor="midleft")


def draw_event_labels(surf, strap, name, y, label_x, bead_x):
    pygame.draw.line(surf, (120, 112, 104), (label_x + 2, y), (strap["x0"] - 3, y))
    # The leader carries on into the band as a dotted run so the name is read
    # against its own bead, not against whichever row it happens to sit on.
    lead = pygame.Surface((max(1, int(bead_x - 6 - strap["x0"])), 1), pygame.SRCALPHA)
    for dx in range(0, lead.get_width(), 4):
        lead.fill((40, 34, 30, 105), (dx, 0, 2, 1))
    surf.blit(lead, (int(strap["x0"]) + 2, int(y)))
    text(surf, name, 7, GREY_LABEL, (label_x, y), anchor="midright")


# ── beads ────────────────────────────────────────────────────────────────────
def draw_bead(surf, x, y, kind, keep_chroma=1.0):
    body = {
        "GEYSER": (180, 200, 220),
        "CLOWN": (245, 245, 245),
        "STORM": (120, 130, 145),
        "SNOW": (230, 235, 240),
    }[kind]
    if keep_chroma < 1.0:
        body = desat(body, keep_chroma)
    rw, rh = 8, 11
    rect = pygame.Rect(int(x - rw / 2), int(y - rh / 2), rw, rh)

    shadow = pygame.Surface((rw + 4, rh + 4), pygame.SRCALPHA)
    pygame.draw.ellipse(shadow, (20, 16, 24, 90), pygame.Rect(2, 3, rw, rh))
    surf.blit(shadow, (rect.x - 2, rect.y - 1))

    if kind == "CLOWN":
        pygame.draw.ellipse(surf, (245, 245, 245), rect)
        half = pygame.Surface((rw, rh), pygame.SRCALPHA)
        pygame.draw.rect(half, (24, 22, 26), (0, 0, rw // 2, rh // 2))
        pygame.draw.rect(half, (24, 22, 26), (rw // 2, rh // 2, rw - rw // 2, rh - rh // 2))
        mask = pygame.Surface((rw, rh), pygame.SRCALPHA)
        pygame.draw.ellipse(mask, (255, 255, 255, 255), (0, 0, rw, rh))
        half.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
        surf.blit(half, rect.topleft)
    else:
        pygame.draw.ellipse(surf, scale_v(body, 0.72), rect)
        pygame.draw.ellipse(surf, body, rect.inflate(-2, -2))
        pygame.draw.ellipse(surf, lerp(body, (255, 255, 255), 0.55),
                            pygame.Rect(rect.x + 1, rect.y + 1, 4, 5))
    pygame.draw.ellipse(surf, scale_v(body, 0.5), rect, 1)
    surf.fill(lerp(body, (255, 255, 255), 0.9), (rect.x + 2, rect.y + 2, 2, 2))
    if kind == "SNOW":
        for dx, dy in ((-5, -6), (5, 5), (5, -5)):
            surf.fill((255, 255, 255), (int(x + dx), int(y + dy), 1, 1))


# ── death ────────────────────────────────────────────────────────────────────
def draw_death(surf, strap, y, phase, slack=0.0, reach=20):
    """Broken weft: both ends spring loose, keep their crimp, and the run is
    tied off with the one scarlet knot on the screen."""
    dx, sq = row_shift(y, slack)
    x0 = strap["x0"] + dx
    x1 = strap["x1"] + dx
    end_col = dye_for_phase(max(0.0, phase - 0.01))
    for side, ex in ((-1, x0), (1, x1)):
        pts = []
        for k in range(0, 23):
            t = k / 22.0
            px = ex + side * (2 + reach * t)
            py = y + 1 + math.sin(t * 6.6) * 4.6 * min(1.0, t * 3.0) + t * t * 5.0
            pts.append((px, py))
        pygame.draw.aalines(surf, (18, 14, 22), False, [(p[0], p[1] + 1) for p in pts])
        pygame.draw.aalines(surf, end_col, False, pts)
        tip = pts[-1]
        pygame.draw.circle(surf, scale_v(end_col, 0.8), (int(tip[0]), int(tip[1])), 2, 1)

    cx = (x0 + x1) * 0.5
    ky = y + 2
    pygame.draw.circle(surf, (18, 14, 22), (int(cx), int(ky) + 1), 7)
    pygame.draw.circle(surf, SCARLET, (int(cx), int(ky)), 6)
    pygame.draw.circle(surf, scale_v(SCARLET, 0.62), (int(cx), int(ky)), 3)
    pygame.draw.circle(surf, SCARLET_LIT, (int(cx) - 2, int(ky) - 2), 2)
    for sgn in (-1, 1):
        pygame.draw.aalines(surf, SCARLET, False, [
            (cx + sgn * 4, ky + 4), (cx + sgn * 8, ky + 8), (cx + sgn * 9, ky + 13)])


# ── one screen ───────────────────────────────────────────────────────────────
def draw_screen(run, two_strap=False, min_rule=False):
    surf = pygame.Surface((W, H))
    draw_background(surf)

    straps = [STRAP_D1, STRAP_D2] if two_strap else [STRAP_SOLO]
    live = straps[-1]
    phase = run["phase"]

    # Snap the break to a real pick so the knot never floats between rows.
    death_y = WEAVE_TOP + round(phase * WEAVE_H / ROW_H) * ROW_H
    if min_rule:
        death_y = WEAVE_TOP + 10

    for s in straps:
        # A survived day has been cut off the loom, so its warp stops at the
        # last pick; only the live strap still runs off the bottom edge.
        finished = two_strap and s is STRAP_D1
        draw_warps(surf, s, BAR_Y1, WEAVE_BOT if finished else H, FLAX,
                   slack=(0.9 if finished else 0.0))

    if two_strap:
        draw_weave(surf, STRAP_D1, 0.0, 1.0, keep_chroma=0.6, slack=0.9)
        for p, _n in PHASE_BOUNDARIES[1:]:
            draw_gold_pass(surf, STRAP_D1, p, slack=0.9)
        draw_fringe(surf, STRAP_D1, slack=0.9)
        for p, name in EVENT_MARKERS:
            bx = warp_x(STRAP_D1, EVENT_WARP_NARROW[name], WEAVE_TOP + p * WEAVE_H, 0.9)
            draw_bead(surf, bx, WEAVE_TOP + p * WEAVE_H, name, keep_chroma=0.45)

    if min_rule:
        draw_heading_cord(surf, live, WEAVE_TOP)
    else:
        draw_weave(surf, live, 0.0, (death_y - WEAVE_TOP) / WEAVE_H)
        draw_gold_pass(surf, live, 0.0)
        for p, _n in PHASE_BOUNDARIES[1:]:
            if WEAVE_TOP + p * WEAVE_H < death_y:
                draw_gold_pass(surf, live, p)

    draw_bare_warp(surf, live, death_y)

    label_x = live["x1"] + 8
    draw_phase_labels(surf, live, (death_y - WEAVE_TOP) / WEAVE_H, label_x,
                      size=(7 if two_strap else 8), short=two_strap,
                      flown_gold=not two_strap)

    # Day end: the warp keeps going past it, so the boundary is a whisper.
    dash = pygame.Surface((int(live["x1"] - live["x0"]) + 14, 2), pygame.SRCALPHA)
    for dx in range(0, dash.get_width(), 8):
        dash.fill((*GOLD_MUTED, 150), (dx, 0, 4, 1))
    surf.blit(dash, (int(live["x0"]) - 7, WEAVE_BOT))
    text(surf, "DAY %d ENDS" % run["day"], 7, GOLD_MUTED, (label_x, WEAVE_BOT + 1),
         anchor="midleft")

    ev_warp = EVENT_WARP_NARROW if two_strap else EVENT_WARP_SOLO
    for p, name in EVENT_MARKERS:
        ey = WEAVE_TOP + p * WEAVE_H
        if min_rule and ey < death_y:
            continue
        bx = warp_x(live, ev_warp[name], ey)
        if not two_strap:
            draw_event_labels(surf, live, name, ey, live["x0"] - 12, bx)
        draw_bead(surf, bx, ey, name)

    draw_death(surf, live, death_y, phase, reach=13 if two_strap else 20)

    pct = max(1, int(round(phase * 100)))
    text(surf, "%d%% OF DAY %d WOVEN" % (pct, run["day"]), 8, INK,
         ((live["x0"] + live["x1"]) // 2, death_y + 17), anchor="center")

    if min_rule:
        ly = WEAVE_TOP + 5
        pygame.draw.line(surf, GOLD_MUTED, (live["x1"] + 2, ly), (live["x1"] + 12, ly))
        pygame.draw.line(surf, GOLD_MUTED, (live["x1"] + 12, ly), (live["x1"] + 16, ly - 6))
        leader = "3%  ·  PILLAR 180"
        if font(8).size(leader)[0] > W - (live["x1"] + 18) - 4:
            text(surf, "3%", 10, GOLD, (live["x1"] + 18, ly - 15), anchor="topleft")
            text(surf, "PILLAR 180", 7, GOLD_MUTED, (live["x1"] + 18, ly - 2), anchor="topleft")
        else:
            text(surf, leader, 8, GOLD, (live["x1"] + 18, ly - 7), anchor="topleft")

    draw_bar(surf, straps)
    if two_strap:
        for s, tag in ((STRAP_D1, "DAY 1"), (STRAP_D2, "DAY 2")):
            text(surf, tag, 8, GOLD_MUTED if s is STRAP_D1 else GOLD,
                 ((s["x0"] + s["x1"]) // 2, BAR_Y0 - 5), anchor="midbottom")

    # ── chrome ──
    text(surf, "FLIGHT LOG", 13, GOLD, (W // 2, 16), anchor="midtop", track=3)
    text(surf, "PILLAR %d  ·  DAY %d" % (run["pillar"], run["day"]), 9, GOLD_MUTED,
         (20, 46), anchor="midleft")
    phase_name = "DAY"
    for p, n in PHASE_BOUNDARIES:
        if p <= run["phase"]:
            phase_name = n
    text(surf, "%s  ·  %s" % (phase_name, run["time"]), 9, GOLD_MUTED,
         (W - 20, 46), anchor="midright")
    pygame.draw.line(surf, (58, 48, 40), (20, 62), (W - 20, 62))

    btn = pygame.Rect(22, 588, 88, 30)
    pygame.draw.rect(surf, (22, 18, 28), btn, border_radius=6)
    pygame.draw.rect(surf, GOLD_DEEP, btn, 2, border_radius=6)
    pygame.draw.rect(surf, GOLD, btn.inflate(-4, -4), 1, border_radius=5)
    text(surf, "BACK", 10, GOLD, btn.center, anchor="center", track=1)
    return surf


# ── review sheet ─────────────────────────────────────────────────────────────
SHEET_W, SHEET_H = 1480, 1120

READING_KEY = [
    ("WARP", "the whole day — every pillar of"),
    (None, "it — tensioned from the heddle bar"),
    (None, "and running off the bottom edge."),
    ("", ""),
    ("WEFT", "what you actually flew. One dye"),
    (None, "per phase, over/under grain, and a"),
    (None, "single gold pass at every change."),
    ("", ""),
    ("BARE WARP", "what you never reached."),
    (None, "No hue at all, and the brightest"),
    (None, "mass on the screen — thread"),
    (None, "still waiting to be woven."),
    ("", ""),
    ("BEADS", "events, strung on one warp:"),
    (None, "pale blue geyser, black-and-white"),
    (None, "clown, slate storm, frosted snow."),
    ("", ""),
    ("KNOT", "the break. The weft springs"),
    (None, "loose at both selvedges and is"),
    (None, "tied off — the only scarlet here."),
]


def crop2x(src, rect):
    sub = pygame.Surface((rect[2], rect[3]))
    sub.blit(src, (0, 0), rect)
    return pygame.transform.smoothscale(sub, (rect[2] * 2, rect[3] * 2))


def build_sheet():
    hero = draw_screen(RUN_A)
    day2 = draw_screen(RUN_B, two_strap=True)
    min3 = draw_screen(RUN_C, two_strap=True, min_rule=True)

    sheet = pygame.Surface((SHEET_W, SHEET_H))
    for y in range(SHEET_H):
        sheet.fill(lerp((20, 18, 26), (10, 9, 14), y / float(SHEET_H)), (0, y, SHEET_W, 1))

    text(sheet, "SKYBIT  ·  FLIGHT LOG  ·  LOOM BAND", 20, GOLD, (40, 26), track=3)
    text(sheet, "round 1  —  the day is a warp; what you flew is woven, what you "
                "missed is bare thread still waiting on the loom",
         12, (150, 142, 132), (40, 56))

    panels = [
        (hero, 40, "RUN A  ·  1:1  (360x640)",
         "pillar 25, day 1, fell at phase 0.184 — 18% woven, 82% bare warp"),
        (day2, 460, "DAY 2  ·  two straps on one bar",
         "day 1 finished, slack + 40% desaturated; day 2 live at right"),
        (min3, 880, "3% FLOOR  ·  doubled heading cord",
         "a 3% run still gets 10 px of gold cord plus a right-margin leader"),
    ]
    for img, x, title, sub in panels:
        pygame.draw.rect(sheet, (44, 38, 32), (x - 2, 88 - 2, W + 4, H + 4), 2)
        sheet.blit(img, (x, 88))
        text(sheet, title, 12, GOLD_MUTED, (x, 740))
        text(sheet, sub, 10, (132, 124, 116), (x, 758))

    details = [
        ((80, 60, 200, 125), 40, "HEDDLE BAR + FIRST PICKS  (2x)"),
        ((80, 150, 200, 125), 460, "BREAK, KNOT + BARE WARP  (2x)"),
        ((80, 250, 200, 125), 880, "BEADS ON THE WARP  (2x)"),
    ]
    for rect, x, title in details:
        img = crop2x(hero, rect)
        pygame.draw.rect(sheet, (44, 38, 32), (x - 2, 786 - 2, img.get_width() + 4,
                                               img.get_height() + 4), 2)
        sheet.blit(img, (x, 786))
        text(sheet, title, 11, GOLD_MUTED, (x, 786 + img.get_height() + 8))

    kx, ky = 1264, 92
    text(sheet, "HOW TO READ IT", 12, GOLD, (kx, ky), track=2)
    ky += 24
    for head, body in READING_KEY:
        if head == "":
            ky += 8
            continue
        x = kx
        if head is not None:
            r = text(sheet, head, 10, GOLD_MUTED, (x, ky))
            x = r.right + 5
        text(sheet, body, 10, (146, 138, 130), (x, ky))
        ky += 14

    small = pygame.transform.smoothscale(hero, (135, 240))
    sx, sy = 1310, 786
    pygame.draw.rect(sheet, (44, 38, 32), (sx - 2, sy - 2, 139, 244), 2)
    sheet.blit(small, (sx, sy))
    text(sheet, "0.375x  legibility", 11, GOLD_MUTED, (sx, sy + 250))

    swy = 1082
    text(sheet, "PALETTE", 10, (120, 112, 104), (40, swy - 14))
    sw = [("bg", BG), ("gold", GOLD), ("scarlet (knot only)", SCARLET),
          ("flax warp", FLAX), ("bare ground", GROUND_TOP)]
    x = 40
    for name, col in sw:
        pygame.draw.rect(sheet, col, (x, swy, 22, 16))
        pygame.draw.rect(sheet, (70, 62, 56), (x, swy, 22, 16), 1)
        r = text(sheet, name, 10, (140, 132, 124), (x + 28, swy + 8), anchor="midleft")
        x = r.right + 22
    return sheet, hero


def main():
    sheet, hero = build_sheet()
    pygame.image.save(sheet, OUT)

    probe = pygame.image.load(OUT)
    print("saved", OUT, probe.get_size())
    checks = [
        ("hero bg", hero.get_at((6, 300))[:3]),
        ("heddle bar", hero.get_at((180, 86))[:3]),
        ("weave day row", hero.get_at((150, 130))[:3]),
        ("weave golden row", hero.get_at((150, 180))[:3]),
        ("bare ground", hero.get_at((250, 300))[:3]),
        ("bare ground low", hero.get_at((250, 500))[:3]),
        ("knot", hero.get_at((180, 187))[:3]),
        ("below day end", hero.get_at((180, 570))[:3]),
    ]
    for name, col in checks:
        print("  %-18s %s  lum=%.0f" % (name, col, lum(col)))
    print("  sheet bytes", os.path.getsize(OUT))


if __name__ == "__main__":
    main()
    pygame.quit()
    sys.exit(0)
