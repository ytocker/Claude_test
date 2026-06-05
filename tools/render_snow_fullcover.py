"""DESIGN EXPLORATION — Pip gets buried in a squall and ends as a SNOWMAN (the
full-cover end state). Throwaway sheet tool; touches NO game code.

ROUND 7 redesign. Round 6 (direction "C") built an upright stacked snowman but
the owner rejected it: the shapes "looked bad and the placement of elements was
not correct" (scattered red marks, vertical bars down the chest, floating arms,
a dense comparison grid). This round throws out the buried-bird envelope entirely
and builds a PURE CLASSIC SNOWMAN from analytic geometry — we LOSE Pip: no macaw
crown tuft, no blue wing-tip, no scarlet. Just a real snowman, rendered LARGE
(it is expected to be bigger than the bird in-game).

THE CORE FIX is rigorous element placement on a stacked-ball skeleton:
  * Body  — 2 or 3 vertically-aligned balls, each higher ball smaller.
  * Hat   — flat on TOP of the head ball, brim horizontal, brim ~ head width.
  * Eyes  — two coal dots, symmetric about the vertical axis, upper-front of head.
  * Nose  — HORIZONTAL carrot, below-and-between the eyes, on the head front.
  * Mouth — a short downward ARC of coal dots below the carrot (a smile), never
            vertical bars.
  * Scarf — wrapped at the NECK (head/torso junction), one tail down a side.
  * Buttons — 2-3 coal dots in a vertical line down the CENTRE-FRONT of the torso.
  * Arms  — thin bare twigs out the SIDES of the middle ball, rooted ON the
            contour, each ending in 2-3 forked fingers.

The SNOW is the faithful shipped snow_fx W2 recipe run down the stacked contour:
OFF body fill + bright WHITE crest over the top ~18% + cool-blue BLUE under-edge
over the bottom ~26% + a soft cornice overhang + the sine ripple. It must still
read as the GAME's snow — just snowman-shaped.

The sheet is CLEAN (the owner loved docs/snow_full_cover/progression.png and
disliked the dense round_6 grid): ONE row of 5 LARGE, well-spaced variants on a
simple sky, each with a compact WHITEOUT chip below proving the silhouette and
its value-carriers (dark hat, warm carrot, cool-blue under-edge) survive a white
sky. The 5 vary ONE/TWO structural axes (ball count, hat, arm pose) over the
SAME correct face placement.

numpy-free / pure pygame so the contour + recipe port straight into snow_fx.py.

Run from repo root:
  SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python -m tools.render_snow_fullcover
Output: docs/snow_full_cover/round_7.png
"""
from __future__ import annotations

import math
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

pygame.init()
pygame.display.set_mode((360, 640))

from game import snow_fx
from game.draw import make_gradient_surface

OUT_DIR = os.path.join(ROOT, "docs", "snow_full_cover")
os.makedirs(OUT_DIR, exist_ok=True)

# Snow palette — VERBATIM from snow_fx so the snowman body is the shipped look.
WHITE = snow_fx.WHITE
OFF = snow_fx.OFF
BLUE = snow_fx.BLUE

# Snowman material palette (drawn ON TOP of the finished snow body). These are
# the value-contrast carriers against the white snow / white sky: a near-black
# hat + coal, a warm carrot, and the cool-blue snow under-edge.
CARROT = (240, 130, 32)
CARROT_HI = (255, 176, 92)
CARROT_RIDGE = (196, 92, 18)
COAL = (28, 30, 38)
COAL_HI = (96, 100, 112)
GLINT = (236, 244, 252)
TWIG = (110, 78, 48)
TWIG_HI = (150, 112, 74)
SCARF_RED = (210, 58, 62)
SCARF_DARK = (168, 40, 46)
SCARF_WHITE = (244, 248, 252)
HAT_BLACK = (32, 34, 44)
HAT_HI = (74, 78, 96)
HAT_BAND = (196, 60, 64)


