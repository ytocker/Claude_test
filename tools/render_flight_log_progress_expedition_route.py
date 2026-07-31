#!/usr/bin/env python3
"""
expedition-route  ·  flight_log_progress  ·  round 1

The day cycle drawn as a surveyed expedition route on a sandstone field plate.
Octolinear, because Beck's rule -- horizontals, verticals and 45s only -- is
what buys the horizontal station names: three stacked runs give ~780 px of
usable path, so all seven time-of-day phases set flat at full size instead of
stacking or rotating. The fold-backs are pure schematic licence: each run
carries a different phase-per-pixel density, which is exactly how a transit
diagram trades geographic truth for legibility, and it is what pulls the
geyser start and the death marker apart on run one.

Warm ink on parchment throughout -- no starfield, no neon, no glow. The only
"flown" signal is an additive amber rail laid inside the ink from the start
to the death phase; everything ahead keeps full contrast, because a route you
have not walked is still charted at full strength on a real map.
"""
import os
import sys
import math
import random

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import pygame
pygame.init()
pygame.display.set_mode((1, 1))

from game.biome import PHASE_BOUNDARIES, palette_for_phase
from game.weather import (THERMAL_START_PHASE, THERMAL_END_PHASE, SNOW_STORM_CENTER,
                          _phase_for_pillar)
from game.config import LATE_GAME_PILLAR, CLOWN_START_PILLAR, RAIN_START_PILLAR

# Pillar-gated events ride the same phase axis as the weather ones, so the map
# has a single ruler: every mark sits at the phase the player will actually
# reach it, not at a decorative slot.
LAMP_PHASE = _phase_for_pillar(LATE_GAME_PILLAR)
CLOWN_PHASE = _phase_for_pillar(CLOWN_START_PILLAR)
RAIN_PHASE = _phase_for_pillar(RAIN_START_PILLAR)


W, H = 360, 640
SS = 3                                  # supersample factor for every curve

FONT_PATH = os.path.join(ROOT, "game", "assets", "LiberationSans-Bold.ttf")
_FONTS = {}


def font(size):
    if size not in _FONTS:
        _FONTS[size] = pygame.font.Font(FONT_PATH, size)
    return _FONTS[size]


# ── plate palette ────────────────────────────────────────────────────────────
PARCH_TOP = (236, 221, 191)
PARCH_BOT = (221, 202, 168)
PARCH_PANEL = (228, 211, 178)
INK = (70, 44, 29)
INK_SOFT = (128, 99, 71)
INK_FAINT = (168, 145, 116)
CREAM = (252, 242, 218)
AMBER_ADD = (152, 90, 22)               # added ON TOP of the ink, not beside it
AMBER_FLAT = (222, 134, 51)             # the same rail, pre-blended, for keys
SCARLET = (172, 40, 32)
SLATE = (74, 96, 130)


def lerp_c(a, b, t):
    return (round(a[0] + (b[0] - a[0]) * t),
            round(a[1] + (b[1] - a[1]) * t),
            round(a[2] + (b[2] - a[2]) * t))


def lum(c):
    return 0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2]


# Key grid: three columns keeps all six marks on two rows inside the 64 px
# strip between the cartouche and the footer.
KEY_COLS = (44, 152, 254)
KEY_ROWS = (527, 550)


# ── mock run ─────────────────────────────────────────────────────────────────
DEATH_PHASE = 0.184
DEATH_PILLAR = 25
DAY_NUMBER = 1
TIME_ALIVE = 47


# ── route geometry ───────────────────────────────────────────────────────────
# Three runs stacked 100 px apart, folded by chamfered 45 corners. The corner
# chamfer is what makes the fold read as one continuous line rather than three
# separate rules with a bracket.
LEFT, RIGHT = 40, 300
ROW_Y = (150, 250, 350)
CH = 22

RUN1 = [(LEFT, ROW_Y[0]), (RIGHT, ROW_Y[0])]
CNR1 = [(RIGHT, ROW_Y[0]), (RIGHT + CH, ROW_Y[0] + CH),
        (RIGHT + CH, ROW_Y[1] - CH), (RIGHT, ROW_Y[1])]
RUN2 = [(RIGHT, ROW_Y[1]), (LEFT, ROW_Y[1])]
CNR2 = [(LEFT, ROW_Y[1]), (LEFT - CH, ROW_Y[1] + CH),
        (LEFT - CH, ROW_Y[2] - CH), (LEFT, ROW_Y[2])]
RUN3 = [(LEFT, ROW_Y[2]), (RIGHT, ROW_Y[2])]

# Phase span per leg. Run one deliberately swallows the whole crowded opening
# of the day (both hazards, the genie, the clown and the rain) so no event ever
# lands on a fold, where a pendant would have nowhere to hang.
LEGS = [
    (RUN1, 0.00, 0.46),
    (CNR1, 0.46, 0.47),
    (RUN2, 0.47, 0.75),
    (CNR2, 0.75, 0.76),
    (RUN3, 0.76, 1.00),
]

FULL_PATH = (RUN1 + CNR1[1:] + RUN2[1:] + CNR2[1:] + RUN3[1:])


def _cum(pts):
    out = [0.0]
    for a, b in zip(pts, pts[1:]):
        out.append(out[-1] + math.dist(a, b))
    return out


def _walk(pts, s):
    """Point + unit direction at arc length s along a polyline."""
    cum = _cum(pts)
    s = max(0.0, min(cum[-1], s))
    for i in range(len(pts) - 1):
        if s <= cum[i + 1] or i == len(pts) - 2:
            seg = cum[i + 1] - cum[i]
            t = (s - cum[i]) / seg if seg else 0.0
            ax, ay = pts[i]
            bx, by = pts[i + 1]
            d = math.hypot(bx - ax, by - ay) or 1.0
            return (ax + (bx - ax) * t, ay + (by - ay) * t,
                    (bx - ax) / d, (by - ay) / d)
    return (*pts[-1], 1.0, 0.0)


def at_phase(p):
    """(x, y, dx, dy) for a day phase in [0,1]."""
    p = max(0.0, min(1.0, p))
    for pts, p0, p1 in LEGS:
        if p0 <= p <= p1:
            t = (p - p0) / (p1 - p0)
            return _walk(pts, t * _cum(pts)[-1])
    return _walk(RUN3, _cum(RUN3)[-1])


def up_normal(dx, dy):
    """Perpendicular that leans up (then left) -- one light direction for the
    whole plate, so the ink highlight never flips side across a fold."""
    a, b = (-dy, dx), (dy, -dx)
    if a[1] < b[1] or (a[1] == b[1] and a[0] < b[0]):
        return a
    return b


# ── stroking ─────────────────────────────────────────────────────────────────
def stroke(surf, pts, w, color):
    """Thick polyline as quads + round joins, drawn on the SS surface."""
    r = w * SS / 2.0
    for a, b in zip(pts, pts[1:]):
        ax, ay = a[0] * SS, a[1] * SS
        bx, by = b[0] * SS, b[1] * SS
        dx, dy = bx - ax, by - ay
        L = math.hypot(dx, dy)
        if L < 1e-6:
            continue
        nx, ny = -dy / L * r, dx / L * r
        pygame.draw.polygon(surf, color, [(ax + nx, ay + ny), (bx + nx, by + ny),
                                          (bx - nx, by - ny), (ax - nx, ay - ny)])
    if r >= 1:
        for p in pts:
            pygame.draw.circle(surf, color, (int(round(p[0] * SS)),
                                             int(round(p[1] * SS))), int(round(r)))


def sample_phase_range(p0, p1, n=120):
    return [at_phase(p0 + (p1 - p0) * i / n)[:2] for i in range(n + 1)]


def disc(surf, x, y, r, color):
    pygame.draw.circle(surf, color, (int(round(x * SS)), int(round(y * SS))),
                       int(round(r * SS)))


def ring(surf, x, y, r, w, outer, inner):
    disc(surf, x, y, r, outer)
    disc(surf, x, y, r - w, inner)