# ── stacked-ball snowman contour (numpy-free) ────────────────────────────────
# A snowman is a column of vertically-aligned balls, each higher one smaller.
# We union the circles into one per-column (top, bot) envelope, then run the W2
# recipe down it. `balls` is a list of (cy_fraction, radius_fraction) measured in
# cell-height units, drawn bottom-first (largest first). Returning the analytic
# ball list lets every kit element seat on a real centre — nothing floats.
def _snowman_contour(cw, ch, balls):
    cx = cw * 0.5
    circles = [(cx, ch * fy, ch * fr) for (fy, fr) in balls]

    top = [-1.0] * cw
    bot = [-1.0] * cw
    x_min, x_max = -1, -1
    for x in range(cw):
        ys = []
        for (ccx, ccy, rr) in circles:
            dx = x - ccx
            if abs(dx) <= rr:
                dy = math.sqrt(max(0.0, rr * rr - dx * dx))
                ys.append((ccy - dy, ccy + dy))
        if not ys:
            continue
        top[x] = min(y0 for y0, _ in ys)
        bot[x] = max(y1 for _, y1 in ys)
        if x_min < 0:
            x_min = x
        x_max = x
    if x_min < 0:
        return None
    # smooth the union seams (necks between balls) so the column reads as one
    # snow body, not stacked discs.
    for _ in range(2):
        st, sb = list(top), list(bot)
        for x in range(x_min, x_max + 1):
            if top[x] < 0:
                continue
            ts = [top[k] for k in (x - 1, x, x + 1) if 0 <= k < cw and top[k] >= 0]
            bs = [bot[k] for k in (x - 1, x, x + 1) if 0 <= k < cw and bot[k] >= 0]
            st[x] = sum(ts) / len(ts)
            sb[x] = sum(bs) / len(bs)
        top, bot = st, sb
    return top, bot, x_min, x_max, circles


def _snow_body(ov, contour):
    """Run the faithful snow_fx W2 recipe per-column down the stacked contour:
    OFF fill + bright WHITE crest over the top 18% + cool-blue BLUE under-edge
    over the bottom 26% + a soft cornice overhang + the sine ripple."""
    top, bot, x_min, x_max, _circles = contour
    cw = len(top)
    taper_w = 14.0
    for x in range(cw):
        yt = top[x]
        yb = bot[x]
        if yt < 0 or yb < 0 or yb <= yt:
            continue
        # rear-weight the cornice from the left edge, as snow_fx does (the
        # tailwind drives accumulation onto the back/left shoulder).
        rear = 1.0 - (x - x_min) / max(1.0, x_max - x_min)
        te = snow_fx._smooth((x - x_min) / taper_w)
        over = snow_fx.CORNICE * rear * te
        nb = (math.sin(x * 1.26) + math.sin(x * 0.34)) * 0.25 + 0.5
        y0 = yt - over
        y1 = yb + (nb - 0.5) * 2.4
        d = y1 - y0
        if d < 1.0:
            continue
        pygame.draw.line(ov, (*OFF, 255), (x, int(y0)), (x, int(y1)), 1)
        pygame.draw.line(ov, (*WHITE, 255), (x, int(y0)), (x, int(y0 + d * 0.18)), 1)
        pygame.draw.line(ov, (*BLUE, 255), (x, int(y1 - d * 0.26)), (x, int(y1)), 1)


# ── classic-snowman kit, every element seated on an analytic ball centre ─────
def _coal_dot(ov, x, y, r, *, glint=False):
    pygame.draw.circle(ov, COAL, (int(round(x)), int(round(y))), int(r))
    if r >= 2:
        pygame.draw.circle(ov, COAL_HI, (int(round(x)), int(round(y))), int(r), 1)
    if glint:
        pygame.draw.circle(ov, GLINT,
                           (int(round(x - r * 0.4)), int(round(y - r * 0.4))), 1)


def _coal_eyes(ov, hx, hy, hr):
    """Two coal dots side by side, symmetric about the vertical axis, on the
    UPPER-FRONT of the head ball."""
    r = max(2.0, hr * 0.16)
    sep = hr * 0.34
    ey = hy - hr * 0.30
    for s in (-1, +1):
        _coal_dot(ov, hx + s * sep, ey, r, glint=True)