# ── parchment ────────────────────────────────────────────────────────────────
def build_parchment():
    """Cached noise plate: gradient + blotch + fibre + speck, built once."""
    surf = pygame.Surface((W, H)).convert()
    for y in range(H):
        pygame.draw.line(surf, lerp_c(PARCH_TOP, PARCH_BOT, y / (H - 1)),
                         (0, y), (W, y))

    rng = random.Random(20260731)

    stain = pygame.Surface((W, H), pygame.SRCALPHA)
    for _ in range(90):
        cx, cy = rng.randrange(-20, W + 20), rng.randrange(-20, H + 20)
        r = rng.randint(18, 70)
        a = rng.randint(6, 16)
        tone = (176, 152, 116, a) if rng.random() < 0.6 else (255, 246, 224, a)
        pygame.draw.circle(stain, tone, (cx, cy), r)
    surf.blit(stain, (0, 0))

    fibre = pygame.Surface((W, H), pygame.SRCALPHA)
    for _ in range(520):
        x, y = rng.randrange(W), rng.randrange(H)
        L = rng.randint(3, 11)
        a = rng.randint(10, 26)
        if rng.random() < 0.5:
            pygame.draw.line(fibre, (150, 126, 94, a), (x, y), (x + L, y))
        else:
            pygame.draw.line(fibre, (255, 250, 232, a), (x, y), (x + L, y))
    surf.blit(fibre, (0, 0))

    for _ in range(26000):
        x, y = rng.randrange(W), rng.randrange(H)
        r, g, b = surf.get_at((x, y))[:3]
        d = rng.randint(-13, 11)
        surf.set_at((x, y), (max(0, min(255, r + d)),
                             max(0, min(255, g + d)),
                             max(0, min(255, b + d))))

    edge = pygame.Surface((W, H), pygame.SRCALPHA)
    for i in range(26):
        a = int(30 * (1 - i / 26) ** 1.6)
        if a <= 0:
            continue
        pygame.draw.line(edge, (128, 100, 70, a), (i, 0), (i, H))
        pygame.draw.line(edge, (128, 100, 70, a), (W - 1 - i, 0), (W - 1 - i, H))
        pygame.draw.line(edge, (128, 100, 70, a), (0, i), (W, i))
        pygame.draw.line(edge, (128, 100, 70, a), (0, H - 1 - i), (W, H - 1 - i))
    surf.blit(edge, (0, 0))
    return surf


# ── type ─────────────────────────────────────────────────────────────────────
def ls_surf(size, text, color, sp=1):
    f = font(size)
    glyphs = [f.render(ch, True, color) for ch in text]
    w = sum(g.get_width() for g in glyphs) + sp * max(0, len(text) - 1)
    h = max((g.get_height() for g in glyphs), default=1)
    out = pygame.Surface((max(1, w), h), pygame.SRCALPHA)
    x = 0
    for g in glyphs:
        out.blit(g, (x, 0))
        x += g.get_width() + sp
    return out


def put(dst, surf, x, y, anchor="center"):
    r = surf.get_rect()
    setattr(r, anchor, (x, y))
    dst.blit(surf, r)
    return r


# ── event glyphs (all on the SS layer) ───────────────────────────────────────
def glyph_geyser(s, cx, cy):
    """Thermal vent: lipped mouth, tapering jet, rounded plume head."""
    pygame.draw.line(s, INK, ((cx - 8) * SS, cy * SS), ((cx - 2) * SS, cy * SS), 2 * SS)
    pygame.draw.line(s, INK, ((cx + 2) * SS, cy * SS), ((cx + 8) * SS, cy * SS), 2 * SS)
    jet = [(cx - 2.4, cy - 1), (cx - 4.0, cy - 9), (cx - 5.2, cy - 15),
           (cx + 5.2, cy - 15), (cx + 4.0, cy - 9), (cx + 2.4, cy - 1)]
    pygame.draw.polygon(s, (198, 132, 52), [(p[0] * SS, p[1] * SS) for p in jet])
    for dx, dy, r in ((-3.2, -16.2, 3.4), (3.2, -16.2, 3.4), (0, -19.0, 4.2)):
        disc(s, cx + dx, cy + dy, r, (198, 132, 52))
    core = [(cx - 1.1, cy - 2), (cx - 2.0, cy - 12), (cx + 2.0, cy - 12), (cx + 1.1, cy - 2)]
    pygame.draw.polygon(s, CREAM, [(p[0] * SS, p[1] * SS) for p in core])
    disc(s, cx, cy - 17.4, 2.4, CREAM)
    disc(s, cx - 7.6, cy - 12.4, 1.3, (198, 132, 52))
    disc(s, cx + 7.6, cy - 13.6, 1.1, (198, 132, 52))