def _carrot(ov, hx, hy, hr):
    """HORIZONTAL carrot nose, pointing forward (right), rooted on the head
    FRONT below-and-between the eyes. A flat triangle with a faint upward droop
    so it reads as a real carrot, plus segment ridges and a lit top edge."""
    droop = math.radians(6.0)                    # barely-there droop, not up-cheek
    fx, fy = math.cos(droop), math.sin(droop)
    # root centred on the head front, just below the eye band
    rx = hx - hr * 0.04
    ry = hy - hr * 0.04
    length = hr * 0.95
    half = max(2.4, hr * 0.20)                    # base half-height
    nx, ny = -fy, fx
    tip = (rx + fx * length, ry + fy * length)
    b1 = (rx + nx * half, ry + ny * half)
    b2 = (rx - nx * half, ry - ny * half)
    pygame.draw.polygon(ov, CARROT, [b1, tip, b2])
    pygame.draw.polygon(ov, CARROT_RIDGE, [b1, tip, b2], 1)
    for t in (0.34, 0.60, 0.82):
        cx = rx + (tip[0] - rx) * t
        cy = ry + (tip[1] - ry) * t
        hw = half * (1.0 - t) + 0.4
        pygame.draw.line(ov, CARROT_RIDGE,
                         (cx + nx * hw, cy + ny * hw),
                         (cx - nx * hw, cy - ny * hw), 1)
    pygame.draw.line(ov, CARROT_HI, b1, tip, 1)


def _coal_smile(ov, hx, hy, hr, *, n=5):
    """A short downward ARC of small coal dots BELOW the carrot — a smile that
    curves with the head ball. NEVER vertical bars."""
    cy = hy + hr * 0.34
    span = hr * 0.92
    n = max(4, n)
    for i in range(n):
        t = i / (n - 1)
        px = hx + (t - 0.5) * span
        py = cy + math.sin(t * math.pi) * (hr * 0.20)   # downward curve
        _coal_dot(ov, px, py, max(1.2, hr * 0.075))


def _buttons(ov, bx, by, br, *, n=3):
    """2-3 coal dots in a vertical line down the CENTRE-FRONT of the torso/base
    ball, evenly spaced about the ball centre."""
    r = max(2, int(br * 0.10))
    total = br * 1.05
    for i in range(n):
        t = (i + 0.5) / n - 0.5                   # centred, even spacing
        _coal_dot(ov, bx, by + t * total, r)


def _twig_arms(ov, mx, my, mr, *, pose="up"):
    """Two thin bare twigs out the SIDES of the MIDDLE ball, rooted ON the ball
    contour (not floating), each ending in 2-3 forked fingers. `pose` toggles
    raised vs relaxed/down. `ang` is the outward rise angle; the root is the
    point on the circle along that same angle, so every arm starts exactly on
    the contour."""
    ang = math.radians(26) if pose == "up" else math.radians(-15)
    for s in (-1, +1):
        # root point ON the ball contour, in the outward+rise direction
        rx = mx + s * math.cos(ang) * mr
        ry = my - math.sin(ang) * mr
        ln = mr * 1.15
        ex = rx + s * math.cos(ang) * ln
        ey = ry - math.sin(ang) * ln
        pygame.draw.line(ov, TWIG, (rx, ry), (ex, ey), 2)
        pygame.draw.line(ov, TWIG_HI, (rx, ry),
                         ((rx + ex) / 2, (ry + ey) / 2), 1)
        # forked fingers: a two-prong split at the tip + one branch midway
        for fk, spread in ((1.0, (20, -24)), (0.62, (26,))):
            mxp = rx + (ex - rx) * fk
            myp = ry + (ey - ry) * fk
            for dd in spread:
                fa = ang + math.radians(dd)
                fr = ln * 0.34
                pygame.draw.line(ov, TWIG, (mxp, myp),
                                 (mxp + s * math.cos(fa) * fr,
                                  myp - math.sin(fa) * fr), 1)