def glyph_lamp(s, cx, cy):
    """Genie lamp: bellied body, long spout, ring handle, wisp."""
    body = []
    for i in range(24):
        a = i / 24 * math.tau
        body.append((cx + math.cos(a) * 7.4, cy + 1.2 + math.sin(a) * 4.3))
    pygame.draw.polygon(s, INK, [(p[0] * SS, p[1] * SS) for p in body])
    pygame.draw.polygon(s, INK, [((cx - 5) * SS, (cy - 0.5) * SS),
                                 ((cx - 14) * SS, (cy - 3.6) * SS),
                                 ((cx - 5) * SS, (cy + 3.2) * SS)])
    ring(s, cx + 9.4, cy - 0.6, 4.0, 1.6, INK, PARCH_PANEL)
    pygame.draw.polygon(s, INK, [((cx - 1.6) * SS, (cy - 2.6) * SS),
                                 ((cx + 1.6) * SS, (cy - 2.6) * SS),
                                 ((cx + 1.0) * SS, (cy - 5.0) * SS),
                                 ((cx - 1.0) * SS, (cy - 5.0) * SS)])
    disc(s, cx - 12.4, cy - 6.4, 1.7, (198, 132, 52))
    disc(s, cx - 10.8, cy - 9.6, 1.2, (198, 132, 52))
    pygame.draw.polygon(s, CREAM, [((cx - 3.4) * SS, (cy - 1.4) * SS),
                                   ((cx + 1.4) * SS, (cy - 2.4) * SS),
                                   ((cx + 1.4) * SS, (cy - 1.2) * SS),
                                   ((cx - 3.4) * SS, (cy - 0.2) * SS)])


def glyph_clown(s, cx, cy):
    """Harlequin lozenge -- quartered diamond with a scarlet pip."""
    r = 8.2
    top, bot = (cx, cy - r), (cx, cy + r)
    lft, rgt = (cx - r * 0.72, cy), (cx + r * 0.72, cy)
    quads = [((top, lft, (cx, cy)), INK), ((top, rgt, (cx, cy)), CREAM),
             ((bot, lft, (cx, cy)), CREAM), ((bot, rgt, (cx, cy)), INK)]
    for tri, col in quads:
        pygame.draw.polygon(s, col, [(p[0] * SS, p[1] * SS) for p in tri])
    stroke(s, [top, rgt, bot, lft, top], 1.4, INK)
    disc(s, cx, cy, 1.8, SCARLET)


def glyph_rain(s, cx, cy):
    """Teardrop plus two slanted fall ticks."""
    drop = [(cx, cy - 8.4)]
    for i in range(19):
        a = math.pi * (-0.36 + 1.72 * i / 18)
        drop.append((cx + math.sin(a) * 5.2, cy + 1.4 + math.cos(a) * -5.2))
    pygame.draw.polygon(s, SLATE, [(p[0] * SS, p[1] * SS) for p in drop])
    stroke(s, [(cx - 1.6, cy - 5.6), (cx - 2.6, cy - 1.2)], 1.4, (196, 214, 238))
    for dx in (-8.0, 8.0):
        stroke(s, [(cx + dx, cy - 3.0), (cx + dx - 1.8, cy + 2.6)], 1.4, SLATE)


def glyph_snow(s, cx, cy):
    """Six-spoke asterism with barbs."""
    for i in range(6):
        a = i / 6 * math.tau
        ex, ey = cx + math.cos(a) * 8.0, cy + math.sin(a) * 8.0
        stroke(s, [(cx, cy), (ex, ey)], 1.5, SLATE)
        for sgn in (-1, 1):
            ba = a + sgn * 0.85
            mx, my = cx + math.cos(a) * 5.0, cy + math.sin(a) * 5.0
            stroke(s, [(mx, my), (mx + math.cos(ba) * 3.0, my + math.sin(ba) * 3.0)],
                   1.2, SLATE)
    disc(s, cx, cy, 1.8, CREAM)
    disc(s, cx, cy, 1.1, SLATE)


# ── station beads ────────────────────────────────────────────────────────────
def bead_color(phase):
    """Phase's own sky, pushed toward ink only as far as the parchment needs."""
    c = palette_for_phase(phase)["sky_mid"]
    c = (round(c[0]), round(c[1]), round(c[2]))
    base = lum(PARCH_TOP)
    for _ in range(24):
        if abs(lum(c) - base) >= 58:
            break
        c = lerp_c(c, INK, 0.08)
    return c


# ── the screen ───────────────────────────────────────────────────────────────
def render_screen():
    screen = build_parchment()

    # plate frame + corner ticks
    frame = pygame.Surface((W, H), pygame.SRCALPHA)
    pygame.draw.rect(frame, (*INK, 105), pygame.Rect(9, 9, W - 18, H - 18), 1)
    pygame.draw.rect(frame, (*INK, 45), pygame.Rect(12, 12, W - 24, H - 24), 1)
    for cx, cy, sx, sy in ((9, 9, 1, 1), (W - 10, 9, -1, 1),
                           (9, H - 10, 1, -1), (W - 10, H - 10, -1, -1)):
        pygame.draw.line(frame, (*INK, 130), (cx, cy + 7 * sy), (cx + 7 * sx, cy))
    screen.blit(frame, (0, 0))

    ink_l = pygame.Surface((W * SS, H * SS), pygame.SRCALPHA)
    rail_l = pygame.Surface((W * SS, H * SS))          # black elsewhere: ADD-safe
    marks = pygame.Surface((W * SS, H * SS), pygame.SRCALPHA)

    # ── route ink + cream inner highlight ────────────────────────────────
    stroke(ink_l, FULL_PATH, 4, INK)
    for a, b in zip(FULL_PATH, FULL_PATH[1:]):
        d = math.hypot(b[0] - a[0], b[1] - a[1]) or 1.0
        nx, ny = up_normal((b[0] - a[0]) / d, (b[1] - a[1]) / d)
        stroke(ink_l, [(a[0] + nx * 1.0, a[1] + ny * 1.0),
                       (b[0] + nx * 1.0, b[1] + ny * 1.0)], 1, (*CREAM, 190))

    # ── thermal corridor: dashed shoulder above the run it occupies ──────
    corr = sample_phase_range(THERMAL_START_PHASE, THERMAL_END_PHASE, 90)
    dashes, run = [], []
    for i, (x, y) in enumerate(corr):
        if (i // 4) % 2 == 0:
            run.append((x, y - 9))
        elif run:
            dashes.append(run)
            run = []
    if run:
        dashes.append(run)
    for d in dashes:
        if len(d) > 1:
            stroke(ink_l, d, 1.6, (196, 140, 66))
    for end in (corr[0], corr[-1]):
        stroke(ink_l, [(end[0], end[1] - 12), (end[0], end[1] - 6)], 1.6, (196, 140, 66))

    # ── the flown rail: additive amber laid INSIDE the ink ───────────────
    stroke(rail_l, sample_phase_range(0.0, DEATH_PHASE, 80), 2.6, AMBER_ADD)

    # ── terminus cap ─────────────────────────────────────────────────────
    # Only the far end gets one; the DAY bead already caps the start.
    ex, ey, _, _ = at_phase(1.0)
    stroke(marks, [(ex + 1.5, ey - 7), (ex + 1.5, ey + 7)], 3, INK)

    # ── event pendants (below the run) ───────────────────────────────────
    pendants = [
        (THERMAL_START_PHASE, "geyser"),
        (LAMP_PHASE, "lamp"),
        (CLOWN_PHASE, "clown"),
        (RAIN_PHASE, "rain"),
        (SNOW_STORM_CENTER, "snow"),
    ]
    for ph, kind in pendants:
        x, y, dx, dy = at_phase(ph)
        if kind == "geyser":
            # leans back off the route so it clears the GOLDEN HOUR name
            stroke(marks, [(x, y - 5), (x - 8, y - 9)], 1.4, INK_SOFT)
            glyph_geyser(marks, x - 8, y - 9)
            continue
        stroke(marks, [(x, y + 3), (x, y + 10)], 1.4, INK_SOFT)
        gx, gy = x, y + 19
        if kind == "lamp":
            glyph_lamp(marks, gx, gy)
        elif kind == "clown":
            glyph_clown(marks, gx, gy)
        elif kind == "rain":
            glyph_rain(marks, gx, gy)
        else:
            glyph_snow(marks, gx, gy)

    # ── stations ─────────────────────────────────────────────────────────
    for ph, name in PHASE_BOUNDARIES:
        x, y, dx, dy = at_phase(ph)
        col = bead_color(ph)
        if ph <= DEATH_PHASE:
            disc(marks, x, y, 6.0, col)
        else:
            disc(marks, x, y, 4.5, INK)
            disc(marks, x, y, 3.0, col)

    # ── death marker + forward flag ──────────────────────────────────────
    # The flag hangs clear of the pendant band so the banner can run forward
    # under the events it never reached.
    dx_, dy_, _, _ = at_phase(DEATH_PHASE)
    flag_top, flag_bot = dy_ + 30, dy_ + 56
    stroke(marks, [(dx_, dy_ + 4), (dx_, flag_bot - 1)], 1.6, INK)
    lab_a = "ENDED HERE"
    lab_b = "PILLAR %d · DAY %.3f" % (DEATH_PILLAR, DEATH_PHASE)
    wa = ls_surf(8, lab_a, SCARLET, 1).get_width()
    wb = ls_surf(8, lab_b, INK, 1).get_width()
    bw = 11 + max(wa, wb) + 13
    tail = 7
    banner = [(dx_, flag_top), (dx_ + bw, flag_top), (dx_ + bw - tail, (flag_top + flag_bot) / 2),
              (dx_ + bw, flag_bot), (dx_, flag_bot)]
    pygame.draw.polygon(marks, CREAM, [(p[0] * SS, p[1] * SS) for p in banner])
    stroke(marks, banner + [banner[0]], 1.4, INK)
    pygame.draw.polygon(marks, SCARLET, [(dx_ * SS, flag_top * SS),
                                         ((dx_ + 5) * SS, flag_top * SS),
                                         ((dx_ + 5) * SS, flag_bot * SS),
                                         (dx_ * SS, flag_bot * SS)])
    ring(marks, dx_, dy_, 6.2, 2.0, INK, SCARLET)

    # ── cartouche + legend + footer plates ───────────────────────────────
    cart = pygame.Rect(26, 414, 308, 84)
    notch = 9
    cpoly = [(cart.left + notch, cart.top), (cart.right - notch, cart.top),
             (cart.right, cart.top + notch), (cart.right, cart.bottom - notch),
             (cart.right - notch, cart.bottom), (cart.left + notch, cart.bottom),
             (cart.left, cart.bottom - notch), (cart.left, cart.top + notch)]
    pygame.draw.polygon(marks, (*PARCH_PANEL, 235), [(p[0] * SS, p[1] * SS) for p in cpoly])
    stroke(marks, cpoly + [cpoly[0]], 1.4, INK)
    inner = [(p[0] + (3 if p[0] < cart.centerx else -3),
              p[1] + (3 if p[1] < cart.centery else -3)) for p in cpoly]
    stroke(marks, inner + [inner[0]], 0.8, (*INK, 90))

    pill = pygame.Rect(120, 581, 120, 36)
    pygame.draw.rect(marks, (*PARCH_PANEL, 250),
                     pygame.Rect(pill.x * SS, pill.y * SS, pill.w * SS, pill.h * SS),
                     border_radius=18 * SS)
    pygame.draw.rect(marks, INK,
                     pygame.Rect(pill.x * SS, pill.y * SS, pill.w * SS, pill.h * SS),
                     width=2 * SS, border_radius=18 * SS)
    ax, ay = pill.x + 26, pill.centery
    stroke(marks, [(ax + 4, ay - 5), (ax - 1, ay), (ax + 4, ay + 5)], 2, INK)

    # key swatches -- three columns, drawn at the same scale they read on the map
    c0, c1, c2 = KEY_COLS
    r0, r1 = KEY_ROWS
    disc(marks, c0, r0, 6.0, bead_color(0.0))
    disc(marks, c0, r1, 4.5, INK)
    disc(marks, c0, r1, 3.0, bead_color(0.6438))
    stroke(marks, [(c1 - 8, r0), (c1 + 8, r0)], 4, INK)
    stroke(marks, [(c1 - 8, r0), (c1 + 8, r0)], 2.6, AMBER_FLAT)
    ring(marks, c1, r1, 6.2, 2.0, INK, SCARLET)
    for k in range(3):
        stroke(marks, [(c2 - 9 + k * 7, r0), (c2 - 5 + k * 7, r0)], 1.6, (196, 140, 66))
    stroke(marks, [(c2, r1 - 7), (c2, r1 - 3)], 1.4, INK_SOFT)
    disc(marks, c2, r1 + 1, 3.4, INK)

    # ── composite ────────────────────────────────────────────────────────
    screen.blit(pygame.transform.smoothscale(ink_l, (W, H)), (0, 0))
    screen.blit(pygame.transform.smoothscale(rail_l, (W, H)), (0, 0),
                special_flags=pygame.BLEND_RGB_ADD)
    screen.blit(pygame.transform.smoothscale(marks, (W, H)), (0, 0))

    # ── type layer ───────────────────────────────────────────────────────
    put(screen, ls_surf(8, "SKYBIT · AERIAL SURVEY", INK_SOFT, 2), 180, 24)
    put(screen, ls_surf(27, "FLIGHT LOG", INK, 2), 180, 38, "midtop")
    put(screen, ls_surf(9, "EXPEDITION 001  ·  DAY %d  ·  %d s ALOFT"
                        % (DAY_NUMBER, TIME_ALIVE), INK_SOFT, 1), 180, 76)

    rule = pygame.Surface((W, H), pygame.SRCALPHA)
    for yy, a in ((95, 120), (98, 55)):
        pygame.draw.line(rule, (*INK, a), (26, yy), (166, yy))
        pygame.draw.line(rule, (*INK, a), (194, yy), (334, yy))
    pygame.draw.polygon(rule, (*INK, 150), [(180, 91), (185, 96.5), (180, 102), (175, 96.5)])
    pygame.draw.line(rule, (*INK, 70), (26, 504), (334, 504))
    pygame.draw.line(rule, (*INK, 70), (26, 567), (334, 567))
    screen.blit(rule, (0, 0))

    # station names -- horizontal, full size, above the line
    for ph, name in PHASE_BOUNDARIES:
        x, y, _, _ = at_phase(ph)
        s = ls_surf(9, name, INK, 1)
        put(screen, s, min(max(x, 14 + s.get_width() / 2), W - 14 - s.get_width() / 2),
            y - 16, "midbottom")

    put(screen, ls_surf(8, "DAY 2", INK_SOFT, 1), 300, ROW_Y[2] - 16, "midbottom")
    put(screen, ls_surf(8, "OPEN SKY · NO HAZARD CHARTED", INK_FAINT, 1),
        190, ROW_Y[1] + 20, "midtop")

    # death flag copy
    bx = dx_ + 11
    put(screen, ls_surf(8, lab_a, SCARLET, 1), bx, flag_top + 8, "midleft")
    put(screen, ls_surf(8, lab_b, INK, 1), bx, flag_top + 19, "midleft")

    # cartouche copy
    put(screen, ls_surf(9, "STILL AHEAD", INK, 3), 180, cart.top + 12)
    pygame.draw.line(screen, INK_FAINT, (124, cart.top + 21), (236, cart.top + 21))
    rows = [("lamp", "GENIE LAMP", "PILLAR %d" % LATE_GAME_PILLAR),
            ("clown", "CLOWN GAUNTLET", "PILLAR %d" % CLOWN_START_PILLAR),
            ("rain", "STORM FRONT", "PILLAR %d" % RAIN_START_PILLAR)]
    for i, (kind, what, where) in enumerate(rows):
        yy = cart.top + 34 + i * 17
        put(screen, ls_surf(9, what, INK, 1), 66, yy, "midleft")
        put(screen, ls_surf(9, where, INK_SOFT, 1), 306, yy, "midright")
        pygame.draw.line(screen, (*INK_FAINT, 255), (66 + ls_surf(9, what, INK, 1).get_width() + 6,
                                                     yy + 4),
                         (306 - ls_surf(9, where, INK_SOFT, 1).get_width() - 6, yy + 4))

    # key copy
    for cx, r, txt in ((c0, r0, "LOGGED"), (c0, r1, "AHEAD"),
                       (c1, r0, "FLOWN"), (c1, r1, "ENDED"),
                       (c2, r0, "HAZARD"), (c2, r1, "EVENT")):
        put(screen, ls_surf(8, txt, INK, 1), cx + 13, r, "midleft")
    put(screen, ls_surf(7, "KEY", INK_FAINT, 2), 26, 508, "topleft")

    put(screen, ls_surf(12, "BACK", INK, 2), 190, pill.centery)
    return screen, cart


# ── cartouche glyph pass (needs the SS pipeline, so it rides a second layer) ──
def add_cartouche_glyphs(screen, cart):
    layer = pygame.Surface((W * SS, H * SS), pygame.SRCALPHA)
    for i, fn in enumerate((glyph_lamp, glyph_clown, glyph_rain)):
        fn(layer, 46, cart.top + 34 + i * 17)
    screen.blit(pygame.transform.smoothscale(layer, (W, H)), (0, 0))


# ── review sheet ─────────────────────────────────────────────────────────────
def build_sheet(screen):
    SW, SH = 1010, 900
    sheet = pygame.Surface((SW, SH))
    sheet.fill((48, 45, 43))
    for y in range(SH):
        pygame.draw.line(sheet, lerp_c((52, 49, 46), (36, 34, 33), y / (SH - 1)),
                         (0, y), (SW, y))

    put(sheet, font(19).render(
        "SKYBIT  ·  FLIGHT LOG PROGRESS  ·  CONCEPT: EXPEDITION ROUTE  ·  ROUND 1",
        True, (238, 228, 210)), 24, 22, "midleft")
    put(sheet, font(11).render(
        "octolinear dogleg · warm ink on parchment · seven phase names horizontal at full size",
        True, (156, 146, 136)), 24, 44, "midleft")

    def panel(x, y, surf, label, scale=1.0):
        if scale != 1.0:
            surf = pygame.transform.smoothscale(
                surf, (int(surf.get_width() * scale), int(surf.get_height() * scale)))
        pygame.draw.rect(sheet, (18, 17, 16),
                         pygame.Rect(x - 2, y - 2, surf.get_width() + 4,
                                     surf.get_height() + 4))
        sheet.blit(surf, (x, y))
        put(sheet, font(12).render(label, True, (176, 166, 154)),
            x, y + surf.get_height() + 12, "midleft")
        return surf.get_height()

    panel(24, 68, screen, "FULL SCREEN  ·  360 × 640  ·  1:1")

    route = pygame.Surface((340, 292))
    route.blit(screen, (0, 0), pygame.Rect(10, 112, 340, 292))
    panel(416, 68, route, "ROUTE BAND  ·  1.7×  ·  folds, beads, pendants, flag", 1.7)

    lower = pygame.Surface((340, 220))
    lower.blit(screen, (0, 0), pygame.Rect(10, 406, 340, 220))
    panel(416, 600, lower, "CARTOUCHE · KEY · FOOTER  ·  1.4×", 1.4)

    return sheet


def main():
    screen, cart = render_screen()
    add_cartouche_glyphs(screen, cart)

    out_dir = os.path.join(ROOT, "docs", "flight_log_progress", "expedition_route")
    os.makedirs(out_dir, exist_ok=True)
    sheet = build_sheet(screen)
    path = os.path.join(out_dir, "round_1.png")
    pygame.image.save(sheet, path)
    print("saved", path, sheet.get_size())

    for ph, name in PHASE_BOUNDARIES:
        x, y, _, _ = at_phase(ph)
        c = bead_color(ph)
        print("  %-12s phase %.4f  ->  (%6.1f, %3.0f)  bead %s  dL %.0f"
              % (name, ph, x, y, c, abs(lum(c) - lum(PARCH_TOP))))
    for lbl, ph in (("geyser", THERMAL_START_PHASE), ("death", DEATH_PHASE),
                    ("genie", LAMP_PHASE), ("clown", CLOWN_PHASE),
                    ("rain", RAIN_PHASE), ("snow", SNOW_STORM_CENTER)):
        x, y, _, _ = at_phase(ph)
        print("  %-8s phase %.4f -> (%6.1f, %3.0f)" % (lbl, ph, x, y))

    print("  -- station name extents (frame is 12..348) --")
    spans = []
    for ph, name in PHASE_BOUNDARIES:
        x, y, _, _ = at_phase(ph)
        w = ls_surf(9, name, INK, 1).get_width()
        cx = min(max(x, 14 + w / 2), W - 14 - w / 2)
        spans.append((y, cx - w / 2, cx + w / 2, name))
    for y, a, b, name in spans:
        clash = [n for yy, aa, bb, n in spans
                 if n != name and yy == y and aa < b and a < bb]
        print("  %-12s row %3.0f  x %5.1f..%5.1f%s"
              % (name, y, a, b, "  CLASH " + str(clash) if clash else ""))


if __name__ == "__main__":
    main()