def _scarf(ov, hx, neck_y, neck_w, *, tail="right"):
    """Scarf wrapped at the NECK (head/torso junction): a band of short across-
    stripes hugging the neck, with ONE tail hanging down a side."""
    band_h = neck_w * 0.42
    nseg = max(4, int(band_h + 2))
    for i in range(nseg):
        t = i / max(1, nseg - 1)
        col = SCARF_RED if (i // 2) % 2 == 0 else SCARF_WHITE
        yy = neck_y - band_h * 0.5 + t * band_h
        hw = neck_w * (0.74 + 0.26 * math.sin(t * math.pi))   # hug the neck
        pygame.draw.line(ov, col, (hx - hw, yy), (hx + hw, yy), 1)
    pygame.draw.line(ov, SCARF_DARK, (hx - neck_w * 0.74, neck_y),
                     (hx + neck_w * 0.74, neck_y), 1)
    # ONE tail hanging down the chosen side
    s = 1 if tail == "right" else -1
    tx = hx + s * neck_w * 0.62
    ty = neck_y + band_h * 0.4
    seg = max(6, int(neck_w * 0.9))
    for j in range(seg):
        t = j / seg
        x0 = tx + math.sin(t * 3.0) * 1.4                # gentle flutter
        y0 = ty + t * neck_w * 1.05
        col = SCARF_RED if (j // 2) % 2 == 0 else SCARF_WHITE
        pygame.draw.line(ov, col, (x0 - neck_w * 0.16, y0),
                         (x0 + neck_w * 0.16, y0), 2)


def _hat_top(ov, hx, hy, hr):
    """Black top hat sitting FLAT ON TOP of the head ball: a horizontal brim of
    ~head-ball width on the crown, then a vertical crown box and a red band."""
    seat_y = hy - hr * 0.66                       # rests on the head crown
    brim_w = hr * 1.18
    brim_h = max(2.0, hr * 0.14)
    crown_w = hr * 0.78
    crown_h = hr * 1.25
    # brim (horizontal slab)
    pygame.draw.ellipse(ov, HAT_BLACK,
                        (hx - brim_w, seat_y - brim_h, brim_w * 2, brim_h * 2.2))
    # crown
    cy_top = seat_y - crown_h
    pygame.draw.rect(ov, HAT_BLACK,
                     (hx - crown_w, cy_top, crown_w * 2, crown_h),
                     border_radius=max(1, int(hr * 0.06)))
    # red band at the crown base
    pygame.draw.rect(ov, HAT_BAND,
                     (hx - crown_w, seat_y - crown_h * 0.26,
                      crown_w * 2, crown_h * 0.20))
    # lit left + top edges so the felt reads as a solid block, not a void
    pygame.draw.line(ov, HAT_HI, (hx - crown_w, seat_y),
                     (hx - crown_w, cy_top), 1)
    pygame.draw.line(ov, HAT_HI, (hx - crown_w, cy_top),
                     (hx + crown_w, cy_top), 1)


def _coal_cap(ov, hx, hy, hr):
    """A low coal-lump cap — a cluster of dark stones on the head crown for a
    rustic, hatless-but-not-bare read."""
    seat_y = hy - hr * 0.62
    pts = [(-0.45, 0.10), (-0.18, -0.20), (0.10, -0.26),
           (0.36, -0.10), (0.20, 0.16), (-0.12, 0.20)]
    for (fx, fy) in pts:
        _coal_dot(ov, hx + fx * hr * 1.1, seat_y + fy * hr, max(2, hr * 0.16))


# ── face cluster shared by every variant (SAME correct placement) ────────────
def _classic_face(ov, hx, hy, hr):
    _coal_eyes(ov, hx, hy, hr)
    _carrot(ov, hx, hy, hr)
    _coal_smile(ov, hx, hy, hr)


# ── the 5 variant builders ───────────────────────────────────────────────────
# Each returns (contour, draw_kit). draw_kit(ov, contour) lays the dressing on
# the finished snow body. We vary ball count, hat, and arm pose over the SAME
# face placement so the owner can pick a structure + dressing.
def _neck_y(circles, upper_i, lower_i):
    """Vertical junction between two stacked balls (where the scarf wraps)."""
    ux, uy, ur = circles[upper_i]
    lx, ly, lr = circles[lower_i]
    return (uy + ur + (ly - lr)) * 0.5


def build_variant(cw, ch, key):
    if key == "3ball_tophat_up":
        balls = [(0.78, 0.215), (0.50, 0.165), (0.255, 0.120)]
        contour = _snowman_contour(cw, ch, balls)
        circles = contour[4]
        base, mid, head = circles
        def kit(ov, c):
            _twig_arms(ov, mid[0], mid[1], mid[2], pose="up")
            _buttons(ov, base[0], base[1], base[2], n=3)
            _classic_face(ov, head[0], head[1], head[2])
            _scarf(ov, head[0], _neck_y(circles, 2, 1), head[2] * 1.05, tail="right")
            _hat_top(ov, head[0], head[1], head[2])
        return contour, kit

    if key == "3ball_tophat_down":
        balls = [(0.78, 0.215), (0.50, 0.165), (0.255, 0.120)]
        contour = _snowman_contour(cw, ch, balls)
        circles = contour[4]
        base, mid, head = circles
        def kit(ov, c):
            _twig_arms(ov, mid[0], mid[1], mid[2], pose="down")
            _buttons(ov, base[0], base[1], base[2], n=3)
            _classic_face(ov, head[0], head[1], head[2])
            _scarf(ov, head[0], _neck_y(circles, 2, 1), head[2] * 1.05, tail="left")
            _hat_top(ov, head[0], head[1], head[2])
        return contour, kit

    if key == "3ball_coalcap":
        balls = [(0.78, 0.215), (0.50, 0.165), (0.255, 0.120)]
        contour = _snowman_contour(cw, ch, balls)
        circles = contour[4]
        base, mid, head = circles
        def kit(ov, c):
            _twig_arms(ov, mid[0], mid[1], mid[2], pose="up")
            _buttons(ov, base[0], base[1], base[2], n=3)
            _classic_face(ov, head[0], head[1], head[2])
            _scarf(ov, head[0], _neck_y(circles, 2, 1), head[2] * 1.05, tail="right")
            _coal_cap(ov, head[0], head[1], head[2])
        return contour, kit

    if key == "2ball_tophat_up":
        balls = [(0.70, 0.255), (0.345, 0.165)]
        contour = _snowman_contour(cw, ch, balls)
        circles = contour[4]
        body, head = circles
        def kit(ov, c):
            _twig_arms(ov, body[0], body[1] - body[2] * 0.30, body[2], pose="up")
            _buttons(ov, body[0], body[1] + body[2] * 0.15, body[2], n=3)
            _classic_face(ov, head[0], head[1], head[2])
            _scarf(ov, head[0], _neck_y(circles, 1, 0), head[2] * 1.05, tail="right")
            _hat_top(ov, head[0], head[1], head[2])
        return contour, kit

    if key == "2ball_bare":
        balls = [(0.70, 0.255), (0.345, 0.165)]
        contour = _snowman_contour(cw, ch, balls)
        circles = contour[4]
        body, head = circles
        def kit(ov, c):
            _twig_arms(ov, body[0], body[1] - body[2] * 0.30, body[2], pose="down")
            _buttons(ov, body[0], body[1] + body[2] * 0.15, body[2], n=3)
            _classic_face(ov, head[0], head[1], head[2])
            _scarf(ov, head[0], _neck_y(circles, 1, 0), head[2] * 1.05, tail="left")
        return contour, kit

    raise KeyError(key)


def render_snowman(cw, ch, key):
    """Full snowman cell: stacked snow body + classic kit, on a transparent
    surface so it can drop on any backdrop."""
    contour, kit = build_variant(cw, ch, key)
    body = pygame.Surface((cw, ch), pygame.SRCALPHA)
    _snow_body(body, contour)
    kit(body, contour)
    return body


# ── backdrops ────────────────────────────────────────────────────────────────
def sky_panel(w, h):
    return make_gradient_surface(w, h, [(0.0, (150, 192, 232)), (1.0, (206, 226, 244))])


def whiteout_panel(w, h):
    s = make_gradient_surface(w, h, [(0.0, (224, 232, 242)), (1.0, (204, 216, 232))])
    for i in range(int(w * h / 70)):
        x = (math.sin(i * 12.9898) * 43758.5) % 1.0 * w
        y = (math.sin(i * 78.233) * 12543.7) % 1.0 * h
        r = 1 + int((math.sin(i * 3.1) * 0.5 + 0.5) * 2)
        a = 130 + int((math.sin(i * 1.7) * 0.5 + 0.5) * 90)
        fl = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
        pygame.draw.circle(fl, (255, 255, 255, a), (r, r), r)
        s.blit(fl, (int(x), int(y)))
    return s


def ground_shadow(panel, cx, base_y, w):
    """A soft elliptical ground shadow so the snowman is planted, not floating."""
    sh = pygame.Surface((int(w), int(w * 0.22)), pygame.SRCALPHA)
    pygame.draw.ellipse(sh, (40, 60, 90, 70), sh.get_rect())
    panel.blit(sh, (int(cx - w / 2), int(base_y - sh.get_height() * 0.5)))


# ── CLEAN sheet: one row of 5 large variants, each with a whiteout chip ───────
VARIANTS = [
    ("3-ball - top-hat - arms up", "3ball_tophat_up"),
    ("3-ball - top-hat - arms down", "3ball_tophat_down"),
    ("3-ball - coal cap - arms up", "3ball_coalcap"),
    ("2-ball - top-hat - arms up", "2ball_tophat_up"),
    ("2-ball - bare head - arms down", "2ball_bare"),
]


def main():
    # Render each snowman at a generous native resolution, then scale to a big
    # hero tile. The snowman is deliberately LARGER than the bird; we do NOT
    # optimise for tiny legibility.
    CW, CH = 120, 168                 # native build canvas (portrait)

    pad = 40
    gap = 34
    title_h = 104
    hero_w = 300                      # large hero tile
    hero_h = int(hero_w * CH / CW)
    chip_w = 150
    chip_h = int(chip_w * CH / CW)
    label_h = 30
    chip_label_h = 22

    n = len(VARIANTS)
    col_w = max(hero_w, chip_w)
    sheet_w = pad * 2 + n * col_w + (n - 1) * gap
    sheet_h = (title_h + label_h + hero_h + 18 + chip_label_h + chip_h + pad)

    sheet = make_gradient_surface(sheet_w, sheet_h,
                                  [(0.0, (24, 30, 44)), (1.0, (16, 20, 30))])

    ftitle = pygame.font.SysFont("Arial", 30, bold=True)
    fsub = pygame.font.SysFont("Arial", 15)
    flabel = pygame.font.SysFont("Arial", 16, bold=True)
    fchip = pygame.font.SysFont("Arial", 12)

    GOLD = (242, 208, 122)
    WLBL = (230, 238, 250)
    DIM = (168, 182, 204)

    sheet.blit(ftitle.render(
        "Pip - SNOW FULL COVER -> SNOWMAN   *   ROUND 7: pure classic snowman, correct element placement",
        True, GOLD), (pad, 26))
    sheet.blit(fsub.render(
        "Pip is fully buried and reads as a real SNOWMAN (no macaw identity). Same correct face on all five - eyes upper-front, HORIZONTAL carrot below-and-between the eyes,",
        True, DIM), (pad, 62))
    sheet.blit(fsub.render(
        "smile a downward arc, scarf at the neck, buttons centred down the body, twigs rooted on the middle ball. Snow is the shipped snow_fx W2 recipe. Whiteout chip under each.",
        True, DIM), (pad, 82))

    # pre-render each snowman once at native res
    natives = {key: render_snowman(CW, CH, key) for _, key in VARIANTS}

    row_y = title_h + label_h
    x = pad
    for label, key in VARIANTS:
        nat = natives[key]
        cx_col = x + col_w / 2

        # label centred over the column
        lbl = flabel.render(label, True, WLBL)
        sheet.blit(lbl, (int(cx_col - lbl.get_width() / 2), row_y - label_h + 4))

        # hero on sky
        hero = sky_panel(hero_w, hero_h)
        big = pygame.transform.smoothscale(nat, (hero_w, hero_h))
        ground_shadow(hero, hero_w / 2, hero_h - hero_h * 0.06, hero_w * 0.46)
        hero.blit(big, (0, 0))
        hx0 = int(cx_col - hero_w / 2)
        sheet.blit(hero, (hx0, row_y))
        pygame.draw.rect(sheet, (96, 112, 140), (hx0 - 1, row_y - 1, hero_w + 2, hero_h + 2), 1)

        # whiteout chip below, with its own little label
        chip_label_y = row_y + hero_h + 14
        clbl = fchip.render("whiteout silhouette test", True, GOLD)
        sheet.blit(clbl, (int(cx_col - clbl.get_width() / 2), chip_label_y))
        chip = whiteout_panel(chip_w, chip_h)
        small = pygame.transform.smoothscale(nat, (chip_w, chip_h))
        chip.blit(small, (0, 0))
        cx0 = int(cx_col - chip_w / 2)
        cy0 = chip_label_y + chip_label_h
        sheet.blit(chip, (cx0, cy0))
        pygame.draw.rect(sheet, (130, 146, 172), (cx0 - 1, cy0 - 1, chip_w + 2, chip_h + 2), 1)

        x += col_w + gap

    out = os.path.join(OUT_DIR, "round_7.png")
    pygame.image.save(sheet, out)
    print(f"saved {out}  ({sheet_w}x{sheet_h})")


if __name__ == "__main__":
    main()
